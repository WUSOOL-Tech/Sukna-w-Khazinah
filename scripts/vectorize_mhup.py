#!/usr/bin/env python3
"""Trace the Ministry of Housing and Urban Planning logo (raster JPG) into vectors.

The supplied file is a JPG, so this rebuilds it as vectors for large-format print:
  1. Start from the background-free crop (brand/partners/mhup/mhup_logo_transparent.png,
     made by scripts/build_cobrand.py).
  2. Split the artwork into its two inks by region: navy (Arabic name) and grey (English name + emblem).
  3. Upscale each layer 4×, threshold, and trace it with potrace into smooth Bézier curves.
  4. Write SVG, vector PDF (RGB + CMYK) and PDF-compatible AI files.

This is a high-fidelity trace, not the ministry's own master artwork. Use the official
vector file in its place as soon as the ministry supplies one.

Requires potrace (apt install potrace) and python3 with Pillow + reportlab.
Usage: python3 scripts/vectorize_mhup.py
"""
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageFilter
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MHUP = os.path.join(ROOT, "brand/partners/mhup")
SRC = os.path.join(MHUP, "mhup_logo_transparent.png")
UP = 4  # upscale factor before tracing
# Region boundaries in the trimmed crop (found from empty columns/rows of the alpha mask).
EMBLEM_X = 1630   # emblem occupies x ≥ 1630
ENGLISH_Y = 600   # English name occupies y ≥ 600 (left of the emblem)

# Inks measured from the official file (median of solid pixels per region).
INKS = {
    "navy": {"hex": "#03486F", "rgb": (3, 72, 111), "cmyk": (100, 55, 15, 45)},
    "grey": {"hex": "#4A5662", "rgb": (74, 86, 98), "cmyk": (25, 10, 0, 70)},
    "white": {"hex": "#FFFFFF", "rgb": (255, 255, 255), "cmyk": (0, 0, 0, 0)},
    "black": {"hex": "#000000", "rgb": (0, 0, 0), "cmyk": (0, 0, 0, 100)},
}
# name: colour per layer (navy layer, grey layer)
VARIANTS = {
    "full-colour": ("navy", "grey"),
    "mono-black": ("black", "black"),
    "mono-white": ("white", "white"),
}


def split_layers(im):
    """Return {layer: L-mode mask} at UP× resolution, anti-aliased."""
    w, h = im.size
    alpha = im.getchannel("A")
    # The two inks never touch, so split by region (more reliable than per-pixel hue on a JPG,
    # where thin emblem lines drift blue): Arabic name = navy; English name and emblem = grey.
    cls = Image.new("L", (w, h), 0)
    cls.paste(255, (0, 0, EMBLEM_X, ENGLISH_Y))
    big = (w * UP, h * UP)
    alpha_up = alpha.resize(big, Image.LANCZOS).filter(ImageFilter.GaussianBlur(UP * 0.35))
    cls_up = cls.resize(big, Image.NEAREST)
    navy = Image.composite(alpha_up, Image.new("L", big, 0), cls_up)
    grey = Image.composite(Image.new("L", big, 0), alpha_up, cls_up)
    return {"navy": navy, "grey": grey}


def trace(mask, tmp, name):
    bw = mask.point(lambda v: 0 if v >= 118 else 255).convert("1")  # potrace traces black
    pbm = os.path.join(tmp, name + ".pbm")
    svg = os.path.join(tmp, name + ".svg")
    bw.save(pbm)
    subprocess.run(["potrace", pbm, "-s", "-o", svg, "--turdsize", "12", "--alphamax", "1.0",
                    "--opttolerance", "0.2", "--flat"], check=True)
    text = open(svg).read()
    g = re.search(r'<g transform="([^"]+)"[^>]*>(.*?)</g>', text, re.S)
    paths = re.findall(r'\sd="([^"]+)"', g.group(2))
    return g.group(1), " ".join(p.replace("\n", " ") for p in paths)


def parse_potrace(d):
    """potrace path data (M/m, L/l, C/c, z) → absolute segments, in potrace units."""
    toks = re.findall(r"[MLCmlcZz]|-?\d+(?:\.\d+)?", d)
    out, i, x, y, sx, sy, cmd = [], 0, 0.0, 0.0, 0.0, 0.0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if t in "zZ":
                out.append(("Z", []))
                x, y = sx, sy
            continue
        rel = cmd.islower()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if cmd in "mM":
            x, y = ox + float(toks[i]), oy + float(toks[i + 1])
            sx, sy = x, y
            out.append(("M", [x, y]))
            i += 2
            cmd = "l" if rel else "L"
        elif cmd in "lL":
            x, y = ox + float(toks[i]), oy + float(toks[i + 1])
            out.append(("L", [x, y]))
            i += 2
        elif cmd in "cC":
            v = [float(t) for t in toks[i:i + 6]]
            out.append(("C", [ox + v[0], oy + v[1], ox + v[2], oy + v[3], ox + v[4], oy + v[5]]))
            x, y = ox + v[4], oy + v[5]
            i += 6
    return out


def to_px(segs, transform, height_px):
    """Apply potrace's translate(0,H) scale(s,-s) and divide by UP → original-pixel coordinates."""
    m = re.search(r"translate\(([-\d.]+),([-\d.]+)\)\s*scale\(([-\d.]+),([-\d.]+)\)", transform)
    tx, ty, kx, ky = map(float, m.groups())
    res = []
    for op, a in segs:
        b = []
        for j in range(0, len(a), 2):
            b += [(tx + a[j] * kx) / UP, (ty + a[j + 1] * ky) / UP]
        res.append((op, b))
    return res


def fmt(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def d_attr(segs):
    return "".join(op + " ".join(fmt(v) for v in a) for op, a in segs)


def write_svg(path, w, h, layers, colours, title):
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">',
             f'<title id="t">{title}</title>']
    for (name, segs), colour in zip(layers.items(), colours):
        parts.append(f'<path id="{name}" fill="{INKS[colour]["hex"]}" d="{d_attr(segs)}"/>')
    parts.append("</svg>")
    open(path, "w").write("\n".join(parts) + "\n")


def write_pdf(path, w, h, layers, colours, cmyk, title):
    c = canvas.Canvas(path, pagesize=(w, h), pageCompression=1)
    c.setTitle(title)
    for (name, segs), colour in zip(layers.items(), colours):
        if cmyk:
            c.setFillColorCMYK(*(v / 100 for v in INKS[colour]["cmyk"]))
        else:
            c.setFillColorRGB(*(v / 255 for v in INKS[colour]["rgb"]))
        p = c.beginPath()
        for op, a in segs:
            pts = [(a[j], h - a[j + 1]) for j in range(0, len(a), 2)]
            if op == "M":
                p.moveTo(*pts[0])
            elif op == "L":
                p.lineTo(*pts[0])
            elif op == "C":
                p.curveTo(*pts[0], *pts[1], *pts[2])
            else:
                p.close()
        c.drawPath(p, stroke=0, fill=1, fillMode=1)  # potrace emits nonzero-compatible outlines
    c.showPage()
    c.save()


def main():
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    tmp = tempfile.mkdtemp()
    layers = {}
    for name, mask in split_layers(im).items():
        transform, d = trace(mask, tmp, name)
        layers[name] = to_px(parse_potrace(d), transform, h)
    out = os.path.join(MHUP, "vector")
    os.makedirs(out, exist_ok=True)
    title = "وزارة الإسكان والتخطيط العمراني — Ministry of Housing and Urban Planning"
    for variant, colours in VARIANTS.items():
        base = os.path.join(out, f"mhup_logo_{variant}")
        write_svg(base + ".svg", w, h, layers, colours, title)
        write_pdf(base + ".pdf", w, h, layers, colours, False, title)
        write_pdf(base + ".ai", w, h, layers, colours, False, title)
        if variant != "mono-white":
            write_pdf(base + "_cmyk.pdf", w, h, layers, colours, True, title)
    n = sum(1 for segs in layers.values() for op, _ in segs if op == "M")
    print(f"traced {w}x{h}: {n} sub-paths → {out}")
    return w, h, layers


if __name__ == "__main__":
    main()
