"""Builds an animated 1080x1920 Parket Lux Reel from a work video, in the Facebook post style.

Usage: python3 build_reel.py <video> <photos-dir> <out.mp4> [music-file]

The machine sound is dropped. Pass a music file only if you have the rights to use it;
otherwise the Reel is silent and music can be added in the Facebook app.
"""
import math
import os
import shutil
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import build_fb as fb

W, H, FPS = 1080, 1920, 30
VIDEO, PHOTOS, OUTFILE = sys.argv[1], sys.argv[2], sys.argv[3]
MUSIC = sys.argv[4] if len(sys.argv) > 4 else None
TMP = os.path.join(os.path.dirname(os.path.abspath(OUTFILE)), "reel_tmp")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
T_IN, T_RES, T_OUT, XF = 3.5, 4.5, 4.5, 0.6


def ease(p):
    return 1 - (1 - p) ** 3


def ease_back(p):
    c1 = 1.70158
    return 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2


def text_sprite(s, size, fill, max_w=W - 140):
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    while probe.textlength(s, font=fb.f(size)) > max_w:
        size -= 2
    font = fb.f(size)
    x0, y0, x1, y1 = probe.textbbox((0, 0), s, font=font)
    pad = 12
    im = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), s, font=font, fill=(0, 0, 0, 150))
    im = im.filter(ImageFilter.GaussianBlur(4))
    ImageDraw.Draw(im).text((pad - x0 - 2, pad - y0 - 3), s, font=font, fill=fill)
    return im


def pill_sprite(w, h, text, size, fill, color):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2 if h < 120 else 44, fill=fill, outline=fb.GOLD, width=4)
    t = text_sprite(text, size, color)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return im


def line_sprite(w):
    return Image.new("RGBA", (w, 5), fb.GOLD + (255,))


def place(c, sprite, cx, cy, t, start, kind, dur=0.6):
    """Draws a sprite animating in: 'up' (fade + rise), 'pop' (springy scale) or 'wipe' (grows from center)."""
    p = min(max((t - start) / dur, 0), 1)
    if p <= 0:
        return
    sp, alpha, dy = sprite, ease(p), 0
    if kind == "up":
        dy = (1 - ease(p)) * 70
    elif kind == "pop":
        s = max(ease_back(p), 0.02)
        sp = sprite.resize((max(1, int(sprite.width * s)), max(1, int(sprite.height * s))), Image.LANCZOS)
        alpha = min(1, p * 2.5)
    elif kind == "wipe":
        w = max(1, int(sprite.width * ease(p)))
        sp = sprite.crop(((sprite.width - w) // 2, 0, (sprite.width + w) // 2, sprite.height))
        alpha = 1
    if alpha < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2 + dy)))


def make_bg(src):
    c = ImageOps.fit(Image.open(src).convert("RGB"), (int(W * 1.12), int(H * 1.12)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
    shade = fb.gradient(c.width, c.height, fb.GREEN, fb.DGREEN).convert("RGBA")
    shade.putalpha(190)
    c = c.convert("RGBA")
    c.alpha_composite(shade)
    return c


def bg_at(bg, p):
    """Background with a slow Ken Burns zoom, p in [0, 1]."""
    z = 1.12 - 0.1 * p
    w, h = int(W * z), int(H * z)
    x, y = (bg.width - w) // 2, (bg.height - h) // 2
    c = bg.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS)
    ImageDraw.Draw(c).rounded_rectangle((36, 36, W - 36, H - 36), 36, outline=fb.GOLD, width=7)
    return c


def render(name, dur, bg, draw):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    n = int(dur * FPS)
    for i in range(n):
        c = bg_at(bg, i / n)
        draw(c, i / FPS)
        c.convert("RGB").save(os.path.join(d, f"{i:04d}.jpg"), quality=93)
    return os.path.join(d, "%04d.jpg")


def intro(frame):
    logo = fb.badge(420)
    title = text_sprite("პარკეტის ციკლოვკა", 92, fb.LGOLD)
    line = line_sprite(640)
    s1 = text_sprite("უმტვეროდ • გერმანული აპარატით", 52, fb.WHITE)
    s2 = text_sprite("2006 წლიდან", 52, fb.WHITE)

    def draw(c, t):
        place(c, logo, W / 2, 620, t, 0.2, "pop", 0.8)
        place(c, title, W / 2, 1000, t, 0.8, "up")
        place(c, line, W / 2, 1090, t, 1.1, "wipe", 0.7)
        place(c, s1, W / 2, 1160, t, 1.3, "up")
        place(c, s2, W / 2, 1240, t, 1.5, "up")
    return render("intro", T_IN, make_bg(frame), draw)


def result(before, after):
    """Before photo, then a gold divider sweeps across revealing the finished floor."""
    title = text_sprite("შედეგი", 96, fb.LGOLD)
    pw, ph, x0, y0 = 900, 1300, 90, 330
    bimg = ImageOps.fit(Image.open(before).convert("RGB"), (pw, ph), Image.LANCZOS)
    aimg = ImageOps.fit(Image.open(after).convert("RGB"), (pw, ph), Image.LANCZOS)
    lab_b = pill_sprite(300, 76, "მანამდე", 42, fb.DGREEN, fb.LGOLD)
    lab_a = pill_sprite(300, 76, "შემდეგ", 42, fb.GOLD, fb.DGREEN)
    cap = text_sprite("ლაქით დაფარული იატაკი — ახალივით", 50, fb.WHITE)

    def draw(c, t):
        place(c, title, W / 2, 200, t, 0.1, "up")
        if t > 0.3:
            frame = Image.new("RGBA", (pw + 18, ph + 18), (0, 0, 0, 0))
            ImageDraw.Draw(frame).rounded_rectangle((0, 0, pw + 17, ph + 17), 24, fill=fb.GOLD)
            photo = bimg.copy()
            w = int(pw * ease(min(max((t - 1.3) / 1.6, 0), 1)))
            if w > 0:
                photo.paste(aimg.crop((0, 0, w, ph)), (0, 0))
                ImageDraw.Draw(photo).rectangle((w - 4, 0, w + 4, ph), fill=fb.GOLD)
            frame.paste(photo, (9, 9))
            place(c, frame, W / 2, y0 + ph / 2, t, 0.3, "up", 0.5)
        place(c, lab_b, x0 + 190, y0 + 70, t, 0.6, "pop")
        place(c, lab_a, x0 + pw - 190, y0 + 70, t, 2.8, "pop")
        place(c, cap, W / 2, y0 + ph + 110, t, 3.1, "up")
    return render("result", T_RES, make_bg(after), draw)


def outro(frame):
    logo = fb.badge(380)
    title = text_sprite("იატაკის განახლება", 84, fb.LGOLD)
    full = text_sprite("სრული ხარჯი", 56, fb.WHITE)
    price = pill_sprite(680, 190, "30 ₾-დან", 116, fb.GOLD, fb.DGREEN)
    per = text_sprite("კვადრატულ მეტრზე", 56, fb.LGOLD)
    line = line_sprite(640)
    phone = text_sprite(fb.PHONE, 66, fb.WHITE)
    wa = text_sprite(fb.WHATSAPP, 50, fb.LGOLD)

    def draw(c, t):
        place(c, logo, W / 2, 500, t, 0.1, "pop", 0.8)
        place(c, title, W / 2, 810, t, 0.5, "up")
        place(c, full, W / 2, 920, t, 0.8, "up")
        if t > 1.9:
            s = 1 + 0.035 * math.sin((t - 1.9) * 5)
            sp = price.resize((int(price.width * s), int(price.height * s)), Image.LANCZOS)
            c.alpha_composite(sp, (int(W / 2 - sp.width / 2), int(1075 - sp.height / 2)))
        else:
            place(c, price, W / 2, 1075, t, 1.1, "pop", 0.8)
        place(c, per, W / 2, 1235, t, 1.5, "up")
        place(c, line, W / 2, 1330, t, 1.8, "wipe", 0.7)
        place(c, phone, W / 2, 1410, t, 2.0, "up")
        place(c, wa, W / 2, 1505, t, 2.2, "up")
    return render("outro", T_OUT, make_bg(frame), draw)


def bands():
    top = fb.gradient(W, 190, fb.GREEN, fb.DGREEN).convert("RGBA")
    top.putalpha(220)
    ImageDraw.Draw(top).line((0, 187, W, 187), fill=fb.GOLD, width=5)
    t = text_sprite("უმტვერო ციკლოვკა", 72, fb.LGOLD)
    top.alpha_composite(t, ((W - t.width) // 2, (190 - t.height) // 2))
    bot = fb.gradient(W, 230, fb.GREEN, fb.DGREEN).convert("RGBA")
    bot.putalpha(220)
    ImageDraw.Draw(bot).line((0, 2, W, 2), fill=fb.GOLD, width=5)
    bot.alpha_composite(fb.badge(170), (50, 30))
    ImageDraw.Draw(bot).text((250, 45), "PARKET LUX", font=fb.f(62), fill=fb.LGOLD)
    ImageDraw.Draw(bot).text((250, 125), fb.PHONE, font=fb.f(46), fill=fb.WHITE)
    top.save(os.path.join(TMP, "top.png"))
    bot.save(os.path.join(TMP, "bot.png"))


def run(args):
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    frame = os.path.join(TMP, "frame.jpg")
    run(["-ss", "5", "-i", VIDEO, "-frames:v", "1", frame])
    vdur = float(subprocess.run([FFMPEG, "-i", VIDEO], capture_output=True, text=True).stderr
                 .split("Duration: ")[1].split(",")[0].split(":")[2])
    total = T_IN + vdur + T_RES + T_OUT - 3 * XF
    seq_in = intro(frame)
    seq_res = result(os.path.join(PHOTOS, "4.webp"), os.path.join(PHOTOS, "5.jpg"))
    seq_out = outro(frame)
    bands()

    slide = "pow(1-min(1\\,t/0.7)\\,3)"
    fc = (
        "[0:v]fps=30,format=yuv420p,settb=AVTB,fade=in:st=0:d=0.8[i];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,setpts=PTS-STARTPTS[vv];"
        f"[vv][2:v]overlay=x=0:y=-200*{slide}:shortest=1[v1];"
        f"[v1][3:v]overlay=x=0:y=main_h-230+240*{slide}:shortest=1,fps=30,format=yuv420p,settb=AVTB[v];"
        "[4:v]fps=30,format=yuv420p,settb=AVTB[r];"
        "[5:v]fps=30,format=yuv420p,settb=AVTB[o];"
        f"[i][v]xfade=transition=smoothup:duration={XF}:offset={T_IN - XF}[x1];"
        f"[x1][r]xfade=transition=slideleft:duration={XF}:offset={T_IN + vdur - 2 * XF}[x2];"
        f"[x2][o]xfade=transition=fade:duration={XF}:offset={T_IN + vdur + T_RES - 3 * XF},"
        f"fade=out:st={total - 1.2}:d=1.2[outv];"
        f"[6:a]atrim=0:{total},afade=in:st=0:d=1.5,afade=out:st={total - 2}:d=2[outa]"
    )
    audio_in = ["-i", MUSIC] if MUSIC else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    run([
        "-framerate", "30", "-i", seq_in,
        "-i", VIDEO,
        "-loop", "1", "-framerate", "30", "-i", os.path.join(TMP, "top.png"),
        "-loop", "1", "-framerate", "30", "-i", os.path.join(TMP, "bot.png"),
        "-framerate", "30", "-i", seq_res,
        "-framerate", "30", "-i", seq_out,
        *audio_in,
        "-filter_complex", fc, "-map", "[outv]", "-map", "[outa]", "-t", str(total),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUTFILE,
    ])
    shutil.rmtree(TMP, ignore_errors=True)
    print(OUTFILE)
