"""금융 항목 세트 사전 조사: 업종별 1곳씩 연결손익계산서 행 라벨 출력."""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "kr")
import collect_round1 as cr, collect_round2 as c2

CORPS = {"기업은행": "00149646", "삼성생명": "00126256", "삼성증권": "00104856", "KB금융": "00688996", "삼성카드": "00126292", "카카오페이": "01244601"}
dkey = c2.dart_key()
for name, cc in CORPS.items():
    reps = c2.pick_reports(dkey, cc)
    for p in [x for x in ("2022.12", "2025.12", "2026.06") if x in reps]:
        for _ in range(3):
            try:
                st = cr.statements(cr.fs_section(reps[p])); break
            except Exception as e:
                print("retry", e); import time; time.sleep(5)
        print("=====", name, p, reps[p], sorted(st))
        for k in ("IS", "CI"):
            if k in st:
                print("--", k, st[k][1][:80])
                for r in st[k][2]:
                    if r: print("   ", cr.norm(r[0]), cr.values(r)[:2])
                break
