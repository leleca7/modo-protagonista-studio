from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

def _font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()

def make_thumbnail(text: str, out_path: Path, background: Path | None = None) -> Path:
    W, H = 1280, 720
    img = None
    if background and background.exists() and background.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        try:
            img = Image.open(background).convert("RGB")
            scale = max(W / img.width, H / img.height)
            img = img.resize((int(img.width * scale), int(img.height * scale)))
            left = (img.width - W) // 2
            top = (img.height - H) // 2
            img = img.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(1.2))
        except Exception:
            img = None
    if img is None:
        img = Image.new("RGB", (W, H), "#1A1420")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((58, 52, 1222, 668), radius=42, fill=(255, 248, 240, 218))
    draw.ellipse((960, 70, 1175, 285), fill=(214, 255, 82, 230))
    draw.text((92, 92), "MODO PROTAGONISTA", fill="#19151E", font=_font(34, True))
    wrapped = textwrap.fill((text or "MODO PROTAGONISTA").upper(), width=18)
    draw.multiline_text((92, 215), wrapped, fill="#E63F93", font=_font(84, True), spacing=4)
    draw.text((92, 600), "afirmações • relaxamento • visualização", fill="#19151E", font=_font(25, False))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, quality=94)
    return out_path
