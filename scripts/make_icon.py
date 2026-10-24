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
CARROT, RADISH, ONION = (214, 150, 104), (196, 138, 168), (184, 154, 200)  # terracotta-gold, pink, orchid


def s(v):
    return round(v * SS)


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


def shape(points, fill):
    d.polygon([(s(x), s(y)) for x, y in points], fill=fill)


def curve(cx, top, bottom, half_width, profile):
    """Mirror-symmetric body from `top` to `bottom`; profile(t) in 0..1 gives width."""
    left, right = [], []
    for i in range(41):
        t = i / 40
        w = half_width * profile(t)
        y = top + (bottom - top) * t
        left.append((cx - w, y))
        right.append((cx + w, y))
    return left + right[::-1]


def shade(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color)


# Carrot: wide shoulders tapering to a tip
cx, base = 62, 170
for angle, length, width in ((-40, 40, 8), (40, 40, 8), (0, 52, 9)):
    leaf(cx, base, angle, length, width, LEAF)
shape(curve(cx, base - 4, base + 38, 15, lambda t: (1 - t) ** 0.85), CARROT)
for y in (base + 10, base + 22):
    d.line([(s(cx - 8 + (y - base) * 0.12), s(y)), (s(cx - 2), s(y))], fill=shade(CARROT, -45), width=s(2))

# Radish: plump oval
cx, base = 128, 160
for angle, length, width in ((-48, 40, 8), (48, 40, 8), (-16, 50, 9), (16, 50, 9)):
    leaf(cx, base, angle, length, width, LEAF)
shape(curve(cx, base - 4, base + 40, 15, lambda t: math.sin(math.pi * min(1, t * 0.9 + 0.1)) ** 0.7 if t < 0.95 else 0.1), RADISH)
d.ellipse([s(cx - 8), s(base + 2), s(cx - 2), s(base + 10)], fill=shade(RADISH, 40))

# Onion: bulb with a pointed neck
cx, base = 194, 170
for angle, length, width in ((-20, 56, 6), (20, 56, 6)):
    leaf(cx, base - 12, angle, length, width, LEAF)
shape(curve(cx, base - 14, base + 40, 19, lambda t: (math.sin(math.pi * t * 0.92) ** 0.9) * (0.25 + 0.75 * min(1, t * 3)) ** 1.0), ONION)
for dx in (-8, 0, 8):
    d.line([(s(cx + dx * 0.4), s(base - 6)), (s(cx + dx), s(base + 30))], fill=shade(ONION, -35), width=s(1.5))

# Soil lip in front of each vegetable so it reads as growing out of the bed
for cx, base in ((62, 170), (128, 160), (194, 170)):
    d.ellipse([s(cx - 30), s(base + 22), s(cx + 30), s(base + 44)], fill=SOIL)
    d.arc([s(cx - 30), s(base + 22), s(cx + 30), s(base + 44)], 205, 335, fill=SOIL_LIGHT, width=s(2))

mask = Image.new("L", img.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, s(SIZE) - 1, s(SIZE) - 1], radius=s(48), fill=255)
img.putalpha(mask)
OUT.parent.mkdir(exist_ok=True)
img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
print(OUT)
