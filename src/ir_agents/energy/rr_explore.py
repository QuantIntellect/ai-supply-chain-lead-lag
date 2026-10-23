import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/rr"
url = sys.argv[1]
out = sys.argv[2]
r = irlib.fetch(url)
print(r.status_code, len(r.content), r.url)
with open(os.path.join(SCR, out), "wb") as f:
    f.write(r.content)
