"""Assemble post v2: skills-mcp-post.html (figures from figs2.json, numbers from analysis/derived/v2)."""
import json, os, re
B = os.path.dirname(os.path.abspath(__file__))
fig = json.load(open(os.path.join(B, "figs2.json")))
t = open(os.path.join(B, "post.tpl.html")).read(); css = t[t.index("<style>") + 7:t.index("</style>")]
css = css.replace("--s-haiku:#f0a050; --s-sonnet:#8aa6ff; --s-gpt:#5fd39a", "--s-haiku:#cf7c2e; --s-sonnet:#6f8be6; --s-gpt:#2fa86f;"
  " --seg-target:#4fc1b9; --on-seg-target:#0d1f1e; --seg-eq:#2c7a75; --on-seg-eq:#e5e8eb; --seg-alt:#6b7681; --on-seg-alt:#ffffff; --seg-none:#3a434b; --on-seg-none:#e5e8eb; --seg-cap:#3a434b; --on-seg-cap:#e5e8eb;"
  " --seq1:#2a5a57; --seq2:#3f938c; --seq3:#7fd3cc; --band-hi:#22a094; --band-mid:#8b949e; --band-lo:#e4664c")
css = css.replace("--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;", "--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;"
  " --seg-target:#0f6e6a; --on-seg-target:#ffffff; --seg-eq:#7fbcb7; --on-seg-eq:#0d1f1e; --seg-alt:#8a949e; --on-seg-alt:#ffffff; --seg-none:#d9dee2; --on-seg-none:#1d2126; --seg-cap:#d9dee2; --on-seg-cap:#1d2126;"
  " --seq1:#a9d6d2; --seq2:#4f9e98; --seq3:#0b4f4c; --band-hi:#00897b; --band-mid:#8a949e; --band-lo:#c4432b;")
assert css.count("--seg-target") == 3, css.count("--seg-target")
css += """
.matrix td{min-width:13rem} .matrix td b{display:block;font-weight:600;margin-top:.35rem} .matrix td b:first-child{margin-top:0}
.note{font:.88rem/1.55 var(--sans);color:var(--muted)}
.callout{border-left:3px solid var(--accent);padding:.2rem 0 .2rem .9rem;font-style:italic}
.ci{color:var(--muted);font-size:.88em;white-space:nowrap}
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
fig_ = lambda k, cap: f'<figure>{fig[k]}<figcaption>{cap}</figcaption></figure>'

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

body = f"""
<article>
<div class="tags">AI Agents · Claude Code · Codex · Agent Skills · MCP</div>
<h1>A Closet Full of Skills and Nothing to Wear: The More Skills You Install, the Less Often Your Agent Picks the Right One (MCP Tools Hold Up Better)</h1>
<p class="dek">I installed up to 1,000 skills and 791 MCP tools in Claude Code and Codex. The right skill went from being picked 78–100% of the time to 10–34%. In Claude Code, single-step MCP tool selection fell less, from 86–92% to 77–78%, and held steady from 220 to 791 tools.</p>
<div class="byline">Galina Alperovich · November 2026</div>

<p class="tldr">tldr; Installing a skill does not guarantee that your agent will select it. I sent 120 natural requests to Claude Code and Codex, each written for one particular skill. With only that skill installed, it was selected in 78–100% of runs; with 1,000 more skills next to it, in 10–34%. On the same requests that is a drop of 59–90 percentage points, and every 95% CI excludes zero. MCP tools showed a different pattern: in Claude Code, selection across 15 single-step tool targets was 78% for Haiku and 77% for Sonnet with 220 tools installed, and unchanged with 791 (paired change 0 points, 95% CI about ±5). These are selection measurements in empty folders, with stubbed instructions and a short observation window. They do not measure how good the answer was.</p>

<p>Agent skills became the new npm. A skill is a folder with a <code>SKILL.md</code> file: a name, a short description, and instructions the agent reads only when it needs them. The biggest community collection I found, {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, has over 3,000 skills, and its README invites you to install all of them. MCP servers went the same way: one GitHub server alone exposes 149 tools.</p>

<p>Here is what made me curious. The agent chooses a skill from its description, and the descriptions in that one collection add up to about 129K tokens. <em>The Great Gatsby</em> is about 72K. No harness sends two Gatsbys with every request: Claude Code and Codex both cap the listing. So what happens to the skills that do not fit, and to the ones that do?</p>

<p>People run into this. {A(L["i81081"], "One Claude Code issue")} reports that 27 of 36 project skills reached the model with only a name, and {A(L["i11364"], "one user counted")} 67,300 tokens of tool definitions from seven MCP servers before the first message. More reports are in the references. What I did not find was the selection rate itself, measured for skills next to MCP tools.</p>

<h2>How an agent picks a skill or a tool</h2>
<p>It helps to see this as a pipeline, because I measured only one stage of it:</p>
<ol>
<li><b>Installed.</b> The skill folder or MCP server is on disk and enabled.</li>
<li><b>Listed.</b> The harness builds a listing of names and descriptions within a budget. Claude Code gives it 1% of the context window and drops descriptions when it overflows ({A(L["cc_skills"], "docs")}). Codex gives it 2%, at most 10,000 tokens, and shortens descriptions first ({A(L["codex_skills"], "docs")}).</li>
<li><b>Selected.</b> The model decides to load a skill or call a tool. <b>This is the stage I measured.</b></li>
<li><b>Loaded and used.</b> The full <code>SKILL.md</code> is read, the tool runs, the task gets done. Not measured.</li>
</ol>
{fig_("fig_how", "A request arrives together with a capped skill listing and the MCP tools. The model loads a skill, calls a tool, or uses only the harness’s built-in actions (search files, read, run a shell). Loading a skill is itself a tool call: it returns the skill’s instructions, and the work then happens in further tool calls.")}
<p>MCP tools differ at stage 2 in Claude Code: the model sees tool names and loads the full definitions on demand with a <code>ToolSearch</code> call. That is a harness feature. In your own agent built on a model API, every tool definition you pass is sent in full, and search is yours to implement (see <a href="#trick-search">[Trick #3]</a>).</p>
<p><b>Loading a skill is itself a tool call.</b> In Claude Code the model calls the <code>Skill</code> tool; in Codex it reads the file with a shell command such as <code>cat .agents/skills/pdf/SKILL.md</code>. That call returns the skill’s instructions, and the actual work happens in the tool calls that follow. So a skill is a tool call with an extra step in front, while an MCP tool does its work in the call itself (in Claude Code, often right after a <code>ToolSearch</code> call that loads its definition). The first call is what I count as “selected”; I did not check that the file was read successfully.</p>

<h2>The experiment</h2>
<p>I picked 20 well-known skills ({A(L["anth_skills"], "Anthropic’s")} pdf, xlsx, pptx and docx, {A(L["mattpocock"], "Matt Pocock’s")} tdd and grill-me, and others; the full list is in <a href="#appendix-a">Appendix A</a>) and 20 everyday MCP tools out of 791 real tool definitions from 73 servers ({A(L["ghmcp"], "GitHub")}, {A(L["cdt"], "Chrome DevTools")}, {A(L["pwmcp"], "Playwright")}, and 70 servers from {A(L["livemcp_gh"], "LiveMCPBench")}).</p>
<p>For each target I wrote six requests the way a person would ask, with no explicit invocation: no <code>/pdf</code>, no “use the pdf skill”. Some overlap with names is unavoidable: 63 of the 150 skill requests share a word with the skill’s name, such as “pdf” or “grill”. {A(L["r_prompts"], "All requests are in the repo.")}</p>
<div class="wrap"><table>
<tr><th>Target</th><th>Example requests</th></tr>
<tr><td><code>pdf</code> skill</td><td>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file.”</td></tr>
<tr><td><code>seo-audit</code> skill</td><td>“Why did our organic traffic drop last month?”</td></tr>
<tr><td><code>grill-me</code> skill</td><td>“Grill me on this plan before I start building.”</td></tr>
<tr><td><code>github.create_issue</code> tool</td><td>“Open an issue in acme/webapp saying the login button is broken on Safari.”</td></tr>
</table></div>
<p>Each request ran in four setups:</p>
<ul>
<li><b>Alone:</b> only the target is installed. “Alone” still includes what the harness ships: Claude Code reported 23 built-in skills in every setup, plus its built-in tools.</li>
<li><b>20:</b> all 20 targets together.</li>
<li><b>~220:</b> the 20 plus 200 others, drawn at random.</li>
<li><b>All:</b> the 20 plus 1,000 other skills, or all 771 other tools.</li>
</ul>
<p>The configurations: Claude Haiku and Claude Sonnet in Claude Code (v2.1.328), and GPT (gpt-6-astra, medium reasoning) in Codex CLI (v0.160.0). Differences between them belong to the whole configuration, not to the model alone.</p>
<p>Four details matter for reading the numbers:</p>
<ul>
<li><b>Stubs.</b> Every skill keeps its real name and description, but its instructions are one line: “reply with one short sentence”. MCP tools return a similar stub. Whatever happens <em>after</em> the first selection is not normal behaviour.</li>
<li><b>Empty folders.</b> Each run starts in a fresh folder with no files, so a request about <code>report.pdf</code> has no such file.</li>
<li><b>Observation window.</b> Claude Code was capped at 3 turns (4 with MCP). A Codex run is one user turn, which can contain several model and tool steps, with no cap. A selection later than the window is not seen.</li>
<li><b>Scoring.</b> A skill request counts only if the designated skill is selected. A tool request also counts an equivalent tool on another server. Afterwards, a separate Claude session rated every selected alternative, seeing only the request and the two descriptions. That is a retrospective rating by a model, not human validation ({A(L["r_judge"], "prompt and rules")}).</li>
</ul>
<p><b>How to read the numbers.</b></p>
<ul>
<li><b>Unit of analysis: the request.</b> Each configuration got 120 skill requests and 90 single-step tool requests. Sonnet ran every skill request three times; its repeats are averaged within the request, so each request counts once.</li>
<li><b>Intervals.</b> 95% confidence intervals (CIs) come from a request-cluster bootstrap (2,000 resamples, fixed seed). Where every run succeeded (GPT alone, 120 of 120), the bootstrap collapses to a point, so I use a Wilson score interval instead.</li>
<li><b>Changes are paired.</b> A change between two setups compares the same requests, in percentage points (pp), with a bootstrap CI for the mean paired difference.</li>
<li><b>Robustness.</b> A two-stage bootstrap that also resamples which skills were chosen gives wider CIs (in the {A(L["r_meth"], "methodology")}). Every skill drop from “alone” to 1,020 skills still excludes zero. For Haiku’s MCP tools, the two-stage CI from alone to 791 tools just includes it (−20 to +1 pp).</li>
<li><b>What the intervals do not cover:</b> the single random draw of extra skills, my choice of wording beyond these requests, and harness versions. The analysis is exploratory, with no correction for multiple comparisons.</li>
</ul>

<h2>Result 1: skills fade</h2>
<div class="wrap"><table>
<tr><th>Setup</th><th class="n">Skills</th><th class="n">Haiku</th><th class="n">Sonnet</th><th class="n">GPT (Codex)</th></tr>
<tr><td>Target skill alone</td><td class="n">1</td><td class="n">78% <span class="ci">[71–85]</span></td><td class="n">93% <span class="ci">[88–97]</span></td><td class="n">100% <span class="ci">[97–100]</span></td></tr>
<tr><td>20 skills together</td><td class="n">20</td><td class="n">48% <span class="ci">[38–57]</span></td><td class="n">76% <span class="ci">[68–82]</span></td><td class="n">99% <span class="ci">[98–100]</span></td></tr>
<tr><td>Plus 200 others</td><td class="n">220</td><td class="n">25% <span class="ci">[18–32]</span></td><td class="n">56% <span class="ci">[48–64]</span></td><td class="n">83% <span class="ci">[77–89]</span></td></tr>
<tr><td>Plus 1,000 others</td><td class="n">1,020</td><td class="n">16% <span class="ci">[9–22]</span></td><td class="n">34% <span class="ci">[26–42]</span></td><td class="n">10% <span class="ci">[5–16]</span></td></tr>
</table></div>
<p class="note">95% CIs in brackets: request-cluster bootstrap; Wilson score interval for GPT alone (120 of 120).</p>
{fig_("fig_skills", "Share of requests where the designated skill was selected within the observation window. Bars are 95% CIs from resampling requests, except GPT alone (120 of 120), which uses a Wilson score CI. Sonnet ran each request 3 times (360 runs per point); Haiku and GPT once (120). The x axis is not to scale.")}
<p><b>The decline is already there at 20.</b> These are 20 skills about different things: PDFs, SEO, TDD, animation. On the same requests, Haiku lost 31 pp (95% CI 22–40) and Sonnet 17 pp (11–24). For Haiku, 34% of requests got worse and 3% better (41 and 4 of 120); for Sonnet, 23% got worse and none better (27 of 120). You do not need 1,000 skills to see it. The 20 descriptions total about 7,700 characters, but Claude Code’s built-in skills and the listing format also count toward its budget, and I did not capture the listing the model received. So this setup does not separate competition between entries from truncation.</p>
<p><b>GPT holds, then drops:</b> 99% at 20 skills, 83% at 220 and 10% at 1,020, a paired drop of 90 pp from alone (95% CI 84–95). Codex reports cache-write tokens per run, summed over the model requests in that run. That total went 13.2K → 15.2K → 18.9K → 20.3K across the four setups, while the descriptions I installed grew by about 45K tokens. This fits Codex’s documented 10,000-token cap on the listing, but it is a weak inference: I did not see what the model saw.</p>
<p><b>A stronger model helped, but did not remove the decline.</b> Sonnet was ahead of Haiku at every size, and both fell.</p>

<h3>What happened when the target was not selected</h3>
{fig_("fig_misses", "Outcomes with 1,020 skills installed. “Equivalent alternative”: the rater judged the other skill a fine choice for that request. “Other alternative” combines alternatives rated related, inappropriate or unassessable. Hatched: the run hit Claude Code’s 3-turn limit with no skill selected.")}
<p>Most misses were not a clearly wrong skill. They were runs with no detected skill selection at all, which changes the debugging question from “why this wrong skill?” to “was a skill exposed and selected at all?” I did not keep the response text, so such a run may have completed the task with built-in tools, asked for the missing file, or stopped for another reason.</p>
<ul>
<li><b>Haiku:</b> 55% of its no-skill runs (53 of 97) hit the 3-turn limit. With a longer window, some of them might have selected the skill later.</li>
<li><b>Sonnet:</b> 67% of its misses (160 of 239) ended normally with no skill selected.</li>
<li><b>GPT:</b> 27% of its misses (29 of 108) selected a different skill, and the rater judged 11% of all its misses (12 of 108) equivalent. Counting those, GPT’s rate at 1,020 skills is 20% (95% CI 14–28%), not 10%.</li>
</ul>
<p>One request shows why that adjustment matters. “Interview me about my plan for the onboarding redesign” was written for <code>grill-me</code>. With 220 skills installed, all three configurations selected <code>interview-me</code> instead. Strict scoring counts three misses. The rater called the alternative equivalent, and I agree.</p>

<h3>Which skills kept being selected</h3>
{fig_("fig_dumbbell", "Sonnet. Each arrow runs from a skill installed alone (hollow dot) to the same skill among 1,020 others (filled dot), 18 runs each: 6 requests × 3 repetitions. Skills are grouped by where they end up. At this size a 95% Wilson CI is wide (14 of 18 is 78%, 95% CI 55–91%), so a difference of a run or two is noise.")}
<p>Two contrasting cases. <code>grill-me</code> went from 100% to 94% (18 and 17 of 18): nothing else in the crowd is named “grill”. <code>seo-audit</code> went from 100% to 0% (18 and 0 of 18; 95% CI for 0 of 18: 0–18%), next to 16 other skills mentioning “seo”. Skills with an unusual name or file type (<code>json-canvas</code>, <code>xlsx</code>) held up, and skills on a crowded topic (security, debugging, animation) did not. My design cannot show that distinctiveness is the cause.</p>

<h2>Result 2: MCP tools hold up better</h2>
<p>The same design with MCP tools: 20 target tools on their real servers, then 20 together, about 220, and all 791.</p>
<p><b>First, a measurement failure.</b> Five of the 20 targets are browser tools, and “take a screenshot of example.com” needs two steps: open the page, then take the screenshot. In the larger setups, agents opened the page first, my stub answered “reply with one short sentence”, and the run ended. The strict score for those five targets fell to 0–17% (0–5 of 30), while “called a capable browser server” stayed at 83–100% (25–30 of 30). Neither number says whether the screenshot would have happened. A sensible first step made a naive metric look worse.</p>
<p>After seeing this, I separated the 15 single-step targets. That is an exploratory subset chosen after the fact, not a preplanned benchmark.</p>
{fig_("fig_fade", "Claude Code only. Bars are 95% CIs from resampling requests. “All installed” means 1,020 skills or 791 tools. The two experiments use different tasks and scoring rules, and the x axis is not to scale.")}
<div class="wrap"><table>
<tr><th>Tools installed</th><th class="n">Haiku · 15</th><th class="n">Sonnet · 15</th><th class="n">Sonnet · all 20</th></tr>
<tr><td>Target alone</td><td class="n">86% <span class="ci">[78–92]</span></td><td class="n">92% <span class="ci">[87–97]</span></td><td class="n">85% <span class="ci">[79–91]</span></td></tr>
<tr><td>20</td><td class="n">79% <span class="ci">[70–87]</span></td><td class="n">81% <span class="ci">[73–89]</span></td><td class="n">66% <span class="ci">[57–74]</span></td></tr>
<tr><td>~220</td><td class="n">78% <span class="ci">[69–86]</span></td><td class="n">77% <span class="ci">[68–86]</span></td><td class="n">58% <span class="ci">[48–66]</span></td></tr>
<tr><td>791</td><td class="n">78% <span class="ci">[69–87]</span></td><td class="n">77% <span class="ci">[68–86]</span></td><td class="n">58% <span class="ci">[48–66]</span></td></tr>
</table></div>
<p class="note">“15”: the single-step targets. “All 20”: including the five browser targets. 95% CIs in brackets (request-cluster bootstrap).</p>
<p><b>The curve bends, then flattens.</b> Most of the loss came with the first 20 tools, which include near neighbours such as several GitHub tools: from alone, the paired change was −7 pp (95% CI −12 to −2) for Haiku and −11 pp (−18 to −6) for Sonnet at 20 tools, and −8 pp (−14 to −2) and −16 pp (−23 to −8) at 791. Between 220 and 791 installed tools (571 more), the aggregate rate did not move: 78% for Haiku and 77% for Sonnet, a paired change of 0 pp (95% CI −6 to +6 and −4 to +4). Individual requests still moved both ways: 3% got worse and 3% better for Haiku (3 and 3 of 90), 2% and 2% for Sonnet (2 and 2 of 90). So this is “no change observed”, not proof of no effect: an equivalence claim would need a margin set in advance and more requests.</p>
<p>Claude Code called <code>ToolSearch</code> in 81–95% of these runs (97–114 of 120 per setup). That is consistent with deferred discovery helping, but it is not a controlled test of retrieval.</p>
<p><b>GPT is only partly measured.</b> With the target tool alone, GPT selected it 91% of the time (82 of 90; 95% CI 84–97%). With 20 tools I have only 27% of the requests (24 of 90), because I paused the GPT runs over cost. On those same 24 requests, selection went from 100% to 92% (24 and 22 of 24), a paired change of −8 pp (95% CI −21 to 0). Comparing 91% with 92% would look like a small increase, and it is not one: the request mixes differ. I have no GPT data for the larger tool setups.</p>
<p><b>Both experiments on one scale.</b> The forest plot shows each configuration’s paired change from “alone”, with its 95% CI. The skill CIs move steadily left as the catalog grows; the tool CIs stay within about 25 points of zero.</p>
{fig_("fig_forest", "Paired change from the target alone, in percentage points, with 95% CIs (request-cluster bootstrap). Filled dots: skills, 120 requests per row. Hollow dots: the 15 single-step MCP tool targets, 90 requests per row. GPT with 20 tools covers only the 24 requests that were run.")}

<h2>Result 3: skills and tools together</h2>
<p>Real setups have both. I built two: a smaller one with 100 skills and 437 tools, and a larger one with 400 skills and all 791 tools, including servers that overlap with skills (<code>xlsx</code> next to an Excel server). Then I sent 150 skill requests (the 20 targets plus five skills from repos trending this month) and the tool requests.</p>
{fig_("fig_mix", "Claude Code. Share of requests where the designated component was selected. “Single component” is the target installed alone, with every request weighted equally. Tool requests are the 90 for the 15 single-step targets. Whiskers: 95% CI (request-cluster bootstrap).")}
<p>Skill requests lost 48–59 pp, and none of the four 95% CIs comes within 39 points of zero. Single-step tool requests lost 9–18 pp, with 95% CIs between −27 and −2. Read that gap with care:</p>
<ul>
<li><b>The scoring is not symmetric.</b> A skill request counts only the exact designated skill; a tool request also counts an equivalent tool. Counting the alternatives the rater judged equivalent raises the skill rates by 1–3 points.</li>
<li><b>The tasks differ.</b> Skill requests and tool requests are different jobs, so this is not a matched comparison of skills against tools.</li>
<li><b>These are two setups I constructed.</b> Separating the effect of skills from the effect of tools needs a crossed design.</li>
</ul>
<p>In 76% of the skill requests that missed (306 of 401), only built-in tools were called: <code>Glob</code> in 94% of those (288), <code>Grep</code> in 44% (134) and <code>Read</code> in 11% (35). Three examples from Sonnet in the larger setup, with only what was recorded:</p>
<ul>
<li>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder…” → called <code>Glob</code>, then hit the turn limit. No <code>pdf</code> skill. (The folder is empty by design.)</li>
<li>“Analyze the SEO of acme.dev.” → called the <code>fetch</code> and <code>sitemap</code> MCP tools, not the <code>seo</code> skill.</li>
<li>“Open sales.xlsx and add a column with the month-over-month growth.” → selected the <code>xlsx</code> skill.</li>
</ul>

<h2>What might explain the difference?</h2>
<p>The data show where selection changed, not why. Here are the explanations I find plausible, what I observed for each, and what is missing. My logs cannot separate them.</p>
<div class="wrap"><table>
<tr><th>Possible explanation</th><th>What I observed</th><th>What is missing</th></tr>
<tr><td><b>The entry never reached the model</b> (listing budget)</td><td>Both harnesses document caps. At 220 and 1,020 skills, my descriptions were far over Claude Code’s documented budget, and Codex’s cache-write totals nearly stopped growing.</td><td>The listing as the model received it. I never captured it.</td></tr>
<tr><td><b>Visible entries compete</b></td><td><code>seo-audit</code> fell from 100% to 0% (18 and 0 of 18) next to 16 other “seo” skills, while <code>grill-me</code> held at 94%.</td><td>A test that keeps every description visible and varies only the look-alikes.</td></tr>
<tr><td><b>The agent can proceed without a skill</b></td><td>Most misses had no detected skill selection. In the mixed setups I see <code>Glob</code>, <code>Grep</code> and <code>Read</code> calls instead.</td><td>The response text. I cannot say whether the task was completed.</td></tr>
<tr><td><b>Search instead of a listing</b> (MCP)</td><td><code>ToolSearch</code> was called in 81–95% of Claude Code MCP runs, and the paired change from 220 to 791 tools was 0 pp (95% CI about ±5).</td><td>The same tools with search turned off, and a search step for skills.</td></tr>
</table></div>
<p>Research on long contexts makes the second explanation plausible without proving it here. {A(L["nolima"], "NoLiMa")} found that when a question shares no words with the passage it needs, even one of the stronger models it tested fell from 99.3% to 69.7% at 32K tokens. Chroma’s {A(L["rot"], "Context Rot")} study reports that on-topic distractors hurt more than unrelated ones. Those are different tasks, models and metrics, so I treat them as background, not as evidence about my runs. (A toy calculation of the dilution idea is in <a href="#appendix-c">Appendix C</a>.)</p>
<p><b>The test that would settle the most:</b> keep the visible listing and the files constant, and vary only the number of distractors, with search on and off. If selection still falls when every description is visible, truncation is not the whole story. If it does not, most of what I measured is a budget effect.</p>
<p><b>Why measure selection at all</b>, if the answer may still be fine? Because some skills are procedures you require: a release checklist, a security review, a house style. Skipping one of those matters even when the task looks done. For a convenience wrapper, it may not.</p>

<h2>What you can do about it</h2>
<div class="wrap"><table>
<tr><th>What I observed</th><th>How sure</th><th>What to do</th></tr>
<tr><td>Selection of the designated skill fell as more skills were installed, starting at 20</td><td>Measured; 95% CIs exclude zero from 20 skills on (Claude); one sample of extra skills</td><td>Enable fewer skills per project</td></tr>
<tr><td>Most misses had no skill selected at all</td><td>Measured; the cause is unknown</td><td>Check what the model can see before rewriting descriptions</td></tr>
<tr><td>Single-step MCP selection in Claude Code held from 220 to 791 tools</td><td>Measured: 0 pp change, 95% CI about ±5; search not isolated</td><td>Prefer search over a full listing where you can</td></tr>
</table></div>
<h3>[Trick #1] Check what is actually exposed</h3>
<p>In Claude Code, <code>/context</code> shows the size of your skill listing and <code>/doctor</code> tells you whether descriptions are being dropped. Codex prints a warning when it goes over its budget ({A(L["c19679"], "codex#19679")}). Blake Crosley wrote a good account of {A(L["crosley"], "the skills his agent could not see")}. This is a diagnostic, and it is the first thing I would do.</p>
<h3>[Trick #2] Enable less, per project</h3>
<p>This is the one manipulation I tested: with fewer skills installed, the designated one was selected more often (answer quality not measured). Enable plugins per project, turn off unused skills with <code>/skills</code>, and if you only need <code>pdf</code> from a 3,000-skill collection, install <code>pdf</code>. Overlapping collections can expose the same skill twice, a case I did not measure, so check what is actually enabled.</p>
<h3 id="trick-search">[Trick #3] Test other ways to discover and invoke (untested here)</h3>
<ul>
<li><b>Invoke required skills by name</b> (<code>/skill-name</code>) instead of hoping for a match.</li>
<li><b>Give a skill a trigger nobody else has.</b> The skills that held in my sample had concrete nouns and file types. That is an observation, not a controlled test.</li>
<li><b>Raise the listing budget</b> (<code>skillListingBudgetFraction</code> in Claude Code, <code>skills.max_context_tokens</code> in Codex). You pay for it on every request.</li>
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

# Codex: prints the SKILL.md files it read
codex exec --json -s read-only "Audit the SEO of my site." \\
  | grep -o 'skills/[a-z0-9-]*/SKILL.md' | sort -u</code></pre>
<p>Then repeat with only that skill enabled. A handful of requests will not give you a reliable rate, but it will show whether the skill is ever selected. I would genuinely love to see your numbers.</p>

<h2>What this cost</h2>
<div class="wrap"><table>
<tr><th>Item</th><th class="n">Runs</th><th class="n">Cost</th></tr>
<tr><td>GPT, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">$119.13</td></tr>
<tr><td>GPT, MCP experiment so far (OpenAI API)</td><td class="n">170</td><td class="n">$52.60</td></tr>
<tr><td><b>Calculated API fees</b></td><td class="n">650</td><td class="n"><b>$171.73</b></td></tr>
<tr><td>Claude Haiku and Sonnet in Claude Code (my Claude subscription; API list price for reference)</td><td class="n">4,020</td><td class="n">$0 extra ($192.61 list)</td></tr>
</table></div>
<p>The GPT figures are calculated from the token usage Codex reported, at {A(L["price"], "OpenAI’s list prices")}. I have not reconciled them against the invoice. Cache writes were 76–87% of each run’s calculated cost. {A(L["r_cost"], "The per-batch breakdown is in the repo.")}</p>
<p>Running every remaining GPT cell at full size would cost about $1,400 by my estimate, most of it in the mixed setups. That assumes Codex loads every tool definition, as my 20-tool runs suggest. {A(L["contextbolt"], "Another measured post")} reports that Codex defers MCP tools, so the estimate may be too high. I have not reconciled the two.</p>

<h2>Limitations</h2>
<ul>
<li><b>Selection, not quality.</b> A run without the skill can still produce a fine answer.</li>
<li><b>Minimal setup.</b> Empty folders, stub instructions, and 3–4 turns in Claude Code. Some capped runs might have selected the skill later.</li>
<li><b>No captured listing, no response text.</b> I know what was called, not what the model saw or wrote.</li>
<li><b>Few samples.</b> One random sample of extra skills, and six requests per target, all written by me. The CIs cover variation across these requests and runs, not the draw of extra skills or the wording I chose.</li>
<li><b>Configurations, not models.</b> Claude Code and Codex differ in model, prompts, budgets and permissions.</li>
<li><b>GPT data is thinner.</b> One run per request, and MCP only with 1 tool and, partly, with 20.</li>
<li><b>Things change.</b> Harness limits, commands and prices are as documented in November 2026. The issue reports I link are motivation, not evidence of current behaviour.</li>
</ul>
<p>The {A(L["r_meth"], "full methodology")}, {A(L["r_rev"], "an external review of it")}, {A(L["r_chg"], "my response to that review")}, and all data and scripts are in {A(L["repo"], "the GitHub repo")}.</p>

<h2>What’s next</h2>
<p>Three tests come first:</p>
<ol>
<li><b>Validation.</b> Capture the listing the model receives, put real files in the folders, and give Claude 10 turns instead of 3.</li>
<li><b>More catalogs.</b> Repeat with other random samples of extra skills, and add control requests.</li>
<li><b>Search and a crossed design.</b> Search on and off, skills and tools varied separately, and browser tasks with realistic stub responses.</li>
</ol>
<p>The full plan with costs is in {A(L["r_follow"], "the follow-up protocol")}. Its GPT part is cut down to fit $100 of API fees, and its Claude part runs on my subscription.</p>

<h2>Conclusion</h2>
<p>I started with a simple question: if I install a thousand skills, does my agent get more capable? What changed my view is the difference between installing a capability and having it reliably available when a request needs it. In this test, selection of the designated skill fell as the collection grew, while single-step MCP tool selection in Claude Code held up better. Before adding another big collection, I would check what the agent can actually see, and I would measure answer quality separately before deciding that more activation is always better.</p>
<p>Thanks for reading! If you run the check on your own setup, tell me what you got.</p>

<h2 id="appendix-a">Appendix A: the 20 target skills</h2>
{SK_TABLE}

<h2 id="appendix-b">Appendix B: a survey of 42 popular skill repos</h2>
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
<p><b>Overlapping collections.</b> Whether two copies of a skill are both exposed depends on how you install them. Claude Code namespaces plugin skills as <code>/plugin-name:skill-name</code>, so both load ({A(L["cc_skills"], "docs")}). Codex’s {A(L["codex_skills"], "docs")} say same-name skills are not merged. Copying folders by hand into one skills folder keeps one copy. If you install overlapping collections, check what is actually enabled. I deduplicated names in my setups, so the experiment did not measure duplicates.</p>

<h2 id="appendix-c">Appendix C: a toy calculation about dilution</h2>
<p>This is illustrative arithmetic, not a model of these agents, and nothing in my data measures attention. It only shows why “more entries can dilute a match” is a reasonable thing to test.</p>
<p>In a {A(L["vaswani"], "transformer")}, each attention head turns scores into weights with a softmax, and within one head the weights add up to 1:</p>
<p class="formula"><i>a<sub>i</sub></i> = e<sup><i>s<sub>i</sub></i></sup> / Σ<sub><i>j</i></sub> e<sup><i>s<sub>j</sub></i></sup></p>
<p>Now a cartoon with several assumptions: each skill description is one block, the target scores 20 times higher than every unrelated skill, look-alikes score the same as the target, scores do not change when entries are added, and nothing else is in the context. Then the target’s share is 20 / (20 + <i>n</i>) for <i>n</i> other skills:</p>
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

html = f'<title>A Closet Full of Skills</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">\n<style>{css}</style>\n{body}\n{CHART_JS}'
open(os.path.join(B, "skills-mcp-post.html"), "w").write(html)
print("ok", len(html))
