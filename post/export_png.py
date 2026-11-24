import json, os, re, subprocess, tempfile
B = os.path.dirname(os.path.abspath(__file__)); fig = json.load(open(os.path.join(B, "figs.json")))
html = open(os.path.join(B, "skills-mcp-post.html")).read()
css = html[html.index("<style>") + 7:html.index("</style>")]
CH = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
tmp = tempfile.mkdtemp(prefix="png2_")
W = 800
for k, svg in fig.items():
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    h = int((W - 40) * vb[3] / vb[2]) + 90   # extra room: Chrome sometimes reserves space below the first paint
    page = f'<!doctype html><html data-theme="light"><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"><style>{css} body{{margin:0;background:#ffffff}} .f{{padding:20px;width:{W-40}px}} .f svg{{width:100%;height:auto;display:block;color:var(--fg)}}</style></head><body><div class="f">{svg}</div></body></html>'
    hp = os.path.join(tmp, k + ".html"); open(hp, "w").write(page)
    out = os.path.join(B, "images", k + ".png")
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/prof", "--force-device-scale-factor=2",
                    f"--window-size={W},{h}", "--virtual-time-budget=4000", f"--screenshot={out}", "file://" + hp], capture_output=True, timeout=90)
    print(k, os.path.exists(out), h)
# link-preview card (1200x630, rendered at 2x): the hero image on white, used as og:image and as the website thumbnail
card = f'<!doctype html><html data-theme="light"><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"><style>{css} html,body{{margin:0;background:#ffffff;overflow:hidden}} .c{{width:1200px;height:630px;box-sizing:border-box;padding:26px;display:flex;align-items:center}} .c>div{{flex:1;border:2px solid #d9dee2;border-radius:22px;padding:18px 24px 6px}} .c svg{{width:100%;height:auto;display:block;color:var(--fg)}}</style></head><body><div class="c"><div>{fig["fig_hero"]}</div></div></body></html>'
hp = os.path.join(tmp, "card.html"); open(hp, "w").write(card)
out = os.path.join(B, "images", "card.png")
subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/prof", "--force-device-scale-factor=2",
                "--window-size=1200,630", "--virtual-time-budget=4000", f"--screenshot={out}", "file://" + hp], capture_output=True, timeout=90)
print("card", os.path.exists(out))
# the same image as a 3:2 thumbnail (the personal site crops post thumbnails to 3:2)
hp = os.path.join(tmp, "thumb.html"); open(hp, "w").write(card.replace("height:630px", "height:800px"))
out = os.path.join(B, "images", "thumb_3x2.png")
subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/prof", "--force-device-scale-factor=1",
                "--window-size=1200,800", "--virtual-time-budget=4000", f"--screenshot={out}", "file://" + hp], capture_output=True, timeout=90)
print("thumb", os.path.exists(out))
