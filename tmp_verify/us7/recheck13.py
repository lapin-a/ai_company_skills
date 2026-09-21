"""미국 라운드 6·7 계산값 이상치 재확인 (경로 A: 저장 검산 재계산, 경로 B: 원문 XBRL 누적값)."""
import csv, importlib.util, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import collect_us_round1 as c
import collect_us_round2 as r2

spec = importlib.util.spec_from_file_location("o", os.path.join(ROOT, "tmp_verify", "outliers_kr.py"))
o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
nums = lambda s: [float(x) for x in re.findall(r"-?\d{5,}(?:\.\d+)?|-?\d+\.\d+|(?<=분할비율 )\d+", s)]

for rnd in (13,14,15):
    mod = importlib.import_module("collect_us_round%d" % rnd)
    rows = list(csv.DictReader(open(os.path.join(ROOT, "us-round%d-dataset.csv" % rnd), encoding="utf-8-sig")))
    D = {(r["종목코드"], r["기간"], r["항목"]): r for r in rows}
    TK = {r["기업"]: r["종목코드"] for r in rows}
    CIK = {t: k for _, t, k in mod.c.TOP10}
    out, _ = o.judge(rows)
    targets = [(TK[x[0]], x[2], x[1]) for x in out if x[6].startswith("계산")]
    badA = ocf_bad = 0
    for tk, per, item in targets:
        r = D[(tk, per, item)]
        s = r["검산"].split(" ; ")[0]
        if "연간(연결-비지배)" in r["값구분"]:
            n = [float(x) for x in re.findall(r"-?\d{4,}", s)]
            v = n[0] - n[1] - (n[2] - n[3] if len(n) > 3 else n[2])
        else:
            n = nums(re.sub(r"\([^)]*\)", "", s))
            v = round(n[0] * n[1] / (n[2] if len(n) > 2 else 1)) if r["값구분"] == "계산(종가×주식수)" else n[0] - sum(n[1:])
        if abs(v - float(r["값"])) > 1:
            badA += 1
            print("경로A 불일치", rnd, tk, per, item, r["값"], s[:110])
    # 경로 B: 누적차감 건은 원문 XBRL에서 두 누적값을 다시 읽는다
    for tk, per, item in targets:
        r = D[(tk, per, item)]
        if "누적차감" not in r["값구분"]:
            continue
        cik = CIK[tk]
        reps, _ = c.reports(cik)
        lab = {mod.c.label(e): e for e in reps}
        end = lab[per]
        prevs = [e for e in sorted(reps) if e < end]
        n = nums(re.sub(r"\([^)]*\)", "", r["검산"].split(" ; ")[0]))
        vals = []
        for e in (end, prevs[-1] if prevs else None):
            if not e:
                continue
            x = c.instance(cik, reps[e][0])
            vals.append({v for v, d, m in r2.members(x, r"NetCashProvidedByUsedInOperatingActivities(?:ContinuingOperations)?") if d == e and not m})
        ok = vals and n[0] in vals[0] and (len(vals) < 2 or n[1] in vals[1])
        if not ok:
            ocf_bad += 1
            print("경로B 확인필요", rnd, tk, per, n[:2], [sorted(v)[:3] for v in vals])
    print("라운드 %d | 계산값 이상치 %d건 | 경로A 불일치 %d | 경로B 확인필요 %d" % (rnd, len(targets), badA, ocf_bad))
