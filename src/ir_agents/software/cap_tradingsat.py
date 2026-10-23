"""Fetch tradingsat.com (CercleFinance/BFM) Capgemini news pages; print published_time + headline (timing evidence)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "CAP.PA", "tradingsat_evidence.json")

def main(urls):
    old = json.load(open(OUT)) if os.path.exists(OUT) else []
    have = {d["url"] for d in old}
    for u in urls:
        if u in have:
            continue
        h = fu.cached_html(u)
        if not h:
            print("NOFETCH", u); continue
        pt = re.search(r'article:published_time" content="([^"]+)"', h)
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        t = re.sub(r"\s+", " ", fu.html_to_text(h))
        m = re.search(r"(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche) \d{1,2} \w+ \d{4} à \d{2}h\d{2}[^-]{0,40}- .{0,300}", t)
        d = {"url": u, "published_time": pt.group(1) if pt else None,
             "title": title.group(1).strip()[:150] if title else None, "lead": m.group(0)[:400] if m else None}
        old.append(d)
        print(d["published_time"], "|", (d["title"] or "")[:90])
    json.dump(old, open(OUT, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main(sys.argv[1:])
