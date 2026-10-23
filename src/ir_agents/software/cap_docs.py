"""Download Capgemini results press releases / presentations (+CMD) and extract text; write manifest rows."""
import sys, os, re, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
import cap_util as cu

T = "CAP.PA"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
EVP = os.path.join(RAW, "event_pages.json")
CARDS = os.path.join(RAW, "event_cards.json")

def collect_cards():
    evs = json.load(open(EVP))
    out = []
    for e in evs:
        h = fu.cached_html(e["url"])
        slug = e["url"].rstrip("/").split("/")[-1]
        for c in cu.parse_cards(h):
            c["event_slug"] = slug
            out.append(c)
    json.dump(out, open(CARDS, "w"), indent=1)
    return out

def period_for(c):
    slug = c["event_slug"]
    et, fp = cu.event_period(slug)
    if fp:
        return fp
    if "capital-market" in slug:
        return re.search(r"(\d{4})", slug).group(1) + "CMD"
    if "wns" in slug:
        return "2025WNS"
    return None

def doctype_for(c):
    t = (c["type"] or "").lower()
    title = (c["title"] or "").lower()
    if "notice of publication" in title:
        return None
    if t.startswith("press"):
        return "press_release"
    if t == "presentation":
        return "cmd_presentation" if "capital market" in title else "presentation"
    if t == "transcript":
        return "transcript"
    return None

def main():
    cards = collect_cards()
    os.makedirs(TXT, exist_ok=True)
    rows = []
    for c in cards:
        dt = doctype_for(c)
        fp = period_for(c)
        if not dt or not fp or not c["file"] or c["filetype"] != "pdf":
            continue
        d = cu.to_iso(c["date"]) or ""
        yr = int(d[:4]) if d else 0
        # scope: all results press releases 2016+ (timing evidence); presentations 2021Q3+; CMD 2021/2026 key decks
        if dt == "press_release" and yr < 2016:
            continue
        if dt == "presentation" and d < "2021-10-01":
            continue
        if dt == "cmd_presentation":
            if not ("2026" in fp or ("2021" in fp and ("financial" in c["title"].lower() or "strategy" in c["title"].lower()))):
                continue
        fid = re.search(r"/file/(\d+)", c["file"]).group(1)
        suffix = ""
        if dt == "cmd_presentation" and "2021" in fp:
            suffix = "_" + ("financial" if "financial" in c["title"].lower() else "strategy")
        tl = (c["title"] or "").lower()
        if dt == "press_release":
            if "completes" in tl:
                suffix = "_closing"
            elif "approved by its shareholders" in tl:
                suffix = "_shareholder_approval"
            elif "regulatory approvals" in tl:
                suffix = "_regulatory_approval"
            elif "estimated" in tl:
                suffix = "_prelim"
        if dt == "press_release" and fp.endswith("CMD") is False and "acquisition" in (c["title"] or "").lower() and fp != "2025WNS":
            continue
        local = os.path.join(RAW, "%s_%s%s_%s.pdf" % (fp, dt, suffix, fid))
        ok = fu.download(c["file"], local)
        if not ok:
            continue
        txtp = os.path.join(TXT, "%s_%s%s.txt" % (fp, dt, suffix))
        if not os.path.exists(txtp):
            try:
                with open(txtp, "w") as f:
                    f.write(fu.pdf_to_text(local))
            except Exception as e:
                print("PDFERR", local, e)
        rows.append({"ticker": T, "local_path": os.path.relpath(local, fu.ROOT), "url": c["file"],
                     "doc_type": dt + suffix, "fiscal_period": fp, "pub_date": d,
                     "_time": cu.to_hhmm(c["time"]), "_view": c["view"] or "", "_title": c["title"]})
        print(fp, dt + suffix, d, c["time"], os.path.getsize(local))
    json.dump(rows, open(os.path.join(RAW, "docs_rows.json"), "w"), indent=1)
    man = os.path.join(fu.PROC_IR, "%s_manifest.csv" % T)
    with open(man, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"])
        for r in sorted(rows, key=lambda r: (r["pub_date"], r["doc_type"])):
            w.writerow([r["ticker"], r["local_path"], r["url"], r["doc_type"], r["fiscal_period"], r["pub_date"]])
    print("manifest rows", len(rows))

if __name__ == "__main__":
    main()
