"""Render images/icon.png: an eggplant with a sage calyx on aubergine ink.

Drawn at 4x with Pillow and downsampled for anti-aliasing.

    python3 scripts/make_icon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE, SS = 256, 4
OUT = Path(__file__).resolve().parent.parent / "images" / "icon.png"

BG_TOP, BG_BOTTOM = (38, 31, 36), (22, 19, 19)
BODY, BODY_SHADE, BODY_LIGHT = (88, 75, 109), (54, 38, 49), (132, 116, 158)
SAGE, SAGE_SHADE = (122, 154, 122), (82, 93, 83)
PEACH = (233, 202, 174)


def s(v):
    return int(v * SS)


def gradient(top, bottom):
    img = Image.new("RGB", (1, SIZE * SS))
    for y in range(SIZE * SS):
        t = y / (SIZE * SS - 1)
        img.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return img.resize((SIZE * SS, SIZE * SS))


canvas = gradient(BG_TOP, BG_BOTTOM).convert("RGBA")

# Eggplant body: a tilted teardrop made of a big ellipse and a narrower neck.
body = Image.new("L", canvas.size, 0)
d = ImageDraw.Draw(body)
d.ellipse([s(54), s(104), s(190), s(228)], fill=255)
d.polygon([(s(96), s(118)), (s(150), s(118)), (s(150), s(56)), (s(116), s(46)), (s(98), s(70))], fill=255)
d.ellipse([s(96), s(40), s(152), s(100)], fill=255)
body = body.rotate(-18, center=(s(128), s(140)), resample=Image.BICUBIC)

# Body shading: dark plum fill, lighter plum lobe, peach glint.
shade = Image.new("RGBA", canvas.size, BODY_SHADE + (255,))
lobe = Image.new("L", canvas.size, 0)
ImageDraw.Draw(lobe).ellipse([s(40), s(90), s(170), s(210)], fill=255)
lobe = lobe.filter(ImageFilter.GaussianBlur(s(22)))
shade.paste(Image.new("RGBA", canvas.size, BODY + (255,)), mask=lobe)
glint = Image.new("L", canvas.size, 0)
ImageDraw.Draw(glint).ellipse([s(72), s(130), s(92), s(180)], fill=200)
glint = glint.filter(ImageFilter.GaussianBlur(s(5)))
shade.paste(Image.new("RGBA", canvas.size, BODY_LIGHT + (255,)), mask=glint)
canvas.paste(shade, mask=body)

# Calyx: sage cap with pointed sepals, and a short stem.
cap = Image.new("L", canvas.size, 0)
d = ImageDraw.Draw(cap)
cx, cy = 126, 62
for dx, dy in [(-38, 22), (-18, 34), (0, 38), (20, 34), (40, 22)]:
    d.polygon([(s(cx - 14), s(cy)), (s(cx + 14), s(cy)), (s(cx + dx), s(cy + dy))], fill=255)
d.ellipse([s(cx - 22), s(cy - 12), s(cx + 22), s(cy + 12)], fill=255)
d.rounded_rectangle([s(cx - 6), s(cy - 38), s(cx + 6), s(cy - 4)], radius=s(5), fill=255)
cap = cap.rotate(-18, center=(s(128), s(140)), resample=Image.BICUBIC)
canvas.paste(Image.new("RGBA", canvas.size, SAGE + (255,)), mask=cap)
rim = Image.new("L", canvas.size, 0)
ImageDraw.Draw(rim).rectangle([0, s(75), SIZE * SS, SIZE * SS], fill=255)
canvas.paste(Image.new("RGBA", canvas.size, SAGE_SHADE + (255,)), mask=Image.composite(cap, Image.new("L", canvas.size, 0), rim).point(lambda v: v // 3))

# Rounded-square mask like the other icons.
mask = Image.new("L", canvas.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE * SS - 1, SIZE * SS - 1], radius=s(48), fill=255)
canvas.putalpha(mask)

OUT.parent.mkdir(exist_ok=True)
canvas.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
print(OUT)
