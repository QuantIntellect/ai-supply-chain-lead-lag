"""Extract main text from an NVIDIA newsroom / blog HTML page.

Picks the largest plausible content container (blogs.nvidia.com <article> may
hold only a teaser). Usage: python -I textify.py <html> [<out_txt>]
"""
import re
import sys
from bs4 import BeautifulSoup

CANDIDATE_SELECTORS = [
    "div.full-width-layout__sections", "div.entry-content", "div.article-body", "div.article-content",
    "div.release-body", "div.body", "article", "main", "div.content",
    "div.post-content", "section.article-body", "div.press-release-body",
]


DROP_CLASS = re.compile(r"^(related|recent-news|full-width-layout__news|share|social|comments?$|"
                        r"comment-|post-tags|tag-list|post-categories|breadcrumb|author-box|"
                        r"newsletter|subscribe|recommended|more-news|entry-sidebar|nvidia-sidebar|"
                        r"single-latest-news)", re.I)
STOP_LINES = re.compile(r"^(Categories:|Tags:|Related News|Related Posts|Recommended For You|"
                        r"Share This Article|Explore more|Leave a Reply)\s*$", re.I)


def clean_soup(soup):
    for t in soup(["script", "style", "noscript", "svg", "iframe", "form",
                   "header", "footer", "nav", "aside", "button"]):
        t.decompose()
    for el in soup.find_all(True):
        if el.attrs is None:
            continue
        toks = el.get("class", []) or []
        if el.name not in ("body", "html", "article", "main") and any(DROP_CLASS.search(t) for t in toks):
            el.decompose()
    return soup


def strip_tail(text):
    out = []
    for line in text.split("\n"):
        if STOP_LINES.match(line.strip()):
            break
        out.append(line)
    return "\n".join(out).strip()


def best_container(soup):
    best, best_len = None, 0
    for sel in CANDIDATE_SELECTORS:
        for el in soup.select(sel):
            n = len(el.get_text(" ", strip=True))
            if n > best_len:
                best, best_len = el, n
    return best


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    elif soup.title:
        title = soup.title.get_text(" ", strip=True)
    meta = {}
    for prop in ["article:published_time", "og:title", "og:url", "article:modified_time"]:
        m = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
        if m and m.get("content"):
            meta[prop] = m["content"]
    can = soup.find("link", rel="canonical")
    if can and can.get("href"):
        meta["canonical"] = can["href"]
    # JSON-LD dates
    for s in soup.find_all("script", type="application/ld+json"):
        mt = re.search(r'"datePublished"\s*:\s*"([^"]+)"', s.string or "")
        if mt and "datePublished" not in meta:
            meta["datePublished"] = mt.group(1)
    if "datePublished" not in meta and "article:published_time" not in meta:
        for el in soup.find_all(class_=re.compile(r"date", re.I)):
            mt = re.search(r"(January|February|March|April|May|June|July|August|September|October|"
                           r"November|December) \d{1,2}, \d{4}", el.get_text(" ", strip=True))
            if mt:
                meta["page_date"] = mt.group(0)
                break
    clean_soup(soup)
    cont = best_container(soup) or soup.body or soup
    # keep block structure
    for br in cont.find_all(["br"]):
        br.replace_with("\n")
    blocks = []
    for el in cont.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote", "td", "figcaption"]):
        if el.find(["p", "li", "h2", "h3", "h4"]):
            continue  # avoid double counting nested blocks
        t = el.get_text(" ", strip=True)
        if t:
            blocks.append(t)
    text = "\n".join(blocks) if sum(map(len, blocks)) > 0.5 * len(cont.get_text(" ", strip=True)) \
        else cont.get_text("\n", strip=True)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = strip_tail(text)
    return title, meta, text


if __name__ == "__main__":
    html = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    title, meta, text = html_to_text(html)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(text)
    print(title, "|", meta, "|", len(text))
