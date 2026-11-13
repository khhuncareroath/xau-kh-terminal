from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def _scene(points, labels=None, rects=None, segs=None, caption="", w=420, h=190):
    """Price path (0-100, like zigzag) plus shaded zones and free lines.
    labels = {i: (text, colour[, 'a'|'b'])}  ('a' above, 'b' below; default: above on an up-move)
    rects  = [(y_lo, y_hi, i_from, i_to, text, colour)]          zones (supply / demand)
    segs   = [(i1, y1, i2, y2, text, colour, dashed)]            any straight line (trendline, channel, level)"""
    labels, rects, segs = labels or {}, rects or [], segs or []
    n = len(points)
    X = lambda i: 20 + i * (w - 40) / (n - 1)
    Y = lambda v: h - 20 - v * (h - 40) / 100
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for (lo, hi, a, b, t, col) in rects:
        out.append(f'<rect x="{X(a):.1f}" y="{Y(hi):.1f}" width="{X(b) - X(a):.1f}" height="{Y(lo) - Y(hi):.1f}" rx="4" '
                   f'fill="{col}" fill-opacity=".16" stroke="{col}" stroke-opacity=".6" stroke-width="1"/>')
        if t:
            out.append(f'<text x="{X(a) + 4:.1f}" y="{Y(lo) + 13:.1f}" fill="{col}" class="lt">{t}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(points))
    out.append(f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linejoin="round"/>')
    for (i1, y1, i2, y2, t, col, dash) in segs:
        out.append(f'<line x1="{X(i1):.1f}" y1="{Y(y1):.1f}" x2="{X(i2):.1f}" y2="{Y(y2):.1f}" stroke="{col}" stroke-width="1.8"'
                   + (' stroke-dasharray="5 4"' if dash else "") + "/>")
        if t:
            out.append(f'<text x="{X(i2) - 2:.1f}" y="{Y(y2) - 6:.1f}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    for i, lab in labels.items():
        t, col = lab[0], lab[1]
        pos = lab[2] if len(lab) > 2 else ("a" if i > 0 and points[i] >= points[i - 1] else "b")
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(points[i]):.1f}" r="3.2" fill="{col}"/>')
        out.append(f'<text x="{X(i):.1f}" y="{Y(points[i]) + (-9 if pos == "a" else 17):.1f}" text-anchor="middle" fill="{col}" class="pt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=7, part="PART 2 · Technical Analysis & Market Structure",
    title_km="កម្រិតគាំទ្រ និងកម្រិតទប់", title_en="Support & Resistance · Supply & Demand",
    intro="""<span class='en-term'>Support</span> និង <span class='en-term'>Resistance</span> គឺជាឧបករណ៍ចាស់ជាងគេ
និងប្រើច្រើនជាងគេក្នុង trading។ វាប្រាប់យើងថា<b>តម្លៃណា</b>ដែលអ្នកទិញ ឬអ្នកលក់ធ្លាប់ការពារ ហើយអាចនឹងការពារម្ដងទៀត។
ក្នុងជំពូកនេះ អ្នកនឹងរៀនគូរ level ផ្ដេក ស្គាល់ <span class='en-term'>Supply / Demand zone</span>
បែងចែក level <b>ខ្លាំង</b> និង<b>ខ្សោយ</b> ហើយសំខាន់បំផុត គឺបែងចែក <b>breakout ពិត</b> ពី <b>false breakout</b>។""",
    sections=[
        ("Support និង Resistance គឺជាអ្វី?", """
<p><span class='en-term'>Support</span> (កម្រិតគាំទ្រ) គឺជាតម្លៃ<b>ខាងក្រោម</b>ដែលតម្លៃធ្លាប់ឈប់ធ្លាក់ ហើយលោតឡើងវិញ
ព្រោះមាន<b>អ្នកទិញ</b>ច្រើនរង់ចាំនៅទីនោះ។ <span class='en-term'>Resistance</span> (កម្រិតទប់) គឺជាតម្លៃ<b>ខាងលើ</b>
ដែលតម្លៃធ្លាប់ឈប់ឡើង ហើយធ្លាក់វិញ ព្រោះមាន<b>អ្នកលក់</b>ច្រើន។</p>
""" + zigzag([30, 72, 34, 74, 31, 70, 33, 60], {1: ("R", DN), 3: ("R", DN), 5: ("R", DN), 2: ("S", UP), 4: ("S", UP), 6: ("S", UP)},
             lines=[(73, 0, 7, "Resistance 4,050", DN, True), (32, 0, 7, "", UP, True)],
             caption="បន្ទាត់បៃតង = Support 4,000 · តម្លៃលោតរវាង Support (4,000) និង Resistance (4,050) = Range $50 = 500 pips") + """
<p>ហេតុអ្វីបានជាវាដំណើរការ? ព្រោះមនុស្ស<b>ចងចាំតម្លៃ</b>។ អ្នកដែលខកខានទិញនៅ 4,000 លើកមុន នឹងរង់ចាំទិញនៅទីនោះម្ដងទៀត។
អ្នកដែលទិញនៅ 4,050 ហើយជាប់ខាត នឹងចង់លក់ចេញពេលតម្លៃត្រឡប់មកដល់ 4,050 វិញ ("ឱ្យតែរួចដើម")។
Orders ទាំងនេះប្រមូលផ្ដុំនៅ level ដដែល។</p>
<div class='box tip'>💡 Support / Resistance <b>មិនមែនជាជញ្ជាំងដែក</b>ទេ។ វាគ្រាន់តែជាតំបន់ដែល<b>ឱកាស</b>ឱ្យតម្លៃប្រតិកម្មខ្ពស់ជាងធម្មតា។
គ្រប់ level អាចបែកបាន។</div>
"""),
        ("របៀបគូរ Horizontal Level", """
<p>ចាប់ផ្ដើមពី timeframe <b>ធំ</b> (Daily, 4H) រួចចុះមកតូច (1H, 15m) ដូចដែលបានរៀនក្នុង Chapter 6។
Level ពី timeframe ធំ <b>សំខាន់ជាង</b> level ពី 5m។ កន្លែងល្អសម្រាប់គូរ level:</p>
<table><tr><th>ប្រភព level</th><th>ឧទាហរណ៍</th></tr>
<tr><td>Swing high / swing low ច្បាស់ៗ</td><td>កំពូលដែលតម្លៃធ្លាក់ចុះខ្លាំងពីវា</td></tr>
<tr><td><span class='en-term'>PDH / PDL</span> (Previous Day High/Low)</td><td>ខ្ពស់ / ទាបបំផុតរបស់ម្សិលមិញ</td></tr>
<tr><td>លេខគត់ (<span class='en-term'>round number</span>)</td><td>4,000 · 4,050 · 4,100</td></tr>
<tr><td>កន្លែងដែលតម្លៃប៉ះច្រើនដង</td><td>បាតដដែល 2–3 ដង</td></tr>
<tr><td>Level ចាស់ដែលបែក ហើយប្ដូរតួនាទី</td><td>Resistance ចាស់ ក្លាយជា Support</td></tr></table>
<ul><li>គូរលើ<b>ចុង wick</b> ឬ<b>តួទៀន (body)</b> ក៏បាន ប៉ុន្តែត្រូវ<b>ធ្វើដូចគ្នាជានិច្ច</b>។</li>
<li>កុំគូរ level ច្រើនពេក។ Chart ដែលមាន 15 បន្ទាត់ គឺស្មើនឹងគ្មាន level ណាមួយសំខាន់។ ជ្រើសតែ <b>2–4 level</b> ជិតតម្លៃបច្ចុប្បន្ន។</li></ul>
<div class='box ok'>✅ នៅ XAU.KH រៀងរាល់ព្រឹក <b>Daily Outlook</b> ផ្ដល់ <b>🔴 Resistance · 🟡 Pivot · 🟢 Support</b> រួចជាស្រេច
(ផ្អែកលើ level 4H, PDH/PDL និង POC)។ ប្រើវាជាចំណុចចាប់ផ្ដើម ហើយផ្ទៀងផ្ទាត់លើ chart MT5 របស់អ្នក។</div>
"""),
        ("Level ជា \"តំបន់\" មិនមែនបន្ទាត់តែមួយ", """
<p>មាសជាទីផ្សារដែលលឿន។ តម្លៃកម្រប៉ះ level <b>ចំ</b>សេនណាស់។ ពេលខ្លះវាឈប់មុន $1–2 ពេលខ្លះហួស $2–3 ទើបត្រឡប់។
ដូច្នេះ យើងគួរគិតពី level ជា<b>តំបន់ (zone)</b> ដែលមានកម្រាស់បន្តិច។</p>
""" + _scene([70, 45, 62, 40, 58, 43, 65, 80],
             labels={1: ("1", UP, "a"), 3: ("2", UP, "a"), 5: ("3", UP, "a")},
             rects=[(38, 47, 0, 7, "Support zone 3,998–4,004", UP)],
             caption="បាតទាំង 3 មិនស្មើគ្នាចំ ប៉ុន្តែនៅក្នុងតំបន់តែមួយ") + """
<ul><li>គូរ zone ពី<b>ចុង wick</b> ដល់<b>តួទៀន</b>នៃប្រតិកម្មសំខាន់។</li>
<li>Zone លើ 4H / Daily ជាធម្មតា<b>ធំជាង</b> zone លើ 15m។</li>
<li>Zone ធំពេក (ឧ. $20) មិនអាចប្រើបាន ព្រោះ Stop Loss នឹងធំពេក។ បើ zone ធំ សូមចុះទៅ timeframe តូច ដើម្បីរកផ្នែកដែលច្បាស់ជាង។</li></ul>
<div class='box warn'>⚠️ កុំដាក់ Stop Loss <b>ចំលើ</b> level។ ដាក់វានៅ<b>ខាងក្រៅ zone</b> បន្ថែម buffer បន្តិច (ព្រោះ spread និងតម្លៃ broker ខុសគ្នា ដូចបានរៀនក្នុង Chapter 2)។</div>
"""),
        ("Supply Zone និង Demand Zone", """
<p><span class='en-term'>Demand zone</span> គឺជាតំបន់ដែលតម្លៃ<b>រត់ឡើងលឿន</b>ចេញពីវា (អ្នកទិញខ្លាំងជាង)។
<span class='en-term'>Supply zone</span> គឺជាតំបន់ដែលតម្លៃ<b>ធ្លាក់លឿន</b>ចេញពីវា (អ្នកលក់ខ្លាំងជាង)។
ខុសពី S/R ធម្មតា យើងមិនរាប់ចំនួនដងដែលតម្លៃប៉ះទេ។ យើងមើលលើ<b>កម្លាំងនៃការរត់ចេញ</b>។</p>
""" + flow([("Drop", "ធ្លាក់", DN), ("Base", "ឈប់ ទៀនតូចៗ", GR), ("Rally", "ឡើងលឿន", UP), ("Demand", "= តំបន់ Base", UP)],
           caption="Drop-Base-Rally (DBR) បង្កើត Demand · Rally-Base-Drop (RBD) បង្កើត Supply") + _scene(
    [70, 40, 38, 41, 39, 75, 68, 88, 60, 44, 74],
    labels={9: ("", UP)},
    rects=[(36, 43, 1, 10, "DEMAND", UP)],
    caption="Base (ទៀនតូចៗ) → Rally ខ្លាំង · ពេលត្រឡប់មក zone ដំបូង ជាឱកាសរកការទិញ") + """
<p>គំនិតនៅពីក្រោយ: នៅក្នុង <b>base</b> អ្នកជួញដូរធំៗអាចមិនទាន់ទិញគ្រប់ចំនួនដែលគេចង់បាន។
ពេលតម្លៃត្រឡប់មក zone នោះ orders ដែលនៅសល់អាចរុញតម្លៃឡើងម្ដងទៀត។ (យើងនឹងរៀនគំនិតស្រដៀងគ្នាលម្អិតជាងនេះក្នុង
<span class='en-term'>Order Block</span> នៅ PART 3)។</p>
<div class='box tip'>💡 នៅលើរូប <b>📊 Analysis</b> និងសញ្ញា <b>🚨 Signals</b> របស់ XAU.KH អ្នកនឹងឃើញប្រអប់ <b>DEMAND</b> (បៃតង) និង <b>SUPPLY</b> (ក្រហម)។
Bot ពិនិត្យ Demand/Supply លើ 15m ដល់ Daily ហើយ<b>មិនផ្ញើ</b>សញ្ញាដែលមាន zone ផ្ទុយទិសនៅជិតពេកទេ។</div>
"""),
        ("Level ខ្លាំង និង Level ខ្សោយ", """
<p>Level ទាំងអស់មិនស្មើគ្នាទេ។ មុនពេលប្រើ level មួយ សូមសួរសំណួរខាងក្រោម:</p>
<table><tr><th>លក្ខណៈ</th><th>Level ខ្លាំង 💪</th><th>Level ខ្សោយ</th></tr>
<tr><td>Timeframe</td><td>Daily / 4H</td><td>5m / 1m</td></tr>
<tr><td>ការរត់ចេញ</td><td>លឿន ទៀនធំ (displacement)</td><td>យឺត ទៀនតូចៗ</td></tr>
<tr><td>ភាពស្រស់</td><td>Fresh: មិនទាន់ត្រឡប់មកប៉ះ</td><td>ប៉ះច្រើនដងរួចហើយ</td></tr>
<tr><td>ទីតាំង</td><td>ស្របនឹងលេខគត់ ឬ PDH/PDL</td><td>នៅកណ្ដាល range គ្មានអ្វីពិសេស</td></tr>
<tr><td>ទិសដៅ trend</td><td>Demand ក្នុង uptrend / Supply ក្នុង downtrend</td><td>ទិញនៅ demand ក្នុង downtrend ខ្លាំង</td></tr></table>
<div class='box ok'>✅ Level ដែលមានលក្ខណៈខ្លាំង <b>ច្រើន</b> (ឧ. Daily + fresh + លេខគត់ 4,000 + ស្របនឹង trend) សមនឹងការយកចិត្តទុកដាក់ជាង level ដែលមានតែមួយ។
ប៉ុន្តែនៅតែត្រូវការ Stop Loss ជានិច្ច។</div>
"""),
        ("Fresh Zone និង Tested Zone", """
<p><span class='en-term'>Fresh zone</span> គឺជា zone ដែលតម្លៃ<b>មិនទាន់</b>ត្រឡប់មកប៉ះ ចាប់តាំងពីវាត្រូវបានបង្កើត។
<span class='en-term'>Tested zone</span> គឺជា zone ដែលតម្លៃបានប៉ះរួចម្ដង ឬច្រើនដង។</p>
""" + _scene([75, 40, 70, 42, 60, 44, 52, 43, 46, 25],
             labels={1: ("Fresh", UP, "b"), 3: ("Test 1", OR, "b"), 5: ("Test 2", OR, "b"), 7: ("Test 3", DN, "b")},
             rects=[(38, 46, 0, 9, "", UP)],
             caption="ការលោតខ្សោយទៅៗ ក្រោយការប៉ះម្ដងៗ → ទីបំផុត zone បែក") + """
<p>រាល់ពេលតម្លៃមកប៉ះ zone orders មួយចំនួនត្រូវបាន<b>ប្រើអស់</b>។ ដូច្នេះ ជាទូទៅ ការប៉ះលើកទី <b>1</b> មានឱកាសប្រតិកម្មល្អជាងគេ
ហើយការប៉ះលើកក្រោយៗ ខ្សោយទៅៗ។ សូមសង្កេតក្នុងរូបខាងលើ: ការលោតឡើងនីមួយៗ<b>ទាបជាងមុន</b> (ជាសញ្ញាថាអ្នកលក់កំពុងខ្លាំងឡើង)។</p>
<div class='box warn'>⚠️ ពាក្យថា "level ដែលប៉ះច្រើនដង = ខ្លាំង" គឺ<b>ត្រូវមួយផ្នែក</b>ប៉ុណ្ណោះ។ វាបង្ហាញថា level នោះ<b>សំខាន់</b> ប៉ុន្តែការប៉ះច្រើនក៏អាចធ្វើឱ្យវា<b>ងាយបែក</b>ដែរ
ជាពិសេសពេលការលោតនីមួយៗខ្សោយជាងមុន។</div>
"""),
        ("ការប្ដូរតួនាទី: Support ក្លាយជា Resistance", """
<p>នៅពេល level មួយ<b>បែកពិតប្រាកដ</b> វាជារឿយៗប្ដូរតួនាទី (<span class='en-term'>role reversal</span> ឬ <span class='en-term'>flip</span>)។
Resistance ចាស់ ក្លាយជា Support ថ្មី ហើយ Support ចាស់ ក្លាយជា Resistance ថ្មី។</p>
""" + zigzag([20, 55, 35, 56, 38, 80, 57, 92], {1: ("R", DN), 3: ("R", DN), 6: ("S ថ្មី", UP)},
             lines=[(56, 0, 7, "", BL, True)],
             caption="បែក Resistance 4,050 → ត្រឡប់មកប៉ះ (retest) → 4,050 ក្លាយជា Support") + """
<p>ហេតុផល: អ្នកដែលលក់នៅ 4,050 ហើយតម្លៃបែកឡើង ជាប់ខាត។ ពេលតម្លៃត្រឡប់មក 4,050 វិញ ពួកគេជាច្រើន<b>ទិញត្រឡប់</b>ដើម្បីបិទ
trade "រួចដើម"។ អ្នកដែលខកខាន breakout ក៏ចង់ទិញនៅទីនោះដែរ។</p>
"""),
        ("Breakout: ការបែក Level ពិតប្រាកដ", """
<p><span class='en-term'>Breakout</span> កើតឡើងនៅពេលដែលតម្លៃ<b>បិទទៀន</b>ឆ្លងកាត់ level ហើយ<b>នៅបាន</b>ខាងក្រៅវា។
សញ្ញាដែលធ្វើឱ្យ breakout គួរឱ្យទុកចិត្តជាង:</p>
<ul><li>ទៀនបែកមាន<b>តួធំ</b> បិទជិតចុងរបស់វា (wick តូច)</li>
<li>ការបែកស្របនឹង <b>trend</b> លើ timeframe ធំ</li>
<li>មានការ <b>retest</b> ហើយ level ថ្មីការពារបាន</li>
<li>មិនមែនបែកនៅពេលព័ត៌មានធំ ដែលតម្លៃលោតចុះឡើងខ្លាំង (មើល <b>📰 News</b>)</li></ul>
""" + flow([("Level", "Resistance 4,050", DN), ("Break", "បិទទៀនលើ 4,050", UP), ("Retest", "ត្រឡប់មកប៉ះ 4,050", OR), ("Entry", "ទៀនបញ្ជាក់ ↑", UP)],
           caption="Breakout + Retest: អ្នកមិនចាំបាច់ដេញទៀនបែកទេ") + """
<div class='box ok'>✅ ឧទាហរណ៍: មាសបិទលើ 4,050 រួចត្រឡប់មក 4,052។ អ្នកទិញ <b>0.01 lot</b> នៅ 4,052 SL 4,044 (ក្រោម zone)។
ចម្ងាយ SL = $8 = 80 pips → ហានិភ័យ <b>$8</b>។ TP 4,068 = $16 = 160 pips → ចំណេញ <b>$16</b> (2R)។ បើ SL ប៉ះ អ្នកខាត $8 ដូចបានគ្រោងទុក។</div>
"""),
        ("False Breakout: អន្ទាក់ដ៏ពេញនិយមបំផុត", """
<p><span class='en-term'>False breakout</span> (ឬ <span class='en-term'>fakeout</span>) គឺនៅពេលដែលតម្លៃឆ្លង level
ហើយ<b>ត្រឡប់ចូលវិញ</b>យ៉ាងលឿន។ ជាញឹកញាប់វាឆ្លងតែ <b>wick</b> ហើយទៀនបិទនៅខាងក្នុងវិញ។</p>
""" + _scene([30, 60, 40, 62, 45, 80, 58, 35, 20],
             labels={5: ("Wick ឆ្លង", DN, "a")},
             segs=[(0, 63, 8, 63, "Resistance 4,050", DN, True)],
             caption="ឆ្លង 4,050 តែ wick → បិទក្រោមវិញ → ធ្លាក់ខ្លាំង: អ្នកទិញ breakout ជាប់អន្ទាក់") + """
<p>ហេតុអ្វីវាកើតឡើង? នៅលើ resistance មាន <b>Stop Loss របស់អ្នកលក់</b> និង <b>Buy Stop</b> របស់អ្នកដេញ breakout។
តម្លៃរត់ទៅយក orders ទាំងនោះ (<span class='en-term'>liquidity</span>) រួចបង្វិលត្រឡប់។ យើងនឹងរៀនរឿងនេះលម្អិតនៅ
Chapter 12 (<span class='en-term'>Liquidity Sweep</span>)។</p>
<table><tr><th></th><th>Breakout ពិត</th><th>False breakout</th></tr>
<tr><td>ទៀនបិទ</td><td>ខាងក្រៅ level</td><td>ខាងក្នុង level វិញ</td></tr>
<tr><td>Wick</td><td>តូច</td><td>វែង ចង្អុលទៅ level</td></tr>
<tr><td>Retest</td><td>Level ការពារបាន</td><td>តម្លៃធ្លាក់ចូលជ្រៅ</td></tr></table>
<div class='box warn'>⚠️ រង់ចាំ<b>ទៀនបិទ</b>ជានិច្ច។ ការទិញពេលទៀនកំពុងឆ្លង level (មុនទៀនបិទ) គឺជាមូលហេតុមួយនៃការជាប់ false breakout។</div>
"""),
        ("កំហុសញឹកញាប់ និងការអនុវត្តនៅ XAU.KH", """
<ul><li>❌ គូរ level ច្រើនពេក រហូតគ្រប់តម្លៃសុទ្ធតែជា "support"</li>
<li>❌ ទិញនៅ support ដោយមិនមើល trend (ក្នុង downtrend ខ្លាំង support បែកញឹកញាប់)</li>
<li>❌ ដាក់ SL ចំលើ level ឬក្នុង zone</li>
<li>❌ ដេញទៀនបែកដោយមិនរង់ចាំទៀនបិទ</li>
<li>❌ ប្រើ level 1m ហើយភ្លេច level 4H ដែលនៅជិត</li></ul>
<div class='box tip'>💡 <b>ការអនុវត្តប្រចាំថ្ងៃ</b>: អានកម្រិត R / Pivot / S ក្នុង Daily Outlook → មើលប្រអប់ DEMAND / SUPPLY លើរូប <b>📊 Analysis</b>
→ ផ្ទៀងផ្ទាត់លើ MT5 → វាយ <b>/check</b> ក្នុង group ដើម្បីមើលស្ថានភាពបច្ចុប្បន្ន។ ពេលមើល <b>📈 Proof</b> សូមសង្កេតថាសញ្ញាជាច្រើនចូលនៅជិត level ទាំងនេះ។</div>
"""),
    ],
    summary=["Support = តំបន់ដែលអ្នកទិញការពារ · Resistance = តំបន់ដែលអ្នកលក់ការពារ",
             "Level ជា <b>តំបន់</b> មិនមែនបន្ទាត់ · SL នៅខាងក្រៅ zone ជានិច្ច",
             "Demand/Supply = តំបន់ដែលតម្លៃរត់ចេញលឿន · Fresh ល្អជាង tested",
             "Breakout ពិតត្រូវ<b>បិទទៀន</b>ឆ្លង level · ឆ្លងតែ wick = false breakout",
             "Level ដែលបែកពិត ច្រើនតែប្ដូរតួនាទី (S ↔ R)"],
    exercise=["បើក chart មាស 4H លើ MT5 ហើយគូរ Support 2 និង Resistance 2 ដែលជិតតម្លៃបច្ចុប្បន្នបំផុត។",
              "ចុះទៅ 15m ហើយរក Demand zone មួយ និង Supply zone មួយ (DBR / RBD)។ តើវា fresh ឬ tested?",
              "រក false breakout មួយក្នុង 5 ថ្ងៃចុងក្រោយ: wick ឆ្លង level ហើយទៀនបិទត្រឡប់ចូលវិញ។",
              "ប្រៀបធៀប level របស់អ្នកជាមួយ R / Pivot / S ក្នុង Daily Outlook ថ្ងៃនេះ។"],
)
