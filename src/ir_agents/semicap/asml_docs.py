"""Download ASML quarterly documents listed on asml.com/en/investors/financial-results (2021Q1-2026Q3),
extract text, and build the manifest rows (saved as JSON for the final writer)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
T = 'ASML.AS'
links = json.load(open(os.path.join(irlib.raw_dir(T), '_finres_links.json')))
MAP = [(r'press release quarterly results', 'press_release', 'press_release'),
       (r'presentation investor relations', 'presentation', 'presentation'),
       (r'investor call prepared remarks', 'transcript', 'transcript'),
       (r'video transcript|transcript video', 'transcript', 'video_transcript'),
       (r'presentation press conference', 'presentation', 'press_presentation')]
rows = []
for L in links:
    lab = re.sub(r'^(PDF|ZIP) - ', '', L['label']).lower()
    for pat, dtype, fname in MAP:
        if re.fullmatch(pat, lab):
            break
    else:
        continue
    per = L['period']
    path = os.path.join(irlib.raw_dir(T), f'{per}_{fname}.pdf')
    st, b = irlib.fetch(L['url'], path)
    if st != 200 or not b.startswith(b'%PDF'):
        print('FAIL', per, fname, st, b[:20]); continue
    txt = irlib.to_text(path)
    tp = irlib.write_text(T, per, fname, txt)
    rows.append({'ticker': T, 'local_path': os.path.relpath(path, irlib.ROOT), 'url': L['url'], 'doc_type': dtype,
                 'fiscal_period': per, 'pub_date': '', 'text_path': os.path.relpath(tp, irlib.ROOT), 'fname': fname})
    print(per, fname, len(b) // 1024, 'KB', len(txt), 'chars')
json.dump(rows, open(os.path.join(irlib.raw_dir(T), '_manifest_rows.json'), 'w'), indent=0)
print('total', len(rows))
