"""Nokia: download quarterly report PDFs (Nasdaq Nordic attachments) for FY2021Q4..FY2026Q3, slides where
available from nokia.com, extract text, write manifest."""
import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "NOKIA.HE"
df = pd.read_csv(os.path.join(irlib.raw_dir(T), "nasdaq_news", "nokia_notices.csv"))
ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"))
ev = ev[ev.event_type.str.match(r"^Q[1-4]$") & (ev.event_date >= "2022-01-01")]
man = []
for _, e in ev.iterrows():
    n = df[df.messageUrl == e.source_url]
    if n.empty:
        continue
    atts = json.loads(n.iloc[0].attachments)
    pdfs = [a for a in atts if a["name"] and a["name"].lower().endswith(".pdf") and "fin" not in a["name"].lower()[:3]]
    pdfs = [a for a in pdfs if "english" in a["name"].lower() or "eng" in a["name"].lower()] or pdfs
    fp = e.fiscal_period
    if pdfs:
        a = pdfs[0]
        dest = os.path.join(irlib.raw_dir(T), f"{fp}_interim_report.pdf")
        if irlib.download(a["url"], dest):
            irlib.extract_text(dest, T, fp, "interim_report")
            man.append(dict(local_path=dest, url=a["url"], doc_type="interim_report", fiscal_period=fp,
                            pub_date=e.event_date))
    y, q, ym = fp[2:6], fp[-1], e.event_date[:7]
    su = f"https://www.nokia.com/system/files/{ym}/nokia_slides_{y}_q{q}.pdf"
    dest = os.path.join(irlib.raw_dir(T), f"{fp}_presentation.pdf")
    if irlib.download(su, dest):
        with open(dest, "rb") as f:
            ok = f.read(4) == b"%PDF"
        if ok:
            irlib.extract_text(dest, T, fp, "presentation")
            man.append(dict(local_path=dest, url=su, doc_type="presentation", fiscal_period=fp, pub_date=e.event_date))
        else:
            os.remove(dest)
p, out = irlib.write_manifest(T, man)
print(p, len(out), out.doc_type.value_counts().to_dict())
