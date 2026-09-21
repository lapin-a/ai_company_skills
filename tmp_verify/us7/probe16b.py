"""라운드 16 시장조사 보충: EIX 재조회 + 차순위 후보 6곳 검증. SPY xlsx는 1차에서 받았으므로 생략."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import us_probe as u
import collect_us_round1 as c

SRC = "tmp_verify/us7/us_r16.json"
TODO = ["EIX", "CMS", "STZ", "EXE", "LUV", "LYB", "STE"]
KNOWN_CIK = {"EIX": "0000827052"}  # 1차에서 efts 조회 실패 → 기존 후보 풀 값으로 확인

d = json.load(open(SRC, encoding="utf-8"))
rows = [r for r in d["rows"] if r.get("ticker") not in TODO]
for tk in TODO:
    try:
        r = u.probe(tk)
        if not r.get("cik") and tk in KNOWN_CIK:
            r = u.probe(tk, cik=KNOWN_CIK[tk]) if "cik" in u.probe.__code__.co_varnames else r
        if r.get("sharesSrc") != "dei" and not r.get("error") and r.get("cik"):
            reps, _ = c.reports(r["cik"])
            got = c.instance_shares(r["cik"], reps[max(reps)][0])
            if got:
                r.update(sharesXbrl=got[0], mcapXbrl=r["price"] * got[0])
    except Exception as e:
        r = {"ticker": tk, "error": repr(e)[:120]}
    rows.append(r)
    m = (r.get("mcapXbrl") or r.get("mcap") or 0) / 1e9
    print("%-6s %-26s cik=%s SIC %-5s %7.1fB run=%-3s q=%-6s" % (
        tk, (r.get("name") or "")[:26], r.get("cik"), r.get("sic"), m, r.get("run"), r.get("qCloses")), flush=True)
json.dump({"asof": d["asof"], "rows": rows}, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("updated", SRC)
