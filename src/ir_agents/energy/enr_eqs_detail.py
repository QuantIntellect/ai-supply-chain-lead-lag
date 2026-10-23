"""Fetch each EQS ad-hoc page for Siemens Energy and extract the dateline (dd-Mon-yyyy / HH:MM CET/CEST)
plus a short lead. Saves raw HTML to data/raw/ir/ENR.DE/ (regulatory source evidence)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr"
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(SP, "eqs_ADHOC.tsv"))]
out = open(os.path.join(SP, "eqs_adhoc_detail.tsv"), "w")
for ts, shown, dgrp, cat, title, url in rows:
    d = irlib.safe_name(dgrp.replace(" ", "_"))
    fn = f"eqs_adhoc_{d}_{url.rstrip('/').split('/')[-1][:8]}.html"
    rel = irlib.download(url, "ENR.DE", fn)
    if not rel:
        print("FAIL", url); continue
    txt = re.sub(r"\s+", " ", irlib.html_to_text(rel))
    m = re.search(r"(\d{2}[.-][A-Za-z]{3}[.-]\d{4}\s*/\s*\d{2}:\d{2}\s*(?:CET/CEST|CET|CEST|UTC)?)", txt)
    m2 = re.search(r"(\d{2}\.\d{2}\.\d{4}\s*/\s*\d{2}:\d{2}\s*(?:CET/CEST|CET|CEST)?)", txt)
    dl = m.group(1) if m else (m2.group(1) if m2 else "")
    i = txt.find("Disclosure of an inside information") if "Disclosure of an inside information" in txt else txt.find(title[:30])
    print(f"{dgrp} | shown {shown} | dateline: {dl} | {rel}")
    out.write("\t".join([dgrp, shown, dl, title, url, rel]) + "\n")
out.close()
