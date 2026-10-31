"""pipeline/swarm_orchestrator.py — 9-Subagent Token-Frugal Swarm Engine for Automation V3.

Upgraded from V2.1's 8 Subagents to 9 Specialized Video & Shorts Micro-Subagents:
  1. `TrendHarvesterAgent` (0 LLM tokens — Python RSS Scraper) -> Compresses live YouTube outlier signals into a 120-token digest.
  2. `ParadoxIdeatorAgent` (`fast_light` tier) -> Generates 5 high-CTR TED-Ed × Ifverse candidate concepts optimized for US/UK/CA/AU high-RPM audiences.
  3. `ViralCriticAgent` (`reasoning_heavy` tier) -> Scores candidates out of 100, picks #1 Winner, and locks The One Limiting Rule.
  4. `ActArchitectAgent` (`reasoning_heavy` tier) -> Designs the 6-Act Blueprint & Cast (exact scientific benchmarks per act).
  5. `ParallelActWriterSwarm` (`creative_writer` tier) -> 3 parallel micro-writers (`Writer_Act1_2`, `Writer_Act3_4`, `Writer_Act5_6`),
     each writing ~220–320 words so no model ever hits output token limits.
  6. `ScriptPolisherAndSEOAgent` (`fast_light` tier) -> Stitches Acts I–VI seamlessly and outputs US-targeted chapters, SEO tags & 4K thumbnail text.
  7. `MicroBatchStoryboardSwarm` (`structured_json` tier) -> Splits `beats.json` into micro-batches of 8 beats per subagent call,
     assigning the 12 Ifverse × TED-Ed shot templates, SFX cues, and punchline drops.
  8. `DeterministicSafetyNet` (0 LLM tokens) -> Instant local fallback for any micro-batch if all 22 cloud models are unreachable.
  9. `ViralShortsArchitectAgent` (`creative_writer` tier, in `shorts_generator.py`) -> Generates 5 standalone 9:16 vertical Shorts/Reels daily.
"""
import concurrent.futures, json, os, re
from llm_client import call_llm, extract_json, SWARM_TELEMETRY
from market_ideator import fetch_live_youtube_signals
from ifverse_storyboard_director import _heuristic_shot_spec


# ==============================================================================
# SUBAGENTS 1, 2 & 3: IDEATION & VIRAL CRITIC SWARM (High-RPM US/Tier-1 Calibrated)
# ==============================================================================
def run_ideation_swarm(history_path: str, custom_focus: str = "") -> dict:
    # Subagent 1: TrendHarvesterAgent (0 tokens)
    signals = fetch_live_youtube_signals()[:8]
    history = []
    if os.path.exists(history_path):
        try:
            history = [h.get("title", "") for h in json.load(open(history_path, encoding="utf-8"))][-15:]
        except Exception:
            history = []

    # Subagent 2: ParadoxIdeatorAgent (~300 tokens)
    ideator_sys = (
        "You are Subagent 2 (ParadoxIdeator). Generate 5 viral YouTube titles (6-10 words, <62 chars) fusing "
        "Ifverse ('What If You Had 500 IQ?', 'What If One Second Felt Like Ten?') with TED-Ed ('What if you didn't brush your teeth for a year?'). "
        "Target high-RPM US/UK/CA/AU viewer curiosity: alter ONE everyday human brain/body ability or habit and push it to a numerical extreme. "
        "Return STRICT JSON: {\"ideas\": [{\"title\": \"...\", \"paradox\": \"1-sentence scientific backfire\"}]}"
    )
    ideator_usr = (
        f"Live Signals: {'; '.join(signals)}\n"
        f"Avoid: {'; '.join(history) if history else 'None'}\n"
        f"Focus: {custom_focus or 'Human brain, time perception, memory, sleep, dopamine, longevity, biology paradoxes'}"
    )
    raw_ideas = call_llm(
        ideator_sys, ideator_usr, expect_json=True, temperature=0.8, task_tier="fast_light", subagent_name="Subagent2_ParadoxIdeator", max_tokens=700
    )
    ideas_list = extract_json(raw_ideas).get("ideas", [])

    # Subagent 3: ViralCriticAgent (~350 tokens)
    critic_sys = (
        "You are Subagent 3 (ViralCritic & Science Lock). Pick the #1 highest-CTR concept from the candidate list and enrich it with "
        "real peer-reviewed neuroscience/biology benchmarks for a 3-7 minute 4K TED-Ed × Ifverse animation. "
        "Return STRICT JSON: {"
        "\"title\": \"...\", \"viral_score\": 98, \"core_paradox\": \"...\", "
        "\"cold_open_hook\": \"Exact first 2 sentences (sensory scene + benchmark vs You?)\", "
        "\"limiting_rule\": \"The 1 real physical/biological constraint that makes this dangerous\", "
        "\"scientific_mechanisms\": [\"Named mechanism 1\", \"Named mechanism 2\", \"Named mechanism 3\"], "
        "\"thumbnail_text\": \"2-3 WORD HOOK\", \"thumbnail_badge\": \"SHORT METRIC\"}"
    )
    raw_winner = call_llm(
        critic_sys,
        json.dumps(ideas_list),
        expect_json=True,
        temperature=0.5,
        task_tier="reasoning_heavy",
        subagent_name="Subagent3_ViralCritic",
        max_tokens=800,
    )
    winner = extract_json(raw_winner)
    SWARM_TELEMETRY["estimated_tokens_saved"] += 3200
    return {"winner": winner, "candidates": ideas_list}


# ==============================================================================
# SUBAGENTS 4, 5A/5B/5C & 6: 6-ACT SCRIPTWRITING SWARM
# ==============================================================================
def run_scriptwriting_swarm(idea: dict) -> dict:
    # Subagent 4: ActArchitectAgent (~400 tokens)
    arch_sys = (
        "You are Subagent 4 (ActArchitect). Design a compact 6-Act Story & Science Blueprint for a 5-minute (700-word) "
        "TED-Ed × Ifverse video told in 2nd person ('you', hero named Max, best friend Jake, scientist Dr. Lee). "
        "Return STRICT JSON: {"
        "\"act1_2_brief\": \"Cold open scene + exact baseline number vs You + The 1 Limiting Rule\", "
        "\"act3_4_brief\": \"4 escalating timeline beats (Day 1 -> Month 1) + deep TED-Ed brain/body mechanism analogy\", "
        "\"act5_6_brief\": \"High-stakes crisis choice with Jake/Dr. Lee + real-world biology takeaway & comment question\"}"
    )
    raw_arch = call_llm(
        arch_sys,
        json.dumps(idea),
        expect_json=True,
        temperature=0.6,
        task_tier="reasoning_heavy",
        subagent_name="Subagent4_ActArchitect",
        max_tokens=700,
    )
    arch = extract_json(raw_arch)

    writer_base_rules = (
        "Write pure spoken narration for TTS in the fused style of Ifverse (2nd-person 'you', short punchy 5-10 word sentences, "
        "benchmark-then-'You?' contrasts, inline 1-line reactions from Jake or Dr. Lee without speaker labels) and TED-Ed "
        "(vivid scientific analogies and real numbers). Use American English phrasing for high-RPM US/UK/CA/AU retention. "
        "NO [VISUAL] tags, NO speaker names ('MAX:'), NO markdown bold. "
        "Return STRICT JSON: {\"spoken_text\": \"...\"}"
    )

    def _write_chunk(agent_id: str, act_label: str, brief: str, word_target: str) -> str:
        prompt = (
            f"Video Title: {idea.get('title')}\n"
            f"Limiting Rule: {idea.get('limiting_rule')}\n"
            f"Scientific Mechanisms: {', '.join(idea.get('scientific_mechanisms', []))}\n"
            f"Your Assigned Section ({act_label} — target {word_target} words):\n{brief}"
        )
        res = call_llm(
            writer_base_rules,
            prompt,
            expect_json=True,
            temperature=0.72,
            task_tier="creative_writer",
            subagent_name=agent_id,
            max_tokens=1100,
        )
        return extract_json(res).get("spoken_text", "").strip()

    # Subagents 5A, 5B, 5C run in parallel across different models in the mesh!
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        f_12 = ex.submit(_write_chunk, "Subagent5A_Writer_Act1_2", "Acts I & II (Cold Open + Rule)", arch.get("act1_2_brief", ""), "150-180")
        f_34 = ex.submit(_write_chunk, "Subagent5B_Writer_Act3_4", "Acts III & IV (Montage + Deep Science)", arch.get("act3_4_brief", ""), "280-340")
        f_56 = ex.submit(_write_chunk, "Subagent5C_Writer_Act5_6", "Acts V & VI (Climax + TED-Ed Takeaway)", arch.get("act5_6_brief", ""), "200-250")
        part_12 = f_12.result()
        part_34 = f_34.result()
        part_56 = f_56.result()

    full_script = f"{part_12} {part_34} {part_56}".strip()
    full_script = re.sub(r"\[[^\]]*\]", "", full_script)
    full_script = re.sub(r"\s+", " ", full_script).strip()

    # Subagent 6: ScriptPolisherAndSEOAgent (~300 tokens)
    seo_sys = (
        "You are Subagent 6 (Packaging & US High-RPM SEO). Given the video title and scientific mechanisms, output YouTube metadata "
        "optimized for US/UK/Canada/Australia audiences. "
        "Return STRICT JSON: {"
        "\"alt_titles\": [\"...\", \"...\", \"...\"], "
        "\"thumbnail_text\": \"2-4 WORDS\", \"thumbnail_badge\": \"SHORT METRIC\", "
        "\"youtube_description\": \"2-paragraph engaging summary\", "
        "\"youtube_tags\": [\"tag1\", \"tag2\", \"tag3\", \"tag4\", \"tag5\", \"tag6\"]}"
    )
    raw_seo = call_llm(
        seo_sys,
        f"Title: {idea.get('title')}\nMechanisms: {idea.get('scientific_mechanisms')}",
        expect_json=True,
        temperature=0.6,
        task_tier="fast_light",
        subagent_name="Subagent6_PackagingSEO",
        max_tokens=600,
    )
    seo = extract_json(raw_seo)
    SWARM_TELEMETRY["estimated_tokens_saved"] += 6400

    return {
        "title": idea.get("title", "What If?"),
        "alt_titles": seo.get("alt_titles", []),
        "style": "ted_ifverse",
        "word_count": len(full_script.split()),
        "thumbnail_text": seo.get("thumbnail_text") or idea.get("thumbnail_text", "1 SEC = 10 SEC"),
        "thumbnail_badge": seo.get("thumbnail_badge") or idea.get("thumbnail_badge", "10x BRAIN"),
        "cast": {
            "HERO": {"top": "hoodie", "color": "#d64a33", "head": "none"},
            "FRIEND": {"top": "tshirt", "color": "#3a6ea5", "head": "cap", "headColor": "#f2c21a"},
            "SCIENTIST": {"top": "labcoat", "face": "glasses", "head": "none"},
        },
        "spoken_script": full_script,
        "chapters": [
            {"time": "0:00", "title": "The Everyday Anomaly"},
            {"time": "0:40", "title": "The One Biological Rule"},
            {"time": "1:25", "title": "The Escalation Montage"},
            {"time": "2:45", "title": "Inside the Brain & Body Mechanism"},
            {"time": "3:55", "title": "The Breaking Point & Choice"},
            {"time": "4:55", "title": "Real Science & Daily Takeaway"},
        ],
        "scientific_references": idea.get("scientific_mechanisms", []),
        "youtube_description": seo.get("youtube_description", ""),
        "youtube_tags": seo.get("youtube_tags", ["what if", "ted ed", "science animation", "neuroscience", "4k animation"]),
    }


# ==============================================================================
# SUBAGENT 7 & 8: MICRO-BATCH STORYBOARD SWARM + DETERMINISTIC SAFETY NET
# ==============================================================================
def run_storyboard_swarm(project_dir: str, script_data: dict, use_llm_swarm: bool = True) -> dict:
    beats_path = os.path.join(project_dir, "timeline", "beats.json")
    beats = json.load(open(beats_path, encoding="utf-8"))
    total_dur = round(float(beats[-1]["end"]), 3)

    # Write scenes/cast.js
    cast_dir = os.path.join(project_dir, "scenes")
    os.makedirs(cast_dir, exist_ok=True)
    cast = script_data.get("cast") or {
        "HERO": {"top": "hoodie", "color": "#d64a33", "head": "none"},
        "FRIEND": {"top": "tshirt", "color": "#3a6ea5", "head": "cap", "headColor": "#f2c21a"},
        "SCIENTIST": {"top": "labcoat", "face": "glasses", "head": "none"},
    }
    cast_js = f"window.PROJECT_CAST = {json.dumps(cast, indent=2)};\n"
    for k, v in cast.items():
        cast_js += f"export const {k} = {json.dumps(v)};\n"
    cast_js += f"export const CAST = [{', '.join(cast.keys())}];\n"
    with open(os.path.join(cast_dir, "cast.js"), "w", encoding="utf-8") as f:
        f.write(cast_js)

    sets_cycle = ["cafe", "lab", "street", "bedroom", "classroom", "rooftop", "hospital", "park"]
    llm_shots_map = {}

    if use_llm_swarm:
        batch_size = 8
        batches = [beats[i:i + batch_size] for i in range(0, len(beats), batch_size)]

        micro_sys = (
            "You are a Storyboard Micro-Subagent. For each beat `i`, assign one `template` from: "
            "`establishing_wide, medium_two_shot, over_the_shoulder, big_face_reaction, time_freeze, "
            "blueprint_pipeline, blueprint_compare, data_card_counter, timeline_progression, orbit_3d, title_card, end_screen` "
            "and one `set` from `cafe, lab, street, bedroom, classroom, rooftop, hospital, park`. "
            "Never repeat the same template twice in a row. "
            "Return STRICT JSON: {\"shots\": [{\"i\": 0, \"template\": \"...\", \"set\": \"...\", \"scene\": \"short visual description\"}]}"
        )

        def _process_batch(b_idx: int, chunk: list[dict]):
            compact_chunk = [{"i": c["i"], "text": c["text"][:90]} for c in chunk]
            try:
                raw = call_llm(
                    micro_sys,
                    json.dumps(compact_chunk),
                    expect_json=True,
                    temperature=0.4,
                    task_tier="structured_json",
                    subagent_name=f"Subagent7_StoryboardBatch_{b_idx + 1}",
                    max_tokens=700,
                )
                return extract_json(raw).get("shots", [])
            except Exception as e:
                print(f"  [Swarm:StoryboardBatch_{b_idx + 1}] Using Subagent 8 Deterministic Safety Net ({e})")
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(_process_batch, b_idx, chunk) for b_idx, chunk in enumerate(batches)]
            for fut in concurrent.futures.as_completed(futures):
                for item in fut.result():
                    if "i" in item:
                        llm_shots_map[int(item["i"])] = item
        SWARM_TELEMETRY["estimated_tokens_saved"] += 4500

    shots = []
    valid_templates = (
        "establishing_wide", "medium_two_shot", "over_the_shoulder", "big_face_reaction",
        "time_freeze", "blueprint_pipeline", "blueprint_compare", "data_card_counter",
        "timeline_progression", "orbit_3d", "title_card", "end_screen"
    )
    for idx, b in enumerate(beats):
        sid = f"s{idx + 1:03d}"
        start = round(float(b["start"]), 3)
        end = round(float(b["end"]), 3)
        line = b["text"]
        base_spec = _heuristic_shot_spec(idx, len(beats), line, script_data.get("title", ""), sets_cycle)
        sw_spec = llm_shots_map.get(idx, {})
        tpl = sw_spec.get("template") if sw_spec.get("template") in valid_templates else base_spec["template"]
        if idx == len(beats) - 1:
            tpl = "end_screen"
        set_name = sw_spec.get("set") if sw_spec.get("set") in sets_cycle else base_spec["set"]

        shots.append({
            "id": sid,
            "start": start,
            "end": end,
            "line": line,
            "template": tpl,
            "set": set_name,
            "scene": sw_spec.get("scene") or base_spec["scene"],
            "bars": "scope" if tpl in ("title_card", "time_freeze", "big_face_reaction") else "wide",
            "in": base_spec.get("in", {"type": "cut"}),
            "sfx": base_spec.get("sfx", []),
            "amb": base_spec.get("amb", {"name": "roomtone", "gain": -24}),
            "params": base_spec.get("params", {}),
            "captions": False if tpl in ("title_card", "end_screen") else None,
        })

    music_plan = [
        {"start": 0.0, "end": round(total_dur * 0.16, 2), "mood": "mystery", "intensity": 0.45},
        {"start": round(total_dur * 0.16, 2), "end": round(total_dur * 0.45, 2), "mood": "wonder", "intensity": 0.55},
        {"start": round(total_dur * 0.45, 2), "end": round(total_dur * 0.72, 2), "mood": "tension", "intensity": 0.68},
        {"start": round(total_dur * 0.72, 2), "end": round(total_dur * 0.88, 2), "mood": "action", "intensity": 0.82},
        {"start": round(total_dur * 0.88, 2), "end": total_dur, "mood": "hopeful", "intensity": 0.60},
    ]
    punchline_drops = []
    if len(shots) >= 4:
        climax_shot = shots[int(len(shots) * 0.78)]
        punchline_drops = [{"start": round(climax_shot["start"], 2), "end": round(min(climax_shot["end"], climax_shot["start"] + 1.25), 2)}]

    story_dir = os.path.join(project_dir, "story")
    os.makedirs(story_dir, exist_ok=True)
    shots_payload = {
        "title": script_data.get("title", "What If?"),
        "duration": total_dur,
        "shots": shots,
        "music": music_plan,
        "punchline_drops": punchline_drops,
        "swarm_telemetry": SWARM_TELEMETRY,
    }
    with open(os.path.join(story_dir, "shots.json"), "w", encoding="utf-8") as f:
        json.dump(shots_payload, f, indent=2)

    bible_md = (
        f"# Production Bible — {script_data.get('title')}\n\n"
        f"- **Style:** `{script_data.get('style', 'ted_ifverse')}`\n"
        f"- **Duration:** `{total_dur:.1f}s` ({len(shots)} contiguous shots)\n"
        f"- **Swarm Telemetry:** `{SWARM_TELEMETRY['total_calls']}` micro-calls | `{SWARM_TELEMETRY['failovers_triggered']}` auto-failovers | `~{SWARM_TELEMETRY['estimated_tokens_saved']}` tokens saved\n"
    )
    with open(os.path.join(story_dir, "bible.md"), "w", encoding="utf-8") as f:
        f.write(bible_md)

    return shots_payload
