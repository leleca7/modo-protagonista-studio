from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

def windows_sapi_available() -> bool:
    return shutil.which("powershell") is not None or shutil.which("pwsh") is not None

def synthesize_windows_sapi(text: str, out_wav: Path, rate: int = -1) -> Path:
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        raise RuntimeError("PowerShell não encontrado. Este TTS gratuito é destinado ao Windows.")
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    text_path = out_wav.with_suffix(".tts.txt")
    ps_path = out_wav.with_suffix(".tts.ps1")
    text_path.write_text(text, encoding="utf-8")
    safe_text_path = str(text_path.resolve()).replace("'", "''")
    safe_out_path = str(out_wav.resolve()).replace("'", "''")
    ps_path.write_text(f"""
Add-Type -AssemblyName System.Speech
$text = Get-Content -Raw -Encoding UTF8 '{safe_text_path}'
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = {int(rate)}
$synth.SetOutputToWaveFile('{safe_out_path}')
$synth.Speak($text)
$synth.Dispose()
""", encoding="utf-8-sig")
    try:
        subprocess.run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)], check=True)
    finally:
        text_path.unlink(missing_ok=True)
        ps_path.unlink(missing_ok=True)
    return out_wav
