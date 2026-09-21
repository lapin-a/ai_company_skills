"""미국 라운드 26 기획 2팀: TOP 5 수집 -> us-round26-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round26-dataset.csv"
c.TOP10 = [
    ("Skyworks", "SWKS", "0000004127"),
    ("Charles River Laboratories", "CRL", "0001100682"),
    ("Albemarle", "ALB", "0000915913"),
    ("McCormick", "MKC", "0000063754"),
    ("J.M. Smucker", "SJM", "0000091419"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 영업이익 태그 모두 정상
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
