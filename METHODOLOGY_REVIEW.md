# Methodology review and executor handoff

Review date: 20 November 2026.

Reviewed: `METHODOLOGY.md`, `../blog/skills-blog-post.html`, `build.py`, `run.py`, `run_codex.py`, `mcp/build_v2.py`, `mcp/run2.py`, and the existing result JSONL files. This is a review and implementation brief, not a revised protocol or an instruction to launch paid runs. Counts below describe the files inspected during this review; recheck files that are still receiving results.

## 1. Decision and scope

Keep the existing experiment as exploratory evidence. Its Experiment 1 hit totals reproduce the methodology table. The core observation is useful: designated-target selection declines across the tested installed collections. The current evidence does not establish task-quality loss, the mechanism causing the decline, or the behaviour of arbitrary installations.

Do not discard the existing data or silently replace historical scores. Preserve original records and produce versioned derived analysis. Some limitations can remain if the claim is narrowed. Others require analysis corrections regardless of wording. New experiments are necessary only for claims the current design cannot support.

Recommended research question for the existing study:

> In these model–harness configurations, how often is a designated skill or accepted MCP operation selected within the observation window as the installed collection changes?

Distinguish three questions throughout:

1. **Target retention:** was the designated component selected?
2. **Appropriate routing:** was an acceptable component selected for the request?
3. **Task performance:** was the request completed correctly?

The existing study measures proxies for the first two. It does not measure the third.

## 2. Classification and priorities

The categories are not mutually exclusive. A setup choice can remain while its analysis and description need correction.

| Item | May remain as disclosed setup | Required correction before publication | New data needed for stronger claims |
|---|---|---|---|
| Fixed turn limits | Yes, for bounded selection | Separate budget exhaustion; state observation window | Larger-budget sensitivity / aligned decision opportunity |
| Exact-target skill scoring | Yes, as target retention | Stop calling every alternative wrong | Independent accepted-set validation where existing evidence is insufficient |
| Stub instructions/results | Yes, for initial routing | Separate selections before and after synthetic feedback | Realistic fixtures/results for multistep behaviour |
| Empty working directory | Yes, as a minimal-context test | Stop presenting it as ordinary task execution | Fixture-backed validation |
| One filler sample | Yes, as a case study | Limit inference to that collection | Multiple filler samples for generalization |
| Unequal repetitions | Yes | Show denominators; use paired uncertainty | More balanced repetitions if comparing stochastic reliability |
| Native built-ins and discovery | Yes | Inventory them; compare model–harness pairs | Controlled exposure for model-only or mechanism claims |
| Mixed API/subscription access | Yes, with batch labels | Report separately where possible; do not assume equivalence | Matched bridge sample if pooling needs validation |
| Browser-family scoring | Only as a secondary routing measure | Rename; strict operation metric must be distinct | Realistic browser state for completion claims |
| Codex path-regex detector | Historical proxy only | Document limitations; improve future logging/detection | Validation reruns when raw evidence is absent |
| Two mixed setups | Yes, as constructed scenarios | Remove causal interaction and “typical user” claims | Crossed design for interaction |
| Reconstructed schemas | Yes, with fidelity labels | Validate schemas; avoid claiming all definitions are exact | Exact schema subset / sensitivity if needed |
| Static survey | Yes, as a selected corpus | Bound claims to what the scanner detects | Broader sampling needed for ecosystem prevalence |

Priorities: **P0** = correct before publishing the affected claim; **P1** = implement before new confirmatory runs; **P2** = optional extension tied to a stronger research question.

## 3. P0: corrections to existing analysis

### 3.1 Separate observation-window exhaustion from ordinary completion

Evidence: `run.py` records the result subtype but only sets `error` when no result subtype exists. Thus `error_max_turns` is retained without an `error` flag. `mcp/run2.py` uses the same general pattern for Claude results.

Observed Experiment 1 counts:

| Model | Setup | Runs | Ended at turn limit | Ended at limit without target hit |
|---|---|---:|---:|---:|
| Haiku | alone | 120 | 13 | 5 |
| Haiku | pack20 | 120 | 32 | 26 |
| Haiku | crowd200 | 120 | 53 | 47 |
| Haiku | crowd1000 | 120 | 60 | 56 |
| Sonnet | alone | 360 | 2 | 0 |
| Sonnet | pack20 | 360 | 3 | 3 |
| Sonnet | crowd200 | 360 | 55 | 55 |
| Sonnet | crowd1000 | 360 | 71 | 71 |

Totals: 158/480 Haiku runs and 131/1,440 Sonnet runs ended at the turn limit. This establishes substantial truncation of observation; it does not establish that those runs would eventually select the target.

Executor actions:

- Derive `termination_status` independently of the selection outcome: completed, turn_limit, timeout, API_error, harness_error, unknown.
- Retain turn-limited runs in the denominator for “selected within the allotted window.” A hit before exhaustion remains a hit for that metric.
- Report target hit, alternative selection, and no observed selection by termination status. A capped target miss is not necessarily a no-skill run.
- Do not exclude capped runs and call the remainder unbiased. Exclusion preferentially removes harder runs and larger catalogs.
- Correct “no errors remained”: distinguish retried infrastructure errors from retained budget-exhausted runs.
- Replace “this favours Codex slightly” with “this makes direct cross-harness comparison difficult; the size and direction of its effect are not quantified.”

Acceptance: every table has an explicit denominator and observation window; termination counts reproduce the source files; no claim equates “not observed within the window” with “never selected.”

### 3.2 Preserve exact-target scoring, but stop equating it with correctness

An alternate debugging, SEO, or document skill may be appropriate. This matters particularly when added fillers supply competing valid capabilities. Exact-target scoring is legitimate if the question is whether an installed favourite continues to activate.

Executor actions:

- Rename the existing metric `designated_target_selection` in prose and derived outputs.
- Retain the original scores for comparability.
- Add a separate acceptable-component analysis where the retained records allow it. Define acceptable sets per request, since a tool or skill can fit one request and not another within the same target group.
- Review the candidate inventory, rather than accepting only alternatives that happened to be chosen. Use independent review where feasible.
- Label any accepted sets developed after seeing results as retrospective/exploratory. Freeze them before new runs.
- Do not infer task completion or answer quality from an acceptable selection.

Acceptance: a target miss can be an appropriate alternative, an inappropriate alternative, no observed selection, or unassessable. These are not silently collapsed into “wrong.”

### 3.3 Separate first selection from behaviour after stub feedback

Methodology §4.3 says only the initial selection is meaningful, while §4.5 scores a target selected at any time. Stub instructions explicitly tell the agent to stop with a short reply. Stub MCP results and permission rejections also alter later decisions.

Executor actions:

- Retain the historical any-time metric, labeled as behaviour in a stubbed environment.
- Derive first observed skill selection from `fired` where possible. Explain that this is a proxy, not a reconstruction of the full first decision: built-in actions or built-in skill results may have preceded it.
- For MCP, first recorded distinct component in `used` is not a complete event trace. ToolSearch is stored separately, repeated calls are deduplicated, and arguments/results may be absent. Do not claim recovery of information that was never recorded.
- For new runs, record ordered events and identify the first selection batch before any stub result, denial, or synthetic instruction is delivered. Define how parallel selections are scored.
- If sequential behaviour is a desired endpoint, replace terminal stubs with controlled realistic responses and define that as a separate protocol.

Acceptance: headline claims do not use post-stub actions as evidence of unmodified agent behaviour. Missing historical evidence is marked unknown.

### 3.4 Separate browser-server routing from operation selection

`mcp/run2.py` treats any call to specified browser servers as a hit for browser targets. A server-level match does not prove the requested screenshot, trace, console inspection, or audit was attempted. `OVERLAP` also contains broad server prefixes; any Excel call is not necessarily an appropriate response to an Excel request.

Executor actions:

- Preserve the old family score as `capable_server_selected`, a secondary measure.
- Report `hit_strict` separately as accepted tool-name selection. Make clear that without arguments it still does not prove the right operation was requested: for example, a multi-operation issue tool may need a create-specific argument.
- Make request-appropriate operation selection the primary MCP metric where arguments are available; otherwise explicitly use tool-name selection.
- Replace overlap-prefix assertions with request-specific acceptable operations where evidence permits. Rename unverifiable historical flags to “overlapping server/tool family selected.”
- Do not describe a request as “served” solely because an overlap flag is true.

Acceptance: strict tool selection, capable-server routing, and task completion are never interchangeable labels.

### 3.5 Audit detection, infrastructure failures, and retry accounting

Codex runners match `skills/<name>/SKILL.md` in command text. This can count an unsuccessful read or a non-reading command and miss a read through variables or different paths. A completed command event is not proof of a successful file read. Claude Skill calls similarly demonstrate an attempt unless loading success is verified.

Executor actions:

- Label historical detection accurately: Claude invocation attempt / Codex matching command proxy.
- For future logs, retain command, exit status, output, tool arguments, tool results, and event ordering. Distinguish attempted from confirmed loading.
- Validate detection against a manually checked sample stratified by harness and catalog size, including apparent hits and misses. If historic logs are absent, perform a small validation rerun and disclose that it cannot retroactively certify every old record.
- Inventory API errors, process return codes, absent final events, failed MCP connections, and missing target exposure. Failure to connect should not be silently interpreted as model non-selection.
- Define whether infrastructure availability is part of an end-to-end endpoint or an exclusion for a routing endpoint. Report availability either way.
- Deduplicate retry records using a documented logical-run key. Retain all attempts separately; choose the retained attempt by a fixed rule, never by whether it hit.

Acceptance: selection, execution, and infrastructure availability have separate fields; derived denominators can be independently reproduced.

### 3.6 Revise uncertainty and comparisons

The 2,400 runs reuse 120 requests attached to 20 skills. Repetitions are not independent new task scenarios. Request-cluster intervals improve on independent-run intervals, but do not capture skill sampling, filler-set sampling, or generalization to arbitrary users.

Executor actions:

- Report paired condition differences, preserving the same requests across conditions in each resample. Average repetitions within request/condition as appropriate.
- State the inferential target: variation over these requests, over target skills, or over installations. Choose resampling accordingly. For a broader skill claim, include a skill-level or hierarchical sensitivity analysis and acknowledge only 20 selected skills.
- Do not resample conditions independently when estimating paired changes.
- Annotate GPT alone's bootstrap `100–100%`: resampling all-success observations cannot reveal unseen failures. Keep an appropriately qualified interval/model for uncertainty; do not imply certainty about future prompts.
- Remove the blanket claim that setup-level intervals do not overlap. Several adjacent intervals in §4.7 do overlap. Interval overlap is not the appropriate paired significance test anyway.
- Publish analysis code, resampling seed, weighting rule, exclusion rule, and denominators.

Acceptance: no claim treats runs as 2,400 independent tasks, or uses non-overlap as a universal justification for the trend.

## 4. Setup choices that may remain, with explicit boundaries

### 4.1 Empty folders and restrictive permissions

These can remain in a minimal-context routing benchmark. Describe the missing inputs and permissions near the methods and main results, not only in the limitations. Do not infer why the agent abstained when its text is unavailable. “It was confident it could do that itself” is unsupported without direct evidence.

For normal-workflow claims, add valid small files, a minimal repository, and controlled browser pages. Keep fixtures identical across catalog conditions. Track missing-input/clarification responses separately where logs permit.

### 4.2 One source collection, one filler seed, authored requests

These can remain for an exploratory case study. Say “one sampled collection” and “experimenter-written requests.” Random sampling from one repository does not make it a representative sample of user installations. Added skills are not necessarily unrelated; several intentionally or accidentally overlap with targets.

Claims about installations in general require several sampled catalogs. More repetitions of the same requests in one catalog are not a substitute. Human-authored requests are acceptable; independent sourcing or review strengthens external validity but is not a prerequisite for reporting this case study.

### 4.3 Native harness behaviours and built-ins

Built-in skills/tools, catalog compression, and tool discovery can remain: these are part of an end-to-end harness test. Record them. “Alone” means one experimental skill, not one available capability. Use an observed inventory rather than assuming a fixed built-in count across versions.

The systems differ in model, harness, tool affordances, budgets, and permissions. Call them model–harness configurations. Do not attribute their differences purely to model intelligence or purely to harness implementation.

### 4.4 Repetitions, versions, and access routes

Unequal repetition counts can remain if disclosed and analyzed correctly. Date and version pinning are useful. Record resolved model IDs when available; an alias and an asserted model version are not equivalent evidence.

API and subscription runs may remain as distinct batches. Tag access route, runner version, and configuration. If access route changed partway through ordered conditions, its effect may be confounded with condition. A small matched bridge sample can assess this; do not assume identical model names establish identical execution environments.

### 4.5 Static survey and reconstructed MCP definitions

Keep the static corpus survey, but call it a selected sample of popular repositories, not a verified ranking of the globally most popular repositories. “Distinct skills” here means distinct file contents under the stated hash rule, not distinct capabilities.

The scanner detects certain file patterns. “No detected bundled tests” does not mean the skill has never been tested; tests may be external or at repository level. Conversely, a matching filename does not establish a meaningful evaluation. Low detected defect rates do not establish runtime correctness.

Reconstructed MCP schemas may remain with provenance and fidelity labels. Do not assert that schema differences cannot affect selection. Validate required fields/types and audit representative schemas against the pinned source. Define a sensitivity subset using exact schemas if fidelity becomes central to the claim.

## 5. New experiments needed only for stronger claims

### 5.1 Mechanism: visibility, catalog length, or semantic competition?

Installed counts do not establish what the model saw. The official Codex documentation describes both shortening descriptions and possible omission from the initial catalog: https://learn.chatgpt.com/docs/build-skills (checked during this review). Documentation supports plausibility, not the causal explanation for these specific runs; current documentation also does not prove historical-version behaviour.

For a mechanism experiment:

- Capture the rendered catalog or the closest verifiable representation, including target presence, surviving description length, position, paths, and total size.
- Distinguish discovered, listed, retrieved, selected, and successfully loaded.
- Compare similarly sized catalogs with related versus unrelated fillers while holding target exposure constant.
- Where supported, compare catalog budgets at fixed installed contents. Treat any instrumented or overridden harness as a separate configuration.
- Measure actual order; do not assume shuffling filesystem creation order shuffles the model's catalog.

If capture is unavailable, leave the mechanism unresolved. That is an acceptable limitation for the end-to-end study.

### 5.2 Interaction between skills and MCP tools

The current mixed scenarios change skills and tools simultaneously. Keep them as two constructed scenarios, renamed “mixed smaller” and “mixed larger,” unless real-installation data justify “typical.”

To claim interaction, add a crossed design using the same targets and requests:

| | Fewer tools | More tools |
|---|---|---|
| Fewer skills | A | B |
| More skills | C | D |

Use nested sampled pools and paired runs. Estimate the difference between the tool-load effects at the two skill levels, with uncertainty. An all-zero experimental-component control can help characterize baseline built-in behaviour, but does not itself identify the interaction.

### 5.3 Robustness and ordinary workflows

Before a larger confirmatory campaign, prioritize a small validation study:

1. Validate logging and detectors.
2. Compare empty-folder versus fixture-backed requests.
3. Compare original versus larger observation budgets using paired cases selected without reference to favourable outcomes.
4. Use multiple filler seeds and randomize execution order across conditions.
5. Add explicit skill-invocation positive controls and unrelated-request negative controls. Keep control scores separate from natural-request activation scores.

The number of seeds, requests, and repetitions should follow a prespecified precision/budget target. No arbitrary minimum guarantees a sound study. Do not launch a larger run before the small validation confirms that the measurement pipeline works.

## 6. Wording changes for the methodology and blog

These are suggested replacements, not assertions of new results.

| Current wording or implication | Fairer replacement |
|---|---|
| “Why your AI agent ignores its skills” | “When installed skills stop being selected: an experiment with Claude Code and Codex” |
| “The right skill fired” | “The designated target skill was selected under our detection rule” |
| “Wrong skill” | “A different skill was selected; some alternatives may be appropriate” |
| “Most misses are silence” | “Most target misses involved no detected skill selection within the observation window” |
| “The agent just starts working” | Use only where retained traces establish this; otherwise state that no skill selection was detected |
| “Stubbing does not change the result” | “Stubbing preserves the tested metadata, but changes subsequent behaviour; initial routing and later actions are analyzed separately” |
| “Only the target skill is installed” | “Only the target experimental skill is installed; harness-provided capabilities remain” |
| “20 good, unrelated skills” / “unrelated fillers” | “20 selected skills” / “sampled additional skills, some overlapping with targets” |
| “The harnesses fail differently” | “The tested model–harness configurations show different selection curves” |
| “Codex's budget causes the cliff” | “Catalog limits are one plausible explanation; target visibility was not directly measured” |
| “Distinctive names/triggers survive” | “Several distinctive targets retained higher selection rates in this sample; the design does not isolate the effect of distinctiveness” |
| “The model was confident it could do it itself” | “The target was not selected; the retained data do not establish the reason” |
| “Same mechanism, same failure” as MCP | “A related routing problem; shared mechanisms remain to be tested” |
| “The overall curves are not noisy” | “The observed declines are large, but uncertainty and generalization depend on the reused requests and sampled collection” |
| “Does installing skills make the agent smarter? No.” | “Installing more skills reduced designated-target selection in this test; task quality was not measured” |
| “Almost nobody tests skills” | “Our scanner detected bundled test/eval files in approximately X% of the sampled distinct SKILL.md records” |
| “The 35 most popular repositories” | “A selected sample of popular repositories found through the stated searches” |
| “Every extra skill costs tokens on every request” | “Larger installed collections increased measured input usage in our pilot; catalog compression, omission, caching, and repeated turns affect the relationship” |
| “10K extra tokens on every single request” | “In the single-turn Haiku pilot, the measured difference was about 10K input tokens” |
| “A real setup has fewer but more overlapping skills” | “Real installations may differ in size and overlap; we did not sample their distribution” |

Keep untested mitigation advice explicitly hypothetical. Fewer installed skills is directly related to a tested manipulation, but improved task quality is still unmeasured. Sharper descriptions, router skills, hooks, retrieval, and larger budgets need their own evaluations before being called demonstrated fixes.

### 6.1 Reconcile survey versions and numeric prose

The draft uses the earlier 35-repository/6,741-skill survey; the methodology reports 42 skill-containing repositories and 6,908 distinct records. Choose one frozen survey version for the main narrative, or distinguish the original and expanded samples explicitly. Recompute all tables, counts, percentages, duplicate-name statistics, and figure captions for that chosen version. Do not combine 732 duplicate names from the earlier subset with the expanded denominator without labeling it.

“Never naming the skill” also needs a precise definition. Prompts such as “Grill me…” and file extensions have strong lexical overlap with names. A defensible description is “no explicit slash-command or skill-invocation syntax,” if verified across the prompt file. Lexical overlap is not inherently a flaw, but it affects distinctiveness interpretations.

### 6.2 Cost and caching claims need a separate audit

The methodology interprets non-cached input as cache writes and attributes dominant cost to fresh-session writes. The records and review so far do not establish that interpretation. A fresh session alone is insufficient evidence for a billing category.

Executor actions:

- Inspect the actual usage field semantics for the specific model/provider and collection date.
- Distinguish total input, cached reads, explicitly reported cache creation, output, estimated list-price cost, and actual billing.
- Do not relabel the difference between total and cached input as cache-write tokens without provider evidence.
- Check whether token totals are first-request usage or sums across turns. The latter cannot isolate initial catalog overhead.
- Verify historical price sources before recalculating dollar amounts. If unavailable, retain token counts and label dollar estimates unverified or omit them.

This review does not certify the quoted model pricing or provide a replacement price.

## 7. Executor sequence and deliverables

### Phase A: preserve and audit existing evidence

1. Freeze a manifest of input files, hashes, collection dates, configurations, and script versions. Preserve historical JSONL unchanged.
2. Build one reproducible analysis entry point with explicit filtering and retry rules.
3. Produce an audit table by harness/model/condition/access batch: attempted logical runs, retained runs, failures, turn-limit endings, target exposure where known, and raw-log coverage.
4. Reproduce original rates before adding corrected metrics. Explain every discrepancy.

### Phase B: correct analysis and publication claims

1. Add termination breakdowns, exact-target versus acceptable-component distinctions, and strict versus family MCP metrics.
2. Produce paired differences and appropriately scoped uncertainty.
3. Mark unavailable historical evidence rather than reconstructing it by assumption.
4. Update methodology, figures, captions, and blog together. Keep exploratory post-hoc analysis distinguishable from original endpoints.
5. Reconcile survey versions and audit token/cost language.

### Phase C: improve the pipeline before any new campaign

1. Save full ordered raw events from process start, including partial output on timeouts where feasible. Exclude credentials from saved configuration manifests.
2. Record exact invocation, model resolution, access route, environment/catalog manifest, detector version, and scoring version.
3. Validate loaded capabilities and MCP connectivity before scoring routing failure.
4. Test detectors using known positive/negative cases, failed reads, alternative path forms, and operation arguments. These tests are necessary because measurement code defines the result.
5. Run the small validation study, then decide which stronger claims justify additional runs.

Expected deliverables from the executor:

- A reproducible audit and analysis script.
- Versioned derived tables, with original metrics retained alongside corrected or newly named metrics.
- Updated `METHODOLOGY.md` and blog text/figures, consistent with each other.
- A change log identifying which claims were corrected, narrowed, removed, or left unresolved.
- A proposed follow-up protocol, separate from completed results, if stronger claims remain desired.

## 8. Completion checklist

- [ ] Original Experiment 1 totals reproduced.
- [ ] Turn-limit outcomes reported separately without selectively removing them.
- [ ] Observation windows and harness differences visible near results.
- [ ] Target retention, acceptable routing, and task quality clearly distinguished.
- [ ] Browser-family/overlap flags no longer presented as completed operations.
- [ ] Stub-induced behaviour and missing raw traces explicitly bounded.
- [ ] Detector validation and infrastructure availability documented.
- [ ] Retry deduplication and denominators reproducible.
- [ ] Paired comparisons and uncertainty match the claimed population.
- [ ] Mechanism explanations labeled as hypotheses unless directly tested.
- [ ] Mixed scenarios not described as a causal interaction experiment.
- [ ] Static survey figures use one clearly identified corpus version.
- [ ] Token overhead, caching, and cost claims supported by the appropriate fields and sources.
- [ ] No task-quality, “smarter agent,” or universal-installation conclusion inferred from target activation alone.

The minimum publishable revision does not require rerunning everything. It requires transparent measurement, corrected analysis, and narrower claims. General claims about mechanisms, ordinary task outcomes, or skills–tools interactions require additional evidence rather than a longer limitations paragraph.
