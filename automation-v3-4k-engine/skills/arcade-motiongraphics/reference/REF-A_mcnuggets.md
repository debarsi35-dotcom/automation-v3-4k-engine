# REF-A: McDonald's "Spicy McNuggets Side Mission" (8-bit × real-food hybrid)

Pinterest 1107533733410842379, posted by Jared Tomkins (animation studio) for Harbor Picture Co / McDonald's UK, 2025.
30.0 s · 25 fps · 750 frames · 9:16 (downloaded at 360×640, the only size Pinterest serves).
Every frame was read on labelled contact sheets (`analysis/sheets/A_01…25.jpg`), and the cuts were measured by frame difference
(`A_diff.tsv`, diff > 28 = big change). The sound was split with Demucs and studied separately (see SOUND.md).

**What it is:** a game-world story told in 30 s. It opens fully 8-bit, with a pixel city and a pixel crew member who talks
in an RPG dialog box. Then it "levels up" into real macro food footage that keeps the game's UI on top: pixel
text, HUD meters, crosshairs, pixel flames, pixel sparks. The photo and the pixel art keep swapping into each other.

## Beat table

| frames | time (s) | what happens | device |
|---|---|---|---|
| 1–10 | 0.00–0.40 | A pale, knitted texture (vertical columns of V-stitches that wobble) resolves into a pixel sky with clouds | **knit dissolve** |
| 9–30 | 0.32–1.20 | The camera tilts down from the sky to a city skyline, and the restaurant rises from the bottom with an overshoot | **tilt-down + rise** |
| 21–60 | 0.80–2.40 | A red car drives in and parks, a pedestrian walks, the clouds drift. The world is alive while it holds | **living hold** |
| 62–77 | 2.44–3.04 | 8 wedges rotate and grow, revealing the next shot. The centre sits on the next subject's head | **pinwheel wipe** |
| 74–140 | 2.92–5.56 | A yellow RPG dialog box pops in (stepped corners, black outline, dark drop shadow, stepped tail). Its text types word by word *on the voice* | **dialog + typewriter** |
| 136–142 | 5.40–5.64 | The box squashes and stretches before it goes (anticipation) | squash |
| 143–150 | 5.68–5.96 | The box bursts into white rings. The title flies in flipped and rotated with smear copies and speed lines. A black slash crosses. **The whole scene turns red** | **title slam + colour-state change** |
| 151–190 | 6.00–7.60 | The title settles with an elastic overshoot and a sparkle glint. The character bites (an idle hold) | hold + garnish |
| 191–204 | 7.64–8.12 | The knit stitches return over the frame | knit (2nd use) |
| 204–206 | 8.12–8.20 | A white manga starburst, then a giant pixel nugget | **starburst cut** |
| 205–236 | 8.2–9.4 | The nugget spins, white stair-stepped pixel lightning crawls over it, and it heats from orange to red. A yellow HEAT meter with a flame icon fills along the bottom. Radial speed lines | **power-up + HUD meter** |
| 233–240 | 9.32–9.56 | The nugget shrinks into a spinning white pixel ring | pixel ring |
| 237–243 | 9.44–9.68 | Vertical CRT-line texture, a purple chroma flash | **CRT glitch** |
| 244–270 | 9.76–10.76 | A **real** photo nugget on an orange halftone. A yellow **crosshair** locks on. White pixel plus-sparks twinkle. The meter becomes a full flame-patterned bar | **real × pixel HUD** |
| 271–278 | 10.8–11.1 | The nugget recedes, then rushes at the camera | zoom-through |
| 279–300 | 11.16–12.0 | A real macro of the crumb with white stair-step pixel lightning. "MAXIMUM" pops in pixel fire type | pixel type on footage |
| 301–353 | 12.0–14.1 | "MAXIMUM" (small) is stacked over "FLAVOUR" (big). A cut to a tear-open macro. "HEAT" slides in from the left, then becomes "HEAT MODE" | **word stack** |
| 354–393 | 14.16–15.68 | "ON" flies up from the bottom and lands under "HEAT MODE:" with a bounce | word fly-up |
| 394–431 | 15.76–17.2 | Orange halftone, real nuggets fly in, a starburst, vertical scanline glow and a flare. Diagonal pixel "CRUNCH!" words, dark pixel slashes | crunch beat |
| 432–450 | 17.28–17.96 | **White horizontal stripes sweep down each real nugget and leave it as pixel art** | **stripe scan real→pixel** |
| 451–461 | 18.0–18.4 | A starburst, then the stripes sweep back from pixel to real | stripe scan back |
| 470–489 | 18.8–19.56 | A real dip. Pixel speed dashes, a pixel flame sprite licks the edge, 8-bit smoke puffs | sprite on footage |
| 490–513 | 19.6–20.5 | A posterised macro of the sauce | posterise |
| 514–530 | 20.56–21.2 | A giant pixel flame bursts in through a vertical-scanline glitch and shrinks to embers | big sprite pop |
| 545–580 | 21.8–23.2 | A macro crumb, pixel lightning streaks, a slow push | |
| 582–626 | 23.28–25.0 | Real nuggets fall over a halftone, with pixel flames, white blobs and radial lines | |
| 627–700 | 25.08–27.96 | Packshot: a nugget drops with 3 white motion lines. The title flies in with a smear and lands. A pixel flame and pixel impact rings appear where the nugget lands | packshot + title |
| 701–750 | 28.0–30.0 | The logo on stepped (posterised) red bands with a dotted bottom row | **banded end card** |

Measured big changes: 69 frames over 30 s, clustered in bursts (5.7–5.9, 8.1–9.0, 9.4–9.7, 16.1–16.4, 18.1–18.4,
20.5–20.8, 22.0–22.2). So the edit is not cut-every-second. It **holds a world for 1.5–3 s, then fires a 0.2–0.4 s burst**
(a starburst, glitch, stripe scan or slam) into the next one.

## What to steal
1. **The game frame is the story frame.** Every claim becomes a game event: an item gets picked up, a meter fills, a
   name is entered, a level is completed.
2. **Pixel UI on real material.** Crosshairs, meters, sparks, sprites and pixel type sit on top of real photos, and the
   stripe scan converts one into the other.
3. **One colour-state change per act.** The scene turns red when the "spicy" mission starts. Use a dither swap, or a
   flash plus a new palette.
4. **Supers are the voice's own words.** Small word over big word ("MAXIMUM / FLAVOUR", "HEAT MODE: / ON"). Fire-gradient
   pixel type with a dark outline and a 1-pixel extrusion.
5. **Transitions have a game cause:** knit, pinwheel, starburst, CRT glitch, stripe scan, a bubble pop.
6. **Hold and burst rhythm.** Hold 1.5–3 s with constant small motion (clouds, idle blink, sparks), then 0.2–0.4 s of chaos.
