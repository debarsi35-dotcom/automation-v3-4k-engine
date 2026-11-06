#!/usr/bin/env bash
# usage: bash new_film.sh <project-dir> "<Title>"   -> a ready HyperFrames project wired to the arcade kit
set -euo pipefail
AMG="${AMG:-$HOME/.claude/skills/arcade-motiongraphics}"
P="$1"; TITLE="${2:-Arcade Story}"
mkdir -p "$P"/{assets/{arcade,fonts,vendor,img/src,audio},work,renders,tools}
cp "$AMG/kit/arcade.js" "$P/assets/arcade/"
cp "$AMG/kit/fonts/"* "$P/assets/fonts/"
cp "$AMG/kit/vendor/gsap.min.js" "$P/assets/vendor/"
cp "$AMG/kit/hyperframes.json" "$P/"
sed "s|{{TITLE}}|$TITLE|" "$AMG/kit/index.template.html" > "$P/index.html"
cp "$AMG/example/film.js" "$P/assets/film.js"                      # start from the worked example, then rewrite the scenes
cp "$AMG/example/img/"* "$P/assets/img/" 2>/dev/null || true       # the example's 4 Commons images (credits in example/SOURCES.md); replace with yours
cp "$AMG/example/music.json" "$AMG/example/make_cues.py" "$P/work/"
[ -f "$P/work/script.json" ] || cp "$AMG/example/script.json" "$P/work/script.json"
cat > "$P/package.json" <<JSON
{ "name": "$(basename "$P")", "private": true, "type": "module",
  "scripts": { "check": "npx --yes hyperframes@0.8.203 check", "render": "npx --yes hyperframes@0.8.203 render" } }
JSON
echo "project ready: $P  (edit work/script.json first)"
