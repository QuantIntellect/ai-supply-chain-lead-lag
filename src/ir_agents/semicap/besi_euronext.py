"""Scrape Euronext Live company press-release list for Besi (issuer id 062133): exact publication timestamps.
Output: scratchpad besi_euronext.csv (released, title, href)"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from bs4 import BeautifulSoup
import irlib

SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad"
D = irlib.ensure(os.path.join(irlib.raw_dir("BESI.AS"), "euronext"))
BASE = "https://live.euronext.com/en/listview/company-press-release/062133"

def main(maxpage=60):
    rows = []
    for p in range(0, maxpage):
        url = BASE + (f"?page={p}" if p else "")
        st, b = irlib.fetch(url, os.path.join(D, f"list_p{p}.html"))
        soup = BeautifulSoup(b, "html.parser")
        n = 0
        for tr in soup.select("table tr"):
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            a = tr.find("a", href=True)
            href = ""
            for aa in tr.find_all("a"):
                if aa.get("data-node-nid"):
                    href = "https://live.euronext.com/ajax/node/company-press-release/" + aa.get("data-node-nid")
            rows.append({"released": " ".join(tds[0].get_text(" ", strip=True).split()),
                         "title": " ".join(tds[2].get_text(" ", strip=True).split()), "href": href, "page": p})
            n += 1
        print(p, st, n, rows[-1]["released"] if n else "")
        if n == 0:
            break
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(SCR, "besi_euronext.csv"), index=False)
    print(len(df))

if __name__ == "__main__":
    main()
