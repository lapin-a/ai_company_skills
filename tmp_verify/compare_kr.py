"""tmp_verify/kr-recheck-pNN-dataset.csv(재수집)와 기존 round1~4-dataset.csv를 (종목코드, 기간, 항목) 단위로 비교한다.
실행: python tmp_verify/compare_kr.py   (프로젝트 루트에서, 있는 묶음만 비교)
"""

import csv
import glob
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
old = {}
for f in ("round1-dataset.csv", "round2-dataset.csv", "round3-dataset.csv", "round4-dataset.csv"):
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        old[(r["종목코드"], r["기간"], r["항목"])] = (r["값(원)"], r["값구분"], r["기업"], f)
new = {}
for f in sorted(glob.glob("tmp_verify/kr-recheck-p*-dataset.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        new[(r["종목코드"], r["기간"], r["항목"])] = (r["값(원)"], r["값구분"], r["기업"], f)

codes = {k[0] for k in new}
print("비교 기업 %d개, 재수집 칸 %d" % (len(codes), len(new)))
missing = [k for k in old if k[0] in codes and k not in new]
diff = [(k, old[k], new[k]) for k in new if k in old and old[k][:2] != new[k][:2]]
print("재수집에 없는 칸:", len(missing))
print("달라진 칸:", len(diff))
for k, o, n in sorted(diff):
    print("  %s %s %s | 기존 %s (%s) → 재수집 %s (%s)" % (o[2], k[1], k[2], o[0], o[1], n[0], n[1]))
