"""Build ABBN.SW_events.csv from MFN (Cision/EQS distribution timestamps, Europe/Stockholm == CET/CEST)."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = 'ABBN.SW'
items = json.load(open(os.path.join(RAW_IR, T, 'pages', 'mfn_items.json')))
# de-dup
uniq = {}
for it in items:
    uniq.setdefault((it['date'], it['time'], it['href']), it)
items = sorted(uniq.values(), key=lambda x: (x['date'], x['time']))

RESULTS = {  # fiscal_period -> release date (from ABB IR quarterly table + MFN)
 '2014Q4': '2015-02-05', '2015Q1': '2015-04-29', '2015Q2': '2015-07-23', '2015Q3': '2015-10-21',
 '2015Q4': '2016-02-03', '2016Q1': '2016-04-20', '2016Q2': '2016-07-21', '2016Q3': '2016-10-27',
 '2016Q4': '2017-02-08', '2017Q1': '2017-04-20', '2017Q2': '2017-07-20', '2017Q3': '2017-10-26',
 '2017Q4': '2018-02-08', '2018Q1': '2018-04-19', '2018Q2': '2018-07-19', '2018Q3': '2018-10-25',
 '2018Q4': '2019-02-28', '2019Q1': '2019-04-17', '2019Q2': '2019-07-25', '2019Q3': '2019-10-23',
 '2019Q4': '2020-02-05', '2020Q1': '2020-04-28', '2020Q2': '2020-07-22', '2020Q3': '2020-10-23',
 '2020Q4': '2021-02-04', '2021Q1': '2021-04-27', '2021Q2': '2021-07-22', '2021Q3': '2021-10-21',
 '2021Q4': '2022-02-03', '2022Q1': '2022-04-21', '2022Q2': '2022-07-21', '2022Q3': '2022-10-20',
 '2022Q4': '2023-02-02', '2023Q1': '2023-04-25', '2023Q2': '2023-07-20', '2023Q3': '2023-10-18',
 '2023Q4': '2024-02-01', '2024Q1': '2024-04-18', '2024Q2': '2024-07-18', '2024Q3': '2024-10-17',
 '2024Q4': '2025-01-30', '2025Q1': '2025-04-17', '2025Q2': '2025-07-17', '2025Q3': '2025-10-16',
 '2025Q4': '2026-01-29', '2026Q1': '2026-04-22', '2026Q2': '2026-07-16', '2026Q3': '2026-10-20',
}
NOT_RESULTS = re.compile(r'buyback|återköp|Sverige|kontrakt|contract|joint venture|förvärv|acquisition|'
                         r'names|CFO|Rotork|General Meeting|stämma|Strategy update|appoints|completes', re.I)
# Fallback times from ABB newsroom (DatePublished is UTC 'Z'): not on MFN
NEWSROOM = {'2021-02-04': ('06:45', 'https://new.abb.com/news/detail/73590/q4-and-full-year-2020-results')}

rows = []
for fp, d in RESULTS.items():
    cands = [it for it in items if it['date'] == d and not NOT_RESULTS.search(it['title'])]
    q = int(fp[-1])
    if cands:
        it = cands[0]  # earliest (sorted by time)
        rows.append(dict(event_date=d, event_time_local=it['time'][:5], event_type=f'Q{q}',
                         fiscal_period=fp, source_url='https://www.mfn.se' + it['href']))
    elif d in NEWSROOM:
        tm, url = NEWSROOM[d]
        rows.append(dict(event_date=d, event_time_local=tm, event_type=f'Q{q}', fiscal_period=fp, source_url=url))
    else:
        rows.append(dict(event_date=d, event_time_local='', event_type=f'Q{q}', fiscal_period=fp,
                         source_url='https://global.abb/group/en/investors/quarterly-results'))
        print('NO TIME', fp, d)

def pick(d, rx):
    c = [it for it in items if it['date'] == d and re.search(rx, it['title'], re.I)]
    return c[0] if c else None

EXTRA = [  # (date, title regex, event_type, fiscal_period)
 ('2015-09-09', r'Next Level|transformeringen', 'CMD', ''),
 ('2016-10-04', r'Next stage of unlocking value', 'CMD', ''),
 ('2017-02-22', r'South Korean', 'profit_warning', '2016Q4'),      # ~$100m pre-tax charge vs reported 2016 results
 ('2017-12-20', r'EPC business model', 'profit_warning', '2017Q4'),  # Q4'17 hit ~$150m op. EBITA + $75m
 ('2020-03-30', r'COVID-19 update', 'trading_update', '2020Q1'),
 ('2020-11-19', r'Capital Markets Day 2020', 'CMD', ''),
 ('2021-04-15', r'trading update', 'trading_update', '2021Q1'),
 ('2025-11-18', r'Capital Markets Day 2025', 'CMD', ''),
]
for d, rx, et, fp in EXTRA:
    it = pick(d, rx)
    if not it:
        print('MISSING', d, rx); continue
    rows.append(dict(event_date=d, event_time_local=it['time'][:5], event_type=et, fiscal_period=fp,
                     source_url='https://www.mfn.se' + it['href']))
p = write_events(T, rows)
print(p, len(rows))
