from academy_pdf import zigzag, flow
from academy_book.ch11 import dealing_range

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def fib(w=420, h=250, caption=""):
    """Fibonacci retracement of an up-leg 4,000 -> 4,080: premium/discount halves, the OTE band and a retrace into it."""
    hi, lo = 4080.0, 4000.0
    top, bot, x0, x1 = 26, h - 26, 64, w - 74
    Y = lambda r: top + r * (bot - top)            # r = retracement ratio (0 = high, 1 = low)
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{Y(.5) - top:.1f}" fill="{DN}" fill-opacity=".07"/>',
           f'<rect x="{x0}" y="{Y(.5):.1f}" width="{x1 - x0}" height="{bot - Y(.5):.1f}" fill="{UP}" fill-opacity=".07"/>',
           f'<rect x="{x0}" y="{Y(.618):.1f}" width="{x1 - x0}" height="{Y(.79) - Y(.618):.1f}" fill="{GOLD}" fill-opacity=".28"/>']
    for r, col, dash in [(0, DN, False), (.5, GR, True), (.618, GOLD, True), (.705, GOLD, False), (.79, GOLD, True), (1, UP, False)]:
        price = hi - r * (hi - lo)
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(r):.1f}" y2="{Y(r):.1f}" stroke="{col}" stroke-width="1.3"'
                   + (' stroke-dasharray="5 4"' if dash else "") + "/>")
        out.append(f'<text x="{x0 - 6}" y="{Y(r) + 4:.1f}" text-anchor="end" fill="{col}" class="lt">{r:g}</text>')
        out.append(f'<text x="{x1 + 6}" y="{Y(r) + 4:.1f}" text-anchor="start" fill="{col}" class="lt">{price:,.2f}</text>')
    pts = [(x0 + 6, Y(1)), (x0 + 70, Y(.55)), (x0 + 100, Y(.7)), (x0 + 150, Y(0)), (x0 + 205, Y(.71)), (x1 - 4, Y(-.02))]
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{x:.0f},{y:.1f}" for i, (x, y) in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{x0 + 205}" cy="{Y(.71):.1f}" r="3.5" fill="{BL}"/>')
    out.append(f'<text x="{x0 + 40}" y="{Y(.2):.1f}" text-anchor="middle" fill="{DN}" class="bt">Premium</text>')
    out.append(f'<text x="{x0 + 110}" y="{Y(.9) + 4:.1f}" text-anchor="middle" fill="{UP}" class="bt">Discount</text>')
    out.append(f'<text x="{x0 + 150}" y="{Y(.705) + 4:.1f}" text-anchor="middle" fill="{BL}" class="pt">OTE</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=15, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="តំបន់ថ្លៃ និងតំបន់ថោក", title_en="Premium & Discount: Dealing Range · EQ · Fibonacci · OTE",
    intro="""ក្នុង Chapter 11 យើងបានស្គាល់ <span class='en-term'>dealing range</span> និងបន្ទាត់ <span class='en-term'>EQ 50%</span> ដោយសង្ខេប។
ជំពូកនេះពន្យល់លម្អិតថា ហេតុអ្វីបានជា ICT trader ចង់ <b>BUY នៅតំបន់ថោក (discount)</b> និង <b>SELL នៅតំបន់ថ្លៃ (premium)</b>,
របៀបគូរ range ឱ្យត្រូវ, របៀបប្រើ <span class='en-term'>Fibonacci</span> ដើម្បីរក <span class='en-term'>OTE</span> និងរបៀបភ្ជាប់វាជាមួយ
market structure, OB និង FVG ដែលអ្នកបានរៀនរួច។ គោលបំណងគឺ<b>ជៀសវាងការទិញថ្លៃ និងលក់ថោក</b> ដែលជាកំហុសញឹកញាប់បំផុតរបស់អ្នកចាប់ផ្ដើម។""",
    sections=[
        ("Dealing Range: ជ្រើស Range ណា?", """
<p><span class='en-term'>Dealing range</span> គឺជាចន្លោះរវាង <b>swing high</b> និង <b>swing low</b> សំខាន់ ដែលតម្លៃកំពុងដើរនៅក្នុង។
ការជ្រើស swing ខុស នឹងធ្វើឱ្យ premium/discount ទាំងអស់ខុសតាម។ ដូច្នេះច្បាប់សំខាន់គឺ: ប្រើ swing ដែល<b>បង្កើត BOS ចុងក្រោយ</b>។</p>
""" + zigzag([18, 48, 34, 62, 10, 40, 30, 85, 55, 66], {4: ("Swing Low", UP), 7: ("Swing High", DN), 3: ("high ចាស់", GR)},
             lines=[(62, 3, 6, "BOS ↑", OR, True), (85, 4, 9, "", DN, False), (10, 4, 9, "", UP, False), (47.5, 4, 9, "EQ 50%", GR, True)],
             caption="Uptrend: range = ពី swing low ដែលចាប់ផ្ដើម impulse ទៅ swing high ថ្មីដែលបង្កើត BOS") + """
<ul><li><b>Uptrend</b>: ពី swing low ដែលចាប់ផ្ដើម impulse → ទៅ swing high ថ្មីបំផុត</li>
<li><b>Downtrend</b>: ពី swing high ដែលចាប់ផ្ដើម impulse → ទៅ swing low ថ្មីបំផុត</li>
<li><b>Range (ចំហៀង)</b>: ពីកំពូល ទៅបាតនៃ range ដែលតម្លៃគោរពច្រើនដង</li>
<li>ពេលតម្លៃ<b>បិទទៀនហួស</b>ចុង range (BOS ថ្មី) → គូរ range ថ្មី</li></ul>
<div class='box tip'>💡 ក្នុងពេលតម្លៃកំពុងឡើងហួស high ចាស់ យើងមិនទាន់ដឹងថា high ថ្មីនៅឯណាទេ។ Range ត្រូវបានកំណត់ច្បាស់ តែពេល swing high ថ្មី<b>ត្រូវបានបញ្ជាក់</b> (Chapter 9)។</div>
"""),
        ("Equilibrium (EQ): ចំណុចតម្លៃ \"យុត្តិធម៌\"", """
<p><span class='en-term'>Equilibrium (EQ)</span> គឺជាចំណុច <b>50%</b> នៃ dealing range។ វាជាព្រំដែនរវាង "ថ្លៃ" និង "ថោក"។
នៅ EQ តម្លៃមិនថ្លៃ មិនថោក ដូច្នេះ RR សម្រាប់ទិញ ឬលក់នៅទីនោះ ច្រើនតែមិនល្អបំផុត។</p>
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>ឧទាហរណ៍</th></tr>
<tr><td>Swing High</td><td>4,080.00</td></tr>
<tr><td>Swing Low</td><td>4,000.00</td></tr>
<tr><td>ទំហំ range</td><td>$80 = <b>800 pips</b></td></tr>
<tr><td>EQ = (High + Low) ÷ 2</td><td>(4,080 + 4,000) ÷ 2 = <b>4,040.00</b></td></tr></table>
<ul><li>តម្លៃច្រើនតែ<b>ប្រតិកម្ម</b>ជុំវិញ EQ (ឈប់បន្តិច ឬ reject) ព្រោះ trader ជាច្រើនមើលកម្រិតនេះ</li>
<li>EQ ក៏ជា<b>គោលដៅដំបូង</b>ដ៏ពេញនិយមសម្រាប់ trade ដែលចូលនៅចុង range</li>
<li>គំនិតដូចគ្នានឹង <span class='en-term'>CE</span> នៃ FVG (Chapter 13) និង <span class='en-term'>Mean Threshold</span> នៃ OB (Chapter 14)</li></ul>
"""),
        ("Premium Zone: តំបន់ថ្លៃ", """
<p><span class='en-term'>Premium</span> គឺជាពាក់កណ្ដាល<b>លើ</b> EQ។ នៅទីនេះ តម្លៃ<b>ថ្លៃ</b>ធៀបនឹង range។ ICT trader រក <b>SELL</b> នៅ premium
ជាពិសេសពេល HTF កំពុងធ្លាក់។ ការ BUY នៅ premium មានន័យថា ទិញថ្លៃ: SL ឆ្ងាយ ហើយគោលដៅខាងលើនៅជិត។</p>
""" + dealing_range(caption="Dealing range 4,000 – 4,060 · EQ 4,030 · លើ = Premium · ក្រោម = Discount") + """
<div class='box warn'>⚠️ Premium <b>មិនមែន</b>មានន័យថា "តម្លៃនឹងធ្លាក់" ទេ។ ក្នុង uptrend ខ្លាំង តម្លៃអាចនៅ premium យូរ ហើយបន្តឡើង។
Premium គ្រាន់តែប្រាប់ថា "<b>កុំទិញនៅទីនេះ</b>" ច្រើនជាង "ត្រូវលក់នៅទីនេះ"។</div>
"""),
        ("Discount Zone: តំបន់ថោក", """
<p><span class='en-term'>Discount</span> គឺជាពាក់កណ្ដាល<b>ក្រោម</b> EQ។ នៅទីនេះ តម្លៃ<b>ថោក</b>ធៀបនឹង range។ ICT trader រក <b>BUY</b> នៅ discount
ជាពិសេសពេល HTF កំពុងឡើង។ ដូចការទិញទំនិញពេលបញ្ចុះតម្លៃ: ទិញថោក → SL ជិត (ក្រោម swing low) → គោលដៅ (high) ឆ្ងាយ។</p>
<table style='break-inside:avoid'><tr><th></th><th>BUY នៅ Discount (4,020)</th><th>BUY នៅ Premium (4,070)</th></tr>
<tr><td>SL (ក្រោម low 4,000)</td><td>4,000 − buffer → ~$22</td><td>~$72</td></tr>
<tr><td>Target (high 4,080)</td><td>+$60</td><td>+$10</td></tr>
<tr><td>RR ប្រហែល</td><td><b>1 : 2.7</b> ✅</td><td>1 : 0.14 ❌</td></tr></table>
<div class='box tip'>💡 លេខខាងលើបង្ហាញតែ <b>RR</b> (ទំហំចំណេញធៀបនឹងខាត) មិនមែនឱកាសឈ្នះទេ។ Discount ផ្ដល់ RR ល្អជាង ប៉ុន្តែតម្លៃអាចបន្តធ្លាក់ទម្លុះ low បាន
ជាពិសេសបើ HTF ធ្លាក់។ ហេតុនេះហើយបានជាយើងត្រូវមើល structure ជាមួយ (ផ្នែកទី 7)។</div>
"""),
        ("Fibonacci Retracement: ឧបករណ៍វាស់", """
<p><span class='en-term'>Fibonacci retracement</span> គឺជាឧបករណ៍គូរដែលមានក្នុង <b>MT5</b> (Insert → Objects → Fibonacci → Retracement)។
វាបែងចែក range ជាកម្រិតភាគរយ។ ICT ប្រើកម្រិតសំខាន់ៗ: <b>0.5</b> (EQ), <b>0.618</b>, <b>0.705</b>, <b>0.79</b>។</p>
""" + fib(caption="Up-leg 4,000 → 4,080 · តំបន់មាស = OTE 0.618–0.79 · តម្លៃ retrace ចូល OTE ហើយឡើងបន្ត") + """
<p>រូបមន្តសម្រាប់ uptrend: <b>កម្រិត = High − (High − Low) × ratio</b></p>
<table style='break-inside:avoid'><tr><th>Ratio</th><th>គណនា (range $80)</th><th>តម្លៃ</th></tr>
<tr><td>0.5 (EQ)</td><td>4,080 − 40.00</td><td>4,040.00</td></tr>
<tr><td>0.618</td><td>4,080 − 49.44</td><td>4,030.56</td></tr>
<tr><td>0.705</td><td>4,080 − 56.40</td><td>4,023.60</td></tr>
<tr><td>0.79</td><td>4,080 − 63.20</td><td>4,016.80</td></tr></table>
<div class='box tip'>💡 សម្រាប់ BUY: គូរពី <b>swing low ទៅ swing high</b>។ សម្រាប់ SELL: គូរពី <b>swing high ទៅ swing low</b>។ ក្នុង MT5 អ្នកអាចកែកម្រិត (Levels)
ដើម្បីបន្ថែម 0.705 និង 0.79។ ពេលមិនច្បាស់ថាកម្រិតណាជា 0 ណាជា 1 សូមផ្ទៀងផ្ទាត់ជាមួយរូបមន្តខាងលើ។</div>
"""),
        ("OTE: Optimal Trade Entry", """
<p><span class='en-term'>OTE (Optimal Trade Entry)</span> គឺជាតំបន់ <b>0.618 – 0.79</b> នៃ range ដែល ICT ចាត់ទុកថាជាកន្លែង entry ល្អ
សម្រាប់ pullback ក្នុងនិន្នាការ។ វាស្ថិតនៅជ្រៅក្នុង discount (សម្រាប់ BUY) ឬជ្រៅក្នុង premium (សម្រាប់ SELL)។ ICT ហៅ 0.705 ថាជា "sweet spot"។</p>
""" + flow([("Impulse", "BOS ក្នុងទិស HTF", BL), ("គូរ Fib", "low → high", GR), ("Retrace", "ចូល OTE", GOLD), ("Confluence", "OB / FVG / CHOCH", UP)],
           caption="OTE មានន័យបំផុត ពេលវាត្រួតជាមួយ OB ឬ FVG ហើយមានការបញ្ជាក់លើ LTF") + """
<ul><li>OTE <b>មិនមែន</b>ជាកម្រិតវេទមន្តទេ។ តម្លៃអាចឈប់នៅ 0.5 ហើយឡើងដោយមិនមកដល់ OTE ឬអាចទម្លុះ 0.79 ហើយធ្លាក់បន្ត</li>
<li>បើតម្លៃ<b>បិទទៀនហួស</b> swing low (ratio 1) នោះ range ចាស់<b>បរាជ័យ</b> · idea BUY លែងត្រឹមត្រូវ</li>
<li>OTE ដែលត្រួតនឹង <b>bullish OB</b> ឬ <b>FVG</b> (Chapter 13–14) ផ្ដល់ហេតុផលច្រើនជាង OTE តែឯង</li></ul>
"""),
        ("Premium / Discount + Market Structure", """
<p>Premium/discount ដោយខ្លួនឯងមិនប្រាប់ទិសទេ។ <b>Structure</b> (Chapter 9) ប្រាប់ទិស ហើយ premium/discount ប្រាប់<b>កន្លែង</b>:</p>
<table style='break-inside:avoid'><tr><th>Structure</th><th>រកអ្វី</th><th>កន្លែងណា</th></tr>
<tr><td>Uptrend (HH + HL)</td><td>BUY</td><td>Discount / OTE នៃ up-leg ចុងក្រោយ</td></tr>
<tr><td>Downtrend (LH + LL)</td><td>SELL</td><td>Premium / OTE នៃ down-leg ចុងក្រោយ</td></tr>
<tr><td>Range (ចំហៀង)</td><td>ទាំងពីរ</td><td>BUY បាត · SELL កំពូល · ជៀសវាងកណ្ដាល</td></tr>
<tr><td>CHOCH ថ្មី</td><td>រង់ចាំ</td><td>គូរ range ថ្មី រួចរង់ចាំ retrace</td></tr></table>
""" + zigzag([10, 50, 32, 75, 52, 98, 62, 90], {0: ("Low", UP), 3: ("BOS", OR), 5: ("High ថ្មី", DN), 6: ("Discount", UP)},
             lines=[(75, 4, 6, "EQ", GR, True), (52, 4, 7, "", UP, False)],
             caption="Uptrend: BOS → គូរ range ពី HL ទៅ high ថ្មី → រង់ចាំ retrace ចូល discount (ក្រោម EQ) → ឡើងបន្ត") + """
<div class='box ok'>✅ <b>ករណីលើកលែង</b>: ពេល <b>breakout</b> ពិត (ដូចសញ្ញា ⭐ របស់ XAU.KH) តម្លៃចាកចេញពី range ចាស់ ដូច្នេះ premium/discount នៃ range នោះសំខាន់តិច។
Breakout និង pullback គឺជារចនាបថពីរខុសគ្នា។ កុំលាយវាចូលគ្នា។</div>
"""),
        ("Timeframe ច្រើន: Premium លើ 4H, Discount លើ 15m?", """
<p>Range នីមួយៗមាន premium/discount ផ្ទាល់ខ្លួន។ តម្លៃអាចនៅ <b>discount លើ 15m</b> ប៉ុន្តែនៅ <b>premium លើ 4H</b>។ ពេលនោះ BUY លើ 15m
គឺកំពុងទិញនៅតំបន់ថ្លៃនៃរូបភាពធំ។</p>
<table style='break-inside:avoid'><tr><th>4H</th><th>15m</th><th>អត្ថន័យ</th></tr>
<tr><td>Discount + uptrend</td><td>Discount</td><td>✅ ស្របគ្នា · BUY មានហេតុផលច្រើន</td></tr>
<tr><td>Premium + downtrend</td><td>Premium</td><td>✅ ស្របគ្នា · SELL មានហេតុផលច្រើន</td></tr>
<tr><td>Premium</td><td>Discount</td><td>⚠️ BUY ខ្លីប៉ុណ្ណោះ · គោលដៅតូច ឬរំលង</td></tr>
<tr><td>ជិត EQ</td><td>ណាមួយ</td><td>⚠️ កណ្ដាល range · RR មិនច្បាស់</td></tr></table>
"""),
        ("ឧទាហរណ៍ជាលេខ: SELL ក្នុង Premium", """
<p>ស្ថានភាព: 4H downtrend (LH + LL)។ Down-leg ចុងក្រោយ ពី <b>4,080</b> (swing high) ទៅ <b>4,020</b> (swing low)។ Range = $60 = 600 pips។</p>
<p>រូបមន្តសម្រាប់ downtrend: <b>កម្រិត = Low + (High − Low) × ratio</b></p>
<table style='break-inside:avoid'><tr><th>កម្រិត</th><th>គណនា</th><th>តម្លៃ</th></tr>
<tr><td>EQ 0.5</td><td>4,020 + 30.00</td><td>4,050.00</td></tr>
<tr><td>OTE 0.618</td><td>4,020 + 37.08</td><td>4,057.08</td></tr>
<tr><td>OTE 0.705</td><td>4,020 + 42.30</td><td>4,062.30</td></tr>
<tr><td>OTE 0.79</td><td>4,020 + 47.40</td><td>4,067.40</td></tr></table>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>កម្រិត</th><th>ចម្ងាយ</th></tr>
<tr><td>Entry (0.705 + bearish FVG ត្រួតគ្នា)</td><td>4,062.30</td><td>–</td></tr>
<tr><td>Stop Loss (លើ swing high 4,080 + buffer)</td><td>4,082.00</td><td>$19.70 = 197 pips</td></tr>
<tr><td>Target (swing low / SSL)</td><td>4,020.00</td><td>$42.30 = 423 pips</td></tr></table>
<ul><li>នៅ <b>0.01 lot</b> (1 oz): ខាតប្រហែល <b>$19.70</b> ឬចំណេញប្រហែល <b>$42.30</b> (មិនរាប់ spread) · RR ≈ 1 : 2.1</li>
<li>SL នៅក្រោយ structure គឺធំ ដូច្នេះត្រូវ<b>កាត់បន្ថយ lot</b> ឱ្យខាតមិនលើស % ដែលអ្នកកំណត់ (Part Risk Management)</li></ul>
"""),
        ("កំហុសញឹកញាប់ និងការអនុវត្តក្នុង Group", """
<ul><li>❌ គូរ range ពី swing តូចៗ ដែលមិនបានបង្កើត BOS</li>
<li>❌ BUY ព្រោះ "ថោក" ក្នុង downtrend ខ្លាំង (discount អាចកាន់តែថោក)</li>
<li>❌ ភ្លេចគូរ range ថ្មី ក្រោយ BOS ហើយប្រើ EQ ចាស់</li>
<li>❌ ចាត់ទុក 0.618 / 0.705 / 0.79 ជាកម្រិតដែលតម្លៃ "ត្រូវតែ" ប្រតិកម្ម</li></ul>
<div class='box tip'>💡 ក្នុង group XAU.KH: រូប 📊 Analysis គូរប្រអប់ dealing range និងបន្ទាត់ <b>EQ 50%</b> ឱ្យរួចជាស្រេច។ មើលថាតម្លៃឥឡូវនៅលើ ឬក្រោម EQ
ហើយវាយ <b>/check</b> ដើម្បីមើល bias។ ពេល 🚨 Signal ចេញ សាកវិភាគថាវានៅ premium ឬ discount ឬជា breakout ⭐ ហើយមើលលទ្ធផលពិតនៅ 📈 Proof។ មុន 📰 News ធំ តម្លៃអាចរត់ឆ្លង range ទាំងមូល។</div>
"""),
    ],
    summary=["Dealing range = swing low ↔ swing high នៃ BOS ចុងក្រោយ",
             "EQ = (High + Low) ÷ 2 = 50% · លើ EQ = Premium (ថ្លៃ) · ក្រោម EQ = Discount (ថោក)",
             "Uptrend → BUY ក្នុង discount · Downtrend → SELL ក្នុង premium · ជៀសវាងកណ្ដាល range",
             "Fib: 0.5 = EQ · OTE = 0.618–0.79 · មិនមែនវេទមន្ត",
             "Structure ប្រាប់ទិស · Premium/Discount ប្រាប់កន្លែង · ចាប់ផ្ដើមពី HTF ជានិច្ច"],
    exercise=["គូរ dealing range 4H ពី swing ដែលបង្កើត BOS ចុងក្រោយ។ គណនា EQ និងទំហំ range (pips)។",
              "ប្រើ Fibonacci ក្នុង MT5 រក 0.618, 0.705, 0.79 ហើយផ្ទៀងផ្ទាត់ជាមួយរូបមន្ត។",
              "តើមាន OB ឬ FVG ត្រួតនឹង OTE ហើយស្រប structure 4H ឬអត់?",
              "ប្រៀបធៀប EQ របស់អ្នក ជាមួយ EQ 50% លើរូប 📊 Analysis ថ្ងៃនេះ។"],
)
