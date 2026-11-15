from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def candles(data, zones=None, lines=None, notes=None, w=420, h=200, caption=""):
    """Candlestick sketch. data = [(open, high, low, close)] in 0-100 (100 = top).
    zones = [(y_top, y_bottom, from_index, to_index, colour, label[, 'inside'|'above'|'below'])] shaded boxes (label on the right).
    lines = [(y, from_index, to_index, text, colour, dashed[, 'below'])] horizontal lines (text above, or below, the left end).
    notes = {index: (text, colour, 'top'|'bottom')}."""
    zones, lines, notes = zones or [], lines or [], notes or {}
    n = len(data)
    step = (w - 40) / n
    X = lambda i: 20 + (i + .5) * step
    Y = lambda v: h - 22 - v * (h - 44) / 100
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for zn in zones:
        (yt, yb, a, b, col, lab), pos = zn[:6], (zn[6] if len(zn) > 6 else "inside")
        x0, x1 = X(a) - step * .4, min(X(b) + step * .4, w - 8)
        out.append(f'<rect x="{x0:.1f}" y="{Y(yt):.1f}" width="{x1 - x0:.1f}" height="{Y(yb) - Y(yt):.1f}" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-width="1" stroke-dasharray="3 3"/>')
        if lab:
            ty = {"above": Y(yt) - 5, "below": Y(yb) + 13}.get(pos, (Y(yt) + Y(yb)) / 2 + 4)
            out.append(f'<text x="{x1 - 4:.1f}" y="{ty:.1f}" text-anchor="end" fill="{col}" class="lt">{lab}</text>')
    for ln in lines:
        (y, a, b, t, col, dash), below = ln[:6], len(ln) > 6 and ln[6] == "below"
        x0, x1 = X(a) - step * .4, min(X(b) + step * .4, w - 8)
        out.append(f'<line x1="{x0:.1f}" x2="{x1:.1f}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="{col}" stroke-width="1.5"'
                   + (' stroke-dasharray="5 4"' if dash else "") + "/>")
        if t:
            out.append(f'<text x="{x0 + 2:.1f}" y="{Y(y) + (14 if below else -5):.1f}" text-anchor="start" fill="{col}" class="lt">{t}</text>')
    for i, (o, hi, lo, c) in enumerate(data):
        cx, bw = X(i), step * .56
        col = UP if c >= o else DN
        out.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.6"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 1.5):.1f}" rx="1.5" fill="{col}"/>')
        if i in notes:
            t, ncol, pos = notes[i]
            ty = Y(hi) - 7 if pos == "top" else Y(lo) + 15
            out.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{ncol}" class="lt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def level_map(w=420, h=250, caption=""):
    """Liquidity map: key highs above price (BSL) and lows below price (SSL)."""
    lv = [("PWH · Prev Week High", "4,110", 22, DN), ("PDH · Prev Day High", "4,072", 62, DN), ("Asia High", "4,058", 98, DN),
          ("Asia Low", "4,041", 150, UP), ("PDL · Prev Day Low", "4,028", 186, UP), ("PWL · Prev Week Low", "3,985", 228, UP)]
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for name, price, y, col in lv:
        out.append(f'<line x1="14" x2="{w - 64}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        out.append(f'<text x="16" y="{y - 5}" fill="{col}" class="lt">{name}</text>')
        out.append(f'<text x="{w - 14}" y="{y + 4}" text-anchor="end" fill="{col}" class="lt">{price}</text>')
    pts = [(130, 140), (155, 108), (180, 132), (205, 104), (230, 138), (255, 112), (280, 124)]
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="280" cy="124" r="3.5" fill="{BL}"/><text x="290" y="128" text-anchor="start" fill="{BL}" class="pt">តម្លៃឥឡូវ</text>')
    out.append(f'<text x="{w - 70}" y="44" text-anchor="end" fill="{DN}" class="bt">BSL ↑ (Stop របស់អ្នក SELL)</text>')
    out.append(f'<text x="{w - 70}" y="210" text-anchor="end" fill="{UP}" class="bt">SSL ↓ (Stop របស់អ្នក BUY)</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=12, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="សាច់ប្រាក់រង់ចាំ (Liquidity)", title_en="Liquidity: BSL · SSL · Pools · Sweeps & Raids",
    intro="""ក្នុង Chapter 11 យើងបានដឹងថា ICT មើលទីផ្សារតាមរយៈ <b>liquidity</b>។ ជំពូកនេះនឹងបង្រៀនអ្នកឱ្យ<b>រកឃើញ</b> liquidity
លើ chart មាសដោយខ្លួនឯង: តើវាដេកនៅឯណា ហេតុអ្វីបានជាកន្លែងខ្លះខ្លាំងជាងកន្លែងខ្លះ ហើយនៅពេលដែលតម្លៃ<b>បោសយក</b> (sweep) វា
តើយើងគួរអានវាយ៉ាងដូចម្ដេច។ បើអ្នកយល់ជំពូកនេះ អ្នកនឹងលែងភ្ញាក់ផ្អើលពេល wick មួយប៉ះ Stop Loss របស់អ្នក ហើយតម្លៃរត់ទៅទិសដែលអ្នកគិតវិញ។""",
    sections=[
        ("Liquidity គឺជាអ្វី? (រំលឹកខ្លី)", """
<p><span class='en-term'>Liquidity</span> ក្នុងន័យ ICT គឺជា<b>ក្រុម orders</b> ដែលដេករង់ចាំនៅកម្រិតតម្លៃមួយ ជាពិសេស
<span class='en-term'>Stop Loss</span> និង <span class='en-term'>pending orders</span> (Buy Stop / Sell Stop)។
ពេលតម្លៃប៉ះកម្រិតនោះ orders ទាំងនេះ<b>ក្លាយជា market orders</b> ភ្លាមៗ ហើយផ្ដល់ "គូ" ឱ្យអ្នក trade ធំៗ បំពេញ order របស់ពួកគេ។</p>
<table style='break-inside:avoid'><tr><th>Order ដែលដេក</th><th>ពេលប៉ះ វាក្លាយជា</th><th>ដេកនៅ</th></tr>
<tr><td>SL របស់អ្នក <b>SELL</b></td><td><b>BUY</b></td><td>លើ high</td></tr>
<tr><td>Buy Stop (breakout buyers)</td><td><b>BUY</b></td><td>លើ high</td></tr>
<tr><td>SL របស់អ្នក <b>BUY</b></td><td><b>SELL</b></td><td>ក្រោម low</td></tr>
<tr><td>Sell Stop (breakout sellers)</td><td><b>SELL</b></td><td>ក្រោម low</td></tr></table>
<div class='box tip'>💡 ចាំងាយៗ: <b>លើ high = BUY orders</b> ច្រើន · <b>ក្រោម low = SELL orders</b> ច្រើន។ អ្នកធំដែលចង់ <b>SELL</b> ច្រើន ត្រូវការ BUY orders ច្រើន
ដូច្នេះ high ជាកន្លែងល្អសម្រាប់ពួកគេលក់។ អ្នកធំដែលចង់ <b>BUY</b> ច្រើន ត្រូវការ SELL orders ដូច្នេះ low ជាកន្លែងល្អសម្រាប់ពួកគេទិញ។</div>
"""),
        ("BSL និង SSL", """
<p><span class='en-term'>BSL</span> (Buy-side liquidity) = liquidity <b>ខាងលើ</b> swing high ។
<span class='en-term'>SSL</span> (Sell-side liquidity) = liquidity <b>ខាងក្រោម</b> swing low ។
Swing high/low ណាដែល<b>មើលឃើញច្បាស់</b> ទំនងជាមាន orders ច្រើន ព្រោះ trader ច្រើនដាក់ SL នៅទីនោះដូចគ្នា។</p>
""" + zigzag([40, 78, 55, 70, 30, 52, 22, 46, 60, 50], {1: ("Swing High", DN), 6: ("Swing Low", UP)},
            lines=[(78, 1, 9, "BSL $$", DN, True), (22, 6, 9, "SSL $$", UP, True)],
            caption="BSL ដេកលើ swing high · SSL ដេកក្រោម swing low") + """
<ul><li>ក្នុង <b>uptrend</b>: SSL នៅក្រោម HL ចុងក្រោយ = កន្លែងដែល SL របស់អ្នកទិញភាគច្រើនដេក</li>
<li>ក្នុង <b>downtrend</b>: BSL នៅលើ LH ចុងក្រោយ = កន្លែងដែល SL របស់អ្នកលក់ភាគច្រើនដេក</li>
<li>Liquidity <b>មិនបាត់</b>ទេ រហូតដល់តម្លៃមកយកវា ឬ structure ផ្លាស់ប្ដូរទាំងស្រុង</li></ul>
<div class='box warn'>⚠️ យើងមិនអាចឃើញចំនួន SL ពិតប្រាកដទេ។ BSL/SSL គឺជា<b>ការប៉ាន់ស្មានឡូជីខល</b>ថា "orders ទំនងជានៅទីនេះ" មិនមែនទិន្នន័យផ្ទាល់ពី broker ទេ។</div>
"""),
        ("Equal Highs និង Equal Lows", """
<p><span class='en-term'>Equal highs (EQH)</span> គឺជាកំពូល 2 ឬ 3 ដែលនៅ<b>កម្រិតស្ទើរតែដូចគ្នា</b>។
<span class='en-term'>Equal lows (EQL)</span> គឺជាបាតដែលនៅកម្រិតស្ទើរតែដូចគ្នា។ មនុស្សជាច្រើនឃើញវាជា
"double top / resistance ខ្លាំង" ហើយដាក់ SL ពីលើវាបន្តិច។ ដូច្នេះ EQH/EQL ច្រើនតែជា <b>liquidity ធំ</b>។</p>
""" + zigzag([30, 72, 50, 73, 45, 72.5, 40, 60, 92, 66], {1: ("EQH", DN), 3: ("EQH", DN), 5: ("EQH", DN), 8: ("Sweep $$", DN)},
            lines=[(72, 1, 7, "", DN, True)],
            caption="កំពូល 3 នៅ ~4,052 = EQH = BSL ច្បាស់ · តម្លៃរត់ឡើងបោសយក ហើយធ្លាក់វិញ") + """
<p>ឧទាហរណ៍លើ 15m: កំពូលទី 1 នៅ <b>4,052.30</b> កំពូលទី 2 នៅ <b>4,052.60</b>។ ខុសគ្នាត្រឹម $0.30 = <b>3 pips</b> → ចាត់ទុកជា EQH។
មិនមានលេខផ្លូវការថា "ស្មើ" ត្រូវខុសគ្នាប៉ុន្មាន pips ទេ។ ជាទូទៅ កាន់តែជិត និងកាន់តែមើលឃើញច្បាស់ កាន់តែទាក់ទាញ SL ច្រើន។</p>
<div class='box tip'>💡 ក្នុងភាសា ICT ពួកគេនិយាយថា EQH/EQL "<b>ស្អាតពេក</b>" (too clean)។ Level ដែលស្អាតពេក ច្រើនតែជា<b>គោលដៅ</b>របស់តម្លៃ មិនមែនជាជញ្ជាំងដែលការពារជានិច្ចទេ។</div>
"""),
        ("Previous Day High និង Low (PDH / PDL)", """
<p><span class='en-term'>PDH</span> = តម្លៃខ្ពស់បំផុតនៃថ្ងៃ trade មុន · <span class='en-term'>PDL</span> = តម្លៃទាបបំផុតនៃថ្ងៃ trade មុន។
Trader ពិភពលោកទាំងមូលមើលកម្រិតទាំងពីរនេះ ដូច្នេះវាជា liquidity ដែល<b>មើលឃើញបំផុត</b>មួយក្នុងមួយថ្ងៃៗ។</p>
<ul><li>ថ្ងៃ trade មាសនៅលើ <b>MT5</b> ធម្មតាចាប់ផ្ដើមតាមម៉ោង server របស់ broker (ច្រើនតែស្របនឹងការបិទ New York) ប្រហែល <b>04:00–05:00 ម៉ោងកម្ពុជា</b> អាស្រ័យលើរដូវ</li>
<li>មើលងាយបំផុត: ប្ដូរ chart ទៅ <b>D1</b> ហើយមើល high/low នៃទៀនម្សិលមិញ</li>
<li>ថ្ងៃដែលតម្លៃ<b>នៅក្នុង</b> PDH–PDL ពេញមួយថ្ងៃ = ថ្ងៃ range (inside day) · liquidity ទាំងសងខាងនៅដដែល</li></ul>
<table style='break-inside:avoid'><tr><th>ស្ថានការណ៍</th><th>ការអានដែលអាចកើត</th></tr>
<tr><td>Wick ឆ្លង PDH ហើយបិទក្រោមវិញ</td><td>Sweep BSL → អាចធ្លាក់ទៅរក PDL ឬ IRL ខាងក្រោម</td></tr>
<tr><td>បិទទៀន 1H/4H លើ PDH ហើយ retest បាន</td><td>Breakout ពិត (acceptance) → និន្នាការឡើងបន្ត</td></tr>
<tr><td>Wick ឆ្លង PDL ហើយបិទលើវិញ</td><td>Sweep SSL → អាចឡើងទៅរក PDH ឬ IRL ខាងលើ</td></tr></table>
"""),
        ("Previous Week High និង Low (PWH / PWL)", """
<p><span class='en-term'>PWH</span> និង <span class='en-term'>PWL</span> គឺជា high និង low នៃសប្ដាហ៍មុន (មើលលើ <b>W1</b>)។
វាជា liquidity កម្រិត <b>HTF</b> ដែលធំជាង PDH/PDL ព្រោះ swing trader និងមូលនិធិក៏មើលវាដែរ។</p>
""" + level_map(caption="ផែនទី liquidity មួយថ្ងៃ: ខាងលើ = BSL · ខាងក្រោម = SSL (តម្លៃជាឧទាហរណ៍)") + """
<ul><li>មាសអាចចំណាយពេល<b>ច្រើនថ្ងៃ</b> មុនពេលទៅដល់ PWH/PWL ដូច្នេះវាជាគោលដៅ<b>សប្ដាហ៍</b> មិនមែនគោលដៅ scalp ទេ</li>
<li>ការ sweep PWH/PWL ច្រើនតែកើតជាមួយព័ត៌មានធំ (NFP, CPI, FOMC) · មើលការព្រមាន 📰 News ក្នុង group</li>
<li>ពេល PDH ឬ PWH ស្ទើរតែនៅកម្រិតដូចគ្នា → liquidity <b>ត្រួតគ្នា</b> = pool ខ្លាំងជាងមុន</li></ul>
"""),
        ("Session Highs និង Lows", """
<p>Session នីមួយៗ (Chapter 16) បន្សល់ទុក high និង low របស់វា។ សម្រាប់ trader ក្នុងថ្ងៃ (intraday) ទាំងនេះជា liquidity ដែលប្រើញឹកញាប់បំផុត:</p>
<table style='break-inside:avoid'><tr><th>Session</th><th>ម៉ោងកម្ពុជា (winter)</th><th>តួនាទី liquidity</th></tr>
<tr><td>🌏 Asia</td><td>07:00–14:00</td><td>Range តូច · បង្កើត Asia High/Low ជា liquidity សងខាង</td></tr>
<tr><td>🇬🇧 London</td><td>14:00–19:00</td><td>ច្រើនតែ sweep Asia High ឬ Low មុនរត់ទិសពិត</td></tr>
<tr><td>🇺🇸 New York</td><td>19:30–00:00</td><td>អាច sweep London High/Low · ព័ត៌មាន US ម៉ោង 20:30</td></tr></table>
<p class='cap'>រដូវក្ដៅ (US DST) ម៉ោងលឿនជាង 1 ម៉ោង</p>
""" + flow([("Asia", "range តូច", GR), ("Asia H / L", "liquidity សងខាង", OR), ("London", "sweep ម្ខាង", DN), ("ចលនាពិត", "ទៅម្ខាងទៀត?", UP)],
           caption="លំនាំដែលឃើញញឹកញាប់: London បោស Asia high ឬ low មុន (មិនមែនរាល់ថ្ងៃទេ)") + """
<div class='box tip'>💡 រូប 📊 Analysis របស់ XAU.KH ចេញមុន session នីមួយៗ (Asia · London · New York) ហើយគូរ high/low សំខាន់ៗឱ្យរួច។
មុន London បើក សូមសម្គាល់ <b>Asia High</b> និង <b>Asia Low</b> ជាមុនសិន។</div>
"""),
        ("Liquidity Pools: កន្លែងដែល orders ប្រមូលផ្ដុំ", """
<p><span class='en-term'>Liquidity pool</span> គឺជាតំបន់ដែល liquidity <b>ច្រើនប្រភេទ</b>ប្រមូលផ្ដុំនៅកន្លែងតែមួយ។
ឧទាហរណ៍ EQH + PDH + Asia High នៅក្បែរ 4,058–4,060។ Pool កាន់តែធំ កាន់តែទាក់ទាញតម្លៃ។ ប្រើតារាងខាងក្រោមដើម្បីវាយតម្លៃ:</p>
<table style='break-inside:avoid'><tr><th>កត្តា</th><th>Pool ខ្សោយ</th><th>Pool ខ្លាំង</th></tr>
<tr><td>Timeframe</td><td>5m swing តូច</td><td>4H / D1 / W1 high-low</td></tr>
<tr><td>ភាពច្បាស់</td><td>Swing តូចមិនសូវឃើញ</td><td>EQH/EQL · កំពូលដែលគ្រប់គ្នាឃើញ</td></tr>
<tr><td>ការត្រួតគ្នា</td><td>Level តែមួយ</td><td>PDH + EQH + Session high ជាមួយគ្នា</td></tr>
<tr><td>ការប៉ះ</td><td>ទើបបង្កើត</td><td>ប៉ះ 2–3 ដង ហើយមិនទាន់បែក</td></tr>
<tr><td>ស្ថានភាព</td><td>ត្រូវបានបោសរួច ($$)</td><td>មិនទាន់ត្រូវយក (untapped)</td></tr></table>
<div class='box warn'>⚠️ Liquidity ដែល<b>ត្រូវបានបោសរួច</b>មិនមែនជាគោលដៅទៀតទេ។ នៅលើរូប Analysis សញ្ញា <b>$$</b> មានន័យថា liquidity នោះត្រូវបានយករួចហើយ។
កុំដាក់ TP នៅ level ដែលត្រូវបានបោសរួច ដោយគិតថាវានៅទាក់ទាញតម្លៃ។</div>
"""),
        ("Sweep និង Raid: ការបោសយក Liquidity", """
<p><span class='en-term'>Liquidity sweep</span> (ឬ <span class='en-term'>stop hunt</span>) កើតឡើងពេលតម្លៃ<b>ឆ្លងកាត់</b> high ឬ low ចាស់ ធ្វើឱ្យ SL ត្រូវប៉ះ
ប៉ុន្តែទៀន<b>បិទត្រឡប់ចូល</b>វិញ។ <span class='en-term'>Raid</span> គឺជាពាក្យស្រដៀងគ្នា ច្រើនប្រើពេលតម្លៃរត់ទៅយក liquidity យ៉ាងលឿន ដោយចេតនា
ហើយមិនបន្តទៅមុខ។ ពួកយើងប្រើពាក្យទាំងពីរ<b>ជិតៗគ្នា</b>។</p>
""" + candles([(64, 68, 52, 55), (55, 58, 44, 47), (47, 50, 34, 38), (38, 44, 31, 41), (41, 43, 14, 37), (37, 52, 35, 50), (50, 64, 48, 62), (62, 76, 60, 74)],
              lines=[(31, 0, 7, "SSL · Low ចាស់ 4,020", UP, True, "below")],
              notes={4: ("Sweep $$", DN, "bottom"), 7: ("ឡើងវិញ", UP, "top")},
              caption="Wick ធ្លាក់ក្រោម 4,020 ប្រហែល $1.70 (17 pips) ប៉ុន្តែបិទលើវិញ = SSL sweep") + """
<table style='break-inside:avoid'><tr><th></th><th>Sweep (បោស)</th><th>Breakout ពិត (acceptance)</th></tr>
<tr><td>ការបិទទៀន</td><td>Wick ឆ្លង · <b>បិទត្រឡប់ចូល</b></td><td><b>បិទហួស</b> level ហើយទៀនបន្ទាប់នៅខាងក្រៅ</td></tr>
<tr><td>បន្ទាប់មក</td><td>ទៀនរុញទៅទិស<b>ផ្ទុយ</b>ខ្លាំង</td><td>Retest level ចាស់ ហើយការពារបាន</td></tr>
<tr><td>Structure</td><td>ច្រើនតែមាន CHOCH ផ្ទុយទិសតាមក្រោយ</td><td>BOS ក្នុងទិស breakout</td></tr></table>
<div class='box tip'>💡 Sweep នេះពន្យល់ពីបទពិសោធន៍ដែលអ្នក trade ច្រើនមាន: "SL ខ្ញុំត្រូវប៉ះ ហើយតម្លៃរត់ទៅទិសខ្ញុំវិញ"។ ដំណោះស្រាយ<b>មិនមែន</b>ការលុប SL ទេ
តែជាការដាក់ SL នៅ<b>កន្លែងសមហេតុផល</b> (ក្រោយ liquidity ឬក្រោយ structure) និងប្រើ lot តូចឱ្យសមនឹងចម្ងាយ SL នោះ (Chapter 30)។</div>
"""),
        ("Sweep + CHOCH: Setup Reversal ដ៏ល្បី", """
<p>Sweep តែឯង<b>មិនទាន់គ្រប់គ្រាន់</b>ដើម្បីចូល trade ទេ។ Setup ដែល ICT trader ច្រើនប្រើគឺ sweep <b>រួចហើយ</b>មាន
<span class='en-term'>CHOCH / MSS</span> ផ្ទុយទិស ជាមួយ <span class='en-term'>displacement</span> (Chapter 9)។</p>
""" + zigzag([85, 55, 70, 40, 58, 30, 50, 20, 66, 54, 80], {3: ("LL", DN), 4: ("LH", DN), 5: ("Low", UP), 7: ("Sweep $$", DN), 8: ("CHOCH ↑", BL)},
            lines=[(30, 5, 8, "", UP, True), (58, 4, 9, "", BL, False)],
            caption="Downtrend → បោស SSL ក្រោម Low → បិទលើ LH ចុងក្រោយ (CHOCH) → ត្រៀមរក BUY") + flow(
            [("Liquidity", "ដឹងគោលដៅ", OR), ("Sweep", "wick + បិទចូល", DN), ("CHOCH", "មាន displacement", BL), ("Entry", "FVG / OB", UP)],
            caption="លំដាប់: កុំលោតចូលភ្លាមពេលឃើញ wick · រង់ចាំ CHOCH មុន") + """
<ul><li><b>SL</b>: ក្រោយចុង wick នៃ sweep (ឧ. ក្រោម 4,018 បើ wick ទៅដល់ 4,018.30)</li>
<li><b>Target</b>: liquidity ខាងម្ខាងទៀត (BSL ដែលនៅជិតបំផុត ឬ PDH)</li>
<li><b>ទំហំ risk</b>: SL ចម្ងាយ $5 = 50 pips · នៅ 0.01 lot ខាតប្រហែល $5 បើ SL ប៉ះ</li></ul>
<div class='box ok'>✅ Entry នៅក្នុង FVG ដែលកើតពី displacement នេះ នឹងរៀននៅ Chapter 13 និង Order Block នៅ Chapter 14។</div>
"""),
        ("កំហុសញឹកញាប់ និងការអនុវត្តក្នុង Group", """
<ul><li>❌ ហៅរាល់ wick ថា "sweep" (sweep ដែលមានន័យ ត្រូវនៅ liquidity <b>សំខាន់</b> ដូចជា PDH/PDL, EQH/EQL, session high/low)</li>
<li>❌ BUY ភ្លាមពេលតម្លៃធ្លាក់ក្រោម low ដោយគិតថា "នេះជា sweep" មុនទៀនបិទ (វាអាចជា breakout ពិត)</li>
<li>❌ ដាក់ SL <b>ចំ</b>ក្រោម EQL ឬ low ច្បាស់ ដែលជាកន្លែង SL របស់មនុស្សគ្រប់គ្នា</li>
<li>❌ ភ្លេចថា liquidity ខាង<b>ផ្ទុយ</b>ក៏អាចជាគោលដៅដែរ · តម្លៃមិនចាំបាច់ទៅទិសដែលអ្នកចង់ទេ</li></ul>
<div class='box tip'>💡 ក្នុង group XAU.KH: រូប 📊 Analysis សម្គាល់ <b>ELQ</b> (liquidity ចុង range) <b>ILQ</b> (liquidity ខាងក្នុង) និង <b>$$</b> (sweep រួច)។
វាយ <b>/check</b> ដើម្បីមើល bias និង level បច្ចុប្បន្ន។ នៅ 🚨 Signals និង 📈 Proof អ្នកអាចសិក្សាថា entry និង SL ត្រូវបានដាក់ទាក់ទងនឹង liquidity យ៉ាងដូចម្ដេច
ហើយចាំថា signal ខ្លះក៏ខាតដែរ។</div>
"""),
    ],
    summary=["BSL = orders លើ high (SL អ្នក SELL) · SSL = orders ក្រោម low (SL អ្នក BUY)",
             "EQH/EQL, PDH/PDL, PWH/PWL និង session high/low ជា liquidity ដែលមើលឃើញច្បាស់",
             "Liquidity pool ខ្លាំង = HTF + ច្បាស់ + ត្រួតគ្នា + មិនទាន់ត្រូវបោស",
             "Sweep = wick ឆ្លង ហើយបិទត្រឡប់ចូល · Breakout = បិទហួស ហើយ retest បាន",
             "Sweep តែឯងមិនគ្រប់គ្រាន់ · រង់ចាំ CHOCH + displacement មុនគិតចូល"],
    exercise=["នៅលើ chart មាស គូរ PDH, PDL, PWH, PWL, Asia High និង Asia Low សម្រាប់ថ្ងៃនេះ។",
              "រក EQH ឬ EQL មួយលើ 15m។ ខុសគ្នាប៉ុន្មាន pips?",
              "រក sweep មួយក្នុង 5 ថ្ងៃចុងក្រោយ។ តើមាន CHOCH តាមក្រោយឬអត់? តម្លៃបន្តទៅដល់ liquidity ខាងម្ខាងទៀតឬអត់?",
              "ប្រៀបធៀបការសម្គាល់របស់អ្នកជាមួយ ELQ / ILQ / $$ លើរូប 📊 Analysis ថ្ងៃនេះ។"],
)
