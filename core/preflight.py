from __future__ import annotations
import shutil
import sys
from pathlib import Path
from .ai import ollama_available
from .tts_windows import windows_sapi_available

def system_preflight(cfg: dict, root: Path) -> dict:
    usage = shutil.disk_usage(root)
    free_gb = round(usage.free / (1024 ** 3), 1)
    ffmpeg_path = cfg.get("ffmpeg_path", "ffmpeg")
    ffmpeg_ok = shutil.which(ffmpeg_path) is not None or Path(ffmpeg_path).exists()
    return {
        "python_ok": sys.version_info >= (3, 10),
        "python": sys.version.split()[0],
        "ffmpeg_ok": ffmpeg_ok,
        "ollama_ok": ollama_available(cfg.get("ollama_url", "http://localhost:11434")),
        "tts_ok": windows_sapi_available(),
        "free_gb": free_gb,
        "disk_warning": free_gb < 15,
    }
