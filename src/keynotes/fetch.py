"""Polite cached fetcher for NVIDIA keynote corpus.

Usage: python -I fetch.py <url> <out_path> [--force]
Also importable: get(url, out_path, force=False) -> (status, text)
"""
import os
import sys
import time
import requests

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
_last = [0.0]
_session = requests.Session()
_session.headers.update({"User-Agent": UA,
                         "Accept-Language": "en-US,en;q=0.9",
                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})


def get(url, out_path, force=False, min_interval=1.1):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 500 and not force:
        with open(out_path, encoding="utf-8", errors="ignore") as f:
            return 200, f.read()
    wait = min_interval - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    try:
        r = _session.get(url, timeout=40)
    except Exception as e:  # network error
        _last[0] = time.time()
        return -1, str(e)
    _last[0] = time.time()
    if r.status_code == 200:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(r.text)
    return r.status_code, r.text


if __name__ == "__main__":
    st, txt = get(sys.argv[1], sys.argv[2], force="--force" in sys.argv)
    print(st, len(txt))
