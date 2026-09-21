"""미국 라운드 8 시장조사: SPY 비중 236~305위 추가 검증."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import us_probe as u
import collect_us_round1 as c

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_r8.json")
DONE = set("""NVDA AAPL GOOGL GOOG MSFT AMZN AVGO META TSLA MU LLY AMD WMT XOM V JNJ INTC MA ABBV CSCO PLTR
ORCL CVX COST KO CAT MRK DELL LRCX AMAT PG GE HD NFLX PANW PM RTX ANET TXN CRWD TMO KLAC IBM MRVL LIN AMGN VZ CRM STX
QCOM GILD DE ADI ABT DIS PEP MCD T NEE UNP ETN TMUS WDC COP PFE BA DHR UBER NOW TJX ISRG NEM GLW VRTX BMY BKNG FTNT
LMT ACN SPGI MPC VLO PH MDT MO CVS SBUX PSX LOW ADP SYK APP FCX MCK ABNB ADBE SO VRT PWR APH GD
HCA TT DUK HWM CEG MAR WMB JCI CSX MMM WM UPS EMR DASH LITE DDOG MCO INTU REGN CMCSA""".split())

asof, hold = u.spy_holdings()
rank = sorted(hold, key=lambda x: -x[2])
print("SPY 기준일", asof, "| 종목 행", len(rank))
todo = [(nm, tk, w) for nm, tk, w in rank[235:305] if tk not in DONE]
print("추가 검증 대상", len(todo))
res = []
for nm, tk, w in todo:
    try:
        r = u.probe(tk)
        if r.get("sharesSrc") != "dei" and not r.get("error"):
            reps, _ = c.reports(r["cik"])
            got = c.instance_shares(r["cik"], reps[max(reps)][0])
            if got:
                r.update(sharesXbrl=got[0], mcapXbrl=r["price"] * got[0])
    except Exception as e:
        r = {"ticker": tk, "error": repr(e)[:100]}
    r["spyWeight"] = w
    res.append(r)
    m = (r.get("mcapXbrl") or r.get("mcap") or 0) / 1e9
    print("%-6s %-26s %s SIC %-5s %6.1f run %s %s" % (tk, (r.get("name") or "")[:26], r.get("cik"), r.get("sic"), m, r.get("run"), r.get("qCloses")), flush=True)
json.dump({"asof": asof, "rows": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
