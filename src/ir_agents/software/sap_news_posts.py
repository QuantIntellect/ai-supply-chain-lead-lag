"""Enumerate SAP News Center posts (WordPress REST API) related to results / outlook / CMD."""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "SAP.DE", "news_sap_posts.json")

def search(term, after="2014-12-01T00:00:00"):
    out, page = [], 1
    while True:
        u = ("https://news.sap.com/wp-json/wp/v2/posts?search=%s&per_page=100&page=%d&after=%s"
             "&_fields=id,date,date_gmt,link,title" % (term.replace(" ", "%20"), page, after))
        r = fu.get(u)
        if r.status_code != 200:
            break
        js = r.json()
        if not js:
            break
        out.extend(js)
        tp = int(r.headers.get("x-wp-totalpages", "1"))
        if page >= tp:
            break
        page += 1
    return out

def main():
    terms = ["announces results", "preliminary", "quarter results", "half-year", "outlook",
             "capital markets", "financial analyst", "fourth quarter", "third quarter",
             "first quarter", "second quarter", "Q1", "Q2", "Q3", "Q4", "guidance", "restructuring",
             "investor", "ambition"]
    seen = {}
    for t in terms:
        for p in search(t):
            seen[p["id"]] = {"id": p["id"], "date_gmt": p["date_gmt"], "date_local_site": p["date"],
                             "link": p["link"], "title": re.sub(r"<[^>]+>", "", p["title"]["rendered"])}
        print(t, len(seen))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(sorted(seen.values(), key=lambda x: x["date_gmt"]), f, indent=1)

if __name__ == "__main__":
    main()
