#!/usr/bin/env python3
"""Build the four redacted stills used in posts/open-dcr.html.

Source is the June 2026 capture of the live flow: three full-screen shots
(2560x1080) taken while the flow ran.

The consenting identity, the tail of the app name, the authorization code and
the issued token values are covered with a solid bar before the crop is scaled
and written to the site. The bars are all #333 - the sources are dark-mode, so
a near-black bar would disappear into the window chrome and read as a rendering
fault rather than a deliberate redaction.

Boxes are full-resolution pixel coordinates measured on the source with
tesseract word boxes. Each mask is applied to the source and the crop happens
afterwards, so the numbers below are source coordinates, not crop-relative.

Crop widths are chosen for legibility, not for framing: the prose column is
800px, so on-screen glyph size is roughly source_px * 800 / crop_width. Crops
wider than ~900px make 13px terminal text unreadable once the figure is laid
out, which is why each still below frames one line of the flow.
"""

from PIL import Image

SRC = "/mnt/c/Users/DARKEY/Videos/Unauthenticated Dynamic Client Registration enables OAuth account takeover"
OUT = "/root/Docue/ppp/shoo0lin.github.io/assets/img/adobe"

BAR = (51, 51, 51)  # #333 - visible against dark chrome without shouting


def redact(im, boxes):
    px = im.load()
    for x0, y0, x1, y1 in boxes:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if 0 <= x < im.width and 0 <= y < im.height:
                    px[x, y] = BAR
    return im


def build(name, src, crop, boxes, scale):
    im = Image.open(f"{SRC}/{src}").convert("RGB")
    redact(im, boxes)
    im = im.crop(crop)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    im.save(f"{OUT}/{name}", optimize=True)
    print(f"{name}: {im.width}x{im.height}")


# --- 1. the consent card: the app name is a client_id, not a name ------------
# crop starts just above the icon row (y 172) and stops after "Sign you in"
# (y 395), before the boilerplate paragraph.
build(
    "01-consent.png",
    "Screenshot_2026-06-02_07-31-24.png",
    (990, 152, 1470, 414),
    [
        (1092, 274, 1420, 312),   # the signed-in name + address line
        (1155, 168, 1470, 208),   # tail of the client_id shown as the app name
    ],
    2.0,
)

# --- 2. the redirect lands on the loopback listener --------------------------
# address-bar strip only. The tab title above it repeats the code, so the crop
# starts below the tab strip (y 34); the mask starts after "…/cb?code=" (x 974)
# so the destination host and the parameter name stay legible.
build(
    "02-loopback.png",
    "Screenshot_2026-06-02_07-31-36.png",
    (700, 34, 1220, 92),
    [(974, 40, 1220, 86)],  # the code value in the address bar
    3.0,
)

# --- 3. the terminal catches the code ---------------------------------------
# keep the "Waiting" line, the banner, the "Authorization code:" label and the
# first base64url characters that identify the value as a JWT; mask the body
# and every continuation line. The trailing "State:" line (y 342) is outside
# the crop.
build(
    "03-code-captured.png",
    "Screenshot_2026-06-02_07-31-28.png",
    (0, 84, 800, 340),
    [
        (470, 140, 800, 172),   # rest of the code on the first line
        (0, 172, 800, 340),     # wrapped continuation lines
    ],
    2.0,
)

# --- 4. the token response --------------------------------------------------
# keep "HTTP 200", "token_type: bearer" and "expires_in: 86399 seconds"; mask
# the script's own banner and every token value. The crop stops above the
# "scope:" line (y 848) - it is the one line in this block that would show the
# granted scopes without redaction, and the post states them in prose anyway.
build(
    "04-token-200.png",
    "Screenshot_2026-06-02_07-31-28.png",
    (0, 532, 800, 842),
    [
        (20, 640, 430, 682),   # "*** FULL ACCOUNT TAKEOVER ***" script banner
        (215, 700, 800, 790),  # access / refresh / id token values
    ],
    2.0,
)
