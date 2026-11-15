from academy_pdf import flow
from academy_book.ch12 import candles

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"

S = lambda v: round((v - 30) * 1.6, 1)   # stretch the sketch to use the full height
BULL = [tuple(S(v) for v in c) for c in
        [(40, 46, 36, 44), (44, 78, 42, 76), (76, 86, 58, 82), (82, 84, 66, 68), (68, 70, 52, 56), (56, 74, 50, 72), (72, 90, 70, 88)]]
BEAR = [(100 - o, 100 - lo, 100 - hi, 100 - c) for (o, hi, lo, c) in BULL]


def fill_types(w=420, h=170, caption=""):
    """Three panels: price taps the FVG edge, reaches CE (50%), or fills it completely."""
    pw = (w - 20) / 3
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    panels = [("ប៉ះគែម (tap)", 74), ("ដល់ CE 50%", 95), ("បំពេញពេញ (full)", 118)]
    for k, (title, low) in enumerate(panels):
        x = 10 + k * pw
        zt, zb = 70, 116
        out.append(f'<rect x="{x + 10:.0f}" y="{zt}" width="{pw - 20:.0f}" height="{zb - zt}" fill="{BL}" fill-opacity=".14" stroke="{BL}" stroke-dasharray="3 3"/>')
        out.append(f'<line x1="{x + 10:.0f}" x2="{x + pw - 10:.0f}" y1="{(zt + zb) / 2}" y2="{(zt + zb) / 2}" stroke="{GR}" stroke-dasharray="4 3"/>')
        path = f"M{x + 16:.0f},40 L{x + pw * .45:.0f},{low} L{x + pw - 18:.0f},30"
        out.append(f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
        out.append(f'<circle cx="{x + pw * .45:.0f}" cy="{low}" r="3.2" fill="{UP}"/>')
        out.append(f'<text x="{x + pw / 2:.0f}" y="{h - 16}" text-anchor="middle" fill="#1C1C1E" class="bt">{title}</text>')
    out.append(f'<text x="14" y="18" fill="{BL}" class="lt">Bullish FVG · បន្ទាត់ចំកណ្ដាល = CE</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=13, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="ចន្លោះតម្លៃមិនស្មើ (Fair Value Gap)", title_en="Fair Value Gaps: FVG · IFVG · CE · Displacement",
    intro="""ពេលមាសរត់លឿនខ្លាំង វាច្រើនតែបន្សល់ទុក<b>ចន្លោះ</b>មួយនៅលើ chart ដែលតម្លៃស្ទើរតែមិនបាន trade ពីរទិស។
ICT ហៅចន្លោះនេះថា <span class='en-term'>Fair Value Gap (FVG)</span>។ វាជាឧបករណ៍ដែលអ្នកនឹងឃើញញឹកញាប់បំផុតលើរូប 📊 Analysis របស់ XAU.KH
ហើយក៏ជាកន្លែងដែល trader ច្រើនរង់ចាំ entry ក្រោយ sweep និង CHOCH (Chapter 12)។ ក្នុងជំពូកនេះ អ្នកនឹងរៀនរក FVG ឱ្យត្រូវ
វាស់ CE ប្រើ IFVG និងសំខាន់បំផុត <b>បែងចែក FVG ល្អ ពី FVG ខ្សោយ</b>។""",
    sections=[
        ("FVG គឺជាអ្វី? ច្បាប់ទៀន 3 គ្រាប់", """
<p><span class='en-term'>FVG</span> ត្រូវបានរកដោយមើល<b>ទៀន 3 គ្រាប់ជាប់គ្នា</b>។ ទៀនទី 2 គឺជាទៀនធំ (displacement)។
បើ <b>wick នៃទៀនទី 1</b> និង <b>wick នៃទៀនទី 3</b> មិនត្រួតគ្នា ចន្លោះរវាងពួកវាគឺជា FVG។</p>
""" + candles(BULL, zones=[(S(58), S(46), 0, 6, BL, "Bullish FVG · ខ្សែដាច់ៗ = CE 50%", "below")], lines=[(S(52), 0, 6, "", GR, True)],
              notes={0: ("1", GR, "bottom"), 1: ("2", GR, "bottom"), 2: ("3", GR, "top")},
              caption="High ទៀន 1 = 4,040 · Low ទៀន 3 = 4,046 → FVG 4,040–4,046 · តម្លៃថយមកប៉ះ CE រួចឡើង") + """
<ul><li>Bullish FVG: ចន្លោះរវាង <b>High ទៀន 1</b> និង <b>Low ទៀន 3</b></li>
<li>Bearish FVG: ចន្លោះរវាង <b>Low ទៀន 1</b> និង <b>High ទៀន 3</b></li>
<li>យើងប្រើ <b>wick</b> (high/low) មិនមែន body ទេ</li></ul>
<div class='box tip'>💡 ហេតុអ្វីហៅថា "Fair Value Gap"? ក្នុងចន្លោះនោះ មានតែភាគីម្ខាងប៉ុណ្ណោះដែល trade (អ្នកទិញរុញឡើងលឿនពេក)។ គំនិត ICT គឺថា
តម្លៃច្រើនតែ<b>ត្រឡប់មកវិញ</b>ដើម្បី "ធ្វើឱ្យស្មើ" មុនបន្តទៅមុខ។ "ច្រើនតែ" មិនមែន "ជានិច្ច" ទេ។</div>
"""),
        ("Bullish FVG និង Bearish FVG", """
<p><span class='en-term'>Bullish FVG</span> កើតពីចលនា<b>ឡើង</b>លឿន ហើយនៅ<b>ក្រោម</b>តម្លៃ។ វាអាចដើរតួជា <b>support</b> ពេលតម្លៃថយចុះមកវិញ។
<span class='en-term'>Bearish FVG</span> កើតពីចលនា<b>ធ្លាក់</b>លឿន ហើយនៅ<b>លើ</b>តម្លៃ។ វាអាចដើរតួជា <b>resistance</b> ពេលតម្លៃឡើងទៅវិញ។</p>
""" + candles(BEAR, zones=[(100 - S(46), 100 - S(58), 0, 6, DN, "Bearish FVG · ខ្សែដាច់ៗ = CE 50%", "above")], lines=[(100 - S(52), 0, 6, "", GR, True)],
              notes={0: ("1", GR, "top"), 1: ("2", GR, "top"), 2: ("3", GR, "bottom")},
              caption="Bearish FVG: Low ទៀន 1 និង High ទៀន 3 មិនត្រួតគ្នា · តម្លៃឡើងប៉ះ ហើយធ្លាក់បន្ត") + """
<table style='break-inside:avoid'><tr><th></th><th>Bullish FVG</th><th>Bearish FVG</th></tr>
<tr><td>កើតពី</td><td>Displacement ឡើង</td><td>Displacement ធ្លាក់</td></tr>
<tr><td>ទីតាំង</td><td>ក្រោមតម្លៃ</td><td>លើតម្លៃ</td></tr>
<tr><td>តួនាទី</td><td>Support · តំបន់រក BUY</td><td>Resistance · តំបន់រក SELL</td></tr>
<tr><td>គែមសំខាន់</td><td>High ទៀន 1 (បាត FVG)</td><td>Low ទៀន 1 (កំពូល FVG)</td></tr></table>
"""),
        ("Displacement: ម្ដាយនៃ FVG", """
<p><span class='en-term'>Displacement</span> (Chapter 9) គឺជាទៀនធំ និងលឿន ដែលបង្ហាញថាមានការទិញ ឬលក់<b>ខ្លាំង</b>។ FVG ល្អ ស្ទើរតែគ្រប់ពេល
កើតពី displacement។ FVG តូចៗ ដែលកើតពីទៀនធម្មតា មានន័យតិចជាង។</p>
""" + flow([("Sweep", "យក liquidity", OR), ("Displacement", "ទៀនធំ លឿន", BL), ("FVG", "ចន្លោះនៅសល់", GOLD), ("Retrace", "ត្រឡប់មកប៉ះ", UP)],
           caption="FVG ដែលមានន័យបំផុត កើតក្រោយ sweep និងជាផ្នែកនៃ displacement ដែលបំបែក structure") + """
<ul><li>វិធីពិនិត្យ displacement: ទៀនទី 2 មាន body <b>ធំជាង</b>ទៀនធម្មតាជុំវិញច្បាស់ (ឧ. ធំជាង ATR) ហើយ wick តូច</li>
<li>Displacement ដែល<b>បំបែក structure</b> (BOS / CHOCH) ធ្វើឱ្យ FVG នោះគួរឱ្យទុកចិត្តជាង</li>
<li>ពេលព័ត៌មានធំ (CPI, NFP) មាសអាចបង្កើត FVG ធំណាស់ ក្នុងរយៈពេលពីរបីវិនាទី · spread ក៏ធំដែរ</li></ul>
<div class='box warn'>⚠️ FVG ដែលកើតពី spike ព័ត៌មាន មិនតែងតែមានន័យដូច FVG ធម្មតាទេ។ ព្រោះ liquidity ស្ដើង តម្លៃអាចឆ្លងកាត់វាវិញយ៉ាងលឿន។ មើល 📰 News ជាមុនជានិច្ច។</div>
"""),
        ("Consequent Encroachment (CE): ចំណុច 50%", """
<p><span class='en-term'>Consequent Encroachment (CE)</span> គឺជាចំណុច<b>ពាក់កណ្ដាល</b>នៃ FVG។ ICT trader ច្រើនមើលថាតម្លៃគោរព CE ឬអត់:
តម្លៃដែលប៉ះ CE ហើយបដិសេធ (reject) បង្ហាញថា FVG នៅតែការពារបាន។</p>
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>ឧទាហរណ៍ Bullish FVG</th></tr>
<tr><td>បាត FVG (High ទៀន 1)</td><td>4,040.00</td></tr>
<tr><td>កំពូល FVG (Low ទៀន 3)</td><td>4,046.00</td></tr>
<tr><td>ទំហំ FVG</td><td>$6.00 = <b>60 pips</b></td></tr>
<tr><td>CE = (កំពូល + បាត) ÷ 2</td><td>(4,046 + 4,040) ÷ 2 = <b>4,043.00</b></td></tr></table>
<ul><li>Bullish FVG: ការ<b>បិទទៀន</b>ក្រោម CE ច្រើនដង = សញ្ញាថា FVG កំពុងខ្សោយ</li>
<li>Bearish FVG: ការ<b>បិទទៀន</b>លើ CE ច្រើនដង = សញ្ញាថា FVG កំពុងខ្សោយ</li>
<li>Trader ខ្លះដាក់ limit order នៅគែម FVG ខ្លះនៅ CE · CE ផ្ដល់តម្លៃល្អជាង ប៉ុន្តែពេលខ្លះតម្លៃមិនមកដល់</li></ul>
<div class='box tip'>💡 CE ប្រើគំនិតដូច <b>EQ 50%</b> នៃ dealing range (Chapter 11) ដែរ ប៉ុន្តែអនុវត្តលើប្រអប់ FVG តូចមួយ។</div>
"""),
        ("FVG Mitigation: ពេលតម្លៃត្រឡប់មកបំពេញ", """
<p><span class='en-term'>Mitigation</span> (ឬ <span class='en-term'>fill</span>) គឺពេលតម្លៃត្រឡប់មកក្នុង FVG។ មាន 3 កម្រិត:</p>
""" + fill_types(caption="តម្លៃអាចប៉ះគែម ដល់ CE ឬបំពេញ FVG ទាំងស្រុង មុនពេលបន្តទិសដើម") + """
<table style='break-inside:avoid'><tr><th>កម្រិត</th><th>អត្ថន័យ</th><th>ស្ថានភាព FVG</th></tr>
<tr><td>Tap (ប៉ះគែម)</td><td>Wick ចូលបន្តិចហើយត្រឡប់</td><td>ខ្លាំង · ការទិញ/លក់នៅតែរង់ចាំ</td></tr>
<tr><td>CE</td><td>ចូលដល់ពាក់កណ្ដាល ហើយ reject</td><td>ធម្មតា · គោរព CE</td></tr>
<tr><td>Full fill</td><td>ចូលដល់គែមម្ខាងទៀត</td><td>ប្រើអស់ · ខ្សោយសម្រាប់លើកក្រោយ</td></tr>
<tr><td>បិទហួស</td><td>ទៀនបិទឆ្លងកាត់ FVG ទាំងមូល</td><td>បរាជ័យ · អាចក្លាយជា IFVG</td></tr></table>
<div class='box warn'>⚠️ FVG ដែលត្រូវ mitigate រួច (ប៉ះ ហើយប្រើរួច) មានកម្លាំងតិចជាង FVG ថ្មី។ ការរង់ចាំ entry នៅ FVG ដដែលជាលើកទី 3 ទី 4 ច្រើនតែមិនល្អ។</div>
"""),
        ("Inversion FVG (IFVG): FVG ដែលប្ដូរតួនាទី", """
<p>ពេលតម្លៃ<b>បិទទៀនឆ្លងកាត់</b> FVG ទាំងស្រុង FVG នោះ<b>បរាជ័យ</b>។ ICT ហៅវាថា <span class='en-term'>Inversion FVG (IFVG)</span>:
Bullish FVG ដែលបែកចុះ អាចក្លាយជា <b>resistance</b> · Bearish FVG ដែលបែកឡើង អាចក្លាយជា <b>support</b>។ គំនិតនេះស្រដៀងនឹង
support ក្លាយជា resistance ក្នុង Chapter 7 ដែរ។</p>
""" + candles([(30, 36, 28, 34), (34, 64, 32, 62), (62, 70, 50, 66), (66, 68, 54, 56), (56, 58, 30, 32), (32, 34, 18, 22), (22, 44, 20, 42), (42, 47, 30, 32), (32, 34, 12, 15)],
              zones=[(50, 36, 0, 3, UP, ""), (50, 36, 4, 8, DN, "IFVG")],
              notes={1: ("Bullish FVG", UP, "top"), 4: ("បិទក្រោម", DN, "bottom"), 7: ("Reject", DN, "top")},
              caption="Bullish FVG (បៃតង) ត្រូវបិទទៀនឆ្លងចុះ → ក្លាយជា IFVG (ក្រហម) → តម្លៃឡើងប៉ះ ហើយធ្លាក់បន្ត") + """
<ul><li>IFVG ត្រូវការ<b>ការបិទទៀន</b>ឆ្លងកាត់ FVG មិនមែនត្រឹមតែ wick ទេ</li>
<li>IFVG ដែលកើតជាមួយ <b>CHOCH</b> ជាសញ្ញាថា ទិសខ្លីអាចកំពុងផ្លាស់ប្ដូរ</li>
<li>ដូច FVG ដែរ IFVG ដំណើរការល្អជាងនៅពេលវាស្របនឹង HTF bias</li></ul>
"""),
        ("FVG ល្អ ទល់នឹង FVG ខ្សោយ", """
<p>Chart មាស 5m មួយថ្ងៃអាចមាន FVG <b>រាប់សិប</b>។ ភាគច្រើនគ្មានន័យទេ។ ប្រើតារាងនេះជាតម្រង (filter):</p>
<table style='break-inside:avoid'><tr><th>កត្តា</th><th>✅ FVG ល្អ</th><th>❌ FVG ខ្សោយ</th></tr>
<tr><td>ប្រភព</td><td>Displacement ក្រោយ sweep</td><td>ទៀនធម្មតា គ្មាន sweep</td></tr>
<tr><td>Structure</td><td>បានបំបែក BOS / CHOCH</td><td>មិនបំបែកអ្វីទាំងអស់</td></tr>
<tr><td>ទិសដៅ HTF</td><td>ស្របនឹង 4H / 1H bias</td><td>ផ្ទុយ HTF</td></tr>
<tr><td>ទីតាំង</td><td>Bullish ក្នុង discount · Bearish ក្នុង premium</td><td>នៅកណ្ដាល range (ជិត EQ)</td></tr>
<tr><td>ទំហំ</td><td>ច្បាស់ ប្រៀបនឹង ATR</td><td>តូចពេក (ពីរបី pips) ឬធំពេកពី spike ព័ត៌មាន</td></tr>
<tr><td>ស្ថានភាព</td><td>ថ្មី មិនទាន់ប៉ះ</td><td>Mitigate រួច ឬប៉ះច្រើនដង</td></tr>
<tr><td>គោលដៅ</td><td>មាន liquidity (ERL) ច្បាស់នៅខាងមុខ</td><td>គ្មានគោលដៅច្បាស់</td></tr></table>
<div class='box ok'>✅ កាន់តែស្រប (tick ✅ ច្រើន) FVG កាន់តែមានគុណភាព។ FVG ដែលមាន ✅ តែមួយពីរ ល្អបំផុតគឺ<b>រំលង</b>។</div>
"""),
        ("ប្រើ FVG ក្នុងផែនការ Trade", """
<p>FVG <b>មិនមែនជា</b>ហេតុផលតែមួយសម្រាប់ចូល trade ទេ។ វាគឺជា<b>កន្លែង</b>ដែលយើងរង់ចាំ entry ក្រោយពេល context ត្រឹមត្រូវ:</p>
""" + flow([("HTF Bias", "4H / 1H", BL), ("CHOCH", "sweep ហើយ CHOCH", OR), ("Retrace", "ចូល FVG / CE", GOLD), ("SL / TP", "SL ក្រោយ FVG", UP)],
           caption="FVG ជាជំហានទី 3 មិនមែនជំហានទី 1") + """
<p>ឧទាហរណ៍ (BUY) ជាមួយ FVG 4,040–4,046 ខាងលើ:</p>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>កម្រិត</th><th>ចម្ងាយ</th></tr>
<tr><td>Entry (CE)</td><td>4,043.00</td><td>–</td></tr>
<tr><td>Stop Loss (ក្រោមបាត FVG + buffer)</td><td>4,038.50</td><td>$4.50 = 45 pips</td></tr>
<tr><td>Target (BSL / ERL ខាងលើ)</td><td>4,058.00</td><td>$15 = 150 pips</td></tr></table>
<ul><li>នៅ <b>0.01 lot</b> (1 oz): បើ SL ប៉ះ ខាតប្រហែល <b>$4.50</b> · បើដល់ target ចំណេញប្រហែល <b>$15</b> (មិនរាប់ spread)</li>
<li>RR ≈ 1 : 3.3 · ប៉ុន្តែ RR ល្អ <b>មិនធានា</b>ថា trade នឹងឈ្នះទេ</li>
<li>បើតម្លៃ<b>បិទទៀនក្រោម</b>បាត FVG មុនពេលចូល → idea លែងត្រឹមត្រូវ · លុប limit order</li></ul>
<div class='box warn'>⚠️ ដូចដែល Chapter 11 បានប្រាប់: XAU.KH បានសាកល្បងលើមាស ហើយឃើញថា entry លើប្រអប់ ICT <b>តែឯង</b> ជាមួយ SL តូចពេក មិនបានផ្ដល់លទ្ធផលល្អ។
ប្រើ FVG ជាមួយ HTF bias, liquidity និង structure ជានិច្ច ហើយរក្សា risk តូចក្នុងមួយ trade។</div>
"""),
        ("កំហុសញឹកញាប់ និងការអនុវត្តក្នុង Group", """
<ul><li>❌ គូររាល់ FVG ទាំងអស់ រហូតដល់ chart ពេញដោយប្រអប់</li>
<li>❌ ប្រើ body ជំនួស wick ពេលវាស់ FVG</li>
<li>❌ BUY នៅ bullish FVG ខណៈ 4H កំពុងធ្លាក់ខ្លាំង ហើយតម្លៃនៅ premium</li>
<li>❌ ដាក់ SL ចំគែម FVG ដោយគ្មាន buffer (spread មាសអាចប៉ះវា)</li>
<li>❌ ភ្លេចថា FVG ដែលត្រូវបិទទៀនឆ្លងកាត់ លែងជា support/resistance ដើមទៀតហើយ (អាចជា IFVG)</li></ul>
<div class='box tip'>💡 ក្នុង group XAU.KH: រូប 📊 Analysis គូរ FVG ជា<b>ប្រអប់ពណ៌</b>។ សញ្ញា SCALP ក្នុង 🚨 Signals ប្រើ FVG លើ <b>15m</b> ជាតំបន់ entry។
សាកមើលថា signal នីមួយៗស្ថិតនៅ FVG ណា ហើយផ្ទៀងផ្ទាត់លទ្ធផល (ទាំងឈ្នះ ទាំងខាត) នៅ 📈 Proof។ វាយ <b>/check</b> ដើម្បីមើល bias មុនពេលពិចារណា FVG ណាមួយ។</div>
"""),
    ],
    summary=["FVG = ចន្លោះរវាង wick ទៀន 1 និងទៀន 3 ក្នុងចលនាលឿន (ទៀន 3 គ្រាប់)",
             "Bullish FVG នៅក្រោមតម្លៃ (support) · Bearish FVG នៅលើតម្លៃ (resistance)",
             "CE = 50% នៃ FVG · Mitigation = ប៉ះគែម / CE / បំពេញពេញ",
             "FVG ដែលត្រូវបិទទៀនឆ្លងកាត់ អាចក្លាយជា IFVG ទិសផ្ទុយ",
             "FVG ល្អ = displacement + sweep + BOS/CHOCH + ស្រប HTF + នៅ discount/premium ត្រឹមត្រូវ"],
    exercise=["នៅលើ chart មាស 15m រក bullish FVG 2 និង bearish FVG 2 ក្នុង 3 ថ្ងៃចុងក្រោយ។ វាស់ទំហំជា pips និងគណនា CE។",
              "សម្រាប់ FVG នីមួយៗ: តម្លៃត្រឡប់មកប៉ះគែម ដល់ CE ឬបំពេញពេញ? ឬវាក្លាយជា IFVG?",
              "ប្រើតារាង \"FVG ល្អ ទល់នឹង FVG ខ្សោយ\" ដើម្បីដាក់ពិន្ទុ FVG ទាំង 4។ មួយណាមានពិន្ទុខ្ពស់បំផុត?",
              "ប្រៀបធៀបជាមួយប្រអប់ FVG លើរូប 📊 Analysis ថ្ងៃនេះ។"],
)
