"""Fetch all Nokia exchange notices 2015-01..2026-10 from the Nasdaq Nordic news API (exact release times).
Saves raw JSON pages to data/raw/ir/NOKIA.HE/nasdaq_news/ and a flat CSV to the same dir."""
import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib  # noqa: E402

T = "NOKIA.HE"
out = irlib.ensure(os.path.join(irlib.raw_dir(T), "nasdaq_news"))
base = ("https://api.news.eu.nasdaq.com/news/query.action?type=json&showAttachments=true&showCnsSpecific=true"
        "&showCompany=true&countResults=true&freeText=&company=Nokia&market=&cnscategory="
        "&fromDate=2015-01-01&toDate=2026-10-23&globalGroup=exchangeNotice&globalName=NordicAllMarkets"
        "&displayLanguage=en&language=en&timeZone=EET&dateMask=yyyy-MM-dd+HH%3Amm%3Ass&limit=200"
        "&start={s}&dir=DESC")
items = []
s = 0
while True:
    st, t, _ = irlib.fetch(base.format(s=s), cache_dir=out)
    j = json.loads(t)
    it = j["results"]["item"]
    items += it
    print(s, len(it), j.get("count"))
    if len(it) < 200:
        break
    s += 200
rows = []
for it in items:
    att = it.get("attachment") or []
    if isinstance(att, dict):
        att = [att]
    rows.append({
        "releaseTime": it.get("releaseTime"), "published": it.get("published"),
        "company": it.get("company"), "headline": it.get("headline"),
        "category": it.get("cnsCategory"), "language": it.get("language"),
        "messageUrl": it.get("messageUrl"), "disclosureId": it.get("disclosureId"),
        "attachments": json.dumps([{"name": a.get("fileName"), "url": a.get("attachmentUrl")} for a in att]),
    })
df = pd.DataFrame(rows)
df.to_csv(os.path.join(out, "nokia_notices.csv"), index=False)
print(df.shape, df.releaseTime.min(), df.releaseTime.max())
print(df.category.value_counts().head(30).to_string())
