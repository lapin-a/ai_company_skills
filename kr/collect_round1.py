"""라운드 1 기획 2팀: DART 공시뷰어에서 삼성전자 연결재무제표 분기 시계열 수집 -> round1-dataset.csv"""

import csv
import html
import io
import json
import re
import time
import urllib.request
import zipfile

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
FIN = False  # 금융회사 라운드만 켠다 (collect_fin.py). 끄면 비금융 라운드와 동작이 같다.


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    time.sleep(1)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp949")


OLD_NO_CONSOL = "<!-- 옛 양식: 본문에 연결재무제표 없음 -->"  # 2010~2012 분기·반기 등 (대표 결정 2026-09-22: 비워 둔다)


def api_doc(rcp):
    """OpenDART 공시서류원본(document.xml) 본문 XML. 공시뷰어는 병렬 조회 때 IP를 막아서(2026-09-22) 원본 API로 바꿨다."""
    with open(".claude/settings.local.json", encoding="utf-8") as f:
        key = json.load(f)["env"]["DART_API_KEY"]
    with urllib.request.urlopen("https://opendart.fss.or.kr/api/document.xml?crtfc_key=%s&rcept_no=%s" % (key, rcp),
                                timeout=60) as r:
        b = r.read()
    time.sleep(0.5)
    if not b.startswith(b"PK"):  # 오류는 zip 대신 상태 메시지로 온다
        msg = b[:300].decode("utf-8", "replace")
        if re.search(r"<status>020|\"020\"", msg):  # 요청 제한 초과: 계속하면 전부 미확인이 되므로 멈춘다
            raise SystemExit("OpenDART 요청 제한 초과 — 중단: " + msg)
        if re.search(r"<status>014", msg):  # 원본 파일 없음 (한화에어로스페이스 2026.03) → 공시뷰어로
            return None
        raise RuntimeError("document.xml 오류: " + msg)
    z = zipfile.ZipFile(io.BytesIO(b))
    raw = z.read(min(z.namelist(), key=lambda n: ("_" in n.rsplit("/", 1)[-1], len(n))))  # 본문 = 접미사 없는 파일
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp949")


def xml_section(x, title_re, level):
    """원본 XML에서 TITLE이 맞는 SECTION-level 장을 잘라, 칸 태그를 공시뷰어처럼 TD로 맞춘다."""
    m = re.search(r"<TITLE[^>]*>\s*" + title_re + r"\s*</TITLE>", x)
    if not m:
        return None
    end = x.find("</SECTION-%d>" % level, m.end())
    body = x[m.start():end if end > 0 else len(x)]
    return re.sub(r"<(/?)T[EU](?=[\s>])", r"<\1TD", body).replace("&cr;", " ")  # TE·TU = DART 전용 칸 태그


def viewer_section(page, rcp, title_re):
    """공시뷰어 목차에서 제목이 맞는 장을 받아 온다 (원본 API에 파일이 없는 보고서용)."""
    m = re.search(r"\['text'\] = \"" + title_re + r"\";(.*?)\['text'\]", page, re.S)
    if not m:
        return None
    attrs = dict(re.findall(r"\['(\w+)'\] = +\"([^\"]*)\"", m.group(1)))
    attrs.setdefault("rcpNo", rcp)
    q = "&".join(k + "=" + attrs[k] for k in ("rcpNo", "dcmNo", "eleId", "offset", "length", "dtd"))
    return fetch("https://dart.fss.or.kr/report/viewer.do?" + q)


def fs_section(rcp):
    x = api_doc(rcp)
    page = fetch(VIEW + rcp) if x is None else None
    get = (lambda t, lv: xml_section(x, t, lv)) if page is None else (lambda t, lv: viewer_section(page, rcp, t))
    doc = get(r"\d+\. ?연결재무제표", 2)
    # 2014.09 이전 옛 양식: 목차에 연결재무제표 장이 없고 "XI. 재무제표 등"에 연결 → 별도 순으로 싣는다 (유한양행 2013~2014).
    # 연결재무상태표가 없으면(2011~2012 분기: 별도만 실음) 쓰지 않는다 — 별도를 연결로 읽지 않게.
    old = doc is None
    if old:
        doc = get(r"[IVX]+\. ?재무제표 등", 1)
    if doc is None:
        return None
    if old:
        if "연결재무상태표" not in re.sub(r"<[^>]+>|&nbsp;|\s", "", doc):
            return OLD_NO_CONSOL
        # 뒤의 별도 재무제표는 잘라낸다 (연결에 없는 표를 별도 표로 채우지 않게)
        for t in re.finditer(r"<TABLE.*?</TABLE>", doc, re.S | re.I):
            if re.sub(r"<[^>]+>|&nbsp;|\s", "", t.group()).startswith("재무상태표"):
                return doc[:t.start()]
    return doc


def cells(row):
    out = []
    for c in re.findall(r"<T[DH][^>]*>(.*?)</T[DH]>", row, re.S | re.I):
        t = html.unescape(re.sub(r"<[^>]+>", "", c))
        out.append(re.sub(r"[\s　\xa0]+", "", t))
    return out


def num(s):
    s = s.replace(",", "")
    if FIN:  # "378,360,504============" (기업은행 2021 합계 밑줄)
        s = s.rstrip("=")
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
# "총자산"·"자산총액" 표기도 있다 (포스코인터내셔널 2024·2025 사업보고서, LS 2026)
TOTALS = {"assets": re.compile(r"^(자산(총계|계|합계|총액)|총자산)$"), "liab": re.compile(r"^(부채(총계|계|합계|총액)|총부채)$"),
          "equity": re.compile(r"^(자본(총계|계|합계|총액)|총자본)$")}
FIN_ITEMS = [("분기말 자산총계", "assets"), ("분기말 부채총계", "liab"), ("분기말 총자본(자기자본)", "equity")]
FLOW_ITEMS = [("분기별 매출액", "rev"), ("분기별 영업이익", "op"), ("분기별 당기순이익(지배)", "ni")]


def norm(label):
    """라벨 정규화: 주석 표시((주3), (주석 4) 등)와 앞 번호(Ⅰ., 1., (1) 등)를 뗀다."""
    label = re.sub(r"\((?:주|주석|Note)[^)]*\)", "", label)
    if FIN:  # "영업수익<주석40>"(DB손해보험 2019), "lll.영업이익"(소문자 l 로마숫자)·"…순이익귀속:"(삼성화재 2021)
        label = re.sub(r"<[^>]*>", "", label).rstrip(":")
        label = re.sub(r"^[lIVX]+\.", "", label)
    return NUMBERING.sub("", label)


def statements(doc):
    """{'BS'|'IS'|'CI'|'CF': (단위배수, 머리행텍스트, 행목록)}

    제목 표(행 6개 미만, 표 이름 포함) 다음에 오는 첫 데이터 표(행 6개 이상)를 그 표 이름으로 잡는다.
    THEAD 유무와 무관하게 동작한다. CI = 연결포괄손익계산서 (별도 손익계산서가 없는 회사용).
    """
    out, cur, unit = {}, None, 1
    for t in re.split(r"(<TABLE.*?</TABLE>)", doc, flags=re.S | re.I):
        if not re.match(r"\s*<TABLE", t, re.I):
            # 표 이름이 표 밖 본문에 있는 보고서도 있다 (현대글로비스·LG이노텍·현대오토에버 2023).
            # 이 문서는 이미 "연결재무제표" 장만 잘라온 것이라 "연결"이 안 붙은 제목도 그대로 쓴다.
            # 제목 줄만 보려고 짧은 텍스트로 제한한다(주석 본문에 걸리지 않게).
            txt = re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", t)
            # 금융: 제목이 긴 안내문 끝에 붙은 보고서가 있다 (기업은행 2022 "…반영할예정입니다.연결포괄손익계산서")
            if len(txt) > 40 and FIN:
                txt = txt[-20:]
            if len(txt) <= 40:
                for key, name in (("BS", "재무상태표"), ("IS", "손익계산서"), ("CI", "포괄손익계산서"), ("CF", "현금흐름표")):
                    if name in txt:
                        cur = key
            continue
        trs = re.findall(r"<TR.*?</TR>", t, re.S | re.I)
        # 데이터 표 = 행 6개 이상 + 숫자 행. 기간 줄이 4개인 제목 표도 6행이다 (신한지주·삼성생명 2021, 유한양행 2015.09)
        # 비금융은 숫자 열이 하나뿐인 첫 사업연도 보고서가 있어 "숫자 있는 행 3개 이상"으로 본다 (대덕전자 2020)
        big = len(trs) >= 6 and (any(len(values(cells(r))) >= 2 for r in trs) if FIN
                                 else sum(bool(values(cells(r))) for r in trs) >= 3)
        if not cur and not out and big:
            # 재무상태표 제목이 "연결재무제표"로만 적힌 보고서 (삼성E&A 2023.09): 첫 데이터 표에
            # 자산·부채 총계 행이 있으면 재무상태표로 본다. 재무상태표는 항상 첫 표다.
            labels = {norm(c[0]) for c in (cells(r) for r in trs) if c}
            if any(TOTALS["assets"].match(x) for x in labels) and any(TOTALS["liab"].match(x) for x in labels):
                cur = "BS"
        if cur and cur not in out and big:
            rows = [cells(r) for r in trs]
            if FIN:  # 주석 번호 열("4,23,34")이 숫자로 읽혀 당기 값 자리를 차지한다 (삼성증권 2022)
                hd = next((r for r in rows[:3] if "주석" in r[1:]), None)
                # 머리행이 2줄(병합 셀)이면 데이터 행과 칸 수가 달라, 칸 수 대신 "과목 바로 다음 열"로 본다 (삼성증권 2019)
                if hd and hd.index("주석", 1) == 1:
                    rows = [r[:1] + r[2:] if len(r) > 2 else r for r in rows]
                elif hd:
                    j = hd.index("주석", 1)
                    rows = [r[:j] + r[j + 1:] if len(r) == len(hd) else r for r in rows]
            # &nbsp;도 지운다: SK스퀘어 2022는 머리행이 "누&nbsp;적"이라 누적 열을 못 알아봤다
            head = "".join(re.sub(r"<[^>]+>|&nbsp;|\s", "", r) for r in trs[:3])
            if FIN:  # 누적 열을 "누계"로 쓰는 보고서 (삼성카드 2020~2022 3분기)
                head = head.replace("누계", "누적")
            out[cur] = (unit, head, rows)
            cur = None
            continue
        txt = re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", t)
        if not big:
            for key, name in (("BS", "재무상태표"), ("IS", "손익계산서"), ("CI", "포괄손익계산서"), ("CF", "현금흐름표")):
                # 원본 XML은 제목 표에 "연결" 없이 "손익계산서…"로만 적힌 보고서가 있다 (LG 2023.09). 이미 연결 장만 잘라온 문서다.
                if "연결" + name in txt or txt.startswith(name):
                    cur = key
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
    if v is None and FIN and values(row) and i < len(row) and row[i] == "":  # "-"는 0이다 (삼성증권 2019)
        # 금융: 항목 열·합계 열이 따로인 재무상태표 (기업은행·KB금융 2019~2023). 비지배지분은 항목 열에 있다.
        # 이 때문에 전기 값을 읽을 위험이 있지만 자체 검증(총자본 = 지배 + 비지배)이 거른다.
        v = values(row)[0]
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


def parse(doc):
    if doc == OLD_NO_CONSOL:
        return {"no_consol": "old"}
    txt_only = re.sub(r"<[^>]+>|&nbsp;", " ", doc or "")
    # "해당사항 없습니다" 외에 "연결대상 종속회사가 없어 연결재무제표를 작성하지 않습니다"도 같은 경우다 (LIG 2019)
    # "해당없음"도 같다 (한전기술 2018.03)
    if (re.search(r"해당\s*(?:사항\s*이?\s*)?없", txt_only) or re.search(r"연결재무제표를?\s*작성하지\s*않", txt_only)) \
            and not re.search(r"<TABLE", doc or "", re.I):
        return {"no_consol": True}  # "2. 연결재무제표 → 해당사항 없습니다" (연결 대상 자체가 없는 기간)
    st = statements(doc)
    bs, cf = st.get("BS"), st.get("CF")
    # 손익 항목은 연결손익계산서 우선, 없거나 행이 빠지면 연결포괄손익계산서에서 찾는다
    cands = [x for x in (st.get("IS"), st.get("CI")) if x]

    def both(fn):
        for stmt in cands:
            cum = 1 if "누적" in stmt[1] else 0
            v3, vc = fn(stmt, 0), fn(stmt, cum)
            if v3 is not None or vc is not None:
                return v3, vc
        return None, None

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
        if period in reports and data.get(period, {}).get("no_consol"):
            label = ("데이터 없음(보고서에 연결재무제표 없음)", "데이터 없음(연결 미수록)") \
                if data[period]["no_consol"] == "old" else ("데이터 없음(연결재무제표 미해당)", "데이터 없음(연결 미해당)")
            for item, _ in FIN_ITEMS + FLOW_ITEMS + [("분기별 영업활동현금흐름", ""), ("분기말 지배지분 자본", "")]:
                out.append(base + [item, *label, VIEW + reports[period]])
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
            if q < 4:
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
