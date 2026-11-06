"""Cross-platform Python implementation of selftest.sh.
Proves the install works: builds the worked example ("How Mario was born", 30 s, 9:16)
end to end: Kokoro voice -> word timings -> chiptune + effects -> mix -> HyperFrames render.
"""
import sys, os, subprocess, shutil
from pathlib import Path

AMG = Path(os.environ.get("AMG", Path(__file__).resolve().parent.parent))
tools = AMG / "tools"
P = Path.home() / "arcade-motiongraphics/_selftest"

print(f"=== ARCADE MOTION GRAPHICS SELFTEST ===")
print(f"Skill root: {AMG}")
print(f"Target dir: {P}")

if P.exists():
    shutil.rmtree(P)

# 1. New film
print("\n[1/8] Initializing project template...")
subprocess.run([sys.executable, str(tools / "new_film.py"), str(P), "Selftest"], check=True)

# 2. Voiceover (vo.py)
print("\n[2/8] Generating Kokoro voiceover (vo.py)...")
subprocess.run([sys.executable, str(tools / "vo.py"), str(P)], check=True)

# 3. Forced alignment (align.py)
print("\n[3/8] Aligning word timestamps via Wav2Vec2 (align.py)...")
subprocess.run([sys.executable, str(tools / "align.py"), str(P)], check=True)

# 4. Words JS (words_js.py)
print("\n[4/8] Generating words.js (words_js.py)...")
subprocess.run([sys.executable, str(tools / "words_js.py"), str(P)], check=True)

# 5. Make cues
print("\n[5/8] Generating SFX cues (make_cues.py)...")
subprocess.run([sys.executable, str(P / "work/make_cues.py")], cwd=str(P), check=True)

# 6. Chiptune synthesis (chip.py)
print("\n[6/8] Synthesizing 8-bit chiptune score & SFX (chip.py)...")
subprocess.run([sys.executable, str(tools / "chip.py"), str(P)], check=True)

# 7. Mix audio (mix.py)
print("\n[7/8] Mastering final audio mix (mix.py)...")
subprocess.run([sys.executable, str(tools / "mix.py"), str(P)], check=True)

# 8. Render video with HyperFrames
print("\n[8/8] Rendering 9:16 video via HyperFrames...")
# On Windows, npx needs shell=True or npx.cmd
npx_cmd = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
subprocess.run([npx_cmd, "--yes", "hyperframes@0.8.203", "render", ".", "-o", "renders/selftest.mp4", "-q", "delivery"], cwd=str(P), shell=True, check=True)

mp4_path = P / "renders/selftest.mp4"
if not mp4_path.exists():
    print("SELFTEST FAILED: renders/selftest.mp4 not found")
    sys.exit(1)

# Check duration via ffprobe
probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4_path)]
res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
duration = float(res.stdout.strip())
print(f"Rendered video duration: {duration:.2f}s")

# Generate contact sheet
sheet_path = P / "work/selftest_sheet.jpg"
sheet_cmd = [
    "ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4_path),
    "-vf", "fps=1,scale=216:-1,tile=10x3", "-frames:v", "1", str(sheet_path)
]
subprocess.run(sheet_cmd, check=True)

if duration > 25:
    print("\n==========================================")
    print(f"SELFTEST PASSED: {mp4_path} ({duration:.2f}s)")
    print(f"Contact Sheet: {sheet_path}")
    print("==========================================")
else:
    print(f"SELFTEST FAILED: Duration too short ({duration:.2f}s)")
    sys.exit(1)
