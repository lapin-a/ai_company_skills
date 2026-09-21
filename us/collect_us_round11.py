"""미국 라운드 11 기획 2팀: TOP 20 수집 -> us-round11-dataset.csv

라운드 4~10과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round11-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round11-dataset.csv"
c.TOP10 = [
    ("Edwards Lifesciences", "EW", "0001099800"), ("eBay", "EBAY", "0001065088"),
    ("Ciena", "CIEN", "0000936395"), ("Becton Dickinson", "BDX", "0000010795"),
    ("Westinghouse Air Brake", "WAB", "0000943452"), ("Vistra", "VST", "0001692819"),
    ("Workday", "WDAY", "0001327811"), ("Entergy", "ETR", "0000065984"),
    ("AutoZone", "AZO", "0000866787"), ("PayPal Holdings", "PYPL", "0001633917"),
    ("Rockwell Automation", "ROK", "0001024478"), ("L3Harris Technologies", "LHX", "0000202058"),
    ("Block", "XYZ", "0001512673"), ("Autodesk", "ADSK", "0000769397"),
    ("Xcel Energy", "XEL", "0000072903"), ("Carrier Global", "CARR", "0001783180"),
    ("IQVIA Holdings", "IQV", "0001478242"), ("Agilent Technologies", "A", "0001090872"),
    ("Monster Beverage", "MNST", "0000865752"), ("Exelon", "EXC", "0001109357"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 이번 라운드는 영업이익 태그가 20곳 모두 정상이다
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
