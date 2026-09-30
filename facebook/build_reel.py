"""Builds a 1080x1920 Parket Lux Reel from a work video, in the Facebook post style.

Usage: python3 build_reel.py <video> <photos-dir> <out.mp4>
"""
import os
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import build_fb as fb

W, H = 1080, 1920
VIDEO, PHOTOS, OUTFILE = sys.argv[1], sys.argv[2], sys.argv[3]
TMP = os.path.join(os.path.dirname(os.path.abspath(OUTFILE)), "reel_tmp")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
fb.IMG = PHOTOS


def ctext(d, y, s, size, fill):
    while d.textlength(s, font=fb.f(size)) > W - 140:
        size -= 2
    d.text(((W - d.textlength(s, font=fb.f(size))) / 2, y), s, font=fb.f(size), fill=fill)


def card_bg(src):
    c = ImageOps.fit(Image.open(src).convert("RGB"), (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(4))
    shade = fb.gradient(W, H, fb.GREEN, fb.DGREEN).convert("RGBA")
    shade.putalpha(185)
    c = c.convert("RGBA")
    c.alpha_composite(shade)
    c = c.convert("RGB")
    ImageDraw.Draw(c).rounded_rectangle((36, 36, W - 36, H - 36), 36, outline=fb.GOLD, width=7)
    return c


def paste_logo(c, size, y):
    lg = fb.badge(size)
    c.paste(lg, ((W - size) // 2, y), lg)


def intro(frame):
    c = card_bg(frame)
    d = ImageDraw.Draw(c)
    paste_logo(c, 420, 380)
    ctext(d, 900, "პარკეტის ციკლოვკა", 92, fb.LGOLD)
    d.line((220, 1040, W - 220, 1040), fill=fb.GOLD, width=4)
    ctext(d, 1080, "უმტვეროდ • გერმანული აპარატით", 52, fb.WHITE)
    ctext(d, 1160, "2006 წლიდან", 52, fb.WHITE)
    return c


def overlay():
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    band = fb.gradient(W, 190, fb.GREEN, fb.DGREEN).convert("RGBA")
    band.putalpha(215)
    c.alpha_composite(band, (0, 0))
    c.alpha_composite(band, (0, H - 230))
    d = ImageDraw.Draw(c)
    d.line((0, 190, W, 190), fill=fb.GOLD, width=5)
    d.line((0, H - 230, W, H - 230), fill=fb.GOLD, width=5)
    ctext(d, 55, "უმტვერო ციკლოვკა", 72, fb.LGOLD)
    lg = fb.badge(170)
    c.alpha_composite(lg, (50, H - 200))
    d.text((250, H - 185), "PARKET LUX", font=fb.f(62), fill=fb.LGOLD)
    d.text((250, H - 105), fb.PHONE, font=fb.f(46), fill=fb.WHITE)
    return c


def result(after):
    c = card_bg(after)
    d = ImageDraw.Draw(c)
    ctext(d, 150, "შედეგი", 96, fb.LGOLD)
    pw, ph, top = 900, 1300, 330
    x = (W - pw) // 2
    d.rounded_rectangle((x - 9, top - 9, x + pw + 9, top + ph + 9), 24, fill=fb.GOLD)
    c.paste(ImageOps.fit(Image.open(after).convert("RGB"), (pw, ph), Image.LANCZOS), (x, top))
    ctext(d, top + ph + 60, "ლაქით დაფარული იატაკი — ახალივით", 50, fb.WHITE)
    return c


def outro(frame):
    c = card_bg(frame)
    d = ImageDraw.Draw(c)
    paste_logo(c, 380, 300)
    ctext(d, 760, "იატაკის განახლება", 84, fb.LGOLD)
    ctext(d, 880, "სრული ხარჯი", 56, fb.WHITE)
    d.rounded_rectangle((200, 980, W - 200, 1170), 44, fill=fb.GOLD)
    ctext(d, 995, "30 ₾-დან", 116, fb.DGREEN)
    ctext(d, 1195, "კვადრატულ მეტრზე", 56, fb.LGOLD)
    d.line((220, 1320, W - 220, 1320), fill=fb.GOLD, width=4)
    ctext(d, 1370, fb.PHONE, 66, fb.WHITE)
    ctext(d, 1470, fb.WHATSAPP, 50, fb.LGOLD)
    return c


def run(args):
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    frame = os.path.join(TMP, "frame.jpg")
    run(["-ss", "5", "-i", VIDEO, "-frames:v", "1", frame])
    after = os.path.join(PHOTOS, "5.jpg")
    for name, img in [("intro", intro(frame)), ("result", result(after)), ("outro", outro(frame))]:
        img.save(os.path.join(TMP, name + ".png"))
    overlay().save(os.path.join(TMP, "overlay.png"))

    card = "scale=1080:1920,fps=30,format=yuv420p,setsar=1"
    fc = (
        f"[0:v]{card},fade=in:0:15,fade=out:st=2.2:d=0.3[i];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[vv];"
        "[vv][2:v]overlay=0:0,format=yuv420p[v];"
        f"[3:v]{card},fade=in:0:10,fade=out:st=2.7:d=0.3[r];"
        f"[4:v]{card},fade=in:0:10[o];"
        "[5:a]atrim=0:2.5[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
        "[5:a]atrim=0:3[a2];[5:a]atrim=0:3.5[a3];"
        "[i][a0][v][a1][r][a2][o][a3]concat=n=4:v=1:a=1[outv][outa]"
    )
    run([
        "-loop", "1", "-t", "2.5", "-i", os.path.join(TMP, "intro.png"),
        "-i", VIDEO,
        "-i", os.path.join(TMP, "overlay.png"),
        "-loop", "1", "-t", "3", "-i", os.path.join(TMP, "result.png"),
        "-loop", "1", "-t", "3.5", "-i", os.path.join(TMP, "outro.png"),
        "-f", "lavfi", "-t", "4", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex", fc, "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", OUTFILE,
    ])
    print(OUTFILE)
