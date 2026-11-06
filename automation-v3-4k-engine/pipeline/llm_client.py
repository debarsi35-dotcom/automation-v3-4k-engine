"""pipeline/llm_client.py — Immortal 7-Provider, 22-Model Free-Tier Failover Mesh & Subagent Router.

Designed for 100% uninterrupted execution even when individual API keys hit 429 Quota Exceeded,
RPM/TPM rate limits, 402 Credit Exhausted, or 503 Server Overload.

SUPPORTED FREE PROVIDERS (Automatic Instant Failover + Multi-Key Rotation):
  1. Groq Cloud Free Tier (`GROQ_API_KEY` — supports comma-separated multiple keys)
     Models: `llama-3.3-70b-versatile`, `deepseek-r1-distill-llama-70b`, `qwen-qwq-32b`, `llama-3.1-8b-instant`
  2. Cerebras Free Inference Tier (`CEREBRAS_API_KEY` — 1,000,000 free tokens/day, comma-separated keys)
     Models: `llama-3.3-70b`, `qwen-3-32b`, `llama3.1-8b`
  3. GitHub Models Free Tier (`GITHUB_MODELS_TOKEN` or built-in `GITHUB_TOKEN` in GitHub Actions)
     Models: `gpt-4o-mini`, `Llama-3.3-70B-Instruct`, `DeepSeek-R1`, `gpt-4o`
  4. Mistral La Plateforme Free Tier (`MISTRAL_API_KEY` — comma-separated keys)
     Models: `mistral-small-latest`, `open-mixtral-8x22b`, `codestral-latest`
  5. OpenRouter Free Model Pool (`OPENROUTER_API_KEY` — comma-separated keys, 7 distinct `:free` models)
     Models: `z-ai/glm-5.3-flash:free`, `deepseek/deepseek-r1:free`, `deepseek/deepseek-chat-v3-0324:free`,
             `qwen/qwen3-235b-a22b:free`, `meta-llama/llama-3.3-70b-instruct:free`,
             `mistralai/mistral-small-3.1-24b-instruct:free`, `google/gemini-2.0-flash-exp:free`
  6. Google Gemini Multi-Model Cascade (`GEMINI_API_KEY` — comma-separated keys, 5 separate quota buckets)
     Models: `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-1.5-flash`
  7. Pollinations.ai Zero-Key Anonymous Fallback (No API key or signup required!)
     Models: `openai`, `mistral`, `deepseek-reasoning`

SUBAGENT TASK TIERS (Routes each micro-subagent to the most token-efficient model pool first, then fails over across all others):
  - `fast_light`: Lightweight classification, polishing, SEO tags, and JSON formatting (uses 8B/mini/lite models first to save heavy quotas).
  - `reasoning_heavy`: Viral paradox scoring, scientific rule design, and 6-act structural architecture.
  - `creative_writer`: High-retention TED-Ed × Ifverse spoken prose generation (200-350 word micro-chunks).
  - `structured_json`: Micro-batch storyboard shot compilation (8 beats per micro-agent).
"""
import json, os, re, time, threading, urllib.request, urllib.error

_LOCK = threading.Lock()
# Tracks cooldown expiration timestamp per (provider, key_suffix, model) when a 429/quota error occurs
_COOLDOWN_UNTIL: dict[tuple[str, str, str], float] = {}
# Telemetry counter for Swarm report
SWARM_TELEMETRY = {
    "total_calls": 0,
    "failovers_triggered": 0,
    "calls_by_provider": {},
    "calls_by_subagent": {},
    "estimated_tokens_saved": 0,
}


def _split_keys(env_var: str) -> list[str]:
    """Support comma-separated multiple API keys in a single secret (e.g. KEY1,KEY2,KEY3)."""
    raw = os.environ.get(env_var, "").strip()
    if not raw:
        return []
    cleaned = []
    for k in raw.split(","):
        item = k.strip().strip('"').strip("'").strip()
        if item:
            cleaned.append(item)
    return cleaned


def build_candidate_pool(task_tier: str = "general") -> list[dict]:
    """Build ordered list of (provider, api_key, model, endpoint) candidates tailored to the subagent's task_tier."""
    pool = []

    # 1. Groq Free Tier
    for k in _split_keys("GROQ_API_KEY"):
        models = (
            ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
            if task_tier == "fast_light"
            else ["deepseek-r1-distill-llama-70b", "qwen-qwq-32b", "llama-3.3-70b-versatile"]
            if task_tier == "reasoning_heavy"
            else ["llama-3.3-70b-versatile", "qwen-qwq-32b", "llama-3.1-8b-instant"]
        )
        for m in models:
            pool.append({"provider": "groq", "key": k, "model": m, "url": "https://api.groq.com/openai/v1/chat/completions"})

    # 2. Cerebras Free Tier
    for k in _split_keys("CEREBRAS_API_KEY"):
        models = ["llama3.1-8b", "llama-3.3-70b"] if task_tier == "fast_light" else ["llama-3.3-70b", "qwen-3-32b", "llama3.1-8b"]
        for m in models:
            pool.append({"provider": "cerebras", "key": k, "model": m, "url": "https://api.cerebras.ai/v1/chat/completions"})

    # 3. GitHub Models Free Tier (uses GITHUB_MODELS_TOKEN or built-in GITHUB_TOKEN)
    gh_keys = _split_keys("GITHUB_MODELS_TOKEN") or _split_keys("GITHUB_TOKEN")
    for k in gh_keys:
        models = (
            ["gpt-4o-mini", "Llama-3.3-70B-Instruct"]
            if task_tier in ("fast_light", "structured_json")
            else ["gpt-4o", "DeepSeek-R1", "Llama-3.3-70B-Instruct", "gpt-4o-mini"]
        )
        for m in models:
            pool.append({"provider": "github_models", "key": k, "model": m, "url": "https://models.inference.ai.azure.com/chat/completions"})

    # 4. Mistral La Plateforme Free Tier
    for k in _split_keys("MISTRAL_API_KEY"):
        for m in ["mistral-small-latest", "open-mixtral-8x22b"]:
            pool.append({"provider": "mistral", "key": k, "model": m, "url": "https://api.mistral.ai/v1/chat/completions"})

    # 5. OpenRouter Free Model Roster (20+ free models; we rotate top 7)
    for k in _split_keys("OPENROUTER_API_KEY"):
        or_models = (
            [
                "mistralai/mistral-small-3.1-24b-instruct:free",
                "z-ai/glm-5.3-flash:free",
                "meta-llama/llama-3.3-70b-instruct:free",
            ]
            if task_tier in ("fast_light", "structured_json")
            else [
                "z-ai/glm-5.3-flash:free",
                "deepseek/deepseek-chat-v3-0324:free",
                "deepseek/deepseek-r1:free",
                "qwen/qwen3-235b-a22b:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemini-2.0-flash-exp:free",
            ]
        )
        for m in or_models:
            pool.append({"provider": "openrouter", "key": k, "model": m, "url": "https://openrouter.ai/api/v1/chat/completions"})

    # 6. Google Gemini Multi-Model Cascade (each model has its own separate RPM/RPD quota bucket!)
    for k in _split_keys("GEMINI_API_KEY"):
        gem_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
        for m in gem_models:
            pool.append({"provider": "gemini", "key": k, "model": m, "url": "gemini_native"})

    # 7. Pollinations.ai Zero-Key Anonymous Fallback (Always available even with 0 keys configured!)
    if os.environ.get("DISABLE_POLLINATIONS_FALLBACK", "").lower() not in ("1", "true"):
        for m in ["openai", "mistral"]:
            pool.append({"provider": "pollinations_free", "key": "anonymous", "model": m, "url": "https://text.pollinations.ai/openai"})

    return pool


def call_llm(
    system_prompt: str,
    user_prompt: str,
    expect_json: bool = False,
    temperature: float = 0.7,
    task_tier: str = "general",
    subagent_name: str = "Subagent",
    max_tokens: int = 2048,
) -> str:
    """Execute a subagent LLM call across the failover mesh. Instantly hops to the next model/provider on any quota/rate error."""
    candidates = build_candidate_pool(task_tier=task_tier)
    if not candidates:
        raise RuntimeError("No LLM candidates available in pool.")

    now = time.time()
    # Sort candidates so non-cooled-down endpoints are tried first, and load-balance across subagents
    with _LOCK:
        offset = SWARM_TELEMETRY["total_calls"] % max(1, min(3, len(candidates)))
    rotated = candidates[offset:] + candidates[:offset]
    active = [c for c in rotated if _COOLDOWN_UNTIL.get((c["provider"], c["key"][-4:], c["model"]), 0) <= now]
    cooled = [c for c in rotated if _COOLDOWN_UNTIL.get((c["provider"], c["key"][-4:], c["model"]), 0) > now]
    ordered = active + cooled

    errors = []
    for idx, cand in enumerate(ordered):
        prov = cand["provider"]
        model = cand["model"]
        key_id = cand["key"][-4:]
        try:
            if prov == "gemini":
                out = _call_gemini(cand["key"], model, system_prompt, user_prompt, expect_json, temperature, max_tokens)
            elif prov == "pollinations_free":
                out = _call_pollinations(model, system_prompt, user_prompt, expect_json, temperature)
            else:
                out = _call_openai_compatible(
                    cand["url"], cand["key"], model, system_prompt, user_prompt, expect_json, temperature, max_tokens
                )
            if not out or not out.strip():
                raise ValueError("Empty response body")
            if expect_json:
                # Validate that JSON can actually be extracted before accepting the response!
                extract_json(out)

            with _LOCK:
                SWARM_TELEMETRY["total_calls"] += 1
                SWARM_TELEMETRY["calls_by_provider"][f"{prov}:{model}"] = (
                    SWARM_TELEMETRY["calls_by_provider"].get(f"{prov}:{model}", 0) + 1
                )
                SWARM_TELEMETRY["calls_by_subagent"][subagent_name] = f"{prov}/{model}"
            print(f"  [Swarm:{subagent_name}] OK via {prov} ({model})")
            return out

        except Exception as e:
            err_str = str(e)
            is_quota = any(code in err_str.lower() for code in ["429", "quota", "rate", "exhausted", "402", "limit", "overloaded", "503"])
            cooldown_sec = 180.0 if is_quota else 45.0
            with _LOCK:
                _COOLDOWN_UNTIL[(prov, key_id, model)] = time.time() + cooldown_sec
                SWARM_TELEMETRY["failovers_triggered"] += 1
            reason = "QUOTA/RATE LIMIT" if is_quota else "ERROR"
            print(f"  [Swarm:{subagent_name}] {reason} on {prov}/{model} ({err_str[:80]}) -> Instantly failing over to next AI...")
            errors.append(f"{prov}/{model}: {err_str[:90]}")

    raise RuntimeError(f"All {len(ordered)} AI models in Failover Mesh failed for {subagent_name}. Details: {' | '.join(errors[:6])}")


def _call_gemini(api_key: str, model: str, system_prompt: str, user_prompt: str, expect_json: bool, temperature: float, max_tokens: int) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    gen_cfg = {"temperature": temperature, "maxOutputTokens": max(max_tokens, 2048)}
    if expect_json:
        gen_cfg["responseMimeType"] = "application/json"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": gen_cfg,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=75) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_compatible(
    url: str, api_key: str, model: str, system_prompt: str, user_prompt: str, expect_json: bool, temperature: float, max_tokens: int
) -> str:
    sys_msg = system_prompt + ("\nReturn ONLY valid JSON." if expect_json and "json" not in system_prompt.lower() else "")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if expect_json and "azure.com" not in url and "cerebras" not in url:
        payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Automation-V2-Swarm/2.1",
            "HTTP-Referer": "https://github.com/automation-v2-ifverse-teded",
            "X-Title": "Automation-V2-Swarm",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=75) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def _call_pollinations(model: str, system_prompt: str, user_prompt: str, expect_json: bool, temperature: float) -> str:
    sys_msg = system_prompt + ("\nRespond strictly with a valid JSON object only." if expect_json else "")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "private": True,
    }
    req = urllib.request.Request(
        "https://text.pollinations.ai/openai",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Automation-V2-Swarm/2.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=75) as resp:
        raw_body = resp.read().decode("utf-8")
    try:
        data = json.loads(raw_body)
        if isinstance(data, dict) and "choices" in data:
            return data["choices"][0]["message"]["content"]
    except Exception:
        pass
    return raw_body


def extract_json(text: str):
    """Safely parse JSON from LLM output even if wrapped in markdown fences or <think> reasoning tags."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        brace = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
        if brace:
            cleaned = brace.group(1)
    return json.loads(cleaned)
