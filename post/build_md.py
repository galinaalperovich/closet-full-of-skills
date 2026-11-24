"""Write post/post.md: a readable Markdown copy of the post, made from skills-mcp-post.html.

post.md is for reading and proposing edits (edit it in a pull request). It is not the source: the page is built by
build_post2.py, so accepted edits are carried over into build_post2.py and post.md is then regenerated.
Charts appear as the PNGs in images2/. Needs beautifulsoup4. Run after build_post2.py (build_page.py runs it)."""
import html, json, os, re
from bs4 import BeautifulSoup, NavigableString, Tag

B = os.path.dirname(os.path.abspath(__file__))
frag = open(os.path.join(B, "skills-mcp-post.html")).read()
figs = json.load(open(os.path.join(B, "figs2.json")))
art = BeautifulSoup(frag, "html.parser").find("article")

def fig_name(svg):   # which images2/<name>.png shows this chart: match its aria-label against figs2.json
    for k, v in figs.items():
        m = re.search(r'aria-label="([^"]*)"', v)
        if m and html.unescape(m.group(1)) == svg.get("aria-label"):
            return k
    raise SystemExit("no PNG matches a figure; rerun figs2.py and export_png2.py")

def inline(node):
    out = []
    for c in node.children:
        if isinstance(c, NavigableString):
            out.append(re.sub(r"\s+", " ", str(c)))
            continue
        t = inline(c)
        if c.name == "a":
            out.append(f"[{t.strip()}]({c.get('href', '')})")
        elif c.name in ("b", "strong"):
            out.append(f"**{t.strip()}**" if t.strip() else t)
        elif c.name in ("i", "em"):
            out.append(f"*{t.strip()}*" if t.strip() else t)
        elif c.name == "code":
            out.append(f"`{c.get_text()}`")
        elif c.name in ("sub", "sup"):
            out.append(f"<{c.name}>{t}</{c.name}>")
        elif c.name == "br":
            out.append("<br>")
        else:   # span (CIs, captions) and anything else: keep the text
            out.append(t)
    return "".join(out)

def lst(node, depth=0):
    lines = []
    for n, li in enumerate(node.find_all("li", recursive=False), 1):
        mark = f"{n}." if node.name == "ol" else "-"
        sub = [c for c in li.children if isinstance(c, Tag) and c.name in ("ul", "ol")]
        for s in sub:
            s.extract()
        lines.append("   " * depth + f"{mark} {inline(li).strip()}")
        for s in sub:
            lines += lst(s, depth + 1)
    return lines

def table(t):
    rows = []
    for tr in t.find_all("tr"):
        rows.append([inline(c).strip().replace("|", "\\|") for c in tr.find_all(["th", "td"])])
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])

blocks = []
for el in art.children:
    if not isinstance(el, Tag):
        continue
    cls = el.get("class") or []
    if el.name == "nav":
        blocks.append("<!-- The table of contents is made from the headings. -->")
    elif el.name in ("h1", "h2", "h3"):
        blocks.append("#" * int(el.name[1]) + " " + inline(el).strip())
    elif el.name == "p":
        text = inline(el).strip()
        if "dek" in cls or "tcap" in cls or "byline" in cls:
            text = f"*{text}*"
        blocks.append(text)
    elif el.name in ("ul", "ol"):
        blocks.append("\n".join(lst(el)))
    elif el.name == "figure":
        cap = inline(el.find("figcaption")).strip() if el.find("figcaption") else ""   # the hero image has no caption
        alt = (el.find("svg") or {}).get("aria-label", "") if el.find("svg") else ""
        blocks.append(f"![{alt.replace('[', '(').replace(']', ')')}](images2/{fig_name(el.find('svg'))}.png)" + (f"\n\n*{cap}*" if cap else ""))
    elif el.name == "pre":
        blocks.append("```\n" + el.get_text().rstrip("\n") + "\n```")
    elif el.name == "div" and el.find("table"):
        blocks.append(table(el.find("table")))
    elif el.name == "div" and "repobox" in cls:
        blocks.append("\n\n".join(inline(d).strip() for d in el.find_all("div", recursive=False)))
    elif el.name == "div":
        blocks.append(inline(el).strip())
    else:
        raise SystemExit(f"build_md.py does not know how to write <{el.name}>; add it")

head = ("<!-- A readable copy of the post, made by post/build_md.py. To suggest changes, edit this file in a pull request;\n"
        "     they are carried over into post/build_post2.py, which builds the page. Numbers, tables and charts come from\n"
        "     the data, so if you think one is wrong, say so in the PR rather than changing the number. -->")
md = head + "\n\n" + "\n\n".join(b for b in blocks if b) + "\n"
open(os.path.join(B, "post.md"), "w").write(md)
print("wrote post/post.md", len(md))
