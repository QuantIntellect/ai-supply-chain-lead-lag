"""Fetch selected ASML press releases from asml.com; print dateline date, stated times and outlook mentions."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
pdir = irlib.ensure(os.path.join(irlib.raw_dir(T), 'press_releases_html'))
rows = json.load(open(sys.argv[1]))
pat = re.compile(sys.argv[2])
seen = set()
res = []
for ts, o in rows:
    m = re.search(r'press-releases/(20(1[4-9]|2[0-6]))/([^?#]+)', o)
    if not m:
        continue
    yr, slug = m.group(1), m.group(3).rstrip('/')
    if (yr, slug) in seen or not pat.search(f'{yr}/{slug}'):
        continue
    seen.add((yr, slug))
    url = f'https://www.asml.com/en/news/press-releases/{yr}/{slug}'
    path = os.path.join(pdir, f'{yr}_{slug[:90]}.html')
    st, b = irlib.fetch(url, path)
    if st != 200:
        print(yr, slug[:60], st); continue
    flat = ' '.join(irlib.html_to_text(b).split())
    dl = re.search(r'Veldhoven, the Netherlands,? ((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? 20\d\d)', flat, re.I)
    times = re.findall(r'[^.]{0,80}\b\d{1,2}[:.]\d{2}\s*(?:hours\s*)?(?:CET|CEST|ET|a\.m\.|p\.m\.)[^.]{0,40}', flat)
    outl = re.findall(r'[^.]{0,100}(?:outlook|guidance|financial impact|material impact|not expect)[^.]{0,120}', flat, re.I)
    r = {'year': yr, 'slug': slug, 'url': url, 'dateline': dl.group(1) if dl else None,
         'times': [t[-120:] for t in times[:3]], 'outlook': [x[:220] for x in outl[:2]]}
    res.append(r)
    print(yr, slug[:70], '|', r['dateline'], '|T:', r['times'][:2], '|O:', r['outlook'][:1])
json.dump(res, open(os.path.join(pdir, '_check_' + re.sub(r'\W+', '_', sys.argv[2])[:30] + '.json'), 'w'), indent=1)
