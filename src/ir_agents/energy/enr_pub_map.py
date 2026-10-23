"""Parse the Siemens Energy 'Publications & Ad hoc' page into (section title, anchor text, url) rows."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os, html, json
from bs4 import BeautifulSoup
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/enr"
src = os.path.join(SP, "www.siemens-energy.com_global_en_home_investor-relations_publications-ad-hoc.html.html")
s = BeautifulSoup(open(src, encoding="utf-8", errors="replace").read(), "html.parser")
rows = []
for item in s.select("[data-cmp-hook-accordion=item]"):
    dl = item.get("data-cmp-data-layer", "")
    m = re.search(r'"dc:title":"(.*?)"', html.unescape(dl))
    title = m.group(1) if m else ""
    for a in item.find_all("a"):
        href = a.get("href", "")
        if ".pdf" in href.lower() or "press-releases" in href or "choruscall" in href or ".xlsx" in href.lower():
            rows.append({"section": title, "text": " ".join(a.get_text(" ").split()), "url": href})
json.dump(rows, open(os.path.join(SP, "pub_map.json"), "w"), indent=0)
print(len(rows))
for r in rows:
    if re.search(r"FY20(2[2-6])|Capital Market|CMD|Annual Report 202[2-5]", r["section"]):
        print(f'{r["section"][:45]:45s} | {r["text"][:60]:60s} | {r["url"].split("/")[-1][:70]}')
