"""Probe reachability of IR sites (status, size, title)."""
import sys, time, re
from curl_cffi import requests as creq

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

def main(urls):
    s = creq.Session(impersonate="chrome")
    for u in urls:
        try:
            r = s.get(u, timeout=30, headers={"User-Agent": UA}, allow_redirects=True)
            t = re.search(r"<title>(.*?)</title>", r.text[:20000], re.S | re.I)
            print(r.status_code, len(r.content), r.url[:120], "|", (t.group(1).strip()[:80] if t else ""))
        except Exception as e:
            print("ERR", u, repr(e)[:150])
        time.sleep(1.1)

if __name__ == "__main__":
    main(sys.argv[1:])
