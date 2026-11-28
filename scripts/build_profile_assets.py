#!/usr/bin/env python3
"""Render the README images in the portfolio's mono + red style.

Black #000, white text, one accent red #ff2a2a, muted #8a8a8a, hairlines rgba(255,255,255,.12).
Anton for display, JetBrains Mono for labels (both bundled in scripts/fonts), Manrope for body
(system fallback if Google Fonts is unreachable).

    pip install playwright pillow && python scripts/build_profile_assets.py

Uses the installed Google Chrome (channel="chrome"); the toolkit grid loads devicon SVGs from jsDelivr.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCRIPTS = ROOT / "scripts"
W = 1200

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap');
@font-face{font-family:Anton;src:url(fonts/Anton-Regular.ttf)}
@font-face{font-family:JBM;src:url(fonts/JetBrainsMono.ttf);font-weight:100 900}
:root{--bg:#000;--bg2:#0b0b0b;--ink:#fff;--muted:#8a8a8a;--line:rgba(255,255,255,.12);--red:#ff2a2a}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:Manrope,system-ui,sans-serif;width:%dpx}
.c{background:var(--bg);position:relative;overflow:hidden}
.d{font-family:Anton,Impact,sans-serif;text-transform:uppercase;font-weight:400;line-height:.88}
.m{font-family:JBM,monospace;text-transform:uppercase;letter-spacing:.14em}
.label{font-family:JBM,monospace;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);display:inline-flex;gap:14px;align-items:center}
.label::before{content:"";width:34px;height:1px;background:var(--red)}
.o{color:transparent;-webkit-text-stroke:2px #fff}
.r{color:var(--red)}
.pill{font-family:JBM,monospace;font-size:13px;letter-spacing:.08em;text-transform:uppercase;padding:6px 13px;border-radius:99px;border:1px solid rgba(255,255,255,.22);color:#fff}
.pill.live{border-color:rgba(255,42,42,.6);color:#ff6b6b}
.pill.wip{border-color:rgba(255,42,42,.6);color:var(--red)}
.pill.client{border-color:rgba(255,255,255,.6)}
""" % W


def page_html(body: str, extra_css: str = "") -> str:
    return f"<!doctype html><meta charset=utf-8><style>{CSS}{extra_css}</style><body>{body}</body>"


class Renderer:
    def __init__(self, page):
        self.page = page
        self.tmp = SCRIPTS / ".render.html"  # next to fonts/ and covers/ so relative URLs resolve

    def load(self, html: str):
        self.tmp.write_text(html, encoding="utf-8")
        self.page.goto(self.tmp.as_uri(), wait_until="networkidle")
        self.page.evaluate("document.fonts.ready")

    def png(self, name: str, body: str, extra_css: str = ""):
        self.load(page_html(body, extra_css))
        out = ASSETS / name
        self.page.locator(".c").first.screenshot(path=str(out))
        print(f"{name}: {out.stat().st_size:,} bytes")


# ---------- content (mirrors nishadcodes18-portfolio.vercel.app) ----------
SECTIONS = {
    "about": ("01", "About", "Who I <span class=o>am</span>", "Off the pitch"),
    "stats": ("02", "Attributes", "Player <span class=o>stats</span>", "Self-rated · 2026"),
    "recognition": ("03", "Recognition", "Trophy <span class=o>cabinet</span>", "On the record"),
    "work": ("04", "Selected work", "Match <span class=o>highlights</span>", "Built end to end"),
    "toolkit": ("05", "Kit bag", "Tools of <span class=o>the trade</span>", "Daily drivers"),
    # (06) Season form header is drawn inside year-of-building.gif by generate_football_contributions.py
}

PROJECTS = [
    ("docusphere", "01", "DocuSphere AI", [("live", "Live"), ("", "AI"), ("", "Next.js"), ("", "pgvector")],
     "Document intelligence &amp; exam studio with hybrid RAG (HNSW + tsvector + RRF) for citation-grounded answers.",
     "covers/docusphere.webp"),
    ("acre", "02", "ACRe", [("wip", "In progress"), ("", "Team lead"), ("", "ML"), ("", "Security")],
     "AI-powered Cyber Resilience Engine: detects and classifies attacks, applies controlled defences, verifies them and explains incidents.",
     "covers/acre.webp"),
    ("nitrro", "03", "Nitrro Zone 360", [("client", "Client work"), ("live", "Live"), ("", "WordPress"), ("", "SEO")],
     "Production website for a gym in Baner–Balewadi, Pune: custom theme, local SEO and WhatsApp-first enquiries.",
     "covers/nitrro.webp"),
    ("careercompiler", "04", "CareerCompiler AI", [("live", "Live"), ("", "AI"), ("", "Next.js"), ("", "FastAPI")],
     "Evidence-backed resume compiler turning verified achievements into ATS-tested resumes.",
     "covers/careercompiler.webp"),
    ("sutra", "05", "S.U.T.R.A.", [("", "Edge AI"), ("", "Python"), ("", "Vision")],
     "Moving traffic, saving lives. Edge-AI traffic node fusing vision and audio for adaptive flow and emergency priority.",
     None),
    ("pt-tracker", "06", "PT Tracker CRM", [("", "Built"), ("", "React"), ("", "Node"), ("", "CRM")],
     "CRM and expense tracker for personal trainers: clients, payments, renewals and business finances in one app.",
     None),
    ("gym", "07", "Gym Site", [("", "HTML"), ("", "CSS"), ("", "JS")],
     "A modern, responsive website template for a fitness centre with high-converting UI.",
     "covers/gym.webp"),
    ("f1", "08", "F1 Site", [("", "HTML"), ("", "CSS"), ("", "JS")],
     "A simple, sleek website dedicated to Formula 1 race tracking &amp; statistics.",
     "covers/f1.webp"),
]

GEN_COVER = {"sutra": ("S.U.T.R.A.", "#ff2a2a", "#111"), "pt-tracker": ("PT Tracker", "#2a2a2a", "#ff2a2a")}

STATS = [("Web Dev", 85), ("Leadership", 81), ("DSA", 65), ("Core CS", 65), ("Problem Solving", 60), ("Mobile Dev", 55)]

TOOLS = [("python/python-original", "Python"), ("javascript/javascript-original", "JavaScript"),
         ("react/react-original", "React"), ("nextjs/nextjs-original", "Next.js"),
         ("fastapi/fastapi-original", "FastAPI"), ("tensorflow/tensorflow-original", "TensorFlow"),
         ("postgresql/postgresql-original", "PostgreSQL"), ("cplusplus/cplusplus-original", "C / C++"),
         ("tailwindcss/tailwindcss-original", "Tailwind"), ("git/git-original", "Git")]

ROLES = ["CSE Student @ MIT-WPU", "AI Product Builder", "Competitive Footballer", "Full-Stack Developer"]
TAPE_A = ["Available for internships 2026", "AI products", "Websites that convert"]
TAPE_B = ["Python", "Next.js", "FastAPI", "RAG", "PostgreSQL"]


# ---------- builders ----------
def build_titles(r: Renderer):
    css = """
    .c{height:250px;padding:40px 48px 0}
    .top{display:flex;justify-content:space-between;align-items:center}
    .top .m{font-size:13px;color:var(--muted)}
    h2{font-size:104px;margin-top:26px;white-space:nowrap}
    .rule{position:absolute;left:48px;right:48px;bottom:0;height:1px;background:var(--line)}
    .rule i{position:absolute;left:0;top:0;height:1px;width:96px;background:var(--red)}
    """
    for key, (num, label, title, side) in SECTIONS.items():
        r.png(f"title-{key}.png",
              f"<div class=c><div class=top><span class=label>({num}) {label}</span><span class=m>{side}</span></div>"
              f"<h2 class=d>{title}</h2><div class=rule><i></i></div></div>", css)


def build_about(r: Renderer):
    css = """
    .c{padding:56px 48px 52px}
    .man{font-weight:800;font-size:54px;line-height:1.08;letter-spacing:-.02em}
    .man .r{color:var(--red)}
    .row{display:flex;gap:0;margin-top:44px;border-top:1px solid var(--line)}
    .row div{flex:1;padding:20px 0 0;border-right:1px solid var(--line);padding-left:22px}
    .row div:first-child{padding-left:0}.row div:last-child{border-right:0}
    .row b{display:block;font-family:Anton;font-weight:400;font-size:44px;line-height:1}
    .row span{font-family:JBM;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
    """
    cells = [("CSE", "MIT-WPU, Pune"), ("8.45", "CGPA"), ("14", "Certificates"), ("1", "Internship"), ("8", "Projects shipped")]
    row = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in cells)
    r.png("about-manifesto.png",
          "<div class=c><p class=man>I bring the intensity of the <span class=r>pitch</span> and the discipline "
          "of the <span class=r>gym</span> into every line of code I ship.</p>"
          f"<div class=row>{row}</div></div>", css)


def build_stats(r: Renderer):
    css = """
    .c{padding:44px 48px 48px;display:grid;grid-template-columns:330px 1fr;gap:56px;align-items:center}
    .big b{font-family:Anton;font-weight:400;font-size:220px;line-height:.82;color:var(--red);display:block;margin:18px 0 6px}
    .big span{font-family:Anton;font-size:40px;text-transform:uppercase;display:block;margin-top:14px}
    .big em{font-style:normal;font-family:JBM;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
    ol{list-style:none}
    li{display:grid;grid-template-columns:200px 1fr 60px;align-items:center;gap:20px;padding:15px 0;border-bottom:1px solid var(--line)}
    li span{font-weight:700;font-size:21px}
    .bar{height:8px;background:rgba(255,255,255,.1);border-radius:4px;overflow:hidden}
    .bar i{display:block;height:100%;background:linear-gradient(90deg,#fff,var(--red));border-radius:4px}
    li b{font-family:Anton;font-weight:400;font-size:30px;text-align:right;color:var(--red)}
    """
    items = "".join(f"<li><span>{n}</span><div class=bar><i style='width:{v}%'></i></div><b>{v}</b></li>" for n, v in STATS)
    r.png("player-stats.png",
          f"<div class=c><div class=big><em>Top attribute</em><b>{STATS[0][1]}</b><span>{STATS[0][0]}</span>"
          f"<em>Playmaker · No. 18</em></div><ol>{items}</ol></div>", css)


def build_recognition(r: Renderer):
    css = """
    .c{padding:40px 48px 48px}
    .g{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line);border-left:1px solid var(--line)}
    .t{padding:30px 30px 32px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);min-height:210px;display:flex;flex-direction:column}
    .t.hot{background:var(--red)}
    .t .m{font-size:13px;color:var(--muted)}
    .t.hot .m{color:#fff;opacity:.8}
    .t h3{font-family:Anton;font-weight:400;text-transform:uppercase;font-size:46px;line-height:.95;margin:16px 0 12px}
    .t p{font-size:19px;color:rgba(255,255,255,.75);margin-top:auto}
    .t.hot p{color:#fff}
    """
    tiles = [
        ("hot", "Hackathon · 2026", "FOSSEE Hackathon", "Team leader · Open Source Hardware · IIT Bombay"),
        ("", "Internship · Jun–Aug 2026", "Gradely Consulting", "Software intern"),
        ("", "Certification", "AI &amp; Machine Learning", "Bhartiya Skill Development University, Jaipur"),
        ("", "14 certificates", "Scaler · HackerRank", "DSA in C++, Python &amp; SQL, React, SQL (Advanced)"),
    ]
    g = "".join(f"<div class='t {c}'><span class=m>{a}</span><h3>{b}</h3><p>{d}</p></div>" for c, a, b, d in tiles)
    r.png("recognition.png", f"<div class=c><div class=g>{g}</div></div>", css)


def build_projects(r: Renderer):
    css = """
    .c{padding:14px 48px}
    .card{display:grid;grid-template-columns:500px 1fr;border:1px solid var(--line);border-radius:22px;overflow:hidden;background:var(--bg2);height:330px}
    .cov{background-size:cover;background-position:top center;position:relative}
    .cov.gen{display:grid;place-items:center}
    .cov.gen span{font-family:Anton;font-size:76px;text-transform:uppercase;color:transparent;-webkit-text-stroke:2px rgba(255,255,255,.8)}
    .body{padding:30px 34px;display:flex;flex-direction:column;gap:14px}
    .row{display:flex;justify-content:space-between;align-items:center}
    .num{font-family:JBM;color:var(--red);font-size:16px}
    .meta{display:flex;gap:8px}
    h3{font-family:Anton;font-weight:400;text-transform:uppercase;font-size:62px;line-height:.95;margin-top:6px}
    p{color:rgba(255,255,255,.72);font-size:20px;line-height:1.45}
    """
    for slug, num, title, pills, desc, cover in PROJECTS:
        if cover:
            cov = f"<div class=cov style=\"background-image:url('{cover}')\"></div>"
        else:
            text, c1, c2 = GEN_COVER[slug]
            cov = (f"<div class='cov gen' style='background:radial-gradient(80% 90% at 90% 0%,{c1},transparent 60%),"
                   f"radial-gradient(70% 80% at 0% 100%,{c2},transparent 65%),#0b0b0b'><span>{text}</span></div>")
        meta = "".join(f"<span class='pill {k}'>{t}</span>" for k, t in pills)
        r.png(f"project-{slug}.png",
              f"<div class=c><div class=card>{cov}<div class=body><div class=row><span class=num>{num}</span>"
              f"<div class=meta>{meta}</div></div><h3>{title}</h3><p>{desc}</p></div></div></div>", css)


def build_toolkit(r: Renderer):
    css = """
    .c{padding:40px 48px 48px}
    .s{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}
    .s div{height:170px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;font-weight:700;font-size:19px}
    .s img{width:58px;height:58px}
    .s div.inv img{filter:invert(1)}
    """
    cells = "".join(
        f"<div class='{'inv' if 'nextjs' in ic else ''}'><img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{ic}.svg'>{n}</div>"
        for ic, n in TOOLS)
    r.png("toolkit.png", f"<div class=c><div class=s>{cells}</div></div>", css)


def build_footer(r: Renderer):
    css = """
    .c{padding:40px 48px 40px}
    .cta{font-size:250px;line-height:.82;display:flex;gap:30px;align-items:flex-end}
    .cta .o{-webkit-text-stroke:3px var(--red)}
    .f{display:flex;justify-content:space-between;margin-top:40px;padding-top:20px;border-top:1px solid var(--line);font-family:JBM;font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
    .f b{color:#fff;font-weight:600}
    """
    r.png("footer-signature.png",
          "<div class=c><span class=label>(07) Contact</span><h2 class='d cta' style='margin-top:26px'>"
          "<span>Let's</span><span class=o>talk</span></h2><div class=f><span><b>Nishad Patil</b> · Playmaking in code.</span>"
          "<span>Pune, IN · ©2026</span></div></div>", css)


def build_hero(r: Renderer, frames: int = 60):
    css = """
    .c{height:640px;padding:30px 44px 0}
    .nav{display:flex;justify-content:space-between;align-items:center}
    .brand{font-family:Anton;text-transform:uppercase;font-size:24px;letter-spacing:.02em;display:flex;align-items:center;gap:10px}
    .brand i{width:10px;height:10px;border-radius:50%;background:var(--red);display:block}
    .nav .m{font-size:13px;color:var(--muted)}
    .intro{display:flex;justify-content:space-between;align-items:flex-start;margin-top:30px}
    .intro p{max-width:330px;font-size:17px;line-height:1.45;font-weight:500}
    h1{font-size:224px;text-align:center;margin-top:22px;letter-spacing:-.005em;white-space:nowrap}
    .bot{display:flex;justify-content:space-between;align-items:flex-end;margin-top:10px}
    .roles{height:44px;overflow:hidden;font-family:Anton;text-transform:uppercase;font-size:36px;line-height:44px}
    .roles div{transform:translateY(calc(var(--ry) * -1px))}
    .roles span{display:block;height:44px;color:var(--red)}
    .bot .m{font-size:12px;color:var(--muted);text-align:right;line-height:1.7}
    .bot .m b{color:#fff;font-weight:600}
    .tapes{position:absolute;left:0;right:0;bottom:0;height:150px}
    .tape{position:absolute;left:-5%;width:110%;top:50%;display:flex;white-space:nowrap;padding:12px 0;font-family:Anton;text-transform:uppercase;font-size:34px;line-height:1}
    .tape.a{background:#fff;color:#000;transform:translateY(-50%) rotate(-3deg)}
    .tape.b{background:var(--red);color:#fff;transform:translateY(-50%) rotate(2.5deg)}
    .tape .tr{display:flex;flex-shrink:0}
    .tape span{padding:0 16px}
    """

    def tape(cls, words, var):
        seg = "".join(f"<span>{w}</span><span>✦</span>" for w in words)
        track = "".join(f"<div class=tr>{seg}</div>" for _ in range(4))
        return f"<div class='tape {cls}'><div class=tr style='transform:translateX(var({var}))'>{track}</div></div>"

    roles = "".join(f"<span>{x}</span>" for x in ROLES + ROLES[:1])
    body = (
        "<div class=c style='--ry:0;--ta:0px;--tb:0px'>"
        "<div class=nav><span class=brand><i></i>Nishad</span><span class=m>(00) Profile · Portfolio ©2026</span></div>"
        "<div class=intro><p>Playmaking in code. Dominating the pitch. CSE student at MIT-WPU building AI products and the web.</p>"
        "<span class=label>Software · Football · Fitness</span></div>"
        "<h1 class=d>Nishad Patil</h1>"
        f"<div class=bot><div class=roles><div>{roles}</div></div>"
        "<span class=m>nishadcodes18-portfolio.vercel.app<br><b>Click to kick off ↗</b></span></div>"
        f"<div class=tapes>{tape('a', TAPE_A, '--ta')}{tape('b', TAPE_B, '--tb')}</div>"
        "</div>"
    )
    r.load(page_html(body, css))
    seg_a, seg_b = r.page.evaluate(
        "[...document.querySelectorAll('.tape .tr .tr')].filter((e,i,a)=>e===e.parentNode.firstElementChild).map(e=>e.getBoundingClientRect().width)")
    el = r.page.locator(".c").first
    shots = []
    per_role = frames // len(ROLES)
    for f in range(frames):
        t = f / frames
        k, ph = divmod(f, per_role)
        slide = min(1.0, max(0.0, (ph - (per_role - 4)) / 4))  # hold, then 4-frame slide to next role
        slide = slide * slide * (3 - 2 * slide)
        r.page.evaluate(
            "([ry,ta,tb])=>{const s=document.querySelector('.c').style;s.setProperty('--ry',ry);s.setProperty('--ta',ta+'px');s.setProperty('--tb',tb+'px')}",
            [(k + slide) * 44, -seg_a * t, -seg_b * (1 - t)])
        shots.append(Image.open(BytesIO(el.screenshot())).convert("RGB"))
    # One shared palette keeps the three-colour look stable across frames.
    pal = shots[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    gif = [s.quantize(palette=pal, dither=Image.Dither.NONE) for s in shots]
    out = ASSETS / "hero.gif"
    gif[0].save(out, save_all=True, append_images=gif[1:], duration=70, loop=0, optimize=True)
    shots[0].save(ASSETS / "hero-preview.png", optimize=True)
    print(f"hero.gif: {out.stat().st_size:,} bytes, {frames} frames")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": W, "height": 900}, device_scale_factor=2)
        r = Renderer(page)
        try:
            build_titles(r)
            build_about(r)
            build_stats(r)
            build_recognition(r)
            build_projects(r)
            build_toolkit(r)
            build_footer(r)
            page.close()
            page = browser.new_page(viewport={"width": W, "height": 900}, device_scale_factor=1)
            r.page = page
            build_hero(r)
        finally:
            r.tmp.unlink(missing_ok=True)
            browser.close()


if __name__ == "__main__":
    main()
