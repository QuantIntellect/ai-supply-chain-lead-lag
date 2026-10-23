"""Write ASML.AS outputs: events, KPIs, manifest (notes.md is written separately by hand-curated text below)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd

T = 'ASML.AS'
R = irlib.raw_dir(T)
EDGAR = 'https://www.sec.gov/Archives/edgar/data/937966/'
WB = 'https://web.archive.org/web/'
FR = 'https://www.asml.com/en/investors/financial-results/'

RES_DATES = ['2015-01-21', '2015-04-15', '2015-07-15', '2015-10-14', '2016-01-20', '2016-04-20', '2016-07-20',
             '2016-10-19', '2017-01-18', '2017-04-19', '2017-07-19', '2017-10-18', '2018-01-17', '2018-04-18',
             '2018-07-18', '2018-10-17', '2019-01-23', '2019-04-17', '2019-07-17', '2019-10-16', '2020-01-22',
             '2020-04-15', '2020-07-15', '2020-10-14', '2021-01-20', '2021-04-21', '2021-07-21', '2021-10-20',
             '2022-01-19', '2022-04-20', '2022-07-20', '2022-10-19', '2023-01-25', '2023-04-19', '2023-07-19',
             '2023-10-18', '2024-01-24', '2024-04-17', '2024-07-17', '2024-10-15', '2025-01-29', '2025-04-16',
             '2025-07-16', '2025-10-15', '2026-01-28', '2026-04-15', '2026-07-15', '2026-10-14']


def period_of(d):
    y, m = int(d[:4]), int(d[5:7])
    return f'{y-1}Q4' if m <= 2 else f'{y}Q{(m - 1) // 3}'


# Documented publication-time evidence (ASML's own pre-announcement text: "available ... at 07:00 CET" /
# "distributed via GlobeNewswire at 07:00"), archived quarter pages or the 6-K announcement-date exhibit.
DOC = {
    '2015Q4': EDGAR + '000119312516423594/d110189dex991.htm',
    '2019Q3': WB + '20191014103354/https://www.asml.com/en/investors/financial-results/q3-2019',
    '2021Q1': WB + '20210413215019/https://www.asml.com/en/investors/financial-results/q1-2021',
    '2021Q2': WB + '20210721022713/https://www.asml.com/en/investors/financial-results/q2-2021',
    '2021Q4': WB + '20220108064535/https://www.asml.com/en/investors/financial-results/q4-2021',
    '2022Q2': WB + '20220715124634/https://www.asml.com/en/investors/financial-results/q2-2022',
    '2022Q4': WB + '20230113142101/https://www.asml.com/en/investors/financial-results/q4-2022',
    '2023Q1': WB + '20230406135613/https://www.asml.com/en/investors/financial-results/q1-2023',
    '2023Q2': WB + '20230711200033/https://www.asml.com/en/investors/financial-results/q2-2023',
    '2023Q4': WB + '20240120032634/https://www.asml.com/en/investors/financial-results/q4-2023',
    '2024Q4': WB + '20250116115740/https://www.asml.com/en/investors/financial-results/q4-2024',
    '2025Q1': WB + '20250404203306/https://www.asml.com/en/investors/financial-results/q1-2025',
    '2025Q2': WB + '20250702112858/https://www.asml.com/en/investors/financial-results/q2-2025',
    '2025Q3': WB + '20251003000622/https://www.asml.com/en/investors/financial-results/q3-2025',
    '2025Q4': WB + '20260115111224/https://www.asml.com/en/investors/financial-results/q4-2025',
    '2026Q1': WB + '20260409014330/https://www.asml.com/en/investors/financial-results/q1-2026',
    '2026Q2': WB + '20260702202323/https://www.asml.com/en/investors/financial-results/q2-2026',
}

# StockTitan (GlobeNewswire wire copy) timestamps, if harvested
st_path = os.path.join(R, 'stocktitan', '_stocktitan_asml.csv')
ST = pd.read_csv(st_path) if os.path.exists(st_path) else pd.DataFrame(columns=['headline', 'url', 'utc', 'local'])
ST['date'] = ST.local.str[:10]
ST['hhmm'] = ST.local.str[11:16]


def st_lookup(date, pat):
    x = ST[(ST.date == date) & ST.headline.str.contains(pat, case=False, regex=True)]
    if len(x):
        r = x.sort_values('utc').iloc[0]
        return r.hhmm, r.url
    return None, None


idx = json.load(open(os.path.join(R, 'edgar_q', '_index.json')))
filing_index = {e['period']: e['filing_index'] for e in idx}
basis = {}
events = []
for d in RES_DATES:
    per = period_of(d)
    q = per[4:]
    src = filing_index.get(per, '')
    if per == '2024Q3':
        hh, su = st_lookup(d, r'Q3 2024|third.quarter')
        events.append({'ticker': T, 'event_date': d, 'event_time_local': '', 'timing': 'INTRADAY', 'event_type': q,
                       'fiscal_period': per,
                       'source_url': 'https://www.asml.com/en/news/press-releases/2024/statement-relating-to-early-publication-of-our-q3-2024-results'})
        basis[per] = 'accidental early publication on 2024-10-15 during Euronext trading (scheduled 2024-10-16 07:00); exact minute not documented; shares reacted shortly before 16:30 CEST' + (f'; wire copy timestamp {hh}' if hh else '')
        continue
    hh, su = st_lookup(d, r'net sales|net income|results')
    if per in DOC:
        b, srcu = 'documented (ASML pre-announcement: 07:00 local)', DOC[per]
        if hh:
            b += f'; wire copy {hh}'
    elif hh:
        b, srcu = f'wire copy timestamp {hh} (StockTitan/GlobeNewswire)', su
    else:
        b, srcu = 'convention 07:00 (verified on 17 documented releases 2016-2026, no regular-release exception)', src
    tm = hh if (hh and per not in DOC) else '07:00'
    basis[per] = b
    events.append({'ticker': T, 'event_date': d, 'event_time_local': tm, 'event_type': q, 'fiscal_period': per,
                   'source_url': srcu})

SPECIAL = [
    # date, type, fiscal_period, source, stocktitan pattern
    ('2016-10-31', 'CMD', '', EDGAR + '000134100416001720/ex99-2.htm', None),
    ('2018-11-08', 'CMD', '', EDGAR + '000119312518321882/', None),
    ('2018-12-03', 'trading_update', '2019Q1', EDGAR + '000119312518340472/d664597dex991.htm', None),
    ('2020-03-30', 'profit_warning', '2020Q1', EDGAR + '000119312520089921/d912704dex991.htm', None),
    ('2021-09-29', 'CMD', '', EDGAR + '000119312521285965/d234184dex991.htm', r'Investor Day'),
    ('2022-01-03', 'trading_update', '2022FY', 'https://www.asml.com/en/news/press-releases/2022/fire-incident-at-asml-berlin', r'^Fire incident'),
    ('2022-01-07', 'trading_update', '2022FY', EDGAR + '000119312522004166/d287041dex992.htm', r'fire'),
    ('2022-11-10', 'CMD', '', EDGAR + '000119312522282132/', None),
    ('2023-01-28', 'trading_update', '2023FY', 'https://www.asml.com/en/news/press-releases/2023/statement', r'^Statement'),
    ('2023-03-08', 'trading_update', '2023FY', 'https://www.asml.com/en/news/press-releases/2023/statement-regarding-additional-export-controls', r'export'),
    ('2023-06-30', 'trading_update', '2023FY', 'https://www.asml.com/en/news/press-releases/2023/statement-regarding-export-control-regulations-dutch-government', r'export'),
    ('2023-10-17', 'trading_update', '2023FY', 'https://www.asml.com/en/news/press-releases/2023/statement-regarding-us-governments-export-control-regulations-announcement', r'export'),
    ('2024-01-01', 'trading_update', '2023FY', 'https://www.asml.com/en/news/press-releases/2023/statement-regarding-partial-revocation-export-license', r'export|revocation'),
    ('2024-09-06', 'trading_update', '2024FY', 'https://www.asml.com/en/news/press-releases/2024/dutch-governments-updated-export-license-requirement', r'export'),
    ('2024-11-14', 'CMD', '', EDGAR + '000093796624000024/', r'Investor Day'),
    ('2024-12-02', 'trading_update', '2025FY', 'https://www.asml.com/en/news/press-releases/2024/asml-expects-impact-of-updated-export-restrictions-to-fall-within-outlook-for-2025', r'export'),
]
# 2024 Investor Day: StockTitan article page shows "11/14/2024 - 01:00 AM EST" (= 07:00 CET), harvested 2026-10-23
MANUAL_TIMES = {
    '2024-11-14': ('07:00', 'https://www.stocktitan.net/news/ASML/asml-provides-updated-view-on-market-opportunities-at-2024-investor-e8gkcnq7uv3t.html')}
# 2022-11-10 CMD release: public on EDGAR by 16:20 CET (6-K header 10:20:28 ET), wire copy 17:24 CET -> INTRADAY, time not exact
TIMING_OVERRIDE = {'2022-11-10': 'INTRADAY'}
for d, typ, fp, src, pat in SPECIAL:
    hh, su = (st_lookup(d, pat) if pat else (None, None))
    if not hh and d in MANUAL_TIMES:
        hh, su = MANUAL_TIMES[d]
    ev = {'ticker': T, 'event_date': d, 'event_time_local': hh or '', 'event_type': typ, 'fiscal_period': fp,
          'source_url': su or src}
    if d in TIMING_OVERRIDE:
        ev['timing'] = TIMING_OVERRIDE[d]
    basis[f'{d} {typ}'] = f'wire copy timestamp {hh} (StockTitan/GlobeNewswire)' if hh else 'time not documented'
    events.append(ev)

ev_df = irlib.write_events(T, events)
json.dump(basis, open(os.path.join(R, '_time_basis.json'), 'w'), indent=1)

# KPIs
kr = json.load(open(os.path.join(R, '_kpi_rows.json')))
for r in kr:
    if r['fiscal_period'] >= '2026Q1':
        r['extra_json']['orders_note'] = 'ASML stopped reporting quarterly bookings after 2025 (stated in Q4 2024 investor call); total systems backlog reported annually from 2026'
    if r['fiscal_period'] == '2020Q1':
        r['extra_json']['guidance_note'] = 'ASML refrained from guidance due to COVID-19 uncertainty'
    if r['fiscal_period'] == '2024Q3':
        r['release_date'] = '2024-10-15'
kp = irlib.write_kpis(T, kr)

# Manifest
man = json.load(open(os.path.join(R, '_manifest_rows.json')))
extra_docs = [
    ('2016-10-31', '', '000134100416001720_ex99-2.htm', EDGAR + '000134100416001720/ex99-2.htm'),
    ('2018-12-03', '2019Q1', '000119312518340472_d664597dex991.htm', EDGAR + '000119312518340472/d664597dex991.htm'),
    ('2020-03-30', '2020Q1', '000119312520089921_d912704dex991.htm', EDGAR + '000119312520089921/d912704dex991.htm'),
    ('2021-09-29', '', '000119312521285965_d234184dex991.htm', EDGAR + '000119312521285965/d234184dex991.htm'),
    ('2022-01-07', '2022FY', '000119312522004166_d287041dex992.htm', EDGAR + '000119312522004166/d287041dex992.htm'),
    ('2022-11-10', '', '000119312522282132_d308550dex991.htm', EDGAR + '000119312522282132/d308550dex991.htm'),
    ('2024-11-14', '', '000093796624000024_pressreleaseinvestorday2024.htm', EDGAR + '000093796624000024/pressreleaseinvestorday2024.htm'),
]
for d, fp, fn, url in extra_docs:
    p = os.path.join(R, 'edgar_6k', fn)
    if os.path.exists(p):
        man.append({'ticker': T, 'local_path': os.path.relpath(p, irlib.ROOT), 'url': url, 'doc_type': 'press_release',
                    'fiscal_period': fp, 'pub_date': d})
mf = irlib.write_manifest(T, man)
print('events', len(ev_df), ev_df.event_date.min(), ev_df.event_date.max(), ev_df.timing.value_counts().to_dict(),
      ev_df.event_type.value_counts().to_dict())
print('kpis', len(kp), 'manifest', len(mf), mf.doc_type.value_counts().to_dict())
