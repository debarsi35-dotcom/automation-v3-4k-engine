---
name: youtube-daily-autopilot
description: >-
  Orchestrates daily YouTube batch generation and publishing with dynamic 24-hour view scaling (1, 3, or 5 videos/day),
  US Eastern high-RPM peak window scheduling, metadata description formatting with sources, and OAuth2 publishing.
---

# YouTube Daily Autopilot & Dynamic Scaler

Manages the autonomous scheduling, dynamic scaling, and YouTube Data API v3 publishing pipeline.

## Dynamic Scaling Matrix
- **Tier 1 (<20k views in 24h)**: 1 video daily.
- **Tier 2 (≥20k views in 24h)**: 3 videos daily.
- **Tier 3 (≥100k views in 24h)**: 5 shorts daily.

## High-RPM US Publication Windows
- **1 Video Daily**: 14:00 EST (19:00 UTC)
- **3 Videos Daily**: 11:30 EST (16:30 UTC), 15:30 EST (20:30 UTC), 19:30 EST (00:30 UTC)
- **5 Shorts Daily**: 09:00 EST, 12:00 EST, 15:00 EST, 18:00 EST, 21:00 EST
