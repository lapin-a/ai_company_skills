"""라운드 4 시장조사팀: 후보 발굴·검증 도구."""

import csv
import json
import re
import time
import urllib.parse
import urllib.request

FILES = ("kr/data/round1-dataset.csv", "kr/data/round2-dataset.csv", "kr/data/round3-dataset.csv")
WINDOW = ["%d.%02d" % (y, m) for y in range(2019, 2027) for m in (3, 6, 9, 12) if (y, m) <= (2026, 6)]
SETTINGS = ".claude/settings.local.json"
DART_KEY = json.load(open(SETTINGS, encoding="utf-8"))["env"]["DART_API_KEY"]
PUBLIC_KEY = urllib.parse.unquote(json.load(open(SETTINGS, encoding="utf-8"))["env"]["PUBLIC_DATA_SERVICE_KEY"])


def collected_codes():
    out = set()
    for f in FILES:
        with open(f, encoding="utf-8-sig") as fh:
            out |= {r["종목코드"] for r in csv.DictReader(fh)}
    return out


def candidates(n=10):
    """largecap100.csv에서 비금융·미수집 상위 n개."""
    done = collected_codes()
    with open("kr/largecap100.csv", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    pool = [r for r in rows if r["금융여부"] == "N" and r["종목코드"] not in done]
    return pool[:n], len(pool)


def reports(corp_code):
    """OpenDART 정기공시 목록 (2019-01-01 이후, 전체 페이지)."""
    got, page = [], 1
    while True:
        params = {
            "crtfc_key": DART_KEY,
            "corp_code": corp_code,
            "bgn_de": "20190101",
            "end_de": "20260918",
            "pblntf_ty": "A",
            "page_no": page,
            "page_count": 100,
        }
        url = "https://opendart.fss.or.kr/api/list.json?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=60) as resp:
            d = json.loads(resp.read())
        time.sleep(0.25)
        got += d.get("list", [])
        if d.get("status") != "000" or page >= int(d.get("total_page", 1)):
            return got
        page += 1


def report_summary(corp_code):
    """정기공시 목록 → 창 내 분기 수·최초 분기·연속 최신 분기·최신 사업보고서."""
    reps = reports(corp_code)
    periods = set()
    for x in reps:
        m = re.search(r"\((\d{4}\.\d{2})\)", x["report_nm"])
        if m:  # [첨부정정]·[첨부추가]도 그 분기 보고서로 센다 (유일한 판본일 수 있다)
            periods.add(m.group(1))
    in_window = sorted(p for p in periods if p in WINDOW)
    run = 0
    for p in reversed(WINDOW):
        if p not in periods:
            break
        run += 1
    annual = [x for x in reps if "사업보고서" in x["report_nm"] and "첨부" not in x["report_nm"]]
    annual.sort(key=lambda x: x["rcept_no"], reverse=True)
    return {
        "보고서수": len(reps),
        "창내분기": len(in_window),
        "최초": in_window[0] if in_window else None,
        "연속최신": run,
        "최신사업보고서": annual[0]["rcept_no"] if annual else None,
    }


def first_trade(code):
    """주식시세 V2에서 그 종목의 가장 이른 거래일과 총 거래일 수."""
    base = "https://apis.data.go.kr/1160100/GetStockSecuritiesInfoService_V2/getStockPriceInfo_V2?"

    def body(**extra):
        params = dict(extra, serviceKey=PUBLIC_KEY, resultType="json", likeSrtnCd=code)
        with urllib.request.urlopen(base + urllib.parse.urlencode(params), timeout=60) as resp:
            return json.loads(resp.read())["response"]["body"]

    total = int(body(numOfRows="1")["totalCount"])
    time.sleep(0.25)
    last_page = (total + 49) // 50
    items = body(numOfRows="50", pageNo=str(last_page))["items"]["item"]
    time.sleep(0.25)
    days = [i["basDt"] for i in items if i["srtnCd"] == code]
    return (min(days) if days else None), total


def gaps(corp_code):
    """창 안에서 최초 분기 이후 빠진 분기 목록."""
    reps = reports(corp_code)
    have = set()
    for x in reps:
        m = re.search(r"\((\d{4}\.\d{2})\)", x["report_nm"])
        if m:
            have.add(m.group(1))
    win = [p for p in WINDOW if p in have]
    if not win:
        return WINDOW
    return [p for p in WINDOW[WINDOW.index(win[0]):] if p not in have]


if __name__ == "__main__":
    cand, pool = candidates()
    print("비금융 미수집 %d개 | 이번 후보 %d개\n" % (pool, len(cand)))
    print("순위 | 기업 | 종목코드 | 시총(조) | 창내분기 | 최초 | 연속최신 | 12분기 | 최초거래일 | 누락분기")
    for r in cand:
        s = report_summary(r["DART corp_code"])
        day, _ = first_trade(r["종목코드"])
        miss = gaps(r["DART corp_code"]) if s["연속최신"] < 12 else []
        print("%3s | %-12s %s | %5.1f | %2d | %s | %2d | %s | %s | %s" % (
            r["순위"], r["기업"], r["종목코드"], int(r["시가총액(원)"]) / 1e12,
            s["창내분기"], s["최초"], s["연속최신"],
            "충족" if s["연속최신"] >= 12 else "미달", day, ",".join(miss) or "-"))
