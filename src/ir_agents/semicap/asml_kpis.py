"""Extract ASML KPIs per quarter from press-release text (EDGAR exhibits) -> list of dicts (JSON) for the writer."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
TX = irlib.text_dir(T)
idx = json.load(open(os.path.join(irlib.raw_dir(T), '_manifest_rows.json')))
PR = {r['fiscal_period']: r for r in idx if r['doc_type'] == 'press_release'}
NUM = r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?'
QEND = {'Q1': '03-31', 'Q2': '06-30', 'Q3': '09-30', 'Q4': '12-31'}


def tonum(s):
    return float(s.replace(',', ''))


def table(flat, per):
    i = flat.find('Figures in millions')
    if i < 0:
        return {}, None
    seg = flat[i:i + 2500]
    hdr = re.findall(r'\b(Q[1-4] 20\d\d|FY ?20\d\d)\b', seg[:200])
    q, y = per[4:], per[:4]
    cur = f'{q} {y}'
    col = hdr.index(cur) if cur in hdr else 1
    labels = [('revenue', r'(?:Total net sales|Net sales)'), ('ibm', r'\.\.\.of which Installed Base Management sales'),
              ('orders', r'(?:Net bookings|Systems net bookings|Net system bookings)'), ('backlog', r'(?:Systems backlog|Backlog)'),
              ('gm', r'Gross margin \(%\)')]
    out = {}
    stops = r'(?=\.\.\.of which|New lithography|Used lithography|Used systems|New systems|Average Selling|Net bookings|Systems backlog|Backlog|Gross profit|Gross margin|Net income|EPS|End-quarter|\(1\)|$)'
    for key, lab in labels:
        m = re.search(lab + r'\s*(.*?)' + stops, seg)
        if not m:
            continue
        toks = re.findall(NUM, m.group(1))
        vals = [t for t in toks if not re.fullmatch(r'[1-9]', t)]
        if len(vals) > col:
            out[key] = tonum(vals[col])
    return out, hdr


def guidance(flat, per):
    head = flat[:9000]
    txt, low, high, basis, fy = [], None, None, None, {}
    for s in re.split(r'(?<=[.])\s+|•', head):
        s2 = re.sub(r'^.*?Exhibit 99\.\d\s*', '', s.strip()).strip('"')
        s2 = re.sub(r'\s*VELDHOVEN, the Netherlands.*$', '', s2, flags=re.I)
        if re.search(r'(ASML (?:expects|guides|now expects|continues to expect|does not expect|refrains)|[Ww]e expect|For the (?:first|second|third|fourth)-quarter of)', s2) and len(s2) < 420:
            if s2 not in txt:
                txt.append(s2)
    k = lambda v, u: tonum(v) * (1000 if u == 'billion' else 1)
    y, q = int(per[:4]), int(per[5])
    nq, ny = (q + 1, y) if q < 4 else (1, y + 1)
    ordn = ['first', 'second', 'third', 'fourth'][nq - 1]
    QP = rf'(?:Q{nq}(?: {ny})?|{ordn}[- ]quarter(?: {ny})?|{ordn}[- ]quarter of {ny},? ASML expects|For the {ordn}-quarter of {ny},? ASML expects)'
    m = re.search(QP + r'[^.\d€]{0,40}?(?:total )?(?:net )?(?:sales|revenue) (?:at |of |to be )?(?:between |of between )(?:€|EUR )\s*(' + NUM + r')\s*(billion|million)?\s*and\s*(?:€|EUR )?\s*(' + NUM + r')\s*(billion|million)', head)
    m2 = re.search(QP + r'[^.\d€]{0,40}?(?:total )?(?:net )?(?:sales|revenue) (?:at |of |to be )?(?:approximately|around|about) (?:€|EUR )\s*(' + NUM + r')\s*(billion|million)', head)
    if m:
        u1 = m.group(2) or m.group(4)
        low, high, basis = k(m.group(1), u1), k(m.group(3), m.group(4)), 'next_quarter'
    elif m2:
        low = high = k(m2.group(1), m2.group(2)); basis = 'next_quarter'
    mf = re.search(r'(?<!Q[1-4] )(?<!quarter )(?:full.year )?(20\d\d) (?:total )?net sales (?:to be |of )?(?:between |in the range of )(?:€|EUR )\s*(' + NUM + r')\s*(billion|million)?\s*(?:and|to|-)\s*(?:€|EUR )?\s*(' + NUM + r')\s*(billion|million)', head)
    if not mf:
        mf = re.search(r'total net sales for (20\d\d) to be (?:between |in the range of )(?:€|EUR )\s*(' + NUM + r')\s*(billion|million)?\s*(?:and|to|-)\s*(?:€|EUR )?\s*(' + NUM + r')\s*(billion|million)', head)
    if mf:
        u1 = mf.group(3) or mf.group(5)
        fy = {'fy_guidance_year': mf.group(1), 'fy_guidance_low': k(mf.group(2), u1), 'fy_guidance_high': k(mf.group(4), mf.group(5))}
    return ' | '.join(txt)[:900], low, high, basis, fy


def backlog_text(flat):
    m = re.search(r'[Bb]acklog (?:at the end of 20\d\d )?(?:of |at )?(around |about |over |more than |approximately )?(?:€|EUR )\s*(' + NUM + r') billion', flat[:12000])
    if m:
        return {'backlog_stated_bn': tonum(m.group(2)), 'backlog_qualifier': (m.group(1) or 'exact').strip()}
    return {}


def ai_notes(flat):
    i = flat.find('CEO statement')
    body = flat[i:] if i >= 0 else flat[:12000]
    j = min([x for x in (body.find('Forward Looking Statements'), body.find('Private Securities'), body.find('About ASML')) if x > 0] or [9000])
    body = body[:j]
    sents = re.split(r'(?<=[.!?"”])\s+', body)
    keep = [s.strip() for s in sents if re.search(r'\bAI\b|artificial intelligence|China|Chinese|HBM|DRAM|[Mm]emory|[Ll]ogic|data cent|export|push.?out', s)
            and 'Securities' not in s]
    if not keep:
        keep = [s.strip() for s in sents if re.search(r'demand|recover|inventor|utiliz|cautious|uncertain|transition year', s) and 'Securities' not in s]
    out = ' '.join(keep[:5])
    return out[:700]


rows = []
for per in sorted(PR):
    r = PR[per]
    flat = ' '.join(open(os.path.join(TX, f'{per}_press_release.txt')).read().split())
    tb, hdr = table(flat, per)
    gtxt, glo, ghi, basis, fy = guidance(flat, per)
    extra = {'orders_definition': 'net (system) bookings; quarterly sum basis', 'source_table_header': hdr}
    if 'ibm' in tb:
        extra['installed_base_mgmt_sales'] = tb['ibm']
        if 'revenue' in tb and 'orders' in tb:
            sys_sales = tb['revenue'] - tb['ibm']
            extra['net_system_sales_derived'] = round(sys_sales, 1)
            extra['derived_btb_bookings_over_system_sales'] = round(tb['orders'] / sys_sales, 2) if sys_sales else None
    if basis:
        extra['guidance_basis'] = basis
    extra.update(fy)
    bt = backlog_text(flat)
    extra.update(bt)
    if tb.get('backlog') is not None:
        for kk in ('backlog_stated_bn', 'backlog_qualifier'):
            extra.pop(kk, None)
    if tb.get('backlog') is None and bt and bt['backlog_qualifier'] in ('exact', 'around', 'about', 'approximately'):
        tb['backlog'] = bt['backlog_stated_bn'] * 1000
    y, q = per[:4], per[4:]
    rows.append({'ticker': T, 'fiscal_period': per, 'period_end': f'{y}-{QEND[q]}', 'release_date': r['pub_date'],
                 'currency': 'EUR', 'unit': 'million', 'revenue': tb.get('revenue'), 'orders': tb.get('orders'),
                 'backlog': tb.get('backlog'), 'gross_margin_pct': tb.get('gm'), 'guidance_text': gtxt,
                 'guidance_rev_low': glo, 'guidance_rev_high': ghi, 'ai_dc_notes': ai_notes(flat), 'extra_json': extra,
                 'source_doc': r['local_path']})
byp = {r['fiscal_period']: r for r in rows}
for r in rows:
    y, q = int(r['fiscal_period'][:4]), r['fiscal_period'][4:]
    prev = byp.get(f'{y-1}{q}')
    for k, kk in [('revenue', 'revenue_yoy_pct'), ('orders', 'orders_yoy_pct')]:
        if prev and prev.get(k) and r.get(k):
            r[kk] = round((r[k] / prev[k] - 1) * 100, 1)
json.dump(rows, open(os.path.join(irlib.raw_dir(T), '_kpi_rows.json'), 'w'), indent=0)
for r in rows:
    print(r['fiscal_period'], r['revenue'], r['orders'], r['backlog'], r['gross_margin_pct'], r['guidance_rev_low'], r['guidance_rev_high'], r['extra_json'].get('fy_guidance_low'), r['extra_json'].get('fy_guidance_high'), '|', r['revenue_yoy_pct'] if 'revenue_yoy_pct' in r else '')
