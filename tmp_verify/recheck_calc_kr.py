"""국내 계산값 이상치(확정 D안, 통일 방식) 원문 재확인. 실행: python tmp_verify/recheck_calc_kr.py round1-dataset.csv ...
경로 A: 출처의 두 보고서를 DART에서 다시 받아 원본 누적값 재추출 → 재계산 = 저장값?
경로 B(4분기 손익만): 같은 해 Q1~Q3 3개월 공시값(저장) + 저장 Q4 = 연간 원본값?  (3분기 누적과 독립)
"""

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "kr"))  # 2026-09-21 폴더 정리 후 수집기는 kr/
sys.path.insert(0, os.path.join(ROOT, "tmp_verify"))
os.chdir(ROOT)
import collect_round1 as cr  # noqa: E402
from outliers_kr import judge  # noqa: E402

KEY = {"분기별 매출액": "rev", "분기별 영업이익": "op", "분기별 당기순이익(지배)": "ni", "분기별 영업활동현금흐름": "ocf"}
files = sys.argv[1:]
rows = [r for f in files for r in csv.DictReader(open(f, encoding="utf-8-sig"))]
R = {(r["기업"], r["기간"], r["항목"]): r for r in rows}
RESTATED = {(r["종목코드"], r["기간"], r["항목"]): r for f in files if os.path.exists(f.replace("-dataset", "-restated"))
            for r in csv.DictReader(open(f.replace("-dataset", "-restated"), encoding="utf-8-sig"))}
cache = {}


def parsed(rcp):
    if rcp not in cache:
        cache[rcp] = cr.parse(cr.fs_section(rcp))
    return cache[rcp]


out, _ = judge(rows)
calc = [x for x in out if x[6].startswith("계산")]
print("계산값 이상치 %d건" % len(calc), flush=True)
ok_a = ok_b = nb = 0
for co, it, q, z, p, c, kind in calc:
    r = R[(co, q, it)]
    ra, rb = re.findall(r"rcpNo=(\d+)", r["출처"])[:2]
    k = KEY[it]
    a, b = parsed(ra).get(k + "C"), parsed(rb).get(k + "C")
    if "재작성 반영" in kind:
        # 재작성 반영 칸은 원 보고서 누적값이 아니라 나중 보고서 비교열 값으로 계산됐다 → 경로 A 대상이 아니다.
        # 대신 -restated.csv 기록의 원 공시값이 원 보고서 재계산값과 같은지 본다.
        rec = RESTATED.get((r["종목코드"], q, it))
        re_v = a - b if None not in (a, b) else None
        good = rec is not None and re_v == int(rec["원 공시값"])
        ok_a += good
        print("| %s | %s | %s | %.1f | %s | 재작성 반영: 원 공시 %s, 원 보고서 재계산 %s → %s |" % (
            co, it.replace("분기별 ", ""), q, z, format(stored := int(r["값(원)"]), ","),
            rec and format(int(rec["원 공시값"]), ","), re_v, "O" if good else "X"), flush=True)
        continue
    re_v = a - b if None not in (a, b) else None
    stored = int(r["값(원)"])
    good_a = re_v == stored
    ok_a += good_a
    line_b = "-"
    if kind.startswith("계산(연간"):  # 경로 B
        y = q[:4]
        q13 = [R.get((co, "%sQ%d" % (y, n), it)) for n in (1, 2, 3)]
        if all(x and x["값구분"] == "공시" for x in q13):
            s = sum(int(x["값(원)"]) for x in q13) + stored
            nb += 1
            ok_b += s == a
            line_b = "Q1~Q3 공시 합 %s + Q4 = %s vs 연간 %s → %s" % (
                format(s - stored, ","), format(s, ","), format(a, ","), "일치" if s == a else "차이 %s" % format(s - a, ","))
        else:
            line_b = "Q1~Q3 중 공시 아닌 칸 있음(건너뜀)"
    print("| %s | %s | %s | %.1f | %s | %s | %s | %s - %s | %s |" % (
        co, it.replace("분기별 ", ""), q, z, format(stored, ","), format(re_v, ",") if re_v is not None else "추출 실패",
        "O" if good_a else "X", format(a, ",") if a is not None else "-", format(b, ",") if b is not None else "-", line_b), flush=True)
print("경로 A 일치 %d/%d | 경로 B 일치 %d/%d" % (ok_a, len(calc), ok_b, nb))
