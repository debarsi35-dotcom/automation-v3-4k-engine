"""pipeline/shorts_generator.py — 5 Daily Standalone Viral Shorts / Reels Engine (4K 2160x3840 / 1440p 1440x2560).

Why Our 5 Daily Shorts Are Engineered as Standalone Money-Makers AND Long-Form Funnel Bridges:
  1. 100% Self-Contained Value: Viewers NEVER feel "clickbaited" or forced to leave the Short to get the answer.
     Each Short delivers a complete 4-stage viral arc inside 32–45 seconds:
       - Stage 1 (0.0–2.5s): Sensory Cold-Open Anomaly (Zero intro fluff)
       - Stage 2 (2.5–16.0s): Real Human Baseline vs. Extreme Paradox Escalation
       - Stage 3 (16.0–28.0s): Complete Scientific Payoff + Actionable Daily Brain/Body Hack
       - Stage 4 (28.0–35.0s): Seamless Verbal Loop + Subtle Channel Bridge ("Full 6-min 4K breakdown pinned on our channel")
  2. 5 Distinct Viral Angles Per Day (So platforms never flag them as duplicate spam):
       - Short #1 (`micro_anomaly`): The 0.025s Sensory Micro-Moment & Flicker Fusion Secret
       - Short #2 (`benchmark_duel`): Normal Human vs. 10x Biological Threshold Showdown
       - Short #3 (`timeline_escalation`): Hour 1 -> Day 7 -> Month 1 Biological Cascade
       - Short #4 (`brain_trap`): The Hidden Dopamine Prediction Error Trap & Real-Life Fix
       - Short #5 (`animal_superpower`): The Extreme Survival Choice & The Real Creature That Lives Like This
  3. True 4K Vertical (`2160x3840`) Preferable / `1440p` Vertical (`1440x2560`) Minimum:
     Rendered natively in 9:16 vertical aspect ratio with word-synced kinetic pop captions in the center safe zone and a custom 4K 9:16 cover thumbnail for each Short.
"""
import json, os, re, subprocess, sys
from llm_client import call_llm, extract_json, SWARM_TELEMETRY
from tts_aligner import generate_voiceover_and_timestamps
from ifverse_storyboard_director import _heuristic_shot_spec


BUILTIN_5_SHORTS_PACK = [
    {
        "short_index": 1,
        "angle": "micro_anomaly",
        "title": "What If 1 Second Felt Like 10 Inside Your Brain? #shorts",
        "hook_caption": "1 SEC = 10 SEC",
        "badge_text": "0.025s BRAIN",
        "bridge_text": "FULL 4K EXPERIMENT ON OUR CHANNEL",
        "spoken_script": (
            "A porcelain coffee cup slips off the table. "
            "A normal human brain takes a quarter of a second just to see it fall and move a muscle. "
            "You? You react in two and a half hundredths of a second. "
            "To your eyes, the falling mug hangs in mid-air like a frozen painting. "
            "Why? Because human vision runs at sixty frames per second, known as your critical flicker fusion rate. "
            "If a mutation boosted your visual cortex to six hundred frames per second, you could catch every drop effortlessly. "
            "There is just one terrifying catch. Your brain is ten times faster... your muscles are still human. "
            "Move too fast, and your own tendons snap before your hand reaches the cup... right as"
        ),
    },
    {
        "short_index": 2,
        "angle": "benchmark_duel",
        "title": "Normal Brain vs 10x Faster Brain (The Hidden Trap) #shorts",
        "hook_caption": "NORMAL VS 10X",
        "badge_text": "600 FPS EYES",
        "bridge_text": "WATCH THE FULL 6-MIN BREAKDOWN",
        "spoken_script": (
            "On average, a pro athlete reacts in zero point one five seconds. "
            "You? Zero point zero two five. "
            "At first, a ten times faster brain feels like the ultimate cheat code. "
            "A two hundred kilometer per hour tennis serve floats toward you like a slow-motion beach ball. "
            "You read an entire book on a twenty minute commute. "
            "But your brain already burns twenty percent of your body's total energy just running at normal speed. "
            "Pushing your neurons ten times harder floods your prefrontal cortex with toxic metabolic waste in minutes. "
            "Without an emergency cooling mechanism, thirty minutes of superhuman focus triggers a blinding shutdown... even though"
        ),
    },
    {
        "short_index": 3,
        "angle": "timeline_escalation",
        "title": "What Happens If Your Brain Speeds Up For 30 Days? #shorts",
        "hook_caption": "DAY 1 VS DAY 30",
        "badge_text": "TIME ISOLATION",
        "bridge_text": "FULL TIMELINE ON OUR CHANNEL",
        "spoken_script": (
            "Day one with a ten times faster brain: you feel invincible, dodging a skidding car in the rain with ten subjective seconds to spare. "
            "Day seven: every three minute conversation with your best friend feels like a thirty minute slow-motion lecture. "
            "You have to force yourself to wait before speaking so people don't think you are interrupting them. "
            "By day thirty, synaptic plasticity speeds the loop up even further. "
            "Every human voice around you drops into an unrecognizable low rumble. "
            "You saved everyone around you, but trapped yourself inside a silent museum where a single afternoon lasts two weeks... starting from"
        ),
    },
    {
        "short_index": 4,
        "angle": "brain_trap",
        "title": "Why Predicting Everything Destroys Your Dopamine #shorts",
        "hook_caption": "0% DOPAMINE",
        "badge_text": "PREDICTION TRAP",
        "bridge_text": "FULL NEUROSCIENCE EPISODE LINKED",
        "spoken_script": (
            "If your brain processed reality ten times faster, you would never feel joy again. "
            "Here is the real neuroscience why. "
            "Deep in your midbrain, dopamine neurons do not fire for rewards themselves. "
            "They fire for reward prediction errors... moments that surprise you by being better than expected. "
            "When your visual cortex runs at six hundred frames per second, you see every micro-expression and hear every punchline three seconds before a person finishes speaking. "
            "Zero surprise means zero dopamine spike. "
            "In real life, you can reset your own dopamine sensitivity today simply by removing predictable scrolling and seeking novel physical challenges... because"
        ),
    },
    {
        "short_index": 5,
        "angle": "animal_superpower",
        "title": "The Creature That Already Sees In Slow Motion #shorts",
        "hook_caption": "250 FPS VISION",
        "badge_text": "REAL BIOLOGY",
        "bridge_text": "FULL 4K EPISODE ON OUR CHANNEL",
        "spoken_script": (
            "Have you ever wondered why it is almost impossible to swat a housefly? "
            "It is not just reflexes. The fly literally lives in a different speed of time than you. "
            "While human eyes refresh at sixty frames per second, a housefly's visual system refreshes two hundred and fifty times every single second. "
            "To a fly, your hand moving at full speed looks like a slow-motion cloud drifting across the room. "
            "And in humans, during a life-or-death emergency, your amygdala floods your hippocampus with norepinephrine, recording memory four times denser so time feels dilated. "
            "If you could dial your brain speed up at will, would you flip the switch... knowing"
        ),
    },
]


def run_subagent9_shorts_architect(idea: dict, script_data: dict, use_llm: bool = True) -> list[dict]:
    """Subagent 9 (`ViralShortsArchitectAgent`): Designs 5 standalone, self-contained 9:16 Shorts from today's topic."""
    if not use_llm:
        return BUILTIN_5_SHORTS_PACK

    sys_prompt = (
        "You are Subagent 9 (ViralShortsArchitect). Given today's main TED-Ed × Ifverse video topic and script, "
        "create EXACTLY 5 standalone, self-contained vertical Shorts/Reels scripts (75–105 words each, ~32–42 seconds). "
        "CRITICAL RULES:\n"
        "1. Each Short MUST be 100% self-contained so a viewer on YouTube Shorts, Instagram Reels, Facebook Reels, or Snapchat Spotlight "
        "gets a complete, mind-blowing scientific paradox AND its resolution without needing to watch the long video.\n"
        "2. Each Short must take a DIFFERENT viral angle:\n"
        "   - Short 1 (`micro_anomaly`): Sensory micro-moment + core biological rule\n"
        "   - Short 2 (`benchmark_duel`): Normal Human vs Extreme Threshold numerical duel\n"
        "   - Short 3 (`timeline_escalation`): Day 1 -> Day 7 -> Day 30 escalation consequence\n"
        "   - Short 4 (`brain_trap`): Deep brain/body mechanism backfire + 1 real-life actionable habit\n"
        "   - Short 5 (`animal_superpower`): Real-world animal/clinical equivalent + open dilemma\n"
        "3. End the final sentence with an open connector phrase ('...right as', '...because') that loops seamlessly into the first word.\n"
        "Return STRICT JSON: {\"shorts\": [{\"short_index\": 1, \"angle\": \"...\", \"title\": \"... #shorts\", "
        "\"hook_caption\": \"2-3 WORDS\", \"badge_text\": \"SHORT METRIC\", \"bridge_text\": \"FULL 4K VIDEO ON CHANNEL\", \"spoken_script\": \"...\"}]}"
    )
    usr_prompt = (
        f"Main Video Title: {script_data.get('title')}\n"
        f"Core Paradox: {idea.get('core_paradox', '')}\n"
        f"Limiting Rule: {idea.get('limiting_rule', '')}\n"
        f"Mechanisms: {', '.join(script_data.get('scientific_references', []))}\n"
        f"Main Script Excerpt: {script_data.get('spoken_script', '')[:1200]}"
    )
    try:
        raw = call_llm(
            sys_prompt, usr_prompt, expect_json=True, temperature=0.7,
            task_tier="creative_writer", subagent_name="Subagent9_ViralShortsArchitect", max_tokens=2200
        )
        parsed = extract_json(raw).get("shorts", [])
        if len(parsed) >= 5:
            SWARM_TELEMETRY["estimated_tokens_saved"] += 3800
            return parsed[:5]
    except Exception as e:
        print(f"  [Swarm:Subagent9_ViralShortsArchitect] Falling back to built-in 5-Shorts pack ({e})")
    return BUILTIN_5_SHORTS_PACK


def build_and_render_5_shorts(
    main_project_dir: str,
    studio_dir: str,
    idea: dict,
    script_data: dict,
    resolution: str = "2160p",
    style: str = "ted_ifverse",
    voice: str = "en-US-AndrewNeural",
    workers: int = 2,
    use_llm: bool = True,
    demo_fast: bool = False,
    count: int = 5,
) -> list[dict]:
    """Generate, align, storyboard, render (at 4K 2160x3840 or 1440p 1440x2560), mix audio, and create 9:16 thumbnails for all 5 daily Shorts."""
    shorts_specs = run_subagent9_shorts_architect(idea, script_data, use_llm=use_llm)[:count]
    shorts_out_root = os.path.join(main_project_dir, "out", "shorts")
    os.makedirs(shorts_out_root, exist_ok=True)

    # Enforce minimum 1440p floor and preferable 2160p (4K)
    target_res = "1440p" if resolution.lower() in ("1440p", "2k", "qhd") else "2160p"
    sets_cycle = ["cafe", "lab", "street", "bedroom", "rooftop", "hospital", "classroom", "park"]
    rendered_shorts = []

    for spec in shorts_specs:
        idx = int(spec.get("short_index", len(rendered_shorts) + 1))
        short_slug = f"short_{idx}_{re.sub(r'[^a-z0-9]+', '_', spec.get('angle', 'viral').lower()).strip('_')}"
        s_dir = os.path.join(main_project_dir, "shorts_projects", short_slug)
        for sub in ("input", "timeline", "story", "scenes/sets", "scenes/shots", "build", "out"):
            os.makedirs(os.path.join(s_dir, sub), exist_ok=True)

        spoken = spec.get("spoken_script", "").strip()
        if demo_fast:
            # Fast smoke-test slice (first 24 words) when --demo-short is active
            spoken = " ".join(spoken.split()[:24])

        s_cfg = {
            "title": spec.get("title", f"Short #{idx}"),
            "aspect": "9:16",
            "resolution": target_res,
            "fps": 24,
            "style": style,
            "voiceover": "input/voiceover.mp3",
            "script": "input/script.txt",
            "duration": 0,
            "captions": True,
            "bars": "none",
            "fadeIn": 0.25,
            "fadeOut": 0.35,
            "thumbnailText": spec.get("hook_caption", "1 SEC = 10 SEC"),
            "thumbnailBadge": spec.get("badge_text", "10x BRAIN"),
            "bridgeText": spec.get("bridge_text", "FULL 4K VIDEO ON CHANNEL"),
            "music": {"enabled": True, "gainDb": -16, "seed": 10 + idx},
            "sfx": {"enabled": True, "gainDb": -5},
            "loudness": -14,
        }
        with open(os.path.join(s_dir, "config.json"), "w", encoding="utf-8") as f:
            json.dump(s_cfg, f, indent=2)

        # Copy cast.js
        cast = script_data.get("cast") or {
            "HERO": {"top": "hoodie", "color": "#d64a33", "head": "none"},
            "FRIEND": {"top": "tshirt", "color": "#3a6ea5", "head": "cap", "headColor": "#f2c21a"},
            "SCIENTIST": {"top": "labcoat", "face": "glasses", "head": "none"},
        }
        cast_js = f"window.PROJECT_CAST = {json.dumps(cast, indent=2)};\n"
        with open(os.path.join(s_dir, "scenes", "cast.js"), "w", encoding="utf-8") as f:
            f.write(cast_js)

        # 1. Generate voiceover + exact word timestamps (faster +2% pacing for snappy Shorts retention)
        tts_info = generate_voiceover_and_timestamps(s_dir, spoken, studio_dir, voice=voice, rate="+2%")
        beats = json.load(open(os.path.join(s_dir, "timeline", "beats.json"), encoding="utf-8"))
        total_dur = round(float(beats[-1]["end"]), 3)

        # 2. Build tight 9:16 vertical storyboard with high-velocity visual transitions
        shots = []
        short_templates = [
            "big_face_reaction", "time_freeze", "blueprint_compare", "establishing_wide",
            "blueprint_pipeline", "data_card_counter", "medium_two_shot", "timeline_progression", "end_screen"
        ]
        for b_i, b in enumerate(beats):
            sid = f"s{b_i + 1:03d}"
            base_spec = _heuristic_shot_spec(b_i, len(beats), b["text"], s_cfg["title"], sets_cycle)
            tpl = short_templates[b_i % (len(short_templates) - 1)]
            if b_i == 0:
                tpl = "time_freeze" if idx in (1, 5) else "big_face_reaction"
            elif b_i == len(beats) - 1:
                tpl = "end_screen"
            shots.append({
                "id": sid,
                "start": round(float(b["start"]), 3),
                "end": round(float(b["end"]), 3),
                "line": b["text"],
                "template": tpl,
                "set": sets_cycle[(b_i + idx) % len(sets_cycle)],
                "scene": f"Short #{idx} ({spec.get('angle')}): {b['text'][:44]}",
                "bars": "none",
                "in": {"type": "whip" if b_i % 3 == 1 else "flash" if b_i == 1 else "cut", "dur": 0.28},
                "sfx": base_spec.get("sfx", [{"at": 0.05, "name": "whoosh", "gain": -10}]),
                "amb": base_spec.get("amb", {"name": "roomtone", "gain": -25}),
                "params": {
                    **base_spec.get("params", {}),
                    "badge": s_cfg["thumbnailBadge"],
                    "question": "Watch the full 4K breakdown on our channel!",
                },
                "captions": True,
            })

        punchline_drops = []
        if len(shots) >= 3:
            p_shot = shots[max(1, len(shots) - 2)]
            punchline_drops = [{"start": round(p_shot["start"], 2), "end": round(min(p_shot["end"], p_shot["start"] + 0.95), 2)}]

        shots_payload = {
            "title": s_cfg["title"],
            "duration": total_dur,
            "shots": shots,
            "music": [
                {"start": 0.0, "end": round(total_dur * 0.45, 2), "mood": "tension", "intensity": 0.65},
                {"start": round(total_dur * 0.45, 2), "end": total_dur, "mood": "action", "intensity": 0.80},
            ],
            "punchline_drops": punchline_drops,
        }
        with open(os.path.join(s_dir, "story", "shots.json"), "w", encoding="utf-8") as f:
            json.dump(shots_payload, f, indent=2)

        # 3. Render 4K (2160x3840) / 1440p (1440x2560) 9:16 Vertical Thumbnail
        thumb_png = os.path.join(shorts_out_root, f"short_{idx}_thumb.png")
        subprocess.run(
            [
                "node", "tools/render_thumbnail.mjs",
                "--project", s_dir,
                "--text", s_cfg["thumbnailText"],
                "--badge", s_cfg["thumbnailBadge"],
                "--aspect", "9:16",
                "--style", style,
                "--out", thumb_png,
            ],
            cwd=studio_dir,
            check=True,
        )

        # 4. Render 9:16 Vertical Short Video at 4K (2160p) or 1440p
        silent_mp4 = os.path.join(s_dir, "build", "video_silent.mp4")
        subprocess.run(
            [
                "node", "render.mjs",
                "--project", s_dir,
                "--resolution", target_res,
                "--workers", str(workers),
                "--format", "jpeg",
                "--out", silent_mp4,
            ],
            cwd=studio_dir,
            check=True,
        )

        # 5. Mix Audio + Punchline Drops + Master to -14 LUFS
        final_short_mp4 = os.path.join(shorts_out_root, f"short_{idx}_{spec.get('angle', 'viral')}_{target_res}.mp4")
        subprocess.run(
            [
                sys.executable, os.path.join(studio_dir, "audio", "mix.py"),
                "--project", s_dir,
                "--video", silent_mp4,
                "--out", final_short_mp4,
            ],
            check=True,
        )

        # 6. Run 4K/1440p Resolution & Integrity QC
        subprocess.run(
            [sys.executable, os.path.join(studio_dir, "tools", "auto_qc.py"), "--project", s_dir, "--mp4", final_short_mp4],
            check=True,
        )

        rendered_shorts.append({
            "short_index": idx,
            "angle": spec.get("angle"),
            "title": s_cfg["title"],
            "hook_caption": s_cfg["thumbnailText"],
            "badge_text": s_cfg["thumbnailBadge"],
            "duration_sec": total_dur,
            "resolution": target_res,
            "mp4_path": final_short_mp4,
            "thumbnail_path": thumb_png,
            "thumbnail_jpg_path": os.path.splitext(thumb_png)[0] + ".jpg",
            "spoken_script": spoken,
        })
        print(f"  [Shorts Engine V3] Completed Short #{idx}/5 ({target_res} 9:16): {final_short_mp4}")

    manifest_path = os.path.join(shorts_out_root, "shorts_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(rendered_shorts, f, indent=2)
    return rendered_shorts
