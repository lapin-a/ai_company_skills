"""KRX 오픈API 접근 재확인 (자동화 운영팀). 실행: python tmp_verify/krx_probe.py [기준일YYYYMMDD]

라운드 5 0절에서 7개 엔드포인트가 모두 401 `Unauthorized API Call`이었다.
API별 사용 승인이 난 뒤 다시 돌려 확인하는 용도다.
"""
import json, sys, urllib.error, urllib.parse, urllib.request

BASE = "https://data-dbg.krx.co.kr/svc/apis/"
EPS = [("sto/stk_bydd_trd", "유가증권 일별매매정보 ★2019 시장데이터에 필요한 것"),
       ("sto/ksq_bydd_trd", "코스닥 일별매매정보"),
       ("sto/knx_bydd_trd", "코넥스 일별매매정보"),
       ("idx/krx_dd_trd", "KRX 지수 일별"),
       ("idx/kospi_dd_trd", "KOSPI 지수 일별"),
       ("sto/stk_isu_base_info", "종목 기본정보"),
       ("etp/etf_bydd_trd", "ETF 일별매매정보 (수집 대상 아님)")]

KEY = json.load(open(".claude/settings.local.json", encoding="utf-8"))["env"]["KRX_API_KEY"]
basDd = sys.argv[1] if len(sys.argv) > 1 else "20191230"
print("키 %d자 (…%s) | 기준일 %s\n" % (len(KEY), KEY[-4:], basDd))

for path, desc in EPS:
    url = BASE + path + "?" + urllib.parse.urlencode({"basDd": basDd})
    req = urllib.request.Request(url, headers={"AUTH_KEY": KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
        d = json.loads(body)
        rows = next((v for v in d.values() if isinstance(v, list)), [])
        print("  %-24s HTTP %s | 행 %d | %s" % (path, r.status, len(rows), desc))
        if rows:
            print("       첫 행: %s" % json.dumps(rows[0], ensure_ascii=False)[:180])
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace").strip()[:120]
        print("  %-24s HTTP %s | %s | %s" % (path, e.code, msg, desc))
    except Exception as e:
        print("  %-24s 실패 %r | %s" % (path, e, desc))
