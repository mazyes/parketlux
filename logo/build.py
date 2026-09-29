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
    """Rotary floor sander on herringbone parquet: worn planks ahead, restored behind. Box 200x170."""
    floor = []
    for i in range(-2, 12):
        x, col = i * 18, (BROWN if i < 3 else BEIGE)
        floor.append(f'<polygon fill="{col}" points="{x},159.25 {x+7.25},152 {x+23.5},152 {x+16.25},159.25"/>')
        floor.append(f'<polygon fill="{col}" points="{x},160.75 {x+16.25},160.75 {x+23.5},168 {x+7.25},168"/>')
    return f'''<g transform="translate({cx-100},{cy-85})">
  <clipPath id="floor"><rect x="4" y="152" width="192" height="16" rx="2"/></clipPath>
  <g clip-path="url(#floor)">{"".join(floor)}</g>
  <path d="M77,41 C46,38 28,58 40,78 L50,90" fill="none" stroke="{BEIGE}" stroke-width="7" stroke-linecap="round"/>
  <path d="M129,121 L151,30" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linecap="round"/>
  <path d="M112,74 H139" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/>
  <path d="M143,28 L172,21" stroke="{CHAR}" stroke-width="9" stroke-linecap="round"/>
  <rect x="81" y="46" width="34" height="72" rx="3" fill="{BEIGE}"/>
  <path d="M81,68 H115 M81,90 H115" stroke="#fff" stroke-width="3"/>
  <rect x="94" y="27" width="8" height="8" rx="2" fill="{CHAR}"/>
  <rect x="76" y="33" width="44" height="15" rx="6" fill="{CHAR}"/>
  <rect x="36" y="88" width="38" height="30" rx="6" fill="{GREEN}"/>
  <path d="M44,98 H66 M44,104 H66 M44,110 H66" stroke="#fff" stroke-width="2.2" stroke-linecap="round" opacity=".85"/>
  <path d="M30,126 L36,117 H130 L136,126 Z" fill="{GREEN}"/>
  <path d="M22,134 A8,8 0 0 1 30,126 H136 A8,8 0 0 1 144,134 V138 A6,6 0 0 1 138,144 H28 A6,6 0 0 1 22,138 Z" fill="{CHAR}"/>
  <rect x="28" y="145" width="110" height="3.5" rx="1.5" fill="{GOLD}"/>
  <path d="M13,127 A26,26 0 0 0 13,149" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M3,121 A36,36 0 0 0 3,155" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round" opacity=".45"/>
</g>'''

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
tag, tgw = text_path(T5, "პარკეტის ხეხვა და აღდგენა", 16, 0, 0, 0.1)
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
