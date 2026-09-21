"""미국 대형주(S&P500) 후보 발굴·검증 도구 (시장조사팀).

- 구성종목: SPY 일별 보유종목 xlsx (State Street). S&P 공식 목록은 유료라 ETF 보유종목으로 대신한다.
- 재무 이력: SEC EDGAR data.sec.gov submissions (10-Q/10-K, reportDate 기준 연속 분기).
- 시가총액: Yahoo chart 종가 × SEC dei:EntityCommonStockSharesOutstanding (전 클래스 합).
"""

import csv
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date, timedelta

EPOCH = date(1970, 1, 1)  # Windows의 date.fromtimestamp는 1970 이전(음수)에서 OSError
# SEC 공정접근 정책: 이름 + 연락처 (사용자 지정 2026-09-19). 연락처는 저장소에 두지 않고
# .claude/settings.local.json의 env.SEC_USER_AGENT에서 읽는다 (DART·공공데이터 키와 같은 곳).
SEC_UA = {"User-Agent": json.load(open(".claude/settings.local.json", encoding="utf-8"))["env"]["SEC_USER_AGENT"]}
WEB_UA = {"User-Agent": "Mozilla/5.0"}
SPY = "https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx"


def get(url, headers, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
        return r.read()


def spy_holdings():
    """SPY xlsx → [(name, ticker, weight)] 및 기준일. openpyxl 없이 zip+xml로 읽는다."""
    z = zipfile.ZipFile(io.BytesIO(get(SPY, WEB_UA)))
    strs = [re.sub("<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode(), re.S)]
    rows = []
    for r in re.findall(r"<row[^>]*>(.*?)</row>", z.read("xl/worksheets/sheet1.xml").decode(), re.S):
        rows.append([strs[int(v)] if 't="s"' in a and v else v
                     for a, v in re.findall(r"<c ([^>]*?)(?:/>|>(?:<v>(.*?)</v>)?</c>)", r)])
    asof = rows[2][1].replace("As of ", "")
    out = [(r[0], r[1], float(r[4])) for r in rows[4:] if len(r) > 4 and r[1] and r[4] and r[1] != "-"]
    return asof, out


def cik_for(ticker):
    t = ticker.replace(".", "-")
    d = json.loads(get("https://efts.sec.gov/LATEST/search-index?keysTyped=" + urllib.parse.quote(t), SEC_UA))
    for h in d["hits"]["hits"]:
        if t in h["_source"].get("tickers", "").split(", "):
            return h["_id"]
    return None


def filing_run(sub):
    """10-Q/10-K 원본의 reportDate를 최신부터 거슬러 끊김 없는 분기 수. 간격 > 130일이면 끊김(16주 분기 COST 등 ~112일 허용, 한 분기 누락은 ~180일)."""
    pages = [sub["filings"]["recent"]]
    # recent는 최근 1,000건뿐: 424B2 많은 은행은 과거 페이지 필요. 12분기 판정엔 2022년 이후면 충분.
    for f in [f for f in sub["filings"].get("files", []) if f["filingTo"] >= "2022-01-01"]:
        pages.append(json.loads(get("https://data.sec.gov/submissions/" + f["name"], SEC_UA)))
        time.sleep(0.15)
    ends = sorted({rd for p in pages for f, rd in zip(p["form"], p["reportDate"]) if f in ("10-Q", "10-K") and rd}, reverse=True)
    run = 1 if ends else 0
    for a, b in zip(ends, ends[1:]):
        if (date.fromisoformat(a) - date.fromisoformat(b)).days > 130:
            break
        run += 1
    return run, ends[0] if ends else None, ends[run - 1] if ends else None


def shares_outstanding(facts):
    """최신 dei:EntityCommonStockSharesOutstanding(같은 날짜 여러 클래스면 합산).
    클래스별 차원으로만 공시한 회사(GOOGL·META 등)는 companyfacts에 없거나 오래된 값만 남으므로,
    1년 넘게 묵었으면 최근 분기 가중평균 기본주식수로 대신한다(근사)."""
    def latest(tax, tag):
        units = facts["facts"].get(tax, {}).get(tag, {}).get("units", {}).get("shares", [])
        if not units:
            return None, None
        last = max(u["end"] for u in units)
        accn = max((u["filed"], u["accn"]) for u in units if u["end"] == last)[1]
        hit = [u for u in units if u["end"] == last and u["accn"] == accn]
        if "start" in hit[0]:  # 기간 값(가중평균)은 3개월·누적이 같은 end로 겹치므로 가장 짧은 기간 하나만
            return max(hit, key=lambda u: u["start"])["val"], last
        return sum(u["val"] for u in hit), last  # 시점 값(dei)은 클래스별 합산

    sh, d = latest("dei", "EntityCommonStockSharesOutstanding")
    if d and d >= "2025-06-30":
        return sh, d, "dei"
    sh, d = latest("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic")
    return sh, d, "가중평균(근사)"


def yahoo(ticker):
    """Yahoo chart 3년+ 분기말 종가 확인: (최근 종가, 최초 거래일, 최근 13개 분기말 중 종가 있는 수)."""
    t = ticker.replace(".", "-")
    d = json.loads(get("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=5y&interval=1d" % t, WEB_UA))["chart"]["result"][0]
    days = [EPOCH + timedelta(seconds=x) for x in d["timestamp"]]
    closes = d["indicators"]["quote"][0]["close"]
    qends = [date(y, m, dd) for y in range(2023, 2027) for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31)) if date(y, m, dd) <= date(2026, 6, 30)][-13:]
    have = sum(any(q.toordinal() - 7 < x.toordinal() <= q.toordinal() and c for x, c in zip(days, closes)) for q in qends)
    return d["meta"]["regularMarketPrice"], (EPOCH + timedelta(seconds=d["meta"]["firstTradeDate"])).isoformat(), have, len(qends)


def probe(ticker):
    cik = cik_for(ticker)
    if not cik:
        return {"ticker": ticker, "error": "CIK 미확인"}
    c10 = cik.zfill(10)
    sub = json.loads(get("https://data.sec.gov/submissions/CIK%s.json" % c10, SEC_UA))
    time.sleep(0.15)
    facts = json.loads(get("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % c10, SEC_UA))
    time.sleep(0.15)
    run, latest, oldest = filing_run(sub)
    sh, sh_date, sh_src = shares_outstanding(facts)
    price, first, qhave, qn = yahoo(ticker)
    return {
        "ticker": ticker, "cik": c10, "name": sub["name"], "sic": sub.get("sic"), "sicDesc": sub.get("sicDescription"),
        "run": run, "latest": latest, "oldest": oldest, "shares": sh, "sharesDate": sh_date, "sharesSrc": sh_src,
        "price": price, "mcap": price * sh if sh else None, "firstTrade": first, "qCloses": "%d/%d" % (qhave, qn),
    }


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    asof, hold = spy_holdings()
    seen, res = set(), []
    for name, tk, w in sorted(hold, key=lambda x: -x[2]):
        if len(res) >= n:
            break
        try:
            r = probe(tk)
        except Exception as e:
            r = {"ticker": tk, "error": repr(e)[:80]}
        if r.get("cik") in seen:  # 같은 회사의 다른 클래스(GOOG/GOOGL 등)
            continue
        seen.add(r.get("cik"))
        r["spyWeight"] = w
        res.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
    json.dump({"asof": asof, "rows": res}, open("us/us-candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
