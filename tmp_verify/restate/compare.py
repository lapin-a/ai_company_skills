"""재생성본(tmp_verify/restate/) ↔ 현재 데이터셋 셀 단위 대조.
값이 바뀐 칸이 모두 -restated.csv의 '재작성 반영' 칸인지 확인하고, 아닌 칸은 따로 보여준다.
사용: python tmp_verify/restate/compare.py kr|us [라운드...]"""
import csv, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    return rows[0], {(r[1], r[2], r[4]): r for r in rows[1:]}


track = sys.argv[1]
rounds = [int(a) for a in sys.argv[2:]] or list(range(1, 11 if track == "kr" else 17))
V, K = (5, 6) if track == "kr" else (5, 7)  # 값·값구분 열
total = Counter()
for rnd in rounds:
    name = ("round%d" if track == "kr" else "us-round%d") % rnd
    base = os.path.join(ROOT, track, "data", name + "-dataset.csv")
    new = os.path.join(ROOT, "tmp_verify", "restate", name + "-dataset.csv")
    if not os.path.exists(new):
        print(name, "재생성본 없음")
        continue
    _, b = load(base)
    _, n = load(new)
    _, log = load(os.path.join(ROOT, "tmp_verify", "restate", name + "-restated.csv"))
    kinds = Counter(r[5] for r in log.values())
    applied = {k for k, r in log.items() if r[5] == "재작성 반영"}
    c = Counter()
    other = []
    for k in b.keys() | n.keys():
        if k not in b or k not in n:
            c["키 불일치"] += 1
            other.append((k, b.get(k, ["-"] * 9)[V], n.get(k, ["-"] * 9)[V]))
            continue
        if b[k][V] == n[k][V]:
            if b[k][K] != n[k][K] or b[k][7 if track == "kr" else 8] != n[k][7 if track == "kr" else 8]:
                c["값 같고 값구분·출처만 다름"] += 1
            continue
        if k in applied:
            c["재작성 반영"] += 1
        else:
            c["재작성 기록 밖 변경"] += 1
            other.append((k, b[k][V], n[k][V]))
    total.update(c)
    total.update({"기록:" + x: y for x, y in kinds.items()})
    print(name, dict(c), "| 기록", dict(kinds))
    for k, x, y in sorted(other)[:15]:
        print("   ", k, x, "->", y)
print("합계", dict(total))
