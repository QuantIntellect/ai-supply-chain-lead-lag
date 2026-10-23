"""Download keynote live blogs + press-kit docs, extract text, write keynote_docs.csv.

Usage: python -I build_corpus.py [slug ...]
Raw HTML -> data/raw/keynotes/<slug>/ ; text -> data/processed/keynotes/text/<slug>/
"""
import os
import re
import sys
import shutil
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from fetch import get  # noqa: E402
from textify import html_to_text  # noqa: E402
from list_presskits import parse_kit  # noqa: E402
from events import EVENTS, KIT_BASE  # noqa: E402

ROOT = "/Users/sinamirzaei/Documents/aimapping"
RAWK = os.path.join(ROOT, "data/raw/keynotes")
IDX = os.path.join(RAWK, "_index")
PROCK = os.path.join(ROOT, "data/processed/keynotes")
TEXT = os.path.join(PROCK, "text")
ARCH = pd.read_csv(os.path.join(PROCK, "newsroom_archive.csv"), dtype=str)
ARCH["url_n"] = ARCH.url.str.rstrip("/")


def norm_url(u):
    u = u.split("#")[0].split("?")[0].rstrip("/")
    u = u.replace("http://", "https://")
    return u


def doc_name(u):
    seg = u.rstrip("/").split("/")[-1][:110]
    if "nvidianews.nvidia.com/news/" in u:
        return "pr_" + seg
    return "blog_" + seg


def kit_doc_urls(ev):
    html = open(os.path.join(IDX, f"kit_{ev['kit']}.html"), encoding="utf-8", errors="ignore").read()
    _, links = parse_kit(html)
    urls = [norm_url(x["url"]) for x in links]
    # live-update hub pages (blogs.nvidia.com/<x>-news/) linked from the kit
    for h in re.findall(r'href="(https://blogs\.nvidia\.com/[a-z0-9\-]+-news)/?"', html):
        if norm_url(h) not in urls:
            urls.append(norm_url(h))
    return html, urls


def archive_doc_urls(ev):
    urls = []
    for d, rx in ev["archive"]:
        sub = ARCH[(ARCH.date == d) & ARCH.title.str.contains(rx, regex=True)]
        urls += [norm_url(u) for u in sub.url]
    return urls


def resolve_livelog(ev, urls):
    if ev.get("livelog"):
        return norm_url(ev["livelog"])
    sub = ARCH[ARCH.title.str.contains(ev["livelog_regex"], regex=True)]
    return norm_url(sub.url.iloc[0])


def iso_ts(meta):
    for k in ("article:published_time", "datePublished"):
        if meta.get(k):
            return meta[k]
    return ""


def iso_date(meta, arch_date):
    for k in ("article:published_time", "datePublished"):
        if meta.get(k):
            return meta[k][:10]
    if meta.get("page_date"):
        return datetime.strptime(meta["page_date"], "%B %d, %Y").date().isoformat()
    return arch_date or ""


def seed_berlin():
    """Re-use the Berlin pages the project lead already downloaded (keeps originals)."""
    d = os.path.join(RAWK, "gtc_berlin_2026")
    os.makedirs(d, exist_ok=True)
    pairs = [("gtc_berlin_2026_blog.html", "blog_gtc-berlin-2026-keynote.html"),
             ("gtc_berlin_2026_news.html", "blog_gtc-berlin-2026-news.html"),
             ("gtc_berlin_2026_presskit.html", "_presskit.html")]
    for src, dst in pairs:
        if not os.path.exists(os.path.join(d, dst)):
            shutil.copy2(os.path.join(RAWK, src), os.path.join(d, dst))
    dv = os.path.join(RAWK, "davos_2026")
    os.makedirs(dv, exist_ok=True)
    if not os.path.exists(os.path.join(dv, "blog_ai-5-layer-cake.html")):
        shutil.copy2(os.path.join(RAWK, "ai_5_layer_cake.html"), os.path.join(dv, "blog_ai-5-layer-cake.html"))
    old = os.path.join(d, "cloud-partners-europe-sovereign-safety-open-agents.html")
    if os.path.exists(old):
        os.replace(old, os.path.join(d, "blog_cloud-partners-europe-sovereign-safety-open-agents.html"))


def build_event(ev):
    slug = ev["slug"]
    rdir = ensure(os.path.join(RAWK, slug))
    tdir = ensure(os.path.join(TEXT, slug))
    if ev.get("kit"):
        kit_html, urls = kit_doc_urls(ev)
        kp = os.path.join(rdir, "_presskit.html")
        if not os.path.exists(kp):
            with open(kp, "w", encoding="utf-8") as f:
                f.write(kit_html)
    else:
        urls = archive_doc_urls(ev)
    for x in ev.get("extra", []):
        if norm_url(x) not in urls:
            urls.append(norm_url(x))
    live = resolve_livelog(ev, urls)
    if live not in urls:
        urls.insert(0, live)
    else:
        urls.remove(live)
        urls.insert(0, live)
    rows, seen, seen_canon = [], set(), set()
    for u in urls:
        name = doc_name(u)
        if name in seen:
            continue
        seen.add(name)
        st, html = get(u, os.path.join(rdir, name + ".html"))
        if st != 200:
            print("  FAIL", st, u, flush=True)
            continue
        title, meta, text = html_to_text(html)
        canon = norm_url(meta.get("canonical") or meta.get("og:url") or u)
        if "web.archive.org" in canon or not canon.startswith("https://"):
            canon = u
        if canon in seen_canon:  # two kit links resolving to the same article
            continue
        seen_canon.add(canon)
        am = ARCH[ARCH.url_n.isin([u, canon])]
        arch_date = am.date.iloc[0] if len(am) else ""
        pub = iso_date(meta, arch_date)
        tpath = os.path.join(tdir, name + ".txt")
        with open(tpath, "w", encoding="utf-8") as f:
            f.write(title.strip() + "\n\n" + text.strip() + "\n")
        is_hub = int(bool(re.search(r"blogs\.nvidia\.com/(blog/)?[a-z0-9\-]*-news$", canon)) or
                     "Live Updates on What" in title)
        rows.append({"event_slug": slug, "doc_url": canon, "title": title.strip(), "pub_date": pub,
                     "local_path": os.path.relpath(tpath, ROOT), "is_livelog": int(u == live),
                     "n_chars": len(text), "pub_ts": iso_ts(meta), "is_hub": is_hub,
                     "is_extra": int(u in [norm_url(x) for x in ev.get("extra", [])]),
                     "raw_path": os.path.relpath(os.path.join(rdir, name + ".html"), ROOT)})
    rows += add_slide_docs(slug)
    print(slug, len(rows), "docs", flush=True)
    return rows


SLIDES = {
    "gtc_berlin_2026": dict(
        doc_url="https://blogs.nvidia.com/blog/gtc-berlin-2026-keynote#slide-building-europes-ai-economy",
        title="Keynote slide: Building Europe's AI Economy (transcribed from project brief; slide image, not in live-blog text)",
        name="slide_building-europes-ai-economy",
        layers=[
            ("Applications", "AgileRL, Agile Robots, Wandelbots, Avelios, Basecamp Research, Black Forest Labs, Cursive, "
             "DeepL, distil labs, ElevenLabs, Gradium, Helsing, H Company, Humanoid, Inherent, Langdock, Latent Labs, "
             "Legora, Lovable, MicroAGI, Multiverse Computing, n8n, NEURA Robotics, Oxa, PhysicsX, Prima Mente, "
             "Recursive Superintelligence, Synthesia, Wayve"),
            ("Models", "Aleph Alpha, Advanced Machine Intelligence (AMI Labs), Black Forest Labs, Ineffable Intelligence, Mistral AI"),
            ("AI Factories", "Bull, Deutsche Telekom, Firebird, Mistral AI, Nebius, Nscale, Nokia, Radiant, Volta"),
            ("Compute", "NVIDIA"),
            ("Energy", "Rolls-Royce SMR, Schneider Electric, Siemens, Siemens Energy"),
        ]),
}


def add_slide_docs(slug):
    sl = SLIDES.get(slug)
    if not sl:
        return []
    tpath = os.path.join(TEXT, slug, sl["name"] + ".txt")
    with open(tpath, "w", encoding="utf-8") as f:
        f.write(sl["title"] + "\n\n")
        for layer, comps in sl["layers"]:
            f.write(f"{layer} layer: {comps}.\n")
    return [{"event_slug": slug, "doc_url": sl["doc_url"], "title": sl["title"], "pub_date": "2026-10-21",
             "local_path": os.path.relpath(tpath, ROOT), "is_livelog": 0, "n_chars": os.path.getsize(tpath),
             "pub_ts": "", "is_hub": 0, "is_extra": 1, "raw_path": ""}]


def ensure(p):
    os.makedirs(p, exist_ok=True)
    return p


if __name__ == "__main__":
    want = set(sys.argv[1:])
    seed_berlin()
    out = os.path.join(PROCK, "keynote_docs_full.csv")
    prev = pd.read_csv(out, dtype=str) if os.path.exists(out) else pd.DataFrame()
    allrows = []
    for ev in EVENTS:
        if want and ev["slug"] not in want:
            continue
        allrows += build_event(ev)
    df = pd.DataFrame(allrows)
    if len(prev) and want:
        prev = prev[~prev.event_slug.isin(want)]
        df = pd.concat([prev, df], ignore_index=True)
    order = {e["slug"]: i for i, e in enumerate(EVENTS)}
    df["_o"] = df.event_slug.map(order)
    df = df.sort_values(["_o", "is_livelog"], ascending=[True, False]).drop(columns="_o")
    df.to_csv(out, index=False)
    df[["event_slug", "doc_url", "title", "pub_date", "local_path"]].to_csv(
        os.path.join(PROCK, "keynote_docs.csv"), index=False)
    print("total docs", len(df))
