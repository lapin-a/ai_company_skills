"""미국 라운드 1 기획 2팀: TOP 10 재무 8항목(SEC companyfacts) + 시장 3항목(Yahoo chart) -> us-round1-dataset.csv

규칙은 us-round1-log.md 2절(기획 1팀)·3절(QA 보완)을 따른다.
- 분기 라벨: 보고기간 말일에서 가장 가까운 달력 분기말. 실제 보고기간 말일은 기준일 열.
- 보고서: 그 보고기간이 당기인 10-Q/10-K(및 /A) 중 최신 제출본. 그 보고서에 값이 없으면 다음 판본.
  이후 보고서의 비교기간 값(재작성)은 쓰지 않는다.
- Q4(10-K) 손익 = 연간 − 3분기(9개월) 누적, 영업CF Q2~Q4 = 당분기 누적 − 직전 분기 누적.
- 종가는 Yahoo 분할조정 종가를 그 날짜 기준 원래 가격으로 되돌린다(이후 분할 비율 곱).
"""

import csv
import json
import re
import time
from datetime import date, timedelta

import us_probe as u

OUT = "us-round1-dataset.csv"
OUTDIR = "us/data/"  # 회귀 검사는 이 값만 바꿔 다른 폴더에 쓴다
TOP10 = [  # (기업, 티커, CIK) — us-round1-log.md 2절 기획 1팀 선정, 3절 QA 통과
    ("NVIDIA", "NVDA", "0001045810"), ("Apple", "AAPL", "0000320193"), ("Alphabet", "GOOGL", "0001652044"),
    ("Microsoft", "MSFT", "0000789019"), ("Amazon", "AMZN", "0001018724"), ("Broadcom", "AVGO", "0001730168"),
    ("Meta Platforms", "META", "0001326801"), ("Tesla", "TSLA", "0001318605"), ("Micron", "MU", "0000723125"),
    ("Eli Lilly", "LLY", "0000059478"),
]
WINDOW = ["%dQ%d" % (y, q) for y in range(2019, 2027) for q in (1, 2, 3, 4) if (y, q) <= (2026, 2)]
HEAD = ["기업", "종목코드", "기간", "기준일", "항목", "값", "통화", "값구분", "출처", "검산"]
FORMS = ("10-Q", "10-Q/A", "10-K", "10-K/A")
REV = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
       "RevenueFromContractWithCustomerIncludingAssessedTax",  # PLTR 2020 (미국 라운드 2)
       "RegulatedAndUnregulatedOperatingRevenue"]  # 전력·가스 회사 전용 매출 줄 (XEL, 미국 라운드 11)
OCF = ["NetCashProvidedByUsedInOperatingActivities",
       "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]  # 뒤는 INTC 2019 (미국 라운드 2)
NCI_BS = ["MinorityInterest", "NonredeemableNoncontrollingInterest"]  # 뒤는 UBER (미국 라운드 5)
NCI_IS = ["NetIncomeLossAttributableToNoncontrollingInterest"]
NI_COMMON = "NetIncomeLossAvailableToCommonStockholdersBasic"  # TMO 2019~2021 (미국 라운드 3)
EQ_TOTAL = "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
ROW_FIX = None
# 나중 보고서의 재작성 값을 쓴다 (대표 결정 2026-09-21). 원 공시값은 -restated.csv에 남긴다.
# False = 원 공시만, True = 재작성 반영(중단영업 재분류 제외), "all" = 재분류까지(기록 대조용)
RESTATE = True
RESTATED = []   # [행 앞 5열 + 구분, 원 공시값, 원 값구분, 원 출처, 나중 보고서 값, 나중 보고서 출처]


def label(end):
    d = date.fromisoformat(end)
    cands = [date(y, m, dd) for y in (d.year - 1, d.year, d.year + 1) for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31))]
    q = min(cands, key=lambda c: abs((c - d).days))
    return "%dQ%d" % (q.year, (q.month - 1) // 3 + 1)


def days(e):
    return (date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])).days if "start" in e else 0


def link(cik, accn):
    return "https://www.sec.gov/Archives/edgar/data/%d/%s/" % (int(cik), accn.replace("-", ""))


def fix_report_dates(cik, out):
    """SEC 제출 메타 reportDate 오기를 원문 표지로 교정한다(out을 제자리에서 고친다).

    ZTS 0001555280-19-000221은 2019 Q2 10-Q인데 reportDate가 2019-08-06으로 실려 있다.
    그대로 두면 2019-06-30(표지만 있는 10-Q/A)과 별개 분기가 되어 라벨이 밀리고 16칸이 빈다.
    정상 분기 말일은 80일 이상 떨어지므로, 45일 이내로 붙은 말일에 걸린 제출만
    원문 dei:DocumentPeriodEndDate로 확인해 옮긴다(회사당 몇 건뿐이라 비용은 작다).
    """
    rds = sorted(out)
    susp = set()
    for i in range(len(rds) - 1):
        if (date.fromisoformat(rds[i + 1]) - date.fromisoformat(rds[i])).days <= 45:
            susp.update(rds[i:i + 2])
    for rd in sorted(susp):
        for rec in list(out.get(rd, [])):
            m = re.search(r"<(?:\w+:)?DocumentPeriodEndDate[^>]*>\s*([0-9-]{10})\s*<", instance(cik, rec[1]) or "")
            if not m or m.group(1) == rd:
                continue
            out[rd].remove(rec)
            out.setdefault(m.group(1), []).append(rec)
            print("보고기간 교정: CIK %s %s  %s -> %s (원문 DocumentPeriodEndDate)" % (cik, rec[1], rd, m.group(1)))
            if not out[rd]:
                del out[rd]


def reports(cik):
    """{보고기간 말일: [accn, ...] 최신 제출 먼저} — 10-Q/10-K(/A), 2018년 이후."""
    sub = json.loads(u.get("https://data.sec.gov/submissions/CIK%s.json" % cik, u.SEC_UA))
    pages = [sub["filings"]["recent"]]
    for f in sub["filings"].get("files", []):
        if f["filingTo"] >= "2018-01-01":
            pages.append(json.loads(u.get("https://data.sec.gov/submissions/" + f["name"], u.SEC_UA)))
            time.sleep(0.15)
    out = {}
    for p in pages:
        for acc, form, rd, fd in zip(p["accessionNumber"], p["form"], p["reportDate"], p["filingDate"]):
            if form in FORMS and rd >= "2018-01-01":
                out.setdefault(rd, []).append((fd, acc, form))
    fix_report_dates(cik, out)
    return {rd: [a for _, a, _ in sorted(v, reverse=True)] for rd, v in out.items()}, \
           {a: f for v in out.values() for _, a, f in v}


class Facts:
    def __init__(self, cik):
        f = json.loads(u.get("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik, u.SEC_UA))
        self.idx = {}
        for tax in ("us-gaap", "dei"):
            for tag, v in f["facts"].get(tax, {}).items():
                for unit, es in v["units"].items():
                    for e in es:
                        self.idx.setdefault((tag, e["accn"]), []).append(e)

    def find(self, tag, accns, end, kind, start=None):
        """(entry, accn): kind I=시점, Q=3개월, Y=연간, C=최장 누적(1년 이하), S=start 일치."""
        for a in accns:
            es = [e for e in self.idx.get((tag, a), []) if e["end"] == end]
            if kind == "I":
                es = [e for e in es if "start" not in e]
            elif kind == "Q":
                # 16주 분기를 쓰는 회사가 있다(KR 1분기 112일). 4개월(120일 이상)은 받지 않는다.
                es = [e for e in es if 70 <= days(e) <= 118]
            elif kind == "Y":
                es = [e for e in es if 340 <= days(e) <= 380]
            elif kind == "9":
                es = [e for e in es if 250 <= days(e) <= 290]
            elif kind == "C":
                es = sorted([e for e in es if 0 < days(e) <= 380], key=days, reverse=True)
            elif kind == "S":
                es = [e for e in es if e.get("start") == start]
            if es:
                return self.restated(tag, es[0], a) if RESTATE else (es[0], a)
        return None, None

    def restated(self, tag, e, a):
        """같은 태그·같은 기간을 비교기간으로 다시 실은 나중 10-Q/10-K 중 가장 늦게 낸 값 (재작성 반영, 2026-09-21).
        단위만 거칠어진 경우(ABNB: 천 달러 → 백만 달러)는 재작성으로 보지 않고 원 공시의 정밀한 값을 둔다."""
        if not hasattr(self, "by_period"):
            self.by_period = {}
            for (tg, _), es in self.idx.items():
                for x in es:
                    if x.get("form") in FORMS and x.get("filed"):
                        self.by_period.setdefault((tg, x.get("start"), x["end"]), []).append(x)
        later = [x for x in self.by_period.get((tag, e.get("start"), e["end"]), [])
                 if x["filed"] > e.get("filed", "9999")]
        if not later:
            return e, a
        if RESTATE != "all" and "start" in e:
            # 중단영업 손익이 있는 제출본의 손익·현금흐름 비교값은 재분류일 수 있다 (반영 안 함, coverage-log 5번)
            if not hasattr(self, "disc"):
                self.disc = {a2 for (tg, a2), es in self.idx.items()
                             if "DiscontinuedOperation" in tg and any(x.get("val") for x in es)}
            later = [x for x in later if x["accn"] not in self.disc]
            if not later:
                return e, a
        x = max(later, key=lambda x: (x["filed"], x["accn"]))
        scale = 10 ** (len(str(abs(x["val"]))) - len(str(abs(x["val"])).rstrip("0"))) if x["val"] else 1
        # 0.1백만 단위 공시는 1단위(10만) 차이도 반올림으로 본다 (EFX 2020Q1·Q3 총자본)
        if x["val"] == e["val"] or (scale >= 1000 and abs(x["val"] - e["val"]) < scale) \
                or (scale == 10 ** 5 and abs(x["val"] - e["val"]) == scale):
            return e, a
        return x, x["accn"]

    def find_later9(self, tag, end):
        """보고서 구분 없이 그 기간 9개월 누적을 실은 10-Q/10-K 중 가장 늦게 낸 것 (비교기간 값)."""
        es = [e for (tg, _), v in self.idx.items() if tg == tag for e in v
              if e["end"] == end and e.get("form") in FORMS and "start" in e and 250 <= days(e) <= 290]
        e = max(es, key=lambda x: (x.get("filed", ""), x["accn"]), default=None)
        return (e, e["accn"]) if e else (None, None)

    def has(self, tags, accns, end):
        return any(self.find(t, accns, end, k)[0] for t in tags for k in ("I", "Q", "Y", "C"))


def fin_rows(corp, tk, cik, reps, forms, fx):
    ends = sorted(reps)
    prev = {e: (ends[i - 1] if i else None) for i, e in enumerate(ends)}
    k_ends = [e for e in ends if forms[reps[e][-1]].startswith("10-K")]
    rows, fails = {}, []  # rows[(label, 항목)] = row
    qtag = {}  # 항목 -> 직전 분기 값에 쓴 태그 (4분기 계산 때 기준이 섞이지 않게)

    def put(lab, end, item, val, kind, src, chk=""):
        rows[(lab, item)] = [corp, tk, lab, end, item, val, "USD", kind, src, chk]

    for end in ends:
        lab = label(end)
        if lab not in WINDOW:
            continue
        accns = reps[end]
        is_k = forms[accns[-1]].startswith("10-K")  # 원본 판본의 양식
        p = prev[end]

        # 손익 3항목
        for item, tags, nci in (("분기별 매출액", REV, None), ("분기별 영업이익", ["OperatingIncomeLoss"], None),
                                ("분기별 당기순이익(지배)", ["NetIncomeLoss", "ProfitLoss", NI_COMMON], NCI_IS)):
            done = False
            for t in tags:
                note = ""
                if t in ("ProfitLoss", NI_COMMON):  # 비지배지분 손익 태그가 없을 때만 지배 몫으로 본다 (QA 보완 1)
                    if fx.has(nci, accns, end):
                        continue
                    note = ", 비지배 없음" if t == "ProfitLoss" else ", 보통주 귀속"
                if not is_k:
                    e, a = fx.find(t, accns, end, "Q")
                    if e:
                        put(lab, end, item, e["val"], "공시" + note.replace(", ", "(") + (")" if note else ""), link(cik, a))
                        qtag[item] = t
                        done = True
                        break
                else:
                    y, ya = fx.find(t, accns, end, "Y")
                    if not y:
                        continue
                    if not p:
                        put(lab, end, item, "데이터 없음(3분기 누적 보고서 없음)", "데이터 없음(직전 보고서 없음)", link(cik, ya))
                        done = True
                        break
                    # 매출은 연간과 9개월 누적의 태그가 다를 수 있다 (NVDA: Revenues ↔ RevenueFromContract…)
                    c = ca = t2 = None
                    # 비지배가 없으면 ProfitLoss와 보통주 귀속은 같은 지배 몫이다 (VTRS: 연간 ProfitLoss, 1~3분기 보통주 귀속)
                    alt = [x for x in tags if x != t] if item == "분기별 매출액" else \
                        [x for x in ("ProfitLoss", NI_COMMON) if x != t] if note and not fx.has(nci, reps[p], p) \
                        and not fx.find(NI_COMMON, accns, end, "Y")[0] else []
                    for t2 in [t] + alt:
                        c, ca = fx.find(t2, reps[p], p, "9")
                        if c:
                            break
                    if not c and item == "분기별 영업이익":
                        # 직전 10-Q에 9개월 누적이 없으면 나중 보고서 비교기간에서 읽는다 (SNA 2024Q4)
                        c, ca = fx.find_later9(t, p)
                    if c and qtag.get(item) and qtag[item] != t:
                        # 1~3분기와 다른 태그로 4분기를 계산하면 기준이 섞인다. 두 태그의 9개월 누적이
                        # 같을 때만 쓴다 (NVDA는 같고, UNP는 Revenues 16,071 ≠ 계약매출 14,947).
                        q9, _ = fx.find(qtag[item], reps[p], p, "9")
                        if q9 and q9["val"] != c["val"]:
                            put(lab, end, item, "미확인", "미확인", link(cik, ya),
                                "연간 태그(%s)가 1~3분기 태그(%s)와 다르고 9개월 누적도 다르다 (%d vs %d)" % (
                                    t, qtag[item], c["val"], q9["val"]))
                            done = True
                            break
                    if c:
                        tagnote = t if t2 == t else "%s / 9개월 %s" % (t, t2)
                        put(lab, end, item, y["val"] - c["val"], "계산(연간-3분기누적%s)" % note,
                            link(cik, ya) + " ; " + link(cik, ca), "연간 %d − 9개월누적 %d (%s)" % (y["val"], c["val"], tagnote))
                        done = True
                        break
            if not done and nci and not is_k:
                # 분기 지배 순이익 태그 없이 연결(ProfitLoss)·비지배만 있는 10-Q (MA, 미국 라운드 2)
                pl, pla = fx.find("ProfitLoss", accns, end, "Q")
                nc, _ = fx.find(nci[0], accns, end, "Q")
                if pl and nc:
                    put(lab, end, item, pl["val"] - nc["val"], "계산(연결-비지배)", link(cik, pla),
                        "3개월 연결 %d − 비지배 %d" % (pl["val"], nc["val"]))
                    done = True
                elif not nc:
                    # 분기 비지배 없이 누적 비지배만 있어 연결=지배 판정이 안 될 때, 보통주 귀속은 정의상 지배 몫이다 (BALL)
                    cm, cma = fx.find(NI_COMMON, accns, end, "Q")
                    if cm:
                        put(lab, end, item, cm["val"], "공시(보통주 귀속)", link(cik, cma), "분기 비지배 태그 없음")
                        done = True
            if not done and nci and is_k and p:
                # 연간 지배 순이익 태그가 없고 연결(ProfitLoss)·비지배만 있는 10-K (AVGO FY2019·FY2020)
                pl, pla = fx.find("ProfitLoss", accns, end, "Y")
                nc, _ = fx.find(nci[0], accns, end, "Y")
                c, ca = fx.find("NetIncomeLoss", reps[p], p, "9")
                c9 = (c["val"], "9개월누적 %d" % c["val"]) if c else None
                if not c:  # 9개월 누적도 지배 태그가 없으면 같은 방식(연결 − 비지배)
                    c, ca = fx.find("ProfitLoss", reps[p], p, "9")
                    cn, _ = fx.find(nci[0], reps[p], p, "9")
                    if c and cn:
                        c9 = (c["val"] - cn["val"], "9개월 연결 %d − 비지배 %d" % (c["val"], cn["val"]))
                    elif c and not fx.has(nci, reps[p], p):  # 그 보고서에 비지배 태그 자체가 없으면 연결 = 지배
                        c9 = (c["val"], "9개월 연결 %d, 비지배 태그 없음" % c["val"])
                if pl and nc and c9:
                    y = pl["val"] - nc["val"]
                    put(lab, end, item, y - c9[0], "계산(연간(연결-비지배)-3분기누적)", link(cik, pla) + " ; " + link(cik, ca),
                        "연간 연결 %d − 비지배 %d − (%s)" % (pl["val"], nc["val"], c9[1]))
                    done = True
            if not done:
                if item == "분기별 영업이익" and not any(k[0] == "OperatingIncomeLoss" for k in fx.idx):
                    # 5종 결측 라벨 밖이라 미확인으로 둔다 (사용자 결정 2026-09-19). 사유는 출처 열에.
                    put(lab, end, item, "미확인", "미확인",
                        "SEC companyfacts CIK%s: OperatingIncomeLoss 태그 없음(영업이익 미공시)" % cik)
                else:
                    put(lab, end, item, "미확인", "미확인", link(cik, accns[0]))

        # 영업활동현금흐름
        # 누적은 회계연도 시작(직전 10-K 말일 다음 날)부터. AMZN처럼 최근 12개월(TTM) 열이 있으면 "최장"은 틀린다.
        fy0 = max((e for e in k_ends if e < end), default=None)
        for t in OCF:
            cum, ca = fx.find(t, accns, end, "S", (date.fromisoformat(fy0) + timedelta(days=1)).isoformat()) if fy0 else (None, None)
            if not cum:
                cum, ca = fx.find(t, accns, end, "C")
            if cum:
                break
        item = "분기별 영업활동현금흐름"
        if not cum:
            put(lab, end, item, "미확인", "미확인", link(cik, accns[0]))
        elif days(cum) <= 118:
            # 16주 1분기(KR 112일)는 누적이 곧 분기값이다. 분기 태그 필터와 같은 상한을 쓴다.
            put(lab, end, item, cum["val"], "공시", link(cik, ca))
        else:
            pc = pa = None
            for t2 in ([t] + [x for x in OCF if x != t]) if p else []:  # 직전 보고서가 다른 태그일 수 있다
                pc, pa = fx.find(t2, reps[p], p, "S", cum["start"])
                if pc:
                    break
            if pc:
                put(lab, end, item, cum["val"] - pc["val"], "계산(누적차감)", link(cik, ca) + " ; " + link(cik, pa),
                    "누적 %d − 직전누적 %d (시작 %s)" % (cum["val"], pc["val"], cum["start"]))
            else:
                put(lab, end, item, "데이터 없음(직전 분기 누적 보고서 없음)", "데이터 없음(직전 보고서 없음)", link(cik, ca))

        # 저량 4항목
        A, aa = fx.find("Assets", accns, end, "I")
        L, la = fx.find("Liabilities", accns, end, "I")
        TE, ta = fx.find(EQ_TOTAL, accns, end, "I")
        PE, pa = fx.find("StockholdersEquity", accns, end, "I")
        NCI = next((e for t in NCI_BS for e in [fx.find(t, accns, end, "I")[0]] if e), None)
        LSE, lsa = fx.find("LiabilitiesAndStockholdersEquity", accns, end, "I")
        te = pe = None
        if TE:
            te = (TE["val"], "공시", link(cik, ta), "")
        elif PE and not NCI:
            te = (PE["val"], "공시(비지배 없음)", link(cik, pa), "StockholdersEquity, MinorityInterest 태그 없음")
        elif PE and NCI:
            te = (PE["val"] + NCI["val"], "계산(지배+비지배)", link(cik, pa), "지배 %d + 비지배 %d" % (PE["val"], NCI["val"]))
        if PE:
            pe = (PE["val"], "공시", link(cik, pa), "")
        elif TE and not NCI:
            pe = (TE["val"], "공시(비지배 없음)", link(cik, ta), "%s, MinorityInterest 태그 없음" % EQ_TOTAL)
        elif TE and NCI:  # 지배 몫 태그 없이 총자본·비지배만 공시 (CAT·PG, 미국 라운드 3)
            pe = (TE["val"] - NCI["val"], "계산(총자본-비지배)", link(cik, ta),
                  "총자본 %d − 비지배 %d" % (TE["val"], NCI["val"]))
        # 메자닌(일시자본): 합계 태그가 있으면 그것만, 없으면 구성 태그 합 (TSLA 이중합산·MU 누락 사례)
        tot, _ = fx.find("TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests", accns, end, "I")
        # 같은 금액을 두 태그로 함께 공시하는 회사가 있다(HLT: …CarryingAmount와 …CommonCarryingAmount 둘 다 21M).
        # 값 기준으로 중복을 없앤 뒤 더한다.
        mezz = tot["val"] if tot else sum({
            e["val"] for tg in ("TemporaryEquityCarryingAmountAttributableToParent",
                                "RedeemableNoncontrollingInterestEquityCarryingAmount",
                                "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
                                "RedeemableNoncontrollingInterestEquityCommonCarryingAmount")  # WBD·HLT (라운드 9)
            for e in [fx.find(tg, accns, end, "I")[0]] if e})
        if not mezz:  # 장부가 태그 없이 공정가치로만 표시 (MA, 미국 라운드 2)
            fv, _ = fx.find("RedeemableNoncontrollingInterestEquityFairValue", accns, end, "I")
            mezz = fv["val"] if fv else 0
        li = None
        if L:
            li = (L["val"], "공시", link(cik, la), "")
        elif LSE and te:  # 부채및자본에는 메자닌도 들어 있다 (WMT·INTC, 미국 라운드 2)
            li = (LSE["val"] - te[0] - mezz, "계산(부채및자본-총자본)", link(cik, lsa),
                  "부채및자본 %d − 총자본 %d" % (LSE["val"], te[0]) + (" − 메자닌 %d" % mezz if mezz else ""))
        # 자체 검증: 자산 = 부채 + 총자본 (+ 메자닌), 총자본 = 지배 + 비지배
        # 공시 단위(백만·천 달러)에서 반올림된 값끼리는 1단위 차이가 날 수 있다 (GE·PG, 미국 라운드 3)
        # 0.1백만 단위 공시도 있다 (BR·ZBH·STE, 미국 라운드 17~30)
        vals = [v for v in (A and A["val"], li and li[0], te and te[0], pe and pe[0]) if v]
        tol = next((u for u in (10 ** 6, 10 ** 5, 10 ** 3) if vals and all(v % u == 0 for v in vals)), 1)
        ok = A and li and te and abs(A["val"] - li[0] - te[0] - mezz) <= tol
        mezz_in_li = False
        if A and li and te and not ok and mezz and abs(A["val"] - li[0] - te[0]) <= tol:
            # 공시 부채총계에 메자닌이 이미 들어 있는 회사 (CVX·GE, 미국 라운드 3)
            ok, mezz_in_li = True, True
        mezz_note = ""
        if A and li and te and pe and not ok and abs(A["val"] - li[0] - pe[0] - mezz) <= tol:
            # 총자본(비지배 포함) 태그 값이 대차와 맞지 않는 회사 (A 2025~2026: 그 태그가 −280M인데 지배지분은 6,136M)
            te = (pe[0], "공시(지배지분 태그)", pe[2],
                  (pe[3] + " ; " if pe[3] else "") + "총자본 태그 값 %d이 대차와 맞지 않아 지배지분 값을 총자본으로 씀" % te[0])
            ok = True
        if A and li and te and not ok:
            # 부채와 자본 사이에 companyfacts로는 못 읽는 줄이 남아 있다. 원문에서 그 줄을 찾는다.
            # (AVGO 우선주 배당 의무, BKNG 전환사채 자본요소, AEP 조건부 상환 성과주식 — 모두 회사 확장 태그)
            gap = A["val"] - li[0] - te[0] - mezz
            pat = r"\w*(?:TemporaryEquity|ConvertibleDebtEquity|Redeemable|Mezzanine)\w*"
            # 같은 금액을 여러 이름으로 적는 회사가 있다(AEP: aep:MezzanineEquity와 aep:TotalMezzanineEquity 둘 다 72.5M)
            cands = {(t, v) for t, v, d, dim in instance_facts(instance(cik, aa), pat)
                     if d == end and not dim and v == gap}
            if cands:  # 금액이 딱 맞는 줄이 있을 때만 인정한다(값은 하나뿐이다)
                t, v = sorted(cands)[0]
                mezz += v
                mezz_note = "원문 %s %d" % (t, v)
                ok = True
            else:
                ext = [(t, v) for t, v, d, dim in instance_facts(instance(cik, aa), r"\w*(?:TemporaryEquity|ConvertibleDebtEquity)\w*")
                       if d == end and not dim and not t.startswith("us-gaap:")]
                if ext and A["val"] == li[0] + te[0] + mezz + sum(v for _, v in ext):
                    mezz += sum(v for _, v in ext)
                    mezz_note = "원문 " + ", ".join("%s %d" % x for x in ext)
                    ok = True
        # 비지배지분 태그가 없으면 총자본 − 지배로 본다 (정의상 같다. SO 2019Q4·DELL 2021Q4)
        nci_val = NCI["val"] if NCI else (te[0] - pe[0] if te and pe else 0)
        ok2 = te and pe and abs(te[0] - pe[0] - nci_val) <= tol
        if not NCI and te and pe and te[0] != pe[0]:  # 추정했다는 사실을 남긴다
            note = "비지배지분 태그 없음: 총자본 − 지배 = %d로 봄" % nci_val
            te = te[:3] + ((te[3] + " ; " if te[3] else "") + note,)
            pe = pe[:3] + ((pe[3] + " ; " if pe[3] else "") + note,)
        if not ok or not ok2:
            fails.append((lab, "자산=부채+자본" if not ok else "총자본=지배+비지배"))
        for item, v, good in (("분기말 자산총계", (A["val"], "공시", link(cik, aa), "") if A else None, ok),
                              ("분기말 부채총계", li, ok), ("분기말 총자본(자기자본)", te, ok and ok2),
                              ("분기말 지배지분 자본", pe, ok2)):
            if v and good:
                chk = v[3]
                if mezz and item == "분기말 부채총계":
                    chk = (chk + " ; " if chk else "") + "메자닌(일시자본) %d %s%s" % (
                        mezz, "부채총계에 포함" if mezz_in_li else "별도",
                        " (" + mezz_note + ")" if mezz_note else "")
                put(lab, end, item, v[0], v[1], v[2], chk)
            else:
                why = ""
                if v and not ok and A and li and te:
                    why = "자체 검증 실패: 자산 %d ≠ 부채 %d + 총자본 %d + 메자닌 %d (차이 %d)" % (
                        A["val"], li[0], te[0], mezz, A["val"] - li[0] - te[0] - mezz)
                elif v and not ok2 and te and pe:
                    why = "자체 검증 실패: 총자본 %d ≠ 지배 %d + 비지배 %d" % (te[0], pe[0], NCI["val"] if NCI else 0)
                elif v:
                    why = "자체 검증 실패: 값을 만들지 못한 항목이 있다(자산·부채·총자본·지배지분 중 일부 태그 없음)"
                put(lab, end, item, "미확인", "미확인", link(cik, accns[0]), why)
    return rows, fails


def yahoo_series(tk):
    t0 = int(time.mktime(date(2018, 12, 1).timetuple()))
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d&events=splits" % (
        tk, t0, int(time.time()))
    d = json.loads(u.get(url, u.WEB_UA))["chart"]["result"][0]
    series = [(u.EPOCH + timedelta(seconds=ts), c) for ts, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c]
    splits = []
    for s in d.get("events", {}).get("splits", {}).values():
        splits.append((u.EPOCH + timedelta(seconds=int(s["date"])), s["numerator"] / s["denominator"]))
    return series, splits


_INST = {}


def instance(cik, accn):
    """보고서 XBRL 원문(instance) 텍스트. www.sec.gov는 curl로는 안 붙고 urllib로는 된다. 없으면 ""."""
    if accn not in _INST:
        base = "https://www.sec.gov/Archives/edgar/data/%d/%s/" % (int(cik), accn.replace("-", ""))
        names = [x["name"] for x in json.loads(u.get(base + "index.json", u.SEC_UA))["directory"]["item"]]
        time.sleep(0.15)
        inst = [n for n in names if n.endswith("_htm.xml")] or \
               [n for n in names if n.endswith(".xml") and n != "FilingSummary.xml" and not n.endswith(("_cal.xml", "_def.xml", "_lab.xml", "_pre.xml"))]
        _INST[accn] = u.get(base + inst[0], u.SEC_UA).decode("utf-8", "replace") if inst else ""
        time.sleep(0.15)
    return _INST[accn]


def instance_facts(x, pattern):
    """원문에서 태그명이 pattern(정규식)에 맞는 숫자 사실 → [(태그, 값, instant 또는 None, 차원 있음 여부)]."""
    out, seen = [], set()
    for tag, ctx, val in re.findall(r'<([\w-]+:%s)\b[^>]*contextRef="([^"]+)"[^>]*>\s*(-?[\d.]+)\s*<' % pattern, x):
        if (tag, ctx) in seen:  # 원문에 같은 사실이 중복 기재되는 경우가 있다 (AVGO 메자닌 28M ×2)
            continue
        seen.add((tag, ctx))
        m = re.search(r'<(?:\w+:)?context id="%s">(.*?)</(?:\w+:)?context>' % re.escape(ctx), x, re.S)
        body = m.group(1) if m else ""
        inst = re.search(r"<(?:\w+:)?instant>([^<]+)<", body)
        out.append((tag, int(float(val)), inst.group(1) if inst else None, "explicitMember" in body or "typedMember" in body))
    return out


def instance_shares(cik, accn):
    """보고서 XBRL 원문에서 dei:EntityCommonStockSharesOutstanding 클래스별 값 합.
    companyfacts는 차원(클래스) 붙은 값을 빼므로 GOOGL·META는 여기서만 읽힌다. (합계, 기준일, 클래스 수) 또는 None."""
    got = {}
    for _, val, day, _ in instance_facts(instance(cik, accn), "EntityCommonStockSharesOutstanding"):
        got.setdefault(day, []).append(val)
    if not got:
        return None
    day = max(d for d in got if d)
    return sum(got[day]), day, len(got[day])


def market_rows(corp, tk, cik, reps, fx, series, splits):
    rows, bad = {}, []
    for end in sorted(reps):
        lab = label(end)
        if lab not in WINDOW:
            continue
        E = date.fromisoformat(end)
        avail = [x for x in series if x[0] <= E]
        if not avail:  # 상장 전 분기 (CRWD 2019 상장, 미국 라운드 3)
            why = "https://query1.finance.yahoo.com/v8/finance/chart/%s (firstTradeDate %s)" % (tk, series[0][0])
            for item in ("분기말 종가", "분기말 상장주식수", "분기말 시가총액"):
                rows[(lab, item)] = [corp, tk, lab, end, item,
                                     "데이터 없음(API 최초 거래일 %s 이전)" % series[0][0], "", "데이터 없음(상장 전)", why, ""]
            continue
        day, adj = max(avail, key=lambda x: x[0])
        k = 1.0
        for sd, r in splits:
            if sd > day:
                k *= r
        close = round(adj * k, 4)
        ysrc = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&events=splits (%s)" % (tk, day)
        rows[(lab, "분기말 종가")] = [corp, tk, lab, day.isoformat(), "분기말 종가", close, "USD", "API", ysrc,
                                  "분할조정 종가 %s × 이후 분할계수 %g" % (round(adj, 4), k) if k != 1 else ""]
        sh = None
        for a in reps[end]:
            es = fx.idx.get(("EntityCommonStockSharesOutstanding", a), [])
            if es:
                last = max(e["end"] for e in es)
                sh = (sum(e["val"] for e in es if e["end"] == last), last, a)
                break
        src_kind, src_note = "공시(표지 기준일)", "dei:EntityCommonStockSharesOutstanding 클래스 합"
        if not sh:  # companyfacts에 없으면 XBRL 원문에서 (클래스별 차원 공시)
            for a in reps[end]:
                got = instance_shares(cik, a)
                if got:
                    sh = (got[0], got[1], a)
                    src_note = "XBRL 원문 dei:EntityCommonStockSharesOutstanding %d개 클래스 합" % got[2]
                    break
        if not sh:
            why = "SEC companyfacts·XBRL 원문 모두 dei 표지 주식수 없음"
            for item in ("분기말 상장주식수", "분기말 시가총액"):
                rows[(lab, item)] = [corp, tk, lab, end, item, "미확인", "", "미확인", why, ""]
            continue
        # 분할일이 종가 거래일과 표지 기준일 사이면 표지 주식수는 분할 후 기준이다 → 종가 기준으로 되돌린다 (GOOGL 2022Q2)
        cover = date.fromisoformat(sh[1])
        ks = [(sd, r) for sd, r in splits if day < sd <= cover]
        k2 = 1.0
        for _, r in ks:
            k2 *= r
        mcap = round(close * sh[0] / k2)
        chk = "종가 %s × 주식수 %d" % (close, sh[0])
        if ks:
            chk += " ÷ 분할비율 %g (분할일 %s가 거래일 %s와 표지 기준일 %s 사이)" % (k2, ks[0][0], day, sh[1])
        rows[(lab, "분기말 상장주식수")] = [corp, tk, lab, sh[1], "분기말 상장주식수", sh[0], "주", src_kind,
                                      link(cik, sh[2]), src_note + ("; 표지 기준일이 분할 후" if ks else "")]
        rows[(lab, "분기말 시가총액")] = [corp, tk, lab, day.isoformat(), "분기말 시가총액", mcap, "USD", "계산(종가×주식수)",
                                    ysrc + " ; " + link(cik, sh[2]), chk]
    return rows, bad


ITEMS = ["분기별 매출액", "분기별 영업이익", "분기별 당기순이익(지배)", "분기별 영업활동현금흐름", "분기말 자산총계",
         "분기말 부채총계", "분기말 총자본(자기자본)", "분기말 지배지분 자본", "분기말 종가", "분기말 상장주식수", "분기말 시가총액"]
STOCK = ITEMS[4:8]  # 저량 4항목 (자산·부채·총자본·지배지분 자본)


def restate_rows(corp, tk, cik, reps, forms, fx):
    """fin_rows를 원 공시 · 재작성 반영 · 재분류까지 반영, 세 벌로 만들어 대조한다.
    재작성 반영 칸은 값구분에 "(재작성 반영)"을 붙이고 원값을 RESTATED에 남긴다.
    재작성 값으로 자체 검증을 못 통과한 칸은 원 공시를 두고, 재분류로만 달라지는 칸은 기록만 한다."""
    global RESTATE
    RESTATE = False
    orig, ofails = fin_rows(corp, tk, cik, reps, forms, fx)
    RESTATE = "all"
    full, _ = fin_rows(corp, tk, cik, reps, forms, fx)
    RESTATE = True
    new, fails = fin_rows(corp, tk, cik, reps, forms, fx)
    num = lambda v: not isinstance(v, str)
    for key, r in new.items():
        o, f = orig.get(key), full.get(key)
        if not o or not num(o[5]):
            continue
        if not num(r[5]):  # 재작성 값으로 검증 실패 → 원 공시 유지
            new[key] = o
            RESTATED.append(o[:5] + ["재작성 검증 실패(원 공시 유지)", o[5], o[7], o[8], "", r[8]])
        elif r[5] != o[5]:
            RESTATED.append(r[:5] + ["재작성 반영", o[5], o[7], o[8], r[5], r[8]])
            r[7] += "(재작성 반영)"
            r[9] = (r[9] + " ; " if r[9] else "") + "원 공시 %s (%s)" % (o[5], o[8])
        else:
            # 값이 같으면 원 행 그대로 둔다. 한 태그만 재작성돼 대체 규칙이 달리 걸리면
            # 값은 같은데 값구분·출처만 바뀐다 (D 2021Q4 총자본: 공시 → 공시(지배지분 태그))
            new[key] = o
            if f and num(f[5]) and f[5] != o[5]:
                RESTATED.append(o[:5] + ["재분류(미반영)", o[5], o[7], o[8], f[5], f[8]])
    # 저량 4항목은 한 묶음: 하나라도 재작성 검증 실패로 원 공시를 두면 나머지도 원 공시로 되돌린다
    # (지배지분 자본만 재작성값이 들어가 총자본 = 지배 + 비지배가 깨지는 것 방지, us-round31-log.md 5절)
    failed = {(x[2], x[4]) for x in RESTATED if x[1] == tk and x[5] == "재작성 검증 실패(원 공시 유지)"}
    for lab in {lab for lab, item in failed if item in STOCK}:
        for item in STOCK:
            o, r = orig.get((lab, item)), new.get((lab, item))
            if (lab, item) in failed or not o or not num(o[5]) or r is o:
                continue
            new[(lab, item)] = o
            RESTATED[:] = [x for x in RESTATED if not (x[1] == tk and x[2] == lab and x[4] == item)]
            RESTATED.append(o[:5] + ["재작성 검증 실패(원 공시 유지)", o[5], o[7], o[8], r[5], r[8]])
    # 검증 실패 목록은 최종 행 기준 (원 공시로 되돌린 칸은 빼고, 원 공시에서 실패했던 칸은 넣는다)
    left = {lab for (lab, _), r in new.items() if r[5] == "미확인"}
    fails = [x for x in dict.fromkeys(ofails + fails) if x[0] in left]
    return new, fails


def main():
    all_rows, summary = [], []
    for corp, tk, cik in TOP10:
        t0 = time.time()
        reps, forms = reports(cik)
        fx = Facts(cik)
        series, splits = yahoo_series(tk)
        fin, ffail = restate_rows(corp, tk, cik, reps, forms, fx)
        mkt, mbad = market_rows(corp, tk, cik, reps, fx, series, splits)
        got = {**fin, **mkt}
        labs = [label(e) for e in reps if label(e) in WINDOW]
        dup = sorted({l for l in labs if labs.count(l) > 1})
        for lab in WINDOW:
            for item in ITEMS:
                r = got.get((lab, item)) or [corp, tk, lab, "", item, "미확인", "", "미확인", "해당 라벨 보고서 없음", ""]
                all_rows.append(r)
        amended = sorted(label(e) for e, a in reps.items() if len(a) > 1 and label(e) in WINDOW)
        kinds = {}
        for lab in WINDOW:
            for item in ITEMS:
                k = got.get((lab, item), [None] * 8)[7] or "미확인"
                kinds[k] = kinds.get(k, 0) + 1
        summary.append({"기업": corp, "티커": tk, "CIK": cik, "값구분": kinds, "자체검증실패": ffail, "시총검증실패": mbad,
                        "라벨중복": dup, "정정판본있는기간": amended, "분할": [(str(d), r) for d, r in splits]})
        print("%s | %s | 검증실패 %s | 라벨중복 %s | 정정판본 %s | %.0fs" % (tk, kinds, ffail or "없음", dup or "없음",
                                                                  amended or "없음", time.time() - t0), flush=True)
    if ROW_FIX:  # 라운드별 주석 보강 (collect_us_round2.fix_rows)
        ROW_FIX(all_rows)
    # 라운드별 규칙이 나중에 덮어쓴 칸(VRT 합병 전 → 데이터 없음 등)은 재작성 기록에서 뺀다:
    # 최종 값이 기록의 값(반영이면 나중 값, 아니면 원 공시값)과 같은 칸만 남긴다
    final = {(r[1], r[2], r[4]): r[5] for r in all_rows}
    RESTATED[:] = [x for x in RESTATED if final.get((x[1], x[2], x[4])) == (x[9] if x[5] == "재작성 반영" else x[6])]
    with open(OUTDIR + OUT, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([HEAD] + all_rows)
    with open(OUTDIR + OUT.replace("-dataset.csv", "-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(OUTDIR + OUT.replace("-dataset.csv", "-restated.csv"), "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([HEAD[:5] + ["구분", "원 공시값", "원 값구분", "원 출처", "나중 보고서 값", "나중 보고서 출처"]]
                                + RESTATED)
    print("재작성 기록:", {k: sum(r[5] == k for r in RESTATED) for k in sorted({r[5] for r in RESTATED})})
    print("rows:", len(all_rows), "| 빈 값:", sum(r[5] == "" for r in all_rows), "| 빈 출처:", sum(r[8] == "" for r in all_rows))


if __name__ == "__main__":
    main()
