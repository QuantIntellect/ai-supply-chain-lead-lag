"""DT: fetch documents missing from the year pages (from the IR downloads page) + CMD/AI-day decks; fix mislabeled files."""
import sys, os, re, html, json, shutil
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "DTE.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
WANT = {  # filename regex -> (period, doctype)
    r"^dt-23q4-transcript-of-webcast": ("2023Q4", "transcript"),
    r"^DT 23Q4 Media information": ("2023Q4", "press_release"),
    r"^dt-26q1-presentation": ("2026Q1", "presentation"),
    r"^DTE-XE_Transcript_2026-05-13": ("2026Q1", "transcript"),
    r"^DT 26Q1 Interim report": ("2026Q1", "interim_report"),
    r"^DT 26Q1 Media information": ("2026Q1", "press_release"),
    r"^DT 25Q1 Backup": ("2025Q1", "backup"),
    r"^dt-23q2-backup|^DT 23Q2 Backup": ("2023Q2", "backup"),
    r"^DT 24Q2 Backup|^dt-24q2-backup": ("2024Q2", "backup"),
    r"^DT 24Q3 Backup|^dt-24q3-backup": ("2024Q3", "backup"),
    r"^DT 23Q3 Backup|^dt-23q3-backup": ("2023Q3", "backup"),
    r"^DT 24Q2 Media information": ("2024Q2", "press_release"),
    r"^DT 25Q2 Media information": ("2025Q2", "press_release"),
    r"^DT 25Q4 Media information": ("2025Q4", "press_release"),
    r"^DT 25Q2 Interim report|^DT 25Q2 Interim Report": ("2025Q2", "interim_report"),
}

def main():
    rows = []
    h = fu.cached_html("https://www.telekom.com/en/investor-relations/publications/downloads")
    links = [html.unescape(l) for l in re.findall(r'href="(https://delivery-[^"]+)"', h)]
    for l in links:
        nm = unquote(l.split("/as/")[-1].split("?")[0])
        for pat, (per, dtp) in WANT.items():
            if re.search(pat, nm, re.I):
                tp = os.path.join(TXT, "%s_%s.txt" % (per, dtp))
                if os.path.exists(tp):
                    continue
                fn = re.sub(r"[^A-Za-z0-9._-]+", "_", nm)
                dest = os.path.join(RAW, per, fn)
                if fu.download(l, dest, min_bytes=2000):
                    open(tp, "w").write(fu.pdf_to_text(dest))
                    rows.append({"ticker": T, "local_path": os.path.relpath(dest, fu.ROOT), "url": l, "doc_type": dtp,
                                 "fiscal_period": per, "pub_date": ""})
                    print("OK", per, dtp, nm, flush=True)
    # CMD 2024 all-in-one + group strategy transcript; AI Investor Day all-in-one
    for page, per in [("https://www.telekom.com/en/investor-relations/publications/capital-markets-days", "CMD2024"),
                      ("https://www.telekom.com/en/investor-relations/publications/capital-markets-days/ai-investor-day", "AIDAY2026")]:
        hh = fu.cached_html(page)
        for l in [html.unescape(x) for x in re.findall(r'href="(https://delivery-[^"]+)"', hh)]:
            nm = unquote(l.split("/as/")[-1].split("?")[0])
            dtp = None
            if re.search(r"All.?in.?One", nm, re.I): dtp = "cmd_presentation"
            elif re.search(r"transcript", nm, re.I) and not any(r["doc_type"] == "cmd_transcript" and r["fiscal_period"] == per for r in rows): dtp = "cmd_transcript"
            if not dtp: continue
            tp = os.path.join(TXT, "%s_%s.txt" % (per, dtp))
            if os.path.exists(tp): continue
            fn = re.sub(r"[^A-Za-z0-9._-]+", "_", nm)
            dest = os.path.join(RAW, per, fn)
            if fu.download(l, dest, min_bytes=2000):
                open(tp, "w").write(fu.pdf_to_text(dest))
                rows.append({"ticker": T, "local_path": os.path.relpath(dest, fu.ROOT), "url": l, "doc_type": dtp,
                             "fiscal_period": per, "pub_date": "2024-10-10" if per == "CMD2024" else "2026-10-05"})
                print("OK", per, dtp, nm, flush=True)
    json.dump(rows, open(os.path.join(RAW, "dte_docs_extra_rows.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
