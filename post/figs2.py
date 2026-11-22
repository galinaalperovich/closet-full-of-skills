"""SVG figures for post v2, computed from skill-trigger-spike/analysis/derived/v3 (run ANALYSIS_VERSION=3 analyze.py first)."""
import csv, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis", "derived", "v3")
B = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: list(csv.DictReader(open(os.path.join(D, f))))
FONT = 'font-family="IBM Plex Sans, system-ui, sans-serif"'; MONO = 'font-family="IBM Plex Mono, ui-monospace, monospace"'
COL = {"Haiku": "var(--s-haiku)", "Sonnet": "var(--s-sonnet)", "GPT": "var(--s-gpt)"}
F = lambda x: float(x)
out = {}

def line_chart(series, xlabels, aria, w=720, h=330, legend_note="", title=""):
    L, R, T, Bm = 56, 150, 44, 54
    pw, ph = w - L - R, h - T - Bm
    X = lambda i: L + pw * i / (len(xlabels) - 1)
    Y = lambda v: T + ph * (1 - v / 100)
    g = []
    for v in (0, 25, 50, 75, 100):
        g.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{L+pw}" y2="{Y(v):.1f}" stroke="currentColor" stroke-opacity="{.35 if v==0 else .12}"/>'
                 f'<text x="{L-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-size="11.5" fill="currentColor" fill-opacity=".7">{v}%</text>')
    for i, lab in enumerate(xlabels):
        anchor = "start" if i == 0 else ("end" if i == len(xlabels) - 1 else "middle")
        g.append(f'<text x="{X(i):.1f}" y="{T+ph+22}" text-anchor="{anchor}" font-size="12" fill="currentColor" fill-opacity=".8">{lab}</text>')
    lg = []; lx = L
    for s in series:
        da = ' stroke-dasharray="6 5"' if s.get("dash") else ""
        lg.append(f'<line x1="{lx}" y1="16" x2="{lx+22}" y2="16" stroke="{s["color"]}" stroke-width="2.5"{da}/><text x="{lx+28}" y="20" font-size="12" fill="currentColor">{s["name"]}</text>')
        lx += 36 + 7.2 * len(s["name"])
    lines, ends = [], []
    for s in series:
        pts = [(X(i), Y(v), v, i) for i, v in enumerate(s["values"]) if v is not None]
        da = ' stroke-dasharray="6 5"' if s.get("dash") else ""
        lines.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y,_,_ in pts)}" fill="none" stroke="{s["color"]}" stroke-width="2.2"{da}/>')
        for (x, y, v, i) in pts:
            if s.get("ci"):
                lo, hi = s["ci"][i]
                lines.append(f'<line x1="{x:.1f}" y1="{Y(lo):.1f}" x2="{x:.1f}" y2="{Y(hi):.1f}" stroke="{s["color"]}" stroke-opacity=".45" stroke-width="1.5"/>')
            ci_txt = f" (95% CI {s['ci'][i][0]:.0f}–{s['ci'][i][1]:.0f}%)" if s.get("ci") else ""
            lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{"var(--surface)" if s.get("dash") else s["color"]}" stroke="{s["color"]}" stroke-width="2"><title>{s["name"]}, {xlabels[i]}: {v:.1f}%{ci_txt}</title></circle>')
        x, y, v, _ = pts[-1]; ends.append([y, s, v])
    ends.sort(key=lambda e: e[0])
    for k in range(1, len(ends)):
        if ends[k][0] - ends[k-1][0] < 15: ends[k][0] = ends[k-1][0] + 15
    for y, s, v in ends:
        lines.append(f'<text x="{L+pw+12}" y="{y+4:.1f}" font-size="12" fill="currentColor"><tspan font-weight="600">{v:.0f}%</tspan> {s["short"]}</text>')
    dy = 24 if title else 0
    ttl = f'<text x="{L}" y="15" font-size="13" font-weight="600" fill="currentColor">{title}</text>' if title else ""
    return f'<svg viewBox="0 0 {w} {h+dy}" role="img" aria-label="{aria}"><g {FONT}>{ttl}<g transform="translate(0,{dy})">{"".join(g)}{"".join(lg)}{"".join(lines)}</g></g></svg>'

# --- Fig: how selection works (skills vs MCP tools)
out["fig_how"] = f'''<svg viewBox="0 0 980 330" role="img" aria-label="Diagram. Every request is sent with the skill listing (all names and descriptions, capped at a share of the context) and with MCP tool definitions. Claude Code sends tool names and fetches schemas on demand with ToolSearch; for Codex, reported tokens grew when 20 tool definitions were added. The model loads a skill, calls a tool, or uses only built-in actions. Loading a skill is itself a tool call (the Skill tool in Claude Code, a shell read of SKILL.md in Codex) that returns the skill instructions; the work then happens in more tool calls.">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<g stroke-width="1.6">
<rect x="2" y="135" width="164" height="60" rx="6" stroke="var(--accent)" fill="var(--accent)" fill-opacity=".10" stroke-width="2"/>
<rect x="200" y="14" width="300" height="128" rx="6" stroke="var(--s-sonnet)" fill="var(--s-sonnet)" fill-opacity=".08"/>
<rect x="200" y="182" width="300" height="134" rx="6" stroke="var(--s-haiku)" fill="var(--s-haiku)" fill-opacity=".08"/>
<rect x="550" y="14" width="200" height="50" rx="6" stroke="var(--s-sonnet)" fill="var(--s-sonnet)" fill-opacity=".16" stroke-width="2"/>
<rect x="550" y="86" width="200" height="50" rx="6" stroke="var(--band-mid)" fill="var(--band-mid)" fill-opacity=".08" stroke-dasharray="5 4"/>
<rect x="550" y="182" width="200" height="50" rx="6" stroke="var(--s-haiku)" fill="var(--s-haiku)" fill-opacity=".16" stroke-width="2"/>
<rect x="550" y="254" width="200" height="50" rx="6" stroke="var(--band-mid)" fill="var(--band-mid)" fill-opacity=".08" stroke-dasharray="5 4"/>
<rect x="790" y="6" width="180" height="66" rx="6" stroke="var(--s-sonnet)" fill="var(--s-sonnet)" fill-opacity=".08"/>
<rect x="790" y="96" width="180" height="50" rx="6" stroke="var(--s-sonnet)" fill="var(--s-sonnet)" fill-opacity=".08"/>
</g>
<g {FONT} font-size="13" fill="currentColor">
<text x="84" y="161" text-anchor="middle" font-weight="600">Your request</text>
<text x="84" y="180" text-anchor="middle" font-size="11.5" fill-opacity=".75">“Audit the SEO of my site.”</text>
<text x="214" y="36" font-weight="600">Skill listing, sent every time</text>
<text x="214" y="58" {MONO} font-size="11">seo-audit: When the user wants to…</text>
<text x="214" y="76" {MONO} font-size="11">pdf: Use this skill whenever…</text>
<text x="214" y="94" {MONO} font-size="11">tdd: Test-driven development…</text>
<text x="214" y="112" {MONO} font-size="11">… 1,000 more</text>
<text x="214" y="132" font-size="11" fill-opacity=".75">capped: 1% (Claude Code), 2% / 10K tokens (Codex)</text>
<text x="214" y="204" font-weight="600">MCP tool definitions</text>
<text x="214" y="226" font-size="11.5">Claude Code: tool names listed,</text>
<text x="214" y="243" font-size="11.5">schemas fetched with ToolSearch</text>
<text x="214" y="267" font-size="11.5">Codex: reported tokens grew when</text>
<text x="214" y="284" font-size="11.5">I added 20 tool definitions</text>
<text x="214" y="306" font-size="11" fill-opacity=".75">plus built-ins: Glob, Read, shell…</text>
<text x="650" y="44" text-anchor="middle" font-weight="600">Load a skill</text>
<text x="650" y="116" text-anchor="middle" font-weight="600">No skill selected</text>
<text x="650" y="212" text-anchor="middle" font-weight="600">Call an MCP tool</text>
<text x="650" y="284" text-anchor="middle" font-weight="600">Built-in actions only</text>
<text x="880" y="28" text-anchor="middle" font-weight="600">Called as a tool</text>
<text x="880" y="46" text-anchor="middle" font-size="11">Skill tool (Claude Code)</text>
<text x="880" y="62" text-anchor="middle" font-size="11">shell read of SKILL.md (Codex)</text>
<text x="880" y="118" text-anchor="middle" font-weight="600">Instructions come back</text>
<text x="880" y="135" text-anchor="middle" font-size="11">the work is more tool calls</text>
</g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#ah)">
<line x1="166" y1="152" x2="196" y2="96"/>
<line x1="166" y1="178" x2="196" y2="234"/>
<line x1="500" y1="62" x2="546" y2="42"/>
<line x1="500" y1="94" x2="546" y2="110"/>
<line x1="500" y1="230" x2="546" y2="210"/>
<line x1="500" y1="262" x2="546" y2="278"/>
<line x1="750" y1="39" x2="786" y2="39"/>
<line x1="880" y1="72" x2="880" y2="92"/>
</g>
<g {FONT} font-size="11" fill="currentColor" fill-opacity=".75"><text x="505" y="160">model</text><text x="505" y="174">decides</text></g>
</svg>'''

# --- Fig: the experiment in one picture
def dots(x, y, w, h, n, r=2.2):
    # n grey dots in a grid inside the box, the first one replaced by the highlighted target
    import math
    cols = max(1, int(math.ceil(math.sqrt(n * w / h)))); rows_ = int(math.ceil(n / cols))
    dx, dy = w / (cols + 1), h / (rows_ + 1); o = []
    for k in range(n):
        cx, cy = x + dx * (k % cols + 1), y + dy * (k // cols + 1)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="currentColor" fill-opacity=".28"/>')
    return "".join(o)
boxes = [("Alone", "1", 1, 3.2), ("20", "20", 20, 3.0), ("~220", "220", 220, 1.6), ("All", "1,020 skills / 791 tools", 900, 0.9)]
bx = []; X0 = 250; BW = 128; GAP = 14
for k, (lab, sub, n, r) in enumerate(boxes):
    x = X0 + k * (BW + GAP)
    bx.append(f'<rect x="{x}" y="58" width="{BW}" height="112" rx="6" fill="var(--surface)" stroke="currentColor" stroke-opacity=".45" stroke-width="1.3"/>')
    bx.append(dots(x + 4, 62, BW - 8, 104, n - 1, r) if n > 1 else "")   # the target is one of the n
    bx.append(f'<circle cx="{x + BW/2:.1f}" cy="114" r="7" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/>')
    bx.append(f'<text x="{x + BW/2:.1f}" y="192" text-anchor="middle" font-size="13" font-weight="600" fill="currentColor">{k+1}. {lab}</text>')
    bx.append(f'<text x="{x + BW/2:.1f}" y="209" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".7">{sub}</text>')
out["fig_setup"] = f'''<svg viewBox="0 0 980 250" role="img" aria-label="Diagram of the experiment. One request, written for one target skill or tool, is sent in four setups: the target alone, the 20 targets together, about 220 installed, and all of them (1,020 skills or 791 tools). Each run goes to Claude Code with Haiku or Sonnet, or to Codex with GPT. The score is the share of requests where the agent picked the target.">
<defs><marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<g {FONT}>
<rect x="2" y="70" width="210" height="88" rx="6" fill="var(--accent)" fill-opacity=".10" stroke="var(--accent)" stroke-width="2"/>
<text x="107" y="94" text-anchor="middle" font-size="13" font-weight="600" fill="currentColor">1 request</text>
<text x="107" y="114" text-anchor="middle" font-size="11.5" fill="currentColor">“Merge these two PDFs”</text>
<text x="107" y="134" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".75">written for one target:</text>
<text x="107" y="150" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".75"><tspan fill="var(--accent)" font-weight="600">●</tspan> the pdf skill</text>
<text x="{X0 + 2*(BW+GAP) - GAP/2:.0f}" y="40" text-anchor="middle" font-size="13" font-weight="600" fill="currentColor">the same request in 4 setups</text>
{"".join(bx)}
<rect x="822" y="70" width="156" height="88" rx="6" fill="var(--band-hi)" fill-opacity=".10" stroke="var(--band-hi)" stroke-width="1.6"/>
<text x="900" y="96" text-anchor="middle" font-size="13" font-weight="600" fill="currentColor">Picked the target?</text>
<text x="900" y="118" text-anchor="middle" font-size="12" fill="currentColor"><tspan fill="var(--band-hi)" font-weight="600">yes</tspan> / <tspan fill="var(--band-lo)" font-weight="600">no</tspan></text>
<text x="900" y="142" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".75">score = share of yes</text>
<text x="{X0 + 2*(BW+GAP) - GAP/2:.0f}" y="236" text-anchor="middle" font-size="11.5" fill="currentColor" fill-opacity=".75">each run: Claude Code (Haiku, Sonnet) or Codex (GPT)</text>
</g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#ah2)">
<line x1="212" y1="114" x2="246" y2="114"/>
<line x1="{X0 + 4*BW + 3*GAP}" y1="114" x2="818" y2="114"/>
</g>
</svg>'''

# --- Fig: skills curve (E1)
e1 = {(r["model"], r["setup"]): r for r in rd("e1_rates.csv")}
S = ["alone", "pack20", "crowd200", "crowd1000"]
ser = []
for m, nm in (("sonnet", "Sonnet"), ("haiku", "Haiku"), ("gpt", "GPT")):
    vals = [100 * F(e1[(m, s)]["rate"]) for s in S]
    ci = [(100 * F(e1[(m, s)]["req_boot_lo"]), 100 * F(e1[(m, s)]["req_boot_hi"])) for s in S]
    if m == "gpt": ci[0] = (96.9, 100)
    ser.append(dict(name=f"{nm} ({'Codex' if m=='gpt' else 'Claude Code'})", short=nm, color=COL[nm], values=vals, ci=ci))
out["fig_skills"] = line_chart(ser, ["Target alone", "20 skills", "220 skills", "1,020 skills"],
    "Line chart: share of requests where the designated skill was selected. Sonnet 93, 76, 56, 34 percent; Haiku 78, 48, 25, 16; GPT 100, 99, 83, 10, for the target alone, 20, 220 and 1,020 skills installed.")

# --- Fig: skills fade, tools bend (Claude, non-browser tools)
e2 = {(r["model"], r["setup"]): r for r in rd("e2_mcp_rates.csv")}
M = ["mcp_alone", "mcp_pack20", "mcp_crowd200", "mcp_crowdall"]
ser = []
for m, nm in (("sonnet", "Sonnet"), ("haiku", "Haiku")):
    ser.append(dict(name=f"{nm} skills", short=f"{nm} skills", color=COL[nm], values=[100 * F(e1[(m, s)]["rate"]) for s in S],
                    ci=[(100 * F(e1[(m, s)]["req_boot_lo"]), 100 * F(e1[(m, s)]["req_boot_hi"])) for s in S]))
    ser.append(dict(name=f"{nm} MCP tools", short=f"{nm} tools", color=COL[nm], dash=True,
                    values=[100 * F(e2[(m, s)]["nonbrowser_rate"]) for s in M],
                    ci=[(100 * F(e2[(m, s)]["nonbrowser_req_lo"]), 100 * F(e2[(m, s)]["nonbrowser_req_hi"])) for s in M]))
_tl = lambda m: ", ".join(f"{100 * F(e2[(m, s)]['nonbrowser_rate']):.0f}" for s in M)
out["fig_fade"] = line_chart(ser, ["Alone", "20 installed", "~220 installed", "All installed"], title="Claude Code: skills (solid) vs the 15 single-step, non-browser MCP tool targets (dashed)", aria=
    f"Line chart for Claude Code. Skills, solid lines: Sonnet 93 to 34 percent, Haiku 78 to 16 percent. Single-step MCP tools, dashed: Sonnet {_tl('sonnet')} percent; Haiku {_tl('haiku')} percent, for the target alone, 20, about 220 and all installed.")

# --- Fig: what happened on misses at 1,020 skills
segs = [("Designated skill", "target"), ("Equivalent alternative", "eq"), ("Other alternative", "alt"), ("No skill, finished", "none"), ("No skill, hit turn limit", "cap")]
rows = []
for m, nm in (("haiku", "Haiku"), ("sonnet", "Sonnet"), ("gpt", "GPT")):
    r = e1[(m, "crowd1000")]; n = F(r["n"])
    vals = [F(r["target_selected"]), F(r["miss_alt_equivalent"]), F(r["miss_alt_related"]) + F(r["miss_alt_inappropriate"]) + F(r["miss_alt_unassessable"]),
            F(r["miss_no_skill_completed"]), F(r["miss_no_skill_turn_limit"])]
    rows.append((nm, [100 * v / n for v in vals], int(n)))
x0, x1 = 90, 690; bw = x1 - x0; parts = []
leg = []; lx = x0
for n_, (lab, k) in enumerate(segs):
    if n_ == 3: lx = x0
    ly = 8 if n_ < 3 else 28
    leg.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="var(--seg-{k})"/>' + (f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="url(#hatch)"/>' if k == "cap" else "") + f'<text x="{lx+17}" y="{ly+10}" font-size="11.5" fill="currentColor">{lab}</text>')
    lx += 34 + 6.6 * len(lab)
for j, (nm, vals, n) in enumerate(rows):
    y = 60 + j * 50; cx = x0
    parts.append(f'<text x="{x0-10}" y="{y+21}" text-anchor="end" font-size="13" font-weight="600" fill="currentColor">{nm}</text>')
    for (lab, k), v in zip(segs, vals):
        wv = bw * v / 100
        if wv <= 0: continue
        parts.append(f'<rect x="{cx+1:.1f}" y="{y}" width="{max(0,wv-2):.1f}" height="30" fill="var(--seg-{k})"><title>{nm}: {lab} {v:.1f}%</title></rect>')
        if k == "cap": parts.append(f'<rect x="{cx+1:.1f}" y="{y}" width="{max(0,wv-2):.1f}" height="30" fill="url(#hatch)" pointer-events="none"/>')
        if wv > 42: parts.append(f'<text x="{cx+wv/2:.1f}" y="{y+20}" text-anchor="middle" font-size="12" font-weight="600" fill="var(--on-seg-{k})">{v:.0f}%</text>')
        cx += wv
    parts.append(f'<text x="{x1+6}" y="{y+20}" font-size="11" fill="currentColor" fill-opacity=".7">n={n}</text>')
out["fig_misses"] = f'''<svg viewBox="0 0 740 216" role="img" aria-label="Stacked bars at 1,020 skills. Haiku: 16 percent designated skill, 1 equivalent alternative, 3 other alternative, 37 no skill and finished, 44 no skill and hit the turn limit. Sonnet: 34, 2, 0, 44, 19. GPT: 10, 10, 14, 66, 0.">
<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="currentColor" stroke-opacity=".35" stroke-width="2"/></pattern></defs>
<g {FONT}>{"".join(leg)}{"".join(parts)}</g></svg>'''

# --- Fig: mixed scenarios (sequential ramp: load level), request-weighted rates with 95% intervals
ec = {(r["model"], r["series"], r["setup"]): r for r in rd("e3_chart_rates.csv")}
groups = []
for m, nm in (("haiku", "Haiku"), ("sonnet", "Sonnet")):
    for series, lab in (("skill requests", "150 skill requests"), ("single-step tool requests", "90 tool requests")):
        groups.append((nm, lab, [ec[(m, series, st)] for st in ("single component", "mixed_smaller", "mixed_larger")]))
W, Hh = 720, 340; L, T, Bm = 50, 40, 62; pw = W - L - 20; ph = Hh - T - Bm
Y = lambda v: T + ph * (1 - v / 100)
gp = []; gw = pw / len(groups); bwid = 30
for v in (0, 25, 50, 75, 100):
    gp.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{L+pw}" y2="{Y(v):.1f}" stroke="currentColor" stroke-opacity="{.35 if v==0 else .12}"/><text x="{L-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-size="11.5" fill="currentColor" fill-opacity=".7">{v}%</text>')
labs = ["Single component", "Mixed, smaller", "Mixed, larger"]
lx = L
for k, lab in enumerate(labs):
    gp.append(f'<rect x="{lx}" y="10" width="12" height="12" rx="2" fill="var(--seq{k+1})"/><text x="{lx+17}" y="20" font-size="11.5" fill="currentColor">{lab}</text>'); lx += 34 + 6.4 * len(lab)
gp.append(f'<text x="{lx+4}" y="20" font-size="11.5" fill="currentColor" fill-opacity=".75">whiskers: 95% CI</text>')
for gi, (nm, kind, rows) in enumerate(groups):
    cx = L + gw * gi + gw / 2 - 1.5 * bwid - 3
    for k, r in enumerate(rows):
        v, lo, hi = 100 * F(r["rate"]), 100 * F(r["req_lo"]), 100 * F(r["req_hi"])
        x = cx + k * (bwid + 3); y = Y(v); xm = x + bwid / 2
        gp.append(f'<path d="M{x:.1f},{Y(0):.1f} V{y+4:.1f} Q{x:.1f},{y:.1f} {x+4:.1f},{y:.1f} H{x+bwid-4:.1f} Q{x+bwid:.1f},{y:.1f} {x+bwid:.1f},{y+4:.1f} V{Y(0):.1f} Z" fill="var(--seq{k+1})"><title>{nm} {kind}, {labs[k]}: {v:.1f}% (95% CI {lo:.0f}–{hi:.0f}%)</title></path>')
        gp.append(f'<path d="M{xm:.1f},{Y(hi):.1f} V{Y(lo):.1f} M{xm-4:.1f},{Y(hi):.1f} H{xm+4:.1f} M{xm-4:.1f},{Y(lo):.1f} H{xm+4:.1f}" stroke="currentColor" stroke-opacity=".7" stroke-width="1.3" fill="none"/>')
        gp.append(f'<text x="{xm:.1f}" y="{Y(hi)-5:.1f}" text-anchor="middle" font-size="11" fill="currentColor">{v:.0f}</text>')
    gp.append(f'<text x="{L+gw*gi+gw/2:.1f}" y="{T+ph+20}" text-anchor="middle" font-size="12.5" font-weight="600" fill="currentColor">{nm}</text><text x="{L+gw*gi+gw/2:.1f}" y="{T+ph+37}" text-anchor="middle" font-size="12" fill="currentColor" fill-opacity=".8">{kind}</text>')
_ml = lambda m, se: ", ".join(f"{100 * F(ec[(m, se, st)]['rate']):.0f}" for st in ("single component", "mixed_smaller", "mixed_larger"))
out["fig_mix"] = f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="Grouped bars with 95% intervals, Claude Code. Skill requests: Haiku {_ml("haiku", "skill requests")} percent; Sonnet {_ml("sonnet", "skill requests")} percent. Single-step tool requests: Haiku {_ml("haiku", "single-step tool requests")} percent; Sonnet {_ml("sonnet", "single-step tool requests")} percent, for single component, mixed smaller and mixed larger setups."><g {FONT}>{"".join(gp)}</g></svg>'

# --- Fig: forest plot, paired change versus "alone" (percentage points, 95% CI by request-cluster bootstrap)
pv = rd("paired_vs_alone.csv")
SIZE = {"pack20": "20", "crowd200": "~220", "crowd1000": "1,020", "mcp_pack20": "20", "mcp_crowd200": "~220", "mcp_crowdall": "791"}
NM = {"haiku": "Haiku", "sonnet": "Sonnet", "gpt": "GPT"}
sections = [("Skills: change vs target skill alone", "E1 skills", "skills"), ("Single-step MCP tools: change vs target tool alone", "E2 MCP single-step tools", "tools")]
W = 720; x0, x1 = 210, 580; X = lambda d: x0 + (x1 - x0) * (d + 100) / 110
rows_svg = []; y = 44
for v in (-100, -75, -50, -25, 0):
    rows_svg.append(f'<text x="{X(v):.1f}" y="30" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".7">{v:+d}</text>'.replace("+0", "0"))
grid_top = y
for title, exp, unit in sections:
    rows_svg.append(f'<text x="12" y="{y+14}" font-size="12.5" font-weight="600" fill="currentColor">{title}</text>'); y += 26
    for r in [r for r in pv if r["experiment"] == exp]:
        d, lo, hi = (100 * F(r[k]) for k in ("diff", "req_lo", "req_hi"))
        col = COL[NM[r["model"]]]; n = r["n_pairs"]
        lab = f'{NM[r["model"]]}, {SIZE[r["to_setup"]]} {unit}' + (" (24 requests)" if n == "24" else "")
        fill = col if unit == "skills" else "var(--surface)"
        rows_svg.append(f'<text x="{x0-12}" y="{y+4}" text-anchor="end" font-size="12" fill="currentColor">{lab}</text>'
                        f'<line x1="{X(lo):.1f}" y1="{y}" x2="{X(hi):.1f}" y2="{y}" stroke="{col}" stroke-width="2.5" stroke-linecap="round"/>'
                        f'<circle cx="{X(d):.1f}" cy="{y}" r="5.5" fill="{fill}" stroke="{col}" stroke-width="2"><title>{lab}: {d:+.1f} pp (95% CI {lo:+.1f} to {hi:+.1f}), {n} paired requests</title></circle>'
                        f'<text x="{x1+12}" y="{y+4}" font-size="11.5" fill="currentColor"><tspan font-weight="600">{d:+.0f}</tspan> [{lo:+.0f}, {hi:+.0f}]</text>'.replace("+0]", "0]").replace("[+0,", "[0,"))
        y += 22
    y += 10
grid = "".join(f'<line x1="{X(v):.1f}" y1="{grid_top}" x2="{X(v):.1f}" y2="{y-6}" stroke="currentColor" stroke-opacity="{.45 if v==0 else .1}" stroke-width="{1.5 if v==0 else 1}"/>' for v in (-100, -75, -50, -25, 0))
rows_svg.append(f'<text x="{(x0+x1)/2:.1f}" y="{y+10}" text-anchor="middle" font-size="11.5" fill="currentColor" fill-opacity=".75">change in percentage points (same requests in both setups)</text>')
_fl = lambda exp, m: ", ".join(f"{100 * F(r['diff']):+.0f}" for r in pv if r["experiment"] == exp and r["model"] == m)
_aria = ("Forest plot of paired changes versus the target alone, in percentage points, with 95% confidence intervals. "
         f"Skills at 20, 220 and 1,020: Haiku {_fl('E1 skills', 'haiku')}; Sonnet {_fl('E1 skills', 'sonnet')}; GPT {_fl('E1 skills', 'gpt')}. "
         f"Single-step MCP tools at 20, 220 and 791: Haiku {_fl('E2 MCP single-step tools', 'haiku')}; Sonnet {_fl('E2 MCP single-step tools', 'sonnet')}; GPT {_fl('E2 MCP single-step tools', 'gpt')} at 20 tools on 24 requests.")
out["fig_forest"] = (f'<svg viewBox="0 0 {W} {y+22}" role="img" aria-label="{_aria}">'
                     f'<g {FONT}>{grid}{"".join(rows_svg)}</g></svg>')

# --- Fig: which skills kept being selected (Sonnet): an arrow per skill from "alone" to "with 1,020 skills",
#     grouped by where the skill ends up. Diverging scheme: teal (kept), grey (sometimes), red-orange (rarely); validated.
pt = [r for r in rd("e1_per_target.csv") if r["model"] == "sonnet"]
frac = lambda s: (int(s.split("/")[0]), int(s.split("/")[1]))
for r in pt:
    r["ka"], r["na"] = frac(r["alone"]); r["kc"], r["nc"] = frac(r["crowd1000"])
    r["a"], r["c"] = 100 * r["ka"] / r["na"], 100 * r["kc"] / r["nc"]
bands = [("Kept being selected", "two-thirds of runs or more", lambda c: c >= 200 / 3 - 1e-9, "hi"),
         ("Sometimes", "a third to two-thirds of runs", lambda c: 100 / 3 - 1e-9 <= c < 200 / 3 - 1e-9, "mid"),
         ("Rarely or never", "under a third of runs", lambda c: c < 100 / 3 - 1e-9, "lo")]
W = 760; x0, x1 = 200, 600; sc = (x1 - x0) / 100; X = lambda v: x0 + v * sc
defs = "".join(f'<marker id="dbh-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--band-{k})"/></marker>' for k in ("hi", "mid", "lo"))
parts = []
# legend: a worked example of one arrow
ly = 14
parts.append(f'<circle cx="{x0}" cy="{ly}" r="5.5" fill="currentColor"/>'
             f'<line x1="{x0+60}" y1="{ly}" x2="{x0+8}" y2="{ly}" stroke="currentColor" stroke-width="2" marker-end="url(#dbh-ex)"/>'
             f'<circle cx="{x0+66}" cy="{ly}" r="5" fill="var(--surface)" stroke="currentColor" stroke-width="2"/>'
             f'<text x="{x0+82}" y="{ly+4}" font-size="11.5" fill="currentColor">arrow: from the skill alone (hollow) to the same skill among 1,020 others (filled)</text>')
defs += '<marker id="dbh-ex" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>'
y = 44
for v in (0, 25, 50, 75, 100):
    parts.append(f'<text x="{X(v):.1f}" y="{y}" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".7">{v}%</text>')
parts.append(f'<text x="{x1+34}" y="{y}" font-size="11" fill="currentColor" fill-opacity=".7">alone → 1,020</text>')
grid_top = y + 8; y += 26
for name, sub, test, k in bands:
    rows = sorted([r for r in pt if test(r["c"])], key=lambda r: (-r["c"], -r["a"], r["target"]))
    parts.append(f'<rect x="12" y="{y-9}" width="4" height="13" rx="1" fill="var(--band-{k})"/>'
                 f'<text x="22" y="{y+2}" font-size="12.5" font-weight="600" fill="currentColor">{name}<tspan font-weight="400" fill-opacity=".7"> · {sub} with 1,020 skills ({len(rows)})</tspan></text>')
    y += 22
    for r in rows:
        xa, xc = X(r["a"]), X(r["c"]); col = f"var(--band-{k})"
        tip = xc + 8 if xa > xc else xc - 8
        # every change gets an arrowhead; a skill whose two dots coincide did not change
        arrow = (f'<line x1="{xa:.1f}" y1="{y}" x2="{tip:.1f}" y2="{y}" stroke="{col}" stroke-width="2.2" marker-end="url(#dbh-{k})"/>' if abs(xa - xc) > 0.5 else "")
        parts.append(f'<text x="{x0-14}" y="{y+4}" text-anchor="end" {MONO} font-size="11.5" fill="currentColor">{r["target"]}</text>' + arrow +
                     f'<circle cx="{xa:.1f}" cy="{y}" r="5" fill="var(--surface)" stroke="{col}" stroke-width="2"><title>{r["target"]} alone: {r["a"]:.0f}% ({r["ka"]} of {r["na"]})</title></circle>'
                     f'<circle cx="{xc:.1f}" cy="{y}" r="5.5" fill="{col}"><title>{r["target"]} with 1,020 skills: {r["c"]:.0f}% ({r["kc"]} of {r["nc"]})</title></circle>'
                     f'<text x="{x1+34}" y="{y+4}" font-size="11.5" fill="currentColor" fill-opacity=".75">{r["a"]:.0f}% → <tspan font-weight="600" fill-opacity="1">{r["c"]:.0f}%</tspan></text>')
        y += 21
    y += 12
grid = "".join(f'<line x1="{X(v):.1f}" y1="{grid_top}" x2="{X(v):.1f}" y2="{y-14}" stroke="currentColor" stroke-opacity=".1"/>' for v in (0, 25, 50, 75, 100))
out["fig_dumbbell"] = (f'<svg viewBox="0 0 {W} {y}" role="img" aria-label="Arrow chart for Sonnet: each skill from installed alone to installed among 1,020 others, 18 runs each, grouped by where it ends up. '
                       'Kept being selected: grill-me and json-canvas 100 to 94 percent, mcp-builder 100 to 78, xlsx 83 to 78, pptx 100 to 67. '
                       'Sometimes: docx 94 to 56, pdf 100 to 50, tdd 100 to 39, obsidian-markdown 83 to 33. '
                       'Rarely or never: 11 skills, including seo-audit, security-and-hardening, diagnosing-bugs and animate, which fell from 100 to 0.">'
                       f'<defs>{defs}</defs><g {FONT}>{grid}{"".join(parts)}</g></svg>')

# --- Fig: toy softmax, share of attention left for the target skill (illustration, not data)
M = 20.0   # target matches the request 20x better than an unrelated skill (score gap ln 20)
toy = [("Alone (1 skill)", 0, 0), ("20 skills", 19, 0), ("220 skills", 219, 0), ("1,020 skills", 1019, 0), ("1,020 incl. 16 look-alikes", 1003, 16)]
segs_a = [("Target skill", "target"), ("Look-alikes (match as well as the target)", "alt"), ("Other skills", "none")]
x0, x1 = 196, 636; bw = x1 - x0; pa = []; lx = x0
for lab, k in segs_a:
    pa.append(f'<rect x="{lx}" y="8" width="12" height="12" rx="2" fill="var(--seg-{k})"/><text x="{lx+17}" y="18" font-size="11.5" fill="currentColor">{lab}</text>'); lx += 34 + 6.3 * len(lab)
for j, (lab, n_other, n_look) in enumerate(toy):
    tot = M + n_other + M * n_look
    vals = [100 * M / tot, 100 * M * n_look / tot, 100 * n_other / tot]
    y = 40 + j * 40; cx = x0
    pa.append(f'<text x="{x0-10}" y="{y+17}" text-anchor="end" font-size="12.5" fill="currentColor">{lab}</text>')
    for (sl, k), v in zip(segs_a, vals):
        wv = bw * v / 100
        if wv <= 0: continue
        pa.append(f'<rect x="{cx+1:.1f}" y="{y}" width="{max(2.5, wv-2):.1f}" height="26" fill="var(--seg-{k})"><title>{lab}: {sl} {v:.1f}%</title></rect>')
        if wv > 46: pa.append(f'<text x="{cx+wv/2:.1f}" y="{y+17}" text-anchor="middle" font-size="11.5" font-weight="600" fill="var(--on-seg-{k})">{v:.0f}%</text>')
        cx += wv
    pa.append(f'<text x="{x1+10}" y="{y+17}" font-size="12" fill="currentColor">target <tspan font-weight="600">{vals[0]:.1f}%</tspan></text>')
pa.append(f'<text x="{x0}" y="{40 + 40*len(toy) + 8}" font-size="11.5" fill="currentColor" fill-opacity=".75">Illustrative arithmetic, not a measurement and not a model of these agents.</text>')
out["fig_attn"] = (f'<svg viewBox="0 0 740 {62 + 40*len(toy)}" role="img" aria-label="Toy model, not data. If the target skill matches the request 20 times better than an unrelated skill, its share of attention is 100 percent alone, 51 percent with 20 skills, 8 percent with 220, 2 percent with 1,020, and 1.5 percent with 1,020 skills of which 16 look-alikes match as well as the target. The look-alikes then take 24 percent.">'
                   f'<g {FONT}>{"".join(pa)}</g></svg>')

old = json.load(open(os.path.join(B, "figs.json")))
out["fig_weight"] = old["fig_weight"]
json.dump(out, open(os.path.join(B, "figs2.json"), "w"))
print("figures:", list(out))
