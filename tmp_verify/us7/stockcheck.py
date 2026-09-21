"""47칸 수정 회귀 판정: 바뀐 칸마다 해당 분기의 자산 = 부채 + 총자본, 암시 비지배(총자본 − 지배)가 원 공시와 같은지 수정 전·후로 본다."""
import collections, csv, os, sys
KEY = ("종목코드", "기간", "항목")
A, L, E, P = "분기말 자산총계", "분기말 부채총계", "분기말 총자본(자기자본)", "분기말 지배지분 자본"
load = lambda p: {tuple(r[k] for k in KEY): r for r in csv.DictReader(open(p, encoding="utf-8-sig"))}
n = lambda d, t, q, i: int(d[(t, q, i)]["값"]) if d[(t, q, i)]["값"].lstrip("-").isdigit() else None
tot = collections.Counter()
for rnd in range(1, 32):
    a, b = load("us/data/us-round%d-dataset.csv" % rnd), load("tmp_verify/us7/qd%d-dataset.csv" % rnd)
    ch = [k for k in a if a[k]["값"] != b[k]["값"] or a[k]["값구분"] != b[k]["값구분"]]
    for t, q in sorted({k[:2] for k in ch}):
        items = [k[2] for k in ch if k[:2] == (t, q)]
        st = []
        for d in (a, b):
            v = [n(d, t, q, i) for i in (A, L, E, P)]
            st.append("대차%s" % ("O" if None not in v[:3] and v[0] == v[1] + v[2] else "X") + " 비지배%s" % (v[2] - v[3] if None not in v[2:] else "?"))
        other = [i for i in items if i not in (A, L, E, P)]
        tot["저량 외" if other else "저량"] += len(items)
        print(rnd, t, q, [i[4:] for i in items], "전:", st[0], "후:", st[1], "저량 외 변경!" if other else "")
print(dict(tot))
