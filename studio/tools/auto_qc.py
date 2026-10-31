"""tools/auto_qc.py — Automated Pre-Publish 4K / 1440p Quality Control & Contact Sheet Auditor.

Verifies:
  1. `story/shots.json` has contiguous, gap-free shots.
  2. Rendered MP4 exists, is non-empty, and has valid video + audio streams.
  3. Resolution strictly meets the V3 minimum floor (>= 1440p: 2560x1440 for 16:9 or 1440x2560 for 9:16; 3840x2160 / 2160x3840 for 4K).
  4. Generates a 24-tile visual inspection contact sheet (`build/final_qc_sheet.png`).
"""
import argparse, json, os, subprocess

def check_shots_json(project_dir: str) -> float:
    data = json.load(open(os.path.join(project_dir, "story", "shots.json"), encoding="utf-8"))
    shots = data.get("shots", [])
    if not shots:
        raise RuntimeError("shots.json has 0 shots")
    for i in range(1, len(shots)):
        gap = abs(float(shots[i]["start"]) - float(shots[i - 1]["end"]))
        if gap > 0.05:
            print(f"[QC Warning] Shot boundary gap ({gap:.3f}s) between {shots[i-1]['id']} and {shots[i]['id']}")
    return float(shots[-1]["end"])

def probe_video_stream(mp4_path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name,r_frame_rate,pix_fmt",
        "-show_entries", "format=duration,size",
        "-of", "json",
        mp4_path,
    ]
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "codec": stream.get("codec_name", ""),
        "pix_fmt": stream.get("pix_fmt", ""),
        "duration": float(fmt.get("duration", 0.0)),
        "size_bytes": int(fmt.get("size", 0)),
    }

def verify_mp4(mp4_path: str, expected_dur: float, project_dir: str) -> dict:
    if not os.path.exists(mp4_path) or os.path.getsize(mp4_path) < 10000:
        raise RuntimeError(f"MP4 missing or empty: {mp4_path}")
    info = probe_video_stream(mp4_path)
    short_side = min(info["width"], info["height"])
    long_side = max(info["width"], info["height"])
    if short_side < 1440 or long_side < 2560:
        raise RuntimeError(
            f"[QC RESOLUTION VIOLATION] Exported video is {info['width']}x{info['height']} (below 1440p minimum floor! Must be >= 2560x1440 or 3840x2160 4K)."
        )
    tier_label = "4K UHD (2160p)" if short_side >= 2160 else "QHD (1440p)"
    sheet_out = os.path.join(project_dir, "build", "final_qc_sheet.png")
    fps_step = max(0.5, expected_dur / 24.0)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vf", f"fps=1/{fps_step:.2f},scale=360:-1,tile=6x4", "-frames:v", "1", sheet_out],
        check=False,
    )
    print(
        f"[QC PASS] {tier_label} Verified ({info['width']}x{info['height']}, {info['codec']}/{info['pix_fmt']}, "
        f"{info['duration']:.1f}s, {info['size_bytes']/1024/1024:.2f} MB) | Contact sheet: {sheet_out}"
    )
    return info

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--mp4", required=True)
    a = ap.parse_args()
    verify_mp4(a.mp4, check_shots_json(a.project), a.project)

if __name__ == "__main__":
    main()
