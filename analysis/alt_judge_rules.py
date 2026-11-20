import json, sys, collections
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, 'alt_judge_input.json')
out = os.path.join(HERE, 'alt_judgments.json')
d = json.load(open(src))

P, E, R, I, U = 'preliminary_step', 'equivalent', 'related_partial', 'inappropriate', 'unassessable'
INTRO = {'mcp:codex.list_mcp_resources', 'mcp:codex.list_mcp_resource_templates',
         'mcp:chrome_devtools.list_mcp_resources', 'mcp:chrome_devtools.list_mcp_resource_templates'}

def judge(x):
    t, a, r = x['designated_target'], x['alternative'], x['request']
    # --- generic MCP introspection calls (not in inventory)
    if a in INTRO:
        return I, 'Generic MCP resource listing; neither performs nor sets up the requested browser operation.'
    # --- browser targets
    if t in ('chrome-devtools.performance_start_trace', 'chrome-devtools.lighthouse_audit', 'chrome-devtools.list_console_messages'):
        op = {'chrome-devtools.performance_start_trace': 'trace',
              'chrome-devtools.lighthouse_audit': 'Lighthouse audit',
              'chrome-devtools.list_console_messages': 'console read'}[t]
        if a in ('mcp:chrome-devtools.new_page', 'mcp:chrome-devtools.navigate_page'):
            return P, f'Opens the URL in the same Chrome; sensible first step before the {op}.'
        if a == 'mcp:chrome-devtools.list_pages':
            return P, f'Checks open pages before loading the URL; orientation step toward the {op}.'
        if a == 'mcp:chrome-devtools.emulate':
            return P, 'Sets mobile emulation before auditing; setup step, does not run Lighthouse.'
        if a == 'mcp:desktop-commander.start_process':
            return E, 'A shell can run the Lighthouse CLI against the URL and list top issues.'
        if a == 'mcp:playwright-mcp.browser_navigate':
            if op == 'trace':
                return R, 'Loads page in Playwright, which lacks a performance-trace tool; does not set up the trace.'
            return P, 'Loads the page in Playwright, which can then read console messages.'
        if a == 'mcp:playwright-mcp.browser_wait_for':
            return P, 'Waits for the page to finish loading before reading console; setup step.'
        if a == 'mcp:playwright-mcp.browser_take_screenshot':
            return I, 'A screenshot does not capture console output.'
    if t == 'playwright-mcp.browser_take_screenshot':
        if a in ('mcp:playwright-mcp.browser_navigate', 'mcp:puppeteer.puppeteer_navigate',
                 'mcp:chrome-devtools.new_page', 'mcp:chrome-devtools.navigate_page'):
            return P, 'Navigates to the URL; required first step before capturing the screenshot.'
        if a == 'mcp:playwright-mcp.browser_resize':
            return P, 'Sets viewport size before the capture; setup step, no screenshot taken.'
        if a == 'mcp:playwright-mcp.browser_wait_for':
            return P, 'Waits for page load before the capture; setup step, no screenshot taken.'
        if a == 'mcp:fetch.fetch':
            return R, 'Returns page text for "what is on it" but no screenshot.'
    if t == 'playwright-mcp.browser_fill_form':
        if a in ('mcp:playwright-mcp.browser_navigate', 'mcp:puppeteer.puppeteer_navigate'):
            return P, 'Opens the form page; required first step before filling the fields.'
        if a == 'mcp:playwright-mcp.browser_snapshot':
            return P, 'Gets element refs needed to fill fields; preparatory step, fills nothing.'
        if a == 'mcp:playwright-mcp.browser_take_screenshot':
            return P, 'Observes the page (vision workflow) before filling; does not enter any values.'
        if a == 'mcp:playwright-mcp.browser_evaluate':
            return R, 'JS could set the field value but bypasses real input; page not yet loaded.'
        if a == 'mcp:fetch.fetch':
            return I, 'Static fetch cannot interact with or fill a web form.'
        if a == 'mcp:playwright-ea.playwright_get':
            return I, 'Plain HTTP GET cannot fill in a browser form.'
    # --- github
    if t == 'github.create_pull_request':
        if a == 'mcp:github.list_pull_requests':
            return P, 'Checks for an existing PR before opening one; does not create it.'
        if a == 'mcp:github.list_branches':
            return P, 'Verifies the branch exists before opening the PR.'
        if a == 'mcp:github.list_commits':
            return P, 'Reads branch commits to write the PR description; does not create the PR.'
        if a == 'mcp:github.search_code':
            return I, 'Code search does not help open a PR whose branch and title are given.'
    if t == 'github.create_issue':
        if a in ('mcp:github.list_issues', 'mcp:github.search_issues'):
            return P, 'Checks for a duplicate issue before filing; does not create it.'
        if a == 'mcp:github.get_me':
            return P, 'Gets own username needed for the assignment; does not create the issue.'
        if a in ('mcp:github.search_code', 'mcp:github.get_file_contents', 'mcp:github.get_repository_tree'):
            return P, 'Locates the broken install-page link to describe in the issue; does not file it.'
    # --- charts / data
    if t == 'mcp-server-chart.generate_bar_chart':
        if a == 'skill:dataviz':
            return E, 'Name indicates a chart-making skill; can produce the requested column chart.'
        if a == 'mcp:mcp-server-chart.generate_dual_axes_chart':
            return R, 'Bar+line combo chart; not the plain column chart requested.'
    if t == 'xlsx':
        if a == 'mcp:excel.excel_write_to_sheet':
            return R, 'Writes cell values; file creation and formula support not evident from description.'
        if a == 'mcp:excel.excel_describe_sheets':
            return P, 'Inspects the workbook sheets first; does not make the chart.'
        if a == 'skill:dataviz':
            return R, 'Covers the chart but not spreadsheet handling; chart-in-workbook reading unserved.'
    if t == 'docx':
        if a == 'mcp:word-document-server.get_document_text':
            return E, 'Directly extracts all text from the Word document.'
        if a == 'mcp:word-document-server.list_available_documents':
            return P, 'Locates the .docx file first; does not perform the edit or extraction.'
        if a == 'mcp:word-document-server.create_document':
            return P, 'Creates the .docx; first step, letter content still to be added.'
        if a == 'mcp:word-document-server.add_paragraph':
            return R, 'One building block of the letter; needs document creation and formatting too.'
    if t == 'pdf' and a == 'mcp:filesystem.list_allowed_directories':
        return P, 'Finds accessible directories to locate the PDF; no PDF operation performed.'
    if t == 'pptx' and a == 'mcp:ppt.list_presentations':
        return P, 'Lists loaded presentations before combining; does not merge them.'
    if t == 'json-canvas' and a == 'mcp:basic-memory.list_directory':
        return P, 'Locates planning.canvas first; does not edit the canvas.'
    if t == 'obsidian-markdown':
        if a == 'mcp:basic-memory.search_notes':
            if 'embeds' in r:
                return P, 'Finds the source note with the diagram before writing the embed.'
            return P, 'Looks up Atlas and people in notes before writing; no Obsidian syntax help.'
        if a == 'mcp:memory.search_nodes':
            return P, 'Looks up Atlas people in the knowledge graph before writing the note.'
        if a == 'mcp:basic-memory.list_memory_projects':
            return P, 'Orients in the notes store before finding the source note; writes nothing.'
    if t == 'time.convert_time':
        if a == 'mcp:12306-mcp.get-current-date':
            return I, 'Returns only the date (Shanghai), not the current time asked for.'
        if a == 'mcp:fetch.fetch':
            return R, 'Could fetch a time service page; indirect, depends on finding one.'
    if t == 'context7.get-library-docs' and a == 'mcp:fetch.fetch':
        return E, 'Fetching the official Tailwind v4 docs page gives the same up-to-date content.'
    # --- seo
    if t == 'seo':
        if a == 'skill:seo-audit':
            return E, 'Dedicated SEO audit skill; covers a full site SEO analysis.'
        if a == 'mcp:fetch.fetch':
            return P, 'Fetches the site content for analysis; does not analyze SEO itself.'
        if a == 'mcp:sitemap.get_sitemap_stats':
            return R, 'Sitemap stats cover one facet of an SEO analysis.'
    if t == 'seo-audit':
        if a == 'skill:canonical-tag-checker':
            if 'hreflang' in r:
                return R, 'Covers canonical tags but not hreflang.'
            return R, 'Canonicals are one possible indexing cause; not a full indexing diagnosis.'
        if a == 'skill:diagnosing-bugs':
            return I, 'Software bug diagnosis skill; matches only on "diagnose", not SEO indexing.'
        if a == 'skill:seo-technical':
            return E, 'Technical SEO audit skill; matches the requested technical SEO check.'
        if a == 'mcp:excel.excel_describe_sheets':
            return I, 'No spreadsheet mentioned; inspecting Excel sheets does not address traffic drop.'
    # --- skills: design / ui
    if t == 'frontend-design':
        if a == 'skill:better-ui':
            return R, 'Polish-level details (radius, shadows, icons); not aesthetic direction, typography or color.'
        if a == 'skill:build-design':
            return I, 'Implements from a Figma file or image; no design source exists here.'
        if a == 'skill:hallmark':
            return E, 'Design skill for new pages that do not look generated; same task.'
        if a == 'skill:landing-page':
            return E, 'Builds non-generic landing pages; directly fits the request.'
        if a == 'skill:artifact-design':
            return U, 'Description not captured; name does not show whether it covers website design.'
    if t == 'hallmark' and a == 'skill:landing-page':
        return E, 'Builds landing/home/product-style pages that avoid AI look; same task.'
    if t == 'web-design-guidelines':
        if a == 'skill:accessibility-compliance-accessibility-audit':
            if 'interaction' in r:
                return R, 'Covers accessibility (keyboard, focus) but not broader interaction details.'
            return E, 'WCAG accessibility audit skill; matches an accessibility review.'
        if a == 'skill:accessibility-engineering':
            return E, 'Accessibility audit and remediation skill; matches an accessibility code review.'
        if a == 'skill:better-interface':
            return E, 'Reviews interface across a11y, layout, typography; equivalent UI/UX review.'
        if a == 'skill:design-how-ui-review':
            return E, 'UI review ranking usability and accessibility defects; equivalent review.'
        if a == 'mcp:chrome-devtools.list_pages':
            return P, 'Identifies "this page" among open browser pages before auditing.'
    if t == 'animate' and a == 'skill:animation-performance':
        return R, 'Covers smoothness/perf of motion, not building the removal transition.'
    if t == 'humanizer' and a == 'skill:better-writing':
        return I, 'Interface copy skill (labels, errors); not removing AI tells from prose.'
    if t == 'vercel-react-best-practices' and a == 'skill:react-best-practices':
        return E, 'Near-duplicate React performance guide adapted from Vercel guidance.'
    if t == 'tdd' and a == 'skill:test-driven-development':
        return E, 'Near-duplicate test-first development skill.'
    if t == 'grill-me' and a == 'skill:interview-me':
        return E, 'One-question-at-a-time interview skill; matches "interview me" about the plan.'
    if t == 'diagnosing-bugs' and a == 'skill:debugging-strategies':
        return E, 'General systematic debugging skill; covers this diagnosis task.'
    # --- security
    if t == 'security-audit' and a == 'skill:security-review':
        return E, 'Name matches the request directly: a security review skill.'
    if t == 'security-and-hardening':
        if a == 'skill:auth-implementation-patterns':
            return E, 'Reviews token/session handling explicitly; fits the session-token review.'
        if a == 'skill:backend-security-coder':
            return E, 'Secure backend coding with input validation; fits hardening an upload endpoint.'
        if a == 'skill:api-security':
            return R, 'API pentest methodology; only partly matches a code-level webhook handler review.'
        if a == 'skill:find-bugs':
            if 'before we ship' in r:
                return E, 'Security review of pending branch changes; fits a pre-ship handler check.'
            return R, 'Scoped to branch changes and general bugs; partly fits auditing one handler.'
    # --- mcp-builder
    if t == 'mcp-builder':
        if a == 'skill:tool-design':
            return E, 'Designing agent tool definitions is exactly the question asked.'
        if a == 'skill:api-designer':
            return I, 'Produces REST endpoint specs, not MCP tool design; shares only "API/design".'
        if a == 'skill:api-integration':
            return I, 'Event-driven/webhook/ETL integration patterns; no MCP server guidance.'
    # --- webapp-testing
    if t == 'webapp-testing':
        if a == 'mcp:playwright-mcp.browser_navigate':
            return P, 'Opens the local app in a browser; first step toward the requested check.'
        if a == 'mcp:playwright-mcp.browser_snapshot':
            return P, 'Inspects page structure before acting or writing locators; performs no check.'
        if a == 'mcp:playwright-mcp.browser_tabs':
            return P, 'Manages browser tabs before navigating; orientation step only.'
        if a == 'mcp:chrome-devtools.list_pages':
            return P, 'Checks open browser pages before loading the local app; orientation step.'
        if a == 'skill:run':
            return U, 'Description not captured; name "run" does not settle what it covers.'
        if a == 'skill:browser-harness':
            return R, 'Drives an existing browser via CDP; does not cover starting and verifying the app.'
        if a == 'skill:browser-automation':
            if 'login form' in r or 'Playwright script' in r:
                return E, 'Guides building reliable browser checks; fits verifying the form/page.'
            if 'console errors' in r:
                return R, 'Covers scripted flows but not capturing console errors.'
            if 'debug' in r:
                return R, 'Oriented to building checks, not debugging a dead button.'
            if 'screenshot' in r:
                return R, 'Oriented to building checks, not screenshotting and visual inspection.'
    return None, None

res = []
miss = []
for x in d:
    lab, why = judge(x)
    if lab is None:
        miss.append(x)
    res.append({'id': x['id'], 'label': lab, 'reason': why})
if miss:
    for m in miss: print('MISSING', m['id'], m['request'])
    sys.exit(1)
VOC = {P, E, R, I, U}
assert len(res) == 210 and len({r['id'] for r in res}) == 210
assert {r['id'] for r in res} == {x['id'] for x in d}
assert all(r['label'] in VOC for r in res)
long = [r for r in res if len(r['reason'].split()) > 20]
assert not long, long
json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
print(collections.Counter(r['label'] for r in res))
