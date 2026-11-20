"""Generate the post's SVG figures from the spike data."""
import json, os
from collections import defaultdict
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
C=["alone","pack20","crowd200","crowd1000"]
def load(f): return [json.loads(l) for l in open(os.path.join(D,f))]
R={"Haiku":load("haiku.jsonl"),"Sonnet":load("sonnet.jsonl"),"GPT":load("gpt.jsonl")}
COL={"Haiku":"var(--s-haiku)","Sonnet":"var(--s-sonnet)","GPT":"var(--s-gpt)"}
FONT='font-family="IBM Plex Sans, system-ui, sans-serif"'; MONO='font-family="IBM Plex Mono, monospace"'
def rate(rs,c):
    x=[r for r in rs if r["cond"]==c]; return 100*sum(r["hit"] for r in x)/len(x)
out={}

# Fig 1: how a skill gets chosen
out["fig_how"]=f'''<svg viewBox="0 0 720 250" role="img" aria-label="Diagram: every request is sent with a list of all skill names and descriptions. The model decides from that list whether to load a skill. Only then is the skill's full instructions file read.">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<g fill="none" stroke="currentColor" stroke-width="1.5">
<rect x="10" y="85" width="140" height="60" rx="6"/>
<rect x="210" y="20" width="230" height="190" rx="6"/>
<rect x="500" y="40" width="200" height="60" rx="6" stroke="var(--accent)" stroke-width="2"/>
<rect x="500" y="150" width="200" height="60" rx="6" stroke-dasharray="5 4"/>
</g>
<g {FONT} font-size="13" fill="currentColor">
<text x="80" y="112" text-anchor="middle" font-weight="600">Your request</text>
<text x="80" y="130" text-anchor="middle" font-size="12" fill-opacity=".75">"Audit the SEO of my site."</text>
<text x="325" y="42" text-anchor="middle" font-weight="600">Skill listing, sent every time</text>
<text x="225" y="70" {MONO} font-size="11.5">seo-audit: When the user wants</text>
<text x="225" y="86" {MONO} font-size="11.5">  to audit or diagnose SEO...</text>
<text x="225" y="108" {MONO} font-size="11.5">pdf: Use this skill whenever...</text>
<text x="225" y="130" {MONO} font-size="11.5">tdd: Test-driven development...</text>
<text x="225" y="152" {MONO} font-size="11.5">seo-technical: ...</text>
<text x="225" y="174" {MONO} font-size="11.5">... 1,000 more names</text>
<text x="325" y="198" text-anchor="middle" font-size="11.5" fill-opacity=".75">capped at 1% (Claude Code) or 2% (Codex) of context</text>
<text x="600" y="67" text-anchor="middle" font-weight="600">Load seo-audit</text>
<text x="600" y="85" text-anchor="middle" font-size="12" fill-opacity=".75">reads the full SKILL.md</text>
<text x="600" y="177" text-anchor="middle" font-weight="600">Load nothing</text>
<text x="600" y="195" text-anchor="middle" font-size="12" fill-opacity=".75">just starts working</text>
</g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#ar)">
<line x1="150" y1="115" x2="206" y2="115"/>
<line x1="440" y1="90" x2="496" y2="72"/>
<line x1="440" y1="140" x2="496" y2="178"/>
</g>
<g {FONT} font-size="11.5" fill="currentColor" fill-opacity=".8">
<text x="452" y="70">model decides</text>
</g>
</svg>'''

# Fig 2: description weight of big collections
coll=[("sickn33/agentic-awesome-skills",3049,129184),("mukul975/Anthropic-Cybersecurity-Skills",818,88887),("davila7/claude-code-templates",904,68277),("github/awesome-copilot",482,41557),("alirezarezvani/claude-skills",467,28769),("K-Dense-AI/scientific-agent-skills",177,17731),("affaan-m/ECC",331,17074),("wshobson/agents",185,12898),("my own laptop",67,9037)]
x0,x1=270,690; mx=130000; s=(x1-x0)/mx; rows=[]
for i,(n,k,t) in enumerate(coll):
    y=30+i*30
    rows.append(f'<text x="{x0-10}" y="{y+14}" text-anchor="end" font-size="12">{n}</text><rect x="{x0}" y="{y+2}" width="{t*s:.1f}" height="18" fill="var(--accent)" fill-opacity="{0.45 if n=="my own laptop" else 0.85}"/><text x="{x0+t*s+6:.1f}" y="{y+15}" {MONO} font-size="11">{t//1000}K</text>')
yb=30+len(coll)*30+4
bud=x0+2000*s; gat=x0+72000*s
out["fig_weight"]=f'''<svg viewBox="0 0 740 {yb+40}" role="img" aria-label="Bar chart: estimated tokens of skill descriptions per collection, from 129 thousand for sickn33 down to 9 thousand on my laptop, against a listing budget of about 2 thousand tokens. The largest collection's descriptions are longer than The Great Gatsby, 72 thousand tokens.">
<g {FONT} fill="currentColor">{''.join(rows)}</g>
<line x1="{bud:.1f}" y1="22" x2="{bud:.1f}" y2="{yb}" stroke="var(--warn)" stroke-width="2"/>
<line x1="{gat:.1f}" y1="22" x2="{gat:.1f}" y2="{yb}" stroke="currentColor" stroke-dasharray="4 4" stroke-opacity=".6"/>
<g {FONT} font-size="11.5">
<text x="{bud+4:.1f}" y="{yb+16}" fill="var(--warn)" font-weight="600">≈2K budget</text>
<text x="{gat:.1f}" y="{yb+16}" text-anchor="middle" fill="currentColor" fill-opacity=".8">The Great Gatsby ≈72K tokens</text>
<text x="{x0}" y="14" fill="currentColor" fill-opacity=".7">Estimated tokens of skill descriptions (characters ÷ 4)</text>
</g></svg>'''

# Fig 3: main curve
X=[70,240,410,580]; y=lambda v:260-2.3*v
lines=[];dots=[];labs=[]
ends={}
for m,rs in R.items():
    vals=[rate(rs,c) for c in C]; ends[m]=vals[-1]
    pts=" ".join(f"{X[i]},{y(v):.1f}" for i,v in enumerate(vals))
    lines.append(f'<polyline fill="none" stroke="{COL[m]}" stroke-width="2.5" points="{pts}"/>')
    dots+= [f'<circle cx="{X[i]}" cy="{y(v):.1f}" r="4" fill="{COL[m]}"/>' for i,v in enumerate(vals)]
lab_y={"Sonnet":y(ends["Sonnet"])+4,"Haiku":y(ends["Haiku"])-2,"GPT":y(ends["GPT"])+12}
labs=[f'<text x="592" y="{lab_y[m]:.1f}" fill="{COL[m]}">{m} {ends[m]:.0f}%</text>' for m in R]
grid="".join(f'<line x1="70" y1="{y(v):.1f}" x2="580" y2="{y(v):.1f}"/>' for v in (0,25,50,75,100))
yl="".join(f'<text x="60" y="{y(v)+4:.1f}">{v}%</text>' for v in (0,25,50,75,100))
out["fig_curve"]=f'''<svg viewBox="0 0 700 300" role="img" aria-label="Line chart of how often the right skill fired. Haiku: 78, 48, 25, 16 percent. Sonnet: 93, 76, 56, 34 percent. GPT: 100, 99, 83, 10 percent, for the skill alone, 20 skills, 220 skills and 1,020 skills installed.">
<g stroke="currentColor" stroke-opacity=".15">{grid}</g>
<g {MONO} font-size="12" fill="currentColor" fill-opacity=".7" text-anchor="end">{yl}</g>
<g {FONT} font-size="12" fill="currentColor" fill-opacity=".8" text-anchor="middle"><text x="70" y="282">alone</text><text x="240" y="282">20 skills</text><text x="410" y="282">220 skills</text><text x="580" y="282">1,020 skills</text></g>
{''.join(lines)}{''.join(dots)}
<g {FONT} font-size="12" font-weight="600">{''.join(labs)}</g></svg>'''

# Fig 4: dumbbell per skill, Sonnet alone vs crowd1000
look={"diagnosing-bugs":14,"security-and-hardening":16,"seo-audit":16,"animate":7,"frontend-design":None,"copywriting":1,"tdd":1,"json-canvas":1,"grill-me":0,"xlsx":0,"pdf":1,"humanizer":0}
t=defaultdict(lambda: defaultdict(lambda:[0,0]))
for r in R["Sonnet"]:
    a=t[r["target"]][r["cond"]]; a[0]+=r["hit"]; a[1]+=1
items=sorted(t, key=lambda k:(t[k]["crowd1000"][0], t[k]["alone"][0]))
x0,x1=210,650; sc=(x1-x0)/100; rows=[]
for i,k in enumerate(items):
    yy=40+i*22; a=100*t[k]["alone"][0]/18; b=100*t[k]["crowd1000"][0]/18
    rows.append(f'<text x="{x0-12}" y="{yy+4}" text-anchor="end" {MONO} font-size="11.5" fill="currentColor">{k}</text>'
      f'<line x1="{x0+b*sc:.1f}" y1="{yy}" x2="{x0+a*sc:.1f}" y2="{yy}" stroke="currentColor" stroke-opacity=".35" stroke-width="2"/>'
      f'<circle cx="{x0+a*sc:.1f}" cy="{yy}" r="5" fill="var(--s-sonnet)" fill-opacity=".35" stroke="var(--s-sonnet)"/>'
      f'<circle cx="{x0+b*sc:.1f}" cy="{yy}" r="5" fill="var(--s-sonnet)"/>')
H=40+len(items)*22
gx="".join(f'<line x1="{x0+v*sc:.1f}" y1="28" x2="{x0+v*sc:.1f}" y2="{H-8}" stroke="currentColor" stroke-opacity=".12"/><text x="{x0+v*sc:.1f}" y="{H+8}" text-anchor="middle" {MONO} font-size="11" fill="currentColor" fill-opacity=".7">{v}%</text>' for v in (0,25,50,75,100))
out["fig_dumbbell"]=f'''<svg viewBox="0 0 680 {H+20}" role="img" aria-label="Dot plot for Sonnet: each skill's hit rate alone versus with 1,000 other skills. diagnosing-bugs, security-and-hardening, animate and seo-audit fall from 100 percent to 0. grill-me and json-canvas stay near 94 percent.">
{gx}
<g {FONT} font-size="11.5" fill="currentColor"><circle cx="{x0}" cy="12" r="5" fill="var(--s-sonnet)" fill-opacity=".35" stroke="var(--s-sonnet)"/><text x="{x0+10}" y="16">alone</text><circle cx="{x0+70}" cy="12" r="5" fill="var(--s-sonnet)"/><text x="{x0+80}" y="16">with 1,000 other skills</text></g>
{''.join(rows)}</svg>'''

# Fig 5: what misses look like at 1,000 skills
bars=[];yy=30
for m,rs in R.items():
    x=[r for r in rs if r["cond"]=="crowd1000"]; n=len(x)
    right=sum(r["hit"] for r in x); other=sum(1 for r in x if not r["hit"] and r["fired"]); none=n-right-other
    xx=150; w=500
    segs=[(right,"var(--accent)","right skill"),(other,"var(--s-haiku)","another skill"),(none,"currentColor","no skill")]
    bars.append(f'<text x="140" y="{yy+16}" text-anchor="end" font-size="12.5" font-weight="600">{m}</text>')
    for v,c,lab in segs:
        ww=w*v/n
        op=' fill-opacity=".22"' if c=="currentColor" else ''
        bars.append(f'<rect x="{xx:.1f}" y="{yy}" width="{ww:.1f}" height="24" fill="{c}"{op}/>')
        if ww>34: bars.append(f'<text x="{xx+ww/2:.1f}" y="{yy+16}" text-anchor="middle" {MONO} font-size="11" fill="currentColor">{100*v/n:.0f}%</text>')
        xx+=ww
    yy+=38
out["fig_misses"]=f'''<svg viewBox="0 0 680 {yy+30}" role="img" aria-label="Stacked bars with 1,000 extra skills installed. Haiku: 16 percent right skill, 3 percent another skill, 81 percent no skill. Sonnet: 34, 2.5 and 64 percent. GPT: 10, 24 and 66 percent.">
<g {FONT} fill="currentColor">{''.join(bars)}</g>
<g {FONT} font-size="11.5" fill="currentColor"><rect x="150" y="{yy+4}" width="12" height="12" fill="var(--accent)"/><text x="168" y="{yy+14}">right skill</text><rect x="260" y="{yy+4}" width="12" height="12" fill="var(--s-haiku)"/><text x="278" y="{yy+14}">another skill</text><rect x="380" y="{yy+4}" width="12" height="12" fill="currentColor" fill-opacity=".22"/><text x="398" y="{yy+14}">no skill at all</text></g></svg>'''
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"figs.json"),"w"))
print({k:len(v) for k,v in out.items()})
