"""검증 2: 계산값 1,616칸을 검산 열의 원본 숫자로 전수 재계산해 대조한다."""
import csv, re, sys

PATS = [
    (r"종가 ([\d.]+) × 주식수 (\d+)", lambda a, b: float(a) * float(b)),
    (r"누적 (-?\d+) − 직전누적 (-?\d+)", lambda a, b: float(a) - float(b)),
    (r"연간 (-?\d+) − 9개월누적 (-?\d+)", lambda a, b: float(a) - float(b)),
    (r"부채및자본 (-?\d+) − 총자본 (-?\d+) − 메자닌 (-?\d+)", lambda a, b, c: float(a) - float(b) - float(c)),
    (r"부채및자본 (-?\d+) − 총자본 (-?\d+)", lambda a, b: float(a) - float(b)),
    (r"연간 연결 (-?\d+) − 비지배 (-?\d+) − \(9개월누적 (-?\d+)\)", lambda a, b, c: float(a) - float(b) - float(c)),
]
path = sys.argv[1]
n = bad = skip = 0
for r in csv.DictReader(open(path, encoding="utf-8-sig")):
    if not r["값구분"].startswith("계산") or r["값"] in ("미확인",) or r["값"].startswith("데이터 없음"):
        continue
    n += 1
    for pat, fn in PATS:
        m = re.search(pat, r["검산"])
        if m:
            got, want = fn(*m.groups()), float(r["값"])
            if abs(got - want) > max(1.0, abs(want) * 1e-9):
                bad += 1
                print("불일치 %s %s %s: 값 %s ≠ 재계산 %s | %s" % (r["종목코드"], r["기간"], r["항목"], r["값"], got, r["검산"]))
            break
    else:
        skip += 1
        print("검산 형식 미인식: %s %s %s | %s" % (r["종목코드"], r["기간"], r["항목"], r["검산"][:90]))
print("계산값 %d칸 | 불일치 %d | 형식 미인식 %d" % (n, bad, skip))
