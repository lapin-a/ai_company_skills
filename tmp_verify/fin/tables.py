import sys, re
doc = open(sys.argv[1], encoding="utf-8").read()
for t in re.split(r"(<TABLE.*?</TABLE>)", doc, flags=re.S | re.I):
    n = len(re.findall(r"<TR", t, re.I))
    txt = re.sub(r"<[^>]+>|&nbsp;|[\s　]", "", t)
    if txt: print(n, len(txt), txt[:90], "…", txt[-40:])
