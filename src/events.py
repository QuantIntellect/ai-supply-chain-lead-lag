"""Build the earnings-event calendar with precise reaction sessions.

Sources (priority): IR calendars collected per EU company (data/processed/ir/<T>_events.csv)
                    > EDGAR 8-K item 2.02 accepted time (US filers)
                    > Yahoo earnings dates (validated with abnormal volume).
Every event gets an estimated UTC timestamp, so the reaction session can be computed on any
exchange: the first session of that exchange whose close is after the event time.

Output: data/processed/events.parquet
"""
import os
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC, load_universe
from panel import exchange_of

PANEL = os.path.join(PROC, "panel")
SEC_FOREIGN = {"ASML.AS", "STMPA.PA", "NOKIA.HE", "SAP.DE", "TSM", "ARM", "NBIS", "CLS", "IREN"}


def session_bounds_utc(ticker, dates):
    """UTC open/close timestamps of the ticker's exchange for the given local dates."""
    tz, o, c = exchange_of(ticker)
    d = pd.DatetimeIndex(dates)
    opens = pd.DatetimeIndex([pd.Timestamp(f"{x.date()} {o}").tz_localize(tz) for x in d]).tz_convert("UTC")
    closes = pd.DatetimeIndex([pd.Timestamp(f"{x.date()} {c}").tz_localize(tz) for x in d]).tz_convert("UTC")
    return opens, closes


class Calendar:
    """Trading days per ticker (from returns panel) with session bounds in UTC."""

    def __init__(self, ret):
        self.days, self.opens, self.closes = {}, {}, {}
        for tk in ret.columns:
            d = ret[tk].dropna().index
            self.days[tk] = d
            self.opens[tk], self.closes[tk] = session_bounds_utc(tk, d)

    def reaction_day(self, ticker, ts_utc):
        """First session whose close is after ts; returns (date, partial_flag)."""
        closes = self.closes[ticker]
        i = closes.searchsorted(ts_utc, side="right")
        if i >= len(closes):
            return None, False
        partial = bool(self.opens[ticker][i] < ts_utc)
        return self.days[ticker][i], partial


# Typical release convention when only the reaction day is known: (rule, local time, tz)
#   BMO: released that morning before the open; AMC: released after the previous session's close
TIMING_OVERRIDE = {
    "TSM": ("BMO", "02:00", "America/New_York"),        # TSMC releases ~14:00 Taipei = before US open
    "ARM": ("AMC", "16:05", "America/New_York"), "CLS": ("AMC", "16:05", "America/New_York"),
    "IREN": ("AMC", "16:05", "America/New_York"), "NBIS": ("BMO", "07:00", "America/New_York"),
    "000660.KS": ("BMO", "08:00", "Asia/Seoul"), "005930.KS": ("BMO", "08:00", "Asia/Seoul"),
}
SUFFIX_TIMING = {".TW": ("AMC", "14:30"), ".T": ("AMC", "15:30"), ".KS": ("BMO", "08:00")}


def default_release_ts(tk, d, days):
    tz, o, c = exchange_of(tk)
    rule, tm = "BMO", "07:00"
    for suf, (r, t) in SUFFIX_TIMING.items():
        if tk.endswith(suf):
            rule, tm = r, t
    if tk in TIMING_OVERRIDE:
        rule, tm, tz = TIMING_OVERRIDE[tk]
    day = d
    if rule == "AMC":
        i = days.get_loc(d)
        day = days[i - 1] if i > 0 else d - pd.Timedelta(days=1)
    return pd.Timestamp(f"{day.date()} {tm}").tz_localize(tz).tz_convert("UTC")


def edgar_events():
    idx = pd.read_parquet(os.path.join(PROC, "edgar_earnings_index.parquet"))
    e = idx[idx.form.str.startswith("8-K") & idx["items"].fillna("").str.contains("2.02")].copy()
    e = e[e.accepted_et.notna()]
    e["ts_et"] = pd.to_datetime(e.accepted_et).dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
    e = e[e.ts_et.notna()].sort_values(["ticker", "ts_et"])
    # collapse multiple 2.02 filings within 3 days (amendments, follow-ups) -> keep first
    e["gap"] = e.groupby("ticker").ts_et.diff().dt.total_seconds() / 86400
    e = e[(e.gap.isna()) | (e.gap > 3)]
    return pd.DataFrame({"ticker": e.ticker, "ts_utc": e.ts_et.dt.tz_convert("UTC"), "source": "edgar_8k",
                         "ts_quality": "exact", "accession": e.accessionNumber})


def ir_events():
    rows = []
    for f in glob.glob(os.path.join(PROC, "ir", "*_events.csv")):
        try:
            df = pd.read_csv(f, dtype=str).fillna("")
        except Exception:
            continue
        for r in df.itertuples():
            if not r.event_date or r.event_type in ("CMD",):
                continue
            tz = r.timezone if getattr(r, "timezone", "") else exchange_of(r.ticker)[0]
            tm = (r.event_time_local or "").strip()
            timing = (r.timing or "UNKNOWN").upper()
            if not tm:
                tm = {"BMO": "07:00", "AMC": "18:00", "INTRADAY": "12:00"}.get(timing, "")
                quality = "timing_class" if tm else "date_only"
                tm = tm or "07:00"
            else:
                quality = "exact"
            try:
                ts = pd.Timestamp(f"{r.event_date} {tm[:5]}").tz_localize(tz).tz_convert("UTC")
            except Exception:
                continue
            rows.append({"ticker": r.ticker, "ts_utc": ts, "source": "ir", "ts_quality": quality,
                         "event_type": r.event_type, "fiscal_period": getattr(r, "fiscal_period", "")})
    return pd.DataFrame(rows)


def yahoo_events():
    y = pd.read_parquet(os.path.join(PROC, "yahoo_earnings_dates.parquet"))
    y = y[y.eps_act.notna() | y.surprise_pct.notna()]  # realized events only
    y["ts_utc"] = pd.to_datetime(y.earn_ts_utc, utc=True)
    return y


def main():
    ret = pd.read_parquet(os.path.join(PANEL, "ret.parquet"))
    av = pd.read_parquet(os.path.join(PANEL, "abvol.parquet"))
    ar = pd.read_parquet(os.path.join(PANEL, "abret.parquet"))
    cal = Calendar(ret)
    uni = load_universe()
    yh = yahoo_events()
    ed = edgar_events()
    ir = ir_events()
    print("edgar events", len(ed), "ir events", len(ir), "yahoo realized", len(yh))
    events = []
    for tk in uni.ticker:
        if tk not in cal.days:
            continue
        days = cal.days[tk]
        own = []
        if len(ir) and tk in set(ir.ticker):
            own = ir[ir.ticker == tk].assign(av_check=False).to_dict("records")
        elif tk in set(ed.ticker) and tk not in SEC_FOREIGN:
            own = ed[ed.ticker == tk].assign(av_check=False).to_dict("records")
            # add Yahoo events that EDGAR misses (companies that skip item 2.02 8-Ks some quarters)
            et = ed[ed.ticker == tk].ts_utc
            for r in yh[yh.ticker == tk].itertuples():
                if et.empty or (et - r.ts_utc).abs().min() > pd.Timedelta(days=4):
                    own.append({"ticker": tk, "ts_utc": r.ts_utc, "source": "yahoo", "ts_quality": "approx",
                                "av_check": True})
        else:
            for r in yh[yh.ticker == tk].itertuples():
                own.append({"ticker": tk, "ts_utc": r.ts_utc, "source": "yahoo", "ts_quality": "approx",
                            "av_check": True})
        for ev in own:
            ts = ev["ts_utc"]
            if ts < pd.Timestamp("2014-09-01", tz="UTC"):
                continue
            d, partial = cal.reaction_day(tk, ts)
            if d is None:
                continue
            if ev["av_check"]:
                # Yahoo dates/times are approximate: pick the max abnormal-volume day in [d-2, d+2]
                i = days.get_loc(d)
                cand = days[max(0, i - 2): i + 3]
                v = av[tk].reindex(cand)
                if v.notna().any():
                    d = v.idxmax()
                ts = default_release_ts(tk, d, days)
                partial = False
            ev.update({"react_date": d, "partial": partial, "ts_utc": ts,
                       "av": av[tk].get(d, np.nan), "ar": ar[tk].get(d, np.nan)})
            events.append(ev)
    E = pd.DataFrame(events)
    E = E.sort_values(["ticker", "react_date"]).drop_duplicates(["ticker", "react_date"])
    # attach Yahoo EPS surprise (nearest within 4 days)
    yh2 = yh[["ticker", "ts_utc", "eps_est", "eps_act", "surprise_pct"]].rename(columns={"ts_utc": "y_ts"})
    E = E.sort_values("ts_utc")
    yh2 = yh2.sort_values("y_ts")
    E = pd.merge_asof(E, yh2, left_on="ts_utc", right_on="y_ts", by="ticker", direction="nearest",
                      tolerance=pd.Timedelta(days=4))
    E = E.sort_values(["ticker", "react_date"]).reset_index(drop=True)
    E["event_id"] = E.ticker + "_" + E.react_date.dt.strftime("%Y%m%d")
    E.to_parquet(os.path.join(PROC, "events.parquet"), index=False)
    print("events:", len(E), "tickers:", E.ticker.nunique())
    print(E.groupby("source").agg(n=("ticker", "size"), med_av=("av", "median"),
                                  share_av_gt2=("av", lambda x: (x > 2).mean())).round(2))
    low = E[(E.react_date >= "2023-01-01") & (E.av < 1.5)]
    print("AI-era events with weak volume confirmation (av<1.5):", len(low))
    print(low.groupby("ticker").size().sort_values(ascending=False).head(15).to_string())


if __name__ == "__main__":
    main()
