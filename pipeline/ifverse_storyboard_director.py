"""pipeline/ifverse_storyboard_director.py — Heuristic & Deterministic Shot Director."""
import re

def _heuristic_shot_spec(idx: int, total: int, line: str, title: str, sets_cycle: list[str]) -> dict:
    low = line.lower()
    set_name = sets_cycle[(idx // 3) % len(sets_cycle)]
    amb_map = {"cafe": {"name": "murmur", "gain": -25}, "lab": {"name": "roomtone", "gain": -24}, "street": {"name": "city", "gain": -24}, "bedroom": {"name": "rain", "gain": -24}, "classroom": {"name": "roomtone", "gain": -25}, "rooftop": {"name": "wind", "gain": -23}, "hospital": {"name": "hum", "gain": -25}, "park": {"name": "wind", "gain": -25}}
    amb = amb_map.get(set_name, {"name": "roomtone", "gain": -24})
    if idx == total - 1:
        return {"template": "end_screen", "set": "rooftop", "scene": "End screen", "bars": "wide", "in": {"type": "fade", "dur": 0.5}, "sfx": [{"at": 0.1, "name": "shimmer", "gain": -8}], "amb": amb, "params": {"question": "What would YOU do? Tell us below."}}
    if idx == 2 or ("what if" in low and idx <= 5):
        return {"template": "title_card", "set": "rooftop", "scene": f"Title Card: {title}", "bars": "scope", "in": {"type": "fade", "dur": 0.5}, "sfx": [{"at": 0.05, "name": "stinger", "gain": -6}], "amb": amb, "params": {"mood": "dusk"}}
    if any(k in low for k in ["freeze", "frozen", "slow motion", "stopped", "hundredth", "instant", "millisecond"]):
        return {"template": "time_freeze", "set": set_name, "scene": f"Time-freeze: {line[:48]}", "bars": "scope", "in": {"type": "flash", "dur": 0.35}, "sfx": [{"at": 0.0, "name": "freeze", "gain": -6}], "amb": amb, "params": {"actor": "HERO", "pose": "ready", "expr": "awe", "badge": "TIME FROZEN"}}
    if any(k in low for k in ["normal", "average", "most people", "compared to", "versus", "times faster", "times more"]):
        return {"template": "blueprint_compare", "set": "lab", "scene": f"Blueprint compare: {line[:48]}", "bars": "wide", "in": {"type": "dip", "dur": 0.4}, "sfx": [{"at": 0.2, "name": "counter", "gain": -12}, {"at": 0.6, "name": "ding", "gain": -9}], "amb": {"name": "hum", "gain": -26}, "params": {"row1": {"label": "HUMAN BASELINE", "value": "1.0x", "frac": 0.28}, "row2": {"label": "YOUR THRESHOLD", "value": "10.0x", "frac": 0.92}, "badge": "10x SHIFT"}}
    if any(k in low for k in ["brain", "cortex", "neuron", "cell", "microb", "bacteria", "blood", "hormone", "dopamine", "signal", "oxygen", "system", "dna", "gene", "organ"]):
        return {"template": "blueprint_pipeline", "set": "lab", "scene": f"Blueprint pipeline: {line[:48]}", "bars": "wide", "in": {"type": "zoom", "dur": 0.45}, "sfx": [{"at": 0.1, "name": "pop", "gain": -10}, {"at": 0.5, "name": "blip", "gain": -10}], "amb": {"name": "hum", "gain": -26}, "params": {"nodes": [{"icon": "eye", "label": "INPUT SIGNAL"}, {"icon": "brain", "label": "NEURAL FILTER"}, {"icon": "lightning", "label": "SYSTEM OUTPUT"}], "readoutLabel": "PATHWAY:", "readoutValue": "ACTIVE"}}
    nums = re.findall(r"\b\d+(?:\.\d+)?\b", line)
    if nums or any(k in low for k in ["study", "research", "percent", "million", "billion", "seconds", "hours", "days", "years"]):
        target_val = float(nums[0]) if nums else 100.0
        return {"template": "data_card_counter", "set": set_name, "scene": f"Data card: {line[:48]}", "bars": "wide", "in": {"type": "whip", "dur": 0.35}, "sfx": [{"at": 0.1, "name": "swish", "gain": -10}, {"at": 0.35, "name": "counter", "gain": -12}], "amb": amb, "params": {"title": "EMPIRICAL BENCHMARK", "subtitle": "MEASURED RESPONSE", "from": 0, "to": target_val if target_val > 0 else 100, "decimals": 1 if "." in (nums[0] if nums else "") else 0, "unit": "x" if "times" in low else "%" if "percent" in low else ""}}
    cycle = ["establishing_wide", "big_face_reaction", "medium_two_shot", "over_the_shoulder", "timeline_progression"]
    tpl = cycle[idx % len(cycle)]
    return {"template": tpl, "set": set_name, "scene": f"{tpl} in {set_name}: {line[:48]}", "bars": "scope" if tpl == "big_face_reaction" else "wide", "in": {"type": "cut"}, "sfx": [{"at": 0.15, "name": "whoosh", "gain": -12}], "amb": amb, "params": {"actor": "HERO", "walk": idx % 2 == 0, "expr": "determined"}}
