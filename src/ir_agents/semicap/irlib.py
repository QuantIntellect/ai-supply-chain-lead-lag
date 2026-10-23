"""Shared helpers for the European semicap IR collection (ASML.AS, ASM.AS, BESI.AS, AIXA.DE, VACN.SW).

CONVENTIONS (apply identically for every company)
  * Directories: raw downloads -> data/raw/ir/<TICKER>/ ; text -> data/processed/ir_text/<TICKER>/<period>_<doctype>.txt
    outputs -> data/processed/ir/<TICKER>_{events,kpis,manifest}.csv and <TICKER>_notes.md  (TICKER = Yahoo ticker).
  * Dates ISO YYYY-MM-DD (local date of publication). Times HH:MM 24h local. timezone = IANA name of home market
    (Europe/Amsterdam for ASML/ASM/BESI, Europe/Berlin for AIXA, Europe/Zurich for VACN).
  * timing: home exchange continuous session 09:00-17:30 local (Euronext Amsterdam, Xetra, SIX).
        time < 09:00 -> BMO ; time >= 17:30 -> AMC ; otherwise INTRADAY ; no time -> UNKNOWN.
        Weekend/holiday publications keep the time-based class (note it in notes.md).
    A company-wide publication-time convention may be applied to un-timestamped releases ONLY after verifying it on
    >=3 timestamped releases in different years with no exceptions; otherwise leave time blank / UNKNOWN.
    Never use EDGAR acceptanceDateTime as the release time (6-Ks are filed hours later) - use it only to cross-check dates.
  * fiscal_period: 2025Q3, 2025H1, 2025FY. Combined Q4+FY release of a quarterly reporter -> event_type Q4,
    fiscal_period 2025Q4. FY only for semi-annual reporters (VAT) or separate annual publications.
    VAT Q1/Q3 order/sales updates -> event_type trading_update, fiscal_period 2025Q1 / 2025Q3.
    Pre-announced/preliminary quarterly figures -> prelim. Guidance cuts / ad-hoc negative updates -> profit_warning.
    Other unscheduled updates -> trading_update. Capital markets / investor days -> CMD (fiscal_period blank).
  * KPI units: currency = EUR/CHF, unit = "million" (all money columns in millions). Percentages as numbers (e.g. 51.6).
    revenue_yoy_pct / orders_yoy_pct only if computable from stated numbers or stated in the doc.
    Leave blank anything not stated; never estimate. KPI definitions (net bookings vs order intake, etc.) -> extra_json.
  * Manifest doc_type: press_release | presentation | transcript | interim_report | annual_report | other.
"""
import os
import re
import time
import json
import csv
from urllib.parse import urlparse

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAW_IR = os.path.join(ROOT, "data", "raw", "ir")
PROC_IR = os.path.join(ROOT, "data", "processed", "ir")
TEXT_IR = os.path.join(ROOT, "data", "processed", "ir_text")

WEB_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126 Safari/537.36")
SEC_UA = "aimapping-research research@example.org"

TZ = {"ASML.AS": "Europe/Amsterdam", "ASM.AS": "Europe/Amsterdam", "BESI.AS": "Europe/Amsterdam",
      "AIXA.DE": "Europe/Berlin", "VACN.SW": "Europe/Zurich"}

EVENT_COLS = ["ticker", "event_date", "event_time_local", "timezone", "timing", "event_type", "fiscal_period",
              "source_url"]
KPI_COLS = ["ticker", "fiscal_period", "period_end", "release_date", "currency", "unit", "revenue",
            "revenue_yoy_pct", "orders", "orders_yoy_pct", "book_to_bill", "backlog", "gross_margin_pct",
            "guidance_text", "guidance_rev_low", "guidance_rev_high", "ai_dc_notes", "extra_json", "source_doc"]
MANIFEST_COLS = ["ticker", "local_path", "url", "doc_type", "fiscal_period", "pub_date"]
EVENT_TYPES = {"Q1", "Q2", "Q3", "Q4", "H1", "FY", "trading_update", "profit_warning", "prelim", "CMD"}

_last_hit = {}
_session = None


def ensure(p):
    os.makedirs(p, exist_ok=True)
    return p


def raw_dir(ticker):
    return ensure(os.path.join(RAW_IR, ticker))


def text_dir(ticker):
    return ensure(os.path.join(TEXT_IR, ticker))


def session():
    global _session
    if _session is None:
        from curl_cffi import requests as cr
        _session = cr.Session(impersonate="chrome")
    return _session


def throttle(url, min_gap=1.1):
    host = urlparse(url).netloc
    dt = time.time() - _last_hit.get(host, 0)
    if dt < min_gap:
        time.sleep(min_gap - dt)
    _last_hit[host] = time.time()


def fetch(url, path=None, sec=False, timeout=60, min_gap=1.1, retries=2):
    """GET url politely. If path given: cache (skip if exists & non-empty) and return bytes. Returns (status, bytes)."""
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        return 200, open(path, "rb").read()
    last = None
    for attempt in range(retries + 1):
        throttle(url, min_gap)
        try:
            if sec:
                import requests
                r = requests.get(url, headers={"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"},
                                 timeout=timeout)
            else:
                r = session().get(url, timeout=timeout)
            if r.status_code == 200 and path:
                ensure(os.path.dirname(path))
                with open(path, "wb") as f:
                    f.write(r.content)
            if r.status_code in (429, 503) and attempt < retries:
                time.sleep(5 * (attempt + 1))
                continue
            return r.status_code, r.content
        except Exception as e:  # network error
            last = e
            time.sleep(3)
    print("FETCH-ERR", url, str(last)[:150])
    return -1, b""


def html_to_text(b):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(b, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    return txt.strip()


def pdf_to_text(path):
    import pymupdf
    out = []
    with pymupdf.open(path) as doc:
        for page in doc:
            out.append(page.get_text())
    return "\n".join(out)


def to_text(path):
    low = path.lower()
    data = open(path, "rb").read()
    if low.endswith(".pdf") or data[:5] == b"%PDF-":
        return pdf_to_text(path)
    return html_to_text(data)


def write_text(ticker, period, doctype, text):
    p = os.path.join(text_dir(ticker), f"{period}_{doctype}.txt")
    with open(p, "w") as f:
        f.write(text)
    return p


def timing_class(hhmm):
    if not hhmm:
        return "UNKNOWN"
    h, m = map(int, hhmm.split(":"))
    mins = h * 60 + m
    if mins < 9 * 60:
        return "BMO"
    if mins >= 17 * 60 + 30:
        return "AMC"
    return "INTRADAY"


def _write(path, cols, rows, sort_keys=None):
    import pandas as pd
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    if sort_keys:
        df = df.sort_values(sort_keys, kind="stable")
    ensure(os.path.dirname(path))
    df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)
    return df


def write_events(ticker, rows):
    for r in rows:
        assert r["event_type"] in EVENT_TYPES, r
        r.setdefault("timezone", TZ[ticker])
        if not r.get("timing"):
            r["timing"] = timing_class(r.get("event_time_local", ""))
    return _write(os.path.join(PROC_IR, f"{ticker}_events.csv"), EVENT_COLS, rows, ["event_date", "event_type"])


def write_kpis(ticker, rows):
    for r in rows:
        if isinstance(r.get("extra_json"), (dict, list)):
            r["extra_json"] = json.dumps(r["extra_json"], ensure_ascii=False)
    return _write(os.path.join(PROC_IR, f"{ticker}_kpis.csv"), KPI_COLS, rows, ["fiscal_period"])


def write_manifest(ticker, rows):
    return _write(os.path.join(PROC_IR, f"{ticker}_manifest.csv"), MANIFEST_COLS, rows, ["pub_date", "doc_type"])


def grep(path, pattern, width=160, maxhits=12, flags=re.I):
    """Print short context snippets around regex matches in a text file (token-economical inspection)."""
    t = open(path, errors="ignore").read()
    n = 0
    for m in re.finditer(pattern, t, flags):
        s = max(0, m.start() - width)
        e = min(len(t), m.end() + width)
        print("...", " ".join(t[s:e].split()), "...")
        n += 1
        if n >= maxhits:
            break
    return n
