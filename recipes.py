import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

FALLBACK_MODELS = ["gemini-3.6-flash"]


def _load_env():
    p = Path(__file__).parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get_setting(name, default=None):
    value = os.environ.get(name)
    if value is not None:
        return value
    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default


def _call(model, key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-goog-api-key": key,
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode())
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def ask_gemini(prompt):
    _load_env()
    key = _get_setting("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Set it in .env locally or in Streamlit Cloud secrets."
        )
    primary = _get_setting("GEMINI_MODEL", "gemini-4-hydrogen")
    last_error = ""
    models = dict.fromkeys([primary] + FALLBACK_MODELS)
    for model in models:
        for attempt in range(3):
            try:
                return _call(model, key, prompt)
            except urllib.error.HTTPError as e:
                last_error = f"{model} -> error {e.code}: {e.read().decode()[:200]}"
                if e.code in (429, 500, 503):
                    time.sleep(3 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_error = f"{model} -> {e}"
                time.sleep(2)
    raise RuntimeError("Gemini failed. Last error: " + last_error)


def suggest_recipes(items, num=3, diet="Any"):
    from schemas import RecipeList
    lines = []
    for it in items:
        lines.append(f"- {it['name']} ({it['qty']}), {it['status']}, days left: {it['days_left']}")
    inventory = "\n".join(lines)
    prompt = (
        "You are a helpful home-cooking assistant for an Indian household. "
        f"Suggest {num} simple recipes using mainly the ingredients below. "
        "Use items with the fewest days left first. "
        f"Diet preference: {diet}. Assume basic pantry items (salt, oil, spices, water) are available. "
        "Put any other ingredient the user does not have in missing_ingredients.\n\n"
        f"Ingredients:\n{inventory}\n\n"
        'Return ONLY JSON in this shape: {"recipes": [{"title": "", "description": "", '
        '"time_minutes": 0, "ingredients_used": [""], "missing_ingredients": [""], "steps": [""]}]}'
    )
    raw = ask_gemini(prompt).strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[4:] if raw.lower().startswith("json") else raw
    return RecipeList.model_validate_json(raw.strip()).recipes
