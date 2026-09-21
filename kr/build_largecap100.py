"""대형주 100 목록 생성 -> largecap100.csv

규칙(coverage-log.md): 기준일 KOSPI 시가총액 순 → 우선주·리츠/인프라 제외 → 상위 100.
각 종목에 DART corp_code·업종코드·금융여부·수집상태를 붙인다.
금융여부: KSIC 65·66 또는 64(64992 제외) = 금융. 64992(지주회사)는 최신 사업보고서 연결재무제표의
금융형 표지(순이자이익·예수부채·보험계약부채·보험서비스결과·순보험손익)로 판단한다.
"""

import csv
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import html as H

sys.path.insert(0, ".")
import collect_round1 as cr

BASE_DT = "20260916"
OUT = "kr/largecap100.csv"
PREF = re.compile(r"(\d?우[B-C]?|우\(전환\))$")
REIT = re.compile(r"(?<!메)리츠|REIT|인프라|부동산투자|선박투자|유전|펀드")
FIN_MARK = re.compile(r"순이자이익|예수부채|보험계약부채|보험서비스결과|순보험손익")
DONE = {"005930": 1, "000660": 2, "402340": 2, "009150": 2, "373220": 2, "005380": 2,
        "207940": 2, "028260": 2, "012450": 2, "034020": 2, "000270": 2}
env = json.load(open(".claude/settings.local.json", encoding="utf-8"))["env"]
DK, PK = env["DART_API_KEY"], urllib.parse.unquote(env["PUBLIC_DATA_SERVICE_KEY"])
calls = {"public": 0, "dart": 0, "viewer": 0}


def get(url, kind):
    calls[kind] += 1
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    time.sleep(0.25)
    return data


def kospi():
    q = urllib.parse.urlencode({"serviceKey": PK, "resultType": "json", "basDt": BASE_DT,
                                "mrktCls": "KOSPI", "numOfRows": "1000"})
    b = json.loads(get("https://apis.data.go.kr/1160100/GetStockSecuritiesInfoService_V2/getStockPriceInfo_V2?" + q, "public"))["response"]["body"]
    items = b["items"]["item"]
    assert len(items) == int(b["totalCount"]), "전체 종목을 못 받았다"
    return sorted(items, key=lambda i: int(i["mrktTotAmt"]), reverse=True)


def corp_map():
    z = zipfile.ZipFile(io.BytesIO(get("https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=" + DK, "dart")))
    root = ET.fromstring(z.read(z.namelist()[0]))
    return {c.findtext("stock_code").strip(): c.findtext("corp_code")
            for c in root.iter("list") if (c.findtext("stock_code") or "").strip()}


def latest_annual(corp_code):
    q = urllib.parse.urlencode({"crtfc_key": DK, "corp_code": corp_code, "bgn_de": "20250101",
                                "end_de": "20260918", "pblntf_detail_ty": "A001", "page_count": "100"})
    d = json.loads(get("https://opendart.fss.or.kr/api/list.json?" + q, "dart"))
    lst = sorted([x for x in d.get("list", []) if "사업보고서" in x["report_nm"] and "첨부" not in x["report_nm"]],
                 key=lambda x: x["rcept_no"], reverse=True)
    return lst[0]["rcept_no"] if lst else None


def has_fin_marks(rcp):
    doc = cr.fs_section(rcp) or ""
    calls["viewer"] += 2
    txt = H.unescape(re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", doc))
    return sorted(set(FIN_MARK.findall(txt)))


def main():
    items = kospi()
    pref = [i for i in items if PREF.search(i["itmsNm"])]
    reit = [i for i in items if REIT.search(i["itmsNm"])]
    pool = [i for i in items if i not in pref and i not in reit][:100]
    print("KOSPI %d | 우선주 %d | 리츠·인프라 %d | 상위 100 확정" % (len(items), len(pref), len(reit)))
    print("제외된 상위 30위 내 종목:", [(i["itmsNm"]) for i in items[:30] if i in pref or i in reit])

    cmap = corp_map()
    rows = []
    for rank, i in enumerate(pool, 1):
        code = i["srtnCd"]
        cc = cmap.get(code)
        induty = fin = marks = None
        if cc:
            d = json.loads(get("https://opendart.fss.or.kr/api/company.json?" + urllib.parse.urlencode({"crtfc_key": DK, "corp_code": cc}), "dart"))
            induty = d.get("induty_code")
        if induty:
            if induty.startswith(("65", "66")) or (induty.startswith("64") and induty != "64992"):
                fin, marks = "Y", "업종코드"
            elif induty == "64992":
                rcp = latest_annual(cc)
                found = has_fin_marks(rcp) if rcp else []
                fin, marks = ("Y" if found else "N"), (",".join(found) if found else "표지없음")
            else:
                fin, marks = "N", "업종코드"
        rows.append([rank, code, i["itmsNm"], int(i["mrktTotAmt"]), cc or "", induty or "", fin or "미확인",
                     marks or "", DONE.get(code, "")])
        if rank % 20 == 0:
            print("  ...%d위까지 처리" % rank, flush=True)

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["순위", "종목코드", "기업", "시가총액(원)", "DART corp_code", "업종코드", "금융여부", "금융판정근거", "수집완료라운드"])
        w.writerows(rows)
    fin_n = sum(1 for r in rows if r[6] == "Y")
    print("완료: %s | 금융 %d | 비금융 %d | 미확인 %d | 수집완료 %d" % (
        OUT, fin_n, sum(1 for r in rows if r[6] == "N"), sum(1 for r in rows if r[6] == "미확인"),
        sum(1 for r in rows if r[8])))
    print("호출:", calls)
    print("100위 시가총액: %.2f조원 | 1위 %s" % (rows[-1][3] / 1e12, rows[0][2]))


if __name__ == "__main__":
    main()
