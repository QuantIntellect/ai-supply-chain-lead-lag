"""Fetch Capgemini publication pages and record WordPress article:published_time + short body text."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "CAP.PA", "publication_meta.json")

def meta(url):
    h = fu.cached_html(url)
    if not h:
        return None
    pt = re.search(r'article:published_time" content="([^"]+)"', h)
    mt = re.search(r'article:modified_time" content="([^"]+)"', h)
    t = re.sub(r"\s+", " ", fu.html_to_text(h))
    i = t.find("Search Switch sites")
    body = t[i + 60:] if i >= 0 else t
    files = sorted(set(re.findall(r'href="(https://investors\.capgemini\.com/en/file/\d+\?download=1)"', h)))
    return {"url": url, "published_time": pt.group(1) if pt else None,
            "modified_time": mt.group(1) if mt else None, "body": body[:1500], "files": files}

def main(urls):
    old = {}
    if os.path.exists(OUT):
        old = {d["url"]: d for d in json.load(open(OUT))}
    for u in urls:
        if u in old:
            continue
        d = meta(u)
        if d:
            old[u] = d
            print(d["published_time"], u.split("/publication/")[-1][:60])
    json.dump(list(old.values()), open(OUT, "w"), indent=1)

if __name__ == "__main__":
    main(sys.argv[1:])
