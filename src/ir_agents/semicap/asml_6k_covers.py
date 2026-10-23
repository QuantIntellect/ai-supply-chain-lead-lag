"""Fetch ASML 6-K primary documents (non-quarterly) from EDGAR and print a short description of their content."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
T = 'ASML.AS'
cdir = irlib.ensure(os.path.join(irlib.raw_dir(T), 'edgar_6k'))
df = pd.read_parquet(os.path.join(irlib.ROOT, 'data/processed/edgar_filings.parquet'))
a = df[(df.ticker == T) & (df.form == '6-K') & (df.filingDate >= '2014-12-01')].sort_values('filingDate')
skip = re.compile(r'quarterly|results|annualreport', re.I)
out = []
for _, r in a.iterrows():
    if skip.search(r.primaryDocument):
        continue
    acc = r.accessionNumber.replace('-', '')
    url = f'https://www.sec.gov/Archives/edgar/data/937966/{acc}/{r.primaryDocument}'
    path = os.path.join(cdir, f'{r.filingDate}_{acc}_{r.primaryDocument}')
    st, b = irlib.fetch(url, path, sec=True, min_gap=0.2)
    flat = ' '.join(irlib.html_to_text(b).split()) if st == 200 else ''
    m = re.search(r'(?:Exhibit|EXHIBIT)s?\s*(?:No\.?)?\s*99[^A-Za-z]{0,10}(.{0,220})', flat)
    desc = m.group(1) if m else flat[flat.find('Commission File'):][:0]
    if not desc:
        i = flat.lower().find('veldhoven')
        desc = flat[i:i + 220] if i >= 0 else flat[800:1020]
    out.append({'filingDate': r.filingDate, 'url': url, 'desc': desc})
    print(r.filingDate, '|', desc[:200])
json.dump(out, open(os.path.join(cdir, '_covers.json'), 'w'), indent=1)
