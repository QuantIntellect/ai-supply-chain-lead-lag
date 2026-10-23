"""Documents for RR.L: (1) RNS announcement bodies from Investegate (results statements, trading
updates, CMD release, event notices) for 2015-2026; (2) rolls-royce.com results presentations,
appendices and transcripts (FY2021 results -> HY2026, CMD 2023, Power Systems teach-in 2026).
Extracts text and writes data/processed/ir/RR.L_manifest.csv."""
import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import os, json
import rr_common as C
import rr_calendar as CAL

M = "https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/investors/"
# (fiscal_period/label, doc_type, pub_date, [candidate urls], local filename)
# NOTE: the verified URL must be first: irlib.download returns early when the file already exists,
# so on re-runs the first candidate is the one recorded in the manifest.
SITE = [
    ("FY2021Q4", "transcript", "2021-12-09", [M + "trading-update-transcript-2021.pdf"], "web_2021-12-09_trading_update_transcript.pdf"),
    ("FY2021", "presentation", "2022-02-24", [M + "2021-fy-presentation.pdf"], "web_2022-02-24_FY2021_presentation.pdf"),
    ("FY2021", "transcript", "2022-02-24", [M + "2021-full-year-results-transcript.pdf"], "web_2022-02-24_FY2021_transcript.pdf"),
    ("FY2022H1", "presentation", "2022-08-04", [M + "2022-hy-presentation.pdf"], "web_2022-08-04_HY2022_presentation.pdf"),
    ("FY2022H1", "presentation", "2022-08-04", [M + "2022-hy-results-appendices.pdf"], "web_2022-08-04_HY2022_appendices.pdf"),
    ("FY2022H1", "transcript", "2022-08-04", [M + "2022-hy-results-trancript.pdf", M + "2022-hy-results-transcript.pdf"], "web_2022-08-04_HY2022_transcript.pdf"),
    ("FY2022", "presentation", "2023-02-23", [M + "2022-full-year-results-presentation-v2.pdf", M + "2022-full-year-results-presentation.pdf"], "web_2023-02-23_FY2022_presentation.pdf"),
    ("FY2022", "transcript", "2023-02-23", [M + "2022-full-year-results-transcript.pdf"], "web_2023-02-23_FY2022_transcript.pdf"),
    ("FY2023Q2", "trading_update", "2023-07-26", [M + "rolls-royce-holdings-plc-trading-update-july-2023.pdf"], "web_2023-07-26_trading_update.pdf"),
    ("FY2023H1", "presentation", "2023-08-03", [M + "rr-plc-holdings-2023-half-year-results-presentation.pdf"], "web_2023-08-03_HY2023_presentation.pdf"),
    ("FY2023H1", "transcript", "2023-08-03", [M + "rr-plc-holdings-hy-results-transcript-2023.pdf"], "web_2023-08-03_HY2023_transcript.pdf"),
    ("CMD_2023-11-28", "presentation", "2023-11-28", [M + "rr-2023-capital-markets-day.pdf"], "web_2023-11-28_CMD_presentation.pdf"),
    ("CMD_2023-11-28", "presentation", "2023-11-28", [M + "capital-markets-day/rr-cmd-power-systems-23.pdf"], "web_2023-11-28_CMD_power_systems.pdf"),
    ("CMD_2023-11-28", "transcript", "2023-11-28", [M + "capital-markets-day-transcript-2023.pdf"], "web_2023-11-28_CMD_transcript.pdf"),
    ("FY2023", "presentation", "2024-02-22", [M + "results/2023-full-year-results/rr-plc-holdings-2023-full-year-results-presentation-22-feb.pdf"], "web_2024-02-22_FY2023_presentation.pdf"),
    ("FY2023", "transcript", "2024-02-22", [M + "results/2023-full-year-results/rr-plc-holdings-2023-full-year-results-transcript.pdf",
                                             M + "results/2023-full-year-results/rr-plc-holdings-fy-results-transcript-2023.pdf",
                                             M + "rr-plc-holdings-fy-results-transcript-2023.pdf",
                                             M + "rr-plc-holdings-2023-full-year-results-transcript.pdf"], "web_2024-02-22_FY2023_transcript.pdf"),
    ("FY2024H1", "presentation", "2024-08-01", [M + "results/2024-half-year-results/rr-plc-holdings-2024-half-year-results-presentation-1-aug.pdf"], "web_2024-08-01_HY2024_presentation.pdf"),
    ("FY2024H1", "transcript", "2024-08-01", [M + "rr-plc-holdings-hy-results-transcript-2024.pdf"], "web_2024-08-01_HY2024_transcript.pdf"),
    ("FY2024", "presentation", "2025-02-27", [M + "results/2024-full-year-results/rr-plc-holdings-2024-full-year-results-presentation.pdf"], "web_2025-02-27_FY2024_presentation.pdf"),
    ("FY2024", "transcript", "2025-02-27", [M + "results/2024-full-year-results/rr-plc-holdings-2024-full-year-results-transcript.pdf"], "web_2025-02-27_FY2024_transcript.pdf"),
    ("FY2025H1", "presentation", "2025-07-31", [M + "rr-plc-holdings-2025-half-year-results-presentation.pdf",
                                                 M + "rr-holdings-plc-2025-half-year-results-presentation.pdf"], "web_2025-07-31_HY2025_presentation.pdf"),
    ("FY2025H1", "presentation", "2025-07-31", [M + "rr-plc-holdings-2025-half-year-results-appendices.pdf"], "web_2025-07-31_HY2025_appendices.pdf"),
    ("FY2025H1", "transcript", "2025-07-31", [M + "rr-plc-holdings-hy-results-transcript-2025.pdf"], "web_2025-07-31_HY2025_transcript.pdf"),
    ("FY2025", "presentation", "2026-02-26", [M + "results/2025-full-year-results/rr-holdings-plc-2025-full-year-results-presentation.pdf"], "web_2026-02-26_FY2025_presentation.pdf"),
    ("FY2025", "transcript", "2026-02-26", [M + "results/2025-full-year-results/rr-plc-holdings-fy-results-transcript-2025.pdf"], "web_2026-02-26_FY2025_transcript.pdf"),
    ("PS_teach-in_2026-06-26", "presentation", "2026-06-26", [M + "power-systems-teach-in-webinar.pdf"], "web_2026-06-26_power_systems_teach_in.pdf"),
    ("FY2026H1", "presentation", "2026-07-30", [M + "rr-holdings-plc-2026-half-year-results-presentation.pdf"], "web_2026-07-30_HY2026_presentation.pdf"),
    ("FY2026H1", "presentation", "2026-07-30", [M + "rr-holdings-plc-2026-half-year-results-appendices.pdf"], "web_2026-07-30_HY2026_appendices.pdf"),
    ("FY2026H1", "transcript", "2026-07-30", [M + "rr-holdings-plc-hy-results-transcript-2026.pdf"], "web_2026-07-30_HY2026_transcript.pdf"),
]
NOTICES = [("2015-09-18", "ROLLS-ROYCE PROVIDES DATES FOR Q4 IR EVENTS"),
           ("2018-04-20", "Notice of Capital Markets Event & 2018 HY Results"),
           ("2020-12-04", "Notice of Trading Update"),
           ("2021-11-23", "Notice of Trading Update and Conference Call"),
           ("2022-05-06", "Civil Aerospace Investor Day - 13 May 2022")]


def main():
    meta = {(m["date"], m["headline"]): m for m in json.load(open(os.path.join(C.SCR, "rns_meta.json")))}
    events = CAL.build()
    man = []
    # 1) RNS bodies for calendar events
    for e in events:
        key = None
        for (d, h), m in meta.items():
            if d == e["event_date"] and m["url"] == e["source_url"]:
                key = (d, h)
        if not key:
            continue  # e.g. 2022-05-13 CMD (no RNS on the day)
        m = meta[key]
        if e["event_type"] in ("FY", "H1"):
            dt = "press_release"
        elif e["event_type"] == "CMD":
            dt = "press_release"
        else:
            dt = "trading_update"
        period = e["fiscal_period"] or f"CMD_{e['event_date']}"
        txt = irlib.extract_text(m["body"], C.TICKER, period, dt)
        man.append({"local_path": m["body"], "url": m["url"], "doc_type": dt,
                    "fiscal_period": e["fiscal_period"], "pub_date": e["event_date"], "txt": txt})
    # 2) notices evidencing event dates/times
    for d, h in NOTICES:
        m = meta[(d, h)]
        txt = irlib.extract_text(m["body"], C.TICKER, f"notice_{d}", "other")
        man.append({"local_path": m["body"], "url": m["url"], "doc_type": "other",
                    "fiscal_period": "", "pub_date": d, "txt": txt})
    # 3) company website PDFs
    missing = []
    for fp, dt, pub, urls, fname in SITE:
        rel = None
        for u in urls:
            rel = irlib.download(u, C.TICKER, fname)
            if rel:
                with open(os.path.join(irlib.ROOT, rel), "rb") as f:
                    if not f.read(5).startswith(b"%PDF"):
                        print("  not a pdf:", u); os.remove(os.path.join(irlib.ROOT, rel)); rel = None; continue
                break
        if not rel:
            missing.append((fp, dt, pub, urls[0])); continue
        txt = irlib.extract_text(rel, C.TICKER, fp, dt + ("_appendices" if "appendices" in fname else "") + ("_ps" if "power_systems" in fname else ""))
        man.append({"local_path": rel, "url": u, "doc_type": dt,
                    "fiscal_period": fp if irlib.FP_RE.match(fp) else "", "pub_date": pub, "txt": txt})
        print("ok", fp, dt, rel, txt)
    irlib.write_manifest(C.TICKER, man)
    json.dump(man, open(os.path.join(C.SCR, "manifest_txt.json"), "w"), indent=1)
    print("MISSING:", missing)


if __name__ == "__main__":
    main()
