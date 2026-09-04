#!/usr/bin/env python3
"""Johnson Electric brand assets: logo, sunburst motif, and sourced appendix images."""

from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# User-provided screenshots
SRC = Path("/home/ubuntu/.cursor/projects/workspace/assets")
USER_IMAGES = {
    "gcms_equipment.jpg": "43d6c215-5dfe-454f-ab5e-97a24fff332c.jpg",
    "gcms_curve.png": "1ab3220a-b5dc-4344-a763-353fa54a4ba6.png",
    "supply_traceability.png": "f563f905-2eab-42d6-8ed3-7b431ae2ee14.png",
    "supply_hydrocarbon.png": "ad262aaf-be30-4d9f-9016-cc5748c33b42.png",
}
JE_TEMPLATE_2 = SRC / "6b50b713-105f-47fa-82b0-ca227a163dee.jpg"

ORANGE = (245, 130, 32)
ORANGE_DARK = (230, 110, 18)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
WHITE = (255, 255, 255)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def copy_user_images() -> None:
    for dest_name, src_name in USER_IMAGES.items():
        src = SRC / src_name
        if src.exists():
            shutil.copy2(src, ASSETS / dest_name)


def _clean_white(im: Image.Image) -> Image.Image:
    """Force near-white photo pixels to transparent for a clean lockup."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r > 235 and g > 235 and b > 235:
                px[x, y] = (255, 255, 255, 0)
    return im


def make_logo() -> Path:
    """Prefer the official lockup cropped from JE Template 2; fallback to a drawn mark."""
    path = ASSETS / "je_logo.png"
    if JE_TEMPLATE_2.exists():
        t2 = Image.open(JE_TEMPLATE_2)
        w, h = t2.size
        im = t2.crop((w - 400, h - 128, w - 22, h - 34))
        im = _clean_white(im)
        im = im.resize((im.width * 3, im.height * 3), Image.Resampling.LANCZOS)
        im.save(path, "PNG")
        return path

    w, h = 1100, 280
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 36, 176, 172), radius=8, fill=ORANGE)
    d.rounded_rectangle((78, 22, 122, 188), radius=6, fill=BLACK)
    d.pieslice((28, 148, 130, 248), 10, 180, fill=BLACK)
    d.ellipse((78, 6, 122, 50), fill=BLACK)
    d.text((210, 48), "JOHNSON", fill=BLACK, font=_font(64, bold=True))
    d.text((210, 128), "ELECTRIC", fill=BLACK, font=_font(64, bold=True))
    img.save(path, "PNG")
    return path


def make_sunburst() -> Path:
    """Template-1 radial motif: orange outer dashes, gray inner rays on the right edge."""
    w, h = 900, 2200
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    cx, cy = w - 8, h // 2
    rays = 36
    for i in range(rays):
        ang = math.radians(180 - 8 - i * (164 / (rays - 1)))
        # long faint inner
        x0 = cx + 90 * math.cos(ang)
        y0 = cy + 90 * math.sin(ang)
        x1 = cx + 520 * math.cos(ang)
        y1 = cy + 520 * math.sin(ang)
        d.line([(x0, y0), (x1, y1)], fill=(210, 210, 210, 255), width=3)
        # mid gray
        x2 = cx + 540 * math.cos(ang)
        y2 = cy + 540 * math.sin(ang)
        x3 = cx + 680 * math.cos(ang)
        y3 = cy + 680 * math.sin(ang)
        d.line([(x2, y2), (x3, y3)], fill=(170, 170, 170, 255), width=4)
        # orange outer dash
        x4 = cx + 710 * math.cos(ang)
        y4 = cy + 710 * math.sin(ang)
        x5 = cx + 860 * math.cos(ang)
        y5 = cy + 860 * math.sin(ang)
        d.line([(x4, y4), (x5, y5)], fill=(*ORANGE, 255), width=12)

    path = ASSETS / "je_sunburst.png"
    img.save(path, "PNG")
    return path


def make_title_wash() -> Path:
    """Soft white-to-transparent wash used behind title text."""
    img = Image.new("RGBA", (1600, 400), (255, 255, 255, 0))
    path = ASSETS / "je_wash.png"
    img.save(path, "PNG")
    return path


def generate_all() -> None:
    copy_user_images()
    make_logo()
    make_sunburst()
    make_title_wash()
    print(f"JE assets ready in {ASSETS}")


if __name__ == "__main__":
    generate_all()
