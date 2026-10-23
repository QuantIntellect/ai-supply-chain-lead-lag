"""Write data/processed/keynotes/keynote_events.csv (+ keynote_events_sources.csv with evidence).

Keynote dates/times were taken from NVIDIA pages where they state them (pre-event
announcement posts saved in data/raw/keynotes/_timing/, live blogs, press-kit docs);
where NVIDIA pages give no clock time, the time comes from the cited external page or is
left blank. keynote_time_et is an ISO-8601 datetime with UTC offset in America/New_York.
"""
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from events import EVENTS, KIT_BASE  # noqa: E402

ROOT = "/Users/sinamirzaei/Documents/aimapping"
PROCK = os.path.join(ROOT, "data/processed/keynotes")
WAYBACK = {
    "ces-2023-news": "https://web.archive.org/web/20230203115518/https://nvidianews.nvidia.com/online-press-kit/ces-2023-news",
    "gtc-2023-news": "https://web.archive.org/web/20250317024506/https://nvidianews.nvidia.com/online-press-kit/gtc-2023-news",
    "computex-2023-news": "https://web.archive.org/web/20250120031509/https://nvidianews.nvidia.com/online-press-kit/computex-2023-news",
    "siggraph-2023-news": "https://web.archive.org/web/20250212214316/https://nvidianews.nvidia.com/online-press-kit/siggraph-2023-news",
}

# slug: (local date, local time HH:MM or "", time source / verification note)
TIMES = {
    "ces_2023": ("2023-01-03", "08:00", "Kit docs dated 2023-01-03; 8 a.m. PT per NVIDIA CES 2023 announcement (guru3d/shacknews citing NVIDIA)"),
    "gtc_2023": ("2023-03-21", "08:00", "NVIDIA release 2023-02-21 + blog 2023-03-16: 'Tuesday, March 21, at 8 a.m. Pacific'"),
    "computex_2023": ("2023-05-29", "11:00", "Live blog: Huang 'today kicked off COMPUTEX' (pub 2023-05-29 UTC); 11:00 Taipei per pre-event press (pcgameshardware: 5 a.m. CEST)"),
    "siggraph_2023": ("2023-08-08", "08:00", "NVIDIA blog 2023-08-04: 'Tuesday, Aug. 8, at 8 a.m. PT in Los Angeles'"),
    "sc23": ("2023-11-13", "07:00", "NVIDIA H200 release: 'Watch Buck's SC23 special address on Nov. 13 at 6 a.m. PT' (= 7 a.m. MT)"),
    "ces_2024": ("2024-01-08", "08:00", "NVIDIA blog 2023-12-19: special address 'Jan. 8, at 8 a.m. PT'"),
    "gtc_2024": ("2024-03-18", "13:00", "NVIDIA release 2024-02-20: 'Monday, March 18, at 1 p.m. Pacific time'"),
    "computex_2024": ("2024-06-02", "19:00", "NVIDIA blog 2024-05-08: 'livestreamed at 7 p.m. Taiwan time'; live blog pub 2024-06-02"),
    "siggraph_2024": ("2024-07-29", "14:30", "NVIDIA blog 2024-07-15: 'Monday, July 29'; times per SIGGRAPH release: Goode chat 2:30 p.m. MDT, Zuckerberg chat 4:00 p.m. MDT"),
    "ai_summit_dc_2024": ("2024-10-08", "10:00", "NVIDIA blog 2024-10-01: Bob Pette special address 'October 8, at 10 a.m. ET'"),
    "ai_summit_india_2024": ("2024-10-24", "", "NVIDIA blogs: fireside chat 'on October 24' / 'said Thursday'; clock time not published (Mumbai daytime = before US open)"),
    "ai_summit_japan_2024": ("2024-11-13", "", "NVIDIA recap blog: 'At NVIDIA's AI Summit Japan on Wednesday' (Nov 13); clock time not published (Tokyo daytime = before US open)"),
    "sc24": ("2024-11-18", "", "SC24 recap blog pub 2024-11-18 ('NVIDIA kicked off SC24'); clock time not found"),
    "ces_2025": ("2025-01-06", "18:30", "NVIDIA blog 2024-12-16: 'Jan. 6 at 6:30 p.m. PT'"),
    "gtc_2025": ("2025-03-18", "10:00", "NVIDIA release 2025-03-05: 'Tuesday, March 18, at 10 a.m. PT'; live blog 'At 10:00 a.m. PT, Huang takes the stage'"),
    "computex_2025": ("2025-05-19", "11:00", "Live blog: Huang 'took the stage at a packed Taipei Music Center Monday'; 11 a.m. Taiwan time per TAITRA (embeddedcomputing.com)"),
    "gtc_paris_2025": ("2025-06-11", "11:00", "Kit/keynote recap dated 2025-06-11; 11 a.m. CEST per nvidia.com/en-eu/gtc/keynote and VivaTech release"),
    "siggraph_2025": ("2025-08-11", "16:00", "Recap blog pub 2025-08-11; NVIDIA Research special address 4-5 p.m. PT per SIGGRAPH/NVIDIA listings"),
    "gtc_dc_2025": ("2025-10-28", "12:00", "Live blog: 'keynote address on Tuesday, Oct. 28, at 12 p.m. ET'"),
    "apec_korea_2025": ("2025-10-31", "", "NVIDIA blog pub 2025-10-31; AP: keynote at APEC CEO Summit special session Friday Oct 31 (KST); clock time not found. Partnership releases dated 2025-10-30 (US)"),
    "sc25": ("2025-11-17", "16:00", "Kit docs dated 2025-11-17; 'AI Transforming Science' special address Monday Nov 17, 4-5:30 p.m. CT per nvevents.nvidia.com/sc25fireside"),
    "ces_2026": ("2026-01-05", "13:00", "Kit docs dated 2026-01-05 ('presentation on Monday'); 1 p.m. PT per NVIDIA CES page (wccftech/techcrunch)"),
    "davos_2026": ("2026-01-21", "", "NVIDIA blog pub 2026-01-21; Bloomberg: Huang-Fink conversation Wednesday Jan 21; session clock time not found"),
    "gtc_2026": ("2026-03-16", "11:00", "NVIDIA release 2026-03-03 + live blog: 'Monday, March 16, at 11 a.m. PT'"),
    "gtc_taipei_2026": ("2026-06-01", "11:00", "Live blog: 'keynote at COMPUTEX on Monday, June 1, at 11 a.m. Taipei time'"),
    "dell_tech_world_2024": ("2024-05-20", "", "NVIDIA recap blog pub 2024-05-20 (Huang on stage with Michael Dell, Las Vegas); clock time not verified"),
    "snowflake_summit_2024": ("2024-06-03", "", "NVIDIA recap blog (pub 2024-06-04T01:10Z): Huang 'told thousands of attendees Monday' (Mon 2024-06-03) at Snowflake Summit, San Francisco; clock time not verified (evening PT per blog timing)"),
    "london_tech_week_2025": ("2025-06-09", "", "NVIDIA blog pub 2025-06-09: Huang and PM Starmer opened London Tech Week; clock time not verified (London morning = before US open)"),
    "3dx_world_2026": ("2026-02-03", "", "NVIDIA blog + Dassault/NVIDIA release both dated 2026-02-03 (3DEXPERIENCE World, Houston); clock time not verified"),
    "dell_tech_world_2026": ("2026-05-18", "", "NVIDIA recap blog pub 2026-05-18 (Dell Technologies World, Las Vegas); clock time not verified"),
    "dreamforce_2026": ("2026-09-15", "", "NVIDIA recap blog pub 2026-09-15 (Dreamforce, San Francisco); clock time not verified"),
    "gtc_berlin_2026": ("2026-10-21", "11:00", "News hub: keynote 'begins Wednesday, October 21 at 11 a.m. CEST'"),
}


def to_et(date, hhmm, tz):
    if not hhmm:
        return ""
    loc = datetime.fromisoformat(f"{date}T{hhmm}").replace(tzinfo=ZoneInfo(tz))
    return loc.astimezone(ZoneInfo("America/New_York")).isoformat(timespec="minutes")


if __name__ == "__main__":
    docs = pd.read_csv(os.path.join(PROCK, "keynote_docs_full.csv"))
    docs = docs.drop(columns=[c for c in ("days_from_keynote", "event_window") if c in docs.columns])
    rows, src = [], []
    for e in EVENTS:
        s = e["slug"]
        date, hhmm, note = TIMES[s]
        d = docs[docs.event_slug == s]
        live = d[d.is_livelog == 1].doc_url.iloc[0]
        if e.get("kit"):
            kit = WAYBACK.get(e["kit"], KIT_BASE + e["kit"])
        else:
            kit = ""
        rows.append(dict(event_slug=s, event_name=e["name"], city=e["city"], keynote_date=date,
                         keynote_time_local=hhmm, timezone=e["tz"], keynote_time_et=to_et(date, hhmm, e["tz"]),
                         livelog_url=live, presskit_url=kit, n_docs=len(d)))
        src.append(dict(event_slug=s, huang_speaker=int("not Huang" not in e["name"]), timing_source=note,
                        doc_source=("online press kit" if e.get("kit") and e["kit"] not in WAYBACK else
                                    "press kit via Wayback snapshot (docs fetched live)" if e.get("kit") else
                                    "no press kit: NVIDIA newsroom archive items for " +
                                    ", ".join(dt for dt, _ in e["archive"]))))
    # doc-level timing flags relative to the keynote (written back to keynote_docs_full.csv)
    kd = {s: TIMES[s][0] for s in TIMES}
    gap = (pd.to_datetime(docs.pub_date) - pd.to_datetime(docs.event_slug.map(kd))).dt.days
    docs["days_from_keynote"] = gap
    docs["event_window"] = (gap.abs() <= 2).astype(int)
    docs.to_csv(os.path.join(PROCK, "keynote_docs_full.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(PROCK, "keynote_events.csv"), index=False)
    pd.DataFrame(src).to_csv(os.path.join(PROCK, "keynote_events_sources.csv"), index=False)
    print(pd.DataFrame(rows)[["event_slug", "keynote_date", "keynote_time_local", "timezone",
                              "keynote_time_et", "n_docs"]].to_string())
