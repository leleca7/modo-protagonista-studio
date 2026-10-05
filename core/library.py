from __future__ import annotations
from pathlib import Path
from .config import ROOT

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"}

def ensure_asset_folders() -> None:
    for p in [ROOT / "assets" / "backgrounds", ROOT / "assets" / "ambient"]:
        p.mkdir(parents=True, exist_ok=True)

def backgrounds() -> list[Path]:
    ensure_asset_folders()
    return sorted([p for p in (ROOT / "assets" / "backgrounds").iterdir() if p.suffix.lower() in VIDEO_EXT | IMAGE_EXT])

def ambient_sounds() -> list[Path]:
    ensure_asset_folders()
    return sorted([p for p in (ROOT / "assets" / "ambient").iterdir() if p.suffix.lower() in AUDIO_EXT])
