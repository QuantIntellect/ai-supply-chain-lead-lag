"""Infineon: fetch the client-rendered 'generic-table' JSON blocks of the financial-results page and
collect every document link -> data/raw/ir/IFX.DE/doc_links.csv"""
import os
import re
import sys
import json
import html as htmlmod
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "IFX.DE"
cache = os.path.join(irlib.raw_dir(T), "pages")
base = "https://www.infineon.com"
st, page, _ = irlib.fetch(base + "/about/investor/reports-presentations/financial-results", cache_dir=cache)
urls = sorted(set(htmlmod.unescape(u) for u in re.findall(r'(/dataApi/en/about/investor/reports-presentations/'
                                                           r'financial-results\.generic-table\.en\.json\?path=[^"\'\s<>]+)', page)))
print("tables", len(urls))
rows = []


def walk(o, ctx):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, ctx + [str(k)])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, ctx + [str(i)])
    elif isinstance(o, str):
        for m in re.finditer(r'(/assets/[^"\'\s<>]+\.pdf|https?://[^"\'\s<>]+\.pdf)', o):
            rows.append(dict(link=m.group(1), ctx="/".join(ctx[-3:]), text=o[:300]))


for u in urls:
    st, t, _ = irlib.fetch(base + u, cache_dir=cache)
    try:
        j = json.loads(t)
    except Exception:  # noqa
        print("nojson", st, u[-60:])
        continue
    n0 = len(rows)
    walk(j, [])
    # also keep cell texts to find labels / dates
    s = json.dumps(j)
    print(u[-45:], st, len(rows) - n0)
    with open(os.path.join(cache, "tbl_" + re.sub(r"[^A-Za-z0-9]", "_", u[-40:]) + ".json"), "w") as f:
        f.write(s)
df = pd.DataFrame(rows).drop_duplicates("link")
df["link"] = df.link.apply(lambda x: x if x.startswith("http") else base + x)
df.to_csv(os.path.join(irlib.raw_dir(T), "doc_links.csv"), index=False)
print(df.shape)
print("\n".join(df.link.str.replace(base, "").head(60)))
