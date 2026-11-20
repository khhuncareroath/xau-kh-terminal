from academy_pdf import flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"

PRICES = ["4,122.0", "4,121.5", "4,121.0", "4,120.5", "4,120.0", "4,119.5", "4,119.0"]
# (bid, ask) per row, top to bottom; None = no trades at that price. All numbers are made up for teaching.
A = ("ទៀន A", [(12, 30), (40, 80), (35, 160), (30, 140), (40, 120), (35, 70), (25, 10)], 5, 1)
B = ("ទៀន B", [None, (60, 55), (90, 85), (110, 100), (70, 75), None, None], 2, 3)
C = ("ទៀន C", [None, (30, 25), (150, 40), (170, 40), (130, 50), (60, 35), (40, 30)], 1, 6)


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def imbalances(rows, ratio=3.0, mode="diag"):
    """Return (buy_rows, sell_rows). Diagonal: ask at a price vs bid one row LOWER (buy), bid at a price vs ask one row
    HIGHER (sell). Horizontal: bid and ask of the same row."""
    buy, sell = set(), set()
    for i, r in enumerate(rows):
        if not r:
            continue
        b, a = r
        if mode == "diag":
            lo = rows[i + 1] if i + 1 < len(rows) else None
            hi = rows[i - 1] if i > 0 else None
            if lo and a >= ratio * max(lo[0], 1):
                buy.add(i)
            if hi and b >= ratio * max(hi[1], 1):
                sell.add(i)
        else:
            if a >= ratio * max(b, 1):
                buy.add(i)
            if b >= ratio * max(a, 1):
                sell.add(i)
    return buy, sell


def footprint(candles, w=420, rh=19, caption="", mode="diag", show_imb=True, show_poc=True, show_delta=True, note=""):
    """Footprint candles drawn as bid x ask cells. candles = [(title, rows, open_row, close_row)]."""
    n = len(candles)
    rows = len(PRICES)
    top = 26
    h = top + rows * rh + (44 if show_delta else 8) + (14 if note else 0)
    ax = 54
    cw = (w - ax - 8) / n
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, p in enumerate(PRICES):
        out.append(f'<text x="{ax - 6}" y="{top + i * rh + rh - 6:.1f}" text-anchor="end" fill="{GR}" class="st">{p}</text>')
    for k, (title, rs, o, c) in enumerate(candles):
        x0 = ax + k * cw
        bull = c < o
        col = UP if bull else DN
        buy, sell = imbalances(rs, mode=mode) if show_imb else (set(), set())
        filled = [i for i, r in enumerate(rs) if r]
        poc = max(filled, key=lambda i: sum(rs[i]))
        out.append(f'<text x="{x0 + cw / 2:.1f}" y="16" text-anchor="middle" fill="#1C1C1E" class="bt">{title}</text>')
        # wick + body bar on the left edge of the column
        out.append(f'<line x1="{x0 + 8:.1f}" x2="{x0 + 8:.1f}" y1="{top + filled[0] * rh + 2:.1f}" y2="{top + (filled[-1] + 1) * rh - 4:.1f}" stroke="{col}" stroke-width="1.4"/>')
        b0, b1 = min(o, c), max(o, c)
        out.append(f'<rect x="{x0 + 5:.1f}" y="{top + b0 * rh + 1:.1f}" width="6" height="{(b1 - b0 + 1) * rh - 5:.1f}" rx="2" fill="{col}"/>')
        cx = x0 + 14 + (cw - 18) / 2
        for i, r in enumerate(rs):
            if not r:
                continue
            y = top + i * rh
            out.append(f'<rect x="{x0 + 14:.1f}" y="{y:.1f}" width="{cw - 18:.1f}" height="{rh - 3}" rx="3" fill="#F7F7FA"'
                       + (f' stroke="{GOLD}" stroke-width="1.6"' if show_poc and i == poc else "") + "/>")
            if i in sell:
                out.append(f'<rect x="{cx - 34:.1f}" y="{y + 1:.1f}" width="28" height="{rh - 5}" rx="3" fill="{DN}" fill-opacity=".22"/>')
            if i in buy:
                out.append(f'<rect x="{cx + 6:.1f}" y="{y + 1:.1f}" width="28" height="{rh - 5}" rx="3" fill="{UP}" fill-opacity=".25"/>')
            out.append(f'<text x="{cx - 8:.1f}" y="{y + rh - 7:.1f}" text-anchor="end" fill="{DN if i in sell else "#3A3A3C"}" class="lt">{r[0]}</text>')
            out.append(f'<text x="{cx:.1f}" y="{y + rh - 7:.1f}" text-anchor="middle" fill="{GR}" class="st">×</text>')
            out.append(f'<text x="{cx + 8:.1f}" y="{y + rh - 7:.1f}" fill="{"#1E8E3E" if i in buy else "#3A3A3C"}" class="lt">{r[1]}</text>')
        if show_delta:
            d = sum(r[1] - r[0] for r in rs if r)
            v = sum(r[0] + r[1] for r in rs if r)
            yb = top + rows * rh + 14
            out.append(f'<text x="{cx:.1f}" y="{yb:.1f}" text-anchor="middle" fill="{UP if d > 0 else DN}" class="lt">Δ {d:+d}</text>')
            out.append(f'<text x="{cx:.1f}" y="{yb + 16:.1f}" text-anchor="middle" fill="{GR}" class="st">Vol {v}</text>')
    if show_delta:
        yb = top + rows * rh + 14
        out.append(f'<text x="{ax - 6}" y="{yb:.1f}" text-anchor="end" fill="#1C1C1E" class="st">Delta</text>')
        out.append(f'<text x="{ax - 6}" y="{yb + 16:.1f}" text-anchor="end" fill="#1C1C1E" class="st">Volume</text>')
    if note:
        out.append(f'<text x="{w / 2:.0f}" y="{h - 6}" text-anchor="middle" fill="{GR}" class="st">{note}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def imb_compare(w=420, h=150, caption=""):
    """Diagonal vs horizontal imbalance on the same two rows of candle A."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for k, (title, diag) in enumerate([("Diagonal (ពេញនិយម)", True), ("Horizontal", False)]):
        x0 = 14 + k * 206
        out.append(f'<text x="{x0 + 92}" y="18" text-anchor="middle" fill="#1C1C1E" class="bt">{title}</text>')
        for i, (p, b, a) in enumerate([("4,121.0", 35, 160), ("4,120.5", 30, 140)]):
            y = 32 + i * 30
            out.append(f'<text x="{x0 + 46}" y="{y + 17}" text-anchor="end" fill="{GR}" class="st">{p}</text>')
            out.append(f'<rect x="{x0 + 52}" y="{y}" width="120" height="24" rx="4" fill="#F7F7FA" stroke="#E5E5EA"/>')
            out.append(f'<text x="{x0 + 100}" y="{y + 17}" text-anchor="end" fill="#3A3A3C" class="lt">{b}</text>')
            out.append(f'<text x="{x0 + 112}" y="{y + 17}" text-anchor="middle" fill="{GR}" class="st">×</text>')
            out.append(f'<text x="{x0 + 124}" y="{y + 17}" fill="#3A3A3C" class="lt">{a}</text>')
        if diag:
            out.append(f'<line x1="{x0 + 132}" y1="{32 + 19}" x2="{x0 + 96}" y2="{62 + 8}" stroke="{UP}" stroke-width="2"/>')
            out.append(f'<text x="{x0 + 92}" y="112" text-anchor="middle" fill="{UP}" class="lt">Ask 4,121.0 ÷ Bid 4,120.5</text>')
            out.append(f'<text x="{x0 + 92}" y="130" text-anchor="middle" fill="{UP}" class="lt">160 ÷ 30 = 5.3× → buy imbalance</text>')
        else:
            out.append(f'<line x1="{x0 + 96}" y1="{32 + 26}" x2="{x0 + 132}" y2="{32 + 26}" stroke="{OR}" stroke-width="2"/>')
            out.append(f'<text x="{x0 + 92}" y="112" text-anchor="middle" fill="{OR}" class="lt">Ask 4,121.0 ÷ Bid 4,121.0</text>')
            out.append(f'<text x="{x0 + 92}" y="130" text-anchor="middle" fill="{OR}" class="lt">160 ÷ 35 = 4.6×</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=23, part="PART 5 · Order Flow Intelligence",
    title_km="Footprint Chart: មើលខាងក្នុងទៀន", title_en="Footprint Charts: Bid × Ask · Volume at Price · Delta · Imbalances",
    intro="""ទៀនធម្មតាប្រាប់តែ 4 លេខ: <b>Open, High, Low, Close</b>។ វាមិនប្រាប់ថានៅខាងក្នុងទៀននោះ <b>អ្នកណាប្រញាប់</b>ទិញ ឬលក់
នៅតម្លៃនីមួយៗទេ។ <span class='en-term'>Footprint chart</span> "បើក" ទៀនឱ្យយើងមើលខាងក្នុង: នៅគ្រប់កម្រិតតម្លៃ
វាបង្ហាញ <span class='en-term'>Bid volume</span> (market sell) និង <span class='en-term'>Ask volume</span> (market buy) ដែលអ្នកបានរៀនក្នុង Chapter 22។
ជំពូកនេះបង្រៀនរចនាសម្ព័ន្ធ footprint, <span class='en-term'>volume at price</span>, <span class='en-term'>delta</span> និង <span class='en-term'>imbalance</span>។
លេខទាំងអស់ក្នុងរូបជា<b>ឧទាហរណ៍សម្រាប់រៀន</b> មិនមែនទិន្នន័យពិតទេ។""",
    sections=[
        ("រចនាសម្ព័ន្ធ Footprint Chart", """
<p>Footprint មួយគឺជាទៀនមួយ ដែលត្រូវបាន<b>កាត់ជាជួរ</b>តាមកម្រិតតម្លៃ។ ជួរនីមួយៗមានលេខពីរ: <b>Bid × Ask</b>។</p>
""" + footprint([A], show_imb=False, show_poc=False, show_delta=False,
                note="ឆ្វេង = Bid volume (market sell) · ស្ដាំ = Ask volume (market buy)",
                caption="ទៀន A មួយគ្រាប់ (5 នាទី) បើកមើលខាងក្នុង · ជួរនីមួយៗ = $0.50 · របារពណ៌នៅឆ្វេង = body និង wick ធម្មតា") + """
<ul><li><b>ជួរ (row)</b> = កម្រិតតម្លៃមួយ · ទំហំជួរអាចជា 1 tick ($0.10 = 1 pip) ឬបូកបញ្ចូលគ្នា ឧ. $0.50 (5 pips) ដើម្បីងាយមើលលើមាស</li>
<li><b>លេខឆ្វេង</b> = ចំនួន contracts ដែលបានជួញដូរនៅ <b>Bid</b> (sellers ប្រញាប់)</li>
<li><b>លេខស្ដាំ</b> = ចំនួន contracts ដែលបានជួញដូរនៅ <b>Ask</b> (buyers ប្រញាប់)</li>
<li>ក្រោមទៀន ច្រើនបង្ហាញ <b>Delta</b> និង <b>Volume</b> សរុប (ផ្នែក 4)</li></ul>
<div class='box tip'>💡 Footprint មានឈ្មោះផ្សេងៗតាម software: <span class='en-term'>Cluster chart</span>, <span class='en-term'>Numbers bars</span>,
<span class='en-term'>Bid/Ask footprint</span>។ គំនិតដូចគ្នា: volume តាមកម្រិតតម្លៃ ខាងក្នុងទៀន។</div>
"""),
        ("Bid × Ask: អានជួរមួយ", """
<p>យកជួរ <b>4,121.0</b> ក្នុងទៀន A: <b>35 × 160</b>។</p>
<ul><li><b>35</b> contracts ត្រូវបានលក់ដោយ market sell ទៅលើ limit buyers នៅ Bid</li>
<li><b>160</b> contracts ត្រូវបានទិញដោយ market buy ពី limit sellers នៅ Ask</li>
<li>Buyers aggressive ច្រើនជាង sellers aggressive <b>ប្រហែល 4.6 ដង</b> នៅកម្រិតនេះ</li></ul>
<table style="break-inside: avoid"><tr><th>អ្វីដែលអ្នកឃើញ</th><th>ការអានដំបូង</th></tr>
<tr><td>Ask ធំជាង Bid ច្រើន</td><td>Buyers ប្រញាប់ទិញនៅកម្រិតនេះ</td></tr>
<tr><td>Bid ធំជាង Ask ច្រើន</td><td>Sellers ប្រញាប់លក់នៅកម្រិតនេះ</td></tr>
<tr><td>Bid ≈ Ask ហើយលេខធំ</td><td>ការប្រកួតខ្លាំង · ភាគីទាំងពីរសកម្ម</td></tr>
<tr><td>Bid ≈ Ask ហើយលេខតូច</td><td>សកម្មភាពតិច · តម្លៃឆ្លងលឿន</td></tr></table>
<div class='box warn'>⚠️ <b>ការអានដ៏ត្រឹមត្រូវ</b>: software ភាគច្រើនប្រៀបធៀប Bid និង Ask តាម<b>អង្កត់ទ្រូង</b> (diagonal) មិនមែនក្នុងជួរតែមួយទេ (ផ្នែក 6)។
ការប្រៀបធៀបក្នុងជួរតែមួយ ងាយយល់សម្រាប់ចាប់ផ្ដើម ប៉ុន្តែមិនមែនជាវិធីដែលអ្នកជំនាញប្រើភាគច្រើន។</div>
"""),
        ("Volume at Price: POC នៃទៀន", """
<p>បើយើងបូក <b>Bid + Ask</b> នៃជួរនីមួយៗ យើងបាន <span class='en-term'>volume at price</span> (volume នៅកម្រិតតម្លៃ)។
វាគឺជា <b>Volume Profile តូចមួយ</b> (Chapter 19) សម្រាប់ទៀនតែមួយ។ ជួរដែលមាន volume ច្រើនជាងគេ ហៅថា
<span class='en-term'>POC</span> នៃទៀន (ខ្លះហៅថា <span class='en-term'>candle POC</span>)។</p>
""" + bars([("4,122.0", 42, GR), ("4,121.5", 120, BL), ("4,121.0", 195, GOLD), ("4,120.5", 170, BL), ("4,120.0", 160, BL), ("4,119.5", 105, BL), ("4,119.0", 35, GR)],
           caption="Volume at price នៃទៀន A (Bid + Ask) · មាស = POC នៃទៀន នៅ 4,121.0 (35 + 160 = 195)") + """
<ul><li>POC នៅ<b>ជិតកំពូល</b>ទៀនឡើង = buyers ទទួលយកតម្លៃខ្ពស់ · ច្រើនជាសញ្ញាល្អសម្រាប់ការបន្ត</li>
<li>POC នៅ<b>ចុង wick</b> (ឧ. wick វែងខាងលើ ហើយ POC នៅទីនោះ) = volume ច្រើននៅកន្លែងដែលតម្លៃត្រូវបានបដិសេធ · អ្នកទិញនៅទីនោះអាច "ជាប់" (trapped)</li>
<li>ក្នុងរូប footprint ខាងក្រោម ជួរដែលមានស៊ុមពណ៌មាស គឺជា POC នៃទៀននីមួយៗ</li></ul>
"""),
        ("Delta: Ask − Bid", """
<p><span class='en-term'>Delta</span> = <b>Ask volume − Bid volume</b>។ វាវាស់ថា aggressive buyers ឬ aggressive sellers ខ្លាំងជាង។
យើងអាចគណនា delta សម្រាប់<b>ជួរនីមួយៗ</b> ឬសម្រាប់<b>ទៀនទាំងមូល</b>។</p>
<table><tr><th>ជួរ (ទៀន A)</th><th>Bid</th><th>Ask</th><th>Delta</th></tr>
<tr><td>4,122.0</td><td>12</td><td>30</td><td style="color:#1E8E3E">+18</td></tr>
<tr><td>4,121.5</td><td>40</td><td>80</td><td style="color:#1E8E3E">+40</td></tr>
<tr><td>4,121.0</td><td>35</td><td>160</td><td style="color:#1E8E3E">+125</td></tr>
<tr><td>4,120.5</td><td>30</td><td>140</td><td style="color:#1E8E3E">+110</td></tr>
<tr><td>4,120.0</td><td>40</td><td>120</td><td style="color:#1E8E3E">+80</td></tr>
<tr><td>4,119.5</td><td>35</td><td>70</td><td style="color:#1E8E3E">+35</td></tr>
<tr><td>4,119.0</td><td>25</td><td>10</td><td style="color:#FF3B30">−15</td></tr>
<tr><th>សរុប</th><th>217</th><th>610</th><th style="color:#1E8E3E">+393</th></tr></table>
<p>Delta សរុបនៃទៀន A = 610 − 217 = <b>+393</b>។ Volume សរុប = 610 + 217 = <b>827</b>។
Delta ធៀបនឹង volume ≈ 48% ពោលគឺ aggressive buying ច្បាស់ណាស់ក្នុងទៀននេះ។</p>
<div class='box tip'>💡 Software ខ្លះបង្ហាញ <b>Delta %</b> = Delta ÷ Volume។ វាងាយប្រៀបធៀបទៀនដែលមាន volume ខុសគ្នា
(ឧ. ទៀនម៉ោង Asia volume តិច ធៀបនឹងទៀនម៉ោង New York volume ច្រើន)។</div>
"""),
        ("Positive Delta និង Negative Delta", """
<p>មើលទៀនបីជាប់គ្នា:</p>
""" + footprint([A, B, C], caption="A: delta វិជ្ជមានធំ (buyers) · B: delta ជិតសូន្យ (balance) · C: delta អវិជ្ជមានធំ (sellers) · ស៊ុមមាស = POC នៃទៀន") + """
<table style="break-inside: avoid"><tr><th>ទៀន</th><th>តម្លៃ</th><th>Delta</th><th>អានបែបណា</th></tr>
<tr><td>បិទឡើង</td><td>↑</td><td><b>+</b> ធំ</td><td>Buyers aggressive រុញតម្លៃ · <b>ស្របគ្នា</b> (confirmation)</td></tr>
<tr><td>បិទចុះ</td><td>↓</td><td><b>−</b> ធំ</td><td>Sellers aggressive រុញតម្លៃ · ស្របគ្នា</td></tr>
<tr><td>បិទឡើង</td><td>↑</td><td><b>−</b></td><td>Sellers ប្រញាប់ ប៉ុន្តែតម្លៃមិនចុះ · passive buyers ធំកំពុងស្រូប? (absorption: Chapter 24)</td></tr>
<tr><td>បិទចុះ</td><td>↓</td><td><b>+</b></td><td>Buyers ប្រញាប់ ប៉ុន្តែតម្លៃមិនឡើង · passive sellers ធំកំពុងរារាំង?</td></tr></table>
""" + bars([("A", 393, UP), ("B", -15, GR), ("C", -360, DN)],
           caption="Delta នៃទៀន A, B, C · ការប្ដូរពី + ធំ ទៅ − ធំ ក្នុងរយៈពេលខ្លី បង្ហាញថា aggression បានប្ដូរភាគី") + """
<div class='box warn'>⚠️ Delta វិជ្ជមាន <b>មិនមានន័យថា</b>តម្លៃត្រូវតែឡើងទេ។ Delta វាស់តែ aggressive orders ប៉ុណ្ណោះ។
Passive orders ធំៗ (limit) អាចបញ្ឈប់ aggressive buyers បាន។ ពេល delta និងតម្លៃ<b>មិនស្របគ្នា</b> នោះជាព័ត៌មានដ៏សំខាន់ (Chapter 24)។</div>
"""),
        ("Imbalance: Diagonal និង Horizontal", """
<p><span class='en-term'>Imbalance</span> = នៅកម្រិតមួយ ភាគីម្ខាងប្រញាប់<b>ច្រើនជាងម្ខាងទៀតខ្លាំង</b>។ កម្រិតដែលពេញនិយមគឺ <b>3 ដង (300%)</b>
ប៉ុន្តែ software អនុញ្ញាតឱ្យប្ដូរ (ខ្លះប្រើ 2.5× ឬ 4×)។</p>
""" + imb_compare(caption="ជួរពីរដូចគ្នា · Diagonal ប្រៀបធៀប Ask នៅតម្លៃមួយ ជាមួយ Bid នៅតម្លៃមួយជួរ<b>ទាបជាង</b>") + """
<ul><li><span class='en-term'>Diagonal imbalance</span> (ពេញនិយមបំផុត):
<b>Buy imbalance</b> = Ask នៅតម្លៃ P ≥ 3 × Bid នៅតម្លៃ<b>មួយជួរទាបជាង</b> P ·
<b>Sell imbalance</b> = Bid នៅតម្លៃ P ≥ 3 × Ask នៅតម្លៃ<b>មួយជួរខ្ពស់ជាង</b> P</li>
<li><b>ហេតុអ្វីអង្កត់ទ្រូង?</b> នៅពេលណាមួយ Bid និង Ask នៅ<b>ឃ្លាតគ្នាមួយ tick</b>។ ពេល Ask = 4,121.0, Bid ពិតនៅទាបជាងបន្តិច។
ដូច្នេះ Ask នៅជួរ P និង Bid នៅជួរខាងក្រោម គឺជា<b>គូដែលប្រកួតគ្នានៅពេលតែមួយ</b></li>
<li><span class='en-term'>Horizontal imbalance</span> = ប្រៀបធៀប Bid និង Ask ក្នុង<b>ជួរតែមួយ</b> · ងាយមើល ប៉ុន្តែប្រៀបធៀបពីរពេលខុសគ្នា</li></ul>
<div class='box tip'>💡 ក្នុង software ភាគច្រើន buy imbalance ត្រូវបានលាបពណ៌<b>បៃតង</b>ខាង Ask ហើយ sell imbalance លាបពណ៌<b>ក្រហម</b>ខាង Bid
ដូចក្នុងរូប footprint នៃជំពូកនេះ។ ពិនិត្យការកំណត់ (settings) ជានិច្ច ដើម្បីដឹងថាវាប្រើ diagonal ឬ horizontal និងកម្រិតប៉ុន្មាន។</div>
"""),
        ("Stacked Imbalances", """
<p><span class='en-term'>Stacked imbalances</span> = imbalance ម្ខាងដូចគ្នា <b>3 ជួរ ឬច្រើនជាងនេះ ជាប់គ្នា</b>។
វាបង្ហាញថាភាគីម្ខាងបានរុញតម្លៃ<b>ឆ្លងកាត់ច្រើនកម្រិតដោយកម្លាំង</b> មិនមែនត្រឹមតែកម្រិតមួយទេ។</p>
""" + footprint([A, C], show_delta=False, caption="ទៀន A: buy imbalances 3 ជួរជាប់គ្នា (4,121.0–4,120.0) · ទៀន C: sell imbalances 3 ជួរជាប់គ្នា (4,121.0–4,120.0)") + """
<ul><li><b>Stacked buy imbalances</b> ក្នុងទៀនឡើង = buyers aggressive ខ្លាំង · តំបន់នោះច្រើនត្រូវបានគេមើលជា <b>support</b> ពេលតម្លៃត្រឡប់មក</li>
<li><b>Stacked sell imbalances</b> ក្នុងទៀនចុះ = sellers aggressive ខ្លាំង · តំបន់នោះច្រើនត្រូវបានគេមើលជា <b>resistance</b></li>
<li>ពេលតម្លៃត្រឡប់មកតំបន់ stacked imbalance ហើយ<b>បិទឆ្លងកាត់</b>វាទាំងស្រុង = កម្លាំងដើមបានបាត់ · តំបន់នោះលែងមានសុពលភាព</li></ul>
<div class='box ok'>✅ គំនិតនេះស្រដៀងនឹង <b>FVG</b> (Chapter 13) និង <b>displacement</b> (Chapter 9): ចលនាដែលមានកម្លាំង ទុក "ស្នាមជើង"
ដែលតម្លៃអាចប្រតិកម្មនៅពេលត្រឡប់មក។ Stacked imbalance ក្នុង FVG ឬ Order Block = confluence ខ្លាំងជាង (Chapter 27)។</div>
<div class='box warn'>⚠️ Stacked imbalance មិនមែនជាការធានាទេ។ នៅពេល news (📰 News) imbalance កើតឡើងច្រើនណាស់ ព្រោះ liquidity តិច (Chapter 22) ដូច្នេះវាមានន័យតិចជាង។</div>
"""),
        ("ត្រូវការអ្វីដើម្បីមើល Footprint ពិត?", """
<table style="break-inside: avoid"><tr><th>តម្រូវការ</th><th>ហេតុអ្វី</th></tr>
<tr><td>ទិន្នន័យ <b>futures</b> (COMEX GC ឬ MGC)</td><td>ត្រូវដឹងថា trade នីមួយៗកើតនៅ Bid ឬ Ask · CFD របស់ broker គ្មានទិន្នន័យនេះ</td></tr>
<tr><td>Data feed ពី exchange</td><td>ច្រើនតែមានថ្លៃប្រចាំខែ</td></tr>
<tr><td>Software footprint</td><td>ឧ. ATAS, Sierra Chart, Quantower (ភាគច្រើនបង់ប្រាក់ · XAU.KH មិនណែនាំ ឬទទួលកម្រៃពីណាមួយទេ)</td></tr></table>
<ul><li>MT5 ដែលអ្នកប្រើសម្រាប់ XAUUSD (CFD) <b>មិនបង្ហាញ footprint ពិត</b>ទេ ព្រោះគ្មានទិន្នន័យ Bid/Ask volume ពី exchange</li>
<li>Tick ពិតនៃ GC = $0.10 (= 1 pip តាមរបៀបរាប់របស់យើង) · ប៉ុន្តែតម្លៃ futures ខុសពី spot បន្តិច · ត្រូវបកប្រែកម្រិតដោយប្រុងប្រយ័ត្ន</li>
<li>Indicator ខ្លះ "ប៉ាន់ស្មាន" delta ពីទៀន: ទៀនបិទឡើង = volume ទិញ · ទៀនបិទចុះ = volume លក់។ ការស្រាវជ្រាវរបស់ XAU.KH ក៏ប្រើការប៉ាន់ស្មានបែបនេះ
ជា<b>ជំនួយ</b>តែប៉ុណ្ណោះ (Chapter 24)។ វា<b>មិនមែន</b> footprint ពិតទេ ព្រោះទៀនមួយបិទឡើងអាចមាន market sell ច្រើនជាង market buy</li></ul>
<div class='box tip'>💡 អ្នក<b>មិនចាំបាច់</b>ទិញ software ដើម្បីជោគជ័យ។ ការយល់ footprint ជួយឱ្យអ្នកយល់ពីអ្វីដែលកើតឡើងខាងក្នុងទៀន
ពេលអ្នកឃើញ displacement ឬ rejection លើ chart MT5 ធម្មតា ឬលើរូប 📊 <b>Analysis</b>។</div>
"""),
        ("Workflow: ប្រើ Footprint ឱ្យត្រឹមត្រូវ", """
<p>Footprint គឺជាឧបករណ៍<b>បញ្ជាក់</b> (confirmation) នៅ<b>ទីតាំង</b>ដែលបានរៀបចំរួច។ វាមិនមែនជាកន្លែងចាប់ផ្ដើមវិភាគទេ។</p>
""" + flow([("Bias", "HTF structure", PU), ("Location", "OB · FVG · VAL", GOLD), ("Footprint", "delta · imbalance", BL), ("Trigger", "MSS / close", UP), ("Risk", "SL · RR", DN)],
           caption="ទិសដៅ → ទីតាំង → មើល footprint នៅទីតាំងនោះ → ការបញ្ជាក់ structure → គ្រប់គ្រងហានិភ័យ") + """
<p><b>ឧទាហរណ៍គំនិត (ទិញ):</b> 4H bias ឡើង · តម្លៃ pullback មក VAL ថ្ងៃមុន ដែលស្របនឹង bullish OB · នៅទីនោះ ទៀន 5m បង្ហាញ
sell delta ធំ ប៉ុន្តែតម្លៃ<b>មិនធ្លាក់បន្ត</b> រួចទៀនបន្ទាប់មាន <b>stacked buy imbalances</b> និង delta វិជ្ជមាន · ទៀន 15m បិទ MSS ឡើង → ទើបពិចារណាចូល
ជាមួយ SL ក្រោមបាតនៃតំបន់។</p>
<div class='box warn'>⚠️ កុំ trade imbalance គ្រប់កន្លែង។ នៅកណ្ដាល range គ្មានទីតាំងច្បាស់ footprint នឹងបង្ហាញ imbalance ច្រើនដែលគ្មានន័យ។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ច្រឡំឆ្វេង/ស្ដាំ: ឆ្វេង = Bid (market <b>sell</b>) · ស្ដាំ = Ask (market <b>buy</b>)</li>
<li>❌ គិតថា delta វិជ្ជមាន = តម្លៃត្រូវតែឡើង (passive orders អាចរារាំង)</li>
<li>❌ មិនពិនិត្យ settings: diagonal ឬ horizontal? 3× ឬ 2.5×? ទំហំជួរប៉ុន្មាន?</li>
<li>❌ ប្រើ footprint ដោយគ្មាន bias និងទីតាំង (Part 2–4)</li>
<li>❌ យកលេខ volume ពី futures ទៅប្រៀបធៀបផ្ទាល់ជាមួយ tick volume ក្នុង MT5</li>
<li>❌ ទុកចិត្ត imbalance ពេល news ខណៈ liquidity តិច</li></ul>
"""),
    ],
    summary=["Footprint = ទៀនដែលបើកមើលខាងក្នុង · ជួរនីមួយៗ = Bid × Ask (ឆ្វេង market sell · ស្ដាំ market buy)",
             "Volume at price = Bid + Ask · ជួរធំជាងគេ = POC នៃទៀន",
             "Delta = Ask − Bid · វិជ្ជមាន = buyers aggressive · អវិជ្ជមាន = sellers aggressive · មិនធានាទិសតម្លៃ",
             "Imbalance ≥ 3× (diagonal: Ask នៅ P ធៀប Bid មួយជួរទាប) · Stacked = 3 ជួរ+ ជាប់គ្នា → តំបន់ S/R",
             "Footprint ពិតត្រូវការទិន្នន័យ futures · ប្រើជាការបញ្ជាក់នៅទីតាំងល្អ មិនមែនជា signal តែឯង"],
    exercise=["ក្នុងទៀន C គណនា delta នៃជួរនីមួយៗ ហើយផ្ទៀងផ្ទាត់ថាសរុប = −360។ ជួរណាជា POC?",
              "ជួរ P មាន 40 × 210 ហើយជួរខាងក្រោម P មាន 65 × 90។ តើជួរ P មាន diagonal buy imbalance (3×) ដែរឬទេ? ហេតុអ្វី?",
              "ទៀន 5m បិទឡើង ប៉ុន្តែ delta = −250។ សរសេរការពន្យល់ពីរដែលអាចកើតឡើង។",
              "បើក 📊 <b>Analysis</b> ចុងក្រោយក្នុង group ហើយរកទីតាំងមួយ (OB, FVG ឬ VAL) ដែលអ្នកនឹងចង់មើល footprint ប្រសិនបើមាន។"],
)
