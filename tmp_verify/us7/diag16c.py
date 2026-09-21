"""라운드 16 미확인 진단 3: companyfacts 사실 수 + XBRL 원문에 태그가 있는지."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import collect_us_round1 as c
import collect_us_round2 as r2

CASES = [("CHD", "0000313927", ["0000950170-25-061624", "0000950170-25-101235", "0001193125-25-260515"],
          "OperatingActivities"),
         ("PHM", "0000822416", ["0000822416-21-000018"], "Revenues$|RevenueFromContract")]

for tk, cik, accns, pat in CASES:
    print("=" * 78); print(tk, cik)
    fx = c.Facts(cik)
    cnt = {}
    for (_, a), es in fx.idx.items():
        cnt[a] = cnt.get(a, 0) + len(es)
    for a in accns:
        print("-- accn %s | companyfacts 사실 수 %s" % (a, cnt.get(a, 0)))
        x = c.instance(cik, a)
        print("   원문 길이 %d" % len(x or ""))
        hits = [(t, v, d) for t, v, d, dim in c.instance_facts(x, pat) if not dim]
        for t, v, d in hits[:12]:
            print("   원문태그 %-58s %s %s" % (t, d, v))
        if not hits:
            print("   원문에도 패턴 태그 없음")
