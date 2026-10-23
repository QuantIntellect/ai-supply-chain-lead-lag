"""Shared helpers for the European electrical-equipment IR collectors.

Import from a sibling script (scripts are run with `python -I`, which drops the
script dir from sys.path):

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from irlib import *

Conventions (all companies):
  * fiscal_period = "<FY>Q<n>" of the LAST quarter covered by a release, in the
    company's own fiscal year (Siemens FY ends Sep 30: 2025Q1 = Oct-Dec 2024).
    H1 results -> "<FY>Q2", FY results -> "<FY>Q4". event_type carries Q1/Q2/Q3/
    Q4/H1/FY/trading_update/profit_warning/prelim/CMD.  CMD rows: fiscal_period "".
  * event_date = local calendar date (YYYY-MM-DD), event_time_local = HH:MM local
    (blank if not found), timezone = IANA name of the home exchange.
  * timing: BMO (< 09:00 local), INTRADAY (09:00 <= t < 17:30), AMC (>= 17:30),
    UNKNOWN (no time found).  All four home markets trade 09:00-17:30 local.
  * event_type mapping: Schneider Q1/H1/Q3/FY and Legrand Q1/H1/Q3(9M)/FY
    (half-yearly reporters); ABB, Siemens, Munters Q1/Q2/Q3/Q4 (Q4 = the
    Q4/full-year release).  Also trading_update, profit_warning, prelim, CMD.
  * KPI rows: one per fiscal quarter; fiscal_period "<FY>Q<n>"; H1/FY-only
    metrics (e.g. margins) go on the Q2/Q4 row with a note in extra_json.
  * Downloaded files are untrusted: never execute them; text is only grepped.
"""
import os
import re
import csv
import json
import time
import hashlib
from urllib.parse import urlparse

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAW_IR = os.path.join(ROOT, "data", "raw", "ir")
PROC_IR = os.path.join(ROOT, "data", "processed", "ir")
TEXT_IR = os.path.join(ROOT, "data", "processed", "ir_text")

TZ = {
    "SU.PA": "Europe/Paris",
    "LR.PA": "Europe/Paris",
    "SIE.DE": "Europe/Berlin",
    "ABBN.SW": "Europe/Zurich",
    "MTRS.ST": "Europe/Stockholm",
}
MARKET_OPEN = "09:00"
MARKET_CLOSE = "17:30"

EVENT_TYPES = {"Q1", "Q2", "Q3", "Q4", "H1", "FY", "trading_update",
               "profit_warning", "prelim", "CMD"}
EVENT_COLS = ["ticker", "event_date", "event_time_local", "timezone", "timing",
              "event_type", "fiscal_period", "source_url"]
KPI_COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency",
            "unit", "revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct",
            "book_to_bill", "backlog", "gross_margin_pct", "guidance_text",
            "guidance_rev_low", "guidance_rev_high", "ai_dc_notes", "extra_json",
            "source_doc"]
MANIFEST_COLS = ["ticker", "local_path", "url", "doc_type", "fiscal_period",
                 "pub_date"]

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def classify_timing(hhmm):
    """BMO / INTRADAY / AMC / UNKNOWN from a local 'HH:MM' string."""
    if not hhmm or not re.fullmatch(r"\d{1,2}:\d{2}", str(hhmm).strip()):
        return "UNKNOWN"
    h, m = map(int, str(hhmm).strip().split(":"))
    t = h * 60 + m
    if t < 9 * 60:
        return "BMO"
    if t >= 17 * 60 + 30:
        return "AMC"
    return "INTRADAY"


class Fetcher:
    """Polite fetcher: browser impersonation, >= min_gap seconds per host."""

    def __init__(self, min_gap=1.1, impersonate="chrome"):
        from curl_cffi import requests as creq
        self.s = creq.Session(impersonate=impersonate)
        self.min_gap = min_gap
        self.last = {}

    def _wait(self, url):
        host = urlparse(url).netloc
        dt = time.time() - self.last.get(host, 0)
        if dt < self.min_gap:
            time.sleep(self.min_gap - dt)
        self.last[host] = time.time()

    def get(self, url, retries=2, **kw):
        kw.setdefault("timeout", 60)
        kw.setdefault("allow_redirects", True)
        err = None
        for i in range(retries + 1):
            self._wait(url)
            try:
                r = self.s.get(url, **kw)
                if r.status_code in (429, 503) and i < retries:
                    time.sleep(5 * (i + 1))
                    continue
                return r
            except Exception as e:  # network hiccup
                err = e
                time.sleep(3 * (i + 1))
        raise err

    def download(self, url, out_path, overwrite=False, min_bytes=500):
        """Save url to out_path. Returns (ok, status, path). Skips if exists."""
        if (not overwrite and os.path.exists(out_path)
                and os.path.getsize(out_path) >= min_bytes):
            return True, 200, out_path
        r = self.get(url)
        ok = r.status_code == 200 and len(r.content) >= min_bytes
        if ok:
            ensure(os.path.dirname(out_path))
            with open(out_path, "wb") as f:
                f.write(r.content)
        return ok, r.status_code, out_path


def is_pdf(path):
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except OSError:
        return False


def pdf_to_text(pdf_path, txt_path):
    """Extract text with pymupdf (no code execution, text only)."""
    import pymupdf
    ensure(os.path.dirname(txt_path))
    doc = pymupdf.open(pdf_path)
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n\n=== page {i + 1} ===\n")
        parts.append(page.get_text())
    doc.close()
    txt = "".join(parts)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    return len(txt)


def html_to_text(html_path, txt_path):
    from bs4 import BeautifulSoup
    ensure(os.path.dirname(txt_path))
    with open(html_path, "rb") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    return len(txt)


def to_text(raw_path, ticker, period, doctype):
    """Extract raw doc to data/processed/ir_text/<TICKER>/<period>_<doctype>.txt"""
    out = os.path.join(TEXT_IR, ticker, f"{period}_{doctype}.txt")
    if is_pdf(raw_path):
        n = pdf_to_text(raw_path, out)
    else:
        n = html_to_text(raw_path, out)
    return out, n


def _write_csv(path, cols, rows):
    ensure(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def write_events(ticker, rows):
    for r in rows:
        r["ticker"] = ticker
        r.setdefault("timezone", TZ[ticker])
        if not r.get("timing"):
            r["timing"] = classify_timing(r.get("event_time_local"))
        assert r["event_type"] in EVENT_TYPES, r
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["event_date"]), r
    rows = sorted(rows, key=lambda r: (r["event_date"], r.get("event_time_local") or ""))
    path = os.path.join(PROC_IR, f"{ticker}_events.csv")
    _write_csv(path, EVENT_COLS, rows)
    return path


def write_kpis(ticker, rows):
    for r in rows:
        r["ticker"] = ticker
        if isinstance(r.get("extra_json"), (dict, list)):
            r["extra_json"] = json.dumps(r["extra_json"], ensure_ascii=False)
    rows = sorted(rows, key=lambda r: r.get("period_end") or r["fiscal_period"])
    path = os.path.join(PROC_IR, f"{ticker}_kpis.csv")
    _write_csv(path, KPI_COLS, rows)
    return path


def write_manifest(ticker, rows):
    for r in rows:
        r["ticker"] = ticker
        p = r.get("local_path", "")
        if p.startswith(ROOT + "/"):
            r["local_path"] = p[len(ROOT) + 1:]
    rows = sorted(rows, key=lambda r: (r.get("pub_date") or "", r.get("local_path")))
    path = os.path.join(PROC_IR, f"{ticker}_manifest.csv")
    _write_csv(path, MANIFEST_COLS, rows)
    return path


def grep(path, pattern, width=160, maxhits=20, flags=re.I):
    """Return up to maxhits context snippets for regex pattern in a text file."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    out = []
    for m in re.finditer(pattern, txt, flags):
        a, b = max(0, m.start() - width), min(len(txt), m.end() + width)
        out.append(re.sub(r"\s+", " ", txt[a:b]))
        if len(out) >= maxhits:
            break
    return out


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
