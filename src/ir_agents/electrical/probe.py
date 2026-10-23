"""Quick accessibility probe of IR sites (status code + size only)."""
import sys, time
from curl_cffi import requests as creq

URLS = sys.argv[1:]
s = creq.Session(impersonate="chrome")
for u in URLS:
    try:
        r = s.get(u, timeout=30, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        print(r.status_code, len(r.content), ct[:40], r.url[:120])
    except Exception as e:
        print("ERR", u, type(e).__name__, str(e)[:120])
    time.sleep(1.1)
