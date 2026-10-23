"""Fetch ASML per-quarter results pages (asml.com/en/investors/financial-results/qN-YYYY) and extract
publication date/time statements. Saves raw HTML to data/raw/ir/ASML.AS/pages/ and a JSON summary."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
pdir = irlib.ensure(os.path.join(irlib.raw_dir(T), 'pages'))
out = {}
quarters = [(2014, 4)] + [(y, q) for y in range(2015, 2027) for q in range(1, 5) if (y, q) <= (2026, 3)]
for y, q in quarters:
    slug = f'q{q}-{y}'
    url = f'https://www.asml.com/en/investors/financial-results/{slug}'
    path = os.path.join(pdir, f'{slug}.html')
    st, b = irlib.fetch(url, path)
    if st != 200:
        out[slug] = {'url': url, 'status': st}
        print(slug, st)
        continue
    t = irlib.html_to_text(b)
    flat = ' '.join(t.split())
    times = re.findall(r'[^.]{0,140}\b\d{1,2}[:.]\d{2}\s*(?:CET|CEST|ET|EST|EDT|US Eastern|a\.m\.|p\.m\.)[^.]{0,80}', flat)
    dates = re.findall(r'(?:announced|publishe[sd]|will publish|released)[^.]{0,120}?(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? 20\d\d', flat)
    out[slug] = {'url': url, 'status': st, 'times': times[:6], 'dates': dates[:4]}
    print(slug, st, '| T:', (times[0][:160] if times else '-'), '| D:', (dates[0][-60:] if dates else '-'))
json.dump(out, open(os.path.join(pdir, '_summary.json'), 'w'), indent=1)
