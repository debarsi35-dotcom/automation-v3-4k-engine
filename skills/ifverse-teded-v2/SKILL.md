---
name: ifverse-teded-v3-4k
description: Complete Automation V3 4K (3840x2160) & 1440p (2560x1440) Ifverse 2.5D/3D Stickman × TED-Ed Storytelling Studio, 5 Daily Standalone Viral Shorts Generator, and India-Compliant US High-RPM Omni-Platform Publisher.
---
# Automation V3 — 4K / 1440p Ifverse × TED-Ed Omni-Platform Swarm Skill

1. **Resolution Standard**:
   - Preferable Default: `2160p` (4K UHD: `3840x2160` for 16:9 Long-Form, `2160x3840` for 9:16 Shorts).
   - Bare Minimum Floor: `1440p` (QHD: `2560x1440` for 16:9 Long-Form, `1440x2560` for 9:16 Shorts).
   - 1080p and 720p are strictly disabled.
2. **One-Command Daily Execution**:
   ```bash
   python3 pipeline/run_daily_v2.py --resolution 2160p --shorts-count 5 --style ted_ifverse --voice en-US-AndrewNeural --workers 2
   ```
3. **9-Subagent Swarm Modules**:
   - `pipeline/llm_client.py`: 7-Provider, 22-Model Free Failover Mesh with Multi-Key Rotation.
   - `pipeline/swarm_orchestrator.py`: Subagents 1–8 (Ideation, Viral Critic, 6-Act Parallel Writers, SEO, Micro-Batch Storyboard & Safety Net).
   - `pipeline/shorts_generator.py`: Subagent 9 (5 Standalone 4K/1440p 9:16 Shorts/Reels + 5 Vertical Thumbnails daily).
   - `pipeline/multi_platform_publisher.py`: India-Compliant (blocks TikTok/CapCut/etc.), US Eastern Peak Scheduled Publisher across YouTube, Facebook, Instagram, Snapchat, Dailymotion & X.
