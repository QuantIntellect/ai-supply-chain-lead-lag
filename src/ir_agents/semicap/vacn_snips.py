"""Print compact KPI snippets from VAT release texts.
Usage: vacn_snips.py <period_doctype> [head_chars] [table_chars]"""
import os
import re
import sys

D = "/Users/sinamirzaei/Documents/aimapping/data/processed/ir_text/VACN.SW"


def hits(t, pat, n, w=130):
    out, last = [], -10**9
    for m in re.finditer(pat, t, re.I):
        if m.start() - last < 250:
            continue
        last = m.start()
        out.append(t[max(0, m.start() - w):m.end() + w])
        if len(out) >= n:
            break
    return out


def main():
    key = sys.argv[1]
    head = int(sys.argv[2]) if len(sys.argv) > 2 else 900
    tab = int(sys.argv[3]) if len(sys.argv) > 3 else 650
    t = " ".join(open(os.path.join(D, key + ".txt"), errors="ignore").read().split())
    t = re.sub(r"Forward-looking statement.*$", "", t, flags=re.I | re.S)
    print("=== %s (%d chars)" % (key, len(t)))
    print("HEAD:", t[:head])
    m = re.search(r"in CHF million", t)
    if m:
        print("TABLE:", t[m.start():m.start() + tab])
    for h in hits(t, r"backlog", 2):
        print(" BL:", h)
    for h in hits(t, r"gross (?:profit )?margin", 1):
        print(" GM:", h)
    for h in hits(t, r"(?:expects?|guidance|anticipates?)[^.]{0,160}CHF ?\d", 3, 180):
        print(" GUID:", h)
    for h in hits(t, r"\bAI\b|artificial intelligence|China|Chinese|\bGAA\b|gate-all-around|HBM|DRAM|advanced logic|"
                     r"leading[- ]edge|tariff|push[- ]?out", int(os.environ.get("NAI", "4")), 150):
        print(" AI:", h)


if __name__ == "__main__":
    main()
