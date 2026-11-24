from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def position_box(w=420, h=210, caption=""):
    """MT5-style long position: SL below, TP1 (1R) and TP2 (3R) above, risk and reward zones shaded."""
    # price -> y : 4,030 at bottom, 4,135 at top
    lo, hi = 4030, 4135
    Y = lambda p: h - 14 - (p - lo) * (h - 28) / (hi - lo)
    x0, x1 = 60, w - 20
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{x0}" y="{Y(4060):.1f}" width="{x1 - x0}" height="{Y(4038) - Y(4060):.1f}" fill="{DN}" fill-opacity=".12"/>',
           f'<rect x="{x0}" y="{Y(4126):.1f}" width="{x1 - x0}" height="{Y(4060) - Y(4126):.1f}" fill="{UP}" fill-opacity=".10"/>']
    for p, t, col, dash in [(4126, "TP2 4,126 · 3R", UP, True), (4082, "TP1 4,082 · 1R", UP, True),
                            (4060, "Entry 4,060", "#1C1C1E", False), (4038, "SL 4,038 · −1R", DN, True)]:
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(p):.1f}" y2="{Y(p):.1f}" stroke="{col}" stroke-width="1.6"'
                   + (' stroke-dasharray="5 4"' if dash else "") + "/>")
        out.append(f'<text x="{x1 - 4}" y="{Y(p) - 5:.1f}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    out.append(f'<text x="{x0 - 6}" y="{(Y(4060) + Y(4038)) / 2 + 4:.1f}" text-anchor="end" fill="{DN}" class="st">$22</text>')
    out.append(f'<text x="{x0 - 6}" y="{(Y(4126) + Y(4060)) / 2 + 4:.1f}" text-anchor="end" fill="{UP}" class="st">$66</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def trailing(w=420, h=200, caption=""):
    """Rising price path with a stepped stop that only moves up, under each new higher low."""
    pts = [(20, 170), (60, 140), (90, 152), (140, 110), (170, 124), (225, 80), (255, 94), (310, 52), (340, 68), (400, 30)]
    steps = [(20, 182, 140), (140, 160, 225), (225, 132, 310), (310, 102, 400)]  # (x_from, y, x_to)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           '<path d="' + " ".join(f"{'M' if k == 0 else 'L'}{x},{y}" for k, (x, y) in enumerate(pts))
           + '" fill="none" stroke="#1C1C1E" stroke-width="2.3" stroke-linejoin="round"/>']
    d = ""
    for k, (a, y, b) in enumerate(steps):
        d += (f"M{a},{y} " if k == 0 else f"L{a},{y} ") + f"L{b},{y} "
    out.append(f'<path d="{d}" fill="none" stroke="{DN}" stroke-width="1.8" stroke-dasharray="5 3"/>')
    for (x, y), t in [((90, 152), "HL"), ((170, 124), "HL"), ((255, 94), "HL"), ((340, 68), "HL")]:
        out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{UP}"/><text x="{x}" y="{y + 16}" text-anchor="middle" fill="{UP}" class="st">{t}</text>')
    out.append(f'<text x="24" y="196" fill="{DN}" class="st">SL ដំបូង</text>')
    out.append(f'<text x="396" y="118" text-anchor="end" fill="{DN}" class="st">SL ឡើងតាម HL ↑</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=30, part="PART 7 · Trade Execution",
    title_km="Stop Loss និង Take Profit", title_en="Stop Loss & Take Profit: Placement, R:R, Partials, Break-even and Trailing",
    intro="""Chapter 29 បង្រៀនពី<b>របៀបចូល</b>។ ជំពូកនេះបង្រៀនពី<b>របៀបចេញ</b>។ ការចេញសំខាន់ដូចការចូលដែរ ព្រោះវាកំណត់ថាការខាតមួយ<b>តូចប៉ុណ្ណា</b>
ហើយការឈ្នះមួយ<b>ធំប៉ុណ្ណា</b>។ អ្នកជំនាញក៏ខាតដែរ។ អ្វីដែលធ្វើឱ្យគណនីរស់បាន គឺ <b>ខាតតូច ចំណេញធំ</b>។
យើងនឹងរៀន <span class='en-term'>Stop Loss</span> តាម structure និងតាម volatility · គោលដៅ (target) · <span class='en-term'>R:R</span> ·
ការបិទមួយផ្នែក · <span class='en-term'>break-even</span> · <span class='en-term'>trailing stop</span> និងពេលដែល<b>មិនត្រូវ</b>ផ្លាស់ SL។""",
    sections=[
        ("SL គឺជាចំណុចដែល Idea ខុស", """
<p><span class='en-term'>Stop Loss (SL)</span> មិនមែនជាលេខដែលអ្នក "អាចទ្រាំខាតបាន" ទេ។ វាជា<b>តម្លៃដែលប្រាប់ថា idea របស់អ្នកខុស</b>។
បើតម្លៃទៅដល់ទីនោះ ហេតុផលដែលអ្នកចូល trade លែងមានទៀតហើយ។</p>
""" + flow([("Idea", "ហេតុអ្វីចូល?", BL), ("Invalidation", "តម្លៃណា = ខុស?", DN), ("SL", "ដាក់ហួសចំណុចនោះ", OR), ("Lot", "គណនាពី SL", UP)],
           caption="លំដាប់ត្រឹមត្រូវ: រក SL ពី chart មុន → បន្ទាប់មកគណនា lot ពី SL (Chapter 32)") + """
<div class='box warn'>⚠️ លំដាប់ខុសដែលអ្នកចាប់ផ្ដើមច្រើនធ្វើ: ជ្រើស lot ធំមុន → ដាក់ SL តូចឱ្យ "ខាតតិច"។ SL បែបនេះនៅ<b>ក្នុង noise</b> របស់មាស ហើយត្រូវប៉ះញឹកញាប់ ទោះ idea ត្រឹមត្រូវក៏ដោយ។</div>
<div class='box tip'>💡 គណិតមាស XAU.KH: <b>$1 = 10 pips</b> · SL $22 = <b>220 pips</b> · ជាមួយ 0.01 lot (1 oz) SL $22 = ខាត <b>$22</b> · 0.02 lot = $44។</div>
"""),
        ("Structural Stop Loss · SL តាមរចនាសម្ព័ន្ធ", """
<p><span class='en-term'>Structural SL</span> ដាក់<b>ហួស swing</b> ឬ zone ដែលការពារ idea។ ទិញ → SL ក្រោម <b>HL ចុងក្រោយ</b> ឬក្រោម OB/FVG ·
លក់ → SL លើ <b>LH ចុងក្រោយ</b>។ បើតម្លៃបិទហួសចំណុចនោះ structure ត្រូវបានបំបែក (Chapter 9)។</p>
""" + zigzag([20, 55, 38, 75, 58, 70, 90], {2: ("HL", UP), 4: ("HL ចុងក្រោយ", UP), 5: ("Entry", BL)},
             lines=[(30, 3, 6, "SL ក្រោម HL + buffer", DN, True)],
             caption="ទិញក្នុង uptrend: SL ក្រោម HL ចុងក្រោយ មិនមែននៅលើវាត្រង់ៗ") + """
<ul><li><b>Buffer</b>: ដាក់ SL ហួស swing បន្តិច (ឧ. $1–$2 = 10–20 pips) ដើម្បីការពារពី wick និង spread</li>
<li>កុំដាក់ SL <b>ត្រង់</b>លើ swing ឬលេខមូល (4,000 · 4,050) ព្រោះ liquidity ប្រមូលផ្ដុំនៅទីនោះ (Chapter 12)</li>
<li>បើ SL តាម structure ធំពេក សម្រាប់ risk របស់អ្នក → <b>បន្ថយ lot</b> ឬ<b>រំលង</b> trade កុំបង្រួម SL</li></ul>
"""),
        ("Volatility-based Stop Loss · SL តាម ATR", """
<p><span class='en-term'>ATR</span> (Average True Range) វាស់ថាជាមធ្យមទៀនមួយដើរប៉ុន្មាន។ មាសមិនស្ងាត់ដូចគ្នារាល់ថ្ងៃទេ: ថ្ងៃខ្លះ ATR តូច ថ្ងៃខ្លះ ATR ធំ (ព័ត៌មាន ឬភ័យខ្លាច)។
<span class='en-term'>Volatility SL</span> = SL ដែលធំជាងចលនាធម្មតា ឧ. <b>1.5 – 2 × ATR</b> ពីចំណុចចូល។</p>
""" + bars([("ATR តូច $4", 8, BL), ("ATR ធម្មតា $6", 12, GOLD), ("ATR ធំ $10", 20, DN)],
           caption="ចំនួនលើរបារ = SL ជា $ · ឧទាហរណ៍ SL = 2 × ATR លើ timeframe ដដែល · ទីផ្សារលោតខ្លាំង → SL ត្រូវឆ្ងាយជាង → lot ត្រូវតូចជាង") + """
<table style='break-inside:avoid'><tr><th></th><th>Structural SL</th><th>Volatility SL</th></tr>
<tr><td>ផ្អែកលើ</td><td>Swing · OB · FVG</td><td>ATR (ចលនាជាមធ្យម)</td></tr>
<tr><td>ចំណុចខ្លាំង</td><td>មានអត្ថន័យ: ហួស = idea ខុស</td><td>សមស្របនឹងល្បឿនទីផ្សារ</td></tr>
<tr><td>ចំណុចខ្សោយ</td><td>ពេលខ្លះឆ្ងាយពេក ឬជិតពេក</td><td>មិនមើល structure</td></tr></table>
<div class='box ok'>✅ <b>វិធីល្អ: ប្រើទាំងពីរ</b>។ ដាក់ SL ក្រោម structure ហើយពិនិត្យថាវា<b>មិនតូចជាង</b>ប្រហែល 1 × ATR។ បើតូចជាង noise ធម្មតាអាចប៉ះវា។</div>
<div class='box tip'>💡 សញ្ញា ⭐ ក្នុង 🚨 <b>Signals</b> ប្រើ SL ប្រហែល <b>0.55%</b> នៃតម្លៃ (~$22 នៅ $4,000)។ ក្នុងការសាកល្បងរបស់ក្រុម SL <b>តូចជាងនេះ</b> ផ្ដល់លទ្ធផល<b>ខាត</b> ព្រោះត្រូវប៉ះដោយ noise ញឹកញាប់ពេក។</div>
"""),
        ("Target: Fixed ឬ Dynamic?", """
<p><span class='en-term'>Take Profit (TP)</span> អាចកំណត់តាមពីរវិធី:</p>
<table style='break-inside:avoid'><tr><th></th><th>Fixed target</th><th>Dynamic target</th></tr>
<tr><td>របៀប</td><td>ចម្ងាយថេរ ឧ. 2R · 3R</td><td>តាម chart: liquidity · swing · POC · VAH/VAL</td></tr>
<tr><td>ចំណុចខ្លាំង</td><td>សាមញ្ញ · ងាយសាកល្បង · គ្មានអារម្មណ៍</td><td>គោលដៅមានហេតុផល · តម្លៃច្រើនឈប់ទីនោះ</td></tr>
<tr><td>ចំណុចខ្សោយ</td><td>អាចនៅហួស level ធំ</td><td>ត្រូវការបទពិសោធន៍ · ងាយ "ផ្លាស់" តាមអារម្មណ៍</td></tr></table>
""" + zigzag([40, 70, 52, 80, 58, 64, 30, 45, 40, 95], {6: ("Entry", BL)},
             lines=[(80, 0, 7.6, "TP2 · Swing high (liquidity)", UP, True), (64, 0, 7.6, "TP1 · high ខាងក្នុង", GOLD, True), (18, 0, 7.6, "SL", DN, True)],
             caption="Dynamic target: TP1 នៅ high ខាងក្នុង · TP2 នៅ swing high ដែលមាន liquidity ខាងលើ") + """
<div class='box tip'>💡 គន្លឹះ: ដាក់ TP <b>មុន</b> level ធំបន្តិច (មិនមែនលើវាត្រង់ៗ) ព្រោះតម្លៃជាញឹកញាប់ប្រតិកម្មមុនដល់ level ពិត ហើយ spread ក៏ត្រូវគិតដែរ។</div>
"""),
        ("Risk-to-Reward Ratio · R:R", """
<p><span class='en-term'>R</span> = ចំនួនដែលអ្នកប្រថុយក្នុង trade មួយ។ <span class='en-term'>R:R</span> = ចំណេញដែលរំពឹង ÷ ការខាត។
ឧ. SL $22 · TP $66 → R:R = <b>1:3</b>។</p>
""" + position_box(caption="ទិញ 4,060 · SL 4,038 ($22 = 220 pips = 1R) · TP1 4,082 (1R) · TP2 4,126 (3R = 660 pips)") + """
<p>R:R ធំ មិនមែនល្អជានិច្ចទេ។ វាត្រូវតែគិតជាមួយ <b>win rate</b> (អត្រាឈ្នះ)។ តារាងខាងក្រោមគឺជា<b>គណិតវិទ្យា</b> (មិនមែនស្ថិតិ):
win rate អប្បបរមាដើម្បី "មិនខាត" (មិនទាន់គិត spread) = 1 ÷ (1 + R:R)។</p>
""" + bars([("1:0.5", 66.7, DN), ("1:1", 50, OR), ("1:2", 33.3, GOLD), ("1:3", 25, UP)], unit="%",
           caption="Win rate អប្បបរមា ដើម្បីស្មើសូន្យ តាម R:R នីមួយៗ") + """
<div class='box warn'>⚠️ R:R 1:5 ដែលមិនដែលដល់ TP គ្មានប្រយោជន៍ទេ។ R:R ត្រូវតែ<b>ប្រាកដនិយម</b>: គោលដៅត្រូវនៅកន្លែងដែលតម្លៃអាចទៅដល់បាន។
វាស់ win rate ពិតរបស់អ្នកក្នុង journal ហើយមើល 📈 <b>Proof</b> ក្នុង group ដើម្បីឃើញលទ្ធផលពិត ទាំងឈ្នះ និងខាត។</div>
"""),
        ("Partial Profit Taking · បិទមួយផ្នែក", """
<p><span class='en-term'>Partial close</span> = បិទមួយផ្នែកនៃ position នៅ TP1 ហើយទុកផ្នែកនៅសល់ឱ្យទៅ TP2។ វាផ្ដល់ចំណេញខ្លះមុន ហើយកាត់បន្ថយសម្ពាធចិត្ត។</p>
""" + flow([("ចូល 0.02 lot", "SL $22 · risk $44", BL), ("TP1 (1R)", "បិទ 0.01 · +$22", GOLD), ("SL → Entry", "break-even", OR), ("TP2 (3R)", "0.01 · +$66", UP)],
           caption="វិធីរបស់សញ្ញា ⭐: TP1 1R បិទពាក់កណ្ដាល + ប្ដូរ SL មក entry · TP2 3R") + """
<table style='break-inside:avoid'><tr><th>លទ្ធផល</th><th>គណនា (0.02 lot · $1 = $2)</th><th>សរុប</th></tr>
<tr><td>ប៉ះ SL មុន TP1</td><td>0.02 × −$22</td><td><b style='color:#FF3B30'>−$44 (−1R)</b></td></tr>
<tr><td>TP1 រួចត្រឡប់មក BE</td><td>+$22 + $0</td><td><b>+$22 (+0.5R)</b></td></tr>
<tr><td>TP1 រួចដល់ TP2</td><td>+$22 + (0.01 × $66)</td><td><b style='color:#34C759'>+$88 (+2R)</b></td></tr></table>
<div class='box tip'>💡 Lot អប្បបរមាលើ MT5 ជាធម្មតា 0.01។ បើអ្នកចូលតែ 0.01 lot អ្នក<b>មិនអាច</b>បិទពាក់កណ្ដាលបានទេ។ ត្រូវជ្រើសរើស: TP តែមួយ ឬចូល 0.02 lot (ប្រសិនបើ risk អនុញ្ញាត · Chapter 32)។</div>
"""),
        ("Break-even Management · ប្ដូរ SL មក Entry", """
<p><span class='en-term'>Break-even (BE)</span> = ប្ដូរ SL មកតម្លៃចូល។ ពេលនោះ trade នៅសល់ "គ្មានហានិភ័យ" (លើកលែង slippage ពេលព័ត៌មាន)។</p>
""" + zigzag([30, 48, 40, 62, 44, 54, 34, 30, 42], {1: ("Entry", BL), 3: ("TP1 ✓", GOLD)},
             lines=[(40, 1, 8, "SL → BE", OR, True)],
             caption="ប្ដូរ BE ក្រោយ TP1: ត្រឡប់មកវិញក៏នៅតែទុក +0.5R ពីផ្នែកដែលបានបិទ") + """
<table style='break-inside:avoid'><tr><th>ប្ដូរ BE</th><th>ផលល្អ</th><th>ផលអាក្រក់</th></tr>
<tr><td><b>លឿនពេក</b> (ឧ. +$3)</td><td>ខាតតិច</td><td>Pullback ធម្មតាប៉ះ BE · ខកខាន trade ល្អច្រើន</td></tr>
<tr><td><b>ក្រោយ TP1 / BOS ថ្មី</b></td><td>ការពារចំណេញពិត</td><td>នៅមាន pullback ខ្លះប៉ះ BE</td></tr>
<tr><td><b>មិនដែលប្ដូរ</b></td><td>ទុកលំហឱ្យ trade</td><td>Trade ឈ្នះអាចក្លាយជាខាតពេញ −1R</td></tr></table>
<div class='box ok'>✅ ច្បាប់សាមញ្ញ: ប្ដូរ BE ដោយផ្អែកលើ<b>ព្រឹត្តិការណ៍</b> (ដល់ TP1 · BOS ថ្មីក្នុងទិសរបស់អ្នក) មិនមែនដោយសារ "ភ័យ" ទេ។</div>
"""),
        ("Trailing Stop · SL ដើរតាមតម្លៃ", """
<p><span class='en-term'>Trailing stop</span> = SL ដែលផ្លាស់ទី<b>តែក្នុងទិសចំណេញ</b>។ វាអនុញ្ញាតឱ្យ trade ដែលរត់ខ្លាំងបន្តទៅ ខណៈពេលដែលការពារចំណេញដែលបានហើយ។</p>
""" + trailing(caption="Structure trailing: ក្រោយ HL ថ្មីនីមួយៗត្រូវបានបញ្ជាក់ ប្ដូរ SL ទៅក្រោម HL នោះ · SL មិនដែលចុះក្រោមវិញ") + """
<ul><li><b>Structure trail</b>: ប្ដូរ SL ក្រោម HL ថ្មី (ទិញ) ឬលើ LH ថ្មី (លក់) ក្រោយ swing ត្រូវបានបញ្ជាក់ · សមស្របជាមួយ PART 2</li>
<li><b>ATR trail</b>: SL នៅចម្ងាយ 2 × ATR ពីតម្លៃខ្ពស់បំផុត</li>
<li><b>MT5 Trailing Stop</b>: ចុចស្ដាំលើ position → Trailing Stop → ជ្រើសចម្ងាយ (pips/points)។ ⚠️ វាដំណើរការតែពេល <b>MT5 terminal បើក</b> និងភ្ជាប់អ៊ីនធឺណិតប៉ុណ្ណោះ</li></ul>
<div class='box warn'>⚠️ Trailing តឹងពេក (ឧ. $2 លើមាស) នឹងចេញភ្លាមៗដោយ pullback ធម្មតា។ Trail តាម <b>timeframe ដែលអ្នក trade</b> កុំ trail តាម 1m ពេល setup ជា 1H។</div>
"""),
        ("ពេលណាមិនត្រូវផ្លាស់ SL", """
<p>ច្បាប់មាស: <b>SL អាចខិតទៅជិតចំណេញបាន តែមិនដែលឆ្ងាយចេញទៀតទេ</b>។</p>
<table style='break-inside:avoid'><tr><th>ស្ថានភាព</th><th>❌ កុំធ្វើ</th><th>✅ ធ្វើ</th></tr>
<tr><td>តម្លៃជិតដល់ SL</td><td>ផ្លាស់ SL ឆ្ងាយទៀត "ឱ្យវាមានលំហ"</td><td>ទុកឱ្យ SL ធ្វើការងាររបស់វា</td></tr>
<tr><td>Trade ខាតហើយ</td><td>បន្ថែម lot (average down)</td><td>ទទួលយកការខាត −1R</td></tr>
<tr><td>📰 News ជិតចេញ</td><td>លុប SL ចោល</td><td>បិទ ឬកាត់ lot មុនព័ត៌មាន (Chapter 31)</td></tr>
<tr><td>ចំណេញតិចតួច</td><td>ប្ដូរ BE ភ្លាមដោយភ័យ</td><td>រង់ចាំ TP1 ឬ BOS ថ្មី</td></tr>
<tr><td>Idea នៅត្រឹមត្រូវ</td><td>ប្ដូរ TP ចុះជិតៗ ដោយសារភ័យ</td><td>តាមផែនការ ឬបិទមួយផ្នែក</td></tr></table>
<div class='box warn'>⚠️ ការផ្លាស់ SL ឆ្ងាយទៀតមួយដង អាចប្ដូរការខាត −1R ទៅជា −3R ឬ −5R។ ការខាតធំមួយអាចលុបចំណេញពីច្រើនសប្ដាហ៍។ <b>កុំ trade ដោយគ្មាន SL</b>។</div>
"""),
        ("កំហុសញឹកញាប់ និង Checklist", """
<ul><li>❌ SL តូចពេកក្នុង noise ដើម្បីបាន lot ធំ</li>
<li>❌ SL ត្រង់លើ swing ឬលេខមូល (ងាយត្រូវ sweep)</li>
<li>❌ R:R ស្អាតលើក្រដាស ប៉ុន្តែ TP ហួស level ធំដែលតម្លៃមិនទំនងទៅដល់</li>
<li>❌ ប្ដូរ BE លឿនពេក ហើយត្អូញថា "ទីផ្សារ hunt SL"</li>
<li>❌ ភ្លេចថា MT5 trailing stop ឈប់ដំណើរការពេលបិទកុំព្យូទ័រ</li></ul>
<div class='box ok'>✅ <b>Checklist មុនចុច:</b> ① SL នៅកន្លែង idea ខុស + buffer ② SL ≥ ប្រហែល 1 × ATR ③ TP នៅមុន level ពិត ④ R:R ≥ 1:2 ពីតម្លៃចូលពិត
⑤ ដឹងរួចថានឹងបិទមួយផ្នែក / BE នៅណា ⑥ Lot គណនាពី SL (Chapter 32)</div>
<div class='box tip'>💡 មើលសញ្ញាក្នុង 🚨 <b>Signals</b> និងរូប 📊 <b>Analysis</b>: សង្កេតថា SL នៅក្រោម/លើ structure ណា ហើយ TP1/TP2 នៅជិត level ណា។ ប្រើ <b>/check</b> ដើម្បីមើល structure បច្ចុប្បន្ន។</div>
"""),
    ],
    summary=["SL = កន្លែងដែល idea ខុស (structure) + buffer · ពិនិត្យជាមួយ ATR · lot គណនាពី SL",
             "TP: fixed (2R · 3R) ឬ dynamic (liquidity · swing · POC) · ដាក់មុន level ពិតបន្តិច",
             "R:R ត្រូវគិតជាមួយ win rate · win rate អប្បបរមា = 1 ÷ (1 + R:R)",
             "Partial នៅ TP1 + BE ក្រោយ TP1 · trailing តាម structure ក្នុង timeframe ដែលអ្នក trade",
             "SL ខិតជិតចំណេញបាន តែមិនដែលឆ្ងាយចេញ · កុំ trade ដោយគ្មាន SL"],
    exercise=["ទិញ 4,072 · HL ចុងក្រោយ 4,058 · ATR(15m) = $5។ ដាក់ SL ជាមួយ buffer $1.50។ SL ប៉ុន្មាន $ និងប៉ុន្មាន pips? ធំជាង 1 × ATR ឬទេ?",
              "លក់ 4,110 · SL 4,128 · TP1 1R · TP2 3R។ សរសេរតម្លៃ TP1 និង TP2។ ជាមួយ 0.02 lot គណនាលទ្ធផលទាំង 3 ករណី (SL · TP1→BE · TP1→TP2)។",
              "R:R របស់អ្នក 1:1.5។ តើ win rate អប្បបរមាប៉ុន្មាន % ដើម្បីមិនខាត?",
              "យក trade 10 ចុងក្រោយក្នុង journal: ប៉ុន្មានដងដែលអ្នកផ្លាស់ SL ឆ្ងាយចេញ ឬប្ដូរ BE លឿនពេក? លទ្ធផលល្អជាង ឬអាក្រក់ជាង?"],
)
