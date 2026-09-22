"""미국 라운드 3 기획 2팀: TOP 20 수집 -> us-round3-dataset.csv

collect_us_round1(수집 본체) + collect_us_round2(원문 XBRL 보충·클래스 주식수·주석)를 재사용한다.
라운드 3에서 더한 것은 분기 라벨 보완 하나다(대표 결정 2026-09-20, us-round3-log.md 3절).
  한 회사의 분기 말일들이 "가장 가까운 달력 분기말" 규칙으로 서로 다른 라벨을 만들지 못하면(COST 16주 분기),
  그 회사만 첫 분기 라벨을 기준으로 회계분기 순서대로 연속된 달력 분기에 배정한다.
"""

from datetime import date

import collect_us_round1 as c
import collect_us_round2 as r2

c.OUT = "us-round3-dataset.csv"
c.TOP10 = [  # us-round3-log.md 2절 선정, 3절 QA 통과(COST는 라벨 보완 후 포함)
    ("Oracle", "ORCL", "0001341439"), ("Chevron", "CVX", "0000093410"), ("Costco", "COST", "0000909832"),
    ("Coca-Cola", "KO", "0000021344"), ("Caterpillar", "CAT", "0000018230"), ("Merck", "MRK", "0000310158"),
    ("Dell Technologies", "DELL", "0001571996"), ("Lam Research", "LRCX", "0000707549"),
    ("Applied Materials", "AMAT", "0000006951"), ("Procter & Gamble", "PG", "0000080424"),
    ("GE Aerospace", "GE", "0000040545"), ("Home Depot", "HD", "0000354950"), ("Netflix", "NFLX", "0001065280"),
    ("Palo Alto Networks", "PANW", "0001327567"), ("Philip Morris Intl", "PM", "0001413329"),
    ("RTX", "RTX", "0000101829"), ("Arista Networks", "ANET", "0001596532"),
    ("Texas Instruments", "TXN", "0000097476"), ("CrowdStrike", "CRWD", "0001535527"),
    ("Thermo Fisher", "TMO", "0000097745"),
]
r2.c = c
r2.A_ONLY = set()            # DELL 전환비율 1.0 확인(3절) → 클래스 합
r2.UNVERIFIED = {}           # 전환비율 미확인 클래스 없음
r2.NO_OPINC = {"0000093410", "0000310158", "0000040545"}  # CVX·MRK·GE (LLY 선례)
c.ROW_FIX = r2.fix_rows

_label = c.label
SEQ = {}  # 분기 말일 -> 보완 라벨


def next_label(lab):
    y, q = int(lab[:4]), int(lab[-1])
    return "%dQ%d" % (y + 1, 1) if q == 4 else "%dQ%d" % (y, q + 1)


def prev_label(lab):
    y, q = int(lab[:4]), int(lab[-1])
    return "%dQ4" % (y - 1) if q == 1 else "%dQ%d" % (y, q - 1)


def seq_labels(ends):
    """마지막 말일을 기존 규칙으로 잡고, 거꾸로 이웃 말일 간격(약 91일 = 1분기)만큼 당겨 배정한다.
    16주·12주 분기도 1분기로 센다(COST). 처음에는 첫 말일 기준으로 앞에서부터 매겼는데, 2010 창에서 앞쪽의
    보고서 공백·겹침이 최근 라벨까지 밀어서(T·SWKS·TRGP·OKE) 마지막 말일 기준으로 바꿨다(2026-09-22).
    최신 보고서가 최근 것인데 수집 창 마지막 분기를 못 채우면 한 분기 당긴다(AZO)."""
    ends = sorted(ends)
    if not ends:
        return {}
    lab = _label(ends[-1])
    if ends[-1] >= "2026-04-15" and lab < c.WINDOW[-1]:
        lab = next_label(lab)
    out = {ends[-1]: lab}
    for prev, cur in zip(reversed(ends[:-1]), reversed(ends[1:])):
        gap = (date.fromisoformat(cur) - date.fromisoformat(prev)).days
        for _ in range(max(1, round(gap / 91.3))):
            lab = prev_label(lab)
        out[prev] = lab
    return out


def label(end):
    return SEQ.get(end) or _label(end)


c.label = label
r2.c.label = label
_reports = c.reports


def reports(cik):
    reps, forms = _reports(cik)
    SEQ.clear()  # 회사마다 새로 판단한다 (main은 한 번에 한 회사씩 처리한다)
    ends = sorted(reps)
    labs = [_label(e) for e in ends]
    why = None
    if len(set(labs)) < len(labs):  # 라벨 겹침 (COST·NOW)
        why = "겹치던 라벨 %d개" % (len(labs) - len(set(labs)))
    elif ends and labs and labs[-1] < c.WINDOW[-1] and ends[-1] >= "2026-04-15":
        # 최신 보고서가 수집 창 마지막 분기를 채우지 못하고 한 분기 앞으로 붙는 회사 (AZO: 5월 초 종료 → 2026Q1)
        # 대표 결정 (가), 2026-09-20: 이 경우도 회계분기 순서대로 배정한다.
        why = "최신 라벨 %s가 창 끝(%s)보다 앞섬" % (labs[-1], c.WINDOW[-1])
    if why:
        SEQ.update(seq_labels(ends))
        print("라벨 보완: CIK %s, %s → 순차 배정" % (cik, why))
    return reps, forms


c.reports = reports

if __name__ == "__main__":
    c.main()
