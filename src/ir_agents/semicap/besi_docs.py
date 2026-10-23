"""Download Besi documents and extract text; write manifest.
 - Press releases: Euronext Live regulatory attachments (official PDFs) for every results / trading-update /
   investor-day release since May-2018 (Euronext node pages).
 - Presentations: quarterly results 'Webinar' decks + investor-day decks from Wayback captures of besi.com
   (besi.com refuses connections from this machine)."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from bs4 import BeautifulSoup
import irlib, besi_wb

T = "BESI.AS"
SCR = besi_wb.SCR
RAW = irlib.raw_dir(T)
PRD = irlib.ensure(os.path.join(RAW, "press_releases"))
PSD = irlib.ensure(os.path.join(RAW, "presentations"))

# Besi web page (highlights + outlook only) used where the official PDF is unavailable
WAYBACK_FALLBACK = {"2020Q1": ("20230929000000", "https://www.besi.com/investor-relations/press-releases/2020/details/test/")}


def pr_docs():
    ev = pd.read_csv(os.path.join(SCR, "besi_events_annotated.csv")).fillna("")
    ev = ev[ev.source_url.str.contains("euronext")]
    out = []
    for _, e in ev.iterrows():
        st, b = irlib.fetch(e.source_url, os.path.join(RAW, "euronext", "node_" + e.source_url.split("/")[-1] + ".html"))
        soup = BeautifulSoup(b, "html.parser")
        pdfs = [a["href"] for a in soup.find_all("a", href=True) if ".pdf" in a["href"].lower()]
        if not pdfs:
            print("no pdf", e.event_date, e.note[:60]); continue
        u = pdfs[0] if pdfs[0].startswith("http") else "https://live.euronext.com" + pdfs[0]
        per = e.fiscal_period or ("CMD" + e.event_date[:4])
        kind = "press_release" if e.event_type in ("Q1", "Q2", "Q3", "Q4") else e.event_type.lower()
        fn = os.path.join(PRD, f"{per}_{kind}_{e.event_date}.pdf")
        st, _ = irlib.fetch(u, fn)
        if st != 200:
            print("fail", st, u); continue
        # Euronext occasionally serves another issuer's file under a colliding attachment name -> validate
        if not re.search(r"Besi|BE Semiconductor", irlib.to_text(fn)[:5000]):
            print("WRONG ATTACHMENT (not a Besi document) - discarded:", u)
            os.remove(fn)
            fb = WAYBACK_FALLBACK.get(e.fiscal_period)
            if not fb:
                continue
            ts, orig = fb
            fn = os.path.join(PRD, f"{per}_{kind}_{e.event_date}_web.html")
            st, _ = besi_wb.wb_get(ts, orig, fn)
            if st != 200:
                continue
            u = orig
        out.append(dict(ticker=T, local_path=fn, url=u, doc_type="press_release", fiscal_period=e.fiscal_period,
                        pub_date=e.event_date, _per=per, _kind=kind))
    return out

def deck_docs():
    rows = besi_wb.cdx_rows()
    want = {}
    for y in range(2022, 2027):
        for q in range(1, 5):
            want[f"Webinar_Q{q}-{y}.pdf"] = (f"{y}Q{q}", "presentation")
    extra = {"Investor_Presentation_August_2026.pdf": ("2026Q2", "presentation"),
             "Capital_Markets_Day_Presentation_2022.pdf": ("CMD2022", "presentation"),
             "Investor_Day_2024.pdf": ("CMD2024", "presentation"),
             "2025_CMD_Presentation.pdf": ("CMD2025", "presentation"),
             "2026_CMD_Presentation_Final.pdf": ("CMD2026", "presentation")}
    want.update(extra)
    # live CDX lookups for 2026 items not in the cached CDX dump
    live = []
    for pre in ("besi.com/fileadmin/data/Investor_Relations/Webcasts/", "besi.com/fileadmin/data/Investor_Relations/Investor_Presentations/",
                "besi.com/fileadmin/user_upload/2026", "besi.com/fileadmin/user_upload/Webinar"):
        live += besi_wb.cdx_query(pre, "&matchType=prefix&filter=statuscode:200&from=2025")
    best = {}
    for r in rows + live:
        if len(r) < 5 or r[4] != "200":
            continue
        name = besi_wb.norm(r[2]).split("/")[-1]
        if name in want and (name not in best or r[1] > best[name][0]):
            best[name] = (r[1], r[2])
    out = []
    for name, (per, kind) in sorted(want.items(), key=lambda x: x[1][0]):
        if name not in best:
            continue
        ts, orig = best[name]
        fn = os.path.join(PSD, name)
        st, b = besi_wb.wb_get(ts, orig, fn)
        if st != 200 or not b.startswith(b"%PDF"):
            print("fail", name, st); continue
        out.append(dict(ticker=T, local_path=fn, url=orig.replace("http://", "https://"), doc_type="presentation",
                        fiscal_period=per if not per.startswith("CMD") else "", pub_date=ts[:4] + "-" + ts[4:6] + "-" + ts[6:8],
                        _per=per, _kind=kind, _wayback=besi_wb.wb_url(ts, orig)))
    return out

def main():
    docs = pr_docs() + deck_docs()
    man = []
    for d in docs:
        try:
            txt = irlib.to_text(d["local_path"])
        except Exception as ex:
            print("text fail", d["local_path"], ex); continue
        kind = d["_kind"] if d["doc_type"] == "press_release" else "presentation"
        tp = irlib.write_text(T, d["_per"], kind if kind == "press_release" else (kind if d["doc_type"] == "press_release" else "presentation"), txt)
        man.append({k: v for k, v in d.items() if not k.startswith("_")})
    # presentation pub_date: use the results release date for the quarter where available (Wayback capture date otherwise)
    ev = pd.read_csv(os.path.join(SCR, "besi_events_annotated.csv")).fillna("")
    rel = {r.fiscal_period: r.event_date for _, r in ev.iterrows() if r.event_type in ("Q1", "Q2", "Q3", "Q4")}
    for m in man:
        if m["doc_type"] == "presentation" and m["fiscal_period"] in rel and "Webinar" in m["local_path"]:
            m["pub_date"] = rel[m["fiscal_period"]]
    cmd_dates = {"CMD2022": "2022-06-15", "CMD2024": "2024-06-06", "CMD2025": "2025-06-12", "CMD2026": "2026-06-18"}
    for m in man:
        base = os.path.basename(m["local_path"])
        for k, v in cmd_dates.items():
            if m["doc_type"] == "presentation" and k[3:] in base and ("CMD" in base or "Investor_Day" in base or "Capital_Markets" in base):
                m["pub_date"] = v
        if base == "Investor_Presentation_August_2026.pdf":
            m["pub_date"] = ""  # published Aug-2026, exact day unknown (Wayback capture 2026-09-27)
    df = irlib.write_manifest(T, man)
    print(len(df), df.doc_type.value_counts().to_dict())

if __name__ == "__main__":
    main()
