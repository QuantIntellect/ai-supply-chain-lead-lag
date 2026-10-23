"""Fetch every Aixtron finance-news / ad-hoc item page, save raw HTML, parse EQS/DGAP publication timestamp."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd

T = "AIXA.DE"
MON = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def parse_ts(text):
    """Return (date, HH:MM, raw) from EQS/DGAP header, e.g. '17-Oct-2025 / 14:38 CET/CEST' or '23.02.2017 / 07:30'."""
    m = re.search(r"(\d{1,2})-([A-Z][a-z]{2})-(\d{4})\s*/\s*(\d{1,2}):(\d{2})", text)
    if m:
        mo = MON.get(m.group(2).lower())
        if mo:
            return f"{m.group(3)}-{mo:02d}-{int(m.group(1)):02d}", f"{int(m.group(4)):02d}:{m.group(5)}", m.group(0)
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\s*/\s*(\d{1,2}):(\d{2})", text)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}", f"{int(m.group(4)):02d}:{m.group(5)}", m.group(0)
    return "", "", ""


def main():
    d = irlib.ensure(os.path.join(irlib.raw_dir(T), "news"))
    fin = pd.read_csv(os.path.join(irlib.raw_dir(T), "listing_finance.csv"))
    adh = pd.read_csv(os.path.join(irlib.raw_dir(T), "listing_adhoc.csv"))
    allx = pd.read_csv(os.path.join(irlib.raw_dir(T), "listing_all.csv"))
    # press releases in the main list whose titles look results/guidance related (not already covered)
    pr = allx[allx.category.eq("Press Releases") & allx.title.str.contains(
        r"preliminar|guidance|capital markets|investor day|results|Q[1-4]/|quarter", case=False)]
    df = pd.concat([fin.assign(src="finance"), adh.assign(src="adhoc"), pr.assign(src="press")])
    df["nid"] = df.url.str.extract(r"_n(\d+)$")[0]
    df = df.drop_duplicates(["nid", "src"])
    rows = []
    for _, r in df.iterrows():
        path = os.path.join(d, f"{r.date}_{r.src}_n{r.nid}.html")
        st, b = irlib.fetch(r.url, path)
        if st != 200:
            print("ERR", st, r.url); continue
        txt = irlib.html_to_text(b)
        dt, hm, raw = parse_ts(txt)
        dl = re.search(r"Herzogenrath,?\s+(?:Germany,\s+)?([A-Z][a-z]+ \d{1,2},? \d{4})", txt)
        rows.append({"list_date": r.date, "src": r.src, "nid": r.nid, "title": r.title[:140], "url": r.url,
                     "ts_date": dt, "ts_time": hm, "ts_raw": raw, "dateline": dl.group(1) if dl else "",
                     "local_path": path})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(irlib.raw_dir(T), "news_timestamps.csv"), index=False)
    print(len(out), "pages; with time:", (out.ts_time != "").sum())


if __name__ == "__main__":
    main()
