"""Per-company digests of the demand-relevant sentences in each earnings call (2022+).

For every transcript, keep up to N sentences that mention a demand keyword AND carry a number or a
directional word, ranked by keyword density. Output: data/processed/digests/<TICKER>.md
(one section per call date) - compact enough to read the whole AI-era history of a company.
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import PROC, ensure

KEY = re.compile(r"\b(demand|guidance|outlook|expect\w*|backlog|orders?|bookings?|book-to-bill|constrain\w*|supply|capacity|"
                 r"capex|capital expenditure\w*|data ?cent(?:er|re)s?|hyperscal\w*|AI|inference|training|GPU\w*|accelerat\w*|"
                 r"lead times?|visibility|inventory|pricing|gigawatt\w*|power|customers?|sovereign|neocloud\w*|Blackwell|Rubin|HBM)\b", re.I)
SIGNAL = re.compile(r"(\d|record|strong|accelerat|unprecedented|sold out|constrain|tight|exceed|raise|increase|double|triple|"
                    r"declin|weak|soft|slow|digest|push|delay|caution|lower|cut)", re.I)
N = 22


def spoken(text):
    i = text.find("Operator:")
    return text[i:] if i >= 0 else text


def main():
    out = ensure(os.path.join(PROC, "digests"))
    for d in sorted(glob.glob(os.path.join(PROC, "transcripts", "*"))):
        tk = os.path.basename(d)
        parts = [f"# {tk} — earnings-call demand digest (auto-extracted sentences, 2022+)\n"]
        for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
            date = os.path.basename(f)[:10]
            if date < "2022-01-01":
                continue
            txt = re.sub(r"\s+", " ", spoken(open(f, encoding="utf-8", errors="ignore").read()))
            sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", txt)
            scored = []
            for i, s in enumerate(sents):
                if len(s) < 60 or len(s) > 450:
                    continue
                k = len(KEY.findall(s))
                if k >= 2 and SIGNAL.search(s):
                    scored.append((k + (1 if re.search(r"\d", s) else 0), i, s))
            top = sorted(sorted(scored, reverse=True)[:N], key=lambda x: x[1])
            slug = os.path.basename(f)[11:-4]
            parts.append(f"\n## {date} ({slug})\n" + "\n".join(f"- {s}" for _, _, s in top))
        with open(os.path.join(out, f"{tk}.md"), "w") as fh:
            fh.write("\n".join(parts))
    sizes = {os.path.basename(p)[:-3]: os.path.getsize(p) // 1000 for p in glob.glob(os.path.join(out, "*.md"))}
    print(len(sizes), "digests; KB:", dict(sorted(sizes.items(), key=lambda x: -x[1])[:15]), "total KB", sum(sizes.values()))


if __name__ == "__main__":
    main()
