"""Formatting helpers + SVG chart primitives for the report.

All charts are RTL: category order runs right -> left, bars grow from a right-hand baseline
towards the left, and time reads right -> left (WUSOOL data rule, Arabic reading order).
Every chart is plain SVG (no JS) so it prints crisply and is saved under charts/ as well.
"""
import re
from datetime import date, datetime
from html import escape

# ------------------------------------------------------------------ palette (brand-locked)
INK = '#0B2A1E'          # Sukna ink — text
DEEP = '#00563A'         # Sukna deep green
GREEN = '#02C277'        # Sukna green
YELLOW = '#F0FF0B'       # Khazinah yellow
PAPER = '#F6F8F5'
MIDNIGHT = '#014750'     # WUSOOL primary — main data series
AQUA = '#66C8C9'         # WUSOOL aquamarine — comparison series
AQUA_TEXT = '#1F7476'
MARIGOLD = '#FFCC31'     # WUSOOL highlight — one per chart
MUTED = '#55655D'        # secondary text (6.0:1 on white)
FAINT = '#7C8A83'        # axis text (3.6:1 — large/axis only)
GRID = '#E3E8E5'
TRACK = '#F0F3F1'

AR_MONTHS = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
AR_DAYS = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
ARABIC = re.compile('[؀-ۿ]')


# ------------------------------------------------------------------ number / text formatting
def num(x, dec=0):
    return f'{x:,.{dec}f}'


def money(x, dec=2):
    return f'{x:,.{dec}f}'


def pct(x, dec=1):
    return f'{x:.{dec}f}%'


def N(s, cls=''):
    """Isolate a Latin-digit token so the bidi algorithm never reorders it inside Arabic text."""
    return f'<span class="num{(" " + cls) if cls else ""}">{escape(str(s))}</span>'


def OMR(x, dec=2, unit=True):
    return N(money(x, dec)) + (' <span class="cur">ر.ع.</span>' if unit else '')


def d_ar(dstr, year=True, weekday=False):
    d = date.fromisoformat(dstr[:10])
    s = f'{N(d.day)} {AR_MONTHS[d.month - 1]}' + (f' {N(d.year)}' if year else '')
    return (AR_DAYS[d.weekday()] + ' ' + s) if weekday else s


def phone_fmt(p):
    p = re.sub(r'\D', '', p or '')
    return f'{p[:4]} {p[4:]}' if len(p) == 8 else (p or '—')


def esc(s):
    return escape(str(s))


# ------------------------------------------------------------------ SVG primitives
def _t(x, y, s, align='right', size=11, weight=400, fill=INK, family='plex', extra=''):
    """Text with explicit visual alignment. Arabic strings use direction=rtl (anchor semantics flip)."""
    s = str(s)
    rtl = bool(ARABIC.search(s))
    if rtl:
        anchor = {'right': 'start', 'left': 'end', 'center': 'middle'}[align]
    else:
        anchor = {'right': 'end', 'left': 'start', 'center': 'middle'}[align]
    fam = {'plex': "'IBM Plex Sans Arabic'", 'changa': "'Changa'", 'almarai': "'Almarai'"}[family]
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" direction="{"rtl" if rtl else "ltr"}" '
            f'font-family="{fam}, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{escape(s)}</text>')


def _bar_h(x_right, y, length, h, color, r=3):
    """Horizontal bar anchored on the right baseline growing left, rounded data-end (left) only."""
    if length <= 0:
        return ''
    r = min(r, length / 2, h / 2)
    x0 = x_right - length
    return (f'<path d="M{x_right:.2f},{y:.2f} H{x0 + r:.2f} Q{x0:.2f},{y:.2f} {x0:.2f},{y + r:.2f} '
            f'V{y + h - r:.2f} Q{x0:.2f},{y + h:.2f} {x0 + r:.2f},{y + h:.2f} H{x_right:.2f} Z" fill="{color}"/>')


def _col(x, y_base, w, length, color, r=3):
    """Vertical column from a baseline, rounded top only."""
    if length <= 0:
        return ''
    r = min(r, length / 2, w / 2)
    yt = y_base - length
    return (f'<path d="M{x:.2f},{y_base:.2f} V{yt + r:.2f} Q{x:.2f},{yt:.2f} {x + r:.2f},{yt:.2f} '
            f'H{x + w - r:.2f} Q{x + w:.2f},{yt:.2f} {x + w:.2f},{yt + r:.2f} V{y_base:.2f} Z" fill="{color}"/>')


def svg(w, h, body, title=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img" aria-label="{escape(title)}" class="chart">{body}</svg>')


# ------------------------------------------------------------------ charts
def hbars(items, w=640, label_w=150, bar_h=16, gap=10, color=MIDNIGHT, vmax=None, value_w=90, title='', label_size=11):
    """items: list of dict(label, value, vlabel, hl=False, sub=None)."""
    vmax = vmax or max(i['value'] for i in items) or 1
    x_base = w - label_w - 10
    track = x_base - value_w
    row = bar_h + gap
    h = len(items) * row + 4
    out = []
    for k, it in enumerate(items):
        y = 2 + k * row
        out.append(_t(w, y + bar_h / 2 + 4, it['label'], 'right', label_size, 500))
        if it.get('sub'):
            pass
        L = track * it['value'] / vmax
        out.append(_bar_h(x_base, y, L, bar_h, MARIGOLD if it.get('hl') else color))
        out.append(_t(x_base - L - 6, y + bar_h / 2 + 4, it['vlabel'], 'right', 10.5, 600, INK))
    out.append(f'<line x1="{x_base + .5}" y1="0" x2="{x_base + .5}" y2="{h}" stroke="{INK}" stroke-width="1"/>')
    return svg(w, h, ''.join(out), title)


def stacked_hbars(items, series, w=640, label_w=150, bar_h=16, gap=10, value_w=60, title=''):
    """items: dict(label, parts=[v1, v2..], vlabel). series: [(name, color)]. 2px surface gap between parts."""
    vmax = max(sum(i['parts']) for i in items) or 1
    x_base = w - label_w - 10
    track = x_base - value_w
    row = bar_h + gap
    leg_h = 26
    h = leg_h + len(items) * row + 4
    out = []
    # legend (top, right-aligned)
    lx = w
    for name, col in series:
        out.append(f'<rect x="{lx - 10:.1f}" y="6" width="10" height="10" rx="2" fill="{col}"/>')
        out.append(_t(lx - 16, 15, name, 'right', 10, 500, MUTED))
        lx -= 16 + 7.2 * len(name) + 22
    for k, it in enumerate(items):
        y = leg_h + k * row
        out.append(_t(w, y + bar_h / 2 + 4, it['label'], 'right', 11, 500))
        x = x_base
        for (name, col), v in zip(series, it['parts']):
            L = track * v / vmax
            if L > 0:
                out.append(f'<rect x="{x - L:.2f}" y="{y}" width="{max(L - 2, 0.8):.2f}" height="{bar_h}" fill="{col}" rx="1.5"/>')
            x -= L
        out.append(_t(x - 6, y + bar_h / 2 + 4, it['vlabel'], 'right', 10.5, 600))
    out.append(f'<line x1="{x_base + .5}" y1="{leg_h - 4}" x2="{x_base + .5}" y2="{h}" stroke="{INK}" stroke-width="1"/>')
    return svg(w, h, ''.join(out), title)


def columns(items, w=640, h=220, color=MIDNIGHT, vmax=None, col_w=None, title='', top_pad=22, axis_h=40, label_size=10.5,
            series2=None):
    """RTL columns: items[0] is drawn at the right. item: dict(label, sub, value, vlabel, hl, v2)."""
    n = len(items)
    slot = w / n
    cw = col_w or min(28, slot * 0.55)
    vmax = vmax or max(i['value'] for i in items) or 1
    base = h - axis_h
    plot = base - top_pad
    out = [f'<line x1="0" y1="{base + .5}" x2="{w}" y2="{base + .5}" stroke="{INK}" stroke-width="1"/>']
    for k, it in enumerate(items):
        cx = w - slot * (k + .5)
        L = plot * it['value'] / vmax
        out.append(_col(cx - cw / 2, base, cw, L, MARIGOLD if it.get('hl') else it.get('color', color)))
        if it.get('vlabel') is not None:
            out.append(_t(cx, base - L - 6, it['vlabel'], 'center', 10.5, 600))
        out.append(_t(cx, base + 15, it['label'], 'center', label_size, 500))
        if it.get('sub'):
            out.append(_t(cx, base + 29, it['sub'], 'center', 9.5, 400, MUTED))
    return svg(w, h, ''.join(out), title)


def heatmap(rows, col_labels, w=640, label_w=110, cell_h=26, title='', color_rgb=(1, 71, 80)):
    """rows: [(label, sublabel, [values])]. RTL: first column at the right. Sequential single hue (Midnight)."""
    ncol = len(col_labels)
    gw = w - label_w - 8
    cw = gw / ncol
    vmax = max(max(r[2]) for r in rows) or 1
    head = 18
    h = head + len(rows) * (cell_h + 3) + 2
    out = []
    for j, lab in enumerate(col_labels):
        cx = w - label_w - 8 - cw * (j + .5)
        out.append(_t(cx, 12, lab, 'center', 9.5, 500, MUTED))
    for i, (lab, sub, vals) in enumerate(rows):
        y = head + i * (cell_h + 3)
        out.append(_t(w, y + cell_h / 2 + 1, lab, 'right', 10.5, 600))
        if sub:
            out.append(_t(w, y + cell_h / 2 + 12, sub, 'right', 9, 400, MUTED))
        for j, v in enumerate(vals):
            x = w - label_w - 8 - cw * (j + 1)
            a = 0.06 + 0.94 * (v / vmax)
            r, g, b = color_rgb
            # blend with white -> solid colour (prints predictably, no transparency)
            col = '#%02X%02X%02X' % tuple(round(255 - (255 - c) * a) for c in (r, g, b))
            out.append(f'<rect x="{x + 1.5:.2f}" y="{y}" width="{cw - 3:.2f}" height="{cell_h}" rx="2" fill="{col}"/>')
            out.append(_t(x + cw / 2, y + cell_h / 2 + 4, v if v else '', 'center', 9.5, 600, '#FFFFFF' if a > .55 else INK))
    return svg(w, h, ''.join(out), title)


def donut(segments, size=170, ring=0.075, title='', center=None, center_sub=None):
    """Thin-ring donut (WUSOOL: ring ≈ 5–8% of the diameter). segments: [(value, color)]. Starts at 12 o'clock, runs counter-clockwise (RTL)."""
    import math
    tot = sum(v for v, _ in segments) or 1
    cx = cy = size / 2
    R = size / 2 - 2
    sw = size * ring
    r = R - sw / 2
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="{TRACK}" stroke-width="{sw:.2f}"/>']
    ang = -90.0
    gap_deg = 1.6
    for v, col in segments:
        sweep = 360 * v / tot
        a0, a1 = ang, ang - sweep + gap_deg  # counter-clockwise
        large = 1 if sweep - gap_deg > 180 else 0
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        out.append(f'<path d="M{x0:.2f},{y0:.2f} A{r:.2f},{r:.2f} 0 {large} 0 {x1:.2f},{y1:.2f}" fill="none" stroke="{col}" stroke-width="{sw:.2f}" stroke-linecap="butt"/>')
        ang -= sweep
    if center:
        out.append(_t(cx, cy + 6, center, 'center', size * 0.13, 700, INK, 'changa'))
    if center_sub:
        out.append(_t(cx, cy + 6 + size * 0.11, center_sub, 'center', 10, 500, MUTED))
    return svg(size, size, ''.join(out), title)


def strip(points, lo, hi, w=640, h=120, ticks=(), title='', fmt=lambda v: f'{v:,.0f}'):
    """Dot/strip plot on a value axis increasing to the LEFT (RTL). points: [(value, label)] — stacked when equal."""
    pad = 24
    def X(v):
        return w - pad - (w - 2 * pad) * (v - lo) / (hi - lo)
    base = h - 30
    out = [f'<line x1="{pad}" y1="{base + .5}" x2="{w - pad}" y2="{base + .5}" stroke="{INK}" stroke-width="1"/>']
    for t in ticks:
        out.append(f'<line x1="{X(t):.1f}" y1="{base}" x2="{X(t):.1f}" y2="{base + 5}" stroke="{INK}" stroke-width="1"/>')
        out.append(_t(X(t), base + 18, fmt(t), 'center', 9.5, 500, MUTED))
    stack = {}
    for v, lab in sorted(points):
        k = stack.get(v, 0)
        stack[v] = k + 1
        cy = base - 12 - k * 14
        out.append(f'<circle cx="{X(v):.2f}" cy="{cy:.2f}" r="5.5" fill="{MIDNIGHT}" stroke="#fff" stroke-width="2"/>')
    for v, k in stack.items():
        out.append(_t(X(v), base - 12 - (k - 1) * 14 - 14, f'{fmt(v)}  ×{k}' if k > 1 else fmt(v), 'center', 10, 600))
    return svg(w, h, ''.join(out), title)
