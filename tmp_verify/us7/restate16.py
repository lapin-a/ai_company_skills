"""규칙 2(후속 보고서 비교기간)로 채운 칸의 재작성 노출도 측정.

그 기간이 실린 보고서를 전부 모아 값이 서로 다른지 본다.
값이 하나뿐이면 재작성이 없었다는 뜻이고, 규칙 2는 원 공시값과 같은 숫자를 쓴 것이다.
"""
import csv, glob, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import collect_us_round1 as c

FLOW = {"분기별 매출액": c.REV, "분기별 영업이익": ["OperatingIncomeLoss"],
        "분기별 당기순이익(지배)": ["NetIncomeLoss"],
        "분기별 영업활동현금흐름": c.OCF}
STOCK = {"분기말 자산총계": ["Assets"], "분기말 부채총계": ["Liabilities"],
         "분기말 총자본(자기자본)": ["StockholdersEquity"], "분기말 지배지분 자본": ["StockholdersEquity"]}
TAG = {**FLOW, **STOCK}
rows = []
for f in sorted(glob.glob("us/data/us-round*-dataset.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        if r["값구분"] == "공시(후속 보고서 비교기간)":
            rows.append((os.path.basename(f), r))
print("대상 %d칸\n" % len(rows))

fx_cache, same, diff = {}, 0, []
for fn, r in rows:
    tk, cik = r["종목코드"], None
    for g in glob.glob("us/collect_us_round*.py"):
        pass
    # CIK는 출처 URL에서 뽑는다
    cik = r["출처"].split("/data/")[1].split("/")[0].zfill(10)
    if cik not in fx_cache:
        fx_cache[cik] = c.Facts(cik)
    fx = fx_cache[cik]
    vals = collections.defaultdict(set)
    for tag in TAG[r["항목"]]:
        for (tg, a), es in fx.idx.items():
            if tg != tag:
                continue
            for e in es:
                inst = r["항목"] in STOCK
                ok = (e["end"] == r["기준일"]) and (("start" not in e) if inst else 70 <= c.days(e) <= 118)
                if ok:
                    vals[tag].add(e["val"])
    v = vals.get(next((t for t in TAG[r["항목"]] if t in vals), ""), set())
    if len(v) <= 1:
        same += 1
    else:
        diff.append((tk, r["기간"], r["항목"], sorted(v), r["값"]))
    print("  %-5s %-7s %-16s 보고서별 값 %d종 %s" % (tk, r["기간"], r["항목"], len(v), sorted(v)))
print("\n값이 하나뿐(재작성 없음): %d칸 | 여러 개: %d칸" % (same, len(diff)))
for d in diff:
    print("  ! %s" % (d,))
