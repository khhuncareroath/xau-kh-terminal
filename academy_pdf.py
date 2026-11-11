"""XAU.KH Academy PDF builder: one phone-friendly PDF (A5) per chapter, Khmer-first with English terms,
diagrams drawn as SVG (Chromium shapes Khmer script correctly) and optional real chart images.

A chapter for the PDF is a dict: ch, part, title_km, title_en, intro, sections=[(heading, html)], summary=[...],
exercise=[...]. Diagrams: use zigzag(...) inside a section's html.
build(chapter, out_pdf, images={name: path}) -> out_pdf
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "fonts")


def _font(name):
    p = os.path.join(FONT, name)
    return base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else ""


def zigzag(points, labels=None, lines=None, w=420, h=190, caption=""):
    """A clean price-swing diagram. points = [y0, y1, ...] in 0-100 (100 = top). labels = {index: (text, colour)}.
    lines = [(y, x_from_index, x_to_index, text, colour, dashed)]."""
    labels, lines = labels or {}, lines or []
    n = len(points)
    X = lambda i: 20 + i * (w - 40) / (n - 1)
    Y = lambda v: h - 20 - v * (h - 40) / 100
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(points))
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linejoin="round"/>']
    for (y, a, b, t, col, dash) in lines:
        out.append(f'<line x1="{X(a):.1f}" y1="{Y(y):.1f}" x2="{X(b):.1f}" y2="{Y(y):.1f}" stroke="{col}" stroke-width="1.6"'
                   + (' stroke-dasharray="5 4"' if dash else "") + "/>")
        out.append(f'<text x="{X(b) - 2:.1f}" y="{Y(y) - 5:.1f}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    for i, (t, col) in labels.items():
        up = i > 0 and points[i] >= points[i - 1]
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(points[i]):.1f}" r="3.2" fill="{col}"/>')
        out.append(f'<text x="{X(i):.1f}" y="{Y(points[i]) + (-9 if up else 17):.1f}" text-anchor="middle" fill="{col}" class="pt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def flow(steps, caption="", w=420):
    """Boxes joined by arrows, left to right (wraps to 2 rows if more than 4). steps = [(title, sub, colour)]."""
    per = 4 if len(steps) > 4 else len(steps)
    rows = (len(steps) + per - 1) // per
    bw, gap, bh = (w - 20 - (per - 1) * 16) / per, 16, 62
    h = 14 + rows * (bh + 18)
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, sub, col) in enumerate(steps):
        r, c = divmod(i, per)
        x, y = 10 + c * (bw + gap), 10 + r * (bh + 18)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{bh}" rx="10" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-width="1.4"/>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{y + 18}" text-anchor="middle" fill="{col}" class="pt">{i + 1}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{y + 36}" text-anchor="middle" fill="#1C1C1E" class="bt">{t}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{y + 52}" text-anchor="middle" fill="#6E6E73" class="st">{sub}</text>')
        if c < per - 1 and i < len(steps) - 1:
            ax = x + bw + 2
            out.append(f'<path d="M{ax:.1f},{y + bh / 2} l{gap - 5},0 m-5,-4 l5,4 l-5,4" stroke="#8E8E93" stroke-width="1.6" fill="none"/>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def bars(items, caption="", w=420, h=170, unit=""):
    """Simple vertical bars. items = [(label, value, colour)]; values may be negative."""
    n = len(items)
    vmax = max(abs(v) for _, v, _ in items) or 1
    neg = any(v < 0 for _, v, _ in items)
    zero = h / 2 if neg else h - 28
    scale = (h / 2 - 26) / vmax if neg else (h - 50) / vmax
    bw = (w - 40) / n * 0.62
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="14" x2="{w - 14}" y1="{zero:.1f}" y2="{zero:.1f}" stroke="#C7C7CC"/>']
    for i, (lab, v, col) in enumerate(items):
        cx = 20 + (i + .5) * (w - 40) / n
        top = zero - v * scale
        y0, hh = (top, zero - top) if v >= 0 else (zero, top - zero)
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(hh, 1):.1f}" rx="4" fill="{col}"/>')
        ty = top - 5 if v >= 0 else top + 13
        out.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{col}" class="lt">{v:+g}{unit}</text>' if neg else
                   f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{col}" class="lt">{v:g}{unit}</text>')
        ly = h - 8 if not neg else (zero + 14 if v >= 0 else zero - 6)
        out.append(f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#6E6E73" class="st">{lab}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def twolines(a, b, la, lb, ca="#FFB800", cb="#0A84FF", w=420, h=170, caption=""):
    """Two series on their own scales (e.g. gold vs dollar) to show they move opposite."""
    def path(vs):
        lo, hi = min(vs), max(vs)
        n = len(vs)
        return " ".join(f"{'M' if i == 0 else 'L'}{20 + i * (w - 40) / (n - 1):.1f},{h - 24 - (v - lo) / (hi - lo or 1) * (h - 50):.1f}"
                        for i, v in enumerate(vs))
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<path d="{path(a)}" fill="none" stroke="{ca}" stroke-width="2.6" stroke-linejoin="round"/>',
           f'<path d="{path(b)}" fill="none" stroke="{cb}" stroke-width="2.6" stroke-linejoin="round" stroke-dasharray="6 4"/>',
           f'<rect x="20" y="8" width="12" height="4" fill="{ca}"/><text x="37" y="14" class="lt" fill="{ca}">{la}</text>',
           f'<rect x="{w / 2:.0f}" y="8" width="12" height="4" fill="{cb}"/><text x="{w / 2 + 17:.0f}" y="14" class="lt" fill="{cb}">{lb}</text>',
           "</svg>"]
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CSS = """
@font-face { font-family: 'KH'; src: url(data:font/ttf;base64,%(kp)s); font-weight: 100 900; }
@font-face { font-family: 'Inter'; src: url(data:font/otf;base64,%(inter)s); font-weight: 400 700; }
@page { size: A5; margin: 14mm 12mm 14mm 12mm; }
* { box-sizing: border-box; }
body { font-family: 'KH', 'Inter', sans-serif; color: #1C1C1E; font-size: 10.6pt; line-height: 1.75; margin: 0; }
.cover { background: #0B0B0F; color: white; border-radius: 14px; padding: 18px 18px 16px; margin-bottom: 14px; }
.brand { color: #0A84FF; font-weight: 800; font-family: 'Inter', 'KH'; letter-spacing: .5px; font-size: 10pt; }
.part { color: #AEAEB2; font-size: 8.5pt; margin-top: 2px; }
.cover h1 { font-size: 19pt; line-height: 1.45; margin: 8px 0 2px; font-weight: 700; }
.cover .en { color: #FFD60A; font-family: 'Inter', 'KH'; font-weight: 600; font-size: 11pt; }
.bar { height: 5px; background: #2C2C2E; border-radius: 3px; margin-top: 12px; }
.bar i { display: block; height: 5px; background: #0A84FF; border-radius: 3px; }
.intro { background: #F2F2F7; border-radius: 12px; padding: 10px 13px; margin: 0 0 12px; }
h2 { font-size: 12.5pt; margin: 16px 0 4px; color: #0A84FF; font-weight: 700; break-after: avoid; }
h2 .num { display: inline-block; background: #0A84FF; color: white; border-radius: 6px; padding: 0 7px; margin-right: 6px; font-family: 'Inter'; font-size: 10pt; }
p { margin: 4px 0 8px; }
b { font-weight: 700; }
.en-term { font-family: 'Inter', 'KH'; font-weight: 600; color: #1C1C1E; }
ul { margin: 2px 0 8px 0; padding-left: 18px; } li { margin: 2px 0; }
.dia { width: 100%%; height: auto; background: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 12px; margin: 6px 0 2px; }
.dia .pt { font: 700 12px 'Inter', 'KH'; } .dia .lt { font: 600 11px 'Inter', 'KH'; }
.dia .bt { font: 700 11.5px 'KH', 'Inter'; } .dia .st { font: 500 9.5px 'KH', 'Inter'; }
.fig { break-inside: avoid; }
.cap { font-size: 8.5pt; color: #8E8E93; text-align: center; margin-bottom: 10px; }
.box { border-radius: 12px; padding: 9px 12px; margin: 8px 0; break-inside: avoid; }
.tip { background: #E8F2FF; border-left: 4px solid #0A84FF; }
.warn { background: #FFF1F0; border-left: 4px solid #FF3B30; }
.ok { background: #EAFBEF; border-left: 4px solid #34C759; }
.chart { width: 100%%; border-radius: 12px; border: 1px solid #E5E5EA; margin: 6px 0 2px; }
table { width: 100%%; border-collapse: collapse; font-size: 9.5pt; margin: 6px 0 10px; }
th, td { border-bottom: 1px solid #E5E5EA; padding: 5px 6px; text-align: left; vertical-align: top; }
th { background: #F2F2F7; font-weight: 700; }
.sum { background: #0B0B0F; color: white; border-radius: 12px; padding: 10px 14px; break-inside: avoid; }
.sum h2 { color: #FFD60A; margin-top: 2px; }
.foot { color: #8E8E93; font-size: 7.5pt; text-align: center; margin-top: 14px; }
"""


def build(c, out_pdf, images=None, total=45):
    images = images or {}
    css = CSS % {"kp": _font("KantumruyPro.ttf"), "inter": _font("Inter-SemiBold.otf")}
    html = [f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>",
            f"<div class='cover'><div class='brand'>XAU.KH ACADEMY</div><div class='part'>{c['part']} · ជំពូកទី {c['ch']} / {total}</div>"
            f"<h1>{c['title_km']}</h1><div class='en'>{c['title_en']}</div>"
            f"<div class='bar'><i style='width:{100 * c['ch'] / total:.0f}%'></i></div></div>",
            f"<div class='intro'>{c['intro']}</div>"]
    for k, (head, body) in enumerate(c["sections"], 1):
        for name, path in images.items():
            if "{img:" + name + "}" in body:
                b64 = base64.b64encode(open(path, "rb").read()).decode()
                body = body.replace("{img:" + name + "}", f"<img class='chart' src='data:image/png;base64,{b64}'/>")
        html.append(f"<h2><span class='num'>{k}</span>{head}</h2>{body}")
    html.append("<div class='sum'><h2>📌 សេចក្ដីសង្ខេប · Summary</h2><ul>" + "".join(f"<li>{x}</li>" for x in c["summary"]) + "</ul></div>")
    if c.get("exercise"):
        html.append("<h2><span class='num'>✍</span>លំហាត់អនុវត្ត · Practice</h2><ol>" + "".join(f"<li>{x}</li>" for x in c["exercise"]) + "</ol>")
    html.append("<div class='foot'>XAU.KH Academy · ការអប់រំ មិនមែនដំបូន្មានហិរញ្ញវត្ថុ · Education, not financial advice</div></body></html>")
    tmp = out_pdf.replace(".pdf", ".html")
    open(tmp, "w", encoding="utf-8").write("".join(html))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        pg.goto("file://" + os.path.abspath(tmp))
        pg.wait_for_timeout(300)
        pg.pdf(path=out_pdf, format="A5", print_background=True,
               margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
        br.close()
    return out_pdf
