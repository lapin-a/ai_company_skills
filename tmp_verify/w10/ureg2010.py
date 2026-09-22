"""미국 라운드 1~31을 2010 창(collect_us_round1.WINDOW)으로 tmp_verify/w10/u2010/에 재생성 (원본은 건드리지 않는다). 라운드별 별도 프로세스."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = """
import sys, importlib; sys.path.insert(0, "us")
import collect_us_round1 as c
rnd = %d
if rnd > 1:
    importlib.import_module("collect_us_round%%d" %% rnd)
c.OUT = "us-round%%d-dataset.csv" %% rnd
c.OUTDIR = "tmp_verify/w10/u2010/"
c.main()
"""
for rnd in [int(a) for a in sys.argv[1:]] or range(1, 32):
    for attempt in range(2):  # SEC 503 일시 오류는 한 번 더 돌린다
        p = subprocess.run([sys.executable, "-c", C % rnd], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        open(os.path.join(ROOT, "tmp_verify/w10/u2010/us-round%d.log" % rnd), "w", encoding="utf-8").write(p.stdout + p.stderr)
        if p.returncode == 0:
            break
    print("미국 라운드 %d rc=%d" % (rnd, p.returncode), flush=True)
