"""재작성 반영 (대표 결정 2026-09-21): 나중 보고서의 비교기간 열이 원 공시와 다르면 나중 값을 쓰고, 원 공시값은 기록으로 남긴다.

DART 보고서의 비교기간 열:
- 손익: 분기·반기보고서는 [당기 3개월, 당기 누적, 전기 3개월, 전기 누적], 1분기·사업보고서는 [당기, 전기]
  → 1년 전 같은 분기의 3개월 값과 누적값.
- 현금흐름: [당기 누적, 전기 누적] → 1년 전 같은 분기의 누적값.
- 재무상태표: [당기말, 전기말(, 전전기말)] → 직전 사업연도 말(12월) 값.
열 수가 이 모양과 정확히 맞는 행만 쓴다. 빈 칸이 섞여 열이 밀렸을 수 있는 행은 원 공시를 그대로 둔다.
재무상태표는 자산·부채·총자본·지배지분 자본을 한 묶음으로 바꾸고, 묶음이 자산 = 부채 + 총자본을 통과할 때만 쓴다.
"""

import copy

import collect_round1 as cr

LOG_HEAD = ["기업", "종목코드", "기간", "기준일", "항목", "구분", "원 공시값", "원 값구분", "원 출처", "나중 보고서 값", "나중 보고서 출처"]

FLOW = {"rev": cr.pick_rev, "op": lambda s, c: cr.pick(s, lambda x: bool(cr.OP.match(x)), c), "ni": cr.pick_parent_ni}


def width(fn, stmt):
    """fn(stmt, col)이 값을 돌려주는 열 수."""
    n = 0
    while n < 6 and fn(stmt, n) is not None:
        n += 1
    return n


def prior(doc, period):
    """보고서 한 건의 비교기간 값 → {(비교기간, 키): 값}. period는 이 보고서의 당기 "YYYY.MM"."""
    if not doc:
        return {}
    st = cr.statements(doc)
    y, mm = int(period[:4]), period[5:]
    last = "%d.%s" % (y - 1, mm)
    # 중단영업 손익이 있는 보고서의 손익·현금흐름 비교열은 재분류일 수 있다 (반영 안 함, coverage-log 5번)
    out = {"_disc": any(r and cr.norm(r[0]).startswith("중단영업") and cr.values(r)
                        for s in (st.get("IS"), st.get("CI")) if s for r in s[2])}
    for stmt in (x for x in (st.get("IS"), st.get("CI")) if x):
        cum = "누적" in stmt[1]
        for k, fn in FLOW.items():
            if (last, k + "3") in out or (last, k + "C") in out:
                continue
            w = width(fn, stmt)
            if cum and w == 4:
                out[(last, k + "3")], out[(last, k + "C")] = fn(stmt, 2), fn(stmt, 3)
            elif not cum and w == 2 and mm in ("03", "12"):  # 1분기·사업보고서: 3개월 = 누적
                out[(last, k + "3")] = out[(last, k + "C")] = fn(stmt, 1)
    cf = st.get("CF")
    ocf = lambda s, c: cr.pick(s, lambda x: x.startswith("영업활동") and "현금흐름" in x, c)
    if cf and width(ocf, cf) == 2:
        out[(last, "ocfC")] = ocf(cf, 1)
    bs = st.get("BS")
    if bs:
        ye = "%d.12" % (y - 1)
        parent = lambda s, c: cr.pick(s, lambda x: "지배" in x and "비지배" not in x, c)
        got = {k: cr.pick_total(bs, k, 1) for k in ("assets", "liab", "equity")}
        got["parent_eq"] = parent(bs, 1)
        ok = all(v is not None for v in got.values()) and width(parent, bs) in (2, 3) \
            and all(width(lambda s, c, k=k: cr.pick_total(s, k, c), bs) in (2, 3) for k in ("assets", "liab", "equity")) \
            and cr.close(got["assets"], got["liab"] + got["equity"]) and not cr.held_for_sale_split(bs)[2]
        if ok:
            got["nci"] = got["equity"] - got["parent_eq"]
            out.update({(ye, k): v for k, v in got.items()})
    return out


FLOW_KEYS = {"rev3", "revC", "op3", "opC", "ni3", "niC", "ocfC"}


def unit_only(old, new):
    """나중 보고서가 단위만 거칠게 쓴 경우(천원 → 백만원): 재작성으로 보지 않는다."""
    scale = 10 ** (len(str(abs(new))) - len(str(abs(new)).rstrip("0"))) if new else 1
    return scale >= 1000 and abs(new - old) < scale


def apply(data, reports, docs_prior, reclass=False):
    """data를 제자리에서 고친다. docs_prior: {보고기간: prior() 결과}.
    reclass=False면 중단영업이 있는 보고서의 손익·현금흐름 비교값은 쓰지 않는다."""
    for src in sorted(docs_prior, key=lambda p: reports[p]):  # 나중 접수본이 이긴다
        disc = docs_prior[src].get("_disc")
        for pk, val in docs_prior[src].items():
            if pk == "_disc":
                continue
            period, key = pk
            d = data.get(period)
            if period not in reports or not d or d.get("no_consol") or val is None:
                continue
            if disc and key in FLOW_KEYS and not reclass:
                continue
            old = d.get(key)
            if old is None or cr.close(old, val) or unit_only(old, val):
                continue
            d[key] = val
            d.setdefault("_restated", {})[key] = reports[src]


def rows(corp, code, reports, data, pri, window):
    """재무 행을 원 공시 · 재작성 반영 · 재분류까지 반영, 세 벌로 만들어 대조한다.
    반환: (행, 검증실패, 기록행). 재작성 반영 칸은 값구분에 "(재작성 반영)"을 붙이고,
    재작성값으로 자체 검증을 못 통과한 칸은 원 공시를 둔다. 재분류로만 달라지는 칸은 기록만 한다."""
    def build(reclass):
        d = copy.deepcopy(data)
        if reclass is not None:
            apply(d, reports, pri, reclass)
        return cr.build_fin_rows(corp, code, reports, d, window) + (d,)

    orig, ofails, _ = build(None)
    new, fails, dn = build(False)
    full, _, df = build(True)
    period_of = {r: p for p, r in reports.items()}
    num = lambda v: not isinstance(v, str)

    def sources(row, d):
        ps = [period_of[r] for r in period_of if r in row[7]]
        return " ; ".join(cr.VIEW + r for r in sorted({s for p in ps for s in d.get(p, {}).get("_restated", {}).values()}))

    log = []
    for i, (o, n, f) in enumerate(zip(orig, new, full)):
        if not num(o[5]):
            continue
        if not num(n[5]):  # 재작성값으로 검증 실패 → 원 공시 유지
            new[i] = list(o)
            log.append(o[:5] + ["재작성 검증 실패(원 공시 유지)", o[5], o[6], o[7], "", sources(n, dn)])
        elif n[5] != o[5]:
            src = sources(n, dn)
            log.append(n[:5] + ["재작성 반영", o[5], o[6], o[7], n[5], src])
            n[6] += "(재작성 반영)"
            n[7] += " ; 재작성 출처: " + src
        elif num(f[5]) and f[5] != o[5]:
            log.append(o[:5] + ["재분류(미반영)", o[5], o[6], o[7], f[5], sources(f, df)])
    # 검증 실패 목록은 최종 행 기준 (원 공시로 되돌린 칸은 빼고, 원 공시에서 실패했던 칸은 넣는다)
    left = {r[2] for r in new if r[5] == "미확인"}
    fails = {p: v for p, v in {**ofails, **fails}.items() if "%sQ%d" % (p[:4], int(p[5:]) // 3) in left}
    return new, fails, log
