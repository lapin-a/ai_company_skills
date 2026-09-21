"""라운드 16 미확인 진단 2: 해당 분기 보고서(accn) 안에 어떤 태그가 실제로 있는지 본다."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import collect_us_round1 as c

CASES = [("PPG", "0000079879", ["2024-12-31", "2025-12-31", "2023-12-31"], "Operating.*Income|IncomeLossFromContinuing"),
         ("CHD", "0000313927", ["2025-03-31", "2025-06-30", "2025-09-30"], "OperatingActivities"),
         ("PHM", "0000822416", ["2021-03-31"], "Revenue|Sales")]

for tk, cik, ends, pat in CASES:
    print("=" * 78); print(tk, cik, "| 패턴", pat)
    reps, forms = c.reports(cik)
    fx = c.Facts(cik)
    for end in ends:
        accns = reps.get(end)
        print("-- 보고기간 %s | accn %s | form %s" % (end, accns, [forms.get(a) for a in (accns or [])]))
        if not accns:
            print("   (해당 보고기간 없음)"); continue
        found = False
        for (tag, a), es in fx.idx.items():
            if a not in accns or not re.search(pat, tag):
                continue
            for e in es:
                if not e.get("start") or c.days(e) < 60:
                    continue
                found = True
                print("   %-58s %s~%s %4d일 %15d" % (tag, e["start"], e["end"], c.days(e), e["val"]))
        if not found:
            print("   (패턴에 맞는 기간 태그 없음)")
