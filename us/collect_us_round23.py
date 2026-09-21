"""미국 라운드 23 기획 2팀: TOP 5 수집 -> us-round23-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round23-dataset.csv"
c.TOP10 = [
    ("Zebra Technologies", "ZBRA", "0000877212"),
    ("IDEX", "IEX", "0000832101"),
    ("NVR", "NVR", "0000906163"),
    ("News Corp", "NWSA", "0001564708"),
    ("Ball", "BALL", "0000009389"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000906163", "0001564708"}  # NVR·NWSA: OperatingIncomeLoss 태그 없음 (LLY 선례)
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
