# 국내 회귀 대조: 라운드 1~14 dataset·restated를 원본과 비교
export PYTHONIOENCODING=utf-8
for n in $(seq 1 14); do
  echo "R$n $(python tmp_verify/w10/cmp.py tmp_verify/w10/kreg/round$n-dataset.csv kr/data/round$n-dataset.csv 2>&1 | head -1) | 재작성 기록 차이 $(diff <(sort kr/data/round$n-restated.csv) <(sort tmp_verify/w10/kreg/round$n-restated.csv) | grep -c '^[<>]')"
done
