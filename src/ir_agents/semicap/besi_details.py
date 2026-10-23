"""Fetch Besi press-release detail pages (latest Wayback capture per slug) for results, call-invites, trading updates,
order/guidance releases and investor days. Parses release date + any stated release time.
Output: scratchpad besi_details.csv"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import besi_wb, irlib

RAW = irlib.raw_dir("BESI.AS")
DDIR = irlib.ensure(os.path.join(RAW, "wayback_details"))
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = re.compile(r"Duiven,?\s+(?:the\s+)?Netherlands,?\s+(" + MONTHS + r")\s+(\d{1,2}),?\s+(\d{4})", re.I)
REL = re.compile(r"(announces-(q[1-4]|annual|full-year)|besi-(posts|reports)|strong-q4|results|conference-call|trading-update|"
                 r"guidance|orders?-|order-for|disruption|investor-day|capital-markets|analyst|symposium|update)", re.I)
EXCL = re.compile(r"(annual-general-meeting|agenda-items|share-repurchase|transactions-under|convertible|bond|dividend|"
                  r"supervisory|ratings|euronext|stoxx|nasdaq|anniversary|french|test)", re.I)

def main():
    rows = besi_wb.cdx_rows()
    cand = {}
    for r in rows:
        u = besi_wb.norm(r[2])
        if "/details" not in u or r[3] != "text/html":
            continue
        slug = u.rstrip("/").split("/")[-1]
        if not REL.search(slug) or EXCL.search(slug):
            continue
        # prefer investor-relations pages over events pages; then latest capture
        key = slug
        pri = 1 if "/investor-relations/" in u else 0
        if key not in cand or (pri, r[1]) > (cand[key][0], cand[key][1]):
            cand[key] = (pri, r[1], r[2])
    print("candidates", len(cand))
    out = []
    for slug, (pri, ts, orig) in sorted(cand.items()):
        fn = os.path.join(DDIR, slug[:120] + ".html")
        st, b = besi_wb.wb_get(ts, orig, fn)
        if st != 200:
            print("fail", st, slug); continue
        t = irlib.html_to_text(b)
        m = DATE_RE.search(t)
        date = f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else ""
        # stated release time in call-invite releases
        rt = re.search(r"(?:release|publish|announce)\w*\s+its\s+(?:[^.]{0,160}?)\s+on\s+(\w+,?\s+(?:" + MONTHS + r")\s+\d{1,2},?\s+\d{4})"
                       r"[^.]{0,80}?(\d{1,2}[.:]\d{2})\s*(a\.?m\.?|p\.?m\.?)?\s*(CET|CEST)?", t, re.I | re.S)
        # title
        title = ""
        mt = re.search(r"\n\s*(BE Semiconductor[^\n]{5,250}|Besi[^\n]{5,250})\n", t)
        if mt: title = mt.group(1).strip()
        out.append({"slug": slug, "date": date, "title": title, "url": orig, "cap": ts, "local": fn,
                    "rel_date": rt.group(1) if rt else "", "rel_time": rt.group(2) if rt else "",
                    "ampm": (rt.group(3) or "") if rt else "", "tz": (rt.group(4) or "") if rt else ""})
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(besi_wb.SCR, "besi_details.csv"), index=False)
    print(len(df), (df.date == "").sum())

if __name__ == "__main__":
    main()
