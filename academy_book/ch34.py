from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def trade_levels(w=420, h=200, caption=""):
    """A buy trade drawn as price levels: SL, entry, TP1 (1R), TP2 (3R), with the 12h time exit on the right."""
    lv = [("TP2 · 3R", 4080, UP), ("TP1 · 1R", 4060, UP), ("Entry", 4050, BL), ("SL · −1R", 4040, DN)]
    Y = lambda p: 22 + (4084 - p) * (h - 44) / 48
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    out.append(f'<rect x="70" y="{Y(4080):.1f}" width="230" height="{Y(4050) - Y(4080):.1f}" fill="{UP}" fill-opacity=".10"/>')
    out.append(f'<rect x="70" y="{Y(4050):.1f}" width="230" height="{Y(4040) - Y(4050):.1f}" fill="{DN}" fill-opacity=".10"/>')
    path = [(70, 4050), (95, 4046), (120, 4055), (145, 4052), (175, 4062), (200, 4058), (235, 4071), (260, 4067), (290, 4080)]
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{x},{Y(p):.1f}" for i, (x, p) in enumerate(path))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    for t, p, col in lv:
        out.append(f'<line x1="70" x2="300" y1="{Y(p):.1f}" y2="{Y(p):.1f}" stroke="{col}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        out.append(f'<text x="64" y="{Y(p) + 4:.1f}" text-anchor="end" fill="{col}" class="lt">{p:,}</text>')
        out.append(f'<text x="306" y="{Y(p) + 4:.1f}" fill="{col}" class="lt">{t}</text>')
    out.append(f'<circle cx="175" cy="{Y(4060):.1f}" r="4" fill="{UP}"/>')
    out.append(f'<text x="78" y="{Y(4071):.1f}" fill="{UP}" class="st">● TP1: បិទពាក់កណ្ដាល · SL → entry</text>')
    out.append(f'<line x1="300" x2="300" y1="16" y2="{h - 16}" stroke="{GR}" stroke-width="1.2"/>')
    out.append(f'<text x="296" y="{h - 6}" text-anchor="end" fill="{GR}" class="st">12 ម៉ោង = បិទទោះនៅណាក៏ដោយ</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def rule_meter(w=420, h=150, caption=""):
    """Vague → measurable: the same idea written three ways, from a bad rule to a testable rule."""
    rows = [("❌ មិនច្បាស់", "\"ទិញពេលមាសមើលទៅខ្លាំង\"", DN),
            ("⚠️ ល្អជាង", "\"ទិញពេល 4H បំបែកឡើង\"", OR),
            ("✅ វាស់បាន", "\"ទិញពេលទៀន 4H បិទលើ high 30 ទៀនមុន\"", UP)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (tag, txt, col) in enumerate(rows):
        y = 14 + i * 44
        out.append(f'<rect x="12" y="{y}" width="{w - 24}" height="34" rx="9" fill="{col}" fill-opacity=".10" stroke="{col}"/>')
        out.append(f'<text x="24" y="{y + 22}" fill="{col}" class="bt">{tag}</text>')
        out.append(f'<text x="118" y="{y + 22}" fill="#1C1C1E" class="st">{txt}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=34, part="PART 9 · Strategy Development & Testing",
    title_km="ការកសាង Strategy", title_en="Building a Trading Strategy: Rules · Entry · Exit · Filters · Invalidation · Trading Plan",
    intro="""រហូតមកដល់ពេលនេះ អ្នកបានរៀន<b>ឧបករណ៍</b>ជាច្រើន: structure, liquidity, FVG, session, risk។ ប៉ុន្តែឧបករណ៍ច្រើន<b>មិនមែន</b>ជា strategy ទេ។
<span class='en-term'>Strategy</span> គឺជា<b>ច្បាប់សរសេរច្បាស់</b> ដែលប្រាប់ថា: ចូលពេលណា · ចេញពេលណា · ពេលណាមិន trade · និង idea ខុសនៅពេលណា។
ច្បាប់ល្អ = មនុស្ស <b>2 នាក់</b>អានវា ហើយយក trade <b>ដូចគ្នា</b>។ ជំពូកនេះបង្រៀនពីរបៀបសរសេរច្បាប់ទាំងនោះ ហើយភ្ជាប់វាទៅជា
<span class='en-term'>Trading Plan</span> ពេញលេញ ដែលអ្នកអាចសាកល្បង (Chapter 35) មុនប្រើលុយពិត។""",
    sections=[
        ("Idea · Strategy · Trading Plan", """
<p>ពាក្យទាំងបីនេះ ច្រើនតែត្រូវបានប្រើលាយគ្នា ប៉ុន្តែវាខុសគ្នា:</p>
<table style='break-inside:avoid'><tr><th></th><th>អត្ថន័យ</th><th>ឧទាហរណ៍</th></tr>
<tr><td><b>Idea</b></td><td>គំនិតមួយអំពីទីផ្សារ</td><td>"មាសច្រើនតែបន្តទិស ក្រោយបំបែក range ធំ"</td></tr>
<tr><td><b>Strategy</b></td><td>ច្បាប់ entry · exit · filter ដែលវាស់បាន</td><td>"ទិញពេល 4H បិទលើ high 30 ទៀន · SL · TP · 12h"</td></tr>
<tr><td><b>Trading Plan</b></td><td>Strategy + risk + ម៉ោង + journal + ការពិនិត្យ</td><td>"Risk 1% · trade 3 ដង/ថ្ងៃ · ពិនិត្យរាល់ថ្ងៃសៅរ៍"</td></tr></table>
""" + flow([("Idea", "គំនិត", GR), ("Rules", "សរសេរច្បាប់", BL), ("Backtest", "Chapter 35", GOLD), ("Forward", "Demo · Ch 36", PU), ("Live", "lot តូច", UP)],
           caption="ផ្លូវរបស់ strategy មួយ: idea ត្រូវក្លាយជាច្បាប់ ហើយត្រូវសាកល្បង មុនប្រើលុយពិត") + """
<div class='box tip'>💡 Idea ភាគច្រើន<b>មិនឆ្លង</b>ការសាកល្បងទេ។ នោះជារឿងធម្មតា។ គោលដៅមិនមែនរក idea "ស្អាត" ទេ គឺរក idea ដែល<b>នៅរស់</b>ក្រោយការសាកល្បងដោយស្មោះត្រង់។</div>
"""),
        ("Strategy Rules: ច្បាប់ដែលវាស់បាន", """
<p>ច្បាប់ល្អមានលក្ខណៈ 3: <b>ច្បាស់</b> (គ្មានពាក្យ "មើលទៅ" "ប្រហែល") · <b>វាស់បាន</b> (មានលេខ ឬលក្ខខណ្ឌ យល់ព្រម/មិនយល់ព្រម) · <b>ដូចគ្នាគ្រប់ពេល</b> (មិនប្ដូរតាមអារម្មណ៍)។</p>
""" + rule_meter(caption="Idea ដដែល សរសេរ 3 របៀប · តែជួរចុងក្រោយទេ ដែលអាចសាកល្បងបាន") + """
<table style='break-inside:avoid'><tr><th>ច្បាប់មិនល្អ</th><th>ច្បាប់ល្អ</th></tr>
<tr><td>"SL នៅកន្លែងសមរម្យ"</td><td>"SL ក្រោម swing low 15m ចុងក្រោយ + $1"</td></tr>
<tr><td>"Trade ពេលទីផ្សារសកម្ម"</td><td>"Trade តែ 14:00–23:00 ម៉ោងភ្នំពេញ"</td></tr>
<tr><td>"កុំ trade ពេលព័ត៌មាន"</td><td>"⛔ 15 នាទីមុន និងក្រោយព័ត៌មាន 🔴 ក្នុង 📰 News"</td></tr>
<tr><td>"ចេញពេលវាឈប់ឡើង"</td><td>"TP1 = 1R · TP2 = 3R · បិទក្រោយ 12 ម៉ោង"</td></tr></table>
<div class='box warn'>⚠️ <b>Discretion</b> (ការវិនិច្ឆ័យផ្ទាល់ខ្លួន) មិនមែនជារឿងហាមឃាត់ទេ ប៉ុន្តែវាពិបាក<b>សាកល្បង</b>។ សម្រាប់អ្នកចាប់ផ្ដើម ចូរចាប់ផ្ដើមជាមួយច្បាប់<b>100% ច្បាស់</b>សិន។</div>
"""),
        ("Entry Conditions: លក្ខខណ្ឌចូល", """
<p>Entry ល្អ ច្រើនតែមាន 3 ស្រទាប់:</p>
<ul><li><b>Context</b> (បរិបទ): HTF bias · structure 4H/1H · តំបន់ premium / discount</li>
<li><b>Setup</b>: ស្ថានភាពដែលអ្នករង់ចាំ (ឧ. liquidity sweep · breakout range)</li>
<li><b>Trigger</b> (កែះ): ព្រឹត្តិការណ៍ច្បាស់មួយ ដែលប្រាប់ថា "ចូលឥឡូវ" (ឧ. <b>ទៀនបិទ</b>ហួសកម្រិត · CHOCH 5m)</li></ul>
""" + zigzag([40, 62, 45, 64, 47, 63, 50, 88, 80, 95], {1: ("H", GR), 3: ("H", GR), 5: ("H", GR), 7: ("Trigger", UP), 8: ("Entry", BL)},
             lines=[(64, 0, 7, "", OR, True), (64, 0, 2, "high 30 ទៀន", OR, True)],
             caption="Setup = range មាន high ច្បាស់ · Trigger = ទៀនបិទលើ high · Entry = ក្រោយការបិទ (មិនមែនមុន)") + """
<div class='box ok'>✅ <b>ឧទាហរណ៍ច្បាប់ entry (ទិញ)</b>:<br>1. ទៀន 4H <b>បិទ</b>លើ high នៃ 30 ទៀនមុន<br>2. 📏 Day Meter ≥ 70%<br>3. ទៀនបំបែក<b>បិទខ្លាំង</b> (បិទនៅផ្នែកខាងលើ 30% នៃទៀន)<br>4. គ្មានព័ត៌មាន 🔴 ក្នុង 15 នាទីខាងមុខ<br>→ ទាំង 4 = <b>បាទ</b> → ចូល។ មួយ "ទេ" → មិនចូល។</div>
<div class='box tip'>💡 Entry ក្នុង 🚨 <b>Signals</b> របស់ XAU.KH ក៏សរសេរជាលក្ខខណ្ឌច្បាស់ៗដូចនេះដែរ (4H breakout + Day Meter + trend ស្អាត)។ អ្នកអាចប្រៀបធៀបច្បាប់របស់អ្នកជាមួយ /check ។</div>
"""),
        ("Exit Conditions: លក្ខខណ្ឌចេញ", """
<p>Trader ភាគច្រើនគិតច្រើនពី entry តែ<b>ចំណេញ ឬខាត</b>ត្រូវបានកំណត់ដោយ exit។ Exit ត្រូវសរសេរ<b>មុន</b>ចូល trade និងគ្របដណ្ដប់ 4 ករណី:</p>
<ul><li><span class='en-term'>Stop Loss</span>: idea ខុស → ចេញ (−1R)</li>
<li><span class='en-term'>Take Profit</span>: TP1 / TP2 (គិតជា R)</li>
<li><span class='en-term'>Break-even</span>: ពេលណាផ្លាស់ SL ទៅ entry</li>
<li><span class='en-term'>Time exit</span>: បិទក្រោយ X ម៉ោង ប្រសិនបើគ្មានអ្វីកើតឡើង</li></ul>
""" + trade_levels(caption="ឧទាហរណ៍ Buy $4,050 · SL $4,040 ($10 = 100 pips) · TP1 1R $4,060 · TP2 3R $4,080 · ពេលអតិបរមា 12 ម៉ោង") + """
<table style='break-inside:avoid'><tr><th>ករណី (0.02 lot · risk $20)</th><th>លទ្ធផល</th></tr>
<tr><td>SL ប៉ះមុន TP1</td><td>−$20 = <b>−1R</b></td></tr>
<tr><td>TP1 ប៉ះ (បិទ 0.01) → ក្រោយមកប៉ះ entry</td><td>+$10 = <b>+0.5R</b></td></tr>
<tr><td>TP1 ប៉ះ → TP2 ប៉ះ</td><td>+$10 + $30 = <b>+2R</b></td></tr>
<tr><td>12 ម៉ោងហួស មិនប៉ះអ្វីទាំងអស់</td><td>បិទតាមតម្លៃពេលនោះ (ឧ. +$4 = +0.2R)</td></tr></table>
<div class='box warn'>⚠️ Lot តូចបំផុតគឺ <b>0.01</b>។ បើចង់បិទ "ពាក់កណ្ដាល" នៅ TP1 អ្នកត្រូវបើកយ៉ាងតិច <b>0.02 lot</b>។ គណនាវាក្នុង risk 1% របស់អ្នក (Chapter 32)។</div>
"""),
        ("Market Filters: ពេលណាច្បាប់ដំណើរការល្អជាង", """
<p><span class='en-term'>Filter</span> គឺជាលក្ខខណ្ឌបន្ថែម ដែល<b>បិទ</b> strategy ក្នុងស្ថានភាពដែលវាខ្សោយ។ Filter ញឹកញាប់សម្រាប់មាស:</p>
<ul><li><b>Session</b>: London / New York ធៀបនឹង Asia ស្ងាត់ (Chapter 16)</li>
<li><b>News</b>: CPI · NFP · FOMC (📰 News)</li>
<li><b>Trend quality</b>: trend ស្អាត ធៀបនឹង choppy (ឡើងចុះគ្មានទិស)</li>
<li><b>Volatility</b>: ថ្ងៃស្ងាត់ពេក ឬព្រៃពេក · ATR</li>
<li><b>Spread</b>: spread ធំ (ពេលបើកទីផ្សារ · ព័ត៌មាន) → មិនចូល</li></ul>
""" + bars([("DM ខ្ពស់ · ចាស់", 0.33, UP), ("DM ខ្ពស់ · ថ្មី", 0.60, UP), ("DM ទាប · ចាស់", 0.01, GR), ("DM ទាប · ថ្មី", -0.08, DN)], unit="R",
           caption="Avg R នៃ 4H breakout តាម Day Meter (DM) · ទិន្នន័យចាស់ 70% / ថ្មី 30% · studies/RESULTS.md (មាស 2 ឆ្នាំ 5m · ថ្លៃ $0.40/trade)") + """
<div class='box tip'>💡 Filter ល្អត្រូវ<b>ជួយទាំងលើទិន្នន័យចាស់ និងថ្មី</b> (ដូចក្រាហ្វខាងលើ)។ Filter ដែលជួយតែលើទិន្នន័យមួយផ្នែក ច្រើនតែជាសំណាង។ ក្នុងកំណត់ត្រាស្រាវជ្រាវដដែល filter "session" ល្អលើទិន្នន័យចាស់ តែអាក្រក់លើថ្មី ដូច្នេះ<b>មិនត្រូវបានប្រើ</b>ទេ។</div>
<div class='box warn'>⚠️ កុំបន្ថែម filter រហូតដល់គ្មាន trade នៅសល់។ Filter នីមួយៗ<b>កាត់ចំនួន trade</b> ហើយ trade តិច = លទ្ធផលមិនអាចទុកចិត្ត (Chapter 35)។</div>
"""),
        ("Trade Invalidation: idea ខុសនៅពេលណា?", """
<p><span class='en-term'>Invalidation</span> គឺជាចំណុចដែលហេតុផលនៃ trade <b>លែងពិត</b>។ វាមាន 2 ពេល:</p>
<ul><li><b>មុនចូល</b>: setup ត្រូវលុបចោល (ឧ. តម្លៃបិទត្រឡប់ក្នុង range មុនទៀន trigger · ព័ត៌មានធំកំពុងមក)</li>
<li><b>ក្រោយចូល</b>: structure ដែលគាំទ្រ trade ត្រូវបានបំបែក → នោះជាកន្លែង SL</li></ul>
""" + zigzag([30, 58, 44, 72, 56, 66, 50, 38, 30], {2: ("HL", UP), 3: ("HH", UP), 4: ("HL ចុងក្រោយ", OR), 7: ("✕ ខុស", DN)},
             lines=[(56, 4, 8, "Invalidation", DN, True)],
             caption="ទិញក្នុង uptrend: បិទក្រោម HL ចុងក្រោយ = structure ឡើងខូច = idea ខុស → SL នៅទីនេះ") + """
<div class='box ok'>✅ សរសេរ invalidation ជាប្រយោគមួយ មុនចុចទិញ: <i>"ខ្ញុំខុស ប្រសិនបើ 15m បិទក្រោម $4,040"</i>។ បើអ្នកមិនអាចសរសេរវាបាន អ្នកមិនទាន់មាន trade ទេ។</div>
<div class='box warn'>⚠️ កុំរំកិល SL ឱ្យឆ្ងាយ ពេលតម្លៃជិតដល់។ ការធ្វើបែបនោះ = ប្ដូរ invalidation ក្រោយចូល = ប្ដូរ strategy ពេលកំពុង trade។</div>
"""),
        ("No-Trade Conditions: សរសេរពេលមិន trade", """
<p>Strategy អាជីព សរសេរពេល<b>មិន trade</b> ច្បាស់ដូច entry ដែរ។ "មិន trade" គឺជាការសម្រេចចិត្តមួយ មិនមែនការខ្ជិលទេ។</p>
<table style='break-inside:avoid'><tr><th>ស្ថានភាព</th><th>ហេតុផល</th></tr>
<tr><td>15 នាទីមុន/ក្រោយព័ត៌មាន 🔴</td><td>Spread ធំ · slippage · ចលនាព្រៃ</td></tr>
<tr><td>Market choppy · គ្មាន structure ច្បាស់</td><td>Breakout បរាជ័យញឹកញាប់</td></tr>
<tr><td>ថ្ងៃសុក្រយប់ · មុនចុងសប្ដាហ៍</td><td>Gap ថ្ងៃច័ន្ទ · liquidity ទាប</td></tr>
<tr><td>ថ្ងៃឈប់សម្រាកធំ (US / UK)</td><td>ទីផ្សារស្ងាត់ · ចលនាមិនធម្មតា</td></tr>
<tr><td>Spread ធំជាងធម្មតា</td><td>ថ្លៃចូលខ្ពស់ · ស៊ី R</td></tr>
<tr><td>ដល់ max daily loss ឬខាត 2 ដងជាប់</td><td>ច្បាប់ risk (Chapter 32 · 33)</td></tr>
<tr><td>ហត់ · ខឹង · ឈឺ · មានបញ្ហាផ្ទាល់ខ្លួន</td><td>ការសម្រេចចិត្តខ្សោយ (Chapter 38)</td></tr></table>
""" + flow([("មានព័ត៌មាន?", "បាទ → ⛔", DN), ("Choppy?", "បាទ → ⛔", OR), ("ដល់ limit?", "បាទ → ⛔", PU), ("Setup ពេញ?", "បាទ → ✅", UP)],
           caption="ពិនិត្យ no-trade មុន · បន្ទាប់មកទើបរក setup") + """
"""),
        ("Trading Plan ពេញលេញ: Template", """
<p><span class='en-term'>Trading Plan</span> ភ្ជាប់ strategy ជាមួយ risk និងទម្លាប់ប្រចាំថ្ងៃ។ ចម្លង template នេះ ហើយបំពេញតាមខ្លួនឯង:</p>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>សំណួរ</th></tr>
<tr><td>1. Market</td><td>Trade អ្វី? (ឧ. XAUUSD តែមួយ)</td></tr>
<tr><td>2. Timeframes</td><td>Bias លើ TF ណា? Entry លើ TF ណា?</td></tr>
<tr><td>3. ម៉ោង</td><td>Trade ពីម៉ោងណា ដល់ម៉ោងណា (ម៉ោងភ្នំពេញ)?</td></tr>
<tr><td>4. Setup + Entry</td><td>លក្ខខណ្ឌទាំងអស់ (បញ្ជី បាទ/ទេ)</td></tr>
<tr><td>5. Exit</td><td>SL · TP1 · TP2 · break-even · time exit</td></tr>
<tr><td>6. Filters + No-trade</td><td>ពេលណាមិនចូល?</td></tr>
<tr><td>7. Risk</td><td>% / trade · trade អតិបរមា/ថ្ងៃ · max daily/weekly loss</td></tr>
<tr><td>8. Journal</td><td>កត់អ្វីខ្លះ? រូប chart មុន/ក្រោយ</td></tr>
<tr><td>9. Review</td><td>ពិនិត្យពេលណា? (ឧ. រាល់ថ្ងៃសៅរ៍)</td></tr>
<tr><td>10. ប្ដូរច្បាប់</td><td>ប្ដូរតែក្រោយ 30+ trade និងតាម backtest</td></tr></table>
<div class='box tip'>💡 Plan ល្អ <b>ខ្លី</b> (1 ទំព័រ)។ បើវាវែងពេក អ្នកនឹងមិនអានវាមុន trade ទេ។</div>
"""),
        ("ឧទាហរណ៍: Plan ដែលបំពេញរួច", """
<p>ខាងក្រោមជា<b>ឧទាហរណ៍សម្រាប់រៀន</b> (មិនមែនដំបូន្មាន) ដែលប្រើគំនិត 4H breakout ដូចបានរៀនក្នុង Chapter 28:</p>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>ច្បាប់</th></tr>
<tr><td>Market · TF</td><td>XAUUSD · bias 4H · entry ក្រោយទៀន 4H បិទ</td></tr>
<tr><td>ម៉ោង</td><td>ពិនិត្យរាល់ពេលទៀន 4H បិទ · មិនបើកថ្មីថ្ងៃសុក្រក្រោយ 22:00</td></tr>
<tr><td>Entry (ទិញ)</td><td>4H បិទលើ high 30 ទៀន · Day Meter ≥ 70% · trend ស្អាត · ទៀនបិទខ្លាំង</td></tr>
<tr><td>Entry (លក់)</td><td>ផ្ទុយគ្នា: 4H បិទក្រោម low 30 ទៀន + លក្ខខណ្ឌដដែល</td></tr>
<tr><td>Exit</td><td>SL ថេរ · TP1 1R (បិទពាក់កណ្ដាល · SL → entry) · TP2 3R · បិទក្រោយ 12h</td></tr>
<tr><td>No-trade</td><td>ព័ត៌មាន 🔴 ±15 នាទី · choppy · spread ធំ</td></tr>
<tr><td>Risk</td><td>1% / trade · ≤ 2 trade បើកក្នុងពេលតែមួយ · max daily 3%</td></tr>
<tr><td>Journal · Review</td><td>រូប chart ពេលចូល/ចេញ · ពិនិត្យរាល់ថ្ងៃសៅរ៍</td></tr></table>
<div class='box ok'>✅ សូមកត់សម្គាល់: គ្រប់ជួរ<b>វាស់បាន</b>។ អ្នកណាក៏អាចយក plan នេះទៅ backtest ហើយទទួលបាន trade ដូចគ្នា។ នោះហើយជាលក្ខណៈ strategy ពិត។</div>
<div class='box warn'>⚠️ Plan នេះ<b>មិនធានា</b>ចំណេញទេ។ លទ្ធផលអតីតកាលនៃគំនិតនេះមាននៅក្នុង studies/RESULTS.md ហើយ live record ពិតនៅ 📈 <b>Proof</b>។ អ្វីៗត្រូវសាកល្បងដោយខ្លួនឯង (Chapter 35 · 36)។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ មាន "strategy" ក្នុងក្បាល ប៉ុន្តែមិនដែលសរសេរ</li>
<li>❌ ច្បាប់ entry ច្បាស់ តែគ្មានច្បាប់ exit ឬ time exit</li>
<li>❌ ប្ដូរច្បាប់រាល់ពេលខាត 2–3 ដង (មុនមាន 30+ trade)</li>
<li>❌ ប្រើ indicator 6–7 ក្នុងពេលតែមួយ ដែលប្រាប់រឿងដដែល</li>
<li>❌ គ្មាន no-trade conditions ដូច្នេះ trade រាល់ថ្ងៃ</li>
<li>❌ ចម្លង strategy អ្នកដទៃ ដោយមិនយល់ និងមិនសាកល្បង</li>
<li>❌ ប្រើលុយពិតភ្លាម មុន backtest និង demo</li></ul>
"""),
    ],
    summary=["Strategy = ច្បាប់ច្បាស់ ដែលមនុស្ស 2 នាក់យក trade ដូចគ្នា",
             "Entry = context + setup + trigger · Exit = SL + TP + break-even + time exit",
             "Filters បិទ strategy ពេលវាខ្សោយ · ត្រូវជួយលើទិន្នន័យចាស់ និងថ្មី",
             "Invalidation និង no-trade conditions ត្រូវសរសេរមុនចូល",
             "Trading Plan = strategy + risk + ម៉ោង + journal + review (1 ទំព័រ)"],
    exercise=["យក idea មួយដែលអ្នកចូលចិត្ត ហើយសរសេរវាជាច្បាប់ entry 3–4 ជួរ ដែលឆ្លើយបានតែ បាទ/ទេ។",
              "សរសេរ exit ទាំង 4 ករណី (SL · TP1 · TP2 · time exit) សម្រាប់ Buy $4,100 ជាមួយ SL $12។ TP1 1R និង TP2 3R នៅតម្លៃប៉ុន្មាន?",
              "សរសេរ no-trade conditions យ៉ាងតិច 5 សម្រាប់ខ្លួនឯង។ ពិនិត្យ 📰 News ដើម្បីរកព័ត៌មាន 🔴 សប្ដាហ៍នេះ។",
              "បំពេញ Trading Plan template ទាំង 10 ផ្នែក (1 ទំព័រ) ហើយរក្សាទុក។ Chapter 35 នឹងប្រើវាសម្រាប់ backtest។"],
)
