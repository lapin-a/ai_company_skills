"""시험: OpenDART document.xml(원본 XML)에서 연결재무제표 장을 잘라 공시뷰어 섹션과 같은 모양으로 만든다."""
import io, json, re, sys, time, urllib.request, zipfile
sys.path.insert(0, "kr")
import collect_round1 as cr

KEY = json.load(open(".claude/settings.local.json", encoding="utf-8"))["env"]["DART_API_KEY"]


def api_doc(rcp):
    b = urllib.request.urlopen("https://opendart.fss.or.kr/api/document.xml?crtfc_key=%s&rcept_no=%s" % (KEY, rcp), timeout=60).read()
    time.sleep(0.5)
    if not b.startswith(b"PK"):  # 오류는 zip 대신 상태 메시지로 온다 (020 = 요청 제한 초과)
        msg = b[:300].decode("utf-8", "replace")
        if "<status>020" in msg or '"020"' in msg:
            raise SystemExit("OpenDART 요청 제한 초과 — 중단: " + msg)
        raise RuntimeError("document.xml 오류: " + msg)
    z = zipfile.ZipFile(io.BytesIO(b))
    main = min(z.namelist(), key=lambda n: ("_" in n.rsplit("/", 1)[-1], len(n)))  # 본문 = 접미사 없는 파일
    raw = z.read(main)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp949")


def section(x, title_re, level):
    m = re.search(r"<TITLE[^>]*>\s*" + title_re + r"\s*</TITLE>", x)
    if not m:
        return None
    end = x.find("</SECTION-%d>" % level, m.end())
    body = x[m.start():end if end > 0 else len(x)]
    body = re.sub(r"<(/?)T[EU](?=[\s>])", r"<\1TD", body)  # DART 전용 칸 태그 → TD
    return body.replace("&cr;", " ")


def fs_section(rcp):
    x = api_doc(rcp)
    doc = section(x, r"\d+\. ?연결재무제표", 2)
    if doc is not None:
        return doc
    doc = section(x, r"[IVX]+\. ?재무제표 등", 1)
    if doc is None:
        return None
    if "연결재무상태표" not in re.sub(r"<[^>]+>|&nbsp;|\s", "", doc):
        return cr.OLD_NO_CONSOL
    for t in re.finditer(r"<TABLE.*?</TABLE>", doc, re.S | re.I):
        if re.sub(r"<[^>]+>|&nbsp;|\s", "", t.group()).startswith("재무상태표"):
            return doc[:t.start()]
    return doc


if __name__ == "__main__":
    for rcp in sys.argv[1:]:
        d = fs_section(rcp)
        p = cr.parse(d) if d else None
        print(rcp, len(d or ""), {k: v for k, v in (p or {}).items()})
