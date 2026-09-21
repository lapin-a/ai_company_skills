"""라운드 11~14 기획 2팀: 국내 금융회사 19곳 (금융 항목 세트, round3-log.md 결정 2) -> roundN-dataset.csv

실행: python kr/collect_fin.py 11   (라운드 번호 11~14)
재무 7항목 + 순이자이익·순수수료이익 = 10항목, 시장 3항목. 매출액 자리는 "영업수익" 줄만 쓴다.
회사가 그 줄을 싣지 않은 보고서는 "데이터 없음(항목 미공시)"로 둔다 (계산해서 채우지 않는다).
파서·재작성 반영·시장데이터는 collect_round1/2·restate를 그대로 쓰고, cr.FIN으로 금융 보정만 켠다.
"""

import csv
import json
import re
import sys
import time

import collect_market_round1 as cm
import collect_round1 as cr
import collect_round2 as c2
import restate

ROUNDS = {  # 대형주 100 금융 19곳(카카오뱅크 제외 18곳), 시가총액 순 5곳씩 (대표 지시 2026-09-21)
    11: [("KB금융", "105560", "00688996"), ("삼성생명", "032830", "00126256"), ("신한지주", "055550", "00382199"),
         ("하나금융지주", "086790", "00547583"), ("삼성화재", "000810", "00139214")],
    12: [("우리금융지주", "316140", "01350869"), ("메리츠금융지주", "138040", "00860332"), ("미래에셋증권", "006800", "00111722"),
         ("기업은행", "024110", "00149646"), ("DB손해보험", "005830", "00159102")],
    # 카카오뱅크(323410)는 전 기간 연결재무제표 미해당이라 커버리지에서 뺐다 (대표 결정 2026-09-21, round11-14-log.md 9절)
    13: [("한국금융지주", "071050", "00432102"), ("NH투자증권", "005940", "00120182"),
         ("삼성증권", "016360", "00104856"), ("키움증권", "039490", "00296290")],
    14: [("JB금융지주", "175330", "00980122"), ("카카오페이", "377300", "01244601"), ("삼성카드", "029780", "00126292"),
         ("한화생명", "088350", "00113058")],
}
NII = re.compile(r"^순이자(이익|손익|수익)(\((비용|손실)\))?$")
FEE = re.compile(r"^순수수료(이익|손익|수익)(\((비용|손실)\))?$")
FIN_PICK = {
    "rev": lambda s, c: cr.pick(s, lambda x: x == "영업수익", c),
    "nii": lambda s, c: cr.pick(s, lambda x: bool(NII.match(x)), c),
    "fee": lambda s, c: cr.pick(s, lambda x: bool(FEE.match(x)), c),
}
ITEM_KEY = {"분기별 영업수익": "rev", "분기별 순이자이익": "nii", "분기별 순수수료이익": "fee"}
ABSENT = "데이터 없음(항목 미공시)"

cr.FIN = True
cr.FLOW_ITEMS = [("분기별 영업수익", "rev"), ("분기별 영업이익", "op"), ("분기별 당기순이익(지배)", "ni"),
                 ("분기별 순이자이익", "nii"), ("분기별 순수수료이익", "fee")]
restate.FLOW = {**restate.FLOW, **FIN_PICK}
restate.FLOW_KEYS |= {"nii3", "niiC", "fee3", "feeC"}
_parse = cr.parse


def parse(doc):
    d = _parse(doc)
    if d.get("no_consol") or not doc:
        return d
    st = cr.statements(doc)
    cands = [x for x in (st.get("IS"), st.get("CI")) if x]
    d["_absent"] = set()
    # 3개월 열 없이 누적만 싣는 분기·반기보고서 (신한지주 2019~2023): 3개월 값은 누적 차감으로 만든다 (fill_cum_only)
    d["_cum_only"] = bool(cands) and "3개월" not in cands[0][1] and "누적" not in cands[0][1]
    for k, fn in FIN_PICK.items():
        d[k + "3"] = d[k + "C"] = None
        for stmt in cands:
            cum = 1 if "누적" in stmt[1] else 0
            v3, vc = fn(stmt, 0), fn(stmt, cum)
            if v3 is not None or vc is not None:
                d[k + "3"], d[k + "C"] = v3, vc
                break
        else:
            if cands:  # 손익표는 읽었는데 그 줄이 없다 = 회사가 싣지 않았다
                d["_absent"].add(k)
    return d


cr.parse = parse


FLOWS = ("rev", "op", "ni", "nii", "fee")


def fill_cum_only(data, reports):
    """누적만 있는 2·3분기 보고서: 누적은 kC로, 3개월은 당분기 누적 − 직전 분기 누적으로 채운다. {기간: 직전 기간}"""
    done = {}
    for p, d in data.items():
        q = int(p[5:]) // 3
        prev = "%s.%02d" % (p[:4], (q - 1) * 3)
        if not d.get("_cum_only") or q not in (2, 3) or prev not in data:
            continue
        for k in FLOWS:
            d[k + "C"] = d.get(k + "3")  # 누적 열이 없다고 본 파서가 col 0(누적)을 3개월 자리에 넣었다
            a, b = d[k + "C"], data[prev].get(k + "C")
            d[k + "3"] = a - b if None not in (a, b) else None
        done[p] = prev
    return done


def mark_calc(fin, done, reports):
    for r in fin:
        p = "%s.%02d" % (r[2][:4], int(r[2][-1]) * 3)
        if p in done and r[4] in dict(cr.FLOW_ITEMS) and r[6].startswith("공시"):
            r[6] = r[6].replace("공시", "계산(누적차감)", 1)
            r[7] += " ; " + cr.VIEW + reports[done[p]]


def mark_absent(fin, data):
    """미확인 칸 중 그 기간(4분기 계산이면 3분기 보고서 포함) 보고서에 해당 줄이 없는 칸을 '항목 미공시'로 바꾼다."""
    n = 0
    for r in fin:
        k = ITEM_KEY.get(r[4])
        if r[5] != "미확인" or not k:
            continue
        y, q = r[2][:4], int(r[2][-1])
        ps = ["%s.%02d" % (y, q * 3)] + (["%s.09" % y] if q == 4 else [])
        if any(k in data.get(p, {}).get("_absent", ()) for p in ps):
            r[5], r[6] = ABSENT, "데이터 없음(항목 미공시)"
            n += 1
    return n


def main(rnd):
    out = "round%d-dataset.csv" % rnd
    dkey, pkey = c2.dart_key(), cm.service_key()
    per = len(cr.FIN_ITEMS) + len(cr.FLOW_ITEMS) + 2  # 재무 10행
    all_rows, summary, relog = [], [], []
    for corp, code, cc in ROUNDS[rnd]:
        t0 = time.time()
        reports = c2.pick_reports(dkey, cc)
        got = {p: c2.fetch_parse(r, p) for p, r in sorted(reports.items())}
        data = {p: v[0] for p, v in got.items()}
        done = fill_cum_only(data, reports)
        fin, fails, log = restate.rows(corp, code, reports, data, {p: v[1] for p, v in got.items()}, c2.WINDOW)
        absent = mark_absent(fin, data)
        mark_calc(fin, done, reports)
        relog += log
        first = c2.first_trade_date(pkey, code)
        mkt, mbad = c2.market_rows(pkey, corp, code, first)
        for i, _ in enumerate(c2.WINDOW):
            all_rows += [r + ["금융"] for r in fin[i * per:(i + 1) * per] + mkt[i * 3:(i + 1) * 3]]
        kinds = {}
        for r in fin + mkt:
            kinds[r[6]] = kinds.get(r[6], 0) + 1
        summary.append({"기업": corp, "항목세트": "금융", "보고서": len(reports), "값구분": kinds, "재무검증실패": fails,
                        "시총검증실패": mbad, "API최초거래일": first.isoformat(), "항목미공시": absent})
        print("%s | 보고서 %d | %s | 재무검증실패 %s | 시총검증실패 %s | %.0fs" % (
            corp, len(reports), kinds, fails or "없음", mbad or "없음", time.time() - t0), flush=True)

    with open(c2.OUTDIR + out, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([c2.HEAD + ["항목세트"]] + all_rows)
    with open(c2.OUTDIR + out.replace("-dataset.csv", "-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(c2.OUTDIR + out.replace("-dataset.csv", "-restated.csv"), "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([restate.LOG_HEAD] + relog)
    print("재작성 기록:", {k: sum(r[5] == k for r in relog) for k in sorted({r[5] for r in relog})})
    print("rows:", len(all_rows), "| 빈칸:", sum(v == "" for r in all_rows for v in map(str, r)))


if __name__ == "__main__":
    main(int(sys.argv[1]))
