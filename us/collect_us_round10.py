"""미국 라운드 10 기획 2팀: TOP 20 수집 -> us-round10-dataset.csv

라운드 4~9와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round10-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round10-dataset.csv"
c.TOP10 = [
    ("ONEOK", "OKE", "0001039684"), ("Occidental Petroleum", "OXY", "0000797468"),
    ("Comfort Systems USA", "FIX", "0001035983"), ("Teradyne", "TER", "0000097210"),
    ("NXP Semiconductors", "NXPI", "0001413447"), ("Keysight Technologies", "KEYS", "0001601046"),
    ("Baker Hughes", "BKR", "0001701605"), ("Nucor", "NUE", "0000073309"),
    ("Fastenal", "FAST", "0000815556"), ("Dominion Energy", "D", "0000715957"),
    ("AMETEK", "AME", "0001037868"), ("Diamondback Energy", "FANG", "0001539838"),
    ("Corteva", "CTVA", "0001755672"), ("Devon Energy", "DVN", "0001090012"),
    ("Sempra", "SRE", "0001032208"), ("Garmin", "GRMN", "0001121788"),
    ("NIKE", "NKE", "0000320187"), ("Ford Motor", "F", "0000037996"),
    ("Cardinal Health", "CAH", "0000721371"), ("Delta Air Lines", "DAL", "0000027904"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
# 영업이익 태그가 없거나 수집 구간 전에 끊긴 7곳 (LLY 선례)
r2.NO_OPINC = {"0000797468", "0001701605", "0000073309", "0001755672", "0001090012", "0001032208", "0000320187"}
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
