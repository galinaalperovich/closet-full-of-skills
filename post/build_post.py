"""Assemble the post: skills-mcp-post.html (figures from figs.json; numbers read from analysis/derived and listing/)."""
import json, os, re
B = os.path.dirname(os.path.abspath(__file__))
fig = json.load(open(os.path.join(B, "figs.json")))
t = open(os.path.join(B, "post.tpl.html")).read(); css = t[t.index("<style>") + 7:t.index("</style>")]
css = css.replace("--s-haiku:#f0a050; --s-sonnet:#8aa6ff; --s-gpt:#5fd39a", "--s-haiku:#cf7c2e; --s-sonnet:#6f8be6; --s-gpt:#2fa86f; --s-fable:#d867a8;"
  " --seg-target:#4fc1b9; --on-seg-target:#0d1f1e; --seg-eq:#2c7a75; --on-seg-eq:#e5e8eb; --seg-alt:#6b7681; --on-seg-alt:#ffffff; --seg-none:#3a434b; --on-seg-none:#e5e8eb; --seg-cap:#3a434b; --on-seg-cap:#e5e8eb;"
  " --seq1:#2a5a57; --seq2:#3f938c; --seq3:#7fd3cc; --band-hi:#22a094; --band-mid:#8b949e; --band-lo:#e4664c;"
  " --row-good:rgba(34,160,148,.17); --row-bad:rgba(228,102,76,.17); --row-warn:rgba(240,190,60,.17); --box-bg:rgba(79,193,185,.08)")
css = css.replace("--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;", "--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a; --s-fable:#a8257a;"
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
li.hl{background:var(--row-warn);border-radius:4px;padding:.15rem .4rem;margin-left:-.4rem}
.repobox{border:2px solid var(--accent);border-radius:8px;background:var(--box-bg);padding:.6rem 1rem;margin:.4rem 0 .2rem;font:.95rem/1.55 var(--sans)}
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
 "price": "https://developers.openai.com/api/docs/models/gpt-6-astra.md", "price_sol": "https://developers.openai.com/api/docs/models/gpt-6-sol.md",
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
CM = ("haiku", "sonnet")                       # Claude Code models that also ran the mixed setups
C3 = ("haiku", "sonnet", "fable")              # Claude Code models with the skills and MCP experiments
T4 = ("haiku", "sonnet", "fable", "gpt_sol")   # configurations with the complete MCP experiment
ALLM = ("haiku", "sonnet", "fable", "gpt", "gpt_sol")
MNAME = {"haiku": "Haiku", "sonnet": "Sonnet", "fable": "Fable", "gpt": "GPT-6 Astra", "gpt_sol": "GPT-6 Sol"}
LIST = lambda xs: (lambda v: ", ".join(v[:-1]) + " and " + v[-1])(list(xs))   # "a, b and c"
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
                                 "".join(f'<td class="n">{e1_cell(m, s)}</td>' for m in ALLM) + "</tr>")
T_SKILLS = ('<div class="wrap"><table>\n<tr><th>Setup</th><th class="n">Skills</th>' + "".join(f'<th class="n">{MNAME[m]}</th>' for m in ALLM) + '</tr>\n' +
            "\n".join([_e1row(' class="row-good"', "Target skill alone", "1", "alone"), _e1row("", "20 skills together", "20", "pack20"),
                       _e1row("", "Plus 200 others", "220", "crowd200"), _e1row(' class="row-bad"', "Plus 1,000 others", "1,020", "crowd1000")]) +
            "\n</table></div>")
E1R = lambda m, s: P(E1[(m, s)]["rate"])
def MISS(m):   # misses at 1,020 skills: total, another skill picked, of those rated equivalent / never rated, no skill
    r = E1[(m, "crowd1000")]; g = lambda k: int(r[k])
    alt = g("miss_alt_equivalent") + g("miss_alt_related") + g("miss_alt_inappropriate") + g("miss_alt_unassessable")
    return dict(n=g("n") - g("target_selected"), alt=alt, eq=g("miss_alt_equivalent"), unrated=g("miss_alt_unassessable"),
                none=g("miss_no_skill_completed") + g("miss_no_skill_turn_limit"))
MF, MA, MS = MISS("fable"), MISS("gpt"), MISS("gpt_sol")
SEE = lambda hid, text: f'<a href="#{hid}">→ {text}</a>'
NB = lambda m, st: P(E2[(m, st)]["nonbrowser_rate"])
SUM_MCP = (f'Single-step tool selection went from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in T4)}% alone to '
           f'{RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in T4)}% among 791, in both harnesses.')
def BRW2(m):   # the five browser targets in the two larger setups, where a tool to open the page is installed
    rs = [E2[(m, st)] for st in ("mcp_crowd200", "mcp_crowdall")]
    return sum(int(r["browser_strict"]) for r in rs), sum(int(r["browser_n"]) for r in rs)
BRW_ALL = (sum(BRW2(m)[0] for m in T4), sum(BRW2(m)[1] for m in T4))
BRS = lambda m: f'{sum(int(E2[(m, st)]["browser_strict"]) for st in ("mcp_alone", "mcp_pack20"))} of {sum(int(E2[(m, st)]["browser_n"]) for st in ("mcp_alone", "mcp_pack20"))}'
CB = rdv("cost_by_batch.csv")
_cost = lambda m, exp: sum(float(r["list_price_usd"]) for r in CB if r["model"] == m and r["exp"] == exp and r["batch"] == "main")
_runs = lambda m, exp: sum(int(r["attempts"]) for r in CB if r["model"] == m and r["exp"] == exp and r["batch"] == "main")
SOL_E1, SOL_E2 = _cost("gpt_sol", "E1"), _cost("gpt_sol", "E2")
SOL_FB = 12.60   # e1_fullbudget_gpt_sol.jsonl, from reported token usage at list prices
SOL_E2_FIRST = 39.00   # the first GPT-6 Sol MCP run (mcp/gpt_sol.jsonl), replaced by the third round
HS_COST = sum(_cost(m, e) for m in CM for e in ("E1", "E2", "E3", "E3b")); HS_RUNS = sum(_runs(m, e) for m in CM for e in ("E1", "E2", "E3", "E3b"))
FABLE_COST, FABLE_RUNS = _cost("fable", "E1") + _cost("fable", "E2"), _runs("fable", "E1") + _runs("fable", "E2")
_mcprow = lambda cls, lab, st: f'<tr{cls}><td>{lab}</td>' + "".join(f'<td class="n">{mcp_cell(m, st)}</td>' for m in T4) + "</tr>"
T_MCP = ('<div class="wrap"><table>\n<tr><th>Tools installed</th>' + "".join(f'<th class="n">{MNAME[m]}</th>' for m in T4) + "</tr>\n"
         + "\n".join([_mcprow(' class="row-good"', "Target alone", "mcp_alone"), _mcprow("", "20", "mcp_pack20"),
                      _mcprow("", "~220", "mcp_crowd200"), _mcprow(' class="row-warn"', "791", "mcp_crowdall")]) + "\n</table></div>")
_r = {m: E2P[(m, "mcp_alone", "mcp_crowdall", "nonbrowser15")] for m in CM}
_inc = {m: float(_r[m]["skill_lo"]) < 0 < float(_r[m]["skill_hi"]) for m in CM}
_ci2 = lambda m: f'{m.capitalize()} ({CIP(_r[m]["skill_lo"], _r[m]["skill_hi"])} pp)'
ROBUST_MCP = ("For MCP tools, the two-stage CI from alone to 791 tools excludes zero for both models: " + " and ".join(_ci2(m) for m in CM) + "." if not any(_inc.values())
              else "For MCP tools, the two-stage CI from alone to 791 tools includes zero for " + " and ".join(_ci2(m) for m in CM if _inc[m])
              + ("" if all(_inc.values()) else ", but not for " + " and ".join(_ci2(m) for m in CM if not _inc[m])) + ".")
ROBUST_MCP_SHORT = ("For single-step MCP tools from alone to 791, it excludes zero for both models." if not any(_inc.values()) else
                    "For single-step MCP tools from alone to 791, it includes zero for " + " and ".join(m.capitalize() for m in CM if _inc[m])
                    + ("" if all(_inc.values()) else " but not for " + " and ".join(m.capitalize() for m in CM if not _inc[m])) + ".")
_ts = sorted(round(100 * int(E2[(m, st)]["toolsearch"]) / int(E2[(m, st)]["n"])) for m in C3 for st in ("mcp_crowd200", "mcp_crowdall"))
TOOLSEARCH_SHARE = f"{_ts[0]}–{_ts[-1]}%"

_f = [E2P[(m, "mcp_crowd200", "mcp_crowdall", "nonbrowser15")] for m in T4]
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
_sol = {r["target"]: r for r in rdv("e1_per_target.csv") if r["model"] == "gpt_sol"}
SOL1K_HITS = sum(int(r["crowd1000"].split("/")[0]) for r in _sol.values())
SOL1K_LISTED_HITS = sum(int(_sol[t]["crowd1000"].split("/")[0]) for t in CX1K_NAMES)
_n = lambda x: f"{int(x):,}"
SEO_CHARS = next(r["desc_chars_installed"] for r in LT if r["target"] == "seo-audit")
_pt = {(r["model"], r["target"]): r for r in rdv("e1_per_target.csv")}
SEO = lambda m, st: _pt[(m, "seo-audit")][st].replace("/", " of ")
_fb = [json.loads(l) for l in open(os.path.join(B, "..", "fable.jsonl"))]
SEO_FABLE_ALT = sorted({x.split(":")[-1] for r in _fb if r["target"] == "seo-audit" and r["cond"] == "crowd1000" and not r["hit"] for x in r.get("fired", [])})
T_SEEN = f"""<div class="wrap"><table>
<thead><tr><th>Setup</th><th>What the model saw</th><th>Picked</th></tr></thead><tbody>
<tr class="row-good"><td>20 skills</td><td><code>seo-audit: When the user wants to audit or diagnose SEO…</code></td><td>Sonnet: {SEO("sonnet", "pack20")}</td></tr>
<tr class="row-bad"><td>1,020 skills, Claude Code</td><td><code>seo-audit</code></td><td>Sonnet: {SEO("sonnet", "crowd1000")}</td></tr>
<tr class="row-bad"><td>1,020 skills, Codex</td><td>nothing</td><td>GPT-6 Astra: {SEO("gpt", "crowd1000")}</td></tr>
</tbody></table></div>"""
# The listing budget raised to its limit (e1_fullbudget_*.jsonl: 120 requests at 1,020 skills per model; captures in listing/)
def _fb(m):
    rs = [json.loads(l) for l in open(os.path.join(B, "..", f"e1_fullbudget_{m}.jsonl"))]; rs = [r for r in rs if not r.get("error")]
    return rs
FB = {m: _fb(m) for m in ("haiku", "sonnet", "fable", "gpt_sol")}
FBR = lambda m: f'{round(100 * sum(r["hit"] for r in FB[m]) / len(FB[m]))}%'
FB_CX_LISTED = ["animate", "caveman", "copywriting", "diagnosing-bugs", "docx", "frontend-design", "grill-me", "humanizer", "json-canvas"]   # targets Codex lists at 10,000 tokens (capture)
_fbl = [r for r in FB["gpt_sol"] if r["target"] in FB_CX_LISTED]; _fbn = [r for r in FB["gpt_sol"] if r["target"] not in FB_CX_LISTED]
FB_SOL_LISTED = f'{sum(r["hit"] for r in _fbl)} of {len(_fbl)}'; FB_SOL_UNLISTED = f'{sum(r["hit"] for r in _fbn)} of {len(_fbn)}'
_cost1 = lambda rs: sum(r["cost"] for r in rs) / len(rs)
def _basecost(m):
    rs = [json.loads(l) for l in open(os.path.join(B, "..", f"{m}.jsonl"))]; rs = [r for r in rs if r["cond"] == "crowd1000" and r.get("cost")]
    return _cost1(rs)
FB_CX_LAST = "maxia"   # last installed skill in the captured listing at the maximum budget
FB_COST = {m: (_basecost(m), _cost1(FB[m])) for m in ("sonnet", "fable")}
_fbrow = lambda m: f'<td class="n">{E1R(m, "crowd1000")}% → <b>{FBR(m)}</b></td>'
T_BUDGET = f"""<div class="wrap"><table>
<thead><tr><th></th><th>Claude Code</th><th>Codex</th></tr></thead><tbody>
<tr><td>Default budget for the skill listing</td><td>1% of the context window</td><td>2% of the context window</td></tr>
<tr><td>Setting that raises it</td><td><code>skillListingBudgetFraction</code> in settings, or the <code>SLASH_COMMAND_TOOL_CHAR_BUDGET</code> environment variable</td><td><code>skills.max_context_tokens</code> in <code>config.toml</code></td></tr>
<tr><td>How far it goes</td><td>up to the whole context window</td><td>10,000 tokens at most</td></tr>
<tr><td>Listing at 1,020 skills, default</td><td>{_n(LS[("claude", "crowd1000")]["entries"])} names, {LS[("claude", "crowd1000")]["entries_with_description"]} with a description</td><td>{CX1K["entries"]} names, no descriptions; {CX1K["targets_listed"]} of the 20 targets</td></tr>
<tr class="row-good"><td>Listing at 1,020 skills, setting raised</td><td>all {_n(LS[("claude", "crowd1000")]["entries"])} with a description, about 184,000 characters in every request</td><td>618 names, still no descriptions; 9 of the 20 targets</td></tr>
<tr class="row-warn"><td>Designated skill picked at 1,020 skills, default → raised</td><td>Haiku {E1R("haiku", "crowd1000")}% → <b>{FBR("haiku")}</b><br>Sonnet {E1R("sonnet", "crowd1000")}% → <b>{FBR("sonnet")}</b><br>Fable {E1R("fable", "crowd1000")}% → <b>{FBR("fable")}</b></td><td>GPT-6 Sol {E1R("gpt_sol", "crowd1000")}% → <b>{FBR("gpt_sol")}</b></td></tr>
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
<tr><td>Selection of the designated skill fell as more skills were installed, starting at 20</td><td>Measured; 95% CIs exclude zero from 20 skills on for Haiku and Sonnet, at 1,020 for all five models; one sample of extra skills</td><td>Enable fewer skills per project</td></tr>
<tr><td>Past a few hundred skills, the listing was cut: Codex dropped skills alphabetically, Claude Code kept mostly names</td><td>Captured after the study with the same versions; no model called</td><td>Check what the model can see before rewriting descriptions</td></tr>
<tr><td>Single-step MCP tool selection held from 220 to 791 tools, in Claude Code and in Codex</td><td>Measured: no change, paired 95% CIs within ±{FLAT_CI} points; search not isolated</td><td>Prefer search over a full listing where you can</td></tr>
</table></div>"""
T_COST = f"""<div class="wrap"><table>
<tr><th>Item</th><th class="n">Runs</th><th class="n">Cost</th></tr>
<tr><td>GPT-6 Astra, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">$119.13</td></tr>
<tr><td>GPT-6 Astra, partial MCP run with my first setup, not in these results (OpenAI API)</td><td class="n">170</td><td class="n">$52.60</td></tr>
<tr><td>GPT-6 Sol, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">${SOL_E1:.2f}</td></tr>
<tr><td>GPT-6 Sol, MCP experiment (OpenAI API)</td><td class="n">480</td><td class="n">${SOL_E2:.2f}</td></tr>
<tr><td>GPT-6 Sol, first MCP run, discarded (OpenAI API)</td><td class="n">480</td><td class="n">${SOL_E2_FIRST:.2f}</td></tr>
<tr><td>GPT-6 Sol, 1,020 skills with the maximum listing budget (OpenAI API)</td><td class="n">120</td><td class="n">${SOL_FB:.2f}</td></tr>
<tr><td><b>Calculated API fees</b></td><td class="n">2,210</td><td class="n"><b>${171.73 + SOL_E1 + SOL_E2 + SOL_E2_FIRST + SOL_FB:.2f}</b></td></tr>
<tr><td>Claude Haiku and Sonnet in Claude Code, the runs in these results (my Claude subscription; API list price for reference)</td><td class="n">{HS_RUNS:,}</td><td class="n">$0 extra (${HS_COST:.2f} list)</td></tr>
<tr><td>Claude Fable 5.2 in Claude Code (same subscription)</td><td class="n">{FABLE_RUNS:,}</td><td class="n">$0 extra (${FABLE_COST:.2f} list)</td></tr>
<tr><td>Haiku, Sonnet and Fable at 1,020 skills with the full listing budget (same subscription)</td><td class="n">360</td><td class="n">$0 extra (${sum(r["cost"] for m in ("haiku", "sonnet", "fable") for r in FB[m]):.2f} list)</td></tr>
<tr><td>Claude Code runs I discarded: two earlier rounds of MCP and mixed runs, a rerun I stopped, and 18 skill runs I repeated (same subscription)</td><td class="n">{3233 + 1920:,}</td><td class="n">$0 extra (${149.64 + 177.90:.2f} list)</td></tr>
</table></div>"""
_sk = [E3P[(m, f"skill: single-skill baseline -> {st}")]["diff"] for m in CM for st in ("mixed_smaller", "mixed_larger")]
_tl = [E3P[(m, f"tool nonbrowser: mcp_alone -> {st}")]["diff"] for m in CM for st in ("mixed_smaller", "mixed_larger")]
SK_LOSS, TOOL_LOSS = RNGP(_sk), RNGP(_tl)
_mx = lambda m, se: " → ".join(P(EC[(m, se, st)]["rate"]) + "%" for st in ("single component", "mixed_smaller", "mixed_larger"))
MIXLINE = ("From the component alone to the smaller and the larger mix, skill requests went " + " and ".join(f"{_mx(m, 'skill requests')} for {MNAME[m]}" for m in CM)
           + ", and single-step tool requests " + " and ".join(f"{_mx(m, 'single-step tool requests')} for {MNAME[m]}" for m in CM) + ".")
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
<p class="dek" data-desc="I installed up to 1,000 skills and ~800 MCP tools in Claude Code and Codex. The skill each request was written for went from being picked {RNG(E1[(m, "alone")]["rate"] for m in ALLM)}% of the time to {RNG(E1[(m, "crowd1000")]["rate"] for m in ALLM)}%, depending on the model. In Claude Code, single-step MCP tool selection fell much less, from {RNG(E2[(m, "mcp_alone")]["nonbrowser_rate"] for m in C3)}% to {RNG(E2[(m, "mcp_crowdall")]["nonbrowser_rate"] for m in C3)}%, and held steady from ~200 to ~800 tools.">I installed up to 1,000 skills and ~800 MCP tools in Claude Code and Codex, and measured how often the agent still picked the one each request was written for.</p>

<div class="repobox">
<div><span class="lbl">The experiment, data and analysis:</span> {A(L["repo"], "github.com/galinaalperovich/closet-full-of-skills")}. Every request, every result record and every script, so you can reproduce all the numbers for free.</div>
<div><span class="lbl">A skill to check your own agent:</span> <span class="soon">coming soon</span></div>
</div>

<h2>Summary</h2>
<p class="tldr">Installing a skill doesn’t mean your agent will use it. I wanted to see how bad it gets, so I sent 120 natural requests to Claude Code and Codex, each written for one skill, and kept installing more skills around it:</p>
<ol>
<li><b>Skills fade.</b> Alone, the skill was picked in {RNG(E1[(m, "alone")]["rate"] for m in ALLM)}% of runs. Among 1,000 others, in {RNG(E1[(m, "crowd1000")]["rate"] for m in ALLM if m != "fable")}%, and in {E1R("fable", "crowd1000")}% for the strongest model. {SEE("result-1", "Result 1")}</li>
<li><b>For smaller models, twenty is enough.</b> This one surprised me: among just 20 unrelated skills, Haiku fell from {E1R("haiku", "alone")}% to {E1R("haiku", "pack20")}% and Sonnet from {E1R("sonnet", "alone")}% to {E1R("sonnet", "pack20")}%. {SEE("result-1", "Result 1")}</li>
<li><b>Past a few hundred skills, the harness quietly cuts the listing.</b> Of 1,020 skills, Codex listed {CX1K["entries"]}, alphabetically. Claude Code kept every name but only {LS[("claude", "crowd1000")]["entries_with_description"]} descriptions. I found a setting that raises the cap, but it won back only about ten points. {SEE("result-2", "Result 2")}</li>
<li><b>A stronger model buys room, not immunity.</b> Fable 5.2 held at {E1R("fable", "crowd200")}% up to ~220 skills and fell only after the listing was cut. For a strong model, the harness explains more of the loss than the model’s own confusion. {SEE("result-2", "Result 2")}</li>
<li><b>Most misses are no skill at all, not a wrong one.</b> The agent uses built-in tools or just writes the answer itself, and nothing tells you. {SEE("misses", "What the agent did instead")}</li>
<li><b>MCP tools held up better.</b> {SUM_MCP} {SEE("result-3", "Result 3")}</li>
</ol>
<p>The experiment has <a href="#limitations-of-the-experiment">its limits</a>. At the end I share <a href="#what-you-can-do-about-it">a few tricks for dealing with this problem</a>.</p>
<!--toc-->
<h2>Problem statement</h2>

<p>Agent skills became <b>the new npm</b>. A skill is a folder with a <code>SKILL.md</code> file: a name, a short description, and instructions the agent reads only when it needs them. The biggest collection I found, {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, has over 3,000, and its README invites you to install them all. One GitHub MCP server alone exposes 149 tools.</p>

<p>Here is what made me curious. The agent chooses a skill from its description, and the descriptions in that one collection add up to about 129K tokens. <em>The Great Gatsby</em> is about 72K. No harness sends <b>two Gatsbys</b> with every request: Claude Code and Codex both cap the listing. So what happens to the skills that do not fit, and to the ones that do?</p>

<p>It is a harder version of the <b>needle-in-a-haystack test</b>. The {A(L["niah"], "original")} hides one fact in a long document and asks for it. Here the needle is one skill among hundreds, and nobody asks for it: the model has to notice that the request needs it. A few benchmarks study parts of this ({A(L["metatool"], "MetaTool")}, {A(L["longfunc"], "LongFuncEval")}, {A(L["wild"], "Liu et al.")}), but none shows the full picture of a real harness. What is new in my study:</p>
<ul>
<li><b>Real harnesses, not a bare model.</b> What the harness does before the model sees anything turned out to matter most.</li>
<li><b>Real skills and tools:</b> 20 popular skills and 20 published MCP tools, among up to 1,000 real skills and 791 real tool definitions.</li>
<li><b>Requests that never name the skill</b>, sent unchanged to every setup.</li>
<li><b>Skills and MCP tools side by side, then mixed.</b></li>
<li><b>What the model actually received:</b> I captured the listing each harness sent.</li>
</ul>

<h2>Why it matters</h2>
<p>I used to think the worst case was the agent picking a wrong skill. The worst case is quieter than that:</p>
<ul>
<li><b>A skipped skill fails silently.</b> The agent answers anyway. Ask for Apple’s stock price without the finance tool being called, and you may get <b>a confident number from the model’s memory</b>.</li>
<li><b>One skipped skill can skip a whole recipe:</b> run the linter, then the tests, then open the pull request.</li>
<li><b>If you have rules to follow, it gets worse.</b> “We installed the skill and hoped for the best” is not an audit trail.</li>
<li><b>It takes an everyday setup, not an extreme one.</b> {A(L["i81081"], "One Claude Code issue")} reports 27 of 36 project skills reaching the model with only a name, and {A(L["uber"], "Uber")} has more than 5,000 skills in its internal marketplace.</li>
</ul>

<h2>How an agent picks a skill or a tool</h2>
<p>A <b>skill</b> is a folder of instructions that teaches the agent <em>how</em> to do something. An <b>MCP tool</b> is a function on a server that <em>does</em> one thing, such as creating an issue.</p>
<p><b>Loading a skill is itself a tool call.</b> Claude Code calls its <code>Skill</code> tool; Codex reads the file with a shell command such as <code>cat .agents/skills/pdf/SKILL.md</code>. That first call is what I count as “selected” (for Codex, a command naming the skill’s <code>SKILL.md</code>; I did not check that the read succeeded).</p>
<p>The two reach the model differently. Skills sit in one listing of names and descriptions, sent with every request. MCP tools are listed by name only, and the model fetches a full definition on demand.</p>
{fig_("fig_how", "How a request reaches a skill or a tool, with MCP tools handled the way Claude Code does it.")}
<p>Between installing a skill and the skill doing its job there are four stages:</p>
<ol>
<li><b>Installed.</b> The skill folder or MCP server is on disk and enabled.</li>
<li><b>Listed.</b> The harness fits names and descriptions into a budget: {A(L["cc_skills"], "1% of the context window in Claude Code")}, {A(L["codex_skills"], "2% in Codex")}. <b>Checked afterwards.</b></li>
<li class="hl"><b>Selected.</b> The model loads the skill or calls the tool. <b>Measured here.</b></li>
<li><b>Used.</b> The instructions are followed and the task gets done. Not measured.</li>
</ol>

<h2>The experiment setup</h2>
{fig_("fig_setup", "The same request in four setups, from the target alone to 1,000 other skills (or 791 tools).")}
<p>I needed two things: targets, and a crowd to hide them in.</p>
<ul>
<li><b>Targets:</b> 20 well-known skills ({A(L["anth_skills"], "Anthropic’s")} pdf, xlsx, pptx and docx, {A(L["mattpocock"], "Matt Pocock’s")} tdd and grill-me, and others; full list in <a href="#appendix-a">Appendix A</a>) and 20 everyday MCP tools, such as creating a GitHub issue or getting a stock price.</li>
<li><b>The crowd:</b> 1,000 other real skills, drawn at random from {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, and 771 other real tool definitions, making 791 tools from 73 servers ({A(L["ghmcp"], "GitHub")}, {A(L["cdt"], "Chrome DevTools")}, {A(L["pwmcp"], "Playwright")}, and 70 from {A(L["livemcp_gh"], "LiveMCPBench")}).</li>
</ul>
<p>For each target an LLM wrote six realistic requests with no explicit invocation: no <code>/pdf</code>, no “use the pdf skill” ({A(L["r_prompts"], "all requests")}).</p>
{tab_("Example requests. Every target had six like these.", T_EXAMPLES)}
<p>Each request ran in four setups:</p>
<ol>
<li><b>Alone:</b> only the target, plus what the harness ships (23 built-in skills in Claude Code, 5 in Codex).</li>
<li><b>20:</b> all 20 targets together.</li>
<li><b>~220:</b> the 20 plus 200 from the crowd.</li>
<li><b>All:</b> the 20 plus the whole crowd: 1,000 skills, or 771 tools.</li>
</ol>
<p>Five configurations ran them: Claude Haiku, Sonnet and Fable 5.2 in Claude Code (v2.1.328), and GPT-6 Astra and GPT-6 Sol (medium reasoning) in Codex CLI (v0.160.0). Fable and Astra are the top models of the two families; Sol is Astra’s sibling at a fifth of the price. Each configuration is a model plus a harness, so a difference between Codex and Claude Code may be either, but a difference between two models inside one harness is the model.</p>
<p>Four details matter for reading the numbers:</p>
<ol>
<li><b>Fake skill bodies.</b> Each skill keeps its real name and description, but its instructions are one line: “reply with one short sentence”. MCP tools keep their real definitions and answer every call with “Done.”</li>
<li><b>Fresh, empty folders.</b> Every setup sees the same thing, and Claude Code’s per-folder memory cannot carry notes from one run to the next. I learned about that memory the hard way, and reran every affected run with a little less enthusiasm than the first time.</li>
<li><b>Short observation window.</b> Claude Code was capped at 3 turns for skills and 8 for MCP tools. Codex has no turn cap.</li>
<li><b>Scoring.</b> A hit is exactly the designated skill, or the designated tool or an equivalent one on another server. Other picks were rated later by a separate Claude session ({A(L["r_judge"], "prompt and rules")}).</li>
</ol>
<p><b>How to read the numbers.</b> Each configuration got 120 skill requests and 120 tool requests, 90 of them for tools that need a single call. Brackets are 95% confidence intervals from resampling requests. They do not cover the random draw of extra skills or the request wording; details are in the {A(L["r_meth"], "methodology")}.</p>

<h2 id="result-1">Result 1: Skills fade</h2>
{tab_("Share of requests where the agent picked the designated skill, with 95% CIs. Haiku, Sonnet and Fable ran in Claude Code; GPT-6 Astra and GPT-6 Sol in Codex.", T_SKILLS)}
{fig_("fig_skills", "The same numbers as a chart. GPT-6 Sol is the dashed line, almost on top of GPT-6 Astra. Sonnet: 360 runs per point; the others: 120. The x axis is not to scale.")}
<p><b>For Haiku and Sonnet, the decline is already there at 20.</b> These are 20 skills about different things: PDFs, SEO, TDD, animation. Still, Haiku fell from {P(E1[("haiku", "alone")]["rate"])}% to {P(E1[("haiku", "pack20")]["rate"])}% and Sonnet from {P(E1[("sonnet", "alone")]["rate"])}% to {P(E1[("sonnet", "pack20")]["rate"])}%. I expected trouble at a thousand skills, not at twenty, but <b>twenty is enough</b>.</p>
<p><b>A stronger model holds longer.</b> Honestly, I hoped a stronger model would simply fix it, and for a while it did. Fable stayed at {E1R("fable", "alone")}%, {E1R("fable", "pack20")}% and {E1R("fable", "crowd200")}% up to ~220 skills, and only then gave way: {E1R("fable", "crowd1000")}% at 1,020. Still more than one request in four missed.</p>
<p><b>In Codex, the model made no difference.</b> I thought the cheaper model would do worse. It drew the same curve as GPT-6 Astra: {LIST(E1R("gpt_sol", st) + "%" for st in ("alone", "pack20", "crowd200", "crowd1000"))}, next to {LIST(E1R("gpt", st) + "%" for st in ("alone", "pack20", "crowd200", "crowd1000"))}. Result 2 shows why.</p>

<h3 id="misses">When the designated skill was not picked, what did the agent do instead?</h3>
{fig_("fig_misses", "Outcomes with 1,020 skills. Hatched: the run hit Claude Code’s 3-turn limit. “No skill detected”: no <code>Skill</code> call in Claude Code; in Codex, no command naming a <code>SKILL.md</code> (reads of Codex’s own skills under <code>skills/.system/</code> are not detected).")}
<p>I went in expecting wrong skills. What I found is that most misses were not a wrong skill: they were runs where <b>no skill was detected at all</b>: the agent used its built-in tools or simply answered.</p>
<ul>
<li><b>Haiku:</b> more than half of its no-skill runs (53 of 97) hit the 3-turn limit, so a longer window might have caught later picks.</li>
<li><b>Sonnet:</b> two thirds of its misses (160 of 239) ended normally, with no skill.</li>
<li><b>Fable:</b> {MF["none"]} of its {MF["n"]} misses had no skill, and {MF["alt"]} picked a different one. {MF["eq"]} of those were rated equivalent, which would make its rate {round(100 * (120 - MF["n"] + MF["eq"]) / 120)}%, not {E1R("fable", "crowd1000")}%.</li>
<li><b>GPT-6 Astra and GPT-6 Sol:</b> about a quarter of their misses picked a different skill. Counting the ones rated equivalent ({MA["eq"]} and {MS["eq"]}) would make their rates {round(100 * (120 - MA["n"] + MA["eq"]) / 120)}% and {round(100 * (120 - MS["n"] + MS["eq"]) / 120)}%, not {E1R("gpt", "crowd1000")}% and {E1R("gpt_sol", "crowd1000")}%.</li>
</ul>

<h2 id="result-2">Result 2: What the model actually saw</h2>
<p>At this point I had a curve and no explanation. Was the listing cut, or did the model choose badly from a full one? I honestly did not know, so I pointed every skills setup at a stand-in server that records what each harness sends, with no model called ({A(L["r_listing"], "scripts and results")}).</p>
{tab_("What the skill listing contained in each setup. Haiku, Sonnet and Fable received the same listing.", T_LISTING)}
<p><b>At 20 skills, nothing was cut</b>, so the drop there is the model’s own choice. Everything after that is a different story: <b>the model was choosing from a listing that the harness had already cut.</b></p>

<h3>One skill, three listings</h3>
<p>This is the example that made it click for me. Take <code>seo-audit</code> and its six requests, such as “Audit the SEO of my site.”</p>
{tab_("The same skill, the same requests. Only the listing changed.", T_SEEN)}
<p>In Claude Code the skill became a bare name among 16 other names with “seo” in them; in Codex it was never offered.</p>

<h3>Codex: first shorter, then gone</h3>
<ul>
<li><b>At ~220 skills</b> Codex keeps every skill but cuts each description to about {CX200_CHARS} characters. GPT-6 Astra still picked the right skill in {P(E1[("gpt", "crowd200")]["rate"])}% of requests: a name and five words were nearly enough.</li>
<li><b>At 1,020 skills</b> it listed only {CX1K["entries"]} entries, alphabetically up to “developer-listening”, with no descriptions. Of the 20 targets, only {", ".join(f"<code>{t}</code>" for t in CX1K_NAMES[:-1])} and <code>{CX1K_NAMES[-1]}</code> made it in.</li>
</ul>
<p>Those three account for {GPT1K_LISTED_HITS} of GPT-6 Astra’s {GPT1K_HITS} hits at 1,020 skills and {SOL1K_LISTED_HITS} of GPT-6 Sol’s {SOL1K_HITS}. So <b>the Codex cliff is the alphabet</b>, not a model choosing badly. I did not believe it until I read the list myself. If your skill is called <code>zebra-something</code>, I have bad news.</p>

<h3>Claude Code: every name, few descriptions</h3>
<p>Claude Code never drops a skill; it drops descriptions. The listing stops growing at about {CC_CAP:,} characters, already at ~220 skills. At 1,020, only {LS[("claude", "crowd1000")]["entries_with_description"]} of {_n(LS[("claude", "crowd1000")]["entries"])} entries had a description, so the model mostly chooses from <b>bare names</b>. How much a model makes of a bare name is where the three differ: {E1R("haiku", "crowd1000")}% for Haiku, {E1R("sonnet", "crowd1000")}% for Sonnet, {E1R("fable", "crowd1000")}% for Fable.</p>
<p><b>Which descriptions survive? The ones you have used.</b> I noticed that the few surviving descriptions were skills I had already used, and it was not a coincidence. Claude Code records how often and how recently you used each skill, across all your projects:</p>
<ul>
<li><b>A clean record, 1,020 skills:</b> {("none" if LS[("claude-fresh", "crowd1000")]["targets_with_description"] == "0" else LS[("claude-fresh", "crowd1000")]["targets_with_description"])} of the 20 targets had a description.</li>
<li><b>A record seeded with uses of <code>seo-audit</code> and <code>pdf</code>:</b> exactly those two got theirs back.</li>
</ul>
<p>A twist, and this one is on me: my own runs fed that record, so I cannot say which targets had a description in each run. <b>A new skill in a big collection starts life as a bare name.</b></p>

<h3 id="raise-the-cap">Can you just raise the cap?</h3>
<p>Yes, both harnesses have a setting, and I nearly missed it. I was sure this would fix everything, so I ran the 1,020-skill setup again with the budget at its limit:</p>
{tab_("The listing budget, the setting that raises it, and what raising it did at 1,020 skills (120 requests per model; listings captured with no model called).", T_BUDGET)}
<ul>
<li><b>In Claude Code, the full listing gave back about ten points.</b> Not what I hoped for. Sonnet went from {E1R("sonnet", "crowd1000")}% to {FBR("sonnet")} and Fable from {E1R("fable", "crowd1000")}% to {FBR("fable")}, still far from their {E1R("sonnet", "alone")}% and {E1R("fable", "alone")}% with the skill alone. Haiku got worse. So the cut explains part of the loss, and <b>a thousand full descriptions are their own kind of haystack</b>.</li>
<li><b>It is not free.</b> The descriptions travel with every request: at list prices a Sonnet run went from ${FB_COST["sonnet"][0]:.2f} to ${FB_COST["sonnet"][1]:.2f} and a Fable run from ${FB_COST["fable"][0]:.2f} to ${FB_COST["fable"][1]:.2f}.</li>
<li><b>In Codex, the maximum only moves the cliff.</b> The list runs about twice as far into the alphabet, to “{FB_CX_LAST}”, so 9 targets are offered instead of {CX1K["targets_listed"]}. GPT-6 Sol picked the right skill in {FB_SOL_LISTED} requests for those nine, and in {FB_SOL_UNLISTED} for the other eleven.</li>
</ul>
<p>One run per request, so read these as directions, not precise sizes.</p>

<h3>What this means for your skills</h3>
<ul>
<li><b>The name does most of the work.</b> In a big collection it is often all the model gets, so name a skill with the words people will actually type.</li>
<li><b>A new skill starts at the back of the queue.</b> In Claude Code, used skills keep their descriptions. Calling a new one by name is the obvious way in.</li>
<li><b>In Codex, past about {round(int(CX1K["entries"]), -1)} skills, the end of the alphabet does not exist</b> (about 620 at the maximum budget). Beyond that, the only fix I know is fewer skills.</li>
</ul>

<p>Which of the 20 skills survived, and why, is in <a href="#appendix-e">Appendix E</a>.</p>

<h2 id="result-3">Result 3: MCP tools hold up better</h2>
<p>Then I repeated the design with 20 everyday MCP tools, each served from its real published definition. I expected the same collapse.</p>
<p><b>To my surprise, the tools held up, in both harnesses.</b> With the target tool alone, the agent picked it for {LIST(NB(m, "mcp_alone") + "% (" + MNAME[m] + ")" for m in T4)} of the single-step requests. With all 791 tools installed, for {LIST(NB(m, "mcp_crowdall") + "%" for m in T4)}. Skills, remember, fell to {LIST(E1R(m, "crowd1000") + "%" for m in T4)}.</p>
{fig_("fig_fade", "Skills (solid) against the 15 single-step MCP tool targets (dashed), with 95% CIs. Haiku, Sonnet and Fable ran in Claude Code, GPT-6 Sol in Codex. Different tasks and scoring rules; the x axis is not to scale.")}
<p>What loss there was came at the first step, from one tool to twenty. After that the curve is flat: 571 more tools changed <b>nothing measurable</b>.</p>
{tab_("Share of single-step tool requests where the agent called the designated tool (or an equivalent one), with 95% CIs.", T_MCP)}
<p><b>Neither harness lists all the tools.</b> Both list MCP tools by name and have the model look a definition up (<code>ToolSearch</code> in Claude Code). That is the main difference from skills, where everything hangs on one listing.</p>
<p class="note">Five of the 20 tools need a first step, such as opening a page before a screenshot, and a tool for that exists only in the two larger setups. There the agent took both steps in {round(100 * BRW_ALL[0] / BRW_ALL[1])}% of requests ({BRW_ALL[0]} of {BRW_ALL[1]}). I keep these five out of the curve.</p>

<h2>Result 4: Skills and tools together</h2>
<p>Real setups have both, and I wondered whether mixing changes the picture. So I mixed them: 400 skills and all 791 tools in one setup, tested with Haiku and Sonnet.</p>
{fig_("fig_mix", "Sonnet in Claude Code: the component installed alone, and in the mix of 400 skills and 791 tools. Tool requests: the 15 single-step targets. Whiskers: 95% CI.")}
<p><b>It does not: the same pattern.</b> In the mix, Sonnet picked the designated skill in {P(EC[("sonnet", "skill requests", "mixed_larger")]["rate"])}% of requests and the designated tool in {P(EC[("sonnet", "single-step tool requests", "mixed_larger")]["rate"])}%. Haiku: {P(EC[("haiku", "skill requests", "mixed_larger")]["rate"])}% and {P(EC[("haiku", "single-step tool requests", "mixed_larger")]["rate"])}%. A smaller mix of 100 skills and 437 tools was already enough: {P(EC[("sonnet", "skill requests", "mixed_smaller")]["rate"])}% and {P(EC[("sonnet", "single-step tool requests", "mixed_smaller")]["rate"])}% for Sonnet.</p>
<p>When the agent skipped the skill, it mostly <b>used only built-in tools</b>: “Merge invoice-jan.pdf and invoice-feb.pdf” became two <code>Glob</code> searches in the empty folder and “I couldn’t find the files”.</p>

<h2>Why do skills fade while tools hold up?</h2>
{fig_("fig_forest", "Change from the target alone, in percentage points, with 95% CIs, model by model. Filled dots: skills, 120 requests. Hollow dots: single-step MCP tools, 90 requests. GPT-6 Astra ran the skills experiment only.")}
<p>I can’t open the models and look inside, but three explanations fit what I saw. The first is measured; the other two are my guesses:</p>
<ol>
<li><b>Skills lose their descriptions; tools can be searched.</b> A skill listing is like <b>a restaurant menu printed on one page</b>: the more dishes, the smaller the print. Tools are more like asking the waiter: the model searches and gets the full definition back. Retrieving a few tools instead of listing them all raised selection from 13.6% to 43.1% in {A(L["ragmcp"], "RAG-MCP")}.</li>
<li><b>Tools match the words of a request; skills match its meaning.</b> A tool name is a verb the request nearly repeats (<code>create_issue</code>). A skill describes a workflow in broad words its neighbours share ({A(L["nolima"], "NoLiMa")}, {A(L["rot"], "Context Rot")}).</li>
<li><b>An action needs a tool; a goal does not.</b> “Open an issue” cannot be done without the GitHub tool. “Rewrite the copy on our homepage” can ({A(L["metatool"], "MetaTool")}).</li>
</ol>
<p>A toy calculation of the dilution idea is in <a href="#appendix-c">Appendix C</a>.</p>

<h2>What you can do about it</h2>
<h3>[Trick #1] Check what is actually exposed</h3>
<p>In Claude Code, <code>/context</code> shows the size of your skill listing and {A(L["cc_skills"], "<code>/doctor</code> tells you whether descriptions are being dropped")}. Codex prints a warning when it goes over its budget. Since November 2026, {A(L["skills_mcp"], "MCP servers can ship skills too")}, so your listing can grow without you installing anything. This is the first thing I would check.</p>
<h3>[Trick #2] Raise the listing budget, if you can afford it</h3>
<ul>
<li><b>Claude Code:</b> <code>skillListingBudgetFraction</code> in your settings (default <code>0.01</code>), or the environment variable <code>SLASH_COMMAND_TOOL_CHAR_BUDGET</code> in characters.</li>
<li><b>Codex:</b> <code>skills.max_context_tokens</code> in <code>config.toml</code>, up to 10,000.</li>
</ul>
<p>It helped less than I hoped (<a href="#raise-the-cap">Result 2</a>), and every request carries the longer listing. It makes sense when you are a little over the budget, not ten times over.</p>
<h3>[Trick #3] Enable less, per project</h3>
<p>If I had to pick one trick, this is it. Enable plugins per project, turn off unused skills with <code>/skills</code>, and if you only need <code>pdf</code> from a 3,000-skill collection, install <code>pdf</code>.</p>
<h3 id="trick-search">[Trick #4] Try other ways to discover and invoke (untested here)</h3>
<ul>
<li><b>Invoke required skills by name</b> (<code>/skill-name</code>) instead of hoping for a match.</li>
<li><b>Give a skill a trigger nobody else has.</b> In my sample, skills with concrete nouns and file types held up.</li>
<li><b>Use a router skill or a hook.</b> {A(L["spence"], "A hook that makes Claude evaluate skills before answering")} reached 84% activation in Scott Spence’s test, against 20% for a keyword hook. {A(L["uber"], "Uber")} keeps about 100 skills on by default and uses a <code>find-skills</code> skill to search the other 5,000.</li>
<li><b>Search instead of listing.</b> In your own agent, use the Claude API’s {A(L["toolsearch"], "tool search tool")}, or embed the descriptions and retrieve the closest few.</li>
</ul>

<h2>Check your own agent</h2>
<p>I am packaging this check as a skill you can run on your own setup (<span class="soon">coming soon</span> on {A(L["repo"], "GitHub")}). Yes, a skill that checks whether your skills get picked. I see the irony too. Let’s hope your harness picks it! Until then, the {A(L["repo"] + "#check-your-own-agent", "README")} has a manual version in two commands.</p>

<h2>Limitations of the experiment</h2>
<p>This is one person’s experiment, not a benchmark. Here is what it cannot tell you:</p>
<ul>
<li><b>Selection, not quality.</b> A run without the skill can still produce a fine answer.</li>
<li><b>Listing captured afterwards</b>, so the exact listing of each run is unknown.</li>
<li><b>Few samples.</b> One random draw of extra skills and six LLM-written requests per target.</li>
<li><b>Configurations, not models.</b> Models can be compared inside one harness, not across the two.</li>
<li><b>The tool runs are a second attempt.</b> My first test server ended a run after its first call, and my first Codex setup blocked the calls. I repeated all tool runs with both fixed.</li>
<li><b>Thinner data for Fable and Codex.</b> One run per request, no mixed setups, and GPT-6 Astra ran the skills experiment only.</li>
</ul>
<p>The {A(L["r_meth"], "full methodology")}, all data and all scripts are in {A(L["repo"], "the GitHub repo")}.</p>

<h2>What’s next</h2>
<ol>
<li><b>Validation.</b> Real files in the folders, 10 turns instead of 3, and a fixed usage record so every run sees the same listing.</li>
<li><b>Search for skills.</b> Does a <code>ToolSearch</code>-style step help skills the way it seems to help tools?</li>
<li><b>More catalogs and controls.</b> Other draws of extra skills, other harnesses (Cursor, Gemini CLI), and the quality of the final answer.</li>
</ol>
<p>The full plan is in {A(L["r_follow"], "the follow-up protocol")}. {A(L["repo"], "The repo")} is open, and reruns on newer versions, other models or other harnesses are very welcome.</p>

<h2>Conclusion</h2>
<p>I started with a simple question: if I install a thousand skills, does my agent get more capable? Mostly, it gets a bigger closet. What changed my view is the gap between installing a capability and having it reliably picked when a request needs it. Before adding another big collection, I would check what the agent can actually see. I still install skills. I just stopped assuming they are there.</p>
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
<p>The GPT-6 figures are calculated from the token usage Codex reported, at OpenAI’s list prices ({A(L["price"], "Astra")}, {A(L["price_sol"], "Sol")}; Sol’s cache-write price is not listed, and I assumed the same ratio as Astra’s), and not reconciled against the invoice ({A(L["r_cost"], "per-batch breakdown")}). The Claude Code list prices leave out the tool runs that I stopped as soon as the designated tool was called, because a stopped run reports no cost.</p>
</details>

<details class="fold"><summary><h2 id="appendix-e">Appendix E: Which skills kept being selected</h2></summary>
{fig_("fig_dumbbell", "Sonnet: each skill alone (hollow dot) and among 1,020 others (filled dot), 18 runs each, grouped by where it ends up. Each dot rests on 6 requests, so a difference of a few runs is not a ranking.")}
<p><code>grill-me</code> went from 100% to 94%, <code>seo-audit</code> from 100% to <b>0%</b>. A skill held up if its description survived the cut (<code>grill-me</code>, <code>json-canvas</code>), or if its name says it all (<code>xlsx</code>, <code>pptx</code>, <code>docx</code>). It vanished if the model believes it can do the job without help: write copy, find a bug, audit SEO. Observations over 20 skills, not a test.</p>
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
<li>OpenAI model pages and pricing: {A(L["price"], "gpt-6-astra")} · {A(L["price_sol"], "gpt-6-sol")}</li>
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
