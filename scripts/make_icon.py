"""Render images/icon.png: the 47-arm Lucas seed spiral in the theme's colors on ink.

Drawn at 4x with Pillow and downsampled for anti-aliasing.

    python3 scripts/make_icon.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

SIZE, SS = 256, 4
OUT = Path(__file__).resolve().parent.parent / "images" / "icon.png"

INK, AUBERGINE = (27, 24, 24), (54, 38, 49)
# Seed colors from the center out: plum -> orchid -> pink -> terracotta -> peach
RAMP = [(88, 75, 109), (184, 154, 200), (196, 138, 168), (201, 143, 122), (233, 202, 174)]
SEEDS, ANGLE = 260, math.radians(99.5)  # Lucas divergence angle: 47 spiral arms


def ramp(t):
    x = t * (len(RAMP) - 1)
    i = min(int(x), len(RAMP) - 2)
    f = x - i
    return tuple(round(a + (b - a) * f) for a, b in zip(RAMP[i], RAMP[i + 1]))


img = Image.new("RGBA", (SIZE * SS, SIZE * SS), INK + (255,))
d = ImageDraw.Draw(img)
c = SIZE * SS / 2
d.ellipse([c - 112 * SS, c - 112 * SS, c + 112 * SS, c + 112 * SS], fill=AUBERGINE)

scale = 100 * SS / math.sqrt(SEEDS)
for n in range(1, SEEDS + 1):
    r, a = scale * math.sqrt(n) * 1.0, n * ANGLE
    x, y = c + r * math.cos(a), c + r * math.sin(a)
    rad = (2.0 + 4.2 * n / SEEDS) * SS
    col = ramp(n / SEEDS)
    d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)

mask = Image.new("L", img.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE * SS - 1, SIZE * SS - 1], radius=48 * SS, fill=255)
img.putalpha(mask)
OUT.parent.mkdir(exist_ok=True)
img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
print(OUT)
