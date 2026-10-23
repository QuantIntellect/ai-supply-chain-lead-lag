"""Print compact KPI-relevant snippets from Capgemini press-release texts (for manual KPI entry)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

D = os.path.join(fu.TXT_IR, "CAP.PA")

def norm(s):
    return re.sub(r"\s+", " ", s)

def main(periods):
    for p in periods:
        fn = os.path.join(D, "%s_press_release.txt" % p)
        if not os.path.exists(fn):
            print("== MISSING", p); continue
        t = norm(open(fn).read())
        print("=" * 10, p)
        i = t.find("Paris, ")
        head = t[:i]
        j = head.find("vincent.biraud@capgemini.com")
        if j < 0:
            j = max(head.find("@capgemini.com"), 0)
        print("HEAD:", head[j:][:900])
        print("LEAD:", t[i:i + 420])
        for pat in [r"[^.]{0,200}(?:generative|Gen ?AI|agentic)[^.]{0,250}bookings[^.]{0,150}\.",
                    r"[^.]{0,120}bookings[^.]{0,200}(?:generative|Gen ?AI|agentic)[^.]{0,200}\.",
                    r"(?:OUTLOOK|Outlook)[^.]{0,30}\.? [^§]{0,700}",
                    r"[Hh]eadcount[^.]{0,160}\.",
                    r"[Oo]perating margin[^.]{0,30}(?:was|of|stood at|totaled|reached)[^.]{0,160}\.",
                    r"[Oo]rganic free cash flow[^.]{0,30}(?:was|of|totaled|reached|amounted)[^.]{0,120}\.",
                    r"[Oo]rganic growth[^.]{0,200}\."]:
            for m in list(re.finditer(pat, t))[:2]:
                print("  >", m.group(0)[:700])

if __name__ == "__main__":
    main(sys.argv[1:])
