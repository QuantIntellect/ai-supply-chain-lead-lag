"""Inject reports/report_data.json into reports/template.html -> reports/ai_supply_chain_lead_lag.html."""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import REPORTS


def main():
    tpl = open(os.path.join(REPORTS, "template.html"), encoding="utf-8").read()
    data = json.load(open(os.path.join(REPORTS, "report_data.json")))
    blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/").replace("<!--", "\\u003c!--")
    out = os.path.join(REPORTS, "ai_supply_chain_lead_lag.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(tpl.replace("__DATA__", blob))
    print("wrote", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
