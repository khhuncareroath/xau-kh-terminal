from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def candles(data, level=None, level_text="", notes=None, w=420, h=190, caption=""):
    """Small candlestick sketch. data = [(open, high, low, close)] in 0-100 (100 = top).
    level = y of a horizontal line; notes = {index: (text, colour, 'top'|'bottom')}."""
    notes = notes or {}
    n = len(data)
    step = (w - 40) / n
    Y = lambda v: h - 22 - v * (h - 44) / 100
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    if level is not None:
        out.append(f'<line x1="14" x2="{w - 14}" y1="{Y(level):.1f}" y2="{Y(level):.1f}" stroke="{BL}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        out.append(f'<text x="16" y="{Y(level) - 5:.1f}" text-anchor="start" fill="{BL}" class="lt">{level_text}</text>')
    for i, (o, hi, lo, c) in enumerate(data):
        cx = 20 + (i + .5) * step
        col = UP if c >= o else DN
        bw = step * .56
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


CH = dict(
    ch=10, part="PART 2 · Technical Analysis & Market Structure",
    title_km="សកម្មភាពតម្លៃ", title_en="Price Action: Impulse · Momentum · Rejection · Retest",
    intro="""<b>Price Action (សកម្មភាពតម្លៃ)</b> គឺជាការអាន<b>របៀប</b>ដែលតម្លៃផ្លាស់ទី ដោយមើលទៀន និង swing ផ្ទាល់
មិនមែនពឹងលើ indicator។ ក្នុង Chapter 9 យើងរៀន<b>កន្លែង</b>ដែល structure បែក។ ក្នុងជំពូកនេះ យើងរៀនមើល
<b>កម្លាំង</b>នៅពីក្រោយចលនានោះ: តើទីផ្សារកំពុងរុញខ្លាំង ឬកំពុងសម្រាក? តើ level មួយកំពុងការពារបាន ឬកំពុងត្រូវបំបែក?
ចម្លើយទាំងនេះ ជួយឱ្យអ្នកដឹងថា<b>ពេលណាត្រូវរង់ចាំ</b> និង<b>ពេលណាត្រូវត្រៀមខ្លួន</b>។""",
    sections=[
        ("Price Action គឺជាអ្វី?", """
<p>រាល់ទៀនមួយៗ គឺជាលទ្ធផលនៃការប្រយុទ្ធរវាង<b>អ្នកទិញ</b> និង<b>អ្នកលក់</b>។ Price Action គឺការអានរឿងរ៉ាវនោះ:</p>
<ul><li><b>ទំហំ body</b>: body ធំ = ភាគីមួយឈ្នះច្បាស់ · body តូច = ស្មើគ្នា ឬស្ទាក់ស្ទើរ</li>
<li><b>Wick (ស្រមោល)</b>: wick វែង = តម្លៃទៅដល់ហើយ<b>ត្រូវរុញត្រឡប់</b></li>
<li><b>ល្បឿន</b>: ទៀនជាប់ៗគ្នាធំៗ = មានអ្នកធំចូល · ទៀនតូចៗត្រួតគ្នា = ទីផ្សារស្ងាត់</li>
<li><b>ទីតាំង</b>: ទៀនដដែល មានអត្ថន័យខុសគ្នា នៅកណ្ដាល range និងនៅ level សំខាន់</li></ul>
<div class='box tip'>💡 Price Action មិនមែនជាការទន្ទេញឈ្មោះទៀន (Chapter 5) ទេ។ វាជាការសួរថា "<b>តើភាគីណាកំពុងគ្រប់គ្រង ហើយកំពុងខ្សោយ ឬខ្លាំងឡើង?</b>"</div>
"""),
        ("Impulse និង Correction", """
<p>តម្លៃមិនដែលរត់ត្រង់ទេ។ វាដើរជា<b>រលក</b>:</p>
<ul><li><span class='en-term'>Impulse</span> (ចលនារុញ) = ចលនាខ្លាំង លឿន ទៀនធំ ទៅ<b>តាមទិស trend</b> ហើយច្រើនតែបង្កើត BOS</li>
<li><span class='en-term'>Correction</span> (ចលនាថយ) = ការថយក្រោយ<b>យឺតៗ</b> ទៀនតូច ត្រួតគ្នា ទៅផ្ទុយទិស trend</li></ul>
""" + zigzag([10, 52, 38, 80, 64, 96], {1: ("Impulse", UP), 2: ("Correction", OR), 3: ("Impulse", UP), 4: ("Correction", OR)},
            caption="Uptrend ល្អ: impulse វែង និងលឿន · correction ខ្លី និងយឺត") + """
<table style='break-inside:avoid'><tr><th>លក្ខណៈ</th><th>Impulse</th><th>Correction</th></tr>
<tr><td>ទិសដៅ</td><td>តាម trend</td><td>ផ្ទុយ trend</td></tr>
<tr><td>ទៀន</td><td>Body ធំ wick តូច</td><td>Body តូច wick ច្រើន ត្រួតគ្នា</td></tr>
<tr><td>ល្បឿន</td><td>លឿន (ទៀនតិច ចម្ងាយឆ្ងាយ)</td><td>យឺត (ទៀនច្រើន ចម្ងាយខ្លី)</td></tr>
<tr><td>អ្វីដែលយើងធ្វើ</td><td>កុំដេញតាម</td><td>រង់ចាំ entry នៅចុងរបស់វា</td></tr></table>
<div class='box ok'>✅ គំនិតសំខាន់: យើង<b>មិនចូលកណ្ដាល impulse</b>ទេ។ យើងរង់ចាំ correction មកដល់ level ល្អ (support, FVG, OB) រួចចូលតាមទិស impulse បន្ទាប់។</div>
"""),
        ("Momentum: កម្លាំងនៃចលនា", """
<p><span class='en-term'>Momentum</span> គឺជាល្បឿន និងកម្លាំងនៃតម្លៃ។ យើងអាចមើលវាដោយផ្ទាល់ពីទៀន:</p>
""" + candles([(20, 34, 18, 32), (32, 50, 30, 48), (48, 70, 46, 68), (68, 74, 62, 70), (70, 76, 64, 67), (67, 75, 63, 71)],
              notes={0: ("ខ្លាំង", UP, "bottom"), 2: ("ខ្លាំង", UP, "top"), 4: ("ខ្សោយ", OR, "top")},
              caption="ទៀន 1–3: body ធំ = momentum ខ្លាំង · ទៀន 4–6: body តូច wick វែង = momentum ចុះខ្សោយ") + """
<ul><li><b>Momentum ខ្លាំង</b>: body ធំ បិទជិត high (ឡើង) ឬជិត low (ធ្លាក់) ទៀនតាមគ្នាច្រើនក្នុងទិសតែមួយ</li>
<li><b>Momentum ខ្សោយ</b>: body តូចៗ wick វែង swing ថ្មីទៅបានតែបន្តិច ទោះបីនៅតែបង្កើត HH</li>
<li><b>Divergence ដោយភ្នែក</b>: impulse នីមួយៗខ្លីជាងមុន = trend កំពុងអស់កម្លាំង (មិនមែនសញ្ញាបង្វិលភ្លាមៗទេ)</li></ul>
""" + bars([("Leg 1", 42, UP), ("Leg 2", 30, UP), ("Leg 3", 18, OR), ("Leg 4", 9, DN)], unit="",
           caption="ឧទាហរណ៍: impulse នីមួយៗរបស់មាសខ្លីទៅៗ ($42 → $9) = momentum កំពុងធ្លាក់") + """
<div class='box warn'>⚠️ Momentum ខ្សោយ <b>មិនមែន</b>មានន័យថាត្រូវ SELL ភ្លាមៗទេ។ វាគ្រាន់តែប្រាប់ថា "<b>កុំ BUY ដេញតាមទៀត</b>" ហើយរង់ចាំ CHOCH (Chapter 9) មុន។</div>
"""),
        ("Consolidation និង Expansion", """
<p>ទីផ្សារប្ដូររវាងពីរស្ថានភាពរហូត:</p>
<ul><li><span class='en-term'>Consolidation</span> (ការប្រមូលផ្ដុំ) = តម្លៃនៅក្នុង range តូច ទៀនតូច អ្នកទិញ និងអ្នកលក់ស្មើគ្នា។ Orders និង Stop Loss កើនឡើងនៅសងខាង range។</li>
<li><span class='en-term'>Expansion</span> (ការពង្រីក) = តម្លៃបែកចេញពី range ដោយទៀនធំៗ ហើយរត់ឆ្ងាយ។</li></ul>
""" + flow([("Consolidation", "range តូច ស្ងាត់", GR), ("Breakout", "បែកចេញ ទៀនធំ", BL),
            ("Expansion", "រត់ខ្លាំង", UP), ("Consolidation", "សម្រាកម្ដងទៀត", GR)],
           caption="វដ្តទីផ្សារ: សម្រាក → ពង្រីក → សម្រាក → ...") + zigzag(
    [40, 52, 42, 51, 43, 50, 44, 88, 76, 92], {6: ("Range", GR), 7: ("Expansion", UP)},
    lines=[(52, 0, 6, "", GR, True), (42, 0, 6, "", GR, True)],
    caption="Range តូចយូរ → expansion ខ្លាំង ពេលតម្លៃបែកចេញ") + """
<div class='box tip'>💡 Range កាន់តែតូច និងយូរ ជាញឹកញាប់ expansion បន្ទាប់កាន់តែខ្លាំង។ សញ្ញា ⭐ 4H ក្នុង 🚨 Signals របស់ XAU.KH
ផ្អែកលើគំនិតនេះ: វារង់ចាំ <b>expansion</b> ចេញពី range ប្រហែល 30 ទៀន 4H។</div>
<div class='box warn'>⚠️ ក្នុង consolidation តម្លៃលោតឡើងចុះគ្មានទិស។ Trade ច្រើនក្នុង range តូច = ខាត spread និង SL ច្រើនដង។ ការ<b>រង់ចាំ</b>ក៏ជាការសម្រេចចិត្តមួយដែរ។</div>
"""),
        ("Rejection និង Acceptance", """
<p>ពេលតម្លៃមកដល់ level សំខាន់ មានលទ្ធផលពីរ:</p>
<ul><li><span class='en-term'>Rejection</span> (ការបដិសេធ) = តម្លៃប៉ះ ឬឆ្លង level ហើយ<b>ត្រូវរុញត្រឡប់</b>។ ឃើញជា wick វែង ហើយបិទនៅខាងដើមវិញ។</li>
<li><span class='en-term'>Acceptance</span> (ការទទួលយក) = តម្លៃ<b>បិទទៀនច្រើន</b>នៅខាងម្ខាងទៀតនៃ level ហើយនៅទីនោះបាន។ ទីផ្សារទទួលយកតម្លៃថ្មី។</li></ul>
""" + candles([(30, 44, 28, 42), (42, 58, 40, 55), (55, 78, 52, 58), (58, 62, 44, 47), (47, 50, 36, 38)], level=70, level_text="Resistance 4,050",
              notes={2: ("Rejection", DN, "top")},
              caption="Rejection: wick ឡើងហួស 4,050 ប៉ុន្តែបិទក្រោមវិញ → អ្នកលក់ការពារ level") + candles(
    [(30, 44, 28, 42), (42, 60, 40, 58), (58, 76, 56, 74), (74, 80, 70, 77), (77, 84, 73, 81)], level=70, level_text="Resistance 4,050",
    notes={3: ("Acceptance", UP, "top")},
    caption="Acceptance: បិទលើ 4,050 ច្រើនទៀនជាប់គ្នា → level ចាស់អាចក្លាយជា support") + """
<table style='break-inside:avoid'><tr><th></th><th>Rejection</th><th>Acceptance</th></tr>
<tr><td>ទៀន</td><td>Wick វែង បិទត្រឡប់</td><td>Body បិទហួស level ច្រើនដង</td></tr>
<tr><td>អត្ថន័យ</td><td>Level ការពារបាន</td><td>Level ត្រូវបំបែក</td></tr>
<tr><td>គំនិតបន្ទាប់</td><td>អាចត្រឡប់ទិស</td><td>អាចបន្ត ហើយ retest</td></tr></table>
<div class='box tip'>💡 Wick តែមួយ មិនទាន់គ្រប់គ្រាន់ទេ។ ចាំមើលទៀន<b>បន្ទាប់</b>: បើវាបន្តទៅផ្ទុយពី level នោះ rejection កាន់តែច្បាស់។</div>
"""),
        ("Breakout និង Retest", """
<p><span class='en-term'>Breakout</span> កើតឡើងពេលតម្លៃបិទទៀនហួស level សំខាន់។ ជាញឹកញាប់ តម្លៃ<b>ត្រឡប់មកប៉ះ</b> level នោះម្ដងទៀត
ហៅថា <span class='en-term'>Retest</span>។ Resistance ចាស់ក្លាយជា support ថ្មី (ឬផ្ទុយមកវិញ)។</p>
""" + zigzag([20, 50, 36, 52, 38, 78, 56, 92], {5: ("Breakout", UP), 6: ("Retest", BL)},
            lines=[(56, 0, 2, "4,050", BL, True), (56, 2, 7, "", BL, True)], caption="បែក 4,050 → ត្រឡប់មក retest (resistance ចាស់ = support ថ្មី) → បន្តឡើង") + flow(
    [("Breakout", "បិទទៀនហួស level", BL), ("Retest", "ត្រឡប់មកប៉ះ", OR), ("Confirm", "rejection 15m", UP), ("Entry", "SL ក្រោម retest", GOLD)],
    caption="ជំហាន breakout + retest") + """
<div class='box ok'>✅ ការចូលនៅ retest ល្អជាងដេញ breakout ព្រោះ SL <b>ខ្លីជាង</b> និងច្បាស់ជាង (ក្រោម retest low)។ ប៉ុន្តែ breakout ខ្លាំងៗ ពេលខ្លះ<b>មិន retest</b>ទេ: ទទួលយកថាអ្នកនឹងខកខានខ្លះ។</div>
"""),
        ("False Breakout: ការបែកក្លែងក្លាយ", """
<p><span class='en-term'>False breakout</span> (ឬ fakeout) = តម្លៃឆ្លង level បន្តិច ហើយ<b>ត្រឡប់មកក្នុងវិញភ្លាម</b>។ វាច្រើនតែជាការ
<b>បោសយក Stop Loss</b> (liquidity sweep: Chapter 12) មុនពេលរត់ទៅទិសពិត។</p>
""" + zigzag([30, 62, 40, 61, 42, 72, 50, 20], {5: ("Fake", DN), 7: ("ធ្លាក់ពិត", DN)},
            lines=[(62, 0, 7, "Resistance", GR, True)], caption="ឆ្លងលើ resistance បន្តិច → បិទត្រឡប់មកក្រោម → ធ្លាក់ខ្លាំង") + """
<ul><li>សញ្ញា false breakout: wick ហួស ប៉ុន្តែ body បិទក្នុង range · គ្មាន displacement · ត្រឡប់មកវិញក្នុង 1–3 ទៀន</li>
<li>សញ្ញា breakout ពិត: body ធំបិទហួស · ទៀនបន្ទាប់នៅខាងក្រៅ · មាន acceptance</li></ul>
<div class='box warn'>⚠️ កុំ BUY ភ្លាមៗ ពេលទៀនកំពុងឆ្លង resistance។ រង់ចាំទៀន<b>បិទ</b> (យ៉ាងហោចណាស់ 15m) ហើយប្រសើរជាងនេះ រង់ចាំ retest។</div>
"""),
        ("អានតម្លៃនៅជុំវិញ Level សំខាន់", """
<p>សំណួរសំខាន់បំផុតគឺ "<b>តម្លៃមកដល់ level ដោយរបៀបណា?</b>"</p>
<table style='break-inside:avoid'><tr><th>ការមកដល់ level</th><th>អត្ថន័យទំនង</th><th>អ្វីត្រូវធ្វើ</th></tr>
<tr><td>Impulse ខ្លាំង ទៀនធំ ជាប់ៗ</td><td>មានកម្លាំង អាចបំបែក level</td><td>កុំប្រឆាំង · ចាំមើល acceptance ឬ retest</td></tr>
<tr><td>Correction យឺតៗ ទៀនតូច</td><td>Level ទំនងការពារបាន</td><td>រកមើល rejection ដើម្បីចូលតាម trend</td></tr>
<tr><td>ប៉ះ level ច្រើនដងជាប់គ្នា</td><td>Orders ត្រូវប្រើអស់បន្តិចម្ដងៗ</td><td>ប្រយ័ត្ន breakout (level ខ្សោយទៅៗ: Chapter 7)</td></tr>
<tr><td>Wick ហួស ហើយបិទត្រឡប់</td><td>Sweep / rejection</td><td>ចាំ CHOCH លើ timeframe តូច</td></tr></table>
<div class='box tip'>💡 Level ដែលល្អសម្រាប់មាស: high/low ថ្ងៃមុន លេខមូល (4,000 · 4,050 · 4,100) និង level 4H។ រូប 📊 Analysis របស់ XAU.KH គូរ level ទាំងនេះរួចហើយ។
វាយ <b>/check</b> ក្នុង group ដើម្បីមើលថាតម្លៃឥឡូវនៅជិត level ណា។</div>
"""),
        ("ឧទាហរណ៍ជាលេខ: មាសនៅ 4,050", """
<p>ស្មើថា 4H ជា uptrend។ មាសរត់ពី 4,010 ទៅ 4,068 ក្នុង 3 ទៀន 4H (<b>impulse</b> $58 = 580 pips) ហើយបែក resistance 4,050។
បន្ទាប់មក ក្នុង 10 ទៀន 1H វាថយមក 4,052 យឺតៗ (<b>correction</b> ទៅ retest)។ នៅ 4,052 ទៀន 15m មួយមាន wick ក្រោមវែង
ហើយបិទ 4,058 (<b>rejection</b>)។</p>
<table style='break-inside:avoid'><tr><th>ផែនការ</th><th>តម្លៃ</th><th>ចម្ងាយ</th><th>0.01 lot</th></tr>
<tr><td>Entry BUY</td><td>4,058</td><td>—</td><td>—</td></tr>
<tr><td>SL (ក្រោម retest low)</td><td>4,048</td><td>$10 = 100 pips</td><td>−$10</td></tr>
<tr><td>TP (high ចាស់)</td><td>4,068</td><td>$10 = 100 pips</td><td>+$10</td></tr>
<tr><td>TP2 (បើបន្ត)</td><td>4,082</td><td>$24 = 240 pips</td><td>+$24</td></tr></table>
<div class='box warn'>⚠️ នេះជាឧទាហរណ៍សម្រាប់រៀន មិនមែនជា signal ទេ។ TP1 = 1:1 និង TP2 ≈ 1:2.4: មុនចូល trade ត្រូវគិត <b>Risk:Reward</b> ជានិច្ច (PART 7)។
ហើយ setup ល្អបំផុត ក៏អាចខាតបានដែរ។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ដេញទិញនៅចុង impulse ពេលទៀនធំបំផុតទើបបិទ</li>
<li>❌ ហៅ wick តែមួយថា rejection ដោយមិនមើលទៀនបន្ទាប់</li>
<li>❌ Trade ច្រើនក្នុង consolidation ហើយខាតដោយសារ spread</li>
<li>❌ ចូល breakout មុនទៀនបិទ ហើយត្រូវ false breakout</li>
<li>❌ មើលទៀន 1m តែឯង ដោយគ្មាន context 4H / 1H</li></ul>
<div class='box ok'>✅ ក្នុង 📈 Proof អ្នកអាចមើល trade ចាស់ៗរបស់ XAU.KH ហើយហាត់សួរថា: តើតម្លៃមកដល់ entry ដោយ impulse ឬ correction?</div>
"""),
    ],
    summary=["Impulse = ចលនាខ្លាំងតាម trend · Correction = ថយក្រោយយឺតៗ: ចូលនៅចុង correction",
             "Momentum មើលពី body ទៀន ល្បឿន និងប្រវែង impulse",
             "Consolidation → Expansion: range តូចយូរ ច្រើនតែនាំទៅចលនាខ្លាំង",
             "Rejection = wick ហើយបិទត្រឡប់ · Acceptance = បិទហួស level ច្រើនទៀន",
             "Breakout + Retest ល្អជាងដេញ · ប្រយ័ត្ន false breakout"],
    exercise=["បើក chart មាស 1H ហើយសម្គាល់ impulse 3 និង correction 3 ចុងក្រោយ។ តើ impulse ណាវែងជាង?",
              "រក range (consolidation) មួយលើ 15m ហើយមើលថាវាបែកចេញទិសណា និងបែកដោយ displacement ឬអត់។",
              "រក level មួយដែលមាន rejection និង level មួយដែលមាន acceptance នៅសប្ដាហ៍នេះ។",
              "វាយ <b>/check</b> ក្នុង group ហើយប្រៀបធៀប level ដែលវាបង្ហាញ ជាមួយអ្វីដែលអ្នកឃើញ។"],
)
