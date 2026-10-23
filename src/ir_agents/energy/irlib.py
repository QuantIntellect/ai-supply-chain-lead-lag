"""Shared helpers for the European energy-equipment / cable IR collection.

Import from a script run with `python -I` (isolated mode does NOT put the
script directory on sys.path):

    import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy")
    import irlib

Conventions (shared by all five companies)
------------------------------------------
fiscal_period
    FY2024Q1 / FY2024Q2 / FY2024Q3 / FY2024Q4  discrete quarter
    FY2024H1                                     six months (half-year)
    FY2024_9M                                    nine months cumulative (KPI file only)
    FY2024                                       full fiscal year
  Siemens Energy fiscal year ends 30 Sep: FY2025Q1 = Oct-Dec 2024 (period_end 2024-12-31).
  Others are calendar years.
  Events file: fiscal_period is the period the release reports on (a 9M/Q3 release -> FY2024Q3;
  an annual release -> FY2024). Trading updates -> latest quarter covered (May AGM update ->
  FY2024Q1, Nov update -> FY2024Q3). Profit warning -> the fiscal year affected (FY2023).
  CMD -> may be blank.
event_type  one of EVENT_TYPES. Release titled half-year -> H1; titled Q2 -> Q2; annual -> FY.
timing      BMO / AMC / INTRADAY / UNKNOWN, from the local publication clock time vs home
            market continuous-trading hours (see MARKETS). Use classify_timing().
units       currency = reporting currency (EUR/GBP/DKK); unit = "m" (millions). Convert bn -> m
            by x1000 only (exact). Percentages as plain numbers (12.3 means 12.3%).
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAW_IR = os.path.join(ROOT, "data", "raw", "ir")
PROC_IR = os.path.join(ROOT, "data", "processed", "ir")
TEXT_IR = os.path.join(ROOT, "data", "processed", "ir_text")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ticker -> (IANA tz, open HH:MM, close HH:MM, exchange) -- continuous trading session
MARKETS = {
    "ENR.DE": ("Europe/Berlin", "09:00", "17:30", "XETRA"),
    "RR.L": ("Europe/London", "08:00", "16:30", "LSE"),
    "PRY.MI": ("Europe/Rome", "09:00", "17:30", "Borsa Italiana"),
    "NEX.PA": ("Europe/Paris", "09:00", "17:30", "Euronext Paris"),
    "NKT.CO": ("Europe/Copenhagen", "09:00", "17:00", "Nasdaq Copenhagen"),
}

EVENT_TYPES = {"Q1", "Q2", "Q3", "Q4", "H1", "FY", "trading_update", "profit_warning", "prelim", "CMD"}
TIMINGS = {"BMO", "AMC", "INTRADAY", "UNKNOWN"}
DOC_TYPES = {"press_release", "trading_update", "presentation", "transcript", "report", "other"}

EVENT_COLS = ["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type",
              "fiscal_period", "source_url"]
KPI_COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue",
            "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "backlog",
            "gross_margin_pct", "guidance_text", "guidance_rev_low", "guidance_rev_high",
            "ai_dc_notes", "extra_json", "source_doc"]
MANIFEST_COLS = ["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"]
NUM_KPI = ["revenue", "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "backlog",
           "gross_margin_pct", "guidance_rev_low", "guidance_rev_high"]

FP_RE = re.compile(r"^FY\d{4}(Q[1-4]|H1|H2|_9M)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


# ----------------------------------------------------------------------------- HTTP
_last: dict[str, float] = {}
_session = None


def _sess():
    global _session
    if _session is None:
        from curl_cffi import requests as cr
        _session = cr.Session(impersonate="chrome")
    return _session


def fetch(url: str, min_interval: float = 1.1, retries: int = 3, timeout: int = 60, **kw):
    """Polite GET (<=1 req/s per host) with a browser fingerprint. Returns the response."""
    host = urlparse(url).netloc
    err = None
    for i in range(retries):
        wait = min_interval - (time.time() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        try:
            r = _sess().get(url, timeout=timeout, allow_redirects=True, **kw)
            if r.status_code in (429, 500, 502, 503, 504):
                err = f"HTTP {r.status_code}"
                time.sleep(3 * (i + 1))
                continue
            return r
        except Exception as e:  # network hiccup
            err = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {err}")


def raw_dir(ticker: str) -> str:
    d = os.path.join(RAW_IR, ticker)
    os.makedirs(d, exist_ok=True)
    return d


def safe_name(s: str, maxlen: int = 120) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return s[:maxlen] or "file"


def download(url: str, ticker: str, filename: str, force: bool = False, min_bytes: int = 500):
    """Download url to data/raw/ir/<ticker>/<filename> unless present.
    Returns the path relative to ROOT, or None on failure (non-200 / tiny body)."""
    path = os.path.join(raw_dir(ticker), safe_name(filename))
    rel = os.path.relpath(path, ROOT)
    if os.path.exists(path) and os.path.getsize(path) >= min_bytes and not force:
        return rel
    try:
        r = fetch(url)
    except RuntimeError as e:
        print("  download error:", e)
        return None
    if r.status_code != 200 or len(r.content) < min_bytes:
        print(f"  download skip {r.status_code} {len(r.content)}B {url[:120]}")
        return None
    with open(path, "wb") as f:
        f.write(r.content)
    return rel


# ----------------------------------------------------------------------------- text
def pdf_to_text(path: str) -> str:
    import pymupdf
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with pymupdf.open(p) as doc:
        return "\n".join(page.get_text() for page in doc)


def html_to_text(path_or_html: str, is_html: bool = False) -> str:
    from bs4 import BeautifulSoup
    if is_html:
        html = path_or_html
    else:
        p = path_or_html if os.path.isabs(path_or_html) else os.path.join(ROOT, path_or_html)
        with open(p, "rb") as f:
            html = f.read().decode("utf-8", "replace")
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript", "svg"]):
        t.decompose()
    txt = s.get_text("\n")
    return re.sub(r"\n\s*\n+", "\n\n", txt)


def extract_text(raw_rel_path: str, ticker: str, period: str, doctype: str, overwrite: bool = False) -> str | None:
    """Write data/processed/ir_text/<ticker>/<period>_<doctype>.txt (suffix _2, _3 if taken by
    another source). Returns relative path of the txt file."""
    src = os.path.join(ROOT, raw_rel_path)
    d = os.path.join(TEXT_IR, ticker)
    os.makedirs(d, exist_ok=True)
    base = f"{safe_name(period)}_{safe_name(doctype)}"
    marker = f"[source: {raw_rel_path}]\n"
    k = 1
    while True:
        name = base + ("" if k == 1 else f"_{k}") + ".txt"
        out = os.path.join(d, name)
        if not os.path.exists(out):
            break
        with open(out, encoding="utf-8", errors="replace") as f:
            if f.readline() == marker:  # same source already extracted
                if not overwrite:
                    return os.path.relpath(out, ROOT)
                break
        k += 1
    low = src.lower()
    try:
        with open(src, "rb") as f:
            head = f.read(5)
        if head.startswith(b"%PDF"):
            txt = pdf_to_text(src)
        elif low.endswith((".htm", ".html")) or head.lstrip()[:1] == b"<":
            txt = html_to_text(src)
        else:
            with open(src, "rb") as f:
                txt = f.read().decode("utf-8", "replace")
    except Exception as e:
        print("  extract error", raw_rel_path, type(e).__name__, str(e)[:100])
        return None
    with open(out, "w", encoding="utf-8") as f:
        f.write(marker + txt)
    return os.path.relpath(out, ROOT)


# ----------------------------------------------------------------------------- time
def to_local(dt_str: str, src_tz: str, ticker: str, fmt: str | None = None):
    """Convert a naive timestamp string in src_tz (e.g. 'UTC', 'Europe/London') into the
    company's local (date 'YYYY-MM-DD', time 'HH:MM')."""
    dt = datetime.strptime(dt_str, fmt) if fmt else datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(src_tz))
    loc = dt.astimezone(ZoneInfo(MARKETS[ticker][0]))
    return loc.strftime("%Y-%m-%d"), loc.strftime("%H:%M")


def classify_timing(ticker: str, hhmm: str | None) -> str:
    """BMO if before the continuous session opens, AMC if at/after it closes, else INTRADAY."""
    if not hhmm or not TIME_RE.match(hhmm):
        return "UNKNOWN"
    _, op, cl, _ = MARKETS[ticker]
    if hhmm < op:
        return "BMO"
    if hhmm >= cl:
        return "AMC"
    return "INTRADAY"


# ----------------------------------------------------------------------------- writers
def _write(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})
    print(f"wrote {len(rows)} rows -> {os.path.relpath(path, ROOT)}")


def write_events(ticker: str, rows: list[dict]):
    tz = MARKETS[ticker][0]
    out, seen = [], set()
    for r in rows:
        r = dict(r)
        r["ticker"] = ticker
        r["timezone"] = tz
        t = (r.get("event_time_local") or "").strip()
        r["event_time_local"] = t
        assert DATE_RE.match(r["event_date"]), r
        assert r["event_type"] in EVENT_TYPES, r
        assert not t or TIME_RE.match(t), r
        fp = r.get("fiscal_period") or ""
        assert not fp or FP_RE.match(fp), r
        calc = classify_timing(ticker, t)
        if not r.get("timing") or calc != "UNKNOWN":
            r["timing"] = calc  # clock time is authoritative when present
        assert r["timing"] in TIMINGS, r
        key = (r["event_date"], r["event_type"], fp)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    out.sort(key=lambda r: (r["event_date"], r["event_time_local"]))
    _write(os.path.join(PROC_IR, f"{ticker}_events.csv"), EVENT_COLS, out)


def write_kpis(ticker: str, rows: list[dict]):
    out, seen = [], set()
    for r in rows:
        r = dict(r)
        r["ticker"] = ticker
        assert FP_RE.match(r["fiscal_period"]), r
        for c in ("period_end", "release_date"):
            assert not r.get(c) or DATE_RE.match(r[c]), r
        for c in NUM_KPI:
            v = r.get(c)
            if v in (None, ""):
                r[c] = ""
            else:
                r[c] = float(v)
        ej = r.get("extra_json")
        if isinstance(ej, (dict, list)):
            r["extra_json"] = json.dumps(ej, ensure_ascii=False, sort_keys=True)
        elif ej:
            json.loads(ej)  # must be valid JSON
        if r["fiscal_period"] in seen:
            raise ValueError(f"duplicate fiscal_period {r['fiscal_period']}")
        seen.add(r["fiscal_period"])
        out.append(r)
    out.sort(key=lambda r: (r.get("period_end") or "", r["fiscal_period"]))
    _write(os.path.join(PROC_IR, f"{ticker}_kpis.csv"), KPI_COLS, out)


def write_manifest(ticker: str, rows: list[dict]):
    out, seen = [], set()
    for r in rows:
        r = dict(r)
        r["ticker"] = ticker
        assert r["doc_type"] in DOC_TYPES, r
        assert os.path.exists(os.path.join(ROOT, r["local_path"])), r
        assert not r.get("pub_date") or DATE_RE.match(r["pub_date"]), r
        if r["local_path"] in seen:
            continue
        seen.add(r["local_path"])
        out.append(r)
    out.sort(key=lambda r: (r.get("pub_date") or "", r["local_path"]))
    _write(os.path.join(PROC_IR, f"{ticker}_manifest.csv"), MANIFEST_COLS, out)


def read_csv(path: str) -> list[dict]:
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def grep(rel_txt: str, pattern: str, width: int = 160, maxn: int = 12) -> list[str]:
    """Return up to maxn context snippets of a regex in an extracted text file (token-cheap)."""
    p = rel_txt if os.path.isabs(rel_txt) else os.path.join(ROOT, rel_txt)
    with open(p, encoding="utf-8", errors="replace") as f:
        t = re.sub(r"\s+", " ", f.read())
    out = []
    for m in re.finditer(pattern, t, re.I):
        a, b = max(0, m.start() - width), min(len(t), m.end() + width)
        out.append(t[a:b])
        if len(out) >= maxn:
            break
    return out
