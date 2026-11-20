# Prompt given to the blind alternative rater

The rater was a separate Claude agent (general-purpose subagent) that could read only `analysis/alt_judge_input.json`. It recorded its 210 judgements as the rules in `analysis/alt_judge_rules.py`, which writes `analysis/alt_judgments.json`. The prompt, verbatim except for repository-relative paths:

---

You are acting as an independent rater for a research study on how coding agents choose skills and MCP tools. Work only from the file named below. Do NOT open any other files in the project (especially no *.jsonl result files, METHODOLOGY*.md, or blog files): you must stay blind to which model chose what and how often.

Input: analysis/alt_judge_input.json — a JSON list of 210 items. Each item has: id, request (what a user typed to the agent), designated_target (the component the experimenter intended), target_description, alternative (a different component the agent actually selected; "skill:<name>" or "mcp:<server>.<tool>"), alternative_description.

Context you need: the agent ran in an EMPTY working folder (files mentioned in the request do not exist), and could choose among installed skills (instruction packages, selected by name+description) and MCP tools. We want to know, for each item, whether selecting the alternative INSTEAD of the designated target was a reasonable routing choice for that specific request. Judge the request, not the target group: the same alternative can fit one request and not another.

Label each item with exactly one of:
- "equivalent": the alternative can by itself do what the request asks about as well as the designated target (e.g. another server's stock-price tool for a stock-price request; a near-duplicate skill covering the same task).
- "preliminary_step": a sensible first step toward the request that does not itself perform the asked operation (e.g. opening/navigating a browser page before taking the screenshot or trace that was asked for; listing repos before searching code).
- "related_partial": related to the request but would only partly serve it, or serves a different reading of it.
- "inappropriate": does not fit the request.
- "unassessable": the description is missing or too vague to decide (e.g. "(Claude Code built-in skill; description not captured)" where the name alone doesn't settle it).

Be consistent and conservative; do not reward an alternative just because it shares a keyword. Write the output with a script or the Write tool to analysis/alt_judgments.json as a JSON list of {"id": ..., "label": ..., "reason": "<= 20 words"} covering all 210 ids exactly once (validate the count and the label vocabulary before finishing). Reply with only a short summary: label counts and any items you found genuinely ambiguous.
