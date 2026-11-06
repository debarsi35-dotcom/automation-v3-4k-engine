"""Cross-platform Python implementation of new_film.sh.
usage: python new_film.py <project-dir> ["<Title>"]
"""
import sys, os, shutil
from pathlib import Path

AMG = Path(os.environ.get("AMG", Path(__file__).resolve().parent.parent))

if len(sys.argv) < 2:
    print("usage: python new_film.py <project-dir> ['<Title>']")
    sys.exit(1)

P = Path(sys.argv[1]).resolve()
title = sys.argv[2] if len(sys.argv) > 2 else "Arcade Story"

# Create directories
for sub in ["assets/arcade", "assets/fonts", "assets/vendor", "assets/img/src", "assets/audio", "work", "renders", "tools"]:
    (P / sub).mkdir(parents=True, exist_ok=True)

# Copy kit assets
shutil.copy2(AMG / "kit/arcade.js", P / "assets/arcade/arcade.js")
for f in (AMG / "kit/fonts").glob("*"):
    if f.is_file():
        shutil.copy2(f, P / "assets/fonts" / f.name)
shutil.copy2(AMG / "kit/vendor/gsap.min.js", P / "assets/vendor/gsap.min.js")
shutil.copy2(AMG / "kit/hyperframes.json", P / "hyperframes.json")

# Template index.html
tpl = (AMG / "kit/index.template.html").read_text(encoding="utf-8")
(P / "index.html").write_text(tpl.replace("{{TITLE}}", title), encoding="utf-8")

# Example film.js and images
shutil.copy2(AMG / "example/film.js", P / "assets/film.js")
for f in (AMG / "example/img").glob("*"):
    if f.is_file():
        shutil.copy2(f, P / "assets/img" / f.name)

shutil.copy2(AMG / "example/music.json", P / "work/music.json")
shutil.copy2(AMG / "example/make_cues.py", P / "work/make_cues.py")
if not (P / "work/script.json").exists():
    shutil.copy2(AMG / "example/script.json", P / "work/script.json")

pkg_json = f'''{{
  "name": "{P.name}",
  "private": true,
  "type": "module",
  "scripts": {{
    "check": "npx --yes hyperframes@0.8.203 check",
    "render": "npx --yes hyperframes@0.8.203 render"
  }}
}}'''
(P / "package.json").write_text(pkg_json, encoding="utf-8")
print(f"project ready: {P}  (edit work/script.json first)")
