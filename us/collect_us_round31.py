"""미국 라운드 31 기획 2팀: TOP 5 수집 -> us-round31-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round31-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round31-dataset.csv"
c.TOP10 = [
    ("Bloom Energy", "BE", "0001664703"),
    ("Illumina", "ILMN", "0001110803"),
    ("Everpure", "P", "0001474432"),
    ("Leidos", "LDOS", "0001336920"),
    ("Rollins", "ROL", "0000084839"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
