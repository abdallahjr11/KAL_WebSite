import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "promo_frames"
OUT_DIR.mkdir(exist_ok=True)
OUT = ROOT / "KAL_promo_video.mp4"
LOGO = ROOT / "logo.png"
W, H = 1920, 1080
FPS = 30
DURATION = 18
TOTAL = FPS * DURATION

BLACK = (0, 0, 0)
SOFT_BLACK = (7, 7, 7)
CHARCOAL = (17, 17, 17)
WHITE = (255, 255, 255)
LIME = (223, 255, 0)
MUTED_LIME = (191, 218, 18)
GREY = (172, 172, 172)

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
    Path("C:/Windows/Fonts/Arial.ttf"),
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p.exists()), None)
if not FONT_PATH:
    raise SystemExit("No usable system font found")

def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)

FONT_KAL = font(260)
FONT_TITLE = font(88)
FONT_SUB = font(42)
FONT_SMALL = font(28)
FONT_TINY = font(20)

logo = Image.open(LOGO).convert("RGBA")
logo_ratio = logo.width / logo.height

def clamp(x, a=0, b=1):
    return max(a, min(b, x))

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def segment(t, start, end):
    return smooth((t - start) / (end - start))

def fade_window(t, start, hold_start, hold_end, end):
    return min(segment(t, start, hold_start), 1 - segment(t, hold_end, end))

def lerp(a, b, x):
    return a + (b - a) * x

def text_center(draw, y, text, fnt, fill, alpha=255):
    color = fill + (int(alpha),)
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((W - (box[2] - box[0])) / 2, y), text, font=fnt, fill=color)

def draw_soft_background(img, t):
    bg = Image.new("RGBA", (W, H), SOFT_BLACK + (255,))
    d = ImageDraw.Draw(bg)

    # Slow, breathing radial light in lime, almost like a studio glow.
    for r in range(760, 40, -28):
        a = int(18 * (1 - r / 760) * (0.72 + 0.28 * math.sin(t * 0.45)))
        cx = int(W * 0.62 + math.sin(t * 0.22) * 90)
        cy = int(H * 0.45 + math.cos(t * 0.18) * 70)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIME + (a,))

    # Soft charcoal panel drifting across the canvas.
    drift = math.sin(t * 0.16) * 90
    d.polygon([(W * 0.50 + drift, 0), (W, 0), (W, H), (W * 0.34 + drift, H)], fill=(17, 17, 17, 140))

    # Quiet grid, much less aggressive than the first version.
    step = 96
    grid_alpha = 13
    off = int(t * 8) % step
    for x in range(-step, W + step, step):
        d.line([(x + off, 0), (x + off - 160, H)], fill=LIME + (grid_alpha,), width=1)
    for y in range(-step, H + step, step):
        d.line([(0, y + off // 2), (W, y + off // 2)], fill=WHITE + (6,), width=1)

    img.alpha_composite(bg)

def draw_thin_frame(draw, cx, cy, size, color, alpha, angle, width=2):
    half = size / 2
    ca, sa = math.cos(angle), math.sin(angle)
    pts = []
    for x, y in [(-half, -half), (half, -half), (half, half), (-half, half)]:
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    draw.line(pts + [pts[0]], fill=color + (int(alpha),), width=width)

    # L-shaped corner accents, calm design-system detail.
    tick = size * 0.12
    for x, y in pts:
        draw.rectangle([x - 2, y - 2, x + 2, y + 2], fill=color + (int(alpha * 0.9),))
        draw.line([(x, y), (x + tick * ca, y + tick * sa)], fill=color + (int(alpha * 0.7),), width=width)

def add_blurred_line(img, y, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([0, y - 2, W, y + 2], fill=LIME + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(layer)

for i in range(TOTAL):
    t = i / FPS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_soft_background(img, t)
    draw = ImageDraw.Draw(img)

    # Very slow scan, more like light passing over paper.
    scan_y = int(((t / DURATION) * 1.35 % 1) * (H + 300) - 150)
    add_blurred_line(img, scan_y, 34)

    # Header metadata, subtle.
    draw.text((72, 56), "KAL", font=FONT_SMALL, fill=LIME + (220,))
    draw.text((W - 440, 58), "CREATIVE STUDIO  /  BRAND SYSTEMS", font=FONT_TINY, fill=WHITE + (120,))

    # Central calm logo lockup.
    cx, cy = W * 0.62, H * 0.48
    breathe = 1 + 0.025 * math.sin(t * 0.78)
    draw_thin_frame(draw, cx, cy, 540 * breathe, LIME, 105, t * 0.035, 2)
    draw_thin_frame(draw, cx, cy, 390 * (1 + 0.02 * math.sin(t * 0.6 + 1)), WHITE, 65, -t * 0.025, 1)
    draw_thin_frame(draw, cx, cy, 690 * (1 + 0.012 * math.sin(t * 0.42)), MUTED_LIME, 45, t * 0.015, 1)

    logo_alpha = int(255 * segment(t, 0.8, 2.6))
    logo_size = int(220 * breathe)
    logo_img = logo.resize((int(logo_size * logo_ratio), logo_size), Image.Resampling.LANCZOS)
    if logo_alpha < 255:
        logo_img.putalpha(logo_img.getchannel("A").point(lambda p: int(p * logo_alpha / 255)))
    img.alpha_composite(logo_img, (int(cx - logo_img.width / 2), int(cy - logo_img.height / 2)))

    # A large quiet KAL wordmark as background, fading in and out.
    word_alpha = int(32 + 24 * math.sin(t * 0.35))
    draw.text((70, H - 315), "KAL", font=FONT_KAL, fill=LIME + (word_alpha,))

    # Story text, calm scene transitions.
    scenes = [
        (1.2, 4.8, "A BRAND THAT BREATHES", "quiet confidence, designed to stay"),
        (5.0, 8.6, "SHARP IDEAS", "softly framed for bold businesses"),
        (8.8, 12.4, "IDENTITY IN MOTION", "logo, strategy, packaging, recognition"),
        (12.6, 16.8, "KAL CREATIVE STUDIO", "your brand deserves to be remembered"),
    ]
    for start, end, title, sub in scenes:
        a = fade_window(t, start, start + 0.8, end - 0.8, end)
        if a <= 0:
            continue
        x = lerp(70, 110, a)
        y = 335
        draw.text((x, y), title, font=FONT_TITLE, fill=WHITE + (int(245 * a),))
        draw.text((x + 3, y + 112), sub.upper(), font=FONT_SUB, fill=LIME + (int(220 * a),))
        draw.rectangle([x + 4, y + 188, x + 4 + 360 * a, y + 192], fill=LIME + (int(180 * a),))

    # Closing button, calm final call.
    cta = segment(t, 15.0, 16.6)
    if cta > 0:
        bw, bh = 300 * cta, 68
        bx, by = W / 2 - bw / 2, 815
        draw.rectangle([bx, by, bx + bw, by + bh], fill=LIME + (int(235 * cta),))
        if cta > 0.65:
            text_center(draw, by + 17, "ENQUIRE", FONT_SMALL, BLACK, 255)

    # Gentle letterbox bars for premium calm framing.
    draw.rectangle([0, 0, W, 34], fill=BLACK + (180,))
    draw.rectangle([0, H - 34, W, H], fill=BLACK + (180,))

    img.convert("RGB").save(OUT_DIR / f"frame_{i:04d}.jpg", quality=94)
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
