"""라운드 3·5에서 검증했던 미수집 후보 재조회 (이전 결과 파일이 사라져 다시 만든다)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import us_probe as u
import collect_us_round1 as c

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_prev.json")
TICKERS = """TT HWM DUK MAR CSX JCI WMB MMM CEG EMR WM DASH LITE DDOG UPS MCO INTU CMCSA HPE REGN
MDLZ CDNS SHW ITW MSI SLB EOG NOC SNPS CMI GM ROST TGT NSC CL WBD ORLY HLT""".split()
res = []
import time
for tk in TICKERS:
    r = None
    for attempt in range(3):  # 일시적 네트워크 끊김이 있었다(2026-09-20)
        try:
            r = u.probe(tk)
            break
        except Exception as e:
            err, r = repr(e)[:100], None
            time.sleep(5)
    try:
        if r is None:
            raise RuntimeError(err)
        if r.get("sharesSrc") != "dei" and not r.get("error"):
            reps, _ = c.reports(r["cik"])
            got = c.instance_shares(r["cik"], reps[max(reps)][0])
            if got:
                r.update(sharesXbrl=got[0], mcapXbrl=r["price"] * got[0])
    except Exception as e:
        r = {"ticker": tk, "error": repr(e)[:100]}
    res.append(r)
    print("%-6s %s SIC %-5s %6.1f run %s %s" % (tk, r.get("cik"), r.get("sic"),
          (r.get("mcapXbrl") or r.get("mcap") or 0) / 1e9, r.get("run"), r.get("qCloses")), flush=True)
json.dump({"rows": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
