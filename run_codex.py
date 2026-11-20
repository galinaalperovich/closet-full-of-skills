"""Same test on Codex CLI. A skill 'fires' when the agent reads skills/<name>/SKILL.md."""
import json, os, re, shutil, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
S=os.path.dirname(os.path.abspath(__file__))
CODEX=os.environ.get("CODEX_BIN") or shutil.which("codex") or "/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex"
conds=sys.argv[1].split(","); reps=int(sys.argv[2]); effort=sys.argv[3]; out=sys.argv[4]
prompts=json.load(open(os.path.join(S,"prompts.json")))
done=set()
if os.path.exists(out):
    for l in open(out):
        r=json.loads(l)
        if not r.get("error"): done.add((r["cond"],r["target"],r["i"],r["rep"]))
jobs=[(c,k.split(":")[1],i,p,r) for c in conds for k,ps in prompts.items() for i,p in enumerate(ps) for r in range(reps)]
jobs=[j for j in jobs if (j[0],j[1],j[2],j[4]) not in done]
lock=threading.Lock(); f=open(out,"a")
SK=re.compile(r"skills/([a-z0-9][a-z0-9\-]*)/SKILL\.md")
def one(j):
    c,t,i,p,rep=j
    cwd=os.path.join(S,"envs","alone",t) if c=="alone" else os.path.join(S,"envs",c)
    rec={"cond":c,"target":t,"i":i,"rep":rep,"model":"codex-default","effort":effort,"fired":[]}
    try:
        pr=subprocess.run([CODEX,"exec","--json","--ephemeral","--skip-git-repo-check","-s","read-only","-c",f'model_reasoning_effort="{effort}"',p],cwd=cwd,capture_output=True,text=True,timeout=300,stdin=subprocess.DEVNULL)
        for l in pr.stdout.splitlines():
            try: e=json.loads(l)
            except Exception: continue
            it=e.get("item") or {}
            if e.get("type")=="item.completed" and it.get("type")=="command_execution":
                for n in SK.findall(it.get("command","")):
                    if n not in rec["fired"]: rec["fired"].append(n)
            if e.get("type")=="turn.completed":
                rec["usage"]=e.get("usage"); rec["sub"]="ok"
        if "sub" not in rec: rec["error"]=(pr.stderr or pr.stdout)[-300:]
    except Exception as ex: rec["error"]=repr(ex)[:300]
    rec["hit"]=t in rec["fired"]
    with lock: f.write(json.dumps(rec)+"\n"); f.flush()
    return rec
with ThreadPoolExecutor(int(os.environ.get("PAR","6"))) as ex: rs=list(ex.map(one,jobs))
print("ran",len(rs),"errors",sum(1 for r in rs if r.get("error")))
