import math
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError as exc:
    raise SystemExit("Pillow is required to render frames: " + str(exc))

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "promo_frames"
OUT_DIR.mkdir(exist_ok=True)
OUT = ROOT / "KAL_promo_video.mp4"
LOGO = ROOT / "logo.png"
W, H = 1920, 1080
FPS = 30
DURATION = 12
TOTAL = FPS * DURATION
BLACK = (0, 0, 0)
CHARCOAL = (17, 17, 17)
WHITE = (255, 255, 255)
LIME = (223, 255, 0)
GREY = (160, 160, 160)

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/Arial.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p.exists()), None)
if not FONT_PATH:
    raise SystemExit("No usable system font found")

def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)

FONT_HERO = font(230)
FONT_BIG = font(118)
FONT_MED = font(58)
FONT_SMALL = font(34)
FONT_TINY = font(24)

logo = Image.open(LOGO).convert("RGBA")
logo_ratio = logo.width / logo.height

def ease(x):
    x = max(0, min(1, x))
    return 1 - pow(1 - x, 3)

def between(t, a, b):
    return max(0, min(1, (t - a) / (b - a)))

def text_center(draw, xy, text, fnt, fill, spacing=0):
    box = draw.textbbox((0, 0), text, font=fnt, spacing=spacing)
    x = xy[0] - (box[2] - box[0]) / 2
    y = xy[1] - (box[3] - box[1]) / 2
    draw.text((x, y), text, font=fnt, fill=fill, spacing=spacing)

def draw_grid(draw, offset):
    step = 64
    for x in range(-step, W + step, step):
        xx = x + int(offset % step)
        draw.line([(xx, 0), (xx - 260, H)], fill=(223, 255, 0, 22), width=1)
    for y in range(-step, H + step, step):
        yy = y + int((offset * 0.55) % step)
        draw.line([(0, yy), (W, yy)], fill=(223, 255, 0, 16), width=1)

def draw_frame(draw, cx, cy, size, color, width, angle=0):
    # Sharp square frame with rotating corner ticks.
    half = size / 2
    pts = [(-half, -half), (half, -half), (half, half), (-half, half)]
    ca, sa = math.cos(angle), math.sin(angle)
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    draw.line(pts + [pts[0]], fill=color, width=width, joint="curve")
    tick = size * 0.12
    for x, y in pts:
        draw.rectangle([x - tick / 4, y - tick / 4, x + tick / 4, y + tick / 4], outline=color, width=max(1, width - 1))

def add_glow(base, box, color, blur=28):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle(box, outline=color + (180,), width=6)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)

for i in range(TOTAL):
    t = i / FPS
    img = Image.new("RGBA", (W, H), BLACK + (255,))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, t * 38)

    # dark diagonal overlays
    draw.polygon([(0, H), (W * 0.58, 0), (W, 0), (W, H)], fill=(17, 17, 17, 210))
    draw.rectangle([0, 0, W, 84], fill=(0, 0, 0, 180))
    draw.rectangle([0, H - 84, W, H], fill=(0, 0, 0, 180))

    # Animated scan line
    scan_y = int(((t * 0.52) % 1) * (H + 260) - 130)
    scan = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for yy in range(120):
        alpha = int(100 * (1 - abs(yy - 60) / 60))
        sd.line([(0, yy), (W, yy)], fill=LIME + (alpha,), width=1)
    img.alpha_composite(scan, (0, scan_y))

    # Header/footer microcopy
    draw.text((70, 36), "KAL CREATIVE STUDIO", font=FONT_TINY, fill=LIME)
    draw.text((W - 350, 36), "BRAND IDENTITY / LOGO / VISUAL STRATEGY", font=FONT_TINY, fill=(255, 255, 255, 185))
    draw.text((70, H - 56), "YOUR BRAND DESERVES TO BE REMEMBERED", font=FONT_TINY, fill=(255, 255, 255, 190))

    # Logo and geometric lockup
    pulse = 1 + 0.035 * math.sin(t * math.tau * 1.4)
    logo_size = int(238 * pulse)
    logo_resized = logo.resize((int(logo_size * logo_ratio), logo_size), Image.Resampling.LANCZOS)
    lx, ly = W - 485, 240
    glow_box = [lx - 52, ly - 52, lx + 52 + logo_resized.width, ly + 52 + logo_resized.height]
    add_glow(img, glow_box, LIME, 30)
    img.alpha_composite(logo_resized, (lx, ly))
    draw_frame(draw, lx + logo_resized.width / 2, ly + logo_size / 2, 390 + 18 * math.sin(t * 1.8), LIME, 4, t * 0.18)
    draw_frame(draw, lx + logo_resized.width / 2, ly + logo_size / 2, 515 + 24 * math.sin(t * 1.3 + 1), WHITE, 2, -t * 0.12)

    # Scene text timing
    if t < 3.2:
        a = ease(between(t, 0.15, 0.9))
        x = int(80 - 70 * (1 - a))
        draw.text((x, 310), "KAL", font=FONT_HERO, fill=LIME)
        draw.text((x + 10, 535), "BUILT TO BE", font=FONT_MED, fill=WHITE)
        draw.text((x + 10, 602), "REMEMBERED", font=FONT_BIG, fill=WHITE)
    elif t < 6.4:
        a = ease(between(t, 3.2, 3.9))
        x = int(80 - 70 * (1 - a))
        draw.text((x, 300), "BRANDING", font=FONT_BIG, fill=LIME)
        draw.text((x, 430), "THAT SPARKS", font=FONT_BIG, fill=WHITE)
        draw.text((x, 560), "RECOGNITION", font=FONT_BIG, fill=WHITE)
        draw.rectangle([x, 710, x + int(710 * a), 728], fill=LIME)
    elif t < 9.4:
        a = ease(between(t, 6.4, 7.05))
        x = int(80 - 70 * (1 - a))
        services = ["BRAND IDENTITY", "LOGO DESIGN", "VISUAL STRATEGY", "PACKAGING & PRINT"]
        draw.text((x, 245), "4 WAYS", font=FONT_BIG, fill=LIME)
        for n, item in enumerate(services):
            yy = 420 + n * 88
            item_a = ease(between(t, 6.55 + n * 0.18, 7.15 + n * 0.18))
            draw.rectangle([x, yy, x + 560 * item_a, yy + 2], fill=(255, 255, 255, 110))
            draw.text((x, yy + 18), item, font=FONT_SMALL, fill=WHITE if item_a > 0.5 else GREY)
    else:
        a = ease(between(t, 9.4, 10.25))
        text_center(draw, (W / 2, 380), "BREAK", FONT_BIG, WHITE)
        text_center(draw, (W / 2, 515), "BOUNDARIES", FONT_BIG, LIME)
        box_w = int(420 * a)
        draw.rectangle([W / 2 - box_w / 2, 690, W / 2 + box_w / 2, 765], fill=LIME)
        if a > 0.4:
            text_center(draw, (W / 2, 720), "ENQUIRE", FONT_SMALL, BLACK)

    # Film grain/digital bars
    for n in range(10):
        y = int((math.sin(t * 2.1 + n) * 0.5 + 0.5) * H)
        draw.rectangle([0, y, W, y + 1], fill=(255, 255, 255, 18))

    img.convert("RGB").save(OUT_DIR / f"frame_{i:04d}.jpg", quality=92)
    if i % FPS == 0:
        print(f"rendered {i // FPS}/{DURATION}s")

cmd = [
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", str(OUT_DIR / "frame_%04d.jpg"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-movflags", "+faststart", str(OUT)
]
print("encoding", OUT)
subprocess.run(cmd, check=True)
print("created", OUT)
