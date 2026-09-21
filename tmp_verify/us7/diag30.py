"""라운드 17~30 미확인 진단: 해당 보고서에 실린 손익·현금흐름 후보 태그를 나열한다."""
import csv, json, os, re, sys
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us")); os.chdir(ROOT)
import us_probe as u

PAT = {"매출액": r"Revenue|Sales", "영업이익": r"OperatingIncome|OperatingExpenses$|CostsAndExpenses$",
       "당기순이익(지배)": r"NetIncomeLoss|ProfitLoss", "영업활동현금흐름": r"CashProvided.*Operating"}
only = sys.argv[1:]
FX = {}
for n in range(17, 31):
    for r in csv.DictReader(open("us/data/us-round%d-dataset.csv" % n, encoding="utf-8-sig")):
        it = r["항목"].replace("분기별 ", "")
        if r["값"] != "미확인" or it not in PAT or (only and r["종목코드"] not in only):
            continue
        cik = re.search(r"data/(\d+)/(\d{18})", r["출처"])
        if not cik:
            print(r["종목코드"], r["기간"], it, "출처 링크 없음 |", r["출처"][:80])
            continue
        ck, acc = cik.group(1), cik.group(2)
        accn = "%s-%s-%s" % (acc[:10], acc[10:12], acc[12:])
        if ck not in FX:
            FX[ck] = json.loads(u.get("https://data.sec.gov/api/xbrl/companyfacts/CIK%010d.json" % int(ck), u.SEC_UA))["facts"]
        out = []
        for tax, tags in FX[ck].items():
            for t, v in tags.items():
                if not re.search(PAT[it], t):
                    continue
                for es in v["units"].values():
                    for e in es:
                        if e["accn"] == accn and e["end"] == r["기준일"] and "start" in e:
                            d = (date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])).days
                            out.append("%s:%s %dd %s" % (tax[:4], t, d, format(e["val"], ",")))
        print("%s %s %s %s | %s" % (r["종목코드"], r["기간"], it, accn, " ; ".join(sorted(set(out))) or "후보 태그 없음"))
