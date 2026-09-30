"""Builds a fast, Reels-style 1080x1920 video from a long walkthrough clip.

Hook text in the first second, the clip sped up, kinetic captions every few seconds,
a gold progress bar, a brand bar, and the animated price/contact ending.

Usage: python3 build_viral_reel.py <video> <out.mp4> [speed] [music-file]
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

import build_fb as fb
import build_reel as br

W, H, FPS = 1080, 1920, 30
HOOK = ("ასე ბზინავს იატაკი", "ციკლოვკის შემდეგ ✨")
CAPTIONS = ["უმტვერო ციკლოვკა", "გერმანული აპარატი", "ევროპული ლაქი", "პრიალა ან მატოვი", "2006 წლიდან"]


def hook_sprites():
    a = br.text_sprite(HOOK[0], 84, fb.WHITE)
    b = br.text_sprite(HOOK[1].replace(" ✨", ""), 96, fb.DGREEN)
    plate = Image.new("RGBA", (b.width + 70, b.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle((0, 0, plate.width - 1, plate.height - 1), 28, fill=fb.GOLD)
    plate.alpha_composite(b, (35, 15))
    return a, plate


def caption_sprite(text):
    t = br.text_sprite(text, 78, fb.LGOLD)
    plate = Image.new("RGBA", (t.width + 80, t.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle((0, 0, plate.width - 1, plate.height - 1), 30,
                                            fill=fb.DGREEN + (225,), outline=fb.GOLD, width=5)
    plate.alpha_composite(t, (40, 20))
    return plate


def brand_bar():
    bar = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    g = fb.gradient(W, 170, fb.GREEN, fb.DGREEN).convert("RGBA")
    g.putalpha(210)
    bar.alpha_composite(g)
    ImageDraw.Draw(bar).line((0, 2, W, 2), fill=fb.GOLD, width=5)
    bar.alpha_composite(fb.badge(130), (40, 20))
    d = ImageDraw.Draw(bar)
    d.text((200, 28), "PARKET LUX", font=fb.f(54), fill=fb.LGOLD)
    d.text((200, 96), fb.PHONE, font=fb.f(40), fill=fb.WHITE)
    return bar


def compose(frames_dir, out_dir, clip_len):
    a, b = hook_sprites()
    caps = [caption_sprite(c) for c in CAPTIONS]
    bar = brand_bar()
    slot = (clip_len - 3.0) / len(caps)
    files = sorted(os.listdir(frames_dir))
    for i, name in enumerate(files):
        t = i / FPS
        c = Image.open(os.path.join(frames_dir, name)).convert("RGBA")
        # Soft dark top gradient keeps text readable on bright floors.
        shade = Image.linear_gradient("L").rotate(180).resize((W, 700)).point(lambda v: int(v * 0.55))
        dark = Image.new("RGBA", (W, 700), (0, 0, 0, 255))
        dark.putalpha(shade)
        c.alpha_composite(dark)
        if t < 3.2:
            out = max(0, (t - 2.8) / 0.4)
            if out < 1:
                br.place(c, a, W / 2, 330 - out * 80, t, 0.05, "pop", 0.5)
                br.place(c, b, W / 2, 450 - out * 80, t, 0.35, "pop", 0.55)
        else:
            k = min(int((t - 3.0) // slot), len(caps) - 1)
            local = t - (3.0 + k * slot)
            if local < slot - 0.25:
                br.place(c, caps[k], W / 2, 340, local, 0, "pop", 0.45)
        prog = Image.new("RGBA", (max(1, int(W * t / clip_len)), 10), fb.GOLD + (255,))
        c.alpha_composite(prog, (0, 0))
        br.place(c, bar, W / 2, H - 85, t, 0.2, "up", 0.6)
        c.convert("RGB").save(os.path.join(out_dir, name), quality=92)


if __name__ == "__main__":
    video, outfile = sys.argv[1], sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    music = sys.argv[4] if len(sys.argv) > 4 else None
    tmp = os.path.join(os.path.dirname(os.path.abspath(outfile)), "viral_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    raw, comp = os.path.join(tmp, "raw"), os.path.join(tmp, "comp")
    os.makedirs(raw)
    os.makedirs(comp)
    br.TMP = tmp

    br.run(["-i", video, "-vf",
            f"setpts=PTS/{speed},fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=saturation=1.15:contrast=1.05,unsharp=5:5:0.6",
            "-q:v", "3", os.path.join(raw, "%05d.jpg")])
    clip_len = len(os.listdir(raw)) / FPS
    compose(raw, comp, clip_len)
    frame = os.path.join(raw, sorted(os.listdir(raw))[len(os.listdir(raw)) // 2])
    seq_out = br.outro(frame)

    xf, t_out = 0.5, br.T_OUT
    total = clip_len + t_out - xf
    audio_in = ["-i", music] if music else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    fc = (
        f"[0:v]fps={FPS},format=yuv420p,settb=AVTB[v];"
        f"[1:v]fps={FPS},format=yuv420p,settb=AVTB[o];"
        f"[v][o]xfade=transition=zoomin:duration={xf}:offset={clip_len - xf},"
        f"fade=out:st={total - 1.0}:d=1.0[outv];"
        f"[2:a]atrim=0:{total},afade=in:st=0:d=0.5,afade=out:st={total - 1.5}:d=1.5[outa]"
    )
    br.run([
        "-framerate", str(FPS), "-i", os.path.join(comp, "%05d.jpg"),
        "-framerate", str(FPS), "-i", seq_out,
        *audio_in,
        "-filter_complex", fc, "-map", "[outv]", "-map", "[outa]", "-t", str(total),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", outfile,
    ])
    shutil.rmtree(tmp, ignore_errors=True)
    print(outfile, round(total, 1), "s")
