import sys, time
from curl_cffi import requests as cr
urls = sys.argv[1:]
s = cr.Session(impersonate="chrome")
for u in urls:
    try:
        r = s.get(u, timeout=30)
        t = r.text
        print(r.status_code, len(t), u, '| title:', (t.split('<title>')[1].split('</title>')[0][:80].strip() if '<title>' in t else '-'))
    except Exception as e:
        print('ERR', u, e)
    time.sleep(1)
