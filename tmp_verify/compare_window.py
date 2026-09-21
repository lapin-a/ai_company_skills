"""2010년대 백필 회귀 검사: 새 데이터셋의 2019Q1 이후 행이 기존 데이터셋과 같은지 본다.

실행: python tmp_verify/compare_window.py <기존 csv> <새 csv>
키 = (종목코드, 기간, 항목). 기준일·값·값구분·출처(·검산) 열을 모두 비교한다.
"""
import csv
import sys


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    return {(r["종목코드"], r["기간"], r["항목"]): r for r in rows}


old, new = load(sys.argv[1]), load(sys.argv[2])
keep = {k for k in new if k[1] >= "2019Q1"}
missing = set(old) - keep
extra = keep - set(old)
diff = {}
for k in set(old) & keep:
    cols = [c for c in old[k] if old[k][c] != new[k].get(c)]
    if cols:
        diff[k] = cols
val_diff = [k for k, cols in diff.items() if any(c.startswith("값") for c in cols)]
print("%s | 기존 %d행 · 새(2019~) %d행 · 빠진 행 %d · 늘어난 행 %d · 다른 행 %d (값·값구분 다른 행 %d)" % (
    sys.argv[1].replace("\\", "/").split("/")[-1], len(old), len(keep), len(missing), len(extra), len(diff), len(val_diff)))
for k in sorted(diff)[:int(sys.argv[3]) if len(sys.argv) > 3 else 8]:
    print("   ", k, {c: (old[k][c], new[k][c]) for c in diff[k]})
