"""미국 라운드 13 기획 2팀: TOP 20 수집 -> us-round13-dataset.csv

라운드 4~12와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round13-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round13-dataset.csv"
c.TOP10 = [
    ("TKO Group Holdings", "TKO", "0001973266"),
    ("Kroger", "KR", "0000056873"),
    ("PG&E", "PCG", "0001004980"),
    ("United Airlines", "UAL", "0000100517"),
    ("Public Service Enterprise", "PEG", "0000788784"),
    ("Kenvue", "KVUE", "0001944048"),
    ("Hershey", "HSY", "0000047111"),
    ("Estee Lauder", "EL", "0001001250"),
    ("Steel Dynamics", "STLD", "0001022671"),
    ("DexCom", "DXCM", "0001093557"),
    ("WEC Energy", "WEC", "0000783325"),
    ("Expedia Group", "EXPE", "0001324424"),
    ("EMCOR Group", "EME", "0000105634"),
    ("Kimberly-Clark", "KMB", "0000055785"),
    ("ResMed", "RMD", "0000943819"),
    ("Biogen", "BIIB", "0000875045"),
    ("Jabil", "JBL", "0000898293"),
    ("EQT", "EQT", "0000033213"),
    ("Vulcan Materials", "VMC", "0001396009"),
    ("HP", "HPQ", "0000047217"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0000875045"}  # BIIB: 영업이익 태그 2022-03까지
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
