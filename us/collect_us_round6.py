"""미국 라운드 6 기획 2팀: TOP 20 수집 -> us-round6-dataset.csv

라운드 4·5와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round6-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round6-dataset.csv"
c.TOP10 = [
    ("Valero Energy", "VLO", "0001035002"), ("Parker-Hannifin", "PH", "0000076334"),
    ("Medtronic", "MDT", "0001613103"), ("Altria", "MO", "0000764180"), ("CVS Health", "CVS", "0000064803"),
    ("Starbucks", "SBUX", "0000829224"), ("Phillips 66", "PSX", "0001534701"),
    ("Lowe's", "LOW", "0000060667"), ("Automatic Data Processing", "ADP", "0000008670"),
    ("Stryker", "SYK", "0000310764"), ("AppLovin", "APP", "0001751008"),
    ("Freeport-McMoRan", "FCX", "0000831259"), ("McKesson", "MCK", "0000927653"),
    ("Airbnb", "ABNB", "0001559720"), ("Adobe", "ADBE", "0000796343"), ("Southern Company", "SO", "0000092122"),
    ("Vertiv Holdings", "VRT", "0001674101"), ("Quanta Services", "PWR", "0001050915"),
    ("Amphenol", "APH", "0000820313"), ("General Dynamics", "GD", "0000040533"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0001534701", "0000008670"}  # PSX·ADP: OperatingIncomeLoss 태그 없음

# VRT는 2020-02 SPAC 합병으로 상장했다. 그 전 보고서는 합병 전 SPAC(GS Acquisition Holdings)의 것이라
# 지금 사업과 다른 실체다 → 대표 결정 (가), 2026-09-20: 합병 전 분기는 "데이터 없음"으로 둔다.
VRT_PRE = "2019Q4"  # 이 분기까지가 합병 전


ABNB = "0001559720"
# ABNB FY2020 10-K에는 XBRL이 아예 없다(추출 XML도, 본문 인라인 태그도 없다).
# 대표 결정 (나), 2026-09-20: 더 파고들어 채운다 — 같은 기간 수치가 "나중 보고서의 비교기간"에 있다.
# 값구분에 `공시(후속 보고서 비교기간)`을 붙여 원보고서 공시값과 구분한다.
ABNB_FLOW = {"분기별 매출액": "RevenueFromContractWithCustomerExcludingAssessedTax",
             "분기별 영업이익": "OperatingIncomeLoss", "분기별 당기순이익(지배)": "NetIncomeLoss",
             "분기별 영업활동현금흐름": "NetCashProvidedByUsedInOperatingActivities"}
ABNB_STOCK = {"분기말 자산총계": "Assets", "분기말 부채총계": "Liabilities",
              "분기말 총자본(자기자본)": "StockholdersEquity", "분기말 지배지분 자본": "StockholdersEquity"}


def abnb_2020q4():
    """2020Q4 = FY2020 연간 − 9개월 누적. 둘 다 나중 보고서의 비교기간에서 읽는다. {항목: (값, 출처, 검산)}."""
    fx = c.Facts(ABNB)

    def pick(tag, end, start=None):
        hits = [(e.get("filed", ""), e["accn"], e["val"]) for k, es in fx.idx.items() if k[0] == tag
                for e in es if e["end"] == end and e.get("start") == start]
        return min(hits)[1:] if hits else None  # 가장 먼저 낸 보고서

    out = {}
    for item, tag in ABNB_FLOW.items():
        y = pick(tag, "2020-12-31", "2020-01-01")
        n9 = pick(tag, "2020-09-30", "2020-01-01")
        if y and n9:
            out[item] = (y[1] - n9[1], "%s ; %s" % (c.link(ABNB, y[0]), c.link(ABNB, n9[0])),
                         "연간 %d − 9개월누적 %d (%s, 후속 보고서 비교기간)" % (y[1], n9[1], tag))
    for item, tag in ABNB_STOCK.items():
        v = pick(tag, "2020-12-31")
        if v:
            out[item] = (v[1], c.link(ABNB, v[0]), "%s (후속 보고서 비교기간)" % tag)
    return out


def fix_rows(rows):
    r2.fix_rows(rows)
    fill = abnb_2020q4()
    for r in rows:
        if r[1] == "ABNB" and r[2] == "2020Q4" and r[5] == "미확인" and r[4] in fill:
            v, src, chk = fill[r[4]]
            kind = "계산(연간-3분기누적, 후속 보고서 비교기간)" if r[4] in ABNB_FLOW else "공시(후속 보고서 비교기간)"
            r[5:10] = [v, "USD", kind, src, chk]
    for r in rows:
        if r[1] == "VRT" and r[2] <= VRT_PRE:
            r[5:10] = ["데이터 없음(최초 보고기간 이전)", "USD" if r[4] not in ("분기말 상장주식수",) else "",
                       "데이터 없음(최초 보고기간 전)",
                       "https://data.sec.gov/submissions/CIK0001674101.json (2020-02 SPAC 합병 전 보고 실체가 다름)",
                       "합병 전 보고서는 GS Acquisition Holdings(SPAC)의 것이다"]


c.ROW_FIX = fix_rows

if __name__ == "__main__":
    c.main()
