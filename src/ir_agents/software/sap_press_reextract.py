"""Re-extract SAP News Center press-release text from the article header + entry-content only
(drops site chrome and 'related posts', which can include later-dated headlines)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
from bs4 import BeautifulSoup

log = json.load(open(os.path.join(fu.RAW_IR, "SAP.DE", "download_log.json")))
n = 0
for r in log:
    if r["doc_type"] != "press_release":
        continue
    h = open(os.path.join(fu.ROOT, r["local_path"]), encoding="utf-8").read()
    soup = BeautifulSoup(h, "html.parser")
    parts = []
    for sel in ["article", "div.entry-content"]:
        el = soup.select_one(sel)
        if el:
            parts.append(el.get_text("\n"))
    if not parts:
        continue
    txt = re.sub(r"\n\s*\n+", "\n\n", "\n".join(parts)).strip()
    with open(os.path.join(fu.ROOT, r["text_path"]), "w", encoding="utf-8") as f:
        f.write(txt)
    n += 1
print("re-extracted", n)
