"""Render images/icon.png: a plum stockpot with syntax-colored steam on ink.

Drawn at 4x with Pillow and downsampled for anti-aliasing.

    python3 scripts/make_icon.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE, SS = 256, 4
OUT = Path(__file__).resolve().parent.parent / "images" / "icon.png"

BG_TOP, BG_BOTTOM = (36, 30, 34), (20, 17, 17)
PLUM, PLUM_DARK, PLUM_LIGHT = (88, 75, 109), (62, 51, 80), (112, 98, 136)
PEACH, PEACH_SHADE = (233, 202, 174), (203, 170, 142)
AUBERGINE = (54, 38, 49)
SAGE = (122, 154, 122)
STEAM = [((184, 154, 200), 90, 0.0), ((159, 180, 138), 128, 0.7), ((141, 177, 204), 166, 1.4)]  # orchid, sage, blue


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

# Soft ground shadow
sh = Image.new("L", img.size, 0)
ImageDraw.Draw(sh).ellipse([s(54), s(206), s(202), s(226)], fill=140)
sh = sh.filter(ImageFilter.GaussianBlur(s(5)))
img.paste(Image.new("RGBA", img.size, (0, 0, 0, 255)), mask=sh)
d = ImageDraw.Draw(img)

# Steam wisps rising from the pot
for col, cx, phase in STEAM:
    pts = []
    for i in range(41):
        t = i / 40
        y = 96 - 66 * t
        x = cx + 7 * math.sin(t * 2 * math.pi * 1.1 + phase * 2)
        pts.append((s(x), s(y)))
    d.line(pts, fill=col, width=s(7), joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - s(3.5), p[1] - s(3.5), p[0] + s(3.5), p[1] + s(3.5)], fill=col)

# Handles
for x0, x1 in ((40, 62), (194, 216)):
    d.rounded_rectangle([s(x0), s(124), s(x1), s(146)], radius=s(10), fill=PEACH_SHADE)
    d.rounded_rectangle([s(x0 + 5), s(129), s(x1 - 5), s(141)], radius=s(6), fill=BG_BOTTOM)

# Pot body: straight sides, rounded bottom
d.rounded_rectangle([s(54), s(104), s(202), s(208)], radius=s(34), fill=PLUM_DARK)
d.rectangle([s(54), s(104), s(202), s(150)], fill=PLUM_DARK)
lit = Image.new("L", img.size, 0)
ImageDraw.Draw(lit).ellipse([s(40), s(100), s(150), s(230)], fill=255)
lit = lit.filter(ImageFilter.GaussianBlur(s(18)))
body_mask = Image.new("L", img.size, 0)
bm = ImageDraw.Draw(body_mask)
bm.rounded_rectangle([s(54), s(104), s(202), s(208)], radius=s(34), fill=255)
bm.rectangle([s(54), s(104), s(202), s(150)], fill=255)
img.paste(Image.new("RGBA", img.size, PLUM + (255,)), mask=Image.composite(lit, Image.new("L", img.size, 0), body_mask))
d = ImageDraw.Draw(img)

# Rim: peach ellipse with an aubergine opening
d.ellipse([s(50), s(92), s(206), s(120)], fill=PEACH)
d.ellipse([s(58), s(96), s(198), s(116)], fill=AUBERGINE)
d.arc([s(50), s(92), s(206), s(120)], 20, 160, fill=PEACH_SHADE, width=s(2))

# Sage sprig on the front, like the snowflake on the mug
cx, cy = 128, 164
d.line([(s(cx), s(cy + 22)), (s(cx), s(cy - 20))], fill=SAGE, width=s(4))
for side in (-1, 1):
    for dy, ln in ((-8, 20), (6, 24)):
        x1, y1 = cx + side * ln, cy + dy - 12
        pts = [(s(cx), s(cy + dy)), (s(cx + side * ln * 0.55), s(cy + dy - 14)), (s(x1), s(y1)),
               (s(cx + side * ln * 0.45), s(cy + dy + 1))]
        d.polygon(pts, fill=SAGE)
d.ellipse([s(cx - 6), s(cy - 30), s(cx + 6), s(cy - 14)], fill=SAGE)

mask = Image.new("L", img.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, s(SIZE) - 1, s(SIZE) - 1], radius=s(48), fill=255)
img.putalpha(mask)
OUT.parent.mkdir(exist_ok=True)
img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
print(OUT)
