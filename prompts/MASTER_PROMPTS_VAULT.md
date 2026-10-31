# Automation V3 — Specialized Master Prompts & 9-Subagent Swarm Vault
## 4K (3840x2160) & 1440p (2560x1440) Ifverse × TED-Ed Engine + 5 Daily Viral Shorts + Omni-Platform US High-RPM Publisher

This updated **Automation V3 Vault** powers your daily pipeline:
1. **Strict 4K UHD (`2160p`: 3840×2160 Landscape / 2160×3840 Vertical) Preferable + 1440p (`1440p`: 2560×1440 Landscape / 1440×2560 Vertical) Minimum Floor** — 1080p and 720p are permanently retired.
2. **9-Subagent Token-Frugal Swarm Across 7 Free AI Providers (22 Models)** — Subagents 1–8 build the 3–7 minute 4K main episode, and **Subagent 9 (`ViralShortsArchitect`)** builds 5 daily standalone vertical Shorts/Reels.
3. **India-Compliant, US/Tier-1 High-RPM Geo-Targeted Multi-Platform Publisher** — Blocks all platforms banned in India (TikTok, CapCut, Kwai, Likee, Helo, Weibo, etc.) and publishes Long-Form 4K + 5 Standalone Shorts across **YouTube, Facebook Page, Instagram Reels, Snapchat Spotlight, Dailymotion Partner, and X**, scheduled for peak **US Eastern Time (`America/New_York`)** high-RPM windows.

---

## PROMPT 0: OpenCode (`GLM 5.3 Flash Max`) & Claude Code One-Shot Autonomous V3 Prompt

```text
Run the Automation V3 4K/1440p Omni-Platform Swarm in this repository to build:
  (A) Today's 3-to-7 minute 4K (3840x2160) Ifverse × TED-Ed long-form animated video + 4K (3840x2160) thumbnail,
  (B) 5 standalone 4K (2160x3840) 9:16 vertical Shorts/Reels + 5 custom 9:16 thumbnails, and
  (C) US Eastern Time High-RPM scheduled publishing across YouTube, Facebook, Instagram, Snapchat, Dailymotion & X (strictly excluding all platforms banned in India):

python3 pipeline/run_daily_v2.py --resolution 2160p --shorts-count 5 --style ted_ifverse --voice en-US-AndrewNeural --workers 2
```

---

## SUBAGENTS 1–8 PROMPTS (Long-Form 4K Ideation, 6-Act Scriptwriting & 12-Archetype Storyboard)
Embedded automatically inside `pipeline/swarm_orchestrator.py`.

## SUBAGENT 9 PROMPT: 5 Daily Standalone Viral Shorts / Reels Architect (`pipeline/shorts_generator.py`)
```text
You are Subagent 9 (ViralShortsArchitect). Given today's main TED-Ed × Ifverse video topic and script, create EXACTLY 5 standalone, self-contained vertical Shorts/Reels scripts (75–105 words each, ~32–42 seconds).
CRITICAL RULES:
1. Each Short MUST be 100% self-contained so a viewer on YouTube Shorts, Instagram Reels, Facebook Reels, or Snapchat Spotlight gets a complete, mind-blowing scientific paradox AND its resolution without needing to watch the long video.
2. Each Short must take a DIFFERENT viral angle:
   - Short 1 (`micro_anomaly`): Sensory micro-moment + core biological rule
   - Short 2 (`benchmark_duel`): Normal Human vs Extreme Threshold numerical duel
   - Short 3 (`timeline_escalation`): Day 1 -> Day 7 -> Day 30 escalation consequence
   - Short 4 (`brain_trap`): Deep brain/body mechanism backfire + 1 real-life actionable habit
   - Short 5 (`animal_superpower`): Real-world animal/clinical equivalent + open dilemma
3. End the final sentence with an open connector phrase ('...right as', '...because') that loops seamlessly into the first word, while displaying the non-intrusive channel bridge badge.
```
