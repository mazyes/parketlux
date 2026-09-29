"""Generates the Parket Lux logo SVGs (text converted to outlines)."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else "."
BROWN, CHAR, BEIGE, GOLD = "#5B3820", "#26221F", "#CDAE84", "#B8923E"
GREEN = "#2E6B45"

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

def mark(cx, cy):
    """Rotary floor sander on a parquet strip: worn planks ahead, restored planks behind. Box 200x170."""
    floor = []
    for i in range(-1, 10):
        x = i * 24
        col = BROWN if x + 10 < 64 else BEIGE
        floor.append(f'<polygon fill="{col}" points="{x+8},152 {x+29},152 {x+21},170 {x},170"/>')
    return f'''<g transform="translate({cx-100},{cy-85})">
  <clipPath id="floor"><rect x="0" y="152" width="200" height="18" rx="3"/></clipPath>
  <g clip-path="url(#floor)">{"".join(floor)}</g>
  <path d="M78,44 C52,44 32,58 38,78 C41,88 46,92 50,96" fill="none" stroke="{BEIGE}" stroke-width="8" stroke-linecap="round"/>
  <line x1="120" y1="118" x2="146" y2="30" stroke="{GREEN}" stroke-width="8" stroke-linecap="round"/>
  <line x1="134" y1="26" x2="170" y2="18" stroke="{CHAR}" stroke-width="8" stroke-linecap="round"/>
  <rect x="78" y="46" width="36" height="72" rx="5" fill="{BEIGE}"/>
  <rect x="78" y="70" width="36" height="3" fill="#fff"/>
  <rect x="78" y="94" width="36" height="3" fill="#fff"/>
  <rect x="74" y="34" width="44" height="14" rx="5" fill="{CHAR}"/>
  <rect x="40" y="92" width="34" height="28" rx="5" fill="{GREEN}"/>
  <rect x="28" y="118" width="108" height="10" rx="3" fill="{GREEN}"/>
  <rect x="22" y="128" width="120" height="18" rx="9" fill="{CHAR}"/>
  <path d="M8,124 A30,30 0 0 0 8,150" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>
  <path d="M-4,118 A40,40 0 0 0 -4,156" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round" opacity=".55"/>
</g>'''

def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{body}\n</svg>\n'

M7, M5, G6 = f"{FONTS}/mont700.ttf", f"{FONTS}/mont500.ttf", f"{FONTS}/geo600.ttf"

# Horizontal lockup
parket, pw = text_path(M7, "PARKET", 64, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 64, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 25, 0, 0, 0.12)
gap = 20
tw = pw + gap + lw
tag, tgw = text_path(G6, "პარკეტის ხეხვა და აღდგენა", 16, 0, 0, 0.1)
tx, W, H = 290, 290 + tw + 60, 260
body = mark(150, 130)
body += f'<path fill="{CHAR}" transform="translate({tx},128)" d="{parket}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+pw+gap},128)" d="{lux}"/>'
body += f'<rect x="{tx}" y="148" width="{tw}" height="2" fill="{GOLD}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+(tw-gw)/2},188)" d="{geo}"/>'
body += f'<path fill="{GREEN}" transform="translate({tx+(tw-tgw)/2},222)" d="{tag}"/>'
open("logo-horizontal.svg", "w").write(svg(round(W), H, body))

# Stacked / square (profile picture)
S = 600
parket, pw = text_path(M7, "PARKET", 58, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 58, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 24, 0, 0, 0.12)
tag, tgw = text_path(G6, "პარკეტის ხეხვა და აღდგენა", 16, 0, 0, 0.1)
tw = pw + 18 + lw
tx = (S - tw) / 2
body = mark(S / 2, 196)
body += f'<path fill="{CHAR}" transform="translate({tx},358)" d="{parket}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+pw+18},358)" d="{lux}"/>'
body += f'<rect x="{tx}" y="378" width="{tw}" height="2" fill="{GOLD}"/>'
body += f'<path fill="{BROWN}" transform="translate({(S-gw)/2},418)" d="{geo}"/>'
body += f'<path fill="{GREEN}" transform="translate({(S-tgw)/2},456)" d="{tag}"/>'
open("logo-stacked.svg", "w").write(svg(S, S, body))

# Symbol only
open("logo-mark.svg", "w").write(svg(240, 240, mark(120, 120)))
