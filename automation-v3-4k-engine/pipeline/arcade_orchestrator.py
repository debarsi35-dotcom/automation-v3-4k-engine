"""pipeline/arcade_orchestrator.py — Master Arcade Motion Graphics YouTube Autopilot.

Replaces legacy run_daily_v2.py:
  1. Dynamically scales daily output (1, 3, or 5 shorts) based on 24-hr view performance.
  2. Schedules releases for US Eastern / Tier-1 high-RPM peak windows.
  3. 100% $0 local generation (Kokoro TTS, Wav2Vec2, chiptune synth, HyperFrames render).
  4. Generates dual-source fact-checked SOURCES.md and credits for every episode.
  5. Runs contact sheet Visual QA before approving any upload.

Usage:
  python pipeline/arcade_orchestrator.py [--dry-run] [--mock-views N] [--force-quota 1|3|5] [--topic SLUG]
"""
import os, sys, json, time, shutil, subprocess, argparse, datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT_DIR / "archive"
HISTORY_PATH = ARCHIVE_DIR / "published_history.json"
SKILL_DIR = ROOT_DIR / "skills/arcade-motiongraphics"
TOOLS_DIR = SKILL_DIR / "tools"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analytics_scaler import get_daily_upload_quota
from high_rpm_scheduler import calculate_schedule_times
from arcade_researcher import select_topic_for_today, write_project_sources_markdown, CURATED_STORIES
from arcade_film_writer import generate_film_js
from visual_qa import run_visual_qa
from youtube_uploader import upload_to_youtube, backup_with_rclone


def run_episode_pipeline(story: dict, schedule_info: dict, dry_run: bool = False) -> dict:
    slug = story["slug"]
    title = story["title"]
    print(f"\n=======================================================")
    print(f"🎮 GENERATING ARCADE SHORT: {title} ({slug})")
    print(f"⏰ High-RPM Target: {schedule_info.get('est_time_str')} ({schedule_info.get('iso_publish_time')})")
    print(f"=======================================================")

    project_dir = Path.home() / f"arcade-motiongraphics/{slug}"
    if project_dir.exists():
        shutil.rmtree(project_dir)

    t0 = time.time()

    # Step 1: New Film Scaffolding
    print("\n[Step 1/8] Initializing Arcade Motion Graphics project...")
    new_film_cmd = [sys.executable, str(TOOLS_DIR / "new_film.py"), str(project_dir), title]
    subprocess.run(new_film_cmd, check=True)

    # Write custom script.json & SOURCES.md
    script_data = {
        "voice": story.get("voice", "am_fenrir"),
        "speed": story.get("speed", 1.18),
        "gap": story.get("gap", 0.12),
        "lead": story.get("lead", 0.75),
        "lines": story["lines"]
    }
    (project_dir / "work/script.json").write_text(json.dumps(script_data, indent=1), encoding="utf-8")
    write_project_sources_markdown(project_dir, story)

    # Step 2: Voiceover Synthesis (Kokoro-82M)
    print("\n[Step 2/8] Synthesizing narration with local Kokoro-82M (vo.py)...")
    subprocess.run([sys.executable, str(TOOLS_DIR / "vo.py"), str(project_dir)], check=True)

    # Step 3: Forced Alignment (Wav2Vec2)
    print("\n[Step 3/8] Extracting millisecond word timestamps (align.py)...")
    subprocess.run([sys.executable, str(TOOLS_DIR / "align.py"), str(project_dir)], check=True)

    # Step 4: Words JS
    print("\n[Step 4/8] Generating assets/words.js (words_js.py)...")
    subprocess.run([sys.executable, str(TOOLS_DIR / "words_js.py"), str(project_dir)], check=True)

    # Step 5: SFX Cues & Chiptune Synthesis
    print("\n[Step 5/8] Composing original 8-bit chiptune score & SFX...")
    subprocess.run([sys.executable, str(project_dir / "work/make_cues.py")], cwd=str(project_dir), check=True)
    subprocess.run([sys.executable, str(TOOLS_DIR / "chip.py"), str(project_dir)], check=True)

    # Step 6: Audio Mix Mastering (-15 LUFS)
    print("\n[Step 6/8] Mastering final audio mix (mix.py)...")
    subprocess.run([sys.executable, str(TOOLS_DIR / "mix.py"), str(project_dir)], check=True)

    # Step 7: Dynamic film.js Authoring
    print("\n[Step 7/8] Generating dynamic film.js code...")
    generate_film_js(project_dir, story)

    # Step 8: Headless Render via HyperFrames
    print("\n[Step 8/8] Rendering 9:16 vertical video via HyperFrames...")
    output_mp4 = project_dir / f"renders/{slug}.mp4"
    npx_cmd = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
    render_cmd = [
        npx_cmd, "--yes", "hyperframes@0.8.203", "render", ".",
        "-o", f"renders/{slug}.mp4", "-q", "delivery"
    ]
    subprocess.run(render_cmd, cwd=str(project_dir), shell=True, check=True)

    render_time = time.time() - t0
    print(f"Render completed in {render_time:.1f}s -> {output_mp4}")

    # Visual QA Gate
    print("\n[QA Gate] Running Contact Sheet & Frame Quality Assurance...")
    qa_report = run_visual_qa(output_mp4, project_dir)
    print("QA Result:", qa_report["status"])
    if qa_report["status"] != "PASSED":
        print(f"Warning: Visual QA reported issues: {qa_report}")

    # Prepare YouTube Metadata with Fact-Checking Sources & Credits
    sources_text = "\n".join(f"• {s['claim']} (Sources: {s['sources']})" for s in story.get("sources", []))
    image_credits = "\n".join(f"• {im['file']}: {im['source']} ({im['license']})" for im in story.get("image_attributions", []))

    description = (
        f"{title} — The 8-bit story of how a legendary product was built.\n\n"
        f"🕹️ TOLD AS AN ARCADE GAME:\n"
        f"Drawn in code, narrated locally, featuring real archival materials.\n\n"
        f"📚 FACT-CHECK CITATIONS (2 Sources Per Claim):\n{sources_text}\n\n"
        f"🖼️ ARCHIVAL & IMAGE CREDITS:\n{image_credits}\n\n"
        f"🎵 SOUNDTRACK: Original procedurally synthesised 8-bit chiptune (100% $0 local).\n\n"
        f"#ArcadeMotionGraphics #FounderStories #TechHistory #Shorts #RetroGaming"
    )

    yt_script_data = {
        "title": f"{title} 🕹️",
        "youtube_description": description,
        "youtube_tags": [slug.replace("-", " "), "arcade motion graphics", "founder story", "tech history", "retro gaming", "shorts"],
        "chapters": [{"time": "0:00", "title": "The Level One Problem"}]
    }

    # Upload or Dry-run
    if dry_run:
        print("\n[DRY RUN] Skipping YouTube Data API v3 live upload.")
        upload_result = {
            "status": "dry_run_success",
            "video_id": f"dry_run_{slug}",
            "url": f"https://youtu.be/dry_run_{slug}",
            "scheduled_time": schedule_info.get("iso_publish_time")
        }
    else:
        print(f"\n[YouTube Publisher] Uploading and scheduling for {schedule_info.get('iso_publish_time')}...")
        upload_result = upload_to_youtube(
            str(output_mp4),
            thumbnail_path=str(project_dir / "work/contact_sheet.jpg"),
            script_data=yt_script_data,
            privacy_status="private" if schedule_info.get("iso_publish_time") else "public"
        )
        upload_result["scheduled_time"] = schedule_info.get("iso_publish_time")

    # Log to published_history.json
    record = {
        "slug": slug,
        "title": title,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "published_at": schedule_info.get("iso_publish_time"),
        "scheduled_est": schedule_info.get("est_time_str"),
        "render_seconds": round(render_time, 1),
        "video_duration": qa_report["checks"].get("duration_seconds", 30.0),
        "mp4_path": str(output_mp4),
        "contact_sheet": str(project_dir / "work/contact_sheet.jpg"),
        "youtube_video_id": upload_result.get("video_id"),
        "youtube_url": upload_result.get("url"),
        "qa_status": qa_report["status"]
    }

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    history = []
    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(record)
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return record


def main():
    parser = argparse.ArgumentParser(description="Master Arcade Motion Graphics YouTube Autopilot")
    parser.add_argument("--dry-run", action="store_true", help="Run full pipeline locally without uploading to YouTube")
    parser.add_argument("--mock-views", type=int, help="Mock 24h view count to test quota scaling (e.g. 5000, 25000, 100000)")
    parser.add_argument("--force-quota", type=int, choices=[1, 3, 5], help="Force daily quota to 1, 3, or 5")
    parser.add_argument("--topic", type=str, help="Specific topic slug to generate")
    args = parser.parse_args()

    print("\n==================================================================")
    print("🚀 AUTOMATION V3: AUTONOMOUS ARCADE MOTION GRAPHICS PIPELINE")
    print("==================================================================")

    # 1. Determine dynamic daily quota
    quota_info = get_daily_upload_quota(force_quota=args.force_quota, mock_views=args.mock_views)
    quota = quota_info["quota"]
    print(f"\n📊 Dynamic Analytics Evaluation:")
    print(f"   Max 24h Single-Video Views: {quota_info['max_24h_views']:,}")
    print(f"   Target Daily Quota: {quota} video(s)")
    print(f"   Tier: {quota_info['tier_description']}")

    # 2. Calculate High-RPM Schedules
    schedules = calculate_schedule_times(quota)
    print(f"\n📅 High-RPM Publication Schedule (US Eastern Peak Windows):")
    for s in schedules:
        print(f"   Slot {s['slot_index']}/{quota}: {s['est_time_str']} -> UTC: {s['iso_publish_time']}")

    # 3. Generate episodes for today's quota
    results = []
    for idx in range(quota):
        sched = schedules[idx]
        if args.topic and idx == 0:
            story = select_topic_for_today(forced_slug=args.topic)
        else:
            story = CURATED_STORIES[idx % len(CURATED_STORIES)]

        record = run_episode_pipeline(story, sched, dry_run=args.dry_run)
        results.append(record)

    print("\n==================================================================")
    print(f"🎉 PIPELINE EXECUTION COMPLETE: {len(results)} episode(s) generated.")
    for r in results:
        print(f"   • {r['title']} | Render: {r['render_seconds']}s | Scheduled: {r['scheduled_est']} | URL: {r.get('youtube_url')}")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
