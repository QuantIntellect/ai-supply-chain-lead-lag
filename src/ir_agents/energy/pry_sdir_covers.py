"""Download eMarket Storage PDFs (eMarket SDIR / 1Info cover sheets) and parse the regulatory stamp:
'Informazione Regolamentata n. 0902-xx-YYYY', 'Data/Ora Ricezione', 'Data/Ora Inizio Diffusione presunta', 'Oggetto'.
Appends to data/raw/ir/PRY.MI/sdir_covers.csv. Usage: pry_sdir_covers.py <url> [<url> ...]  (or @file)"""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import csv, os, re
MESI = {"Gennaio": 1, "Febbraio": 2, "Marzo": 3, "Aprile": 4, "Maggio": 5, "Giugno": 6, "Luglio": 7, "Agosto": 8,
        "Settembre": 9, "Ottobre": 10, "Novembre": 11, "Dicembre": 12}
args = sys.argv[1:]
if args and args[0].startswith("@"):
    args = open(args[0][1:]).read().split()
out = os.path.join(irlib.RAW_IR, "PRY.MI", "sdir_covers.csv")
done = {r["url"] for r in irlib.read_csv(out)}
rows = irlib.read_csv(out)
def parse_dt(s):
    m = re.search(r"(\d{1,2}) (\w+) (\d{4}) (\d{1,2}):(\d{2}):(\d{2})", s or "")
    if not m or m.group(2) not in MESI: return ""
    return f"{m.group(3)}-{MESI[m.group(2)]:02d}-{int(m.group(1)):02d} {int(m.group(4)):02d}:{m.group(5)}:{m.group(6)}"
for url in args:
    url = url.replace("https://emarketstorage.it/", "https://www.emarketstorage.it/")
    if url in done: continue
    fn = "sdir_" + url.rsplit("/", 1)[-1]
    rel = irlib.download(url, "PRY.MI", fn)
    if not rel:
        rows.append({"url": url, "local": "", "n": "", "ricezione": "", "diffusione": "", "oggetto": "FAIL"}); continue
    try:
        t = re.sub(r"\s+", " ", irlib.pdf_to_text(rel)[:4000])
    except Exception as e:
        t = ""
    n = re.search(r"Informazione Regolamentata n\. ?([0-9-]+)", t)
    ric = re.search(r"Data/Ora Ricezione ?:? ?(\d{1,2} \w+ \d{4} \d{1,2}:\d{2}:\d{2})", t)
    dif = re.search(r"Data/Ora Inizio Diffusione( presunta)? ?:? ?(\d{1,2} \w+ \d{4} \d{1,2}:\d{2}:\d{2})", t)
    ogg = re.search(r"Oggetto ?: ?(.{0,140}?)(Testo del comunicato|$)", t)
    row = {"url": url, "local": rel, "n": n.group(1) if n else "",
           "ricezione": parse_dt(ric.group(1)) if ric else "", "diffusione": parse_dt(dif.group(2)) if dif else "",
           "oggetto": ogg.group(1).strip() if ogg else t[:100]}
    print(row["n"], row["ricezione"], row["diffusione"], "|", row["oggetto"][:90])
    rows.append(row)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["url", "local", "n", "ricezione", "diffusione", "oggetto"])
    w.writeheader(); w.writerows(rows)
print("rows", len(rows))
