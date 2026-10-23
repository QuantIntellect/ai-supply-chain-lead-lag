"""Classify downloaded VAT docs into (fiscal_period, doctype), extract text, write manifest.
Text -> data/processed/ir_text/VACN.SW/<period>_<doctype>.txt ; manifest -> data/processed/ir/VACN.SW_manifest.csv"""
import os
import sys
import re
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import raw_dir, to_text, write_text, write_manifest, html_to_text
from bs4 import BeautifulSoup

T = "VACN.SW"
R = raw_dir(T)

# manifest doc_type and text-file doctype
RULES = [
    # (regex on title+url, period builder, text doctype, manifest doc_type)
    (r"capital[ _-]markets[ _-]day[ _-]?(20\d\d)[ _-]presentation|(20\d\d)[ _-]capital[ _-]markets[ _-]day[ _-]presentation|cmd[_-](20\d\d)",
     "CMD{y}", "cmd_presentation", "presentation"),
    (r"capital[ _-]markets[ _-]day[ _-]?(20\d\d)", "CMD{y}", "cmd_release", "press_release"),
    (r"investor[ _-]deck.*?(20\d\d)", "{y}DECK", "investor_deck", "presentation"),
    (r"q1[ _-](20\d\d)[ _-]sales[ _-]expectations|sales expectations", "{y}Q1", "adhoc_release", "press_release"),
    (r"ahead[ _-]of[ _-]q3[ _-](20\d\d)", "{y}Q3", "adhoc_release", "press_release"),
    (r"q4[ _-]and[ _-]fy[ _-](20\d\d)[ _-]prelim|q4[ _-](20\d\d)[ _-]prelim", "{y}Q4", "prelim_release", "press_release"),
    (r"(20\d\d)[ _-]sales$|media release - (20\d\d) sales", "{y}Q4", "prelim_release", "press_release"),
    (r"q2[ _-]and[ _-]hy[ _-](20\d\d)[ _-]prelim|q2[ _-](20\d\d)[ _-]trading[ _-]update|sales[ _-]half[ _-]year[ _-](20\d\d)",
     "{y}Q2", "prelim_release", "press_release"),
    (r"(?:q2[ _-]and[ _-])?half[ _-]?year[ _-](20\d\d)[ _-]?(?:results[ _-]+)?presentation|half[ _-]year[ _-](20\d\d)[ _-]results[ _-]+presentation|q2[ _-]half[ _-]year[ _-](20\d\d)[ _-]presentation|half[ _-]year[ _-]presentation[ _-](20\d\d)|half[_-]year[_-](20\d\d)[_-]results[_-]presentation",
     "{y}H1", "presentation", "presentation"),
    (r"half[ _-]?year[ _-]?(20\d\d)[ _-]?report|half[ _-]year[ _-]report[ _-](20\d\d)|half_year_(20\d\d)_report", "{y}H1",
     "interim_report", "interim_report"),
    (r"half[ _-]?year[ _-]?(?:results[ _-]+)?(20\d\d)|h1[ _-](20\d\d)|halbjahresabschluss[ _-](20\d\d)|half[ _-]year[ _-](20\d\d)",
     "{y}H1", "press_release", "press_release"),
    (r"(?:full[ _-]?year|fy)[ _-](20\d\d)[ _-]+(?:results[ _-]+)?presentation|presentation[ _-]on[ _-]full[ _-]year[ _-](20\d\d)|full[ _-]year[ _-](20\d\d)[ _-]+presentation|full_year_(20\d\d)_presentation",
     "{y}FY", "presentation", "presentation"),
    (r"annual[ _-]report[ _-]?(20\d\d)|annual_report_(20\d\d)", "{y}FY", "annual_report", "annual_report"),
    (r"full[ _-]?year[ _-]?(?:results[ _-]+)?(20\d\d)|jahresabschluss[ _-](20\d\d)", "{y}FY", "press_release", "press_release"),
    (r"q([13])[ _-](20\d\d)[ _-]+(?:trading[ _-]update|results)[ _-]+presentation|presentation[ _-]on[ _-]q([13])[ _-](20\d\d)",
     "{y}Q{q}", "presentation", "presentation"),
    (r"q([13])[ _-](20\d\d)[ _-]+(?:trading[ _-]update|results)|lagebericht[ _-]q([13])[ _-](20\d\d)", "{y}Q{q}", "press_release",
     "press_release"),
]


def classify(title, url):
    s = (title + " | " + url.split("/")[-1]).lower().replace("%20", " ")
    for pat, per, dt, mt in RULES:
        m = re.search(pat, s)
        if m:
            g = [x for x in m.groups() if x]
            if "{q}" in per:
                q, y = g[0], g[1]
                return per.format(y=y, q=q), dt, mt
            y = next((x for x in g if len(x) == 4), "")
            return per.format(y=y), dt, mt
    return None, None, None


def news_article_text(path):
    b = open(path, "rb").read()
    soup = BeautifulSoup(b, "html.parser")
    m = soup.find("section", class_="page-basic__content")
    if not m:
        return html_to_text(b)
    for t in m(["script", "style"]):
        t.decompose()
    return re.sub(r"\n\s*\n+", "\n\n", m.get_text("\n")).strip()


EVT_DOCTYPE = {"H1": "press_release", "FY": "press_release", "trading_update": "press_release",
               "prelim": "prelim_release", "profit_warning": "adhoc_release", "CMD": "cmd_release"}


def quarter_of(date):
    return f"{date[:4]}Q{(int(date[5:7]) - 1) // 3 + 1}"


def main():
    docs = json.load(open(os.path.join(R, "docs_list.json")))
    events = json.load(open(os.path.join(R, "events_detail.json")))
    ev_by_url = {e["source_url"]: e for e in events}
    # (period, kind) -> event date, for docs that are not themselves event sources (reports, presentations)
    ev_by_period = {}
    for e in events:
        fp = e["fiscal_period"] or ("CMD" + e["event_date"][:4])
        ev_by_period.setdefault(fp, e["event_date"])
    rows, chosen = [], {}
    for d in docs:
        if not d.get("local_path"):
            continue
        e = ev_by_url.get(d["url"])
        if e:
            per = e["fiscal_period"] or ("CMD" + e["event_date"][:4])
            dt = EVT_DOCTYPE[e["event_type"]]
            if "short time" in e.get("title", "").lower():
                dt = "stw_release"
            mt = "press_release"
            d["pub_date"] = e["event_date"]
        else:
            per, dt, mt = classify(d["title"], d["url"])
            if per:
                d["pub_date"] = d.get("news_date") or ev_by_period.get(per, "")
        if not per:
            per, dt, mt = (quarter_of(d["news_date"]) if d.get("news_date") else ""), "other", "other"
            d["pub_date"] = d.get("news_date", "")
        d["period"], d["doctype"], d["mtype"] = per, dt, mt
        if dt == "other" or not per:
            continue
        key = (per, dt)
        prio = 0 if d["local_path"].lower().endswith(".pdf") else 1
        chosen.setdefault(key, []).append((prio, d))
    for (per, dt), cands in sorted(chosen.items()):
        best = ""
        for prio, d in sorted(cands, key=lambda x: x[0]):
            p = d["local_path"]
            try:
                txt = news_article_text(p) if p.endswith(".html") else to_text(p)
            except Exception as ex:
                print("EXTRACT-ERR", p, ex)
                continue
            if len(txt.strip()) > len(best.strip()):
                best, src = txt, d
            if len(txt.strip()) >= 1500:  # PDFs with no text layer fall back to the HTML article
                break
        if best:
            src["text_path"] = write_text(T, per, dt, best)
    json.dump(docs, open(os.path.join(R, "docs_classified.json"), "w"), indent=1)
    for d in docs:
        if not d.get("local_path"):
            continue
        rows.append({"ticker": T, "local_path": os.path.relpath(d["local_path"], "/Users/sinamirzaei/Documents/aimapping"),
                     "url": d["url"], "doc_type": d["mtype"],
                     "fiscal_period": "" if re.match(r"CMD|\d{4}DECK", d["period"] or "") else d["period"],
                     "pub_date": d.get("pub_date", "")})
    write_manifest(T, rows)
    print("manifest rows", len(rows), "texts", len(chosen),
          "other", sum(1 for d in docs if d.get("doctype") == "other"))
    for d in docs:
        if d.get("local_path") and not d.get("pub_date"):
            print("  NO-PUBDATE", d["period"], d["doctype"], d["url"].split("/")[-1][:70])


if __name__ == "__main__":
    main()
