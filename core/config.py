from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"

DEFAULTS = {
    "ai_provider": "ollama",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "qwen3:4b",
    "ffmpeg_path": "ffmpeg",
    "default_voice_rate": -1,
    "voice_volume": 0.10,
    "ambient_volume": 0.62,
    "tone_volume": 0.035,
    "youtube_client_secret": "client_secret.json",
    "youtube_token": "token.json",
    "default_privacy": "private",
    "similarity_regenerate_threshold": 0.78,
}

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULTS, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    return {**DEFAULTS, **data}

def save_config(data: dict) -> None:
    CONFIG_PATH.write_text(json.dumps({**DEFAULTS, **data}, ensure_ascii=False, indent=2), encoding="utf-8")
