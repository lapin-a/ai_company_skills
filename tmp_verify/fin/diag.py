"""python tmp_verify/fin/diag.py corp_code period — 표 목록·파싱 결과 출력, 원문은 tmp_verify/fin/<corp>-<period>.html"""
import os, sys, re
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "kr")
import collect_fin as cf, collect_round1 as cr, collect_round2 as c2
cc, p = sys.argv[1], sys.argv[2]
rcp = c2.pick_reports(c2.dart_key(), cc)[p]
doc = cr.fs_section(rcp)
open("tmp_verify/fin/%s-%s.html" % (cc, p), "w", encoding="utf-8").write(doc or "")
print(rcp, "doc", len(doc or ""))
st = cr.statements(doc)
for k, (u, h, rows) in st.items():
    print("==", k, u, h[:60], len(rows))
    for r in rows[:int(sys.argv[3]) if len(sys.argv) > 3 else 0]: print("   ", r[:5])
d = cf.parse(doc)
print({k: v for k, v in d.items()})
print("verify", cr.verify(d))
