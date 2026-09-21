"""2019년 국내 시장데이터 백필 (KRX 오픈API). 실행: python kr/backfill_2019_krx.py [출력폴더]

공공데이터포털 주식시세 V2는 서비스 시작일이 2020-01-02라 2019년 4개 분기를 못 받았다(612칸).
KRX 오픈API 사용 승인이 확인돼(2026-09-21) 같은 3항목을 KRX에서 받아 채운다.

- 분기말이 휴장일이면 분기말 이하 최신 거래일을 쓰고, 실제 거래일을 기준일 열에 적는다(기존 규칙).
- 코스피·코스닥을 모두 조회한다. 2019년에 시장이 달랐던 기업이 있다(포스코퓨처엠=포스코케미칼, 당시 코스닥).
- 자체 검증: 종가 × 상장주식수 = 시가총액. 어긋나면 값을 넣지 않고 미확인으로 둔다.
- KRX에도 없으면 상장 전이다. 종목 기본정보의 상장일로 확인해 `데이터 없음(상장 전)`으로 바로잡는다.
"""
import csv, glob, json, os, sys, urllib.parse, urllib.request
from datetime import date, timedelta

BASE = "https://data-dbg.krx.co.kr/svc/apis/"
MKTS = [("KOSPI", "sto/stk_bydd_trd"), ("KOSDAQ", "sto/ksq_bydd_trd")]
ITEM = {"분기말 종가": "TDD_CLSPRC", "분기말 상장주식수": "LIST_SHRS", "분기말 시가총액": "MKTCAP"}
KEY = json.load(open(".claude/settings.local.json", encoding="utf-8"))["env"]["KRX_API_KEY"]
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "kr/data"


def api(path, **kw):
    url = BASE + path + "?" + urllib.parse.urlencode(kw)
    req = urllib.request.Request(url, headers={"AUTH_KEY": KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
    return next(v for v in d.values() if isinstance(v, list)), url


def quarter_day(q_end):
    """분기말 이하 최신 거래일과 그날의 {종목코드: (행, 시장, 출처url)}."""
    d = q_end
    for _ in range(12):
        day, got = d.strftime("%Y%m%d"), {}
        for mkt, path in MKTS:
            rows, url = api(path, basDd=day)
            for x in rows:
                got.setdefault(x["ISU_CD"], (x, mkt, url))
        if got:
            return d.isoformat(), got
        d -= timedelta(days=1)
    raise SystemExit("거래일을 찾지 못했다: %s" % q_end)


def main():
    qs = {}
    for q, qe in (("2019Q1", date(2019, 3, 31)), ("2019Q2", date(2019, 6, 30)),
                  ("2019Q3", date(2019, 9, 30)), ("2019Q4", date(2019, 12, 31))):
        day, got = quarter_day(qe)
        qs[q] = (day, got)
        print("%s 거래일 %s | 종목 %d" % (q, day, len(got)), flush=True)

    listed = {}  # 종목코드 -> 상장일 (KRX에 없는 칸의 부재 근거)
    rows, base_url = api("sto/stk_isu_base_info", basDd="20260918")
    for x in rows:
        listed[x["ISU_SRT_CD"]] = x.get("LIST_DD", "")

    filled = relabel = unver = 0
    for f in sorted(glob.glob("kr/data/*-dataset.csv")):
        rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
        head = list(rows[0].keys())
        for r in rows:
            if r["기간"] not in qs or r["항목"] not in ITEM or r["값(원)"].isdigit():
                continue
            day, got = qs[r["기간"]]
            hit = got.get(r["종목코드"])
            if not hit:
                ld = listed.get(r["종목코드"], "")
                r["값(원)"] = "데이터 없음(최초 거래일 %s 이전)" % (
                    "%s-%s-%s" % (ld[:4], ld[4:6], ld[6:]) if len(ld) == 8 else "미확인")
                r["값구분"] = "데이터 없음(상장 전)"
                r["출처"] = "%s (%s 코스피·코스닥 일별매매정보에 없음 ; 상장일 %s)" % (base_url, day, ld or "미확인")
                relabel += 1
                continue
            x, mkt, url = hit
            close, shrs, cap = int(x["TDD_CLSPRC"]), int(x["LIST_SHRS"]), int(x["MKTCAP"])
            if close * shrs != cap:  # 자체 검증 실패 칸은 값을 넣지 않는다
                r["값(원)"], r["값구분"] = "미확인", "미확인"
                r["출처"] = "%s (%s, %s ; 종가×주식수 %d ≠ 시가총액 %d)" % (url, day, mkt, close * shrs, cap)
                unver += 1
                continue
            r["값(원)"] = str({"분기말 종가": close, "분기말 상장주식수": shrs, "분기말 시가총액": cap}[r["항목"]])
            r["값구분"] = "API"
            r["기준일"] = day
            r["출처"] = "%s (%s, %s ; 종가 %d × 상장주식수 %d = 시가총액 %d)" % (url, mkt, x["ISU_NM"], close, shrs, cap)
            filled += 1
        out = os.path.join(OUTDIR, os.path.basename(f))
        with open(out, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, head)
            w.writeheader()
            w.writerows(rows)
        print("  %s -> %s" % (os.path.basename(f), out), flush=True)
    print("\n채움 %d칸 | 상장 전 라벨 정정 %d칸 | 검증실패(미확인) %d칸" % (filled, relabel, unver))


if __name__ == "__main__":
    main()
