#!/usr/bin/env python3
"""Build every logo deliverable for «سكنة وخزينة» from the approved Illustrator PDF.

Pipeline
  1. pdftocairo turns artboard 3 (mono black) of the source PDF into SVG.
  2. The 18 vector paths are parsed and re-based to a tight bounding box,
     giving the master geometry (brand/logo/master/sukna-w-khazinah_master.json).
  3. Each variant is written as SVG, as vector PDF (RGB, plus CMYK for print),
     as PDF-compatible .ai, and as transparent PNG at several sizes.

Requirements: poppler-utils (pdftocairo), python3 with reportlab.
Usage:       python3 scripts/build_logo.py
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "brand/logo/source/sukna-w-khazinah_original-artboards.pdf")
OUT = os.path.join(ROOT, "brand/logo")
NAME = "sukna-w-khazinah"

# Approved colours, read from the fill operators of the source PDF
# ("0.008 0.761 0.467 rg" and "0.941 1 0.043 rg").
COLORS = {
    "green": {"hex": "#02C277", "rgb": (2, 194, 119), "cmyk": (75, 0, 70, 0)},
    "yellow": {"hex": "#F0FF0B", "rgb": (240, 255, 11), "cmyk": (8, 0, 92, 0)},
    "black": {"hex": "#000000", "rgb": (0, 0, 0), "cmyk": (0, 0, 0, 100)},
    "white": {"hex": "#FFFFFF", "rgb": (255, 255, 255), "cmyk": (0, 0, 0, 0)},
    "ink": {"hex": "#0B2A1E", "rgb": (11, 42, 30), "cmyk": (85, 50, 75, 65)},
}

# Unit D = diameter of a dot in the mark (≈36 units on a 641-unit-wide mark).
DOT = 36.0
CLEAR = 2 * DOT   # minimum clear space around the mark
FIELD = 4 * DOT   # comfortable padding used by the "on field" lockups

# name: (mark colour, background colour or None, padding, square?)
VARIANTS = {
    "primary": ("green", "yellow", FIELD, False),
    "reverse": ("yellow", "green", FIELD, False),
    "mono-black-on-white": ("black", "white", FIELD, False),
    "mark-green": ("green", None, 0, False),
    "mark-yellow": ("yellow", None, 0, False),
    "mark-black": ("black", None, 0, False),
    "mark-white": ("white", None, 0, False),
    "mark-ink": ("ink", None, 0, False),
    "avatar-yellow": ("green", "yellow", FIELD, True),
    "avatar-green": ("yellow", "green", FIELD, True),
}
PNG_WIDTHS = [512, 1024, 2048, 4096]
AVATAR_SIZES = [400, 1080, 2048]
CMYK_VARIANTS = ["primary", "reverse", "mark-green", "mark-yellow", "mark-black"]


def extract_master():
    tmp = tempfile.mkdtemp()
    svg_path = os.path.join(tmp, "p3.svg")
    subprocess.run(["pdftocairo", "-svg", "-f", "3", "-l", "3", SOURCE, svg_path], check=True)
    svg = open(svg_path).read()
    shutil.rmtree(tmp)

    paths = []
    for d in re.findall(r'<path[^>]*?\sd="([^"]+)"', svg):
        toks = re.findall(r"[MLCZ]|-?[\d.]+", d)
        cmds, i = [], 0
        while i < len(toks):
            c = toks[i]
            i += 1
            n = {"M": 2, "L": 2, "C": 6, "Z": 0}[c]
            cmds.append((c, [float(x) for x in toks[i:i + n]]))
            i += n
        paths.append(cmds)

    xs = [v for p in paths for _, a in p for v in a[0::2]]
    ys = [v for p in paths for _, a in p for v in a[1::2]]
    x0, y0 = min(xs), min(ys)
    based = [[(c, [v - (x0 if j % 2 == 0 else y0) for j, v in enumerate(a)]) for c, a in p] for p in paths]
    return {"width": max(xs) - x0, "height": max(ys) - y0, "paths": based}


def fmt(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def path_d(cmds, dx=0.0, dy=0.0):
    out = []
    for c, a in cmds:
        out.append(c + " ".join(fmt(v + (dx if j % 2 == 0 else dy)) for j, v in enumerate(a)))
    return "".join(out)


def geometry(master, pad, square):
    w, h = master["width"] + 2 * pad, master["height"] + 2 * pad
    dx = dy = pad
    if square:
        side = max(w, h)
        dx += (side - w) / 2
        dy += (side - h) / 2
        w = h = side
    return w, h, dx, dy


def write_svg(master, variant, fg, bg, pad, square, path):
    w, h, dx, dy = geometry(master, pad, square)
    d = "".join(path_d(p, dx, dy) for p in master["paths"])
    title = "سكنة وخزينة — Sukna w Khazinah"
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}" '
        f'width="{fmt(w)}" height="{fmt(h)}" role="img" aria-labelledby="title">',
        f'<title id="title">{title}</title>',
    ]
    if bg:
        parts.append(f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="{COLORS[bg]["hex"]}"/>')
    parts.append(f'<path fill="{COLORS[fg]["hex"]}" d="{d}"/>')
    parts.append("</svg>")
    open(path, "w").write("\n".join(parts) + "\n")


def write_pdf(master, fg, bg, pad, square, path, cmyk=False, title=""):
    w, h, dx, dy = geometry(master, pad, square)
    c = canvas.Canvas(path, pagesize=(w, h), pageCompression=1)
    c.setTitle(title or "Sukna w Khazinah — سكنة وخزينة")
    c.setAuthor("Sukna w Khazinah Initiative")
    c.setCreator("scripts/build_logo.py")

    def fill(name):
        if cmyk:
            cc, m, y, k = COLORS[name]["cmyk"]
            c.setFillColorCMYK(cc / 100, m / 100, y / 100, k / 100)
        else:
            r, g, b = COLORS[name]["rgb"]
            c.setFillColorRGB(r / 255, g / 255, b / 255)

    if bg:
        fill(bg)
        c.rect(0, 0, w, h, stroke=0, fill=1)
    fill(fg)
    p = c.beginPath()
    for cmds in master["paths"]:
        for op, a in cmds:
            pts = [(a[j] + dx, h - (a[j + 1] + dy)) for j in range(0, len(a), 2)]
            if op == "M":
                p.moveTo(*pts[0])
            elif op == "L":
                p.lineTo(*pts[0])
            elif op == "C":
                p.curveTo(*pts[0], *pts[1], *pts[2])
            else:
                p.close()
    c.drawPath(p, stroke=0, fill=1, fillMode=1)  # nonzero winding, as in the source
    c.showPage()
    c.save()


def write_png(pdf_path, png_path, width, transparent):
    stem = png_path[:-4]
    args = ["pdftocairo", "-png", "-singlefile", "-scale-to-x", str(width), "-scale-to-y", "-1"]
    if transparent:
        args.append("-transp")
    subprocess.run(args + [pdf_path, stem], check=True)


def main():
    master = extract_master()
    for sub in ["master", "svg", "pdf", "pdf-cmyk", "ai", "png"]:
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)

    json.dump(
        {
            "name": "سكنة وخزينة",
            "latin": "Sukna w Khazinah",
            "width": round(master["width"], 3),
            "height": round(master["height"], 3),
            "unit_D_dot_diameter": DOT,
            "clear_space": CLEAR,
            "ascent_angle_deg": 7.5,
            "paths": [path_d(p) for p in master["paths"]],
        },
        open(os.path.join(OUT, "master", f"{NAME}_master.json"), "w"),
        ensure_ascii=False,
        indent=1,
    )
    write_svg(master, "master", "black", None, 0, False, os.path.join(OUT, "master", f"{NAME}_master.svg"))

    for variant, (fg, bg, pad, square) in VARIANTS.items():
        base = f"{NAME}_{variant}"
        write_svg(master, variant, fg, bg, pad, square, os.path.join(OUT, "svg", base + ".svg"))
        pdf = os.path.join(OUT, "pdf", base + ".pdf")
        write_pdf(master, fg, bg, pad, square, pdf, title=f"Sukna w Khazinah — {variant}")
        # Illustrator reads PDF-compatible .ai files natively (fully editable vectors).
        write_pdf(master, fg, bg, pad, square, os.path.join(OUT, "ai", base + ".ai"), title=f"Sukna w Khazinah — {variant}")
        if variant in CMYK_VARIANTS:
            write_pdf(master, fg, bg, pad, square, os.path.join(OUT, "pdf-cmyk", base + "_cmyk.pdf"), cmyk=True,
                      title=f"Sukna w Khazinah — {variant} (CMYK)")
        sizes = AVATAR_SIZES if square else PNG_WIDTHS
        for px in sizes:
            write_png(pdf, os.path.join(OUT, "png", f"{base}_{px}px.png"), px, transparent=bg is None)
    # All three original artboards, as an Illustrator file.
    shutil.copy(SOURCE, os.path.join(OUT, "ai", f"{NAME}_original-artboards.ai"))
    print(f"mark {master['width']:.2f} x {master['height']:.2f} — {len(VARIANTS)} variants written to {OUT}")


if __name__ == "__main__":
    main()
