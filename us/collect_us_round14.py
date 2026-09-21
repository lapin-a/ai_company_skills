"""미국 라운드 14 기획 2팀: TOP 20 수집 -> us-round14-dataset.csv

라운드 4~13와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round14-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round14-dataset.csv"
c.TOP10 = [
    ("Carnival", "CCL", "0000815097"),
    ("Zoetis", "ZTS", "0001555280"),
    ("Martin Marietta", "MLM", "0000916076"),
    ("GE HealthCare", "GEHC", "0001932393"),
    ("Kraft Heinz", "KHC", "0001637459"),
    ("Cognizant", "CTSH", "0001058290"),
    ("Ameren", "AEE", "0001002910"),
    ("Halliburton", "HAL", "0000045012"),
    ("Teledyne", "TDY", "0001094285"),
    ("Mettler-Toledo", "MTD", "0001037646"),
    ("Ingersoll Rand", "IR", "0001699150"),
    ("VeriSign", "VRSN", "0001014473"),
    ("ON Semiconductor", "ON", "0001097864"),
    ("Quest Diagnostics", "DGX", "0001022079"),
    ("EchoStar", "ECHO", "0001415404"),
    ("Copart", "CPRT", "0000900075"),
    ("Atmos Energy", "ATO", "0000731802"),
    ("Fox", "FOXA", "0001754301"),
    ("American Water Works", "AWK", "0001410636"),
    ("Dollar General", "DG", "0000029534"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0001555280", "0001037646", "0001754301"}  # ZTS·MTD·FOXA
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
