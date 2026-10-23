"""Normalize the KPI 'unit' column to '<CUR> million' across tickers."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *
for t in sys.argv[1:]:
    p = os.path.join(PROC_IR, f"{t}_kpis.csv")
    k = pd.read_csv(p, dtype=str, keep_default_na=False)
    before = k.unit.unique().tolist()
    k["unit"] = [f"{c} million" if u.strip().lower() in ("million", "m", f"{c.lower()} m", "mn", f"{c.lower()} mn") else u
                 for c, u in zip(k.currency, k.unit)]
    k = k[KPI_COLS]
    k.to_csv(p, index=False)
    print(t, before, "->", k.unit.unique().tolist())
