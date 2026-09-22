import csv, collections, sys
new=list(csv.DictReader(open(sys.argv[1],encoding="utf-8-sig")))
old=list(csv.DictReader(open(sys.argv[2],encoding="utf-8-sig")))
V="값(원)" if "값(원)" in new[0] else "값"
k=lambda r:(r["종목코드"],r["기간"],r["항목"])
o={k(r):r for r in old}
ch=[r for r in new if k(r) in o and (r[V],r["값구분"])!=(o[k(r)][V],o[k(r)]["값구분"])]
print("기존 행",len(old),"새 행",len(new),"기존 기간 값·값구분 변경",len(ch))
for r in ch[:15]: q=o[k(r)]; print(" ",k(r),q[V],q["값구분"],"->",r[V],r["값구분"])
newp=[r for r in new if k(r) not in o]
c=collections.Counter((r["기간"][:4], "값" if r[V] else r["값구분"][:25]) for r in newp)
for x,v in sorted(c.items()): print(x,v)
c=collections.Counter((r["항목"], r["값구분"][:25]) for r in newp if not r[V])
for x,v in sorted(c.items()): print(x,v)
