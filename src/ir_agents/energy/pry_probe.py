import sys; sys.path.insert(0, "/Users/sinamirzaei/Documents/aimapping/src/ir_agents/energy"); import irlib
import re, os
SCR = "/private/tmp/claude-501/-Users-sinamirzaei-Documents-aimapping/57e0a0d0-6441-40ef-828b-57eeb87e7b21/scratchpad/pry"
urls = sys.argv[1:]
for u in urls:
    try:
        r = irlib.fetch(u)
    except Exception as e:
        print("ERR", u, e); continue
    name = irlib.safe_name(u.split("//",1)[1])[:100] + ".html"
    with open(os.path.join(SCR, name), "wb") as f:
        f.write(r.content)
    print(r.status_code, len(r.content), r.url, "->", name)
