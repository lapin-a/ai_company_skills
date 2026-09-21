"""미국 라운드 9 기획 2팀: TOP 20 수집 -> us-round9-dataset.csv

라운드 4~8과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round9-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round9-dataset.csv"
c.TOP10 = [
    ("Warner Bros. Discovery", "WBD", "0001437107"), ("Colgate-Palmolive", "CL", "0000021665"),
    ("Hilton Worldwide", "HLT", "0001585689"), ("O'Reilly Automotive", "ORLY", "0000898173"),
    ("Republic Services", "RSG", "0001060391"), ("Royal Caribbean Cruises", "RCL", "0000884887"),
    ("Honeywell International", "HON", "0000773840"), ("American Electric Power", "AEP", "0000004904"),
    ("United Rentals", "URI", "0001067701"), ("Air Products & Chemicals", "APD", "0000002969"),
    ("Boston Scientific", "BSX", "0000885725"), ("Targa Resources", "TRGP", "0001389170"),
    ("Coherent", "COHR", "0000820318"), ("Moderna", "MRNA", "0001682852"),
    ("PACCAR", "PCAR", "0000075362"), ("TransDigm Group", "TDG", "0001260221"),
    ("Monolithic Power Systems", "MPWR", "0001280452"), ("W.W. Grainger", "GWW", "0000277135"),
    ("TE Connectivity", "TEL", "0001385157"), ("Cencora", "COR", "0001140859"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
# PCAR는 OperatingIncomeLoss 태그가 없고, COHR는 2024-06에서 끊겼다 (LLY 선례)
r2.NO_OPINC = {"0000075362", "0000820318"}
c.ROW_FIX = r2.fix_rows

if __name__ == "__main__":
    c.main()
