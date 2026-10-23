"""Download ASM special releases (prelims, guidance updates, investor days) from GlobeNewswire; save raw + text."""
import sys, os, re, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir, html_to_text, write_text
SP = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm"
T = "ASM.AS"
SPECIAL = {  # date_local -> (period, doctag)
    "2020-01-14": ("2019Q4", "prelim"),
    "2021-07-01": ("2021Q2", "prelim"),
    "2021-09-28": ("2021Q3", "investor_day"),
    "2022-11-28": ("2022Q4", "guidance_update"),
    "2023-01-17": ("2022Q4", "prelim"),
    "2023-09-26": ("2023Q3", "investor_day"),
    "2024-12-04": ("2024Q4", "export_update"),
    "2025-09-23": ("2025Q3", "investor_day"),
    "2026-01-19": ("2025Q4", "prelim"),
}
rows = list(csv.DictReader(open(os.path.join(SP, "gnw_all.csv"))))
out = []
for r in rows:
    if r["date_local"] in SPECIAL and re.search(r"guidance|pre-announce|investor day|export|above", r["title"], re.I) \
            and not re.search(r"net zero|details|to host", r["title"], re.I):
        per, tag = SPECIAL[r["date_local"]]
        path = os.path.join(raw_dir(T), "special", f"{r['date_local']}_{tag}.html")
        st, b = fetch(r["url"], path=path)
        txt = html_to_text(b)
        i = txt.find("Almere")
        txt = txt[i:] if i > 0 else txt
        j = txt.find("About ASM")
        txt = txt[:j] if j > 0 else txt
        tp = write_text(T, per, tag, txt)
        out.append({**r, "period": per, "tag": tag, "path": path, "text": tp, "nchar": len(txt)})
        print(r["date_local"], r["time_local"], per, tag, len(txt), r["title"][:70])
json.dump(out, open(os.path.join(SP, "special.json"), "w"), indent=0)
