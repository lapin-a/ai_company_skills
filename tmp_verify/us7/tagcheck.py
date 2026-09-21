"""라운드 13~15 후보 60곳 태그 사전 점검 + QA(중복·라벨 겹침)."""
import csv, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import us_probe as u
import collect_us_round1 as c
import collect_us_round3 as r3

GROUPS = {
    13: [("TKO", "0001973266"), ("KR", "0000056873"), ("PCG", "0001004980"), ("UAL", "0000100517"),
         ("PEG", "0000788784"), ("KVUE", "0001944048"), ("HSY", "0000047111"), ("EL", "0001001250"),
         ("STLD", "0001022671"), ("DXCM", "0001093557"), ("WEC", "0000783325"), ("EXPE", "0001324424"),
         ("EME", "0000105634"), ("KMB", "0000055785"), ("RMD", "0000943819"), ("BIIB", "0000875045"),
         ("JBL", "0000898293"), ("EQT", "0000033213"), ("VMC", "0001396009"), ("HPQ", "0000047217")],
    14: [("CCL", "0000815097"), ("ZTS", "0001555280"), ("MLM", "0000916076"), ("GEHC", "0001932393"),
         ("KHC", "0001637459"), ("CTSH", "0001058290"), ("AEE", "0001002910"), ("HAL", "0000045012"),
         ("TDY", "0001094285"), ("MTD", "0001037646"), ("IR", "0001699150"), ("VRSN", "0001014473"),
         ("ON", "0001097864"), ("DGX", "0001022079"), ("ECHO", "0001415404"), ("CPRT", "0000900075"),
         ("ATO", "0000731802"), ("FOXA", "0001754301"), ("AWK", "0001410636"), ("DG", "0000029534")],
    15: [("DTE", "0000936340"), ("WSM", "0000719955"), ("FE", "0001031296"), ("CPAY", "0001175454"),
         ("OTIS", "0001781335"), ("LH", "0000920148"), ("LVS", "0001300514"), ("SMCI", "0001375365"),
         ("ES", "0000072741"), ("WST", "0000105770"), ("DOV", "0000029905"), ("XYL", "0001524472"),
         ("FISV", "0000798354"), ("PPL", "0000922224"), ("INCY", "0000879169"), ("CNP", "0001130310"),
         ("EXPD", "0000746515"), ("FFIV", "0001048695"), ("DRI", "0000940944"), ("HUBB", "0000048898")],
}

done = set()
for i in range(1, 13):
    done |= {r["종목코드"] for r in csv.DictReader(open(os.path.join(ROOT, "us-round%d-dataset.csv" % i), encoding="utf-8-sig"))}
print("중복:", [t for g in GROUPS.values() for t, _ in g if t in done] or "0건")

for rnd, group in GROUPS.items():
    noop = []
    print("\n=== 라운드 %d ===" % rnd)
    for tk, cik in group:
        f = None
        for _ in range(3):
            try:
                f = json.loads(u.get("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik, u.SEC_UA))["facts"]
                break
            except Exception:
                time.sleep(5)
        g = (f or {}).get("us-gaap", {})

        def rng(t):
            us = g.get(t, {}).get("units", {}).get("USD", [])
            return max(x["end"] for x in us)[:7] if us else None

        oi = rng("OperatingIncomeLoss")
        if not oi or oi < "2026-01":
            noop.append((tk, cik, oi))
        reps, _ = c.reports(cik)
        labs = [r3.label(e) for e in reps if "2018-10-01" <= e <= "2026-09-30"]
        dup = sorted({l for l in labs if labs.count(l) > 1})
        dei = (f or {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
        print("  %-5s 영업이익 %-8s 부채 %-8s dei %-8s 보고 %2d 겹침 %s" % (
            tk, oi or "없음", rng("Liabilities") or "없음",
            max(x["end"] for x in dei)[:7] if dei else "없음", len(labs), dup or "없음"))
    print("  NO_OPINC:", [(t, o) for t, _, o in noop])
    print("  NO_OPINC_CIK:", {cik for _, cik, _ in noop})
