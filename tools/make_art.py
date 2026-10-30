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
<radialGradient id="eba" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fff1b8"/><stop offset=".6" stop-color="#ecc75e"/><stop offset="1" stop-color="#c99a32"/></radialGradient>
<radialGradient id="fufu" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffffff"/><stop offset=".65" stop-color="#ece6d8"/><stop offset="1" stop-color="#c9c0ab"/></radialGradient>
<radialGradient id="semo" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fffaf0"/><stop offset=".6" stop-color="#efe0bd"/><stop offset="1" stop-color="#cdb486"/></radialGradient>
<linearGradient id="ponmo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0c48c"/><stop offset="1" stop-color="#b9783f"/></linearGradient>
<radialGradient id="liver" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#8e3a2c"/><stop offset="1" stop-color="#3d0f0a"/></radialGradient>
<radialGradient id="bokoto" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#f6d7a6"/><stop offset=".6" stop-color="#d9a066"/><stop offset="1" stop-color="#a5622c"/></radialGradient>
<linearGradient id="yamcube" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe7a0"/><stop offset="1" stop-color="#e3a43a"/></linearGradient>
<linearGradient id="croaker" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8b86e"/><stop offset=".5" stop-color="#b8742f"/><stop offset="1" stop-color="#6c3812"/></linearGradient>
<linearGradient id="fry" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe08a"/><stop offset="1" stop-color="#e2a13a"/></linearGradient>
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


def rice(rng, cx, cy, r, palette, grains=650, bits=(), length=1.0):
    out = [f'<path d="{blob(rng, cx, cy, r * 1.02, r * 0.95, 12, 0.07)}" fill="{palette[-1]}"/>']
    for _ in range(grains):
        x, y, d = in_ellipse(rng, cx, cy, r * 0.97, r * 0.9)
        # darker grains toward the bottom-right edge read as shading
        shade = d > 0.78 and (x - cx) + (y - cy) > 0
        col = rng.choice(palette[3:]) if shade else rng.choice(palette[:4])
        s = r / 170
        out.append(
            f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(8.5 * s * length)}" ry="{n(3.4 * s)}" fill="{col}" '
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
        f'<path d="{blob(rng, cx, cy, length / 2, width / 2, 12, 0.1, a)}" fill="url(#turkey)"/>',
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


# ---------------------------------------------------------------- more components

def dome(rng, cx, cy, r, grad, speck="#000"):
    """A wrap of swallow (eba, fufu, semo, amala) seen from above."""
    out = [
        shadow(cx + 4, cy + 10, r, r * 0.95, 0.4),
        f'<path d="{blob(rng, cx, cy, r, r * 0.95, 10, 0.05)}" fill="url(#{grad})"/>',
        f'<ellipse cx="{n(cx - r * 0.3)}" cy="{n(cy - r * 0.36)}" rx="{n(r * 0.38)}" ry="{n(r * 0.15)}" fill="#fff" opacity=".5" transform="rotate(-22 {n(cx - r * 0.3)} {n(cy - r * 0.36)})"/>',
    ]
    for _ in range(int(r * 0.5)):
        x, y, _d = in_ellipse(rng, cx, cy, r * 0.85, r * 0.8)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1, 2.2))}" fill="{speck}" opacity=".25"/>')
    return out


def egg(cx, cy, r, rot=0):
    return [
        f'<ellipse cx="{cx + 3}" cy="{cy + 6}" rx="{r}" ry="{n(r * 0.78)}" fill="#3a1404" opacity=".3" transform="rotate({rot} {cx} {cy})"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{n(r * 0.78)}" fill="#fffaf0" transform="rotate({rot} {cx} {cy})"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{n(r * 0.42)}" fill="#f2ae25"/>',
        f'<circle cx="{n(cx - r * 0.12)}" cy="{n(cy - r * 0.12)}" r="{n(r * 0.16)}" fill="#ffd56a"/>',
    ]


def glaze(rng, cx, cy, rx, ry, dabs=6):
    """Red pepper sauce dabs and flecks over a piece of meat or fish."""
    out = []
    for _ in range(dabs):
        x, y, _d = in_ellipse(rng, cx, cy, rx, ry)
        out.append(f'<path d="{blob(rng, x, y, rng.uniform(6, 13), rng.uniform(4, 8), 7, 0.3, rng.random() * 3)}" fill="{rng.choice(["#c42a1a", "#d8401d", "#a8170d"])}" opacity=".9"/>')
    for _ in range(dabs):
        x, y, _d = in_ellipse(rng, cx, cy, rx, ry)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(1.5, 3))}" fill="{rng.choice(["#f3c48a", "#7d120a", "#3f8a2f"])}"/>')
    return out


def beef(rng, cx, cy, r):
    return goat(rng, cx, cy, r) + glaze(rng, cx, cy, r * 0.7, r * 0.5, 4)


def ponmo(rng, cx, cy, w, h, rot):
    return [
        f'<g transform="rotate({rot} {cx} {cy})">',
        f'<rect x="{n(cx - w / 2 + 4)}" y="{n(cy - h / 2 + 6)}" width="{w}" height="{h}" rx="{n(h / 2)}" fill="#3a1404" opacity=".35"/>',
        f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{w}" height="{h}" rx="{n(h / 2)}" fill="url(#ponmo)"/>',
        f'<path d="M{n(cx - w * 0.34)} {cy}H{n(cx + w * 0.34)}" stroke="#9c5f2c" stroke-width="{n(h * 0.16)}" stroke-linecap="round" opacity=".5"/>',
        *glaze(rng, cx, cy, w * 0.4, h * 0.35, 3),
        "</g>",
    ]


def shaki(rng, cx, cy, r):
    out = [
        f'<path d="{blob(rng, cx + 4, cy + 6, r, r * 0.75, 8, 0.2)}" fill="#3a1404" opacity=".3"/>',
        f'<path d="{blob(rng, cx, cy, r, r * 0.75, 8, 0.2, rng.random() * 3)}" fill="#d6c3a2"/>',
    ]
    for _ in range(int(r * 0.7)):
        x, y, _d = in_ellipse(rng, cx, cy, r * 0.75, r * 0.5)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rng.uniform(2.5, 4.5))}" fill="none" stroke="#a48b66" stroke-width="1.6"/>')
    return out + glaze(rng, cx, cy, r * 0.6, r * 0.4, 3)


def liver(rng, cx, cy, r):
    return [
        f'<path d="{blob(rng, cx + 4, cy + 6, r, r * 0.7, 8, 0.15)}" fill="#200a02" opacity=".35"/>',
        f'<path d="{blob(rng, cx, cy, r, r * 0.7, 8, 0.15, rng.random() * 3)}" fill="url(#liver)"/>',
        f'<ellipse cx="{n(cx - r * 0.25)}" cy="{n(cy - r * 0.25)}" rx="{n(r * 0.35)}" ry="{n(r * 0.12)}" fill="#d07a64" opacity=".45"/>',
    ] + glaze(rng, cx, cy, r * 0.6, r * 0.4, 2)


def roundabout(rng, cx, cy, r):
    return [
        f'<circle cx="{cx + 4}" cy="{cy + 6}" r="{r}" fill="none" stroke="#3a1404" stroke-opacity=".3" stroke-width="{n(r * 0.6)}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e9cda4" stroke-width="{n(r * 0.6)}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{n(r * 1.18)}" fill="none" stroke="#c49a6b" stroke-width="2"/>',
    ] + glaze(rng, cx, cy, r, r, 2)


def bokoto_piece(rng, cx, cy, r):
    return [
        f'<path d="{blob(rng, cx + 4, cy + 7, r, r * 0.85, 9, 0.18)}" fill="#3a1404" opacity=".35"/>',
        f'<path d="{blob(rng, cx, cy, r, r * 0.85, 9, 0.18, rng.random() * 3)}" fill="url(#bokoto)"/>',
        f'<circle cx="{n(cx + r * 0.22)}" cy="{n(cy - r * 0.1)}" r="{n(r * 0.3)}" fill="#fbf3e1"/>',
        f'<circle cx="{n(cx + r * 0.22)}" cy="{n(cy - r * 0.1)}" r="{n(r * 0.13)}" fill="#c98a5a"/>',
    ] + glaze(rng, cx, cy, r * 0.7, r * 0.6, 5)


def noodles(rng, cx, cy, r, strands=120):
    out = [f'<path d="{blob(rng, cx, cy, r, r * 0.92, 12, 0.08)}" fill="#c98d3c"/>']
    for _ in range(strands):
        x, y, _d = in_ellipse(rng, cx, cy, r * 0.82, r * 0.78)
        a, length = rng.uniform(0, 6.28), rng.uniform(30, 70)
        x2, y2 = x + math.cos(a) * length, y + math.sin(a) * length
        mx, my = (x + x2) / 2 + rng.uniform(-25, 25), (y + y2) / 2 + rng.uniform(-25, 25)
        out.append(f'<path d="M{n(x)} {n(y)}Q{n(mx)} {n(my)} {n(x2)} {n(y2)}" fill="none" stroke="{rng.choice(["#f2c978", "#e9b860", "#dca04a", "#c98a37"])}" stroke-width="5" stroke-linecap="round"/>')
    return out


def slaw(rng, cx, cy, r):
    out = [f'<path d="{blob(rng, cx, cy, r, r * 0.9, 12, 0.1)}" fill="#eef1da"/>']
    for colours, count in ((["#f7f8ea", "#dfe9c2", "#cfe0a8", "#ffffff"], 260), (["#f08a2c", "#f6a24a"], 60)):
        for _ in range(count):
            x, y, _d = in_ellipse(rng, cx, cy, r * 0.9, r * 0.82)
            a, length = rng.uniform(0, 3.14), rng.uniform(12, 30)
            out.append(f'<path d="M{n(x)} {n(y)}l{n(math.cos(a) * length)} {n(math.sin(a) * length)}" stroke="{rng.choice(colours)}" stroke-width="3.2" stroke-linecap="round"/>')
    return out


def fries(rng, cx, cy, rx, ry, count=26):
    out = []
    for _ in range(count):
        x, y, _d = in_ellipse(rng, cx, cy, rx, ry)
        length, rot = rng.uniform(60, 95), rng.randint(0, 179)
        out.append(f'<rect x="{n(x - length / 2)}" y="{n(y - 7)}" width="{n(length)}" height="14" rx="5" fill="url(#fry)" stroke="#c98a2e" stroke-width="1" transform="rotate({rot} {n(x)} {n(y)})"/>')
    return out


def croaker(rng, cx, cy, length, rot):
    h = length * 0.3
    L = length
    body = (f"M{n(-L * 0.5)} 0C{n(-L * 0.38)} {n(-h)} {n(L * 0.15)} {n(-h * 1.05)} {n(L * 0.3)} {n(-h * 0.15)}"
            f"L{n(L * 0.5)} {n(-h * 0.7)}Q{n(L * 0.43)} 0 {n(L * 0.5)} {n(h * 0.7)}L{n(L * 0.3)} {n(h * 0.15)}"
            f"C{n(L * 0.15)} {n(h * 1.05)} {n(-L * 0.38)} {n(h)} {n(-L * 0.5)} 0Z")
    out = [f'<g transform="translate({cx} {cy}) rotate({rot})">',
           f'<path d="{body}" fill="#3a1404" opacity=".35" transform="translate(6 9)"/>',
           f'<path d="{body}" fill="url(#croaker)"/>']
    for i in range(4):
        x = -L * 0.2 + i * L * 0.11
        out.append(f'<path d="M{n(x)} {n(-h * 0.6)}q{n(L * 0.04)} {n(h * 0.6)} 0 {n(h * 1.2)}" fill="none" stroke="#5a2a0c" stroke-width="5" stroke-linecap="round" opacity=".7"/>')
    out.append(f'<circle cx="{n(-L * 0.36)}" cy="{n(-h * 0.18)}" r="{n(L * 0.03)}" fill="#fff8e8"/>')
    out.append(f'<circle cx="{n(-L * 0.36)}" cy="{n(-h * 0.18)}" r="{n(L * 0.014)}" fill="#141211"/>')
    out += glaze(rng, 0, 0, L * 0.3, h * 0.5, 8)
    out.append("</g>")
    return out


def yam_chunks(rng, cx, cy, rx, ry, count=12):
    out = []
    for _ in range(count):
        x, y, _d = in_ellipse(rng, cx, cy, rx, ry)
        s, rot = rng.uniform(30, 44), rng.randint(0, 89)
        out.append(f'<rect x="{n(x - s / 2 + 3)}" y="{n(y - s / 2 + 5)}" width="{n(s)}" height="{n(s)}" rx="9" fill="#5a1d06" opacity=".35" transform="rotate({rot} {n(x)} {n(y)})"/>')
        out.append(f'<rect x="{n(x - s / 2)}" y="{n(y - s / 2)}" width="{n(s)}" height="{n(s)}" rx="9" fill="url(#yamcube)" transform="rotate({rot} {n(x)} {n(y)})"/>')
    return out


def soup(rng, cx, cy, r, base, specks, oil=True):
    out = [f'<path d="{blob(rng, cx, cy, r, r * 0.95, 14, 0.06)}" fill="{base}"/>']
    for colours, count, lo, hi in specks:
        for _ in range(count):
            x, y, _d = in_ellipse(rng, cx, cy, r * 0.9, r * 0.85)
            size = rng.uniform(lo, hi)
            out.append(f'<path d="{blob(rng, x, y, size, size * 0.7, 6, 0.35, rng.random() * 3)}" fill="{rng.choice(colours)}"/>')
    if oil:
        for _ in range(12):
            x, y, _d = in_ellipse(rng, cx, cy, r * 0.85, r * 0.8)
            out.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rng.uniform(10, 22))}" ry="{n(rng.uniform(3, 6))}" fill="#e2541c" opacity=".45"/>')
    return out


EGUSI = [(["#e8c35e", "#d7aa45", "#f0d27c"], 170, 5, 12), (["#2f6b2f", "#3f8a3a"], 45, 6, 12)]
EFO = [(["#3f7a26", "#24481a", "#5b8f33"], 240, 5, 12), (["#c42a1a", "#e2531f"], 45, 3, 6)]
EWEDU = [(["#2b5417", "#5f9439", "#76a84a"], 260, 1.5, 3.5)]


# ---------------------------------------------------------------- dishes

JOLLOF = ["#f6a75a", "#f39243", "#ef7a32", "#e4632a", "#d9531f", "#c94a1a", "#b8401a"]
FRIED = ["#f5dd94", "#f0d27a", "#e9c766", "#dcb24e", "#cfa443", "#bf9236", "#b0852e"]
WHITE = ["#ffffff", "#fdfaf3", "#f7f1e4", "#efe7d6", "#e6dcc6", "#dacdb2", "#cdbf9f"]
OFADA = ["#f3e8d2", "#e9dcc0", "#dcc9a5", "#cdb48a", "#b99a6c", "#a5845a", "#8f6f48"]
GARNISH = (("#3f8a2f", 14, 6), ("#e8331c", 10, 5), ("#f3e3c4", 8, 5))
VEG = (("#5a9a2e", 40, 5), ("#f07a24", 40, 5), ("#f3e3c4", 10, 5))


def base():
    return plate(300, 300, 280)


def side_dodo(rng, spots):
    out = []
    for cx, cy, rot in spots:
        out += dodo(rng, cx, cy, 44, 28, rot)
    return out


def jollof_enjoyment():
    rng = random.Random(7)
    b = base() + rice(rng, 245, 300, 168, JOLLOF, 700, GARNISH)
    b += beef(rng, 395, 205, 42) + beef(rng, 452, 285, 38) + egg(380, 368, 42, -20)
    b += side_dodo(rng, ((300, 462, 20), (378, 455, -15), (445, 410, 40)))
    return svg(600, 600, b)


def royal_basmati():
    rng = random.Random(9)
    b = base() + rice(rng, 245, 300, 168, FRIED, 520, VEG, length=1.6)
    b += beef(rng, 395, 210, 42) + beef(rng, 452, 292, 38)
    b += side_dodo(rng, ((318, 458, 20), (395, 448, -15), (455, 385, 40)))
    return svg(600, 600, b)


def white_rice_special():
    rng = random.Random(13)
    b = base() + rice(rng, 245, 300, 165, WHITE, 650)
    b += sauce(rng, 235, 255, 95, 60)
    b += beef(rng, 395, 195, 38) + shaki(rng, 458, 275, 38) + egg(425, 365, 40, 15)
    b += side_dodo(rng, ((300, 462, 20), (370, 460, -15)))
    return svg(600, 600, b)


def ofada_special():
    rng = random.Random(17)
    b = base() + rice(rng, 245, 300, 165, OFADA, 650, (("#8f3a1c", 30, 3),), length=0.8)
    b += liver(rng, 395, 195, 36) + shaki(rng, 458, 270, 36) + roundabout(rng, 380, 270, 18) + egg(430, 368, 40, -10)
    b += side_dodo(rng, ((300, 462, 20), (370, 460, -15)))
    return svg(600, 600, b)


def basmati_fried_rice():
    rng = random.Random(53)
    return svg(600, 600, base() + rice(rng, 300, 300, 210, FRIED, 800, VEG, length=1.6))


def jollof_rice():
    rng = random.Random(19)
    return svg(600, 600, base() + rice(rng, 300, 300, 210, JOLLOF, 950, GARNISH))


def ofada_rice():
    rng = random.Random(23)
    return svg(600, 600, base() + rice(rng, 300, 300, 210, OFADA, 950, (("#8f3a1c", 45, 3),), length=0.8))


def stir_fry_spaghetti():
    rng = random.Random(29)
    b = base() + noodles(rng, 300, 300, 200)
    for _ in range(14):
        x, y, _d = in_ellipse(rng, 300, 300, 150, 140)
        b.append(pepper_strip(round(x), round(y), rng.randint(30, 50), rng.randint(0, 179), rng.choice(["#3f8a2f", "#e8331c", "#f07a24"])))
    for _ in range(7):
        x, y, _d = in_ellipse(rng, 300, 300, 140, 130)
        b.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="15" fill="#c8735a" stroke="#9c4f3a" stroke-width="3"/>')
    return svg(600, 600, b)


def porridge():
    rng = random.Random(31)
    b = base() + soup(rng, 300, 300, 215, "#d9661f", [(["#e5772a", "#c9501a"], 80, 5, 10), (["#2f6b2f", "#3f8a3a"], 30, 6, 12)])
    b += yam_chunks(rng, 300, 300, 160, 150, 14)
    return svg(600, 600, b)


def chicken_chips():
    rng = random.Random(37)
    b = base() + fries(rng, 215, 330, 105, 120, 30)
    b += drumstick(rng, 365, 230, 130, -35) + drumstick(rng, 390, 370, 125, 5)
    b += ['<circle cx="190" cy="175" r="44" fill="#fffaf2" stroke="#e6dac4" stroke-width="3"/>', '<circle cx="190" cy="175" r="33" fill="#c91d14"/>']
    return svg(600, 600, b)


def fried_chicken():
    rng = random.Random(41)
    b = base() + drumstick(rng, 215, 250, 140, -20) + drumstick(rng, 330, 210, 135, 35) + drumstick(rng, 300, 370, 140, -5)
    return svg(600, 600, b)


def amala_feast():
    rng = random.Random(43)
    b = base() + soup(rng, 385, 320, 160, "#3f6e25", EWEDU, oil=False)
    b += soup(rng, 430, 405, 85, "#dba140", [(["#bf8a2a"], 50, 1.5, 3)], oil=False)
    b += sauce(rng, 360, 195, 85, 55) + beef(rng, 335, 195, 32) + beef(rng, 400, 205, 30)
    b += dome(rng, 190, 225, 92, "amala") + dome(rng, 205, 385, 90, "amala")
    return svg(600, 600, b)


def semo_combo():
    rng = random.Random(47)
    b = base() + soup(rng, 380, 330, 165, "#2f5a1c", EFO)
    b += beef(rng, 380, 230, 36) + beef(rng, 445, 310, 34) + ponmo(rng, 375, 420, 90, 32, -20)
    b += dome(rng, 195, 270, 118, "semo", "#8a6d3b")
    return svg(600, 600, b)


def swallow(grad, speck, seed):
    rng = random.Random(seed)
    return svg(600, 600, base() + dome(rng, 300, 300, 170, grad, speck))


def egusi():
    rng = random.Random(59)
    b = base() + soup(rng, 300, 300, 215, "#c99a3a", EGUSI)
    b += beef(rng, 250, 250, 38) + beef(rng, 360, 350, 36)
    return svg(600, 600, b)


def efo_riro():
    rng = random.Random(61)
    b = base() + soup(rng, 300, 300, 215, "#2f5a1c", EFO)
    b += beef(rng, 245, 260, 38) + ponmo(rng, 360, 340, 90, 32, 25)
    return svg(600, 600, b)


def fried_turkey():
    rng = random.Random(11)
    b = base() + turkey(rng, 225, 285, 270, 120, -62) + turkey(rng, 330, 275, 280, 124, -70) + turkey(rng, 410, 330, 240, 110, -52)
    for cx, cy, r, rot in ((170, 430, 22, 20), (430, 180, 20, -30), (300, 450, 18, 60)):
        b += onion(cx, cy, r, rot)
    return svg(600, 600, b)


def bokoto():
    rng = random.Random(67)
    b = base() + sauce(rng, 300, 300, 210, 200)
    for cx, cy, r in ((225, 235, 52), (340, 220, 48), (400, 320, 50), (285, 330, 54), (215, 395, 44), (335, 420, 46)):
        b += bokoto_piece(rng, cx, cy, r)
    return svg(600, 600, b)


def asun():
    rng = random.Random(71)
    b = base()
    for cx, cy, r in ((230, 230, 42), (310, 205, 38), (385, 240, 40), (205, 315, 38), (290, 290, 44), (380, 325, 40), (240, 395, 40), (325, 380, 42), (410, 405, 34)):
        b += beef(rng, cx, cy, r)
    for cx, cy, rot, colour in ((265, 255, 30, "#e8331c"), (350, 300, -20, "#3f8a2f"), (260, 350, 70, "#e8331c"), (345, 245, 10, "#3f8a2f")):
        b.append(pepper_strip(cx, cy, 52, rot, colour))
    b += onion(300, 340, 22, 15) + onion(230, 280, 20, -25) + onion(390, 280, 18, 40)
    return svg(600, 600, b)


def croaker_fish():
    rng = random.Random(73)
    b = base() + sauce(rng, 300, 300, 215, 205) + croaker(rng, 300, 300, 400, -25)
    b += onion(180, 420, 22, 20) + onion(420, 190, 20, -30)
    return svg(600, 600, b)


def eja_kika():
    rng = random.Random(23)
    b = base() + sauce(rng, 300, 300, 215, 210)
    b += fish(rng, 225, 230, 170, 110, -20) + fish(rng, 370, 240, 160, 104, 25)
    b += fish(rng, 240, 380, 160, 104, 15) + fish(rng, 385, 385, 150, 100, -30)
    return svg(600, 600, b)


def peppered_beef():
    rng = random.Random(79)
    b = base() + sauce(rng, 300, 300, 200, 190)
    for cx, cy, r in ((235, 235, 40), (320, 215, 38), (390, 270, 40), (230, 330, 38), (310, 305, 42), (385, 365, 36), (275, 400, 38)):
        b += beef(rng, cx, cy, r)
    b += [pepper_strip(280, 270, 50, 30, "#3f8a2f"), pepper_strip(350, 340, 46, -20, "#3f8a2f")]
    b += onion(300, 350, 22, 15) + onion(245, 285, 18, -25)
    return svg(600, 600, b)


def assorted_meat():
    rng = random.Random(83)
    b = base() + sauce(rng, 300, 300, 210, 200)
    b += shaki(rng, 230, 240, 48) + shaki(rng, 375, 360, 46) + shaki(rng, 240, 380, 40)
    b += liver(rng, 340, 225, 42) + liver(rng, 410, 280, 36) + liver(rng, 300, 420, 36)
    b += roundabout(rng, 300, 310, 24) + roundabout(rng, 190, 310, 20) + roundabout(rng, 420, 420, 20)
    return svg(600, 600, b)


def ponmo_plate():
    rng = random.Random(89)
    b = base() + sauce(rng, 300, 300, 210, 200)
    for cx, cy, rot in ((230, 230, -20), (350, 215, 15), (215, 320, 40), (310, 300, -35), (400, 300, 60), (260, 400, 10), (370, 395, -15)):
        b += ponmo(rng, cx, cy, 110, 40, rot)
    return svg(600, 600, b)


def plantain():
    rng = random.Random(5)
    b = base()
    spots = [(300, 300, 0)] + [(300 + 120 * math.cos(a), 300 + 115 * math.sin(a), math.degrees(a) + 90) for a in [i * math.pi / 4 for i in range(8)]]
    spots += [(300 + 60 * math.cos(a), 300 + 58 * math.sin(a), math.degrees(a)) for a in [i * math.pi / 2 + 0.5 for i in range(4)]]
    for cx, cy, rot in spots:
        b += dodo(rng, round(cx), round(cy), 58, 36, round(rot))
    return svg(600, 600, b)


def salad():
    rng = random.Random(97)
    return svg(600, 600, base() + slaw(rng, 300, 300, 205))


def moi_moi():
    rng = random.Random(71)
    b = base()
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
        "jollof-enjoyment": jollof_enjoyment, "royal-basmati": royal_basmati,
        "white-rice-special": white_rice_special, "ofada-special": ofada_special,
        "basmati-fried-rice": basmati_fried_rice, "jollof-rice": jollof_rice, "ofada-rice": ofada_rice,
        "stir-fry-spaghetti": stir_fry_spaghetti, "porridge": porridge, "chicken-chips": chicken_chips,
        "fried-chicken": fried_chicken, "amala-feast": amala_feast, "semo-combo": semo_combo,
        "eba": lambda: swallow("eba", "#a07a1e", 101), "fufu": lambda: swallow("fufu", "#8a8170", 103),
        "semo": lambda: swallow("semo", "#8a6d3b", 107), "egusi": egusi, "efo-riro": efo_riro,
        "turkey": fried_turkey, "bokoto": bokoto, "asun": asun, "croaker": croaker_fish,
        "eja-kika": eja_kika, "beef": peppered_beef, "assorted-meat": assorted_meat, "ponmo": ponmo_plate,
        "plantain": plantain, "salad": salad, "moi-moi": moi_moi, "zobo": zobo, "pepper-pot": pepper_pot,
    }
    for name, fn in dishes.items():
        (ART / f"{name}.svg").write_text(fn())
    (PAT / "on-red.svg").write_text(pattern("#ff6a6f", 0.42))
    (PAT / "on-cream.svg").write_text(pattern("#e9c49c", 0.55))
    (PAT / "band.svg").write_text(pattern("#fdf0dc", 0.95))
    print(f"wrote {len(dishes)} dishes and 3 patterns")


if __name__ == "__main__":
    main()
