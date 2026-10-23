"""Discover and download Motley Fool earnings-call transcripts for US-listed universe names.

1. monthly sitemaps (fool.com/sitemap/YYYY/MM) -> every /earnings/call-transcripts/ URL
2. keep URLs whose slug contains one of our tickers ("-nvda-q2-2027-...")
3. download page, extract transcript body text

Outputs: data/raw/transcripts/fool/<TICKER>/<yyyy-mm-dd>_<slug>.html (raw)
         data/processed/transcripts/<TICKER>/<yyyy-mm-dd>_<slug>.txt (text)
         data/processed/fool_transcripts_index.csv
"""
import os
import re
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import requests
from bs4 import BeautifulSoup
from common import RAW, PROC, WEB_UA, ensure

S = requests.Session()
S.headers.update({"User-Agent": WEB_UA})
SM_DIR = ensure(os.path.join(RAW, "transcripts", "fool_sitemaps"))

# slug ticker -> universe ticker (ADR/US lines for foreign names; historical tickers)
TICKERS = {t: t.upper() for t in """nvda amd avgo mrvl intc arm alab crdo mpwr tsm mu wdc stx sndk amat lrcx klac ter
anet csco cien cohr lite fn smci dell hpe cls jbl crwv nbis iren apld cifr wulf eqix dlr msft googl goog amzn meta
orcl pltr now crm adbe snow gev ceg vst tln nrg oklo smr be vrt etn nvt mod hubb pwr""".split()}
TICKERS.update({"goog": "GOOGL", "fb": "META", "asml": "ASML.AS", "sap": "SAP.DE", "nok": "NOKIA.HE",
                "stm": "STMPA.PA", "iivi": "COHR", "yndx": "NBIS"})
SLUG_RE = re.compile(r"-(%s)-(q[1-4]|fy|h[12]|\d{4})" % "|".join(sorted(TICKERS, key=len, reverse=True)))


def get(url, path=None, tries=3):
    if path and os.path.exists(path) and os.path.getsize(path) > 2000:
        return open(path, encoding="utf-8", errors="ignore").read()
    for i in range(tries):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200:
                if path:
                    ensure(os.path.dirname(path))
                    with open(path, "w") as f:
                        f.write(r.text)
                return r.text
            if r.status_code == 404:
                return ""
        except requests.RequestException:
            pass
        time.sleep(3 * (i + 1))
    return ""


def discover():
    urls = set()
    for y in range(2016, 2027):
        for m in range(1, 13):
            if (y, m) > (2026, 10):
                break
            path = os.path.join(SM_DIR, f"{y}_{m:02d}.xml")
            fresh = not os.path.exists(path) or (y, m) >= (2026, 9)
            if fresh and os.path.exists(path):
                os.remove(path)
            xml = get(f"https://www.fool.com/sitemap/{y}/{m:02d}", path)
            if fresh:
                time.sleep(0.8)
            urls.update(re.findall(r"https://www\.fool\.com/earnings/call-transcripts/[^<\s]+", xml))
    rows = []
    for u in sorted(urls):
        slug = u.rstrip("/").split("/")[-1]
        m = SLUG_RE.search(slug)
        d = re.search(r"/call-transcripts/(\d{4})/(\d{2})/(\d{2})/", u)
        if m and d:
            rows.append({"ticker": TICKERS[m.group(1)], "slug_ticker": m.group(1), "url": u, "slug": slug,
                         "pub_date": f"{d.group(1)}-{d.group(2)}-{d.group(3)}"})
    df = pd.DataFrame(rows).drop_duplicates("url")
    print("transcript urls total:", len(urls), "matched:", len(df))
    return df


def extract(html):
    s = BeautifulSoup(html, "html.parser")
    body = s.select("div.article-body")
    el = max(body, key=lambda e: len(e.get_text())) if body else None
    if el is None:
        return ""
    for t in el(["script", "style", "noscript", "aside", "figure"]):
        t.decompose()
    return "\n".join(l.strip() for l in el.get_text("\n").splitlines() if l.strip())


def main():
    df = discover()
    df.to_csv(os.path.join(PROC, "fool_transcripts_index.csv"), index=False)
    out_txt = ensure(os.path.join(PROC, "transcripts"))
    n_ok = 0
    for i, r in enumerate(df.sort_values("pub_date", ascending=False).itertuples()):
        raw_path = os.path.join(RAW, "transcripts", "fool", r.ticker, f"{r.pub_date}_{r.slug}.html")
        txt_path = os.path.join(out_txt, r.ticker, f"{r.pub_date}_{r.slug}.txt")
        if os.path.exists(txt_path):
            n_ok += 1
            continue
        had = os.path.exists(raw_path)
        html = get(r.url, raw_path)
        if not had:
            time.sleep(1.0)
        txt = extract(html) if html else ""
        if len(txt) > 3000:
            ensure(os.path.dirname(txt_path))
            with open(txt_path, "w") as f:
                f.write(txt)
            n_ok += 1
        if i % 100 == 0:
            print(i, r.ticker, r.pub_date, len(txt), "ok so far", n_ok, flush=True)
    print("done; transcripts saved:", n_ok)


if __name__ == "__main__":
    main()
