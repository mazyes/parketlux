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
INK = "#FFFFFF"
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
    hose = "M-11,-99 C-44,-102 -50,-70 -30,-52"
    HL, DG, DARK = "#FFE36B", "#146A30", "#2B2F33"
    out.append(f'''<g transform="translate(0,-40) scale(1.3) translate(0,40)">
  <path d="M26,-46 L35,-113" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/>
  <path d="M27.5,-50 L31,-76" stroke="{DG}" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="18" y="-127" width="36" height="12" rx="6" fill="none" stroke="{SILVER}" stroke-width="4.5"/>
  <path d="M40,-127 H48 M40,-115 H48" stroke="{STEEL}" stroke-width="4.5"/>
  <rect x="31.5" y="-118" width="7" height="6" rx="1.5" fill="{GREEN}"/>
  <path d="M-24,-66 C-10,-90 8,-92 29,-84" fill="none" stroke="{YELLOW}" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M33,-88 C44,-96 46,-106 44,-113" fill="none" stroke="{YELLOW}" stroke-width="1.5" stroke-linecap="round"/>
  <rect x="27" y="-91" width="9" height="9" rx="2" fill="{YELLOW}" transform="rotate(8 31.5 -86.5)"/>
  <path d="M-36,-36 V-31 A36,18 0 0 0 36,-31 V-36 Z" fill="{DARK}"/>
  <path d="M-36,-40 V-35 A36,18 0 0 0 36,-35 V-40 Z" fill="{DYELLOW}"/>
  <ellipse cx="0" cy="-40" rx="36" ry="18" fill="{YELLOW}"/>
  <path d="M-30,-31 A36,18 0 0 0 30,-31" fill="none" stroke="{HL}" stroke-width="1.4" stroke-linecap="round"/>
  <circle cx="-22" cy="-30" r="1.4" fill="{DARK}"/><circle cx="22" cy="-30" r="1.4" fill="{DARK}"/>
  <path d="{hose}" fill="none" stroke="{TAN}" stroke-width="6.5" stroke-linecap="round"/>
  <path d="{hose}" fill="none" stroke="#A9854C" stroke-width="6.5" stroke-dasharray="1.2 2.4"/>
  <rect x="-15" y="-103" width="6" height="8" rx="1.5" fill="{DARK}"/>
  <rect x="-34" y="-54" width="8" height="6" rx="1.5" fill="{DARK}" transform="rotate(35 -30 -51)"/>
  <rect x="-10" y="-50" width="26" height="6" rx="2" fill="{GREEN}"/>
  <rect x="-9" y="-68" width="24" height="20" rx="2" fill="{STEEL}"/>
  <rect x="-6" y="-66" width="3" height="16" rx="1.5" fill="#8C959B"/>
  <rect x="-10" y="-70" width="26" height="3.5" rx="1" fill="{YELLOW}"/>
  <rect x="-9" y="-94" width="24" height="24" rx="1.5" fill="{SILVER}"/>
  <path d="M-5.5,-94 V-70 M-2,-94 V-70 M1.5,-94 V-70 M5,-94 V-70 M8.5,-94 V-70 M12,-94 V-70" stroke="#9AA1A6" stroke-width=".9"/>
  <path d="M-9,-82 H15" stroke="#9AA1A6" stroke-width="1.6"/>
  <path d="M-11,-94 V-101 Q-11,-110 3,-110 Q17,-110 17,-101 V-94 Z" fill="{YELLOW}"/>
  <rect x="-11" y="-97" width="28" height="3" fill="{DYELLOW}"/>
  <path d="M-6,-104 Q-4,-108 3,-108" fill="none" stroke="{HL}" stroke-width="1.4" stroke-linecap="round"/>
  <rect x="1" y="-116" width="4" height="7" rx="1" fill="{SILVER}"/>
  <rect x="-1" y="-117" width="8" height="2.5" rx="1" fill="{SILVER}"/>
  <path d="M-13,-47 H24 M11,-47 L28.1,-62" fill="none" stroke="{BG}" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M-13,-47 H24 M11,-47 L28.1,-62" fill="none" stroke="{GREEN}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M-12,-45.4 H22" stroke="{DG}" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="21" y="-52" width="10" height="10" rx="2.5" fill="{GREEN}" stroke="{BG}" stroke-width="1.5"/>
  <circle cx="26" cy="-47" r="1.5" fill="{SILVER}"/>
  <rect x="24.6" y="-65" width="7" height="6" rx="1.5" fill="{GREEN}" stroke="{BG}" stroke-width="1.5" transform="rotate(7.6 28.1 -62)"/>
  <circle cx="28.1" cy="-62" r="1.1" fill="{SILVER}"/>
  <rect x="-38" y="-58" width="24" height="15" rx="2.5" fill="{GREEN}"/>
  <rect x="-35.5" y="-55.5" width="9" height="8" rx="1" fill="{WHITE}" stroke="{DARK}" stroke-width="1.2"/>
  <path d="M-34,-50 L-29.5,-53.5" stroke="{DARK}" stroke-width=".9" stroke-linecap="round"/>
  <circle cx="-21" cy="-53" r="1.6" fill="{YELLOW}"/><circle cx="-17" cy="-53" r="1.6" fill="{DARK}"/>
  <rect x="-37" y="-72" width="22" height="14" rx="6" fill="{GREEN}"/>
  <path d="M-31,-71 V-59 M-27,-71 V-59 M-23,-71 V-59 M-19,-71 V-59" stroke="{DG}" stroke-width="1.3"/>
  <circle cx="-15" cy="-65" r="4.5" fill="{DG}"/>
  <circle cx="-15" cy="-65" r="1.6" fill="{SILVER}"/></g>''')
    return f'<g transform="translate({cx},{cy+43})">' + "".join(out) + '</g>'


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n'


LAT, GEO_B, GEO_M = f"{FONTS}/fira800.woff", f"{FONTS}/geo800.ttf", f"{FONTS}/geo700.ttf"
NAME_KA, TAG_KA = mtavruli("პარკეტ ლუქსი"), mtavruli("პარკეტის მოხვეწა და აღდგენა")


def wordmark(x, y, size, rule_above=False):
    """PARKET LUX / rule / big Georgian name / tagline, all set to the same width. Returns (svg, width, height)."""
    parket, pw = text_path(LAT, "PARKET", size, 0.05)
    lux, lw = text_path(LAT, "LUX", size, 0.05)
    gap = size * 0.3
    tw = pw + gap + lw
    gsz = 100 * tw / text_path(GEO_B, NAME_KA, 100, 0.06)[1]
    w1, w2 = NAME_KA.split(" ")
    geo1, _ = text_path(GEO_B, w1, gsz, 0.06)
    geo2, g2w = text_path(GEO_B, w2, gsz, 0.06)
    g2x = tw - g2w
    tag, _ = fit_path(GEO_M, TAG_KA, tw, 0.12)
    cap = size * 0.7
    if rule_above:
        y2 = y
        y1 = y + size * 0.4 + cap
        y3 = y1 + size * 0.3 + size * 0.62
    else:
        y1 = y + cap
        y2 = y1 + size * 0.28
        y3 = y2 + size * 0.2 + size * 0.62
    y4 = y3 + size * 0.5
    out = f'<path fill="{INK}" transform="translate({x:.2f},{y1:.2f})" d="{parket}"/>'
    out += f'<path fill="{GREEN}" transform="translate({x+pw+gap:.2f},{y1:.2f})" d="{lux}"/>'
    out += f'<rect x="{x:.2f}" y="{y2:.2f}" width="{tw:.2f}" height="{size*0.045:.2f}" fill="{YELLOW}"/>'
    out += f'<path fill="{INK}" transform="translate({x:.2f},{y3:.2f})" d="{geo1}"/>'
    out += f'<path fill="{GREEN}" transform="translate({x+g2x:.2f},{y3:.2f})" d="{geo2}"/>'
    out += f'<path fill="{INK}" transform="translate({x:.2f},{y4:.2f})" d="{tag}"/>'
    return out, tw, y4 - y


# Black (default) and white-background variants
for sfx, BG, INK in (("", "#0B0B0B", "#FFFFFF"), ("-white", "#FFFFFF", "#1C1C1C")):
    # Horizontal lockup
    _, tw, th = wordmark(0, 0, 64)
    H = 330
    body, tw, th = wordmark(260, (H - th) / 2 - 4, 64)
    body = mark(130, H / 2) + body
    open(f"logo-horizontal{sfx}.svg", "w").write(svg(round(260 + tw + 60), H, body))

    # Stacked / square (profile picture)
    S = 600
    _, tw, th = wordmark(0, 0, 58, True)
    top = (S - (245 + 20 + th)) / 2
    body = mark(S / 2, top + 122)
    wm, tw, th = wordmark((S - tw) / 2, top + 265, 58, True)
    open(f"logo-stacked{sfx}.svg", "w").write(svg(S, S, body + wm))

    # Symbol only
    open(f"logo-mark{sfx}.svg", "w").write(svg(280, 280, mark(140, 140)))
