"""공용 코드 수정 회귀 검사: 미국 라운드 1~16 재생성 후 원본과 대조.
원본 데이터셋은 건드리지 않는다. 결과는 tmp_verify/us7/qd<N>-dataset.csv.
한 라운드씩 별도 프로세스로 돌린다(모듈 전역 상태 공유 방지)."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.path.join(ROOT, "tmp_verify", "us7")

CHILD = """
import sys, importlib
sys.path.insert(0, %r)
import os
os.chdir(%r)
import collect_us_round1 as c
rnd = %d
if rnd > 1:
    importlib.import_module("collect_us_round%%d" %% rnd)  # 라운드 모듈이 c를 설정·확장한다
c.OUT = %r
c.OUTDIR = "tmp_verify/us7/"
c.main()
"""

if __name__ == "__main__":
    rounds = [int(a) for a in sys.argv[1:]] or list(range(1, 32))
    for rnd in rounds:
        src = CHILD % (os.path.join(ROOT, "us"), ROOT, rnd, "qd%d-dataset.csv" % rnd)
        p = subprocess.run([sys.executable, "-c", src], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        open(os.path.join(TMP, "qd%d.log" % rnd), "w", encoding="utf-8").write(p.stdout + p.stderr)
        print("라운드 %d 재생성 rc=%d" % (rnd, p.returncode), flush=True)
