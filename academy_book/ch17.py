from academy_pdf import zigzag, flow
from academy_book.ch12 import candles

UP, DN, BL, OR, GR, GOLD, PU, SI = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE", "#636366"


def po3(w=420, h=210, caption=""):
    """Power of Three: a bullish daily candle on the left (open, manipulation wick, distribution, close)
    and the intraday path that builds it on the right."""
    top, bot = 22, h - 30
    Y = lambda v: bot - v * (bot - top) / 100
    o, lo, hi, c = 40, 18, 92, 84
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    cx = 70
    out.append(f'<line x1="{cx}" x2="{cx}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{UP}" stroke-width="2"/>')
    out.append(f'<rect x="{cx - 18}" y="{Y(c):.1f}" width="36" height="{Y(o) - Y(c):.1f}" rx="3" fill="{UP}"/>')
    for v, t, col in [(o, "Open", GR), (lo, "Low", DN), (c, "Close", UP)]:
        out.append(f'<line x1="{cx + 22}" x2="{w - 16}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{col}" stroke-width="1" stroke-dasharray="4 4"/>')
        out.append(f'<text x="{cx - 24}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    pts = [(150, o), (175, 46), (200, 34), (225, 44), (245, 38), (270, lo), (292, 46), (318, 60), (340, 56), (368, 86), (385, 80), (402, c)]
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{x},{Y(v):.1f}" for i, (x, v) in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    for x0, x1, t, col in [(150, 250, "A", GOLD), (250, 300, "M", OR), (300, 402, "D", UP)]:
        out.append(f'<rect x="{x0}" y="{h - 24}" width="{x1 - x0 - 2}" height="16" rx="4" fill="{col}" fill-opacity=".85"/>')
        out.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{h - 12}" text-anchor="middle" fill="white" class="lt">{t}</text>')
    out.append(f'<text x="200" y="{Y(58):.1f}" text-anchor="middle" fill="{GOLD}" class="st">Asia: range</text>')
    out.append(f'<text x="272" y="{Y(lo) + 16:.1f}" text-anchor="middle" fill="{OR}" class="st">sweep ក្រោម open</text>')
    out.append(f'<text x="350" y="{Y(94):.1f}" text-anchor="middle" fill="{UP}" class="st">NY: ចលនាពិត</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def smt(w=420, h=230, caption=""):
    """Bullish SMT: gold makes a lower low, silver makes a higher low at the same time."""
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']

    def panel(vals, y0, y1, name, col, low_txt, low_col):
        n = len(vals)
        X = lambda i: 30 + i * (w - 60) / (n - 1)
        Y = lambda v: y1 - v * (y1 - y0) / 100
        out.append(f'<text x="14" y="{y0 + 2}" fill="{col}" class="bt">{name}</text>')
        out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
                   + f'" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>')
        a, b = 2, 4
        out.append(f'<line x1="{X(a):.1f}" y1="{Y(vals[a]):.1f}" x2="{X(b):.1f}" y2="{Y(vals[b]):.1f}" stroke="{low_col}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        for i in (a, b):
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(vals[i]):.1f}" r="3.2" fill="{low_col}"/>')
        out.append(f'<text x="{X(b):.1f}" y="{Y(vals[b]) + 16:.1f}" text-anchor="middle" fill="{low_col}" class="lt">{low_txt}</text>')

    panel([80, 55, 30, 60, 12, 50, 85], 20, 100, "XAU (មាស)", "#1C1C1E", "Lower Low", DN)
    panel([80, 52, 22, 62, 38, 70, 90], 130, 205, "XAG (ប្រាក់)", SI, "Higher Low", UP)
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=17, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="គំនិត ICT កម្រិតខ្ពស់", title_en="Advanced ICT: PO3 · AMD · SMT · OTE · Turtle Soup",
    intro="""ជំពូកនេះបញ្ចប់ PART 3 (ICT)។ យើងនឹងរៀនគំនិតកម្រិតខ្ពស់ដែល ICT trader និយាយញឹកញាប់: <span class='en-term'>Power of Three (PO3)</span>,
<span class='en-term'>AMD</span> (Accumulation · Manipulation · Distribution), <span class='en-term'>SMT divergence</span>,
<span class='en-term'>OTE</span>, <span class='en-term'>Turtle Soup</span> និង <span class='en-term'>liquidity engineering</span>។
គំនិតទាំងនេះមិនមែនថ្មីទាំងស្រុងទេ: វាជាការ<b>ភ្ជាប់</b> structure, liquidity, FVG/OB, premium/discount និង<b>ពេលវេលា</b> (Chapter 9–16) ចូលគ្នា។
ផ្នែកចុងក្រោយបង្រៀនរបៀបប្រើវាដោយ<b>មិនធ្វើឱ្យ chart រញ៉េរញ៉ៃ</b> និងបង្ហាញលទ្ធផលសាកល្បងពិតរបស់ XAU.KH ដោយស្មោះត្រង់។""",
    sections=[
        ("Power of Three (PO3): ទៀនមួយ មានបីដំណាក់កាល", """
<p>ICT មើលទៀន<b>ថ្ងៃ (Daily)</b> មួយ ថាត្រូវបានបង្កើតឡើងជា <b>3 ដំណាក់កាល</b>។ សម្រាប់ថ្ងៃឡើង (bullish):</p>
<ul><li><b>Open</b> → តម្លៃដើរចំហៀងជិត open (<b>A</b>ccumulation)</li>
<li>តម្លៃធ្លាក់<b>ក្រោម open</b> ដើម្បី sweep sell stops ហើយបង្កើត <b>wick ខាងក្រោម</b> (<b>M</b>anipulation)</li>
<li>តម្លៃឡើងខ្លាំង ហើយបិទជិត high (<b>D</b>istribution)</li></ul>
""" + po3(caption="ឆ្វេង: ទៀនថ្ងៃឡើង · ស្ដាំ: ផ្លូវតម្លៃក្នុងថ្ងៃដែលបង្កើតវា · A → M → D") + """
<p>ថ្ងៃធ្លាក់ (bearish PO3) គឺផ្ទុយ: តម្លៃឡើង<b>លើ open</b> ជាមុន (wick ខាងលើ) រួចធ្លាក់ ហើយបិទជិត low។
គំនិតសំខាន់: <b>ក្នុងថ្ងៃឡើង ទិញក្រោម open ប្រសើរជាងទិញលើ open</b> ព្រោះ wick ខាងក្រោមជាកន្លែង "ថោក" នៃថ្ងៃ។</p>
<div class='box tip'>💡 PO3 ប្រើបានលើ timeframe ច្រើន: ទៀនសប្ដាហ៍ (ច័ន្ទ–អង្គារ = manipulation ញឹកញាប់តាម ICT), ទៀនថ្ងៃ ឬទៀន 4H។ ប៉ុន្តែអ្នក<b>មិនដឹងជាមុន</b>ថាទៀនថ្ងៃនេះនឹងឡើងឬធ្លាក់ទេ។
PO3 មានប្រយោជន៍តែពេលអ្នកមាន <b>daily bias</b> (Chapter 16) រួចហើយ។</div>
"""),
        ("AMD តាម Session: Asia → London → New York", """
<p>ក្នុងទម្រង់ដែល ICT បង្រៀនញឹកញាប់ AMD ត្រូវនឹង session ក្នុងម៉ោងកម្ពុជា (winter):</p>
<table style='break-inside:avoid'><tr><th>ដំណាក់កាល</th><th>Session</th><th>អ្វីដែលកើតឡើង</th></tr>
<tr><td><b>A</b>ccumulation</td><td>🌏 Asia 06:00–14:00</td><td>Range តូច · liquidity កកកុញនៅ Asia high/low</td></tr>
<tr><td><b>M</b>anipulation</td><td>🇬🇧 London KZ 14:00–17:00</td><td>Judas swing · sweep Asia high ឬ low</td></tr>
<tr><td><b>D</b>istribution</td><td>🇬🇧→🇺🇸 London–NY 17:00–22:00</td><td>ចលនាពិត ទៅរក draw on liquidity (PDH/PDL)</td></tr></table>
""" + zigzag([50, 56, 46, 55, 47, 54, 30, 44, 38, 62, 56, 84, 76, 94],
             {1: ("A", GOLD), 6: ("M", OR), 9: ("D", UP), 13: ("PDH", DN)},
             lines=[(56, 0, 5, "", GOLD, True), (46, 0, 8, "Asia Low", GOLD, True), (94, 9, 13, "", DN, True)],
             caption="Bullish AMD: Asia range → London sweep Asia low (M) → MSS ឡើង → NY ទៅយក PDH (D)") + """
<div class='box warn'>⚠️ ថ្ងៃជាច្រើនមិនដើរតាមលំនាំនេះទេ: ពេលខ្លះ manipulation កើតនៅ NY, ពេលខ្លះ Asia ខ្លួនឯងរត់ខ្លាំង, ពេលខ្លះគ្មាន sweep ទាល់តែសោះ។
ចងចាំការសាកល្បង XAU.KH ក្នុង Chapter 16: ការ trade ផ្ទុយ sweep ព្រឹក Asia ដោយគ្មានការបញ្ជាក់ <b>ខាត</b>។ AMD គឺជាផែនទីសម្រាប់<b>រង់ចាំ</b> មិនមែនច្បាប់ចូល trade ទេ។</div>
"""),
        ("SMT Divergence: ការខ្វែងគ្នារវាងទីផ្សារបងប្អូន", """
<p><span class='en-term'>SMT divergence</span> (Smart Money Technique) កើតឡើងនៅពេលទីផ្សារពីរដែលជាធម្មតាដើរ<b>ជាមួយគ្នា</b> ធ្វើ swing មិនដូចគ្នា។
សម្រាប់មាស ទីផ្សារបងប្អូនដែលពេញនិយម គឺ <b>ប្រាក់ (XAGUSD)</b>។ ឧទាហរណ៍ bullish SMT:</p>
""" + smt(caption="មាសធ្វើ Lower Low (sweep SSL) ប៉ុន្តែប្រាក់ធ្វើ Higher Low → ការធ្លាក់របស់មាសខ្សោយ → សញ្ញាឡើងអាចកើត") + """
<ul><li><b>Bullish SMT</b>: មាសធ្វើ low ថ្មី ប៉ុន្តែប្រាក់<b>មិនធ្វើ</b> → អ្នកលក់មិនខ្លាំងពិត</li>
<li><b>Bearish SMT</b>: មាសធ្វើ high ថ្មី ប៉ុន្តែប្រាក់<b>មិនធ្វើ</b> → អ្នកទិញមិនខ្លាំងពិត</li>
<li>អាចប្រៀបធៀបជាមួយ <b>Dollar Index (DXY)</b> ក៏បាន ប៉ុន្តែត្រូវ<b>បញ្ច្រាស</b>: មាស low ថ្មី ខណៈ DXY <b>មិន</b>ធ្វើ high ថ្មី</li></ul>
<div class='box tip'>💡 ក្នុង <b>MT5</b> បើក chart XAUUSD និង XAGUSD ចំហៀងគ្នា (Window → Tile) ក្នុង timeframe ដូចគ្នា។ Broker ខ្លះមិនមាន DXY ទេ: ពេលនោះប្រើប្រាក់ជាការប្រៀបធៀបចម្បង។</div>
<div class='box warn'>⚠️ ទំនាក់ទំនងរវាងមាស ប្រាក់ និងដុល្លារ <b>មិនថេរ</b>ទេ (Chapter 2)។ ពេលខ្លះប្រាក់ដើរតាមរឿងរបស់ខ្លួន (ឧ. ឧស្សាហកម្ម)។
SMT គឺជា<b>ភស្តុតាងបន្ថែម</b> នៅកន្លែង liquidity សំខាន់ មិនមែនសញ្ញាចូល trade ដោយខ្លួនឯងទេ។</div>
"""),
        ("OTE: Optimal Trade Entry ក្នុងការអនុវត្ត", """
<p>យើងបានរៀន OTE (0.62–0.79) ក្នុង Chapter 15។ នៅទីនេះ យើងភ្ជាប់វាជាមួយលំដាប់ ICT ពេញលេញ: <b>sweep → displacement → retrace ចូល OTE</b>។
គូរ Fibonacci លើ <b>leg ដែលបង្កើត MSS</b> (ពីចំណុច sweep ទៅ high ថ្មី)។</p>
""" + zigzag([60, 40, 52, 20, 48, 42, 80, 62, 66, 52, 76, 96],
             {3: ("Sweep", OR), 6: ("High ថ្មី", DN), 9: ("OTE", BL), 11: ("Target", UP)},
             lines=[(48, 3, 7, "MSS ↑", UP, False), (56.6, 6, 11, "0.705", GOLD, True), (20, 3, 11, "SL ក្រោម 1.0", DN, True)],
             caption="Leg ពី sweep ទៅ high ថ្មី → retrace ចូល OTE (0.62–0.79) → SL ក្រោម sweep → គោលដៅ liquidity ខាងលើ") + """
<table style='break-inside:avoid'><tr><th>ឧទាហរណ៍ BUY</th><th>គណនា</th><th>តម្លៃ</th></tr>
<tr><td>Sweep low (1.0)</td><td>–</td><td>4,100.00</td></tr>
<tr><td>High ថ្មី (0)</td><td>Leg = $60 = 600 pips</td><td>4,160.00</td></tr>
<tr><td>OTE 0.62</td><td>4,160 − 37.20</td><td>4,122.80</td></tr>
<tr><td>OTE 0.705 (entry)</td><td>4,160 − 42.30</td><td>4,117.70</td></tr>
<tr><td>OTE 0.79</td><td>4,160 − 47.40</td><td>4,112.60</td></tr>
<tr><td>Stop Loss</td><td>ក្រោម 4,100 + buffer</td><td>4,097.00 (−$20.70)</td></tr>
<tr><td>Target (BSL ខាងលើ / −0.27)</td><td>4,160 + 60 × 0.27</td><td>4,176.20 (+$58.50)</td></tr></table>
<p>នៅ <b>0.01 lot</b> (1 oz): ខាតប្រហែល <b>$20.70</b> ឬចំណេញប្រហែល <b>$58.50</b> (មិនរាប់ spread) · RR ≈ 1 : 2.8។ RR ល្អ <b>មិនមែន</b>មានន័យថាឱកាសឈ្នះខ្ពស់ទេ។</p>
<div class='box tip'>💡 ICT ប្រើកម្រិត <span class='en-term'>Fibonacci extension</span> (−0.27, −0.62) ជាគោលដៅ។ ប៉ុន្តែគោលដៅដែលមានហេតុផលជាងគឺ <b>liquidity ពិត</b> (PDH, equal highs, Asia high)។
បើ extension និង liquidity នៅជិតគ្នា នោះកាន់តែល្អ។</div>
"""),
        ("Turtle Soup: ការ Breakout ក្លែងក្លាយ", """
<p><span class='en-term'>Turtle Soup</span> ជាឈ្មោះដែលមកពី Linda Raschke និង Larry Connors (ឆ្លើយតបនឹងប្រព័ន្ធ "Turtle" ដែលទិញ breakout នៃ high 20 ថ្ងៃ)។
ICT ប្រើវាសម្រាប់: តម្លៃ<b>ឆ្លងហួស high/low ចាស់</b> (យក stops) ហើយ<b>បិទត្រឡប់ចូលវិញ</b> → trade ទិសផ្ទុយ។</p>
""" + candles([(40, 48, 36, 46), (46, 60, 44, 57), (57, 62, 50, 52), (52, 55, 44, 47), (47, 56, 45, 54), (54, 74, 52, 58), (58, 59, 40, 42), (42, 44, 28, 30), (30, 34, 18, 20)],
              lines=[(62, 0, 8, "High ចាស់ · BSL", GOLD, True)],
              notes={5: ("Sweep", OR, "top"), 6: ("បិទក្រោម", DN, "bottom")},
              caption="Bearish Turtle Soup: wick ឆ្លង high ចាស់ → ទៀនបិទត្រឡប់ក្រោម → ទៀនបន្ទាប់ធ្លាក់ (MSS)") + """
<ul><li><b>Bearish</b>: sweep high ចាស់ (BSL) → បិទក្រោម high → SELL · SL លើ wick នៃ sweep</li>
<li><b>Bullish</b>: sweep low ចាស់ (SSL) → បិទលើ low → BUY · SL ក្រោម wick នៃ sweep</li>
<li>Turtle Soup ល្អជាង ពេលវាកើតក្នុង <b>kill zone</b>, ផ្ទុយ high/low ធំ (PDH, PWH) និង<b>ស្រប bias</b> HTF</li></ul>
<div class='box warn'>⚠️ <b>ការសាកល្បងពិតរបស់ XAU.KH</b> (12 Nov 2026): Turtle Soup ជុំវិញព័ត៌មាន 8:30 New York ត្រូវបានសាកល្បង <b>72 version</b> លើទិន្នន័យ 5m រយៈពេល 2 ឆ្នាំ។
Version ដើម (TP ~1.2R) ឈ្នះប្រហែល 47–49% ហើយលទ្ធផលមធ្យម<b>តិចជាងសូន្យបន្តិច</b>។ Version ល្អបំផុតក្នុងចំណោម 72 មិនខុសពីលទ្ធផលដោយចៃដន្យទេ។
<b>គ្មាន version ណាមួយត្រូវបានបញ្ជាក់</b> ដូច្នេះ XAU.KH មិនផ្ញើវាជា signal ទេ។</div>
"""),
        ("Liquidity Engineering: តម្លៃ \"សាងសង់\" Liquidity", """
<p><span class='en-term'>Liquidity engineering</span> ជាគំនិតរបស់ ICT ថា មុនចលនាធំ តម្លៃច្រើនតែបង្កើតកម្រិតដែល<b>មើលឃើញងាយ</b> ដែល retail trader
ដាក់ stop ឬ entry ច្រើន ហើយបន្ទាប់មកតម្លៃមកយក liquidity នោះ។ ទម្រង់ដែលឃើញញឹកញាប់:</p>
<ul><li><span class='en-term'>Equal highs / equal lows</span> (EQH / EQL): កំពូល ឬបាតពីរនៅកម្រិតដូចគ្នា (Chapter 12)</li>
<li><span class='en-term'>Trendline liquidity</span>: បាតជាច្រើនដែលប៉ះខ្សែ trendline តែមួយ → stops នៅក្រោមខ្សែ</li>
<li><span class='en-term'>Inducement</span>: swing តូចមួយនៅមុន POI ដែល "ទាក់ទាញ" trader ចូលមុនពេល</li></ul>
""" + zigzag([55, 72, 40, 66, 40, 64, 40, 26, 52, 74, 92],
             {2: ("1", BL), 4: ("2", BL), 6: ("3", BL), 7: ("Sweep", OR), 10: ("BSL", UP)},
             lines=[(40, 1, 8, "", GR, True)],
             caption="Equal lows 1-2-3 (EQL) ច្បាស់ពេក → sell stops កកកុញនៅក្រោម → sweep → ឡើងទៅយក BSL") + """
<div class='box tip'>💡 យើងមិនដឹងថាអ្នកណាជា "អ្នកសាងសង់" ឬគោលបំណងរបស់គេទេ។ ចូរយល់វាដោយសាមញ្ញ: កម្រិតដែល<b>ច្បាស់ពេក</b>មាន orders ច្រើន
ហើយតម្លៃច្រើនតែទៅប៉ះកម្រិតនោះ។ កុំដាក់ SL របស់អ្នកនៅ<b>កន្លែងដែលអ្នកដទៃទាំងអស់ដាក់</b> (ពីក្រោម equal lows ផ្ទាល់)។</div>
"""),
        ("ភ្ជាប់គំនិតទាំងអស់: លំដាប់ ICT មួយ", """
<p>គំនិតទាំងអស់ក្នុង PART 3 អាចរៀបជា<b>លំដាប់</b>តែមួយ។ គោលដៅគឺឆ្លើយសំណួរ 6 តាមលំដាប់ មិនមែនរកគ្រប់ concept លើ chart ទេ:</p>
""" + flow([("Bias", "Daily/4H + draw", BL), ("Time", "Kill zone", GOLD), ("Sweep", "M / Judas / TS", OR),
            ("MSS", "+ displacement", UP), ("Entry", "FVG/OB ក្នុង OTE", PU), ("Target", "liquidity ផ្ទុយ", DN)],
           caption="Bias → ពេលវេលា → sweep → MSS → entry ក្នុង OTE → គោលដៅ liquidity · ខ្វះជំហានណាមួយ = រង់ចាំ") + """
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>សំណួរ</th><th>Chapter</th></tr>
<tr><td>Bias</td><td>HTF ចង់ទៅយក liquidity ខាងណា?</td><td>9, 12, 15, 16</td></tr>
<tr><td>Time</td><td>ឥឡូវជា kill zone ឬម៉ោងស្ងាត់?</td><td>16</td></tr>
<tr><td>Sweep</td><td>មាន liquidity ផ្ទុយ bias ត្រូវបានយកឬទេ?</td><td>12, 16, 17</td></tr>
<tr><td>MSS</td><td>LTF បិទទៀនបំបែក structure ជាមួយ displacement?</td><td>9</td></tr>
<tr><td>Entry</td><td>FVG ឬ OB នៅក្នុង OTE / discount?</td><td>13, 14, 15</td></tr>
<tr><td>Target</td><td>Liquidity ផ្ទុយនៅឯណា? RR ≥ 1 : 2?</td><td>12</td></tr></table>
"""),
        ("ឧទាហរណ៍ពេញលេញ: Bearish PO3 ក្នុង London", """
<p><b>ស្ថានភាព (ឧទាហរណ៍សម្រាប់រៀន):</b> 4H downtrend (LH + LL) · draw on liquidity = PDL 4,112 · ព្រឹកនេះ Asia range 4,128–4,142។</p>
<ol><li><b>Accumulation</b>: Asia ដើរចំហៀង 4,128–4,142 (range $14 = 140 pips)</li>
<li><b>Manipulation</b>: 14:40 (London KZ) តម្លៃឡើងហួស Asia high ដល់ <b>4,146.50</b> (sweep BSL = Judas swing / Turtle Soup)</li>
<li><b>MSS</b>: ទៀន 15m បិទក្រោម swing low 4,133 ជាមួយ displacement · leg ពី 4,146.50 ទៅ 4,126.00 ទុក bearish FVG 4,138–4,141</li>
<li><b>OTE</b> នៃ leg ($20.50): 0.62 = 4,138.71 · 0.705 = 4,140.45 · 0.79 = 4,142.20 → FVG ត្រួតនឹង OTE ✅</li></ol>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>កម្រិត</th><th>ចម្ងាយ</th></tr>
<tr><td>SELL limit (ក្នុង FVG + OTE)</td><td>4,140.00</td><td>–</td></tr>
<tr><td>Stop Loss (លើ sweep 4,146.50 + buffer)</td><td>4,148.00</td><td>$8.00 = 80 pips</td></tr>
<tr><td>TP1 (Asia low)</td><td>4,128.00</td><td>$12.00 = 120 pips</td></tr>
<tr><td>TP2 (PDL · SSL)</td><td>4,112.00</td><td>$28.00 = 280 pips</td></tr></table>
<ul><li>0.01 lot: ខាត ~$8 · TP1 ~$12 · TP2 ~$28 (មិនរាប់ spread)</li>
<li>បើតម្លៃ<b>បិទលើ 4,146.50</b> មុនប៉ះ entry → idea ខុស · លុប limit order</li>
<li>បើមាន 📰 News ធំនៅ 20:30 ហើយ trade នៅតែបើក → ពិចារណាកាត់ទំហំ ឬបិទមុន</li></ul>
<div class='box ok'>✅ ឧទាហរណ៍នេះបង្ហាញ<b>ដំណើរការគិត</b> មិនមែនការធានាលទ្ធផលទេ។ Setup ដែលល្អឥតខ្ចោះក៏អាចខាតបាន។ សូមគ្រប់គ្រងហានិភ័យរាល់ trade (PART Risk Management)។</div>
"""),
        ("កុំដាក់ Concept ច្រើនពេកលើ Chart", """
<p>អ្នកចាប់ផ្ដើម ICT ច្រើនតែគូរ FVG, OB, breaker, fib, session box, SMT, ... ទាំងអស់លើ chart តែមួយ។ លទ្ធផល: chart រញ៉េរញ៉ៃ
ហើយអ្នកអាច<b>រកហេតុផលសម្រាប់ទិសណាក៏បាន</b>។ នេះហៅថា <span class='en-term'>confirmation bias</span>។</p>
<table style='break-inside:avoid'><tr><th>ត្រូវមាន ✅</th><th>ជំនួយ (ជ្រើស 1–2)</th><th>រំលង ❌</th></tr>
<tr><td>Structure HTF · liquidity ធំ (PDH/PDL) · MSS លើ LTF</td><td>FVG ឬ OB · OTE · kill zone · SMT</td><td>Fib គ្រប់ swing · OB ចាស់ៗរាប់សិប · indicator ច្រើន</td></tr></table>
<ul><li>ច្បាប់ XAU.KH: <b>2–3 concept ស្របគ្នា គ្រប់គ្រាន់</b> · បើត្រូវការ 7 ហេតុផលដើម្បីចូល នោះ setup មិនច្បាស់ទេ</li>
<li>លុប object ចាស់ៗពី chart ជារៀងរាល់សប្ដាហ៍ · ប្រើ template MT5 តែមួយ</li>
<li>សរសេរ<b>ច្បាប់ចូល</b>មុនបើក chart ហើយកុំប្ដូរវាពេលកំពុងមើលតម្លៃ</li></ul>
<div class='box tip'>💡 រូប 📊 <b>Analysis</b> របស់ XAU.KH គូរ structure, liquidity (ELQ/ILQ), CHOCH/BOS, EQ 50% និង Asia box ឱ្យរួចហើយ។ ប្រើវាជាគំរូនៃ chart "ស្អាត"។</div>
"""),
        ("ការអនុវត្តក្នុង Group និងការសាកល្បងដោយស្មោះត្រង់", """
<ul><li>📊 <b>Analysis</b> មុន session: រក Asia range (A), មើលថា London sweep ខាងណា (M) ហើយ NY ដើរទៅណា (D)</li>
<li><b>/check</b>: ពិនិត្យ bias និងកម្រិតដែលនៅជិតតម្លៃ មុនគិតពី OTE ឬ Turtle Soup</li>
<li>🚨 <b>Signals</b>: មើលថា signal ចេញក្រោយ sweep + MSS ឬអត់ · 📈 <b>Proof</b> បង្ហាញលទ្ធផលពិតទាំងឈ្នះទាំងខាត</li>
<li>📰 <b>News</b>: Manipulation ធំៗច្រើនកើតជុំវិញព័ត៌មាន · កុំចូលមុនព័ត៌មានដោយសារតែ "PO3"</li></ul>
<div class='box warn'>⚠️ <b>មេរៀនពីការសាកល្បង XAU.KH:</b> model ICT (HTF zone → sweep + MSS → entry នៅ OB) ត្រូវបានសាកល្បងជាង 60 version។
Version ដែលមាន <b>HTF bias</b> មានលទ្ធផលល្អជាង version ដែលគ្មាន bias ហើយ version ជាច្រើនផ្សេងទៀតនៅជិតសូន្យ ឬខាត។
មានន័យថា concept ល្អ ≠ ចំណេញ។ ការលម្អិតច្បាប់ (bias, SL, ពេលវេលា) សំខាន់ ហើយត្រូវ<b>សាកល្បង (backtest)</b> មុនប្រើលុយពិត (Chapter 35)។</div>
<p><b>កំហុសញឹកញាប់:</b></p>
<ul><li>❌ ទាយ PO3 មុនមាន bias ហើយចូលនៅ "manipulation" ដោយគ្មាន MSS</li>
<li>❌ ប្រើ SMT ជាមួយ timeframe ឬ swing ខុសគ្នារវាងមាស និងប្រាក់</li>
<li>❌ ដាក់ limit order នៅ OTE រាល់ retrace ដោយមិនមើល structure</li>
<li>❌ Fade រាល់ breakout ដោយហៅវាថា Turtle Soup (breakout ពិតក៏មានដែរ)</li></ul>
"""),
    ],
    summary=["PO3 / AMD = Accumulation (Asia) → Manipulation (sweep / Judas) → Distribution (ចលនាពិត) · ទៀនថ្ងៃឡើង: ទិញក្រោម open",
             "SMT = មាស និងប្រាក់ (ឬ DXY បញ្ច្រាស) ធ្វើ swing មិនដូចគ្នានៅ liquidity សំខាន់ → ភស្តុតាងបន្ថែម",
             "OTE = 0.62–0.79 នៃ leg ដែលបង្កើត MSS · SL ក្រោម/លើ sweep · គោលដៅ = liquidity ពិត",
             "Turtle Soup = sweep high/low ចាស់ ហើយបិទត្រឡប់ · XAU.KH សាកល្បង 72 version: មិនបានបញ្ជាក់",
             "Bias → Time → Sweep → MSS → Entry → Target · 2–3 concept ស្របគ្នាគ្រប់គ្រាន់"],
    exercise=["រកថ្ងៃ 5 ចុងក្រោយលើ chart Daily មាស។ ថ្ងៃណាខ្លះមានរូប PO3 ច្បាស់ (wick ផ្ទុយទិស + body ធំ)? ថ្ងៃណាមិនមាន?",
              "បើក XAUUSD និង XAGUSD 15m ចំហៀងគ្នា ហើយរក SMT divergence មួយនៅ Asia high/low ឬ PDH/PDL។",
              "លើ leg ចុងក្រោយដែលបង្កើត MSS គណនា OTE 0.62 / 0.705 / 0.79 ជាលេខ ហើយពិនិត្យថាមាន FVG ឬ OB ត្រួតឬអត់។",
              "សរសេរច្បាប់ 6 ជំហានរបស់អ្នកលើក្រដាសតែមួយ។ ប្រៀបធៀបជាមួយ 🚨 Signals និង 📈 Proof មួយសប្ដាហ៍ ហើយកត់ត្រាលទ្ធផល។"],
)
