"""Fetch 3ds.com newsroom press-release pages (English) for results/outlook/CMD items and record
article:published_time + dateline. Output: data/raw/ir/DSY.PA/newsroom_times.json"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

OUT = os.path.join(fu.RAW_IR, "DSY.PA", "newsroom_times.json")
urls = [l.strip() for l in open(os.path.join(fu.RAW_IR, "DSY.PA", "3ds_sitemap_press_urls.txt")) if l.strip()]
urls = [u for u in urls if re.match(r"https://www\.3ds\.com/newsroom/press-releases/", u)]
kw = re.compile(r"(quarter|results|outlook|full-year|fy-|capital-markets|eps|preliminary|objectives|guidance|"
                r"q[1-4]-|1q|2q|3q|4q|q416|doubl|2014-organic|3d-univrses|univ)", re.I)
neg = re.compile(r"(schedules|survey|ericsson|glm|fca-|pg-technology|dividend|khalifa|richard-petty|aisin|"
                 r"green-global|delmia|solo-keeps|enterprise-transaction)", re.I)
cand = sorted(set(u for u in urls if kw.search(u.split("/")[-1]) and not neg.search(u.split("/")[-1])))
out = []
for u in cand:
    h = fu.cached_html(u)
    if not h:
        out.append({"url": u, "status": "fail"}); continue
    m = re.search(r'article:published_time" content="([^"]+)"', h)
    t = re.sub(r"\s+", " ", fu.html_to_text(h))
    d = re.search(r"(V[ÉE]LIZY[- ]VILLACOUBLAY|PARIS)[^—–-]*[—–-]+\s*([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})", t)
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    rec = {"url": u, "published_time": m.group(1) if m else "", "dateline": d.group(2) if d else "",
           "title": title.group(1).strip()[:200] if title else ""}
    out.append(rec)
    print(rec["published_time"], "|", rec["dateline"], "|", u.split("/")[-1][:90])
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
