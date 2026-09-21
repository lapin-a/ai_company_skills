"""미국 라운드 12 기획 2팀: TOP 20 수집 -> us-round12-dataset.csv

라운드 4~11과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round12-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round12-dataset.csv"
c.TOP10 = [
    ("Chipotle Mexican Grill", "CMG", "0001058090"), ("Keurig Dr Pepper", "KDP", "0001418135"),
    ("Veeva Systems", "VEEV", "0001393052"), ("Waters", "WAT", "0001000697"),
    ("Paychex", "PAYX", "0000723531"), ("Archer-Daniels-Midland", "ADM", "0000007084"),
    ("IDEXX Laboratories", "IDXX", "0000874716"), ("MSCI", "MSCI", "0001408198"),
    ("Flex", "FLEX", "0000866374"), ("Microchip Technology", "MCHP", "0000827054"),
    ("Live Nation Entertainment", "LYV", "0001335258"), ("Consolidated Edison", "ED", "0001047862"),
    ("NetApp", "NTAP", "0001002047"), ("D.R. Horton", "DHI", "0000882184"),
    ("Take-Two Interactive", "TTWO", "0000946581"), ("Sysco", "SYY", "0000096021"),
    ("Yum! Brands", "YUM", "0001041061"), ("Roper Technologies", "ROP", "0000882835"),
    ("Axon Enterprise", "AXON", "0001069183"), ("Old Dominion Freight Line", "ODFL", "0000878927"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000007084", "0000882184"}  # ADM·DHI: OperatingIncomeLoss 태그 없음
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
