"""Wayback helpers for BESI (besi.com refuses connections from this machine).
Usage as module: wb_latest(url_path) -> (timestamp, original); wb_get(ts, original, save_path) -> bytes"""
import os, sys, json, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad"
_cdx = None

def cdx_rows():
    global _cdx
    if _cdx is None:
        rows = []
        for f in ("besi_cdx_html.json", "besi_cdx_pdf.json"):
            p = os.path.join(SCR, f)
            if os.path.exists(p):
                rows += json.load(open(p))[1:]
        _cdx = rows
    return _cdx

def norm(u):
    return re.sub(r'^https?://(www\.)?besi\.com(:80|:443)?', '', u).split('?')[0]

def find(pattern):
    pat = re.compile(pattern, re.I)
    return [r for r in cdx_rows() if pat.search(norm(r[2]))]

def wb_url(ts, orig):
    return f"https://web.archive.org/web/{ts}id_/{orig}"

def wb_get(ts, orig, path=None):
    st, b = irlib.fetch(wb_url(ts, orig), path, min_gap=1.5)
    return st, b

def cdx_query(url, extra=""):
    """Live CDX query for all captures of one URL (not collapsed)."""
    q = f"https://web.archive.org/cdx/search/cdx?url={url}&output=json{extra}"
    st, b = irlib.fetch(q, None, min_gap=1.5)
    if st != 200:
        return []
    try:
        return json.loads(b)[1:]
    except Exception:
        return []
