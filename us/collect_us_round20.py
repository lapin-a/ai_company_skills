"""미국 라운드 20 기획 2팀: TOP 5 수집 -> us-round20-dataset.csv

라운드 4~16과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 라운드 17부터 5곳 단위.
us-round17-30-log.md 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round20-dataset.csv"
c.TOP10 = [
    ("Lennar", "LEN", "0000920760"),
    ("Evergy", "EVRG", "0001711269"),
    ("Fidelity National Information Services", "FIS", "0001136893"),
    ("International Paper", "IP", "0000051434"),
    ("CDW", "CDW", "0001402057"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
r2.NO_OPINC = set()  # 영업이익 태그 모두 정상
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
