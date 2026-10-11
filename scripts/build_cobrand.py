#!/usr/bin/env python3
"""Prepare the Ministry of Housing and Urban Planning logo and build the co-branding lockups.

Input   brand/partners/mhup/source/mhup_logo_original.jpg   (official file, kept untouched)
Outputs brand/partners/mhup/mhup_logo.png                   (trimmed, white background)
        brand/partners/mhup/mhup_logo_transparent.png       (trimmed, background removed, colours kept)
        brand/logo/cobrand/sukna-w-khazinah_x_mhup_{white,transparent}_<w>px.png
        brand/logo/cobrand/sukna-w-khazinah_x_mhup.pdf

Lockup (RTL): ministry logo on the right, then an Ink vertical divider, then the initiative logo.
Both logos have the same height; the gap on each side of the divider is 2D (D = logo dot diameter).
Run scripts/build_logo.py first. Usage: python3 scripts/build_cobrand.py
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MHUP = os.path.join(ROOT, "brand/partners/mhup")
SOURCE = os.path.join(MHUP, "source/mhup_logo_original.jpg")
MARK_PDF = os.path.join(ROOT, "brand/logo/pdf/sukna-w-khazinah_mark-green.pdf")
OUT = os.path.join(ROOT, "brand/logo/cobrand")
INK = (11, 42, 30)
MARK_W, MARK_H, DOT = 641.363, 531.059, 36.0
WIDTHS = [1200, 2400, 4800]


def remove_white(im):
    """Unblend the artwork from its white background: alpha from darkness, colour un-premultiplied."""
    im = im.convert("RGB")
    out = Image.new("RGBA", im.size)
    src, dst = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = src[x, y]
            a = 255 - min(r, g, b)
            a = 0 if a < 6 else min(255, int(a * 1.04))
            if a == 0:
                dst[x, y] = (255, 255, 255, 0)
                continue
            f = a / 255
            dst[x, y] = tuple(max(0, min(255, round(255 - (255 - c) / f))) for c in (r, g, b)) + (a,)
    return out


def prepare_ministry():
    im = Image.open(SOURCE).convert("RGB")
    clear = remove_white(im)
    box = clear.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    pad = round(0.01 * im.width)
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
    im.crop(box).save(os.path.join(MHUP, "mhup_logo.png"), optimize=True)
    clear = clear.crop(box)
    clear.save(os.path.join(MHUP, "mhup_logo_transparent.png"), optimize=True)
    return clear


def mark_png(height):
    tmp = tempfile.mkdtemp()
    stem = os.path.join(tmp, "mark")
    subprocess.run(["pdftocairo", "-png", "-singlefile", "-transp", "-scale-to-x", "-1", "-scale-to-y", str(height),
                    MARK_PDF, stem], check=True)
    return Image.open(stem + ".png").convert("RGBA")


def lockup(ministry, total_w, background):
    # Work out the layout at unit height H, then scale to the requested width.
    gap = 2 * DOT / MARK_H            # 2D relative to logo height
    rule = 0.25 * DOT / MARK_H        # divider thickness = ¼D
    margin = 2 * DOT / MARK_H         # clear space around the whole lockup
    m_ratio = ministry.width / ministry.height
    unit_w = 2 * margin + MARK_W / MARK_H + gap + rule + gap + m_ratio
    h = round(total_w / unit_w)
    W, Hh = total_w, round(h * (1 + 2 * margin))
    canvas_im = Image.new("RGBA", (W, Hh), background)
    x, y = round(margin * h), round(margin * h)
    mark = mark_png(h)
    canvas_im.alpha_composite(mark, (x, y))
    x += mark.width + round(gap * h)
    rule_px = max(2, round(rule * h))
    canvas_im.alpha_composite(Image.new("RGBA", (rule_px, h), INK + (255,)), (x, y))
    x += rule_px + round(gap * h)
    m = ministry.resize((round(h * m_ratio), h), Image.LANCZOS)
    canvas_im.alpha_composite(m, (min(x, W - m.width - round(margin * h)), y))
    return canvas_im


def lockup_pdf(ministry_png_path, ministry):
    gap, rule, margin = 2 * DOT, 0.25 * DOT, 2 * DOT
    m_w = MARK_H * ministry.width / ministry.height
    W = 2 * margin + MARK_W + 2 * gap + rule + m_w
    H = MARK_H + 2 * margin
    path = os.path.join(OUT, "sukna-w-khazinah_x_mhup.pdf")
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Sukna w Khazinah × Ministry of Housing and Urban Planning")
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # Initiative mark as vectors, straight from the master geometry.
    r, g, b = (2 / 255, 194 / 255, 119 / 255)
    c.setFillColorRGB(r, g, b)
    p = c.beginPath()
    for cmds in build_logo.extract_master()["paths"]:
        for op, a in cmds:
            pts = [(a[j] + margin, H - (a[j + 1] + margin)) for j in range(0, len(a), 2)]
            if op == "M":
                p.moveTo(*pts[0])
            elif op == "L":
                p.lineTo(*pts[0])
            elif op == "C":
                p.curveTo(*pts[0], *pts[1], *pts[2])
            else:
                p.close()
    c.drawPath(p, stroke=0, fill=1, fillMode=1)
    x = margin + MARK_W + gap
    c.setFillColorRGB(*(v / 255 for v in INK))
    c.rect(x, margin, rule, MARK_H, stroke=0, fill=1)
    c.drawImage(ministry_png_path, x + rule + gap, margin, m_w, MARK_H, mask="auto")
    c.showPage()
    c.save()


def main():
    os.makedirs(OUT, exist_ok=True)
    ministry = prepare_ministry()
    for w in WIDTHS:
        lockup(ministry, w, (255, 255, 255, 255)).convert("RGB").save(
            os.path.join(OUT, f"sukna-w-khazinah_x_mhup_white_{w}px.png"), optimize=True)
        lockup(ministry, w, (255, 255, 255, 0)).save(
            os.path.join(OUT, f"sukna-w-khazinah_x_mhup_transparent_{w}px.png"), optimize=True)
    lockup_pdf(os.path.join(MHUP, "mhup_logo_transparent.png"), ministry)
    print(f"ministry logo {ministry.width}x{ministry.height} → lockups in {OUT}")


if __name__ == "__main__":
    main()
