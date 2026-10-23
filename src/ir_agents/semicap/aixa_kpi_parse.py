"""Parse Aixtron 'Key financials' table from extracted press-release text -> quarter values (EUR million)."""
import os, sys, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import irlib

T = "AIXA.DE"
NUM = re.compile(r"^[-–]?\d[\d,]*\.?\d*%?$|^n\.m\.\*?$|^[-–]?\d+\s?pp$|^\(\d+\)\s?(pp)?$")


def toks_after(lines, label_re, start=0, n=6):
    for i in range(start, len(lines)):
        if re.match(label_re, lines[i], re.I):
            vals, j = [], i + 1
            while j < len(lines) and len(vals) < n:
                x = lines[j].replace("–", "-").replace(" ", "")
                if NUM.match(x):
                    vals.append(x)
                elif vals:  # a non-number after numbers ends the row
                    break
                j += 1
            return vals, i
    return [], -1


def f(x):
    try:
        return float(x.rstrip("%").replace(",", "").replace("pp", ""))
    except Exception:
        return None


def parse(path, q):
    t = open(path).read()
    k = t.find("in EUR million")
    k = t.find("EUR million") if k < 0 else k
    lines = [l.strip() for l in t[k:k + 4000].split("\n") if l.strip()]
    lines = [("Order backlog (Equipment only)" if l.startswith("Order backlog") else l) for l in lines]
    # merge "Order backlog" + "(equipment only)" handled by prefix match
    head = " ".join(lines[:10])
    three_col_q1 = q == 1 and not re.search(r"Q4[ /]20\d\d", head)
    out = {}
    for key, lab in [("orders", r"^(Order intake|Incoming orders)"), ("backlog", r"^Order backlog"),
                     ("revenue", r"^Revenues?$"), ("gross_profit", r"^Gross profit")]:
        v, idx = toks_after(lines, lab)
        if not v:
            continue
        if q == 1:
            cur, prior = v[0], v[1]
        else:
            cur, prior = (v[3], v[4]) if len(v) >= 5 else (None, None)
        out[key], out[key + "_py"] = f(cur) if cur else None, f(prior) if prior else None
        if key == "gross_profit":
            pv, _ = toks_after(lines, r"^%$", idx + 1)
            if pv:
                if q == 1:
                    out["gm"], out["gm_py"] = f(pv[0]), f(pv[1])
                elif len(pv) >= 5:
                    out["gm"], out["gm_py"] = f(pv[3]), f(pv[4])
    return out


if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(irlib.text_dir(T), "202*_press_release.txt"))):
        b = os.path.basename(p)
        if "adhoc" in b:
            continue
        q = int(b[5])
        print(b[:6], parse(p, q))
