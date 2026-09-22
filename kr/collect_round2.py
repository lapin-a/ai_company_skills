"""라운드 2 기획 2팀: TOP 10 기업 재무 8항목(DART) + 시장 3항목(주식시세 V2) -> round2-dataset.csv

재무 파서·행 생성은 collect_round1.py, 분기말 거래일 조회는 collect_market_round1.py를 재사용한다.
보고서 선택: 기간별 최신 접수본([기재정정] 포함), [첨부정정]·[첨부추가]는 연결재무제표 섹션이 없어 제외.
"""

import csv
import datetime as dt
import json
import re
import time
import urllib.parse
import urllib.request

import backfill_2019_krx as krx
import collect_market_round1 as cm
import collect_round1 as cr
import restate

OUT = "round2-dataset.csv"
OUTDIR = "kr/data/"  # 회귀 검사는 이 값만 바꿔 다른 폴더에 쓴다
TOP10 = [  # (기업, 종목코드, DART corp_code) — coverage-log.md 라운드 2 기획 1팀 선정
    ("SK하이닉스", "000660", "00164779"), ("SK스퀘어", "402340", "01596425"), ("삼성전기", "009150", "00126371"),
    ("LG에너지솔루션", "373220", "01515323"), ("현대차", "005380", "00164742"), ("삼성바이오로직스", "207940", "00877059"),
    ("삼성물산", "028260", "00149655"), ("한화에어로스페이스", "012450", "00126566"), ("두산에너빌리티", "034020", "00159616"),
    ("기아", "000270", "00106641"),
]
WINDOW = ["%d.%02d" % (y, m) for y in range(2010, 2027) for m in (3, 6, 9, 12) if (y, m) <= (2026, 6)]  # 2010~ (대표 결정 2026-09-22)
HEAD = ["기업", "종목코드", "기간", "기준일", "항목", "값(원)", "값구분", "출처"]


def dart_key():
    with open(".claude/settings.local.json", encoding="utf-8") as f:
        return json.load(f)["env"]["DART_API_KEY"]


def pick_reports(dkey, corp_code):
    """{"YYYY.MM": rcept_no} — 창 안 분기말 보고서만, 기간별 최신 접수본, 첨부정정 제외."""
    got, page = [], 1
    while True:
        q = urllib.parse.urlencode({"crtfc_key": dkey, "corp_code": corp_code, "bgn_de": WINDOW[0][:4] + "0101", "end_de": "20260918",
                                    "pblntf_ty": "A", "page_no": page, "page_count": 100})
        d = json.loads(urllib.request.urlopen("https://opendart.fss.or.kr/api/list.json?" + q, timeout=60).read())
        time.sleep(0.3)
        if d.get("status") != "000":
            raise SystemExit("OpenDART list 실패 %s %s — 중단" % (d.get("status"), d.get("message")))
        got += d["list"]
        if page >= int(d["total_page"]):
            break
        page += 1
    plain, attach = {}, {}
    for x in got:
        m = re.search(r"\((\d{4}\.\d{2})\)", x["report_nm"])
        if not m or m.group(1) not in WINDOW:
            continue
        # [첨부정정]·[첨부추가]는 연결재무제표 섹션이 없을 수 있어 일반 판본을 우선한다.
        # 다만 그 분기의 유일한 판본이면 쓴다 (HD현대일렉트릭 2024.03이 그런 경우).
        box = attach if "첨부" in x["report_nm"] else plain
        if x["rcept_no"] > box.get(m.group(1), ""):
            box[m.group(1)] = x["rcept_no"]
    return {**attach, **plain}  # 같은 분기면 일반 판본이 덮어쓴다


def fetch_parse(rcp, period):
    """공시뷰어 조회는 최대 3회 재시도. (파싱 결과, 비교기간 값). 실패하면 빈 dict (해당 칸 미확인)."""
    for attempt in range(3):
        try:
            doc = cr.fs_section(rcp)
            return (cr.parse(doc), restate.prior(doc, period)) if doc else ({}, {})
        except Exception as e:
            print("    %s 시도 %d 실패: %s %s" % (rcp, attempt + 1, type(e).__name__, getattr(e, "reason", e)))
            time.sleep(3)
    return {}, {}


def first_trade_date(pkey, code):
    base = cm.URL + "?"

    def body(**p):  # 연결 끊김·시간 초과는 3회까지 다시 (cm.last_trading_day와 같은 방식, 2010 창 회귀 라운드 10·11)
        for attempt in range(3):
            try:
                return json.loads(urllib.request.urlopen(base + urllib.parse.urlencode(
                    dict(p, serviceKey=pkey, resultType="json", likeSrtnCd=code)), timeout=60).read())["response"]["body"]
            except urllib.error.HTTPError:
                raise
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(5)
    n = int(body(numOfRows="1")["totalCount"])
    items = body(numOfRows="50", pageNo=str((n + 49) // 50))["items"]["item"]  # 최신순 정렬 → 마지막 페이지가 가장 이른 날
    return dt.datetime.strptime(min(i["basDt"] for i in items if i["srtnCd"] == code), "%Y%m%d").date()


def market_rows(pkey, corp, code, first_trade):
    out, bad = [], []
    for period in WINDOW:
        y, q = int(period[:4]), int(period[5:]) // 3
        qend = dt.date(y, *cm.QEND[q])
        base = [corp, code, "%dQ%d" % (y, q), qend.isoformat()]
        if qend < cm.SERVICE_START:
            # 공공데이터포털은 2020-01-02부터라 그 이전 분기는 KRX 오픈API에서 받는다 (krx-backfill-log.md)
            out += krx.krx_market_rows(corp, code, base[2], qend)
            continue
        if qend < first_trade:
            label = "데이터 없음(API 최초 거래일 %s 이전)" % first_trade.isoformat()
            out += [base + [item, label, "데이터 없음(상장 전)", "공공데이터포털 주식시세 V2"] for item in cm.FIELDS]
            continue
        it = cm.last_trading_day(pkey, qend, code)
        time.sleep(0.3)
        ok = it and int(it["clpr"]) * int(it["lstgStCnt"]) == int(it["mrktTotAmt"])
        if it and not ok:
            bad.append(period)
        for item, field in cm.FIELDS.items():
            if not ok:
                out.append(base + [item, "미확인", "미확인", "공공데이터포털 주식시세 V2"])
            else:
                day = "%s-%s-%s" % (it["basDt"][:4], it["basDt"][4:6], it["basDt"][6:])
                src = "%s?basDt=%s&likeSrtnCd=%s (serviceKey 제외)" % (cm.URL, it["basDt"], code)
                out.append([corp, code, base[2], day, item, it[field], "API", src])
    return out, bad


def main():
    dkey, pkey = dart_key(), cm.service_key()
    all_rows, summary, relog = [], [], []
    for corp, code, cc in TOP10:
        t0 = time.time()
        reports = pick_reports(dkey, cc)
        got = {p: fetch_parse(r, p) for p, r in sorted(reports.items())}
        data = {p: v[0] for p, v in got.items()}
        # 재작성 반영 (대표 결정 2026-09-21): 나중 보고서 비교열 값을 쓰고 원 공시는 relog에 남긴다
        fin, fails, log = restate.rows(corp, code, reports, data, {p: v[1] for p, v in got.items()}, WINDOW)
        relog += log
        first = first_trade_date(pkey, code)
        mkt, mbad = market_rows(pkey, corp, code, first)
        for i, period in enumerate(WINDOW):  # 분기별 재무 8행 + 시장 3행
            all_rows += fin[i * 8:(i + 1) * 8] + mkt[i * 3:(i + 1) * 3]
        kinds = {}
        for r in fin + mkt:
            kinds[r[6]] = kinds.get(r[6], 0) + 1
        ci_only = sorted(p for p, d in data.items() if d.get("is_kind") == "CI")
        summary.append({"기업": corp, "보고서": len(reports), "값구분": kinds, "재무검증실패": fails, "시총검증실패": mbad,
                        "API최초거래일": first.isoformat(), "포괄손익표사용기간수": len(ci_only)})
        print("%s | 보고서 %d | %s | 재무검증실패 %s | 시총검증실패 %s | 포괄손익표 %d기간 | %.0fs" % (
            corp, len(reports), kinds, fails or "없음", mbad or "없음", len(ci_only), time.time() - t0), flush=True)

    with open(OUTDIR + OUT, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([HEAD] + all_rows)
    with open(OUTDIR + OUT.replace("-dataset.csv", "-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)  # 파일명은 OUT 기준
    with open(OUTDIR + OUT.replace("-dataset.csv", "-restated.csv"), "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([restate.LOG_HEAD] + relog)
    print("재작성 기록:", {k: sum(r[5] == k for r in relog) for k in sorted({r[5] for r in relog})})
    print("rows:", len(all_rows), "| 빈칸:", sum(v == "" for r in all_rows for v in map(str, r)))


if __name__ == "__main__":
    main()
