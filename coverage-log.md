# Coverage Log

수집 현황 요약과 확정된 규칙만 둔다. 부서별 상세 로그·진단 기록은 라운드 로그 파일에 쓴다.

- 라운드 1 상세: [round1-log.md](kr/logs/round1-log.md) — 삼성전자
- 라운드 2 상세: [round2-log.md](kr/logs/round2-log.md) — TOP 10 기업
- 라운드 3 상세: [round3-log.md](kr/logs/round3-log.md) — 규칙 결정 4건, 대형주 100 목록, TOP 10, QA
- 라운드 5 상세: [round5-log.md](kr/logs/round5-log.md) — 국내 20곳, 공용 파서 결함 7종 수정, KRX 키 접근 시험
- KRX 2019년 백필: [krx-backfill-log.md](kr/logs/krx-backfill-log.md) — 라운드 1~5 국내 2019년 시장데이터 567칸, 결측 라벨 45칸 정정 (2026-09-21)
- 라운드 4 상세: [round4-log.md](kr/logs/round4-log.md) — 이상치 D안 확정, 첨부판 보고서 선택 규칙, TOP 10, QA, 계산값 10건 재확인
- 미국 트랙: [us-round1-log.md](us/logs/us-round1-log.md) — S&P500 상위 후보 검증 (`us_probe.py`, `us-candidates.json`)
- 미국 라운드 2: [us-round2-log.md](us/logs/us-round2-log.md) — 후보 재확인(V 시총 범위·XOM 옛 CIK 27분기·UNH 판정 자료)
- 미국 라운드 3: [us-round3-log.md](us/logs/us-round3-log.md) — S&P500 분모 전환, 20곳, COST 분기 라벨 보완
- 미국 라운드 4: [us-round4-log.md](us/logs/us-round4-log.md) — 20곳, MRVL 옛 CIK 이어 붙임, UNP 매출 태그 기준 혼합 차단
- 미국 라운드 6: [us-round6-log.md](us/logs/us-round6-log.md) — 20곳, 상장 전 분기 처리 일반화, 비지배지분 추정, VRT 합병 전 제외, ABNB 후속 보고서 비교기간으로 보완
- 미국 라운드 16: [us-round16-log.md](us/logs/us-round16-log.md) — 20곳. **공용 코드 수정 2종**(회사 확장 태그 · 후속 보고서 비교기간)과 라운드 1~16 회귀. 미확인 93칸은 모두 회사 미공시분
- 미국 라운드 15: [us-round15-log.md](us/logs/us-round15-log.md) — 20곳, 미확인 0칸(첫 사례), 새 규칙·코드 수정 0건
- 미국 라운드 14: [us-round14-log.md](us/logs/us-round14-log.md) — 20곳, SEC 제출 메타 reportDate 오기 교정(ZTS·NOW 라벨 밀림), 라운드 1~13·15 회귀
- 미국 라운드 13: [us-round13-log.md](us/logs/us-round13-log.md) — 20곳, 16주 분기 수용(KR 32칸 복구)
- 미국 라운드 12: [us-round12-log.md](us/logs/us-round12-log.md) — 20곳, 새 규칙·코드 수정 0건
- 미국 라운드 11: [us-round11-log.md](us/logs/us-round11-log.md) — 20곳, 총자본 태그 대체(A)·전력회사 매출 태그(XEL)·분기 라벨 보완 확장(AZO)
- 미국 라운드 10: [us-round10-log.md](us/logs/us-round10-log.md) — 20곳, 금융·보험 판정 기준 정리(SIC 60~65·67), 영업이익 미공시 7곳
- 미국 라운드 9: [us-round9-log.md](us/logs/us-round9-log.md) — 20곳, SPY 306~385위 추가 검증, 메자닌 처리 3종 보완(WBD·HLT·AEP)
- 미국 라운드 8: [us-round8-log.md](us/logs/us-round8-log.md) — 20곳, SPY 236~305위 추가 검증, 새 규칙·코드 수정 0건
- 미국 라운드 7: [us-round7-log.md](us/logs/us-round7-log.md) — 20곳, SPY 171~235위 추가 검증(HCA 발굴), CEG 분사 전 제외, 중복 합산 사고와 복구(7절)
- 미국 라운드 5: [us-round5-log.md](us/logs/us-round5-log.md) — 20곳, SPY 111~170위 추가 검증(TMUS 발굴), ACN Class A만, UBER 비지배 태그
- **폴더 구조(2026-09-21 정리):** 국내는 `kr/`(스크립트 · `kr/data/` · `kr/logs/`), 미국은 `us/`(스크립트 · `us/data/` · `us/logs/`). 스크립트는 저장소 루트에서 실행한다(예: `python us/collect_us_round16.py`).
- 데이터셋: 국내 `kr/data/round1-dataset.csv` ~ `round5-dataset.csv` (5개) · 미국 `us/data/us-round1-dataset.csv` ~ `us-round16-dataset.csv` (16개). 라운드별 요약은 같은 이름의 `-summary.json`.
- 대형주 100 목록: `kr/largecap100.csv` (기준일 2026-09-16, 생성 `kr/build_largecap100.py`)
- 수집 스크립트 (국내): `collect_round1.py`(DART 재무 파서·공통 로직), `collect_market_round1.py`(시장데이터), `collect_round2.py`(수집 실행 본체), `collect_round3.py`·`collect_round4.py`·`collect_round5.py`(대상·출력 파일만 바꿔 collect_round2 재사용), `round4_probe.py`(후보 검증, 라운드 5도 재사용), `backfill_2019_krx.py`(KRX 오픈API로 2019년 시장 3항목 백필 · 수집기가 쓰는 `krx_market_rows`)
- 수집 스크립트 (미국): `us_probe.py`(후보 발굴·검증), `collect_us_round1.py`(수집 본체), `collect_us_round2.py`(원문 XBRL 보충·클래스 주식수·주석), `collect_us_round3.py`(분기 라벨 보완), `collect_us_round4.py`(MRVL 옛 CIK 이어 붙임), `collect_us_round5.py`(ACN Class A), `collect_us_round6.py`(VRT 합병 전 처리·ABNB 후속 보고서 보완), `collect_us_round7.py`(CEG 분사 전 처리), `collect_us_round8.py`·`collect_us_round9.py`·`collect_us_round10.py`·`collect_us_round11.py`·`collect_us_round12.py`·`collect_us_round13.py`·`collect_us_round14.py`·`collect_us_round15.py`·`collect_us_round16.py`(대상만 교체)
  - 라운드 4 이후 미국 스크립트는 1→2→3을 차례로 재사용한다. 공용 규칙은 모두 `collect_us_round1.py`에 있다.
- 검증 스크립트: `tmp_verify/outliers_kr.py`(이상치·부호전환, 국내·미국 공용), `tmp_verify/recheck_calc_kr.py`(국내 계산값 재확인), `tmp_verify/compare_kr.py`·`recheck_kr.py`(국내 재수집 비교)
  - 미국 트랙: `tmp_verify/us7/recheck*.py`(계산값 이상치 두 경로 재확인), `tmp_verify/us7/qa_recheck*.py`(브랜드 검수팀 재검증), `tmp_verify/us7/regq.py`·`regdiff.py`(공용 코드 수정 후 전 라운드 회귀·셀 단위 대조), `tmp_verify/us7/labelcheck.py`(라벨-기준일 정합성 전수 점검), `tmp_verify/us7/gapsum.py`(라운드별 결측 요약)

## 커버리지 요약

| 라운드 | 기업 | 종목코드 | 수집 분기 범위 | 값 있는 칸 | 데이터 없음 | 미확인 | 상태 |
|---|---|---|---|---:|---:|---:|---|
| 1 | 삼성전자 | 005930 | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| 2 | SK하이닉스 · 기아 · 두산에너빌리티 · 삼성물산 · 삼성전기 · 한화에어로스페이스 · 현대차 | 000660·000270·034020·028260·009150·012450·005380 | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| 2 | 삼성바이오로직스 | 207940 | 2020Q1~2026Q2 (2019 연결 미해당) | 298 | 32 | 0 | 완료 |
| 2 | LG에너지솔루션 | 373220 | 재무 2020Q4~ · 시장 2022Q1~ | 238 | 92 | 0 | 완료 |
| 2 | SK스퀘어 | 402340 | 2021Q4~2026Q2 (19) | 209 | 121 | 0 | 완료 |
| 3 | LG전자 · LS ELECTRIC · NAVER · POSCO홀딩스 · SK · 삼성SDI · 셀트리온 · 현대모비스 · 효성중공업 | 066570·010120·035420·005490·034730·006400·068270·012330·298040 | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| 3 | HD현대중공업 | 329180 | 재무 2020Q4~ · 시장 2021Q3~ | 244 | 86 | 0 | 완료 |
| 4 | HD한국조선해양 · HD현대일렉트릭 · HMM · LG화학 · SK이노베이션 · 고려아연 · 한국전력 · 한미반도체 · 한화오션 | 009540·267260·011200·051910·096770·010130·015760·042700·042660 | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| 4 | 두산 | 000150 | 2019Q1~2026Q2 (30) | 329 | 0 | 1 | 완료 |
| 5 | GS · HD현대 · KT · KT&G · LG · LG이노텍 · S-Oil · SK텔레콤 · 대한항공 · 삼성에스디에스 · 삼성중공업 · 카카오 · 포스코퓨처엠 · 한국항공우주 · 현대건설 · 현대글로비스 · 현대로템 · 현대오토에버 | 078930·267250·030200·033780·003550·011070·010950·017670·003490·018260·010140·035720·003670·047810·000720·086280·064350·307950 | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| 5 | LIG디펜스앤에어로스페이스 | 079550 | 2019Q1~2026Q2 (30) | 313 | 17 | 0 | 완료 (2019Q1~Q2 연결 미해당) |
| 5 | 한화시스템 | 272210 | 재무 2019Q4~ · 시장 2019Q4~ | 297 | 33 | 0 | 완료 |
| | **합계 51개 기업** | | 각 330칸 | **16,448** | **381** | **1** | |

- 값 있는 칸 **16,448** = 공시 9,827 · API 4,482 · 계산 2,139. (2026-09-21 KRX 2019년 백필 반영, 데이터셋 직접 집계)
- 2026-09-19 전체 재수집 검증(round4-log.md 9절): 라운드 4 미확인 9칸을 채웠다. 라운드 2 기아·LG에너지솔루션 지배 순이익 6칸은 총포괄이익 지배분이 들어가 있던 오류라서 순이익으로 고쳤다.
- 2026-09-19 2차 재수집 검증(round4-log.md 11절)에서 37칸을 더 고쳤다.
  - SK스퀘어 2022Q4 손익 3칸: 누적 열을 인식하지 못했다.
  - 삼성전기 2019Q2~2026Q2 순이익 28칸, 삼성SDI 2024Q3~2025Q4 순이익 6칸: 계속영업 지배분이 들어가 있었다 → 전체 순이익 지배분으로 고쳤다.
  - 칸 수 집계는 변동 없다.
- 데이터 없음 **381** = 최초 보고기간 전 224 + 상장 전 108 + 연결 미해당 48 + 직전 보고서 없음 1.
  - **소스 시작일 372칸은 0이 됐다.** KRX 오픈API로 2019년 시장데이터를 채웠다 (2026-09-21, [krx-backfill-log.md](kr/logs/krx-backfill-log.md)).
- 미확인 1 = 두산 2022Q2 지배지분 자본. 매각예정 기타포괄손익 6.2B의 지배·비지배 구분이 원문에 없다. (원래 미확인 10칸 중 9칸은 파서 수정으로 채웠다. round4-log.md 9절)
- 기업별 한 줄 집계는 round2-log.md "수치 재정리" 절 참조.

- 대형주 대비 진행률: **51 / 100 = 51.0%** (라운드 1~5 완료). 목록 확정됨(`largecap100.csv`, 기준일 2026-09-16, 100위 대덕전자 5.03조원).
- 구성: 비금융 81 (수집 완료 51, 미수집 30) · 금융 19 (항목 체계 준비 후 수집). 비금융 기준 진행률 51 / 81 = 63.0%.
- 국내 + 미국 누적: **351개 기업**, 값 있는 칸 **113,014** · 데이터 없음 **1,562** · 미확인 **1,254**. (데이터셋 직접 집계, 2026-09-21 라운드 16 + KRX 2019년 백필 + 라운드 1~16 회귀 재생성 반영)
  - 미확인 내역(2026-09-21 회귀 재생성 후 재집계): 국내 1(두산) · 미국 1,253. 이 중 **영업이익이 1,181칸(50곳, 전 구간 30칸인 곳 34)**으로 94%다. 회사가 영업이익 줄을 공시하지 않거나 일부 기간만 태그한 경우로, LLY 선례(2026-09-19 대표 결정)에 따라 미확인으로 두고 사유를 출처 열에 적는다.
    - 영업이익 전 구간(각 30칸) 34곳 = 1,020: ADM·ADP·BMY·CASY·COP·CTVA·CVX·DHI·DOW·DVN·EMR·ETN·FOXA·GE·HCA·IBM·JCI·JNJ·KLAC·LLY·MRK·MTD·NEM·NKE·NUE·OXY·PCAR·PFE·PHM·PSX·SRE·TJX·XOM·ZTS
    - 영업이익 일부 구간 16곳 = 161: ROK 25 · ROST 21 · LHX 17 · CVNA 17 · BIIB 17 · HON 11 · DE 11 · SLB 9 · COHR 8 · SHW 7 · FLEX 7 · BKR 6 · PPG 2 · VRT 1 · SYY 1 · GEHC 1
      - 라운드 16 규칙 2(후속 보고서 비교기간)로 22칸이 채워졌다. F는 0칸이 돼 목록에서 빠졌다.
    - 영업이익 외 73칸: WEC 15(2019·2020·2021 4분기 대차 + 순이익) · LHX 11 · MTD 8(dei 표지 주식수 없음) · SYY 8 · GEHC 7(분사 직후 첫 보고) · COHR 6(차액 766.8M 미설명) · A 3 · TGT 3 · ABNB 2 · MA·TMO·UNP·HWM·ECL·MNST·PCG·AEE·EIX 각 1 · 국내 두산 1
      - CHD 3칸·PHM 1칸은 라운드 16 공용 코드 수정으로 채워져 빠졌다.
    - DELL 2칸은 2026-09-20 공용 코드 수정으로 해소했다(us-round3-log.md 7절).
- 시장데이터는 전 기업 공통으로 2020-01-02 이전 분기를 받을 수 없다.

## 커버리지 요약 — 미국 트랙 (SEC EDGAR + Yahoo, 단위 USD)

데이터셋 `us-round1-dataset.csv`, 스크립트 `collect_us_round1.py`, 상세·규칙 [us-round1-log.md](us/logs/us-round1-log.md) 2~5절.

| 라운드 | 기업 | 티커 | 수집 분기 범위 | 값 있는 칸 | 데이터 없음 | 미확인 | 상태 |
|---|---|---|---|---:|---:|---:|---|
| US1 | NVIDIA | NVDA | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Apple | AAPL | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Alphabet | GOOGL | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (주식수는 XBRL 원문) |
| US1 | Microsoft | MSFT | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Amazon | AMZN | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Broadcom | AVGO | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (확장 태그 메자닌 반영) |
| US1 | Meta Platforms | META | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (주식수는 XBRL 원문) |
| US1 | Tesla | TSLA | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Micron | MU | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US1 | Eli Lilly | LLY | 2019Q1~2026Q2 (30) | 300 | 0 | 30 | 완료 (영업이익 미공시) |
| US2 | AMD | AMD | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US2 | Walmart | WMT | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US2 | Exxon Mobil | XOM | 2019Q1~2026Q2 (30) | 300 | 0 | 30 | 완료 (영업이익 미공시 · 2026Q2 새 CIK) |
| US2 | Visa | V | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (주식수 Class A만) |
| US2 | Johnson & Johnson | JNJ | 2019Q1~2026Q2 (30) | 300 | 0 | 30 | 완료 (영업이익 미공시) |
| US2 | Intel | INTC | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US2 | Mastercard | MA | 2019Q1~2026Q2 (30) | 329 | 0 | 1 | 완료 |
| US2 | AbbVie | ABBV | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US2 | Cisco | CSCO | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 |
| US2 | Palantir | PLTR | 재무·시장 2020Q3~ (24) | 263 | 67 | 0 | 완료 (상장 2020-09-30) |
| US3 | Oracle · Coca-Cola · Caterpillar · Dell · Lam Research · Applied Materials · P&G · Home Depot · Netflix · Palo Alto · Philip Morris · RTX · Arista · Texas Instruments | ORCL·KO·CAT·DELL·LRCX·AMAT·PG·HD·NFLX·PANW·PM·RTX·ANET·TXN | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US3 | Costco | COST | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (분기 라벨 순차 배정) |
| US3 | Chevron · Merck · GE Aerospace | CVX·MRK·GE | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시) |
| US3 | CrowdStrike | CRWD | 재무 2019Q1~ · 시장 2019Q2~ | 327 | 3 | 0 | 완료 (상장 2019-06) |
| US3 | Thermo Fisher | TMO | 2019Q1~2026Q2 (30) | 329 | 0 | 1 | 완료 |
| US4 | Marvell · Linde · Amgen · Verizon · Salesforce · Seagate · Qualcomm · Gilead · Analog Devices · Abbott · Disney · PepsiCo · McDonald's · AT&T · NextEra · Union Pacific | MRVL·LIN·AMGN·VZ·CRM·STX·QCOM·GILD·ADI·ABT·DIS·PEP·MCD·T·NEE·UNP | 2019Q1~2026Q2 (30) | 330씩 (DIS 329 · UNP 329) | 0 (DIS 1) | 0 (UNP 1) | 완료 (MRVL 2019Q1~2020Q4는 옛 CIK) |
| US4 | KLA · IBM · Eaton | KLAC·IBM·ETN | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시) |
| US4 | Deere | DE | 2019Q1~2026Q2 (30) | 319 | 0 | 11 | 완료 (영업이익 태그 2024-10까지) |
| US5 | T-Mobile · Western Digital · Boeing · Danaher · Uber · ServiceNow · Intuitive Surgical · Corning · Vertex · Booking · Fortinet · Lockheed · Accenture · S&P Global · Marathon Petroleum | TMUS·WDC·BA·DHR·UBER·NOW·ISRG·GLW·VRTX·BKNG·FTNT·LMT·ACN·SPGI·MPC | 2019Q1~2026Q2 (30) | 330씩 (UBER 327) | 0 (UBER 3) | 0 | 완료 (ACN 주식수 Class A만 · UBER 상장 2019-05) |
| US5 | ConocoPhillips · Pfizer · TJX · Newmont · Bristol Myers | COP·PFE·TJX·NEM·BMY | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시) |
| US6 | Valero · Parker-Hannifin · Medtronic · Altria · CVS · Starbucks · Lowe's · Stryker · Freeport · McKesson · Adobe · Southern · Quanta · Amphenol · General Dynamics | VLO·PH·MDT·MO·CVS·SBUX·LOW·SYK·FCX·MCK·ADBE·SO·PWR·APH·GD | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US6 | Phillips 66 · Automatic Data Processing | PSX·ADP | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시) |
| US6 | AppLovin | APP | 재무·시장 2021Q2~ | 239 | 91 | 0 | 완료 (상장 2021-04) |
| US6 | Airbnb | ABNB | 재무·시장 2020Q4~ | 251 | 77 | 2 | 완료 (2020Q4는 후속 보고서 비교기간, 주식수·시총 2칸 미확인) |
| US6 | Vertiv Holdings | VRT | 2020Q1~2026Q2 (26) | 285 | 44 | 1 | 완료 (2019년은 합병 전 SPAC → 데이터 없음, 대표 결정 2026-09-20) |
| US7 | Trane · Duke · Howmet · Marriott · Williams · CSX · 3M · Waste Mgmt · UPS · DoorDash · Lumentum · Datadog · Moody's · Intuit · Regeneron · Comcast | TT·DUK·HWM·MAR·WMB·CSX·MMM·WM·UPS·DASH·LITE·DDOG·MCO·INTU·REGN·CMCSA | 2019Q1~2026Q2 (30) | 330씩 (HWM 329 · DASH 254 · DDOG 307) | 0 (DASH 76 · DDOG 23) | 0 (HWM 1) | 완료 |
| US7 | HCA · Johnson Controls · Emerson | HCA·JCI·EMR | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시) |
| US7 | Constellation Energy | CEG | 2022Q1~2026Q2 (18) | 198 | 132 | 0 | 완료 (2022-02 분사 전 제외, 대표 결정) |
| US8 | Cintas · Mondelez · Cadence · Illinois Tool Works · Motorola Solutions · EOG · Northrop · Synopsys · Cummins · GM · FedEx · Kinder Morgan · Norfolk Southern · HPE | CTAS·MDLZ·CDNS·ITW·MSI·EOG·NOC·SNPS·CMI·GM·FDX·KMI·NSC·HPE | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US8 | Ross Stores · Carvana · SLB · Sherwin-Williams · Target · Ecolab | ROST·CVNA·SLB·SHW·TGT·ECL | 2019Q1~2026Q2 (30) | 309·313·321·323·327·329 | 0 | 21·17·9·7·3·1 | 완료 (영업이익·순이익 태그 없는 구간) |
| US9 | Warner Bros. Discovery · Colgate · Hilton · O'Reilly · Republic Services · Royal Caribbean · American Electric Power · United Rentals · Air Products · Boston Scientific · Targa · Moderna · TransDigm · Monolithic Power · Grainger · TE Connectivity · Cencora | WBD·CL·HLT·ORLY·RSG·RCL·AEP·URI·APD·BSX·TRGP·MRNA·TDG·MPWR·GWW·TEL·COR | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US9 | Honeywell · Coherent · PACCAR | HON·COHR·PCAR | 2019Q1~2026Q2 (30) | 319·316·300 | 0 | 11·14·30 | 완료 (영업이익 태그 없는 구간 · COHR 대차 6칸) |
| US10 | ONEOK · Comfort Systems · Teradyne · NXP · Keysight · Fastenal · Dominion · AMETEK · Diamondback · Garmin · Ford · Cardinal Health · Delta | OKE·FIX·TER·NXPI·KEYS·FAST·D·AME·FANG·GRMN·F·CAH·DAL | 2019Q1~2026Q2 (30) | 330씩 (NXPI 307) | 0 (NXPI 23) | 0 | 완료 |
| US10 | Occidental · Nucor · Corteva · Devon · Sempra · NIKE · Baker Hughes | OXY·NUE·CTVA·DVN·SRE·NKE·BKR | 2019Q1~2026Q2 (30) | 300씩 (CTVA 297 · BKR 324) | 0 (CTVA 3) | 30씩 (BKR 6) | 완료 (영업이익 미공시) |
| US11 | Edwards · eBay · Ciena · Becton Dickinson · Wabtec · Vistra · Workday · Entergy · PayPal · Block · Autodesk · Xcel · IQVIA · Exelon | EW·EBAY·CIEN·BDX·WAB·VST·WDAY·ETR·PYPL·XYZ·ADSK·XEL·IQV·EXC | 2019Q1~2026Q2 (30) | 330씩 (CIEN 329) | 0 (CIEN 1) | 0 | 완료 |
| US11 | Carrier Global | CARR | 2020Q1~2026Q2 (26) | 286 | 44 | 0 | 완료 (2020-04 분사 전 제외) |
| US11 | AutoZone | AZO | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (분기 라벨 순차 배정, 2026-09-20 대표 결정) |
| US11 | Rockwell · L3Harris · Agilent · Monster | ROK·LHX·A·MNST | 2019Q1~2026Q2 (30) | 305·302·327·329 | 0 | 25·28·3·1 | 완료 (영업이익 등 태그 없는 구간) |
| US12 | Chipotle · Keurig Dr Pepper · Veeva · Waters · Paychex · IDEXX · MSCI · Microchip · Live Nation · ConEd · NetApp · Take-Two · Yum · Roper · Axon · Old Dominion | CMG·KDP·VEEV·WAT·PAYX·IDXX·MSCI·MCHP·LYV·ED·NTAP·TTWO·YUM·ROP·AXON·ODFL | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US12 | Archer-Daniels-Midland · D.R. Horton · Flex · Sysco | ADM·DHI·FLEX·SYY | 2019Q1~2026Q2 (30) | 300·300·323·320 | 0 (SYY 1) | 30·30·7·9 | 완료 (영업이익 태그 없는 구간 · SYY 2021Q2) |
| US13 | United Airlines · PSEG · Hershey · Estee Lauder · Steel Dynamics · DexCom · Expedia · EMCOR · Kimberly-Clark · ResMed · Jabil · EQT · Vulcan · HP | UAL·PEG·HSY·EL·STLD·DXCM·EXPE·EME·KMB·RMD·JBL·EQT·VMC·HPQ | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US13 | Kroger | KR | 2019Q1~2026Q2 (30) | 330 | 0 | 0 | 완료 (16주 1분기 수용, 32칸 복구) |
| US13 | PG&E · WEC Energy · Biogen | PCG·WEC·BIIB | 2019Q1~2026Q2 (30) | 329·315·313 | 0 | 1·15·17 | 완료 (태그 없는 구간) |
| US13 | TKO Group | TKO | 2023Q3~2026Q2 (12) | 131 | 199 | 0 | 완료 (최초 보고기간 2023Q3) |
| US13 | Kenvue | KVUE | 2023Q1~2026Q2 (14) | 151 | 179 | 0 | 완료 (최초 보고기간 2023Q1, 상장 2023-05) |
| US14 | Carnival · Martin Marietta · Kraft Heinz · Cognizant · Halliburton · Teledyne · Ingersoll Rand · VeriSign · ON Semi · Quest Diagnostics · EchoStar · Copart · Atmos · American Water · Dollar General | CCL·MLM·KHC·CTSH·HAL·TDY·IR·VRSN·ON·DGX·ECHO·CPRT·ATO·AWK·DG | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US14 | Zoetis · Fox | ZTS·FOXA | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 미공시 · ZTS는 제출 메타 오기 교정) |
| US14 | Mettler-Toledo | MTD | 2019Q1~2026Q2 (30) | 292 | 0 | 38 | 완료 (영업이익 30 · dei 표지 주식수 없는 4분기 8칸) |
| US14 | Ameren | AEE | 2019Q1~2026Q2 (30) | 329 | 0 | 1 | 완료 (2019Q4 매출 태그 불일치) |
| US14 | GE HealthCare | GEHC | 2022Q4~2026Q2 (15) | 157 | 165 | 8 | 완료 (2023-01 분사, 최초 보고기간 2022Q4) |
| US15 | DTE · Williams-Sonoma · FirstEnergy · Corpay · Labcorp · Las Vegas Sands · Super Micro · Eversource · West Pharm · Dover · Xylem · Fiserv · PPL · Incyte · CenterPoint · Expeditors · F5 · Darden · Hubbell | DTE·WSM·FE·CPAY·LH·LVS·SMCI·ES·WST·DOV·XYL·FISV·PPL·INCY·CNP·EXPD·FFIV·DRI·HUBB | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 |
| US15 | Otis Worldwide | OTIS | 2020Q1~2026Q2 (26) | 286 | 44 | 0 | 완료 (2020-04 분사 전 제외) |
| US16 | Ulta Beauty · Verisk · Tapestry · Global Payments · J.B. Hunt · Omnicom · NRG · IFF · First Solar · Dollar Tree · Packaging Corp · Fair Isaac · CMS Energy · Constellation Brands · Church & Dwight | ULTA·VRSK·TPR·GPN·JBHT·OMC·NRG·IFF·FSLR·DLTR·PKG·FICO·CMS·STZ·CHD | 2019Q1~2026Q2 (30) | 330씩 | 0 | 0 | 완료 (CHD는 2025 10-Q 회사 확장 태그, 9절) |
| US16 | Casey's · PulteGroup · Dow | CASY·PHM·DOW | 2019Q1~2026Q2 (30) | 300씩 | 0 | 30씩 | 완료 (영업이익 태그 없음) |
| US16 | Edison International | EIX | 2019Q1~2026Q2 (30) | 329 | 0 | 1 | 완료 (2021Q4 순이익 태그 불일치) |
| US16 | PPG Industries | PPG | 2019Q1~2026Q2 (30) | 328 | 0 | 2 | 완료 (FY2024·FY2025 10-K에 영업이익 태그 없음) |
| | **합계 300개 기업** | | 각 330칸 | **96,566** | **1,181** | **1,253** | |

- **분모(대표 결정 2026-09-20): S&P500 전체.** SPY 보유종목(2026-09-17) 종목 행 504개(클래스 중복 포함)를 분모로 쓴다. 진행률 **300 / 504 = 59.5%**. SPY 비중 상위 **475위**까지 업종 판정을 마쳤다(라운드 8에서 386~475위 추가, `tmp_verify/us7/probe13.py`).
  - 금융·리츠를 뺀 분모는 아직 정하지 않았다. 504개 전수 업종 조회가 필요하다. 지금까지 비중 상위 110위까지만 판정했고, 그 범위에서 금융 14곳·리츠 2곳·이력 미달 2곳을 뺐다(us-round3-log.md 1절).
  - 라운드 1·2는 상위 40위 안에서 골랐고, 그 기준으로는 20 / 32였다.
- **라운드 규모(대표 결정 2026-09-20): 20곳.** 라운드 1·2는 10곳이었다.
- 미국 라운드 3 데이터셋 `us-round3-dataset.csv`, 스크립트 `collect_us_round3.py`, 상세 [us-round3-log.md](us/logs/us-round3-log.md).
  - 라운드 3 규칙: 분기 라벨이 겹치는 회사(COST, 16주 4분기)는 회계분기 순서대로 연속된 달력 분기에 배정한다.
  - 공용 코드 수정 5건을 반영했다. 라운드 1·2 데이터셋을 다시 만들어 비교한 결과 차이 0칸이다.
- 미국 라운드 2 데이터셋 `us-round2-dataset.csv`, 스크립트 `collect_us_round2.py`(collect_us_round1 재사용), 상세 [us-round2-log.md](us/logs/us-round2-log.md) 2~4절.
  - 라운드 2 규칙: V 상장주식수는 Class A만 센다. XOM 2026Q2는 공동 제출 10-Q의 새 CIK 수치를 쓴다. companyfacts에 아직 없는 보고서는 원문 XBRL에서 읽는다.
  - 공용 코드 수정 5건(메자닌 이중 계산 등)을 반영했다. 라운드 1 데이터셋을 다시 만들어 비교한 결과 차이 0칸이다.
- 미국 트랙 전용 규칙(분기 라벨 = 가장 가까운 달력 분기말, 분할 역조정, 표지 주식수, 메자닌 포함 대차 검증, 회계연도 시작 기준 누적)은 us-round1-log.md 2·4절에 있다.
- 미국 라운드 13 규칙 — **16주 분기 수용(2026-09-21)**: 분기 태그와 영업CF 분기 판정의 기간 상한을 110일 → **118일**로 넓힌다. Kroger의 회계 1분기가 16주(112일)라 기존 상한에서 걸렸다. 4개월(120일 이상) 누적은 여전히 받지 않는다. KR 32칸 복구(us-round13-log.md 4절).
- 미국 라운드 14 규칙 — **SEC 제출 메타 `reportDate` 오기 교정(2026-09-21)**: `submissions` API의 보고기간 말일이 틀린 제출이 있다. 정상 분기 말일은 80일 이상 떨어지므로, **45일 이내로 붙은 말일 쌍**에 걸린 제출만 원문 표지의 `dei:DocumentPeriodEndDate`를 읽어 진짜 말일로 옮긴다(`collect_us_round1.py`의 `fix_report_dates`).
  - 전 라운드에서 걸린 건 2건: ZTS `0001555280-19-000221`(2019-08-06 → 2019-06-30), NOW `0001373715-18-000058`(2018-02-28 → 2017-12-31).
  - 두 건 모두 **라벨 겹침 → 순차 배정**을 잘못 발동시켜 해당 회사의 30개 분기 라벨을 통째로 한 칸씩 밀고 있었다. ZTS 315칸·NOW 330칸을 고쳤고, `us-round5-dataset.csv`·`us-round14-dataset.csv`를 다시 만들어 정본으로 채택했다.
  - 국내 5 + 미국 15 데이터셋 전체(331개 기업)에 같은 유형이 더 없는지 라벨-기준일 정합성을 전수 점검했다(`tmp_verify/us7/labelcheck.py`) → **0건**.
- 미국 라운드 16 규칙 — **읽기 경로가 놓친 칸 보완(2026-09-21)**, `collect_us_round2.py`. 상세 [us-round16-log.md](us/logs/us-round16-log.md) 9절.
  - **규칙 1 · 회사 확장 태그**: 항목의 태그 계열(매출·영업이익·순이익·영업CF)이 보고서에서 **통째로** 빠졌을 때만 XBRL 원문을 연다. 이름이 us-gaap 폐지 태그와 같아 뜻이 분명한 확장 태그(`ALIAS`)만 표준 이름으로 읽는다. 그 회사 원문에도 없으면 같은 계열로는 다시 열지 않는다.
  - **규칙 2 · 후속 보고서 비교기간**: 그래도 미확인인 손익 칸(4분기 제외)은 같은 기간이 비교기간으로 실린 다른 보고서에서 읽는다. **가장 먼저 낸 보고서**를 쓰고 값구분 `공시(후속 보고서 비교기간)`으로 구분한다. 라운드 6 ABNB 특례를 일반 규칙으로 올렸다.
  - **규칙 2는 재작성 미반영 원칙(진행 중 사항 5번)과 어긋나지 않는다.** 그 분기 보고서에 읽을 수 있는 값이 **아예 없을 때만** 작동하므로 원 공시값을 덮어쓰는 일이 없다. 실측 근거는 5번 항목에 적었다.

## 확정 규칙

### 대상 선정

1. **분모(대형주 100):** 유가증권시장 시가총액 상위 100. 기준일은 라운드 선정 시점에 API로 조회 가능한 가장 최근 거래일로 정하고, 그 라운드 동안 고정한다. 라운드 2 기준일 2026-09-16.
2. **우선주 제외:** 종목명이 우선주 패턴(`우`, `우B`, `우C`, `1우`, `2우B`, `우(전환)` 등)으로 끝나면 제외. 보조 확인으로 단축코드 끝자리 ≠ 0. 두 규칙이 어긋나면 자동 판정하지 않고 "미확인"으로 두고 사람이 확인한다.
3. **리츠·인프라펀드 제외:** 종목명 패턴(`리츠`, `REIT`, `인프라` 등, "메리츠" 제외)으로 선별하고 사람이 확인한다.
4. **금융회사:** 분모에는 포함, 수집은 보류(별도 항목 체계 필요). 판별은 ① KSIC 65·66 또는 64992를 제외한 64, ② 연결재무제표에 금융형 표지(순이자이익·예수부채·보험계약부채·보험서비스결과·순보험손익) 존재 — 둘 중 하나.
5. **최소 수집 이력:** 최근 분기부터 끊김 없이 **12개 분기(3개년) 이상**. 재무제표와 시장데이터 모두 충족해야 한다. 미달이면 제외하고 다음 순위 기업으로 대체한다.
6. **라운드당 규모:** 10개 기업. 이미 수집한 기업은 다시 넣지 않는다.

### 수집 항목

- 재무 8항목: 분기별 매출액 · 분기별 영업이익 · 분기별 당기순이익(지배) · 분기별 영업활동현금흐름 · 분기말 자산총계 · 분기말 부채총계 · 분기말 총자본(자기자본) · 분기말 지배지분 자본
- 시장 3항목: 분기말 종가 · 분기말 상장주식수 · 분기말 시가총액
- 기간 2019Q1~2026Q2, 연결재무제표, 보통주, 단위 원.
- 총자본 = 연결 전체(회계검증용), 지배지분 자본 = 주주 몫(ROE 등 비율용).

### 값 만드는 방식

- **매출액·영업이익·당기순이익:** Q1~Q3는 보고서의 "3개월" 열 값(공시). Q4만 `연간 − 1~3분기 누적`(계산).
- **영업활동현금흐름:** Q1만 공시. Q2~Q4는 `당분기 누적 − 직전 분기 누적`(계산).
- **저량 항목(자산·부채·총자본·지배지분 자본):** 전 분기 공시값, 계산 없음.
- **최초 사업연도가 4분기에 시작한 회사:** 직전 분기 누적이 없으므로 연간 공시값을 그대로 그 분기 값으로 쓰고 "공시"로 표시한다. 이 값은 분기 전체가 아니라 회사가 존재한 기간만 담는다.
- 값은 각 보고서가 공시한 수치이며, 이후 재작성은 반영하지 않는다.
- **영업이익을 공시하지 않는 회사는 미확인으로 둔다 (LLY 선례 2026-09-19, 재확인 2026-09-21).** 계산해서 채우지 않는다.
  - 검토했다 기각한 안: `매출 − 매출원가 − 판관비`. 영업이익을 **공시하는** 회사에서 이 식을 계산해 공시값과 대조한 결과 네 곳 모두 과대 계상됐고 오차 폭도 제각각이다(`tmp_verify/us7/opicheck.py`, FY2024, 백만 달러).

    | 회사 | 공시 영업이익 | 매출−원가−판관비 | 차이 | 빠진 것 |
    |---|---:|---:|---:|---|
    | Apple | 123,216 | 154,586 | +25.5% | R&D 31,370 (차이와 정확히 일치) |
    | Microsoft | 109,433 | 163,399 | +49.3% | R&D 29,510 + 판매·마케팅(별도 태그) |
    | Home Depot | 21,526 | 24,560 | +14.1% | R&D 태그 없음. 감가상각·무형자산상각 |
    | Coca-Cola | 9,992 | 14,155 | +41.7% | 기타 영업비용 |

  - 기각 사유 3가지:
    1. 회사마다 빠지는 항목이 달라 한 식으로 맞출 수 없다(오차 14~49%).
    2. **검증할 기준값이 없다.** 이 식을 적용할 대상은 정의상 공시 영업이익이 없는 회사라, 오차를 확인할 방법이 원천적으로 없다.
    3. 계산조차 안 되는 회사가 있다(XOM은 `CostOfGoodsAndServicesSold` 계열 태그 자체가 없다). 영업 소계를 두지 않는 손익계산서 구조라 매출원가·판관비 구분도 기대한 형태로 없다.
  - 회사가 발표하지 않은 수치를 만들지 않는다는 원칙, 그리고 회사 간 비교 가능성을 지키는 쪽을 택했다.

### 보고서 선택

- DART 정기보고서(사업·반기·분기), 기간별 **최신 접수본**을 쓴다([기재정정] 포함).
- **분기별로 일반 판본을 우선 쓰고, 일반 판본이 없으면 첨부판([첨부정정]·[첨부추가])을 쓴다** (확정: round4-log.md 3절·6절). 첨부판은 연결재무제표 섹션이 없을 수 있어 일반 판본보다 후순위지만, 그 분기의 유일한 판본이면 제외하지 않는다.
  - 구현: `collect_round2.py`의 `pick_reports`, `round4_probe.py`의 `report_summary`·`gaps`.
- 보고서가 "연결재무제표 → 해당사항 없습니다"면 그 기간은 "데이터 없음(연결재무제표 미해당)".
- DART 웹 공시검색은 검색기간이 10년을 넘으면 결과가 비므로 기간을 쪼갠다.

### 라벨 인식 (파서)

라벨은 주석 표시((주3), (주석 4))와 앞 번호(Ⅰ., 1., (1))를 떼고 비교한다.

| 항목 | 인식 라벨 |
|---|---|
| 매출액 | 우선순위대로 매출액 → 매출 → 매출액및기타수익 → 수익(매출액) → 영업수익 → 영업수익및기타수익 → 수익 |
| 영업이익 | 영업이익 / 영업이익(손실) / 영업손익 / 영업손실 로 시작 |
| 자산·부채·자본 총계 | 자산(총계·계·합계), 부채(총계·계·합계), 자본(총계·계·합계) |
| 지배지분 순이익 | "…의 귀속" 행 아래 첫 비(非)비지배 행. 손익계산서 → 없으면 포괄손익계산서 |
| 지배지분 자본 | 재무상태표에서 "지배" 포함·"비지배" 제외 행 |
| 영업활동현금흐름 | "영업활동"으로 시작하고 "현금흐름" 포함 |

- 손익 항목은 **연결손익계산서 우선, 없거나 행이 빠지면 연결포괄손익계산서**에서 찾는다.
- 값은 행의 **숫자 셀 순서**로 읽는다(빈 칸·주석 칸이 섞여도 열이 밀리지 않는다). 3개월/누적 열은 머리행에 "누적"이 있을 때만 2열로 본다.
- 단위는 표의 "(단위 : 원/천원/백만원)" 표기를 따른다.

### 시장데이터 (공공데이터포털 주식시세 V2)

- 엔드포인트: `https://apis.data.go.kr/1160100/GetStockSecuritiesInfoService_V2/getStockPriceInfo_V2` (구 `service/...` 주소는 키가 있어도 403)
- 서비스키는 Encoding/Decoding 어느 쪽이 들어와도 한 번만 인코딩한다.
- **`endBasDt` 당일은 결과에서 제외된다.** 분기말 조회는 `beginBasDt = 분기말 − 14일`, `endBasDt = 분기말 + 1일`로 하고, 분기말 이하 최신 거래일을 쓴다.
- 분기말이 휴장일이면 직전 거래일 값을 쓰고, 실제 거래일을 기준일 열에 적는다.
- `likeSrtnCd`는 부분 일치라 단축코드 완전 일치로 한 번 더 거른다.
- 자체 검증: 종가 × 상장주식수 = 시가총액.
- 문서 점검(예측 표현 검색 등)은 `*`·`_`·백틱을 지운 뒤 수행한다. 강조표시가 단어를 쪼개 검색을 빠져나간 사례가 있었다.

### 결측 표시

빈칸을 두지 않는다. 값 열과 값구분 열을 함께 채운다.

| 표시 | 쓰는 경우 |
|---|---|
| ~~`데이터 없음(소스 서비스 시작일 2020-01-02 이전)`~~ | 2019년 시장데이터. **2026-09-21 KRX 백필로 국내는 0칸이 됐다.** 다른 소스에서 같은 상황이 생기면 그때 다시 쓴다 |
| `데이터 없음(API 최초 거래일 YYYY-MM-DD 이전)` | 상장 전 분기 시장데이터 |
| `데이터 없음(최초 보고기간 이전)` | 회사 설립·분할 전 분기 재무 |
| `데이터 없음(연결재무제표 미해당)` | 보고서가 연결재무제표 해당 없음이라고 밝힌 기간 |
| `데이터 없음(3분기 누적 보고서 없음)` / `(직전 분기 누적 보고서 없음)` | 계산에 필요한 직전 보고서가 없을 때 |

값구분 열에는 원인별 짧은 형태를 쓴다: `데이터 없음(최초 보고기간 전)` · `(연결 미해당)` · `(소스 시작일)` · `(상장 전)` · `(직전 보고서 없음)`.
| `미확인` | 위에 해당하지 않는데 값을 못 얻었을 때(파싱 실패, 자체 검증 실패 등) |

### 이상치 판정 (확정 2026-09-18)

계열 = 기업 × 항목. 관측 12개 이상인 계열만 본다.

- 아래 세 조건을 **모두** 만족할 때만 이상치로 표시한다.
  1. 직전 분기 대비 변화율의 로버스트 z(|변화율 − 중앙값| / (1.4826 × MAD)) > 3.5
  2. 절대 변화량 ≥ 계열 절대값 중앙값의 20%
  3. 직전 분기 값 ≥ 계열 절대값 중앙값의 20%
- 직전 분기 값이 0 이하인 구간은 변화율을 계산하지 않는다. 부호가 바뀐 분기(적자↔흑자)는 이상치와 섞지 않고 따로 센다.
  - **구현 명확화 (2026-09-19):** 양→음 구간도 변화율 분포(중앙값·MAD)와 이상치 후보에서 뺀다. 즉 직전·당기 모두 > 0인 구간만 계산한다.
  - 라운드 1~3 집계(189건)는 이 구간을 넣었고, 라운드 4 집계(60건)는 뺐다. 이 방식으로 통일했다.
  - 스크립트: `tmp_verify/outliers_kr.py` (국내 round1~4 전체 재집계).
- **현재 집계 (2026-09-19, 통일된 방식, 데이터 수정 반영):**
  - 국내 31개사 이상치 **235건**(계산값 36, 모두 재확인 끝, 계산 오류 0): 라운드 1 12 · 라운드 2 101 · 라운드 3 60 · 라운드 4 62
  - 국내 부호전환 488건: 영업이익 81 · 당기순이익(지배) 177 · 영업활동현금흐름 230
  - 미국 라운드 1 10개사 이상치 **76건**(계산값 18, 모두 재확인 끝) · 부호전환 19건
  - 미국 라운드 2 10개사 이상치 **45건**(계산값 17, 모두 재확인 끝, 계산 오류 0) · 부호전환 51건 (us-round2-log.md 5·6절)
  - 미국 라운드 3 20개사 이상치 **135건**(계산값 35, 모두 재확인 끝, 계산 오류 0) · 부호전환 101건 (us-round3-log.md 5·6절)
  - 미국 라운드 4 20개사 이상치 **151건**(계산값 40, 모두 재확인 끝, 계산 오류 0) · 부호전환 112건 (us-round4-log.md 5·6절)
  - 미국 라운드 5 20개사 이상치 **154건**(계산값 34, 모두 재확인 끝, 계산 오류 0) · 부호전환 177건 (us-round5-log.md 5·6절)
  - 미국 라운드 6 20개사 이상치 **100건**(계산값 21, 모두 재확인 끝, 계산 오류 0) · 부호전환 157건 (us-round6-log.md 5·6절)
  - 국내 라운드 5 20개사 이상치 **140건**(계산값 23, 모두 재확인 끝, 계산 오류 0) · 부호전환 372건 (round5-log.md 5·6절)
  - 미국 라운드 7 20개사 이상치 **178건**(계산값 48, 모두 재확인 끝, 계산 오류 0) · 부호전환 137건 (us-round7-log.md 5·6절)
  - 미국 라운드 8 20개사 이상치 **140건**(계산값 33, 모두 재확인 끝, 계산 오류 0) · 부호전환 136건 (us-round8-log.md 5·6절)
  - 미국 라운드 9 20개사 이상치 **146건**(계산값 36, 모두 재확인 끝, 계산 오류 0) · 부호전환 147건 (us-round9-log.md 5절)
  - 미국 라운드 10 20개사 이상치 **147건**(계산값 28, 모두 재확인 끝, 계산 오류 0) · 부호전환 179건 (us-round10-log.md 5·6절)
  - 미국 라운드 11 20개사 이상치 **130건**(계산값 29, 모두 재확인 끝, 계산 오류 0) · 부호전환 122건 (us-round11-log.md 5·6절)
  - 미국 라운드 12 20개사 이상치 **142건**(계산값 34, 모두 재확인 끝, 계산 오류 0) · 부호전환 148건 (us-round12-log.md 5·6절)
  - 미국 라운드 13 20개사 이상치 **106건**(계산값 23, 모두 재확인 끝, 계산 오류 0) · 부호전환 195건 (us-round13-log.md 5·6절)
  - 미국 라운드 14 20개사 이상치 **125건**(계산값 38, 모두 재확인 끝, 계산 오류 0) · 부호전환 114건 (us-round14-log.md 6절)
  - 미국 라운드 15 20개사 이상치 **113건**(계산값 34, 모두 재확인 끝, 계산 오류 0) · 부호전환 104건 (us-round15-log.md 5·6절)
  - 미국 라운드 16 20개사 이상치 **171건**(계산값 48 = 재무 33 + 시가총액 15, 재무 33건 모두 재확인 끝, 계산 오류 0) · 부호전환 219건 (us-round16-log.md 6·7절)
  - **라운드 1~16 회귀 재생성(2026-09-21) 뒤 재집계다.** 값이 바뀐 라운드(6·8·9·10·11·12·16)는 계산값 재확인을 다시 돌렸고 전부 일치, 계산 오류 0이다. 위 계산값 수는 재무 항목 기준이며 시가총액 계산값은 자체 검증으로 따로 확인한다.
- 이상치는 관찰 표시일 뿐이며, 값을 고치거나 빼지 않는다.

### 자체 검증

- 자산총계 = 부채총계 + 총자본
- 총자본 = 지배지분 자본 + 비지배지분(행이 없으면 0)
- 종가 × 상장주식수 = 시가총액
- 검증에 실패한 칸은 값을 넣지 않고 "미확인"으로 둔다.

### 접근 불가 소스 (재시도 불필요)

- ~~KRX 오픈API 401~~ → **2026-09-21 재확인: 7개 엔드포인트 모두 HTTP 200, 사용 가능해졌다.** 키·헤더(`AUTH_KEY`)는 2026-09-20과 같고 응답만 바뀌었다 — API 사용 승인이 난 것으로 보인다(승인 시점 미확인).
  - 2019년 시장데이터 **567칸을 채웠다**(국내 612칸 중). 상세 [krx-backfill-log.md](kr/logs/krx-backfill-log.md), 이전 401 기록은 [round5-log.md](kr/logs/round5-log.md) 0절.
  - 쓰는 엔드포인트: `sto/stk_bydd_trd`(코스피)·`sto/ksq_bydd_trd`(코스닥) 일별매매정보 — `TDD_CLSPRC`(종가)·`LIST_SHRS`(상장주식수)·`MKTCAP`(시가총액). `sto/stk_isu_base_info`는 상장일 확인용.
  - **코스피·코스닥을 함께 조회한다.** 2019년에 시장이 달랐던 기업이 있다(포스코퓨처엠 = 당시 포스코케미칼·코스닥).
  - **수집기 반영(2026-09-21):** `collect_round2.market_rows`가 2020-01-02 이전 분기를 KRX에서 받는다. 라운드 6부터 2019년 시장데이터가 처음부터 채워진다. 백필과 수집기가 같은 함수(`backfill_2019_krx.krx_market_rows`)를 쓰고, 국내 612칸으로 대조해 전부 일치했다.
  - **`sto/ksq_isu_base_info`(코스닥 종목 기본정보)만 아직 401이다.** 승인받은 7개에 없었다. 2019년 KRX 일별매매에 없는 코스닥 종목은 상장일을 확인할 수 없어 `미확인`으로 둔다(추측으로 상장 전을 붙이지 않는다). 지금 데이터셋엔 해당 칸이 없다.
- ~~SEC 연결 불가~~ → **2026-09-19 재확인: `data.sec.gov`(submissions·companyfacts)·`efts.sec.gov` 접근 가능.** `www.sec.gov`도 **Python urllib로는 접근 가능**하다(curl만 실패, 000). 원문 XBRL(`Archives/…/*_htm.xml`)은 urllib로 받는다. 상세 [us-round1-log.md](us/logs/us-round1-log.md) 8절
- KRX (`data.krx.co.kr`, `kind.krx.co.kr`, `openapi.krx.co.kr`), 네이버 금융: ~~연결 불가~~ → 2026-09-19 재확인(Python urllib). `data.krx.co.kr`은 접속되지만 로그인이 필요하다. `kind.krx.co.kr`은 접속된다. 네이버 `fchart` 차트 API는 접근된다(비공식, 종가만 제공). KRX API 키는 `.claude/settings.local.json`의 `env.KRX_API_KEY`에 등록돼 있고, 2026-09-21부터 `data-dbg.krx.co.kr` 오픈API가 열렸다(위 항목). 2019년 시장데이터는 그것으로 채웠다.
- 증권상품시세(ETF) API: 이번 프로젝트 수집 대상 아님

## 진행 중 사항 (다음 라운드로 넘김)

1. ~~라운드 3 성과리뷰~~ → 완료. **라운드 4**도 완료(성과리뷰·계산값 10건 재확인 끝, round4-log.md). **미국 라운드 1**도 완료(성과리뷰·계산값 17건 재확인 끝, 오류 0, us-round1-log.md 6·7절).
9. ~~라운드 4 LG화학 미확인 1칸~~ → 원인은 매출 라벨 "매출및기타수익"이었다. 채웠다(round4-log.md 9절).
11. ~~라운드 2 순이익 6칸 수정의 후속~~ → 이상치·부호전환을 재집계했다(round4-log.md 10절). 집계 방식 불일치(라운드 1~3과 라운드 4)도 발견해서 통일했다. 위 "이상치 판정" 절 참조.
12. ~~라운드 1~3 계산값 이상치 28건 재확인~~ → 완료(round4-log.md 11절).
    - 파서 결함 2건을 찾아 고쳤다(누적 열 `&nbsp;`, 계속영업이익 귀속). 데이터 37칸을 반영하자 계산값 이상치는 26건이 됐다.
    - 라운드 4 10건도 3개월 합산으로 재확인했다. 계산 오류는 0이다.
    - 남은 불일치는 반올림 2건과 HMM 2023 재작성 1건이다.
10. **미국 트랙 미결 사항** (us-round1-log.md 1·5절)
    - ~~GOOGL·META 상장주식수·시가총액 미확인 120칸~~ → XBRL 원문으로 채웠다(2026-09-19, us-round1-log.md 8절).
    - ~~AVGO 대차 차이 28백만 달러~~ → 원인은 우선주 배당 의무(회사 확장 태그 메자닌)다. 반영해서 채웠다(8절).
    - 남은 미국 미확인: LLY·XOM·JNJ 영업이익 각 30칸(회사가 영업이익을 공시하지 않음), MA 2019Q4 순이익 1칸.
    - ~~XOM 승계 CIK 처리, V 시총 확인~~ → 라운드 2에서 처리했다(us-round2-log.md 2~4절). **UNH 금융 판정**은 남아 있다.
    - Yahoo 비공식 API 의존(자동화 운영팀). ~~SEC User-Agent 연락처~~ → 결정: `lapin sirocuro01@gmail.com` (2026-09-19, `us_probe.SEC_UA`).
    - S&P500 전체 분모 확정.
8. ~~이상치 규칙 최종안~~ → **확정: D안 (2026-09-18).** 21개 기업(라운드 1~3) 재적용 결과:

   | 규칙 | 21개사 | 11개사(라운드 1·2) |
   |---|---:|---:|
   | A. 현행 (변화율 z > 3.5) | 298건 | 170건 |
   | B. 결정 3 (z + 절대변화 ≥ 계열 중앙값 20%) | 251건 | 145건 |
   | C. 참고 (z + 직전 분기 값 ≥ 중앙값 20%) | 232건 | 147건 |
   | **D. B+C 동시 → 확정 규칙** | **189건** | **123건** |

   - 부호 전환(적자↔흑자, 이상치와 분리 집계): 21개사 279건 = 영업활동현금흐름 144 + 당기순이익(지배) 97 + 영업이익 38. (11개사 148건 = 92 + 40 + 16)
   - 상세는 round3-log.md.
13. ~~영업이익 미확인 1,111칸을 계산으로 채울지~~ → **결정: 채우지 않는다 (가), 2026-09-21.** 위 "값 만드는 방식" 절에 근거와 기각한 계산안을 적었다. 이 항목은 닫혔다.

2. **금융회사 수집** — 항목 세트는 결정됨(영업수익·순이자이익·순수수료이익 + 공통 7항목, round3-log.md 결정 2). 대상 19개 기업은 별도 라운드로 수집한다.
3. ~~대형주 100 목록 확정~~ → 완료: `largecap100.csv` (2026-09-18).
4. **상장주식수 변동 사유** — 삼성전자 2025Q1·2026Q2 감소는 API 원값 확인만 했고 사유는 미확인.
5. **재작성(restatement) 반영 여부** — 현재는 반영하지 않는다. 각 분기 값은 **그 분기 보고서**에서 읽고, 나중 보고서의 재작성 숫자로 덮어쓰지 않는다.
   - 실제 사례: HMM 2023Q1 지배 순이익은 처음 공시값이 285,402백만인데, 2분기 보고서에서 297,612백만으로 재작성됐다.
   - 그래서 1~4분기 합(4분기는 재작성이 반영된 9개월 누적으로 계산)이 연간값과 12,210백만 어긋난다(round4-log.md 11절).
   - **라운드 16 규칙 2와의 관계 — 정리됨 (2026-09-21).** 규칙 2는 나중 보고서에서 값을 가져오지만, 그 분기 보고서에 읽을 수 있는 값이 아예 없을 때만 작동한다. 덮어쓸 원 공시값이 없으므로 이 원칙과 충돌하지 않는다. "가장 먼저 낸 보고서"를 써서 원 공시에 가장 가까운 숫자를 고른다.
     - **실측(`tmp_verify/us7/restate16.py`):** 해당 값구분 28칸마다 그 기간이 실린 보고서를 전부 모아 값을 비교했다.
     - **26칸은 모든 보고서의 값이 같다** — 재작성이 없었고, 규칙 2는 원 공시와 같은 숫자를 썼다.
     - **2칸(ABNB 2020Q4 총자본·지배지분 자본)만 둘로 갈린다.** 2021-05~2022-11 보고서 7건은 2,901,783,000, FY2022 10-K(2023-02) 이후는 2,901,000,000이다. ABNB가 이때 공시 단위를 천 달러 → 백만 달러로 바꿨다. 반올림이면 2,902M이어야 해서 단순 반올림은 아니다(합계 맞춤 조정 또는 소폭 재작성, 미확인). **"가장 먼저 낸 보고서" 규칙이 원래의 정밀한 값 2,901,783,000을 골랐다** — 의도대로 작동했다.
   - **남은 질문(대표 결정 필요):** HMM처럼 **원 공시값이 있는데 나중에 재작성된 경우**에 재작성값을 쓸지는 여전히 열려 있다. 지금은 원 공시값을 쓴다.
6. ~~이상치 규칙 보완~~ → **확정 (2026-09-18): D안.** 아래 "이상치 판정" 절 참조. 21개 기업 기준 189건(당시 방식). 통일된 방식으로는 174건이다(2026-09-19).
7. ~~별도재무제표 수집 여부~~ → 결정: 연결 원칙 유지, 별도로 채우지 않는다 (round3-log.md 결정 4).

14. ~~미국 라운드 16 — 읽기 경로가 놓친 칸, 공용 코드 수정 여부~~ → **완료 (2026-09-21).** 규칙 2종(회사 확장 태그 · 후속 보고서 비교기간)을 `collect_us_round2.py`에 넣었다. 라운드 1~16 회귀 재생성·채택까지 끝났고 **기존 값 변경 0건, 개선 28칸**이다. 상세 [us-round16-log.md](us/logs/us-round16-log.md) 9절
    - CHD 2025Q1~Q3 영업활동현금흐름 3칸: 회사 확장 태그 `chd:NetCashProvidedByOperatingActivities`. companyfacts에 안 실리고, 원문 대체 경로는 "사실 20개 미만"에서만 발동한다.
    - PHM 2021Q1 매출액 1칸: 그 10-Q의 매출 사실이 전부 차원(세그먼트) 부착이라 무차원 연결 총계가 없다.
    - 두 값 모두 회사의 **다음 해 보고서 비교열에 표준 태그로** 실려 있어 확인된다. 고치려면 `Facts.find`의 원문 대체 조건을 넓혀야 하고, 라운드 14 선례대로 전 라운드(국내 5 + 미국 16) 회귀 검사가 따라붙는다.
    - 상세 us-round16-log.md 5절.

15. ~~2019년 국내 시장데이터 372칸~~ → **완료 (2026-09-21).** KRX 오픈API 사용 승인이 확인돼 567칸을 채웠고, 남은 45칸은 상장 전이라 라벨을 바로잡았다. `데이터 없음(소스 시작일)`은 0이 됐다. 상세 [krx-backfill-log.md](kr/logs/krx-backfill-log.md)

## 로그 작성 규칙

- 라운드별 상세 기록(부서별 보고, 진단, 원문 대조)은 `roundN-log.md`에 쓴다.
- coverage-log.md에는 라운드당 요약 한두 줄과 규칙 변경만 남긴다.
