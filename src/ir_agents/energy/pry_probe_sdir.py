"""Locate a migrated eMarket Storage PDF for a given date by probing sequential document ids (HEAD, polite).
Usage: pry_probe_sdir.py YYYYMMDD start end stride  -> prints hits; downloads hits in the day's tail and checks
the SDIR cover for PRYSMIAN (writes results via pry_sdir_covers-style lines)."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import time, re
day, a, b, stride = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
BASE = "https://www.emarketstorage.it/sites/default/files/comunicati/2022-05/"
s = irlib._sess()
last = [0.0]
def head(i):
    w = 1.05 - (time.time() - last[0])
    if w > 0: time.sleep(w)
    last[0] = time.time()
    try:
        r = s.head(f"{BASE}{day}_{i}.pdf", timeout=30, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False
hits = [i for i in range(a, b, stride) if head(i)]
print("phase1 hits", hits, flush=True)
if not hits:
    sys.exit(0)
# extend forward to the end of the day
i, miss, end = max(hits) + 1, 0, max(hits)
while miss < 25:
    if head(i):
        end, miss = i, 0
    else:
        miss += 1
    i += 1
lo = min(hits) - stride
print("day range approx", lo, end, flush=True)
# scan from the end backwards, fetch hits and check cover
found = 0
for j in range(end, lo, -1):
    if not head(j):
        continue
    rel = irlib.download(f"{BASE}{day}_{j}.pdf", "PRY.MI", f"probe_{day}_{j}.pdf")
    if not rel: continue
    t = re.sub(r"\s+", " ", irlib.pdf_to_text(rel)[:1500])
    is_pry = "PRYSMIAN" in t.upper()[:900]
    m = re.search(r"Data/Ora Inizio Diffusione( presunta)? ?:? ?(\d{1,2} \w+ \d{4} \d{1,2}:\d{2}:\d{2}).{0,40}Oggetto ?: ?(.{0,90})", t)
    print(j, "PRY" if is_pry else "---", m.group(2) if m else "", (m.group(3) if m else "")[:80], flush=True)
    if is_pry:
        found += 1
        print("PRYSMIAN_URL", f"{BASE}{day}_{j}.pdf", flush=True)
        if found >= 3: break
    else:
        import os; os.remove(irlib.ROOT + "/" + rel)
