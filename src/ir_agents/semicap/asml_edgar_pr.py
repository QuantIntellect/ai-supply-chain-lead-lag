"""Fetch press-release (and presentation) exhibits of ASML's quarterly-results 6-Ks from EDGAR, 2015-2026.
Saves raw files to data/raw/ir/ASML.AS/edgar_q/<period>_<name>, text to ir_text, and a JSON index."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
T = 'ASML.AS'
qd = irlib.ensure(os.path.join(irlib.raw_dir(T), 'edgar_q'))
df = pd.read_parquet(os.path.join(irlib.ROOT, 'data/processed/edgar_filings.parquet'))
a = df[(df.ticker == T) & (df.form == '6-K') & (df.filingDate >= '2015-01-01')].sort_values('filingDate')
# quarterly results 6-Ks: one per results date (dates verified from 6-K exhibit list / ASML pages)
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


index = []
for d in RES_DATES:
    per = period_of(d)
    cands = a[a.filingDate == d]
    got = False
    for _, r in cands.iterrows():
        acc = r.accessionNumber.replace('-', '')
        base = f'https://www.sec.gov/Archives/edgar/data/937966/{acc}/'
        st, b = irlib.fetch(base + 'index.json', sec=True, min_gap=0.15)
        if st != 200:
            continue
        names = [i['name'] for i in json.loads(b)['directory']['item']]
        htm = [n for n in names if n.lower().endswith(('.htm', '.html')) and n != r.primaryDocument and 'index' not in n]
        for n in htm:
            low = n.lower()
            if re.search(r'financialstatement|us-?gaap|ifrs|statutory|agenda|remuneration', low):
                continue
            kind = 'presentation' if 'presentation' in low else 'press_release'
            path = os.path.join(qd, f'{per}_{n}')
            st2, b2 = irlib.fetch(base + n, path, sec=True, min_gap=0.15)
            if st2 != 200:
                continue
            txt = irlib.html_to_text(b2)
            head = ' '.join(txt[:3000].split())
            if kind == 'press_release' and not re.search(r'net sales|results', head, re.I):
                continue
            if kind == 'press_release' and re.search(r'share buy.?back program\s+Repurchase', head, re.I):
                continue
            if kind == 'press_release' and len(txt) < 4000:
                continue
            index.append({'period': per, 'date': d, 'kind': kind, 'url': base + n, 'path': os.path.relpath(path, irlib.ROOT),
                          'chars': len(txt), 'filing_index': base})
            got = True
            print(per, d, kind, n, len(txt))
    if not got:
        print('NO-PR', per, d)
json.dump(index, open(os.path.join(qd, '_index.json'), 'w'), indent=0)
