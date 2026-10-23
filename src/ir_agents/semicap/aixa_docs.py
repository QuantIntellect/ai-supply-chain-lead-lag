"""Download Aixtron docs (results presentations, interim/annual reports, call transcripts/speeches) + press releases
-> data/raw/ir/AIXA.DE/docs/, text -> data/processed/ir_text/AIXA.DE/<period>_<doctype>.txt, manifest CSV."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

T = "AIXA.DE"
RAW = irlib.raw_dir(T)
DOCS = irlib.ensure(os.path.join(RAW, "docs"))


def period_from(name, text=""):
    s = unquote(name).replace("_", " ") + " " + text
    B, E = r"(?<![A-Za-z0-9])", r"(?!\d)"
    m = re.search(B + r"(Q[1-4])[-/ ]?(20\d\d)" + E, s, re.I)
    if m:
        return f"{m.group(2)}{m.group(1).upper()}"
    m = re.search(B + r"FY[-/ ]?(20\d\d)" + E, s, re.I)
    if m:
        return f"{m.group(1)}Q4"
    m = re.search(B + r"H1[-/ ]?(20\d\d)" + E, s, re.I)
    if m:
        return f"{m.group(1)}Q2"
    return ""


def report_period(url):
    u = unquote(url)
    y = re.search(r"/(20\d\d)/", u).group(1)
    f = u.rsplit("/", 1)[1]
    yy = re.search(r"(20\d\d)", f)
    y = yy.group(1) if yy else y
    if re.search(r"3-Months", f): return f"{y}Q1", "interim_report"
    if re.search(r"6-Months|Half-Year", f): return f"{y}Q2", "interim_report"
    if re.search(r"9-Months", f): return f"{y}Q3", "interim_report"
    if re.search(r"Annual", f): return f"{y}FY", "annual_report"
    return "", ""


def main():
    ev = pd.read_csv(os.path.join(irlib.PROC_IR, f"{T}_events.csv"), dtype=str).fillna("")
    reg = ev[ev.event_type.isin(["Q1", "Q2", "Q3", "Q4"])].set_index("fiscal_period").event_date.to_dict()
    targets = []  # (url, period, doctype, pubdate)
    soup = BeautifulSoup(open(os.path.join(RAW, "listing", "publications.html"), "rb").read(), "html.parser")
    for a in soup.find_all("a", href=True):
        u = urljoin("https://www.aixtron.com/en/investors/publications", a["href"])
        if not u.lower().endswith(".pdf"):
            continue
        if "ir-praesentationen" in u:
            p = period_from(u.rsplit("/", 1)[1])
            if p and p >= "2022Q1":
                targets.append((u, p, "presentation", reg.get(p, "")))
        elif re.search(r"/publikationen/20(2[2-6])/(en|englisch)/", u) and "Sustainability" not in u:
            p, dt = report_period(u)
            if p:
                targets.append((u, p, dt, reg.get(p.replace("FY", "Q4"), "")))
    # call transcripts / speeches (company-published) - archive + active pages
    for page, tag in [("https://www.aixtron.com/en/investors/events/conference-calls/archive", "cc_archive"),
                      ("https://www.aixtron.com/en/investors/events/conference-calls", "cc_active")]:
        st, b = irlib.fetch(page, os.path.join(RAW, "listing", f"{tag}.html"))
        s2 = BeautifulSoup(b, "html.parser")
        for a in s2.find_all("a", href=True):
            u = urljoin(page, a["href"])
            if not u.lower().endswith(".pdf") or "telefonkonferenz" not in u:
                continue
            txt = " ".join(a.get_text(" ", strip=True).split())
            f = unquote(u.rsplit("/", 1)[1])
            p = period_from(f, txt) or period_from(txt)
            if not p:
                m = re.search(r"(\d{2})(\d{2})(\d{2})[ _.]", f)
                print("no period", f, txt); continue
            targets.append((u, p, "transcript", reg.get(p, "")))
    targets = list(dict.fromkeys(targets))
    man, seen = [], set()
    for u, p, dt, pub in targets:
        key = (p, dt)
        suffix = "" if key not in seen else "_2"
        seen.add(key)
        fn = f"{p}_{dt}{suffix}__" + re.sub(r"[^A-Za-z0-9._-]+", "_", unquote(u.rsplit('/', 1)[1]))
        path = os.path.join(DOCS, fn)
        st, b = irlib.fetch(u, path, timeout=120)
        if st != 200:
            print("ERR", st, u); continue
        try:
            txt = irlib.to_text(path)
        except Exception as e:
            print("TEXT-ERR", fn, e); continue
        irlib.write_text(T, p, dt + suffix, txt)
        man.append({"ticker": T, "local_path": path, "url": u, "doc_type": dt, "fiscal_period": p, "pub_date": pub})
    # press releases (HTML pages already fetched) for 2022Q1+ results and ad-hoc/prelim releases
    ts = pd.read_csv(os.path.join(RAW, "news_timestamps.csv"), dtype=str).fillna("")
    for _, e in ev[ev.event_date >= "2022-01-01"].iterrows():
        if e.fiscal_period < "2022Q1":
            continue
        c = ts[(ts.list_date == e.event_date)]
        if len(c):
            r = c.sort_values("src").iloc[0]  # 'adhoc' < 'finance' < 'press'
            path, url = r.local_path, r.url
        else:
            fs = [f for f in os.listdir(os.path.join(RAW, "news")) if f.startswith(e.event_date)]
            path, url = os.path.join(RAW, "news", fs[0]), e.source_url
        t = irlib.html_to_text(open(path, "rb").read())
        i = t.find("Herzogenrath")
        j = min([k for k in [t.find("EQS News ID"), t.find("End of Announcement"), t.find("End of Inside Information"),
                             t.find("Our registered trademarks")] if k > i] or [len(t)])
        body = t[max(0, i - 800):j]
        dtp = "press_release" if e.event_type in ("Q1", "Q2", "Q3", "Q4") else "adhoc_press_release"
        irlib.write_text(T, e.fiscal_period, dtp, body)
        man.append({"ticker": T, "local_path": path, "url": url, "doc_type": "press_release",
                    "fiscal_period": e.fiscal_period, "pub_date": e.event_date})
    df = irlib.write_manifest(T, man)
    print(len(df), df.doc_type.value_counts().to_dict())


if __name__ == "__main__":
    main()
