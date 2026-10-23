"""NKT release calendar 2015-2026 from investors.nkt.com announcement stamps (local Copenhagen time),
cross-checked against GlobeNewswire (ET -> Europe/Copenhagen) where available (to Sep 2025)."""
import sys, re, os
from datetime import datetime
sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib

T = "NKT.CO"
ir = irlib.read_csv("data/raw/ir/NKT.CO/ir_announcements_list.csv")
gnw = []
for r in irlib.read_csv("data/raw/ir/NKT.CO/globenewswire_list.csv"):
    if not r["listed"]:
        continue
    d = datetime.strptime(r["listed"].replace(" ET", ""), "%B %d, %Y %H:%M")
    ld, lt = irlib.to_local(d.strftime("%Y-%m-%d %H:%M"), "America/New_York", T)
    gnw.append((ld, lt, r["title"], r["url"]))

AD_HOC = {  # title regex -> (event_type, fiscal_period)
    r"Capital Markets Day 2015 focused": ("CMD", "FY2015"),
    r"Updated 2017 outlook for NKT Cables": ("trading_update", "FY2017"),
    r"Q1 2020 trading statement": ("profit_warning", "FY2020"),  # NKT Photonics 2020 outlook withdrawn
    r"Financial outlook 2020 reinstated": ("trading_update", "FY2020"),
    r"updates 2021 financial outlook and resumes": ("prelim", "FY2021Q2"),
    r"updates 2021 financial outlook and announces preliminary Q3": ("prelim", "FY2021Q3"),
    r"preliminary Q1 2023": ("prelim", "FY2023Q1"),
    r"NKT updates financial outlook for 2023": ("trading_update", "FY2023"),
    r"preliminary Q3 2023": ("prelim", "FY2023Q3"),
    r"preliminary Q2 2024": ("prelim", "FY2024Q2"),
    r"NKT updates financial outlook for 2025": ("trading_update", "FY2025"),
    r"NKT updates financial outlook for 2026": ("trading_update", "FY2026"),
    r"capital allocation priorities at Investor Day": ("CMD", "FY2026"),
    r"launches new strategy with updated medium-term ambition": ("CMD", "FY2022"),
    r"upgrades medium-term financial ambitions": ("trading_update", "FY2023"),
    r"NKT updates medium-term financial ambitions": ("CMD", "FY2024"),
    r"launches new strategy, medium-term financial ambitions for 2030": ("CMD", "FY2025"),
}
MON = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                   "September", "October", "November", "December"], 1)}


def results_type(title, year):
    t = title
    if re.search(r"Annual Report (20\d\d)|(20\d\d) Annual Report", t):
        fy = re.search(r"(20\d\d)", t.split("Annual Report")[1] if re.search(r"Annual Report 20\d\d", t) else t).group(1)
        return "FY", f"FY{fy}"
    m = re.search(r"\b(Q[1-3]|H1)(?:[ -]Q3)? (20\d\d)|Interim Report (Q1-Q3|Q[1-3]|H1) (20\d\d)", t)
    if m:
        q = m.group(1) or m.group(3); y = m.group(2) or m.group(4)
        if q == "Q1-Q3":
            q = "Q3"
        return q, f"FY{y}{q}"
    m = re.search(r"NKT (Q[1-3]) (20\d\d)", t)
    if m:
        return m.group(1), f"FY{m.group(2)}{m.group(1)}"
    return None, None


out, notes = [], []
for r in ir:
    title = re.sub(r"^report ", "", r["title"])
    mo, dd = r["date"].split()
    date = f"{int(r['year']):04d}-{MON[mo]:02d}-{int(dd):02d}"
    et = fp = None
    if r["category"].startswith("Financial"):
        et, fp = results_type(title, r["year"])
        if et is None:
            notes.append(("unparsed", date, title[:60])); continue
    else:
        for pat, (e, f) in AD_HOC.items():
            if re.search(pat, title, re.I):
                et, fp = e, f
                break
        if et is None:
            continue
    # GNW cross-check (same local date, overlapping title words)
    key = re.sub(r"[^a-z0-9 ]", "", title.lower())[:25]
    g = [x for x in gnw if x[0] == date and (re.sub(r"[^a-z0-9 ]", "", x[2].lower())[:12] == key[:12] or re.search(r"(Q[1-3]|Annual Report|outlook|preliminary|Capital Markets)", x[2]) and re.search(r"(Q[1-3]|Annual Report|outlook|preliminary|Capital Markets)", title))]
    if g and abs(int(g[0][1][:2]) * 60 + int(g[0][1][3:]) - (int(r["time"][:2]) * 60 + int(r["time"][3:]))) > 2:
        notes.append(("time mismatch", date, r["time"], g[0][1], title[:40]))
    if not g and date < "2025-09-01":
        notes.append(("no gnw match", date, r["time"], title[:50]))
    out.append({"event_date": date, "event_time_local": r["time"], "event_type": et, "fiscal_period": fp, "source_url": r["url"]})

# CMD 2017-09-19: announced 2017-08-17 (no same-day announcement in the IR list) -> time unknown
cmd17 = [r for r in ir if "Capital Markets Day on 19 september 2017" in r["title"]]
out.append({"event_date": "2017-09-19", "event_time_local": "", "timing": "UNKNOWN", "event_type": "CMD", "fiscal_period": "FY2017",
            "source_url": cmd17[0]["url"] if cmd17 else "https://investors.nkt.com/company-announcements/"})
irlib.write_events(T, out)
for n in notes:
    print("  ", n)
