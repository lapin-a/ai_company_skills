"""미국 라운드 16 기획 2팀: TOP 20 수집 -> us-round16-dataset.csv

라운드 4~15와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round16-log.md 1~3절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round16-dataset.csv"
c.TOP10 = [
    ("PPG Industries", "PPG", "0000079879"),
    ("Ulta Beauty", "ULTA", "0001403568"),
    ("Verisk Analytics", "VRSK", "0001442145"),
    ("Tapestry", "TPR", "0001116132"),
    ("Global Payments", "GPN", "0001123360"),
    ("Church & Dwight", "CHD", "0000313927"),
    ("Casey's General Stores", "CASY", "0000726958"),
    ("J.B. Hunt Transport", "JBHT", "0000728535"),
    ("PulteGroup", "PHM", "0000822416"),
    ("Omnicom Group", "OMC", "0000029989"),
    ("NRG Energy", "NRG", "0001013871"),
    ("Edison International", "EIX", "0000827052"),
    ("International Flavors & Fragrances", "IFF", "0000051253"),
    ("First Solar", "FSLR", "0001274494"),
    ("Dollar Tree", "DLTR", "0000935703"),
    ("Packaging Corp of America", "PKG", "0000075677"),
    ("Dow", "DOW", "0001751788"),
    ("Fair Isaac", "FICO", "0000814547"),
    ("CMS Energy", "CMS", "0000811156"),
    ("Constellation Brands", "STZ", "0000016918"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000726958", "0000822416", "0001751788"}  # CASY·PHM·DOW (QA 3절)
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
