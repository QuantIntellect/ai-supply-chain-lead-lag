"""Try candidate Legrand news slugs; print datePublished for hits. Usage: lr_news_guess.py slug1 slug2 ..."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
f = Fetcher()
pdir = ensure(os.path.join(RAW_IR, "LR.PA", "pages", "newsroom"))
for s in sys.argv[1:]:
    r = f.get(f"https://www.legrand.com/en/news/{s}")
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', r.text) if r.status_code == 200 else None
    if m:
        open(os.path.join(pdir, f"news_{s}.html"), "w").write(r.text)
    print(r.status_code, s, m.group(1) if m else "")
