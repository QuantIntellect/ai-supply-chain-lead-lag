"""Targeted regex probes per Capgemini press release (print compact evidence for KPI entry)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu
D = os.path.join(fu.TXT_IR, "CAP.PA")

PATS = {
    "table": r"(?:Revenues|in millions of euros\)) ?(?:\d{4} \d{4} )?(?:At current exchange rates )?(?:At constant exchange rates\*? )?(?:Q[1-4]|H1|First half|Full year|2nd quarter|Q2|Q4)[^A-Za-z]{0,40}(?:[A-Za-z ]{0,20}[^A-Za-z]{0,40}){0,3}",
    "book": r"(?:Bookings|bookings) (?:totaled|totalled|reached|amounted to|of)[^.]{0,200}(?:\.\d+)?[^.]{0,60}",
    "b2b": r"book-? ?to-?bill(?: ratio)?(?: for the (?:year|period))?(?: of| at| reached| was| is)? \d\.\d\d",
    "organic": r"organic(?:ally)?\*?(?: growth\*?)?(?: of| was| at)? [+-]?\d+(?:[.,]\d)?%",
    "om": r"[Oo]perating margin\*?(?: rate\*?)?[^.]{0,60}?\d{2}(?:\.\d)?% of revenues|[Oo]perating margin\*?[^.]{0,40}(?:to|at) \d{2}\.\d%",
    "ofcf": r"[Oo]rganic free cash flow\*? (?:of|was|at|stable at)[^.]{0,30}€[\d,.]+ (?:million|billion)",
    "hc": r"headcount stood at [\d,]+",
    "outlook": r"(?:Outlook|OUTLOOK)[^•]{0,40}(?:•[^•]{0,220}){1,3}",
}

def main(periods):
    for p in periods:
        t = re.sub(r"\s+", " ", open(os.path.join(D, "%s_press_release.txt" % p)).read())
        print("=" * 6, p)
        for k, pat in PATS.items():
            ms = [m.group(0) for m in re.finditer(pat, t)]
            if k == "table":
                ms = ms[:3]
            else:
                ms = ms[:2]
            for m in ms:
                print("  %-7s %s" % (k, m[:330]))

if __name__ == "__main__":
    main(sys.argv[1:])
