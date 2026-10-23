"""Download ASM quarterly press releases (2015Q1+) and investor presentations from the results center; extract text.
Writes data/processed/ir/ASM.AS_manifest.csv (pub_date filled later by asm_build.py from text/GNW)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir, to_text, write_text, session, throttle
from bs4 import BeautifulSoup
from urllib.parse import urljoin

T = "ASM.AS"
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm"
html = open(os.path.join(SP, "results_center.html")).read()
soup = BeautifulSoup(html, "html.parser")
targets = {}
for a in soup.find_all("a", href=True):
    u = urljoin("https://www.asm.com/", a["href"])
    m = re.search(r"/(\d{4})-q([1-4])-quarterly-report$", u) or re.search(r"/(\d{4})_q([1-4])_quarterly_report\.pdf$", u)
    if m:
        targets[(f"{m.group(1)}Q{m.group(2)}", "press_release")] = u
        continue
    m = re.search(r"/(\d{4})-q([1-4])-investor-presentation$", u)
    if m:
        targets[(f"{m.group(1)}Q{m.group(2)}", "presentation")] = u
rows = []
rd = raw_dir(T)
log = {}
for (per, dt), u in sorted(targets.items()):
    if per < "2015Q1":
        continue
    path = os.path.join(rd, f"{per}_{dt}.pdf")
    final_url = u
    if not (os.path.exists(path) and os.path.getsize(path) > 0):
        throttle(u)
        r = session().get(u, timeout=90, allow_redirects=True)
        if r.status_code != 200 or r.content[:5] != b"%PDF-":
            print("FAIL", per, dt, r.status_code, u); continue
        open(path, "wb").write(r.content)
        final_url = r.url
        log[path] = final_url
    txt = to_text(path)
    tp = write_text(T, per, dt, txt)
    rows.append({"ticker": T, "local_path": os.path.relpath(path, "/Users/sinamirzaei/Documents/aimapping"),
                 "url": final_url, "doc_type": dt, "fiscal_period": per, "pub_date": ""})
    print(per, dt, len(txt))
json.dump({r["local_path"]: r["url"] for r in rows}, open(os.path.join(SP, "dl_urls.json"), "w"), indent=0)
json.dump(log, open(os.path.join(SP, "dl_final_urls.json"), "a"))
print("docs", len(rows))
