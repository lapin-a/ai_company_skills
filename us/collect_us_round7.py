"""미국 라운드 7 기획 2팀: TOP 20 수집 -> us-round7-dataset.csv

라운드 4~6과 같은 구성(라운드 1 본체 + 라운드 2 보충 + 라운드 3 라벨 보완). 새 규칙 없음.
us-round7-log.md 1·2절 참조.
"""

import collect_us_round1 as c
import collect_us_round2 as r2
import collect_us_round3 as r3  # 라벨 보완 규칙

c.OUT = "us-round7-dataset.csv"
c.TOP10 = [
    ("HCA Healthcare", "HCA", "0000860730"), ("Trane Technologies", "TT", "0001466258"),
    ("Duke Energy", "DUK", "0001326160"), ("Howmet Aerospace", "HWM", "0000004281"),
    ("Constellation Energy", "CEG", "0001868275"), ("Marriott International", "MAR", "0001048286"),
    ("Williams Companies", "WMB", "0000107263"), ("Johnson Controls", "JCI", "0000833444"),
    ("CSX", "CSX", "0000277948"), ("3M", "MMM", "0000066740"), ("Waste Management", "WM", "0000823768"),
    ("United Parcel Service", "UPS", "0001090727"), ("Emerson Electric", "EMR", "0000032604"),
    ("DoorDash", "DASH", "0001792789"), ("Lumentum Holdings", "LITE", "0001633978"),
    ("Datadog", "DDOG", "0001561550"), ("Moody's", "MCO", "0001059556"), ("Intuit", "INTU", "0000896878"),
    ("Regeneron Pharmaceuticals", "REGN", "0000872589"), ("Comcast", "CMCSA", "0001166691"),
]
r2.c = c
r2.A_ONLY = set()
r2.UNVERIFIED = {}
# HCA·EMR은 OperatingIncomeLoss 태그가 없고, JCI는 2016-06까지만 있다 (LLY 선례)
r2.NO_OPINC = {"0000860730", "0000032604", "0000833444"}

# CEG는 2022-02 Exelon에서 분사했다. 첫 사업보고서(FY2021)의 수치는 전부 사업부문 차원으로만 태그돼 있어
# 연결 합계 줄이 없다 → 대표 결정 (가), 2026-09-20: 분사 전 분기는 "데이터 없음"으로 둔다 (VRT와 같은 처리).
CEG_PRE = "2021Q4"


def fix_rows(rows):
    r2.fix_rows(rows)
    for r in rows:
        if r[1] == "CEG" and r[2] <= CEG_PRE and r[5] in ("미확인",):
            r[5:10] = ["데이터 없음(최초 보고기간 이전)", "USD" if r[4] != "분기말 상장주식수" else "",
                       "데이터 없음(최초 보고기간 전)",
                       "https://data.sec.gov/submissions/CIK0001868275.json (2022-02 Exelon 분사 전)",
                       "FY2021 10-K 수치는 사업부문 차원으로만 공시돼 연결 합계가 없다"]


c.ROW_FIX = fix_rows

if __name__ == "__main__":
    c.main()
