"""미국 라운드 15 기획 2팀: TOP 20 수집 -> us-round15-dataset.csv

라운드 4~14와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round15-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round15-dataset.csv"
c.TOP10 = [
    ("DTE Energy", "DTE", "0000936340"),
    ("Williams-Sonoma", "WSM", "0000719955"),
    ("FirstEnergy", "FE", "0001031296"),
    ("Corpay", "CPAY", "0001175454"),
    ("Otis Worldwide", "OTIS", "0001781335"),
    ("Labcorp Holdings", "LH", "0000920148"),
    ("Las Vegas Sands", "LVS", "0001300514"),
    ("Super Micro Computer", "SMCI", "0001375365"),
    ("Eversource Energy", "ES", "0000072741"),
    ("West Pharmaceutical", "WST", "0000105770"),
    ("Dover", "DOV", "0000029905"),
    ("Xylem", "XYL", "0001524472"),
    ("Fiserv", "FISV", "0000798354"),
    ("PPL", "PPL", "0000922224"),
    ("Incyte", "INCY", "0000879169"),
    ("CenterPoint Energy", "CNP", "0001130310"),
    ("Expeditors International", "EXPD", "0000746515"),
    ("F5", "FFIV", "0001048695"),
    ("Darden Restaurants", "DRI", "0000940944"),
    ("Hubbell", "HUBB", "0000048898"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 영업이익 태그 20곳 모두 정상
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
