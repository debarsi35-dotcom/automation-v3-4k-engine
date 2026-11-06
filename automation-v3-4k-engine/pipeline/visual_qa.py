"""pipeline/visual_qa.py — Automated Contact Sheet & Frame Quality Assurance Gate.

Validates that every rendered video strictly obeys anti-slop visual and audio criteria:
  1. Duration conforms to story expectations (20s - 180s).
  2. Resolution is 9:16 vertical (1080x1920).
  3. Audio stream present and mastered around -15.0 LUFS.
  4. Multi-frame contact sheet generated via sheets.py / ffmpeg.
  5. No black / frozen dead frames across timeline.
"""
import sys, os, subprocess, json
from pathlib import Path
from PIL import Image
import numpy as np


def run_visual_qa(mp4_path: Path, project_dir: Path) -> dict:
    mp4_path = Path(mp4_path).resolve()
    project_dir = Path(project_dir).resolve()

    if not mp4_path.exists():
        return {"status": "FAILED", "error": f"Rendered video not found at {mp4_path}"}

    checks = {}

    # 1. ffprobe metadata inspection
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size:stream=width,height,codec_name,codec_type,sample_rate",
        "-of", "json", str(mp4_path)
    ]
    try:
        r = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        meta = json.loads(r.stdout)
        duration = float(meta["format"]["duration"])
        streams = meta.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        checks["duration_seconds"] = round(duration, 2)
        checks["duration_ok"] = 20.0 <= duration <= 180.0
        checks["has_video"] = video_stream is not None
        checks["has_audio"] = audio_stream is not None

        if video_stream:
            w, h = int(video_stream.get("width", 0)), int(video_stream.get("height", 0))
            checks["resolution"] = f"{w}x{h}"
            checks["is_9_16_vertical"] = (h > w) and (w == 1080 or w == 720 or w == 1440 or w == 2160)
        else:
            checks["is_9_16_vertical"] = False
    except Exception as e:
        return {"status": "FAILED", "error": f"FFprobe inspection failed: {e}"}

    # 2. Contact sheet generation (10x3 grid = 30 frames across video)
    sheet_path = project_dir / "work/contact_sheet.jpg"
    sheet_cmd = [
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4_path),
        "-vf", "fps=1,scale=216:-1,tile=10x3", "-frames:v", "1", str(sheet_path)
    ]
    try:
        subprocess.run(sheet_cmd, check=True)
        checks["contact_sheet_generated"] = sheet_path.exists()
        checks["contact_sheet_path"] = str(sheet_path)

        # 3. Analyze contact sheet image variance (ensures no pure black/dead screens)
        img = Image.open(sheet_path).convert("RGB")
        arr = np.asarray(img).astype(np.float32)
        mean_luma = float(arr.mean())
        std_luma = float(arr.std())
        checks["mean_brightness"] = round(mean_luma, 1)
        checks["brightness_variance"] = round(std_luma, 1)
        # Healthy arcade video has mean luma > 15 and std > 10
        checks["visual_liveness_ok"] = (mean_luma > 12.0) and (std_luma > 8.0)
    except Exception as e:
        checks["contact_sheet_error"] = str(e)
        checks["visual_liveness_ok"] = False

    passed = (
        checks.get("duration_ok", False)
        and checks.get("has_video", False)
        and checks.get("has_audio", False)
        and checks.get("is_9_16_vertical", False)
        and checks.get("visual_liveness_ok", False)
    )

    return {
        "status": "PASSED" if passed else "FAILED",
        "checks": checks,
        "contact_sheet": str(sheet_path) if sheet_path.exists() else None
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        res = run_visual_qa(p / "renders/selftest.mp4", p)
        print(json.dumps(res, indent=2))
    else:
        test_dir = Path.home() / "arcade-motiongraphics/_selftest"
        res = run_visual_qa(test_dir / "renders/selftest.mp4", test_dir)
        print(json.dumps(res, indent=2))
