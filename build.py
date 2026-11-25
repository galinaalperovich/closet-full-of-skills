"""Build isolated project dirs. Skills are reduced to name+description with a stub body, so nothing from the repos can execute."""
import json, os, random, re, shutil, sys, yaml
S=os.path.dirname(os.path.abspath(__file__)); REPOS=os.environ.get("SKILL_REPOS", os.path.join(S,"third_party","repos"))  # cloned by scripts/fetch_sources.sh
BUILTIN={"deep-research","design","slides","design-sync","dataviz","artifact-diagramming","whiteboard","artifact-capabilities","update-config","verify","debug","code-review","simplify","batch","fewer-permission-prompts","doctor","loop","schedule","claude-api","workflow-authoring","run","run-skill-generator","plugin-authoring","init","security-review"}
def load(repo):
    out={}
    for dp,dn,fn in os.walk(os.path.join(REPOS,repo)):
        dn[:]=[d for d in dn if d!=".git"]
        if "SKILL.md" in fn:
            t=open(os.path.join(dp,"SKILL.md"),encoding="utf-8",errors="replace").read()
            m=re.match(r"---[ \t]*\r?\n(.*?)\r?\n---",t,re.S)
            try: meta=yaml.safe_load(m.group(1)) if m else {}
            except Exception: meta={}
            if not isinstance(meta,dict): continue
            n=str(meta.get("name") or os.path.basename(dp)); d=str(meta.get("description") or "").strip()
            w=str(meta.get("when_to_use") or "").strip()
            if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$",n) and d and n not in out: out[n]=(d,w)
    return out
def write(base,name,d,w):
    p=os.path.join(base,".claude","skills",name); os.makedirs(p,exist_ok=True)
    ag=os.path.join(base,".agents"); os.makedirs(ag,exist_ok=True)   # Codex reads skills from .agents/skills: link it to the same folder
    if not os.path.lexists(os.path.join(ag,"skills")): os.symlink("../.claude/skills",os.path.join(ag,"skills"))
    fm={"name":name,"description":d}
    if w: fm["when_to_use"]=w
    open(os.path.join(p,"SKILL.md"),"w").write("---\n"+yaml.safe_dump(fm,allow_unicode=True,width=10**6,sort_keys=False)+"---\n\nThe instructions for this skill are omitted in this test. Reply with one short sentence.\n")
prompts=json.load(open(os.path.join(S,"prompts.json")))
targets={}
for key in prompts:
    repo,name=key.split(":"); targets[name]=load(repo)[name]
pool=load("sickn33_agentic-awesome-skills")
names=sorted(n for n in pool if n not in targets and n not in BUILTIN)
random.Random(7).shuffle(names)
shutil.rmtree(os.path.join(S,"envs"),ignore_errors=True)
for name,(d,w) in targets.items(): write(os.path.join(S,"envs","alone",name),name,d,w)
for cond,k in (("pack20",0),("crowd200",200),("crowd1000",1000)):
    b=os.path.join(S,"envs",cond)
    for name,(d,w) in targets.items(): write(b,name,d,w)
    for n in names[:k]: write(b,n,*pool[n])
    tot=sum(len(n)+min(1536,len(" ".join(x)))for n,x in list(targets.items())+[(n,pool[n]) for n in names[:k]])
    print(cond,len(targets)+k,"skills, listing chars",tot)
print("pool",len(names))
