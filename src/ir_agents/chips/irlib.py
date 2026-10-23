"""Shared helpers for the chips IR collectors (IFX.DE, STMPA.PA, SOI.PA, SMHN.DE, NOKIA.HE).

- polite fetching (browser impersonation via curl_cffi, >=1.1 s between requests per host,
  enforced across processes with a lock file), on-disk caching of fetched pages
- SEC EDGAR fetching with the required User-Agent
- text extraction (pymupdf for PDFs, bs4 for HTML)
- exact output schemas + writers/validators for events / kpis / manifest CSVs
Downloaded files are untrusted data: we only parse them, never execute them.

CONVENTIONS (shared by all five collectors -- do not deviate):
- fiscal_period uses the company's own fiscal labels: quarters "FY2026Q3", half-years "FY2026H1",
  full year "FY2026".  Infineon FY ends 30 Sep (FY2026Q3 = Apr-Jun 2026), Soitec FY ends 31 Mar
  (FY2026Q1 = Apr-Jun 2025); STM, SUSS, Nokia = calendar years.  period_end = calendar date of the
  period end (YYYY-MM-DD) -- this is the join key.
- event_type: quarterly reporters (IFX, STM, NOK, SUSS) -> Q1..Q4; a combined Q4+FY release is ONE
  "Q4" row.  SUSS: preliminary FY figures (Jan/Feb ad-hoc) -> "prelim"; annual report publication
  (March) -> "FY"; H1 report -> "Q2".  Soitec: Q1 revenue -> "Q1", H1 results -> "H1", Q3 revenue ->
  "Q3", FY results -> "FY".  Pre-released quarter figures / ad-hoc guidance raises -> "prelim" or
  "trading_update"; guidance cuts / negative ad-hocs -> "profit_warning"; capital markets / investor
  days -> "CMD".
- event_time_local: HH:MM in the HOME exchange's local time (convert if the source states another
  tz); timezone = IANA name of the home exchange (Europe/Berlin, Europe/Paris, Europe/Helsinki).
  timing via timing_class(): BMO if < open (09:00 DE/FR, 10:00 HE), AMC if >= close incl. closing
  auction (17:35 DE/FR, 18:30 HE), else INTRADAY; UNKNOWN when no time is documented.
- Time sources, in priority: release header/dateline/feed timestamps (newswire, EQS, stock-exchange
  release headers, Q4-platform JSON, article:published_time meta), then "announces timing"/calendar
  statements ("before market open" / "after market close" -> timing class without HH:MM).  NEVER
  use EDGAR acceptanceDateTime or Yahoo timestamps as the publication time (dates only).
- doc_type vocabulary: press_release, interim_report, presentation, transcript, annual_report,
  other.  Raw file name: data/raw/ir/<TICKER>/<period>_<doctype>.<ext>; text:
  data/processed/ir_text/<TICKER>/<period>_<doctype>.txt.
- KPIs: leave blank when not stated; values as reported (unit column e.g. "EUR m", "USD m");
  revenue_yoy_pct / margins in percent (e.g. 12.3); derived numbers (e.g. guidance low/high from a
  midpoint +/- range) must be flagged in extra_json, e.g. {"guidance_derived": true}.
"""
import os
import re
import io
import time
import json
import fcntl
import hashlib
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAW_IR = os.path.join(ROOT, "data", "raw", "ir")
PROC_IR = os.path.join(ROOT, "data", "processed", "ir")
TXT_IR = os.path.join(ROOT, "data", "processed", "ir_text")
LOCK_DIR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/ratelimit"

WEB_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126 Safari/537.36")
SEC_UA = "aimapping-research research@example.org"

EVENT_COLS = ["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type",
              "fiscal_period", "source_url"]
KPI_COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue",
            "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "backlog",
            "gross_margin_pct", "guidance_text", "guidance_rev_low", "guidance_rev_high",
            "ai_dc_notes", "extra_json", "source_doc"]
MANIFEST_COLS = ["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"]
EVENT_TYPES = {"Q1", "Q2", "Q3", "Q4", "H1", "FY", "trading_update", "profit_warning", "prelim", "CMD"}
TIMINGS = {"BMO", "AMC", "INTRADAY", "UNKNOWN"}
DOC_TYPES = {"press_release", "interim_report", "presentation", "transcript", "annual_report", "other"}

# Home market (IANA tz, continuous-trading open, close incl. closing auction)
MARKET = {
    "IFX.DE": ("Europe/Berlin", "09:00", "17:35"),     # Xetra 09:00-17:30 + closing auction
    "SMHN.DE": ("Europe/Berlin", "09:00", "17:35"),
    "STMPA.PA": ("Europe/Paris", "09:00", "17:35"),    # Euronext Paris 09:00-17:30 + auction
    "SOI.PA": ("Europe/Paris", "09:00", "17:35"),
    "NOKIA.HE": ("Europe/Helsinki", "10:00", "18:30"),  # Nasdaq Helsinki 10:00-18:25 + auction
}


def ensure(p):
    os.makedirs(p, exist_ok=True)
    return p


def raw_dir(ticker):
    return ensure(os.path.join(RAW_IR, ticker))


def txt_dir(ticker):
    return ensure(os.path.join(TXT_IR, ticker))


# ---------------------------------------------------------------- polite fetching
def _throttle(host, min_gap=1.1):
    ensure(LOCK_DIR)
    lf = os.path.join(LOCK_DIR, re.sub(r"[^A-Za-z0-9.]", "_", host) + ".lock")
    with open(lf, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        s = f.read().strip()
        last = float(s) if s else 0.0
        wait = last + min_gap - time.time()
        if wait > 0:
            time.sleep(wait)
        f.seek(0)
        f.truncate()
        f.write(str(time.time()))
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


_SESSION = None


def _session():
    global _SESSION
    if _SESSION is None:
        from curl_cffi import requests as creq
        _SESSION = creq.Session(impersonate="chrome")
    return _SESSION


def fetch(url, cache_dir=None, binary=False, retries=3, min_gap=1.1, headers=None, refresh=False,
          timeout=60):
    """GET a URL politely. If cache_dir given, cache by sha1(url). Returns (status, content|text, final_url)."""
    cpath = None
    if cache_dir:
        ensure(cache_dir)
        h = hashlib.sha1(url.encode()).hexdigest()[:16]
        cpath = os.path.join(cache_dir, h + (".bin" if binary else ".html"))
        if os.path.exists(cpath) and not refresh and os.path.getsize(cpath) > 0:
            with open(cpath, "rb") as f:
                data = f.read()
            return 200, (data if binary else data.decode("utf-8", "replace")), url
    host = urlparse(url).netloc
    last_err = None
    for i in range(retries):
        _throttle(host, min_gap)
        try:
            r = _session().get(url, timeout=timeout, allow_redirects=True, headers=headers or {})
            if r.status_code == 200:
                if cpath:
                    with open(cpath, "wb") as f:
                        f.write(r.content)
                return 200, (r.content if binary else r.text), str(r.url)
            if r.status_code in (404, 410, 403):
                return r.status_code, (b"" if binary else ""), str(r.url)
            last_err = r.status_code
        except Exception as e:  # noqa
            last_err = repr(e)[:200]
        time.sleep(2 * (i + 1))
    return -1, (b"" if binary else str(last_err)), url


def download(url, dest_path, min_gap=1.1, headers=None, sec=False):
    """Download a document to dest_path (skip if exists). Returns True if file present."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return True
    ensure(os.path.dirname(dest_path))
    if sec:
        st, data, _ = sec_fetch(url, binary=True)
    else:
        st, data, _ = fetch(url, binary=True, min_gap=min_gap, headers=headers)
    if st == 200 and data:
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    print("download failed", st, url)
    return False


def sec_fetch(url, binary=False, retries=3):
    import requests
    host = "www.sec.gov" if "sec.gov" in url else urlparse(url).netloc
    for i in range(retries):
        _throttle("sec.gov", 0.6)
        try:
            r = requests.get(url, headers={"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"},
                             timeout=60)
            if r.status_code == 200:
                return 200, (r.content if binary else r.text), r.url
            if r.status_code == 404:
                return 404, (b"" if binary else ""), r.url
        except Exception as e:  # noqa
            pass
        time.sleep(3 * (i + 1))
    return -1, (b"" if binary else ""), url


# ---------------------------------------------------------------- text extraction
def pdf_to_text(path):
    import pymupdf
    out = []
    with pymupdf.open(path) as doc:
        for page in doc:
            out.append(page.get_text())
    return "\n".join(out)


def html_to_text(path_or_html, is_html=False):
    from bs4 import BeautifulSoup
    if is_html:
        html = path_or_html
    else:
        with open(path_or_html, "rb") as f:
            html = f.read().decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return txt


def extract_text(src_path, ticker, period, doctype, overwrite=False):
    """Extract text of a downloaded doc to ir_text/<TICKER>/<period>_<doctype>.txt. Returns out path."""
    out = os.path.join(txt_dir(ticker), f"{period}_{doctype}.txt")
    if os.path.exists(out) and not overwrite:
        return out
    low = src_path.lower()
    try:
        with open(src_path, "rb") as f:
            head = f.read(5)
        if head.startswith(b"%PDF"):
            txt = pdf_to_text(src_path)
        else:
            txt = html_to_text(src_path)
    except Exception as e:  # noqa
        print("extract failed", src_path, repr(e)[:120])
        return None
    with open(out, "w") as f:
        f.write(txt)
    return out


# ---------------------------------------------------------------- timing
def timing_class(ticker, hhmm, date=None):
    """BMO / INTRADAY / AMC relative to the home market's continuous session; UNKNOWN if no time."""
    if not hhmm or not re.match(r"^\d{1,2}:\d{2}$", str(hhmm)):
        return "UNKNOWN"
    tz, op, cl = MARKET[ticker]
    t = tuple(int(x) for x in hhmm.split(":"))
    o = tuple(int(x) for x in op.split(":"))
    c = tuple(int(x) for x in cl.split(":"))
    if t < o:
        return "BMO"
    if t >= c:
        return "AMC"
    return "INTRADAY"


def convert_time(date_str, hhmm, from_tz, to_tz):
    """Convert local time between tz names, returns HH:MM in to_tz (date may roll; returns (date, hhmm))."""
    from zoneinfo import ZoneInfo
    dt = datetime.strptime(f"{date_str} {hhmm}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(from_tz))
    d2 = dt.astimezone(ZoneInfo(to_tz))
    return d2.strftime("%Y-%m-%d"), d2.strftime("%H:%M")


# ---------------------------------------------------------------- writers / validators
def write_events(ticker, rows):
    df = pd.DataFrame(rows)
    for c in EVENT_COLS:
        if c not in df.columns:
            df[c] = ""
    df = df[EVENT_COLS].fillna("")
    df["ticker"] = ticker
    df["timezone"] = df["timezone"].replace("", MARKET[ticker][0])
    bad = df[~df.event_type.isin(EVENT_TYPES)]
    assert bad.empty, f"bad event_type: {bad.event_type.unique()}"
    badt = df[~df.timing.isin(TIMINGS)]
    assert badt.empty, f"bad timing: {badt.timing.unique()}"
    assert df.event_date.str.match(r"^\d{4}-\d{2}-\d{2}$").all(), "bad dates"
    df = df.sort_values(["event_date", "event_type"]).drop_duplicates(
        ["event_date", "event_type", "fiscal_period"])
    p = os.path.join(ensure(PROC_IR), f"{ticker}_events.csv")
    df.to_csv(p, index=False)
    return p, df


def write_kpis(ticker, rows):
    df = pd.DataFrame(rows)
    for c in KPI_COLS:
        if c not in df.columns:
            df[c] = ""
    df = df[KPI_COLS]
    df["ticker"] = ticker
    df = df.sort_values("period_end")
    p = os.path.join(ensure(PROC_IR), f"{ticker}_kpis.csv")
    df.to_csv(p, index=False)
    return p, df


def write_manifest(ticker, rows):
    df = pd.DataFrame(rows)
    for c in MANIFEST_COLS:
        if c not in df.columns:
            df[c] = ""
    df = df[MANIFEST_COLS].fillna("")
    df["ticker"] = ticker
    df = df.drop_duplicates("local_path").sort_values(["fiscal_period", "doc_type"])
    p = os.path.join(ensure(PROC_IR), f"{ticker}_manifest.csv")
    df.to_csv(p, index=False)
    return p, df


def grep(path, pattern, width=220, maxhits=8, flags=re.I):
    """Return short context snippets for a regex in a text file (token-economical inspection)."""
    with open(path, errors="replace") as f:
        txt = f.read()
    out = []
    for m in re.finditer(pattern, txt, flags):
        s = max(0, m.start() - width // 2)
        out.append(re.sub(r"\s+", " ", txt[s:m.end() + width // 2]))
        if len(out) >= maxhits:
            break
    return out
