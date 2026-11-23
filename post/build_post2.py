"""Assemble the post: skills-mcp-post.html (figures from figs2.json; MCP and mixed numbers read from analysis/derived/v3)."""
import json, os, re
B = os.path.dirname(os.path.abspath(__file__))
fig = json.load(open(os.path.join(B, "figs2.json")))
t = open(os.path.join(B, "post.tpl.html")).read(); css = t[t.index("<style>") + 7:t.index("</style>")]
css = css.replace("--s-haiku:#f0a050; --s-sonnet:#8aa6ff; --s-gpt:#5fd39a", "--s-haiku:#cf7c2e; --s-sonnet:#6f8be6; --s-gpt:#2fa86f;"
  " --seg-target:#4fc1b9; --on-seg-target:#0d1f1e; --seg-eq:#2c7a75; --on-seg-eq:#e5e8eb; --seg-alt:#6b7681; --on-seg-alt:#ffffff; --seg-none:#3a434b; --on-seg-none:#e5e8eb; --seg-cap:#3a434b; --on-seg-cap:#e5e8eb;"
  " --seq1:#2a5a57; --seq2:#3f938c; --seq3:#7fd3cc; --band-hi:#22a094; --band-mid:#8b949e; --band-lo:#e4664c;"
  " --row-good:rgba(34,160,148,.17); --row-bad:rgba(228,102,76,.17); --box-bg:rgba(79,193,185,.08)")
css = css.replace("--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;", "--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;"
  " --seg-target:#0f6e6a; --on-seg-target:#ffffff; --seg-eq:#7fbcb7; --on-seg-eq:#0d1f1e; --seg-alt:#8a949e; --on-seg-alt:#ffffff; --seg-none:#d9dee2; --on-seg-none:#1d2126; --seg-cap:#d9dee2; --on-seg-cap:#1d2126;"
  " --seq1:#a9d6d2; --seq2:#4f9e98; --seq3:#0b4f4c; --band-hi:#00897b; --band-mid:#8a949e; --band-lo:#c4432b;"
  " --row-good:rgba(0,137,123,.11); --row-bad:rgba(196,67,43,.10); --box-bg:rgba(15,110,106,.05);")
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
tr.row-good td{background:var(--row-good)} tr.row-bad td{background:var(--row-bad)}
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
 "ctxeng": "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "repo": "https://github.com/galinaalperovich/closet-full-of-skills", "r_meth": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/METHODOLOGY.md", "r_chg": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/analysis/CHANGELOG.md", "r_rev": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/METHODOLOGY_REVIEW.md",
 "r_follow": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/FOLLOWUP_PROTOCOL.md", "r_prompts": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/prompts.json", "r_judge": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/analysis/alt_judge_prompt.md",
 "r_cost": "https://github.com/galinaalperovich/closet-full-of-skills/blob/main/analysis/derived/v2/cost_by_batch.csv", "contextbolt": "https://contextbolt.com/blog/too-many-mcp-servers/", "davila7": "https://github.com/davila7/claude-code-templates",
 "i81081": "https://github.com/anthropics/claude-code/issues/81081", "i56710": "https://github.com/anthropics/claude-code/issues/56710", "i64606": "https://github.com/anthropics/claude-code/issues/64606",
 "i10768": "https://github.com/anthropics/claude-code/issues/10768", "c19679": "https://github.com/openai/codex/issues/19679", "r_cc": "https://www.reddit.com/r/ClaudeCode/comments/1qo0s2b/",
 "r_hell": "https://www.reddit.com/r/claudeskills/comments/1w2a45r/", "fsck": "https://blog.fsck.com/2025/12/17/claude-code-skills-not-triggering",
 "i6915": "https://github.com/anthropics/claude-code/issues/6915", "i7328": "https://github.com/anthropics/claude-code/issues/7328", "i37793": "https://github.com/anthropics/claude-code/issues/37793",
 "i11364": "https://github.com/anthropics/claude-code/issues/11364", "cur79686": "https://forum.cursor.com/t/mcp-40-tools-way-to-less/79686", "g21823": "https://github.com/google-gemini/gemini-cli/issues/21823",
 "r_mcp1": "https://www.reddit.com/r/mcp/comments/1xnmicj/", "r_mcp2": "https://www.reddit.com/r/mcp/comments/1y0a4a2/",
 "hallmark": "https://github.com/Nutlope/hallmark", "cfsec": "https://github.com/cloudflare/security-audit-skill", "claudeseo": "https://github.com/AgriciDaniel/claude-seo",
 "ffmpeg": "https://github.com/kajisho5/ffmpeg-skill", "igskill": "https://github.com/Jakeschincariol/instagram-agent-skill", "mattpocock": "https://github.com/mattpocock/skills",
 "marketing": "https://github.com/coreyhaines31/marketingskills", "obsidian": "https://github.com/obsidianmd/obsidian-skills",
}
# Numbers for the MCP and mixed experiments are read from the analysis output (analysis version 3), not typed in.
import csv
DV = next(d for d in (os.path.join(B, "..", "analysis", "derived", "v3"), os.path.join(B, "..", "skill-trigger-spike", "analysis", "derived", "v3")) if os.path.isdir(d))
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
# Skills table and E1 sentences, read from analysis/derived/v3 (request-cluster CI; Wilson where every run succeeded)
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
            '<th class="n">Sonnet (Claude Code)</th><th class="n">GPT (Codex)</th></tr>\n' +
            "\n".join([_e1row(' class="row-good"', "Target skill alone", "1", "alone"), _e1row("", "20 skills together", "20", "pack20"),
                       _e1row("", "Plus 200 others", "220", "crowd200"), _e1row(' class="row-bad"', "Plus 1,000 others", "1,020", "crowd1000")]) +
            "\n</table></div>")
T_MCP = f"""<div class="wrap"><table>
<tr><th>Tools installed</th><th class="n">Haiku · 15 single-step</th><th class="n">Sonnet · 15 single-step</th><th class="n">Haiku · all 20</th><th class="n">Sonnet · all 20</th></tr>
<tr class="row-good"><td>Target alone</td><td class="n">{mcp_cell("haiku", "mcp_alone")}</td><td class="n">{mcp_cell("sonnet", "mcp_alone")}</td><td class="n">{mcp_cell("haiku", "mcp_alone", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_alone", True)}</td></tr>
<tr><td>20</td><td class="n">{mcp_cell("haiku", "mcp_pack20")}</td><td class="n">{mcp_cell("sonnet", "mcp_pack20")}</td><td class="n">{mcp_cell("haiku", "mcp_pack20", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_pack20", True)}</td></tr>
<tr><td>~220</td><td class="n">{mcp_cell("haiku", "mcp_crowd200")}</td><td class="n">{mcp_cell("sonnet", "mcp_crowd200")}</td><td class="n">{mcp_cell("haiku", "mcp_crowd200", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_crowd200", True)}</td></tr>
<tr><td>791</td><td class="n">{mcp_cell("haiku", "mcp_crowdall")}</td><td class="n">{mcp_cell("sonnet", "mcp_crowdall")}</td><td class="n">{mcp_cell("haiku", "mcp_crowdall", True)}</td><td class="n">{mcp_cell("sonnet", "mcp_crowdall", True)}</td></tr>
</table></div>"""
_r = {m: E2P[(m, "mcp_alone", "mcp_crowdall", "nonbrowser15")] for m in CM}
_inc = {m: float(_r[m]["skill_lo"]) < 0 < float(_r[m]["skill_hi"]) for m in CM}
_ci2 = lambda m: f'{m.capitalize()} ({CIP(_r[m]["skill_lo"], _r[m]["skill_hi"])} pp)'
ROBUST_MCP = ("For MCP tools, the two-stage CI from alone to 791 tools excludes zero for both models: " + " and ".join(_ci2(m) for m in CM) + "." if not any(_inc.values())
              else "For MCP tools, the two-stage CI from alone to 791 tools includes zero for " + " and ".join(_ci2(m) for m in CM if _inc[m])
              + ("" if all(_inc.values()) else ", but not for " + " and ".join(_ci2(m) for m in CM if not _inc[m])) + ".")
_b = [BRW[(m, st)] for m in CM for st in ("mcp_crowd200", "mcp_crowdall")]
_bl, _bn = sum(int(r["target_definition_loaded"]) for r in _b), sum(int(r["runs"]) for r in _b)
BROWSER_LOADED = (f"In all {_bn} browser runs of the two larger setups, the agent had already loaded the target tool’s definition with <code>ToolSearch</code>." if _bl == _bn
                  else f"In {_bl} of the {_bn} browser runs of the two larger setups, the agent had already loaded the target tool’s definition with <code>ToolSearch</code>.")
_ts = sorted(round(100 * int(E2[(m, st)]["toolsearch"]) / int(E2[(m, st)]["n"])) for m in CM for st in ("mcp_alone", "mcp_pack20", "mcp_crowd200", "mcp_crowdall"))
TOOLSEARCH_SHARE = f"{_ts[0]}–{_ts[-1]}%"

T_EXPLAIN = f"""<div class="wrap"><table>
<tr><th>Possible explanation</th><th>What I observed</th><th>What is missing</th></tr>
<tr><td><b>The entry never reached the model</b> (listing budget)</td><td>Both {A(L["cc_skills"], "Claude Code")} and {A(L["codex_skills"], "Codex")} document caps on the listing. At 220 and 1,020 skills, my descriptions were far over Claude Code’s budget, and Codex’s cache-write totals nearly stopped growing.</td><td>The listing as the model received it. I never captured it.</td></tr>
<tr><td><b>Visible entries compete</b></td><td><code>seo-audit</code> fell from 100% to 0% next to 16 other “seo” skills, while <code>grill-me</code> held at 94%.</td><td>A test that keeps every description visible and varies only the look-alikes.</td></tr>
<tr><td><b>The agent can proceed without a skill</b></td><td>Most misses had no skill selected at all. In the mixed setups the agent searched the folder with <code>Glob</code> and <code>Grep</code> instead.</td><td>Whether the task got done. Only the rerun mixed runs kept the agent’s text.</td></tr>
</table></div>"""
_f = [E2P[(m, "mcp_crowd200", "mcp_crowdall", "nonbrowser15")] for m in CM]
FLAT_CI = max(abs(round(100 * float(r[k]))) for r in _f for k in ("req_lo", "req_hi"))
T_TODO = f"""<div class="wrap"><table>
<tr><th>What I observed</th><th>How sure</th><th>What to do</th></tr>
<tr><td>Selection of the designated skill fell as more skills were installed, starting at 20</td><td>Measured; 95% CIs exclude zero from 20 skills on (Claude); one sample of extra skills</td><td>Enable fewer skills per project</td></tr>
<tr><td>Most misses had no skill selected at all</td><td>Measured; the cause is unknown</td><td>Check what the model can see before rewriting descriptions</td></tr>
<tr><td>Single-step MCP selection in Claude Code held from 220 to 791 tools</td><td>Measured: no change, paired 95% CIs within ±{FLAT_CI} points; search not isolated</td><td>Prefer search over a full listing where you can</td></tr>
</table></div>"""
T_COST = f"""<div class="wrap"><table>
<tr><th>Item</th><th class="n">Runs</th><th class="n">Cost</th></tr>
<tr><td>GPT, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">$119.13</td></tr>
<tr><td>GPT, MCP experiment so far (OpenAI API)</td><td class="n">170</td><td class="n">$52.60</td></tr>
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
R3_EXAMPLES = """<li>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file.” → searched the folder twice with <code>Glob</code>, then answered: “I couldn’t find invoice-jan.pdf or invoice-feb.pdf.” No <code>pdf</code> skill. (The folder is empty by design.)</li>
<li>“What should we fix to rank better on Google?” → four <code>Glob</code> searches and a <code>Grep</code>, then: “I can’t tell what to fix yet, because there’s no website in this working directory.” No <code>seo</code> skill.</li>
<li>“Open sales.xlsx and add a column with the month-over-month growth.” → selected the <code>xlsx</code> skill first, then looked for the file.</li>"""
body = f"""
<article>
<div class="tags">AI Agents · Claude Code · Codex · Agent Skills · MCP</div>
<h1>A Closet Full of Skills and Nothing to Wear: The More Skills You Install, the Less Often Your Agent Picks the Right One (MCP Tools Hold Up Better)</h1>
<p class="dek">I installed up to 1,000 skills and 791 MCP tools in Claude Code and Codex. The skill each request was written for went from being picked 78–100% of the time to 10–34%. In Claude Code, single-step MCP tool selection fell much less, from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in CM)}% to {RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in CM)}%, and held steady from 220 to 791 tools.</p>
<div class="byline">Galina Alperovich · November 2026</div>

<div class="repobox">
<div><span class="lbl">The experiment, data and analysis:</span> {A(L["repo"], "github.com/galinaalperovich/closet-full-of-skills")}. Every request, every result record and every script, so you can reproduce all the numbers for free.</div>
<div><span class="lbl">A skill to check your own agent:</span> <span class="soon">coming soon</span></div>
</div>

<p class="tldr">tldr; Installing a skill doesn’t mean your agent will use it. I sent 120 natural requests to Claude Code and Codex, each written for one particular skill. With only that skill installed, the agent picked it in 78–100% of runs. With 1,000 other skills next to it, in only 10–34%. MCP tools held up much better: in Claude Code, single-step tool selection went from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in CM)}% with the tool alone to {RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in CM)}% with all 791 tools installed. The experiment has its limits (empty folders, stub skills, a short observation window, one sample of extra skills), and they limit how far the result generalizes. But in every configuration I tested, the more skills were installed, the less often the agent picked the one the request was written for. At the end I share a few tricks for dealing with it.</p>

<p>Agent skills became <b>the new npm</b>. A skill is a folder with a <code>SKILL.md</code> file: a name, a short description, and instructions the agent reads only when it needs them. The biggest community collection I found, {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, has over 3,000 skills, and its README invites you to install all of them. MCP servers went the same way: one GitHub server alone exposes 149 tools.</p>

<p>Here is what made me curious. The agent chooses a skill from its description, and the descriptions in that one collection add up to about 129K tokens. <em>The Great Gatsby</em> is about 72K. No harness sends <b>two Gatsbys</b> with every request: Claude Code and Codex both cap the listing. So what happens to the skills that do not fit, and to the ones that do?</p>

<p>People run into this. {A(L["i81081"], "One Claude Code issue")} reports that 75% of project skills (27 of 36) reached the model with only a name, and {A(L["i11364"], "one user counted")} 67,300 tokens of tool definitions from seven MCP servers before the first message. More reports are in the references. What I did not find was the selection rate itself, measured for skills next to MCP tools.</p>

<h2>Why this is a problem</h2>
<p>A skipped skill or tool does not fail loudly. The agent still answers, with its built-in tools and what it already knows, and the result looks plausible. That is the dangerous case when the skill or tool carries something the model does not have: your release checklist, a house template, a compliance rule, or live data. Ask for Apple’s stock price without the finance tool being called, and you may get <b>a confident number from the model’s memory</b>.</p>
<p>Skipping a skill can also cost more than one step. A skill is often a recipe that tells the agent which tools to call and in which order: run the linter, then the tests, then open the pull request. <b>Skip the skill, and nothing makes sure those steps happen.</b> The agent may still do some of them on its own. This experiment did not measure what was left out, but it is the reason the question matters.</p>
<p>These are everyday setups, not edge cases: a few plugins and MCP servers are enough, as the reports above show. Nothing in the answer says the skill was never loaded. Only the trace does, and unless you log tool calls and check for the ones that should have happened, you will not know.</p>

<h2>How an agent picks a skill or a tool</h2>
<p>First, the two things I compare. A <b>skill</b> is a folder of instructions (<code>SKILL.md</code>) that the agent reads when a task matches its description: it teaches the agent <em>how</em> to do something. An <b>MCP tool</b> is a function on a server that the agent calls with arguments and gets a result back: it <em>does</em> one thing, such as creating an issue or fetching a page.</p>
<p><b>Loading a skill is itself a tool call.</b> In Claude Code the model calls the <code>Skill</code> tool; in Codex it reads the file with a shell command such as <code>cat .agents/skills/pdf/SKILL.md</code>. That call returns the skill’s instructions, and the actual work happens in the tool calls that follow. So a skill is a tool call with an extra step in front, while an MCP tool does its work in the call itself. The first call is what I count as “selected”. For Codex, that means a shell command naming the skill’s <code>SKILL.md</code>; I did not check that the read succeeded.</p>
<p>MCP tools also reach the model differently. In Claude Code the model sees only the tool names and loads a full definition when it needs one, with a <code>ToolSearch</code> call. That is a feature of the Claude Code harness. In your own agent built on a model API, every tool definition you pass is sent in full, and search is yours to build (see <a href="#trick-search">[Trick #3]</a>).</p>
{fig_("fig_how", "How a request reaches a skill or a tool. The request arrives together with a capped skill listing and the MCP tools. The model loads a skill, calls a tool, or uses only the harness’s built-in actions (search files, read, run a shell). Loading a skill is itself a tool call: it returns the skill’s instructions, and the work then happens in further tool calls.")}
<p>It helps to see the whole thing as a pipeline, because I measured only one stage of it:</p>
<ol>
<li><b>Installed.</b> The skill folder or MCP server is on disk and enabled.</li>
<li><b>Listed.</b> The harness builds a listing of names and descriptions within a budget. Claude Code gives it {A(L["cc_skills"], "1% of the context window and drops descriptions when it overflows")}. Codex gives it {A(L["codex_skills"], "2%, at most 10,000 tokens, and shortens descriptions first")}.</li>
<li><b>Selected.</b> The model decides to load a skill or call a tool. <b>This is the stage I measured.</b></li>
<li><b>Loaded and used.</b> The full <code>SKILL.md</code> is read, the tool runs, the task gets done. Not measured.</li>
</ol>

<h2>The experiment setup</h2>
{fig_("fig_setup", "The design in one picture. The same request is sent in four setups, from the target alone to 1,000 other skills (or 791 tools), and I count how often the agent picks the target.")}
<p>I picked 20 well-known skills ({A(L["anth_skills"], "Anthropic’s")} pdf, xlsx, pptx and docx, {A(L["mattpocock"], "Matt Pocock’s")} tdd and grill-me, and others; see <a href="#appendix-a">Appendix A</a> for the full list of skills used in the experiment) and 20 everyday MCP tools out of 791 real tool definitions from 73 servers ({A(L["ghmcp"], "GitHub")}, {A(L["cdt"], "Chrome DevTools")}, {A(L["pwmcp"], "Playwright")}, and 70 servers from {A(L["livemcp_gh"], "LiveMCPBench")}).</p>
<p>For each target I used an LLM to write six realistic requests, phrased the way a person would ask, with no explicit invocation: no <code>/pdf</code>, no “use the pdf skill”. Some overlap with names is unavoidable: 63 of the 150 skill requests share a word with the skill’s name, such as “pdf” or “grill”. {A(L["r_prompts"], "All requests are in the repo.")}</p>
{tab_("Example requests. Every target had six like these.", T_EXAMPLES)}
<p>Each request ran in four setups:</p>
<ol>
<li><b>Alone:</b> only the target is installed. “Alone” still includes what the harness ships: Claude Code reported 23 built-in skills in every setup, plus its built-in tools. Codex installs 5 skills of its own on first start, such as <code>skill-creator</code> and <code>imagegen</code>. I did not turn them off, so they were very likely listed in every Codex run too.</li>
<li><b>20:</b> all 20 targets together.</li>
<li><b>~220:</b> the 20 plus 200 others, drawn at random.</li>
<li><b>All:</b> the 20 plus 1,000 other skills, or all 771 other tools.</li>
</ol>
<p>The configurations: Claude Haiku and Claude Sonnet in Claude Code (v2.1.328), and GPT (gpt-6-astra, medium reasoning) in Codex CLI (v0.160.0). Differences between them belong to the whole configuration, not to the model alone.</p>
<p>Four details matter for reading the numbers:</p>
<ul>
<li><b>Stubs.</b> Every skill keeps its real name and description, but its instructions are one line: “reply with one short sentence”. MCP tools return a similar stub. Whatever happens <em>after</em> the first selection is not normal behaviour.</li>
<li><b>Empty folders.</b> Each run starts in a folder with no files, so a request about <code>report.pdf</code> has no such file.</li>
<li><b>Observation window.</b> Claude Code was capped at 3 turns (4 with MCP). Why so short? Picking a skill or a tool is the first decision an agent makes, and it almost always happens in the first turn or two. A short cap kept thousands of runs fast and affordable. The price is that a later selection is not seen. A Codex run is one user turn, which can contain several model and tool steps, with no cap.</li>
<li><b>Scoring.</b> A skill request counts only if the designated skill is selected. A tool request also counts an equivalent tool on another server. Afterwards, a separate Claude session rated the alternatives the agent picked instead, seeing only the request and the two descriptions. That is a retrospective rating by a model, not human validation ({A(L["r_judge"], "prompt and rules")}). It covers every alternative in the skill experiment. In the rerun MCP and mixed runs, 13 misses picked alternatives that were never rated, and I count those as not equivalent.</li>
</ul>
<p><b>How to read the numbers.</b></p>
<ul>
<li><b>Unit of analysis: the request.</b> Each configuration got 120 skill requests and 90 single-step tool requests. Sonnet ran every skill request three times, and its repeats are averaged within the request, so each request counts once. Haiku and GPT ran each request once, GPT because of the API budget.</li>
<li><b>Intervals.</b> 95% confidence intervals (CIs) come from a request-cluster bootstrap (2,000 resamples, fixed seed). Where every run succeeded (GPT alone, 120 of 120), the bootstrap collapses to a point, so I use a Wilson score interval instead.</li>
<li><b>Changes are paired.</b> A change between two setups compares the same requests, in percentage points (pp), with a bootstrap CI for the mean paired difference.</li>
<li><b>Robustness.</b> A two-stage bootstrap that also resamples which skills were chosen gives wider CIs (in the {A(L["r_meth"], "methodology")}). Every skill drop from “alone” to 1,020 skills still excludes zero. {ROBUST_MCP}</li>
<li><b>What the intervals do not cover:</b> the single random draw of extra skills, the wording of these particular requests, and harness versions. The analysis is exploratory, with no correction for multiple comparisons.</li>
</ul>

<h2>Result 1: Skills fade</h2>
{tab_("Share of requests where the agent picked the designated skill, with 95% CIs.", T_SKILLS)}
<p class="note">CIs: request-cluster bootstrap; Wilson score interval for GPT alone (120 of 120).</p>
{fig_("fig_skills", "Share of requests where the designated skill was selected within the observation window. Bars are 95% CIs from resampling requests, except GPT alone (120 of 120), which uses a Wilson score CI. Sonnet ran each request 3 times (360 runs per point); Haiku and GPT once (120). The x axis is not to scale.")}
<p><b>The decline is already there at 20.</b> These are 20 skills about different things: PDFs, SEO, TDD, animation. On the same requests, Haiku lost {E1_DROP("haiku", "pack20")} points and Sonnet {E1_DROP("sonnet", "pack20")}, and almost no request got better. You do not need 1,000 skills to see it: <b>twenty is enough</b>. The 20 descriptions total only about 7,700 characters, but Claude Code’s built-in skills and the listing format also count toward its budget, and I did not capture the listing the model received. So this setup cannot separate competition between entries from truncation.</p>
<p><b>GPT holds, then falls off a cliff:</b> 99% at 20 skills, 83% at 220 and <b>10%</b> at 1,020. Codex reports how many tokens it writes to its cache in each run, and that number barely grew (13.2K → 20.3K tokens) while the descriptions I installed grew by about 45K. That fits Codex’s {A(L["codex_skills"], "documented 10,000-token cap on the listing")}, but it is a weak inference: I did not see what the model saw.</p>
<p><b>Sonnet picked the designated skill more often than Haiku at every size</b>, and both declined.</p>

<h3>When the designated skill was not picked, what did the agent do instead?</h3>
<p>A miss can mean three different things. The agent picked another skill, sometimes an equally good one. It picked no skill at all and carried on with its built-in tools. Or it ran out of turns before choosing anything. Figure 4 splits the runs with 1,020 skills into these groups.</p>
{fig_("fig_misses", "Outcomes with 1,020 skills installed. “Equivalent alternative”: the rater judged the other skill a fine choice for that request. “Other alternative” combines alternatives rated related, inappropriate or unassessable. Hatched: the run hit Claude Code’s 3-turn limit with no skill selected. “No skill detected”: in Claude Code, no <code>Skill</code> call. In Codex, no shell command naming a skill’s <code>SKILL.md</code>; a read of one of Codex’s own 5 skills (<code>skills/.system/…</code>) would not be detected.")}
<p>Most misses were not a wrong skill. They were runs where <b>no skill was detected at all</b>, which changes the debugging question from “why this wrong skill?” to “was a skill exposed and selected at all?” What the agent did in those runs instead is worth investigating further.</p>
<ul>
<li><b>Haiku:</b> more than half of its no-skill runs (53 of 97) hit the 3-turn limit. With a longer window, some of them might have picked the skill later.</li>
<li><b>Sonnet:</b> two thirds of its misses (160 of 239) ended normally, with no skill selected.</li>
<li><b>GPT:</b> about a quarter of its misses (29 of 108) picked a different skill, and the rater judged 12 of those equivalent. Counting them, GPT’s rate at 1,020 skills is 20%, not 10%.</li>
</ul>
<p>One request shows why that adjustment matters. “Interview me about my plan for the onboarding redesign” was written for <code>grill-me</code>. With 220 skills installed, all three configurations selected <code>interview-me</code> instead. Strict scoring counts three misses. The rater called the alternative equivalent, and I agree.</p>

<h3>Which skills kept being selected</h3>
{fig_("fig_dumbbell", "Sonnet. Each arrow runs from a skill installed alone (hollow dot) to the same skill among 1,020 others (filled dot), 18 runs each. A skill with no arrow did not change. Skills are grouped by where they end up. The 18 runs are 3 repetitions of only 6 distinct requests, so each dot rests on 6 requests, and a difference of a few runs between two skills is not a ranking.")}
<p>Two contrasting cases. <code>grill-me</code> went from 100% to 94%: nothing else in the crowd is named “grill”. <code>seo-audit</code> went from 100% to <b>0%</b>, next to 16 other skills mentioning “seo”. Skills with an unusual name or file type (<code>json-canvas</code>, <code>xlsx</code>) held up, and skills on a crowded topic (security, debugging, animation) did not. My design cannot show that distinctiveness is the cause.</p>

<h2>Result 2: MCP tools hold up better</h2>
<p>Then I repeated the whole design with MCP tools. I picked 20 everyday tools, such as creating a GitHub issue, taking a screenshot of a web page or getting a stock price, and served each one from its real published definition. Each tool request ran in four setups: (1) only the target tool; (2) all 20 target tools together; (3) the 20 plus 200 random tools, about 220 in total; (4) all 791 tools from 73 servers.</p>
<p><b>The tools held up much better.</b> With the target tool alone, Claude Code picked it for {P(E2[("haiku", "mcp_alone")]["nonbrowser_rate"])}% (Haiku) and {P(E2[("sonnet", "mcp_alone")]["nonbrowser_rate"])}% (Sonnet) of the single-step requests. With all 791 tools installed, it still did for {P(E2[("haiku", "mcp_crowdall")]["nonbrowser_rate"])}% and {P(E2[("sonnet", "mcp_crowdall")]["nonbrowser_rate"])}%. Skills, remember, fell to 16% and 34%.</p>
{fig_("fig_fade", "Claude Code only. Skills (solid lines) against the 15 single-step MCP tool targets (dashed lines). Bars are 95% CIs from resampling requests. “All installed” means 1,020 skills or 791 tools. The two experiments use different tasks and scoring rules, and the x axis is not to scale.")}
<p>What loss there was came mostly at the first step, from one tool to twenty, where near neighbours appear for the first time: four GitHub tools, two browser servers. After that the curve is flat. Adding 571 more tools, from about 220 to 791, changed <b>nothing measurable</b> ({P(E2[("haiku", "mcp_crowd200")]["nonbrowser_rate"])}% → {P(E2[("haiku", "mcp_crowdall")]["nonbrowser_rate"])}% for Haiku, {P(E2[("sonnet", "mcp_crowd200")]["nonbrowser_rate"])}% → {P(E2[("sonnet", "mcp_crowdall")]["nonbrowser_rate"])}% for Sonnet). “No change observed” is not proof of no effect, but it is a very different picture from the skills.</p>
{tab_("Share of tool requests where Claude Code called the designated tool (or an equivalent one), with 95% CIs.", T_MCP)}
<p class="note">“15 single-step”: the targets that need one call. “All 20”: including the five browser targets described below. I made this split after seeing the first results, which is why both are shown. CIs: request-cluster bootstrap.</p>
<p><b>Five of the tools measured my setup, not the agent.</b> “Take a screenshot of example.com” needs two steps: open the page, then take the screenshot. In the larger setups the agent did the sensible thing. It loaded both tools, opened the page, got my stub reply (“reply with one short sentence”), and stopped. {BROWSER_LOADED} So for these five targets I know the agent found the right tool, but not whether it would have used it. I report them separately and keep them out of the main curve.</p>
<p><b>GPT is only partly measured.</b> With the target tool alone, GPT picked it 91% of the time. With 20 tools I ran only 24 of the 90 requests before I paused the GPT runs to save budget. On those 24, selection went from 100% to 92%. I have no GPT data for the larger tool setups. Codex blocked these MCP calls after the model had made them (more on that {A("#check-your-own-agent", "below")}), so the choice of tool is measured, but not what the agent did with the result.</p>

<h2>Result 3: Skills and tools together</h2>
<p>Real setups have both. I built two: a smaller one with 100 skills and 437 tools, and a larger one with 400 skills and all 791 tools, including servers that overlap with skills (<code>xlsx</code> next to an Excel server). Then I sent the skill requests (the 20 targets plus five skills from repos trending this month, 150 in total) and the tool requests.</p>
{fig_("fig_mix", "Claude Code. Share of requests where the designated component was selected. “Single component” is the target installed alone, with every request weighted equally. Tool requests are the 90 for the 15 single-step targets. Whiskers: 95% CI (request-cluster bootstrap).")}
<p><b>The same pattern, only stronger.</b> Compared with the component installed alone, skill requests lost {SK_LOSS} points and single-step tool requests lost {TOOL_LOSS}. Read that gap with some care:</p>
<ul>
<li><b>The scoring is not symmetric.</b> A skill request counts only the exact designated skill; a tool request also counts an equivalent tool. Counting the alternatives the rater judged equivalent raises the skill rates by {EQ_GAIN} points, possibly a little more: 5 skill misses in these setups picked alternatives that were never rated, and I count them as not equivalent.</li>
<li><b>The tasks differ.</b> Skill requests and tool requests are different jobs, so this is not a matched comparison of skills against tools.</li>
<li><b>These are two setups I constructed.</b> Separating the effect of skills from the effect of tools needs a crossed design.</li>
</ul>
<p>So what did the agent do when it skipped the skill? In {BUILTIN_SHARE} of the skill requests that missed {BUILTIN_COUNT}, it <b>only used built-in tools</b>, mostly <code>Glob</code> and <code>Grep</code>: it went looking in the empty folder for the files the request mentioned. Three examples from Sonnet in the larger setup:</p>
<ul>
{R3_EXAMPLES}
</ul>

<h2>Why did tools hold up better than skills?</h2>
<p>Put both experiments on one scale, and the difference is hard to miss. The forest plot below shows, for every configuration, how much selection changed compared with the target installed alone, on the same requests. The skill rows slide further left as the collection grows. The tool rows stay close to zero.</p>
{fig_("fig_forest", "Paired change from the target alone, in percentage points, with 95% CIs (request-cluster bootstrap). Filled dots: skills, 120 requests per row. Hollow dots: the 15 single-step MCP tool targets, 90 requests per row. GPT with 20 tools covers only the 24 requests that were run.")}
<p>My data cannot say why, but here is the intuition I find most convincing. <b>A skill listing is like a restaurant menu printed on one page.</b> Every dish has to fit, so the more dishes there are, the smaller the print, and past a certain size the printer starts dropping descriptions. The model reads that whole page with every request and has to spot the right line. <b>MCP tools in Claude Code work more like asking the waiter.</b> The model sees only the tool names, and when it needs one it searches and gets the full definition back. Claude Code called <code>ToolSearch</code> in {TOOLSEARCH_SHARE} of the MCP runs. A long menu barely matters if you can ask for what you want.</p>
<p>Two more things probably help the tools. A tool name is usually a verb that matches the request almost literally (<code>create_issue</code>, <code>take_screenshot</code>, <code>get_current_stock_price</code>), while a skill describes a whole workflow in broad words that its neighbours share: 16 skills in my crowd mention “seo”. And a tool request asks for an action, while a skill request describes a goal, which leaves more room for the model to decide it can manage on its own.</p>
<p>Treat all of this as hypotheses. The two experiments use different tasks and different scoring, so this is not a matched comparison of skills against tools. The test that would settle it is described in <a href="#what-s-next">What’s next</a>.</p>

<h2>What else might explain the skill decline?</h2>
<p>The data show where selection changed, not why. Here are the explanations I find plausible, what I observed for each, and what is missing. My logs cannot separate them.</p>
{tab_("Possible explanations for the skill decline.", T_EXPLAIN)}
<p>Research on long contexts makes the second explanation plausible without proving it here. {A(L["nolima"], "NoLiMa")} found that when a question shares no words with the passage it needs, even one of the stronger models it tested fell from 99.3% to 69.7% at 32K tokens. Chroma’s {A(L["rot"], "Context Rot")} study reports that on-topic distractors hurt more than unrelated ones. Those are different tasks, models and metrics, so I treat them as background, not as evidence about my runs. (A toy calculation of the dilution idea is in <a href="#appendix-c">Appendix C</a>.)</p>
<p><b>Why measure selection at all</b>, if the answer may still be fine? Because some skills are procedures you require: a release checklist, a security review, a house style. Skipping one of those matters even when the task looks done. For a convenience wrapper, it may not.</p>

<h2>What you can do about it</h2>
{tab_("What I observed, how sure I am, and what to do about it.", T_TODO)}
<h3>[Trick #1] Check what is actually exposed</h3>
<p>In Claude Code, <code>/context</code> shows the size of your skill listing and {A(L["cc_skills"], "<code>/doctor</code> tells you whether descriptions are being dropped")}. Codex prints a warning when it goes over its budget ({A(L["c19679"], "codex#19679")}). Blake Crosley wrote a good account of {A(L["crosley"], "the skills his agent could not see")}. This is a diagnostic, and it is the first thing I would do.</p>
<h3>[Trick #2] Enable less, per project</h3>
<p>This is the one manipulation I tested: with fewer skills installed, the designated one was selected more often (answer quality not measured). Enable plugins per project, turn off unused skills with <code>/skills</code>, and if you only need <code>pdf</code> from a 3,000-skill collection, install <code>pdf</code>. Overlapping collections can expose the same skill twice, a case I did not measure, so check what is actually enabled.</p>
<h3 id="trick-search">[Trick #3] Test other ways to discover and invoke (untested here)</h3>
<ul>
<li><b>Invoke required skills by name</b> (<code>/skill-name</code>) instead of hoping for a match.</li>
<li><b>Give a skill a trigger nobody else has.</b> The skills that held in my sample had concrete nouns and file types. That is an observation, not a controlled test.</li>
<li><b>Raise the listing budget</b> ({A(L["cc_skills"], "<code>skillListingBudgetFraction</code> in Claude Code")}, {A(L["codex_skills"], "<code>skills.max_context_tokens</code> in Codex")}). You pay for it on every request.</li>
<li><b>Use a router skill or a hook.</b> Scott Spence measured {A(L["spence"], "a hook that makes Claude evaluate skills before answering")}: 84% activation against 20% for a simple keyword hook. Ivan Seleznov ran {A(L["seleznov"], "650 activation trials")} on similar ideas.</li>
<li><b>Search instead of listing.</b> Claude Code already defers MCP tools behind {A(L["toolsearch"], "tool search")}. In your own agent you have to build it: the Claude API’s tool search tool can defer tools, and with any model you can embed the descriptions and retrieve the closest few. {A(L["ragmcp"], "RAG-MCP")} reports 13.6% → 43.1% tool selection with retrieval, and Anthropic 49% → 74% on {A(L["advtool"], "an internal evaluation")}. Neither is measured for skills.</li>
</ul>

<h2>Check your own agent</h2>
<p>Pick a skill you rely on, go to a real project folder where the files it needs exist, and send a few requests the way you would really ask:</p>
<pre><code># Claude Code: prints the skill or MCP tool it selected
claude -p "Audit the SEO of my site." --output-format stream-json --verbose --max-turns 3 \\
  | jq -r 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use") | select(.name=="Skill" or (.name|startswith("mcp__")))
           | if .name=="Skill" then "skill: " + .input.skill else "tool: " + .name end'

# Codex: prints the SKILL.md paths named in its commands (a match does not prove
# the read succeeded, and Codex's own skills under skills/.system are not matched)
codex exec --json -s read-only "Audit the SEO of my site." \\
  | grep -o 'skills/[a-z0-9-]*/SKILL.md' | sort -u</code></pre>
<p>Then repeat with only that skill enabled. A handful of requests will not give you a reliable rate, but it will show whether the skill is ever selected. I would genuinely love to see your numbers.</p>
<p>Four things I learned the hard way. The two about Claude Code forced me to rerun part of this study:</p>
<ul>
<li><b>In <code>-p</code> mode, Claude Code refuses MCP calls you have not allowed.</b> Nobody is there to approve them. The command above still prints the selection, but whatever the agent does next is a reaction to the refusal. Add <code>--allowedTools mcp__&lt;server&gt;</code> for the servers you are testing.</li>
<li><b>Claude Code keeps a memory per folder.</b> A note saved in one test run is loaded at the start of the next run in the same folder. Use a fresh folder for every run, or check <code>~/.claude/projects/</code> between runs.</li>
<li><b>Codex blocks MCP calls too.</b> With <code>approval_policy="never"</code>, which I used, Codex lets the model choose a tool on a server you have not approved, then blocks the call. The choice still shows, but the agent gets an approval error instead of the result. Approve the servers you are testing with <code>-c 'mcp_servers.&lt;name&gt;.default_tools_approval_mode="approve"'</code>.</li>
<li><b>Codex ships skills of its own.</b> It installs 5 on first start. To test a skill truly alone, turn them off with <code>-c skills.bundled.enabled=false</code>.</li>
</ul>

<h2>What this cost</h2>
{tab_("What the runs cost.", T_COST)}
<p>The GPT figures are calculated from the token usage Codex reported, at {A(L["price"], "OpenAI’s list prices")}. I have not reconciled them against the invoice. Cache writes were 76–87% of each run’s calculated cost. {A(L["r_cost"], "The per-batch breakdown is in the repo.")}</p>
<p>Running every remaining GPT cell at full size would cost about $1,400 by my estimate, most of it in the mixed setups. That assumes Codex loads every tool definition, as my 20-tool runs suggest. {A(L["contextbolt"], "Another measured post")} reports that Codex defers MCP tools, so the estimate may be too high. I have not reconciled the two.</p>

<h2>Limitations of the experiment</h2>
<ul>
<li><b>Selection, not quality.</b> A run without the skill can still produce a fine answer.</li>
<li><b>Minimal setup.</b> Empty folders, stub instructions, and 3–4 turns in Claude Code. Some capped runs might have selected the skill later.</li>
<li><b>No captured listing, little response text.</b> I know what was called, not what the model saw. Full logs, including what the agent wrote, exist only for the rerun Claude Code MCP and mixed runs.</li>
<li><b>Few samples.</b> One random sample of extra skills, and six LLM-written requests per target. The CIs cover variation across these requests and runs, not the draw of extra skills or the wording of the requests.</li>
<li><b>Configurations, not models.</b> Claude Code and Codex differ in model, prompts, budgets and permissions. For example, Codex could search the web in these runs, and Claude Code could not.</li>
<li><b>GPT data is thinner.</b> One run per request, and MCP only with 1 tool and, partly, with 20. Codex also does not report an MCP server that failed to start, so a GPT tool miss could be a server that never connected.</li>
<li><b>Things change.</b> Harness limits, commands and prices are as documented in November 2026. The issue reports I link are motivation, not evidence of current behaviour.</li>
</ul>
<p>The {A(L["r_meth"], "full methodology")}, {A(L["r_rev"], "an external review of it")}, {A(L["r_chg"], "my response to that review")}, and all data and scripts are in {A(L["repo"], "the GitHub repo")}.</p>

<h2>What’s next</h2>
<p>This experiment highlights three things. <b>Installing a skill is not the same as having it available</b> when a request needs it. The decline starts early, already at 20 skills. And tools that the agent finds by search held up much better than skills that sit in one long listing.</p>
<p>The next steps I would check:</p>
<ol>
<li><b>Validation.</b> Capture the listing the model actually receives, put real files in the folders, and give Claude 10 turns instead of 3.</li>
<li><b>Search for skills.</b> Does a <code>ToolSearch</code>-style step help skills the way it seems to help tools? The clean test keeps the visible listing and the files constant and varies only the number of look-alikes, with search on and off.</li>
<li><b>More catalogs and controls.</b> Other random samples of extra skills, control requests, and skills and tools varied separately.</li>
</ol>
<p>Also worth looking at: other harnesses (Cursor, Gemini CLI), skills that call other tools, where one missed selection could cost a whole chain of calls, and the quality of the final answer, not just the selection. The full plan with costs is in {A(L["r_follow"], "the follow-up protocol")}.</p>
<p>If you want to contribute: {A(L["repo"], "the experiment repo")} is open, and reruns on newer harness versions, other models or other harnesses are very welcome. The skill for checking your own setup is coming soon.</p>

<h2>Conclusion</h2>
<p>I started with a simple question: if I install a thousand skills, does my agent get more capable? What changed my view is the difference between installing a capability and having it reliably available when a request needs it. In this test, selection of the designated skill fell as the collection grew, while single-step MCP tool selection in Claude Code held up better. Before adding another big collection, I would check what the agent can actually see, and I would measure answer quality separately before deciding that more activation is always better.</p>
<p>Thanks for reading! If you run the check on your own setup, tell me what you got.</p>

<h2 id="appendix-a">Appendix A: The 20 target skills</h2>
{tab_("The 20 target skills, where they come from, and one of their six requests.", SK_TABLE)}

<h2 id="appendix-b">Appendix B: A survey of 42 popular skill repos</h2>
<p>Before the experiment I cloned a sample of popular skill repositories, found through GitHub topic searches plus seven repos {A(L["trending"], "trending this month")}: 42 repos. A static script checked frontmatter, names, file links, bundled scripts and size. No code was run. This covers skills only, not MCP servers.</p>
<p>Two counts are used below. The repos contain 14,418 <code>SKILL.md</code> files with 7,848 distinct contents. Counting each skill name once per repo gives 6,908 skills.</p>
<ul>
<li><b>Few structural problems.</b> The scanner found each issue it checks for (broken links, missing scripts, invalid names) in 0–3% of skills.</li>
<li><b>Few bundled tests.</b> It detected test or eval files for 2.6% of skills (177 of 6,908), and none at all in 64% of the repos (27 of 42). Tests can live elsewhere. {A(L["marketing"], "coreyhaines31/marketingskills")} ships evals for all 53 of its skills.</li>
<li><b>Many repeated files.</b> 46% of the files (6,570 of 14,418) repeat another file’s content, mostly because collections ship each skill once per packaging format. That does not mean an installation loads them all.</li>
<li><b>Shared names.</b> 831 skill names appear in two or more repos. For 32% of them (270 of 831), at least two repos carry nearly identical descriptions (80% or more of the text matches), for example 18 of Anthropic’s 20 skills inside {A(L["davila7"], "davila7/claude-code-templates")}. A shared name is not always the same skill: <code>seo-audit</code> exists in five repos with five different descriptions.</li>
<li><b>Trigger phrases.</b> 48% of the distinct files lacked the trigger phrases my heuristic looks for (“when”, “use for”, “trigger”). That is a keyword check, not a judgment of the description.</li>
<li><b>Size.</b> Installed whole, 38% of the repos (16 of 42) have more description text than Claude Code’s listing budget for a 200K window (about 8,000 characters). The largest is roughly 60 times over, and even Anthropic’s own 20 skills are slightly over at about 9,700 characters.</li>
</ul>
{fig_("fig_weight", "Estimated size of the skill descriptions if you install each collection whole. The red line is roughly Claude Code’s listing budget for a 200K window.")}
<p><b>Overlapping collections.</b> Whether two copies of a skill are both exposed depends on how you install them. {A(L["cc_skills"], "Claude Code namespaces plugin skills")} as <code>/plugin-name:skill-name</code>, so both load. {A(L["codex_skills"], "Codex’s documentation")} says same-name skills are not merged. Copying folders by hand into one skills folder keeps one copy. If you install overlapping collections, check what is actually enabled. I deduplicated names in my setups, so the experiment did not measure duplicates.</p>

<h2 id="appendix-c">Appendix C: A toy calculation about dilution</h2>
<p>This is illustrative arithmetic, not a model of these agents, and nothing in my data measures attention. It only shows why “more entries can dilute a match” is a reasonable thing to test.</p>
<p>In a {A(L["vaswani"], "transformer")}, each attention head turns scores into weights with a softmax, and within one head the weights add up to 1:</p>
<p class="formula"><i>a<sub>i</sub></i> = e<sup><i>s<sub>i</sub></i></sup> / Σ<sub><i>j</i></sub> e<sup><i>s<sub>j</sub></i></sup></p>
<p>Now a cartoon with several assumptions: each skill description is one block, the target’s weight before normalising (e<sup><i>s</i></sup>) is 20 times that of every unrelated skill, which means a score higher by ln 20 ≈ 3, look-alikes get the same weight as the target, scores do not change when entries are added, and nothing else is in the context. Then the target’s share is 20 / (20 + <i>n</i>) for <i>n</i> unrelated skills, and 20 / (20 + 20<i>k</i> + <i>n</i>) if <i>k</i> of them are look-alikes:</p>
{fig_("fig_attn", "Toy arithmetic under the assumptions in the text. Real models have many heads and layers, scores change with the input, and an attention weight is not a probability of selecting a skill.")}
<p>Nakanishi’s {A(L["ssmax"], "Scalable-Softmax")} paper describes a related effect, attention weights flattening as inputs grow, and proposes a fix. That is background research, not evidence about my runs.</p>

<h2>References</h2>
<ol class="refs">
<li>Code, data and methodology for this post: {A(L["repo"], "galinaalperovich/closet-full-of-skills")}</li>
<li>{A(L["cc_skills"], "Claude Code documentation: Skills")}</li>
<li>{A(L["codex_skills"], "Codex documentation: Build skills")}</li>
<li>{A(L["spec"], "Agent Skills specification")}</li>
<li>{A(L["anth_skills"], "anthropics/skills")} · {A(L["sickn33"], "sickn33/agentic-awesome-skills")} · {A(L["mattpocock"], "mattpocock/skills")} · {A(L["obsidian"], "obsidianmd/obsidian-skills")} · {A(L["marketing"], "coreyhaines31/marketingskills")} · {A(L["davila7"], "davila7/claude-code-templates")}</li>
<li>Trending skills used in Result 3: {A(L["hallmark"], "Nutlope/hallmark")} · {A(L["cfsec"], "cloudflare/security-audit-skill")} · {A(L["claudeseo"], "AgriciDaniel/claude-seo")} · {A(L["ffmpeg"], "kajisho5/ffmpeg-skill")} · {A(L["igskill"], "Jakeschincariol/instagram-agent-skill")}</li>
<li>MCP sources: {A(L["ghmcp"], "github/github-mcp-server")} · {A(L["cdt"], "ChromeDevTools/chrome-devtools-mcp")} · {A(L["pwmcp"], "microsoft/playwright-mcp")} · {A(L["livemcp_gh"], "LiveMCPBench")} ({A(L["livemcp"], "paper")})</li>
<li>Gan &amp; Sun. {A(L["ragmcp"], "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation")} (2025)</li>
<li>Anthropic: {A(L["toolsearch"], "Tool search tool")} · {A(L["advtool"], "Advanced tool use")}</li>
<li>Reports about skills: {A(L["i81081"], "claude-code#81081")} · {A(L["i56710"], "#56710")} · {A(L["i64606"], "#64606")} · {A(L["i10768"], "#10768")} · {A(L["c19679"], "codex#19679")} · {A(L["r_cc"], "r/ClaudeCode")} · {A(L["r_hell"], "r/claudeskills")} · {A(L["fsck"], "Jesse Vincent")}</li>
<li>Reports about MCP tools: {A(L["i6915"], "claude-code#6915")} · {A(L["i7328"], "#7328")} · {A(L["i37793"], "#37793")} · {A(L["i11364"], "#11364")} · {A(L["cursor40"], "Cursor forum 1")} · {A(L["cur79686"], "Cursor forum 2")} · {A(L["g21823"], "gemini-cli#21823")} · {A(L["r_mcp1"], "r/mcp 1")} · {A(L["r_mcp2"], "r/mcp 2")}</li>
<li>{A(L["spence"], "Scott Spence: How to make Claude Code skills activate reliably")} · {A(L["seleznov"], "Ivan Seleznov: 650 trials")} · {A(L["crosley"], "Blake Crosley: The skills my agent could not see")}</li>
<li>{A(L["contextbolt"], "ContextBolt: Too Many MCP Servers? What Each One Costs, Measured")}</li>
<li>{A(L["price"], "OpenAI: gpt-6-astra model page and pricing")}</li>
<li>Modarressi et al. {A(L["nolima"], "NoLiMa: Long-Context Evaluation Beyond Literal Matching")} (ICML 2025)</li>
<li>Hong, Troynikov &amp; Huber. {A(L["rot"], "Context Rot: How Increasing Input Tokens Impacts LLM Performance")} (Chroma, 2025)</li>
<li>Vaswani et al. {A(L["vaswani"], "Attention Is All You Need")} (2017)</li>
<li>Nakanishi. {A(L["ssmax"], "Scalable-Softmax Is Superior for Attention")} (2025)</li>
</ol>
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
    i = body.index('class="tldr"'); j = body.index("</p>", i) + 4
    return body[:j] + "\n\n" + "".join(out) + body[j:]
body = add_toc(body)

html = f'<title>A Closet Full of Skills</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">\n<style>{css}</style>\n{body}\n{CHART_JS}'
open(os.path.join(B, "skills-mcp-post.html"), "w").write(html)
print("ok", len(html))
