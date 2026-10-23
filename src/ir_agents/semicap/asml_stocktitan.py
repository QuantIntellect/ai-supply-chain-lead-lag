"""Harvest StockTitan ASML news list (JSON-LD headline + datePublished UTC) -> CSV with Amsterdam local time."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
T = 'ASML.AS'
d = irlib.ensure(os.path.join(irlib.raw_dir(T), 'stocktitan'))
rows = []
for p in range(1, 27):
    u = 'https://www.stocktitan.net/news/ASML/' + ('' if p == 1 else f'page-{p}.html')
    st, b = irlib.fetch(u, os.path.join(d, f'news_p{p}.html'), timeout=60)
    h = b.decode('utf8', 'ignore')
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            j = json.loads(m.group(1))
        except Exception:
            continue
        graph = j.get('@graph', [j]) if isinstance(j, dict) else j
        for g in graph:
            for part in (g.get('hasPart') or []) if isinstance(g, dict) else []:
                if part.get('@type') == 'NewsArticle':
                    rows.append({'headline': part.get('headline'), 'url': part.get('url'), 'utc': part.get('datePublished')})
df = pd.DataFrame(rows).drop_duplicates('url')
ts = pd.to_datetime(df.utc, utc=True)
df['local'] = ts.dt.tz_convert('Europe/Amsterdam').dt.strftime('%Y-%m-%d %H:%M')
df = df.sort_values('utc')
df.to_csv(os.path.join(d, '_stocktitan_asml.csv'), index=False)
print(len(df), df.local.min(), df.local.max())
pat = r'quarter|Q[1-4]|results|net sales|Investor Day|statement|export|outlook|update|early'
x = df[df.headline.str.contains(pat, case=False, regex=True) & ~df.headline.str.contains('buyback|transactions', case=False)]
for _, r in x.iterrows():
    print(r.local, '|', r.headline[:110])
