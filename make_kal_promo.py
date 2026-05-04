"""Render a clean, premium KAL promo video.

Creative direction:
- Minimal black/lime/white palette from the site.
- Slow editorial pacing.
- Crisp typography, almost no visual noise.
- Logo used as a quiet mark, not over-animated.
"""

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "promo_frames"
OUT = ROOT / "KAL_promo_video.mp4"
LOGO = ROOT / "logo.png"

W, H = 1920, 1080
FPS = 30
DURATION = 16
TOTAL = FPS * DURATION

BLACK = (0, 0, 0)
INK = (5, 5, 5)
CHARCOAL = (14, 14, 14)
WHITE = (255, 255, 255)
LIME = (223, 255, 0)
SOFT_LIME = (210, 238, 18)
GREY = (155, 155, 155)

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
    Path("C:/Windows/Fonts/Arial.ttf"),
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p.exists()), None)
if FONT_PATH is None:
    raise SystemExit("Could not find a usable Windows font")

def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)

F_KAL = font(310)
F_HEAD = font(112)
F_SUB = font(42)
F_SMALL = font(28)
F_TINY = font(20)

logo = Image.open(LOGO).convert("RGBA")

if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir()

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def in_out(t, start, fade_in, fade_out, end):
    return min(ease((t - start) / fade_in), ease((end - t) / fade_out))

def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]

def draw_center(draw, y, text, fnt, fill, alpha=255, tracking=0):
    if tracking == 0:
        tw, th = text_size(draw, text, fnt)
        draw.text(((W - tw) / 2, y), text, font=fnt, fill=fill + (int(alpha),))
        return
    widths = [text_size(draw, ch, fnt)[0] for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (W - total) / 2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill + (int(alpha),))
        x += cw + tracking

def add_vignette(img, strength=185):
    border = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.rectangle([-80, -80, W + 80, H + 80], outline=(0, 0, 0, strength), width=260)
    border = border.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(border)

def background(t):
    img = Image.new("RGBA", (W, H), INK + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = int(W * (0.50 + 0.035 * math.sin(t * 0.22)))
    cy = int(H * (0.49 + 0.025 * math.cos(t * 0.18)))
    for r in range(900, 30, -35):
        power = (1 - r / 900) ** 1.65
        alpha = int(30 * power)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIME + (alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(glow)
    add_vignette(img, 170)
    return img

def paste_logo(img, cx, cy, size, alpha=255):
    ratio = logo.width / logo.height
    mark = logo.resize((int(size * ratio), int(size)), Image.Resampling.LANCZOS)
    if alpha < 255:
        mark.putalpha(mark.getchannel("A").point(lambda p: int(p * alpha / 255)))
    img.alpha_composite(mark, (int(cx - mark.width / 2), int(cy - mark.height / 2)))

def draw_rule(draw, y, progress, alpha=210):
    width = 520 * progress
    draw.rectangle([W / 2 - width / 2, y, W / 2 + width / 2, y + 3], fill=LIME + (int(alpha * progress),))

def scene_intro(img, draw, t):
    a = in_out(t, 0.2, 1.2, 0.9, 4.4)
    if a <= 0:
        return
    scale = 1 + 0.035 * (1 - ease((t - 0.2) / 2.0))
    draw_center(draw, 350, "KAL", F_KAL, LIME, 255 * a, tracking=10)
    paste_logo(img, W / 2, 250, 86 * scale, int(230 * a))
    draw_rule(draw, 700, ease((t - 1.0) / 1.4), 190 * a)
    draw_center(draw, 735, "CREATIVE STUDIO", F_SMALL, WHITE, 180 * a, tracking=7)

def scene_phrase(img, draw, t):
    a = in_out(t, 4.1, 1.0, 0.8, 8.0)
    if a <= 0:
        return
    x_offset = int((1 - ease((t - 4.1) / 1.2)) * 34)
    draw.text((165 - x_offset, 360), "YOUR BRAND", font=F_HEAD, fill=WHITE + (int(245 * a),))
    draw.text((165 - x_offset, 488), "DESERVES TO BE", font=F_HEAD, fill=WHITE + (int(245 * a),))
    draw.text((165 - x_offset, 616), "REMEMBERED", font=F_HEAD, fill=LIME + (int(255 * a),))
    # Clean quiet logo on right
    draw.rectangle([1320, 305, 1665, 650], outline=LIME + (int(105 * a),), width=2)
    paste_logo(img, 1492, 478, 145, int(210 * a))

def scene_services(img, draw, t):
    a = in_out(t, 7.7, 1.0, 0.8, 11.6)
    if a <= 0:
        return
    draw_center(draw, 295, "BRANDING, LOGOS", F_HEAD, WHITE, 245 * a)
    draw_center(draw, 420, "AND VISUAL SYSTEMS", F_HEAD, LIME, 245 * a)
    items = ["IDENTITY", "STRATEGY", "PACKAGING", "RECOGNITION"]
    start_x = 430
    y = 660
    for n, item in enumerate(items):
        ia = min(a, ease((t - 8.4 - n * 0.18) / 0.6))
        x = start_x + n * 275
        draw.text((x, y), item, font=F_SMALL, fill=WHITE + (int(165 * ia),))
        draw.rectangle([x, y + 44, x + 155 * ia, y + 47], fill=LIME + (int(180 * ia),))

def scene_end(img, draw, t):
    a = ease((t - 11.2) / 1.2)
    if a <= 0:
        return
    final_fade = 1 - ease((t - 15.2) / 0.8)
    a = min(a, final_fade)
    paste_logo(img, W / 2, 310, 130, int(240 * a))
    draw_center(draw, 430, "BREAK BOUNDARIES", F_HEAD, WHITE, 245 * a)
    draw_center(draw, 565, "WITH KAL", F_HEAD, LIME, 245 * a)
    bw = 310 * ease((t - 12.5) / 1.0)
    bx, by = W / 2 - bw / 2, 760
    draw.rectangle([bx, by, bx + bw, by + 74], fill=LIME + (int(240 * a),))
    if bw > 260:
        draw_center(draw, by + 19, "ENQUIRE", F_SMALL, BLACK, 255 * a, tracking=5)

for frame in range(TOTAL):
    t = frame / FPS
    img = background(t)
    draw = ImageDraw.Draw(img)

    # One restrained animated accent line.
    line_a = int(42 + 18 * math.sin(t * 0.55))
    y = int(910 + 10 * math.sin(t * 0.3))
    draw.rectangle([140, y, W - 140, y + 1], fill=WHITE + (line_a,))
    draw.rectangle([140, y + 8, 140 + (W - 280) * ((t / DURATION) % 1), y + 11], fill=LIME + (130,))

    draw.text((70, 48), "KAL", font=F_TINY, fill=LIME + (210,))
    draw.text((W - 248, 48), "2026 PROMO", font=F_TINY, fill=WHITE + (110,))

    scene_intro(img, draw, t)
    scene_phrase(img, draw, t)
    scene_services(img, draw, t)
    scene_end(img, draw, t)

    # premium letterbox
    draw.rectangle([0, 0, W, 24], fill=BLACK + (210,))
    draw.rectangle([0, H - 24, W, H], fill=BLACK + (210,))

    img.convert("RGB").save(FRAMES / f"frame_{frame:04d}.jpg", quality=96)
    if frame % FPS == 0:
        print(f"rendered {frame // FPS}/{DURATION}s")

cmd = [
    "ffmpeg",
    "-y",
    "-framerate",
    str(FPS),
    "-i",
    str(FRAMES / "frame_%04d.jpg"),
    "-c:v",
    "libx264",
    "-crf",
    "18",
    "-preset",
    "slow",
    "-pix_fmt",
    "yuv420p",
    "-r",
    str(FPS),
    "-movflags",
    "+faststart",
    str(OUT),
]
print("encoding", OUT)
subprocess.run(cmd, check=True)
print("created", OUT)
