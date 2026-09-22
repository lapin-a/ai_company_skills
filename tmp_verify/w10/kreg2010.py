"""국내 회귀: 라운드 1~14를 2010 창으로 tmp_verify/w10/k2010/에 재생성 (원본은 건드리지 않는다). 라운드별 별도 프로세스."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = """
import sys; sys.path.insert(0, "kr")
import collect_round2 as c2
c2.OUTDIR = "tmp_verify/w10/k2010/"
rnd = %d
if rnd >= 11:
    import collect_fin; collect_fin.main(rnd)
else:
    if rnd == 1: c2.TOP10 = [("삼성전자", "005930", "00126380")]
    elif rnd > 2: __import__("collect_round%%d" %% rnd)
    c2.OUT = "round%%d-dataset.csv" %% rnd
    c2.main()
"""
for rnd in [int(a) for a in sys.argv[1:]] or range(1, 15):
    for attempt in range(2):  # 일시 연결 오류는 한 번 더 돌린다
        p = subprocess.run([sys.executable, "-c", C % rnd], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        open(os.path.join(ROOT, "tmp_verify/w10/k2010/round%d.log" % rnd), "w", encoding="utf-8").write(p.stdout + p.stderr)
        if p.returncode == 0:
            break
    print("라운드 %d rc=%d" % (rnd, p.returncode), flush=True)
