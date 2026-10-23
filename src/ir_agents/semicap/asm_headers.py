"""Parse date and stated time from ASM press-release headers; compare with GNW timestamps."""
import os, re, glob, csv, json
from datetime import datetime
TD = "/Users/sinamirzaei/Documents/aimapping/data/processed/ir_text/ASM.AS"
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm"
gnw = list(csv.DictReader(open(os.path.join(SP, "gnw_all.csv"))))
out = {}
for f in sorted(glob.glob(os.path.join(TD, "*_press_release.txt"))):
    per = os.path.basename(f).split("_")[0]
    head = " ".join(open(f).read()[:700].split())
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})(?:,\s*([0-9:.]+\s*[ap]\.?m\.?)\s*(CET|CEST)?)?", head)
    d = datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").strftime("%Y-%m-%d") if m else ""
    tstr = (m.group(4) or "") if m else ""
    hhmm = ""
    if tstr:
        mm = re.match(r"(\d{1,2})(?:[:.](\d{2}))?\s*([ap])", tstr.replace(" ", ""))
        h = int(mm.group(1)) % 12 + (12 if mm.group(3) == "p" else 0)
        hhmm = f"{h:02d}:{int(mm.group(2) or 0):02d}"
    g = [r for r in gnw if r["date_local"] == d and re.search(r"(reports|announces|report).*(quarter|q[1-4])|results", r["title"], re.I)
         and not re.search(r"conference call|availability|annual report|interim", r["title"], re.I)]
    out[per] = {"date": d, "hdr_time": hhmm, "gnw": [(r["time_local"], r["title"][:60], r["url"]) for r in g]}
    print(per, d, hhmm or "-", "|", "; ".join(f"{t} {ti}" for t, ti, _ in out[per]["gnw"]) or "NO-GNW-MATCH")
json.dump(out, open(os.path.join(SP, "headers.json"), "w"), indent=0)
