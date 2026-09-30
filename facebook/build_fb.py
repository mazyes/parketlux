"""Builds Parket Lux Facebook post images (1080x1080), flat green/gold style.

Usage: python3 build_fb.py <photos-dir>
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = sys.argv[1] if len(sys.argv) > 1 else "."
FONT = os.path.join(HERE, "fonts/FiraGO-ExtraBold.ttf")
OUT = os.path.join(HERE, "posts")
W = H = 1080
GREEN, DGREEN, GOLD, LGOLD, WHITE = (20, 96, 45), (11, 62, 28), (212, 160, 23), (245, 208, 90), (255, 255, 255)
PHONE, WHATSAPP = "+995 558 61 11 62", "WhatsApp: 599 90 70 47"


def f(n):
    return ImageFont.truetype(FONT, n)


def gradient(w, h, a, b):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / h
        d.line((0, y, w, y), fill=tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)))
    return g


def ctext(d, y, s, size, fill, max_w=W - 120):
    while d.textlength(s, font=f(size)) > max_w:
        size -= 2
    d.text(((W - d.textlength(s, font=f(size))) / 2, y), s, font=f(size), fill=fill)


def background(src):
    c = ImageOps.fit(Image.open(os.path.join(IMG, src)).convert("RGB"), (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    shade = gradient(W, H, GREEN, DGREEN).convert("RGBA")
    shade.putalpha(175)
    c = c.convert("RGBA")
    c.alpha_composite(shade)
    c = c.convert("RGB")
    ImageDraw.Draw(c).rounded_rectangle((30, 30, W - 30, H - 30), 30, outline=GOLD, width=6)
    return c


def badge(size):
    b = Image.open(os.path.join(HERE, "logo.jpg")).convert("RGB").crop((78, 78, 946, 946)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    b.putalpha(m)
    return b


def contacts(c, y):
    d = ImageDraw.Draw(c)
    ctext(d, y, PHONE, 38, WHITE)
    ctext(d, y + 50, WHATSAPP, 30, LGOLD)


def before_after(bf, af, title, out):
    c = background(af)
    d = ImageDraw.Draw(c)
    lg = badge(150)
    c.paste(lg, ((W - 150) // 2, 55), lg)
    ctext(d, 215, title, 52, LGOLD)
    pw, ph, gap, top = 440, 590, 40, 300
    x0 = (W - 2 * pw - gap) // 2
    for i, (src, lab) in enumerate([(bf, "მანამდე"), (af, "შემდეგ")]):
        x = x0 + i * (pw + gap)
        d.rounded_rectangle((x - 7, top - 7, x + pw + 7, top + ph + 7), 18, fill=GOLD)
        c.paste(ImageOps.fit(Image.open(os.path.join(IMG, src)).convert("RGB"), (pw, ph), Image.LANCZOS), (x, top))
        tw = d.textlength(lab, font=f(40))
        px, py = x + pw / 2 - tw / 2 - 30, top + ph - 90
        d.rounded_rectangle((px, py, px + tw + 60, py + 68), 34, fill=DGREEN if i == 0 else GOLD, outline=GOLD, width=4)
        d.text((px + 30, py + 8), lab, font=f(40), fill=LGOLD if i == 0 else DGREEN)
    contacts(c, 920)
    c.save(os.path.join(OUT, out), quality=92)


def offer(src, out):
    c = background(src)
    d = ImageDraw.Draw(c)
    lg = badge(250)
    c.paste(lg, ((W - 250) // 2, 70), lg)
    ctext(d, 360, "გთავაზობთ", 52, WHITE)
    ctext(d, 430, "იატაკის განახლებას", 72, LGOLD)
    ctext(d, 530, "გერმანული აპარატებით და ლაქებით", 44, WHITE)
    d.line((200, 620, W - 200, 620), fill=GOLD, width=3)
    ctext(d, 650, "სრული ხარჯი", 46, WHITE)
    d.rounded_rectangle((200, 730, W - 200, 900), 40, fill=GOLD)
    ctext(d, 745, "30 ₾-დან", 100, DGREEN)
    ctext(d, 915, "კვადრატულ მეტრზე", 48, LGOLD)
    ctext(d, 985, PHONE, 36, WHITE)
    c.save(os.path.join(OUT, out), quality=92)


def why_us(src, out):
    c = background(src)
    d = ImageDraw.Draw(c)
    lg = badge(250)
    c.paste(lg, ((W - 250) // 2, 70), lg)
    ctext(d, 360, "რატომ Parket Lux?", 64, LGOLD)
    d.line((200, 460, W - 200, 460), fill=GOLD, width=3)
    items = ["გერმანული აპარატი — უმტვერო ციკლოვკა", "ევროპული ლაქი — პრიალა ან მატოვი",
             "2006 წლიდან — 20 წლის გამოცდილება", "მთელ თბილისში და შემოგარენში"]
    x0 = (W - max(d.textlength(t, font=f(38)) for t in items) - 44) / 2
    for i, t in enumerate(items):
        y = 500 + i * 80
        d.rounded_rectangle((x0, y + 14, x0 + 20, y + 34), 4, fill=GOLD)
        d.text((x0 + 44, y), t, font=f(38), fill=WHITE)
    d.line((200, 840, W - 200, 840), fill=GOLD, width=3)
    contacts(c, 880)
    c.save(os.path.join(OUT, out), quality=92)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    before_after("3.jpg", "2.jpg", "ძველი პარკეტი ახალივით", "01-herringbone.jpg")
    offer("5.jpg", "02-offer-30.jpg")
    before_after("4.webp", "5.jpg", "მხატვრული პარკეტის ციკლოვკა", "03-patterned.jpg")
    why_us("10.webp", "04-why-us.jpg")
    before_after("8.webp", "9.webp", "ფიცრის იატაკის ლაქირება", "05-plank.jpg")
    before_after("11.webp", "10.webp", "პარკეტის უმტვერო ციკლოვკა", "06-dust-free.jpg")
    before_after("6.webp", "7.webp", "ვარსკვლავებიანი პარკეტის ციკლოვკა", "07-star.jpg")
    before_after("17.webp", "18.webp", "ფიცრის იატაკი ახალივით", "08-plank-gloss.jpg")
