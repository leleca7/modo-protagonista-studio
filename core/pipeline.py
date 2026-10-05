from __future__ import annotations
from pathlib import Path
import shutil
from .db import recent_projects, save_project, update_project
from .generator import generate_package, write_project_files
from .visual import make_procedural_background
from .thumbnail import make_thumbnail
from .tts_windows import synthesize_windows_sapi, windows_sapi_available
from .renderer import render_video, ffmpeg_available

def copy_uploaded(uploaded_file, out_dir: Path, basename: str) -> Path | None:
    if uploaded_file is None:
        return None
    ext = Path(uploaded_file.name).suffix.lower()
    out = out_dir / f"{basename}{ext}"
    out.write_bytes(uploaded_file.getbuffer())
    return out

def create_project(meta: dict, cfg: dict, background_upload=None, ambient_upload=None,
                   library_background: Path | None = None, library_ambient: Path | None = None) -> dict:
    history = recent_projects(20)
    package, similarity = generate_package(meta, history, cfg)
    out_dir = write_project_files(meta, package)

    bg = copy_uploaded(background_upload, out_dir, "background")
    amb = copy_uploaded(ambient_upload, out_dir, "ambient")

    if not bg and library_background and library_background.exists():
        bg = out_dir / ("background" + library_background.suffix.lower())
        shutil.copy2(library_background, bg)
    if not amb and library_ambient and library_ambient.exists():
        amb = out_dir / ("ambient" + library_ambient.suffix.lower())
        shutil.copy2(library_ambient, amb)
    if not bg:
        bg = make_procedural_background(meta["theme"], out_dir / "background.png")

    project_id = save_project(meta, package, str(out_dir), similarity_score=similarity["score"])
    return {
        "id": project_id,
        "meta": meta,
        "package": package,
        "out_dir": out_dir,
        "background": bg,
        "ambient": amb,
        "similarity": similarity,
    }

def generate_voice(project: dict, cfg: dict) -> Path:
    if not windows_sapi_available():
        raise RuntimeError("O TTS gratuito do Windows não está disponível neste sistema.")
    out = Path(project["out_dir"])
    voice = out / "voice.wav"
    text = ". ".join(project["package"].get("affirmations", []))
    synthesize_windows_sapi(text, voice, int(cfg.get("default_voice_rate", -1)))
    update_project(project["id"], status="voz_gerada")
    return voice

def generate_thumbnail(project: dict, chosen_text: str) -> Path:
    out = Path(project["out_dir"])
    bg = next(iter(out.glob("background.*")), None)
    thumb = make_thumbnail(chosen_text, out / "thumbnail.jpg", bg)
    update_project(project["id"], thumbnail_path=str(thumb), status="thumbnail_gerada")
    return thumb

def render_project(project: dict, cfg: dict) -> Path:
    if not ffmpeg_available(cfg.get("ffmpeg_path", "ffmpeg")):
        raise RuntimeError("FFmpeg não encontrado.")
    out = Path(project["out_dir"])
    voice = out / "voice.wav"
    bg = next(iter(out.glob("background.*")), None)
    amb = next(iter(out.glob("ambient.*")), None)
    video = render_video(
        out / "video_final.mp4",
        project["meta"]["duration_minutes"],
        cfg.get("ffmpeg_path", "ffmpeg"),
        voice,
        amb,
        bg,
        project["meta"].get("frequency", 0),
        float(cfg.get("voice_volume", 0.10)),
        float(cfg.get("ambient_volume", 0.62)),
        float(cfg.get("tone_volume", 0.035)),
    )
    update_project(project["id"], video_path=str(video), status="video_renderizado")
    return video
