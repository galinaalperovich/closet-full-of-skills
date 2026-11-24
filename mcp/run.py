"""Runner for experiments 2 and 3. Usage: run.py <claude|codex> <model> <jobset: mcp|trend|mixed> <out.jsonl>"""
import json, os, re, shutil, subprocess, sys, threading, time, gzip, uuid
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); SP=os.path.dirname(H)
ENV=os.environ.get("ENVS2_DIR", os.path.join(SP,"envs2"))
CODEX=os.environ.get("CODEX_BIN") or shutil.which("codex") or "/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex"
harness, model, jobset, out = sys.argv[1:5]
T=json.load(open(os.path.join(H,"mcp_targets.json")))
P1=json.load(open(os.path.join(SP,"prompts.json"))); P2=json.load(open(os.path.join(H,"trending_skill_prompts.json")))
SKP={k.split(":")[1]:v for k,v in list(P1.items())+list(P2.items())}
OVERLAP={"pdf":{"pdf-reader-mcp.read_pdf","searxng.pdf_merger","searxng.pdf_splitter"},"xlsx":{"excel."},"pptx":{"ppt.","okppt."},"docx":{"word-document-server."},"webapp-testing":{"playwright-mcp.","chrome-devtools.","playwright-ea.","puppeteer."}}
jobs=[]
def add(env, kind, target, accept, prompts):
    for i,p in enumerate(prompts): jobs.append({"env":env,"kind":kind,"target":target,"accept":sorted(accept),"i":i,"prompt":p})
if jobset=="mcp":
    for tid,v in T.items(): add(f"mcp_alone/{tid.replace('.','__')}","tool",tid,v["accept"],v["prompts"])
    for e in ("mcp_pack20","mcp_crowd200","mcp_crowdall"):
        for tid,v in T.items(): add(e,"tool",tid,v["accept"],v["prompts"])
elif jobset=="trend":
    for k,v in P2.items(): n=k.split(":")[1]; add(f"sk_alone/{n}","skill",n,["skill:"+n],v)
elif jobset=="mixed":
    for e in ("mixed_typical","mixed_heavy"):
        for n,v in SKP.items(): add(e,"skill",n,["skill:"+n],v)
        for tid,v in T.items(): add(e,"tool",tid,v["accept"],v["prompts"])
done=set()
if os.path.exists(out):
    for l in open(out):
        r=json.loads(l)
        if not r.get("error"): done.add((r["env"],r["target"],r["i"]))
jobs=[j for j in jobs if (j["env"],j["target"],j["i"]) not in done]
if os.environ.get("ONLY_ENV"): jobs=[j for j in jobs if j["env"]==os.environ["ONLY_ENV"]]
if os.environ.get("ONLY_I"): jobs=[j for j in jobs if j["i"]==int(os.environ["ONLY_I"])]
if os.environ.get("ONLY_TARGET"): jobs=[j for j in jobs if j["target"]==os.environ["ONLY_TARGET"]]
lock=threading.Lock(); f=open(out,"a")
SK=re.compile(r"skills/([a-z0-9][a-z0-9\-]*)/SKILL\.md")
FAMILY={"playwright-mcp.browser_take_screenshot":{"playwright-mcp","chrome-devtools","puppeteer","playwright-ea"},
 "playwright-mcp.browser_fill_form":{"playwright-mcp","chrome-devtools","puppeteer","playwright-ea"},
 "chrome-devtools.performance_start_trace":{"chrome-devtools","playwright-mcp"},
 "chrome-devtools.list_console_messages":{"chrome-devtools","playwright-mcp","playwright-ea"},
 "chrome-devtools.lighthouse_audit":{"chrome-devtools"}}
def classify(rec, used):
    acc=set(rec["accept"]); rec["used"]=used
    def ok(u): return u in acc or (u.startswith("mcp:") and u[4:] in acc)
    rec["hit_strict"]=any(ok(u) for u in used)
    fam=FAMILY.get(rec["target"],set())
    rec["hit"]=rec["hit_strict"] or any(u.startswith("mcp:") and u[4:].split(".")[0] in fam for u in used)
    if rec["hit"]: rec["outcome"]="hit"
    elif any(u.startswith("skill:") for u in used): rec["outcome"]="other_skill"
    elif any(u.startswith("mcp:") for u in used): rec["outcome"]="other_mcp"
    elif any(u.startswith("builtin:") for u in used): rec["outcome"]="builtin"
    else: rec["outcome"]="none"
    ov=OVERLAP.get(rec["target"]) if rec["kind"]=="skill" else None
    rec["overlap_tool"]=bool(ov) and any(u.startswith("mcp:") and any(u[4:].startswith(o) for o in ov) for u in used)
RAW=os.path.join(H,"raw")
# ISOLATE=1: run each Claude Code job in a fresh copy of its test folder, at a new path with the same folder name.
# Claude Code keeps auto-memory per folder path (~/.claude/projects/<path>/memory); without this, notes saved by one run
# are loaded by later runs in the same folder. Memory files a run writes are kept in its raw log.
ISO=os.environ.get("ISOLATE")
PROJ=os.path.join(os.path.expanduser("~"),".claude","projects")
def proj_dir(path): return os.path.join(PROJ, re.sub(r"[^A-Za-z0-9]","-",path))
def read_memory(path):
    m=os.path.join(proj_dir(path),"memory"); out={}
    if os.path.isdir(m):
        for n in sorted(os.listdir(m)):
            try: out[n]=open(os.path.join(m,n),errors="replace").read()[:4000]
            except OSError: pass
    return out
def save_raw(rec, pr, cmd, extra=None):
    d=os.path.join(RAW,f'{rec["harness"]}_{rec["model"]}',rec["env"].replace("/","__")); os.makedirs(d,exist_ok=True)
    fn=os.path.join(d,f'{rec["target"]}__{rec["i"]}__{int(time.time()*1000)}.json.gz')
    with gzip.open(fn,"wt") as g: json.dump({"cmd":[c for c in cmd],"stdout_events":pr.stdout,"stderr":pr.stderr[-20000:],"returncode":pr.returncode,**(extra or {})},g)
    rec["raw"]=os.path.relpath(fn,H)
STOP=[False]
# LOAD_MAX=<n>: wait before starting a job while the 1-minute load average is above n. The mixed setups start up to
# 73 stub servers per run, and 8 parallel runs once made the machine unresponsive. Default off.
LOAD_MAX=float(os.environ.get("LOAD_MAX","0"))
def one(j):
    if STOP[0]: return {"skipped":True}
    while LOAD_MAX and os.getloadavg()[0]>LOAD_MAX: time.sleep(5)
    cwd=os.path.join(ENV,j["env"]); cfg=json.load(open(os.path.join(cwd,"_mcp.json")))["mcpServers"]
    iso=None
    if ISO and harness=="claude":
        iso=os.path.join(ENV+"_iso",uuid.uuid4().hex[:12]); dst=os.path.join(iso,os.path.basename(cwd))
        shutil.copytree(cwd,dst,symlinks=True); cwd=dst
    rec=dict(j, harness=harness, model=model)
    used=[]; ts=False
    try:
        if harness=="claude":
            cmd=["claude","-p",j["prompt"],"--model",model,"--output-format","stream-json","--verbose","--setting-sources","project","--strict-mcp-config","--no-session-persistence","--max-turns","4","--disallowedTools","Bash"]
            if cfg: cmd+=["--mcp-config",os.path.join(cwd,"_mcp.json")]
            # ALLOW_MCP=1: headless Claude Code denies MCP calls that are not allowed, so without it every MCP call gets a
            # permission denial instead of the stub result (the first-round runs). The published runs used it.
            if cfg and os.environ.get("ALLOW_MCP"): cmd+=["--allowedTools",",".join("mcp__"+s for s in cfg)]
            pr=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=420,stdin=subprocess.DEVNULL)
            mem=read_memory(cwd); rec["memory_files_after"]=len(mem)
            save_raw(rec, pr, cmd, {"isolated":bool(iso),"memory_after":mem})
            for l in pr.stdout.splitlines():
                try: e=json.loads(l)
                except Exception: continue
                if e.get("type")=="system" and e.get("subtype")=="init":
                    rec["n_tools"]=len(e.get("tools",[])); rec["n_skills"]=len(e.get("skills",[])); rec["mcp_failed"]=[m["name"] for m in e.get("mcp_servers",[]) if m.get("status")!="connected"]
                if e.get("type")=="assistant":
                    for b in e.get("message",{}).get("content",[]):
                        if b.get("type")!="tool_use": continue
                        n=b.get("name","")
                        if n=="Skill": used.append("skill:"+str((b.get("input") or {}).get("skill","")).split(":")[-1])
                        elif n.startswith("mcp__"):
                            _,s,t=n.split("__",2); used.append("mcp:"+f"{s}.{t}")
                        elif n=="ToolSearch": ts=True
                        else: used.append("builtin:"+n)
                if e.get("type")=="result":
                    rec["cost"]=e.get("total_cost_usd"); rec["sub"]=e.get("subtype"); u=e.get("usage",{})
                    rec["in_tok"]=(u.get("input_tokens") or 0)+(u.get("cache_creation_input_tokens") or 0)+(u.get("cache_read_input_tokens") or 0)
            if "sub" not in rec: rec["error"]=(pr.stderr or pr.stdout)[-300:]
        else:
            cmd=[CODEX,"exec","--json","--ephemeral","--skip-git-repo-check","--ignore-user-config","-s","read-only","-c",'model="gpt-6-astra"',"-c",'model_reasoning_effort="medium"',"-c",'approval_policy="never"']
            for s,c in cfg.items():
                cmd+=["-c",f'mcp_servers.{s}.command="{c["command"]}"',"-c",f"mcp_servers.{s}.args={json.dumps(c['args'])}"]
            cmd.append(j["prompt"])
            pr=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=420,stdin=subprocess.DEVNULL)
            save_raw(rec, pr, cmd)
            for l in pr.stdout.splitlines():
                try: e=json.loads(l)
                except Exception: continue
                it=e.get("item") or {}
                if e.get("type")=="item.started" and it.get("type")=="mcp_tool_call":
                    used.append("mcp:"+f'{it.get("server")}.{it.get("tool")}')
                if e.get("type")=="item.completed" and it.get("type")=="command_execution":
                    sk=SK.findall(it.get("command",""))
                    if sk: used+=["skill:"+x for x in sk]
                    else: used.append("builtin:shell")
                if e.get("type")=="item.completed" and it.get("type") in ("web_search","file_change"): used.append("builtin:"+it["type"])
                if e.get("type")=="turn.completed": rec["usage"]=e.get("usage"); rec["sub"]="ok"
                if e.get("type")=="turn.failed": rec["error"]=json.dumps(e)[:300]
            if "sub" not in rec and "error" not in rec: rec["error"]=(pr.stderr or pr.stdout)[-300:]
    except Exception as ex: rec["error"]=repr(ex)[:300]
    finally:
        if iso:   # remove the copy and the per-path data Claude Code created for it (memory is already in the raw log)
            shutil.rmtree(iso,ignore_errors=True)
            pd=proj_dir(cwd)
            if os.path.basename(pd).find("-envs2-iso-")>0 and os.path.dirname(pd)==PROJ: shutil.rmtree(pd,ignore_errors=True)
    rec["isolated"]=bool(iso)
    rec["toolsearch"]=ts
    seen=[]; [seen.append(u) for u in used if u not in seen]
    classify(rec, seen)
    rec["ts"]=time.time()
    if os.environ.get("STOP_ON_429") and "429" in str(rec.get("error","")): STOP[0]=True
    with lock: f.write(json.dumps(rec)+"\n"); f.flush()
    return rec
with ThreadPoolExecutor(int(os.environ.get("PAR","4"))) as ex: rs=list(ex.map(one,jobs))
rs=[r for r in rs if not r.get("skipped")]
print("ran",len(rs),"errors",sum(1 for r in rs if r.get("error")),"stopped_on_429",STOP[0])
if STOP[0]: sys.exit(3)
