"""Download every NVIDIA online press kit (index pages 1-2) and list doc links."""
import os
import re
import sys
import json
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from fetch import get  # noqa: E402

ROOT = "/Users/sinamirzaei/Documents/aimapping"
IDX = os.path.join(ROOT, "data/raw/keynotes/_index")
BASE = "https://nvidianews.nvidia.com"


def kit_slugs():
    slugs = []
    for fn in ["online_press_kit_index.html", "opk_page2.html"]:
        t = open(os.path.join(IDX, fn), encoding="utf-8").read()
        for s in re.findall(r'/online-press-kit/([a-z0-9\-]+)', t):
            if s not in slugs:
                slugs.append(s)
    return slugs


def parse_kit(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["header", "footer", "nav", "script", "style"]):
        t.decompose()
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        h = a["href"].split("#")[0]
        if h.startswith("/news/"):
            h = BASE + h
        if not re.search(r"(nvidianews\.nvidia\.com/news/[a-z0-9\-]+|blogs\.nvidia\.com/blog/[a-z0-9\-/]+)", h):
            continue
        if re.search(r"/blog/(tag|category|author)/", h):
            continue
        h = h.rstrip("/")
        if h in seen:
            continue
        seen.add(h)
        out.append({"url": h, "text": a.get_text(" ", strip=True)[:150]})
    title = soup.title.get_text(strip=True) if soup.title else ""
    return title, out


if __name__ == "__main__":
    res = {}
    for slug in kit_slugs():
        url = f"{BASE}/online-press-kit/{slug}"
        st, html = get(url, os.path.join(IDX, f"kit_{slug}.html"))
        title, links = parse_kit(html)
        res[slug] = {"url": url, "status": st, "title": title, "links": links}
        print(slug, st, len(links), title[:60])
    json.dump(res, open(os.path.join(IDX, "presskits.json"), "w"), indent=1)
