"""라운드 데이터셋을 회사별 파일로 나눈다. 실행: python split_by_company.py (저장소 루트에서)

원본은 라운드 파일(kr/data/roundN-*, us/data/us-roundN-*)이다. 이 스크립트가 만드는 by-company 폴더는
파생물이라 채택(데이터셋 교체) 뒤마다 다시 돌린다. 매번 폴더를 비우고 새로 쓴다.
  kr/data/by-company/<종목코드>.csv · <종목코드>-restated.csv (재작성 기록이 있는 회사만)
  us/data/by-company/<티커>.csv · <티커>-restated.csv
열은 라운드 파일과 같고 끝에 "라운드" 열을 더한다. 국내 금융(라운드 11~14)은 "항목세트" 열이 있는 그대로 둔다.
"""
import csv, glob, os, re, shutil

TRACKS = {"kr/data": r"round(\d+)-(dataset|restated)\.csv$", "us/data": r"us-round(\d+)-(dataset|restated)\.csv$"}

for folder, pat in TRACKS.items():
    out_dir = os.path.join(folder, "by-company")
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    files = {}  # 출력 경로 -> (머리행, 행 목록)
    for path in sorted(glob.glob(os.path.join(folder, "*.csv"))):
        m = re.search(pat, os.path.basename(path))
        if not m:
            continue
        rnd, kind = m.group(1), m.group(2)
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        head, i = rows[0], rows[0].index("종목코드")
        for r in rows[1:]:
            name = r[i] + ("-restated" if kind == "restated" else "") + ".csv"
            h, got = files.setdefault(os.path.join(out_dir, name), (head + ["라운드"], []))
            if h[:-1] != head:  # 한 회사가 머리행이 다른 두 라운드에 걸치면 섞지 않는다
                raise SystemExit("머리행 불일치: %s (%s)" % (name, path))
            got.append(r + [rnd])
    for out, (h, got) in files.items():
        with open(out, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows([h] + got)
    n = sum(not p.endswith("-restated.csv") for p in files)
    print("%s: 회사 %d곳, 파일 %d개, 행 %d" % (out_dir, n, len(files), sum(len(g) for _, g in files.values())))
