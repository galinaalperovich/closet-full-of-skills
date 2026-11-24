"""SVG figures for the post, computed from analysis/derived (run analysis/analyze.py first). Writes figs.json."""
import csv, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis", "derived")
B = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: list(csv.DictReader(open(os.path.join(D, f))))
FONT = 'font-family="IBM Plex Sans, system-ui, sans-serif"'; MONO = 'font-family="IBM Plex Mono, ui-monospace, monospace"'
COL = {"Haiku": "var(--s-haiku)", "Sonnet": "var(--s-sonnet)", "GPT": "var(--s-gpt)", "GPT-6 Astra": "var(--s-gpt)"}
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

# --- Hero image (top of the post, also the link-preview card): the same skill among more and more others
import math, random
def hero_dots(x, y, s, n, r):
    # n-1 grey dots on a jittered grid inside an s-by-s square, plus the target at a fixed spot (same spot in every square)
    if n == 1: return []
    cols = math.ceil(math.sqrt(n)); rows_ = math.ceil(n / cols); d = s / cols
    cells = [(i, j) for j in range(rows_) for i in range(cols)]
    ti, tj = round(.62 * (cols - 1)), round(.42 * (rows_ - 1))
    cells.remove((ti, tj)); rnd = random.Random(n); rnd.shuffle(cells)
    o = []
    for i, j in cells[:n - 1]:
        jx, jy = (rnd.random() - .5) * d * .45, (rnd.random() - .5) * d * .45
        o.append(f'<circle cx="{x + d * (i + .5) + jx:.1f}" cy="{y + (s - rows_ * d) / 2 + d * (j + .5) + jy:.1f}" r="{r}"/>')
    return o, (x + d * (ti + .5), y + (s - rows_ * d) / 2 + d * (tj + .5))
e1h = {(r["model"], r["setup"]): r for r in rd("e1_rates.csv")}
_rng = lambda s: (lambda v: f"{min(v)}–{max(v)}%")([round(100 * F(e1h[(m, s)]["rate"])) for m in ("haiku", "sonnet", "gpt")])
HS, HG, HX0, HY0 = 240, 44, 60, 108
hero = []
for k, (n, lab, s, r, col) in enumerate([(1, "1 skill", "alone", 0, "var(--band-hi)"), (20, "20 skills", "pack20", 6.5, "currentColor"),
                                         (220, "220 skills", "crowd200", 3.6, "currentColor"), (1020, "1,020 skills", "crowd1000", 2.2, "var(--band-lo)")]):
    x = HX0 + k * (HS + HG); cx = x + HS / 2
    hero.append(f'<rect x="{x}" y="{HY0}" width="{HS}" height="{HS}" rx="10" fill="var(--surface)" stroke="currentColor" stroke-opacity=".35" stroke-width="1.5"/>')
    if n == 1: tx, ty = cx, HY0 + HS / 2
    else:
        dl, (tx, ty) = hero_dots(x + 12, HY0 + 12, HS - 24, n, r)
        hero.append(f'<g fill="currentColor" fill-opacity=".30">{"".join(dl)}</g>')
    hero.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="17" fill="var(--accent)" fill-opacity=".22"/>'
                f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="9" fill="var(--accent)" stroke="var(--surface)" stroke-width="3"/>')
    hero.append(f'<text x="{cx}" y="{HY0 + HS + 44}" text-anchor="middle" font-size="25" font-weight="600" fill="currentColor">{lab}</text>'
                f'<text x="{cx}" y="{HY0 + HS + 100}" text-anchor="middle" font-size="46" font-weight="700" fill="{col}">{_rng(s)}</text>')
out["fig_hero"] = (f'<svg viewBox="0 0 1200 520" role="img" aria-label="Headline image. One skill, shown as a highlighted dot, installed alone and then among 20, 220 and 1,020 skills. '
                   f'How often the agent picked it: {_rng("alone")}, {_rng("pack20")}, {_rng("crowd200")} and {_rng("crowd1000")} of requests, across Claude Code (Haiku, Sonnet) and Codex (GPT-6 Astra).">'
                   f'<g {FONT}><text x="{HX0}" y="56" font-size="30" font-weight="600" fill="currentColor">How often the agent picks the skill <tspan fill="var(--accent)">●</tspan> a request was written for</text>'
                   f'{"".join(hero)}'
                   f'<text x="{HX0}" y="{HY0 + HS + 146}" font-size="21" fill="currentColor" fill-opacity=".65">Range across Claude Code (Haiku, Sonnet) and Codex (GPT-6 Astra), 120 requests each</text>'
                   f'</g></svg>')

# --- Fig: how selection works (skills vs MCP tools)
DASH = ' stroke-dasharray="5 4"'
_box = lambda x, y, w, h, col, dash=False, strong=False: (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" stroke="{col}" fill="{col}" '
                                                         f'fill-opacity="{.14 if strong else .07}" stroke-width="{2 if strong else 1.5}"{DASH if dash else ""}/>')
_t2 = lambda x, y, a, b, anchor="middle": (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="14" font-weight="600">{a}</text>'
                                          f'<text x="{x}" y="{y + 19}" text-anchor="{anchor}" font-size="12" fill-opacity=".72">{b}</text>')
out["fig_how"] = f'''<svg viewBox="0 0 900 250" role="img" aria-label="Diagram. The model gets the request together with the skill listing, which holds every skill's name and description within a capped budget, and the MCP tools, which Claude Code lists by name and loads in full on demand. The model then loads a skill, which is a tool call that returns instructions, calls an MCP tool, or uses only built-in tools such as search, read and shell.">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
{_box(8, 96, 150, 58, "var(--accent)", strong=True)}
{_box(200, 12, 232, 64, "var(--s-sonnet)")}{_box(200, 174, 232, 64, "var(--s-haiku)")}
{_box(476, 96, 118, 58, "currentColor", strong=True)}
{_box(640, 14, 252, 60, "var(--s-sonnet)", strong=True)}{_box(640, 95, 252, 60, "var(--s-haiku)", strong=True)}{_box(640, 176, 252, 60, "var(--band-mid)", dash=True)}
<g {FONT} fill="currentColor">
<text x="83" y="130" text-anchor="middle" font-size="14" font-weight="600">Your request</text>
{_t2(316, 39, "Skill listing", "every name + description, capped")}
{_t2(316, 201, "MCP tools", "names only, details on demand")}
<text x="535" y="122" text-anchor="middle" font-size="14" font-weight="600">Model</text><text x="535" y="140" text-anchor="middle" font-size="12" fill-opacity=".72">decides</text>
{_t2(766, 39, "Load a skill", "a tool call that returns instructions")}
{_t2(766, 120, "Call an MCP tool", "does the job, returns a result")}
{_t2(766, 201, "Neither", "built-in tools: search, read, shell")}
</g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#ah)">
<line x1="158" y1="125" x2="472" y2="125"/>
<path d="M432,52 C460,52 470,70 500,92"/><path d="M432,198 C460,198 470,180 500,158"/>
<line x1="594" y1="110" x2="636" y2="50"/><line x1="594" y1="125" x2="636" y2="125"/><line x1="594" y1="140" x2="636" y2="200"/>
</g>
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
out["fig_setup"] = f'''<svg viewBox="0 0 980 250" role="img" aria-label="Diagram of the experiment. One request, written for one target skill or tool, is sent in four setups: the target alone, the 20 targets together, about 220 installed, and all of them (1,020 skills or 791 tools). Each run goes to Claude Code with Haiku or Sonnet, or to Codex with GPT-6 Astra. The score is the share of requests where the agent picked the target.">
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
<text x="{X0 + 2*(BW+GAP) - GAP/2:.0f}" y="236" text-anchor="middle" font-size="11.5" fill="currentColor" fill-opacity=".75">each run: Claude Code (Haiku, Sonnet) or Codex (GPT-6 Astra)</text>
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
for m, nm in (("sonnet", "Sonnet"), ("haiku", "Haiku"), ("gpt", "GPT-6 Astra")):
    vals = [100 * F(e1[(m, s)]["rate"]) for s in S]
    ci = [(100 * F(e1[(m, s)]["req_boot_lo"]), 100 * F(e1[(m, s)]["req_boot_hi"])) for s in S]
    if m == "gpt": ci[0] = (96.9, 100)
    ser.append(dict(name=f"{nm} ({'Codex' if m=='gpt' else 'Claude Code'})", short=nm, color=COL[nm], values=vals, ci=ci))
out["fig_skills"] = line_chart(ser, ["Target alone", "20 skills", "220 skills", "1,020 skills"],
    "Line chart: share of requests where the designated skill was selected. Sonnet 94, 76, 56, 34 percent; Haiku 78, 48, 25, 16; GPT-6 Astra 100, 99, 83, 10, for the target alone, 20, 220 and 1,020 skills installed.")

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
    f"Line chart for Claude Code. Skills, solid lines: Sonnet 94 to 34 percent, Haiku 78 to 16 percent. Single-step MCP tools, dashed: Sonnet {_tl('sonnet')} percent; Haiku {_tl('haiku')} percent, for the target alone, 20, about 220 and all installed.")

# --- Fig: what happened on misses at 1,020 skills
segs = [("Designated skill", "target"), ("Equivalent alternative", "eq"), ("Other alternative", "alt"), ("No skill detected, finished", "none"), ("No skill detected, hit turn limit", "cap")]
rows = []
for m, nm in (("haiku", "Haiku"), ("sonnet", "Sonnet"), ("gpt", "GPT-6 Astra")):
    r = e1[(m, "crowd1000")]; n = F(r["n"])
    vals = [F(r["target_selected"]), F(r["miss_alt_equivalent"]), F(r["miss_alt_related"]) + F(r["miss_alt_inappropriate"]) + F(r["miss_alt_unassessable"]),
            F(r["miss_no_skill_completed"]), F(r["miss_no_skill_turn_limit"])]
    rows.append((nm, [100 * v / n for v in vals], int(n)))
x0, x1 = 112, 690; bw = x1 - x0; parts = []
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
out["fig_misses"] = f'''<svg viewBox="0 0 740 216" role="img" aria-label="Stacked bars at 1,020 skills. Haiku: 16 percent designated skill, 1 equivalent alternative, 3 other alternative, 37 no skill detected and finished, 44 no skill detected and hit the turn limit. Sonnet: 34, 2, 0, 44, 19. GPT-6 Astra: 10, 10, 14, 66, 0.">
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
NM = {"haiku": "Haiku", "sonnet": "Sonnet", "gpt": "GPT-6 Astra"}
sections = [("Skills: change vs target skill alone", "E1 skills", "skills"), ("Single-step MCP tools: change vs target tool alone", "E2 MCP single-step tools", "tools")]
W = 740; x0, x1 = 250, 600; X = lambda d: x0 + (x1 - x0) * (d + 100) / 110
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
         f"Skills at 20, 220 and 1,020: Haiku {_fl('E1 skills', 'haiku')}; Sonnet {_fl('E1 skills', 'sonnet')}; GPT-6 Astra {_fl('E1 skills', 'gpt')}. "
         f"Single-step MCP tools at 20, 220 and 791: Haiku {_fl('E2 MCP single-step tools', 'haiku')}; Sonnet {_fl('E2 MCP single-step tools', 'sonnet')}; GPT-6 Astra {_fl('E2 MCP single-step tools', 'gpt')} at 20 tools on 24 requests.")
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
out["fig_attn"] = (f'<svg viewBox="0 0 740 {62 + 40*len(toy)}" role="img" aria-label="Toy model, not data. If the target skill gets 20 times the weight of an unrelated skill before normalising, its share of attention is 100 percent alone, 51 percent with 20 skills, 8 percent with 220, 2 percent with 1,020, and 1.5 percent with 1,020 skills of which 16 look-alikes get the same weight as the target. The look-alikes then take 24 percent.">'
                   f'<g {FONT}>{"".join(pa)}</g></svg>')

out["fig_weight"] = open(os.path.join(B, "fig_weight.svg")).read()   # the repo-survey chart, drawn once from weight.json
json.dump(out, open(os.path.join(B, "figs.json"), "w"))
print("figures:", list(out))
