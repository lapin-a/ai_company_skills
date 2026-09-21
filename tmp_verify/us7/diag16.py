"""라운드 16 미확인 7칸 진단: 해당 기업·항목의 태그별 기간 값을 보고서(accn) 단위로 훑는다."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import collect_us_round1 as c

CASES = [("PPG", "0000079879", ["OperatingIncomeLoss"], ("2024-01", "2026-01")),
         ("CHD", "0000313927", c.OCF, ("2024-10", "2025-10")),
         ("PHM", "0000822416", c.REV, ("2020-10", "2021-04"))]

for tk, cik, tags, (lo, hi) in CASES:
    print("=" * 78); print(tk, cik, tags)
    reps, forms = c.reports(cik)
    acc2end = {a: e for e, v in reps.items() for a in v}
    fx = c.Facts(cik)
    for t in tags:
        hits = [(a, e) for (tag, a), es in fx.idx.items() if tag == t for e in es
                if e.get("start") and lo <= e["end"] <= hi]
        if not hits:
            print("  [%s] 구간 값 없음" % t); continue
        print("  [%s]" % t)
        for a, e in sorted(hits, key=lambda x: (acc2end.get(x[0], ""), x[1].get("start"))):
            d = c.days(e)
            if d < 60:
                continue
            print("    보고기간 %s(%s) | %s~%s %4d일 %15d | accn=%s"
                  % (acc2end.get(a, "?"), forms.get(a, "?"), e["start"], e["end"], d, e["val"], a))
