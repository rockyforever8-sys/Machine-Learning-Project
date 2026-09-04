#!/usr/bin/env python3
"""Generate professional thematic slide graphics for D40 risk presentation."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
W, H = 640, 480

# Palette
NAVY = (0, 43, 92)
TEAL = (0, 122, 135)
SLATE = (51, 65, 85)
LIGHT = (241, 245, 249)
WHITE = (255, 255, 255)
RED = (185, 28, 28)
AMBER = (180, 83, 9)
GREEN = (22, 101, 52)
SKY = (224, 242, 254)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(img: Image.Image, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)


def _save(name: str, img: Image.Image) -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    img.save(path, "PNG", optimize=True)
    return path


def _base(theme_top: tuple, theme_bottom: tuple, accent: tuple) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), WHITE)
    _gradient(img, theme_top, theme_bottom)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((24, 24, W - 24, H - 24), radius=28, outline=accent, width=4)
    return img, draw


def _label(draw: ImageDraw.ImageDraw, text: str, y: int = 36) -> None:
    f = _font(22, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, y), text, fill=WHITE, font=f)


def draw_shield(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, color: tuple) -> None:
    pts = [
        (cx, cy - r),
        (cx + r * 0.85, cy - r * 0.45),
        (cx + r * 0.7, cy + r * 0.55),
        (cx, cy + r),
        (cx - r * 0.7, cy + r * 0.55),
        (cx - r * 0.85, cy - r * 0.45),
    ]
    draw.polygon(pts, fill=color, outline=WHITE, width=3)
    draw.line([(cx, cy - r * 0.35), (cx, cy + r * 0.2)], fill=WHITE, width=6)
    draw.line([(cx - r * 0.25, cy - r * 0.05), (cx, cy + r * 0.2), (cx + r * 0.35, cy - r * 0.25)], fill=WHITE, width=6)


def draw_flame(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, color: tuple) -> None:
    s = scale
    draw.ellipse((cx - 18 * s, cy + 10 * s, cx + 18 * s, cy + 42 * s), fill=AMBER)
    draw.polygon(
        [(cx, cy - 50 * s), (cx + 28 * s, cy + 8 * s), (cx, cy + 30 * s), (cx - 28 * s, cy + 8 * s)],
        fill=color,
    )
    draw.polygon([(cx, cy - 30 * s), (cx + 14 * s, cy + 5 * s), (cx, cy + 18 * s), (cx - 14 * s, cy + 5 * s)], fill=AMBER)


def draw_chain(draw: ImageDraw.ImageDraw, y: int, color: tuple, broken: bool = False) -> None:
    x = 90
    while x < W - 90:
        draw.rounded_rectangle((x, y, x + 46, y + 28), radius=8, outline=color, width=4)
        if broken and 250 < x < 340:
            draw.line([(x + 20, y - 12), (x + 55, y + 40)], fill=RED, width=5)
            x += 70
        else:
            x += 58


def draw_bar_chart(draw: ImageDraw.ImageDraw, values: list[int], colors: list[tuple], base_y: int = 360) -> None:
    bw = 52
    gap = 28
    start_x = (W - (len(values) * bw + (len(values) - 1) * gap)) // 2
    for i, (v, c) in enumerate(zip(values, colors)):
        x = start_x + i * (bw + gap)
        h = v * 2.2
        draw.rounded_rectangle((x, base_y - h, x + bw, base_y), radius=8, fill=c)


def graphic_title() -> Path:
    img, draw = _base((10, 55, 110), (0, 90, 100), TEAL)
    _label(draw, "SUPPLY CHAIN INTEGRITY")
    draw_chain(draw, 200, TEAL)
    draw_shield(draw, W // 2, 310, 72, TEAL)
    draw.ellipse((120, 120, 200, 200), outline=SKY, width=3)
    draw.ellipse((440, 130, 520, 210), outline=SKY, width=3)
    draw.line([(200, 160), (300, 220), (440, 170)], fill=WHITE, width=3)
    return _save("01_title", img)


def graphic_executive() -> Path:
    img, draw = _base((25, 45, 85), (8, 70, 82), AMBER)
    _label(draw, "EXECUTIVE RISK VIEW")
    draw_bar_chart(draw, [55, 78, 92, 68], [TEAL, AMBER, RED, GREEN])
    draw.rounded_rectangle((80, 110, 560, 170), radius=12, fill=(*NAVY, 180) if False else NAVY)
    f = _font(18, bold=True)
    draw.text((110, 128), "Cost  |  Safety  |  Quality  |  Compliance", fill=WHITE, font=f)
    draw.polygon([(500, 250), (540, 290), (500, 330), (460, 290)], outline=RED, width=4)
    draw.text((472, 278), "!", fill=RED, font=_font(28, bold=True))
    return _save("02_executive", img)


def graphic_agenda() -> Path:
    img, draw = _base((18, 50, 95), (0, 80, 95), TEAL)
    _label(draw, "ROADMAP")
    steps = ["Context", "Technical", "Risk", "Controls", "Actions"]
    sx = 70
    for i, s in enumerate(steps):
        x = sx + i * 100
        draw.ellipse((x, 250, x + 56, 306), fill=TEAL if i < 3 else SLATE, outline=WHITE, width=2)
        draw.text((x + 18, 268), str(i + 1), fill=WHITE, font=_font(20, bold=True))
        if i < len(steps) - 1:
            draw.line([(x + 56, 278), (x + 100, 278)], fill=WHITE, width=3)
        tw = draw.textbbox((0, 0), s, font=_font(14))[2]
        draw.text((x + 28 - tw / 2, 320), s, fill=WHITE, font=_font(14))
    return _save("03_agenda", img)


def graphic_business() -> Path:
    img, draw = _base((30, 50, 88), (12, 72, 78), TEAL)
    _label(draw, "PM CLEANING")
    # porous part icon
    draw.rounded_rectangle((220, 170, 420, 300), radius=20, outline=WHITE, width=4)
    for x in range(240, 400, 28):
        for y in range(190, 280, 24):
            draw.ellipse((x, y, x + 10, y + 10), fill=SKY)
    draw.line([(160, 360), (260, 300), (360, 330), (480, 250)], fill=AMBER, width=4)
    return _save("04_business", img)


def graphic_product() -> Path:
    img, draw = _base((20, 48, 92), (0, 75, 88), TEAL)
    _label(draw, "D40 SPECIFICATIONS")
    # drum
    draw.rounded_rectangle((250, 150, 390, 360), radius=16, fill=SLATE, outline=WHITE, width=3)
    draw.rectangle((250, 200, 390, 220), fill=TEAL)
    draw.text((275, 250), "D40", fill=WHITE, font=_font(36, bold=True))
    draw.ellipse((248, 140, 392, 170), fill=LIGHT, outline=WHITE, width=2)
    draw.ellipse((248, 340, 392, 370), fill=LIGHT, outline=WHITE, width=2)
    return _save("05_product", img)


def graphic_boiling() -> Path:
    img, draw = _base((35, 42, 82), (10, 68, 80), AMBER)
    _label(draw, "BOILING RANGE")
    # thermometer + narrow band
    draw.rounded_rectangle((300, 120, 340, 380), radius=10, fill=WHITE, outline=SLATE, width=2)
    draw.rounded_rectangle((308, 220, 332, 360), radius=6, fill=RED)
    draw.ellipse((290, 360, 350, 400), fill=RED, outline=WHITE, width=2)
    draw.rounded_rectangle((120, 260, 240, 290), radius=6, fill=TEAL)
    draw.text((130, 265), "163°C", fill=WHITE, font=_font(16, bold=True))
    draw.rounded_rectangle((400, 260, 520, 290), radius=6, fill=TEAL)
    draw.text((418, 265), "187°C", fill=WHITE, font=_font(16, bold=True))
    draw.line([(240, 275), (400, 275)], fill=WHITE, width=3)
    draw.text((255, 300), "Narrow 24°C window", fill=WHITE, font=_font(16, bold=True))
    return _save("06_boiling", img)


def graphic_aromatic() -> Path:
    img, draw = _base((18, 55, 90), (8, 78, 72), GREEN)
    _label(draw, "LOW AROMATICS")
    draw_shield(draw, 200, 280, 60, GREEN)
    draw.ellipse((380, 180, 500, 300), outline=WHITE, width=4)
    draw.line([(410, 240), (470, 240)], fill=WHITE, width=5)
    draw.text((395, 310), "OEL 1200 mg/m³", fill=WHITE, font=_font(16, bold=True))
    draw.text((120, 380), "Safe  •  Low odor  •  Clean surface", fill=WHITE, font=_font(16, bold=True))
    return _save("07_aromatic", img)


def graphic_compare() -> Path:
    img, draw = _base((22, 46, 88), (5, 74, 86), TEAL)
    _label(draw, "D40  vs  D60")
    draw_bar_chart(draw, [85, 55], [TEAL, SLATE])
    draw.text((175, 390), "D40", fill=WHITE, font=_font(18, bold=True))
    draw.text((355, 390), "D60", fill=WHITE, font=_font(18, bold=True))
    draw.text((120, 130), "Faster dry", fill=WHITE, font=_font(16))
    draw.text((360, 130), "Higher flash", fill=WHITE, font=_font(16))
    return _save("08_compare", img)


def graphic_supply_stress() -> Path:
    img, draw = _base((50, 30, 40), (90, 20, 20), RED)
    _label(draw, "SUPPLY STRESS")
    # globe + crack
    draw.ellipse((220, 150, 420, 350), outline=WHITE, width=4)
    draw.arc((240, 170, 400, 330), 20, 160, fill=WHITE, width=2)
    draw.arc((240, 170, 400, 330), 200, 340, fill=WHITE, width=2)
    draw.line([(310, 180), (350, 320)], fill=RED, width=5)
    draw.text((170, 370), "Price ↑   Feedstock risk   Fraud incentive", fill=WHITE, font=_font(15, bold=True))
    return _save("09_supply", img)


def graphic_adulteration() -> Path:
    img, draw = _base((55, 25, 35), (100, 15, 15), RED)
    _label(draw, "ADULTERATION RISK")
    draw.polygon([(320, 140), (400, 320), (240, 320)], outline=WHITE, width=4)
    draw.text((305, 230), "!", fill=WHITE, font=_font(48, bold=True))
    draw.text((120, 360), "MC  •  Methanol  •  Fake labels", fill=WHITE, font=_font(16, bold=True))
    draw_chain(draw, 100, WHITE, broken=True)
    return _save("10_adulteration", img)


def graphic_impact() -> Path:
    img, draw = _base((40, 35, 70), (80, 18, 22), RED)
    _label(draw, "PROPERTY FAILURE")
    labels = ["Dry", "Flash", "HSE", "Clean"]
    for i, lb in enumerate(labels):
        x = 90 + i * 120
        draw.rounded_rectangle((x, 200, x + 90, 340), radius=10, outline=WHITE, width=3)
        draw.line([(x + 20, 230), (x + 70, 310)], fill=RED, width=4)
        draw.line([(x + 70, 230), (x + 20, 310)], fill=RED, width=4)
        draw.text((x + 22, 355), lb, fill=WHITE, font=_font(14, bold=True))
    return _save("11_impact", img)


def graphic_enterprise_risk() -> Path:
    img, draw = _base((28, 42, 78), (12, 65, 75), AMBER)
    _label(draw, "ENTERPRISE EXPOSURE")
    # 2x2 risk matrix
    cols = [GREEN, AMBER, AMBER, RED]
    pos = [(130, 170), (330, 170), (130, 300), (330, 300)]
    names = ["Ops", "Quality", "Finance", "Safety"]
    for (x, y), c, n in zip(pos, cols, names):
        draw.rounded_rectangle((x, y, x + 150, y + 90), radius=12, fill=c, outline=WHITE, width=2)
        draw.text((x + 42, y + 32), n, fill=WHITE, font=_font(20, bold=True))
    return _save("12_enterprise", img)


def graphic_qc() -> Path:
    img, draw = _base((15, 52, 88), (6, 76, 78), GREEN)
    _label(draw, "QUALITY CONTROL")
    draw_shield(draw, 320, 260, 80, GREEN)
    draw.rounded_rectangle((120, 180, 220, 360), radius=8, fill=WHITE)
    draw.line([(140, 220), (200, 280), (140, 340)], fill=GREEN, width=6)
    draw.text((130, 380), "Authorized\nDistributor", fill=WHITE, font=_font(15, bold=True))
    return _save("13_qc", img)


def graphic_traceability() -> Path:
    img, draw = _base((20, 48, 90), (4, 72, 82), TEAL)
    _label(draw, "TRACEABILITY")
    # barcode
    x = 180
    for w in [8, 14, 6, 18, 8, 22, 6, 16, 10, 20, 8, 14]:
        draw.rectangle((x, 200, x + w, 320), fill=WHITE)
        x += w + 4
    draw.text((170, 340), "Batch → Line → Part", fill=WHITE, font=_font(18, bold=True))
    draw_chain(draw, 120, WHITE)
    return _save("14_trace", img)


def graphic_detection() -> Path:
    img, draw = _base((22, 45, 85), (8, 70, 80), TEAL)
    _label(draw, "LAB VERIFICATION")
    draw.ellipse((250, 170, 390, 310), outline=WHITE, width=4)
    draw.ellipse((280, 200, 360, 280), outline=SKY, width=3)
    draw.line([(200, 360), (280, 280)], fill=WHITE, width=5)
    draw.text((420, 250), "GC-MS", fill=WHITE, font=_font(22, bold=True))
    draw.text((150, 370), "CoA  •  Screen  •  Test", fill=WHITE, font=_font(16, bold=True))
    return _save("15_detection", img)


def graphic_actions() -> Path:
    img, draw = _base((18, 50, 86), (6, 74, 76), GREEN)
    _label(draw, "ACTION PLAN")
    y = 150
    for i in range(4):
        draw.rounded_rectangle((100, y, 540, y + 48), radius=10, outline=WHITE, width=2)
        draw.ellipse((115, y + 9, 145, y + 39), fill=GREEN, outline=WHITE, width=2)
        draw.text((123, y + 12), str(i + 1), fill=WHITE, font=_font(16, bold=True))
        y += 62
    return _save("16_actions", img)


def graphic_governance() -> Path:
    img, draw = _base((25, 44, 82), (10, 68, 72), NAVY)
    _label(draw, "GOVERNANCE & KPIs")
    draw.rounded_rectangle((100, 150, 540, 380), radius=16, outline=TEAL, width=3)
    draw_bar_chart(draw, [40, 70, 100, 85], [TEAL, TEAL, GREEN, GREEN], base_y=340)
    draw.text((150, 180), "100% CoA verified", fill=WHITE, font=_font(16, bold=True))
    draw.text((150, 220), "0 unauthorized suppliers", fill=WHITE, font=_font(16, bold=True))
    return _save("17_governance", img)


def graphic_appendix() -> Path:
    img, draw = _base((30, 48, 86), (8, 70, 78), SLATE)
    _label(draw, "REFERENCES")
    for i, x in enumerate([130, 280, 430]):
        draw.rounded_rectangle((x, 180, x + 90, 280), radius=8, fill=WHITE)
        draw.line([(x + 15, 210), (x + 75, 210)], fill=SLATE, width=3)
        draw.line([(x + 15, 230), (x + 60, 230)], fill=SLATE, width=3)
        draw.line([(x + 15, 250), (x + 70, 250)], fill=SLATE, width=3)
    return _save("18_appendix", img)


def graphic_qa() -> Path:
    img, draw = _base((10, 55, 95), (0, 82, 92), TEAL)
    _label(draw, "DISCUSSION")
    draw.ellipse((260, 200, 380, 320), outline=WHITE, width=4)
    draw.ellipse((220, 240, 300, 300), outline=SKY, width=3)
    draw.ellipse((340, 240, 420, 300), outline=SKY, width=3)
    draw.text((255, 350), "Questions?", fill=WHITE, font=_font(26, bold=True))
    return _save("19_qa", img)


def generate_all() -> dict[str, Path]:
    makers = [
        graphic_title,
        graphic_executive,
        graphic_agenda,
        graphic_business,
        graphic_product,
        graphic_boiling,
        graphic_aromatic,
        graphic_compare,
        graphic_supply_stress,
        graphic_adulteration,
        graphic_impact,
        graphic_enterprise_risk,
        graphic_qc,
        graphic_traceability,
        graphic_detection,
        graphic_actions,
        graphic_governance,
        graphic_appendix,
        graphic_qa,
    ]
    return {f"{i+1:02d}": fn() for i, fn in enumerate(makers)}


if __name__ == "__main__":
    paths = generate_all()
    print(f"Generated {len(paths)} graphics in {ASSETS}")
