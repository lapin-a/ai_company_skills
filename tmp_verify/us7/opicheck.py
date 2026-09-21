"""(나)안 검증: 매출 - 매출원가 - 판관비가 공시 영업이익과 맞는지.

영업이익을 공시하는 회사에서 계산해 보고 차이를 본다.
공시 영업이익이 있는 회사에서 안 맞으면, 미공시 회사에서도 맞을 이유가 없다.
"""
import json, sys, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import us_probe as u

REV = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
       "RevenueFromContractWithCustomerIncludingAssessedTax"]
COGS = ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfServices"]
SGA = ["SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"]
RD = ["ResearchAndDevelopmentExpense"]


def facts(cik):
    return json.loads(u.get("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik, u.SEC_UA))["facts"].get("us-gaap", {})


def pick(g, tags, end, dur):
    for t in tags:
        for e in g.get(t, {}).get("units", {}).get("USD", []):
            if e["end"] == end and e.get("start") and not e.get("frame", "x").endswith("Q1I") \
               and 350 <= (__import__("datetime").date.fromisoformat(e["end"]) - __import__("datetime").date.fromisoformat(e["start"])).days <= 380:
                return t, e["val"]
    return None, None


for name, cik, end in sys.argv[1:] and [] or [
        ("Apple", "0000320193", "2024-09-28"), ("Microsoft", "0000789019", "2024-06-30"),
        ("Home Depot", "0000354950", "2025-02-02"), ("Coca-Cola", "0000021344", "2024-12-31"),
        ("Eli Lilly*", "0000059478", "2024-12-31"), ("Merck*", "0000310158", "2024-12-31"),
        ("J&J*", "0000200406", "2024-12-29"), ("Pfizer*", "0000078003", "2024-12-31"),
        ("Exxon*", "0000034088", "2024-12-31"), ("Chevron*", "0000093410", "2024-12-31")]:
    try:
        g = facts(cik)
    except Exception as e:
        print("%-12s 조회 실패 %s" % (name, e)); continue
    tr, rev = pick(g, REV, end, 365)
    tc, cogs = pick(g, COGS, end, 365)
    ts, sga = pick(g, SGA, end, 365)
    td, rd = pick(g, RD, end, 365)
    to, opi = pick(g, ["OperatingIncomeLoss"], end, 365)
    calc = None if rev is None or cogs is None or sga is None else rev - cogs - sga
    line = "%-12s 공시영업이익 %-14s 매출-원가-판관비 %-14s" % (
        name, "{:,}".format(opi) if opi is not None else "없음",
        "{:,}".format(calc) if calc is not None else "계산불가")
    if opi is not None and calc is not None:
        d = calc - opi
        line += " 차이 %+15s (%+.1f%%)" % ("{:,}".format(d), d / abs(opi) * 100)
    line += "  | R&D %s" % ("{:,}".format(rd) if rd is not None else "태그없음")
    print(line)
    if cogs is None or sga is None:
        print("             ^ 누락 태그: %s%s" % ("매출원가 " if cogs is None else "", "판관비" if sga is None else ""))
