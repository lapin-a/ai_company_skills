"""미국 라운드 5 기획 2팀: TOP 20 수집 -> us-round5-dataset.csv

라운드 4와 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완).
더한 것 하나: ACN 상장주식수는 Class A만 센다(us-round5-log.md 2절).
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round5-dataset.csv"
c.TOP10 = [
    ("T-Mobile US", "TMUS", "0001283699"), ("Western Digital", "WDC", "0000106040"),
    ("ConocoPhillips", "COP", "0001163165"), ("Pfizer", "PFE", "0000078003"), ("Boeing", "BA", "0000012927"),
    ("Danaher", "DHR", "0000313616"), ("Uber Technologies", "UBER", "0001543151"),
    ("ServiceNow", "NOW", "0001373715"), ("TJX Companies", "TJX", "0000109198"),
    ("Intuitive Surgical", "ISRG", "0001035267"), ("Newmont", "NEM", "0001164727"), ("Corning", "GLW", "0000024741"),
    ("Vertex Pharmaceuticals", "VRTX", "0000875320"), ("Bristol Myers Squibb", "BMY", "0000014272"),
    ("Booking Holdings", "BKNG", "0001075531"), ("Fortinet", "FTNT", "0001262039"),
    ("Lockheed Martin", "LMT", "0000936468"), ("Accenture", "ACN", "0001467373"),
    ("S&P Global", "SPGI", "0000064040"), ("Marathon Petroleum", "MPC", "0001510295"),
]
r2.c = c
r2.A_ONLY = {"0001467373"}   # ACN: Class X는 비상장, 전환비율 미확인
r2.UNVERIFIED = {}
r2.NO_OPINC = {"0001163165", "0000078003", "0001164727", "0000014272", "0000109198"}  # COP·PFE·NEM·BMY·TJX
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
