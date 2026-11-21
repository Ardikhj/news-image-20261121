#!/usr/bin/env python3
"""Renders the 21 November 2026 world-news summary as a 1024x1024 PNG.

Layout (fresh for this day — a newspaper front page):
  masthead -> hero story (Russian missiles in Poland) -> 2x2 story grid
  -> two mini stories -> source footer.

Every string below is a verified 21 November 2026 story, each with its
source. Nothing is invented: where a detail is unconfirmed it is left out.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 243, 234)      # newsprint cream
INK = (22, 22, 22)           # near-black
MUTED = (90, 86, 76)         # warm grey
RED = (179, 39, 30)          # masthead / kicker red
NAVY = (20, 39, 61)          # hero panel
NAVY_SOFT = (43, 66, 94)
CARD = (255, 255, 255)
CARD_LINE = (216, 210, 192)
CREAM_TEXT = (247, 243, 234)
GOLD = (212, 175, 55)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MARGIN = 28


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def spaced(text):
    """Letter-spaced kicker text."""
    return " ".join(list(text.replace(" ", "  ")))


def radar(draw, box):
    """Stylised radar sweep inside the hero graphic panel."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 8
    for i, rr in enumerate((r, int(r * 0.66), int(r * 0.33))):
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                     outline=(120, 150, 190), width=2 if i == 0 else 1)
    draw.line([cx - r, cy, cx + r, cy], fill=(120, 150, 190), width=1)
    draw.line([cx, cy - r, cx, cy + r], fill=(120, 150, 190), width=1)
    draw.line([cx, cy, cx + int(r * 0.7), cy - int(r * 0.7)],
              fill=GOLD, width=4)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                 outline=CREAM_TEXT, width=2)
    draw.text((cx, y1 - 24), "POLAND", font=font(SANS_B, 15),
              fill=CREAM_TEXT, anchor="mm")


def build_image():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 8], fill=RED)
    d.text((MARGIN, 22), "THE WORLD IN ONE PICTURE",
           font=font(SERIF_B, 42), fill=INK)
    d.text((W - MARGIN, 30), "SATURDAY", font=font(SANS_B, 20),
           fill=RED, anchor="ra")
    d.text((W - MARGIN, 54), "21 NOVEMBER 2026", font=font(SANS_B, 20),
           fill=INK, anchor="ra")
    d.text((MARGIN, 82), "Six stories from one day — reported by Reuters, "
           "One Turn, The Daily Short and Jagran Josh",
           font=font(SANS, 15), fill=MUTED)
    d.line([MARGIN, 108, W - MARGIN, 108], fill=INK, width=2)

    # ---- hero: Russian missiles hit Poland ------------------------------
    hx0, hy0, hx1, hy1 = MARGIN, 124, W - MARGIN, 448
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=6, fill=NAVY)
    d.text((hx0 + 28, hy0 + 22), spaced("MISSILES HIT POLAND"),
           font=font(SANS_B, 19), fill=GOLD)
    head = font(SERIF_B, 50)
    lines = wrap(d, "Russian missiles land in Poland",
                 head, 600)
    y = hy0 + 56
    for line in lines:
        d.text((hx0 + 28, y), line, font=head, fill=CREAM_TEXT)
        y += 58
    body = font(SANS, 19)
    for line in wrap(d, "Warsaw calls it a deliberate provocation. "
                     "NATO calls it a grave violation of its airspace "
                     "and scrambles jets.", body, 600):
        d.text((hx0 + 28, y), line, font=body, fill=(205, 214, 226))
        y += 26
    radar(d, (700, 150, 968, 422))
    d.text((hx0 + 28, hy1 - 34), "ONE TURN  ·  THE INDEPENDENT",
           font=font(SANS, 13), fill=(150, 165, 185))

    # ---- 2x2 story grid -------------------------------------------------
    grid = [
        ("UKRAINE WAR",
         "Putin Wants a Deal",
         "Trump says Putin told him in Shenzhen he wants a "
         "diplomatic end to the Ukraine war — but announced no "
         "ceasefire, no date and no terms.", "REUTERS"),
        ("MARKETS",
         "Wall Street in Correction",
         "The S&P 500 and the Dow slide into correction as AI "
         "shares sell off, down about 3.7% on Friday.", "ONE TURN"),
        ("PERU",
         "6.8 Quake Rattles the Andes",
         "A magnitude 6.8 earthquake strikes Junín in the Andes; "
         "tremors are felt in Lima, 320 km away.", "THE DAILY SHORT"),
        ("INDIA",
         "Cyclone Akvan Hits the Coast",
         "The storm crosses the Odisha coast near Gopalpur with "
         "heavy rain; 300,000 people are evacuated.", "JAGRAN JOSH"),
    ]
    gx = [MARGIN, 520]
    gy = [464, 640]
    cw, chh = 476, 160
    for i, (kick, head_txt, body_txt, src) in enumerate(grid):
        x0 = gx[i % 2]
        y0 = gy[i // 2]
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + chh], radius=5,
                            fill=CARD, outline=CARD_LINE, width=1)
        d.text((x0 + 18, y0 + 12), spaced(kick), font=font(SANS_B, 14),
               fill=RED)
        hf = font(SERIF_B, 25)
        yy = y0 + 36
        for line in wrap(d, head_txt, hf, cw - 36)[:1]:
            d.text((x0 + 18, yy), line, font=hf, fill=INK)
            yy += 32
        bf = font(SANS, 16)
        for line in wrap(d, body_txt, bf, cw - 36)[:3]:
            d.text((x0 + 18, yy), line, font=bf, fill=(52, 52, 52))
            yy += 22
        d.text((x0 + cw - 18, y0 + chh - 12), src, font=font(SANS, 12),
               fill=MUTED, anchor="rb")

    # ---- two mini stories ----------------------------------------------
    d.line([MARGIN, 816, W - MARGIN, 816], fill=INK, width=2)
    minis = [
        ("UK–EU SIGN THREE DEALS",
         "Food trade, carbon markets and youth mobility agreed "
         "at a Brussels summit.", "ONE TURN"),
        ("RIKERS TO CLOSE BY 2032",
         "New York Mayor Mamdani unveils the first full plan to "
         "shut the jail complex.", "THE DAILY SHORT"),
    ]
    for i, (head_txt, body_txt, src) in enumerate(minis):
        x0 = gx[i]
        d.text((x0, 832), head_txt, font=font(SERIF_B, 22), fill=INK)
        bf = font(SANS, 15)
        yy = 864
        for line in wrap(d, body_txt, bf, cw - 4)[:2]:
            d.text((x0, yy), line, font=bf, fill=(52, 52, 52))
            yy += 21
        d.text((x0, 922), src, font=font(SANS, 12), fill=MUTED)

    # ---- footer ---------------------------------------------------------
    d.line([MARGIN, 956, W - MARGIN, 956], fill=CARD_LINE, width=1)
    d.text((W // 2, 972),
           "Also: Eisenkot tapped to form Israel's government  ·  "
           "Record foreign cash into Indian shares  ·  "
           "KL Rahul completes the SENA set",
           font=font(SANS, 14), fill=MUTED, anchor="ma")
    d.text((W // 2, 998),
           "Built by an AI agent for make.fun  ·  news-image-20261121",
           font=font(SANS, 13), fill=MUTED, anchor="ma")
    return img
