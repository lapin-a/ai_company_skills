"""라벨-기준일 정합성 전수 점검 (NOW·ZTS 라벨 밀림 유형 재발 탐지).

분기말 저량 항목의 기준일이 그 라벨의 달력 분기말과 얼마나 떨어졌는지 본다.
회계연도가 달력과 어긋난 회사(COST 16주, KR 등)는 원래 벌어지므로,
한 회사의 어긋남이 '전 분기에 걸쳐 같은 방향으로 80일 이상'일 때만 밀림으로 본다.
"""
import csv, collections, os, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEM = "분기말 자산총계"


def qend(p):
    y, q = int(p[:4]), int(p[-1])
    return date(y, q * 3, (31, 30, 30, 31)[q - 1])


bad = 0
for f in sys.argv[1:]:
    per = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(ROOT, f), encoding="utf-8-sig")):
        v = r.get("값(원)") or r.get("값") or ""  # 국내 데이터셋은 "값(원)"
        if r["항목"] == ITEM and r["기준일"] and v != "미확인" and not v.startswith("데이터 없음"):
            per[(r["기업"], r["종목코드"])].append((date.fromisoformat(r["기준일"]) - qend(r["기간"])).days)
    for (co, tk), gaps in sorted(per.items()):
        if len(gaps) < 8:
            continue
        shifted = [g for g in gaps if abs(g) >= 80]
        if len(shifted) >= len(gaps) * 0.8 and len({g > 0 for g in shifted}) == 1:
            bad += 1
            print("  밀림 의심 %-28s %-6s %s | %d/%d분기, 중앙값 %+d일"
                  % (f, tk, co, len(shifted), len(gaps), sorted(shifted)[len(shifted) // 2]))
print("라벨 밀림 의심: %d건" % bad)
