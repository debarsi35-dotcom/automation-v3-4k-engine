# NOTES: the user's rules for arcade motion graphics (these win over SKILL.md)

Add every piece of feedback here, dated, with the reason.

## Carried over from the user's other styles (standing preferences)
- **Sound must be soft.** The user finds shared synth grooves with ticks, hats, clicks and glitch noise painful and samey
  (2026-10-13). So: one original track per film, band-limited voices, no hi-hats, counter *sweeps* instead of ticks,
  master around −15 LUFS with a soft shelf above 7 kHz.
- **Bright, not dark.** Default to daylight sky, warm orange and red heat worlds; dark worlds only as short contrast beats.
- **Cook autonomously.** Don't stop to ask what to do. Deliver a finished video plus a short note.
- **Real material on every beat where it exists.** Real people, real products, real documents. Never fake a real person's
  quote or signature.

## 2026-10-26: first demo ("How Mario was born")
- Asked for: a new skill called "arcade motiongraphics", learned frame by frame from 2 Pinterest videos, plus a 30 s
  storytelling demo about the story of Mario. Delivered `~/Desktop/How-Mario-Was-Born_Arcade-MG.mp4`. Waiting for the
  user's feedback.
- Build lessons:
  - Kokoro am_fenrir reads "Hair's" / "Hair is" as "here is". Reword lines so they survive TTS, and always
    re-transcribe the voice.
  - The AI matte (`remove-background`) erased the NES's light-grey lid on a white background. Use `matte_white.py`
    for product shots on white.
  - Filling a big grid one item at a time leaves the frame empty for a second. Fill whole rows at once, left to right,
    rows staggered.
  - A Commons cabinet photo can carry third-party branding on top (a sponsor topper). Crop it out of the final frame.
