---
name: arcade-visual-qa
description: >-
  Inspects multi-frame contact sheets (10x3 grid) and video streams from HyperFrames renders to detect visual clipping,
  HUD overlap, pure-black/dead frames, audio LUFS loudness violations, and timing drift before approving YouTube upload.
---

# Arcade Visual QA Gate

Automated frame-by-frame and contact sheet quality assurance for Arcade Motion Graphics films.

## Quality Checks
1. **Resolution & Aspect Ratio**: Strictly 9:16 vertical (1080x1920).
2. **Audio Loudness**: Mastered audio (`mix.wav`) target -15.0 LUFS with -1.2 dB True Peak.
3. **HUD Integrity**: Health bar progresses with story time; coin counter rolls upward; no HUD overlap with word pops.
4. **Visual Liveness**: Mean luma > 12.0 and brightness variance > 8.0 to prevent black screen rendering crashes.
5. **Contact Sheet Export**: 10x3 tile generated at 1 fps covering the entire video timeline.
