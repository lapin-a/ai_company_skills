"""미국 라운드 17~ 시장조사: 미수집 비금융 후보 전체 재검증 (SEC 연속분기 + 시장데이터)."""
import csv, glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import us_probe as u
import collect_us_round1 as c

OUT = "tmp_verify/us7/us_r17.json"
FIN = ("60", "61", "62", "63", "64", "65", "67")  # 라운드 10 확정: SIC 60~65·67 = 금융·보험·리츠

done = set()
for f in glob.glob("us/data/us-round*-dataset.csv"):
    for row in csv.DictReader(open(f, encoding="utf-8-sig")):
        done.add(row["종목코드"])

pool = {}
for f in glob.glob("tmp_verify/us7/us_r*.json") + ["us/us-candidates.json"]:
    if f.endswith("us_r17.json"):
        continue
    for r in json.load(open(f, encoding="utf-8"))["rows"]:
        if r.get("ticker") and r["ticker"] not in pool:
            pool[r["ticker"]] = r

asof, hold = u.spy_holdings()
weight = {tk: w for _, tk, w in hold}
rank = {tk: i + 1 for i, (_, tk, _) in enumerate(sorted(hold, key=lambda x: -x[2]))}
print("SPY 기준일", asof, "| 구성종목", len(hold), flush=True)

todo = [t for t, r in pool.items()
        if t not in done and not r.get("error") and (r.get("sic") or "")[:2] not in FIN]
todo.sort(key=lambda t: -(pool[t].get("mcapXbrl") or pool[t].get("mcap") or 0))
# 전체 재검증 (5곳 단위 라운드용)
print("재검증 대상", len(todo), " ".join(todo), flush=True)

res = []
for tk in todo:
    try:
        r = u.probe(tk)
        if r.get("sharesSrc") != "dei" and not r.get("error"):
            reps, _ = c.reports(r["cik"])
            got = c.instance_shares(r["cik"], reps[max(reps)][0])
            if got:
                r.update(sharesXbrl=got[0], mcapXbrl=r["price"] * got[0])
    except Exception as e:
        r = {"ticker": tk, "error": repr(e)[:120]}
    r["spyWeight"] = weight.get(tk)
    r["spyRank"] = rank.get(tk)
    res.append(r)
    m = (r.get("mcapXbrl") or r.get("mcap") or 0) / 1e9
    print("%-6s %-26s cik=%s SIC %-5s %7.1fB run=%-3s q=%-6s rank=%s" % (
        tk, (r.get("name") or "")[:26], r.get("cik"), r.get("sic"), m,
        r.get("run"), r.get("qCloses"), r.get("spyRank")), flush=True)

json.dump({"asof": asof, "rows": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
