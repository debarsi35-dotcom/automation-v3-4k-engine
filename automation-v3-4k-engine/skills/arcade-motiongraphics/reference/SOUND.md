# Sound: what the references do, and what we do

## REF-A (McNuggets), measured
- Demucs split it into voice and music. The music runs at **129 BPM** with a median spectral centroid of 2.7 kHz.
- 0–5.5 s: a **pure chiptune** intro. The spectrogram shows clean harmonic stacks of square-wave notes, with arpeggios.
- 5.5–27.5 s: an **announcer / sung voice over a beat**: "The Spicy McNuggets side mission. McNuggets have levelled up.
  Maximum flavour. Heat mode on. Crispy crunch, and a spicy dip with a kick. Are you ready?" Every super on screen is
  the voice's own words, landing as they are said.
- 27.6–30 s: a chiptune sting over the logo card.

## REF-B (CRT walk)
- 117 BPM soft chiptune with no voice, made to loop.

## Our rules (the user's ears come first; see NOTES.md)
- **One original chiptune per film**, synthesised in `tools/chip.py`. Never use Nintendo's or any game's real melody.
  The bed follows the story through **sections in `work/music.json`**: a minor groove for the problem, a pad-only drop on
  the failure beat, a bright major hook when the hero arrives, sparse arps under a "thinking" beat, a key lift (+2) for the
  triumph, a pad breakdown for the reflection, then the level-complete fanfare.
- Voices are **band-limited** (additive pulse/triangle, so no aliasing fizz), low-passed, with a 3–8 ms attack on every note.
  The drums are a soft sine kick and a quiet filtered snare. **No hi-hats, no ticks, no clicks, no harsh glitch noise.**
- SFX come from `work/make_cues.py` (`work/sfx.json`), timed from the forced-aligned words. Arcade vocabulary, kept soft:
  coin (two pulse notes), jump (pulse glide up), drop (triangle glide down), item-get arpeggio, power-up arpeggio, thump,
  whoosh, pop, lock-on (two soft blips), counter **sweep** (a tone gliding up instead of ticks), shutter rumble,
  low-passed glitch, game-over jingle, level-complete fanfare, CRT power-on.
- Measured on the Mario demo: music has under 1 % of its energy above 3 kHz (REF-A has 9.7 %), and the max sample jump is
  < 0.1, so there are no clicks. Brighten only by raising the low-pass corners in `chip.py`, never by adding noise.
- Mix (`tools/mix.py`): voice at −16 LUFS, bed −10 LU under it with a sidechain duck (~4 dB), SFX −7 LU, a −2 dB shelf above
  7 kHz, limiter, then loudnorm to **−15 LUFS / −1.2 dBTP**. Re-transcribe the mix to prove every word survives.
