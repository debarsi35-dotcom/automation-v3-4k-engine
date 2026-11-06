# 🕹️ Automation V3 — Autonomous Arcade Motion Graphics YouTube Autopilot

A 100% $0-cost, anti-slop, autonomous YouTube automation engine that crafts viral 30–60 second 9:16 vertical shorts told as retro 8-bit video games. Built on the **Arcade Motion Graphics** toolchain (`HyperFrames`, `GSAP`, `Kokoro-82M` local voiceover, `torchaudio` forced alignment, procedural `numpy/scipy` chiptune synthesis, and `FFmpeg`).

---

## ⚡ Core Upgrades in Automation V3

1. **Strict $0 Local Rendering**:
   - Zero paid AI video generation or credit-burning cloud APIs.
   - All voiceover, word-timing alignment, procedural chiptune music, and visual rendering run 100% locally in under 2 minutes per short.
2. **Dynamic View-Based Scaling Engine**:
   - **Tier 1 (<20k views in 24h)**: 1 video daily until channel momentum breaks out.
   - **Tier 2 (≥20k views in 24h on any video)**: Automatically scales to **3 videos daily**.
   - **Tier 3 (≥100k views in 24h on any video)**: Automatically scales to **5 shorts daily**.
3. **High-RPM US Peak Window Scheduling**:
   - Automatically schedules release times to capture peak viewer traffic in highest RPM Tier-1 countries (US Eastern Time):
     - **1 Daily Video**: 14:00 EST (19:00 UTC)
     - **3 Daily Videos**: 11:30 EST, 15:30 EST, 19:30 EST
     - **5 Daily Shorts**: 09:00 EST, 12:00 EST, 15:00 EST, 18:00 EST, 21:00 EST
4. **Anti-Slop Fact-Checking & Visual QA Gate**:
   - Every historical claim is verified against at least **two independent reliable sources** and logged in `SOURCES.md`.
   - Automated contact sheet quality assurance (`sheets.py` + `visual_qa.py`) validates video duration, audio loudness (-15.0 LUFS), and visual liveness before approving publication.
5. **Retired Legacy Slop Pipeline**:
   - Monolithic 4K long-form and generic 5-shorts splitter completely removed.

---

## 🏗️ Architecture & Directory Layout

```
automation-v3-4k-engine/
├── .github/workflows/
│   └── daily_video_v2.yml        # Cloud daily autopilot running in <15 minutes
├── pipeline/
│   ├── arcade_orchestrator.py    # Master end-to-end multi-agent pipeline
│   ├── analytics_scaler.py       # Dynamic 24h view analytics & quota engine
│   ├── high_rpm_scheduler.py     # US Eastern prime time publication scheduler
│   ├── arcade_researcher.py      # Dual-source topic & script generator
│   ├── arcade_film_writer.py     # Dynamic film.js code generator
│   ├── visual_qa.py              # Automated contact-sheet & audio quality gate
│   ├── youtube_uploader.py       # YouTube Data API v3 publisher
│   └── run_daily_v2.py           # Compatibility wrapper delegating to orchestrator
├── skills/
│   ├── arcade-motiongraphics/    # Vendored core engine (kit, tools, reference)
│   ├── arcade-story-researcher/  # Fact-checking & story design skill
│   ├── arcade-visual-qa/         # Frame QA inspection skill
│   └── youtube-daily-autopilot/  # Scheduling & upload skill
├── archive/
│   ├── published_history.json    # Persistent log of generated episodes
│   └── legacy_slop/              # Retired legacy long-form & splitter scripts
└── README.md
```

---

## 🚀 Quickstart & Local Execution

### 1. Requirements
- **Node.js 22+**
- **Python 3.11 or 3.12**
- **FFmpeg** on system PATH
- **Google Chrome**

### 2. Install Dependencies
```bash
# Python dependencies
pip install numpy scipy pillow soundfile kokoro-onnx torch torchaudio google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# HyperFrames CLI
npx --yes hyperframes@0.8.203 --version
```

### 3. Run Self-Test
```bash
python skills/arcade-motiongraphics/tools/selftest.py
```

### 4. Run Daily Pipeline (Local Dry-Run)
```bash
# Test 1 video daily (Tier 1)
python pipeline/arcade_orchestrator.py --dry-run --mock-views 5000

# Test 3 videos daily (Tier 2 scaling)
python pipeline/arcade_orchestrator.py --dry-run --mock-views 25000

# Test 5 shorts daily (Tier 3 viral scale)
python pipeline/arcade_orchestrator.py --dry-run --mock-views 120000
```

---

## ⚙️ Environment Variables & Secrets

For automated YouTube publishing via GitHub Actions, configure the following repository secrets:

| Secret Name | Description |
|---|---|
| `YOUTUBE_CLIENT_ID` | Google Cloud OAuth2 Client ID |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud OAuth2 Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | YouTube Data API v3 Refresh Token (generated with upload scope) |
| `RCLONE_CONFIG` | *(Optional)* Cloud vault remote backup configuration |
| `RCLONE_REMOTE` | *(Optional)* Remote backup destination folder |
