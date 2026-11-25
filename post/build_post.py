"""Assemble the post: skills-mcp-post.html (figures from figs.json; numbers read from analysis/derived and listing/)."""
import json, os, re
B = os.path.dirname(os.path.abspath(__file__))
fig = json.load(open(os.path.join(B, "figs.json")))
t = open(os.path.join(B, "post.tpl.html")).read(); css = t[t.index("<style>") + 7:t.index("</style>")]
css = css.replace("--s-haiku:#f0a050; --s-sonnet:#8aa6ff; --s-gpt:#5fd39a", "--s-haiku:#cf7c2e; --s-sonnet:#6f8be6; --s-gpt:#2fa86f;"
  " --seg-target:#4fc1b9; --on-seg-target:#0d1f1e; --seg-eq:#2c7a75; --on-seg-eq:#e5e8eb; --seg-alt:#6b7681; --on-seg-alt:#ffffff; --seg-none:#3a434b; --on-seg-none:#e5e8eb; --seg-cap:#3a434b; --on-seg-cap:#e5e8eb;"
  " --seq1:#2a5a57; --seq2:#3f938c; --seq3:#7fd3cc; --band-hi:#22a094; --band-mid:#8b949e; --band-lo:#e4664c;"
  " --row-good:rgba(34,160,148,.17); --row-bad:rgba(228,102,76,.17); --row-warn:rgba(240,190,60,.17); --box-bg:rgba(79,193,185,.08)")
css = css.replace("--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;", "--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;"
  " --seg-target:#0f6e6a; --on-seg-target:#ffffff; --seg-eq:#7fbcb7; --on-seg-eq:#0d1f1e; --seg-alt:#8a949e; --on-seg-alt:#ffffff; --seg-none:#d9dee2; --on-seg-none:#1d2126; --seg-cap:#d9dee2; --on-seg-cap:#1d2126;"
  " --seq1:#a9d6d2; --seq2:#4f9e98; --seq3:#0b4f4c; --band-hi:#00897b; --band-mid:#8a949e; --band-lo:#c4432b;"
  " --row-good:rgba(0,137,123,.11); --row-bad:rgba(196,67,43,.10); --row-warn:rgba(235,175,20,.20); --box-bg:rgba(15,110,106,.05);")
assert css.count("--seg-target") == 3, css.count("--seg-target")
css += """
.matrix td{min-width:13rem} .matrix td b{display:block;font-weight:600;margin-top:.35rem} .matrix td b:first-child{margin-top:0}
.note{font:.88rem/1.55 var(--sans);color:var(--muted)}
.callout{border-left:3px solid var(--accent);padding:.2rem 0 .2rem .9rem;font-style:italic}
.tldr{font-style:normal;font-weight:600}
.toc{border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:.7rem 1rem;font:.9rem/1.5 var(--sans)}
.toc summary{cursor:pointer;font-weight:600} .toc ol{margin:.4rem 0 0;padding-left:1.3rem} .toc ol ol{margin:.15rem 0 .25rem;padding-left:1.1rem;font-size:.95em}
.toc li+li{margin-top:.12rem} .toc a{text-decoration:none} .toc a:hover{text-decoration:underline}
h2[id],h3[id]{scroll-margin-top:1rem}
.ci{color:var(--muted);opacity:.72;font-size:.85em;white-space:nowrap}
tr.row-good td{background:var(--row-good)} tr.row-bad td{background:var(--row-bad)} tr.row-warn td{background:var(--row-warn)}
figure.hero{margin:.2rem 0 1.4rem;border:1.5px solid var(--line);border-radius:14px;background:var(--surface);padding:1.1rem 1.3rem .7rem}
details.fold{margin:2rem 0 0} details.fold>summary{cursor:pointer} details.fold>summary>h2{display:inline-block;margin:0;vertical-align:middle}
details.fold[open]>summary{margin-bottom:1rem} details.fold>summary::marker{color:var(--muted)}
figcaption{font-style:italic}
.tcap{font:italic .85rem/1.5 var(--sans);color:var(--muted);margin:1.4rem 0 .45rem}
.capn{font-weight:600}
.repobox{border:2px solid var(--accent);border-radius:8px;background:var(--box-bg);padding:.8rem 1.1rem;margin:1.2rem 0;font:.95rem/1.55 var(--sans)}
.repobox div+div{margin-top:.45rem} .repobox .lbl{font-weight:600} .repobox .soon{color:var(--muted);font-style:italic}
.update{font:.88rem/1.55 var(--sans);color:var(--muted);border-left:3px solid var(--line);padding:.1rem 0 .1rem .8rem}
@media (max-width:760px){td.n .ci{display:block;margin-top:.1rem} td.n,th.n{white-space:normal} th,td{padding:.45rem .5rem}}
.chart-tip{position:fixed;left:0;top:0;z-index:50;pointer-events:none;opacity:0;transition:opacity .12s;max-width:320px;padding:.45rem .65rem;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--fg);font:.82rem/1.45 var(--sans);box-shadow:0 4px 14px rgba(0,0,0,.14)}
.chart-tip .hd{font-weight:600;margin-bottom:.15rem}
.chart-tip .sw{display:inline-block;width:.7em;height:.7em;border-radius:2px;margin-right:.45em;vertical-align:-.05em}
figure svg [data-tip]{transition:opacity .12s}
figure svg.dim [data-tip]:not(.on){opacity:.35}
figure svg:focus-visible{outline:2px solid var(--accent);outline-offset:4px}

.warning{border-left:3px solid var(--warn);padding:.3rem 0 .3rem .9rem}
.dek{font:1.2rem/1.45 var(--serif);color:var(--muted);margin:.3rem 0 .9rem}
.formula{text-align:center;font:1.15rem/1.6 var(--serif);margin:1.1rem 0;overflow-x:auto}
"""
A = lambda url, text: f'<a href="{url}">{text}</a>'
L = {
 "cc_skills": "https://code.claude.com/docs/en/skills.md", "codex_skills": "https://learn.chatgpt.com/docs/build-skills", "spec": "https://agentskills.io/specification",
 "anth_skills": "https://github.com/anthropics/skills", "sickn33": "https://github.com/sickn33/agentic-awesome-skills", "ragmcp": "https://arxiv.org/abs/2505.03275",
 "toolsearch": "https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool", "advtool": "https://anthropic.com/engineering/advanced-tool-use",
 "cursor40": "https://forum.cursor.com/t/tools-limited-to-40-total/67976", "spence": "https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably",
 "seleznov": "https://medium.com/@ivan.seleznov1/why-claude-code-skills-dont-activate-and-how-to-fix-it-86f679409af1", "crosley": "https://blakecrosley.com/blog/skills-my-agent-could-not-see",
 "livemcp": "https://arxiv.org/abs/2508.01780", "livemcp_gh": "https://github.com/icip-cas/LiveMCPBench", "ghmcp": "https://github.com/github/github-mcp-server",
 "cdt": "https://github.com/ChromeDevTools/chrome-devtools-mcp", "pwmcp": "https://github.com/microsoft/playwright-mcp", "trending": "https://github.com/trending?since=monthly",
 "price": "https://developers.openai.com/api/docs/models/gpt-6-astra.md",
 "vaswani": "https://arxiv.org/abs/1706.03762", "lost": "https://arxiv.org/abs/2307.03172", "ruler": "https://arxiv.org/abs/2404.06654",
 "nolima": "https://arxiv.org/abs/2502.05167", "rot": "https://research.trychroma.com/context-rot", "ssmax": "https://arxiv.org/abs/2501.19399",
 "ctxeng": "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "repo": "https://github.com/galinaalperovich/closet-full-of-skills", "r_meth": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/METHODOLOGY.md", "r_listing": "https://github.com/galinaalperovich/closet-full-of-skills/tree/main/listing",
 "r_follow": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/FOLLOWUP_PROTOCOL.md", "r_prompts": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/prompts.json", "r_judge": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/analysis/alt_judge_prompt.md",
 "r_cost": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/analysis/derived/cost_by_batch.csv", "contextbolt": "https://contextbolt.com/blog/too-many-mcp-servers/", "uber": "https://x.com/UberEng/status/2125008806249930999", "skills_mcp": "https://claude.com/resources/articles/skills-over-mcp-tasks-and-more", "davila7": "https://github.com/davila7/claude-code-templates",
 "i81081": "https://github.com/anthropics/claude-code/issues/81081", "i56710": "https://github.com/anthropics/claude-code/issues/56710", "i64606": "https://github.com/anthropics/claude-code/issues/64606",
 "i10768": "https://github.com/anthropics/claude-code/issues/10768", "c19679": "https://github.com/openai/codex/issues/19679", "r_cc": "https://www.reddit.com/r/ClaudeCode/comments/1qo0s2b/",
 "r_hell": "https://www.reddit.com/r/claudeskills/comments/1w2a45r/", "fsck": "https://blog.fsck.com/2025/12/17/claude-code-skills-not-triggering",
 "i6915": "https://github.com/anthropics/claude-code/issues/6915", "i7328": "https://github.com/anthropics/claude-code/issues/7328", "i37793": "https://github.com/anthropics/claude-code/issues/37793",
 "i11364": "https://github.com/anthropics/claude-code/issues/11364", "cur79686": "https://forum.cursor.com/t/mcp-40-tools-way-to-less/79686", "g21823": "https://github.com/google-gemini/gemini-cli/issues/21823",
 "r_mcp1": "https://www.reddit.com/r/mcp/comments/1xnmicj/", "r_mcp2": "https://www.reddit.com/r/mcp/comments/1y0a4a2/",
 "hallmark": "https://github.com/Nutlope/hallmark", "cfsec": "https://github.com/cloudflare/security-audit-skill", "claudeseo": "https://github.com/AgriciDaniel/claude-seo",
 "ffmpeg": "https://github.com/kajisho5/ffmpeg-skill", "igskill": "https://github.com/Jakeschincariol/instagram-agent-skill", "mattpocock": "https://github.com/mattpocock/skills",
 "marketing": "https://github.com/coreyhaines31/marketingskills", "niah": "https://github.com/gkamradt/LLMTest_NeedleInAHaystack", "metatool": "https://arxiv.org/abs/2310.03128", "longfunc": "https://arxiv.org/abs/2505.10570", "wild": "https://arxiv.org/abs/2604.04323", "skillrouter": "https://arxiv.org/abs/2603.22455", "obsidian": "https://github.com/obsidianmd/obsidian-skills",
}
# Numbers are read from the analysis output, not typed in.
import csv
DV = os.path.join(B, "..", "analysis", "derived")
rdv = lambda f: list(csv.DictReader(open(os.path.join(DV, f))))
P = lambda x: f"{100 * float(x):.0f}"                                   # a rate as a whole percent
PP = lambda x: f"{100 * float(x):+.0f}".replace("-", "−").replace("+0", "0")   # a change in points, signed
CI = lambda lo, hi: f'<span class="ci">[{P(lo)}–{P(hi)}]</span>'
CIP = lambda lo, hi: f"{PP(lo)} to {PP(hi)}"
RNG = lambda xs: (lambda v: f"{min(v)}–{max(v)}" if min(v) != max(v) else f"{v[0]}")(sorted(int(P(x)) for x in xs))
RNGP = lambda xs: (lambda v: f"{min(v)}–{max(v)}" if min(v) != max(v) else f"{v[0]}")(sorted(abs(int(round(100 * float(x)))) for x in xs))
E2 = {(r["model"], r["setup"]): r for r in rdv("e2_mcp_rates.csv")}
E2P = {(r["model"], r["from_setup"], r["to_setup"], r["subset"]): r for r in rdv("e2_paired.csv")}
E3 = {(r["model"], r["setup"], r["kind"]): r for r in rdv("e3_mixed_rates.csv")}
E3P = {(r["model"], r["comparison"]): r for r in rdv("e3_paired.csv")}
EC = {(r["model"], r["series"], r["setup"]): r for r in rdv("e3_chart_rates.csv")}
BRW = {(r["model"], r["setup"]): r for r in rdv("raw_browser.csv")}
CM = ("haiku", "sonnet")
def mcp_cell(m, st, all20=False):
    r = E2[(m, st)]
    return (f'{P(r["strict_rate"])}% {CI(r["strict_req_lo"], r["strict_req_hi"])}' if all20
            else f'{P(r["nonbrowser_rate"])}% {CI(r["nonbrowser_req_lo"], r["nonbrowser_req_hi"])}')
NUM = {"fig": 0, "tab": 0}
def fig_(k, cap):
    NUM["fig"] += 1
    return f'<figure>{fig[k]}<figcaption><span class="capn">Figure {NUM["fig"]}.</span> {cap}</figcaption></figure>'
def tab_(cap, table):
    NUM["tab"] += 1
    return f'<p class="tcap"><span class="capn">Table {NUM["tab"]}.</span> {cap}</p>\n{table}'

SK20 = [  # (skill, repo owner/name, what it does, one of its six requests) - from skill-trigger-spike/prompts.json
 ("pdf", "anthropics/skills", "Read, merge, split and edit PDF files", "Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file."),
 ("xlsx", "anthropics/skills", "Create and edit spreadsheets", "Open sales.xlsx and add a column with the month-over-month growth."),
 ("pptx", "anthropics/skills", "Create and edit PowerPoint decks", "Make a 10-slide pitch deck for my coffee subscription startup as a PowerPoint file."),
 ("docx", "anthropics/skills", "Create and edit Word documents", "Write up these meeting notes as a Word document with headings."),
 ("webapp-testing", "anthropics/skills", "Test local web apps with Playwright", "My app is running on localhost:3000. Check that the login form actually works."),
 ("mcp-builder", "anthropics/skills", "Guide to building MCP servers", "I want to build an MCP server that exposes our internal ticketing API to Claude."),
 ("frontend-design", "anthropics/skills", "Distinctive visual design for UI", "Build a landing page for my design studio. I don’t want it to look generic."),
 ("tdd", "mattpocock/skills", "Test-driven development", "Add a discount code feature to the cart, and do it test-first."),
 ("grill-me", "mattpocock/skills", "A relentless interview to sharpen a plan", "Grill me on this plan before I start building."),
 ("diagnosing-bugs", "mattpocock/skills", "Diagnosis loop for hard bugs and slowdowns", "Diagnose why the checkout page throws a 500 only in production."),
 ("obsidian-markdown", "obsidianmd/obsidian-skills", "Obsidian Markdown: wikilinks, callouts, properties", "Write a note for my Obsidian vault about project Atlas with wikilinks to the people involved."),
 ("json-canvas", "obsidianmd/obsidian-skills", "Create and edit .canvas files", "Create a .canvas file mapping out the architecture of this app."),
 ("humanizer", "blader/humanizer", "Rewrite AI-sounding text", "This paragraph sounds like ChatGPT wrote it. Make it sound like a person."),
 ("vercel-react-best-practices", "vercel-labs/agent-skills", "React and Next.js performance guidelines", "Review this Next.js page for performance problems."),
 ("web-design-guidelines", "vercel-labs/agent-skills", "Review UI code against web interface guidelines", "Review my UI code for accessibility problems."),
 ("security-and-hardening", "addyosmani/agent-skills", "Harden code against vulnerabilities", "Audit this login handler for vulnerabilities."),
 ("animate", "emilkowalski/skills", "Build animations that feel right", "Add an animation to this dropdown so it feels right when it opens."),
 ("caveman", "JuliusBrussee/caveman", "Terse caveman voice", "Talk like caveman from now on."),
 ("seo-audit", "coreyhaines31/marketingskills", "Audit and diagnose SEO", "Why did our organic traffic drop last month?"),
 ("copywriting", "coreyhaines31/marketingskills", "Write or rewrite page copy", "Rewrite the copy on our homepage."),
]
SK_TABLE = ('<div class="wrap"><table>\n<tr><th>#</th><th>Skill</th><th>From</th><th>What it does</th><th>One of its six requests</th></tr>\n'
            + "\n".join(f'<tr><td class="n">{i}</td><td><code>{n}</code></td><td><a href="https://github.com/{r}">{r}</a></td><td>{w}</td><td class="req">“{q}”</td></tr>'
                        for i, (n, r, w, q) in enumerate(SK20, 1)) + '\n</table></div>')


# Tables and computed sentences used in the body below
T_EXAMPLES = """<div class="wrap"><table>
<tr><th>Target</th><th>Example requests</th></tr>
<tr><td><code>pdf</code> skill</td><td>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file.”</td></tr>
<tr><td><code>seo-audit</code> skill</td><td>“Why did our organic traffic drop last month?”</td></tr>
<tr><td><code>grill-me</code> skill</td><td>“Grill me on this plan before I start building.”</td></tr>
<tr><td><code>github.create_issue</code> tool</td><td>“Open an issue in acme/webapp saying the login button is broken on Safari.”</td></tr>
</table></div>"""
# Skills table and E1 sentences, read from analysis/derived (request-cluster CI; Wilson where every run succeeded)
E1 = {(r["model"], r["setup"]): r for r in rdv("e1_rates.csv")}
E1P = {(r["model"], r["from_setup"], r["to_setup"]): r for r in rdv("e1_paired.csv")}
def e1_cell(m, s):
    r = E1[(m, s)]
    lo, hi = (r["wilson_lo"], r["wilson_hi"]) if r["target_selected"] == r["n"] else (r["req_boot_lo"], r["req_boot_hi"])
    return f'{P(r["rate"])}% {CI(lo, hi)}'
E1_DROP = lambda m, to: abs(round(100 * float(E1P[(m, "alone", to)]["diff"])))   # paired drop from alone, in points
_e1row = lambda cls, lab, n, s: (f'<tr{cls}><td>{lab}</td><td class="n">{n}</td>' +
                                 "".join(f'<td class="n">{e1_cell(m, s)}</td>' for m in ("haiku", "sonnet", "gpt")) + "</tr>")
T_SKILLS = ('<div class="wrap"><table>\n<tr><th>Setup</th><th class="n">Skills</th><th class="n">Haiku (Claude Code)</th>'
            '<th class="n">Sonnet (Claude Code)</th><th class="n">GPT-6 Astra (Codex)</th></tr>\n' +
            "\n".join([_e1row(' class="row-good"', "Target skill alone", "1", "alone"), _e1row("", "20 skills together", "20", "pack20"),
                       _e1row("", "Plus 200 others", "220", "crowd200"), _e1row(' class="row-bad"', "Plus 1,000 others", "1,020", "crowd1000")]) +
            "\n</table></div>")
T_MCP = f"""<div class="wrap"><table>
<tr><th>Tools installed</th><th class="n">Haiku · 15 single-step</th><th class="n">Sonnet · 15 single-step</th><th class="n">Haiku · all 20</th><th class="n">Sonnet · all 20</th></tr>
<tr class="row-good"><td>Target alone</td><td class="n">{mcp_cell("haiku", "mcp_alone")}</td><td class="n">{mcp_cell("sonnet", "mcp_alone")}</td><td class="n">{mcp_cell("haiku", "mcp_alone", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_alone", True)}</td></tr>
<tr><td>20</td><td class="n">{mcp_cell("haiku", "mcp_pack20")}</td><td class="n">{mcp_cell("sonnet", "mcp_pack20")}</td><td class="n">{mcp_cell("haiku", "mcp_pack20", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_pack20", True)}</td></tr>
<tr><td>~220</td><td class="n">{mcp_cell("haiku", "mcp_crowd200")}</td><td class="n">{mcp_cell("sonnet", "mcp_crowd200")}</td><td class="n">{mcp_cell("haiku", "mcp_crowd200", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_crowd200", True)}</td></tr>
<tr class="row-warn"><td>791</td><td class="n">{mcp_cell("haiku", "mcp_crowdall")}</td><td class="n">{mcp_cell("sonnet", "mcp_crowdall")}</td><td class="n">{mcp_cell("haiku", "mcp_crowdall", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_crowdall", True)}</td></tr>
</table></div>"""
_r = {m: E2P[(m, "mcp_alone", "mcp_crowdall", "nonbrowser15")] for m in CM}
_inc = {m: float(_r[m]["skill_lo"]) < 0 < float(_r[m]["skill_hi"]) for m in CM}
_ci2 = lambda m: f'{m.capitalize()} ({CIP(_r[m]["skill_lo"], _r[m]["skill_hi"])} pp)'
ROBUST_MCP = ("For MCP tools, the two-stage CI from alone to 791 tools excludes zero for both models: " + " and ".join(_ci2(m) for m in CM) + "." if not any(_inc.values())
              else "For MCP tools, the two-stage CI from alone to 791 tools includes zero for " + " and ".join(_ci2(m) for m in CM if _inc[m])
              + ("" if all(_inc.values()) else ", but not for " + " and ".join(_ci2(m) for m in CM if not _inc[m])) + ".")
ROBUST_MCP_SHORT = ("For single-step MCP tools from alone to 791, it excludes zero for both models." if not any(_inc.values()) else
                    "For single-step MCP tools from alone to 791, it includes zero for " + " and ".join(m.capitalize() for m in CM if _inc[m])
                    + ("" if all(_inc.values()) else " but not for " + " and ".join(m.capitalize() for m in CM if not _inc[m])) + ".")
_b = [BRW[(m, st)] for m in CM for st in ("mcp_crowd200", "mcp_crowdall")]
_bl, _bn = sum(int(r["target_definition_loaded"]) for r in _b), sum(int(r["runs"]) for r in _b)
BROWSER_LOADED = (f"In all {_bn} browser runs of the two larger setups, the agent had already loaded the target tool’s definition with <code>ToolSearch</code>." if _bl == _bn
                  else f"In {_bl} of the {_bn} browser runs of the two larger setups, the agent had already loaded the target tool’s definition with <code>ToolSearch</code>.")
_ts = sorted(round(100 * int(E2[(m, st)]["toolsearch"]) / int(E2[(m, st)]["n"])) for m in CM for st in ("mcp_alone", "mcp_pack20", "mcp_crowd200", "mcp_crowdall"))
TOOLSEARCH_SHARE = f"{_ts[0]}–{_ts[-1]}%"

_f = [E2P[(m, "mcp_crowd200", "mcp_crowdall", "nonbrowser15")] for m in CM]
FLAT_CI = max(abs(round(100 * float(r[k]))) for r in _f for k in ("req_lo", "req_hi"))

# What the model saw: the captured skill listings (listing/capture.py, listing/analyze_listing.py)
LD = os.path.join(B, "..", "listing")
LS = {(r["harness"], r["setup"]): r for r in csv.DictReader(open(os.path.join(LD, "summary.csv")))}
LT = list(csv.DictReader(open(os.path.join(LD, "targets.csv"))))
_cx200 = sorted(int(r["desc_chars_shown"]) for r in LT if r["harness"] == "codex" and r["setup"] == "crowd200")
CX200_CHARS = round(_cx200[len(_cx200) // 2], -1)                       # median description length Codex kept at ~220 skills
CC_CAP = round(max(int(LS[("claude", s)]["listing_chars"]) for s in ("crowd200", "crowd1000")), -3)
CX1K = LS[("codex", "crowd1000")]; CX1K_NAMES = CX1K["targets_listed_names"].split()
_gpt = {r["target"]: r for r in rdv("e1_per_target.csv") if r["model"] == "gpt"}
GPT1K_HITS = sum(int(r["crowd1000"].split("/")[0]) for r in _gpt.values())
GPT1K_LISTED_HITS = sum(int(_gpt[t]["crowd1000"].split("/")[0]) for t in CX1K_NAMES)
_n = lambda x: f"{int(x):,}"
SEO_CHARS = next(r["desc_chars_installed"] for r in LT if r["target"] == "seo-audit")
T_SEEN = f"""<div class="wrap"><table>
<thead><tr><th>Setup</th><th>Claude Code</th><th>Codex</th></tr></thead><tbody>
<tr><td>20 skills</td><td><code>seo-audit: When the user wants to audit or diagnose SEO, or asks why traffic dropped…</code> (all {SEO_CHARS} characters)</td><td>the same, in full</td></tr>
<tr class="row-warn"><td>~220 skills</td><td>in full if you have used it; with a clean record, just <code>seo-audit</code></td><td><code>seo-audit: When the user wants to audit or</code></td></tr>
<tr class="row-bad"><td>1,020 skills</td><td><code>seo-audit</code></td><td>not listed at all</td></tr>
</tbody></table></div>"""
T_LISTING = f"""<div class="wrap"><table>
<tr><th>Setup</th><th>Claude Code</th><th>Codex</th></tr>
<tr><td>Alone</td><td>the target, with its full description</td><td>the target, with its full description</td></tr>
<tr><td>20 skills</td><td>all {LS[("claude", "pack20")]["entries"]} entries, full descriptions</td><td>all {LS[("codex", "pack20")]["entries"]} entries, full descriptions</td></tr>
<tr class="row-warn"><td>~220 skills</td><td>{LS[("claude", "crowd200")]["entries"]} names, only {LS[("claude", "crowd200")]["entries_with_description"]} with a description</td><td>all {LS[("codex", "crowd200")]["entries"]}, each description cut to about {CX200_CHARS} characters</td></tr>
<tr class="row-bad"><td>1,020 skills</td><td>{_n(LS[("claude", "crowd1000")]["entries"])} names, only {LS[("claude", "crowd1000")]["entries_with_description"]} with a description</td><td>only {CX1K["entries"]} entries, in alphabetical order, names only: {CX1K["targets_listed"]} of the 20 targets</td></tr>
</table></div>"""
T_TODO = f"""<div class="wrap"><table>
<tr><th>What I observed</th><th>How sure</th><th>What to do</th></tr>
<tr><td>Selection of the designated skill fell as more skills were installed, starting at 20</td><td>Measured; 95% CIs exclude zero from 20 skills on (Claude); one sample of extra skills</td><td>Enable fewer skills per project</td></tr>
<tr><td>Past a few hundred skills, the listing was cut: Codex dropped skills alphabetically, Claude Code kept mostly names</td><td>Captured after the study with the same versions; no model called</td><td>Check what the model can see before rewriting descriptions</td></tr>
<tr><td>Single-step MCP selection in Claude Code held from 220 to 791 tools</td><td>Measured: no change, paired 95% CIs within ±{FLAT_CI} points; search not isolated</td><td>Prefer search over a full listing where you can</td></tr>
</table></div>"""
T_COST = f"""<div class="wrap"><table>
<tr><th>Item</th><th class="n">Runs</th><th class="n">Cost</th></tr>
<tr><td>GPT-6 Astra, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">$119.13</td></tr>
<tr><td>GPT-6 Astra, MCP experiment so far (OpenAI API)</td><td class="n">170</td><td class="n">$52.60</td></tr>
<tr><td><b>Calculated API fees</b></td><td class="n">650</td><td class="n"><b>$171.73</b></td></tr>
<tr><td>Claude Haiku and Sonnet in Claude Code, the runs in these results (my Claude subscription; API list price for reference)</td><td class="n">4,020</td><td class="n">$0 extra ($198.02 list)</td></tr>
<tr><td>Claude Code runs I discarded: the first MCP and mixed runs, a rerun I stopped, and 18 skill runs I repeated (same subscription)</td><td class="n">3,233</td><td class="n">$0 extra ($149.64 list)</td></tr>
</table></div>"""
_sk = [E3P[(m, f"skill: single-skill baseline -> {st}")]["diff"] for m in CM for st in ("mixed_smaller", "mixed_larger")]
_tl = [E3P[(m, f"tool nonbrowser: mcp_alone -> {st}")]["diff"] for m in CM for st in ("mixed_smaller", "mixed_larger")]
SK_LOSS, TOOL_LOSS = RNGP(_sk), RNGP(_tl)
_e3s = [E3[(m, st, "skill")] for m in CM for st in ("mixed_smaller", "mixed_larger")]
_eq = sorted(round(100 * (int(r["acceptable"]) - int(r["strict"])) / int(r["n"])) for r in _e3s)
EQ_GAIN = f"{_eq[0]}–{_eq[-1]}" if _eq[0] != _eq[-1] else f"{_eq[0]}"
_bk, _bn = sum(int(r["miss_builtin_only"]) for r in _e3s), sum(int(r["n"]) - int(r["strict"]) for r in _e3s)
BUILTIN_SHARE, BUILTIN_COUNT = f"{round(100 * _bk / _bn)}%", f"({_bk} of {_bn})"
R3_EXAMPLES = """<li>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file.” → searched the folder twice with <code>Glob</code>, then answered: “I couldn’t find invoice-jan.pdf or invoice-feb.pdf.” No <code>pdf</code> skill. (The folder is empty by design.)</li>"""
body = f"""
<article>
<figure class="hero">{fig["fig_hero"]}</figure>
<div class="tags">AI Agents · Claude Code · Codex · Agent Skills · MCP</div>
<div class="byline">Galina Alperovich · November 2026</div>
<h1>A Closet Full of Skills and Nothing to Wear: The More Skills You Install, the Less Often Your Agent Picks the Right One (MCP Tools Hold Up Better)</h1>
<p class="dek" data-desc="I installed up to 1,000 skills and ~800 MCP tools in Claude Code and Codex. The skill each request was written for went from being picked 78–100% of the time to 10–34%. In Claude Code, single-step MCP tool selection fell much less, from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in CM)}% to {RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in CM)}%, and held steady from ~200 to ~800 tools.">I installed up to 1,000 skills and ~800 MCP tools in Claude Code and Codex, and measured how often the agent still picked the one each request was written for.</p>

<div class="repobox">
<div><span class="lbl">The experiment, data and analysis:</span> {A(L["repo"], "github.com/galinaalperovich/closet-full-of-skills")}. Every request, every result record and every script, so you can reproduce all the numbers for free.</div>
<div><span class="lbl">A skill to check your own agent:</span> <span class="soon">coming soon</span></div>
</div>

<h2>Summary</h2>
<p class="tldr">Installing a skill doesn’t mean your agent will use it. I sent 120 natural requests to Claude Code and Codex, each written for one particular skill, and kept installing more skills around it. What I found:</p>
<ol>
<li><b>Skills fade.</b> With only that skill installed, the agent picked it in 78–100% of runs. With 1,000 other skills next to it, in only 10–34%.</li>
<li><b>Twenty is enough.</b> With just 20 unrelated skills, and nothing cut from the listing, Haiku already fell from {P(E1[("haiku", "alone")]["rate"])}% to {P(E1[("haiku", "pack20")]["rate"])}% and Sonnet from {P(E1[("sonnet", "alone")]["rate"])}% to {P(E1[("sonnet", "pack20")]["rate"])}%.</li>
<li><b>Past a few hundred skills, the harness quietly cuts the listing.</b> Codex listed only {CX1K["entries"]} skills, in alphabetical order, and dropped the rest. Claude Code kept every name but only {LS[("claude", "crowd1000")]["entries_with_description"]} descriptions, and your usage history decides which.</li>
<li><b>Most misses are no skill at all, not a wrong one.</b> The agent carries on with its built-in tools, and nothing tells you.</li>
<li><b>MCP tools held up better.</b> In Claude Code, single-step tool selection went from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in CM)}% with the tool alone to {RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in CM)}% with all 791 tools installed, and stayed flat from ~200 tools on.</li>
</ol>
<p>The experiment has <a href="#limitations-of-the-experiment">its limits</a>, and they limit how far the result generalizes. At the end I share <a href="#what-you-can-do-about-it">a few tricks for dealing with it</a>.</p>
<!--toc-->
<h2>Problem statement</h2>

<p>Agent skills became <b>the new npm</b>. A skill is a folder with a <code>SKILL.md</code> file: a name, a short description, and instructions the agent reads only when it needs them. The biggest community collection I found, {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, has over 3,000 skills, and its README invites you to install all of them. MCP servers went the same way: one GitHub server alone exposes 149 tools.</p>

<p>Here is what made me curious. The agent chooses a skill from its description, and the descriptions in that one collection add up to about 129K tokens. <em>The Great Gatsby</em> is about 72K. No harness sends <b>two Gatsbys</b> with every request: Claude Code and Codex both cap the listing. So what happens to the skills that do not fit, and to the ones that do?</p>

<p>If this sounds like the <b>needle-in-a-haystack test</b>, it is a harder version of it. The {A(L["niah"], "original test")} hides one fact in a long document and asks for it directly. Here the needle is one skill or tool among hundreds, and nobody asks for it: the model has to notice on its own that the request needs it. Benchmarks come close. {A(L["metatool"], "MetaTool")} tests whether a model knows it needs a tool and which one, and {A(L["longfunc"], "LongFuncEval")} and {A(L["wild"], "Liu et al.")} show tool calling and skill use degrading as catalogs grow. What I did differently:</p>
<ul>
<li><b>Real harnesses, not a bare model.</b> Claude Code and Codex as you run them, with their own listing budgets, prompts and tool search. What the harness does before the model sees anything turned out to matter most.</li>
<li><b>Real skills and tools:</b> 20 popular skills and 20 published MCP tools, among up to 1,000 real skills and 791 real tool definitions.</li>
<li><b>Requests that never name the skill</b>, sent unchanged to every setup, so each change compares the same requests.</li>
<li><b>Skills and MCP tools side by side, then mixed.</b></li>
<li><b>What the model actually received:</b> I captured the listing each harness sent, and it explains most of the drop.</li>
</ul>

<h2>Why it matters</h2>
<ul>
<li><b>A skipped skill fails silently.</b> Nothing breaks, and until you read the traces and logs, you won’t know the skill or tool was never picked. The agent answers anyway, and LLMs are very good at answers that look as if the skill was used, while your instructions were never read and your data was never touched. Ask for Apple’s stock price without the finance tool being called, and you may get <b>a confident number from the model’s memory</b>.</li>
<li><b>One skipped skill can skip a whole recipe.</b> A skill often says which tools to call and in which order: run the linter, then the tests, then open the pull request. Skip the skill, and nothing makes sure those steps happen.</li>
<li><b>If you have rules to follow, it gets worse.</b> Some projects must follow a fixed process or use specific data: a legal review, an approved template, the official price list. How do you prove to an auditor that your agent did not improvise? “We installed the skill and hoped for the best” is not an audit trail. We need to measure, and be able to prove, that the agent uses what it is supposed to use.</li>
<li><b>It takes an everyday setup, not an extreme one.</b> {A(L["i81081"], "One Claude Code issue")} reports that 75% of project skills (27 of 36) reached the model with only a name, and {A(L["i11364"], "one user counted")} 67,300 tokens of tool definitions from seven MCP servers before the first message. At company scale, {A(L["uber"], "Uber reports")} more than 5,000 skills in its internal marketplace after one year, about 100 of them switched on for every employee. More reports are in the references.</li>
</ul>

<h2>How an agent picks a skill or a tool</h2>
<p>A <b>skill</b> is a folder of instructions that teaches the agent <em>how</em> to do something. An <b>MCP tool</b> is a function on a server that <em>does</em> one thing, such as creating an issue, and returns a result.</p>
<p><b>Loading a skill is itself a tool call.</b> Claude Code calls its <code>Skill</code> tool; Codex reads the file with a shell command such as <code>cat .agents/skills/pdf/SKILL.md</code>. The call returns the instructions, and the work happens in the calls that follow. That first call is what I count as “selected” (for Codex, a command naming the skill’s <code>SKILL.md</code>; I did not check that the read succeeded).</p>
<p>The two also reach the model differently. Skills sit in one listing of names and descriptions, sent with every request. Claude Code lists MCP tools by name only and fetches a full definition on demand, with a <code>ToolSearch</code> call.</p>
{fig_("fig_how", "How a request reaches a skill or a tool, with MCP tools handled the way Claude Code does it.")}
<p>Between installing a skill and the skill doing its job there are four stages:</p>
<ol>
<li><b>Installed.</b> The skill folder or MCP server is on disk and enabled.</li>
<li><b>Listed.</b> The harness fits names and descriptions into a budget: {A(L["cc_skills"], "1% of the context window in Claude Code, which drops descriptions when it overflows")}, and {A(L["codex_skills"], "2%, at most 10,000 tokens, in Codex, which shortens them first")}. <b>Checked afterwards.</b></li>
<li><b>Selected.</b> The model loads the skill or calls the tool. <b>Measured here.</b></li>
<li><b>Used.</b> The instructions are followed and the task gets done. Not measured.</li>
</ol>

<h2>The experiment setup</h2>
{fig_("fig_setup", "The same request in four setups, from the target alone to 1,000 other skills (or 791 tools).")}
<p>I picked 20 well-known skills ({A(L["anth_skills"], "Anthropic’s")} pdf, xlsx, pptx and docx, {A(L["mattpocock"], "Matt Pocock’s")} tdd and grill-me, and others; full list in <a href="#appendix-a">Appendix A</a>) and 20 everyday MCP tools out of 791 real tool definitions from 73 servers ({A(L["ghmcp"], "GitHub")}, {A(L["cdt"], "Chrome DevTools")}, {A(L["pwmcp"], "Playwright")}, and 70 servers from {A(L["livemcp_gh"], "LiveMCPBench")}).</p>
<p>For each target an LLM wrote six realistic requests with no explicit invocation: no <code>/pdf</code>, no “use the pdf skill”. {A(L["r_prompts"], "All requests are in the repo.")}</p>
{tab_("Example requests. Every target had six like these.", T_EXAMPLES)}
<p>Each request ran in four setups:</p>
<ol>
<li><b>Alone:</b> only the target, plus what the harness ships: 23 built-in skills in Claude Code, and 5 in Codex, such as <code>skill-creator</code>, which I left on.</li>
<li><b>20:</b> all 20 targets together.</li>
<li><b>~220:</b> the 20 plus 200 others, drawn at random.</li>
<li><b>All:</b> the 20 plus 1,000 other skills, or all 771 other tools.</li>
</ol>
<p>Three configurations ran them: Claude Haiku and Claude Sonnet in Claude Code (v2.1.328), and GPT-6 Astra (medium reasoning) in Codex CLI (v0.160.0). Each is a model plus a harness with its own system prompt, listing budget and permissions, so when Codex behaves differently from Claude Code, I can’t tell how much of it is the model and how much the harness.</p>
<p>Four details matter for reading the numbers:</p>
<ol>
<li><b>Fake skill bodies.</b> Each skill keeps its real name and description, which is all the agent sees when it chooses, but its instructions are one line: “reply with one short sentence”. MCP tools likewise have real definitions and a canned reply. This kept thousands of runs cheap and identical: the choice is realistic, and everything after it is not.</li>
<li><b>Fresh, empty folders.</b> Empty, so every setup sees exactly the same thing, though a request about <code>report.pdf</code> then finds no such file (Result 4 shows what agents did about it). Fresh, because Claude Code keeps a memory per folder: in my first pass, runs shared a folder, and notes saved in one run were loaded by the next. In one folder, five runs started with such a note, and all five missed the skill. I reran every affected run, with a little less enthusiasm than the first time.</li>
<li><b>Short observation window.</b> Claude Code was capped at 3 turns (4 with MCP). Picking a skill is the agent’s first decision, almost always made in the first turn or two, and the cap kept thousands of runs fast, at the price of missing later picks. Codex has no turn cap: a run is one user message, within which the model takes as many steps as it wants.</li>
<li><b>Scoring.</b> A skill request is a hit only if the agent picks exactly the skill the request was written for; a tool request also counts an equivalent tool on another server. When the agent picked something else, a separate Claude session later judged from the two descriptions whether it was just as good: a model’s judgment, not a human’s ({A(L["r_judge"], "prompt and rules")}). 13 alternatives in the Claude Code MCP and mixed runs were never judged and count as misses.</li>
</ol>
<p><b>How to read the numbers.</b> Each configuration got 120 skill requests and 90 single-step tool requests. Brackets are 95% confidence intervals from resampling requests, and changes compare the same requests, in percentage points. They do not cover the random draw of extra skills or the request wording; the details are in the {A(L["r_meth"], "methodology")}.</p>

<h2>Result 1: Skills fade</h2>
{tab_("Share of requests where the agent picked the designated skill, with 95% CIs.", T_SKILLS)}
{fig_("fig_skills", "The same numbers as a chart. Sonnet: 360 runs per point; Haiku and GPT-6 Astra: 120. The x axis is not to scale.")}
<p><b>The decline is already there at 20.</b> These are 20 skills about different things: PDFs, SEO, TDD, animation. On the same requests, Haiku fell from {P(E1[("haiku", "alone")]["rate"])}% to {P(E1[("haiku", "pack20")]["rate"])}% and Sonnet from {P(E1[("sonnet", "alone")]["rate"])}% to {P(E1[("sonnet", "pack20")]["rate"])}%, and almost no request got better. I expected trouble at a thousand skills. I did not expect it at twenty, but <b>twenty is enough</b>.</p>

<h3>When the designated skill was not picked, what did the agent do instead?</h3>
<p>A miss can mean three different things:</p>
<ol>
<li>The agent picked another skill, sometimes an equally good one.</li>
<li>It picked no skill and carried on with its built-in tools.</li>
<li>It ran out of turns before choosing anything.</li>
</ol>
{fig_("fig_misses", "Outcomes with 1,020 skills. Hatched: the run hit Claude Code’s 3-turn limit. “No skill detected”: no <code>Skill</code> call in Claude Code; in Codex, no command naming a <code>SKILL.md</code> (reads of Codex’s own skills under <code>skills/.system/</code> are not detected).")}
<p>Most misses were not a wrong skill. They were runs where <b>no skill was detected at all</b>. That changes the debugging question from “why this wrong skill?” to “was a skill exposed and picked at all?”</p>
<ul>
<li><b>Haiku:</b> more than half of its no-skill runs (53 of 97) hit the 3-turn limit, so a longer window might have caught later picks.</li>
<li><b>Sonnet:</b> two thirds of its misses (160 of 239) ended normally, with no skill.</li>
<li><b>GPT-6 Astra:</b> a quarter of its misses (29 of 108) picked a different skill, 12 of them rated equivalent, which would make its rate 20%, not 10%.</li>
</ul>

<h2>Result 2: What the model actually saw</h2>
<p>Was the listing cut, or did the model choose badly from a full one? It turned out to be the most useful question of the whole study, and the cheapest to answer. I re-ran every skills setup against a stand-in server that records what each harness sends to the model: same versions, commands and folders, no model called, no cost ({A(L["r_listing"], "scripts and results")}).</p>
{tab_("What the skill listing contained in each setup. Haiku and Sonnet received the same listing.", T_LISTING)}
{tab_("The same skill, <code>seo-audit</code>, as it reached the model in each setup.", T_SEEN)}
<p><b>At 20 skills, nothing was cut.</b> Both harnesses showed every description in full, so the drop at 20 is the model’s own choice. Everything after that is a different story: the model was choosing from a listing that the harness had already cut.</p>

<h3>Codex: first shorter, then gone</h3>
<p>Codex cuts in two steps. At ~220 skills it keeps every skill but shortens each description to about {CX200_CHARS} characters, and GPT-6 Astra still picked the designated skill in {P(E1[("gpt", "crowd200")]["rate"])}% of requests: a name and five words were nearly enough.</p>
<p>At 1,020 skills it listed only {CX1K["entries"]} entries: its own 4 skills, then the installed ones in alphabetical order up to “developer-listening”, with no descriptions at all. Of the 20 targets, only {", ".join(f"<code>{t}</code>" for t in CX1K_NAMES[:-1])} and <code>{CX1K_NAMES[-1]}</code> made it in, and they account for {GPT1K_LISTED_HITS} of GPT-6 Astra’s {GPT1K_HITS} hits. Every other skill it picked starts early in the alphabet. So <b>GPT-6 Astra’s cliff is the alphabet</b>: the fall from {P(E1[("gpt", "crowd200")]["rate"])}% to {P(E1[("gpt", "crowd1000")]["rate"])}% is mostly not a model choosing badly, because {20 - int(CX1K["targets_listed"])} of the 20 skills were never offered to it. If your skill is called <code>zebra-something</code>, I have bad news.</p>

<h3>Claude Code: every name, few descriptions</h3>
<p>Claude Code never drops a skill; it drops descriptions. Its listing stops growing at about {CC_CAP:,} characters, and that cap is reached already at ~220 skills: {LS[("claude", "crowd200")]["entries"]} names, {LS[("claude", "crowd200")]["entries_with_description"]} with a description. At 1,020 skills, only {LS[("claude", "crowd1000")]["entries_with_description"]} of {_n(LS[("claude", "crowd1000")]["entries"])} entries had one. So in a big collection the model mostly chooses from <b>bare names</b>, which fits the way Haiku and Sonnet decline: no cliff, just less and less to go on.</p>

<h3>Your history decides which descriptions survive</h3>
<p>Which entries keep a description? Claude Code records how often and how recently you used each skill, across all your projects, and the most-used keep theirs. I checked it three ways:</p>
<ol>
<li><b>A clean record, 1,020 skills:</b> {("none" if LS[("claude-fresh", "crowd1000")]["targets_with_description"] == "0" else LS[("claude-fresh", "crowd1000")]["targets_with_description"])} of the 20 targets had a description.</li>
<li><b>A record seeded with uses of <code>seo-audit</code> and <code>pdf</code>:</b> exactly those two got theirs back.</li>
<li><b>A clean record, ~220 skills:</b> {LS[("claude-fresh", "crowd200")]["targets_with_description"]} of the 20 targets kept a description, and they are the {LS[("claude-fresh", "crowd200")]["targets_with_description"]} that come first in the alphabet (<code>animate</code> to <code>humanizer</code>). Without a history, the alphabet seems to decide here too.</li>
</ol>
<p>There is a twist, and this one is on me: my own runs fed that record, so a skill picked in one run was more likely to keep its description in the next. I captured the listings after the study, so I cannot say exactly which targets had a description in each run, only that at 1,020 skills almost none did. <b>A new skill in a big collection starts life as a bare name.</b></p>

<h3>What this means for your skills</h3>
<ul>
<li><b>The name does most of the work.</b> In a big collection the name is often all the model gets, so name a skill with the words people will actually type.</li>
<li><b>A new skill starts at the back of the queue.</b> In Claude Code, the skills you use keep their descriptions, so a new one in a big collection may wait a long time for its first pick. Calling it by name is the obvious way in (I seeded the record by hand and did not test how many uses it takes).</li>
<li><b>In Codex, past about {round(int(CX1K["entries"]), -1)} skills, the end of the alphabet does not exist.</b> The only fix I know is fewer skills.</li>
</ul>

<h3>Which skills kept being selected</h3>
{fig_("fig_dumbbell", "Sonnet: each skill alone (hollow dot) and among 1,020 others (filled dot), 18 runs each, grouped by where it ends up. Each dot rests on 6 requests, so a difference of a few runs is not a ranking.")}
<p>The extremes: <code>grill-me</code> went from 100% to 94%, <code>seo-audit</code> from 100% to <b>0%</b>. Three things seem to separate the groups (observations over 20 skills, not a test):</p>
<ol>
<li><b>Did the description survive?</b> In my capture, <code>grill-me</code> and <code>json-canvas</code>, the two that held best, were two of the three targets that kept a description at 1,020 skills.</li>
<li><b>If not, does the name say it all?</b> <code>xlsx</code>, <code>pptx</code>, <code>docx</code> and <code>mcp-builder</code> held up fairly well as bare names, because the request mentions the file type or an MCP server. <code>humanizer</code> or <code>caveman</code> say little on their own, and <code>seo-audit</code> sat among 16 other bare names with “seo” in them.</li>
<li><b>Could the model do the job without help?</b> The skills that vanished cover things models believe they already do well (rightly or not): write copy, find a bug, review security, audit SEO, design a page. There the agent did not pick a wrong skill; it picked none (15 of <code>seo-audit</code>’s 18 Sonnet runs).</li>
</ol>

<h2>Result 3: MCP tools hold up better</h2>
<p>Then I repeated the design with 20 everyday MCP tools, such as creating a GitHub issue, taking a screenshot or getting a stock price, each served from its real published definition.</p>
<p><b>The tools held up better.</b> With the target tool alone, Claude Code picked it for {P(E2[("haiku", "mcp_alone")]["nonbrowser_rate"])}% (Haiku) and {P(E2[("sonnet", "mcp_alone")]["nonbrowser_rate"])}% (Sonnet) of the single-step requests. With all 791 tools installed, it still did for {P(E2[("haiku", "mcp_crowdall")]["nonbrowser_rate"])}% and {P(E2[("sonnet", "mcp_crowdall")]["nonbrowser_rate"])}%. Skills, remember, fell to 16% and 34%.</p>
{fig_("fig_fade", "Claude Code. Skills (solid) against the 15 single-step MCP tool targets (dashed), with 95% CIs. Different tasks and scoring rules; the x axis is not to scale.")}
<p>Most of the loss came at the first step, from one tool to twenty, where near neighbours appear: four GitHub tools, two browser servers. After that the curve is flat. Adding 571 more tools, from ~220 to 791, changed <b>nothing measurable</b> ({P(E2[("haiku", "mcp_crowd200")]["nonbrowser_rate"])}% → {P(E2[("haiku", "mcp_crowdall")]["nonbrowser_rate"])}% for Haiku, {P(E2[("sonnet", "mcp_crowd200")]["nonbrowser_rate"])}% → {P(E2[("sonnet", "mcp_crowdall")]["nonbrowser_rate"])}% for Sonnet). Not proof of no effect, but a very different picture from the skills.</p>
{tab_("Share of tool requests where Claude Code called the designated tool (or an equivalent one), with 95% CIs. Highlighted: tools still lost ground, only much less than skills.", T_MCP)}
<p class="note">“15 single-step”: the targets that need one call. “All 20” adds the five browser targets below. I made this split after seeing the first results, which is why both are shown.</p>
<p><b>Five tools measured my setup, not the agent.</b> “Take a screenshot of example.com” needs two steps, and in the larger setups the agent opened the page, got my canned reply, and stopped. Perfectly sensible; the flaw was in my design. {BROWSER_LOADED} I keep these five out of the main curve.</p>
<p><b>GPT-6 Astra is only partly measured:</b> 91% with the tool alone, and 100% → 92% on the 24 of 90 requests I ran with 20 tools before my API bill politely suggested a pause. Codex also blocked these MCP calls after the model chose them (see {A("#check-your-own-agent", "below")}), so the choice is measured, but not what came after.</p>

<h2>Result 4: Skills and tools together</h2>
<p>Real setups have both. I built two: a smaller one with 100 skills and 437 tools, and a larger one with 400 skills and all 791 tools, including overlaps such as <code>xlsx</code> next to an Excel server. Then I sent the skill requests (the 20 targets plus five trending skills, 150 in total) and the tool requests.</p>
{fig_("fig_mix", "Claude Code. “Single component”: the target installed alone. Tool requests: the 15 single-step targets. Whiskers: 95% CI.")}
<p><b>The same pattern, only stronger:</b> compared with the component alone, skill requests lost {SK_LOSS} points and single-step tool requests {TOOL_LOSS}. The scoring differs (a tool may be an equivalent one, a skill must be the exact one), but counting equivalent skills adds only about {EQ_GAIN} points.</p>
<p>When the agent skipped the skill, in {BUILTIN_SHARE} of those requests {BUILTIN_COUNT} it <b>only used built-in tools</b>, mostly <code>Glob</code> and <code>Grep</code>: it went looking in the empty folder for the files the request mentioned. “Merge invoice-jan.pdf and invoice-feb.pdf” became two <code>Glob</code> searches and “I couldn’t find the files”, with no <code>pdf</code> skill.</p>

<h2>Why do skills fade while tools hold up?</h2>
{fig_("fig_forest", "Paired change from the target alone, in percentage points, with 95% CIs. Filled dots: skills, 120 requests per row. Hollow dots: single-step MCP tools, 90 per row (GPT-6 Astra at 20 tools: 24 requests).")}
<p>Result 2 explains a large part of it. Three explanations fit what I saw, the first now measured, and each has research behind it:</p>
<ol>
<li><b>Skills lose their descriptions; tools can be searched.</b> A skill listing is like <b>a restaurant menu printed on one page</b>: the more dishes, the smaller the print, and past a point the descriptions get dropped, which is exactly what I captured. Claude Code’s MCP tools are also listed by name only, but that is more like asking the waiter: the model searches and gets the full definition back (it called <code>ToolSearch</code> in {TOOLSEARCH_SHARE} of the MCP runs). A skill that is only a name has no waiter. Research agrees. {A(L["longfunc"], "LongFuncEval")} saw function-calling accuracy fall by 7–85% as the tool catalog grew, and retrieving a few tools instead of listing them all raised selection from 13.6% to 43.1% in {A(L["ragmcp"], "RAG-MCP")} and from 49% to 74% in {A(L["advtool"], "an internal Anthropic evaluation")}.</li>
<li><b>Tools match the words of a request; skills match its meaning.</b> A tool name is a verb the request nearly repeats (<code>create_issue</code>), while a skill describes a whole workflow in broad words its neighbours share. Without shared words, accuracy drops: in {A(L["nolima"], "NoLiMa")}, one of the stronger models fell from 99.3% to 69.7% at 32K tokens, and Chroma’s {A(L["rot"], "Context Rot")} found on-topic distractors hurt most.</li>
<li><b>An action needs a tool; a goal does not.</b> “Open an issue in acme/webapp” cannot be done without the GitHub tool. “Rewrite the copy on our homepage” can, so the model may decide it needs no help. {A(L["metatool"], "MetaTool")} found that most models struggle to decide whether they need a tool at all, and most of my skill misses had no skill rather than a wrong one.</li>
</ol>
<p>The first is measured; treat the other two as hypotheses. The cited studies use other tasks and models, and my two experiments differ in tasks and scoring. A toy calculation of the dilution idea is in <a href="#appendix-c">Appendix C</a>.</p>

<h2>What you can do about it</h2>
{tab_("What I observed, how sure I am, and what to do about it.", T_TODO)}
<h3>[Trick #1] Check what is actually exposed</h3>
<p>In Claude Code, <code>/context</code> shows the size of your skill listing and {A(L["cc_skills"], "<code>/doctor</code> tells you whether descriptions are being dropped")}. Codex prints a warning when it goes over its budget ({A(L["c19679"], "codex#19679")}). And remember that Claude Code favours the skills you have used before, so a new skill in a big collection may reach the model as a bare name. Since November 2026, {A(L["skills_mcp"], "MCP servers can ship skills too")}, with nothing for you to install, so your listing can grow without you noticing (I have not tested how those are listed). This is the first thing I would check.</p>
<h3>[Trick #2] Enable less, per project</h3>
<p>This is the one thing I tested: with fewer skills installed, the designated one was picked more often (answer quality not measured). Enable plugins per project, turn off unused skills with <code>/skills</code>, and if you only need <code>pdf</code> from a 3,000-skill collection, install <code>pdf</code>.</p>
<h3 id="trick-search">[Trick #3] Try other ways to discover and invoke (untested here)</h3>
<ul>
<li><b>Invoke required skills by name</b> (<code>/skill-name</code>) instead of hoping for a match.</li>
<li><b>Give a skill a trigger nobody else has.</b> In my sample, skills with concrete nouns and file types held up.</li>
<li><b>Use a router skill or a hook.</b> {A(L["spence"], "A hook that makes Claude evaluate skills before answering")} reached 84% activation in Scott Spence’s test, against 20% for a keyword hook. {A(L["uber"], "Uber")} keeps about 100 skills on by default and uses a <code>find-skills</code> skill to search the other 5,000.</li>
<li><b>Search instead of listing.</b> Claude Code already defers MCP tools behind {A(L["toolsearch"], "tool search")}. In your own agent, use the Claude API’s tool search tool, or embed the descriptions and retrieve the closest few.</li>
</ul>

<h2>Check your own agent</h2>
<p>The easy way is on its way: I am packaging this whole check as a skill you can run on your own setup (<span class="soon">coming soon</span>). Yes, a skill that checks whether your skills get picked. I see the irony too.</p>
<p>Until then, the manual version: go to a real project folder and send a few requests the way you would really ask.</p>
<pre><code># Claude Code: prints the skill or MCP tool it selected
claude -p "Audit the SEO of my site." --output-format stream-json --verbose --max-turns 3 \\
  | jq -r 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use") | select(.name=="Skill" or (.name|startswith("mcp__")))
           | if .name=="Skill" then "skill: " + .input.skill else "tool: " + .name end'

# Codex: prints the SKILL.md paths named in its commands (a match does not prove
# the read succeeded, and Codex's own skills under skills/.system are not matched)
codex exec --json -s read-only "Audit the SEO of my site." \\
  | grep -o 'skills/[a-z0-9-]*/SKILL.md' | sort -u</code></pre>
<p>Then repeat with only that skill enabled. A handful of requests won’t give you a reliable rate, but it shows whether the skill is ever picked.</p>
<p>Three things I learned the hard way (the first two forced me to rerun part of this study):</p>
<ul>
<li><b>In <code>-p</code> mode, Claude Code refuses MCP calls you have not allowed</b>, since nobody is there to approve them. The selection still prints, but what follows is a reaction to the refusal. Add <code>--allowedTools mcp__&lt;server&gt;</code>.</li>
<li><b>Claude Code keeps a memory per folder.</b> A note saved in one test run is loaded in the next. Use a fresh folder for every run.</li>
<li><b>Codex has both problems in its own flavour.</b> It blocks MCP calls on servers you have not approved (<code>-c 'mcp_servers.&lt;name&gt;.default_tools_approval_mode="approve"'</code>), and it ships 5 skills of its own (<code>-c skills.bundled.enabled=false</code> to test a skill truly alone).</li>
</ul>

<h2>Limitations of the experiment</h2>
<p>This is one person’s experiment, not a benchmark, and I would rather list the weak spots myself than have you find them:</p>
<ul>
<li><b>Selection, not quality.</b> A run without the skill can still produce a fine answer.</li>
<li><b>Listing captured afterwards.</b> I captured what the model saw after the study, with the same versions and folders. For Claude Code it depends on a usage record that my own runs kept updating, so the exact listing of each run is unknown.</li>
<li><b>Few samples.</b> One random draw of extra skills and six LLM-written requests per target.</li>
<li><b>Configurations, not models.</b> Claude Code and Codex differ in model, prompts, budgets and permissions; Codex could search the web in these runs, and Claude Code could not.</li>
<li><b>Thinner GPT-6 Astra data.</b> One run per request, and MCP only alone and, partly, with 20 tools. Codex does not report an MCP server that failed to start, so a tool miss could be a server that never connected.</li>
</ul>
<p>The {A(L["r_meth"], "full methodology")}, all data and all scripts are in {A(L["repo"], "the GitHub repo")}.</p>

<h2>What’s next</h2>
<p>What I would check next:</p>
<ol>
<li><b>Validation.</b> Put real files in the folders, give Claude 10 turns instead of 3, and fix Claude Code’s usage record so every run sees the same listing.</li>
<li><b>Search for skills.</b> Does a <code>ToolSearch</code>-style step help skills the way it seems to help tools? Keep the visible listing constant, vary only the look-alikes, with search on and off.</li>
<li><b>More catalogs and controls.</b> Other draws of extra skills, control requests, other harnesses (Cursor, Gemini CLI), and the quality of the final answer.</li>
</ol>
<p>The full plan with costs is in {A(L["r_follow"], "the follow-up protocol")}. {A(L["repo"], "The repo")} is open, and reruns on newer versions, other models or other harnesses are very welcome. The skill for checking your own setup is coming soon.</p>

<h2>Conclusion</h2>
<p>I started with a simple question: if I install a thousand skills, does my agent get more capable? Mostly, it gets a bigger closet. What changed my view is the gap between installing a capability and having it reliably picked when a request needs it. Before adding another big collection, I would check what the agent can actually see, and I would measure answer quality separately before deciding that more activation is always better.</p>
<p>Thanks for reading! If you run the check on your own setup, tell me what you got. And if you spot a mistake, tell me too: I have already redone half of this study once, I can take it.</p>

<details class="fold"><summary><h2 id="appendix-a">Appendix A: The 20 target skills</h2></summary>
{tab_("The 20 target skills, where they come from, and one of their six requests.", SK_TABLE)}
</details>

<details class="fold"><summary><h2 id="appendix-b">Appendix B: A survey of 42 popular skill repos</h2></summary>
<p>Before the experiment I cloned 42 popular skill repositories, found through GitHub topic searches plus seven repos {A(L["trending"], "trending this month")}, and checked them with a static script: frontmatter, names, file links, bundled scripts and size. No code was run. They contain 14,418 <code>SKILL.md</code> files with 7,848 distinct contents; counting each skill name once per repo gives 6,908 skills.</p>
<ul>
<li><b>Few bundled tests.</b> Test or eval files for 2.6% of skills (177 of 6,908), and none at all in 64% of the repos (27 of 42). Tests can live elsewhere: {A(L["marketing"], "coreyhaines31/marketingskills")} ships evals for all 53 of its skills.</li>
<li><b>Many repeated files.</b> 46% of the files (6,570 of 14,418) repeat another file’s content, mostly the same skill shipped once per packaging format. Structural problems (broken links, missing scripts, invalid names) were rare: 0–3% of skills each.</li>
<li><b>Shared names.</b> 831 skill names appear in two or more repos. For 32% of them (270 of 831), at least two repos carry nearly identical descriptions, for example 18 of Anthropic’s 20 skills inside {A(L["davila7"], "davila7/claude-code-templates")}. A shared name is not always the same skill: <code>seo-audit</code> exists in five repos with five different descriptions.</li>
<li><b>Size.</b> Installed whole, 38% of the repos (16 of 42) have more description text than Claude Code’s listing budget for a 200K window (about 8,000 characters). The largest is roughly 60 times over, and even Anthropic’s own 20 skills are slightly over, at about 9,700 characters.</li>
</ul>
{fig_("fig_weight", "Estimated size of the skill descriptions if you install each collection whole. The red line is roughly Claude Code’s listing budget for a 200K window.")}
<p><b>Overlapping collections.</b> Whether two copies of a skill are both exposed depends on how you install them. {A(L["cc_skills"], "Claude Code namespaces plugin skills")} as <code>/plugin-name:skill-name</code>, so both load. {A(L["codex_skills"], "Codex’s documentation")} says same-name skills are not merged. Copying folders by hand into one skills folder keeps one copy. I deduplicated names in my setups, so the experiment did not measure duplicates.</p>
</details>

<details class="fold"><summary><h2 id="appendix-c">Appendix C: A toy calculation about dilution</h2></summary>
<p>This is illustrative arithmetic, not a model of these agents, and nothing in my data measures attention. It only shows why “more entries can dilute a match” is a reasonable thing to test.</p>
<p>In a {A(L["vaswani"], "transformer")}, each attention head turns scores into weights with a softmax, and within one head the weights add up to 1:</p>
<p class="formula"><i>a<sub>i</sub></i> = e<sup><i>s<sub>i</sub></i></sup> / Σ<sub><i>j</i></sub> e<sup><i>s<sub>j</sub></i></sup></p>
<p>Now a cartoon with several assumptions: each skill description is one block, the target’s weight before normalising (e<sup><i>s</i></sup>) is 20 times that of every unrelated skill, which means a score higher by ln 20 ≈ 3, look-alikes get the same weight as the target, scores do not change when entries are added, and nothing else is in the context. Then the target’s share is 20 / (20 + <i>n</i>) for <i>n</i> unrelated skills, and 20 / (20 + 20<i>k</i> + <i>n</i>) if <i>k</i> of them are look-alikes:</p>
{fig_("fig_attn", "Toy arithmetic under the assumptions in the text. Real models have many heads and layers, scores change with the input, and an attention weight is not a probability of selecting a skill.")}
<p>Nakanishi’s {A(L["ssmax"], "Scalable-Softmax")} paper describes a related effect, attention weights flattening as inputs grow, and proposes a fix. That is background research, not evidence about my runs.</p>
</details>

<details class="fold"><summary><h2 id="appendix-d">Appendix D: What this cost</h2></summary>
{tab_("What the runs cost.", T_COST)}
<p>The GPT-6 Astra figures are calculated from the token usage Codex reported, at {A(L["price"], "OpenAI’s list prices")}, and not reconciled against the invoice ({A(L["r_cost"], "per-batch breakdown")}). Running every remaining GPT-6 Astra cell would cost about $1,400 by my estimate, assuming Codex loads every tool definition; {A(L["contextbolt"], "another measured post")} reports that it defers MCP tools, so that may be too high.</p>
</details>

<details class="fold"><summary><h2 id="references">References</h2></summary>
<ol class="refs">
<li>Code, data and methodology for this post: {A(L["repo"], "galinaalperovich/closet-full-of-skills")}</li>
<li>{A(L["cc_skills"], "Claude Code documentation: Skills")}</li>
<li>{A(L["codex_skills"], "Codex documentation: Build skills")}</li>
<li>{A(L["spec"], "Agent Skills specification")}</li>
<li>{A(L["anth_skills"], "anthropics/skills")} · {A(L["sickn33"], "sickn33/agentic-awesome-skills")} · {A(L["mattpocock"], "mattpocock/skills")} · {A(L["obsidian"], "obsidianmd/obsidian-skills")} · {A(L["marketing"], "coreyhaines31/marketingskills")} · {A(L["davila7"], "davila7/claude-code-templates")}</li>
<li>Trending skills used in Result 4: {A(L["hallmark"], "Nutlope/hallmark")} · {A(L["cfsec"], "cloudflare/security-audit-skill")} · {A(L["claudeseo"], "AgriciDaniel/claude-seo")} · {A(L["ffmpeg"], "kajisho5/ffmpeg-skill")} · {A(L["igskill"], "Jakeschincariol/instagram-agent-skill")}</li>
<li>MCP sources: {A(L["ghmcp"], "github/github-mcp-server")} · {A(L["cdt"], "ChromeDevTools/chrome-devtools-mcp")} · {A(L["pwmcp"], "microsoft/playwright-mcp")} · {A(L["livemcp_gh"], "LiveMCPBench")} ({A(L["livemcp"], "paper")})</li>
<li>Kamradt. {A(L["niah"], "Needle in a Haystack: pressure testing LLMs")} (2023)</li>
<li>Huang et al. {A(L["metatool"], "MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use")} (ICLR 2024)</li>
<li>Kate et al. {A(L["longfunc"], "LongFuncEval: Measuring the effectiveness of long context models for function calling")} (2025)</li>
<li>Liu et al. {A(L["wild"], "How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings")} (2026)</li>
<li>Gan &amp; Sun. {A(L["ragmcp"], "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation")} (2025)</li>
<li>Anthropic: {A(L["toolsearch"], "Tool search tool")} · {A(L["advtool"], "Advanced tool use")}</li>
<li>Reports about skills: {A(L["i81081"], "claude-code#81081")} · {A(L["i56710"], "#56710")} · {A(L["i64606"], "#64606")} · {A(L["i10768"], "#10768")} · {A(L["c19679"], "codex#19679")} · {A(L["r_cc"], "r/ClaudeCode")} · {A(L["r_hell"], "r/claudeskills")} · {A(L["fsck"], "Jesse Vincent")}</li>
<li>Reports about MCP tools: {A(L["i6915"], "claude-code#6915")} · {A(L["i7328"], "#7328")} · {A(L["i37793"], "#37793")} · {A(L["i11364"], "#11364")} · {A(L["cursor40"], "Cursor forum 1")} · {A(L["cur79686"], "Cursor forum 2")} · {A(L["g21823"], "gemini-cli#21823")} · {A(L["r_mcp1"], "r/mcp 1")} · {A(L["r_mcp2"], "r/mcp 2")}</li>
<li>{A(L["spence"], "Scott Spence: How to make Claude Code skills activate reliably")} · {A(L["seleznov"], "Ivan Seleznov: 650 trials")} · {A(L["crosley"], "Blake Crosley: The skills my agent could not see")}</li>
<li>{A(L["contextbolt"], "ContextBolt: Too Many MCP Servers? What Each One Costs, Measured")}</li>
<li>{A(L["uber"], "Uber Engineering: How Uber Evals 1 Million Agent Skill Invocations a Month")} (2026)</li>
<li>{A(L["skills_mcp"], "Claude: MCP servers can now ship skills, run tasks, and more")} (2026)</li>
<li>{A(L["price"], "OpenAI: gpt-6-astra model page and pricing")}</li>
<li>Modarressi et al. {A(L["nolima"], "NoLiMa: Long-Context Evaluation Beyond Literal Matching")} (ICML 2025)</li>
<li>Hong, Troynikov &amp; Huber. {A(L["rot"], "Context Rot: How Increasing Input Tokens Impacts LLM Performance")} (Chroma, 2025)</li>
<li>Vaswani et al. {A(L["vaswani"], "Attention Is All You Need")} (2017)</li>
<li>Nakanishi. {A(L["ssmax"], "Scalable-Softmax Is Superior for Attention")} (2025)</li>
</ol>
</details>
</article>
"""
CHART_JS = """<script>
/* Interactive charts: the values shown are the ones already in each chart's <title> elements. */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const tip = document.createElement('div'); tip.className = 'chart-tip'; tip.setAttribute('aria-hidden', 'true'); document.body.appendChild(tip);
  const esc = t => t.replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const place = (x, y) => { const r = tip.getBoundingClientRect(); let L = x + 14, T = y + 14;
    if (L + r.width > innerWidth - 8) L = x - r.width - 14; if (T + r.height > innerHeight - 8) T = y - r.height - 14;
    tip.style.transform = `translate(${Math.max(8, L)}px, ${Math.max(8, T)}px)`; };
  const show = (html, x, y) => { tip.innerHTML = html; tip.style.opacity = 1; place(x, y); };
  const hide = () => { tip.style.opacity = 0; };
  document.querySelectorAll('figure svg').forEach(svg => {
    const marks = [...svg.querySelectorAll('title')].map(t => { const el = t.parentElement; el.dataset.tip = t.textContent; t.remove(); return el; });
    if (!marks.length) return;
    const circles = marks.filter(m => m.tagName === 'circle');
    if (svg.querySelector('polyline') && circles.length === marks.length) {
      // Line chart: a crosshair snaps to the nearest x position and lists every series there.
      const host = circles[0].parentNode, groups = new Map();
      circles.forEach(c => { const x = +c.getAttribute('cx'); if (!groups.has(x)) groups.set(x, []); groups.get(x).push(c); });
      const xs = [...groups.keys()].sort((a, b) => a - b);
      const ys = circles.map(c => +c.getAttribute('cy'));
      const cross = document.createElementNS(NS, 'line');
      cross.setAttribute('y1', Math.min(...ys) - 20); cross.setAttribute('y2', Math.max(...ys) + 20);
      Object.entries({stroke: 'currentColor', 'stroke-opacity': '.35', 'stroke-dasharray': '3 3'}).forEach(([k, v]) => cross.setAttribute(k, v));
      cross.style.display = 'none'; cross.style.pointerEvents = 'none'; host.insertBefore(cross, host.firstChild);
      let idx = -1;
      const render = (i, cx, cy) => {
        idx = i; const x = xs[i], pts = groups.get(x).slice().sort((a, b) => a.getAttribute('cy') - b.getAttribute('cy'));
        circles.forEach(c => c.setAttribute('r', 5)); pts.forEach(c => c.setAttribute('r', 7));
        cross.setAttribute('x1', x); cross.setAttribute('x2', x); cross.style.display = '';
        const head = pts[0].dataset.tip.split(': ')[0].split(', ').slice(-1)[0];
        const rows = pts.map(c => { const [lhs, val] = c.dataset.tip.split(': '); const name = lhs.split(', ').slice(0, -1).join(', ');
          return `<div><span class="sw" style="background:${c.getAttribute('stroke')}"></span>${esc(name)}: <b>${esc(val)}</b></div>`; }).join('');
        show(`<div class="hd">${esc(head)}</div>${rows}`, cx, cy);
      };
      const nearest = e => { const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
        const p = pt.matrixTransform(host.getScreenCTM().inverse()); let best = 0;
        xs.forEach((x, i) => { if (Math.abs(x - p.x) < Math.abs(xs[best] - p.x)) best = i; }); return best; };
      svg.addEventListener('pointermove', e => render(nearest(e), e.clientX, e.clientY));
      svg.addEventListener('pointerdown', e => render(nearest(e), e.clientX, e.clientY));
      const reset = () => { hide(); cross.style.display = 'none'; circles.forEach(c => c.setAttribute('r', 5)); };
      svg.addEventListener('pointerleave', reset);
      svg.setAttribute('tabindex', '0');
      svg.addEventListener('keydown', e => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return; e.preventDefault();
        const i = Math.min(xs.length - 1, Math.max(0, idx + (e.key === 'ArrowRight' ? 1 : -1)));
        const r = svg.getBoundingClientRect(); render(i, r.left + r.width / 2, r.top + 20); });
      svg.addEventListener('blur', reset);
    } else {
      // Bars, segments, dots: a tooltip on the hovered mark, others fade. Small dots get a larger invisible target.
      marks.forEach(m => {
        let target = m;
        if (m.tagName === 'circle') { target = document.createElementNS(NS, 'circle');
          ['cx', 'cy'].forEach(a => target.setAttribute(a, m.getAttribute(a))); target.setAttribute('r', 12); target.setAttribute('fill', 'transparent');
          m.after(target); }
        const on = e => { svg.classList.add('dim'); m.classList.add('on'); show(esc(m.dataset.tip), e.clientX, e.clientY); };
        target.addEventListener('pointerenter', on); target.addEventListener('pointerdown', on);
        target.addEventListener('pointermove', e => place(e.clientX, e.clientY));
        target.addEventListener('pointerleave', () => { svg.classList.remove('dim'); m.classList.remove('on'); hide(); });
      });
    }
  });
  document.addEventListener('pointerdown', e => { if (!e.target.closest('figure svg')) hide(); });
  // folded appendices: open the section a link points into
  const openFor = h => { if (!h || h.length < 2) return; const el = document.getElementById(decodeURIComponent(h.slice(1))); const d = el && el.closest('details.fold'); if (d) d.open = true; };
  document.addEventListener('click', e => { const a = e.target.closest('a[href^="#"]'); if (a) openFor(a.getAttribute('href')); });
  addEventListener('hashchange', () => openFor(location.hash)); openFor(location.hash);
  addEventListener('scroll', hide, {passive: true});
})();
</script>"""

import html as _html
def add_toc(body):
    used, items = set(re.findall(r'id="([^"]+)"', body)), []
    def slug(t):
        b = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60] or "section"; s_, k = b, 2
        while s_ in used: s_, k = f"{b}-{k}", k + 1
        used.add(s_); return s_
    def fix(m):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        text = _html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        hid = re.search(r'id="([^"]+)"', attrs)
        hid = hid.group(1) if hid else slug(text)
        items.append((tag, hid, text))
        return f'<{tag} id="{hid}">{inner}</{tag}>' if 'id="' not in attrs else m.group(0)
    body = re.sub(r"<(h[23])((?:\s+[^>]*)?)>(.*?)</\1>", fix, body, flags=re.S)
    out, open_sub = ['<nav class="toc" aria-label="Contents"><details open><summary>Contents</summary><ol>'], False
    for tag, hid, text in items:
        a = f'<a href="#{hid}">{_html.escape(text)}</a>'
        if tag == "h2":
            if open_sub: out.append("</ol></li>"); open_sub = False
            elif len(out) > 1: out.append("</li>")
            out.append(f"<li>{a}")
        else:
            if not open_sub: out.append("<ol>"); open_sub = True
            out.append(f"<li>{a}</li>")
    out.append("</ol></li>" if open_sub else "</li>"); out.append("</ol></details></nav>")
    return body.replace("<!--toc-->", "".join(out), 1)
body = add_toc(body)

html = f'<title>A Closet Full of Skills</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">\n<style>{css}</style>\n{body}\n{CHART_JS}'
open(os.path.join(B, "skills-mcp-post.html"), "w").write(html)
print("ok", len(html))
