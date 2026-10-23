"""Download selected prysmian.com newsroom press-release pages (HTML) and extract text.
Usage: pry_prpages.py <label> <url> [<label> <url> ...]"""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re
args = sys.argv[1:]
for label, url in zip(args[::2], args[1::2]):
    rel = irlib.download(url, "PRY.MI", f"newsroom_{label}.html")
    if not rel:
        print(label, "FAIL"); continue
    txt = irlib.html_to_text(rel)
    t = re.sub(r"\s+", " ", txt)
    i = t.find("Accept Go Back")
    body = t[i + 14:] if i >= 0 else t
    j = body.find("Contacts MEDIA")
    body = body[:j] if j > 0 else body[:6000]
    print("=====", label, rel)
    print(body[:int(sys.argv[0] and 2600)])
