"""Fill transcript gaps (2022+) by predicting Motley Fool URLs from the event calendar.

For each US-listed ticker with at least one known transcript, every earnings event since 2022 without a
transcript within 4 days gets candidate URLs:
  /earnings/call-transcripts/<date>/<company-slug>-<ticker>-q<N>-<FY>-earnings[-call]-transcript/
where <date> ∈ {release date, +1, +2}, the slug prefix comes from the company's known transcripts and the
fiscal-quarter label is extrapolated from the nearest known (event -> label) pair by counting events.
"""
import os
import re
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from common import RAW, PROC, WEB_UA, ensure
from fetch_fool import extract

S = requests.Session()
S.headers.update({"User-Agent": WEB_UA})


def shift_label(q, fy, k):
    idx = fy * 4 + (q - 1) + k
    return idx % 4 + 1, idx // 4


def main():
    idx = pd.read_csv(os.path.join(PROC, "fool_transcripts_index.csv"))
    E = pd.read_parquet(os.path.join(PROC, "events.parquet"))
    E["rel_date"] = E.ts_utc.dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    found = []
    PRIORITY = ["NVDA", "MSFT", "GOOGL", "AMZN", "META", "ORCL", "AVGO", "AMD", "MU", "TSM", "ASML.AS", "VRT", "ETN", "GEV",
                "ANET", "DELL", "SMCI", "CRWV", "MRVL", "LRCX", "AMAT", "KLAC", "CIEN", "COHR", "LITE", "CEG", "VST", "PWR"]
    order = PRIORITY + sorted(t for t in idx.ticker.unique() if t not in PRIORITY)
    streak = {"n429": 0}

    def get(url):
        for attempt in range(3):
            try:
                r = S.get(url, timeout=30)
            except requests.RequestException:
                time.sleep(5)
                continue
            if r.status_code == 429:
                streak["n429"] += 1
                if streak["n429"] >= 8:
                    raise SystemExit("too many 429s; stopping")
                time.sleep(90)
                continue
            streak["n429"] = 0
            time.sleep(4)
            return r
        return None

    for tk in order:
        g = idx[idx.ticker == tk]
        if g.empty:
            continue
        g = g.copy()
        m = g.slug.str.extract(r"^(.*?-%s)-q([1-4])-(\d{4})-" % re.escape(g.slug_ticker.iloc[0]))
        g["prefix"], g["q"], g["fy"] = m[0], pd.to_numeric(m[1]), pd.to_numeric(m[2])
        g = g.dropna(subset=["prefix"])
        if g.empty:
            continue
        ev = E[(E.ticker == tk)].sort_values("rel_date").reset_index(drop=True)
        if ev.empty:
            continue
        g["pd"] = pd.to_datetime(g.pub_date)
        # anchor: map each known transcript to the nearest event index
        anchors = []
        for r in g.itertuples():
            j = (ev.rel_date - r.pd).abs().idxmin()
            if abs((ev.rel_date[j] - r.pd).days) <= 4:
                anchors.append((j, int(r.q), int(r.fy), r.prefix))
        if not anchors:
            continue
        have = set(a[0] for a in anchors)
        for j, e in ev.iterrows():
            if e.rel_date < pd.Timestamp("2022-01-01") or j in have:
                continue
            a = min(anchors, key=lambda x: abs(x[0] - j))
            q, fy = shift_label(a[1], a[2], j - a[0])
            for dd in range(0, 2):
                day = e.rel_date + pd.Timedelta(days=dd)
                ok = False
                for suffix in ["earnings-call-transcript", "earnings-transcript"]:
                    url = f"https://www.fool.com/earnings/call-transcripts/{day:%Y/%m/%d}/{a[3]}-q{q}-{fy}-{suffix}/"
                    r = get(url)
                    if r is not None and r.status_code == 200:
                        txt = extract(r.text)
                        if len(txt) > 3000:
                            slug = url.rstrip("/").split("/")[-1]
                            raw = os.path.join(ensure(os.path.join(RAW, "transcripts", "fool", tk)), f"{day:%Y-%m-%d}_{slug}.html")
                            with open(raw, "w") as f:
                                f.write(r.text)
                            out = os.path.join(ensure(os.path.join(PROC, "transcripts", tk)), f"{day:%Y-%m-%d}_{slug}.txt")
                            with open(out, "w") as f:
                                f.write(txt)
                            found.append({"ticker": tk, "url": url, "slug": slug, "pub_date": f"{day:%Y-%m-%d}",
                                          "slug_ticker": g.slug_ticker.iloc[0]})
                            ok = True
                            break
                if ok:
                    break
        print(tk, "found so far", len(found), flush=True)
        if found:
            pd.DataFrame(found).to_csv(os.path.join(PROC, "fool_gapfill_found.csv"), index=False)
    F = pd.DataFrame(found)
    if len(F):
        allidx = pd.concat([idx, F[idx.columns.intersection(F.columns)]], ignore_index=True).drop_duplicates("url")
        allidx.to_csv(os.path.join(PROC, "fool_transcripts_index.csv"), index=False)
    print("gap-filled transcripts:", len(F))


if __name__ == "__main__":
    main()
