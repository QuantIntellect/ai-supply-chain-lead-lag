"""Rank candidate organisation names in the keynote corpus (for curating non-universe aliases)."""
import re
import sys
import collections
import pandas as pd

sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/keynotes")
from aliases import UNIVERSE_ALIASES  # noqa: E402

docs = pd.read_csv("/Users/sinamirzaei/Documents/aimapping/data/processed/keynotes/keynote_docs_full.csv")
TOK = r"[A-Z][A-Za-z0-9&’'\.\-]*[A-Za-z0-9]|[A-Z]"
NAME = rf"(?:{TOK})(?:\s+(?:{TOK}|de|of|and|&|la|du|von)){{0,3}}"
# list contexts: "including A, B and C" / "partners A, B" / "such as"
LIST = re.compile(r"(?:including|such as|partners|companies|leaders|providers|makers|like|from|with|and|,)\s+(" + NAME + r")")
cnt = collections.Counter()
for p in docs.local_path:
    t = open("/Users/sinamirzaei/Documents/aimapping/" + p, encoding="utf-8").read()
    seen = set()
    for m in LIST.finditer(t):
        n = m.group(1).strip(" .,")
        n = re.sub(r"\s+(and|of|de|la|du|von|&)$", "", n)
        if len(n) < 2:
            continue
        seen.add(n)
    for n in seen:
        cnt[n] += 1
uni = [re.compile(p) for ps in UNIVERSE_ALIASES.values() for p in ps]
stop = re.compile(r"^(NVIDIA|The|This|These|That|In|At|For|With|And|To|On|By|As|It|Its|Our|We|A|An|AI|GPU|GPUs|CPU|CUDA|DGX|HGX|MGX|RTX|NIM|NeMo|Omniverse|Isaac|Blackwell|Hopper|Grace|Rubin|Vera|Jetson|DRIVE|Cosmos|Nemotron|GeForce|BlueField|Spectrum|Quantum|ConnectX|Dynamo|Holoscan|Clara|BioNeMo|Metropolis|Riva|Earth-2|Huang|Jensen|Europe|European|U\.S\.|US|UK|Japan|India|Korea|France|Germany|Taiwan|China|Learn|Read|Watch|See|More|New|Today|Additional|Other|Many|Some|All|Each|Every|Leading|Global|World|Industry|Industries|Partners|Customers|Companies)\b")
rows = [(n, c) for n, c in cnt.items() if c >= 3 and not stop.match(n) and not any(r.search(n) for r in uni)]
rows.sort(key=lambda x: -x[1])
for n, c in rows[:int(sys.argv[1]) if len(sys.argv) > 1 else 400]:
    print(f"{n}:{c}", end=" | ")
print()
