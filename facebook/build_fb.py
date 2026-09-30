"""Builds Parket Lux Facebook post images (1080x1350) styled after the logo.

Usage: python3 build_fb.py <photos-dir>
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = sys.argv[1] if len(sys.argv) > 1 else "."
GEO = os.path.join(HERE, "fonts/NotoSerifGeorgian-Black.ttf")
LAT = os.path.join(HERE, "fonts/Cinzel.ttf")
OUT = os.path.join(HERE, "posts")
W, H = 1080, 1350
DGREEN, GREEN = (6, 40, 18), (16, 86, 40)
GOLD_STOPS = [(255, 243, 176), (240, 196, 70), (178, 118, 16), (236, 190, 72), (255, 230, 140)]
WHITE, INK = (255, 255, 255), (8, 44, 20)


def font(path, size):
    f = ImageFont.truetype(path, size)
    if path == LAT:
        f.set_variation_by_name("Black")
    return f


def runs(text, size):
    """Split text into (chunk, font) runs: Georgian letters and ₾ use Noto Serif Georgian, the rest Cinzel."""
    out = []
    for ch in text:
        f = GEO if "\u10a0" <= ch <= "\u10ff" or ch in "₾ -" else LAT
        if out and out[-1][1] == f:
            out[-1][0] += ch
        else:
            out.append([ch, f])
    return [(t, font(f, size)) for t, f in out]


def text_mask(text, size):
    rs = runs(text, size)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(sum(d.textlength(t, font=f) for t, f in rs)) + 4
    h = int(size * 1.6)
    m = Image.new("L", (w, h), 0)
    md, x = ImageDraw.Draw(m), 2
    for t, f in rs:
        md.text((x, int(size * 1.15)), t, font=f, fill=255, anchor="ls")
        x += md.textlength(t, font=f)
    return m.crop(m.getbbox() or (0, 0, 1, 1))


def vgradient(w, h, stops):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    n = len(stops) - 1
    for y in range(h):
        t = y / max(h - 1, 1) * n
        i = min(int(t), n - 1)
        a, b, k = stops[i], stops[i + 1], t - i
        d.line((0, y, w, y), fill=tuple(int(a[j] * (1 - k) + b[j] * k) for j in range(3)))
    return g


def draw_text(c, cx, y, text, size, fill="gold", max_w=None):
    m = text_mask(text, size)
    if max_w and m.width > max_w:
        return draw_text(c, cx, y, text, int(size * max_w / m.width), fill)
    x = int(cx - m.width / 2)
    shadow = Image.new("RGBA", m.size, (0, 0, 0, 0))
    shadow.putalpha(m.point(lambda v: v * 0.7))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    c.alpha_composite(shadow, (x + 3, y + 4))
    fillimg = vgradient(*m.size, GOLD_STOPS) if fill == "gold" else Image.new("RGB", m.size, fill)
    layer = fillimg.convert("RGBA")
    layer.putalpha(m)
    c.alpha_composite(layer, (x, y))
    return m.height


def gold_bar(c, box, width):
    x0, y0, x1, y1 = box
    g = vgradient(x1 - x0, y1 - y0, GOLD_STOPS).convert("RGBA")
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, g.height - 1), 22, outline=255, width=width)
    g.putalpha(m)
    c.alpha_composite(g, (x0, y0))


def pill(c, cx, y, text, gold):
    m = text_mask(text, 44)
    w, h = m.width + 70, m.height + 36
    x = int(cx - w / 2)
    bg = vgradient(w, h, GOLD_STOPS if gold else [GREEN, DGREEN]).convert("RGBA")
    pm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(pm).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    bg.putalpha(pm)
    c.alpha_composite(bg, (x, y))
    if not gold:
        gold_bar(c, (x, y, x + w, y + h), 4)
    draw_text(c, cx, y + 16, text, 44, INK if gold else "gold")


def background():
    c = vgradient(W, H, [GREEN, DGREEN, (4, 28, 12)]).convert("RGBA")
    vign = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vign).ellipse((-300, -200, W + 300, H + 200), fill=255)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 150))
    dark.putalpha(ImageOps.invert(vign.filter(ImageFilter.GaussianBlur(160))).point(lambda v: v * 0.6))
    c.alpha_composite(dark)
    gold_bar(c, (18, 18, W - 18, H - 18), 8)
    gold_bar(c, (34, 34, W - 34, H - 34), 2)
    return c


def logo(size):
    l = Image.open(os.path.join(HERE, "logo-phone.webp")).convert("RGB")
    s = min(l.size)
    l = l.crop((int(s * 0.045), int(s * 0.045), int(s * 0.955), int(s * 0.955))).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    l = l.convert("RGBA")
    l.putalpha(m)
    return l


def photo(c, src, box):
    x0, y0, x1, y1 = box
    im = ImageOps.fit(Image.open(os.path.join(IMG, src)).convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS)
    c.paste(im, (x0, y0))
    gold_bar(c, (x0 - 8, y0 - 8, x1 + 8, y1 + 8), 8)


def footer(c):
    y = H - 190
    band = vgradient(W - 72, 150, [GREEN, DGREEN]).convert("RGBA")
    c.alpha_composite(band, (36, y))
    for yy in (y, y + 148):
        c.alpha_composite(vgradient(W - 72, 4, GOLD_STOPS).convert("RGBA"), (36, yy))
    draw_text(c, W / 2, y + 20, "PARKET LUX", 64)
    draw_text(c, W / 2, y + 100, "558 61 11 62  •  WhatsApp 599 90 70 47", 30, WHITE)


def before_after(bf, af, title, out):
    c = background()
    lg = logo(170)
    c.alpha_composite(lg, (60, 52))
    draw_text(c, 640, 95, title, 58, max_w=760)
    draw_text(c, 640, 180, "ციკლოვკა • ლაქირება • რესტავრაცია", 28, WHITE, max_w=760)
    top, bot, pw, gap = 270, H - 225, 465, 38
    x0 = (W - 2 * pw - gap) // 2
    for i, (src, lab) in enumerate([(bf, "მანამდე"), (af, "შემდეგ")]):
        x = x0 + i * (pw + gap)
        photo(c, src, (x, top, x + pw, bot))
        pill(c, x + pw / 2, bot - 110, lab, gold=i == 1)
    footer(c)
    c.convert("RGB").save(os.path.join(OUT, out), quality=92)


def offer(bg, out):
    c = background()
    im = ImageOps.fit(Image.open(os.path.join(IMG, bg)).convert("RGB"), (W - 72, 520), Image.LANCZOS)
    c.paste(im, (36, 36))
    fade = vgradient(W - 72, 520, [(0, 0, 0), (0, 0, 0)]).convert("RGBA")
    fade.putalpha(Image.linear_gradient("L").resize((W - 72, 520)).point(lambda v: int(v * 0.9)))
    c.alpha_composite(fade, (36, 36))
    c.alpha_composite(logo(300), ((W - 300) // 2, 300))
    draw_text(c, W / 2, 640, "გთავაზობთ იატაკის განახლებას", 56, max_w=940)
    draw_text(c, W / 2, 725, "გერმანული აპარატებითა და ლაქებით", 36, WHITE, max_w=940)
    draw_text(c, W / 2, 800, "სრული ხარჯი", 40, WHITE)
    pb = (230, 870, W - 230, 1040)
    g = vgradient(pb[2] - pb[0], pb[3] - pb[1], GOLD_STOPS).convert("RGBA")
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, g.height - 1), 40, fill=255)
    g.putalpha(m)
    c.alpha_composite(g, pb[:2])
    draw_text(c, W / 2, 895, "30 ₾-დან", 96, INK)
    draw_text(c, W / 2, 1060, "კვადრატულ მეტრზე", 40, "gold")
    footer(c)
    c.convert("RGB").save(os.path.join(OUT, out), quality=92)


def why_us(bg, out):
    c = background()
    im = ImageOps.fit(Image.open(os.path.join(IMG, bg)).convert("RGB"), (W - 72, 560), Image.LANCZOS, centering=(0.5, 0.6))
    c.paste(im, (36, 36))
    gold_bar(c, (36, 36, W - 36, 596), 6)
    c.alpha_composite(logo(220), ((W - 220) // 2, 480))
    draw_text(c, W / 2, 725, "რატომ Parket Lux?", 60)
    items = ["გერმანული აპარატი — უმტვერო ციკლოვკა", "ევროპული ლაქი — პრიალა ან მატოვი",
             "2006 წლიდან — 20 წლის გამოცდილება", "მთელ თბილისში და შემოგარენში"]
    for i, t in enumerate(items):
        y = 830 + i * 72
        c.alpha_composite(vgradient(18, 18, GOLD_STOPS).convert("RGBA"), (110, y + 14))
        m = text_mask(t, 34)
        layer = Image.new("RGBA", m.size, WHITE)
        layer.putalpha(m)
        c.alpha_composite(layer, (150, y))
    footer(c)
    c.convert("RGB").save(os.path.join(OUT, out), quality=92)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    before_after("3.jpg", "2.jpg", "ძველი პარკეტი ახალივით", "01-herringbone.jpg")
    offer("5.jpg", "02-offer-30.jpg")
    before_after("4.webp", "5.jpg", "მხატვრული პარკეტის ციკლოვკა", "03-patterned.jpg")
    why_us("10.webp", "04-why-us.jpg")
    before_after("8.webp", "9.webp", "ფიცრის იატაკის ლაქირება", "05-plank.jpg")
    before_after("11.webp", "10.webp", "პარკეტის უმტვერო ციკლოვკა", "06-dust-free.jpg")
    before_after("6.webp", "7.webp", "ვარსკვლავებიანი პარკეტის ციკლოვკა", "07-star.jpg")
