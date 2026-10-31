"""pipeline/run_daily_v2.py — Automation V3 Master End-to-End 4K / 1440p Omni-Platform Swarm Orchestrator.

Upgrades in Automation V3 (Clean Video & Multi-Platform Edition):
  1. STRICT 4K PREFERABLE (`2160p`: 3840x2160 16:9 / 2160x3840 9:16) & 1440p MINIMUM (`1440p`: 2560x1440 16:9 / 1440x2560 9:16):
     - Completely eliminates 1080p/720p exports. Defaults to 4K (`2160p`) with `1440p` as the strict minimum floor.
  2. 5 STANDALONE VIRAL SHORTS / REELS DAILY (`shorts_generator.py` — Subagent 9):
     - Generates 5 self-contained 9:16 vertical Shorts/Reels (each with its own hook, standalone scientific payoff,
       word-synced captions, custom 4K 9:16 thumbnail, and subtle bridge to the main long-form video).
  3. INDIA-SAFE, US/TIER-1 HIGH-RPM OMNI-PLATFORM PUBLISHER (`multi_platform_publisher.py`):
     - Excludes all platforms banned in India (TikTok, CapCut, Kwai, Likee, Helo, Weibo, etc.).
     - Publishes Long-Form 4K + 5 Shorts to YouTube, Facebook Page, Dailymotion Partner, and X; publishes the 5 Vertical Shorts/Reels
       to Instagram Reels and Snapchat Spotlight, scheduled for peak US Eastern Time (`America/New_York`) high-RPM windows.

Usage:
  python3 pipeline/run_daily_v2.py [--resolution 2160p|1440p] [--shorts-count 5] [--style ted_ifverse] [--demo] [--skip-upload]
"""
import argparse, datetime, json, os, re, subprocess, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STUDIO_DIR = os.path.join(ROOT_DIR, "studio")
ARCHIVE_DIR = os.path.join(ROOT_DIR, "archive")
HISTORY_PATH = os.path.join(ARCHIVE_DIR, "published_history.json")
sys.path.insert(0, os.path.dirname(__file__))

from llm_client import SWARM_TELEMETRY, build_candidate_pool
from swarm_orchestrator import run_ideation_swarm, run_scriptwriting_swarm, run_storyboard_swarm
from tts_aligner import generate_voiceover_and_timestamps
from shorts_generator import build_and_render_5_shorts
from multi_platform_publisher import publish_everywhere


DEMO_IDEA = {
    "title": "What If One Second Felt Like Ten Inside Your Brain?",
    "core_paradox": "Your prefrontal and visual cortex process reality 10x faster, turning you into a human supercomputer—while your normal human muscles and dopamine system slowly trap you in frozen isolation.",
    "cold_open_hook": "A coffee cup slips off the table. To your friend, it blurs toward the floor in a quarter of a second. To you? It hangs in mid-air like a painting.",
    "limiting_rule": "Your neural clock speeds up tenfold, moving from 60 visual frames per second to 600, but your muscles still obey normal physics and your dopamine receptors stop firing when nothing can surprise you.",
    "scientific_mechanisms": [
        "Critical flicker fusion rate (60 Hz in humans vs 250 Hz in flies)",
        "Visual cortex -> Prefrontal cortex -> Motor cortex reaction pipeline (0.25s baseline vs 0.025s)",
        "Dopamine reward prediction error (neurons only spike on unexpected surprises)",
    ],
    "thumbnail_text": "1 SEC = 10 SEC",
    "thumbnail_badge": "0.025s BRAIN",
    "viral_score": 98,
}

DEMO_SCRIPT_DATA = {
    "title": "What If One Second Felt Like Ten Inside Your Brain?",
    "alt_titles": [
        "What If Your Brain Ran 10x Faster Than Everyone Else?",
        "What Happens When One Second Feels Like Ten?",
        "The Hidden Curse of a 10x Faster Brain",
    ],
    "style": "ted_ifverse",
    "thumbnail_text": "1 SEC = 10 SEC",
    "thumbnail_badge": "10x BRAIN",
    "cast": {
        "HERO": {"top": "hoodie", "color": "#d64a33", "head": "none"},
        "FRIEND": {"top": "tshirt", "color": "#3a6ea5", "head": "cap", "headColor": "#f2c21a"},
        "SCIENTIST": {"top": "labcoat", "face": "glasses", "head": "none"},
    },
    "spoken_script": (
        "A coffee cup slips off the edge of the cafe table. "
        "Your friend Jake gasps, but his hand hasn't even twitched yet. "
        "A normal human brain takes about a quarter of a second just to see the fall, decide what to do, and send a signal to the arm. "
        "You? You react in two and a half hundredths of a second. "
        "You casually reach out, slide your palm underneath the porcelain mug, and catch every single drop before it falls three millimeters. "
        "Jake stares at you in dead silence. How did you do that? "
        "So what if one second felt like ten inside your brain? "
        "In neuroscience, your experience of time is governed by your brain's critical flicker fusion rate. "
        "Most human eyes and visual cortices process about sixty distinct snapshots every second. "
        "That is why movies look like smooth motion instead of flashing still photos. "
        "But imagine a genetic mutation speeds up your neural firing rate ten times over, to six hundred frames per second. "
        "There is just one strict biological rule. "
        "Your brain is ten times faster... your muscles are not. "
        "You cannot run at supersonic speed without tearing your tendons apart. You simply start moving while everyone else is still frozen in the past. "
        "In the first week, life feels like a superpower daydream. "
        "A tennis ball served at two hundred kilometers per hour floats toward you like a beach ball. "
        "You read an entire textbook during a thirty minute train ride. "
        "When a car hydroplanes on a rainy street at night, you don't panic. You have ten full subjective seconds to calculate the exact angle and step out of harm's way. "
        "Amazing, right? Except by month two, the hidden biological cost begins to surface. "
        "Deep inside your midbrain, dopamine neurons don't fire for rewards themselves. They fire for reward prediction errors... moments that are better or more surprising than your brain expected. "
        "When you see every micro-expression, every punchline, and every sentence three seconds before a person finishes speaking, nothing surprises you anymore. "
        "A three minute conversation with your best friend feels like a thirty minute slow-motion lecture. "
        "You have to force yourself to pause before answering so people don't think you are interrupting them. "
        "Worse still, the human brain already consumes twenty percent of your body's energy. Running ten times hot floods your prefrontal cortex with metabolic waste, triggering blinding migraines unless you close your eyes and shut the world out. "
        "Then comes the breaking point at the neurology lab. "
        "Dr. Lee shows you your latest brain scan. Your neural clock isn't stabilizing at ten times normal speed. "
        "Every week, synaptic plasticity is accelerating the loop... eleven times faster, then twelve. "
        "If you keep using the ability to predict and outthink everyone around you, within a year a single second will stretch into an hour of total sensory isolation. "
        "Right then, an equipment rack in the lab snaps loose above Jake. "
        "You have two seconds of real time—twenty seconds in your mind. "
        "You calculate the trajectory, push Jake clear, and accept Dr. Lee's neural dampening protocol to bring your perception back into rhythm with the people you love. "
        "While no human can perceive six hundred frames per second, nature already built creatures that live in this world. "
        "Houseflies process two hundred and fifty visual frames per second—which is why your swatting hand looks like a slow-motion cloud to them. "
        "And in humans, during life-threatening emergencies, the amygdala floods the hippocampus with norepinephrine, packing so many dense details into memory that time feels like it slowed down in hindsight. "
        "So if you could dial your own perception of time up or down at will, what speed would you choose? Tell us in the comments, and subscribe for our next thought experiment."
    ),
    "chapters": [
        {"time": "0:00", "title": "The 0.025-Second Catch"},
        {"time": "0:42", "title": "Critical Flicker Fusion & The One Rule"},
        {"time": "1:35", "title": "The Superpower Montage"},
        {"time": "2:25", "title": "The Dopamine Prediction Trap"},
        {"time": "3:15", "title": "The Lab Crisis & The Choice"},
        {"time": "4:05", "title": "Real Neuroscience & Amygdala Time Dilation"},
    ],
    "scientific_references": [
        "Critical Flicker Fusion Threshold: ~60 Hz in humans vs. ~250 Hz in Musca domestica (Healy et al., Animal Behaviour)",
        "Dopamine Reward Prediction Error: Schultz, Dayan & Montague (Science, 1997)",
        "Amygdala-driven retrospective time dilation during threat perception: Stetson et al. (PLOS ONE, 2007)",
    ],
    "youtube_description": "What would actually happen inside your brain and body if 1 second felt like 10? We combine real neuroscience, reaction-time physics, and dopamine biology to explore the superpower—and the terrifying cost—of a 10x faster mind.",
    "youtube_tags": ["what if", "ted ed", "ifverse", "neuroscience", "reaction time", "time perception", "science animation", "4k"],
}


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:48] or "daily-video"


def normalize_resolution(res_str: str) -> str:
    """Enforce 2160p (4K Preferable) or 1440p (Minimum Floor). Never allow 1080p/720p."""
    low = (res_str or "2160p").strip().lower()
    if low in ("1440p", "2k", "qhd"):
        return "1440p"
    return "2160p"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", default="2160p", help="2160p (4K UHD Preferable Default) or 1440p (QHD Minimum Floor)")
    ap.add_argument("--style", default="ted_ifverse")
    ap.add_argument("--voice", default="en-US-AndrewNeural")
    ap.add_argument("--shorts-count", type=int, default=5, help="Number of standalone vertical Shorts/Reels to generate daily (default: 5)")
    ap.add_argument("--demo", action="store_true", help="Run using verified built-in TED-Ed x Ifverse script (no external LLM key required)")
    ap.add_argument("--demo-short", action="store_true", help="Render a fast verification slice for CI/sandbox smoke testing")
    ap.add_argument("--skip-upload", action="store_true")
    ap.add_argument("--skip-shorts", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()

    target_res = normalize_resolution(a.resolution)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    pool = build_candidate_pool("general")
    print(f"[Failover Mesh V3] Initialized with {len(pool)} active AI model endpoints | Target Export Quality: {target_res} ({'4K UHD 3840x2160' if target_res == '2160p' else 'QHD 2560x1440'}).")

    # STAGE 1 & 2: Subagent Swarm Ideation & 6-Act Parallel Scriptwriting
    use_llm = (not a.demo and not a.demo_short)
    if not use_llm:
        print("[Stage 1 & 2] Running built-in verified TED-Ed × Ifverse flagship production package...")
        idea = DEMO_IDEA
        script_data = dict(DEMO_SCRIPT_DATA)
        if a.demo_short:
            words_list = script_data["spoken_script"].split()[:36]
            script_data["spoken_script"] = " ".join(words_list)
    else:
        try:
            print("[Stage 1 — Swarm] Launching Subagents 1–3 (TrendHarvester -> ParadoxIdeator -> ViralCritic)...")
            ideation = run_ideation_swarm(HISTORY_PATH)
            idea = ideation["winner"]
            print(f"  -> Winning Topic: {idea.get('title')} (Viral Score: {idea.get('viral_score')}/100)")
            print("[Stage 2 — Swarm] Launching Subagents 4–6 (ActArchitect -> 3 Parallel Act Writers -> PackagingSEO)...")
            script_data = run_scriptwriting_swarm(idea)
            print(f"  -> Swarm Script Complete: {script_data['word_count']} words")
        except Exception as e:
            print(f"[Swarm Safety Net] Cloud AI endpoints unreachable ({e}); activating built-in verified production package so daily run never stops...")
            idea = DEMO_IDEA
            script_data = dict(DEMO_SCRIPT_DATA)
            use_llm = False

    script_data["style"] = a.style
    slug = f"{datetime.date.today().isoformat()}-{slugify(script_data['title'])}"
    project_dir = os.path.join(STUDIO_DIR, "projects", slug)
    os.makedirs(project_dir, exist_ok=True)

    cfg = {
        "title": script_data["title"],
        "aspect": "16:9",
        "resolution": target_res,
        "fps": 24,
        "style": a.style,
        "voiceover": "input/voiceover.mp3",
        "script": "input/script.txt",
        "duration": 0,
        "captions": False,
        "bars": "wide",
        "fadeIn": 0.5,
        "fadeOut": 0.8,
        "thumbnailText": script_data.get("thumbnail_text", idea.get("thumbnail_text", "1 SEC = 10 SEC")),
        "thumbnailBadge": script_data.get("thumbnail_badge", idea.get("thumbnail_badge", "10x BRAIN")),
        "music": {"enabled": True, "gainDb": -17, "seed": 7},
        "sfx": {"enabled": True, "gainDb": -6},
        "loudness": -14,
    }
    for sub in ("input", "timeline", "story", "scenes/sets", "scenes/shots", "build", "out", "out/shorts"):
        os.makedirs(os.path.join(project_dir, sub), exist_ok=True)
    with open(os.path.join(project_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    # STAGE 3: TTS + Word-Level Timestamp Alignment
    print("[Stage 3] Generating voiceover and extracting word-level timestamps...")
    tts_info = generate_voiceover_and_timestamps(project_dir, script_data["spoken_script"], STUDIO_DIR, voice=a.voice)
    print(f"  -> Audio duration: {tts_info['duration']}s | Words: {tts_info['words_count']} | Visual beats: {tts_info['beats_count']}")

    # STAGE 4: Micro-Batch Storyboard Swarm (Subagents 7 & 8)
    print("[Stage 4 — Swarm] Launching Subagents 7 & 8 (Micro-Batch Storyboard Swarm + Deterministic Safety Net)...")
    story = run_storyboard_swarm(project_dir, script_data, use_llm_swarm=use_llm)
    print(
        f"  -> Storyboard compiled: {len(story['shots'])} contiguous shots across {story['duration']}s | "
        f"Swarm calls: {SWARM_TELEMETRY['total_calls']} | Auto-failovers: {SWARM_TELEMETRY['failovers_triggered']} | "
        f"Estimated tokens saved: ~{SWARM_TELEMETRY['estimated_tokens_saved']}"
    )

    # STAGE 5: Render 4K Contact Sheet, 4K (3840x2160) Main Thumbnail, and 4K / 1440p Long-Form Video
    print(f"[Stage 5] Rendering contact sheet, 4K (3840x2160) main thumbnail, and {target_res} long-form MP4 frames...")
    subprocess.run(
        ["node", "render.mjs", "--project", project_dir, "--sheet", "--scale", "0.35", "--format", "jpeg"],
        cwd=STUDIO_DIR,
        check=True,
    )
    thumbnail_png = os.path.join(project_dir, "out", "thumbnail.png")
    subprocess.run(
        [
            "node", "tools/render_thumbnail.mjs",
            "--project", project_dir,
            "--text", cfg["thumbnailText"],
            "--badge", cfg["thumbnailBadge"],
            "--aspect", "16:9",
            "--style", a.style,
            "--out", thumbnail_png,
        ],
        cwd=STUDIO_DIR,
        check=True,
    )
    subprocess.run(
        [
            "node", "render.mjs",
            "--project", project_dir,
            "--resolution", target_res,
            "--workers", str(a.workers),
            "--format", "jpeg",
        ],
        cwd=STUDIO_DIR,
        check=True,
    )

    # STAGE 6: Mix Procedural Music, 36 SFX, Punchline Drops & Run 4K/1440p Auto-QC
    print("[Stage 6] Mixing procedural soundtrack, 36 SFX cues, punchline drops, and normalizing to -14 LUFS...")
    subprocess.run([sys.executable, os.path.join(STUDIO_DIR, "audio", "mix.py"), "--project", project_dir], check=True)

    safe_title = re.sub(r"[^\w\- ]+", "", cfg["title"]).strip().replace(" ", "_") or "video"
    final_mp4 = os.path.join(project_dir, "out", f"{safe_title}.mp4")

    subprocess.run(
        [sys.executable, os.path.join(STUDIO_DIR, "tools", "auto_qc.py"), "--project", project_dir, "--mp4", final_mp4],
        check=True,
    )

    # STAGE 7: Generate & Render 5 Standalone 4K / 1440p Vertical Shorts + 5 Vertical Thumbnails (Subagent 9)
    shorts_list = []
    if not a.skip_shorts and a.shorts_count > 0:
        print(f"[Stage 7 — Swarm Subagent 9] Building & rendering {a.shorts_count} standalone {target_res} 9:16 vertical Shorts + thumbnails...")
        shorts_list = build_and_render_5_shorts(
            main_project_dir=project_dir,
            studio_dir=STUDIO_DIR,
            idea=idea,
            script_data=script_data,
            resolution=target_res,
            style=a.style,
            voice=a.voice,
            workers=a.workers,
            use_llm=use_llm,
            demo_fast=a.demo_short,
            count=a.shorts_count,
        )

    # STAGE 8: India-Safe, US High-RPM Scheduled Omni-Platform Publishing (YouTube, Facebook, Instagram, Snapchat, Dailymotion, X)
    publish_report = {"status": "skipped"}
    if not a.skip_upload:
        print("[Stage 8 — Omni-Platform Publisher] Scheduling & publishing Long-Form + 5 Shorts for US High-RPM Windows...")
        publish_report = publish_everywhere(
            project_dir=project_dir,
            long_mp4=final_mp4,
            long_thumb=thumbnail_png,
            script_data=script_data,
            shorts_list=shorts_list,
            slug=slug,
        )

    # Log to published_history.json
    history = []
    if os.path.exists(HISTORY_PATH):
        try:
            history = json.load(open(HISTORY_PATH, encoding="utf-8"))
        except Exception:
            history = []
    history.append({
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "slug": slug,
        "title": script_data["title"],
        "resolution": target_res,
        "duration_sec": story["duration"],
        "shots_count": len(story["shots"]),
        "mp4_path": final_mp4,
        "thumbnail_path": thumbnail_png,
        "shorts_generated": len(shorts_list),
        "shorts_paths": [s["mp4_path"] for s in shorts_list],
        "swarm_telemetry": SWARM_TELEMETRY,
        "multi_platform_publish": publish_report,
    })
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(
        f"\n[Automation V3 Complete]\n"
        f"  • Long-Form Master ({target_res}): {final_mp4}\n"
        f"  • 4K Main Thumbnail: {thumbnail_png}\n"
        f"  • Standalone {target_res} Shorts Rendered: {len(shorts_list)}"
    )


if __name__ == "__main__":
    main()
