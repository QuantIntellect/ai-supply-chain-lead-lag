"""Validate semicap IR outputs against the required schemas; print a compact coverage summary."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
import pandas as pd
for t in ['ASML.AS', 'ASM.AS', 'BESI.AS', 'AIXA.DE', 'VACN.SW']:
    out = []
    pe = os.path.join(irlib.PROC_IR, f'{t}_events.csv')
    if not os.path.exists(pe):
        print(t, 'NO EVENTS FILE'); continue
    e = pd.read_csv(pe, dtype=str).fillna('')
    k = pd.read_csv(os.path.join(irlib.PROC_IR, f'{t}_kpis.csv'), dtype=str).fillna('') if os.path.exists(os.path.join(irlib.PROC_IR, f'{t}_kpis.csv')) else None
    m = pd.read_csv(os.path.join(irlib.PROC_IR, f'{t}_manifest.csv'), dtype=str).fillna('') if os.path.exists(os.path.join(irlib.PROC_IR, f'{t}_manifest.csv')) else None
    notes = os.path.exists(os.path.join(irlib.PROC_IR, f'{t}_notes.md'))
    issues = []
    if list(e.columns) != irlib.EVENT_COLS: issues.append('event cols')
    if k is not None and list(k.columns) != irlib.KPI_COLS: issues.append('kpi cols')
    if m is not None and list(m.columns) != irlib.MANIFEST_COLS: issues.append('manifest cols')
    bad_et = set(e.event_type) - irlib.EVENT_TYPES
    if bad_et: issues.append(f'bad event_type {bad_et}')
    bad_tm = set(e.timing) - {'BMO', 'AMC', 'INTRADAY', 'UNKNOWN'}
    if bad_tm: issues.append(f'bad timing {bad_tm}')
    # timing consistency with time
    inc = e[(e.event_time_local != '') & (e.apply(lambda r: irlib.timing_class(r.event_time_local) != r.timing, axis=1))]
    if len(inc): issues.append(f'{len(inc)} timing/time mismatches e.g. {inc.iloc[0].event_date} {inc.iloc[0].event_time_local} {inc.iloc[0].timing}')
    if (e.event_date > '2026-10-23').any(): issues.append('future events')
    if e.duplicated(['event_date', 'event_type', 'fiscal_period']).any(): issues.append('dup events')
    miss = 0
    if m is not None:
        miss = sum(1 for p in m.local_path if not os.path.exists(os.path.join(irlib.ROOT, p)))
        if miss: issues.append(f'{miss} manifest paths missing')
    print(f"{t}: events {len(e)} [{e.event_date.min()}..{e.event_date.max()}] timing={e.timing.value_counts().to_dict()} types={e.event_type.value_counts().to_dict()}")
    if k is not None:
        cov = {c: int((k[c] != '').sum()) for c in ['revenue', 'orders', 'book_to_bill', 'backlog', 'gross_margin_pct', 'guidance_rev_low', 'ai_dc_notes']}
        print(f"   kpis {len(k)} [{k.fiscal_period.min()}..{k.fiscal_period.max()}] filled={cov}")
    if m is not None:
        print(f"   manifest {len(m)} {m.doc_type.value_counts().to_dict()} notes={notes}")
    print('   ISSUES:', issues or 'none')
