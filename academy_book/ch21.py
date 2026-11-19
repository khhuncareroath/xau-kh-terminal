from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def va_days(days, w=420, h=200, caption="", title_col=BL):
    """Daily value areas as boxes, left to right. days = [(label, val, poc, vah)] in 0-100 (100 = top)."""
    top, bot = 14, h - 26
    Y = lambda v: bot - v * (bot - top) / 100
    n = len(days)
    cw = (w - 30) / n
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    prev = None
    for i, (lab, val, poc, vah) in enumerate(days):
        x = 18 + i * cw
        out.append(f'<rect x="{x + 8:.1f}" y="{Y(vah):.1f}" width="{cw - 16:.1f}" height="{Y(val) - Y(vah):.1f}" rx="6" fill="{title_col}" fill-opacity=".14" stroke="{title_col}" stroke-width="1.2"/>')
        out.append(f'<line x1="{x + 8:.1f}" x2="{x + cw - 8:.1f}" y1="{Y(poc):.1f}" y2="{Y(poc):.1f}" stroke="{GOLD}" stroke-width="2.4"/>')
        out.append(f'<text x="{x + cw / 2:.1f}" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">{lab}</text>')
        if prev:
            out.append(f'<line x1="{prev[0]:.1f}" y1="{Y(prev[1]):.1f}" x2="{x + 8:.1f}" y2="{Y(poc):.1f}" stroke="{GOLD}" stroke-width="1" stroke-dasharray="3 3"/>')
        prev = (x + cw - 8, poc)
    out.append(f'<text x="{w - 12}" y="{top + 8}" text-anchor="end" fill="{GOLD}" class="lt">— POC</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def va_relations(w=420, h=190, caption=""):
    """Today's value area vs yesterday's: higher, lower, inside (overlap), outside (wider)."""
    top, bot = 26, h - 24
    Y = lambda v: bot - v * (bot - top) / 100
    cases = [("Value ខ្ពស់ជាង", (20, 55), (60, 95), UP), ("Value ទាបជាង", (45, 80), (5, 40), DN),
             ("Inside / Overlap", (25, 80), (38, 66), GR), ("Outside (ធំជាង)", (35, 65), (12, 92), OR)]
    cw = (w - 20) / 4
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, y, td, col) in enumerate(cases):
        x = 10 + i * cw
        out.append(f'<text x="{x + cw / 2:.1f}" y="15" text-anchor="middle" fill="{col}" class="st">{t}</text>')
        out.append(f'<rect x="{x + 10:.1f}" y="{Y(y[1]):.1f}" width="{cw / 2 - 14:.1f}" height="{Y(y[0]) - Y(y[1]):.1f}" rx="4" fill="#C7C7CC" fill-opacity=".5" stroke="#AEAEB2"/>')
        out.append(f'<rect x="{x + cw / 2 + 2:.1f}" y="{Y(td[1]):.1f}" width="{cw / 2 - 14:.1f}" height="{Y(td[0]) - Y(td[1]):.1f}" rx="4" fill="{col}" fill-opacity=".18" stroke="{col}" stroke-width="1.4"/>')
        out.append(f'<text x="{x + 10 + (cw / 2 - 14) / 2:.1f}" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">ម្សិល</text>')
        out.append(f'<text x="{x + cw / 2 + 2 + (cw / 2 - 14) / 2:.1f}" y="{h - 8}" text-anchor="middle" fill="{col}" class="st">ថ្ងៃនេះ</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def two_profiles(left, right, lt, rt, w=420, rh=13, caption=""):
    """Two small vertical profiles side by side. left/right = [(volume, colour)] top to bottom."""
    n = max(len(left), len(right))
    h = 36 + n * rh
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for k, (prof, t, x0) in enumerate([(left, lt, 30), (right, rt, w / 2 + 20)]):
        out.append(f'<text x="{x0}" y="16" fill="#1C1C1E" class="bt">{t}</text>')
        vmax = max(v for v, _ in prof)
        for i, (v, col) in enumerate(prof):
            y = 24 + i * rh
            out.append(f'<rect x="{x0}" y="{y:.1f}" width="{max(v / vmax * 140, 2):.1f}" height="{rh - 3}" rx="2.5" fill="{col}"/>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def shapes(w=420, h=170, caption=""):
    """Five profile shapes drawn as small histograms: P, b, D, thin (trend), double distribution."""
    sets = [("P", "buyers", UP, [3, 7, 11, 13, 10, 6, 3, 2, 2, 1, 1, 1]),
            ("b", "sellers", DN, [1, 1, 1, 2, 2, 3, 6, 10, 13, 11, 7, 3]),
            ("D", "balance", BL, [1, 2, 4, 7, 10, 13, 13, 10, 7, 4, 2, 1]),
            ("Thin", "trend", OR, [3, 3, 4, 3, 4, 3, 3, 4, 3, 4, 3, 3]),
            ("Double", "2 តំបន់", PU, [2, 6, 10, 7, 2, 1, 1, 2, 7, 11, 6, 2])]
    cw = (w - 20) / 5
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, sub, col, vs) in enumerate(sets):
        x = 10 + i * cw + 12
        for k, v in enumerate(vs):
            out.append(f'<rect x="{x:.1f}" y="{14 + k * 9}" width="{v * 4.2:.1f}" height="7" rx="2" fill="{col}" fill-opacity=".8"/>')
        out.append(f'<text x="{x + 2:.1f}" y="{h - 22}" fill="{col}" class="pt">{t}</text>')
        out.append(f'<text x="{x + 2:.1f}" y="{h - 8}" fill="{GR}" class="st">{sub}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=21, part="PART 4 · Volume Profile",
    title_km="ការវិភាគ Volume Profile កម្រិតខ្ពស់", title_en="Advanced Volume Profile: Acceptance · Migration · Poor Highs · Shapes",
    intro="""Chapter 19 បង្រៀនពាក្យ (POC, VAH, VAL, HVN, LVN) ហើយ Chapter 20 បង្រៀនថាត្រូវប្រើ profile <b>ប្រភេទណា</b>។
ជំពូកនេះបង្រៀនរបៀប<b>អាន</b> profile ដូចអ្នកជំនាញ: តើតម្លៃត្រូវបាន<b>ទទួលយក</b> ឬ<b>បដិសេធ</b>? តើ value កំពុង<b>ផ្លាស់ទី</b>ទៅណា?
តើកំពូល ឬបាតមួយ "<b>មិនទាន់បញ្ចប់</b>" ទេ? ហើយ<b>រាង</b> profile ប្រាប់អ្វី និង<b>មិនប្រាប់</b>អ្វី។
ចុងក្រោយ យើងនឹងភ្ជាប់ Volume Profile ជាមួយ <span class='en-term'>market structure</span> ដែលអ្នកបានរៀនក្នុង Part 2 និង Part 3។""",
    sections=[
        ("Acceptance និង Rejection", """
<p>នេះជាគំនិតសំខាន់បំផុតក្នុង Volume Profile។ ពេលតម្លៃចេញពី Value Area (ឬឆ្លងកម្រិតសំខាន់មួយ) មានតែពីរលទ្ធផល:</p>
<ul><li><span class='en-term'>Acceptance</span> (ទទួលយក) = តម្លៃ<b>នៅ</b>ក្រៅ ហើយ volume <b>ចាប់ផ្ដើមកកកុញ</b>នៅទីនោះ · value ថ្មីកំពុងកើត</li>
<li><span class='en-term'>Rejection</span> (បដិសេធ) = តម្លៃចេញទៅ ប៉ុន្តែ<b>ត្រឡប់ចូលវិញលឿន</b> · volume តិចនៅខាងក្រៅ · ទុកតែ wick វែង</li></ul>
""" + zigzag([40, 60, 52, 74, 66, 80, 72, 86],
             {3: ("បិទលើ VAH", UP), 4: ("retest", BL), 5: ("កាន់បាន", UP)},
             lines=[(62, 0, 7, "VAH", BL, True), (40, 0, 7, "POC", GOLD, False)],
             caption="Acceptance: បិទលើ VAH → retest ពីខាងលើ ហើយកាន់បាន → value ថ្មីខ្ពស់ជាង") + zigzag([40, 56, 48, 82, 58, 50, 54, 40],
             {3: ("wick លើ VAH", DN), 5: ("ត្រឡប់ចូល", DN)},
             lines=[(62, 0, 7, "VAH", BL, True), (32, 0, 7, "POC", GOLD, False)],
             caption="Rejection: ឆ្លង VAH លឿន ប៉ុន្តែគ្មាន volume កកកុញ → ត្រឡប់ចូល Value Area → ច្រើនតែទៅ POC") + """
<table><tr><th>សញ្ញា</th><th>Acceptance</th><th>Rejection</th></tr>
<tr><td>ពេលវេលានៅក្រៅ</td><td>យូរ (ច្រើនទៀន 15m/30m)</td><td>ខ្លី (1-2 ទៀន)</td></tr>
<tr><td>ការបិទទៀន</td><td>បិទក្រៅ ហើយបន្តបិទក្រៅ</td><td>wick ក្រៅ · body បិទត្រឡប់ចូល</td></tr>
<tr><td>Retest</td><td>កម្រិតចាស់ក្លាយជា S/R ថ្មី</td><td>គ្មាន retest · ត្រឡប់ចូលលឿន</td></tr>
<tr><td>Developing POC</td><td>dPOC ផ្លាស់ទៅតាម (Chapter 20)</td><td>dPOC នៅនឹងកន្លែង</td></tr></table>
<div class='box tip'>💡 គំនិតនេះស្រដៀងនឹង <b>retest</b> និង <b>rejection</b> ក្នុង Price Action (Chapter 10) និង <b>sweep</b> ក្នុង Liquidity (Chapter 12)។
Rejection ពី VAH ច្រើនតែជា sweep នៃ buy-side liquidity ដែលនៅលើ value area។</div>
"""),
        ("Volume Migration: Value ផ្លាស់ទី", """
<p><span class='en-term'>Volume migration</span> (ឬ <span class='en-term'>value migration</span>) = ទីតាំង POC និង Value Area <b>ផ្លាស់ទីពីថ្ងៃមួយ (ឬ session មួយ) ទៅមួយទៀត</b>។
វាប្រាប់ទិសដៅនៃ<b>ការទទួលយក</b> មិនមែនត្រឹមតែទិសដៅនៃតម្លៃទេ។</p>
""" + va_days([("ច័ន្ទ", 14, 24, 34), ("អង្គារ", 26, 36, 46), ("ពុធ", 36, 48, 56), ("ព្រហស្បតិ៍", 50, 60, 70), ("សុក្រ", 62, 74, 84)],
              caption="Value migration ឡើង: Value Area និង POC ខ្ពស់ជាងមុនរាល់ថ្ងៃ = buyers កំពុងរុញ value ឡើង (uptrend ដែលត្រូវបានទទួលយក)") + """
<ul><li>POC ឡើងរាល់ថ្ងៃ = <b>uptrend</b> ដែលមាន volume គាំទ្រ · pullback ទៅ POC / VAH នៃថ្ងៃមុនច្រើនតែត្រូវបានគេទិញ</li>
<li>POC ចុះរាល់ថ្ងៃ = <b>downtrend</b> ដែលមាន volume គាំទ្រ</li>
<li>តម្លៃឡើងខ្ពស់ ប៉ុន្តែ POC <b>មិនផ្លាស់</b> = ចលនាឡើងមិនទាន់ត្រូវបានទទួលយក · ប្រុងប្រយ័ត្ន</li>
<li>POC នៅកន្លែងដដែលច្រើនថ្ងៃ = <b>balance</b> (range) · រង់ចាំ breakout ដែលមាន acceptance</li></ul>
"""),
        ("Value Area Shifts: ប្រៀបធៀបថ្ងៃនេះជាមួយម្សិលមិញ", """
<p>មធ្យោបាយសាមញ្ញមួយ: ប្រៀបធៀប <b>Value Area ថ្ងៃនេះ</b> ជាមួយ <b>Value Area ម្សិលមិញ</b>។ មាន 4 ករណីចម្បង:</p>
""" + va_relations(caption="ប្រផេះ = Value Area ម្សិលមិញ · ពណ៌ = Value Area ថ្ងៃនេះ") + """
<table><tr><th>ករណី</th><th>អត្ថន័យដែលអាចកើត</th></tr>
<tr><td><b>Value ខ្ពស់ជាង</b> (VAL ថ្ងៃនេះ ≥ VAH ម្សិល ឬជិត)</td><td>Buyers គ្រប់គ្រង · bias ឡើង</td></tr>
<tr><td><b>Value ទាបជាង</b></td><td>Sellers គ្រប់គ្រង · bias ចុះ</td></tr>
<tr><td><b>Inside / Overlap</b> (នៅក្នុង VA ម្សិល)</td><td>Balance · ទីផ្សាររង់ចាំ · ច្រើនតែមុន news ធំ ឬមុន breakout</td></tr>
<tr><td><b>Outside</b> (ធំជាងទាំងសងខាង)</td><td>ថ្ងៃប្រែប្រួលខ្លាំង · ភាគីទាំងពីរសកម្ម · ច្រើនកើតនៅថ្ងៃ news (📰 News)</td></tr></table>
<div class='box warn'>⚠️ ការប្រៀបធៀបនេះធ្វើបានពេញលេញតែ<b>ក្រោយ</b>ថ្ងៃបិទ។ ក្នុងថ្ងៃ អ្នកអាចប្រៀបធៀប <b>developing</b> Value Area
ប៉ុន្តែវាអាចប្ដូររហូតដល់ session New York បិទ។</div>
"""),
        ("Poor Highs និង Poor Lows", """
<p>កំពូល ឬបាតដែល "<b>ល្អ</b>" (បញ្ចប់រួច) ច្រើនមាន<b>កន្ទុយ volume តូច</b> (<span class='en-term'>excess</span>): តម្លៃប៉ះកំពូល ហើយត្រូវបានច្រានចេញលឿន
ដូច្នេះមាន volume តិចណាស់នៅចុងកំពូល។ ផ្ទុយទៅវិញ <span class='en-term'>poor high</span> / <span class='en-term'>poor low</span> = កំពូល/បាតដែល
<b>រាបស្មើ</b> មាន volume <b>ក្រាស់</b>រហូតដល់ចុង ហាក់ដូចជាទីផ្សារ "ឈប់ពាក់កណ្ដាលផ្លូវ"។</p>
""" + two_profiles([(1, GR), (2, GR), (4, BL), (8, BL), (12, BL), (14, GOLD), (10, BL), (6, BL), (3, GR)],
                   [(9, DN), (11, DN), (10, BL), (12, BL), (14, GOLD), (10, BL), (6, BL), (3, GR), (2, GR)],
                   "កំពូលល្អ: មាន excess (កន្ទុយតូច)", "Poor high: volume ក្រាស់ដល់ចុង",
                   caption="ឆ្វេង: volume ស្ដើងនៅចុងកំពូល = rejection ច្បាស់ · ស្ដាំ: volume ក្រាស់នៅចុង = កំពូលមិនទាន់បញ្ចប់") + """
""" + zigzag([30, 60, 48, 72, 58, 72, 56, 71, 50, 40],
             {3: ("high", DN), 5: ("high", DN)},
             lines=[(72, 2, 9, "poor high = BSL", DN, True)],
             caption="Poor high លើ chart: កំពូលរាបស្មើច្រើនដង (equal highs) = buy-side liquidity ដែលនៅរង់ចាំ (Chapter 12)") + """
<ul><li>អ្នក trade ជាច្រើនចាត់ទុក poor high/low ជា "<b>អាជីវកម្មមិនទាន់បញ្ចប់</b>" (<span class='en-term'>unfinished business</span>) ហើយរំពឹងថាតម្លៃនឹងត្រឡប់មកយកវិញ</li>
<li>វាត្រូវនឹងគំនិត <b>equal highs / equal lows</b> ក្នុង ICT: stop orders ប្រមូលផ្ដុំនៅលើ/ក្រោម ដូច្នេះជា<b>គោលដៅ</b>ល្អ</li>
<li>វា<b>មិនមែន</b>ការធានាទេ: poor high អាចនៅដដែលច្រើនថ្ងៃ ឬច្រើនសប្ដាហ៍ ពេល trend ប្ដូរ</li></ul>
<div class='box tip'>💡 ប្រើ poor high/low ជា<b>គោលដៅ</b> (TP) ច្រើនជាងជាកន្លែង entry។ កុំដាក់ SL ពីលើ poor high ដោយផ្ទាល់ ព្រោះវាជាកន្លែងដែលតម្លៃច្រើនត្រូវបានទាញទៅ។</div>
"""),
        ("Single Prints", """
<p><span class='en-term'>Single prints</span> មកពី Market Profile (TPO): ជាតម្លៃដែលត្រូវបានជួញដូរក្នុង<b>រយៈពេល 30 នាទីតែមួយ</b>ប៉ុណ្ណោះ
ពោលគឺតម្លៃរត់ឆ្លងលឿនណាស់។ ក្នុង Volume Profile យើងឃើញវាជា<b>តំបន់ស្ដើងខ្លាំង</b> (LVN តូចចង្អៀត) ដែលបង្កើតដោយចលនាមួយទិសលឿន។</p>
""" + two_profiles([(12, BL), (14, GOLD), (10, BL), (2, DN), (1, DN), (1, DN), (2, DN), (9, BL), (13, BL), (8, BL)],
                   [(3, GR), (6, BL), (10, BL), (12, BL), (14, GOLD), (12, BL), (9, BL), (6, BL), (3, GR), (2, GR)],
                   "មាន single prints (តំបន់ស្ដើង)", "Profile ធម្មតា (គ្មាន)",
                   caption="ក្រហម = single prints: តម្លៃរត់ឆ្លងតែម្ដង ស្ទើរគ្មាន volume · ជារឿយៗជា FVG លើ chart") + """
<ul><li>Single prints ច្រើន<b>ត្រូវនឹង FVG / displacement</b> (Chapter 13): ពីរឧបករណ៍ខុសគ្នា មើលឃើញរឿងដូចគ្នា</li>
<li>អ្នក trade ជាច្រើនរំពឹងថាតម្លៃនឹង<b>ត្រឡប់មកបំពេញ</b> (fill) តំបន់នេះនៅពេលណាមួយ · ប៉ុន្តែពេលវេលាមិនច្បាស់ទេ</li>
<li>ពេលតម្លៃត្រឡប់មក single prints ក្នុង<b>ទិសដៅ trend</b> វាអាចដើរតួជា support/resistance (ដូច FVG ដែលកាន់បាន)</li>
<li>បើ single prints ត្រូវបានបំពេញទាំងស្រុង ហើយតម្លៃឆ្លងហួស = ចលនាដើមកំពុងខ្សោយ</li></ul>
"""),
        ("Low-Volume Rejection", """
<p><span class='en-term'>Low-volume rejection</span> = តម្លៃត្រឡប់មក LVN (ឬ single prints) ហើយ<b>ត្រូវបានច្រានចេញភ្លាម</b> ដោយមិនអាចកសាង volume នៅទីនោះ។
វាបង្ហាញថាតម្លៃនៅទីនោះ "<b>មិនត្រូវបានទទួលយក</b>" ម្ដងទៀត។</p>
""" + zigzag([30, 46, 74, 82, 76, 84, 70, 56, 66, 80, 90],
             {7: ("ប៉ះ LVN", BL), 9: ("ច្រានចេញ ↑", UP)},
             lines=[(56, 0, 10, "LVN", DN, True), (80, 2, 6, "HVN", GOLD, False)],
             caption="Impulse ឡើងបង្កើត LVN · pullback មកប៉ះ LVN · ទៀនច្រានចេញលឿន = low-volume rejection · តម្លៃបន្តឡើង") + """
<p><b>របៀបមើល:</b></p>
<ol><li>រក LVN ដែលបង្កើតដោយ impulse ក្នុងទិសដៅ structure (ប្រើ Fixed Range: Chapter 20)</li>
<li>រង់ចាំតម្លៃ pullback មក LVN</li>
<li>មើលការ<b>ច្រានចេញ</b>: wick វែង · ទៀន 15m បិទត្រឡប់ចេញពី LVN · មិនមានទៀនបិទក្នុង LVN ច្រើនគ្រាប់</li>
<li>បើតម្លៃ<b>ចូលកកកុញ</b>ក្នុង LVN (ច្រើនទៀនបិទនៅទីនោះ) = LVN កំពុងក្លាយជា value ថ្មី · rejection បរាជ័យ</li></ol>
<div class='box warn'>⚠️ LVN មានពីរមុខ: វាអាច<b>ច្រានចេញ</b> (rejection) ឬតម្លៃអាច<b>រត់ឆ្លងលឿន</b>ទៅ HVN បន្ទាប់ (Chapter 19)។
អ្នកមិនដឹងមុនទេថាមួយណា។ ដូច្នេះត្រូវរង់ចាំការបញ្ជាក់ ហើយ SL ត្រូវនៅ<b>ម្ខាងទៀតនៃ LVN</b>។</div>
"""),
        ("រាង Profile និងដែនកំណត់របស់វា", """
<p>រាង profile ប្រាប់ពីរបៀបដែល volume ចែកចាយក្នុងរយៈពេលមួយ (ឧ. session មុន):</p>
""" + shapes(caption="P = volume នៅខាងលើ · b = volume នៅខាងក្រោម · D = តុល្យភាព · Thin = trend លឿន · Double = តំបន់ value ពីរ") + """
<table><tr><th>រាង</th><th>ការអានទូទៅ</th><th>ប្រយ័ត្ន</th></tr>
<tr><td><b>P</b></td><td>Buyers គ្រប់គ្រង · តម្លៃឡើងហើយទទួលយកនៅខាងលើ</td><td>ក្នុង downtrend អាចជា short covering តែប៉ុណ្ណោះ</td></tr>
<tr><td><b>b</b></td><td>Sellers គ្រប់គ្រង · តម្លៃធ្លាក់ហើយទទួលយកនៅខាងក្រោម</td><td>ក្នុង uptrend អាចជាការលក់យកចំណេញ (long liquidation)</td></tr>
<tr><td><b>D</b></td><td>Balance · range</td><td>ងាយ breakout ពេល news</td></tr>
<tr><td><b>Thin</b></td><td>Trend មួយទិសលឿន · value មិនទាន់កកកុញ</td><td>ច្រើនទុក single prints</td></tr>
<tr><td><b>Double</b></td><td>Value ពីរកន្លែង បំបែកដោយ LVN</td><td>LVN កណ្ដាលជាកម្រិតសំខាន់</td></tr></table>
<p><b>អ្វីដែលការសាកល្បងរបស់ XAU.KH បានរកឃើញ</b> (ទិន្នន័យមាស 2 ឆ្នាំ · លទ្ធផលអតីតកាល មិនធានាអនាគត):</p>
<ul><li>Trade តាមរាង <b>P/b</b> ទាំងអស់ (pullback ទៅ POC នៃ session មុន): ចំណេញតិចណាស់ ហើយ<b>មិនទាន់ត្រូវបានបញ្ជាក់</b>ជាស្ថិតិ</li>
<li>Trade តាមរាង <b>D</b> (លក់ VAH ទិញ VAL): <b>ខាត</b>ក្នុងការសាកល្បង · ដូច្នេះប្រព័ន្ធមិនប្រើ</li>
<li>ពេលថ្ងៃបានរត់ <b>70%+</b> នៃថ្ងៃធម្មតារួចហើយ (📏 Day Meter): 83 trades · ឈ្នះ 39% · <b>−0.10R</b> = ខាត · ផ្ញើតែជាការព្រមាន ⚠️</li>
<li>P/b ដែល <b>4H មិនទាន់បង្វិល</b>ទិសដូចគ្នា (model 📊 Volume): 122 trades · ឈ្នះ 48% · <b>+0.26R</b></li></ul>
<div class='box warn'>⚠️ <b>ដែនកំណត់នៃរាង:</b> (1) រាងអាស្រ័យលើ<b>ចន្លោះពេល</b> (Chapter 20): ប្ដូរចន្លោះ រាងប្ដូរ ·
(2) Tick volume របស់ broker ខុសពី futures volume (Chapter 18) · (3) រាងប្រាប់ពី<b>អតីតកាល</b> (session មុន) មិនមែនអនាគត ·
(4) ឈ្នះ 48% មានន័យថាខាតជិតពាក់កណ្ដាល · មើល 📈 <b>Proof</b> សម្រាប់លទ្ធផល live ពិត។</div>
"""),
        ("ប្រើ Volume Profile ជាមួយ Market Structure", """
<p>Volume Profile ល្អបំផុតពេលប្រើជា<b>ទីតាំង</b> (location) ខណៈ market structure ផ្ដល់<b>ទិសដៅ</b> (direction) និង<b>ការបញ្ជាក់</b> (trigger)។</p>
""" + flow([("Bias", "4H · Daily", PU), ("Value", "migration", BL), ("Location", "POC · VAL · LVN", GOLD),
            ("Confluence", "OB · FVG", OR), ("Trigger", "15m MSS / close", UP), ("Risk", "SL ក្រៅ VA · RR", DN)],
           caption="លំដាប់គិត: ទិសដៅ → value → ទីតាំង → confluence → ការបញ្ជាក់ → ហានិភ័យ") + """
<table style="break-inside: avoid"><tr><th>Structure (Part 2–3)</th><th>Volume Profile</th><th>រួមគ្នា</th></tr>
<tr><td>FVG / displacement</td><td>LVN · single prints</td><td>តំបន់ដែលតម្លៃរត់ឆ្លងលឿន</td></tr>
<tr><td>Order Block</td><td>HVN · POC</td><td>OB ក្បែរ POC = តំបន់ខ្លាំងជាង</td></tr>
<tr><td>Equal highs / lows (liquidity)</td><td>Poor high / poor low</td><td>គោលដៅ (TP) ល្អ</td></tr>
<tr><td>Premium / Discount</td><td>លើ / ក្រោម POC</td><td>ទិញក្រោម POC ក្នុង uptrend</td></tr>
<tr><td>BOS / MSS</td><td>Acceptance / rejection</td><td>ការបញ្ជាក់ថាកម្រិតត្រូវបានទទួលយក ឬបដិសេធ</td></tr></table>
<div class='box ok'>✅ <b>ឧទាហរណ៍សម្រាប់រៀន:</b> Session London មានរាង <b>P</b> · POC <b>4,128</b> · VAL <b>4,121</b>។ ក្នុង New York តម្លៃ pullback មក 4,128
ដែលក៏ជា bullish FVG ក្នុង 15m។ ទៀន 15m បិទត្រឡប់លើ POC → entry <b>4,129.50</b> · SL ក្រោម VAL <b>4,120.00</b> = $9.50 = <b>95 pips</b> ·
TP 2R = <b>4,148.50</b> (190 pips)។ ជាមួយ <b>0.01 lot</b>: ហានិភ័យ $9.50 · គោលដៅ $19។ មុន entry: ពិនិត្យ 📰 News និង Day Meter។</div>
"""),
        ("Checklist និងកំហុសញឹកញាប់", """
<p><b>Checklist មុនប្រើ Volume Profile ក្នុង trade មួយ:</b></p>
<ol><li>Profile នេះជាប្រភេទណា ហើយគ្របរយៈពេលប៉ុន្មាន? (Chapter 20)</li>
<li>Value កំពុងផ្លាស់ទីទៅណា? (ឡើង · ចុះ · នៅនឹង)</li>
<li>តម្លៃនៅក្នុង ឬក្រៅ Value Area? មាន acceptance ឬ rejection?</li>
<li>មាន poor high/low ឬ single prints ដែលអាចជាគោលដៅទេ?</li>
<li>Structure (BOS / MSS / OB / FVG) យល់ស្របជាមួយកម្រិត profile ទេ?</li>
<li>SL នៅកន្លែងដែល idea ខុស (ក្រៅ VA / ម្ខាងទៀតនៃ LVN) ហើយ RR ≥ 1:2?</li></ol>
<div class='box warn'>⚠️ <b>កំហុសញឹកញាប់:</b><br>
❌ ហៅរាល់ wick ថា "rejection" ដោយមិនរង់ចាំទៀនបិទ<br>
❌ ទិញព្រោះ "រាង P" ទោះថ្ងៃបានរត់ 70%+ រួចហើយ<br>
❌ ចាត់ទុក poor high ជាការធានាថាតម្លៃនឹងឡើងទៅយក<br>
❌ Trade រាង D (លក់ VAH / ទិញ VAL) ដោយមិនដឹងថាវាខាតក្នុងការសាកល្បង<br>
❌ មើល profile តែឯង ហើយភ្លេច structure, news និង risk</div>
<div class='box tip'>💡 មើល Volume Profile ជារៀងរាល់ថ្ងៃលើរូប 📊 <b>Analysis</b> និង <b>/check</b> · signal ដែលប្រើ profile មានស្លាក 📊 <b>Volume</b> ក្នុង 🚨 Signals
ហើយលទ្ធផលពិតរបស់វាត្រូវបានកត់ត្រាក្នុង 📈 <b>Proof</b>។</div>
"""),
    ],
    summary=["<b>Acceptance</b> = នៅក្រៅ ហើយ volume កកកុញ · <b>Rejection</b> = ចេញទៅ ហើយត្រឡប់ចូលលឿន (wick)",
             "<b>Volume migration</b>: POC / Value Area ឡើងរាល់ថ្ងៃ = uptrend ដែលត្រូវបានទទួលយក · ប្រៀបធៀប VA ថ្ងៃនេះ vs ម្សិលមិញ",
             "<b>Poor high/low</b> = កំពូល/បាតរាបស្មើ volume ក្រាស់ · <b>Single prints</b> = តំបន់ស្ដើង (ច្រើនជា FVG) · ជាគោលដៅ មិនមែនការធានា",
             "<b>Low-volume rejection</b> = ប៉ះ LVN ហើយច្រានចេញ · LVN អាចរត់ឆ្លងបានដែរ · SL ម្ខាងទៀតនៃ LVN",
             "រាង <b>P / b / D</b> មានដែនកំណត់ · VP = ទីតាំង · Structure = ទិសដៅ និងការបញ្ជាក់ · ប្រើរួមគ្នាជានិច្ច"],
    exercise=["ក្នុងឧទាហរណ៍ section 8 បើ SL ដាក់ក្រោម VAL ត្រឹម $1 (4,120.00) តែ entry 4,131.00 វិញ: ហានិភ័យប៉ុន្មាន pips ហើយ TP 2R នៅតម្លៃណា? ជាមួយ 0.02 lot ហានិភ័យប៉ុន្មាន $?",
              "កត់ត្រា POC នៃថ្ងៃនីមួយៗរយៈពេល 5 ថ្ងៃ (ពីរូប 📊 Analysis ឬ MT5)។ Value កំពុង migrate ឡើង ចុះ ឬនៅនឹង?",
              "រក poor high ឬ equal highs មួយលើ chart 1H។ តើតម្លៃបានត្រឡប់មកយកវាទេ? ក្រោយប៉ុន្មានថ្ងៃ?",
              "ពេល signal 📊 Volume ចេញក្នុង 🚨 Signals អានហេតុផលក្នុង 🧠 Setup Analysis ហើយសរសេរថា: រាង profile ជាអ្វី · POC នៅឯណា · 4H កំពុងទៅទិសណា។"],
)
