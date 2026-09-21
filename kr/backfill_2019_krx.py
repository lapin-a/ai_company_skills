"""2019년 국내 시장데이터 백필 (KRX 오픈API). 실행: python kr/backfill_2019_krx.py [출력폴더]

공공데이터포털 주식시세 V2는 서비스 시작일이 2020-01-02라 2019년 4개 분기를 못 받았다(612칸).
KRX 오픈API 사용 승인이 확인돼(2026-09-21) 같은 3항목을 KRX에서 받아 채운다.

- 분기말이 휴장일이면 분기말 이하 최신 거래일을 쓰고, 실제 거래일을 기준일 열에 적는다(기존 규칙).
- 코스피·코스닥을 모두 조회한다. 2019년에 시장이 달랐던 기업이 있다(포스코퓨처엠=포스코케미칼, 당시 코스닥).
- 자체 검증: 종가 × 상장주식수 = 시가총액. 어긋나면 값을 넣지 않고 미확인으로 둔다.
- KRX에도 없으면 상장 전이다. 종목 기본정보의 상장일로 확인해 `데이터 없음(상장 전)`으로 바로잡는다.
"""
import csv, glob, json, os, sys, urllib.error, urllib.parse, urllib.request
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


_QCACHE = {}
_LISTED = {}


def listing_date(code):
    """종목 상장일 YYYY-MM-DD (코스피·코스닥 종목 기본정보). 모르면 None."""
    if not _LISTED:
        # ponytail: 기준일 고정 — 이 날 이후 상장 종목은 없지만 수집 창(2019~) 밖이라 무관
        for path in ("sto/stk_isu_base_info", "sto/ksq_isu_base_info"):
            try:
                rows, _ = api(path, basDd="20260918")
            except urllib.error.HTTPError as e:
                # 코스닥 종목 기본정보는 사용 승인 전이다(2026-09-21 401). 상장일을 모르면 미확인으로 둔다
                print("  %s HTTP %s — 건너뜀" % (path, e.code), flush=True)
                continue
            for x in rows:
                ld = x.get("LIST_DD", "")
                if len(ld) == 8:
                    _LISTED[x["ISU_SRT_CD"]] = "%s-%s-%s" % (ld[:4], ld[4:6], ld[6:])
    return _LISTED.get(code)


def absent_label(code, day):
    """KRX 일별매매정보에 없는 칸 → (값, 값구분, 출처). 상장일이 그날 뒤면 상장 전, 아니면 미확인."""
    ld = listing_date(code)
    if ld and ld > day:
        return ("데이터 없음(API 최초 거래일 %s 이전)" % ld, "데이터 없음(상장 전)",
                "KRX 오픈API 종목 기본정보 (상장일 %s ; %s 코스피·코스닥 일별매매정보에 없음)" % (ld, day))
    return ("미확인", "미확인", "KRX 오픈API (%s 코스피·코스닥 일별매매정보에 없음 ; 상장일 %s)" % (day, ld or "미확인"))


def krx_market_rows(corp, code, period, qend):
    """수집기용: 한 기업·한 분기의 시장 3항목 행 (국내 데이터셋 8열 형식).

    `collect_round2.market_rows`가 공공데이터포털 시작일(2020-01-02) 이전 분기에 쓴다.
    분기별 조회 결과는 모든 종목을 담으므로 한 번만 받아 둔다.
    """
    if qend not in _QCACHE:
        _QCACHE[qend] = quarter_day(qend)
    day, got = _QCACHE[qend]
    q = qend.isoformat()  # 값 없는 칸의 기준일은 달력 분기말 (기존 수집기와 같다). 거래일은 값 있는 칸만
    hit = got.get(code)
    if not hit:
        return [[corp, code, period, q, item, *absent_label(code, day)] for item in ITEM]
    x, mkt, url = hit
    close, shrs, cap = int(x["TDD_CLSPRC"]), int(x["LIST_SHRS"]), int(x["MKTCAP"])
    if close * shrs != cap:  # 자체 검증 실패 칸은 값을 넣지 않는다
        return [[corp, code, period, q, item, "미확인", "미확인",
                 "%s (%s ; 종가×주식수 %d ≠ 시가총액 %d)" % (url, mkt, close * shrs, cap)] for item in ITEM]
    val = {"분기말 종가": close, "분기말 상장주식수": shrs, "분기말 시가총액": cap}
    src = "%s (%s, %s ; 종가 %d × 상장주식수 %d = 시가총액 %d)" % (url, mkt, x["ISU_NM"], close, shrs, cap)
    return [[corp, code, period, day, item, str(val[item]), "API", src] for item in ITEM]


def main():
    qs = {}
    for q, qe in (("2019Q1", date(2019, 3, 31)), ("2019Q2", date(2019, 6, 30)),
                  ("2019Q3", date(2019, 9, 30)), ("2019Q4", date(2019, 12, 31))):
        day, got = quarter_day(qe)
        qs[q] = (day, got)
        print("%s 거래일 %s | 종목 %d" % (q, day, len(got)), flush=True)

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
                r["값(원)"], r["값구분"], r["출처"] = absent_label(r["종목코드"], day)
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
