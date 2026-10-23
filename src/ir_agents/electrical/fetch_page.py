"""Fetch one URL to a file (browser impersonation). Usage: fetch_page.py URL OUTFILE"""
import sys, os
from curl_cffi import requests as creq
u, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.dirname(out), exist_ok=True)
r = creq.get(u, impersonate="chrome", timeout=60, allow_redirects=True)
with open(out, "wb") as f:
    f.write(r.content)
print(r.status_code, len(r.content), r.headers.get("content-type", "")[:40], r.url[:150])
