"""누적 대조 불일치 진단: 1~3분기 3개월 합 vs 3분기 누적, 차이 비율. 실행: python tmp_verify/fin/cumdiag.py corp_code 2019:rev,op 2020:rev ..."""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "kr")
import collect_fin as cf, collect_round1 as cr, collect_round2 as c2
reps = c2.pick_reports(c2.dart_key(), sys.argv[1])
for arg in sys.argv[2:]:
    y, ks = arg.split(":")
    docs = [cr.fs_section(reps["%s.%02d" % (y, m)]) for m in (3, 6, 9)]
    ds = [cf.parse(d) for d in docs]
    for k in ks.split(","):
        v = [d.get(k + "3") for d in ds]; c = ds[2].get(k + "C")
        s = sum(v); print(y, k, "3개월", v, "합", s, "3분기누적", c, "차이 %.2f%%" % ((s - c) / c * 100), "중단영업" if any(r and cr.norm(r[0]).startswith("중단영업") for d in docs for st in [cr.statements(d)] for x in (st.get("IS"), st.get("CI")) if x for r in x[2]) else "")
