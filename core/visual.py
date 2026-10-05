from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import random

PALETTES = [
    ((23, 19, 31), (122, 47, 95), (246, 112, 176)),
    ((247, 241, 232), (240, 164, 193), (212, 255, 82)),
    ((15, 22, 35), (62, 75, 117), (217, 140, 184)),
    ((37, 28, 48), (108, 78, 121), (235, 196, 216)),
]

def make_procedural_background(theme: str, out_path: Path, width: int = 1920, height: int = 1080) -> Path:
    seed = int(hashlib.sha256(theme.encode("utf-8")).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    p = PALETTES[seed % len(PALETTES)]
    img = Image.new("RGB", (width, height), p[0])
    px = img.load()
    for y in range(height):
        t = y / max(1, height - 1)
        c = tuple(int(p[0][i] * (1 - t) + p[1][i] * t) for i in range(3))
        for x in range(width):
            px[x, y] = c
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(18):
        r = rnd.randint(70, 260)
        x = rnd.randint(-r, width)
        y = rnd.randint(-r, height)
        alpha = rnd.randint(12, 35)
        draw.ellipse((x, y, x + r, y + r), fill=(*p[2], alpha))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, quality=95)
    return out_path
