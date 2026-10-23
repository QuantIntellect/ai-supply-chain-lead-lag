"""Fetch press.siemens.com results event pages; extract release / call times.

Saves each page to data/raw/ir/SIE.DE/pages/press_event_<period>.html and a
summary JSON press_event_times.json.  Usage: sie_press_events.py [period ...]
Optional URL override per period via sys.argv "2019Q4=https://..."
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
from bs4 import BeautifulSoup
T = "SIE.DE"
ORD = {1: "first", 2: "second", 3: "third", 4: "fourth"}
args = sys.argv[1:]
overrides = dict(a.split("=", 1) for a in args if "=" in a)
periods = [a for a in args if "=" not in a] or list(overrides) or \
    [f"{fy}Q{q}" for fy in range(2015, 2027) for q in range(1, 5) if not (fy == 2026 and q == 4)]
f = Fetcher(min_gap=1.0)
outp = os.path.join(RAW_IR, T, "pages", "press_event_times.json")
res = json.load(open(outp)) if os.path.exists(outp) else {}


def parse(t):
    rec = {}
    m = re.search(r"Save the date (\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})", t)
    rec["save_the_date"] = list(m.groups()) if m else None
    m = re.search(r"releas\w+ our [^.]{0,90}?\((\d{1,2}[:.]\d{2})\s*(a\.m\.|p\.m\.)?\s*(CET|CEST)?\)", t)
    rec["release_time"] = list(m.groups()) if m else None
    m = re.search(r"releas\w+ our [^.]{0,120}", t)
    rec["release_sentence"] = m.group(0)[:200] if m else None
    m = re.search(r"Press Conference(?: Call)? \((\d{1,2}[:.]\d{2})", t)
    rec["press_call"] = m.group(1) if m else None
    m = re.search(r"[Ss]tarting (?:today )?at (\d{1,2}[:.]\d{2})\s*(?:a\.m\.)?\s*(?:CET|CEST)?,? the press conference", t)
    if m and not rec["press_call"]:
        rec["press_call"] = m.group(1)
    return rec


for p in periods:
    if p in res and res[p].get("status") == 200 and p not in overrides:
        continue
    fy, q = int(p[:4]), int(p[-1])
    url = overrides.get(p) or f"https://press.siemens.com/global/en/event/{ORD[q]}-quarter-results-fy-{fy}"
    r = f.get(url)
    rec = {"url": url, "status": r.status_code}
    if r.status_code == 200:
        hp = os.path.join(RAW_IR, T, "pages", f"press_event_{p}.html")
        open(hp, "wb").write(r.content)
        t = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" "))
        rec.update(parse(t))
    res[p] = rec
    print(p, rec["status"], rec.get("save_the_date"), rec.get("release_time"), rec.get("press_call"))
json.dump(res, open(outp, "w"), indent=1)
