"""Generates the Parket Lux logo SVGs (text converted to outlines).

Usage: python3 build.py <fonts-dir>
Fonts: fira800.woff (FiraGO ExtraBold, Latin), geo800.ttf / geo700.ttf (Noto Sans Georgian,
used for Georgian capitals / Mtavruli, which the available FiraGO build lacks).
"""
import math
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else "."
BG, WHITE, SILVER, STEEL, TAN = "#0B0B0B", "#FFFFFF", "#C3C8CC", "#6B7378", "#D8B47A"
GREEN, DGREEN = "#1E8A42", "#14602D"
YELLOW, DYELLOW, WOOD = "#F5C400", "#C99A00", "#E8D3A2"
OAK, WALNUT = "#C8965C", "#94623A"


def mtavruli(s):
    return "".join(chr(ord(c) + 0xBC0) if 0x10D0 <= ord(c) <= 0x10FA else c for c in s)


def text_path(font_file, text, size, tracking=0.0):
    f = TTFont(font_file)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    s = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = 0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, 0)))
        cx += hmtx[g][0] * s + tracking * size
    return pen.getCommands(), cx - tracking * size


def fit_path(font_file, text, width, tracking=0.0):
    _, w = text_path(font_file, text, 100, tracking)
    return text_path(font_file, text, 100 * width / w, tracking)


def mark(cx, cy, R=80):
    """Parquet cube (three-rhombus pattern) with the rotary floor sander standing on its top face."""
    k = math.sqrt(3) / 2
    T, UR, LR, B, LL, UL, C = (0, -R), (k*R, -R/2), (k*R, R/2), (0, R), (-k*R, R/2), (-k*R, -R/2), (0, 0)
    def lerp(a, b, t): return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
    def pts(*ps): return " ".join(f"{x:.2f},{y:.2f}" for x, y in ps)
    out = []
    for (p0, p1, p2, p3), col in (((UL, T, UR, C), WOOD), ((C, UR, LR, B), WALNUT), ((LL, UL, C, B), OAK)):
        out.append(f'<polygon fill="{col}" stroke="{BG}" stroke-width="4" stroke-linejoin="round" points="{pts(p0, p1, p2, p3)}"/>')
        for t in (1/4, 2/4, 3/4):
            a, b = lerp(p0, p3, t), lerp(p1, p2, t)
            out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{BG}" stroke-width="2"/>')
    hose = "M-8,-101 C-44,-104 -50,-70 -30,-50"
    out.append(f'''<g transform="translate(0,-40) scale(1.3) translate(0,40)">
  <path d="M26,-44 L35,-114" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/>
  <rect x="18" y="-127" width="36" height="12" rx="6" fill="none" stroke="{SILVER}" stroke-width="4.5"/>
  <path d="M-24,-60 C-8,-86 12,-104 33,-104 C42,-104 46,-108 47,-115" fill="none" stroke="{YELLOW}" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M-36,-40 V-33 A36,18 0 0 0 36,-33 V-40 Z" fill="{DYELLOW}"/>
  <ellipse cx="0" cy="-40" rx="36" ry="18" fill="{YELLOW}"/>
  <ellipse cx="0" cy="-40" rx="36" ry="18" fill="none" stroke="{BG}" stroke-width="1.2" opacity=".35"/>
  <path d="{hose}" fill="none" stroke="{TAN}" stroke-width="6.5" stroke-linecap="round"/>
  <path d="{hose}" fill="none" stroke="#A9854C" stroke-width="6.5" stroke-dasharray="1.4 2.6"/>
  <rect x="-9" y="-68" width="24" height="24" rx="2" fill="{STEEL}"/>
  <rect x="-9" y="-94" width="24" height="27" rx="2" fill="{SILVER}"/>
  <path d="M-5,-94 V-67 M-1,-94 V-67 M3,-94 V-67 M7,-94 V-67 M11,-94 V-67" stroke="#9AA1A6" stroke-width="1"/>
  <rect x="-9" y="-68" width="24" height="2.5" fill="{YELLOW}"/>
  <path d="M-11,-94 V-102 Q-11,-110 3,-110 Q17,-110 17,-102 V-94 Z" fill="{YELLOW}"/>
  <rect x="0" y="-115" width="6" height="6" rx="1.5" fill="{SILVER}"/>
  <rect x="-36" y="-58" width="24" height="16" rx="3" fill="{GREEN}"/>
  <circle cx="-24" cy="-62" r="7" fill="{GREEN}"/>
  <rect x="-33" y="-54" width="8" height="8" rx="1" fill="{WHITE}"/>
  <path d="M-14,-47 H26" stroke="{GREEN}" stroke-width="4.5" stroke-linecap="round"/></g>''')
    return f'<g transform="translate({cx},{cy+43})">' + "".join(out) + '</g>'


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n'


LAT, GEO_B, GEO_M = f"{FONTS}/fira800.woff", f"{FONTS}/geo800.ttf", f"{FONTS}/geo700.ttf"
NAME_KA, TAG_KA = mtavruli("პარკეტ ლუქსი"), mtavruli("პარკეტის ხეხვა და აღდგენა")


def wordmark(x, y, size):
    """PARKET LUX / rule / big Georgian name / tagline, all set to the same width. Returns (svg, width, height)."""
    parket, pw = text_path(LAT, "PARKET", size, 0.05)
    lux, lw = text_path(LAT, "LUX", size, 0.05)
    gap = size * 0.3
    tw = pw + gap + lw
    geo, _ = fit_path(GEO_B, NAME_KA, tw, 0.06)
    tag, _ = fit_path(GEO_M, TAG_KA, tw, 0.12)
    cap = size * 0.7
    y1 = y + cap
    y2 = y1 + size * 0.28
    y3 = y2 + size * 0.2 + size * 0.62
    y4 = y3 + size * 0.5
    out = f'<path fill="{WHITE}" transform="translate({x:.2f},{y1:.2f})" d="{parket}"/>'
    out += f'<path fill="{GREEN}" transform="translate({x+pw+gap:.2f},{y1:.2f})" d="{lux}"/>'
    out += f'<rect x="{x:.2f}" y="{y2:.2f}" width="{tw:.2f}" height="{size*0.045:.2f}" fill="{YELLOW}"/>'
    out += f'<path fill="{YELLOW}" transform="translate({x:.2f},{y3:.2f})" d="{geo}"/>'
    out += f'<path fill="{SILVER}" transform="translate({x:.2f},{y4:.2f})" d="{tag}"/>'
    return out, tw, y4 - y


# Horizontal lockup
_, tw, th = wordmark(0, 0, 64)
H = 330
body, tw, th = wordmark(260, (H - th) / 2 - 4, 64)
body = mark(130, H / 2) + body
open("logo-horizontal.svg", "w").write(svg(round(260 + tw + 60), H, body))

# Stacked / square (profile picture)
S = 600
_, tw, th = wordmark(0, 0, 58)
top = (S - (245 + 36 + th)) / 2
body = mark(S / 2, top + 122)
wm, tw, th = wordmark((S - tw) / 2, top + 281, 58)
open("logo-stacked.svg", "w").write(svg(S, S, body + wm))

# Symbol only
open("logo-mark.svg", "w").write(svg(240, 240, mark(120, 120)))
