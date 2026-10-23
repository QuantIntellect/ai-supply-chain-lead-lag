"""Soitec: download results press releases (regulated-information page), extract text, derive event dates
from datelines and timing from 'Agenda ... after market close' statements; write SOI.PA events + manifest."""
import os
import re
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SOI.PA"
SCR = os.path.dirname(irlib.LOCK_DIR)
links = [l.split(" | ")[-1].strip() for l in open(os.path.join(SCR, "soi_links.txt")) if " | " in l]
keep = [u for u in links if re.search(r"(pr|cp|sales|results|revenue|trading-update|fy'26|q[1-4]'?2?\d)", u, re.I)
        and not re.search(r"availab|registration|urd|agm|esg|governance|liquidit|appoints|succession|"
                          r"settlement|half-year-report|half-year-financial|rapport_semestriel|financialreport3112|"
                          r"half_year_report|pr-half-year-report|project-signal", u, re.I)]
keep = list(dict.fromkeys(keep))
print("candidate PRs", len(keep))
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
recs = []
for u in keep:
    parts = u.split("?")[0].split("/")
    fn = re.sub(r"[^A-Za-z0-9._-]", "_", parts[-3] + "_" + parts[-1])[-100:]
    u = u.replace("soitec-stg.sitefinity.cloud", "www.soitec.com")
    dest = os.path.join(irlib.raw_dir(T), "src_" + fn)
    if not irlib.download(u, dest):
        continue
    try:
        txt = irlib.pdf_to_text(dest)
    except Exception as e:  # noqa
        print("pdf fail", fn)
        continue
    head = re.sub(r"\s+", " ", txt[:3000])
    m = re.search(rf"(?:France|Grenoble\)?),?\s*(?:on\s*)?((?:{MONTHS})\s*\d{{1,2}}(?:st|nd|rd|th)?,?\s*\d{{4}})", head)
    if not m:
        m = re.search(rf"((?:{MONTHS})\s*\d{{1,2}}(?:st|nd|rd|th)?,?\s*\d{{4}})", head)
    d = None
    if m:
        s = re.sub(r"(st|nd|rd|th)", "", m.group(1)).replace(",", "")
        s = re.sub(r"\s+", " ", s)
        try:
            d = datetime.strptime(s, "%B %d %Y").strftime("%Y-%m-%d")
        except Exception:  # noqa
            d = None
    title = head[:400]
    recs.append(dict(url=u, local=dest, date=d, head=title))
df = pd.DataFrame(recs)
df.to_csv(os.path.join(irlib.raw_dir(T), "pr_index.csv"), index=False)
print(df[["date"]].assign(f=df.local.str[-60:]).to_string())
