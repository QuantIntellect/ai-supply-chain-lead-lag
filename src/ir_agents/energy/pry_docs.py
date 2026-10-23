"""Download Prysmian results press releases / presentations from the Results Centre and extract text.
Writes data/raw/ir/PRY.MI/docs_index.csv (period, doctype, url, local_path, text_path)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os
B = "https://www.prysmian.com/sites/www.prysmian.com/files/media/documents/investors/"
PR = {  # period -> results press release (Results Centre, EN)
 "FY2026H1": "PR_Q2%2726_EN_FINAL.pdf", "FY2026Q1": "PR_Q126_Results_3004226.pdf",
 "FY2025": "PR_Prysmian_FY25_26022026.pdf", "FY2025Q3": "PR_PRYSMIAN_RESULTS_Q3_25_ENGLISH.pdf",
 "FY2025H1": "PR_PRYSMIAN_RESULTS_Q2_25_ENG.pdf", "FY2025Q1": "PR_Prysmian_1Q25_ENG.pdf",
 "FY2024": "PR_Prysmian_FY2024_Results_DEF.pdf", "FY2024Q3": "PR_Prysmian_9M24_results_ENGLISH.pdf",
 "FY2024H1": "PR-Prysmian-1H24-results-ENG.pdf", "FY2024Q1": "pr-1q24-results-eng.pdf",
 "FY2023": "pr-fy23-results-def-eng.pdf", "FY2023Q3": "pr-pg-9-11-23-9m-results-eng-def.pdf",
 "FY2023H1": "pr-pg-1h-27-07-23-eng.pdf", "FY2023Q1": "pr-pg-1q-11-05-23-eng-v2.pdf",
 "FY2022": "pr-fy-2023-03-09-eng.pdf", "FY2022Q3": "pr-pg-9m-10-11-22-eng.pdf",
 "FY2022H1": "pg-1h-28-07-22-eng.pdf", "FY2022Q1": "PR_PG_1Q_12_05_22_ENG_0.pdf",
 "FY2021": "1_3_PR_PG_FY21%20ENG.pdf", "FY2021Q3": "PR_PG_9M_11_11_21-ENG.pdf",
 "FY2021H1": "PG-1H-28-07-21-ENG.pdf", "FY2021Q1": "PR_PG_1Q_13_05_21_ENG.pdf",
 "FY2020": "PR_PG_FY20_10_03_21_ENG.pdf", "FY2020Q3": "PR_%20PG_9M_29_10_20.ENG_.pdf",
 "FY2020H1": "PR%20PG%201H%202020%20ENG.pdf", "FY2020Q1": "PR_PG_Q1%20RESULTS_ENG.pdf",
 "FY2019": "CS_PG_FY19_05_03_20_ENG_0.pdf", "FY2019Q3": "PR_Prysmian_9M_12_11_19_ENG.pdf",
 "FY2019H1": "PR_Prysmian_1H_1_8_19_ENG.pdf", "FY2019Q1": "PR_Prysmian_1Q_13_5_19_ENG_0.pdf",
 "FY2018": "PR_Prysmian%20Group_FY2018_ENG_1_0_0.pdf", "FY2018Q3": "PR_Prysmian%20Group_3Q_14_11_2018_ENG.pdf",
 "FY2018H1": "PR_Prysmian%20Group_H1_18092018_ENG.pdf", "FY2018Q1": "PR_Prysmian%20Group_3Q_10_5_18.pdf",
 "FY2017": "PR_Prysmian%20Group_FY%202017_27_02_18_ENG.pdf", "FY2017Q3": "PR_Prysmian%20Group_9M%202017_07_11_17_ENG.pdf",
 "FY2017H1": "PR_Prysmian%20Group_H1%202017_27_07_17_ENG.pdf", "FY2017Q1": "PR_Prysmian%20Group_Q1%202017_10_05_17_EN.pdf",
 "FY2016": "PR_Prysmian%20Group_FY%202016_01_03_17_EN.pdf", "FY2016Q3": "PR_Prysmian%20Group_9M%202016_08_11_16_EN.pdf",
 "FY2016H1": "PR_Prysmian%20Group_1H%202016_28_07_16_EN.pdf", "FY2016Q1": "Prysmian%20Group_PR_Q1%202016_10_05_16_EN.pdf",
 "FY2015": "PR_Prysmian%20Group_FY%202015_24_02_16_EN.pdf", "FY2015Q3": "PR_Prysmian%20Group_9M%202015_05_11_15_EN.pdf",
 "FY2015H1": "PR_Prysmian%20Group_1H%202015_30_07_15_EN.pdf", "FY2015Q1": "Prysmian%20Group_PR_Q1%202015_07_05_15_EN.pdf",
 "FY2014": "PR_Prysmian%20Group_FY%202014_25_02_15_EN.pdf",
}
PRES = {
 "FY2026H1": "Prysmian_2Q26_Presentation_def.pdf", "FY2026Q1": "Prysmian_1Q26_Presentation_def_0.pdf",
 "FY2025": "Prysmian%20FY25_Presentation_def.pdf", "FY2025Q3": "Prysmian_9M25_Presentation_def.pdf",
 "FY2025H1": "Prysmian_1H25_Presentation_def.pdf", "FY2025Q1": "Prysmian_1Q25_Presentation_def_0.pdf",
 "FY2024": "Prysmian_FY24_Presentation_def_1.pdf", "FY2024Q3": "Prysmian_9M24_Presentation_def_1.pdf",
 "FY2024H1": "Prysmian-1H24-Presentation-def.pdf", "FY2024Q1": "Prysmian-1Q24-presentation-def.pdf",
 "FY2023": "Prysmian-fy23-presentation-def.pdf", "FY2023Q3": "prysmian-9m23-presentation-def.pdf",
 "FY2023H1": "prysmian-1h23-presentation-def-v2.pdf", "FY2023Q1": "prysmian-1q23-presentation-def.pdf",
 "FY2022": "prysmian-fy22-presentation-def.pdf", "FY2022Q3": "prysmian-9m22-presentation-def.pdf",
 "FY2022H1": "prysmian-1H22-presentation-def_0.pdf", "FY2022Q1": "Prysmian%201Q22_Presentation_def.pdf",
}
OTHER = [  # (period label, doctype, url, filename)
 ("CMD2025", "presentation", "https://www.prysmian.com/sites/www.prysmian.com/files/2025-03/250325_Prysmian_CMD_Static_conC_.pdf", "CMD2025_presentation.pdf"),
 ("FY2024Q2_EncoreWire", "presentation", "https://www.prysmian.com/sites/www.prysmian.com/files/media/documents/prysmian-acquisition-of-encore-wire.pdf", "EncoreWire_acquisition_presentation_2024-04-15.pdf"),
 ("FY2026Q3_Atkore", "presentation", "https://www.prysmian.com/sites/www.prysmian.com/files/media/documents/Prysmian-to-acquire-Atkore-Presentation-Read-Only.pdf", "Atkore_acquisition_presentation_2026-08-03.pdf"),
]
jobs = []
for p, f in PR.items():
    jobs.append((p, "press_release", B + f, f"{p}_press_release.pdf"))
for p, f in PRES.items():
    jobs.append((p, "presentation", B + f, f"{p}_presentation.pdf"))
jobs += OTHER
out = os.path.join(irlib.raw_dir("PRY.MI"), "docs_index.csv")
rows = []
for p, dt, url, fn in jobs:
    rel = irlib.download(url, "PRY.MI", fn)
    txt = irlib.extract_text(rel, "PRY.MI", p, dt) if rel else None
    print(p, dt, "OK" if rel else "FAIL", txt or "")
    rows.append({"period": p, "doctype": dt, "url": url, "local_path": rel or "", "text_path": txt or ""})
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["period", "doctype", "url", "local_path", "text_path"])
    w.writeheader(); w.writerows(rows)
print("done", sum(1 for r in rows if r["local_path"]), "/", len(rows))
