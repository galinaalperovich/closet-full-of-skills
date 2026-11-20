"""Read-only survey of SKILL.md files. Stdlib + optional PyYAML. Never executes repo code."""
import ast, hashlib, json, os, re, sys
from collections import Counter, defaultdict
try:
    import yaml
except Exception:
    yaml = None

ROOT = sys.argv[1]
STD = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stdlib.json"))))
CONV = "scripts|references|reference|assets|templates|resources|rules|prompts|examples|docs|data|lib|bin|tools|workflows|agents"
PATH_RE = re.compile(r"(?<![\w/.\-}~$])(?:\./)?((?:%s)/[\w.\-/]+\.[A-Za-z0-9]{1,6})(?![\w/])" % CONV)
LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
STALE = re.compile(r"\b(claude-(?:2|instant|3)[\w.\-]*|claude-(?:opus|sonnet|haiku)-4[\w.\-]*|gpt-3\.5[\w.\-]*|gpt-4(?:o|-turbo|-32k|\.1)?(?![\w.])[\w\-]*|gemini-(?:1\.[05]|pro)[\w.\-]*|text-davinci[\w\-]*)", re.I)
ABS = re.compile(r"(/Users/[A-Za-z][\w.\-]+/|/home/[a-z][\w.\-]+/|[A-Z]:\\Users\\[\w.\-]+)")
NAME_OK = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

def split_fm(text):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]

def loose(fm):
    d = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z_][\w\-]*):\s*(.*)$", line)
        if m:
            d[m.group(1)] = m.group(2).strip().strip("\"'")
    return d

def imports(path):
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except Exception:
        return None
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            mods.add(n.module.split(".")[0])
    return mods

rows = []
for repo in sorted(os.listdir(ROOT)):
    rp = os.path.join(ROOT, repo)
    for dp, dn, fn in os.walk(rp):
        dn[:] = [d for d in dn if d not in (".git", "node_modules")]
        if "SKILL.md" not in fn:
            continue
        p = os.path.join(dp, "SKILL.md")
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        r = {"repo": repo, "path": os.path.relpath(p, rp), "dir": os.path.basename(dp),
             "sha": hashlib.sha1(text.encode()).hexdigest(), "issues": [], "detail": {}}
        I = r["issues"]
        fm, body = split_fm(text)
        meta = {}
        if fm is None:
            I.append("no-frontmatter")
        else:
            meta = loose(fm)
            if yaml:
                try:
                    y = yaml.safe_load(fm)
                    if not isinstance(y, dict):
                        I.append("yaml-invalid"); r["detail"]["yaml"] = "not a mapping"
                    else:
                        meta = {k: v for k, v in y.items()}
                except Exception as e:
                    I.append("yaml-invalid"); r["detail"]["yaml"] = str(e).splitlines()[0][:120]
        name = meta.get("name"); desc = meta.get("description")
        name = name if isinstance(name, str) else (None if name is None else str(name))
        desc = desc if isinstance(desc, str) else (None if desc is None else str(desc))
        r["name"] = name; r["desc_len"] = len(desc or ""); r["lines"] = text.count("\n") + 1
        if fm is not None:
            if not name: I.append("no-name")
            else:
                if name != r["dir"]: I.append("name-dir-mismatch")
                if not NAME_OK.match(name) or len(name) > 64: I.append("name-invalid")
            if not desc: I.append("no-description")
            else:
                if len(desc) > 1024: I.append("desc-over-1024")
                if len(desc) < 40: I.append("desc-under-40")
                if not re.search(r"\b(when|use (?:this|it|for|to|if)|trigger|whenever|使用|当)\b", desc, re.I): I.append("desc-no-trigger")
        if r["lines"] > 500: I.append("body-over-500-lines")
        # references
        dead_link, dead_path, weak_path = [], [], []
        for t in LINK_RE.findall(text):
            t = t.split("#")[0].split("?")[0]
            if not t or re.match(r"^[a-z][a-z0-9+.\-]*:", t, re.I) or t.startswith(("/", "<", "{", "$", "~")) or "{" in t or "<" in t:
                continue
            from urllib.parse import unquote
            if not os.path.exists(os.path.normpath(os.path.join(dp, unquote(t)))):
                dead_link.append(t)
        for t in set(PATH_RE.findall(text)):
            if "*" in t or "XXX" in t: continue
            if os.path.exists(os.path.join(dp, t)): continue
            first = t.split("/")[0]
            if os.path.isdir(os.path.join(dp, first)): dead_path.append(t)
            elif first in ("scripts", "references", "reference", "assets") and not os.path.exists(os.path.join(rp, t)): weak_path.append(t)
        if dead_link: I.append("dead-link"); r["detail"]["dead_link"] = sorted(set(dead_link))[:8]
        if dead_path: I.append("dead-path"); r["detail"]["dead_path"] = sorted(dead_path)[:8]
        if weak_path: I.append("missing-dir-path"); r["detail"]["weak_path"] = sorted(weak_path)[:8]
        # orphans: bundled md/py/sh files never mentioned
        bundled = []
        for d2, dn2, fn2 in os.walk(dp):
            dn2[:] = [d for d in dn2 if d not in (".git", "node_modules", "__pycache__")]
            if d2 != dp and "SKILL.md" in fn2: dn2[:] = []; continue
            for f in fn2:
                if f == "SKILL.md": continue
                bundled.append(os.path.relpath(os.path.join(d2, f), dp))
        r["bundled"] = len(bundled)
        alltext = text
        for b in bundled:
            if b.endswith(".md"):
                try: alltext += open(os.path.join(dp, b), encoding="utf-8", errors="replace").read()
                except Exception: pass
        orph = [b for b in bundled if b.split(".")[-1] in ("md", "py", "sh", "js", "ts") and os.path.basename(b) not in alltext
                and os.path.basename(b).lower() not in ("readme.md", "license.md", "__init__.py", "changelog.md")]
        if orph: I.append("orphan-file"); r["detail"]["orphan"] = orph[:8]; r["orphans"] = len(orph)
        # python deps
        pys = [b for b in bundled if b.endswith(".py")]
        r["py"] = len(pys)
        if pys:
            local = {os.path.splitext(os.path.basename(b))[0] for b in pys} | {b.split("/")[0] for b in bundled} | {x for b in bundled for x in b.split("/")[:-1]}
            third = set(); pep723 = False
            for b in pys:
                src = open(os.path.join(dp, b), encoding="utf-8", errors="replace").read()
                if "# /// script" in src: pep723 = True
                m = imports(os.path.join(dp, b))
                if m: third |= {x for x in m if x not in STD and x not in local and not x.startswith("_")}
            declared = pep723 or any(os.path.exists(os.path.join(dp, x)) for x in ("requirements.txt", "pyproject.toml", "scripts/requirements.txt", "uv.lock", "environment.yml"))
            if third:
                r["detail"]["third"] = sorted(third)[:12]
                low = alltext.lower()
                unmentioned = [x for x in third if x.lower() not in low]
                if not declared and unmentioned:
                    I.append("undeclared-python-dep"); r["detail"]["undeclared"] = sorted(unmentioned)[:12]
        st = sorted({m.lower() for m in STALE.findall(text)})
        if st: I.append("old-model-id"); r["detail"]["models"] = st[:8]
        ab = sorted(set(ABS.findall(text)))
        ab = [a for a in ab if not re.search(r"/(you|user|username|yourname|your-?user|name|me|xxx|example|runner|ubuntu|claude)/?$", a, re.I)]
        if ab: I.append("personal-abs-path"); r["detail"]["abs"] = ab[:5]
        rows.append(r)

json.dump(rows, open(sys.argv[2], "w"))
print(len(rows), "skill files")
