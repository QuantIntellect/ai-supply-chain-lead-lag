"""Download Munters quarterly presentations (munters.com, edge impersonation)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import Fetcher, RAW_IR, is_pdf, to_text  # noqa: E402

T = "MTRS.ST"
BASE = "https://www.munters.com/globalassets/digizuite/"
PRES = {
    "2022Q1": ("24319-en-q1-2022--br-english-2022.pdf", "2022-04-22"),
    "2022Q2": ("24322-en-q2-pres-2022-br-english-2022-.pdf", "2022-07-15"),
    "2022Q3": ("24321-en-q3-pres-2022-br-english-2022-.pdf", "2022-10-21"),
    "2022Q4": ("24324-en-q4-2022--br-english-2022-.pdf", "2023-02-09"),
    "2023Q1": ("23423-en-q1-pres-br-english-2023.pdf", "2023-04-21"),
    "2023Q2": ("23425-en-q2-pres-br-english-2023.pdf", "2023-07-18"),
    "2023Q3": ("23424-en-q3-pres-br-english-2023.pdf", "2023-10-24"),
    "2023Q4": ("23421-en-q4-pres-br-english-2023.pdf", "2024-02-01"),
    "2024Q1": ("23422-en-q1-pres-br-english-2024.pdf", "2024-04-23"),
    "2024Q2": ("23426-en-q2-pres-br-english-202406.pdf", "2024-07-17"),
    "2024Q3": ("25337-en-presentation-q3-2024.pdf", "2024-10-22"),
    "2024Q4": ("27298-en-munters-q4-presentation-2024.pdf", "2025-02-05"),
    "2025Q1": ("28755-en-munters-q1-presentation-2025.pdf", "2025-04-29"),
    "2025Q2": ("30191-en-q2-presentation-2025.pdf", "2025-07-18"),
    "2025Q3": ("31481-en-q3-presentation-2025.pdf", "2025-10-24"),
    "2025Q4": ("32608-en-munters-q4-presentation-2025.pdf", "2026-01-29"),
    "2026Q1": ("33510-en-munters-q1-presentation-2026.pdf", "2026-04-28"),
    "2026Q2": ("34935-en-munters-q2-presentation-2026.pdf", "2026-07-17"),
}
f = Fetcher(min_gap=1.3, impersonate="edge101")
logp = os.path.join(RAW_IR, T, "docs_log.csv")
for per, (fn, d) in PRES.items():
    url = BASE + fn
    out = os.path.join(RAW_IR, T, "docs", f"{per}_presentation.pdf")
    ok, st, p = f.download(url, out)
    if not ok or not is_pdf(p):
        print("FAIL", per, st)
        if os.path.exists(p) and not is_pdf(p):
            os.remove(p)
        continue
    txt, n = to_text(p, T, per, "presentation")
    head = open(txt, encoding="utf-8").read()[:400].replace("\n", " ")
    print(per, os.path.getsize(p), n, "|", head[30:150])
    with open(logp, "a", encoding="utf-8") as fh:
        fh.write(f"{p},{url},presentation,{per},{d}\n")
