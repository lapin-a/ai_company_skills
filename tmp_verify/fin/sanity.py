"""금융 데이터셋 점검: 계열 중앙값의 1/1000보다 작은 0 아닌 값(주석 번호 등 오독 의심). 실행: python tmp_verify/fin/sanity.py kr/data/round11-dataset.csv ..."""
import csv, collections, statistics, sys
S = collections.defaultdict(dict)
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        try: S[(r["기업"], r["항목"])][r["기간"]] = float(r["값(원)"])
        except ValueError: pass
n = 0
for k, ser in S.items():
    med = statistics.median(abs(v) for v in ser.values())
    for p, v in ser.items():
        if v and abs(v) < med / 1000:
            print(k, p, v, "중앙값", med); n += 1
print("의심", n)
