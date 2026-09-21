"""재작성 반영 회귀: 국내 라운드 1~10 · 미국 라운드 1~16을 tmp_verify/restate/에 재생성한다 (원본 데이터셋은 건드리지 않는다).
한 라운드씩 별도 프로세스로 돌린다(모듈 전역 상태 공유 방지). 사용: python tmp_verify/restate/regen.py kr|us [라운드...]"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = "tmp_verify/restate/"

KR = """
import sys; sys.path.insert(0, "kr")
import collect_round2 as c2
rnd = %d
if rnd == 1:  # 라운드 1은 삼성전자 한 곳 (collect_round1.py가 원래 수집, 지금은 c2 본체로 재생성)
    c2.TOP10 = [("삼성전자", "005930", "00126380")]
elif rnd > 2:
    __import__("collect_round%%d" %% rnd)
c2.OUT = "round%%d-dataset.csv" %% rnd
c2.OUTDIR = %r
c2.main()
"""
US = """
import sys, importlib; sys.path.insert(0, "us")
import collect_us_round1 as c
rnd = %d
if rnd > 1:
    importlib.import_module("collect_us_round%%d" %% rnd)
c.OUT = "us-round%%d-dataset.csv" %% rnd
c.OUTDIR = %r
c.main()
"""

if __name__ == "__main__":
    track = sys.argv[1]
    rounds = [int(a) for a in sys.argv[2:]] or list(range(1, 11 if track == "kr" else 17))
    for rnd in rounds:
        src = (KR if track == "kr" else US) % (rnd, OUT)
        p = subprocess.run([sys.executable, "-c", src], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        name = ("round%d" if track == "kr" else "us-round%d") % rnd
        open(os.path.join(ROOT, OUT, name + ".log"), "w", encoding="utf-8").write(p.stdout + p.stderr)
        tail = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith(("재작성 기록", "rows:", "Traceback"))]
        print("%s %s 재생성 rc=%d %s" % (track, rnd, p.returncode, " | ".join(tail)), flush=True)
