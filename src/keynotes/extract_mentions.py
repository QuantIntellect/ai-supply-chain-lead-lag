"""Extract company mentions from the keynote corpus -> data/processed/keynotes/keynote_mentions.csv

One row per (event_slug, doc_url, company[, listing]). Context = best sentence (<=200 chars):
preference = strongest relationship type, then sentence also naming NVIDIA, then shortest.
Docs used: live blog, live-update hub pages and docs within +-2 days of the keynote
(see keynote_docs_full.csv: is_livelog / is_hub / event_window). NVIDIA itself is excluded.
"""
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from aliases import UNIVERSE_ALIASES, DUAL_LISTINGS, EXCLUDE  # noqa: E402
from nonuniverse import NONUNIVERSE  # noqa: E402

ROOT = "/Users/sinamirzaei/Documents/aimapping"
PROCK = os.path.join(ROOT, "data/processed/keynotes")

# entity names that only exist from a given date (avoid e.g. Volta = 2017 GPU architecture)
MIN_DATE = {
    "Volta (Volta Infra)": "2026-07-01", "Radiant (Brookfield)": "2025-11-01", "Firebird": "2025-06-01",
    "Everpure (ex-Pure Storage)": "2026-02-01", "Humanoid (SKL Robotics)": "2025-01-01",
    "Inherent": "2026-05-01", "Gradium": "2025-09-01", "Recursive Superintelligence": "2026-01-01",
    "Ineffable Intelligence": "2026-01-01", "AMI Labs": "2025-11-01", "MicroAGI": "2025-09-01",
    "Verda (ex-DataCrunch)": "2025-01-01", "Thinking Machines Lab": "2025-02-01",
    "Aumovio (Continental spin-off)": "2025-09-01", "Humain": "2025-05-01", "Cursive": "2026-01-01",
}

TYPE_RULES = [
    ("investment", r"\b(invest(s|ed|ing|ment|ments|or|ors)?|stake|funding( round)?|raised|NVentures|venture arm|backed by|equity)\b"),
    ("sovereign_ai", r"\b(sovereign\w*|national (AI|supercomputer|infrastructure|strategy|cloud|research)|government\w*|ministr(y|ies)|public sector|nation[’']s|country[’']s|state-owned)\b"),
    ("partnership", r"\b(partnership|partner(s|ed|ing)? with|strategic partner|collaborat(e|es|ed|ing|ion|ions)|alliance|team(s|ed|ing)? up|co-develop\w*|co-design\w*|co-engineer\w*|joint venture|jointly)\b"),
    ("supplier", r"\b(suppl(y|ies|ier|iers|ying)(?! chain organization)|supply chain partners?|foundr(y|ies)|CoWoS|advanced packaging|HBM\d?E?|memory (chips?|supplier|makers?|partner|technology|solutions?)|wafers?|substrates?|transceivers?|optical (interconnects?|engines?|modules?|components?)|silicon photonics|co-packaged optics|photonics|liquid[- ]cooling (systems?|solutions?|technolog\w+)|cooling (systems?|solutions?|technolog\w+|equipment|partners?|specialists?)|power (delivery|systems?|equipment|distribution|shelves|supplies|and cooling)|turbines?|switchgear|busways?|manufactur(es|ing) (NVIDIA|Blackwell|Hopper|Rubin|GPUs?|chips?|systems|servers|racks|the)|manufacturing partners?|contract manufactur\w*|(energy|power|cooling)( and (energy|power|cooling))? (providers?|partners?|specialists?|suppliers?|leaders?)|(begin|start)s? shipping|available to order|shipping from|ODMs?|OEMs?|system makers?|server makers?|system builders?|systems? manufacturers?|component(s)? (makers?|suppliers?))\b"),
    ("customer/deployment", r"\b(deploy(s|ed|ing)?|deployments? of|adopt(s|ed|ing|ion)?|us(es|ing|ed) [^.;]{0,40}NVIDIA|host(s|ing)? |built on|build(s|ing)? on|powered by|runs? on|running on|instances?|early access|purchas\w+|orders?|ordered|buy(s|ing)?|bought|customers? (include|including|such as)|is a customer|install(s|ed|ing)?|tap(s|ped|ping)|leverag(e|es|ed|ing)|harness(es|ed|ing)?|turn(s|ed|ing)? to|select(s|ed)|chose|choose|rolls? out|rolling out|first to|among the first|accelerated by NVIDIA|AI factor(y|ies)|supercomputers?|adopters?)\b"),
    ("product_integration", r"\b(integrat(e|es|ed|ing|ion|ions)|support(s|ed|ing)? (for )?(NVIDIA|NV\w+)|support for|available (directly )?(on|in|through|via|from)|featuring|NemoClaw|OpenClaw|OpenShell|Isaac|Cosmos|GR00T|Nemotron|Dynamo|DSX|Holoscan|Clara|BioNeMo|Metropolis|Riva|ACE|DLSS|Jetson|DRIVE|Halos|Alpamayo|Earth-2|Modulus|PhysicsNeMo|AI Enterprise|optimi[sz](e|es|ed|ing) (for|on|with)|NIM|NeMo|Omniverse|Blueprints?|CUDA-X|CUDA|cuDF|cuOpt|cuLitho|cuQuantum|TensorRT|libraries|SDKs?|plug-?ins?|connectors?|certified|validated|based on NVIDIA|featuring NVIDIA|equipped with|offer(s|ed|ing)?|bring(s|ing)? NVIDIA|incorporat\w+|embed\w*)\b"),
    ("partnership", r"\b(partner(s|ed|ing|ship|ships)?|collaborat(e|es|ed|ing|ion|ions)|work(s|ed|ing)? (closely )?with|team(s|ed|ing)? (up )?with|alliance|joint(ly)?|together with|co-develop\w*|co-design\w*|co-engineer\w*|ecosystem|join(s|ed|ing)?)\b"),
]
TYPE_RX = [(i, t, re.compile(rx, re.I)) for i, (t, rx) in enumerate(TYPE_RULES)]
OTHER_RANK = len(TYPE_RULES)

ABBR = ["Inc.", "Corp.", "Co.", "Ltd.", "U.S.", "U.K.", "Dr.", "Mr.", "Ms.", "St.", "No.", "Jan.", "Feb.",
        "Aug.", "Sept.", "Oct.", "Nov.", "Dec.", "vs.", "e.g.", "i.e.", "Jr.", "Calif.", "D.C."]
CUT = re.compile(r"\n(About NVIDIA\b|Certain statements in this press release|© ?\d{4} NVIDIA|Media Contacts?\b)")


def classify(sent):
    """Return (rank, type): first matching rule in priority order."""
    for i, t, rx in TYPE_RX:
        if rx.search(sent):
            return i, t
    return OTHER_RANK, "other"


def load_patterns():
    uni = pd.read_csv(os.path.join(ROOT, "config/universe.csv"), dtype=str).fillna("")
    names = dict(zip(uni.ticker, uni.name))
    pats = []
    for tk, ps in UNIVERSE_ALIASES.items():
        if tk in EXCLUDE:
            continue
        comp = "TSMC" if tk in DUAL_LISTINGS else names[tk]
        tickers = DUAL_LISTINGS.get(tk, [tk])
        for p in ps:
            pats.append((comp, tickers, re.compile(p), "", 1))
    for comp, tk, ps in NONUNIVERSE:
        for p in ps:
            pats.append((comp, [tk], re.compile(p), MIN_DATE.get(comp, ""), 0))
    return pats


def sentences(text):
    t = text
    for a in ABBR:
        t = t.replace(a, a.replace(".", "․"))
    spans, start = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-Z0-9“\"‘'(\[])|\n+", t):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(t)))
    return spans


def context(text, s0, s1, m0, m1):
    sent = re.sub(r"\s+", " ", text[s0:s1].replace("․", ".")).strip()
    if len(sent) <= 200:
        return sent
    rel = len(re.sub(r"\s+", " ", text[s0:m0].replace("․", ".")).lstrip())
    a = max(0, rel - 80)
    b = min(len(sent), a + 198)
    a = max(0, b - 198)
    out = sent[a:b].strip()
    return ("…" if a > 0 else "") + out + ("…" if b < len(sent) else "")


def main():
    docs = pd.read_csv(os.path.join(PROCK, "keynote_docs_full.csv"), dtype=str).fillna("")
    ev = pd.read_csv(os.path.join(PROCK, "keynote_events.csv"), dtype=str)
    kdate = dict(zip(ev.event_slug, ev.keynote_date))
    use = docs[(docs.is_livelog == "1") | (docs.is_hub == "1") | (docs.event_window == "1")]
    pats = load_patterns()
    rows = []
    for _, d in use.iterrows():
        raw = open(os.path.join(ROOT, d.local_path), encoding="utf-8").read()
        cut = CUT.search(raw)
        text = raw[:cut.start()] if cut else raw
        prot = text
        for a in ABBR:
            prot = prot.replace(a, a.replace(".", "․"))
        found = []
        for comp, tks, rx, mind, isu in pats:
            if mind and d.pub_date < mind:
                continue
            for m in rx.finditer(prot):
                found.append((m.end() - m.start(), m.start(), m.end(), comp, tks))
        found.sort(key=lambda x: (-x[0], x[1]))
        taken, acc = [], []
        for ln, a, b, comp, tks in found:
            if any(a < y and b > x for x, y in taken):
                continue
            taken.append((a, b))
            acc.append((a, b, comp, tks))
        sp = sentences(prot)
        best = {}
        for a, b, comp, tks in acc:
            s0, s1 = next(((x, y) for x, y in sp if x <= a < y + 1), (max(0, a - 100), min(len(prot), b + 100)))
            sent = prot[s0:s1]
            rank, typ = classify(sent)
            key = (rank, 0 if "NVIDIA" in sent else 1, len(sent))
            if comp not in best or key < best[comp][0]:
                best[comp] = (key, typ, context(prot, s0, s1, a, b), tks)
        if "#slide-" in d.doc_url:  # transcribed keynote slide: companies shown as NVIDIA ecosystem partners
            layer_of = {}
            for line in prot.split("\n"):
                if " layer: " in line:
                    layer_of[line.split(" layer: ")[0]] = line
            for comp in list(best):
                lays = [k for k, v in layer_of.items() if any(
                    rx.search(v) for c2, t2, rx, _, _ in pats if c2 == comp)]
                lay = " & ".join(lays) + (" layers" if len(lays) > 1 else " layer")
                best[comp] = (best[comp][0], "partnership",
                              f"Named on Huang's keynote slide 'Building Europe's AI Economy' ({lay})",
                              best[comp][3])
        for comp, (_, typ, ctx, tks) in best.items():
            for tk in tks:
                rows.append(dict(event_slug=d.event_slug, keynote_date=kdate[d.event_slug], doc_url=d.doc_url,
                                 company=comp, ticker=tk, mention_type=typ, context=ctx))
    out = pd.DataFrame(rows)
    order = {s: i for i, s in enumerate(ev.event_slug)}
    out["_o"] = out.event_slug.map(order)
    out = out.sort_values(["_o", "doc_url", "company", "ticker"]).drop(columns="_o")
    out.to_csv(os.path.join(PROCK, "keynote_mentions.csv"), index=False)
    print(len(out), "mention rows;", out.doc_url.nunique(), "docs;", out.company.nunique(), "companies")
    print("excluded docs (out of +-2d window, not live blog/hub):",
          len(docs) - len(use))


if __name__ == "__main__":
    main()
