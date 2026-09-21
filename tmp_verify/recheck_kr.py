"""국내 31개 기업 재수집(2026-09-19 파서 수정 검증용). 3개 기업마다 결과 파일을 따로 쓴다.

- 결과: tmp_verify/kr-recheck-pNN-dataset.csv (+ -summary.json). 기존 roundN-dataset.csv는 건드리지 않는다.
- 이어하기: 이미 있는 묶음 파일은 건너뛴다. 중간에 끊기면 같은 명령을 다시 실행하면 된다.
- 실행: python tmp_verify/recheck_kr.py   (프로젝트 루트에서)
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import collect_round2 as c2  # noqa: E402

CHUNK = 3
companies = []
for f in ("round1-dataset.csv", "round2-dataset.csv", "round3-dataset.csv", "round4-dataset.csv"):
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        if (r["기업"], r["종목코드"]) not in companies:
            companies.append((r["기업"], r["종목코드"]))
cc = {r["종목코드"]: r["DART corp_code"] for r in csv.DictReader(open("largecap100.csv", encoding="utf-8-sig"))}

parts = [companies[i:i + CHUNK] for i in range(0, len(companies), CHUNK)]
print("%d개 기업, %d묶음" % (len(companies), len(parts)), flush=True)
for n, part in enumerate(parts, 1):
    out = "tmp_verify/kr-recheck-p%02d-dataset.csv" % n
    if os.path.exists(out):
        print("p%02d 건너뜀 (이미 있음)" % n, flush=True)
        continue
    c2.TOP10 = [(name, code, cc[code]) for name, code in part]
    c2.OUT = out + ".part"  # 끝까지 쓴 뒤에만 이름을 바꿔, 중간에 끊긴 파일을 완료로 오인하지 않는다
    c2.main()  # c2가 요약 파일을 OUT의 '-dataset.csv' → '-summary.json'으로 쓴다
    summ = out.replace("-dataset.csv", "-summary.json")
    os.replace(summ + ".part", summ)
    os.replace(out + ".part", out)
    print("p%02d 저장: %s" % (n, ", ".join(p[0] for p in part)), flush=True)
print("완료", flush=True)
