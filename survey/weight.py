import json, os, re, sys
from collections import Counter, defaultdict
import yaml
ROOT=sys.argv[1]
STOP=set("a an the and or of to for in on with when use this that is are be as by it you your from at any all not if using used can will into via e g etc skill skills user users".split())
def toks(s): return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w)>2}
out={}; allnames=defaultdict(set)
for repo in sorted(os.listdir(ROOT)):
    rp=os.path.join(ROOT,repo); sk={}; evald=0; files=0
    for dp,dn,fn in os.walk(rp):
        dn[:]=[d for d in dn if d not in (".git","node_modules")]
        if "SKILL.md" not in fn: continue
        files+=1
        t=open(os.path.join(dp,"SKILL.md"),encoding="utf-8",errors="replace").read()
        m=re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)",t,re.S)
        meta={}
        if m:
            try: meta=yaml.safe_load(m.group(1)) or {}
            except Exception: meta={}
        if not isinstance(meta,dict): meta={}
        name=str(meta.get("name") or os.path.basename(dp)); desc=str(meta.get("description") or "")+" "+str(meta.get("when_to_use") or "")
        has_eval=any(re.search(r"(^|/)(evals?|tests?)(/|$)|evals?\.json$|_test\.|test_", os.path.relpath(os.path.join(d2,f),dp)) for d2,_,fs in os.walk(dp) for f in fs)
        if name in sk: continue
        sk[name]={"desc":desc.strip(),"body":len(t)-(m.end() if m else 0),"eval":has_eval}
    if not sk: continue
    for n in sk: allnames[n].add(repo)
    names=list(sk); T=[toks(sk[n]["desc"]) for n in names]
    pairs=0; involved=set()
    # inverted index to keep it fast
    inv=defaultdict(list)
    for i,ts in enumerate(T):
        for w in ts: inv[w].append(i)
    cand=Counter()
    for w,ids in inv.items():
        if len(ids)>400: continue
        for a in range(len(ids)):
            for b in range(a+1,len(ids)): cand[(ids[a],ids[b])]+=1
    ex=[]
    for (i,j),c in cand.items():
        u=len(T[i]|T[j])
        if u>=6 and c/u>=0.6:
            pairs+=1; involved|={i,j}
            if len(ex)<3: ex.append((names[i],names[j],round(c/u,2)))
    L=[len(n)+min(len(sk[n]["desc"]),1536) for n in names]
    out[repo]={"files":files,"skills":len(sk),"listing_chars":sum(L),"median_desc":sorted(len(sk[n]["desc"]) for n in names)[len(names)//2],
      "over1536":sum(1 for n in names if len(sk[n]["desc"])>1536),"body_chars":sum(sk[n]["body"] for n in names),
      "with_eval":sum(1 for n in names if sk[n]["eval"]),"twin_pairs":pairs,"twin_skills":len(involved),"twin_examples":ex}
json.dump({"repos":out,"shared_names":{n:sorted(r) for n,r in allnames.items() if len(r)>1}},open(sys.argv[2],"w"))
print("repo".ljust(40),"skills listing_tok  x8k-chars  x16k  medDesc  twins  w/eval  body_tok")
for r,v in sorted(out.items(), key=lambda x:-x[1]["listing_chars"]):
    print(r[:40].ljust(40), f"{v['skills']:6d} {v['listing_chars']//4:11d} {v['listing_chars']/8000:9.1f}x {v['listing_chars']/16000:5.1f}x {v['median_desc']:7d} {v['twin_skills']:6d} {v['with_eval']:6d} {v['body_chars']//4:10d}")
sn=json.load(open(sys.argv[2]))["shared_names"]
print("\nskill names used by 2+ repos:",len(sn)); 
for n,r in sorted(sn.items(), key=lambda x:-len(x[1]))[:25]: print(len(r), n)
tot=sum(v["skills"] for v in out.values()); ev=sum(v["with_eval"] for v in out.values())
print("\nskills",tot,"with any eval/test file",ev, f"{100*ev/tot:.1f}%", "repos with any:", sum(1 for v in out.values() if v["with_eval"]))
