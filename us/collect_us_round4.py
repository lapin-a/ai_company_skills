"""미국 라운드 4 기획 2팀: TOP 20 수집 -> us-round4-dataset.csv

라운드 3과 같은 구성이다(collect_us_round1 + round2 보충 + round3 라벨 보완).
더한 것 하나: MRVL은 2021년 지주회사 재편으로 CIK가 바뀌었다. 2019Q1~2020Q4는 옛 CIK에서 가져온다
(라운드 2 XOM과 같은 처리지만, 접수번호가 달라서 출처 링크도 보고서별 CIK로 만든다).
us-round4-log.md 2·3절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙을 그대로 쓴다

c.OUT = "us-round4-dataset.csv"
c.TOP10 = [
    ("KLA", "KLAC", "0000319201"), ("IBM", "IBM", "0000051143"), ("Marvell Technology", "MRVL", "0001835632"),
    ("Linde", "LIN", "0001707925"), ("Amgen", "AMGN", "0000318154"), ("Verizon", "VZ", "0000732712"),
    ("Salesforce", "CRM", "0001108524"), ("Seagate", "STX", "0001137789"), ("Qualcomm", "QCOM", "0000804328"),
    ("Gilead Sciences", "GILD", "0000882095"), ("Deere", "DE", "0000315189"), ("Analog Devices", "ADI", "0000006281"),
    ("Abbott Laboratories", "ABT", "0000001800"), ("Walt Disney", "DIS", "0001744489"), ("PepsiCo", "PEP", "0000077476"),
    ("McDonald's", "MCD", "0000063908"), ("AT&T", "T", "0000732717"), ("NextEra Energy", "NEE", "0000753308"),
    ("Union Pacific", "UNP", "0000100885"), ("Eaton", "ETN", "0001551182"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000051143", "0000319201", "0001551182", "0000315189"}  # IBM·KLAC·ETN·DE
c.ROW_FIX = r2.fix_rows

MRVL_NEW, MRVL_OLD = "0001835632", "0001058057"  # Marvell Technology, Inc. / Marvell Technology Group Ltd
ACC_CIK = {}  # 접수번호 -> 그 보고서를 낸 CIK (출처 링크·원문 경로용)
_reports, _Facts, _link, _instance = c.reports, r3.c.Facts, c.link, c.instance


def reports(cik):
    reps, forms = _reports(cik)
    if cik == MRVL_NEW:
        old, oforms = _reports(MRVL_OLD)
        for end, accns in old.items():
            if end < min(reps):  # 재편 전 분기만 가져온다
                reps[end] = accns
                forms.update({a: oforms[a] for a in accns})
                ACC_CIK.update({a: MRVL_OLD for a in accns})
    return reps, forms


class Facts(_Facts):
    def __init__(self, cik):
        super().__init__(cik)
        if cik == MRVL_NEW:
            for k, v in _Facts(MRVL_OLD).idx.items():
                self.idx.setdefault(k, []).extend(v)


c.reports = reports
c.Facts = Facts
c.link = lambda cik, accn: _link(ACC_CIK.get(accn, cik), accn)
c.instance = lambda cik, accn: _instance(ACC_CIK.get(accn, cik), accn)

if __name__ == "__main__":
    c.main()
