"""Save SAP News Center results press releases (2022Q2+) and relevant ad hoc pages as raw HTML +
text, appending to the SAP download log."""
import sys, os, re, json, shutil, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

T = "SAP.DE"
RAW = os.path.join(fu.RAW_IR, T)
TXT = os.path.join(fu.TXT_IR, T)
LOG = os.path.join(RAW, "download_log.json")
QMAP = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "First": 1, "Second": 2, "Third": 3, "Fourth": 4}

def period_from_title(title):
    m = re.search(r"(Q[1-4]|First|Second|Third|Fourth)(?: Quarter)?(?: and (?:FY|Full-Year|Half-Year|HY))?(?: and Half-Year)? (20\d\d)", title)
    if not m:
        return None
    return "%sQ%d" % (m.group(2), QMAP[m.group(1)])

def main():
    log = json.load(open(LOG))
    have = {r["url"] for r in log}
    posts = json.load(open(os.path.join(RAW, "news_sap_posts.json")))
    for p in posts:
        if not re.match(r"SAP Announces (Q[1-4]|First|Second|Third|Fourth)", p["title"]):
            continue
        per = period_from_title(p["title"])
        if not per or p["link"] in have:
            continue
        h = fu.cached_html(p["link"])
        if not h:
            continue
        slug = p["link"].rstrip("/").split("/")[-1]
        dest = os.path.join(RAW, "news_%s.html" % slug)
        open(dest, "w", encoding="utf-8").write(h)
        txt = fu.html_to_text(h)
        tp = os.path.join(TXT, "%s_press_release.txt" % per)
        open(tp, "w", encoding="utf-8").write(txt)
        log.append({"fiscal_period": per, "doc_type": "press_release", "url": p["link"],
                    "local_path": os.path.relpath(dest, fu.ROOT), "text_path": os.path.relpath(tp, fu.ROOT),
                    "chars": len(txt), "pub_date": p["date_gmt"]})
        print("PR", per, p["date_gmt"])
    # ad hoc pages relevant to results / guidance (2020+)
    ad = json.load(open(os.path.join(RAW, "adhoc_parsed.json")))
    for a in ad:
        if not a.get("eqs_time") or a["url"] in have:
            continue
        if not re.search(r"(Preliminary|Quarter|Forecast|Restructure|Final Results)", a.get("keywords") or ""):
            continue
        d = a["eqs_date"]
        h = fu.cached_html(a["url"])
        slug = a["url"].rstrip("/").split("/")[-1].replace(".html", "")
        dest = os.path.join(RAW, "adhoc_%s_%s.html" % (a["url"].split("/")[-3] + a["url"].split("/")[-2], slug[:12]))
        open(dest, "w", encoding="utf-8").write(h)
        txt = fu.html_to_text(h)
        tp = os.path.join(TXT, "adhoc_%s_%s.txt" % (a["url"].split("/")[-3] + a["url"].split("/")[-2], slug[:12]))
        open(tp, "w", encoding="utf-8").write(txt)
        log.append({"fiscal_period": "", "doc_type": "adhoc", "url": a["url"], "local_path": os.path.relpath(dest, fu.ROOT),
                    "text_path": os.path.relpath(tp, fu.ROOT), "chars": len(txt), "pub_date": d + " " + a["eqs_time"]})
        print("ADHOC", d, a["eqs_time"], a["title"][:60])
    json.dump(log, open(LOG, "w"), indent=1)

if __name__ == "__main__":
    main()
