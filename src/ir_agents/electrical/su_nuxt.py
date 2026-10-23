"""Resolve Nuxt-minified variables in the Schneider financial-results page and
list every document URL per year/row (date, title, cell urls)."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irlib import *

h = open(os.path.join(RAW_IR, "SU.PA", "pages", "financial-results.html"), encoding="utf-8", errors="ignore").read()
i = h.find("(function(a,b,c")
j = h.find("){", i)
params = h[i + len("(function("):j].split(",")
end = h.find("</script>", j)
body = h[j:end]
body = body[:body.rfind("))]")]
# the args list starts at the first '}(' that is followed by a literal and
# yields as many tokens as there are params; try candidates from the end
cands = [m.start() for m in re.finditer(r"\}\(", body)]
argstr = None
for k in reversed(cands):
    a = body[k + 2:]
    if a[:1] in '"-0123456789tfnv{[':
        argstr = a
        if a.count(",") + 1 >= len(params):
            break
# tokenize JS literals
toks = []
p = 0
n = len(argstr)
while p < n:
    c = argstr[p]
    if c in " ,\n":
        p += 1; continue
    if c == '"':
        q = p + 1; buf = []
        while q < n:
            if argstr[q] == "\\":
                buf.append(argstr[q:q + 2]); q += 2; continue
            if argstr[q] == '"':
                break
            buf.append(argstr[q]); q += 1
        s = "".join(buf)
        try:
            s = json.loads('"' + s + '"')
        except Exception:
            pass
        toks.append(s); p = q + 1; continue
    m = re.match(r"(void 0|true|false|null|-?\d+(\.\d+)?(e-?\d+)?|\{\}|\[\])", argstr[p:])
    if m:
        toks.append(m.group(1)); p += len(m.group(1)); continue
    # unknown token: skip to next comma
    q = argstr.find(",", p)
    toks.append(argstr[p:q if q > 0 else n]); p = q + 1 if q > 0 else n
print("params", len(params), "args", len(toks))
var = dict(zip(params, toks))
seg_starts = [(m.start(), m.group(1)) for m in re.finditer(r'\{Id:"table-\d+",year:"(\d{4})"', h)]
out = []
for idx, (s0, y) in enumerate(seg_starts):
    s1 = seg_starts[idx + 1][0] if idx + 1 < len(seg_starts) else s0 + 15000
    seg = h[s0:s1]
    for rm in re.finditer(r'cellType:"date",date:("[^"]*"|\w+),title:("[^"]*"|\w+)\}(.*?)\]\}', seg, re.S):
        date = rm.group(1).strip('"') if rm.group(1).startswith('"') else var.get(rm.group(1), rm.group(1))
        title = rm.group(2).strip('"') if rm.group(2).startswith('"') else var.get(rm.group(2), rm.group(2))
        urls = []
        for um in re.finditer(r'resolvedUrl:("[^"]*"|\w+)', rm.group(3)):
            u = um.group(1)
            u = u.strip('"') if u.startswith('"') else var.get(u, u)
            if isinstance(u, str):
                urls.append(u.replace("\\u002F", "/"))
        out.append({"year": y, "date": date, "title": title, "urls": urls})
json.dump(out, open(os.path.join(RAW_IR, "SU.PA", "pages", "results_table.json"), "w"), indent=1)
for r in out:
    print(r["year"], "|", r["date"], "|", r["title"], "|", len(r["urls"]), "|", " ".join(u.split("/")[-1][:45] for u in r["urls"]))
