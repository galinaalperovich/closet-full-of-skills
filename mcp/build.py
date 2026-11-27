"""Build environments for experiment 2 (MCP tools only) and 3 (skills + MCP tools mixed).
Skills are inert stubs (real name + description). MCP tools are served by stub_server.py with real definitions."""
import json, os, random, re, shutil, yaml
H=os.path.dirname(os.path.abspath(__file__)); SP=os.path.dirname(H)
REPOS=os.environ.get("SKILL_REPOS", os.path.join(SP,"third_party","repos"))  # cloned by sources/fetch_sources.sh
ENV=os.environ.get("ENVS2_DIR", os.path.join(SP,"envs2"))
BUILTIN={"deep-research","design","slides","design-sync","dataviz","artifact-diagramming","whiteboard","artifact-capabilities","update-config","verify","debug","code-review","simplify","batch","fewer-permission-prompts","doctor","loop","schedule","claude-api","workflow-authoring","run","run-skill-generator","plugin-authoring","init","security-review"}
rnd=random.Random(11)
def load_skills(repo):
    out={}
    for dp,dn,fn in os.walk(os.path.join(REPOS,repo)):
        dn[:]=[d for d in dn if d!=".git"]
        if "SKILL.md" in fn:
            t=open(os.path.join(dp,"SKILL.md"),encoding="utf-8",errors="replace").read()
            m=re.match(r"---[ \t]*\r?\n(.*?)\r?\n---",t,re.S)
            try: meta=yaml.safe_load(m.group(1)) if m else {}
            except Exception: meta={}
            if not isinstance(meta,dict): continue
            n=str(meta.get("name") or os.path.basename(dp)); d=str(meta.get("description") or "").strip(); w=str(meta.get("when_to_use") or "").strip()
            if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$",n) and d and n not in out: out[n]=(d,w)
    return out
def write_skill(base,name,d,w):
    p=os.path.join(base,".claude","skills",name); os.makedirs(p,exist_ok=True)
    fm={"name":name,"description":d}
    if w: fm["when_to_use"]=w
    open(os.path.join(p,"SKILL.md"),"w").write("---\n"+yaml.safe_dump(fm,allow_unicode=True,width=10**6,sort_keys=False)+"---\n\nThe instructions for this skill are omitted in this test. Reply with one short sentence.\n")
def finish(base, servers):
    os.makedirs(os.path.join(base,".claude","skills"),exist_ok=True)
    os.makedirs(os.path.join(base,".agents"),exist_ok=True)
    if not os.path.exists(os.path.join(base,".agents","skills")): os.symlink("../.claude/skills",os.path.join(base,".agents","skills"))
    sd=os.path.join(base,"_mcp"); os.makedirs(sd,exist_ok=True); cfg={}
    for s,tools in servers.items():
        if not tools: continue
        json.dump(tools,open(os.path.join(sd,s+".json"),"w"))
        cfg[s]={"command":"python3","args":["-I",os.path.join(H,"stub_server.py"),s,os.path.join(sd,s+".json")]}
    json.dump({"mcpServers":cfg},open(os.path.join(base,"_mcp.json"),"w"))
    return sum(len(v) for v in servers.values())
inv=json.load(open(os.path.join(H,"tools_inventory.json")))
byid={f"{s}.{t['name']}":(s,t) for s,ts in inv.items() for t in ts}
T=json.load(open(os.path.join(H,"mcp_targets.json")))
# skill targets: 20 from experiment 1 + 5 trending
P1=json.load(open(os.path.join(SP,"prompts.json"))); P2=json.load(open(os.path.join(H,"trending_skill_prompts.json")))
sk_targets={}
for k in list(P1)+list(P2):
    repo,name=k.split(":"); sk_targets[name]=load_skills(repo)[name]
# filler skills: trending repos first (realistic), then the big collection
trend_repos=["AgriciDaniel_claude-seo","elementalsouls_Claude-BugHunter","google-labs-code_stitch-skills","kajisho5_ffmpeg-skill","Jakeschincariol_instagram-agent-skill","pbakaus_impeccable","thedotmack_claude-mem","mattpocock_skills","addyosmani_agent-skills","emilkowalski_skills","anthropics_skills","coreyhaines31_marketingskills","vercel-labs_agent-skills","obsidianmd_obsidian-skills"]
fill_trend={}
for r in trend_repos:
    for n,v in load_skills(r).items():
        if n not in sk_targets and n not in BUILTIN and n not in fill_trend: fill_trend[n]=v
big=load_skills("sickn33_agentic-awesome-skills")
fill_big=[n for n in sorted(big) if n not in sk_targets and n not in BUILTIN and n not in fill_trend]; rnd.shuffle(fill_big)
tn=sorted(fill_trend); rnd.shuffle(tn)
shutil.rmtree(ENV,ignore_errors=True); os.makedirs(ENV)
info={}
# --- Experiment 2: MCP only
others=[i for i in byid if i not in T]; rnd.shuffle(others)
def servers_for(ids):
    out={}
    for i in ids:
        s,t=byid[i]; out.setdefault(s,[]).append(t)
    return out
for tid in T:
    b=os.path.join(ENV,"mcp_alone",tid.replace(".","__")); info[f"mcp_alone/{tid}"]=finish(b,servers_for([tid]))
info["mcp_pack20"]=finish(os.path.join(ENV,"mcp_pack20"),servers_for(list(T)))
info["mcp_crowd200"]=finish(os.path.join(ENV,"mcp_crowd200"),servers_for(list(T)+others[:200]))
info["mcp_crowdall"]=finish(os.path.join(ENV,"mcp_crowdall"),servers_for(list(T)+others))
# --- trending skills alone
for k in P2:
    n=k.split(":")[1]; b=os.path.join(ENV,"sk_alone",n); write_skill(b,n,*sk_targets[n]); finish(b,{})
# --- Experiment 3: realistic mix
target_servers={tid.split(".")[0] for tid in T}|{"pdf-reader-mcp","excel","ppt","word-document-server"}
def mixed(name, n_fill, all_tools):
    b=os.path.join(ENV,name)
    for n,v in sk_targets.items(): write_skill(b,n,*v)
    fl=(tn+fill_big)[:n_fill] if n_fill<=len(tn) else tn+fill_big[:n_fill-len(tn)]
    fl=tn[:min(len(tn),n_fill*2//5)]+fill_big[:n_fill-min(len(tn),n_fill*2//5)]
    for n in fl: write_skill(b,n,*(fill_trend.get(n) or big[n]))
    srv={s:list(ts) for s,ts in inv.items()} if all_tools else {s:list(inv[s]) for s in target_servers}
    nt=finish(b,srv); return len(sk_targets)+len(fl), nt
info["mixed_typical"]=mixed("mixed_typical",75,False)
info["mixed_heavy"]=mixed("mixed_heavy",375,True)
json.dump({"skill_targets":list(sk_targets)},open(os.path.join(ENV,"meta.json"),"w"))
for k,v in info.items():
    if not k.startswith("mcp_alone/"): print(k,v)
print("filler pools: trending",len(tn),"big",len(fill_big))
