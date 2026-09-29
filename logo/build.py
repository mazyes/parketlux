"""Generates the Parket Lux logo SVGs (text converted to outlines)."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else "."
BROWN, CHAR, BEIGE, GOLD = "#5B3820", "#26221F", "#CDAE84", "#B8923E"

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

def mark(cx, cy, R=62):
    """Three-rhombus hexagon parquet (as laid on site) inside a sanding-disc arc."""
    import math
    k = math.sqrt(3) / 2
    T, UR, LR, B, LL, UL, C = (0, -R), (k*R, -R/2), (k*R, R/2), (0, R), (-k*R, R/2), (-k*R, -R/2), (0, 0)
    def lerp(a, b, t): return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
    def pts(*ps): return " ".join(f"{x:.2f},{y:.2f}" for x, y in ps)
    out = []
    # rhombus (p0,p1,p2,p3); plank seams run parallel to p0->p1
    for (p0, p1, p2, p3), col in (((UL, T, UR, C), BEIGE), ((C, UR, LR, B), CHAR), ((LL, UL, C, B), BROWN)):
        out.append(f'<polygon fill="{col}" stroke="#fff" stroke-width="5" stroke-linejoin="round" points="{pts(p0, p1, p2, p3)}"/>')
        for t in (1/3, 2/3):
            a, b = lerp(p0, p3, t), lerp(p1, p2, t)
            out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#fff" stroke-width="2.5"/>')
    r = R + 20
    a0, a1 = math.radians(-60), math.radians(210)
    x0, y0, x1, y1 = r*math.cos(a0), r*math.sin(a0), r*math.cos(a1), r*math.sin(a1)
    out.append(f'<path d="M{x0:.2f},{y0:.2f} A{r},{r} 0 1 1 {x1:.2f},{y1:.2f}" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>')
    return f'<g transform="translate({cx},{cy})">' + "".join(out) + '</g>'

def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{body}\n</svg>\n'

M7, M5, G6 = f"{FONTS}/mont700.ttf", f"{FONTS}/mont500.ttf", f"{FONTS}/geo600.ttf"

# Horizontal lockup
parket, pw = text_path(M7, "PARKET", 64, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 64, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 25, 0, 0, 0.12)
gap = 20
tw = pw + gap + lw
tx, W, H = 240, 240 + tw + 60, 240
body = mark(122, 120)
body += f'<path fill="{CHAR}" transform="translate({tx},128)" d="{parket}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+pw+gap},128)" d="{lux}"/>'
body += f'<rect x="{tx}" y="148" width="{tw}" height="2" fill="{GOLD}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+(tw-gw)/2},188)" d="{geo}"/>'
open("logo-horizontal.svg", "w").write(svg(round(W), H, body))

# Stacked / square (profile picture)
S = 600
parket, pw = text_path(M7, "PARKET", 58, 0, 0, 0.06)
lux, lw = text_path(M7, "LUX", 58, 0, 0, 0.06)
geo, gw = text_path(G6, "პარკეტ ლუქსი", 24, 0, 0, 0.12)
tw = pw + 18 + lw
tx = (S - tw) / 2
body = mark(S / 2, 222)
body += f'<path fill="{CHAR}" transform="translate({tx},384)" d="{parket}"/>'
body += f'<path fill="{BROWN}" transform="translate({tx+pw+18},384)" d="{lux}"/>'
body += f'<rect x="{tx}" y="404" width="{tw}" height="2" fill="{GOLD}"/>'
body += f'<path fill="{BROWN}" transform="translate({(S-gw)/2},444)" d="{geo}"/>'
open("logo-stacked.svg", "w").write(svg(S, S, body))

# Symbol only
open("logo-mark.svg", "w").write(svg(240, 240, mark(120, 120)))
