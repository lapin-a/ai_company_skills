"""미국 라운드 21 기획 2팀: TOP 5 수집 -> us-round21-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round21-dataset.csv"
c.TOP10 = [
    ("Zimmer Biomet", "ZBH", "0001136869"),
    ("C.H. Robinson", "CHRW", "0001043277"),
    ("Gen Digital", "GEN", "0000849399"),
    ("Genuine Parts", "GPC", "0000040987"),
    ("DuPont", "DD", "0001666700"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0001666700", "0000040987"}  # DD: 태그 없음 · GPC: 태그 2018년까지 (LLY·BIIB 선례)
c.ROW_FIX = r2.fix_rows

# GPC: SEC 메타 reportDate가 2019-08-09로 실린 정정 보고서 2건(2019Q1 10-Q/A · FY2018 10-K/A)은
# XBRL 없이 표지·증빙만 다시 낸 것이다. 원문 교정(fix_report_dates)이 기간을 못 읽어 가짜 분기가 생기고,
# 라운드 3 순차 배정이 그 뒤 라벨을 전부 한 분기씩 밀었다. 이 라운드에서만 XBRL 없는 정정본을 뺀다.
_fix = c.fix_report_dates


def fix_report_dates(cik, out):
    _fix(cik, out)
    if cik == "0000040987":
        for rd in [rd for rd, v in out.items() if all(f.endswith("/A") for _, _, f in v)
                   and not any(c.instance(cik, a) for _, a, _ in v)]:
            print("정정본 제외: CIK %s %s %s (XBRL 없음)" % (cik, rd, [a for _, a, _ in out[rd]]))
            del out[rd]


c.fix_report_dates = fix_report_dates

if __name__ == "__main__":
    c.main()
