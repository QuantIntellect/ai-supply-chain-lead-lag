"""Extract ABB quarterly KPIs from release + financial-information text (regex, no manual numbers)."""
import os, sys, re, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

T = 'ABBN.SW'
TXT = os.path.join(TEXT_IR, T)
NUM = r'\(?-?[\d,]+\)?'
PCT = r'[+\-]?\d+(?:\.\d+)?%'


def norm(s):
    s = s.replace('−', '-').replace('–', '-').replace('—', '—').replace('\xa0', ' ')
    s = re.sub(r'\(\d\)', '', s)          # footnote markers like (1)
    return re.sub(r'\s+', ' ', s)


def num(x):
    if x is None:
        return None
    neg = x.startswith('(') or x.startswith('-')
    v = float(x.strip('()').replace(',', '').replace('-', ''))
    return -v if neg else v


def pct(x):
    return None if x is None else float(x.replace('%', '').replace('+', ''))


def first(rx, s, flags=0):
    m = re.search(rx, s, flags)
    return m


def load(fp, dt):
    p = os.path.join(TXT, f'{fp}_{dt}.txt')
    return norm(open(p, encoding='utf-8').read()) if os.path.exists(p) else ''


def ba_block(rel, name):
    """Return the business-area key-figure block from the release."""
    m = re.search(r'— ?' + re.escape(name) + r' (?:CHANGE ){1,2}\(\$ millions', rel)
    if not m:
        m = re.search(re.escape(name) + r' (?:CHANGE ){1,2}\(\$ millions', rel)
    if not m:
        return ''
    return rel[m.start(): m.start() + 1200]


def ba_metrics(rel, name):
    b = ba_block(rel, name)
    if not b:
        return {}
    out = {}
    m = re.search(r'Orders (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r')', b)
    if m:
        out.update(orders=num(m.group(1)), orders_usd_pct=pct(m.group(3)), orders_comp_pct=pct(m.group(4)))
    m = re.search(r'Order backlog (' + NUM + r') (' + NUM + r') (' + PCT + r')', b)
    if m:
        out.update(backlog=num(m.group(1)))
    m = re.search(r'Revenues (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r')', b)
    if m:
        out.update(revenue=num(m.group(1)), revenue_usd_pct=pct(m.group(3)), revenue_comp_pct=pct(m.group(4)))
    m = re.search(r'as % of operational revenues (\d+\.\d)%', b)
    if m:
        out.update(op_ebita_margin=float(m.group(1)))
    return out


def fin_table_start(fin, label, group_val):
    """Find '<label> ABB Group <cur> <prior>' table whose group value equals group_val."""
    for m in re.finditer(re.escape(label) + r' ABB Group (' + NUM + r') (' + NUM + r') ', fin):
        if group_val is None or abs(num(m.group(1)) - group_val) < 1:
            return m.start()
    return -1


def fin_ba(fin, name, g_orders, g_rev):
    out = {}
    rxrow = re.escape(name) + r' (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r') (' + PCT + r')'
    i = fin_table_start(fin, 'Orders', g_orders)
    if i >= 0:
        m = re.search(rxrow, fin[i:i + 700])
        if m:
            out.update(orders=num(m.group(1)), orders_usd_pct=pct(m.group(3)), orders_comp_pct=pct(m.group(5)))
    i = fin_table_start(fin, 'Revenues', g_rev)
    if i >= 0:
        m = re.search(rxrow, fin[i:i + 700])
        if m:
            out.update(revenue=num(m.group(1)), revenue_usd_pct=pct(m.group(3)), revenue_comp_pct=pct(m.group(5)))
    m = re.search(r'Order backlog \(end \w+\) ABB Group', fin)
    if m:
        mm = re.search(rxrow, fin[m.start():m.start() + 700])
        if mm:
            out.update(backlog=num(mm.group(1)), backlog_comp_pct=pct(mm.group(5)))
    return out


def sentences_with(s, rx, maxn=3, maxlen=260):
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z•])', s)
    out = []
    for x in sents:
        if re.search(rx, x, re.I):
            x = x.strip()
            if len(x) > maxlen:
                x = x[:maxlen] + '…'
            if x not in out:
                out.append(x)
        if len(out) >= maxn:
            break
    return out


ev = {r['fiscal_period']: r['event_date'] for r in csv.DictReader(open(os.path.join(PROC_IR, f'{T}_events.csv')))
      if r['event_type'] in ('Q1', 'Q2', 'Q3', 'Q4')}
QEND = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}
rows = []
fps = sorted({f.split('_')[0] for f in os.listdir(TXT) if f.endswith('_release.txt')})
for fp in fps:
    if fp < '2022Q1':
        continue
    rel, fin = load(fp, 'release'), load(fp, 'fininfo')
    y, q = int(fp[:4]), int(fp[-1])
    kf = fin[fin.find('Key Figures'):][:2500] if 'Key Figures' in fin else ''
    src = 'fininfo'
    if not kf:
        kf = rel[rel.find('KEY FIGURES'):][:2500]
        src = 'release'
    r = dict(fiscal_period=fp, period_end=f'{y}-{QEND[q]}', release_date=ev.get(fp, ''), currency='USD',
             unit='USD m', source_doc=f'data/processed/ir_text/{T}/{fp}_release.txt; {fp}_fininfo.txt')
    ex = {}
    m = first(r'Orders (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r')', kf)
    if m:
        r['orders'] = num(m.group(1)); r['orders_yoy_pct'] = pct(m.group(3)); ex['orders_comparable_pct'] = pct(m.group(4))
    m = first(r'Order backlog \(end \w+\) (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r')', kf)
    if m:
        r['backlog'] = num(m.group(1)); ex['backlog_usd_pct'] = pct(m.group(3)); ex['backlog_comparable_pct'] = pct(m.group(4))
    m = first(r'Revenues (' + NUM + r') (' + NUM + r') (' + PCT + r') (' + PCT + r')', kf)
    if m:
        r['revenue'] = num(m.group(1)); r['revenue_yoy_pct'] = pct(m.group(3)); ex['revenue_comparable_pct'] = pct(m.group(4))
    m = first(r'Gross Profit (' + NUM + r') (' + NUM + r') (?:' + PCT + r' )?as % of revenues (\d+\.\d)%', kf)
    if m:
        r['gross_margin_pct'] = float(m.group(3))
    m = first(r'Operational EBITA (' + NUM + r') (' + NUM + r') .{0,60}?as % of operational revenues (\d+\.\d)%', kf)
    if m:
        ex['op_ebita'] = num(m.group(1)); ex['op_ebita_margin_pct'] = float(m.group(3))
    # book-to-bill: stated in release text, else computed
    m = first(r'book-to-bill(?: ratio)?(?: of| was| at| reached| came in at| amounted to)? (\d\.\d{1,2})', rel, re.I)
    comp = round(r['orders'] / r['revenue'], 2) if r.get('orders') and r.get('revenue') else None
    if m and comp is not None and abs(float(m.group(1)) - comp) <= 0.03:
        r['book_to_bill'] = float(m.group(1)); ex['book_to_bill_source'] = 'stated'
    elif comp is not None:
        r['book_to_bill'] = comp; ex['book_to_bill_source'] = 'computed orders/revenues'
    # business areas
    for name, key in [('Electrification', 'EL'), ('Motion', 'MO'), ('Process Automation', 'PA'),
                      ('Robotics & Discrete Automation', 'RA'), ('Machine Automation', 'MA'), ('Automation', 'AU')]:
        bm = fin_ba(fin, name, r.get('orders'), r.get('revenue'))
        rb = ba_metrics(rel, name)
        if rb.get('op_ebita_margin') is not None:
            bm['op_ebita_margin'] = rb['op_ebita_margin']
        for k2 in ('orders', 'orders_comp_pct', 'revenue', 'revenue_comp_pct', 'backlog'):
            if bm.get(k2) is None and rb.get(k2) is not None:
                bm[k2] = rb[k2]
        if bm:
            ex[key] = bm
    # outlook / guidance
    oi = rel.find('Outlook')
    gl = [x for x in sentences_with(rel, r'^(?:Morten Wierod CEO |Björn Rosengren CEO )?In (?:the )?(?:first|second|third|fourth|full-year|full year)[^.]{0,40}(?:we expect|we anticipate)', maxn=4, maxlen=330)]
    gl = [re.sub(r'^(?:Morten Wierod|Björn Rosengren) CEO ', '', x) for x in gl]
    r['guidance_text'] = ' | '.join(gl)[:900]
    for x in gl:
        mm = re.search(r'revenue growth[^.]{0,40}?(\d+(?:\.\d+)?)\s?%?\s?(?:-|to)\s?(\d+(?:\.\d+)?)\s?%', x)
        if not mm:
            continue
        if re.match(r'In full-?\s?year', x, re.I) and 'revenue' in x:
            r['guidance_rev_low'] = float(mm.group(1)); r['guidance_rev_high'] = float(mm.group(2))
            ex['guidance_basis'] = 'FY comparable revenue growth %'
        elif re.match(r'In (?:the )?(?:first|second|third|fourth) quarter', x, re.I) and 'revenue' in x:
            ex['next_q_comp_rev_growth_pct'] = [float(mm.group(1)), float(mm.group(2))]
    dc = sentences_with(rel, r'data ?cent', maxn=8, maxlen=280)
    dc = sorted(dc, key=lambda x: 0 if re.search(r'order|demand|growth|digit|\d%', x, re.I) else 1)[:3]
    if not dc:
        pres = load(fp, 'presentation')
        wins = [pres[max(0, m.start() - 90):m.end() + 90].strip() for m in re.finditer(r'data ?cent', pres, re.I)]
        dc = ['[presentation] ' + w for w in wins if re.search(r'order|growth|strong|strength|demand|increase|decline', w, re.I)][:2]
    r['ai_dc_notes'] = ' | '.join(dc)[:900]
    r['extra_json'] = ex
    rows.append(r)
# ---- older quarters (2015Q1-2021Q4): release key-figures table only (cheap pass) ----
CHG = r'([+\-]?\d+%|steady|n\.a\.)'
for fp in fps:
    if fp >= '2022Q1' or fp < '2015Q1':
        continue
    rel = load(fp, 'release')
    y, q = int(fp[:4]), int(fp[-1])
    i = rel.lower().find('key figures')
    kf = rel[i:i + 3000] if i >= 0 else rel[:6000]
    hdr = kf[:400].lower()
    basis = 'like-for-like' if 'like-for' in hdr else ('local currency' if 'local' in hdr and 'compar' not in hdr else 'comparable')
    r = dict(fiscal_period=fp, period_end=f'{y}-{QEND[q]}', release_date=ev.get(fp, ''), currency='USD',
             unit='USD m', source_doc=f'data/processed/ir_text/{T}/{fp}_release.txt')
    basis = 'like-for-like' if fp < '2016Q1' else basis  # 2015 releases report like-for-like growth (checked 2015Q1, 2015Q3)
    ex = {'growth_basis': basis, 'coverage': 'release key-figures table only (pre-2022 cheap pass)'}
    def chg(x):
        return 0.0 if x == 'steady' else (None if x == 'n.a.' else pct(x))
    m = re.search(r'Orders\d? (' + NUM + r') (' + NUM + r') ' + CHG + r' ' + CHG, kf)
    if m:
        r['orders'] = num(m.group(1)); r['orders_yoy_pct'] = chg(m.group(3)); ex['orders_comparable_pct'] = chg(m.group(4))
    m = re.search(r'Revenues\d? (' + NUM + r') (' + NUM + r') ' + CHG + r' ' + CHG, kf)
    if m:
        r['revenue'] = num(m.group(1)); r['revenue_yoy_pct'] = chg(m.group(3)); ex['revenue_comparable_pct'] = chg(m.group(4))
    m = re.search(r'Operational EBITA\d? (' + NUM + r') (' + NUM + r') .{0,60}?% of operational revenues\d? (\d+\.\d)%', kf)
    if m:
        ex['op_ebita'] = num(m.group(1)); ex['op_ebita_margin_pct'] = float(m.group(3))
    if r.get('orders') and r.get('revenue'):
        r['book_to_bill'] = round(r['orders'] / r['revenue'], 2); ex['book_to_bill_source'] = 'computed orders/revenues'
    dc = sentences_with(rel, r'data ?cent', maxn=2, maxlen=280)
    r['ai_dc_notes'] = ' | '.join(dc)[:600]
    r['extra_json'] = ex
    rows.append(r)

p = write_kpis(T, rows)
print(p, len(rows))
for r in rows:
    ex = r['extra_json'] if isinstance(r['extra_json'], dict) else json.loads(r['extra_json'])
    print(r['fiscal_period'], r.get('orders'), r.get('orders_yoy_pct'), ex.get('orders_comparable_pct'), r.get('revenue'),
          r.get('revenue_yoy_pct'), ex.get('revenue_comparable_pct'), r.get('book_to_bill'), ex.get('book_to_bill_source', '')[:4],
          r.get('backlog'), r.get('gross_margin_pct'), ex.get('op_ebita_margin_pct'),
          'EL' in ex and (ex['EL'].get('orders'), ex['EL'].get('orders_comp_pct'), ex['EL'].get('op_ebita_margin')),
          r.get('guidance_rev_low'), len(r.get('ai_dc_notes', '')))
