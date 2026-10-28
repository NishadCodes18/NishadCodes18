#!/usr/bin/env python3
"""Regenerate clean section headers and slow existing profile GIFs once."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MARKER = ASSETS / ".profile-animations-slowed-v1"
W, H = 1280, 160
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
MONO = ImageFont.truetype(str(FONT_DIR / "DejaVuSansMono.ttf"), 14)
SERIF = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif.ttf"), 57)
ITALIC = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif-Italic.ttf"), 57)

HEADERS = {
    "title-about.gif": ("01  ABOUT", "Hello, I'm ", "Nishad.", "WHO I AM"),
    "title-recognition.gif": ("02  RECOGNITION", "Proof, ", "on the record.", "HACKATHONS  ·  ACADEMICS  ·  GROWTH"),
    "title-work.gif": ("03  SELECTED WORK", "Projects with ", "purpose.", "PROJECTS  ·  EXPERIMENTS"),
    "title-toolkit.gif": ("04  TOOLKIT", "The tools I ", "reach for.", "LANGUAGES  ·  AI  ·  WEB  ·  DATA  ·  TOOLS"),
    "title-commits.gif": ("05  COMMIT LOG", "A year of ", "building.", "REAL CONTRIBUTIONS  ·  REFRESHED DAILY"),
    "title-certifications.gif": ("06  CERTIFICATIONS", "Learning, ", "verified.", "COURSES  ·  CREDENTIALS"),
    "title-connect.gif": ("07  CONNECT", "Let's build ", "something.", "OPEN TO COLLABORATION"),
}

def render_header(filename, kicker, prefix, accent, right):
    image = Image.new("P", (W, H), 0)
    palette = [0, 0, 0, 117, 213, 245, 248, 247, 251, 240, 182, 208, 183, 186, 200, 165, 0, 68, 243, 198, 78]
    palette += [0] * (768 - len(palette))
    image.putpalette(palette)
    draw = ImageDraw.Draw(image)
    draw.text((18, 17), kicker, font=MONO, fill=1)
    right_font = ImageFont.truetype(str(FONT_DIR / "DejaVuSansMono.ttf"), 11)
    draw.text((1260, 21), right, font=right_font, fill=4, anchor="ra")
    y = 47
    draw.text((18, y), prefix, font=SERIF, fill=2)
    prefix_width = draw.textbbox((18, y), prefix, font=SERIF)[2] - 18
    draw.text((18 + prefix_width + 7, y), accent, font=ITALIC, fill=3)
    draw.line((18, 137, 1260, 137), fill=5, width=2)
    image.save(ASSETS / filename, format="GIF", transparency=0, duration=5000, loop=0, optimize=True)

def slow_existing_gifs():
    if MARKER.exists():
        print("Existing GIFs were already slowed; skipping cumulative changes.")
        return
    for path in sorted(ASSETS.glob("*.gif")):
        if path.name.startswith("title-") or path.name == "year-of-building.gif":
            continue
        try:
            source = Image.open(path)
        except (OSError, ValueError) as exc:
            print(f"Skipping unreadable GIF {path.name}: {exc}")
            continue
        frames = [frame.copy() for frame in ImageSequence.Iterator(source)]
        if len(frames) < 2:
            continue
        durations = []
        for frame in ImageSequence.Iterator(source):
            old = int(frame.info.get("duration", source.info.get("duration", 120)))
            durations.append(max(180, min(1200, round(old * 2.1))))
        loop = source.info.get("loop", 0)
        transparency = source.info.get("transparency")
        frames[0].save(
            path, save_all=True, append_images=frames[1:], duration=durations,
            loop=loop, optimize=False, disposal=2,
            **({"transparency": transparency} if transparency is not None else {})
        )
        print(f"Slowed {path.name}")
    MARKER.write_text("Profile GIFs slowed once; section headers regenerated without floating orbs.\n", encoding="utf-8")

def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for filename, values in HEADERS.items():
        render_header(filename, *values)
    slow_existing_gifs()

if __name__ == "__main__":
    main()
