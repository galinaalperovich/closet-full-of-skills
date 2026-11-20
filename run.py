import json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
S=os.path.dirname(os.path.abspath(__file__))
conds=sys.argv[1].split(","); reps=int(sys.argv[2]); model=sys.argv[3]; out=sys.argv[4]; limit=int(sys.argv[5]) if len(sys.argv)>5 else 99
prompts=json.load(open(os.path.join(S,"prompts.json")))
done=set()
if os.path.exists(out):
    for l in open(out):
        r=json.loads(l)
        if not r.get("error"): done.add((r["cond"],r["target"],r["i"],r["rep"]))
jobs=[(c,k.split(":")[1],i,p,r) for c in conds for k,ps in prompts.items() for i,p in enumerate(ps[:limit]) for r in range(reps)]
jobs=[j for j in jobs if (j[0],j[1],j[2],j[4]) not in done]
lock=threading.Lock(); f=open(out,"a")
def one(j):
    c,t,i,p,rep=j
    cwd=os.path.join(S,"envs","alone",t) if c=="alone" else os.path.join(S,"envs",c)
    rec={"cond":c,"target":t,"i":i,"rep":rep,"model":model,"fired":[],"first_tool":None}
    try:
        pr=subprocess.run(["claude","-p",p,"--model",model,"--output-format","stream-json","--verbose","--setting-sources","project","--strict-mcp-config","--no-session-persistence","--max-turns","3","--disallowedTools","Bash"],cwd=cwd,capture_output=True,text=True,timeout=240)
        for l in pr.stdout.splitlines():
            try: e=json.loads(l)
            except Exception: continue
            if e.get("type")=="system" and e.get("subtype")=="init": rec["n_skills"]=len(e.get("skills",[]))
            if e.get("type")=="assistant":
                for b in e.get("message",{}).get("content",[]):
                    if b.get("type")=="tool_use":
                        rec["first_tool"]=rec["first_tool"] or b.get("name")
                        if b.get("name")=="Skill": rec["fired"].append((b.get("input") or {}).get("skill") or json.dumps(b.get("input")))
            if e.get("type")=="result":
                rec["cost"]=e.get("total_cost_usd"); rec["sub"]=e.get("subtype"); u=e.get("usage",{})
                rec["in_tok"]=(u.get("input_tokens") or 0)+(u.get("cache_creation_input_tokens") or 0)+(u.get("cache_read_input_tokens") or 0)
        if "sub" not in rec: rec["error"]=(pr.stderr or pr.stdout)[-300:]
    except Exception as ex: rec["error"]=repr(ex)[:300]
    rec["hit"]=t in [x.split(":")[-1] for x in rec["fired"]]
    with lock: f.write(json.dumps(rec)+"\n"); f.flush()
    return rec
with ThreadPoolExecutor(int(os.environ.get("PAR","6"))) as ex: rs=list(ex.map(one,jobs))
print("ran",len(rs),"errors",sum(1 for r in rs if r.get("error")),"cost",round(sum(r.get("cost") or 0 for r in rs),3))
