import json, sys
from collections import Counter, defaultdict
rows = json.load(open(sys.argv[1]))
seen=set(); uniq=[]
for r in rows:
    if r["sha"] in seen: continue
    seen.add(r["sha"]); uniq.append(r)
print("files", len(rows), "unique", len(uniq))
c = Counter(i for r in uniq for i in r["issues"])
print("\n== share of unique skills with each issue ==")
for k,v in c.most_common(): print(f"{k:26s}{v:6d}  {100*v/len(uniq):5.1f}%")
print("any issue (excluding desc-no-trigger, orphan, old-model):", sum(1 for r in uniq if set(r["issues"])-{"desc-no-trigger","orphan-file","old-model-id","body-over-500-lines"}))
keys=["yaml-invalid","name-dir-mismatch","dead-link","dead-path","missing-dir-path","undeclared-python-dep","orphan-file","old-model-id","desc-over-1024","body-over-500-lines","personal-abs-path"]
by=defaultdict(list)
for r in uniq: by[r["repo"]].append(r)
print("\n== per repo: n, then % of skills with each ==")
print("repo".ljust(42),"n".rjust(5)," ".join(k[:9].rjust(9) for k in keys))
tot=Counter()
for repo,rs in sorted(by.items(), key=lambda x:-len(x[1])):
    line=[]
    for k in keys:
        n=sum(1 for r in rs if k in r["issues"]); line.append(f"{100*n/len(rs):8.0f}%")
        if n: tot[k]+=1
    print(repo[:42].ljust(42),str(len(rs)).rjust(5)," ".join(line))
print("\nrepos affected (of %d):"%len(by), dict(tot))
