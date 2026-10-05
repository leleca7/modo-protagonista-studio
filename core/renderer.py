from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

def ffmpeg_available(ffmpeg_path: str = "ffmpeg") -> bool:
    return shutil.which(ffmpeg_path) is not None or Path(ffmpeg_path).exists()

def _duration_seconds(minutes: int) -> int:
    return max(10, int(minutes) * 60)

def render_video(
    out_path: Path,
    duration_minutes: int,
    ffmpeg_path: str = "ffmpeg",
    voice_wav: Path | None = None,
    ambient_file: Path | None = None,
    background_file: Path | None = None,
    frequency: int = 0,
    voice_volume: float = 0.10,
    ambient_volume: float = 0.62,
    tone_volume: float = 0.035,
    resolution: str = "1920x1080",
) -> Path:
    if not ffmpeg_available(ffmpeg_path):
        raise RuntimeError("FFmpeg não encontrado. Rode INSTALAR.bat ou configure o caminho em config.json.")
    if not voice_wav or not voice_wav.exists():
        raise RuntimeError("A voz ainda não foi gerada. Gere voice.wav antes do render final.")

    duration = _duration_seconds(duration_minutes)
    cmd = [ffmpeg_path, "-y"]

    if background_file and background_file.exists():
        ext = background_file.suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".webp"}:
            cmd += ["-loop", "1", "-framerate", "30", "-i", str(background_file)]
        else:
            cmd += ["-stream_loop", "-1", "-i", str(background_file)]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=0x17131f:s={resolution}:r=30:d={duration}"]

    audio_inputs = []
    input_idx = 1
    cmd += ["-stream_loop", "-1", "-i", str(voice_wav)]
    audio_inputs.append((input_idx, voice_volume))
    input_idx += 1

    if ambient_file and ambient_file.exists():
        cmd += ["-stream_loop", "-1", "-i", str(ambient_file)]
        audio_inputs.append((input_idx, ambient_volume))
        input_idx += 1
    if frequency and int(frequency) > 0:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={int(frequency)}:sample_rate=44100:duration={duration}"]
        audio_inputs.append((input_idx, tone_volume))

    filters = []
    labels = []
    if background_file and background_file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        filters.append("[0:v]scale=2000:-2,crop=1920:1080,zoompan=z='min(zoom+0.00003,1.03)':d=1:s=1920x1080:fps=30[vout]")
        video_map = "[vout]"
    elif background_file:
        filters.append("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30[vout]")
        video_map = "[vout]"
    else:
        video_map = "0:v:0"

    for n, (idx, vol) in enumerate(audio_inputs):
        label = f"a{n}"
        filters.append(f"[{idx}:a]aresample=44100,volume={vol}[{label}]")
        labels.append(f"[{label}]")
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]")

    cmd += ["-filter_complex", ";".join(filters), "-map", video_map, "-map", "[aout]"]
    cmd += [
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        str(out_path),
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)
    return out_path
