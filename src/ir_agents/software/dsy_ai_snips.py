"""Print short AI-related snippets per quarter from DSY press releases + call transcripts (for note-writing)."""
import re, os, sys
D = "/Users/sinamirzaei/Documents/aimapping/data/processed/ir_text/DSY.PA"
KW = re.compile(r"(\bAI\b|artificial intelligence|generative|GenAI|UNIV\+RSES|3D UNIV|Aura\b|AI-powered|agentic|virtual companion|Companion|LLM|large language)", re.I)
periods = sys.argv[1:] or sorted(set(f.split("_")[0] for f in os.listdir(D) if f[:4] >= "2022"))
for p in periods:
    out = []
    for dt, n in (("press_release", 2), ("transcript", 3)):
        fp = os.path.join(D, "%s_%s.txt" % (p, dt))
        if not os.path.exists(fp):
            continue
        t = re.sub(r"\s+", " ", open(fp, encoding="utf-8").read())
        sents = re.split(r"(?<=[.!?])\s+", t)
        hits = [s for s in sents if KW.search(s) and 40 < len(s) < 400]
        cnt = len(re.findall(r"\bAI\b", t))
        out.append("  [%s AI-mentions=%d] " % (dt[:5], cnt) + " || ".join(h[:230] for h in hits[:n]))
    print("==", p); print("\n".join(out))
