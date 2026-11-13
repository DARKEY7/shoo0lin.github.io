#!/usr/bin/env python3
"""Build the cover art for posts/open-dcr.html.

Not a screenshot: a reconstruction of the registration exchange, drawn from
scratch. The client_id is truncated exactly as it is in the post.
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
body = f(MONO, 36)
big = f(MONO_B, 74)
value = f(MONO_B, 52)
small = f(MONO, 26)

# --- kicker ---------------------------------------------------------------
label = "ADOBE IMS  \u00b7  OPEN DCR"
lx = (W - (width_tracked(d, label, kicker, 4) + 26)) // 2
d.rectangle([lx, 232, lx + 12, 244], fill=RED)
tracked(d, lx + 26, 220, label, kicker, WHITE, 4)

# --- the request ----------------------------------------------------------
line1 = "POST /ims/register"
x1 = (W - d.textlength(line1, font=big)) // 2
d.text((x1, 300), line1, font=big, fill=WHITE)

line2 = "no Authorization header"
x2 = (W - d.textlength(line2, font=body)) // 2
d.text((x2, 402), line2, font=body, fill=GRAY)

# --- rule -----------------------------------------------------------------
d.line([W // 2 - 470, 476, W // 2 + 470, 476], fill=(45, 45, 45))

# --- the status and the credential it handed back --------------------------
line3 = "201 Created"
x3 = (W - d.textlength(line3, font=value)) // 2
d.text((x3, 510), line3, font=value, fill=RED)

pre = '"client_id": '
val = '"82734d52\u2026"'
wp = d.textlength(pre, font=body)
wv = d.textlength(val, font=value)
x0 = (W - (wp + wv)) // 2
d.text((x0, 596), pre, font=body, fill=GRAY)
d.text((x0 + wp, 586), val, font=value, fill=RED)

# --- the two properties that make it work ---------------------------------
l4 = '"token_endpoint_auth_method": "none"'
x4 = (W - d.textlength(l4, font=small)) // 2
d.text((x4, 690), l4, font=small, fill=GRAY)

l5 = '"redirect_uris": ["http://127.0.0.1:9999/cb"]'
x5 = (W - d.textlength(l5, font=small)) // 2
d.text((x5, 736), l5, font=small, fill=GRAY)

# --- footnote -------------------------------------------------------------
note = "no developer account  \u00b7  no review  \u00b7  no approval"
xn = (W - d.textlength(note, font=small)) // 2
d.text((xn, 842), note, font=small, fill=(116, 116, 116))

img.save("/root/Docue/ppp/shoo0lin.github.io/assets/img/adobe/00-cover-dcr.png")
print("written")
