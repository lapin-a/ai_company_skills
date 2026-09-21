"""미국 라운드 27 기획 2팀: TOP 5 수집 -> us-round27-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round27-dataset.csv"
c.TOP10 = [
    ("Allegion", "ALLE", "0001579241"),
    ("Avery Dennison", "AVY", "0000008818"),
    ("Lennox", "LII", "0001069202"),
    ("Generac", "GNRC", "0001474735"),
    ("GoDaddy", "GDDY", "0001609711"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000008818"}  # AVY: OperatingIncomeLoss 태그 없음 (LLY 선례)
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
