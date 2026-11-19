"""Draws System windows, status windows and ranking boards as crisp text overlays for story episodes.

The image model draws a glowing window with no readable text; the assembler puts these exact words on top, so they
are always spelled right and look the same every time. In a script, put a `[ui: ...]` tag on the beat's image line:

    **32** `[image: close-up of {panel} ...]` `[ui: system | [Refine] | Raise the rank of any item by one. | Rarely, by two.]`
    **80** `[image: ...status window...]` `[ui: status | Aeliss | Tide-Caller · EPIC | HP 90/90 | STR 12/100 | MANA 96/100 | Loyalty 60% | Affinity 5%]`
    **92** `[image: ...leaderboard...]` `[ui: ranking | Daily Ranking · Day 1 | 1 Seo Yun-jae | 2 Kaiser | 3 ...]`

system:  a title line then text lines. status: a name, a subtitle, then "Label value/max" or "Label nn%" bars.
ranking: a title, then "place name" rows (place 1 in gold, 2 silver, 3 bronze).
Rarity words (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, APEX) are drawn in their colour wherever they appear.
Lines are revealed one by one over the first part of the beat, then the whole window stays up.
"""
import os
import re

W = 1920
SCALE = 1.5   # windows are drawn this much bigger than the base layout, so the text reads on a phone


def u(n):
    return int(round(n * SCALE))
RARITY = {"COMMON": (225, 225, 225), "UNCOMMON": (90, 220, 110), "RARE": (70, 150, 255), "EPIC": (190, 100, 255),
          "LEGENDARY": (255, 200, 60), "APEX": (255, 70, 70)}
BAR_COLORS = {"HP": (230, 70, 80), "STR": (240, 150, 50), "AGI": (90, 210, 120), "MANA": (70, 160, 255),
              "LOYALTY": (255, 205, 80), "AFFINITY": (255, 130, 190)}
CYAN, TEXT, DIM = (80, 220, 255), (235, 248, 255), (150, 190, 215)
PLACE = {1: (255, 205, 70), 2: (200, 210, 225), 3: (215, 140, 80)}


def font(size, bold=False):
    from PIL import ImageFont
    names = (["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
             if bold else
             ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for name in names:
        try:
            return ImageFont.truetype(name, u(size))
        except OSError:
            continue
    return ImageFont.load_default()


def parse(spec):
    parts = [p.strip() for p in spec.split("|")]
    return parts[0].lower(), [p for p in parts[1:] if p]


def colored_words(draw, xy, text, fnt, base):
    """Draws text, painting rarity words in their colour."""
    x, y = xy
    for token in re.split(r"(\s+)", text):
        if not token:
            continue
        word = re.sub(r"[^A-Za-z]", "", token).upper()
        draw.text((x, y), token, font=fnt, fill=RARITY.get(word, base))
        x += draw.textlength(token, font=fnt)


def frame(draw, w, h, title):
    draw.rounded_rectangle((u(6), u(6), w - u(6), h - u(6)), radius=u(22), fill=(8, 22, 48, 225), outline=CYAN + (255,), width=u(4))
    draw.rounded_rectangle((u(16), u(16), w - u(16), u(74)), radius=u(14), fill=(20, 70, 120, 235))
    draw.text((u(36), u(22)), title, font=font(36, True), fill=CYAN)


def layout(kind, items):
    """Rows to draw: (kind of row, payload). The first row is the window title."""
    if kind == "status":
        name, sub, rest = items[0], (items[1] if len(items) > 1 else ""), items[2:]
        return "STATUS", [("name", name)] + ([("sub", sub)] if sub else []) + [("bar", r) for r in rest]
    if kind == "ranking":
        return items[0] if items else "RANKING", [("rank", r) for r in items[1:]]
    return (items[0] if items else "SYSTEM"), [("text", r) for r in items[1:]]


def row_height(row):
    return u({"name": 58, "sub": 44, "bar": 54, "rank": 52}.get(row[0], 50))


def draw_row(draw, x, y, w, row):
    kind, value = row
    if kind == "name":
        draw.text((x, y), value, font=font(46, True), fill=TEXT)
    elif kind == "sub":
        colored_words(draw, (x, y + u(4)), value, font(32), DIM)
    elif kind == "bar":
        m = re.match(r"(.+?)\s+(\d+)\s*(?:/\s*(\d+)|(%))\s*$", value)
        if not m:
            colored_words(draw, (x, y + u(6)), value, font(34), TEXT)
            return
        label, num, top, pct = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        frac = num / 100 if pct else num / max(int(top), 1)
        color = BAR_COLORS.get(label.upper(), CYAN)
        draw.text((x, y + u(6)), label, font=font(32, True), fill=TEXT)
        bx, bw = x + u(190), w - u(190) - u(190)
        draw.rounded_rectangle((bx, y + u(12), bx + bw, y + u(40)), radius=u(10), fill=(30, 45, 70, 255))
        if frac > 0:
            draw.rounded_rectangle((bx, y + u(12), bx + max(u(14), int(bw * min(frac, 1))), y + u(40)), radius=u(10), fill=color + (255,))
        draw.text((bx + bw + u(20), y + u(6)), f"{num}%" if pct else f"{num}/{top}", font=font(32), fill=TEXT)
    elif kind == "rank":
        m = re.match(r"#?(\d+)\.?\s+(.*)", value)
        place, name = (int(m.group(1)), m.group(2)) if m else (0, value)
        z = re.match(r"(.*?)\s*(\([^)]*\))\s*$", name)
        name, zone = (z.group(1), z.group(2)) if z else (name, "")
        color = PLACE.get(place, TEXT)
        draw.text((x, y), f"#{place}" if place else "", font=font(38, True), fill=color)
        nf = font(38, place == 1)
        draw.text((x + u(112), y), name, font=nf, fill=color if place in PLACE else TEXT)
        if zone:
            draw.text((x + u(112) + draw.textlength(name, font=nf) + u(16), y + u(6)), zone, font=font(30), fill=DIM)
    else:
        colored_words(draw, (x, y), value, font(38), TEXT)


def wrap(kind, rows, width):
    """Splits long text rows to fit the window."""
    from PIL import Image, ImageDraw
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    out = []
    for row in rows:
        if row[0] != "text":
            out.append(row)
            continue
        line = ""
        for word in row[1].split():
            test = f"{line} {word}".strip()
            if line and probe.textlength(test, font=font(38)) > width:
                out.append(("text", line))
                line = word
            else:
                line = test
        out.append(("text", line))
    return out


def render(spec, folder, tag):
    """PNG files for the window, one per reveal step (the last one shows everything), and the window's size."""
    from PIL import Image, ImageDraw
    kind, items = parse(spec)
    title, rows = layout(kind, items)
    width = u(1100 if kind != "status" else 980)
    rows = wrap(kind, rows, width - u(90))
    height = u(96) + sum(row_height(r) for r in rows) + u(28)
    paths = []
    for step in range(1, len(rows) + 1):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        frame(draw, width, height, title)
        y = u(96)
        for row in rows[:step]:
            draw_row(draw, u(44), y, width - u(88), row)
            y += row_height(row)
        path = os.path.join(folder, f"ui_{tag}_{step:02d}.png")
        img.save(path)
        paths.append(path)
    return paths


def filter_chain(paths, length, first_input, base="[v0]", out="[v]"):
    """ffmpeg filter text overlaying the reveal steps on `base`, centred, within a beat of `length` seconds."""
    reveal = min(length * 0.45, 0.35 * len(paths))
    step = reveal / max(len(paths), 1)
    parts, cur = [], base
    for k, _ in enumerate(paths):
        a = 0.15 + k * step
        b = 0.15 + (k + 1) * step if k < len(paths) - 1 else length + 1
        nxt = out if k == len(paths) - 1 else f"[u{k}]"
        parts.append(f"{cur}[{first_input + k}:v]overlay=x=(W-w)/2:y=(H-h)/2:enable='between(t,{a:.3f},{b:.3f})'{nxt}")
        cur = nxt
    return ";".join(parts)
