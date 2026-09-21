"""라운드별 결측 요약: 값/데이터없음/미확인, 기업별 미확인·데이터없음 내역."""
import csv, collections, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for rnd in [int(a) for a in sys.argv[1:]]:
    rows = list(csv.DictReader(open(os.path.join(ROOT, "us-round%d-dataset.csv" % rnd), encoding="utf-8-sig")))
    kind = lambda v: "미확인" if v == "미확인" else ("없음" if v.startswith("데이터 없음") else "값")
    cnt = collections.Counter(kind(r["값"]) for r in rows)
    unk = collections.Counter(r["종목코드"] for r in rows if r["값"] == "미확인")
    non = collections.Counter(r["종목코드"] for r in rows if r["값"].startswith("데이터 없음"))
    print("\n=== 라운드 %d === 행 %d %s" % (rnd, len(rows), dict(cnt)))
    print("  미확인:", dict(unk) or "0")
    for tk in unk:
        items = collections.Counter(r["항목"] for r in rows if r["종목코드"] == tk and r["값"] == "미확인")
        srcs = {r["출처"] for r in rows if r["종목코드"] == tk and r["값"] == "미확인"}
        print("     %-5s %s | 사유 %s" % (tk, dict(items), list(srcs)[:2]))
    print("  데이터없음:", dict(non) or "0")
    for tk in non:
        srcs = collections.Counter(r["출처"] for r in rows if r["종목코드"] == tk and r["값"].startswith("데이터 없음"))
        print("     %-5s %s" % (tk, dict(srcs)))
