from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
IMG = "../images/"
GEO = "geo-ExtraBold.ttf"; LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GREEN, DGREEN, GOLD, LGOLD = (20,96,45), (11,62,28), (212,160,23), (245,208,90)

def cover(im, w, h):
    return ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.5))

def badge(size):
    b = Image.open(IMG + "1.jpg").convert("RGB").crop((78, 78, 946, 946)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size-1, size-1), fill=255)
    b.putalpha(m); return b

def ctext(d, cx, y, s, font, fill):
    w = d.textlength(s, font=font); d.text((cx - w/2, y), s, font=font, fill=fill)

def gradient(w, h, a, b):
    g = Image.new("RGB", (w, h), a); d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / h; d.line((0, y, w, y), fill=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)))
    return g

def before_after(bf, af, out):
    W, H, HD, FT = 1600, 1200, 150, 110
    c = Image.new("RGB", (W, H)); c.paste(gradient(W, H, GREEN, DGREEN))
    d = ImageDraw.Draw(c)
    bg = badge(120); c.paste(bg, (30, 15), bg)
    ctext(d, W/2 + 40, 28, "პარკეტის ციკლოვკა და ლაქირება", ImageFont.truetype(GEO, 58), LGOLD)
    d.line((180, HD - 12, W - 40, HD - 12), fill=GOLD, width=4)
    pw, ph, gap = 740, H - HD - FT - 20, 40
    x0 = (W - 2*pw - gap) // 2
    lf = ImageFont.truetype(GEO, 44)
    for i, (src, lab) in enumerate([(bf, "მანამდე"), (af, "შემდეგ")]):
        x = x0 + i*(pw + gap); y = HD + 10
        d.rounded_rectangle((x-8, y-8, x+pw+8, y+ph+8), 18, fill=GOLD)
        c.paste(cover(Image.open(IMG + src), pw, ph), (x, y))
        tw = d.textlength(lab, font=lf); px, py = x + pw/2 - tw/2 - 34, y + ph - 100
        d.rounded_rectangle((px, py, px + tw + 68, py + 76), 38, fill=DGREEN if i == 0 else GOLD, outline=GOLD, width=4)
        d.text((px + 34, py + 6), lab, font=lf, fill=LGOLD if i == 0 else DGREEN)
    ctext(d, W/2, H - FT + 28, "PARKET LUX  •  +995 558 61 11 62", ImageFont.truetype(LAT, 46), LGOLD)
    c.save(out, quality=90)

def cover_photo(src, out):
    W, H = 1600, 900
    c = cover(Image.open(IMG + src), W, H)
    band = Image.new("RGBA", (W, 170), (11, 62, 28, 215)); c.paste(band, (0, H - 170), band)
    d = ImageDraw.Draw(c); d.line((0, H - 170, W, H - 170), fill=GOLD, width=5)
    bg = badge(210); c.paste(bg, (40, H - 245), bg)
    d.text((280, H - 150), "პარკეტის ციკლოვკა და ლაქირება", font=ImageFont.truetype(GEO, 56), fill=LGOLD)
    d.text((282, H - 70), "PARKET LUX  •  +995 558 61 11 62", font=ImageFont.truetype(LAT, 40), fill=(255, 255, 255))
    c.save(out, quality=90)

before_after("3.jpg", "2.jpg", "before-after-1.jpg")
before_after("4.webp", "5.jpg", "before-after-2.jpg")
cover_photo("5.jpg", "cover.jpg")
