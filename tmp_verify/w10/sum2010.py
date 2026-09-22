"""2010 창 재생성 대조·집계. 사용: python sum2010.py kr|us [라운드...]
라운드마다: 2019년 이후 기존 칸 값·값구분 변경 수, 2010~2018 새 칸의 숫자/데이터 없음/미확인 수."""
import csv, collections, os, sys
track = sys.argv[1]
rounds = [int(a) for a in sys.argv[2:]] or (range(1, 15) if track == "kr" else range(1, 32))
tot = collections.Counter()
for n in rounds:
    new_f = "tmp_verify/w10/%s/%sround%d-dataset.csv" % (("k2010", "", n) if track == "kr" else ("u2010", "us-", n))
    old_f = ("kr/data/round%d-dataset.csv" if track == "kr" else "us/data/us-round%d-dataset.csv") % n
    if not os.path.exists(new_f):
        print("R%d 결과 없음" % n); continue
    new = list(csv.DictReader(open(new_f, encoding="utf-8-sig")))
    old = list(csv.DictReader(open(old_f, encoding="utf-8-sig")))
    V = "값(원)" if "값(원)" in new[0] else "값"
    k = lambda r: (r["종목코드"], r["기간"], r["항목"])
    o = {k(r): r for r in old}
    ch = [r for r in new if k(r) in o and (r[V], r["값구분"]) != (o[k(r)][V], o[k(r)]["값구분"])]
    lost = len(set(o) - {k(r) for r in new})
    c = collections.Counter()
    for r in new:
        if k(r) in o:
            continue
        v = r[V]
        c["숫자" if v.replace("-", "").replace(".", "").isdigit() else "미확인" if v == "미확인" else "데이터 없음"] += 1
    tot.update(c); tot["변경"] += len(ch); tot["사라짐"] += lost
    print("R%d 기존 %d 변경 %d 사라짐 %d | 새 칸 숫자 %d · 데이터 없음 %d · 미확인 %d" % (n, len(old), len(ch), lost, c["숫자"], c["데이터 없음"], c["미확인"]))
print("합계", dict(tot))
