"""HEAD/GET-probe SAP IR document URL patterns."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import fetch_util as fu

BASE = "https://www.sap.com/docs/download/investors/%d/sap-%d-%s.pdf"
def probe(y, kinds):
    out = {}
    for k in kinds:
        u = BASE % (y, y, k)
        try:
            r = fu.sess().head(u, headers={"User-Agent": fu.UA}, timeout=30, allow_redirects=True)
            fu.time.sleep(0.6)
            out[k] = (r.status_code, r.headers.get("content-length"))
        except Exception as e:
            out[k] = ("ERR", None)
    return out

if __name__ == "__main__":
    ys = [int(a) for a in sys.argv[1].split(",")]
    kinds = sys.argv[2].split(",")
    for y in ys:
        print(y, probe(y, kinds))
