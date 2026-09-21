"""미국 데이터셋의 계산값 이상치를 SEC 원문으로 재생성해 대조한다.

실행: python tmp_verify/recheck_calc_us.py us-roundN-dataset.csv
원본 CSV는 읽기만 하며, 해당 라운드 수집기의 SEC companyfacts/XBRL 규칙을 그대로 쓴다.
"""

import csv
import importlib
import os
import sys

sys.path.insert(0, "us")
sys.path.insert(0, "kr")
sys.path.insert(0, "tmp_verify")
from outliers_kr import judge  # noqa: E402


FINANCIAL_ITEMS = {
    "분기별 매출액", "분기별 영업이익", "분기별 당기순이익(지배)",
    "분기별 영업활동현금흐름", "분기말 자산총계", "분기말 부채총계",
    "분기말 총자본(자기자본)", "분기말 지배지분 자본",
}


def main(path, company=None):
    # us/data/us-round16-dataset.csv -> collect_us_round16, kr/data/round5-dataset.csv -> collect_round5
    module_name = "collect_" + os.path.basename(path).replace("-dataset.csv", "").replace("-", "_")
    module = importlib.import_module(module_name)
    collector = getattr(module, "c", module)
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    outliers, _ = judge(rows)
    calc = [x for x in outliers if x[6].startswith("계산") and x[1] in FINANCIAL_ITEMS]
    if company:
        selected = set(company.split(","))
        calc = [x for x in calc if x[0] in selected]
    targets = {x[0] for x in calc}
    companies = {name: (ticker, cik) for name, ticker, cik in collector.TOP10}
    by_company = {name: [] for name in targets}
    for x in calc:
        by_company[x[0]].append(x)

    ok = failed = errors = 0
    for name, cases in sorted(by_company.items()):
        ticker, cik = companies[name]
        try:
            reports, forms = collector.reports(cik)
            facts = collector.Facts(cik)
            regenerated, _ = collector.fin_rows(name, ticker, cik, reports, forms, facts)
            for _, item, period, _, _, _, _ in cases:
                stored = next(r for r in rows if r["기업"] == name and r["기간"] == period and r["항목"] == item)
                got = regenerated.get((period, item))
                same = got is not None and str(got[5]) == stored["값"]
                ok += same
                failed += not same
                print("%s | %s | %s | %s" % (name, period, item, "O" if same else "X"), flush=True)
        except Exception as exc:
            errors += len(cases)
            print("%s | SEC 재생성 실패 | %s" % (name, exc), flush=True)
    print("SEC 원문 대조: 일치 %d | 불일치 %d | 조회실패 %d | 전체 %d" % (
        ok, failed, errors, len(calc)))
    return failed + errors


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit("데이터셋 파일과 선택적 기업명을 지정하세요.")
    raise SystemExit(main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None))
