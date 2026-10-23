"""Probe IR sites for scripted accessibility (status, size, title). Usage: probe.py URL [URL...]"""
import sys
import re
import time
from curl_cffi import requests as creq

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

for u in sys.argv[1:]:
    try:
        r = creq.get(u, impersonate="chrome", timeout=30, allow_redirects=True)
        t = re.search(r"<title[^>]*>(.*?)</title>", r.text or "", re.S | re.I)
        print(r.status_code, len(r.content), r.url[:120], "|", (t.group(1).strip()[:80] if t else ""))
    except Exception as e:  # noqa
        print("ERR", u, repr(e)[:150])
    time.sleep(1.2)
