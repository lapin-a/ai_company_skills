# Coverage Log — 미국 트랙 (SEC EDGAR + Yahoo, 단위 USD)

미국 수집 현황 요약과 미국 전용 규칙만 둔다. 공통 규칙과 국내+미국 누적 합계는 [../coverage-log.md](../coverage-log.md), 국내 트랙은 [../kr/coverage-log.md](../kr/coverage-log.md).

- 미국 트랙: [us-round1-log.md](logs/us-round1-log.md) — S&P500 상위 후보 검증 (`us_probe.py`, `us-candidates.json`)
- 미국 라운드 2: [us-round2-log.md](logs/us-round2-log.md) — 후보 재확인(V 시총 범위·XOM 옛 CIK 27분기·UNH 판정 자료)
- 미국 라운드 3: [us-round3-log.md](logs/us-round3-log.md) — S&P500 분모 전환, 20곳, COST 분기 라벨 보완
- 미국 라운드 4: [us-round4-log.md](logs/us-round4-log.md) — 20곳, MRVL 옛 CIK 이어 붙임, UNP 매출 태그 기준 혼합 차단
- 미국 라운드 6: [us-round6-log.md](logs/us-round6-log.md) — 20곳, 상장 전 분기 처리 일반화, 비지배지분 추정, VRT 합병 전 제외, ABNB 후속 보고서 비교기간으로 보완
- **재작성 반영 (2026-09-21):** 라운드 1~16 재생성·채택. 재작성 반영 709칸 · 재분류(미반영) 796 · 재작성 검증 실패(원 공시 유지) 503. 기록은 `data/us-roundN-restated.csv`, 규칙은 [../coverage-log.md](../coverage-log.md) 5번. 칸 수(값·데이터 없음·미확인)는 그대로다. 이상치는 라운드 1~16 전체 2,064 → **2,076건**(계산값 569), 부호전환 2,118 → **2,121**.
- 미국 라운드 17~30: [us-round17-30-log.md](logs/us-round17-30-log.md) — **5곳 단위** 14개 라운드, 69곳. APA 옛 CIK(재편 뒤에도 옛 CIK가 계속 보고) · GPC XBRL 없는 정정본 가짜 분기, 둘 다 라운드 스크립트 안에서 처리. **분사를 분할로 처리한 시가총액 15칸(기존 9 포함) 발견, 결정 대기**
- 미국 라운드 31: [us-round31-log.md](logs/us-round31-log.md) — 5곳(BE·ILMN·P·LDOS·ROL), 미확인 10칸. 재작성 검증 실패 시 저량 항목이 섞이는 공용 코드 버그 수정, 라운드 1~31 회귀로 71칸 원 공시 복귀
- 미국 라운드 16: [us-round16-log.md](logs/us-round16-log.md) — 20곳. **공용 코드 수정 2종**(회사 확장 태그 · 후속 보고서 비교기간)과 라운드 1~16 회귀. 미확인 93칸은 모두 회사 미공시분
- 미국 라운드 15: [us-round15-log.md](logs/us-round15-log.md) — 20곳, 미확인 0칸(첫 사례), 새 규칙·코드 수정 0건
- 미국 라운드 14: [us-round14-log.md](logs/us-round14-log.md) — 20곳, SEC 제출 메타 reportDate 오기 교정(ZTS·NOW 라벨 밀림), 라운드 1~13·15 회귀
- 미국 라운드 13: [us-round13-log.md](logs/us-round13-log.md) — 20곳, 16주 분기 수용(KR 32칸 복구)
- 미국 라운드 12: [us-round12-log.md](logs/us-round12-log.md) — 20곳, 새 규칙·코드 수정 0건
- 미국 라운드 11: [us-round11-log.md](logs/us-round11-log.md) — 20곳, 총자본 태그 대체(A)·전력회사 매출 태그(XEL)·분기 라벨 보완 확장(AZO)
- 미국 라운드 10: [us-round10-log.md](logs/us-round10-log.md) — 20곳, 금융·보험 판정 기준 정리(SIC 60~65·67), 영업이익 미공시 7곳
- 미국 라운드 9: [us-round9-log.md](logs/us-round9-log.md) — 20곳, SPY 306~385위 추가 검증, 메자닌 처리 3종 보완(WBD·HLT·AEP)
- 미국 라운드 8: [us-round8-log.md](logs/us-round8-log.md) — 20곳, SPY 236~305위 추가 검증, 새 규칙·코드 수정 0건
- 미국 라운드 7: [us-round7-log.md](logs/us-round7-log.md) — 20곳, SPY 171~235위 추가 검증(HCA 발굴), CEG 분사 전 제외, 중복 합산 사고와 복구(7절)
- 미국 라운드 5: [us-round5-log.md](logs/us-round5-log.md) — 20곳, SPY 111~170위 추가 검증(TMUS 발굴), ACN Class A만, UBER 비지배 태그
- 수집 스크립트 (미국): `us_probe.py`(후보 발굴·검증), `collect_us_round1.py`(수집 본체), `collect_us_round2.py`(원문 XBRL 보충·클래스 주식수·주석), `collect_us_round3.py`(분기 라벨 보완), `collect_us_round4.py`(MRVL 옛 CIK 이어 붙임), `collect_us_round5.py`(ACN Class A), `collect_us_round6.py`(VRT 합병 전 처리·ABNB 후속 보고서 보완), `collect_us_round7.py`(CEG 분사 전 처리), `collect_us_round8.py`·`collect_us_round9.py`·`collect_us_round10.py`·`collect_us_round11.py`·`collect_us_round12.py`·`collect_us_round13.py`·`collect_us_round14.py`·`collect_us_round15.py`·`collect_us_round16.py`(대상만 교체)
  - 라운드 4 이후 미국 스크립트는 1→2→3을 차례로 재사용한다. 공용 규칙은 모두 `collect_us_round1.py`에 있다.
- 검증 스크립트: `tmp_verify/us7/recheck*.py`(계산값 이상치 두 경로 재확인), `tmp_verify/us7/qa_recheck*.py`(브랜드 검수팀 재검증), `tmp_verify/us7/regq.py`·`regdiff.py`(공용 코드 수정 후 전 라운드 회귀·셀 단위 대조), `tmp_verify/us7/labelcheck.py`(라벨-기준일 정합성 전수 점검), `tmp_verify/us7/gapsum.py`(라운드별 결측 요약)

## 커버리지 요약

데이터셋 `us-round1-dataset.csv`, 스크립트 `collect_us_round1.py`, 상세·규칙 [us-round1-log.md](logs/us-round1-log.md) 2~5절.

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
| US17~30 | 5곳씩 14개 라운드: EXE·LUV·LYB·STE·RL / BBY·VTRS·NI·GIS·AMCR / CF·SNA·EFX·BR·TSN / LEN·EVRG·FIS·IP·CDW / ZBH·CHRW·GEN·GPC·DD / NDSN·J·LNT·TSCO·FTV / ZBRA·IEX·NVR·NWSA·BALL / RVTY·APA·CHTR·AKAM·PTC / TYL·MAS·TXT·SWK·TRMB / SWKS·CRL·ALB·MKC·SJM / ALLE·AVY·LII·GNRC·GDDY / HAS·CSGP·IT·BAX·PNW / TECH·JKHY·HII·DECK·AES / COO·LULU·FDS·CLX | 69곳 | 2019Q1~2026Q2 (30) | 22,296 | 67 | 407 | 완료 (영업이익 태그 없음 8곳 · 상세 [us-round17-30-log.md](logs/us-round17-30-log.md)) |
| | **합계 369개 기업** | | 각 330칸 | **118,862** | **1,248** | **1,660** | |

- **분모(대표 결정 2026-09-20): S&P500 전체.** SPY 보유종목(2026-09-17) 종목 행 504개(클래스 중복 포함)를 분모로 쓴다. 진행률 **369 / 504 = 73.2%**(라운드 17~30 반영, 2026-09-21). SPY 비중 상위 **475위**까지 업종 판정을 마쳤다(라운드 8에서 386~475위 추가, `tmp_verify/us7/probe13.py`).
  - 금융·리츠를 뺀 분모는 아직 정하지 않았다. 504개 전수 업종 조회가 필요하다. 지금까지 비중 상위 110위까지만 판정했고, 그 범위에서 금융 14곳·리츠 2곳·이력 미달 2곳을 뺐다(us-round3-log.md 1절).
  - 라운드 1·2는 상위 40위 안에서 골랐고, 그 기준으로는 20 / 32였다.
- **라운드 규모(대표 결정 2026-09-20): 20곳.** 라운드 1·2는 10곳이었다.
- 미국 라운드 3 데이터셋 `us-round3-dataset.csv`, 스크립트 `collect_us_round3.py`, 상세 [us-round3-log.md](logs/us-round3-log.md).
  - 라운드 3 규칙: 분기 라벨이 겹치는 회사(COST, 16주 4분기)는 회계분기 순서대로 연속된 달력 분기에 배정한다.
  - 공용 코드 수정 5건을 반영했다. 라운드 1·2 데이터셋을 다시 만들어 비교한 결과 차이 0칸이다.
- 미국 라운드 2 데이터셋 `us-round2-dataset.csv`, 스크립트 `collect_us_round2.py`(collect_us_round1 재사용), 상세 [us-round2-log.md](logs/us-round2-log.md) 2~4절.
  - 라운드 2 규칙: V 상장주식수는 Class A만 센다. XOM 2026Q2는 공동 제출 10-Q의 새 CIK 수치를 쓴다. companyfacts에 아직 없는 보고서는 원문 XBRL에서 읽는다.
  - 공용 코드 수정 5건(메자닌 이중 계산 등)을 반영했다. 라운드 1 데이터셋을 다시 만들어 비교한 결과 차이 0칸이다.
- 미국 트랙 전용 규칙(분기 라벨 = 가장 가까운 달력 분기말, 분할 역조정, 표지 주식수, 메자닌 포함 대차 검증, 회계연도 시작 기준 누적)은 us-round1-log.md 2·4절에 있다.
- 미국 라운드 13 규칙 — **16주 분기 수용(2026-09-21)**: 분기 태그와 영업CF 분기 판정의 기간 상한을 110일 → **118일**로 넓힌다. Kroger의 회계 1분기가 16주(112일)라 기존 상한에서 걸렸다. 4개월(120일 이상) 누적은 여전히 받지 않는다. KR 32칸 복구(us-round13-log.md 4절).
- 미국 라운드 14 규칙 — **SEC 제출 메타 `reportDate` 오기 교정(2026-09-21)**: `submissions` API의 보고기간 말일이 틀린 제출이 있다. 정상 분기 말일은 80일 이상 떨어지므로, **45일 이내로 붙은 말일 쌍**에 걸린 제출만 원문 표지의 `dei:DocumentPeriodEndDate`를 읽어 진짜 말일로 옮긴다(`collect_us_round1.py`의 `fix_report_dates`).
  - 전 라운드에서 걸린 건 2건: ZTS `0001555280-19-000221`(2019-08-06 → 2019-06-30), NOW `0001373715-18-000058`(2018-02-28 → 2017-12-31).
  - 두 건 모두 **라벨 겹침 → 순차 배정**을 잘못 발동시켜 해당 회사의 30개 분기 라벨을 통째로 한 칸씩 밀고 있었다. ZTS 315칸·NOW 330칸을 고쳤고, `us-round5-dataset.csv`·`us-round14-dataset.csv`를 다시 만들어 정본으로 채택했다.
  - 국내 5 + 미국 15 데이터셋 전체(331개 기업)에 같은 유형이 더 없는지 라벨-기준일 정합성을 전수 점검했다(`tmp_verify/us7/labelcheck.py`) → **0건**.
- 미국 라운드 16 규칙 — **읽기 경로가 놓친 칸 보완(2026-09-21)**, `collect_us_round2.py`. 상세 [us-round16-log.md](logs/us-round16-log.md) 9절.
  - **규칙 1 · 회사 확장 태그**: 항목의 태그 계열(매출·영업이익·순이익·영업CF)이 보고서에서 **통째로** 빠졌을 때만 XBRL 원문을 연다. 이름이 us-gaap 폐지 태그와 같아 뜻이 분명한 확장 태그(`ALIAS`)만 표준 이름으로 읽는다. 그 회사 원문에도 없으면 같은 계열로는 다시 열지 않는다.
  - **규칙 2 · 후속 보고서 비교기간**: 그래도 미확인인 손익 칸(4분기 제외)은 같은 기간이 비교기간으로 실린 다른 보고서에서 읽는다. **가장 먼저 낸 보고서**를 쓰고 값구분 `공시(후속 보고서 비교기간)`으로 구분한다. 라운드 6 ABNB 특례를 일반 규칙으로 올렸다.
  - **규칙 2는 원 공시값을 덮어쓰지 않는다.** 그 분기 보고서에 읽을 수 있는 값이 **아예 없을 때만** 작동한다. 실측 근거는 공통 5번 항목에 적었다.
    - 이 문장은 원래 "재작성 미반영 원칙과 어긋나지 않는다"였다. 2026-09-21 대표 결정으로 재작성을 반영하게 됐으므로(공통 5번) 고쳤다. 원 공시값이 있는 칸의 재작성 반영은 규칙 2와 별개로 `…-restated.csv`에 기록된다.

## 미확인 내역

  - 미확인 내역(2026-09-21 회귀 재생성 후 재집계): 국내 1(두산) · 미국 1,253. 이 중 **영업이익이 1,181칸(50곳, 전 구간 30칸인 곳 34)**으로 94%다. 회사가 영업이익 줄을 공시하지 않거나 일부 기간만 태그한 경우로, LLY 선례(2026-09-19 대표 결정)에 따라 미확인으로 두고 사유를 출처 열에 적는다.
    - 영업이익 전 구간(각 30칸) 34곳 = 1,020: ADM·ADP·BMY·CASY·COP·CTVA·CVX·DHI·DOW·DVN·EMR·ETN·FOXA·GE·HCA·IBM·JCI·JNJ·KLAC·LLY·MRK·MTD·NEM·NKE·NUE·OXY·PCAR·PFE·PHM·PSX·SRE·TJX·XOM·ZTS
    - 영업이익 일부 구간 16곳 = 161: ROK 25 · ROST 21 · LHX 17 · CVNA 17 · BIIB 17 · HON 11 · DE 11 · SLB 9 · COHR 8 · SHW 7 · FLEX 7 · BKR 6 · PPG 2 · VRT 1 · SYY 1 · GEHC 1
      - 라운드 16 규칙 2(후속 보고서 비교기간)로 22칸이 채워졌다. F는 0칸이 돼 목록에서 빠졌다.
    - 영업이익 외 73칸: WEC 15(2019·2020·2021 4분기 대차 + 순이익) · LHX 11 · MTD 8(dei 표지 주식수 없음) · SYY 8 · GEHC 7(분사 직후 첫 보고) · COHR 6(차액 766.8M 미설명) · A 3 · TGT 3 · ABNB 2 · MA·TMO·UNP·HWM·ECL·MNST·PCG·AEE·EIX 각 1 · 국내 두산 1
      - CHD 3칸·PHM 1칸은 라운드 16 공용 코드 수정으로 채워져 빠졌다.
    - DELL 2칸은 2026-09-20 공용 코드 수정으로 해소했다(us-round3-log.md 7절).

## 이상치 집계 — 미국 (판정 규칙은 공통 파일)

  - 미국 라운드 1 10개사 이상치 **76건**(계산값 18, 모두 재확인 끝) · 부호전환 19건
  - 미국 라운드 2 10개사 이상치 **45건**(계산값 17, 모두 재확인 끝, 계산 오류 0) · 부호전환 51건 (us-round2-log.md 5·6절)
  - 미국 라운드 3 20개사 이상치 **135건**(계산값 35, 모두 재확인 끝, 계산 오류 0) · 부호전환 101건 (us-round3-log.md 5·6절)
  - 미국 라운드 4 20개사 이상치 **151건**(계산값 40, 모두 재확인 끝, 계산 오류 0) · 부호전환 112건 (us-round4-log.md 5·6절)
  - 미국 라운드 5 20개사 이상치 **154건**(계산값 34, 모두 재확인 끝, 계산 오류 0) · 부호전환 177건 (us-round5-log.md 5·6절)
  - 미국 라운드 6 20개사 이상치 **100건**(계산값 21, 모두 재확인 끝, 계산 오류 0) · 부호전환 157건 (us-round6-log.md 5·6절)
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

## 접근 불가 소스 — 미국

- ~~SEC 연결 불가~~ → **2026-09-19 재확인: `data.sec.gov`(submissions·companyfacts)·`efts.sec.gov` 접근 가능.** `www.sec.gov`도 **Python urllib로는 접근 가능**하다(curl만 실패, 000). 원문 XBRL(`Archives/…/*_htm.xml`)은 urllib로 받는다. 상세 [us-round1-log.md](logs/us-round1-log.md) 8절

## 진행 중 사항 (다음 라운드로 넘김)

번호는 분리 전 통합 로그의 번호를 그대로 쓴다. 공통 항목(5·13번)은 [../coverage-log.md](../coverage-log.md), 국내 항목은 [../kr/coverage-log.md](../kr/coverage-log.md).

10. **미국 트랙 미결 사항** (us-round1-log.md 1·5절)
    - ~~GOOGL·META 상장주식수·시가총액 미확인 120칸~~ → XBRL 원문으로 채웠다(2026-09-19, us-round1-log.md 8절).
    - ~~AVGO 대차 차이 28백만 달러~~ → 원인은 우선주 배당 의무(회사 확장 태그 메자닌)다. 반영해서 채웠다(8절).
    - 남은 미국 미확인: LLY·XOM·JNJ 영업이익 각 30칸(회사가 영업이익을 공시하지 않음), MA 2019Q4 순이익 1칸.
    - ~~XOM 승계 CIK 처리, V 시총 확인~~ → 라운드 2에서 처리했다(us-round2-log.md 2~4절). **UNH 금융 판정**은 남아 있다.
    - Yahoo 비공식 API 의존(자동화 운영팀). ~~SEC User-Agent 연락처~~ → 결정: `lapin s*******@gmail.com`(실제 값은 `.claude/settings.local.json`의 `env.SEC_USER_AGENT`) (2026-09-19, `us_probe.SEC_UA`).
    - S&P500 전체 분모 확정.

15. **분사를 분할로 처리한 시가총액 15칸 — 고칠지 결정 필요 (2026-09-21 라운드 17~30에서 발견).** Yahoo는 분사를 `splits` 이벤트로 싣고, `market_rows`는 분할일이 종가일~표지 기준일 사이면 주식수를 되돌린다. 분사는 주식수를 바꾸지 않아 시총이 분사 비율만큼 작다. 종가는 맞다. 기존 라운드 9칸 + 이번 6칸. 고치면 공용 코드 수정 + 전 라운드 회귀. 상세 [us-round17-30-log.md](logs/us-round17-30-log.md) 6절
16. ~~SPY 476~504위 업종 판정·미확인 407칸 진단~~ → **완료 (2026-09-21).** 상세 [us-round17-30-log.md](logs/us-round17-30-log.md) 10·11절
    - 미확인 167칸(영업이익 전 구간 미공시 240칸 제외): 값 없음 100 · 읽기 규칙이 막은 공시값 67 → **완료 (2026-09-22).** 공용 코드 4규칙 + 재작성 반올림 1규칙 수정, 라운드 1~30 전부 회귀. 66칸 + 부수 4칸 = **70칸 채움**, 0.1백만 반올림 재작성 9칸은 원 공시값으로 복귀. VTRS 2020Q4 순이익 1칸은 합병 전이라 미확인 유지. 상세 [us-round17-30-log.md](logs/us-round17-30-log.md) 12절
    - 504행 분류 완료. 기준 충족·미수집 20곳 중 **BE·ILMN·P·LDOS 4곳은 후보 풀 누락**. 기준 재수립 초안(분모 500/비금융 402, 이력 기준 폐지 등) 결정 대기
    - 15번(분사 시가총액)은 대표 지시로 보류(킵).

17. ~~재작성 검증 실패 칸의 지배지분 자본 섞임 47칸~~ → **완료 (대표 결정 2026-09-22).** 저량 4항목을 한 묶음으로 원 공시로 되돌리게 공용 코드 수정, 라운드 1~31 회귀·채택. 바뀐 칸 71칸(지배지분 자본 47 + 같은 버그의 부채·자산 24), 전부 저량 항목이고 새로 깨진 대차 0. 상세 [us-round31-log.md](logs/us-round31-log.md) 5절

14. ~~미국 라운드 16 — 읽기 경로가 놓친 칸, 공용 코드 수정 여부~~ → **완료 (2026-09-21).** 규칙 2종(회사 확장 태그 · 후속 보고서 비교기간)을 `collect_us_round2.py`에 넣었다. 라운드 1~16 회귀 재생성·채택까지 끝났고 **기존 값 변경 0건, 개선 28칸**이다. 상세 [us-round16-log.md](logs/us-round16-log.md) 9절
    - CHD 2025Q1~Q3 영업활동현금흐름 3칸: 회사 확장 태그 `chd:NetCashProvidedByOperatingActivities`. companyfacts에 안 실리고, 원문 대체 경로는 "사실 20개 미만"에서만 발동한다.
    - PHM 2021Q1 매출액 1칸: 그 10-Q의 매출 사실이 전부 차원(세그먼트) 부착이라 무차원 연결 총계가 없다.
    - 두 값 모두 회사의 **다음 해 보고서 비교열에 표준 태그로** 실려 있어 확인된다. 고치려면 `Facts.find`의 원문 대체 조건을 넓혀야 하고, 라운드 14 선례대로 전 라운드(국내 5 + 미국 16) 회귀 검사가 따라붙는다.
    - 상세 us-round16-log.md 5절.
