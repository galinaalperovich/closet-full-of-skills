"""Wrap post/skills-mcp-post.html (a page fragment) into a standalone page for GitHub Pages: docs/index.html.
Run after build_post2.py."""
import html, os, re, shutil
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
SITE = "https://galinaalperovich.github.io/in-context-forgetting/"
frag = open(os.path.join(B, "skills-mcp-post.html")).read()
css = frag[frag.index("<style>") + 7:frag.index("</style>")]
body = frag[frag.index("</style>") + 8:].strip()
fonts = re.search(r'<link rel="stylesheet" href="[^"]+">', frag).group(0)
plain = lambda s: html.escape(re.sub(r"<[^>]+>", "", s).strip(), quote=True)
title = plain(re.search(r"<h1>(.*?)</h1>", body, re.S).group(1))
desc = plain(re.search(r'<p class="dek">(.*?)</p>', body, re.S).group(1))
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Galina Alperovich">
<link rel="canonical" href="{SITE}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<style>
html,body{{margin:0}}
{css}</style>
</head>
<body>
{body}
</body>
</html>
"""
D = os.path.join(R, "docs"); os.makedirs(D, exist_ok=True)
open(os.path.join(D, "index.html"), "w").write(page)
open(os.path.join(D, ".nojekyll"), "w").write("")
shutil.copy2(os.path.join(B, "images2", "fig_skills.png"), os.path.join(D, "card.png"))   # link-preview image
print("wrote docs/index.html", len(page))
