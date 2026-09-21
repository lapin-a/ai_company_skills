"""브랜드 검수팀 재검증: 미국 라운드 13~15 (2026-09-21).

기획 2팀이 낸 데이터셋 자체를 검사한다.
1) 예측 표현 (로그 본문)
2) 원문 링크·기준일 유무, 12분기 연속 이력 (재무 8항목·시장 3항목 각각)
3) 커버리지 중복 (국내 5개 라운드 + 미국 15개 라운드 전체)
4) 분기 라벨 겹침·빠짐
"""
import csv, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
ROUNDS = (13, 14, 15)
FIN = ["분기별 매출액", "분기별 영업이익", "분기별 당기순이익(지배)", "분기별 영업활동현금흐름",
       "분기말 자산총계", "분기말 부채총계", "분기말 총자본(자기자본)", "분기말 지배지분 자본"]
MKT = ["분기말 종가", "분기말 상장주식수", "분기말 시가총액"]
WINDOW = ["%dQ%d" % (y, q) for y in range(2019, 2027) for q in (1, 2, 3, 4) if (y, q) <= (2026, 2)]
num = lambda v: re.match(r"-?[\d.]+$", v)

# 1) 예측 표현
pat = r"무조건|반드시 (?:오|상승|하락)|확실히 (?:오|상승)|오를 것|상승할 것|하락할 것|전망이다|예상된다|기대된다"
for rnd in ROUNDS:
    p = os.path.join(ROOT, "us-round%d-log.md" % rnd)
    txt = re.sub(r"[*_`]", "", open(p, encoding="utf-8").read())
    print("라운드 %d 예측 표현: %s" % (rnd, re.findall(pat, txt) or "0건"))

# 3) 중복 (전 라운드)
seen = {}
dups = []
for f, tag in [("round%d-dataset.csv" % i, "국내 R%d" % i) for i in range(1, 6)] + \
              [("us-round%d-dataset.csv" % i, "미국 R%d" % i) for i in range(1, 16)]:
    for r in csv.DictReader(open(os.path.join(ROOT, f), encoding="utf-8-sig")):
        code = r["종목코드"]
        if code in seen and seen[code] != tag:
            dups.append((code, seen[code], tag))
        seen[code] = tag
print("중복 종목:", sorted(set(dups)) or "0건")

# 2)·4) 라운드별 회사 판정
for rnd in ROUNDS:
    rows = list(csv.DictReader(open(os.path.join(ROOT, "us-round%d-dataset.csv" % rnd), encoding="utf-8-sig")))
    per = collections.defaultdict(dict)
    for r in rows:
        per[r["종목코드"]][(r["기간"], r["항목"])] = r
    print("\n=== 라운드 %d ===" % rnd)
    for tk, cells in per.items():
        # 출처·기준일
        bad_src = [k for k, r in cells.items() if num(r["값"]) and not (r["출처"].startswith("http") and r["기준일"])]
        # 라벨 빠짐(그 라벨의 모든 항목이 "해당 라벨 보고서 없음")
        missing_lab = sorted({p for p in WINDOW
                              if all(cells[(p, it)]["출처"] == "해당 라벨 보고서 없음" for it in FIN if (p, it) in cells)
                              and any((p, it) in cells for it in FIN)})

        def run(items):
            n = 0
            for p in reversed(WINDOW):
                if all(num(cells[(p, it)]["값"]) for it in items if (p, it) in cells):
                    n += 1
                else:
                    break
            return n

        fin_run, mkt_run = run(FIN), run(MKT)
        ok = not bad_src and fin_run >= 12 and mkt_run >= 12
        note = []
        if bad_src:
            note.append("출처 누락 %d" % len(bad_src))
        if fin_run < 12:
            note.append("재무 연속 %d" % fin_run)
        if mkt_run < 12:
            note.append("시장 연속 %d" % mkt_run)
        if missing_lab:
            note.append("빈 라벨 " + ",".join(missing_lab))
        print("  %-5s %s %s" % (tk, "O" if ok else "X", " | ".join(note)))
