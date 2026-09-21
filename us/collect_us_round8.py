"""미국 라운드 8 기획 2팀: TOP 20 수집 -> us-round8-dataset.csv

라운드 4~7과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round8-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round8-dataset.csv"
c.TOP10 = [
    ("Hewlett Packard Enterprise", "HPE", "0001645590"), ("Cintas", "CTAS", "0000723254"),
    ("Mondelez International", "MDLZ", "0001103982"), ("Cadence Design Systems", "CDNS", "0000813672"),
    ("Sherwin-Williams", "SHW", "0000089800"), ("Illinois Tool Works", "ITW", "0000049826"),
    ("Motorola Solutions", "MSI", "0000068505"), ("SLB", "SLB", "0000087347"),
    ("EOG Resources", "EOG", "0000821189"), ("Ecolab", "ECL", "0000031462"),
    ("Northrop Grumman", "NOC", "0001133421"), ("Synopsys", "SNPS", "0000883241"),
    ("Cummins", "CMI", "0000026172"), ("Ross Stores", "ROST", "0000745732"),
    ("General Motors", "GM", "0001467858"), ("Target", "TGT", "0000027419"),
    ("FedEx", "FDX", "0001048911"), ("Carvana", "CVNA", "0001690820"),
    ("Kinder Morgan", "KMI", "0001506307"), ("Norfolk Southern", "NSC", "0000702165"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
# SHW(2024-09까지)·SLB(2024-03까지)는 최근 분기 영업이익 태그가 끊겼다 (LLY 선례)
r2.NO_OPINC = {"0000089800", "0000087347"}
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
