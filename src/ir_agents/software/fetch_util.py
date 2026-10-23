"""Shared polite fetch helpers for the software/IT IR agents."""
import os, time, re, hashlib
from urllib.parse import urlparse
from curl_cffi import requests as creq

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAW_IR = os.path.join(ROOT, "data", "raw", "ir")
PROC_IR = os.path.join(ROOT, "data", "processed", "ir")
TXT_IR = os.path.join(ROOT, "data", "processed", "ir_text")
CACHE = os.path.join(ROOT, "data", "raw", "ir", "_cache_html")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
SEC_UA = "aimapping-research research@example.org"

_sess = None
_last = {}

def sess():
    global _sess
    if _sess is None:
        _sess = creq.Session(impersonate="chrome")
    return _sess

def _wait(host, gap=1.1):
    t = _last.get(host, 0)
    d = time.time() - t
    if d < gap:
        time.sleep(gap - d)
    _last[host] = time.time()

def get(url, headers=None, timeout=60, gap=1.1, **kw):
    host = urlparse(url).netloc
    _wait(host, gap)
    h = {"User-Agent": SEC_UA} if "sec.gov" in host else {"User-Agent": UA}
    if headers:
        h.update(headers)
    return sess().get(url, headers=h, timeout=timeout, allow_redirects=True, **kw)

def cached_html(url, refresh=False, **kw):
    """Fetch HTML with on-disk cache (cache is untrusted data, never executed)."""
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest() + ".html")
    if os.path.exists(fn) and not refresh:
        with open(fn, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    r = get(url, **kw)
    if r.status_code != 200:
        return None
    txt = r.text
    with open(fn, "w", encoding="utf-8") as f:
        f.write(txt)
    return txt

def download(url, dest, min_bytes=1000, **kw):
    if os.path.exists(dest) and os.path.getsize(dest) >= min_bytes:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        r = get(url, **kw)
    except Exception as e:
        print("ERR", url, repr(e)[:120]); return False
    if r.status_code != 200 or len(r.content) < min_bytes:
        print("FAIL", r.status_code, len(r.content), url); return False
    with open(dest, "wb") as f:
        f.write(r.content)
    return True

def pdf_to_text(path):
    import pymupdf
    doc = pymupdf.open(path)
    out = []
    for p in doc:
        out.append(p.get_text())
    return "\n".join(out)

def html_to_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    return txt
