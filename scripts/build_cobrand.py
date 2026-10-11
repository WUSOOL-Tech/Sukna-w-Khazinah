#!/usr/bin/env python3
"""Prepare the Ministry of Housing and Urban Planning logo and build the co-branding lockups.

Input   brand/partners/mhup/source/mhup_logo_original.jpg   (official file, kept untouched)
Outputs brand/partners/mhup/mhup_logo.png                   (trimmed, white background)
        brand/partners/mhup/mhup_logo_transparent.png       (trimmed, background removed, colours kept)
        brand/partners/mhup/vector/*                        (traced vectors, via scripts/vectorize_mhup.py)
        brand/logo/cobrand/sukna-w-khazinah_x_mhup[_on-dark].{svg,pdf,ai}  (all-vector lockups)
        brand/logo/cobrand/sukna-w-khazinah_x_mhup_cmyk.pdf
        brand/logo/cobrand/sukna-w-khazinah_x_mhup_{white,transparent,on-dark_transparent}_<w>px.png

Lockup (RTL): ministry logo on the right, then an Ink vertical divider, then the initiative logo.
Both logos have the same height; the gap on each side of the divider is 2D (D = logo dot diameter).
Requires potrace. Run scripts/build_logo.py first. Usage: python3 scripts/build_cobrand.py
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_logo  # noqa: E402
import vectorize_mhup  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MHUP = os.path.join(ROOT, "brand/partners/mhup")
SOURCE = os.path.join(MHUP, "source/mhup_logo_original.jpg")
OUT = os.path.join(ROOT, "brand/logo/cobrand")
COL = {  # rgb, cmyk
    "green": ((2, 194, 119), (75, 0, 70, 0)),
    "yellow": ((240, 255, 11), (8, 0, 92, 0)),
    "ink": ((11, 42, 30), (85, 50, 75, 65)),
    "white": ((255, 255, 255), (0, 0, 0, 0)),
    "navy": (vectorize_mhup.INKS["navy"]["rgb"], vectorize_mhup.INKS["navy"]["cmyk"]),
    "grey": (vectorize_mhup.INKS["grey"]["rgb"], vectorize_mhup.INKS["grey"]["cmyk"]),
}
# lockup: (mark colour, divider colour, ministry navy-layer colour, ministry grey-layer colour)
LOCKUPS = {
    "": ("green", "ink", "navy", "grey"),            # white / light backgrounds
    "_on-dark": ("yellow", "white", "white", "white"),  # Ink or dark backgrounds (see README)
}
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


def layout(mw, mh):
    """Lockup geometry in logo units (the initiative mark is MARK_W × MARK_H)."""
    margin, gap, rule = 2 * DOT, 2 * DOT, 0.25 * DOT
    s = MARK_H / mh                                   # ministry scaled to the same height
    rule_x = margin + MARK_W + gap
    m_x = rule_x + rule + gap
    W = m_x + mw * s + margin
    H = MARK_H + 2 * margin
    return dict(W=W, H=H, margin=margin, rule_x=rule_x, rule=rule, m_x=m_x, s=s)


def hexcol(name):
    return "#%02X%02X%02X" % COL[name][0]


def write_svg(path, L, mark_paths, layers, colours):
    mark, div, navy, grey = colours
    f = build_logo.fmt
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(L["W"])} {f(L["H"])}" width="{f(L["W"])}" '
           f'height="{f(L["H"])}" role="img" aria-labelledby="t">',
           '<title id="t">وزارة الإسكان والتخطيط العمراني × سكنة وخزينة</title>',
           f'<path fill="{hexcol(mark)}" transform="translate({f(L["margin"])} {f(L["margin"])})" '
           f'd="{"".join(build_logo.path_d(p) for p in mark_paths)}"/>',
           f'<rect fill="{hexcol(div)}" x="{f(L["rule_x"])}" y="{f(L["margin"])}" width="{f(L["rule"])}" height="{f(MARK_H)}"/>',
           f'<g transform="translate({f(L["m_x"])} {f(L["margin"])}) scale({L["s"]:.6f})">']
    for (name, segs), col in zip(layers.items(), (navy, grey)):
        out.append(f'<path fill="{hexcol(col)}" d="{vectorize_mhup.d_attr(segs)}"/>')
    out += ["</g>", "</svg>"]
    open(path, "w").write("\n".join(out) + "\n")


def write_pdf(path, L, mark_paths, layers, colours, cmyk=False):
    c = canvas.Canvas(path, pagesize=(L["W"], L["H"]), pageCompression=1)
    c.setTitle("Sukna w Khazinah × Ministry of Housing and Urban Planning")
    H = L["H"]

    def fill(name):
        if cmyk:
            c.setFillColorCMYK(*(v / 100 for v in COL[name][1]))
        else:
            c.setFillColorRGB(*(v / 255 for v in COL[name][0]))

    def draw(segs, ox, oy, k=1.0):
        p = c.beginPath()
        for op, a in segs:
            pts = [(ox + a[j] * k, H - (oy + a[j + 1] * k)) for j in range(0, len(a), 2)]
            if op == "M":
                p.moveTo(*pts[0])
            elif op == "L":
                p.lineTo(*pts[0])
            elif op == "C":
                p.curveTo(*pts[0], *pts[1], *pts[2])
            else:
                p.close()
        c.drawPath(p, stroke=0, fill=1, fillMode=1)

    mark, div, navy, grey = colours
    fill(mark)
    draw([seg for p in mark_paths for seg in p], L["margin"], L["margin"])
    fill(div)
    c.rect(L["rule_x"], H - L["margin"] - MARK_H, L["rule"], MARK_H, stroke=0, fill=1)
    for segs, col in zip(layers.values(), (navy, grey)):
        fill(col)
        draw(segs, L["m_x"], L["margin"], L["s"])
    c.showPage()
    c.save()


def render_png(pdf, png, width, background=None):
    tmp = tempfile.mkdtemp()
    stem = os.path.join(tmp, "x")
    subprocess.run(["pdftocairo", "-png", "-singlefile", "-transp", "-scale-to-x", str(width), "-scale-to-y", "-1",
                    pdf, stem], check=True)
    im = Image.open(stem + ".png").convert("RGBA")
    if background:
        bg = Image.new("RGBA", im.size, background)
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    im.save(png, optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    prepare_ministry()
    mw, mh, layers = vectorize_mhup.main()
    mark_paths = build_logo.extract_master()["paths"]
    L = layout(mw, mh)
    base = os.path.join(OUT, "sukna-w-khazinah_x_mhup")
    for suffix, colours in LOCKUPS.items():
        write_svg(base + suffix + ".svg", L, mark_paths, layers, colours)
        write_pdf(base + suffix + ".pdf", L, mark_paths, layers, colours)
        write_pdf(base + suffix + ".ai", L, mark_paths, layers, colours)
    write_pdf(base + "_cmyk.pdf", L, mark_paths, layers, LOCKUPS[""], cmyk=True)
    for w in WIDTHS:
        render_png(base + ".pdf", f"{base}_white_{w}px.png", w, (255, 255, 255, 255))
        render_png(base + ".pdf", f"{base}_transparent_{w}px.png", w)
        render_png(base + "_on-dark.pdf", f"{base}_on-dark_transparent_{w}px.png", w)
    print(f"lockups {L['W']:.0f} x {L['H']:.0f} units → {OUT}")


if __name__ == "__main__":
    main()
