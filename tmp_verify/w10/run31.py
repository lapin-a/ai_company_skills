"""시험: 미국 라운드 31을 10년 창(2016Q3~2026Q2, 40분기)으로 재생성. 원본은 건드리지 않는다."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "us")); os.chdir(ROOT)
import collect_us_round1 as c
c.WINDOW[:] = ["%dQ%d" % (y, q) for y in range(2016, 2027) for q in (1, 2, 3, 4) if (2016, 3) <= (y, q) <= (2026, 2)]
import collect_us_round31  # noqa: 라운드 설정
c.OUT = "w31-dataset.csv"; c.OUTDIR = "tmp_verify/w10/"
c.main()
