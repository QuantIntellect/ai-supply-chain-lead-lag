"""Fetch Legrand IR listing pages (regulated information per year, agenda, CMD pages)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

BASE = "https://www.legrand.com"
paths = [f"/en/investors-and-shareholders/regulated-information/{y}" for y in range(2015, 2027)]
paths += ["/en/investors-and-shareholders/financial-agenda",
          "/en/investors-and-shareholders/capital-markets-days/capital-markets-day-2024",
          "/en/investors-and-shareholders/capital-markets-days/capital-markets-day-2026",
          "/en/investors-and-shareholders/capital-markets-days/csr-capital-markets-day-2025",
          "/en/investors-and-shareholders/capital-markets-days/esg-capital-markets-day-2022",
          "/en/investors-and-shareholders/investor-day/capital-markets-day-2021",
          "/en/news/2026-first-half-results"]
f = Fetcher()
outdir = ensure(os.path.join(RAW_IR, "LR.PA", "pages"))
for p in paths:
    name = p.strip("/").replace("/", "_") + ".html"
    ok, st, path = f.download(BASE + p, os.path.join(outdir, name))
    print(st, ok, name, os.path.getsize(path) if os.path.exists(path) else 0)
