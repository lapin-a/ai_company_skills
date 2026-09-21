"""미국 라운드 25 기획 2팀: TOP 5 수집 -> us-round25-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round25-dataset.csv"
c.TOP10 = [
    ("Tyler Technologies", "TYL", "0000860731"),
    ("Masco", "MAS", "0000062996"),
    ("Textron", "TXT", "0000217346"),
    ("Stanley Black & Decker", "SWK", "0000093556"),
    ("Trimble", "TRMB", "0000864749"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000217346"}  # TXT: OperatingIncomeLoss 태그 2011년까지 (BIIB 선례)
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
