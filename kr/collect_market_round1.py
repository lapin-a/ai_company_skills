"""라운드 1 기획 2팀: 공공데이터포털 주식시세 V2로 round1-dataset.csv의 시장데이터 3항목을 채운다.

collect_round1.py(DART 재무) 실행 후에 실행한다. 시장데이터 행만 덮어쓴다.
"""

import csv
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

CSV_PATH = "kr/data/round1-dataset.csv"
CODE = "005930"
URL = "https://apis.data.go.kr/1160100/GetStockSecuritiesInfoService_V2/getStockPriceInfo_V2"
SERVICE_START = dt.date(2020, 1, 2)  # 삼성전자 기준 API 최초 데이터일 (2026-09-18 확인)
NO_DATA = "데이터 없음(소스 서비스 시작일 2020-01-02 이전)"
RATE_LIMIT = "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR"
FIELDS = {"분기말 종가": "clpr", "분기말 상장주식수": "lstgStCnt", "분기말 시가총액": "mrktTotAmt"}
QEND = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def service_key():
    key = os.environ.get("PUBLIC_DATA_SERVICE_KEY", "")
    if not key:
        with open(".claude/settings.local.json", encoding="utf-8") as f:
            key = json.load(f)["env"].get("PUBLIC_DATA_SERVICE_KEY", "")
    return urllib.parse.unquote(key)  # Encoding/Decoding 키 모두 한 번만 인코딩되게


def last_trading_day(key, qend, code=CODE):
    """분기말 이전 14일 구간에서 마지막 거래일 행. endBasDt는 해당일 미포함(2026-09-18 확인)이라 +1일."""
    params = {
        "serviceKey": key, "resultType": "json", "likeSrtnCd": code, "numOfRows": "30",
        "beginBasDt": (qend - dt.timedelta(days=14)).strftime("%Y%m%d"),
        "endBasDt": (qend + dt.timedelta(days=1)).strftime("%Y%m%d"),
    }
    for attempt in range(3):
        try:
            with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode(params), timeout=30) as r:
                body = r.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            raise SystemExit("HTTP %s — 중단 (사람 확인 필요)" % e.code)
        except Exception:
            if attempt == 2:
                raise SystemExit("3회 재시도 실패 — 중단 (사람 확인 필요)")
            time.sleep(2)
    if RATE_LIMIT in body:
        raise SystemExit("요청 한도 초과 — 연동 대기, 중단")
    b = json.loads(body)["response"]["body"]
    items = b["items"]["item"] if isinstance(b["items"], dict) else []
    # likeSrtnCd는 부분 일치라 정확히 한 번 더 거른다
    items = [i for i in items if i["srtnCd"] == code and i["basDt"] <= qend.strftime("%Y%m%d")]
    return max(items, key=lambda i: i["basDt"]) if items else None


def main():
    key = service_key()
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head, body = rows[0], rows[1:]
    ci = {name: head.index(name) for name in ("기간", "기준일", "항목", "값(원)", "값구분", "출처")}

    cache, ok, nodata, missing, mismatch = {}, 0, 0, 0, []
    for r in body:
        item = r[ci["항목"]]
        if item not in FIELDS:
            continue
        period = r[ci["기간"]]
        y, q = int(period[:4]), int(period[-1])
        qend = dt.date(y, *QEND[q])
        if qend < SERVICE_START:
            r[ci["값(원)"]], r[ci["값구분"]] = NO_DATA, "데이터 없음(소스 시작일)"
            r[ci["출처"]] = "공공데이터포털 주식시세 V2 (서비스 시작일 이전)"
            nodata += 1
            continue
        if period not in cache:
            cache[period] = last_trading_day(key, qend)
            time.sleep(0.5)
        it = cache[period]
        if it is None:
            r[ci["값(원)"]], r[ci["값구분"]] = "미확인", "미확인"
            missing += 1
            continue
        r[ci["기준일"]] = "%s-%s-%s" % (it["basDt"][:4], it["basDt"][4:6], it["basDt"][6:])
        r[ci["값(원)"]] = it[FIELDS[item]]
        r[ci["값구분"]] = "API"
        r[ci["출처"]] = "%s?basDt=%s&likeSrtnCd=%s (serviceKey 제외)" % (URL, it["basDt"], CODE)
        ok += 1

    # 자체 검증: 종가 × 상장주식수 = 시가총액
    for period, it in cache.items():
        if it and int(it["clpr"]) * int(it["lstgStCnt"]) != int(it["mrktTotAmt"]):
            mismatch.append(period)

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows([head] + body)
    print("API 값 %d칸 | 데이터 없음 %d칸 | 미확인 %d칸 | 분기 조회 %d건" % (ok, nodata, missing, len(cache)))
    print("종가×상장주식수≠시가총액 분기:", mismatch or "없음")


if __name__ == "__main__":
    main()
