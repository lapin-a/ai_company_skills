"""국내 데이터셋 이상치(확정 D안)·부호전환 집계. 실행: python tmp_verify/outliers_kr.py [파일들...]
인자가 없으면 round1~4-dataset.csv. 결과는 라운드별(파일별)과 전체로 출력한다."""
import collections, csv, os, statistics as st, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
files = sys.argv[1:] or ["round1-dataset.csv", "round2-dataset.csv", "round3-dataset.csv", "round4-dataset.csv"]
CALC = ("계산",)


def judge(rows):
    W = sorted({r["기간"] for r in rows})
    S = collections.defaultdict(dict)
    for r in rows:
        v = r.get("값(원)") or r["값"]  # 미국 데이터셋은 "값"+"통화"
        if v != "미확인" and not v.startswith("데이터 없음"):
            S[(r["기업"], r["항목"])][r["기간"]] = (float(v), r["값구분"])
    out, flips = [], collections.Counter()
    for (co, it), ser in S.items():
        if len(ser) < 12:
            continue
        med_abs = st.median(abs(v) for v, _ in ser.values())
        pairs = []
        for a, b in zip(W, W[1:]):
            if a in ser and b in ser:
                p, c = ser[a][0], ser[b][0]
                if p != 0 and c != 0 and (p > 0) != (c > 0):
                    flips[it] += 1
                # 직전 ≤ 0 구간은 변화율 없음. 부호전환 구간(양→음)도 이상치와 섞지 않는다(확정 규칙 문구).
                # 라운드 1~3 집계(189건)는 이 구간을 넣었고 라운드 4(60건)는 뺐다 → 2026-09-19 뺀 쪽으로 통일.
                if p > 0 and c > 0:
                    pairs.append((b, p, c, (c - p) / p, ser[b][1]))
        if len(pairs) < 3:
            continue
        rates = [x[3] for x in pairs]
        m = st.median(rates)
        mad = st.median(abs(x - m) for x in rates)
        if mad == 0:
            continue
        for q, p, c, r, kind in pairs:
            z = abs(r - m) / (1.4826 * mad)
            if z > 3.5 and abs(c - p) >= 0.2 * med_abs and p >= 0.2 * med_abs:
                out.append((co, it, q, round(z, 1), p, c, kind))
    return out, flips


if __name__ == "__main__":
    allrows = []
    for f in files:
        rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        allrows += rows
        o, fl = judge(rows)
        print("%s | 이상치 %d (계산값 %d) | 부호전환 %d %s" % (f, len(o), sum(x[6].startswith(CALC) for x in o), sum(fl.values()), dict(fl)))
    o, fl = judge(allrows)
    print("전체 | 이상치 %d (계산값 %d) | 부호전환 %d %s" % (len(o), sum(x[6].startswith(CALC) for x in o), sum(fl.values()), dict(fl)))
    if os.environ.get("LIST"):
        for x in o:
            if x[0] in os.environ["LIST"].split(","):
                print("  | %s | %s | %s | %.1f | %s |" % (x[0], x[1], x[2], x[3], x[6]))
