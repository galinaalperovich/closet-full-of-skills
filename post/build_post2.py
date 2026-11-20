"""Assemble post v2: skills-mcp-post.html (figures from figs2.json, numbers from analysis/derived/v2)."""
import json, os, re
B = os.path.dirname(os.path.abspath(__file__))
fig = json.load(open(os.path.join(B, "figs2.json")))
t = open(os.path.join(B, "post.tpl.html")).read(); css = t[t.index("<style>") + 7:t.index("</style>")]
css = css.replace("--s-haiku:#f0a050; --s-sonnet:#8aa6ff; --s-gpt:#5fd39a", "--s-haiku:#cf7c2e; --s-sonnet:#6f8be6; --s-gpt:#2fa86f;"
  " --seg-target:#4fc1b9; --on-seg-target:#0d1f1e; --seg-eq:#2c7a75; --on-seg-eq:#e5e8eb; --seg-alt:#6b7681; --on-seg-alt:#ffffff; --seg-none:#3a434b; --on-seg-none:#e5e8eb; --seg-cap:#3a434b; --on-seg-cap:#e5e8eb;"
  " --seq1:#2a5a57; --seq2:#3f938c; --seq3:#7fd3cc")
css = css.replace("--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;", "--s-haiku:#b35c00; --s-sonnet:#3157c4; --s-gpt:#0f7a4a;"
  " --seg-target:#0f6e6a; --on-seg-target:#ffffff; --seg-eq:#7fbcb7; --on-seg-eq:#0d1f1e; --seg-alt:#8a949e; --on-seg-alt:#ffffff; --seg-none:#d9dee2; --on-seg-none:#1d2126; --seg-cap:#d9dee2; --on-seg-cap:#1d2126;"
  " --seq1:#a9d6d2; --seq2:#4f9e98; --seq3:#0b4f4c;")
assert css.count("--seg-target") == 3, css.count("--seg-target")
css += """
.matrix td{min-width:13rem} .matrix td b{display:block;font-weight:600;margin-top:.35rem} .matrix td b:first-child{margin-top:0}
.note{font:.88rem/1.55 var(--sans);color:var(--muted)}
.callout{border-left:3px solid var(--accent);padding:.2rem 0 .2rem .9rem;font-style:italic}
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
 "ctxeng": "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "ewc": "https://arxiv.org/abs/1612.00796", "repo": "https://github.com/galinaalperovich/in-context-forgetting", "davila7": "https://github.com/davila7/claude-code-templates",
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
<h1>Catastrophic Forgetting, Now In-Context: The More Skills and MCP Tools You Install, the Less Your Agent Actually Uses Them</h1>
<p class="dek">I installed up to 1,000 skills and 791 MCP tools into Claude Code and Codex. The right skill went from being picked 78–100% of the time to 10–34%. In Claude Code, the right MCP tool dropped less, then held steady. Part of it is the harness, part of it is the model.</p>
<div class="byline">Galina Alperovich · draft v2</div>

<p class="tldr">tldr; I measured how often Claude Code and Codex pick the skill or MCP tool that a request was written for, as more of them are installed. <b>Skills fade.</b> With only the target skill installed, it was selected 78–100% of the time. With 1,000 other skills next to it, that fell to 10–34%. <b>MCP tools bend.</b> In Claude Code, single-step tools went from 86–92% to 77–78%, and then stayed flat all the way from 220 to 791 tools. When skills and tools were installed together, requests meant for a skill lost about half their hits. This is 4,674 runs, and it measures which component was selected, not how good the answer was. I also explain why it happens and share hints to keep your skills and tools from being “forgotten”.</p>

<p>Agent skills became the new npm. A skill is a folder with a <code>SKILL.md</code> file: a name, a short description, and instructions the agent reads only when it needs them. {A(L["anth_skills"], "Anthropic’s skills repo")} has almost 200K stars. The biggest community collection I found, {A(L["sickn33"], "sickn33/agentic-awesome-skills")}, has over 3,000 skills, and its README invites you to install all of them. MCP servers went the same way. One GitHub server alone exposes 149 tools.</p>

<p>Here is what made me curious. The agent decides which skill to use from the descriptions alone, and every description is sent with every request. The descriptions in that one collection add up to about 129K tokens. For comparison, <em>The Great Gatsby</em> is about 72K tokens. So the agent would scan almost two Gatsbys before answering “fix my PDF”, and Claude Code gives the whole skill listing only about 1% of its context window. MCP tools carry full parameter schemas on top of that.</p>

<p>I wanted to see what actually happens, so I measured it. In this post I cover:</p>
<ul>
<li>Whether people actually run into this (they do, loudly)</li>
<li>How an agent decides to load a skill or call a tool, and where the limits are</li>
<li>What I found in 42 popular skill repositories</li>
<li>Three experiments: skills only, MCP tools only, and skills plus tools together</li>
<li>Which skills survive a crowd, with real requests</li>
<li>Why this happens, even to models that solve olympiad math: attention, context and the “do it myself” default</li>
<li>One big table: harness × skills/tools, with what to know and what to try</li>
<li>How to check your own agent, what this cost, and what I would still like to test</li>
</ul>

<h2>“Short” Summary</h2>
<ol>
<li><b>[Finding #1] Skills fade.</b> On every model, the more skills were installed, the less often the designated one was selected. Sonnet went 93% → 76% → 56% → 34% for 1, 20, 220 and 1,020 skills.</li>
<li><b>[Finding #2] The drop starts at 20.</b> Just putting 20 selected skills side by side cost Haiku 31 points and Sonnet 17 (paired, same requests).</li>
<li><b>[Finding #3] The two harnesses have different curves.</b> Claude Code declines steadily. Codex stays near the top up to 220 skills, then drops to 10% at 1,020. Its token counts suggest the skill listing stopped growing, which fits Codex’s documented listing cap.</li>
<li><b>[Finding #4] Most misses are “no skill at all”.</b> At 1,020 skills, most target misses had no skill selected within the observation window. Few picked a wrong skill, and some of those alternatives were perfectly fine.</li>
<li><b>[Finding #5] MCP tools bend.</b> In Claude Code, single-step tools fell from 86–92% to 77–78%, and nearly all of that loss came with the first 20 tools. From 220 to 791 tools the change was zero.</li>
<li><b>[Finding #6] In a mix, skills lose most.</b> With skills and MCP servers installed together, skill requests lost 48–59 points while single-step tool requests lost 9–18.</li>
<li><b>[Why] Noticing, not reasoning.</b> Every skill takes a share of a fixed attention budget, people rarely use a skill’s own words, and the model can always do the job itself. Smart models still miss, because the hard part is noticing the skill, not reasoning about it.</li>
<li><b>[Finding #7] It is not free.</b> GPT runs cost me $0.19–0.35 each in API fees, and most of that was writing the prompt prefix (skill listing and tools) to the cache.</li>
</ol>
<p><b>And from the survey of 42 popular skill repos:</b></p>
<ul>
<li><b>[Survey #1] Skills are almost never tested.</b> Only 2.6% of 6,908 skills ship a test or eval file, and 27 of the 42 repos ship none at all.</li>
<li><b>[Survey #2] Half of the files are copies.</b> Of 14,418 <code>SKILL.md</code> files, only 7,848 are distinct. 831 skill names appear in two or more repos, and two big collections share 370 skills: install both as plugins and you get those twice.</li>
<li><b>[Survey #3] Half the descriptions never say when to use the skill</b> (48%, by a simple keyword check), and the description is all the agent sees when it decides.</li>
<li><b>[Survey #4] One big collection already overflows the listing.</b> 16 of the 42 repos are over Claude Code’s budget for a 200K window, the largest about 65 times over. Even Anthropic’s own 20 skills are slightly over.</li>
</ul>
<p>Let’s look at each piece in more detail.</p>

<h2>Is this a real problem?</h2>
<p>Before running anything, I checked whether people actually complain about this. They do, in both camps.</p>
<p><b>Skills:</b></p>
<ul>
<li>{A(L["i81081"], "anthropics/claude-code#81081")}, “Session-start skill listing silently truncates most skill descriptions”. Of 36 project skills, 27 reached the model with only a name.</li>
<li>{A(L["i56710"], "#56710")}: a warning said 122 skill descriptions were dropped. {A(L["i64606"], "#64606")}: with 20+ skills, Claude writes the code by hand instead of using the skill. {A(L["i10768"], "#10768")}: “Natural Language Intent Matching Completely Broken”.</li>
<li>{A(L["c19679"], "openai/codex#19679")}, “Make skills metadata context budget configurable instead of hardcoded 2%” (40 reactions).</li>
<li>Reddit: {A(L["r_hell"], "“Skill hell is real: 140+ installed skills made my agents worse at triggering”")} and {A(L["r_cc"], "“Why is claude code ignoring my /skills?”")}. Jesse Vincent wrote {A(L["fsck"], "“Claude Code skills not triggering? It might not see them.”")}</li>
</ul>
<p><b>MCP tools:</b></p>
<ul>
<li>{A(L["i6915"], "anthropics/claude-code#6915")}, “Allow MCP tools to be available only to subagent” (377 reactions), and {A(L["i7328"], "#7328")}, “Allow selective enable/disable of individual tools” (225).</li>
<li>{A(L["i37793"], "#37793")}: subagents fail with “prompt is too long” because tool definitions exceed 200K tokens. {A(L["i11364"], "#11364")}: seven servers took 67,300 tokens before the first message.</li>
<li>Cursor capped tools at 40 ({A(L["cursor40"], "forum")}, {A(L["cur79686"], "“40 tools way to less”")}). Gemini CLI users ask to {A(L["g21823"], "raise the 100-tool limit")}.</li>
<li>r/mcp: {A(L["r_mcp1"], "“How many MCP tools is too many before your agent gets confused?”")} and {A(L["r_mcp2"], "“Tool definitions are eating my context window”")}.</li>
</ul>
<p>The MCP side is also studied in papers. In {A(L["ragmcp"], "the RAG-MCP paper")}, a model picked the right tool 13.6% of the time with a large pool in the prompt, and 43.1% with a retrieved subset. {A(L["livemcp"], "LiveMCPBench")} built a benchmark around 70 servers. Anthropic reports that its {A(L["toolsearch"], "tool search")} raised tool-selection accuracy on an internal evaluation from 49% to 74% for Opus 4 ({A(L["advtool"], "Advanced tool use")}). What I did not find was the same curve measured for skills, next to MCP tools, on two harnesses at once.</p>

<h2>How an agent picks a skill or a tool</h2>
<p>Skills use a trick called progressive disclosure. The agent does not read all skill instructions up front, because they would not fit. Every request carries a short listing instead: each skill’s name and description. From that listing alone, the model decides whether to load a skill, and only then reads its full <code>SKILL.md</code>. MCP tools are similar, except each tool also has a JSON schema for its parameters.</p>
{fig_("fig_how", "Every request carries a skill listing and tool definitions. The model picks from those, or uses only the harness’s built-in actions (search files, read, run a shell). The Codex box is inferred from token counts, explained below.")}
<p>Both harnesses limit the skill listing ({A(L["cc_skills"], "Claude Code docs")}, {A(L["codex_skills"], "Codex docs")}):</p>
<ul>
<li><b>Claude Code</b> gives it 1% of the context window. Each description is capped at 1,536 characters. When the listing overflows, descriptions of your least-used skills are dropped. MCP tools are deferred: the model sees their names and loads schemas on demand with a <code>ToolSearch</code> call. This is a Claude Code feature, not something the model does on its own. <b>If you build your own agent</b> directly on a model API, with your own tool loop or a framework, every tool definition you pass is sent in full with every request, and the skill listing is whatever you put in the prompt. Tool search and retrieval are then yours to implement (see <a href="#trick-search">[Trick #6]</a>).</li>
<li><b>Codex</b> gives the skill listing 2% of the context window, at most 10,000 tokens, and shortens descriptions first.</li>
</ul>
<p>In Claude Code, loading a skill is an explicit <code>Skill</code> tool call, easy to see in the event log. In Codex, the agent reads the file with a shell command such as <code>cat .agents/skills/pdf/SKILL.md</code>, which is also easy to spot. I count those as “selected”. I did not check that the file was actually read successfully. Small print, but it matters.</p>

<h2>What I found in 42 popular skill repos</h2>
<p>I cloned a sample of popular skill repositories, found through GitHub topic searches plus seven repos {A(L["trending"], "trending this month")}: 42 repos with 6,908 skills. This survey covers skills only; I did not scan MCP servers. A static script checked frontmatter, names, file links, bundled scripts and size. No code was run.</p>
<ul>
<li><b>They are clean.</b> Each structural defect (broken links, missing scripts, invalid names) affects 0–3% of skills.</li>
<li><b>Few ship tests.</b> My scanner found test or eval files bundled for 2.6% of skills (177 of 6,908). 27 of the 42 repos ship none at all, and only 3 ship them for every skill. Tests can live elsewhere, but inside the skill folder they are rare. {A(L["marketing"], "coreyhaines31/marketingskills")} is the big exception, with evals for all 53 of its skills.</li>
<li><b>Half the descriptions never say when to use the skill.</b> By a simple keyword check (no “when”, “use for”, “trigger” and the like), 48% of distinct skill files describe only what the skill is. The agent picks a skill from its description alone, so this is the line that matters most.</li>
<li><b>Lots of copying.</b> 831 skill names appear in two or more repos. For 270 of them, at least two repos carry a nearly identical description (80% or more of the text matches). That is mostly re-packaging: collections bundle popular skills so you can install everything from one place, for example 18 of Anthropic’s 20 skills inside {A(L["davila7"], "davila7/claude-code-templates")}. The other names are shared without the text, sometimes as a reworded copy and sometimes just because the name is obvious: <code>seo-audit</code> exists in five repos with five different descriptions. Copying also happens inside repos: of 14,418 <code>SKILL.md</code> files, only 7,848 are distinct, mostly because collections ship each skill once per plugin format (sickn33 has about three copies of each). Some collections even compete with themselves: in sickn33, 161 skills have a near-twin in the same collection, such as <code>code-refactoring-refactor-clean</code> and <code>codebase-cleanup-refactor-clean</code>, whose descriptions are identical.</li>
<li><b>Big collections do not fit.</b> Installed whole, 16 of the 42 repos are over Claude Code’s listing budget for a 200K window. Even Anthropic’s own 20 skills come to about 9,700 characters, a little over the roughly 8,000 the budget allows.</li>
</ul>
<p><b>What this means if you install just one big collection.</b> You are over the budget before you add anything else. The descriptions in {A(L["sickn33"], "sickn33/agentic-awesome-skills")} add up to about 129K tokens: roughly 60 times Claude Code’s budget for a 200K window, and 13 times Codex’s 10K cap. In Claude Code, most of those skills reach the model as a bare name. In Codex, descriptions are shortened and, judging by my token counts, many are left out. In my experiment, with 1,020 skills installed, the right skill was picked only 10–34% of the time, and the drop started at 20. So expect to use a handful of skills with distinctive names reliably, and the rest only when you call them by name (<code>/skill-name</code>). Even my own laptop, with skills I picked up over time, is more than four times over. Install the few you need instead of the whole collection (<a href="#trick-fewer">[Trick #1]</a>).</p>
<p><b>Will two repos pollute your context?</b> It depends on how you install them. In Claude Code, plugin skills are namespaced as <code>/plugin-name:skill-name</code>, so two plugins that both ship <code>seo-audit</code> both load, and both go into the listing ({A(L["cc_skills"], "docs")}). Codex’s {A(L["codex_skills"], "docs")} say it does not merge two skills with the same name; both can appear. Copying folders by hand into one skills folder is different: the second <code>seo-audit</code> folder overwrites the first, and you silently keep one version. And if the same name is in your personal and project folders, Claude Code uses the personal one.</p>
<p>The biggest overlap in my sample is between {A(L["davila7"], "davila7/claude-code-templates")} and {A(L["sickn33"], "sickn33/agentic-awesome-skills")}: 370 shared names, 180 of them with nearly identical descriptions. Install both as plugins, and those 370 skills are listed twice. Every duplicate costs listing budget. In the toy model from “Why does this happen?”, each copy gets about half the attention a single copy would, but the two together get slightly more, so the toy model can’t say whether duplicates help or hurt. When the twin is a reworded copy, the model may also pick the older or weaker version. My crowds were deduplicated by name, so I did not measure this case.</p>
<p class="warning"><b>Warning: duplicated skills waste your context.</b> If you install two collections as plugins in Claude Code, or both in Codex, every skill they share is listed twice. The second copy uses listing budget for nothing, and in Claude Code that can push other skills’ descriptions out of the listing. If the copies differ, the agent may pick the older or weaker one. I did not measure whether duplicates also change how often some copy gets used. Either way, check what a second collection shares with the first, and keep one copy of each skill, from the source you trust.</p>
{fig_("fig_weight", "Estimated size of the skill listing if you install each collection whole. The red line is roughly Claude Code’s budget for a 200K window.")}

<h2>The experiment</h2>
<p>I picked 20 well-known skills: Anthropic’s own ({A(L["anth_skills"], "pdf, xlsx, pptx, docx, webapp-testing, mcp-builder, frontend-design")}), {A(L["mattpocock"], "Matt Pocock’s")} (tdd, grill-me, diagnosing-bugs), {A(L["obsidian"], "Obsidian’s")}, Vercel’s, Addy Osmani’s, Emil Kowalski’s, humanizer, caveman, and two marketing skills (all 20 are in the table below). I added five from repos trending on GitHub this month: {A(L["hallmark"], "hallmark")}, {A(L["cfsec"], "Cloudflare’s security-audit")}, {A(L["claudeseo"], "claude-seo")}, {A(L["ffmpeg"], "ffmpeg-skill")} and {A(L["igskill"], "an Instagram carousel skill")}.</p>
{SK_TABLE}
<p>For MCP, I took 791 real tool definitions from 73 servers: {A(L["ghmcp"], "GitHub’s server")} (exact schemas), {A(L["cdt"], "Chrome DevTools")}, {A(L["pwmcp"], "Microsoft Playwright")}, and 70 servers from {A(L["livemcp_gh"], "LiveMCPBench")}. I picked 20 target tools that people use every day.</p>
<p>For every target I wrote six requests the way a person would ask, never naming the skill or the tool:</p>
<div class="wrap"><table>
<tr><th>Target</th><th>Example requests</th></tr>
<tr><td><code>pdf</code> skill</td><td>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder into a single file.” · “Add a DRAFT watermark across every page of proposal.pdf.”</td></tr>
<tr><td><code>seo-audit</code> skill</td><td>“Why did our organic traffic drop last month?” · “Are our canonical tags and hreflang set up correctly?”</td></tr>
<tr><td><code>grill-me</code> skill</td><td>“Grill me on this plan before I start building.” · “Stress-test my architecture idea by questioning me about it.”</td></tr>
<tr><td><code>caveman</code> skill</td><td>“Be brief. Less words.” · “Stop being so wordy, just give me terse answers.”</td></tr>
<tr><td><code>github.create_issue</code> tool</td><td>“Open an issue in acme/webapp saying the login button is broken on Safari.”</td></tr>
<tr><td><code>yahoo-finance</code> stock price tool</td><td>“What’s Apple’s stock price right now?” · “How is NVDA trading today?”</td></tr>
<tr><td><code>memory.create_entities</code> tool</td><td>“Remember that my manager is Priya and she prefers updates on Fridays.”</td></tr>
<tr><td><code>playwright-mcp</code> screenshot tool</td><td>“Take a screenshot of https://example.com and tell me what’s on it.”</td></tr>
</table></div>
<p>Each request ran in four setups:</p>
<ul>
<li><b>Alone:</b> only the target skill (or tool) is installed.</li>
<li><b>20:</b> all 20 targets together.</li>
<li><b>~220:</b> the 20 plus 200 others, drawn at random.</li>
<li><b>All:</b> the 20 plus 1,000 other skills, or all 771 other tools.</li>
</ul>
<p>The extra skills are one random sample from the big community collection, and some of them overlap with the targets (16 others mention “seo”, for example). A third experiment installed skills and MCP servers together, in two setups that I built: a smaller one with 100 skills and 437 tools, and a larger one with 400 skills and all 791 tools.</p>
<p>Models: Claude Haiku and Claude Sonnet in Claude Code (v2.1.328), and GPT (gpt-6-astra, medium reasoning) in Codex CLI (v0.160.0).</p>
<p>A few details that matter for reading the numbers:</p>
<ul>
<li><b>Stubs.</b> Every skill keeps its real name and description, but its instructions are replaced with one line: “reply with one short sentence”. Every MCP tool returns a similar stub. That keeps exactly what the routing decision depends on, and nothing downloaded can run. It also means whatever happens <em>after</em> the first selection is not normal behaviour.</li>
<li><b>Empty folders.</b> Each run starts in a fresh folder with no files, no repo and no browser. When a request mentions <code>report.pdf</code>, there is no such file. This is a minimal routing test, not a real work session.</li>
<li><b>Observation window.</b> Claude Code was capped at 3 turns (4 with MCP). Codex runs one turn with no cap. A skill selected later than that is not seen.</li>
<li><b>Scoring.</b> A run counts if the agent selects the designated skill or tool, or an equivalent tool on another server (any server’s stock-price tool, say). Selecting a different skill does not count, but I had every alternative rated afterwards, blind, to see which were reasonable.</li>
</ul>

<h2>Result 1: skills fade</h2>
<div class="wrap"><table>
<tr><th>Setup</th><th class="n">Skills</th><th class="n">Haiku</th><th class="n">Sonnet</th><th class="n">GPT (Codex)</th></tr>
<tr><td>Target skill alone</td><td class="n">1</td><td class="n">78%</td><td class="n">93%</td><td class="n">100%</td></tr>
<tr><td>20 skills together</td><td class="n">20</td><td class="n">48%</td><td class="n">76%</td><td class="n">99%</td></tr>
<tr><td>Plus 200 others</td><td class="n">220</td><td class="n">25%</td><td class="n">56%</td><td class="n">83%</td></tr>
<tr><td>Plus 1,000 others</td><td class="n">1,020</td><td class="n">16%</td><td class="n">34%</td><td class="n">10%</td></tr>
</table></div>
{fig_("fig_skills", "Share of requests where the designated skill was selected within the observation window. Bars are 95% intervals from resampling requests. Sonnet ran each request 3 times (360 runs per point); Haiku and GPT once (120). The x axis is not to scale.")}
<p>Three things jump out.</p>
<p><b>The decline starts at 20.</b> These are 20 skills about different things: PDFs, SEO, TDD, animation. Still, comparing the same requests, Haiku lost 31 points (41 requests got worse, 4 got better) and Sonnet lost 17 (27 worse, none better). Every extra entry in the listing is one more thing competing for the model’s attention.</p>
<p><b>GPT holds, then drops.</b> At 220 skills GPT is still at 83%. At 1,020 it falls to 10%. A clue sits in the token counts that Codex reports. From 1 skill to 1,020 skills, the listing I installed grew by about 44K tokens, but the prompt prefix Codex wrote to its cache grew by only about 7K tokens per run. That looks like a cap: most descriptions were cut or left out, which matches Codex’s documented 10,000-token budget. I did not see what the model saw, so this is an explanation, not a proof.</p>
<p><b>Claude declines smoothly.</b> No cliff, just steady loss, which fits Claude Code’s design: names stay, and descriptions disappear gradually.</p>

<h3>What the agent did instead</h3>
{fig_("fig_misses", "What happened with 1,020 skills installed. “Equivalent alternative” means an independent, blind rater judged the other skill a fine choice for that request. Hatched: the run hit Claude Code’s 3-turn limit with no skill selected.")}
<p>When the agent missed the target, it rarely picked a wrong skill. Most of the time it selected no skill at all within the window and went ahead with its built-in tools. You get an ordinary-looking answer, no error, no warning.</p>
<p>The details depend on the model:</p>
<ul>
<li><b>Haiku:</b> more than half of the no-skill runs hit the 3-turn limit, often after searching the empty folder for files the request mentioned. That is a fair warning about my setup. With more turns, some of those runs might have found the skill later. I report what happened inside the window, and I plan to test a longer one.</li>
<li><b>Sonnet:</b> two thirds of its misses (160 of 239) finished normally without selecting a skill.</li>
<li><b>GPT:</b> about a quarter of its misses loaded a look-alike from the crowd. Some of those are not even wrong. The rater judged 12 of GPT’s 108 misses “equivalent”, for example <code>interview-me</code> for “Interview me about my plan”. Counting those, GPT goes from 10% to 20%. The picture stays the same.</li>
</ul>

<h3>Which skills survive a crowd</h3>
{fig_("fig_dumbbell", "Sonnet, each skill alone (hollow) and with 1,020 skills installed (filled), 18 runs per dot.")}
<p>In this sample, skills with an unusual name or trigger kept going, and skills whose topic many others share disappeared. My design cannot prove that distinctiveness is the cause. Still, the contrast is hard to miss:</p>
<div class="wrap"><table>
<tr><th>Skill</th><th>Look-alikes in the crowd</th><th class="n">Sonnet alone</th><th class="n">With 1,020</th></tr>
<tr><td><code>grill-me</code></td><td>none named “grill”</td><td class="n">18/18</td><td class="n">17/18</td></tr>
<tr><td><code>json-canvas</code></td><td>1 other “canvas”</td><td class="n">18/18</td><td class="n">17/18</td></tr>
<tr><td><code>xlsx</code></td><td>no other spreadsheet skill</td><td class="n">15/18</td><td class="n">14/18</td></tr>
<tr><td><code>seo-audit</code></td><td>16 others with “seo”</td><td class="n">18/18</td><td class="n">0/18</td></tr>
<tr><td><code>security-and-hardening</code></td><td>16 others with “security”</td><td class="n">18/18</td><td class="n">0/18</td></tr>
<tr><td><code>diagnosing-bugs</code></td><td>14 others with “bug” or “debug”</td><td class="n">18/18</td><td class="n">0/18</td></tr>
<tr><td><code>animate</code></td><td>7 others with “anim”</td><td class="n">18/18</td><td class="n">0/18</td></tr>
</table></div>
<p>A few requests in detail:</p>
<ul>
<li><b>“Audit the SEO of my site.”</b> Every model selected <code>seo-audit</code> when it was alone. With 1,020 skills, none did.</li>
<li><b>“Create a .canvas file mapping out the architecture of this app.”</b> Haiku and Sonnet hit it in every setup. A file extension is a strong trigger.</li>
<li><b>“Interview me about my plan for the onboarding redesign.”</b> At 220 skills, all three models picked <code>interview-me</code> instead of <code>grill-me</code>. The rater called that equivalent, and I agree.</li>
<li><b>“Be brief. Less words.”</b> This never triggered <code>caveman</code> on Sonnet, even alone. Some descriptions simply do not match how people ask.</li>
</ul>

<h2>Result 2: MCP tools bend</h2>
<p>Now the same design with MCP tools: 20 target tools on their real servers, then 20 together, then about 220, then all 791.</p>
{fig_("fig_fade", "Claude Code. Solid lines: skills. Dashed lines: the 15 single-step MCP tool targets (browser tools are discussed below). “All installed” means 1,020 skills or 791 tools. Bars on the tool lines are 95% intervals. The x axis is not to scale.")}
<div class="wrap"><table>
<tr><th>Setup</th><th class="n">Haiku, single-step tools</th><th class="n">Sonnet, single-step tools</th><th class="n">GPT, single-step tools</th><th class="n">Sonnet, all 20 incl. browser</th></tr>
<tr><td>Target tool alone</td><td class="n">86%</td><td class="n">92%</td><td class="n">91%</td><td class="n">85%</td></tr>
<tr><td>20 tools</td><td class="n">79%</td><td class="n">81%</td><td class="n">92%*</td><td class="n">66%</td></tr>
<tr><td>~220 tools</td><td class="n">78%</td><td class="n">77%</td><td class="n">not run</td><td class="n">58%</td></tr>
<tr><td>791 tools</td><td class="n">78%</td><td class="n">77%</td><td class="n">not run</td><td class="n">58%</td></tr>
</table></div>
<p class="note">* GPT at 20 tools is partial: 24 of 90 single-step runs, before I paused the GPT runs over cost.</p>
<p><b>Tools bend, then flatten.</b> Most of the loss comes from the first 20 tools, which include near neighbours such as several GitHub tools. After that, adding 570 more tools changed nothing for either Claude model: 0.0 points from 220 to 791. Claude Code used <code>ToolSearch</code> in 81–95% of these runs. That is consistent with deferred loading protecting tool selection from catalogue size. I did not test that mechanism, though. Compare that flat line with the skills curve, which kept falling.</p>
<p><b>Browser tools are where my setup breaks down.</b> “Take a screenshot of example.com” needs two steps: open the page, then take the screenshot. With only the screenshot tool installed, agents called it directly. With navigation tools available, they opened the page first. My stub then answered “reply with one short sentence”, and the run ended. So in the big setups, the strict score for the five browser targets falls to 0–5 of 30, while “went to a capable browser server first” stays at 25–30 of 30. Neither number says whether the screenshot would have happened. That is why the headline uses the 15 single-step tools, and why a rerun with realistic browser responses is on my list.</p>
<p><b>A GPT oddity.</b> GPT never called Chrome DevTools’ <code>performance_start_trace</code>, not even with nothing else installed (0 of 6). It called Codex’s own MCP discovery tools and the shell instead. That tool requires a <code>pageId</code>, and there was no page.</p>

<h2>Result 3: skills and tools together</h2>
<p>Real setups have both. So I installed 25 skill targets plus sampled skills next to whole MCP servers, including ones that overlap: <code>xlsx</code> next to an Excel server, <code>webapp-testing</code> next to Playwright. Then I sent all 150 skill requests and 120 tool requests.</p>
{fig_("fig_mix", "Claude Code, share of requests where the designated component was selected. “Single component” is the target installed alone. “Mixed, smaller”: 100 skills, 437 tools. “Mixed, larger”: 400 skills, 791 tools. Tool requests are the 15 single-step targets.")}
<p>Skill requests lost 48–59 points, against 9–18 for tool requests. Note the turn caps: the skills-alone baseline had 3 turns and the mixed setups had 4, which, if anything, favours the mixed setups. These are two setups I constructed, not a measurement of how skills and tools interact. Disentangling that needs a proper crossed design, which is on the list.</p>
<p>Where did the skill requests go? Mostly into built-in actions: <code>Glob</code> in 288 runs, <code>Grep</code> in 134, <code>Read</code> in 35. A few examples from Sonnet in the larger setup:</p>
<ul>
<li>“Merge invoice-jan.pdf and invoice-feb.pdf in this folder…” → searched for the files with <code>Glob</code>, found nothing, hit the turn limit. No <code>pdf</code> skill.</li>
<li>“Build a landing page for my new note-taking app.” → selected <code>landing-page</code>, a look-alike, instead of <code>hallmark</code>.</li>
<li>“Analyze the SEO of acme.dev.” → called the <code>fetch</code> and <code>sitemap</code> MCP tools instead of the <code>seo</code> skill.</li>
<li>“Open sales.xlsx and add a column with the month-over-month growth.” → <code>xlsx</code> skill, first try. The survivors survive here too.</li>
</ul>

<h2>Why does this happen?</h2>
<p>This is the part that bugged me most. The same models solve olympiad-level math problems. So how do they miss a skill literally called <code>seo-audit</code> when I ask them to audit my SEO? I don’t think that is a contradiction. Solving a hard problem and noticing that one entry in a long listing applies to you are different jobs, and the second one gets harder with every entry you add. I call it forgetting as a nod to {A(L["ewc"], "catastrophic forgetting")}, where a network trained on new tasks loses the old ones. Here nothing is retrained: the skill is still in the prompt, and the agent simply stops reaching for it. Here is my best explanation, in four layers. I did not test these mechanisms directly: my data fits them, and the papers I link measured them.</p>

<h3>Layer 1: sometimes the model never sees the skill</h3>
<p>Both harnesses cap the listing, so past some size, descriptions are shortened or dropped before the model reads a word. That fits the Codex cliff. The prompt Codex cached grew by about 2K tokens from 1 to 20 skills, which is the whole listing I added. At 220 skills it grew by less than the listing, and from 220 to 1,020 it barely grew at all. No amount of intelligence finds a description that is not there. In Claude Code, the listing I added was about 42K characters at 220 skills and 179K at 1,020, far over its budget, so many skills arrived as a bare name.</p>
<p>That cannot be the whole story, though. At 20 skills the listing I added was only about 7,700 characters, close to Claude Code’s budget for a 200K window (about 8,000), so at most a little was trimmed. Claude still lost 17–31 points. My data cannot cleanly separate “not shown” from “shown but not noticed”. The studies below, where nothing is trimmed at all, show that the second one is real.</p>

<h3>Layer 2: attention is a budget, and every skill takes a share</h3>
<p>A quick refresher on the {A(L["vaswani"], "transformer")}. The context window is everything the model can look at while it works: the system prompt, tool definitions, the skill listing, your request. For every token the model produces, attention compares the current position with every token in that window, gives each one a score <i>s</i>, and turns the scores into weights with a softmax:</p>
<p class="formula"><i>a<sub>i</sub></i> = e<sup><i>s<sub>i</sub></i></sup> / Σ<sub><i>j</i></sub> e<sup><i>s<sub>j</sub></i></sup></p>
<p>The weights always add up to 1. So attention is a fixed budget: a new token does not bring new attention, it takes a share of the existing one. Anthropic calls this the model’s {A(L["ctxeng"], "attention budget")}. Nakanishi showed that as inputs grow, softmax weights flatten and the largest one shrinks, and named it {A(L["ssmax"], "attention fading")}.</p>
<p>Here is a toy version of my experiment. Treat each skill description as one block, and say the target matches the request 20 times better than an unrelated skill (a score gap of ln 20 ≈ 3). Then the target gets 20 / (20 + <i>n</i>) of the attention, where <i>n</i> is the number of other skills:</p>
{fig_("fig_attn", "A toy model, not a measurement. The only assumption is the 20× match. Look-alikes, such as the 16 other “seo” skills, are assumed to match as well as the target, so even the attention that goes to matching skills is split 17 ways.")}
<p>A real model has dozens of layers and many heads, and it learns to sharpen these weights, so don’t read the numbers literally. The direction is the point. Alone, the description has the stage to itself. With 1,020 skills, it is one voice in a crowd, even when the model reads every word.</p>

<h3>Layer 3: matching meaning is harder than matching words</h3>
<p>You may know needle-in-a-haystack tests, where models find a planted sentence in a million tokens almost perfectly. The catch is that the question usually repeats words from the needle, and a literal match is exactly what attention finds easily. {A(L["nolima"], "NoLiMa")} removed the shared words, so the model had to connect meanings instead. GPT-4o, the best model they tested, fell from 99.3% to 69.7% at just 32K tokens, and most models fell below half of their short-context score. Chroma’s {A(L["rot"], "Context Rot")} study of 18 models found the same decline as inputs grow, even on simple tasks, and distractors that are on topic but wrong made it worse.</p>
<p>My requests are written the way people talk. “Why did our organic traffic drop last month?” shares no word with <code>seo-audit</code>. Now look at the survivors from Result 1: “Grill me on this plan” meets <code>grill-me</code>, “sales.xlsx” meets <code>xlsx</code>, and “a .canvas file” meets <code>json-canvas</code>. Each is a literal match, and a unique one. “Audit the SEO of my site” is literal too, but 16 other skills mention “seo”, so it is not unique anymore. Those 16 are exactly the kind of distractors Chroma tested.</p>

<h3>Layer 4: doing it yourself is always an option</h3>
<p>This is the part I find most interesting. At 20 skills, Sonnet missed the target in 88 of 360 runs, and not one of those misses loaded a wrong skill: 85 went ahead without any skill and 3 hit the turn limit. Even at 1,020 skills, only 9 of Sonnet’s 239 misses loaded another skill. So the real competition is not <code>seo-audit</code> against <code>seo-technical</code>. It is “load a skill” against “I’ll just do it”.</p>
<p>And the model really can just do it. It knows how to merge two PDFs. Skipping the skill raises no error, and the answer looks fine. Loading a skill is an extra step that the listing has to justify. When the evidence for it is diluted (layer 2), or fuzzy and split across look-alikes (layer 3), the default wins, quietly.</p>

<h3>So why don’t smarter models fix this?</h3>
<p>Because the benchmarks they ace test a different job. A math problem puts everything that matters into the request, at the very end of the context, and the model spends thousands of reasoning tokens on exactly that. Skill selection asks the model to notice, unprompted, that one entry in a listing far back in the prompt applies to this request. It is the difference between solving a problem and remembering to check the handbook. A brilliant professor still forgets to buy milk on the way home. That is not a lack of intelligence; it is a missing cue at the right moment. Psychologists call it prospective memory.</p>
<p>A few more things push in the same direction:</p>
<ul>
<li><b>Position.</b> In a listing of 1,020 entries almost every skill is in the middle, and models use the middle of long inputs worst ({A(L["lost"], "Lost in the Middle")}).</li>
<li><b>Advertised versus effective context.</b> A bigger window means the listing fits, not that it gets weighed. {A(L["ruler"], "RULER")} found that only about half of the models claiming 32K tokens or more actually held up at 32K.</li>
<li><b>Training.</b> Models are rewarded for finishing tasks, not for using your skill, and I doubt agent training often shows them a thousand skills at once. That last part is my guess: I can’t see anyone’s training data.</li>
</ul>
<p>Reasoning does seem to help while the listing fits. GPT ran with medium reasoning and stayed at 99% with 20 skills and 83% with 220. My design cannot separate reasoning from everything else that differs between the two harnesses, though.</p>

<h3>And why do MCP tools bend instead?</h3>
<p>In Claude Code the model never reads all 791 tool definitions. It sees the names, usually writes a {A(L["toolsearch"], "ToolSearch")} query, and reads a handful of results. Retrieval does the haystack part, and attention only has to compare a few candidates. That is the same idea behind the jumps in {A(L["ragmcp"], "RAG-MCP")} (13.6% → 43.1%) and in Anthropic’s {A(L["advtool"], "tool search")} evaluation (49% → 74%). Neither harness I tested has a search step for skills. Every skill is listed in every request, so each new one takes its share.</p>
<p class="callout">The model isn’t failing to reason about your skill. It is failing to notice it, and every skill you add makes noticing harder.</p>

<h2>The big table</h2>
<p>Everything above in one place. “Try” items are ideas to measure, not tested fixes, except where a cell says otherwise.</p>
<div class="wrap"><table class="matrix">
<tr><th>Harness</th><th>Skills</th><th>MCP tools</th><th>Skills + tools</th></tr>
<tr><td><b>Claude Code</b> (Haiku, Sonnet)</td>
<td><b>Insight</b>Steady decline: Sonnet 93% → 34%, Haiku 78% → 16%, starting at 20 skills.<b>Good to know</b>The listing gets 1% of context; descriptions of least-used skills are dropped first. Most misses select no skill.<b>Try</b>Fewer skills per project (the tested manipulation). Check <code>/context</code> and <code>/doctor</code>.</td>
<td><b>Insight</b>Single-step tools: 86–92% → 77–78%, flat from 220 to 791 tools.<b>Good to know</b>Tools are deferred behind ToolSearch, used in 81–95% of runs. Multi-step browser tasks were not observable in my stub.<b>Try</b>Turn off servers with near-duplicate tools. Keep tool names and descriptions specific.</td>
<td><b>Insight</b>Skill requests −48 to −59 points; tool requests −9 to −18.<b>Good to know</b>Misses went into <code>Glob</code>/<code>Grep</code>/<code>Read</code>. Overlapping MCP servers took a few skill requests.<b>Try</b>Invoke critical skills by name (<code>/pdf</code>). Enable skills per project.</td></tr>
<tr><td><b>Codex</b> (GPT)</td>
<td><b>Insight</b>Near perfect up to 220 skills (83%), then 10% at 1,020.<b>Good to know</b>The listing gets 2% of context, max 10K tokens. Token counts suggest the listing stopped growing. A quarter of misses were look-alikes, some fine.<b>Try</b>Stay well under the cap. Raise <code>skills.max_context_tokens</code> (untested; you pay for it on every request).</td>
<td><b>Insight</b>87% alone; 92% for single-step tools with 20 (partial data).<b>Good to know</b>Per-run tokens grew with every definition I added, so all tools appear to be in context. At 791 tools I estimate about $2 per request.<b>Try</b>Connect only the servers a project needs.</td>
<td><b>Insight</b>Not measured: about $1.5–2.2 per run on the API.<b>Good to know</b>The cost is the same mechanism: every definition, every request.<b>Try</b>Same as both columns to the left.</td></tr>
</table></div>

<h2>What you can do about it</h2>
<p>Here is everything I found people doing. Only the first was part of my experiment, so treat the rest as options to measure. Each one goes after a layer from “Why does this happen?”: fewer skills means fewer shares of attention, a unique trigger gives the model a literal match, a bigger budget makes sure the description is shown at all, a hook or router makes the model look before it acts, and search swaps the crowd for a shortlist.</p>
<h3 id="trick-fewer">[Trick #1] Install fewer skills and servers, per project</h3>
<p>This is the one thing my data supports directly: fewer installed components meant more frequent selection of the right one (I did not measure answer quality). Enable plugins per project, turn off skills you do not use with <code>/skills</code>, and run <code>/skill-doctor</code> in Claude Code to find the ones that never fire. If you only need <code>pdf</code> from a 3,000-skill collection, install <code>pdf</code>. And if you install two collections as plugins, every skill they share is listed twice, so keep one copy.</p>
<h3>[Trick #2] Check what the model can actually see</h3>
<p>In Claude Code, <code>/context</code> shows the size of your skill listing and <code>/doctor</code> tells you whether descriptions are being dropped. Codex prints a warning when it goes over its 2% budget ({A(L["c19679"], "codex#19679")}). Blake Crosley wrote a good account of {A(L["crosley"], "the skills his agent could not see")}.</p>
<h3>[Trick #3] Give your skill a trigger nobody else has</h3>
<p>The survivors in my sample had concrete nouns and file types (<code>.canvas</code>, <code>.xlsx</code>, “grill”), while the casualties described generic activities (“audit”, “debug”, “secure”). That is an observation, not a controlled test, but it costs nothing to try.</p>
<h3>[Trick #4] Raise the listing budget</h3>
<p>Claude Code has <code>skillListingBudgetFraction</code> and Codex has <code>skills.max_context_tokens</code>. More descriptions survive, but you pay for them on every request. It would also not explain the drop I saw at just 20 skills.</p>
<h3>[Trick #5] Use a router skill or a hook</h3>
<p>Several repos ship one skill that points to the rest (<code>ask-matt</code>, <code>using-agent-skills</code>). Scott Spence measured {A(L["spence"], "a hook that makes Claude evaluate skills before answering")}: 84% activation against 20% for a simple keyword hook. Ivan Seleznov ran {A(L["seleznov"], "650 activation trials")} on similar ideas.</p>
<h3 id="trick-search">[Trick #6] Search instead of listing</h3>
<p>For MCP, Claude Code already defers tools behind {A(L["toolsearch"], "tool search")}, and my tool curves went flat after 220 tools while the skill curves kept falling. Nothing like that exists for skills in the harnesses I tested. If I were building a harness, this is where I would look.</p>
<p><b>If you run your own agent, you have to build this yourself.</b> On the Claude API, the {A(L["toolsearch"], "tool search tool")} lets you mark tools as deferred, so they stay out of the prompt until a search finds them. With any model, the {A(L["ragmcp"], "RAG-MCP")} pattern works: embed every tool and skill description once, retrieve the few closest to each request, and put only those in the prompt. I have not measured either one for skills, so treat them as options to test.</p>

<h2>Check your own agent</h2>
<p>You can get your own numbers in a few minutes. Pick a skill you rely on, write three requests the way you would really ask, and run them in an empty folder:</p>
<pre><code># Claude Code: prints the skill or MCP tool it selected
claude -p "Audit the SEO of my site." --output-format stream-json --verbose --max-turns 3 \\
  | jq -r 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use") | select(.name=="Skill" or (.name|startswith("mcp__")))
           | if .name=="Skill" then "skill: " + .input.skill else "tool: " + .name end'

# Codex: prints the SKILL.md files it read
codex exec --json -s read-only "Audit the SEO of my site." \\
  | grep -o 'skills/[a-z0-9-]*/SKILL.md' | sort -u</code></pre>
<p>Do it for five skills, three requests each, and count the hits. Then repeat with only that one skill enabled. The gap between the two numbers is what your setup is costing you. I would genuinely love to see your numbers.</p>

<h2>What this cost</h2>
<div class="wrap"><table>
<tr><th>Item</th><th class="n">Runs</th><th class="n">Cost</th></tr>
<tr><td>GPT, skills experiment (OpenAI API)</td><td class="n">480</td><td class="n">$119.13</td></tr>
<tr><td>GPT, MCP experiment so far (OpenAI API)</td><td class="n">170</td><td class="n">$52.60</td></tr>
<tr><td><b>Paid in API fees</b></td><td class="n">650</td><td class="n"><b>$171.73</b></td></tr>
<tr><td>Claude Haiku and Sonnet in Claude Code (my Claude subscription; API list price for reference)</td><td class="n">4,020</td><td class="n">$0 extra ($192.61 list)</td></tr>
</table></div>
<p>GPT prices are from {A(L["price"], "OpenAI’s model page")}: $10 input, $1 cached input, $12.50 cache writes and $50 output per million tokens. Writing the prompt prefix (system prompt, skill listing, tools) to the cache was 76–87% of each run’s cost, because every run is a new session. That is also why finishing the GPT MCP experiments in full would cost about $1,400: with 791 tools in context, I estimate about $2 per run.</p>

<h2>Limitations</h2>
<ul>
<li><b>Selection, not quality.</b> I measured whether the designated component was selected, not whether the answer was good. A run without the skill can still produce a fine answer.</li>
<li><b>Requests.</b> I wrote all of them myself, six per target. Different wording would shift the numbers.</li>
<li><b>One sample of extra skills.</b> They came from one big collection, drawn once. A different sample could move the curve.</li>
<li><b>Minimal setup.</b> Empty folders, stub instructions, and 3–4 turns in Claude Code. Real projects with real files may behave differently. In particular, some capped runs might have found the skill later.</li>
<li><b>Configurations, not models.</b> Claude Code and Codex differ in model, prompts, budgets and permissions. Differences between them belong to the whole configuration.</li>
<li><b>GPT data is thinner.</b> One run per request, and only two MCP setups.</li>
<li><b>No raw logs.</b> My runs kept only what the agent called, not its text, so I can say what it did, not why.</li>
</ul>
<p>The full methodology, an external review, and my response to it are in {A(L["repo"], "the GitHub repo")}, along with all the data and the scripts to reproduce every number.</p>

<h2>What’s next</h2>
<p>I have a plan to finish this for under $100 in API fees:</p>
<ul>
<li>Fill in the GPT MCP curve.</li>
<li>Add control requests: “use the pdf skill” and “what is 17 × 23?”.</li>
<li>Re-run the skill crowds with two more random samples.</li>
<li>Give Claude 10 turns instead of 3.</li>
<li>Put real files in the folders.</li>
<li>Re-run the browser tasks with realistic stub responses.</li>
<li>Run a proper crossed design for skills × tools.</li>
</ul>
<p>If you want any of these first, tell me.</p>

<h2>Conclusion</h2>
<p>I started with a simple question: if I install a thousand skills, does my agent get smarter? In this test, it mostly got quieter. The skills are still there, the listing is still sent, you still pay the tokens, but the agent selects the one you meant less and less often, and it does not tell you. MCP tools in Claude Code held up better, probably because they are searched rather than listed. That makes me think the fix for skills will look the same.</p>
<p>Until then: fewer, sharper skills, and a quick check that the ones you have actually get picked. Skills are prompts that behave like software, and we should test them like software.</p>
<p>Thanks for reading! If you run the check on your own setup, tell me what you got.</p>

<h2>References</h2>
<ol class="refs">
<li>Code, data and methodology for this post: {A(L["repo"], "galinaalperovich/in-context-forgetting")}</li>
<li>{A(L["cc_skills"], "Claude Code documentation: Skills")}</li>
<li>{A(L["codex_skills"], "Codex documentation: Build skills")}</li>
<li>{A(L["spec"], "Agent Skills specification")}</li>
<li>{A(L["anth_skills"], "anthropics/skills")} · {A(L["sickn33"], "sickn33/agentic-awesome-skills")} · {A(L["mattpocock"], "mattpocock/skills")} · {A(L["obsidian"], "obsidianmd/obsidian-skills")} · {A(L["marketing"], "coreyhaines31/marketingskills")}</li>
<li>Trending skills: {A(L["hallmark"], "Nutlope/hallmark")} · {A(L["cfsec"], "cloudflare/security-audit-skill")} · {A(L["claudeseo"], "AgriciDaniel/claude-seo")} · {A(L["ffmpeg"], "kajisho5/ffmpeg-skill")} · {A(L["igskill"], "Jakeschincariol/instagram-agent-skill")}</li>
<li>MCP sources: {A(L["ghmcp"], "github/github-mcp-server")} · {A(L["cdt"], "ChromeDevTools/chrome-devtools-mcp")} · {A(L["pwmcp"], "microsoft/playwright-mcp")} · {A(L["livemcp_gh"], "LiveMCPBench")}</li>
<li>Gan &amp; Sun. {A(L["ragmcp"], "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation")} (2025)</li>
<li>{A(L["livemcp"], "LiveMCPBench: Can agents navigate an ocean of MCP tools?")}</li>
<li>Anthropic: {A(L["toolsearch"], "Tool search tool")} · {A(L["advtool"], "Advanced tool use")}</li>
<li>Skill complaints: {A(L["i81081"], "claude-code#81081")} · {A(L["i56710"], "#56710")} · {A(L["i64606"], "#64606")} · {A(L["i10768"], "#10768")} · {A(L["c19679"], "codex#19679")} · {A(L["r_cc"], "r/ClaudeCode")} · {A(L["r_hell"], "r/claudeskills")} · {A(L["fsck"], "Jesse Vincent")}</li>
<li>MCP complaints: {A(L["i6915"], "claude-code#6915")} · {A(L["i7328"], "#7328")} · {A(L["i37793"], "#37793")} · {A(L["i11364"], "#11364")} · {A(L["cursor40"], "Cursor forum 1")} · {A(L["cur79686"], "Cursor forum 2")} · {A(L["g21823"], "gemini-cli#21823")} · {A(L["r_mcp1"], "r/mcp 1")} · {A(L["r_mcp2"], "r/mcp 2")}</li>
<li>{A(L["spence"], "Scott Spence: How to make Claude Code skills activate reliably")} · {A(L["seleznov"], "Ivan Seleznov: 650 trials")} · {A(L["crosley"], "Blake Crosley: The skills my agent could not see")}</li>
<li>{A(L["price"], "OpenAI: gpt-6-astra model page and pricing")}</li>
<li>Vaswani et al. {A(L["vaswani"], "Attention Is All You Need")} (2017)</li>
<li>Liu et al. {A(L["lost"], "Lost in the Middle: How Language Models Use Long Contexts")} (TACL 2024)</li>
<li>Hsieh et al. {A(L["ruler"], "RULER: What’s the Real Context Size of Your Long-Context Language Models?")} (COLM 2024)</li>
<li>Modarressi et al. {A(L["nolima"], "NoLiMa: Long-Context Evaluation Beyond Literal Matching")} (ICML 2025)</li>
<li>Hong, Troynikov &amp; Huber. {A(L["rot"], "Context Rot: How Increasing Input Tokens Impacts LLM Performance")} (Chroma, 2025)</li>
<li>Nakanishi. {A(L["ssmax"], "Scalable-Softmax Is Superior for Attention")} (2025)</li>
<li>Anthropic. {A(L["ctxeng"], "Effective context engineering for AI agents")}</li>
<li>Kirkpatrick et al. {A(L["ewc"], "Overcoming catastrophic forgetting in neural networks")} (PNAS 2017)</li>
</ol>
</article>
"""
html = f'<title>Catastrophic Forgetting, In-Context</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">\n<style>{css}</style>\n{body}'
open(os.path.join(B, "skills-mcp-post.html"), "w").write(html)
print("ok", len(html))
