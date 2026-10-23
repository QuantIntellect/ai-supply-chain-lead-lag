"""Regex KPI extraction from Schneider release texts (2022Q1-2026Q3).
Writes a JSON of candidate values per period for review."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
T = "SU.PA"


def flat(per, kind="release"):
    p = os.path.join(TEXT_IR, T, f"{per}_{kind}.txt")
    if not os.path.exists(p):
        return ""
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"[ \t]*\n[ \t]*", " ", t)
    t = t.replace("’", "'").replace("–", "-").replace("−", "-")
    return re.sub(r"\s{2,}", " ", t)


def first(pat, s, g=1, flags=re.I):
    m = re.search(pat, s, flags)
    return m.group(g) if m else None


out = {}
pers = [f"{y}Q{q}" for y in range(2022, 2027) for q in range(1, 5)][:19]
for per in pers:
    y, q = per[:4], per[-1]
    s = flat(per)
    d = {}
    qn = {"1": "(?:Q1|first quarter)", "2": "(?:Q2|second quarter)", "3": "(?:Q3|third quarter)", "4": "(?:Q4|fourth quarter)"}[q]
    m = re.search(qn + r"[^.€]{0,40}revenues? (?:were|was|of|reached|at|amounted to) (?:of )?€ ?([\d,\.]+) ?(million|billion|bn)[^.]{0,30}?up \+?([\d\.\-]+) ?% organic(?:ally)?(?:[^.]{0,30}?([+-]?[\d\.]+) ?% (?:on a )?reported)?", s, re.I)
    if m:
        v = float(m.group(1).replace(",", ""))
        d["rev"] = v * (1000 if m.group(2).lower() in ("billion", "bn") else 1)
        d["org"] = m.group(3); d["rep"] = m.group(4)
        d["rev_snip"] = s[m.start():m.end()][:200]
    d["em"] = first(r"Energy Management (?:was )?(?:up|grew|growth of|down) ([+-]?[\d\.]+) ?%", s)
    d["ia"] = first(r"Industrial Automation (?:was )?(?:up|grew|growth of|down|declined) ([+-]?[\d\.]+) ?%", s)
    d["systems"] = first(r"Systems \((\d+)% of [^)]*\) (?:grew|were up|was up|declined|were down|was down|decreased) ?([+-]?[\d\.]+)?", s, 0)
    d["ebita"] = first(r"Adj(?:usted|\.)? EBITA[^.]{0,80}?(\d{1,2}\.\d)%", s, 0)
    d["gm"] = first(r"[Gg]ross margin[^.]{0,120}?(\d{2}\.\d)%", s, 0)
    d["backlog"] = [s[max(0, m.start() - 120):m.end() + 160] for m in re.finditer(r"backlog", s, re.I)][:3]
    d["dc"] = [s[max(0, m.start() - 160):m.end() + 200] for m in re.finditer(r"data ?cent(er|re)s?", s, re.I)][:6]
    d["target"] = [s[max(0, m.start() - 60):m.end() + 420] for m in re.finditer(r"(20\d\d|FY\d\d) (?:Target|target|financial target)", s)][:2]
    out[per] = d
json.dump(out, open(os.path.join(RAW_IR, T, "pages", "kpi_candidates.json"), "w"), indent=1, ensure_ascii=False)
for per, d in out.items():
    print(per, d.get("rev"), d.get("org"), d.get("rep"), "| EM", d.get("em"), "IA", d.get("ia"), "| sys", (d.get("systems") or "")[:40], "| ebita", (d.get("ebita") or "")[-30:], "| gm", (d.get("gm") or "")[-20:], "| bl", len(d["backlog"]), "dc", len(d["dc"]))
