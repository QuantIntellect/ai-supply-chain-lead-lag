"""Capgemini-specific helpers: parse event-page publication cards; period mapping."""
import re
from bs4 import BeautifulSoup

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for c in soup.select("div.card-content"):
        tag = c.select_one(".card-tag"); title = c.select_one(".card-title")
        day = c.select_one(".card-date-day"); tm = c.select_one(".card-date-time")
        dl = c.select_one("a.button--download"); view = c.select_one("a.button-link")
        out.append({
            "type": tag.get_text(strip=True) if tag else None,
            "title": re.sub(r"\s+", " ", title.get_text(" ", strip=True)) if title else None,
            "date": re.sub(r"\s+", " ", day.get_text(" ", strip=True)) if day else None,
            "time": re.sub(r"\s*\(CET\)", "", tm.get_text(" ", strip=True)) if tm else None,
            "file": dl["href"] if dl else None,
            "view": view["href"] if view else None,
            "filetype": (re.search(r"(pdf|xlsx|zip|docx|pptx|mp3|mp4)", dl.get_text(" ", strip=True)).group(1)
                         if dl and re.search(r"(pdf|xlsx|zip|docx|pptx|mp3|mp4)", dl.get_text(" ", strip=True)) else None),
        })
    return out

def to_iso(datestr):
    m = re.match(r"(\w+) (\d{1,2}), (\d{4})", datestr.strip())
    if not m:
        return None
    return "%s-%02d-%02d" % (m.group(3), MONTHS.index(m.group(1)) + 1, int(m.group(2)))

def to_hhmm(t):
    if not t:
        return ""
    m = re.match(r"(\d{1,2}):(\d{2}) ([ap])m", t.strip())
    if not m:
        return ""
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "p" else 0)
    return "%02d:%s" % (h, m.group(2))

def timing(hhmm):
    """Euronext Paris continuous session 09:00-17:30 local."""
    if not hhmm:
        return "UNKNOWN"
    if hhmm < "09:00":
        return "BMO"
    if hhmm >= "17:30":
        return "AMC"
    return "INTRADAY"

def event_period(slug):
    """Map an event slug like 'q3-2025-revenues' / 'h1-2026-results' / 'fy-2025-results' to (event_type, fiscal_period)."""
    m = re.search(r"\b(q[1-4])-(\d{4})", slug) or re.search(r"(\d{4})-(q[1-4])", slug)
    if m:
        a, b = m.groups()
        q, y = (a, b) if a.startswith("q") else (b, a)
        return q.upper(), "%s%s" % (y, q.upper())
    m = re.search(r"h1-(\d{4})", slug)
    if m:
        return "H1", "%sH1" % m.group(1)
    m = re.search(r"fy-(\d{4})", slug)
    if m:
        return "FY", "%sFY" % m.group(1)
    return None, None
