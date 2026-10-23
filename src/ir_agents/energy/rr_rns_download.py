"""Download each candidate RNS announcement page from Investegate (irlib.download), write a
body-only copy (no site chrome / AI summary) next to it, and dump plain text to scratch for review."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import os, json
import rr_common as C

idx = C.load_index()
os.makedirs(os.path.join(C.SCR, "rns_txt"), exist_ok=True)
meta = []
for date, head, et, fp, dt in C.CANDIDATES:
    r = C.find(idx, date, head)
    slug = r["url"].rstrip("/").split("/")[-2]
    name = f"rns_{date}_{slug[:60]}_{r['rns_id']}.html"
    rel = irlib.download(r["url"], C.TICKER, name)
    if not rel:
        print("FAILED", date, head)
        continue
    full = open(os.path.join(irlib.ROOT, rel), encoding="utf-8", errors="replace").read()
    hdr = f"[Investegate RNS listing: {r['date_disp']} {r['time_disp']} (UK local) | {head} | {r['url']}]"
    bname = name.replace(".html", "_body.html")
    bpath = os.path.join(irlib.raw_dir(C.TICKER), irlib.safe_name(bname))
    with open(bpath, "w", encoding="utf-8") as f:
        f.write(C.body_html(full, hdr))
    brel = os.path.relpath(bpath, irlib.ROOT)
    txt = irlib.html_to_text(brel)
    with open(os.path.join(C.SCR, "rns_txt", f"{date}_{r['rns_id']}.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    meta.append({"date": date, "headline": head, "hhmm": r["hhmm"], "url": r["url"], "raw": rel,
                 "body": brel, "event_type": et, "fp": fp, "doc_type": dt, "chars": len(txt)})
    print(date, r["hhmm"], et, fp, len(txt), head[:50])
json.dump(meta, open(os.path.join(C.SCR, "rns_meta.json"), "w"), indent=1)
