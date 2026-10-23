"""Slowly fetch remaining StockTitan ASML list pages (429-aware), then re-run the parser."""
import sys, os, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib
d = os.path.join(irlib.raw_dir('ASML.AS'), 'stocktitan')
todo = [p for p in range(2, 27) if not os.path.exists(os.path.join(d, f'news_p{p}.html'))]
for p in todo:
    for attempt in range(4):
        st, b = irlib.fetch(f'https://www.stocktitan.net/news/ASML/page-{p}.html', os.path.join(d, f'news_p{p}.html'),
                            timeout=40, min_gap=12, retries=0)
        print(p, st, flush=True)
        if st == 200:
            break
        time.sleep(60 * (attempt + 1))
subprocess.run([sys.executable, '-I', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asml_stocktitan.py')])
