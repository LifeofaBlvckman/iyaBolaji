#!/usr/bin/env python3
"""Generate the illustrated dish placeholders and doodle patterns in assets/.

Run from anywhere:  python3 tools/make_art.py

The dish illustrations stand in until real food photos are added. To use a
photo instead, drop it in assets/img/ and point the dish's `img` in
js/data.js at it.
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "art"
PAT = ROOT / "assets" / "patterns"

RED = "#d9151d"


def n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def smooth(pts):
    """Closed Catmull-Rom spline through pts, as an SVG path."""
    d = f"M{n(pts[0][0])} {n(pts[0][1])}"
    for i in range(len(pts)):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}"
    return d + "Z"


def blob(rng, cx, cy, rx, ry=None, pts=10, jitter=0.12, rot=0.0):
    ry = rx if ry is None else ry
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for i in range(pts):
        a = 2 * math.pi * i / pts
        k = 1 + rng.uniform(-jitter, jitter)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return smooth(out)


def in_ellipse(rng, cx, cy, rx, ry):
    while True:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y <= 1:
            return cx + x * rx, cy + y * ry, math.hypot(x, y)


DEFS = """
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>
<radialGradient id="enamel" cx="42%" cy="38%" r="65%"><stop offset="0" stop-color="#fffdf8"/><stop offset=".75" stop-color="#f7f0e3"/><stop offset="1" stop-color="#e6dac4"/></radialGradient>
<radialGradient id="well" cx="50%" cy="50%" r="50%"><stop offset=".85" stop-color="#fffaf1" stop-opacity="0"/><stop offset="1" stop-color="#d8c9ad" stop-opacity=".55"/></radialGradient>
<radialGradient id="dodo" cx="45%" cy="40%" r="60%"><stop offset="0" stop-color="#ffdc73"/><stop offset=".55" stop-color="#f5a72f"/><stop offset=".85" stop-color="#d0701c"/><stop offset="1" stop-color="#9b4710"/></radialGradient>
<linearGradient id="turkey" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e39a4c"/><stop offset=".45" stop-color="#b85b1d"/><stop offset="1" stop-color="#6a2a0b"/></linearGradient>
<radialGradient id="puff" cx="38%" cy="32%" r="70%"><stop offset="0" stop-color="#ffd27a"/><stop offset=".5" stop-color="#e09535"/><stop offset="1" stop-color="#8f4712"/></radialGradient>
<radialGradient id="amala" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#8a705c"/><stop offset=".6" stop-color="#57422f"/><stop offset="1" stop-color="#36271b"/></radialGradient>
<radialGradient id="yam" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fffef9"/><stop offset=".65" stop-color="#f1e9d6"/><stop offset="1" stop-color="#d4c6a7"/></radialGradient>
<linearGradient id="moimoi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ec8a4a"/><stop offset=".6" stop-color="#d0602b"/><stop offset="1" stop-color="#a5441a"/></linearGradient>
<linearGradient id="leaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5fae45"/><stop offset="1" stop-color="#2a6422"/></linearGradient>
<linearGradient id="chicken" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eaa54e"/><stop offset=".55" stop-color="#c26e24"/><stop offset="1" stop-color="#7d3a0e"/></linearGradient>
<linearGradient id="goat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a4a20"/><stop offset="1" stop-color="#3f1807"/></linearGradient>
"""


def svg(w, h, body, extra_defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f"<defs>{DEFS}{extra_defs}</defs>{''.join(body)}</svg>\n"
    )


# ---------------------------------------------------------------- components

def plate(cx, cy, r):
    return [
        f'<ellipse cx="{cx}" cy="{cy + r * 0.07}" rx="{r * 0.98}" ry="{r * 0.95}" fill="#2b0a05" opacity=".38" filter="url(#soft)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#enamel)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r - 9}" fill="none" stroke="{RED}" stroke-width="10"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.8}" fill="url(#well)"/>',
    ]


def shadow(cx, cy, rx, ry, opacity=0.35):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#2b0a05" opacity="{opacity}" filter="url(#soft)"/>'


def rice(rng, cx, cy, r, palette, grains=650, bits=()):
    out = [f'<path d="{blob(rng, cx, cy, r * 1.02, r * 0.95, 12, 0.07)}" fill="{palette[-1]}"/>']
    for _ in range(grains):
        x, y, d = in_ellipse(rng, cx, cy, r * 0.97, r * 0.9)
        # darker grains toward the bottom-right edge read as shading
        shade = d > 0.78 and (x - cx) + (y - cy) > 0
        col = rng.choice(palette[3:]) if shade else rng.choice(palette[:4])
        s = r / 170
        out.append(
            f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(8.5 * s)}" ry="{n(3.4 * s)}" fill="{col}" '
            f'transform="rotate({rng.randint(0, 179)} {n(x)} {n(y)})"/>'
        )
    for colour, count, size in bits:
        for _ in range(count):
            x, y, _d = in_ellipse(rng, cx, cy, r * 0.85, r * 0.8)
            out.append(f'<path d="{blob(rng, x, y, size, size * 0.7, 6, 0.3, rng.random() * 3)}" fill="{colour}"/>')
    return out


def dodo(rng, cx, cy, rx, ry, rot):
    out = [
        f'<ellipse cx="{cx + 3}" cy="{cy + 5}" rx="{rx}" ry="{ry}" fill="#5c2508" opacity=".35" transform="rotate({rot} {cx} {cy})"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#dodo)" transform="rotate({rot} {cx} {cy})"/>',
    ]
    for _ in range(3):
        x, y, _d = in_ellipse(rng, cx, cy, rx * 0.6, ry * 0.5)
        out.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx * 0.16)}" ry="{n(ry * 0.12)}" fill="#a84d12" opacity=".45"/>')
    return out


def turkey(rng, cx, cy, length, width, rot):
    a = math.radians(rot)
    out = [
        f'<path d="{blob(rng, cx + 6, cy + 9, length / 2, width / 2, 12, 0.1, a)}" fill="#3a1404" opacity=".45"/>',
        f'<path d="{blob(rng, cx, cy, length / 2, width / 2, 12, 0.1, a)}" fill="url(#turkey)" '
        f'transform="rotate(0)"/>',
    ]
    ca, sa = math.cos(a), math.sin(a)
    # crisp ridges running along the wing
    for off in (-0.22, 0.02, 0.24):
        pts = []
        for t in (-0.38, -0.12, 0.14, 0.36):
            x = t * length
            y = off * width + math.sin(t * 6 + off * 9) * width * 0.05
            pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
        d = f"M{n(pts[0][0])} {n(pts[0][1])}C{n(pts[1][0])} {n(pts[1][1])} {n(pts[2][0])} {n(pts[2][1])} {n(pts[3][0])} {n(pts[3][1])}"
        out.append(f'<path d="{d}" fill="none" stroke="#f6be7c" stroke-opacity=".5" stroke-width="{n(width * 0.06)}" stroke-linecap="round"/>')
    for _ in range(9):
        x, y, _d = in_ellipse(rng, cx, cy, length * 0.4, width * 0.35)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(2, 5))}" fill="#3d1505" opacity=".55"/>')
    for _ in range(10):
        x, y, _d = in_ellipse(rng, cx, cy, length * 0.42, width * 0.36)
        out.append(f'<path d="{blob(rng, x, y, 6, 3.5, 6, 0.3, rng.random() * 3)}" fill="{rng.choice(["#d22a14", "#b01a0c", "#e9561f"])}"/>')
    return out


def sauce(rng, cx, cy, rx, ry):
    out = [
        f'<path d="{blob(rng, cx, cy, rx, ry, 14, 0.08)}" fill="#9e1a0f"/>',
        f'<path d="{blob(rng, cx - rx * 0.05, cy - ry * 0.05, rx * 0.85, ry * 0.82, 12, 0.1)}" fill="#c4321a" opacity=".85"/>',
    ]
    for _ in range(14):
        x, y, _d = in_ellipse(rng, cx, cy, rx * 0.8, ry * 0.8)
        out.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rng.uniform(8, 22))}" ry="{n(rng.uniform(3, 7))}" fill="#f2862f" opacity=".35"/>')
    for _ in range(40):
        x, y, _d = in_ellipse(rng, cx, cy, rx * 0.9, ry * 0.88)
        out.append(f'<path d="{blob(rng, x, y, rng.uniform(3, 7), rng.uniform(2, 4), 6, 0.3, rng.random() * 3)}" fill="{rng.choice(["#7d120a", "#e2531f", "#f3c48a"])}"/>')
    return out


def fish(rng, cx, cy, w, h, rot):
    out = [f'<g transform="rotate({rot} {cx} {cy})">']
    out.append(f'<path d="{blob(rng, cx + 5, cy + 8, w / 2, h / 2, 10, 0.08)}" fill="#3a0d06" opacity=".4"/>')
    out.append(f'<path d="{blob(rng, cx, cy, w / 2, h / 2, 10, 0.08)}" fill="#68707a"/>')
    out.append(f'<path d="{blob(rng, cx, cy + h * 0.14, w * 0.47, h * 0.36, 10, 0.08)}" fill="#ecd9bc"/>')
    for i in range(4):
        x = cx - w * 0.35 + i * w * 0.22
        out.append(f'<path d="M{n(x)} {n(cy - h * 0.38)}q{n(w * 0.05)} {n(h * 0.12)} 0 {n(h * 0.24)}" fill="none" stroke="#2f343b" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    out.append(f'<ellipse cx="{n(cx - w * 0.1)}" cy="{n(cy - h * 0.3)}" rx="{n(w * 0.25)}" ry="{n(h * 0.05)}" fill="#dfe6ee" opacity=".55"/>')
    for _ in range(7):
        x, y, _d = in_ellipse(rng, cx, cy + h * 0.1, w * 0.42, h * 0.3)
        out.append(f'<path d="{blob(rng, x, y, rng.uniform(9, 18), rng.uniform(6, 11), 7, 0.3, rng.random() * 3)}" fill="{rng.choice(["#c42a1a", "#d8401d", "#a8170d"])}" opacity=".92"/>')
    out.append("</g>")
    return out


def puff(rng, cx, cy, r):
    out = [
        f'<circle cx="{cx + 4}" cy="{cy + 7}" r="{r}" fill="#3d1a05" opacity=".35"/>',
        f'<path d="{blob(rng, cx, cy, r, r * 0.96, 9, 0.05)}" fill="url(#puff)"/>',
    ]
    for _ in range(14):
        x, y, _d = in_ellipse(rng, cx - r * 0.1, cy - r * 0.15, r * 0.65, r * 0.6)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1.4, 2.8))}" fill="#fffaf0" opacity=".85"/>')
    return out


def goat(rng, cx, cy, r):
    out = [
        f'<path d="{blob(rng, cx + 4, cy + 6, r, r * 0.8, 7, 0.25, rng.random() * 3)}" fill="#200a02" opacity=".45"/>',
        f'<path d="{blob(rng, cx, cy, r, r * 0.8, 7, 0.25, rng.random() * 3)}" fill="url(#goat)"/>',
        f'<ellipse cx="{n(cx - r * 0.25)}" cy="{n(cy - r * 0.3)}" rx="{n(r * 0.35)}" ry="{n(r * 0.12)}" fill="#e28a4a" opacity=".45"/>',
    ]
    return out


def onion(cx, cy, r, rot):
    return [f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.6}" fill="none" stroke="#f6e7f2" stroke-width="5" transform="rotate({rot} {cx} {cy})"/>',
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.6}" fill="none" stroke="#b57bb0" stroke-width="1.5" opacity=".6" transform="rotate({rot} {cx} {cy})"/>']


def pepper_strip(cx, cy, length, rot, colour):
    return f'<rect x="{cx - length / 2}" y="{cy - 5}" width="{length}" height="10" rx="5" fill="{colour}" transform="rotate({rot} {cx} {cy})"/>'


def drumstick(rng, cx, cy, size, rot):
    out = [f'<g transform="rotate({rot} {cx} {cy})">']
    out.append(f'<rect x="{cx + size * 0.45}" y="{cy - size * 0.08}" width="{size * 0.55}" height="{size * 0.16}" rx="{size * 0.08}" fill="#efe2c9"/>')
    out.append(f'<circle cx="{cx + size}" cy="{cy - size * 0.1}" r="{size * 0.11}" fill="#f5ead6"/><circle cx="{cx + size}" cy="{cy + size * 0.1}" r="{size * 0.11}" fill="#f5ead6"/>')
    out.append(f'<path d="{blob(rng, cx + 5, cy + 8, size * 0.62, size * 0.42, 11, 0.12)}" fill="#3a1404" opacity=".4"/>')
    out.append(f'<path d="{blob(rng, cx, cy, size * 0.62, size * 0.42, 11, 0.12)}" fill="url(#chicken)"/>')
    for _ in range(60):
        x, y, _d = in_ellipse(rng, cx, cy, size * 0.55, size * 0.36)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(2, 6))}" fill="{rng.choice(["#f2b968", "#a4561a", "#d98a39"])}" opacity=".75"/>')
    out.append("</g>")
    return out


# ---------------------------------------------------------------- dishes

JOLLOF = ["#f6a75a", "#f39243", "#ef7a32", "#e4632a", "#d9531f", "#c94a1a", "#b8401a"]
FRIED = ["#f5dd94", "#f0d27a", "#e9c766", "#dcb24e", "#cfa443", "#bf9236", "#b0852e"]
GARNISH = (("#3f8a2f", 14, 6), ("#e8331c", 10, 5), ("#f3e3c4", 8, 5))


def jollof_combo():
    rng = random.Random(7)
    b = plate(300, 300, 280)
    b += rice(rng, 250, 300, 170, JOLLOF, 700, GARNISH)
    b += turkey(rng, 395, 235, 250, 118, -58)
    for cx, cy, rot in ((360, 430, 20), (420, 405, -15), (465, 350, 40), (395, 470, -30)):
        b += dodo(rng, cx, cy, 44, 28, rot)
    return svg(600, 600, b)


def peppered_turkey():
    rng = random.Random(11)
    b = plate(300, 300, 280)
    b += turkey(rng, 225, 285, 270, 120, -62)
    b += turkey(rng, 330, 275, 280, 124, -70)
    b += turkey(rng, 410, 330, 240, 110, -52)
    for cx, cy, r, rot in ((170, 430, 22, 20), (430, 180, 20, -30), (300, 450, 18, 60)):
        b += onion(cx, cy, r, rot)
    b += [pepper_strip(210, 160, 46, 30, "#3f8a2f"), pepper_strip(450, 440, 40, -40, "#e8331c")]
    return svg(600, 600, b)


def fish_stew():
    rng = random.Random(23)
    b = plate(300, 300, 280)
    b += sauce(rng, 300, 300, 215, 210)
    b += fish(rng, 225, 230, 170, 110, -20)
    b += fish(rng, 370, 240, 160, 104, 25)
    b += fish(rng, 240, 380, 160, 104, 15)
    b += fish(rng, 385, 385, 150, 100, -30)
    return svg(600, 600, b)


def dodo_plate():
    rng = random.Random(5)
    b = plate(300, 300, 280)
    spots = [(300, 300, 0)] + [(300 + 120 * math.cos(a), 300 + 115 * math.sin(a), math.degrees(a) + 90) for a in [i * math.pi / 4 for i in range(8)]]
    spots += [(300 + 60 * math.cos(a), 300 + 58 * math.sin(a), math.degrees(a)) for a in [i * math.pi / 2 + 0.5 for i in range(4)]]
    for cx, cy, rot in spots:
        b += dodo(rng, round(cx), round(cy), 58, 36, round(rot))
    return svg(600, 600, b)


def amala_abula():
    rng = random.Random(31)
    b = plate(300, 300, 280)
    b.append(f'<path d="{blob(rng, 380, 330, 160, 150, 12, 0.08)}" fill="#3f6e25"/>')
    for _ in range(260):
        x, y, _d = in_ellipse(rng, 380, 330, 150, 140)
        b.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1.5, 3.5))}" fill="{rng.choice(["#2b5417", "#5f9439", "#76a84a"])}"/>')
    b.append(f'<path d="{blob(rng, 430, 400, 95, 80, 10, 0.12)}" fill="#dba140"/>')
    for _ in range(60):
        x, y, _d = in_ellipse(rng, 430, 400, 85, 70)
        b.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1.5, 3))}" fill="#bf8a2a"/>')
    b += sauce(rng, 350, 200, 90, 60)
    b.append(shadow(205, 300, 125, 120, 0.4))
    b.append(f'<path d="{blob(rng, 200, 290, 125, 118, 10, 0.05)}" fill="url(#amala)"/>')
    b.append(f'<ellipse cx="170" cy="250" rx="45" ry="22" fill="#a8907c" opacity=".35"/>')
    b += goat(rng, 330, 195, 34) + goat(rng, 395, 215, 30)
    return svg(600, 600, b)


def yam_egusi():
    rng = random.Random(41)
    b = plate(300, 300, 280)
    b.append(f'<path d="{blob(rng, 360, 340, 170, 155, 12, 0.1)}" fill="#c99a3a"/>')
    for _ in range(180):
        x, y, _d = in_ellipse(rng, 360, 340, 160, 145)
        b.append(f'<path d="{blob(rng, x, y, rng.uniform(5, 12), rng.uniform(4, 9), 6, 0.35, rng.random() * 3)}" fill="{rng.choice(["#e8c35e", "#d7aa45", "#f0d27c"])}"/>')
    for _ in range(45):
        x, y, _d = in_ellipse(rng, 360, 340, 150, 135)
        b.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rng.uniform(8, 16))}" ry="{n(rng.uniform(4, 7))}" fill="{rng.choice(["#2f6b2f", "#3f8a3a", "#245a24"])}" transform="rotate({rng.randint(0, 179)} {n(x)} {n(y)})"/>')
    for _ in range(14):
        x, y, _d = in_ellipse(rng, 360, 340, 150, 135)
        b.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rng.uniform(10, 20))}" ry="{n(rng.uniform(3, 6))}" fill="#e2541c" opacity=".45"/>')
    b += goat(rng, 420, 300, 34) + goat(rng, 370, 420, 30) + goat(rng, 455, 400, 26)
    b.append(shadow(210, 255, 120, 112, 0.35))
    b.append(f'<path d="{blob(rng, 205, 245, 122, 115, 10, 0.05)}" fill="url(#yam)"/>')
    b.append(f'<ellipse cx="175" cy="205" rx="48" ry="20" fill="#ffffff" opacity=".6"/>')
    return svg(600, 600, b)


def fried_rice():
    rng = random.Random(53)
    b = plate(300, 300, 280)
    b += rice(rng, 260, 300, 175, FRIED, 650, (("#5a9a2e", 40, 5), ("#f07a24", 40, 5), ("#f3e3c4", 10, 5)))
    b += drumstick(rng, 360, 250, 150, -35)
    b += dodo(rng, 410, 420, 44, 28, 25) + dodo(rng, 350, 455, 44, 28, -10)
    return svg(600, 600, b)


def asun_rice():
    rng = random.Random(61)
    b = plate(300, 300, 280)
    b += rice(rng, 300, 300, 200, FRIED, 800, (("#5a9a2e", 40, 5), ("#f07a24", 40, 5)))
    for cx, cy, r in ((260, 250, 40), (330, 230, 36), (300, 310, 42), (370, 300, 34), (240, 340, 32), (340, 370, 36)):
        b += goat(rng, cx, cy, r)
    for cx, cy, rot in ((280, 280, 30), (350, 340, -20), (230, 300, 70)):
        b.append(pepper_strip(cx, cy, 50, rot, rng.choice(["#e8331c", "#3f8a2f"])))
    b += onion(320, 270, 20, 15) + onion(270, 360, 18, -25)
    return svg(600, 600, b)


def moi_moi():
    rng = random.Random(71)
    b = plate(300, 300, 280)
    leaf = "M90 360 C140 190 330 110 520 170 C470 330 280 430 90 360Z"
    b.append(f'<path d="{leaf}" fill="url(#leaf)"/>')
    b.append('<path d="M95 358 C230 300 380 220 515 172" fill="none" stroke="#9fd17e" stroke-width="4" opacity=".7"/>')
    for t in range(1, 8):
        x, y = 95 + t * 52, 358 - t * 25
        b.append(f'<path d="M{x} {y} l-20 -40 M{x} {y} l30 30" stroke="#9fd17e" stroke-width="2" opacity=".5"/>')
    b.append(shadow(300, 300, 150, 90, 0.45))
    b.append(f'<path d="{blob(rng, 300, 290, 150, 92, 12, 0.05, -0.32)}" fill="url(#moimoi)"/>')
    b.append('<ellipse cx="300" cy="290" rx="48" ry="32" fill="#fff8ea" transform="rotate(-18 300 290)"/>')
    b.append('<ellipse cx="302" cy="290" rx="24" ry="17" fill="#f6b72e" transform="rotate(-18 300 290)"/>')
    b.append('<ellipse cx="240" cy="250" rx="60" ry="14" fill="#ffd0a0" opacity=".45" transform="rotate(-18 240 250)"/>')
    for _ in range(30):
        x, y, _d = in_ellipse(rng, 300, 290, 130, 75)
        b.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1.5, 3))}" fill="#9b3d14" opacity=".6"/>')
    return svg(600, 600, b)


def puff_puff():
    rng = random.Random(83)
    b = plate(300, 300, 280)
    balls = [(220, 210), (320, 190), (410, 240), (180, 310), (290, 290), (400, 340), (230, 400), (330, 400), (300, 220)]
    for cx, cy in sorted(balls, key=lambda p: p[1]):
        b += puff(rng, cx, cy, 68)
    return svg(600, 600, b)


def zobo():
    w, h = 420, 620
    extra = """
<linearGradient id="zobo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c22c45"/><stop offset=".35" stop-color="#8f1730"/><stop offset="1" stop-color="#4f0814"/></linearGradient>
<pattern id="stripe" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="24" height="24" fill="#fffaf2"/><rect width="12" height="24" fill="#d9151d"/></pattern>
"""
    glass = "M80 150 L340 150 L312 560 Q310 590 280 590 L140 590 Q110 590 108 560 Z"
    liquid = "M86 210 L334 210 L312 556 Q310 582 282 582 L138 582 Q112 582 110 556 Z"
    b = [
        shadow(210, 590, 150, 22, 0.45),
        '<rect x="232" y="20" width="26" height="420" rx="13" fill="url(#stripe)" transform="rotate(14 245 230)"/>',
        f'<path d="{glass}" fill="#fff" opacity=".18"/>',
        f'<path d="{liquid}" fill="url(#zobo)"/>',
        '<rect x="120" y="230" width="70" height="62" rx="14" fill="#fff" opacity=".22" stroke="#fff" stroke-opacity=".45" stroke-width="3" transform="rotate(-12 155 261)"/>',
        '<rect x="205" y="225" width="64" height="58" rx="14" fill="#fff" opacity=".2" stroke="#fff" stroke-opacity=".45" stroke-width="3" transform="rotate(10 237 254)"/>',
        '<rect x="160" y="292" width="58" height="52" rx="12" fill="#fff" opacity=".16" stroke="#fff" stroke-opacity=".35" stroke-width="3" transform="rotate(20 189 318)"/>',
        '<rect x="104" y="180" width="22" height="370" rx="11" fill="#fff" opacity=".28"/>',
        f'<path d="{glass}" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="5"/>',
        '<ellipse cx="210" cy="150" rx="130" ry="16" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="5"/>',
        # orange slice on the rim
        '<g transform="rotate(-18 320 140)"><path d="M250 140 A70 70 0 0 1 390 140 Z" fill="#f6a12a"/><path d="M262 140 A58 58 0 0 1 378 140 Z" fill="#ffd36a"/>'
        '<path d="M320 140 L270 108 M320 140 L292 88 M320 140 L320 82 M320 140 L348 88 M320 140 L370 108" stroke="#f6a12a" stroke-width="4"/></g>',
        '<path d="M150 150 C120 110 140 80 170 92 C178 120 168 140 150 150Z" fill="#3f8a3a"/>',
        '<path d="M150 150 C150 110 190 90 210 110 C200 135 175 150 150 150Z" fill="#5fae45"/>',
    ]
    return svg(w, h, b, extra)


def pepper_pot():
    """Wide hero image for the 'why it tastes like home' section."""
    rng = random.Random(97)
    w, h = 760, 520
    extra = '<radialGradient id="bg" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#5a160c"/><stop offset="1" stop-color="#1c0603"/></radialGradient>'
    b = [f'<rect width="{w}" height="{h}" fill="url(#bg)"/>',
         '<circle cx="380" cy="270" r="250" fill="#0d0d0d"/>',
         '<circle cx="380" cy="270" r="236" fill="#2a2a2a"/>',
         '<circle cx="380" cy="270" r="222" fill="#141414"/>']
    b += sauce(rng, 380, 270, 205, 205)
    for _ in range(26):
        x, y, _d = in_ellipse(rng, 380, 270, 180, 180)
        r = rng.uniform(6, 20)
        b.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#d8481f" stroke="#f6a35a" stroke-opacity=".7" stroke-width="2"/>')
        b.append(f'<circle cx="{n(x - r * 0.3)}" cy="{n(y - r * 0.3)}" r="{n(r * 0.25)}" fill="#ffe1b8" opacity=".7"/>')
    b += fish(rng, 330, 250, 150, 96, -15) + fish(rng, 450, 320, 140, 92, 30)
    b.append('<path d="M560 60 L700 -30" stroke="#a8743f" stroke-width="26" stroke-linecap="round"/>')
    b.append('<ellipse cx="530" cy="95" rx="52" ry="34" fill="#c08a52" transform="rotate(-33 530 95)"/>')
    for i in range(4):
        x = 230 + i * 90
        b.append(f'<path d="M{x} 40 q-18 -24 0 -48 q18 -24 0 -48" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="10" stroke-linecap="round"/>')
    return svg(w, h, b, extra)


# ---------------------------------------------------------------- patterns

ICONS = {
    "pot": "M-16 -6H16V9Q16 16 9 16H-9Q-16 16-16 9ZM-19 -6H19M-4 -11H4M-16 1H-22M16 1H22",
    "bowl": "M-19 -1H19A19 16 0 0 1-19 -1ZM-7 15H7M-6 -7Q-10 -12-6 -17M6 -7Q2 -12 6 -17",
    "chili": "M-14 9C-3 13 10 5 13 -8C6 -1-3 2-13 3ZM13 -8Q14 -13 18 -15",
    "cup": "M-11 -12H11L8 16H-8ZM-13 -12H13M3 -12L7 -24H13",
    "plantain": "M-17 4C-8 14 10 12 17 -6C9 2-6 4-17 4ZM17 -6L20 -10",
    "star": "M0-15L4.4-6 14.3-4.6 7.1 2.4 8.8 12.1 0 7.5-8.8 12.1-7.1 2.4-14.3-4.6-4.4-6Z",
    "sparkle": "M0-14Q2-2 14 0Q2 2 0 14Q-2 2-14 0Q-2-2 0-14Z",
    "squiggle": "M-15 0Q-11 -6-7 0T1 0 9 0 17 0",
}

LAYOUT = [
    ("pot", 30, 34, -12), ("star", 98, 28, 8), ("cup", 170, 40, 10), ("sparkle", 232, 22, 0),
    ("chili", 62, 98, 20), ("squiggle", 140, 102, -8), ("bowl", 210, 112, 6),
    ("sparkle", 22, 160, 0), ("plantain", 104, 166, -18), ("star", 176, 176, -10),
    ("cup", 240, 200, -8), ("bowl", 40, 228, -6), ("sparkle", 128, 236, 0), ("chili", 196, 248, -24),
]


def pattern(stroke, opacity=1.0):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" width="260" height="260">'
             f'<g fill="none" stroke="{stroke}" stroke-opacity="{opacity}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">']
    for name, x, y, rot in LAYOUT:
        parts.append(f'<path transform="translate({x} {y}) rotate({rot})" d="{ICONS[name]}"/>')
    parts.append("</g></svg>\n")
    return "".join(parts)


def main():
    ART.mkdir(parents=True, exist_ok=True)
    PAT.mkdir(parents=True, exist_ok=True)
    dishes = {
        "jollof-combo": jollof_combo, "peppered-turkey": peppered_turkey, "fish-stew": fish_stew,
        "dodo": dodo_plate, "amala-abula": amala_abula, "yam-egusi": yam_egusi,
        "fried-rice": fried_rice, "asun-rice": asun_rice, "moi-moi": moi_moi,
        "puff-puff": puff_puff, "zobo": zobo, "pepper-pot": pepper_pot,
    }
    for name, fn in dishes.items():
        (ART / f"{name}.svg").write_text(fn())
    (PAT / "on-red.svg").write_text(pattern("#ff6a6f", 0.42))
    (PAT / "on-cream.svg").write_text(pattern("#e9c49c", 0.55))
    (PAT / "band.svg").write_text(pattern("#fdf0dc", 0.95))
    print(f"wrote {len(dishes)} dishes and 3 patterns")


if __name__ == "__main__":
    main()
