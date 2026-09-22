"""시험: 국내 라운드 N을 창 지정으로 재생성. 사용: python runkr.py N 10y|base  (원본은 건드리지 않는다)"""
import sys; sys.path.insert(0, "kr")
import collect_round2 as c2
rnd, mode = int(sys.argv[1]), sys.argv[2]
if mode == "10y":
    c2.WINDOW[:] = ["%d.%02d" % (y, m) for y in range(2016, 2027) for m in (3, 6, 9, 12) if (2016, 9) <= (y, m) <= (2026, 6)]
__import__("collect_round%d" % rnd)
c2.OUT = "kr%d-%s-dataset.csv" % (rnd, mode); c2.OUTDIR = "tmp_verify/w10/"
c2.main()
