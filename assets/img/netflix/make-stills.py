#!/usr/bin/env python3
"""Build the two redacted stills used in posts/profile-lock-pin.html.

Source is a terminal capture of the live session (white background, dark text).
Every 30-char profile GUID and every quoted profile name is covered with a solid
bar before the crop is scaled up and written to the site. The lockPin value is
deliberately left readable: it is the evidence, and the lock it belonged to no
longer exists on the account.

Boxes are full-resolution pixel coordinates measured from the source
(2560x1080) with tesseract word boxes. Padding is asymmetric because the gap
between the GUID column, the name column and the lockPin column is only a few
pixels wide - a symmetric pad clips the text we want to keep.
"""

from PIL import Image

SRC = "/mnt/c/Users/<user>/Videos/Netflix-lock/Screenshot_2026-10-23_15-19-31.png"
OUT = "/root/Docue/ppp/shoo0lin.github.io/assets/img/netflix"

BAR = (17, 17, 17)  # #111 - reads as deliberate redaction, not a glitch


def redact(im, boxes):
    px = im.load()
    for x0, y0, x1, y1, pl, pr, pv in boxes:
        for y in range(y0 - pv, y1 + pv):
            for x in range(x0 - pl, x1 + pr):
                if 0 <= x < im.width and 0 <= y < im.height:
                    px[x, y] = BAR
    return im


def build(name, crop, boxes, scale):
    im = Image.open(SRC).convert("RGB")
    redact(im, boxes)
    im = im.crop(crop)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    im.save(f"{OUT}/{name}", optimize=True)
    print(f"{name}: {im.width}x{im.height}")


# --- 1. the ProfileLockTemplate response: five profiles, five lockPin values ---
# GUID column x 35..269, quoted-name column x 282..347, rows y 276/295/314/333/352.
ROWS = [(276, 291), (295, 310), (314, 329), (333, 348), (352, 366)]
boxes_a = [(35, y0, 269, y1, 8, 5, 5) for y0, y1 in ROWS]      # GUIDs
boxes_a += [(282, y0, 347, y1, 6, 3, 5) for y0, y1 in ROWS]     # quoted names
build("01-lockpin-response.png", (0, 242, 660, 374), boxes_a, 2.0)

# --- 2. the unlock transcript: PIN present, PIN filled, gate passed ---
# pg= GUID sits at x 116..350 on the "[final]" line (y 636..653).
boxes_b = [(116, 636, 350, 653, 3, 5, 3)]
build("02-unlock-transcript.png", (0, 576, 900, 674), boxes_b, 1.5)
