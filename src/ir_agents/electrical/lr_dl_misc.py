"""Download misc Legrand releases (non-results) and extract text."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
B = "https://www.legrand.com"
items = [
    ("2018-09-11", "other", "/sites/default/files/Documents_PDF_Legrand/Finance/2018/autres/Press_Release_Legrand_09112018.pdf"),
    ("2020-03-25", "covid_update", "/sites/default/files/Documents_PDF_Legrand/Finance/2020/autres/Legrand_Press_Release_Regulated_Information_Covid-19_1585161940.pdf"),
    ("2022-10-20", "other", "/sites/default/files/Documents_PDF_Legrand/Finance/2022/autres/Legrand_PressRelease_20102022_1666284381.pdf"),
    ("2025-07-17", "prelim_release", "/sites/default/files/Documents_PDF_Legrand/Finance/2025/6m/Legrand_Press_Release_Sales_H1_2025-vf_1752729073.pdf"),
    ("2026-09-28", "cmd_release", "/sites/default/files/Documents_PDF_Legrand/Finance/2026/autre/CMD/Legrand_Press_Release_CMD_Sep-2026_1790606990.pdf"),
    ("2026-09-29", "cmd_presentation", "/sites/default/files/Documents_PDF_Legrand/Finance/2026/autre/CMD/CMD-2026-Deck_1790662658.pdf"),
    ("2024-09-24", "cmd_release", "/sites/default/files/Documents_PDF_Legrand/Finance/2024/autres/Legrand_Press_Release_CMD_September-2024_1727107150.pdf"),
    ("2024-09-24", "cmd_presentation", "/sites/default/files/Documents_PDF_Legrand/Finance/2024/autres/2024-09-20-CMD-2024-Presentation_1727156999.pdf"),
]
f = Fetcher()
for d, kind, p in items:
    fn = f"{d}_{kind}.pdf"
    ok, st, path = f.download(B + p, os.path.join(RAW_IR, "LR.PA", fn))
    pdf = ok and is_pdf(path)
    print(st, ok, pdf, fn)
    if pdf:
        out, n = to_text(path, "LR.PA", d, kind)
        with open(out) as fh:
            head = " ".join(fh.read()[:1500].split())
        print("   ", head[:700])
