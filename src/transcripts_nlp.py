"""Text features from earnings-call transcripts (Motley Fool) and capex-guidance extraction.

Per transcript (spoken part only, from first 'Operator:' onward):
  words, ai_per10k, dc_per10k, constraint_per10k, demand_pos/neg, order_per10k, inventory/digestion,
  tone = (pos - neg)/(pos + neg), uncertainty_per10k
Capex sentences: sentences mentioning capex / capital expenditures with a $ amount -> extracted rows.
Outputs: data/processed/transcript_features.parquet, data/processed/capex_statements.csv
"""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from common import PROC

T_DIR = os.path.join(PROC, "transcripts")
LEX = {
    "ai": r"\b(ai|artificial intelligence|generative|genai|gen ai|llms?|large language models?|inference|agentic|agents?|accelerated computing|accelerators?|gpus?|tpus?|xpus?|copilot)\b",
    "dc": r"\b(data ?cent(?:er|re)s?|hyperscal\w*|cloud capacity|ai factor(?:y|ies)|clusters?|gigawatts?|megawatts?|power capacity)\b",
    "constraint": r"\b(supply[- ]constrained|capacity[- ]constrained|constrained|shortages?|sold out|tight(?:ness)?|lead times?|allocation|bottlenecks?|backlogged)\b",
    "orders": r"\b(orders?|bookings?|book[- ]to[- ]bill|backlog|pipeline|remaining performance obligations?|rpo|commitments?)\b",
    "digestion": r"\b(digestion|inventory correction|push[- ]?outs?|pushed out|cancellations?|delays?|softness|slowdown|headwinds?|destocking)\b",
    "pos": r"\b(strong(?:er|est)?|record|robust|accelerat\w*|exceptional|unprecedented|outperform\w*|beat|exceed\w*|momentum|surg\w*|expand\w*|upside|raise[ds]?|raising|growth|grew|increase[ds]?|healthy|solid|significant(?:ly)? (?:higher|above))\b",
    "neg": r"\b(weak(?:er|ness)?|declin\w*|decreas\w*|soft(?:er|ness)?|challeng\w*|difficult|downturn|lower|miss(?:ed)?|cut|reduc\w*|pressure[ds]?|uncertain\w*|cautious|disappoint\w*|loss(?:es)?)\b",
    "uncert": r"\b(uncertain\w*|unclear|volatil\w*|risk(?:s|y)?|may|might|could|depend\w*|visibility)\b",
}
RX = {k: re.compile(v, re.I) for k, v in LEX.items()}
CAPEX = re.compile(r"[^.]*\b(capex|capital expenditures?|capital spending|capital investments?)\b[^.]*\$\s?\d[\d,.]*\s?(?:billion|million|bn)[^.]*\.", re.I)
AMT = re.compile(r"\$\s?(\d[\d,.]*)\s?(billion|million|bn)", re.I)


def spoken(text):
    i = text.find("Operator:")
    return text[i:] if i >= 0 else text


def main():
    idx = pd.read_csv(os.path.join(PROC, "fool_transcripts_index.csv"))
    files = glob.glob(os.path.join(T_DIR, "*", "*.txt"))
    rows, capex = [], []
    for f in files:
        tk = os.path.basename(os.path.dirname(f))
        base = os.path.basename(f)[:-4]
        date, slug = base[:10], base[11:]
        txt = spoken(open(f, encoding="utf-8", errors="ignore").read())
        words = len(re.findall(r"\w+", txt))
        if words < 1500:
            continue
        rec = {"ticker": tk, "pub_date": date, "slug": slug, "words": words}
        m = re.search(r"-(q[1-4])-(\d{4})-", slug)
        rec["fq"] = f"{m.group(2)}{m.group(1).upper()}" if m else ""
        for k, rx in RX.items():
            rec[f"{k}_n"] = len(rx.findall(txt))
            rec[f"{k}_per10k"] = rec[f"{k}_n"] / words * 1e4
        rec["tone"] = (rec["pos_n"] - rec["neg_n"]) / max(rec["pos_n"] + rec["neg_n"], 1)
        # split prepared remarks vs Q&A: first analyst question
        qa = re.search(r"\n(?:Operator:)[^\n]*(?:first question|question comes|question-and-answer|Q&A)", txt, re.I)
        if qa:
            rec["qa_share"] = 1 - qa.start() / len(txt)
            q = txt[qa.start():]
            qw = max(len(re.findall(r"\w+", q)), 1)
            rec["qa_tone"] = (len(RX["pos"].findall(q)) - len(RX["neg"].findall(q))) / max(len(RX["pos"].findall(q)) + len(RX["neg"].findall(q)), 1)
            rec["qa_constraint_per10k"] = len(RX["constraint"].findall(q)) / qw * 1e4
        rows.append(rec)
        for c in CAPEX.finditer(txt):
            sent = c.group(0).strip()
            amts = [float(a.replace(",", "")) * (1 if u.lower() in ("billion", "bn") else 1e-3) for a, u in AMT.findall(sent)]
            capex.append({"ticker": tk, "pub_date": date, "fq": rec["fq"], "sentence": sent[:600],
                          "amounts_bn": ";".join(f"{a:g}" for a in amts),
                          "forward": bool(re.search(r"\b(expect|anticipate|plan|guid|outlook|next year|fiscal (?:year )?20\d\d|20\d\d)\b", sent, re.I))})
    F = pd.DataFrame(rows)
    # correct publication dates to the real call dates where the call-reading pass verified them; drop duplicates
    maps = [pd.read_csv(m, dtype=str) for m in glob.glob(os.path.join(PROC, "us_notes", "call_date_map_*.csv"))]
    if maps:
        M = pd.concat(maps, ignore_index=True).fillna("")
        dup = set(zip(M[M.duplicate_of_call != ""].ticker, M[M.duplicate_of_call != ""].slug))
        cm = {(t, sl): c for t, sl, c in zip(M.ticker, M.slug, M.call_date) if c}
        F = F[[(t, sl) not in dup for t, sl in zip(F.ticker, F.slug)]].copy()
        F["file_date"] = F.pub_date
        F["pub_date"] = [cm.get((t, sl), d) for t, sl, d in zip(F.ticker, F.slug, F.pub_date)]
        print("call dates corrected:", int((F.pub_date != F.file_date).sum()), "duplicates dropped:", len(dup))
    F = F.sort_values(["ticker", "pub_date"])
    F.to_parquet(os.path.join(PROC, "transcript_features.parquet"), index=False)
    C = pd.DataFrame(capex)
    C.to_csv(os.path.join(PROC, "capex_statements.csv"), index=False)
    print("transcripts:", len(F), "tickers:", F.ticker.nunique(), "range", F.pub_date.min(), F.pub_date.max())
    print("capex sentences:", len(C), "forward-looking:", int(C.forward.sum()) if len(C) else 0)
    F["year"] = F.pub_date.str[:4]
    print(F.groupby("year")[["ai_per10k", "dc_per10k", "constraint_per10k", "orders_per10k", "digestion_per10k", "tone"]].mean().round(2).to_string())


if __name__ == "__main__":
    main()
