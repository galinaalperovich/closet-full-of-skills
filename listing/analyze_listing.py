"""Summarise the captured requests (listing/capture.py): what the skill listing contained in each setup.

    python3 listing/analyze_listing.py CAPTURE_DIR

Writes listing/summary.csv (one row per harness and setup) and listing/targets.csv (one row per harness, setup and
target skill: listed or not, description characters shown against characters installed). No request text is copied.
"""
import csv, glob, json, os, re, sys
import yaml

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.dirname(os.path.abspath(__file__))
CAP = sys.argv[1]
TARGETS = sorted(os.listdir(os.path.join(S, "envs", "alone")))

def installed_desc(setup, t):
    base = os.path.join(S, "envs", "alone", t) if setup == "alone" else os.path.join(S, "envs", setup)
    txt = open(os.path.join(base, ".claude", "skills", t, "SKILL.md")).read()
    fm = yaml.safe_load(txt.split("---")[1]) if txt.startswith("---") else {}
    return " ".join(str(fm.get("description", "")).split())

def texts(body):
    for m in body.get("messages", []) + body.get("input", []):
        c = m.get("content", "")
        for p in ([c] if isinstance(c, str) else c or []):
            yield p if isinstance(p, str) else p.get("text", "")

def claude_listing(body):
    for t in texts(body):
        k = t.find("The following skills are available for use with the Skill tool:")
        if k >= 0:
            lines = t[k:].split("\n")[1:]
            out = []
            for l in lines:
                if l.startswith("- "): out.append(l[2:])
                elif out and l.strip() == "": break
            return {e.split(": ", 1)[0]: (e.split(": ", 1)[1] if ": " in e else "") for e in out}
    return {}

def codex_listing(body):
    for t in texts(body):
        if "### Skill roots" in t and "### Available skills" in t:
            sec = t[t.index("### Available skills"):]
            ent = {}
            for l in sec.split("\n"):
                m = re.match(r"- ([^:]+): (.*)$", l)
                if m:
                    desc = re.sub(r"\s*\(file: [^)]*\)\s*$", "", m.group(2)).strip()
                    ent[m.group(1)] = desc
            return ent
    return {}

def main_request(files):
    # the harness may send several requests; the main one carries the most text
    return max((json.load(open(f))["body"] for f in files), key=lambda b: len(json.dumps(b)))

groups = {}
for f in glob.glob(os.path.join(CAP, "*__req*.json")):
    h, setup, t, _ = os.path.basename(f).split("__")
    groups.setdefault((h, setup, t), []).append(f)

summary, rows = [], []
for (h, setup, t), files in sorted(groups.items()):
    body = main_request(files)
    lst = claude_listing(body) if h.startswith("claude") else codex_listing(body)
    targets = [t] if setup == "alone" else TARGETS
    for x in targets:
        inst = installed_desc(setup, x)
        rows.append({"harness": h, "setup": setup, "target": x, "listed": int(x in lst),
                     "desc_chars_shown": len(lst.get(x, "")), "desc_chars_installed": len(inst)})
    if setup != "alone":
        summary.append({"harness": h, "setup": setup, "entries": len(lst), "entries_with_description": sum(1 for v in lst.values() if v),
                        "listing_chars": sum(len(k) + len(v) + 4 for k, v in lst.items()),
                        "targets_listed": sum(1 for x in TARGETS if x in lst), "targets_with_description": sum(1 for x in TARGETS if lst.get(x)),
                        "targets_with_description_names": " ".join(x for x in TARGETS if lst.get(x)),
                        "targets_listed_names": " ".join(x for x in TARGETS if x in lst) if sum(1 for x in TARGETS if x in lst) < 20 else "all 20"})
# the "alone" setups, one row per harness
for h in sorted({k[0] for k in groups}):
    al = [r for r in rows if r["harness"] == h and r["setup"] == "alone"]
    if al:
        summary.append({"harness": h, "setup": "alone (20 folders)", "entries": "", "entries_with_description": "", "listing_chars": "",
                        "targets_listed": sum(r["listed"] for r in al), "targets_with_description": sum(1 for r in al if r["desc_chars_shown"]),
                        "targets_with_description_names": "", "targets_listed_names": ""})
order = {"alone (20 folders)": 0, "pack20": 1, "crowd200": 2, "crowd1000": 3}
summary.sort(key=lambda r: (r["harness"], order[r["setup"]]))
for name, data in (("summary.csv", summary), ("targets.csv", rows)):
    with open(os.path.join(D, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
for r in summary: print(r)
