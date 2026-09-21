"""라운드 31 QA 사전 점검(5곳): 중복 · CIK 일치 · 영업이익 태그 · 분기 라벨 겹침 · 보고기간."""
import collections, csv, glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us"))
os.chdir(ROOT)
import us_probe as u
import collect_us_round1 as c

FIN = ("60", "61", "62", "63", "64", "65", "67")
rows = json.load(open("tmp_verify/us7/us_r31.json", encoding="utf-8"))
ok = [r for r in rows if not r.get("error") and (r.get("run") or 0) >= 12
      and r.get("qCloses") == "13/13" and (r.get("sic") or "")[:2] not in FIN]
ok.sort(key=lambda r: -(r.get("mcapXbrl") or r.get("mcap") or 0))
top = ok[:5]

done = set()
for f in glob.glob("us/data/us-round*-dataset.csv"):
    for row in csv.DictReader(open(f, encoding="utf-8-sig")):
        done.add(row["종목코드"])
print("[1] 기수집 중복:", [r["ticker"] for r in top if r["ticker"] in done] or "0건")

bad = []
for r in top:
    live = u.cik_for(r["ticker"])
    if live and live != r["cik"]:
        bad.append((r["ticker"], r["cik"], live))
print("[2] CIK 불일치:", bad or "0건 (전부 일치)")

print("[3] 기업별 점검")
noopi, lap = [], []
for r in top:
    cik = r["cik"]
    facts = json.loads(u.get("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik, u.SEC_UA))
    opi = "OperatingIncomeLoss" in facts["facts"].get("us-gaap", {})
    if not opi:
        noopi.append((r["ticker"], cik))
    reps, _ = c.reports(cik)
    labs = [c.label(e) for e in sorted(reps) if c.label(e) in c.WINDOW]
    dup = [k for k, v in collections.Counter(labs).items() if v > 1]
    if dup:
        lap.append((r["ticker"], dup))
    miss = [w for w in c.WINDOW if w not in labs]
    print("  %-5s 영업이익태그=%-5s 창내분기=%2d/%d 최신=%s 겹침=%s 빠진분기=%s"
          % (r["ticker"], opi, len(labs), len(c.WINDOW), max(sorted(reps)), dup or "-",
             (miss[:4] if len(miss) <= 4 else "%d개" % len(miss)) or "-"))
print("[4] 영업이익 태그 없음:", noopi or "0곳")
print("[5] 라벨 겹침:", lap or "0곳")
json.dump([[r.get("name"), r["ticker"], r["cik"]] for r in top],
          open("tmp_verify/us7/top31.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved tmp_verify/us7/top31.json")
