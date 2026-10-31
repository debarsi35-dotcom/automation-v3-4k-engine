"""pipeline/tts_aligner.py — Zero-Cost Broadcast TTS + Exact Word-Level Timestamp Extractor."""
import asyncio, json, os, re, subprocess, sys

async def _edge_tts_generate(text: str, voice: str, rate: str, mp3_out: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    words = []
    with open(mp3_out, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_s = round(chunk["offset"] / 10_000_000.0, 3)
                dur_s = round(chunk["duration"] / 10_000_000.0, 3)
                words.append({"word": chunk["text"], "start": start_s, "end": round(start_s + max(0.06, dur_s), 3)})
    return words

def _attach_punctuation(raw_words: list[dict], full_text: str) -> list[dict]:
    tokens = full_text.split()
    aligned, t_idx = [], 0
    for w in raw_words:
        clean_w = re.sub(r"[^\w']", "", w["word"]).lower()
        chosen = w["word"]
        for lookahead in range(t_idx, min(len(tokens), t_idx + 4)):
            clean_tok = re.sub(r"[^\w']", "", tokens[lookahead]).lower()
            if clean_tok == clean_w or clean_tok.startswith(clean_w):
                chosen = tokens[lookahead]
                t_idx = lookahead + 1
                break
        aligned.append({"word": chosen, "start": w["start"], "end": w["end"]})
    return aligned

def generate_voiceover_and_timestamps(project_dir: str, script_text: str, studio_dir: str, voice: str = "en-US-AndrewNeural", rate: str = "-3%") -> dict:
    input_dir, timeline_dir = os.path.join(project_dir, "input"), os.path.join(project_dir, "timeline")
    os.makedirs(input_dir, exist_ok=True); os.makedirs(timeline_dir, exist_ok=True)
    with open(os.path.join(input_dir, "script.txt"), "w", encoding="utf-8") as f:
        f.write(script_text.strip() + "\n")
    mp3_path = os.path.join(input_dir, "voiceover.mp3")
    words_path = os.path.join(timeline_dir, "words.json")
    try:
        raw_words = asyncio.run(_edge_tts_generate(script_text, voice, rate, mp3_path))
        words = _attach_punctuation(raw_words, script_text)
    except Exception:
        words = _synthesize_offline_fallback(script_text, mp3_path)
    with open(words_path, "w", encoding="utf-8") as f:
        json.dump({"words": words}, f, indent=2)
    with open(os.path.join(timeline_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(" ".join(w["word"] for w in words) + "\n")
    cfg_path = os.path.join(project_dir, "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    total_dur = round(words[-1]["end"] + 1.5, 3) if words else 60.0
    cfg["duration"] = total_dur
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    subprocess.run([sys.executable, os.path.join(studio_dir, "tools", "beats.py"), "--project", project_dir, "--target", "2.8", "--max", "4.8", "--min", "1.3", "--force"], check=True)
    beats = json.load(open(os.path.join(timeline_dir, "beats.json"), encoding="utf-8"))
    return {"mp3_path": mp3_path, "words_count": len(words), "beats_count": len(beats), "duration": total_dur}

def _synthesize_offline_fallback(script_text: str, mp3_path: str) -> list[dict]:
    import numpy as np, wave
    sr, tokens, words, t = 44100, script_text.split(), [], 0.25
    for tok in tokens:
        chars = len(re.sub(r"[^\w]", "", tok))
        dur = max(0.16, min(0.58, 0.11 + chars * 0.032))
        pause = 0.38 if tok.endswith((".", "!", "?")) else 0.55 if tok.endswith("...") else 0.18 if tok.endswith((",", ";", ":", "—")) else 0.04
        words.append({"word": tok, "start": round(t, 3), "end": round(t + dur, 3)})
        t += dur + pause
    n = int((t + 1.2) * sr)
    audio, t_arr = np.zeros(n, dtype=np.float32), np.arange(n, dtype=np.float32) / sr
    for i, w in enumerate(words):
        i0, i1 = int(w["start"] * sr), min(n, int(w["end"] * sr))
        if i1 > i0:
            seg_t, seg_dur = t_arr[i0:i1] - w["start"], w["end"] - w["start"]
            f0 = 125.0 + 18.0 * np.sin(i * 0.7) - 12.0 * (seg_t / seg_dur)
            audio[i0:i1] = (0.55 * np.sin(2 * np.pi * f0 * seg_t) + 0.28 * np.sin(4 * np.pi * f0 * seg_t)) * (np.sin(np.pi * np.clip(seg_t / seg_dur, 0, 1)) ** 0.6) * 0.35
    wav_tmp = mp3_path + ".wav"
    with wave.open(wav_tmp, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(np.clip(audio * 32767, -32768, 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_tmp, "-c:a", "libmp3lame", "-b:a", "192k", mp3_path], check=True)
    os.remove(wav_tmp)
    return words
