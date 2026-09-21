"""라운드 30 이후 시장조사: SPY 비중 476~504위 판정 + 전체 504행 대비 미수집 현황."""
import csv, glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import us_probe as u
import collect_us_round1 as c

done = set()
for f in glob.glob("us/data/us-round*-dataset.csv"):
    for row in csv.DictReader(open(f, encoding="utf-8-sig")):
        done.add(row["종목코드"])
asof, hold = u.spy_holdings()
rank = sorted(hold, key=lambda x: -x[2])
print("SPY 기준일", asof, "| 종목 행", len(rank), "| 기수집", len(done))
res = []
for i, (nm, tk, w) in enumerate(rank[475:], 476):
    if tk in done:
        continue
    try:
        r = u.probe(tk)
        if r.get("sharesSrc") != "dei" and not r.get("error"):
            reps, _ = c.reports(r["cik"])
            got = c.instance_shares(r["cik"], reps[max(reps)][0])
            if got:
                r.update(sharesXbrl=got[0], mcapXbrl=r["price"] * got[0])
    except Exception as e:
        r = {"ticker": tk, "error": repr(e)[:100]}
    r["spyWeight"], r["spyRank"] = w, i
    res.append(r)
    m = (r.get("mcapXbrl") or r.get("mcap") or 0) / 1e9
    print("%3d %-6s %-26s SIC %-5s %6.1fB run=%s q=%s %s" % (i, tk, (r.get("name") or "")[:26], r.get("sic"), m, r.get("run"), r.get("qCloses"), r.get("error", "")), flush=True)
json.dump({"asof": asof, "rows": res}, open("tmp_verify/us7/us_r30.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
