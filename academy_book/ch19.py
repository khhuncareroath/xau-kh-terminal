from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"

# Teaching example (not real data): volume at each $5 price row, total = 100 -> numbers read as %.
ROWS = [(4150, 2), (4145, 3), (4140, 8), (4135, 14), (4130, 22), (4125, 16), (4120, 10), (4115, 3), (4110, 12), (4105, 7), (4100, 3)]


def profile(rows, poc=None, va=None, marks=None, w=420, h=None, caption=""):
    """Horizontal volume-at-price histogram. rows = [(price, volume)] top to bottom.
    poc = price of the POC row · va = (val, vah) shades the value area · marks = {price: (text, colour)} on the right."""
    marks = marks or {}
    n = len(rows)
    rh = 17
    h = h or 24 + n * rh
    vmax = max(v for _, v in rows)
    x0, wmax = 68, 190
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    if va:
        ys = [12 + i * rh for i, (p, _) in enumerate(rows) if va[0] <= p <= va[1]]
        out.append(f'<rect x="8" y="{min(ys) - 1}" width="{w - 16}" height="{max(ys) - min(ys) + rh + 2}" rx="6" fill="{BL}" fill-opacity=".07"/>')
    for i, (p, v) in enumerate(rows):
        y = 12 + i * rh
        inva = va and va[0] <= p <= va[1]
        col = GOLD if p == poc else (BL if inva else "#AEAEB2")
        out.append(f'<text x="{x0 - 8}" y="{y + 12}" text-anchor="end" fill="#3A3A3C" class="lt">{p:,}</text>')
        out.append(f'<rect x="{x0}" y="{y + 2}" width="{max(v / vmax * wmax, 2):.1f}" height="{rh - 4}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{x0 + v / vmax * wmax + 5:.1f}" y="{y + 12}" fill="{GR}" class="st">{v}</text>')
        if p in marks:
            t, mc = marks[p]
            out.append(f'<text x="{w - 14}" y="{y + 12}" text-anchor="end" fill="{mc}" class="lt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def time_vs_price(w=420, h=200, caption=""):
    """Left: a few candles over time. Right: the same activity stacked sideways by price = the profile."""
    top, bot = 16, h - 26
    Y = lambda v: bot - v * (bot - top) / 100
    data = [(30, 46, 24, 42), (42, 58, 40, 52), (52, 56, 44, 48), (48, 54, 42, 50), (50, 60, 46, 54), (54, 66, 50, 52), (52, 56, 44, 50), (50, 74, 48, 70)]
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (o, hi, lo, c) in enumerate(data):
        cx = 26 + i * 26
        col = UP if c >= o else DN
        out.append(f'<line x1="{cx}" x2="{cx}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.5"/>')
        out.append(f'<rect x="{cx - 7}" y="{Y(max(o, c)):.1f}" width="14" height="{max(Y(min(o, c)) - Y(max(o, c)), 1.5):.1f}" rx="1.5" fill="{col}"/>')
    out.append(f'<text x="120" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">ពេលវេលា (time) →</text>')
    out.append(f'<path d="M232,{h / 2:.0f} l26,0 m-6,-5 l6,5 l-6,5" stroke="#8E8E93" stroke-width="1.8" fill="none"/>')
    prof = [(74, 2), (68, 4), (62, 8), (56, 14), (50, 22), (44, 14), (38, 7), (32, 4), (26, 2)]
    for v, q in prof:
        col = GOLD if q == 22 else BL
        out.append(f'<rect x="272" y="{Y(v) - 7:.1f}" width="{q * 5}" height="12" rx="3" fill="{col}" fill-opacity="{1 if q == 22 else .75}"/>')
    out.append(f'<text x="{272 + 22 * 5 + 6}" y="{Y(50) + 3:.1f}" fill="{GOLD}" class="lt">POC</text>')
    out.append(f'<text x="330" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">volume តាមតម្លៃ (price)</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


def chart_with_profile(w=420, h=210, caption=""):
    """A price path with the profile drawn on the right edge, the way the 📊 Analysis picture shows it."""
    top, bot = 14, h - 16
    Y = lambda v: bot - v * (bot - top) / 100
    pts = [62, 70, 58, 66, 52, 60, 46, 56, 50, 30, 44, 54, 48, 58, 52, 64, 56, 60]
    X = lambda i: 16 + i * 236 / (len(pts) - 1)
    prof = {90: 2, 84: 3, 78: 5, 72: 9, 66: 14, 60: 18, 54: 24, 48: 16, 42: 7, 36: 3, 30: 2, 24: 1}
    vah, val, poc = 68, 46, 54
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="10" y="{Y(vah) - 3:.1f}" width="{w - 20}" height="{Y(val) - Y(vah) + 6:.1f}" fill="{BL}" fill-opacity=".07"/>']
    for v, q in prof.items():
        inva = val <= v <= vah
        bw = q * 4.2
        out.append(f'<rect x="{w - 12 - bw:.1f}" y="{Y(v) - 4.5:.1f}" width="{bw:.1f}" height="9" rx="2" fill="{BL if inva else "#C7C7CC"}" fill-opacity="{.55 if inva else .8}"/>')
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<line x1="10" x2="{w - 10}" y1="{Y(poc):.1f}" y2="{Y(poc):.1f}" stroke="{GOLD}" stroke-width="1.6"/>')
    for v, t, col in [(vah, "VAH", BL), (poc, "POC", GOLD), (val, "VAL", BL)]:
        out.append(f'<text x="262" y="{Y(v) + (-4 if t == "POC" else 4):.1f}" fill="{col}" class="lt">{t}</text>')
    out.append(f'<text x="{X(9):.1f}" y="{Y(30) + 15:.1f}" text-anchor="middle" fill="{DN}" class="st">LVN: wick លឿន</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=19, part="PART 4 · Volume Profile",
    title_km="មូលដ្ឋាន Volume Profile", title_en="Volume Profile Fundamentals: POC · VAH · VAL · HVN · LVN",
    intro="""ក្នុង Chapter 18 យើងបានឃើញ volume ជា bar <b>បញ្ឈរ</b> ក្រោម chart: volume តាម<b>ពេលវេលា</b>។
<span class='en-term'>Volume Profile</span> បង្វិលគំនិតនេះ 90 ដឺក្រេ: វាបង្ហាញ volume ជា bar <b>ផ្ដេក</b> តាម<b>កម្រិតតម្លៃ</b>។
ជំនួសឱ្យការសួរថា "ម៉ោងណាមានការជួញដូរច្រើន?" យើងសួរថា "<b>តម្លៃណា</b>មានការជួញដូរច្រើន?"
ជំពូកនេះបង្រៀនពាក្យគន្លឹះទាំងអស់: <span class='en-term'>POC</span>, <span class='en-term'>Value Area</span>, <span class='en-term'>VAH</span>,
<span class='en-term'>VAL</span>, <span class='en-term'>HVN</span> និង <span class='en-term'>LVN</span> ដែលអ្នកនឹងឃើញលើរូប 📊 Analysis របស់ XAU.KH។""",
    sections=[
        ("Volume Profile បង្ហាញអ្វី?", """
<p>Volume Profile យក volume នៃទៀនទាំងអស់ក្នុងរយៈពេលមួយ (ឧ. មួយថ្ងៃ ឬ 5 ថ្ងៃ) ហើយ<b>បូកបញ្ចូលគ្នាតាមកម្រិតតម្លៃ</b>។
លទ្ធផលគឺជា histogram ផ្ដេកមួយ: bar វែង = តម្លៃដែលមានការជួញដូរច្រើន · bar ខ្លី = តម្លៃដែលមានការជួញដូរតិច។</p>
""" + time_vs_price(caption="ឆ្វេង: ទៀនតាមពេលវេលា · ស្ដាំ: volume ដូចគ្នា ប៉ុន្តែរៀបតាមកម្រិតតម្លៃ = Volume Profile") + """
<ul><li>តម្លៃដែលមាន volume ច្រើន = ទីផ្សារ<b>ទទួលយក</b> (<span class='en-term'>acceptance</span>) · អ្នកទិញ និងអ្នកលក់យល់ព្រមថាតម្លៃនេះ "សមរម្យ"</li>
<li>តម្លៃដែលមាន volume តិច = ទីផ្សារ<b>បដិសេធ</b> (<span class='en-term'>rejection</span>) ឬគ្រាន់តែរត់ឆ្លងកាត់លឿនៗ</li></ul>
<div class='box tip'>💡 គំនិតនេះមានដើមកំណើតពី <span class='en-term'>Market Profile</span> របស់ J. Peter Steidlmayer នៅ Chicago Board of Trade (ទសវត្សរ៍ 1980)។
Volume Profile ប្រើគោលការណ៍ដូចគ្នា ប៉ុន្តែវាស់ដោយ <b>volume</b> ជំនួសឱ្យ<b>ពេលវេលា</b>។</div>
<div class='box warn'>⚠️ សម្រាប់មាស ចងចាំ Chapter 18: profile ដែលសាងសង់ពី <b>tick volume</b> របស់ broker ឬពី <b>futures volume</b> មិនដូចគ្នាទេ។
កម្រិតអាចខុសគ្នាបន្តិចតាមប្រភពទិន្នន័យ។ ចាត់ទុកវាជា<b>តំបន់</b> មិនមែនលេខពិតប្រាកដរហូតដល់សេន។</div>
"""),
        ("Point of Control (POC)", """
<p><span class='en-term'>POC (Point of Control)</span> គឺជា<b>កម្រិតតម្លៃតែមួយ</b>ដែលមាន volume <b>ច្រើនបំផុត</b>ក្នុង profile។
វាជាតម្លៃដែលទីផ្សារចំណាយពេល និងលុយច្រើនបំផុត ហើយច្រើនតែត្រូវបានហៅថា "<b>តម្លៃយុត្តិធម៌</b>" (<span class='en-term'>fair price</span>) នៃរយៈពេលនោះ។</p>
<p>ឧទាហរណ៍សម្រាប់រៀន: volume នៃមួយថ្ងៃ (សរុប = 100 ដើម្បីងាយអានជា %) តាមជួរតម្លៃ $5:</p>
""" + profile(ROWS, poc=4130, marks={4130: ("POC 4,130", GOLD)},
              caption="POC = bar វែងបំផុត = 4,130 (22% នៃ volume ថ្ងៃនោះ) · ឧទាហរណ៍សម្រាប់រៀន មិនមែនទិន្នន័យពិត") + """
<ul><li>តម្លៃច្រើនតែ<b>ត្រូវបានទាញត្រឡប់</b>មក POC វិញ ពេលទីផ្សារនៅក្នុង range (គ្មាននិន្នាការច្បាស់)</li>
<li>POC នៃថ្ងៃមុនដែលតម្លៃមិនទាន់ត្រឡប់មកប៉ះ ហៅថា <span class='en-term'>naked POC</span> (ឬ virgin POC) · អ្នក trade ខ្លះប្រើវាជាគោលដៅ</li>
<li>POC <b>មិនមែន</b>ជាជញ្ជាំងទេ: ក្នុងនិន្នាការខ្លាំង តម្លៃអាចរត់ចេញពី POC ហើយមិនត្រឡប់មកវិញច្រើនថ្ងៃ</li></ul>
"""),
        ("Value Area: តំបន់ 70%", """
<p><span class='en-term'>Value Area (VA)</span> គឺជាចន្លោះតម្លៃជុំវិញ POC ដែលមានប្រហែល <b>70%</b> នៃ volume សរុប។
70% ជា<b>ទម្លាប់ស្តង់ដារ</b> (convention) ដែលមកពី Market Profile ហើយ platform ភាគច្រើនប្រើតាម។ វាជាតំបន់ដែលទីផ្សារ "ទទួលយក" ច្រើនបំផុត។</p>
<p><b>របៀបគណនា</b> (វិធីទូទៅ ដែលកូដ <span class='en-term'>levels.py</span> របស់ XAU.KH ក៏ប្រើដែរ):</p>
""" + flow([("ចាប់ផ្ដើម POC", "22%", GOLD), ("មើលជួរលើ/ក្រោម", "ប្រៀបធៀប", BL), ("បន្ថែមជួរធំជាង", "ម្ដងមួយជួរ", BL), ("ឈប់ពេល ≥70%", "VAH · VAL", UP)],
           caption="ពង្រីកពី POC ទៅជួរដែលមាន volume ច្រើនជាង (លើ ឬក្រោម) រហូតដល់បាន 70%") + """
<table><tr><th>ជំហាន</th><th>ជួរលើ</th><th>ជួរក្រោម</th><th>បន្ថែម</th><th>សរុប</th></tr>
<tr><td>0</td><td>–</td><td>–</td><td>POC 4,130</td><td>22%</td></tr>
<tr><td>1</td><td>4,135 (14)</td><td>4,125 (16)</td><td>4,125</td><td>38%</td></tr>
<tr><td>2</td><td>4,135 (14)</td><td>4,120 (10)</td><td>4,135</td><td>52%</td></tr>
<tr><td>3</td><td>4,140 (8)</td><td>4,120 (10)</td><td>4,120</td><td>62%</td></tr>
<tr><td>4</td><td>4,140 (8)</td><td>4,115 (3)</td><td>4,140</td><td><b>70%</b> ✅</td></tr></table>
<div class='box tip'>💡 Platform ខ្លះប្រៀបធៀប<b>ពីរជួរ</b>ម្ដង ឬប្រើទំហំជួរខុសគ្នា។ រូប 📊 Analysis របស់ XAU.KH ប្រើវិធីសាមញ្ញមួយទៀត: យកជួរដែលមាន volume ធំបំផុតម្ដងមួយៗ រហូតដល់បាន 70%។ ដូច្នេះ VAH/VAL អាចខុសគ្នាបន្តិចពី platform មួយទៅមួយ។ នេះធម្មតា។</div>
"""),
        ("Value Area High (VAH) និង Value Area Low (VAL)", """
<p>ព្រំដែនទាំងពីរនៃ Value Area:</p>
<ul><li><span class='en-term'>VAH (Value Area High)</span> = កម្រិតខាងលើនៃ Value Area · ក្នុងឧទាហរណ៍ = <b>4,140</b></li>
<li><span class='en-term'>VAL (Value Area Low)</span> = កម្រិតខាងក្រោមនៃ Value Area · ក្នុងឧទាហរណ៍ = <b>4,120</b></li></ul>
""" + profile(ROWS, poc=4130, va=(4120, 4140),
              marks={4140: ("VAH 4,140", BL), 4130: ("POC 4,130", GOLD), 4120: ("VAL 4,120", BL)},
              caption="ផ្ទៃខៀវ = Value Area (70%) ពី VAL 4,120 ដល់ VAH 4,140 · ចម្ងាយ $20 = 200 pips") + """
<p><b>ការប្រើ VAH / VAL ជាកម្រិត</b> (គំនិតទូទៅ មិនមែនច្បាប់):</p>
<table><tr><th>ស្ថានភាព</th><th>អត្ថន័យដែលអាចកើត</th></tr>
<tr><td>តម្លៃនៅ<b>ក្នុង</b> VA</td><td>ទីផ្សារមានតុល្យភាព · ច្រើនតែដើរពី VAH ទៅ VAL ឬត្រឡប់មក POC</td></tr>
<tr><td>តម្លៃប៉ះ VAH ហើយ<b>បិទត្រឡប់ចូល</b></td><td>បដិសេធតម្លៃខ្ពស់ · ឱកាសធ្លាក់ទៅ POC / VAL</td></tr>
<tr><td>តម្លៃ<b>បិទលើ</b> VAH ហើយនៅទីនោះ</td><td>ទទួលយកតម្លៃខ្ពស់ជាង · តម្លៃ (value) អាចកំពុងផ្លាស់ឡើង</td></tr>
<tr><td>តម្លៃ<b>បើក</b>ក្រៅ VA នៃថ្ងៃមុន</td><td>ទីផ្សារអាចត្រឡប់ចូល VA ឬបន្តចាកចេញ · រង់ចាំមើល acceptance</td></tr></table>
<div class='box tip'>💡 Acceptance និង rejection នឹងរៀនលម្អិតក្នុង Chapter 21។ ឥឡូវ ចាំគំនិតសាមញ្ញ: <b>បិទទៀនក្រៅ ហើយនៅក្រៅ</b> = acceptance · <b>ឆ្លងហួស ហើយបិទត្រឡប់ចូល</b> = rejection។</div>
"""),
        ("Value Area ក្នុងការអនុវត្ត: ផែនទីនៃ Range", """
<p>Value Area នៃថ្ងៃមុន ឬ session មុន ផ្ដល់ឱ្យយើងនូវ<b>ផែនទី</b>សម្រាប់ថ្ងៃនេះ:</p>
""" + zigzag([50, 70, 46, 72, 30, 68, 50, 74, 64],
             {3: ("rejection", DN), 4: ("bounce", UP)},
             lines=[(72, 0, 8, "VAH 4,140", BL, True), (50, 0, 8, "POC 4,130", GOLD, False), (30, 0, 8, "VAL 4,120", BL, True)],
             caption="ទីផ្សារមានតុល្យភាព: តម្លៃលោតរវាង VAH និង VAL ហើយត្រឡប់មក POC ម្ដងហើយម្ដងទៀត") + """
""" + zigzag([40, 62, 52, 76, 66, 88, 80, 96],
             {3: ("បិទលើ VAH", UP), 4: ("retest", BL), 7: ("ឡើងបន្ត", UP)},
             lines=[(62, 0, 7, "VAH", BL, True), (40, 0, 7, "POC", GOLD, False)],
             caption="ទទួលយកតម្លៃខ្ពស់ជាង: បិទលើ VAH → retest VAH ពីខាងលើ → ឡើងបន្ត · Value Area ថ្មីនឹងផ្លាស់ឡើង") + """
<div class='box warn'>⚠️ តម្លៃមួយប៉ះ VAH <b>មិនមែន</b>សញ្ញាលក់ស្វ័យប្រវត្តិទេ។ នៅតែត្រូវការ structure (MSS / CHOCH), ទីតាំងល្អ និង RR សមរម្យ ដូចក្នុង Chapter 9–17។</div>
"""),
        ("High Volume Nodes (HVN)", """
<p><span class='en-term'>HVN (High Volume Node)</span> = តំបន់ដែល profile មាន bar <b>វែង</b> (volume ខ្ពស់) ជាងតំបន់ជុំវិញ។ POC គឺជា HVN ធំបំផុត
ប៉ុន្តែ profile មួយអាចមាន HVN <b>ច្រើន</b>។ ក្នុងឧទាហរណ៍ 4,110 គឺជា HVN ទីពីរ (12%) ដែលនៅក្រៅ Value Area។</p>
<ul><li>HVN = តម្លៃដែលទីផ្សារ<b>ធ្លាប់ទទួលយក</b> · អ្នកទិញ និងអ្នកលក់មានទីតាំងច្រើននៅទីនោះ</li>
<li>ពេលតម្លៃត្រឡប់មក HVN វា<b>ច្រើនតែយឺត</b> ដើរចំហៀង ឬលោតចុះឡើង (ព្រោះមាន orders ច្រើននៅសងខាង)</li>
<li>HVN អាចដើរតួជា <b>support / resistance</b> ឬជា "មេដែក" ដែលទាញតម្លៃមក</li></ul>
"""),
        ("Low Volume Nodes (LVN)", """
<p><span class='en-term'>LVN (Low Volume Node)</span> = តំបន់ដែល profile មាន bar <b>ខ្លី</b> (volume ទាប) នៅចន្លោះ HVN ពីរ។
ក្នុងឧទាហរណ៍ 4,115 (3%) គឺជា LVN រវាង HVN 4,130 និង HVN 4,110។</p>
""" + profile(ROWS, poc=4130, va=(4120, 4140),
              marks={4130: ("HVN · POC", GOLD), 4115: ("LVN ↯", DN), 4110: ("HVN 2", PU), 4150: ("tail តូច", GR)},
              caption="HVN = bar វែង (តម្លៃយឺត) · LVN = bar ខ្លីរវាង HVN ពីរ (តម្លៃរត់លឿនឆ្លង)") + """
<ul><li>LVN = តម្លៃដែលទីផ្សារ<b>រត់ឆ្លង</b>លឿនពីមុន (ច្រើនជា displacement ឬ FVG: Chapter 13)</li>
<li>ពេលតម្លៃត្រឡប់មក LVN វាអាច<b>រត់ឆ្លងលឿន</b>ម្ដងទៀត ទៅ HVN បន្ទាប់ ឬ<b>ច្រានចេញ</b> (rejection) ពី LVN</li>
<li>LVN ជាកន្លែងល្អសម្រាប់គិតពី<b>ព្រំដែន</b> រវាងតំបន់ពីរ · អ្នក trade ខ្លះដាក់ SL នៅម្ខាងនៃ LVN ជំនួសឱ្យកណ្ដាល HVN</li></ul>
""" + zigzag([70, 62, 66, 58, 64, 30, 22, 28, 20, 26],
             {2: ("HVN", GOLD), 5: ("LVN: លឿន", DN), 8: ("HVN 2", PU)},
             lines=[(64, 0, 4, "", GOLD, True), (24, 5, 9, "", PU, True)],
             caption="តម្លៃយឺតនៅ HVN → រត់លឿនឆ្លង LVN → យឺតម្ដងទៀតនៅ HVN បន្ទាប់") + """
<table><tr><th></th><th>HVN</th><th>LVN</th></tr>
<tr><td>Bar</td><td>វែង</td><td>ខ្លី</td></tr>
<tr><td>អត្ថន័យ</td><td>ទទួលយក · តម្លៃយុត្តិធម៌</td><td>បដិសេធ · រត់ឆ្លង</td></tr>
<tr><td>ពេលតម្លៃត្រឡប់មក</td><td>យឺត · ចំហៀង · S/R</td><td>រត់ឆ្លងលឿន ឬច្រានចេញ</td></tr>
<tr><td>ប្រើជា</td><td>គោលដៅ · តំបន់ entry</td><td>ព្រំដែន · កន្លែងគិតពី SL</td></tr></table>
"""),
        ("អាន Volume Profile លើរូប 📊 Analysis", """
<p>រូប 📊 <b>Analysis</b> និង <b>/check</b> របស់ XAU.KH គូរ Volume Profile នៃ <b>5 ថ្ងៃចុងក្រោយ</b> ជា bar តូចៗនៅ<b>គែមស្ដាំ</b>នៃ chart:
bar <b>ខៀវ</b> = នៅក្នុង Value Area · bar <b>ប្រផេះ</b> = នៅក្រៅ · បន្ទាត់ខៀវដែលមានស្លាក <b>POC</b> = តម្លៃដែលមាន volume ច្រើនបំផុត។ រូបគំនូរខាងក្រោមបង្ហាញគំនិតដូចគ្នា:</p>
""" + chart_with_profile(caption="Profile នៅគែមស្ដាំ · ផ្ទៃខៀវ = Value Area · តម្លៃលោតជុំវិញ POC · wick លឿនឆ្លង LVN ហើយត្រឡប់មកវិញ") + """
<p><b>សំណួរ 3 ដែលត្រូវសួររាល់ពេលមើលរូប:</b></p>
<ol><li>តម្លៃឥឡូវនៅ<b>ក្នុង</b> ឬ<b>ក្រៅ</b> Value Area?</li>
<li>POC នៅ<b>លើ</b> ឬ<b>ក្រោម</b>តម្លៃ ហើយឆ្ងាយប៉ុន្មាន (គិតជា $ និង pips)?</li>
<li>មាន LVN ឬ HVN នៅជិត liquidity ឬ zone ដែលអ្នកកំពុងមើល (PDH/PDL, Asia high/low, FVG, OB) ទេ?</li></ol>
<div class='box warn'>⚠️ <b>មេរៀនពីទិន្នន័យពិត:</b> ពេលរៀបចំជំពូកនេះ យើងបានពិនិត្យ profile 5 ថ្ងៃពីទិន្នន័យ gold futures (ដល់ 17 Nov 2026) ហើយរកឃើញថា POC ត្រូវបានកំណត់ដោយ<b>ទៀន 5m តែមួយ</b>
នៅម៉ោងបិទ session (16:55 New York) ដែលមាន volume ច្រើនជាងទៀនធម្មតារាប់សិបដង។ ទៀនបែបនេះច្រើនជាទិន្នន័យ settlement មិនមែនការជួញដូរធម្មតាទេ។
នេះហើយជាមូលហេតុដែល Chapter 18 និយាយថា volume មានដែនកំណត់: <b>ពិនិត្យជានិច្ចថា POC ធ្វើឱ្យយល់បានជាមួយ chart</b> (តម្លៃពិតជាចំណាយពេលនៅទីនោះឬទេ?)។</div>
<div class='box tip'>💡 ក្នុង <b>MT5</b> មិនមាន Volume Profile ជា indicator ដើម (built-in) ទេ។ បើចង់ប្រើ ត្រូវរក indicator ពី MQL5 Market/CodeBase
ហើយពិនិត្យថាវាប្រើ tick volume ឬ real volume និងគ្របរយៈពេលប៉ុន្មាន។</div>
"""),
        ("Volume Profile ក្នុងប្រព័ន្ធ XAU.KH និងកំហុសញឹកញាប់", """
<p>XAU.KH មាន model មួយដែលប្រើ POC: ពេល profile នៃ session មុនបង្ហាញថាភាគីថ្មីកំពុងគ្រប់គ្រង តម្លៃ pullback មក <b>POC</b>
ហើយទៀន 15m បិទត្រឡប់ → signal ត្រូវបានផ្ញើក្នុង Signals ដោយមានស្លាក <b>📊 Volume</b>។ យោងតាមការសាកល្បងរបស់ platform លើទិន្នន័យ 2 ឆ្នាំ:
<b>122 trades · ឈ្នះ 48% · ជាមធ្យម +0.26R</b> ក្នុងមួយ trade។</p>
<div class='box warn'>⚠️ លទ្ធផលសាកល្បង (backtest) <b>មិនធានា</b>លទ្ធផលអនាគតទេ។ ឈ្នះ 48% មានន័យថាខាត<b>ជិតពាក់កណ្ដាល</b>នៃ trades ហើយអាចខាតជាប់គ្នាច្រើនដង។
XAU.KH តាមដាន model នេះដាច់ដោយឡែក ដើម្បីប្រៀបធៀប live និង test ដោយស្មោះត្រង់ · មើល 📈 <b>Proof</b> សម្រាប់លទ្ធផលពិត។</div>
<p><b>កំហុសញឹកញាប់:</b></p>
<ul><li>❌ ចាត់ទុក POC / VAH / VAL ជាលេខពិតប្រាកដ (ត្រូវចាត់ទុកជា<b>តំបន់</b>)</li>
<li>❌ លក់រាល់ពេលប៉ះ VAH ឬទិញរាល់ពេលប៉ះ VAL ក្នុងថ្ងៃដែលមាននិន្នាការខ្លាំង</li>
<li>❌ ភ្លេចថា profile ពី broker ផ្សេង ឬពី futures ផ្សេងគ្នា</li>
<li>❌ ប្រើ profile ដោយមិនដឹងថាវាគ្របរយៈពេលប៉ុន្មាន (មួយថ្ងៃ? មួយសប្ដាហ៍? Chapter 20)</li>
<li>❌ មើលតែ profile ហើយភ្លេច structure និង liquidity</li></ul>
"""),
    ],
    summary=["Volume Profile = volume តាម<b>តម្លៃ</b> (bar ផ្ដេក) មិនមែនតាមពេលវេលា",
             "POC = តម្លៃដែលមាន volume ច្រើនបំផុត = តម្លៃយុត្តិធម៌ · តម្លៃច្រើនត្រឡប់មកវិញក្នុង range",
             "Value Area = 70% នៃ volume ជុំវិញ POC · VAH = ព្រំខាងលើ · VAL = ព្រំខាងក្រោម",
             "HVN = bar វែង (ទទួលយក · តម្លៃយឺត) · LVN = bar ខ្លី (បដិសេធ · តម្លៃរត់ឆ្លងលឿន)",
             "កម្រិត profile ជាតំបន់ មិនមែនសញ្ញា · ប្រើជាមួយ structure និង liquidity ជានិច្ច"],
    exercise=["ពីតារាងឧទាហរណ៍ បើ 4,140 មាន volume 2 ហើយ 4,115 មាន 9 (ផ្សេងទៀតដដែល សរុបនៅតែ 100) គណនា Value Area ម្ដងទៀតតាមវិធីមួយជួរម្ដង។ VAH/VAL ថ្មីជាអ្វី?",
              "បើករូប 📊 Analysis ថ្ងៃនេះ ហើយកត់ត្រា POC។ តាមដានថាតម្លៃប៉ះ POC ប៉ុន្មានដងក្នុងថ្ងៃនោះ។",
              "លើ chart របស់អ្នក រកតំបន់មួយដែលតម្លៃរត់ឆ្លងលឿន (LVN ដែលអាចកើត) និងតំបន់ចំហៀងយូរ (HVN)។ ពួកវាត្រូវនឹង FVG ឬ OB ណាខ្លះ?",
              "ប្រើ <b>/check</b> មុន session NY ហើយសរសេរថា តម្លៃនៅក្នុង ឬក្រៅ Value Area និងអ្វីដែលអ្នកនឹងរង់ចាំ។"],
)
