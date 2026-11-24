"""Wrap post/skills-mcp-post.html (a page fragment) into a standalone page for GitHub Pages: docs/index.html.
Run after build_post2.py."""
import html, os, re, shutil
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
SITE = "https://galinaalperovich.github.io/closet-full-of-skills/"
frag = open(os.path.join(B, "skills-mcp-post.html")).read()
css = frag[frag.index("<style>") + 7:frag.index("</style>")]
body = frag[frag.index("</style>") + 8:].strip()
HOME = "https://galinaalperovich.github.io/"
nav = (f'<nav style="font:500 .9rem var(--sans);display:flex;gap:1.2rem">'
       f'<a href="{HOME}">← Galina Alperovich</a><a href="{HOME}blog/">blog</a></nav>')
assert body.startswith("<article>")
body = body.replace("<article>", "<article>\n" + nav, 1)   # link back to the personal site
# comments: giscus, stored in the personal site repo's GitHub Discussions ("Announcements")
giscus = ('<section id="comments"><h2>Comments</h2>'
          '<script src="https://giscus.app/client.js" data-repo="galinaalperovich/galinaalperovich.github.io" data-repo-id="R_kgDOV3uGlQ" '
          'data-category="Announcements" data-category-id="DIC_kwDOV3uGlc4DLuo6" data-mapping="pathname" data-strict="1" '
          'data-reactions-enabled="1" data-emit-metadata="0" data-input-position="top" data-theme="preferred_color_scheme" '
          'data-lang="en" data-loading="lazy" crossorigin="anonymous" async></script></section>')
i = body.rindex("</article>"); body = body[:i] + giscus + "\n" + body[i:]
fonts = re.search(r'<link rel="stylesheet" href="[^"]+">', frag).group(0)
plain = lambda s: html.escape(re.sub(r"<[^>]+>", "", s).strip(), quote=True)
title = plain(re.search(r"<h1>(.*?)</h1>", body, re.S).group(1))
desc = plain(re.search(r'<p class="dek">(.*?)</p>', body, re.S).group(1))
# Google Tag Manager (Google Analytics runs inside the container); the same container as the personal site.
GTM = "GTM-KJJKC6QJ"
gtm_head = ("<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
            f"}})(window,document,'script','dataLayer','{GTM}');</script>\n<!-- End Google Tag Manager -->")
gtm_body = (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM}" height="0" width="0" '
            'style="display:none;visibility:hidden"></iframe></noscript>')
page = f"""<!doctype html>
<html lang="en">
<head>
{gtm_head}
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
<meta property="og:image:width" content="2400">
<meta property="og:image:height" content="1260">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<style>
html,body{{margin:0}}
{css}</style>
</head>
<body>
{gtm_body}
{body}
</body>
</html>
"""
D = os.path.join(R, "docs"); os.makedirs(D, exist_ok=True)
open(os.path.join(D, "index.html"), "w").write(page)
open(os.path.join(D, ".nojekyll"), "w").write("")
shutil.copy2(os.path.join(B, "images2", "card.png"), os.path.join(D, "card.png"))   # link-preview image (the hero, 1200x630 at 2x)
print("wrote docs/index.html", len(page))
import subprocess, sys   # and the readable Markdown copy, post/post.md
subprocess.run([sys.executable, os.path.join(B, "build_md.py")], check=True)
