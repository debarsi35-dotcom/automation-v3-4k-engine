---
name: arcade-motiongraphics
description: >-
  "Arcade motion graphics" (also "arcade motiongraphics", "arcade MG", "the 8-bit style", "the Mario style", "the
  McNuggets side-mission style") — a narrated 9:16 story told as a VIDEO GAME: pixel worlds drawn in code (sky + city,
  levels, girders, ? blocks, high-score name entry, CRT cabinets), a game HUD over the whole film (heart + health bar
  = story progress, coin counter = what the hero collects), every spoken key word popping as fire-gradient pixel type,
  RPG dialog boxes typing on the voice, crosshairs locking onto the detail, and REAL material dropped into the game
  (cut-out photos of the real people, real product shots, real ads/pages) with stripe scans that turn the real thing
  into pixels. Game-cause transitions (knit dissolve, pinwheel wipe, starburst, CRT glitch, dither, iris, shutter, pull
  back into a real arcade cabinet), an original soft chiptune score + arcade SFX synthesised locally. Learned frame by
  frame from two Pinterest references (McDonald's "Spicy McNuggets Side Mission" 8-bit ad and a pixel-girl CRT loop).
  Free and local: Kokoro voice, wav2vec2 alignment, canvas + HyperFrames render, numpy chiptune. Use whenever the user
  says arcade motion graphics / arcade style / 8-bit / pixel / retro game style, or wants a story about a game, a
  company, a product launch or a founder told like a video game, or a short like the Mario demo.
---

# ARCADE MOTION GRAPHICS — the story as a video game

The voice tells a real story; the screen plays it as a game. Every claim becomes a **game event**: a level loads, a
counter rolls, an item is picked up (+1 CAP), a name is entered, a GAME OVER is stamped, a LEVEL COMPLETE plays.
Pixel art is drawn in code; the **real** material (people, products, documents) is dropped into the game and gets the
game UI on top.

> **Where it comes from.** `reference/REF-A_mcnuggets.md` (30 s, 750 frames, every one read: 8-bit world → real food
> with pixel HUD) and `reference/REF-B_crt_walk.md` (5 s, 151 frames: HUD + CRT glass + side-scroll). Sound measured
> separately (`reference/SOUND.md`). Worked example: `example/` — **"How Mario was born"** (30 s, 11 worlds, 9
> transition kinds, first demo of 2026-10-26, awaiting feedback, output `~/Desktop/How-Mario-Was-Born_Arcade-MG.mp4`).

**Read before building:** `reference/devices.md` (every device + its kit call) · `reference/SOUND.md` · `NOTES.md`
(the user's rules — they win) · `example/film.js` (the whole demo; copy it and rewrite scenes) · `example/SOURCES.md`.

## ⭐ What makes it arcade (what a first draft gets wrong)
1. **Story beats = game mechanics.** Don't decorate a slideshow with pixels. Ask for each line: *what would this be in a
   game?* "stuck with 2,000 machines" → a warehouse that fills row by row while a counter rolls to 2,000. "named after
   the landlord" → the arcade NAME ENTRY screen deleting JUMPMAN and typing MARIO. "the best-selling ever" → the hero
   powers up (small/big flicker) and the HUD bar hits MAX.
2. **Real material inside the game.** At least 3 real things per film (the founder as a cut-out with a pixel outline
   and a PLAYER 1 nameplate, the real product dropping in, the real ad/page with a crosshair + GAME OVER stamp, a real
   cabinet/device as the final frame). The stripe scan (`A.scanConvert`) turns real → pixel.
3. **The HUD runs the whole film** (REF-B): health = story progress (fills to MAX on the climax word), coins = what the
   hero collected (1, 2, 3 … then the big number rolls into it: x40M). It is the film's spine, keep it consistent.
4. **Hold and burst** (REF-A rhythm): a world holds 1.5–3 s and is always alive (clouds drift, idle frames, sparks,
   counters), then a 0.15–0.4 s burst (starburst, glitch, slam, stripe scan) moves to the next world.
5. **Every key word lands on its onset** in pixel type (`A.ptext` fire / white / gold / cyan) with a stepped pop
   (`A.popCell`). Small word over big word ("THEY CALL HIM / JUMPMAN", "OVER / 40,000,000 / COPIES"). Times come from
   forced alignment (`w(i)` = word i onset), never guessed.
6. **One colour-state change per act** (REF-A turns red for "spicy"): navy graph → orange heat for the "design" act,
   dither or flash into it.
7. **Transitions with a game cause, 6–9 kinds per film**: CRT power-on, knit dissolve, shutter, CRT glitch, pinwheel
   wipe on the next subject's head, starburst, iris, dither, pull back into a real cabinet. Never a plain crossfade.
8. **Pixel honesty**: everything pixel is snapped to its grid (`A.snap`), sprites scale by integers, movement is
   stepped where a game would step it (walk cycles 8–12 fps, counters, typewriters). Only the real photos are smooth.
9. **Original art and music.** Draw characters as *inspired by* (16×16, cap, moustache), never copy ROM sprites or game
   melodies. Real company names/logos only as facts (a sign, an ad), never as our own branding.
10. **Sound is a soft chiptune that follows the acts** + arcade SFX on the events (coin, jump, item-get, lock-on,
    counter sweep, game-over jingle, level-complete fanfare). No ticks, hats or harsh glitches (NOTES.md).

## ⛔ Hard rules
- Facts: every claim checked against two sources while writing (`SOURCES.md`); leave out disputed anecdotes or hedge.
- Images: Wikimedia Commons API with licence + author logged in `SOURCES.md`; credit line on the end card.
- The film is ONE canvas drawn by a pure function of time (`FILM.render(ctx, t)`), driven by one GSAP clock tween.
  No `Math.random()` (use `A.rnd(seed)`), no wall clock, no state carried between frames → every frame is seek-safe.
- Show the user the script first only if they asked for a plan; otherwise cook and deliver. Publish nothing.

## Workflow
`source ~/.claude/skills/arcade-motiongraphics/tools/env.sh` first (sets `$AMG`, `$AMG_TTS`, `$AMG_ALIGN`, `$AMG_AUDIO`, `$AMG_STT`).

0. **Project:** `bash $AMG/tools/new_film.sh <dir> "<Title>"` (default home `~/arcade-motiongraphics/<name>`).
1. **Story + script** (`work/script.json`, 30 s ≈ 10 lines, ~75 words): a year + a problem as the hook ("1981. Nintendo
   is stuck with two thousand arcade machines nobody wants."), the maker, 2–3 concrete design/decision beats, the
   name/identity beat, the big number, the "today" climax, a callback punchline ("Not bad for 256 pixels.").
   `shown` = what appears, `spoken` = what Kokoro says (`_` joins spoken words that make ONE shown word:
   "Nineteen_eighty-one" ↔ "1981."). Voice **am_fenrir ×1.18** (energetic, clear), gap 0.12, lead 0.75.
   - `$AMG_TTS $AMG/tools/vo.py <dir>` → `assets/audio/vo.wav`; then transcribe it (`$AMG_STT`, faster-whisper) and fix
     any word it mishears by respelling `spoken` ("Hair's too hard" read as "here is" → "Can't draw hair?").
   - `$AMG_ALIGN $AMG/tools/align.py <dir>` → `work/words.json`; `python3 $AMG/tools/words_js.py <dir>` → `assets/words.js`
     and a printed index of every word (use these indices for `w(i)`).
2. **Source** real material: people (`npx hyperframes remove-background in.jpg -o out.png`), products on white
   (`python3 $AMG/tools/matte_white.py` — AI mattes eat light-grey plastic), ads/pages (crop the region, note the pixel
   box of the words you'll target), a real device/cabinet for the ending (note its screen opening box). LOOK at a
   contact sheet of the cut-outs on magenta.
3. **Plan the worlds**: one world per line (see the example's 11), alternating light/dark/warm. Mark per world: the
   game event, the supers (word index → text), the real asset, the transition out, the SFX.
4. **Build** `assets/film.js`: keep `PAL/hero()` sprite builder, helpers (`pop`, `tag`, `shake`, `sky`), the `SPANS`
   (scene ownership) + `TR` (transition windows) + `F.render` (HUD on top) structure; rewrite `SC.*` scenes.
   `npx hyperframes check --json` → 0 errors (the full-bleed canvas carries `data-layout-allow-overflow`).
5. **Look**: `npx hyperframes snapshot . --no-end -o work/snaps --at <every beat + every transition midpoint>` and read
   the contact sheets: text clipped at edges, supers over busy art, something visible before its word, an empty frame
   during a fill-in (fill whole rows at once), a sprite too small to read at phone size (hero ≥ 300 px tall on climax).
6. **Sound**: edit `work/music.json` sections on the act times (problem minor → drop → bright hook → breakdown → key lift
   +2 → pad → fanfare), `work/make_cues.py` SFX on word indices → `python3 work/make_cues.py` →
   `$AMG_AUDIO $AMG/tools/chip.py <dir>` (2 s) → `python3 $AMG/tools/mix.py <dir>` (−15 LUFS) → re-transcribe
   `assets/audio/mix.wav` to prove every word survives.
7. **Render**: `npx hyperframes render . -o renders/v1.mp4 -q delivery` (~80 s for 30 s). Contact-sheet the RENDER at
   5 fps (`python3 $AMG/tools/sheets.py frames 5 out`) and look again; fix, re-render v2.
8. Deliver `~/Desktop/<Title>_Arcade-MG.mp4` + a 3-line note (length, what's real, sources).

## Learning another reference into this style
`yt-dlp` the pin → `ffmpeg -i ref.mp4 frames/f_%04d.jpg` → `python3 $AMG/tools/sheets.py frames <fps> out 10 3` → read
EVERY sheet → write `reference/REF-X.md` (frames · time · what · device) → Demucs split + measure the sound → add new
devices to `kit/arcade.js` + `reference/devices.md`, note them in NOTES.md.

## Files
`SKILL.md` · `NOTES.md` · `reference/` (REF-A, REF-B, REF-A_keyframes.jpg, SOUND, devices) · `kit/` (`arcade.js`,
`index.template.html`, OFL fonts: Press Start 2P, Pixelify Sans, Bungee, Silkscreen; gsap) · `tools/` (`env.sh`,
`new_film.sh`, `vo.py`, `align.py`, `words_js.py`, `matte_white.py`, `chip.py`, `mix.py`, `sheets.py`) · `example/`
(`film.js`, `script.json`, `words.json`, `music.json`, `make_cues.py`, `SOURCES.md`).
