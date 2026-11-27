import json, os, subprocess, sys, threading, re, shutil, uuid, gzip, time
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
if os.environ.get("ONLY_TARGET"): jobs=[j for j in jobs if j[1]==os.environ["ONLY_TARGET"]]
jobs=[j for j in jobs if (j[0],j[1],j[2],j[4]) not in done]
lock=threading.Lock(); f=open(out,"a")
# ISOLATE=1: run each job in a fresh copy of its test folder, at a new path with the same folder name, and keep the raw
# output. Claude Code keeps auto-memory per folder path (~/.claude/projects/<path>/memory); in the original E1 runs one
# folder (Sonnet, caveman, alone) picked up a note saved by an earlier run, and its 18 runs were rerun with ISOLATE=1.
ISO=os.environ.get("ISOLATE")
PROJ=os.path.join(os.path.expanduser("~"),".claude","projects")
RAW=os.environ.get("RAW_DIR") or os.path.join(S,"raw_e1")
E=os.environ.get("ENVS_DIR", os.path.join(S,"envs"))   # where build.py put the test folders
def proj_dir(path): return os.path.join(PROJ, re.sub(r"[^A-Za-z0-9]","-",path))
def read_memory(path):
    m=os.path.join(proj_dir(path),"memory"); res={}
    if os.path.isdir(m):
        for n in sorted(os.listdir(m)):
            try: res[n]=open(os.path.join(m,n),errors="replace").read()[:4000]
            except OSError: pass
    return res
def one(j):
    c,t,i,p,rep=j
    cwd=os.path.join(E,"alone",t) if c=="alone" else os.path.join(E,c)
    iso=None
    if ISO:
        iso=os.path.join(E+"_iso",uuid.uuid4().hex[:12]); dst=os.path.join(iso,os.path.basename(cwd))
        shutil.copytree(cwd,dst,symlinks=True); cwd=dst
    rec={"cond":c,"target":t,"i":i,"rep":rep,"model":model,"fired":[],"first_tool":None}
    try:
        cmd=["claude","-p",p,"--model",model,"--output-format","stream-json","--verbose","--setting-sources","project","--strict-mcp-config","--no-session-persistence","--max-turns","3","--disallowedTools","Bash"]
        pr=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=240,stdin=subprocess.DEVNULL if ISO else None)
        if ISO:
            mem=read_memory(cwd); rec["memory_files_after"]=len(mem)
            d=os.path.join(RAW,f"claude_{model}",f"{c}__{t}"); os.makedirs(d,exist_ok=True)
            fn=os.path.join(d,f"{t}__{i}__{rep}__{int(time.time()*1000)}.json.gz")
            with gzip.open(fn,"wt") as g: json.dump({"cmd":cmd,"stdout_events":pr.stdout,"stderr":pr.stderr[-20000:],"returncode":pr.returncode,"isolated":True,"memory_after":mem},g)
            rec["raw"]=os.path.relpath(fn,S)
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
    finally:
        if iso:   # remove the copy and the per-path data Claude Code created for it (memory is already in the raw log)
            shutil.rmtree(iso,ignore_errors=True)
            pd=proj_dir(cwd)
            if "-envs-iso-" in os.path.basename(pd) and os.path.dirname(pd)==PROJ: shutil.rmtree(pd,ignore_errors=True)
    if ISO: rec["isolated"]=True
    rec["hit"]=t in [x.split(":")[-1] for x in rec["fired"]]
    with lock: f.write(json.dumps(rec)+"\n"); f.flush()
    return rec
with ThreadPoolExecutor(int(os.environ.get("PAR","6"))) as ex: rs=list(ex.map(one,jobs))
print("ran",len(rs),"errors",sum(1 for r in rs if r.get("error")),"cost",round(sum(r.get("cost") or 0 for r in rs),3))
