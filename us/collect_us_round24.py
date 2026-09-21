"""미국 라운드 24 기획 2팀: TOP 5 수집 -> us-round24-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round24-dataset.csv"
c.TOP10 = [
    ("Revvity", "RVTY", "0000031791"),
    ("APA", "APA", "0001841666"),
    ("Charter Communications", "CHTR", "0001091667"),
    ("Akamai", "AKAM", "0001086222"),
    ("PTC", "PTC", "0000857005"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 영업이익 태그 모두 정상
c.ROW_FIX = r2.fix_rows

# APA는 2021-03 지주회사 재편으로 CIK가 바뀌었다(옛 Apache Corp 0000006769). 라운드 4 MRVL과 같은 처리.
NEW, OLD = "0001841666", "0000006769"
ACC_CIK = {}
_reports, _Facts, _link, _instance = c.reports, r3.c.Facts, c.link, c.instance


def reports(cik):
    reps, forms = _reports(cik)
    if cik == NEW:
        old, oforms = _reports(OLD)
        for end, accns in old.items():
            if end < min(reps):  # 재편 전 분기만 가져온다
                reps[end] = accns
                forms.update({a: oforms[a] for a in accns})
                ACC_CIK.update({a: OLD for a in accns})
    return reps, forms


class Facts(_Facts):
    def __init__(self, cik):
        super().__init__(cik)
        if cik == NEW:
            # MRVL과 달리 Apache는 재편 뒤에도 자체 보고서를 낸다. 재편 전 보고서의 사실만 합친다.
            for k, v in _Facts(OLD).idx.items():
                if k[1] in ACC_CIK:
                    self.idx.setdefault(k, []).extend(v)


c.reports = reports
c.Facts = Facts
c.link = lambda cik, accn: _link(ACC_CIK.get(accn, cik), accn)
c.instance = lambda cik, accn: _instance(ACC_CIK.get(accn, cik), accn)

if __name__ == "__main__":
    c.main()
