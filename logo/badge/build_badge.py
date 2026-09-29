"""Replaces the English banner text of the round badge with Georgian (Mtavruli) text.

Usage: python3 build_badge.py <fonts-dir>   ->  badge-ka.svg (render to PNG afterwards)
"""
import base64, io, math, sys
import cv2
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else "."
NAME = "ᲞᲐᲠᲙᲔᲢ ᲚᲣᲥᲡᲘ"
TAG = "ᲞᲐᲠᲙᲔᲢᲘᲡ ᲛᲝᲮᲕᲔᲬᲐ ᲓᲐ ᲐᲦᲓᲒᲔᲜᲐ"

# 1. erase the old lettering: bright components inside the banner that are not the long border lines
img = np.array(Image.open("source.webp").convert("RGB"))
x0, y0, x1, y1 = 250, 872, 1005, 1050
roi = img[y0:y1, x0:x1]
tot = roi.astype(int).sum(axis=2)
bright = ((tot > 200) & (tot < 720)).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(bright, 8)
mask = np.zeros(img.shape[:2], np.uint8)
for i in range(1, n):
    x, y, w, h, area = stats[i]
    touches = x == 0 or y == 0 or x + w >= x1 - x0 or y + h >= y1 - y0
    if w < 200 and h < 140 and not touches:
        mask[y0:y1, x0:x1][lab == i] = 255
mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, mask, 9, cv2.INPAINT_TELEA)
buf = io.BytesIO(); Image.fromarray(clean).save(buf, "PNG")
href = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# 2. set Georgian text along the banner curve (circle centred above the badge)
def arc_text(font_file, text, size, tracking, cx, base_y, R, fill):
    f = TTFont(font_file)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    s = size / f["head"].unitsPerEm
    adv = [hmtx[cmap[ord(c)]][0] * s + tracking * size for c in text]
    total = sum(adv) - tracking * size
    cy = base_y - R
    out, pos = [], -total / 2
    for c, a in zip(text, adv):
        g = cmap[ord(c)]
        w = hmtx[g][0] * s
        th = (pos + w / 2) / R
        gx, gy = cx + R * math.sin(th), cy + R * math.cos(th)
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, -w / 2, 0)))
        d = pen.getCommands()
        if d:
            out.append(f'<path d="{d}" transform="translate({gx:.2f},{gy:.2f}) rotate({-math.degrees(th):.3f})"/>')
        pos += a
    return f'<g fill="{fill}">' + "".join(out) + "</g>", total

GOLD = "url(#gold)"
name, nw = arc_text(f"{FONTS}/geo800.ttf", NAME, 100, 0.04, 628, 1000, 1900, GOLD)
k = 690 / nw
name, _ = arc_text(f"{FONTS}/geo800.ttf", NAME, 100 * k, 0.04, 628, 1000, 1900, GOLD)
tag, tw = arc_text(f"{FONTS}/geo700.ttf", TAG, 10, 0.3, 628, 1040, 1940, GOLD)
tag, _ = arc_text(f"{FONTS}/geo700.ttf", TAG, 10 * 600 / tw, 0.3, 628, 1040, 1940, GOLD)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1254 1254" width="1254" height="1254">
<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
<stop offset="0" stop-color="#F8DC8A"/><stop offset=".5" stop-color="#E0B04E"/><stop offset="1" stop-color="#B8862C"/></linearGradient></defs>
<image href="{href}" width="1254" height="1254"/>
<g transform="translate(1.5,2.5)" opacity=".75">{name.replace(GOLD, "#041A0B")}{tag.replace(GOLD, "#041A0B")}</g>
{name}
{tag}
</svg>
'''
open("badge-ka.svg", "w").write(svg)
