"""List all SUSS news items (suss.com/en/news?page=N) -> data/raw/ir/SMHN.DE/news_index.csv"""
import os
import re
import sys
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "SMHN.DE"
cache = os.path.join(irlib.raw_dir(T), "pages")
rows = []
page = 1
while True:
    u = "https://www.suss.com/en/news" + (f"?page={page}" if page > 1 else "")
    st, html, fin = irlib.fetch(u, cache_dir=cache)
    if st != 200:
        break
    soup = BeautifulSoup(html, "html.parser")
    n0 = len(rows)
    for a in soup.find_all("a", href=True):
        href = urljoin(fin, a["href"])
        if not re.search(r"/en/news/[a-z-]+/", href):
            continue
        txt = re.sub(r"\s+", " ", a.get_text(" ")).strip()
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})\s+(.*)", txt)
        if not m:
            continue
        rows.append(dict(date=f"{m.group(3)}-{m.group(2)}-{m.group(1)}", title=m.group(4)[:250], url=href,
                         category=href.split("/en/news/")[1].split("/")[0]))
    print(page, len(rows) - n0, rows[-1]["date"] if rows else "")
    if len(rows) == n0 or page > 60:
        break
    page += 1
df = pd.DataFrame(rows).drop_duplicates("url")
df.to_csv(os.path.join(irlib.raw_dir(T), "news_index.csv"), index=False)
print(df.shape, df.date.min(), df.date.max())
print(df.category.value_counts().to_string())
