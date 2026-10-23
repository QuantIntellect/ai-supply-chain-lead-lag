"""Download VAT Group IR documents.
Sources: financial-reports page, presentations page, news index (investor items: PDFs + detail HTML pages).
Saves into data/raw/ir/VACN.SW/{docs,news_pages}/ and writes docs_list.json with url, local path, title, source."""
import os
import sys
import re
import json
from urllib.parse import unquote, urljoin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir
from bs4 import BeautifulSoup

T = "VACN.SW"
R = raw_dir(T)
DOCS = os.path.join(R, "docs")
NEWS = os.path.join(R, "news_pages")
os.makedirs(DOCS, exist_ok=True)
os.makedirs(NEWS, exist_ok=True)

SKIP = re.compile(r"sustainab|country-by-country|\.mp3|\.mp4", re.I)


def fname(url):
    base = unquote(url.split("?")[0].rstrip("/").split("/")[-1])
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return base[:150]


def news_fname(url):
    """unique local name for news pages (different URLs can share a slug, e.g. 'medienmitteilung')"""
    import hashlib
    return fname(url).replace(".html", "")[:90] + "_" + hashlib.md5(url.encode()).hexdigest()[:8] + ".html"


def page_links(url, cache):
    st, b = fetch(url, cache)
    soup = BeautifulSoup(b, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        h = urljoin(url, a["href"])
        if re.search(r"\.pdf($|\?)", h, re.I) and not SKIP.search(h):
            out.append((h, " ".join(a.get_text(" ", strip=True).split())))
    return out


def main():
    docs = []
    for src, url in [("financial_reports", "https://www.vatgroup.com/investor-relations/financial-reports"),
                     ("presentations", "https://www.vatgroup.com/investor-relations/presentations")]:
        for h, title in page_links(url, os.path.join(R, "listing", f"{src}.html")):
            # annual reports: keep only 2021+ (large files)
            m = re.search(r"annual[-_ ]report[-_ ]?(20\d\d)", h + " " + title, re.I)
            if m and int(m.group(1)) < 2021 and "summary" not in h.lower():
                continue
            if "summary" in h.lower() and "report" in h.lower():
                continue
            docs.append({"url": h, "title": title, "source": src})
    idx = json.load(open(os.path.join(R, "news_index.json")))
    for it in idx:
        if "Investors" not in it["tags"]:
            continue
        if it["url"].lower().endswith(".pdf"):
            docs.append({"url": it["url"], "title": it["title"], "source": "news_pdf", "news_date": it["date"]})
        else:
            docs.append({"url": it["url"], "title": it["title"], "source": "news_page", "news_date": it["date"]})
    seen, out = set(), []
    for d in docs:
        if d["url"] in seen:
            continue
        seen.add(d["url"])
        if d["source"] == "news_page":
            p = os.path.join(NEWS, news_fname(d["url"]))
        else:
            p = os.path.join(DOCS, fname(d["url"]))
            if not p.lower().endswith(".pdf"):
                p += ".pdf"
        st, b = fetch(d["url"], p)
        d["local_path"] = p if st == 200 else ""
        d["status"] = st
        if st != 200:
            print("FAIL", st, d["url"][:120])
        out.append(d)
    json.dump(out, open(os.path.join(R, "docs_list.json"), "w"), indent=1)
    print("docs", len(out), "ok", sum(d["status"] == 200 for d in out))


if __name__ == "__main__":
    main()
