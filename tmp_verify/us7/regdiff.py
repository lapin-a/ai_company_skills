"""회귀 대조: 원본 us-roundN-dataset.csv vs 재생성 qdN-dataset.csv.
키(기업,종목코드,기간,항목)별로 값·통화·값구분·출처를 비교하고, 비고/검산만 다른 건 따로 센다."""
import csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.path.join(ROOT, "tmp_verify", "us7")
KEY = ("기업", "종목코드", "기간", "항목")
HARD = ("값", "통화", "값구분", "출처", "기준일")


def load(p):
    d = {}
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        d[tuple(r[k] for k in KEY)] = r
    return d


for rnd in [int(a) for a in sys.argv[1:]] or list(range(1, 17)):
    a_p = os.path.join(ROOT, "us", "data", "us-round%d-dataset.csv" % rnd)
    b_p = os.path.join(TMP, "qd%d-dataset.csv" % rnd)
    if not os.path.exists(b_p):
        print("라운드 %2d | 재생성 파일 없음" % rnd); continue
    A, B = load(a_p), load(b_p)
    only_a = sorted(set(A) - set(B))
    only_b = sorted(set(B) - set(A))
    hard, soft = [], 0
    for k in set(A) & set(B):
        if any(A[k].get(f, "") != B[k].get(f, "") for f in HARD):
            hard.append(k)
        elif A[k] != B[k]:
            soft += 1
    print("라운드 %2d | 행 %d/%d | 값·출처 변경 %d | 비고만 변경 %d | 원본만 %d | 재생성만 %d"
          % (rnd, len(A), len(B), len(hard), soft, len(only_a), len(only_b)))
    for k in hard[:10]:
        print("   ! %s" % (k,))
        for f in HARD:
            if A[k].get(f, "") != B[k].get(f, ""):
                print("     %s: %r -> %r" % (f, A[k].get(f, ""), B[k].get(f, "")))
    for k in (only_a[:5] + only_b[:5]):
        print("   ? 키 불일치 %s" % (k,))
