"""미국 라운드 18 기획 2팀: TOP 5 수집 -> us-round18-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round18-dataset.csv"
c.TOP10 = [
    ("Best Buy", "BBY", "0000764478"),
    ("Viatris", "VTRS", "0001792044"),
    ("NiSource", "NI", "0001111711"),
    ("General Mills", "GIS", "0000040704"),
    ("Amcor", "AMCR", "0001748790"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 영업이익 태그 모두 정상
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
