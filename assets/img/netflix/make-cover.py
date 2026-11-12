#!/usr/bin/env python3
"""Build the Profile Lock cover art.

Not a screenshot: a reconstruction of the response shape, drawn from scratch.
Identifiers are truncated exactly as they are in the post.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 2000, 1125
BG = (5, 5, 5)
WHITE = (255, 255, 255)
GRAY = (199, 199, 199)
DIM = (102, 102, 102)
RED = (255, 0, 0)

MONO = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Regular.ttf"
MONO_B = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, x, y, text, font, fill, spacing):
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x


def width_tracked(draw, text, font, spacing):
    return sum(draw.textlength(c, font=font) + spacing for c in text) - spacing


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

kicker = f(MONO, 30)
body = f(MONO, 38)
big = f(MONO_B, 82)
small = f(MONO, 28)

# --- kicker ---------------------------------------------------------------
label = "PROFILE LOCK  \u00b7  READ PATH"
lx = (W - (width_tracked(d, label, kicker, 4) + 26)) // 2
d.rectangle([lx, 268, lx + 12, 280], fill=RED)
tracked(d, lx + 26, 256, label, kicker, WHITE, 4)

# --- the response line ----------------------------------------------------
line1 = '{"name": "the protected profile",'
x1 = (W - d.textlength(line1, font=body)) // 2
d.text((x1, 360), line1, font=body, fill=GRAY)

# lockPin line: '"lockPin": ' in white, the value in red
pre = '"lockPin": '
val = '"0978"'
wp = d.textlength(pre, font=big)
wv = d.textlength(val, font=big)
x0 = (W - (wp + wv)) // 2
d.text((x0, 432), pre, font=big, fill=WHITE)
d.text((x0 + wp, 432), val, font=big, fill=RED)

# --- the rest of the array ------------------------------------------------
line3 = "...four other profiles, every lockPin null }"
x3 = (W - d.textlength(line3, font=body)) // 2
d.text((x3, 574), line3, font=body, fill=DIM)

# --- footnote -------------------------------------------------------------
note = "one query  \u00b7  every profile on the account"
xn = (W - d.textlength(note, font=small)) // 2
d.text((xn, 672), note, font=small, fill=(68, 68, 68))

img.save("/root/Docue/ppp/shoo0lin.github.io/assets/img/netflix/00-cover-pin.png")
print("written")
