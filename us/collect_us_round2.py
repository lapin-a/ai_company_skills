"""미국 라운드 2 기획 2팀: collect_us_round1 규칙 그대로 + 라운드 2 추가 규칙 -> us-round2-dataset.csv

규칙은 us-round2-log.md 2절(기획 1팀)·3절(QA 보완)을 따른다.
- XOM: 2026Q2 10-Q(0000034088-26-000093)는 옛·새 CIK 공동 제출이고 수치는 새 CIK companyfacts에만 있다 → 두 companyfacts를 합친다.
- V: 상장주식수는 Class A만. B·C 전환 환산 주식수는 검산 열에 참고로만 남긴다.
- 다중 클래스 회사는 클래스별 주식수를 검산 열에 적는다.
- 영업이익 태그가 없는 회사(XOM·JNJ)는 미확인 + 사유(LLY 선례, 2026-09-19 사용자 결정).
"""

import re

import collect_us_round1 as c

c.OUT = "us-round2-dataset.csv"
c.TOP10 = [  # us-round2-log.md 2절 선정, 3절 QA 통과
    ("AMD", "AMD", "0000002488"), ("Walmart", "WMT", "0000104169"), ("Exxon Mobil", "XOM", "0000034088"),
    ("Visa", "V", "0001403161"), ("Johnson & Johnson", "JNJ", "0000200406"), ("Intel", "INTC", "0000050863"),
    ("Mastercard", "MA", "0001141391"), ("AbbVie", "ABBV", "0001551152"), ("Cisco", "CSCO", "0000858877"),
    ("Palantir", "PLTR", "0001321655"),
]
XOM_NEW = "0002115436"
A_ONLY = {"0001403161"}  # V
UNVERIFIED = {"0001141391": "B주", "0001321655": "F주"}  # 원문에서 전환비율 태그를 찾지 못한 클래스 (QA 보완 2)
NO_OPINC = {"0000034088", "0000200406"}  # XOM·JNJ

CLASSES = {}  # accn -> (기준일, {클래스: 주식수})

# --- 라운드 16 보완 (us-round16-log.md 9절) ---------------------------------
# companyfacts는 us-gaap·dei만 싣는다. 회사가 표준 태그 대신 쓴 확장 태그 중, 이름이 us-gaap
# 폐지 태그와 같아 뜻이 분명한 것만 표준 이름으로 바꿔 읽는다. (CHD 2025 10-Q)
ALIAS = {"NetCashProvidedByOperatingActivities": "NetCashProvidedByUsedInOperatingActivities"}
# 항목별 태그 계열. 보고서에 계열이 통째로 없으면 확장 태그를 의심해 원문을 한 번 열어 본다.
FAMILIES = (tuple(c.REV), ("OperatingIncomeLoss",), ("NetIncomeLoss", "ProfitLoss", c.NI_COMMON), tuple(c.OCF))
FAMILY = {t: f for f in FAMILIES for t in f}
FROM_LATER = {}  # (cik, 항목, 기간) -> 후속 보고서 accn (비교기간에서 채운 칸)
FROM_ALIAS = {}  # accn -> 원문에서 보충한 태그들 (계열 탐색으로 연 보고서)
ITEM_FAMILY = {"분기별 매출액": tuple(c.REV), "분기별 영업이익": ("OperatingIncomeLoss",),
               "분기별 당기순이익(지배)": ("NetIncomeLoss", "ProfitLoss", c.NI_COMMON),
               "분기별 영업활동현금흐름": tuple(c.OCF)}


def members(x, tag):
    """원문에서 tag 사실 → [(값, instant 또는 endDate, 클래스 멤버명 또는 '')]."""
    out, seen = [], set()
    for ctx, val in re.findall(r'<(?:[\w-]+:)?%s\b[^>]*contextRef="([^"]+)"[^>]*>\s*(-?[\d.]+)\s*<' % tag, x):
        if ctx in seen:
            continue
        seen.add(ctx)
        m = re.search(r'<(?:\w+:)?context id="%s">(.*?)</(?:\w+:)?context>' % re.escape(ctx), x, re.S)
        body = m.group(1) if m else ""
        day = re.search(r"<(?:\w+:)?(?:instant|endDate)>([^<]+)<", body)
        mem = re.findall(r">([\w-]+:[\w-]*Member)<", body)
        out.append((float(val), day.group(1) if day else None, mem[0] if mem else ""))
    return out


def instance_shares(cik, accn):
    """round1 instance_shares 대체: 클래스별 값을 CLASSES에 남기고, V는 Class A만 돌려준다."""
    got = {}
    for val, day, mem in members(c.instance(cik, accn), "EntityCommonStockSharesOutstanding"):
        got.setdefault(day, {})[mem or "(클래스 없음)"] = int(val)
    if not got:
        return None
    day = max(d for d in got if d)
    CLASSES[accn] = (day, got[day])
    if cik in A_ONLY:
        a = {k: v for k, v in got[day].items() if k.endswith("CommonClassAMember")}
        return (sum(a.values()), day, 1) if a else None
    return sum(got[day].values()), day, len(got[day])


c.instance_shares = instance_shares
_Facts = c.Facts


class Facts(_Facts):
    def __init__(self, cik):
        super().__init__(cik)
        if cik == "0000034088":
            for k, v in _Facts(XOM_NEW).idx.items():
                self.idx.setdefault(k, []).extend(v)
        self.cik = cik
        # 보고서별 사실 수. 표지(dei)만 몇 개 있고 재무 수치가 없는 보고서도 원문에서 읽어야 한다
        # (CEG 2021 10-K은 companyfacts에 5개뿐이다). 20개 미만이면 "수치 없음"으로 본다.
        cnt = {}
        for (_, a), es in self.idx.items():
            cnt[a] = cnt.get(a, 0) + len(es)
        self.known = {a for a, n in cnt.items() if n >= 20}
        self.loaded = set()  # 원문을 이미 읽은 보고서
        self.probe = {}      # 태그 계열 -> 이 회사 원문에서 그 계열을 찾았는지 (라운드 16)

    def _load(self, accn, probe=False):
        """보고서 XBRL 원문을 읽어 idx에 채운다. companyfacts에 이미 있는 사실은 다시 넣지 않는다.
        (정정본처럼 표지 몇 개만 있는 보고서에서 주식수가 두 번 더해졌다)

        probe=True는 계열 태그를 찾으러 열어본 경우다. 이때는 그 보고서 전체를 "원문에서 읽었다"고
        표시하면 안 된다 — 나머지 값은 그대로 companyfacts에서 온다. 실제로 채워 넣은 태그만 남긴다.
        """
        if accn in self.loaded:
            return
        self.loaded.add(accn)
        self.known.add(accn)
        have = {(tg, e.get("start"), e["end"]) for (tg, a), es in self.idx.items() if a == accn for e in es}
        added = set()
        for tg, e in instance_entries(self.cik, accn):
            if (tg, e.get("start"), e["end"]) not in have:
                self.idx.setdefault((tg, accn), []).append(e)
                added.add(tg)
        if probe:
            if added:
                FROM_ALIAS[accn] = added
        else:
            FROM_INSTANCE.add(accn)

    def find(self, tag, accns, end, kind, start=None):
        # companyfacts에 수치가 없는 보고서(V 2026Q2 10-Q, CEG 2021 10-K)는 XBRL 원문에서 읽는다
        for a in accns:
            if a not in self.known:
                self._load(a)
        got = super().find(tag, accns, end, kind, start)
        if got[0] is not None:
            return got
        # 계열 태그가 보고서에 통째로 없으면 회사 확장 태그를 의심해 원문을 열어 본다 (CHD 2025 10-Q).
        # 그 회사 원문에도 없으면(= 정말 미공시) 같은 계열로는 다시 열지 않는다 — 내려받기를 1회로 묶는다.
        fam = FAMILY.get(tag)
        if fam is None or self.probe.get(fam) is False:
            return got
        miss = [a for a in accns if a not in self.loaded and not any((ft, a) in self.idx for ft in fam)]
        if not miss:
            return got
        for a in miss:
            self._load(a, probe=True)
        self.probe[fam] = any((ft, a) in self.idx for ft in fam for a in miss)
        return super().find(tag, accns, end, kind, start)


FROM_INSTANCE = set()


def _std(prefix, local):
    """원문 태그 → 표준 태그 이름. us-gaap·dei는 그대로, 회사 확장 태그는 ALIAS에 있을 때만."""
    if prefix in ("us-gaap", "dei"):
        return local
    return ALIAS.get(local)


def instance_entries(cik, accn):
    """XBRL 원문 → [(태그, {end, start?, val, accn})] — us-gaap·dei와 ALIAS 확장 태그, 차원 없는 숫자 사실만."""
    x, ctxs, out = c.instance(cik, accn), {}, []
    # 속성이 여러 줄에 걸쳐 쓰인 보고서도 있다 (CEG 2021 10-K)
    for cid, body in re.findall(r'<(?:\w+:)?context\s[^>]*?id="([^"]+)"[^>]*>(.*?)</(?:\w+:)?context>', x, re.S):
        if "explicitMember" in body or "typedMember" in body:
            continue
        p = dict(re.findall(r"<(?:\w+:)?(startDate|endDate|instant)>([^<]+)<", body))
        ctxs[cid] = {"end": p.get("endDate") or p.get("instant"), **({"start": p["startDate"]} if "startDate" in p else {})}
    seen = set()
    for pre, tg, cid, val in re.findall(r'<([\w.-]+):(\w+)\b[^>]*contextRef="([^"]+)"[^>]*>\s*(-?[\d.]+)\s*<', x):
        tg = _std(pre, tg)
        if tg and cid in ctxs and (tg, cid) not in seen:
            seen.add((tg, cid))
            out.append((tg, {**ctxs[cid], "val": int(float(val)), "accn": accn}))
    # 인라인 XBRL(ix:nonFraction) 보고서: 수치가 본문 HTML 안에 있다 (ABNB 2020 10-K, CEG 2021 10-K)
    for attrs, body in re.findall(r"<ix:nonFraction([^>]*)>(.*?)</ix:nonFraction>", x, re.S):
        a = dict(re.findall(r'([\w:]+)="([^"]*)"', attrs))
        name, cid = a.get("name", ""), a.get("contextRef")
        tg = _std(*name.split(":", 1)) if ":" in name else None
        if cid not in ctxs or not tg:
            continue
        if (tg, cid) in seen:
            continue
        txt = re.sub(r"<[^>]+>|[,\s]", "", body)
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", txt):
            continue
        val = float(txt) * 10 ** int(a.get("scale", 0) or 0)
        if a.get("sign") == "-":
            val = -val
        seen.add((tg, cid))
        out.append((tg, {**ctxs[cid], "val": int(val), "accn": accn}))
    return out


c.Facts = Facts


def v_converted(cik, accn):
    """V 전환 환산 주식수(참고): Σ 클래스 주식수 × 같은 보고서의 가장 최근 전환비율(A는 1)."""
    day, cls = CLASSES[accn]
    rates = {}
    for val, d, mem in members(c.instance(cik, accn), r"v:CommonStockConversionRate"):
        if val and d and (mem not in rates or d > rates[mem][1]):
            rates[mem] = (val, d)
    total, parts = 0, []
    for mem, n in cls.items():
        if mem.endswith("CommonClassAMember"):
            total += n
            continue
        if mem not in rates:
            return "전환비율 원문 없음(%s) → 환산 미확인" % mem.split(":")[-1]
        total += n * rates[mem][0]
        parts.append("%s %d×%g(%s)" % (mem.split(":")[-1], n, rates[mem][0], rates[mem][1]))
    return "참고: 전환 환산 %d주 = A %d + %s" % (round(total), [n for m, n in cls.items() if m.endswith("CommonClassAMember")][0],
                                              " + ".join(parts))


def fix_rows(rows):
    """라운드 2 주석: 클래스별 주식수·V Class A만·영업이익 미공시 사유."""
    market = ("분기말 종가", "분기말 상장주식수", "분기말 시가총액")
    # 회사별 최초 보고 분기 = 기준일이 있는 가장 이른 행 (그 앞은 보고서 자체가 없다)
    first = {}
    for r in rows:
        if r[3]:
            first[r[1]] = min(first.get(r[1], r[2]), r[2])
    for r in rows:
        cik = next(k for _, t, k in c.TOP10 if t == r[1])
        if r[1] == "PLTR" and r[8] == "해당 라벨 보고서 없음" and r[2] < "2020Q3":  # 2절 추가 규칙 5 (라운드 2 원문 표기 유지)
            if r[4] in market:
                r[5:9] = ["데이터 없음(API 최초 거래일 2020-09-30 이전)", "", "데이터 없음(상장 전)",
                          "https://query1.finance.yahoo.com/v8/finance/chart/PLTR (firstTradeDate 2020-09-30)"]
            else:
                r[5:9] = ["데이터 없음(최초 보고기간 이전)", "USD", "데이터 없음(최초 보고기간 전)",
                          "https://data.sec.gov/submissions/CIK0001321655.json (최초 10-Q 보고기간 2020-09-30)"]
            continue
        if r[8] == "해당 라벨 보고서 없음" and r[2] < first.get(r[1], "9999Q9"):
            # 상장·설립 전이라 그 분기를 당기로 한 보고서가 없다 (PLTR·APP·ABNB)
            if r[4] in market:
                r[5:9] = ["데이터 없음(상장 전)", "", "데이터 없음(상장 전)",
                          "https://query1.finance.yahoo.com/v8/finance/chart/%s (최초 거래일 이전)" % r[1]]
            else:
                r[5:9] = ["데이터 없음(최초 보고기간 이전)", "USD", "데이터 없음(최초 보고기간 전)",
                          "https://data.sec.gov/submissions/CIK%s.json (최초 보고기간 %s)" % (cik, first.get(r[1]))]
            continue
        if any(a.replace("-", "") in r[8] for a in FROM_INSTANCE) and r[5] != "미확인" and r[4] not in market[:1]:
            r[9] = (r[9] + " ; " if r[9] else "") + "값은 XBRL 원문(companyfacts 미반영 보고서)"
        # 계열 탐색으로 연 보고서는 그 계열 항목만 원문에서 왔다 — 나머지 행에는 주석을 달지 않는다
        alias = {t for a, tags in FROM_ALIAS.items() if a.replace("-", "") in r[8] for t in tags}
        hit = alias & set(ITEM_FAMILY.get(r[4], ()))
        if hit and r[5] != "미확인":
            r[9] = (r[9] + " ; " if r[9] else "") + "값은 XBRL 원문(회사 확장 태그 → %s)" % ", ".join(sorted(hit))
        if r[4] == "분기별 영업이익" and r[5] == "미확인" and cik in NO_OPINC:
            r[8] = "SEC companyfacts CIK%s: 해당 보고서에 OperatingIncomeLoss 태그 없음(영업이익 미공시) ; %s" % (cik, r[8])
        if r[4] not in ("분기말 상장주식수", "분기말 시가총액") or r[5] == "미확인":
            continue
        accn = next((a for a in CLASSES if a.replace("-", "") in r[8]), None)
        if not accn:
            continue
        day, cls = CLASSES[accn]
        detail = "클래스별(%s): " % day + ", ".join("%s %d" % (m.split(":")[-1], n) for m, n in cls.items())
        if cik in A_ONLY:
            r[8] += " ; Class A만, B·C 전환분 미포함"
            if r[4] == "분기말 상장주식수":
                r[9] = "Class A만 ; " + detail + " ; " + v_converted(cik, accn)
        elif r[4] == "분기말 상장주식수" and len(cls) > 1:
            r[9] += " ; " + detail
            if cik in UNVERIFIED:
                r[8] += " ; %s 전환비율 원문 미확인, 합산에 포함" % UNVERIFIED[cik]
    fill_from_later(rows)


# 그 분기 보고서에서 값을 못 얻은 손익 항목만 대상. 4분기는 `연간 − 9개월누적`이라 제외한다.
LATER_TAGS = {"분기별 매출액": c.REV, "분기별 영업이익": ["OperatingIncomeLoss"],
              "분기별 당기순이익(지배)": ["NetIncomeLoss"]}


def fill_from_later(rows):
    """미확인으로 남은 손익 칸을, 같은 기간이 비교기간으로 실린 다른 보고서에서 채운다 (라운드 16 PHM).

    PHM 2021Q1처럼 그 분기 10-Q가 연결 총계를 차원(세그먼트) 붙여서만 태그하면 companyfacts에 안 실린다.
    재작성 영향을 줄이려고 **가장 먼저 낸** 보고서를 쓴다. 값구분으로 원보고서 공시값과 구분한다.
    (ABNB 2020Q4 선례, 라운드 6 — 그때는 회사별 특례였고 여기서 일반 규칙으로 올렸다.)
    """
    fx_cache = {}
    for r in rows:
        if r[5] != "미확인" or r[4] not in LATER_TAGS or not r[3] or r[2].endswith("Q4"):
            continue
        cik = next(k for _, t, k in c.TOP10 if t == r[1])
        if cik not in fx_cache:
            fx_cache[cik] = c.Facts(cik)
        fx = fx_cache[cik]
        for tag in LATER_TAGS[r[4]]:
            hits = [(e.get("filed", ""), e["accn"], e["val"]) for (tg, _), es in fx.idx.items() if tg == tag
                    for e in es if e["end"] == r[3] and 70 <= c.days(e) <= 118]
            if hits:
                filed, accn, val = min(hits)
                r[5:10] = [val, "USD", "공시(후속 보고서 비교기간)", c.link(cik, accn),
                           "%s ; 그 분기 보고서에 연결 총계가 없어 %s 제출본의 비교기간에서 읽었다" % (tag, filed[:10])]
                FROM_LATER[(cik, r[4], r[2])] = accn
                break


c.ROW_FIX = fix_rows

if __name__ == "__main__":
    c.main()
