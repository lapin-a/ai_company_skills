"""라운드 1 기획 2팀: DART 공시뷰어에서 삼성전자 연결재무제표 분기 시계열 수집 -> round1-dataset.csv"""

import csv
import html
import re
import time
import urllib.request

CORP, CODE = "삼성전자", "005930"
# 보고기간 -> rcpNo (DART 공시검색 2019.01.01~2026.09.17 결과, coverage-log.md 참조)
REPORTS = {
    "2019.03": "20190515001605", "2019.06": "20190814002218", "2019.09": "20191114001273", "2019.12": "20200330003851",
    "2020.03": "20200515001451", "2020.06": "20200814001766", "2020.09": "20201116001248", "2020.12": "20210309000744",
    "2021.03": "20210517001185", "2021.06": "20210817001416", "2021.09": "20211115001965", "2021.12": "20220308000798",
    "2022.03": "20220516001751", "2022.06": "20220816001711", "2022.09": "20221114001832", "2022.12": "20230307000542",
    "2023.03": "20230515002335", "2023.06": "20230814002534", "2023.09": "20231114002109", "2023.12": "20240312000736",
    "2024.03": "20240516001421", "2024.06": "20240814003284", "2024.09": "20241114002642", "2024.12": "20250311001085",
    "2025.03": "20250515001922", "2025.06": "20250814003156", "2025.09": "20251114002447", "2025.12": "20260310002820",
    "2026.03": "20260515002181", "2026.06": "20260814003699",
}
VIEW = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="
UNITS = {"원": 1, "천원": 10**3, "백만원": 10**6}
QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
MARKET_ITEMS = ["분기말 종가", "분기말 상장주식수", "분기말 시가총액"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    time.sleep(1)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp949")


OLD_MARK = "<!--XI.재무제표등-->"  # 옛 목차 장에서 가져온 문서 표시 (statements가 엄격 모드로 읽는다)


def fs_section(rcp):
    page = fetch(VIEW + rcp)
    m = re.search(r"\['text'\] = \"\d+\. ?연결재무제표\";(.*?)\['text'\]", page, re.S)
    old = m is None
    if old:
        # 2014년 이전 보고서에는 "N. 연결재무제표" 장이 없다. "XI. 재무제표 등" 장에 연결·별도가 함께 있다
        m = re.search(r"\['text'\] = \"[IVX]+\. ?재무제표 ?등\";(.*?)\['text'\]", page, re.S)
    if not m:
        return None
    attrs = dict(re.findall(r"\['(\w+)'\] = +\"([^\"]*)\"", m.group(1)))
    attrs.setdefault("rcpNo", rcp)
    q = "&".join(k + "=" + attrs[k] for k in ("rcpNo", "dcmNo", "eleId", "offset", "length", "dtd"))
    doc = fetch("https://dart.fss.or.kr/report/viewer.do?" + q)
    return OLD_MARK + doc if old else doc


def cells(row):
    out = []
    for c in re.findall(r"<T[DH][^>]*>(.*?)</T[DH]>", row, re.S | re.I):
        t = html.unescape(re.sub(r"<[^>]+>", "", c))
        out.append(re.sub(r"[\s　\xa0]+", "", t))
    return out


def num(s):
    s = s.replace(",", "")
    neg = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("()-")
    if not s.isdigit():
        return None
    return -int(s) if neg else int(s)


NUMBERING = re.compile(r"^(?:[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+|[IVX]+|\d+|[가-하])[\.\)]|^\(\d+\)")
REV_ORDER = ["매출액", "매출액(영업수익)", "영업수익(매출액)", "매출", "매출액및기타수익", "매출및기타수익", "매출액및기타영업수익", "수익(매출액)", "영업수익", "영업수익및기타수익", "수익",
             # 지주회사 LG는 최상단 줄이 "매출및지분법손익"뿐이다(지분법손익 포함). 다른 매출 줄이 없을 때만 쓴다.
             "매출및지분법손익"]
OP = re.compile(r"^영업(이익|손익|손실)")
NI_TOTAL = re.compile(r"^(당기|분기|반기|중간|당분기)?순(이익|손익|손실)(\(손실\))?$")
TOTALS = {"assets": re.compile(r"^자산(총계|계|합계)$"), "liab": re.compile(r"^부채(총계|계|합계)$"),
          "equity": re.compile(r"^자본(총계|계|합계)$")}
FIN_ITEMS = [("분기말 자산총계", "assets"), ("분기말 부채총계", "liab"), ("분기말 총자본(자기자본)", "equity")]
FLOW_ITEMS = [("분기별 매출액", "rev"), ("분기별 영업이익", "op"), ("분기별 당기순이익(지배)", "ni")]


def norm(label):
    """라벨 정규화: 주석 표시((주3), (주석 4) 등)와 앞 번호(Ⅰ., 1., (1) 등)를 뗀다."""
    label = re.sub(r"\((?:주|주석|Note)[^)]*\)", "", label)
    # K-IFRS 도입(2011) 전 연결재무제표는 비지배지분을 "소수주주지분"이라 불렀다. 못 알아보면 총계가 지배 몫으로 들어간다
    return NUMBERING.sub("", label).replace("소수주주", "비지배")


# 대차대조표 = K-IFRS 도입(2011) 전 재무상태표 이름. 포괄손익계산서는 손익계산서 뒤에 둬야 CI로 잡힌다
NAMES = (("BS", "재무상태표"), ("BS", "대차대조표"), ("IS", "손익계산서"), ("CI", "포괄손익계산서"), ("CF", "현금흐름표"))
TITLE = re.compile(r"연결(재무상태표|대차대조표|손익계산서|포괄손익계산서|현금흐름표)")


def statements(doc, period=None):
    """{'BS'|'IS'|'CI'|'CF': (단위배수, 머리행텍스트, 행목록)}

    제목 표(행 6개 미만, 표 이름 포함) 다음에 오는 첫 데이터 표(행 6개 이상)를 그 표 이름으로 잡는다.
    THEAD 유무와 무관하게 동작한다. CI = 연결포괄손익계산서 (별도 손익계산서가 없는 회사용).
    period("YYYY.MM")를 주면 옛 목차 문서에서는 제목~본표 사이에 그 분기말 날짜가 있는 표만 받는다.
    """
    out, cur, unit, ptxt = {}, None, 1, ""
    # 옛 목차("XI. 재무제표 등")에서 온 문서는 별도재무제표도 함께 있다 → "연결"이 붙은 제목만 인정한다
    old = doc.startswith(OLD_MARK)
    # K-IFRS 도입(2011) 전 분기보고서의 "연결재무제표"는 직전 사업연도 연간 것이다 (SK하이닉스 2010 반기 → 2009년).
    # 대차 검증은 통과하므로 날짜로 걸러야 한다
    want = None
    if old and period:
        y, mm = period.split(".")
        want = re.compile(r"%s[.년-]0?%d[.월-]%s" % (y, int(mm), QEND[int(mm) // 3][3:]))
    for t in re.split(r"(<TABLE.*?</TABLE>)", doc, flags=re.S | re.I):
        if not re.match(r"\s*<TABLE", t, re.I):
            # 표 이름이 표 밖 본문에 있는 보고서도 있다 (현대글로비스·LG이노텍·현대오토에버 2023).
            # 이 문서는 이미 "연결재무제표" 장만 잘라온 것이라 "연결"이 안 붙은 제목도 그대로 쓴다.
            # 제목 줄만 보려고 짧은 텍스트로 제한한다(주석 본문에 걸리지 않게).
            txt = re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", t)
            if len(txt) <= 40:
                for key, name in NAMES:
                    if ("연결" + name if old else name) in txt:
                        cur, ptxt = key, txt
            continue
        trs = re.findall(r"<TR.*?</TR>", t, re.S | re.I)
        txt = re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", t)
        # 제목 표는 보통 6행 미만이다. 2012년 보고서에는 기간 줄이 많아 6행인 제목 표가 있다(삼성전자 2012Q1)
        title = len(trs) < 6 or (len(trs) <= 8 and TITLE.match(txt))
        if cur and cur not in out and not title:
            rows = [cells(r) for r in trs]
            # &nbsp;도 지운다: SK스퀘어 2022는 머리행이 "누&nbsp;적"이라 누적 열을 못 알아봤다
            head = "".join(re.sub(r"<[^>]+>|&nbsp;|\s", "", r) for r in trs[:3])
            if not want or want.search(ptxt + head):
                out[cur] = (unit, head, rows)
            cur = None
            continue
        if title:
            ptxt += txt  # 제목 다음 기간·단위 표 (SK하이닉스 2010은 제목과 따로 있다)
            for key, name in NAMES:
                if "연결" + name in txt:
                    cur, ptxt = key, txt
            u = re.search(r"단위:(원|천원|백만원)", txt)
            if u:
                unit = UNITS[u.group(1)]
    return out


def values(row):
    """행의 숫자 셀만 순서대로. 빈 칸·주석 칸이 섞여 있어도 열 위치가 밀리지 않는다."""
    return [v for v in (num(c) for c in row[1:]) if v is not None]


def pick(stmt, test, col):
    if not stmt:
        return None
    unit, _, rows = stmt
    for r in rows:
        if r and test(norm(r[0])):
            vs = values(r)
            if len(vs) > col:
                return vs[col] * unit
    return None


def pick_total(stmt, key, col=0):
    """총계 행. '자산총계'류가 없으면 값이 있는 마지막 '자산'/'부채'/'자본' 행을 총계로 본다(LS ELECTRIC 등)."""
    v = pick(stmt, lambda s: bool(TOTALS[key].match(s)), col)
    if v is not None or not stmt:
        return v
    word = {"assets": "자산", "liab": "부채", "equity": "자본"}[key]
    unit, _, rows = stmt
    hits = [values(r)[col] for r in rows if r and norm(r[0]) == word and len(values(r)) > col]
    return hits[-1] * unit if hits else None


def aligned(stmt, test):
    """당기 열 값을 자본총계 행의 당기 열 위치로 읽는다. 빈 칸이면 0.
    values()는 빈 칸을 건너뛰어, 당기 칸이 빈 비지배지분 행에서 전기 값을 당기로 읽는다 (HD현대일렉트릭·한화오션 2019~2021)."""
    if not stmt:
        return None
    unit, _, rows = stmt
    ref = next((r for r in rows if r and TOTALS["equity"].match(norm(r[0])) and values(r)), None)
    if ref is None:  # '자본총계' 없이 값 있는 '자본' 행이 총계인 회사 (LS ELECTRIC, pick_total과 같은 규칙)
        ref = next((r for r in reversed(rows) if r and norm(r[0]) == "자본" and values(r)), None)
    row = next((r for r in rows if r and test(norm(r[0]))), None)
    if ref is None or row is None:
        return None
    i = next(k for k in range(1, len(ref)) if num(ref[k]) is not None)
    v = num(row[i]) if i < len(row) else None
    return (v or 0) * unit


def held_for_sale_split(bs):
    """'매각예정…기타포괄손익' 행 아래 지배/비지배 구분 행 (두산 2020Q3·2021Q2). (지배분, 비지배분, 매각예정 행 있음)."""
    if not bs:
        return 0, 0, False
    unit, _, rows = bs
    par = nci = 0
    seen = main_nci = False
    # 자본 구간만 본다 ('매각예정비유동자산' 등 자산 쪽 행 제외): 값 없는 '자본' 머리행 아래.
    # 머리행이 없으면(LS ELECTRIC처럼 '자본' 행이 총계) 첫 '자본' 행부터.
    heads = [k for k, r in enumerate(rows) if r and norm(r[0]) == "자본"]
    start = max((k for k in heads if not values(rows[k])), default=min(heads, default=len(rows)))
    for r in rows[start:]:
        label = norm(r[0]) if r else ""
        if not seen and label.startswith("비지배"):
            main_nci = True
        # 비지배지분 행 뒤의 매각예정 행만 별도 구분이다. 앞에 있으면 지배지분 구성항목이다 (현대차·두산에너빌리티)
        if "매각예정" in label and main_nci:
            seen = True
        elif seen and TOTALS["equity"].match(label):
            break
        elif seen and values(r):
            if label.startswith("비지배"):
                nci += values(r)[0] * unit
            elif "지배" in label:
                par += values(r)[0] * unit
    return par, nci, seen


def parent_equity(bs):
    """지배지분 자본. 지배지분 행이 값 없는 머리행이면 자본총계 − 비지배지분, 비지배지분이 없으면 자본총계.
    매각예정 자본의 지배분이 따로 공시되면 더한다. 매각예정 행이 있는데 구분이 없으면 확정할 수 없다(None)."""
    hp, hn, hseen = held_for_sale_split(bs)
    v = pick(bs, lambda s: "지배" in s and "비지배" not in s, 0)
    if v is not None:
        if hseen and not (hp or hn):
            return None  # 두산 2022Q2: 매각예정 기타포괄손익의 지배/비지배 귀속 미공시
        return v + hp
    if not bs:
        return v
    equity = pick_total(bs, "equity")
    nci = aligned(bs, lambda s: s.startswith("비지배") and "부채" not in s and "자산" not in s)
    if equity is None:
        return None
    return equity - nci if nci is not None else equity


def pick_rev(stmt, col):
    """매출 계열 라벨을 우선순위대로 찾는다 (SK스퀘어는 '영업수익'에 지분법손익이 들어가 '매출액'을 먼저 본다)."""
    for label in REV_ORDER:
        v = pick(stmt, lambda s, l=label: s == l, col)
        if v is not None:
            return v
    return None


def pick_parent_ni(stmt, col):
    """'...의귀속' 행 아래 첫 지배 몫 행. 라벨이 연도마다 달라 위치로 찾는다 (2025.03은 '분기순이익')."""
    if not stmt:
        return None
    unit, _, rows = stmt
    # 1차: 당기순이익의 귀속. '계속영업이익의 귀속'(중단영업 제외, 삼성전기 2019)·'총포괄이익의 귀속'은 건너뛴다.
    # 2차: 그런 머리행이 없으면 처음 나오는 귀속 머리행 (기존 동작)
    for skip in (("계속영업", "포괄"), ()):
        seen = False
        for r in rows:
            label = norm(r[0]) if r else ""
            if label.endswith("귀속"):
                seen = not any(w in label for w in skip)
            elif seen and "비지배" not in label:
                vs = values(r)
                if len(vs) > col:
                    return vs[col] * unit
    # 귀속 머리행이 없는 보고서: '지배…' 행을 직접 찾는다 (SK·효성중공업 등)
    for r in rows:
        label = norm(r[0]) if r else ""
        if "지배" in label and "비지배" not in label:
            vs = values(r)
            if len(vs) > col:
                return vs[col] * unit
    return None


def parse(doc, period=None):
    txt_only = re.sub(r"<[^>]+>|&nbsp;", " ", doc or "")
    # "해당사항 없습니다" 외에 "연결대상 종속회사가 없어 연결재무제표를 작성하지 않습니다"도 같은 경우다 (LIG 2019)
    if (re.search(r"해당\s*사항\s*이?\s*없", txt_only) or re.search(r"연결재무제표를?\s*작성하지\s*않", txt_only)) \
            and not re.search(r"<TABLE", doc or "", re.I):
        return {"no_consol": True}  # "2. 연결재무제표 → 해당사항 없습니다" (연결 대상 자체가 없는 기간)
    st = statements(doc, period)
    if not st and period and doc.startswith(OLD_MARK):
        # 옛 목차 보고서에 그 분기 연결재무제표가 하나도 없다 (K-IFRS 도입 전 분기보고서는 개별 기준만 싣는다)
        return {"no_consol": "미수록"}
    bs, cf = st.get("BS"), st.get("CF")
    # 손익 항목은 연결손익계산서 우선, 없거나 행이 빠지면 연결포괄손익계산서에서 찾는다
    cands = [x for x in (st.get("IS"), st.get("CI")) if x]

    old = (doc or "").startswith(OLD_MARK)
    # 옛 목차 보고서는 누적 열을 "누계"라고 쓴다 (삼성전자 2010 3분기). 새 형식은 회귀 검사 전이라 기존 규칙 그대로
    cum_words = ("누적", "누계") if old else ("누적",)
    # 옛 목차 반기·3분기 보고서 중에는 3개월 열 없이 누적 열만 있는 것이 있다 (LG전자 2010 반기).
    # 이때 첫 열은 누적이다 → 3개월 값은 비워 두고 build_fin_rows가 누적차감으로 만든다
    cum_only = old and period is not None and period[5:] in ("06", "09")

    def both(fn):
        for stmt in cands:
            cum = 1 if any(w in stmt[1] for w in cum_words) else 0
            if old and period and period[5:] == "12":
                cum = 0  # 사업보고서는 3개월 열이 없다. "누계" 머리행이어도 둘째 열은 전년이다 (삼성전자 2010)
            if cum_only and not cum and "3개월" not in stmt[1]:
                vc = fn(stmt, 0)
                if vc is not None:
                    flags.add("cum_only")
                    return None, vc
                continue
            v3, vc = fn(stmt, 0), fn(stmt, cum)
            if v3 is not None or vc is not None:
                return v3, vc
        return None, None

    flags = set()

    has_nci_is = any("비지배" in norm(r[0]) for stmt in cands for r in stmt[2] if r)
    rev3, revC = both(pick_rev)
    op3, opC = both(lambda s, c: pick(s, lambda x: bool(OP.match(x)), c))
    ni3, niC = both(pick_parent_ni)
    if ni3 is None and niC is None and not has_nci_is:
        # 비지배지분이 없는 회사: 귀속 구분 없이 순이익 한 줄만 있다 (HD현대중공업 2021 등)
        ni3, niC = both(lambda stmt, c: pick(stmt, lambda x: bool(NI_TOTAL.match(x)), c))
    equity, equity_kind, nci_fb = pick_total(bs, "equity"), "공시", None
    parent = parent_equity(bs)
    if equity is None and parent is not None:
        # '자본총계' 행이 없는 보고서: 지배 + 비지배로 만든다 (현대건설 2023 사업보고서)
        nci_fb = pick(bs, lambda s: s.startswith("비지배") and "부채" not in s and "자산" not in s, 0) or 0
        equity, equity_kind = parent + nci_fb, "계산(지배+비지배)"
    return {
        "rev3": rev3, "revC": revC, "op3": op3, "opC": opC, "ni3": ni3, "niC": niC,
        "assets": pick_total(bs, "assets"), "liab": pick_total(bs, "liab"), "equity": equity, "equity_kind": equity_kind,
        "parent_eq": parent,
        # "비지배지분부채"처럼 부채 쪽 행이 먼저 걸리면 안 된다 (KT&G·현대건설)
        # aligned()는 자본총계 행을 기준으로 열을 맞춘다. 그 행이 없으면 위 fallback 값을 쓴다.
        "nci": ((aligned(bs, lambda s: s.startswith("비지배") and "부채" not in s and "자산" not in s)
                 if nci_fb is None else nci_fb) or 0) + held_for_sale_split(bs)[1],
        "ocfC": pick(cf, lambda s: s.startswith("영업활동") and "현금흐름" in s, 0),
        "is_kind": "IS" if st.get("IS") else ("CI" if st.get("CI") else None),
        "cum_only": "cum_only" in flags,
    }


def close(a, b):
    """공시 반올림 허용오차: 백만원 단위 공시에서 1단위(=1,000,000원) 차이가 날 수 있다."""
    return abs(a - b) <= max(1_000_000, abs(a) * 1e-9)


def verify(d):
    """자체 검증. 실패한 항목 키 목록을 돌려준다 (실패 칸은 미확인 처리)."""
    bad = []
    if None not in (d.get("assets"), d.get("liab"), d.get("equity")) and not close(d["assets"], d["liab"] + d["equity"]):
        bad += ["assets", "liab", "equity"]
    if None not in (d.get("equity"), d.get("parent_eq")):
        nci = d.get("nci") or 0  # 비지배지분 행이 없는 회사는 0
        if not close(d["equity"], d["parent_eq"] + nci):
            bad += ["parent_eq"]
    return bad


def build_fin_rows(corp, code, reports, data, window):
    """기간×재무 8항목 행. reports: {"YYYY.MM": rcpNo}, data: {"YYYY.MM": parse 결과}, window: 수집 창 기간 목록."""
    out, fails = [], {}
    first = min(reports) if reports else None
    for period in window:
        y, mm = period.split(".")
        q = int(mm) // 3
        base = [corp, code, "%sQ%d" % (y, q), "%s-%s" % (y, QEND[q])]
        nc = data.get(period, {}).get("no_consol")
        if period in reports and nc:
            # "미수록" = 옛 목차 보고서에 그 분기 연결재무제표가 없다 (K-IFRS 도입 전 분기, backfill-2010s-log.md)
            label, kind = (("데이터 없음(연결재무제표 미해당)", "데이터 없음(연결 미해당)") if nc is True else
                           ("데이터 없음(보고서에 해당 분기 연결재무제표 없음)", "데이터 없음(연결 미수록)"))
            for item, _ in FIN_ITEMS + FLOW_ITEMS + [("분기별 영업활동현금흐름", ""), ("분기말 지배지분 자본", "")]:
                out.append(base + [item, label, kind, VIEW + reports[period]])
            continue
        if period not in reports:
            label = "데이터 없음(최초 보고기간 이전)" if first is None or period < first else "미확인"
            kind = "데이터 없음(최초 보고기간 전)" if label.startswith("데이터") else "미확인"
            for item, _ in FIN_ITEMS + FLOW_ITEMS + [("분기별 영업활동현금흐름", ""), ("분기말 지배지분 자본", "")]:
                out.append(base + [item, label, kind, "DART 정기보고서 없음"])
            continue
        d = data.get(period, {})
        bad = verify(d)
        if bad:
            fails[period] = bad
        prev = "%s.%02d" % (y, (q - 1) * 3) if q > 1 else None
        q3 = "%s.09" % y

        def add(item, val, kind, rcps, key=None):
            src = " ; ".join(VIEW + r for r in rcps)
            if key in bad:
                val = None
            out.append(base + [item, val if val is not None else "미확인", kind if val is not None else "미확인", src])

        def nodata(item, why):
            out.append(base + [item, "데이터 없음(%s)" % why, "데이터 없음(직전 보고서 없음)", VIEW + reports[period]])

        for item, k in FIN_ITEMS:
            add(item, d.get(k), d.get(k + "_kind", "공시"), [reports[period]], k)
        for item, k in FLOW_ITEMS:
            if q < 4 and d.get("cum_only"):
                # 3개월 열 없이 누적 열만 있는 옛 보고서 (LG전자 2010 반기): 영업CF와 같은 누적차감
                if prev not in reports or data.get(prev, {}).get("no_consol"):
                    nodata(item, "직전 분기 누적 보고서 없음")
                else:
                    a, b = d.get(k + "C"), data.get(prev, {}).get(k + "C")
                    add(item, a - b if None not in (a, b) else None, "계산(누적차감)", [reports[period], reports[prev]])
            elif q < 4:
                add(item, d.get(k + "3"), "공시", [reports[period]])
            elif q3 not in reports and period == first:
                # 최초 사업연도가 4분기에 시작한 회사: 연간 공시값이 곧 그 기간의 값이다 (계산 아님)
                add(item, d.get(k + "C"), "공시", [reports[period]])
            elif q3 not in reports or data.get(q3, {}).get("no_consol"):
                nodata(item, "3분기 누적 보고서 없음")
            else:
                a, b = d.get(k + "C"), data.get(q3, {}).get(k + "C")
                add(item, a - b if None not in (a, b) else None, "계산(연간-3분기누적)", [reports[period], reports[q3]])
        if q == 1:
            add("분기별 영업활동현금흐름", d.get("ocfC"), "공시", [reports[period]])
        elif prev not in reports and period == first:
            add("분기별 영업활동현금흐름", d.get("ocfC"), "공시", [reports[period]])
        elif prev not in reports or data.get(prev, {}).get("no_consol"):
            # 직전 분기가 "연결 미해당"이면 뺄 누적이 없다 (LIG 2019Q3)
            nodata("분기별 영업활동현금흐름", "직전 분기 누적 보고서 없음")
        else:
            a, b = d.get("ocfC"), data.get(prev, {}).get("ocfC")
            add("분기별 영업활동현금흐름", a - b if None not in (a, b) else None, "계산(누적차감)", [reports[period], reports[prev]])
        add("분기말 지배지분 자본", d.get("parent_eq"), "공시", [reports[period]], "parent_eq")
    return out, fails


def main():
    data = {}
    for period, rcp in REPORTS.items():
        doc = fs_section(rcp)
        data[period] = parse(doc) if doc else {}
        print(period, rcp, "ok" if doc else "연결재무제표 섹션 없음", data[period])

    fin, fails = build_fin_rows(CORP, CODE, REPORTS, data, list(REPORTS))
    out = []
    for i in range(0, len(fin), 8):  # 분기별 재무 8행 뒤에 시장 3행 (collect_market_round1.py가 채운다)
        out += fin[i:i + 8] + [fin[i][:4] + [item, "미확인", "미확인", "collect_market_round1.py 실행 전"] for item in MARKET_ITEMS]

    with open("kr/data/round1-dataset.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["기업", "종목코드", "기간", "기준일", "항목", "값(원)", "값구분", "출처"])
        w.writerows(out)
    print("rows:", len(out), "| 검증 실패 분기:", fails or "없음")


if __name__ == "__main__":
    main()
