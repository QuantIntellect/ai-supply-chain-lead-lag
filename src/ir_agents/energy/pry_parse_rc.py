import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re
from bs4 import BeautifulSoup
p = sys.argv[1]
html = open(p, encoding="utf-8", errors="replace").read()
s = BeautifulSoup(html, "html.parser")
main = s.find("main") or s
# walk: print headings and links in document order
for el in main.find_all(["h1","h2","h3","h4","h5","a","button"]):
    if el.name == "a":
        href = el.get("href","")
        t = " ".join(el.get_text(" ").split())[:90]
        if not href or href.startswith("#") or "javascript" in href: continue
        if any(k in href for k in ["/sites/", "results", "press-releases", "webcast", "youtube", "vimeo", "transcript", "audio", "mp3", "event"]):
            print("  A", t, "|", href[:200])
    else:
        t = " ".join(el.get_text(" ").split())[:100]
        if t: print(el.name.upper(), t)
