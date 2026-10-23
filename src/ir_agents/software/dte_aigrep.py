"""DT: print short AI/data-center snippets per document (for the narrative)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
TXT = os.path.join(fu.TXT_IR, "DTE.DE")
PAT = re.compile(r"(AI [Ff]actor|Industrial AI|NVIDIA|Nvidia|artificial intelligence|AI [Cc]loud|data cent|GPU|sovereign|AI revenue|AI-related|T-Systems)")
files = sys.argv[1:]
for fn in files:
    p = os.path.join(TXT, fn)
    if not os.path.exists(p): print("missing", fn); continue
    body = re.sub(r"\s+", " ", open(p).read())
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", body)
    hits = [s for s in sents if PAT.search(s) and 30 < len(s) < 700]
    print("==", fn, len(hits))
    for s in hits[:int(os.environ.get("N", "4"))]:
        print("  -", s[:380])
