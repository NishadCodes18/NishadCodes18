#!/usr/bin/env python3
"""Generate an animated football-themed GitHub contribution calendar.

Fetches the real public contribution history from github-contributions-api.jogruber.de,
then renders a 53-week heatmap. A small player avatar in a garnet shirt kicks a football
toward active contribution cells; the impact briefly highlights the selected square.

The checked-in GIF can be regenerated locally with:
    python scripts/generate_football_contributions.py

The initial repository preview can be refreshed through .github/workflows/snake.yml.
"""
from __future__ import annotations

import json
import math
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "year-of-building.gif"
USERNAME = "NishadCodes18"
API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"

NAVY = "#0D111B"
NAVY2 = "#151B2A"
GARNET = "#6A1039"
GARNET_BRIGHT = "#B50954"
PINK = "#F0B6D0"
SKY = "#75D5F5"
SKY_LIGHT = "#C6F0FF"
WHITE = "#F8F7FB"
GOLD = "#F3C64E"
MUTED = "#B7BAC8"
CELL_LEVELS = ["#24101D", "#6A1039", "#A50044", "#27A8D8", "#BDEEFF"]

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)

F_MONO = "DejaVuSansMono.ttf"
F_SANS = "DejaVuSans.ttf"
F_BOLD = "DejaVuSans-Bold.ttf"
F_SERIF = "DejaVuSerif.ttf"
F_SERIF_ITALIC = "DejaVuSerif-Italic.ttf"

WIDTH, HEIGHT = 1280, 590
CELL = 14
GAP = 5
STEP = CELL + GAP
GRID_X = 150
GRID_Y = 285
GRID_COLS = 53
GRID_W = GRID_COLS * STEP - GAP

def fetch_data():
    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "NishadCodes18-GitHub-Profile/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = json.loads(response.read().decode("utf-8"))
    items = payload.get("contributions", [])
    if not isinstance(items, list) or not items:
        raise RuntimeError("Contribution API returned no daily contribution data.")
    parsed = {}
    for item in items:
        try:
            day = date.fromisoformat(item["date"])
            count = max(0, int(item["count"]))
            level = int(item.get("level", 0))
            level = min(4, max(0, level))
            parsed[day] = {"count": count, "level": level}
        except (KeyError, TypeError, ValueError):
            continue
    if not parsed:
        raise RuntimeError("Could not parse GitHub contribution data.")
    return parsed

def metrics_for(data):
    days = sorted(data)
    total = sum(data[d]["count"] for d in days)
    active = [d for d in days if data[d]["count"] > 0]
    longest = current = 0
    previous = None
    for d in days:
        if data[d]["count"] > 0:
            current = current + 1 if previous and d == previous + timedelta(days=1) else 1
            longest = max(longest, current)
        else:
            current = 0
        previous = d
    busiest = max(days, key=lambda d: data[d]["count"])
    return total, len(active), longest, busiest, data[busiest]["count"]

def make_grid(data):
    last_day = max(data)
    first_day = last_day - timedelta(days=364)
    # GitHub week columns begin on Sunday.
    start = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    grid = [[None for _ in range(7)] for _ in range(GRID_COLS)]
    date_to_cell = {}
    for offset in range(GRID_COLS * 7):
        day = start + timedelta(days=offset)
        col = offset // 7
        row = offset % 7
        item = data.get(day, {"count": 0, "level": 0})
        grid[col][row] = {"date": day, **item}
        if day in data:
            date_to_cell[day] = (col, row)
    return grid, date_to_cell, start, last_day

def rgb(hex_color):
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_soccer_ball(draw, cx, cy, radius=8, glow=False):
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill="#F9FCFF", outline="#18223A", width=2)
    # recognizable pentagon panels
    points = [
        (cx, cy-radius//2), (cx+radius//2, cy-radius//4),
        (cx+radius//3, cy+radius//2), (cx-radius//3, cy+radius//2),
        (cx-radius//2, cy-radius//4),
    ]
    draw.polygon(points, fill="#16243D")
    for px, py in [(cx,cy-radius+2),(cx+radius-2,cy),(cx,cy+radius-2),(cx-radius+2,cy)]:
        draw.line((cx,cy,px,py), fill="#16243D", width=1)

def draw_player(frame, x, y, phase):
    """Draw a small pixel-style player avatar: dark hair, garnet shirt, sky-blue boots."""
    # Draw on 3x surface, then downsample for crisp miniature edges.
    S = 3
    sw, sh = 54, 72
    sprite = Image.new("RGBA", (sw*S, sh*S), (0,0,0,0))
    d = ImageDraw.Draw(sprite)
    def box(coords, fill, outline=None, width=1):
        c = tuple(int(v*S) for v in coords)
        d.rectangle(c, fill=fill, outline=outline, width=width*S if width else 1)
    # ground shadow
    d.ellipse((8*S, 63*S, 49*S, 69*S), fill=(0,0,0,100))
    # head and hair
    box((18, 4, 35, 21), "#C88A65")
    box((16, 2, 36, 9), "#11131A")
    box((14, 6, 20, 13), "#151821")
    box((31, 4, 38, 12), "#171923")
    box((18, 19, 35, 22), "#B97559")
    # neck
    box((24, 21, 30, 26), "#C88A65")
    # torso, slightly tilted on kick
    box((15, 25, 39, 47), "#A50044")
    box((12, 27, 17, 39), "#8A0B3D")
    box((37, 27, 42, 38), "#8A0B3D")
    box((19, 28, 35, 31), "#D4145A")
    # jersey detail: garnet home kit with a subtle sky-blue training stripe
    box((25, 32, 29, 36), "#F3C64E")
    box((18, 43, 36, 45), "#75D5F5")
    box((21, 39, 34, 41), "#7D0F3D")
    # arms
    box((9, 27, 14, 42), "#C88A65")
    box((40, 27, 44, 41), "#C88A65")
    box((8, 40, 14, 44), "#B97559")
    box((40, 39, 46, 43), "#B97559")
    # shorts
    box((16, 47, 38, 55), "#18243A")
    # planted leg
    box((18, 54, 23, 64), "#C88A65")
    box((21, 62, 30, 67), "#75D5F5")
    # kicking leg changes position through the cycle
    if phase in (3, 4, 5, 6):
        # extended swing leg
        box((32, 53, 37, 58), "#C88A65")
        box((36, 56, 47, 61), "#C88A65")
        box((44, 58, 51, 63), "#75D5F5")
    elif phase in (7,):
        box((32, 54, 38, 63), "#C88A65")
        box((35, 62, 43, 67), "#75D5F5")
    else:
        box((31, 54, 36, 64), "#C88A65")
        box((32, 62, 40, 67), "#75D5F5")
    # small skin-tone ears and simple face detail
    box((19, 12, 21, 14), "#E1A47C")
    box((32, 12, 34, 14), "#E1A47C")
    box((27, 13, 28, 14), "#2B1A19")
    sprite = sprite.resize((72, 96), Image.Resampling.NEAREST)
    frame.alpha_composite(sprite, (int(x), int(y)))

def create_frame(grid, date_to_cell, metrics, frame_index, preview=False):
    frame = Image.new("RGBA", (WIDTH, HEIGHT), NAVY)
    px = frame.load()
    # Subtle coloured stage lighting, not a dull flat black.
    for yy in range(HEIGHT):
        for xx in range(WIDTH):
            left = max(0, 1 - abs(xx/WIDTH - .04)*5) * max(0,1-yy/HEIGHT)
            right = max(0, 1 - abs(xx/WIDTH - .95)*4) * max(0,1-yy/HEIGHT)
            if left > .015 or right > .015:
                base = (13,17,27)
                px[xx,yy] = (
                    int(base[0] + left*30 + right*5),
                    int(base[1] + right*18),
                    int(base[2] + left*10 + right*36),
                    255,
                )
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (2,2,WIDTH-3,HEIGHT-3), 25, (16,20,32,255), (83,61,91,255), 2)
    # Section title
    d.text((46, 28), "05  /  COMMIT LOG", font=font(F_MONO, 15), fill=SKY)
    d.text((46, 58), "A year of", font=font(F_SERIF, 42), fill=WHITE)
    d.text((225, 58), "building.", font=font(F_SERIF_ITALIC, 42), fill=PINK)
    d.text((1230, 38), "REAL DATA  ·  REFRESHED DAILY", font=font(F_MONO, 12), fill=(212,222,237,255), anchor="ra")
    d.text((47, 128), "Every commit is a touch. Keep the game moving.", font=font(F_SERIF_ITALIC, 22), fill=(220,218,229,255))
    # Metrics: no invented values in preview.
    if preview:
        vals = [("CONTRIBUTIONS", "LIVE SYNC"), ("ACTIVE DAYS", "PENDING"), ("LONGEST STREAK", "PENDING"), ("BUSIEST DAY", "PENDING")]
    else:
        total, active, streak, busiest, busy_count = metrics
        vals = [
            ("CONTRIBUTIONS", f"{total:,}"),
            ("ACTIVE DAYS", f"{active:,}"),
            ("LONGEST STREAK", f"{streak} days"),
            ("BUSIEST DAY", f"{busy_count} · {busiest.strftime('%d %b')}"),
        ]
    metric_xs = [690, 835, 980, 1125]
    for (label, value), mx in zip(vals, metric_xs):
        d.text((mx, 113), label, font=font(F_MONO, 10), fill=PINK)
        d.text((mx, 139), value, font=font(F_SERIF, 22), fill=WHITE)
    # Grid background card
    rounded(d, (38, 184, 1242, 552), 20, (26,10,23,210), (112,47,79,210), 1)
    # Month labels
    month_seen = set()
    for col in range(GRID_COLS):
        first = grid[col][0]
        # grid row 0 is Sunday; first date in column
        if first and first["date"].month not in month_seen and first["date"].day <= 7:
            month_seen.add(first["date"].month)
            d.text((GRID_X + col*STEP, 218), first["date"].strftime("%b"), font=font(F_MONO, 10), fill=SKY_LIGHT)
    # weekday labels
    for row, label in [(1,"Mon"), (3,"Wed"), (5,"Fri")]:
        d.text((83, GRID_Y + row*STEP + 1), label, font=font(F_MONO, 9), fill=(197,205,220,255))
    # actual or preview contribution cells
    active_cells = []
    for col in range(GRID_COLS):
        for row in range(7):
            cell = grid[col][row]
            if cell is None:
                continue
            level = cell["level"]
            x = GRID_X + col*STEP
            y = GRID_Y + row*STEP
            fill = CELL_LEVELS[level]
            # Brighten cells with highest counts.
            d.rounded_rectangle((x,y,x+CELL,y+CELL), radius=4, fill=fill, outline=(255,255,255,16), width=1)
            if cell["count"] > 0:
                active_cells.append((col,row,cell["count"]))
    # Use actual active contribution cells for target squares; sample evenly through the year.
    if active_cells:
        n_targets = min(8, len(active_cells))
        target_indexes = [round(i*(len(active_cells)-1)/max(1,n_targets-1)) for i in range(n_targets)]
        targets = [active_cells[i] for i in target_indexes]
    else:
        targets = [(3+i*6, (i*3+1)%7, 0) for i in range(8)]
    # Pick one target per 6-frame kick sequence.
    kick_number = min(len(targets)-1, frame_index // 8)
    phase = frame_index % 8
    target_col, target_row, target_count = targets[kick_number]
    target_x = GRID_X + target_col*STEP + CELL//2
    target_y = GRID_Y + target_row*STEP + CELL//2
    # Previously hit squares keep a faint accent ring, but their heat colour remains the real level.
    hit_count = min(len(targets), frame_index // 8)
    for j in range(hit_count):
        c, r, _ = targets[j]
        cx = GRID_X + c*STEP + CELL//2
        cy = GRID_Y + r*STEP + CELL//2
    # Moving player traverses below the graph while the ball travels to a selected activity square.
    player_x = 86 + kick_number*132 + phase*5
    player_y = 414
    # player shadow / foot marker
    draw_player(frame, player_x, player_y, phase)
    # ball flight arc: starts at kicking foot and climbs to target
    start_x = player_x + 63
    start_y = player_y + 85
    t = phase / 7.0
    ball_x = int(start_x + (target_x - start_x)*t)
    ball_y = int(start_y + (target_y - start_y)*t - math.sin(math.pi*t)*78)
    # Hold near foot before kick, then fly.
    if phase == 0:
        ball_x, ball_y = start_x + 5, start_y - 2
    draw_soccer_ball(d, ball_x, ball_y, radius=8, glow=False)
    # Impact: light up the current square for the last frame of the kick.
    if phase == 7:
        d.rounded_rectangle(
            (target_x-CELL//2-5, target_y-CELL//2-5, target_x+CELL//2+5, target_y+CELL//2+5),
            radius=6, outline=(246,200,78,255), width=3
        )
    # Bottom captions and legend
    d.text((48, 540), "NISHAD  /  DEVELOPER XI", font=font(F_MONO, 11), fill=SKY_LIGHT)
    d.text((984, 540), "LESS", font=font(F_MONO, 9), fill=MUTED, anchor="lm")
    for i, color in enumerate(CELL_LEVELS):
        d.rounded_rectangle((1030+i*17, 534, 1042+i*17, 546), radius=3, fill=color)
    d.text((1122, 540), "MORE", font=font(F_MONO, 9), fill=MUTED, anchor="lm")
    if preview:
        d.rounded_rectangle((942, 153, 1218, 177), radius=11, fill=(8,12,21,230), outline=(117,213,245,180))
        d.text((1080, 165), "PREVIEW · RUN WORKFLOW FOR LIVE DATA", font=font(F_MONO, 9), fill=SKY_LIGHT, anchor="mm")
    return frame.convert("RGB")

def build_animation(data, preview=False):
    grid, date_to_cell, grid_start, last_day = make_grid(data)
    metrics = metrics_for(data) if not preview else None
    frames = []
    frame_count = 64
    for i in range(frame_count):
        frames.append(create_frame(grid, date_to_cell, metrics, i, preview=preview).convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=380,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Saved {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    if metrics:
        print("Contribution metrics:", metrics)

if __name__ == "__main__":
    payload = fetch_data()
    build_animation(payload, preview=False)
