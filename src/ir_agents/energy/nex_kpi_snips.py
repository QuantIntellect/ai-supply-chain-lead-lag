"""Print compact KPI candidate snippets for each Nexans results press release (for manual verification)."""
import sys, re, os
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

T = "NEX.PA"
PATS = {
    "std": r"(standard sales|sales at standard metal prices)[^.]{0,60}?(€|EUR )?\s?([\d,\.]+)\s?(million|billion)",
    "cur": r"(current metal prices)[^.]{0,80}?(€|EUR )?\s?([\d,\.]+)\s?(million|billion)|([\d,\.]+)\s?(million|billion)(?: euros)? at current metal prices",
    "org": r"organic(?:ally)?(?: growth)?[^.]{0,25}?([+\-−–]\s?\d+\.?\d*)\s?%|([+\-−–]?\s?\d+\.?\d*)\s?% organic",
    "ebitda": r"(adjusted )?EBITDA[^.]{0,40}?(€|EUR )\s?([\d,\.]+)\s?(million|billion)",
    "margin": r"(\d+\.\d)\s?% of standard sales|margin[^.]{0,30}?(\d+\.\d)\s?%",
    "backlog": r"backlog[^.]{0,90}?(€|EUR )\s?([\d,\.]+)\s?(billion|million)",
    "guid": r"(guidance|outlook)[^.]{0,30}?(confirmed|upgraded|raised|revised|for 20\d\d)[^.]{0,200}",
    "dc": r"data[ -]?cent(er|re)s?",
}
which = sys.argv[1:]  # e.g. FY2026Q3 FY2026H1
for fp in which:
    f = f"data/processed/ir_text/{T}/{fp}_press_release.txt"
    if not os.path.exists(os.path.join(irlib.ROOT, f)):
        print("missing", f); continue
    print("=====", fp)
    for k, p in PATS.items():
        n = 3 if k in ("guid", "dc", "backlog", "org") else 2
        for s in irlib.grep(f, p, width=70 if k != "guid" else 30, maxn=n):
            print(f"[{k}] {s}")
