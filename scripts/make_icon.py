"""Render images/icon.png: a night vegetable garden, three plants in a soil bed under a moon.

Drawn at 4x with Pillow and downsampled for anti-aliasing.

    python3 scripts/make_icon.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

SIZE, SS = 256, 4
OUT = Path(__file__).resolve().parent.parent / "images" / "icon.png"

BG_TOP, BG_BOTTOM = (36, 30, 34), (22, 19, 20)
PEACH = (233, 202, 174)
SOIL, SOIL_LIGHT = (54, 38, 49), (88, 75, 109)
LEAF = (122, 154, 122)
VEG = [(184, 154, 200), (196, 138, 168), (214, 174, 120)]  # orchid, pink, gold


def s(v):
    return v * SS


img = Image.new("RGBA", (s(SIZE), s(SIZE)))
px = img.load()
for y in range(s(SIZE)):
    t = y / (s(SIZE) - 1)
    row = tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)) + (255,)
    for x in range(s(SIZE)):
        px[x, y] = row
d = ImageDraw.Draw(img)

# Moon (crescent: peach disc with a sky-colored disc cut out)
d.ellipse([s(176), s(30), s(214), s(68)], fill=PEACH)
d.ellipse([s(188), s(24), s(226), s(62)], fill=(BG_TOP[0] + 1, BG_TOP[1] + 1, BG_TOP[2] + 1))
for x, y in ((46, 40), (86, 24), (128, 52), (150, 28)):
    d.ellipse([s(x - 2), s(y - 2), s(x + 2), s(y + 2)], fill=PEACH)

# Soil bed: a wide mound with two furrow lines
d.ellipse([s(-20), s(160), s(276), s(300)], fill=SOIL)
d.arc([s(-20), s(160), s(276), s(300)], 200, 340, fill=SOIL_LIGHT, width=s(3))
for y, inset in ((200, 48), (224, 20)):
    d.line([(s(inset), s(y)), (s(SIZE - inset), s(y))], fill=(44, 31, 40), width=s(5))

# Three plants: a vegetable top peeking out of the soil, with rounded leaves
def leaf(x, y, angle, length, width, fill):
    """A plump lens-shaped leaf from (x, y) pointing `angle` degrees from straight up."""
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)  # along the leaf
    px_, py_ = -uy, ux                  # across it
    top, bottom = [], []
    for i in range(25):
        t = i / 24
        w = width * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)
        cx_, cy_ = x + ux * length * t, y + uy * length * t
        top.append((s(cx_ + px_ * w), s(cy_ + py_ * w)))
        bottom.append((s(cx_ - px_ * w), s(cy_ - py_ * w)))
    d.polygon(top + bottom[::-1], fill=fill)


for cx, base, col in ((62, 196, VEG[0]), (128, 186, VEG[1]), (194, 196, VEG[2])):
    for angle, length, width in ((-52, 42, 9), (52, 42, 9), (-18, 50, 10), (18, 50, 10)):
        leaf(cx, base - 8, angle, length, width, LEAF)
    d.ellipse([s(cx - 15), s(base - 14), s(cx + 15), s(base + 16)], fill=col)
    d.ellipse([s(cx - 9), s(base - 9), s(cx - 2), s(base - 2)], fill=tuple(min(255, c + 40) for c in col))

mask = Image.new("L", img.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, s(SIZE) - 1, s(SIZE) - 1], radius=s(48), fill=255)
img.putalpha(mask)
OUT.parent.mkdir(exist_ok=True)
img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
print(OUT)
