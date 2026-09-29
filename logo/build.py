"""Generates the Parket Lux logo SVGs (text converted to outlines)."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else "."
BROWN, CHAR, BEIGE, GOLD = "#5B3820", "#26221F", "#CDAE84", "#B8923E"
GREEN, DGREEN = "#1E7B3C", "#145A2B"
YELLOW, DYELLOW, WOOD = "#F5C400", "#D9A300", "#E8D3A2"

def text_path(font_file, text, size, x, y, tracking=0.0):
    f = TTFont(font_file)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    s = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx, w = 0, 0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x + cx, y)))
        cx += hmtx[g][0] * s + tracking * size
    return pen.getCommands(), cx - tracking * size

def mark(cx, cy, R=70):
    """Parquet cube (three-rhombus pattern) with a rotary floor sander on its top face. Box ~140x198."""
    import math
    k = math.sqrt(3) / 2
    T, UR, LR, B, LL, UL, C = (0, -R), (k*R, -R/2), (k*R, R/2), (0, R), (-k*R, R/2), (-k*R, -R/2), (0, 0)
    def lerp(a, b, t): return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
    def pts(*ps): return " ".join(f"{x:.2f},{y:.2f}" for x, y in ps)
    out = []
    for (p0, p1, p2, p3), col in (((UL, T, UR, C), WOOD), ((C, UR, LR, B), DGREEN), ((LL, UL, C, B), GREEN)):
        out.append(f'<polygon fill="{col}" stroke="#fff" stroke-width="4" stroke-linejoin="round" points="{pts(p0, p1, p2, p3)}"/>')
        for t in (1/4, 2/4, 3/4):
            a, b = lerp(p0, p3, t), lerp(p1, p2, t)
            out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#fff" stroke-width="2"/>')
    # sander standing on the top face
    out.append(f'''
  <path d="M-13,-104 C-44,-104 -46,-74 -28,-60" fill="none" stroke="{DYELLOW}" stroke-width="5" stroke-linecap="round"/>
  <line x1="20" y1="-42" x2="36" y2="-118" stroke="{GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="28" y1="-121" x2="54" y2="-128" stroke="{CHAR}" stroke-width="8" stroke-linecap="round"/>
  <path d="M-32,-38 V-32 A32,16 0 0 0 32,-32 V-38 Z" fill="{DYELLOW}"/>
  <ellipse cx="0" cy="-38" rx="32" ry="16" fill="{YELLOW}"/>
  <rect x="-34" y="-62" width="20" height="20" rx="4" fill="{GREEN}" stroke="#fff" stroke-width="2.5"/>
  <rect x="-10" y="-100" width="20" height="62" rx="3" fill="{CHAR}" stroke="#fff" stroke-width="2.5"/>
  <path d="M-8.75,-80 H8.75 M-8.75,-60 H8.75" stroke="#fff" stroke-width="2"/>
  <rect x="-14" y="-110" width="28" height="12" rx="5" fill="{YELLOW}" stroke="#fff" stroke-width="2.5"/>
  <line x1="11" y1="-70" x2="28" y2="-70" stroke="{GREEN}" stroke-width="4"/>''')
    return f'<g transform="translate({cx},{cy+29})">' + "".join(out) + '</g>'

def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{body}\n</svg>\n'

M7, G6, T5 = f"{FONTS}/fira800.woff", f"{FONTS}/fira600.woff", f"{FONTS}/fira500.woff"

# Horizontal lockup
parket, pw = text_path(M7, "PARKET", 64, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 64, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 25, 0, 0, 0.12)
gap = 20
tw = pw + gap + lw
tag, tgw = text_path(T5, "პარკეტის ხეხვა და აღდგენა", 16, 0, 0, 0.1)
tx, W, H = 250, 250 + tw + 60, 260
body = mark(130, 130)
body += f'<path fill="{CHAR}" transform="translate({tx},128)" d="{parket}"/>'
body += f'<path fill="{GREEN}" transform="translate({tx+pw+gap},128)" d="{lux}"/>'
body += f'<rect x="{tx}" y="148" width="{tw}" height="2" fill="{DYELLOW}"/>'
body += f'<path fill="{GREEN}" transform="translate({tx+(tw-gw)/2},188)" d="{geo}"/>'
body += f'<path fill="{CHAR}" transform="translate({tx+(tw-tgw)/2},222)" d="{tag}"/>'
open("logo-horizontal.svg", "w").write(svg(round(W), H, body))

# Stacked / square (profile picture)
S = 600
parket, pw = text_path(M7, "PARKET", 58, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 58, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 24, 0, 0, 0.12)
tag, tgw = text_path(T5, "პარკეტის ხეხვა და აღდგენა", 16, 0, 0, 0.1)
tw = pw + 18 + lw
tx = (S - tw) / 2
body = mark(S / 2, 196)
body += f'<path fill="{CHAR}" transform="translate({tx},358)" d="{parket}"/>'
body += f'<path fill="{GREEN}" transform="translate({tx+pw+18},358)" d="{lux}"/>'
body += f'<rect x="{tx}" y="378" width="{tw}" height="2" fill="{DYELLOW}"/>'
body += f'<path fill="{GREEN}" transform="translate({(S-gw)/2},418)" d="{geo}"/>'
body += f'<path fill="{CHAR}" transform="translate({(S-tgw)/2},456)" d="{tag}"/>'
open("logo-stacked.svg", "w").write(svg(S, S, body))

# Symbol only
open("logo-mark.svg", "w").write(svg(240, 240, mark(120, 120)))
