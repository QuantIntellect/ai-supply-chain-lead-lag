"""Scrape GlobeNewswire organization listing for ASM International NV -> CSV (date_et, time_et, local date/time Amsterdam, title, url).
Usage: asm_gnw.py OUTCSV [maxpages]"""
import sys, os, re, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import fetch, raw_dir
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
out = sys.argv[1]
maxpages = int(sys.argv[2]) if len(sys.argv) > 2 else 200
ET, AMS = ZoneInfo('America/New_York'), ZoneInfo('Europe/Amsterdam')
rows, seen = [], set()
cache = os.path.join('/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/asm', 'gnw')
os.makedirs(cache, exist_ok=True)
for p in range(1, maxpages + 1):
    url = f"https://www.globenewswire.com/en/search/organization/ASM%2520International%2520NV?page={p}&pageSize=50"
    st, b = fetch(url, path=os.path.join(cache, f"p{p}.html"))
    if st != 200:
        print('status', st, p); break
    s = BeautifulSoup(b, 'html.parser')
    n_new = 0
    for a in s.find_all('a', href=True):
        h = a['href']
        if '/news-release/' not in h:
            continue
        if h.startswith('/'):
            h = 'https://www.globenewswire.com' + h
        if h in seen:
            continue
        title = ' '.join(a.get_text(' ', strip=True).split())
        if not title:
            continue
        # find timestamp in nearest container
        cont = a
        ts = None
        for _ in range(6):
            cont = cont.parent
            if cont is None:
                break
            m = re.search(r'([A-Z][a-z]+ \d{2}, \d{4}) (\d{2}:\d{2}) ET', cont.get_text(' ', strip=True))
            if m:
                ts = m; break
        seen.add(h)
        n_new += 1
        row = {'title': title, 'url': h, 'date_et': '', 'time_et': '', 'date_local': '', 'time_local': ''}
        if ts:
            dt = datetime.strptime(ts.group(1) + ' ' + ts.group(2), '%B %d, %Y %H:%M').replace(tzinfo=ET)
            loc = dt.astimezone(AMS)
            row.update(date_et=dt.strftime('%Y-%m-%d'), time_et=dt.strftime('%H:%M'),
                       date_local=loc.strftime('%Y-%m-%d'), time_local=loc.strftime('%H:%M'))
        rows.append(row)
    print('page', p, 'new', n_new, rows[-1]['date_local'] if rows else '')
    if n_new == 0:
        break
with open(out, 'w') as f:
    w = csv.DictWriter(f, fieldnames=['date_local', 'time_local', 'date_et', 'time_et', 'title', 'url'])
    w.writeheader(); w.writerows(rows)
print('total', len(rows))
