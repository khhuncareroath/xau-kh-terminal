from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def _path(pts):
    return " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(pts))


def fvg_retrace(w=420, h=190, caption=""):
    """Impulse up leaves a gap (FVG box) between candle 1 high and candle 3 low; price returns into it, then continues."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="96" y="96" width="{w - 116}" height="26" fill="{BL}" fill-opacity=".14" stroke="{BL}" stroke-dasharray="4 3"/>',
           f'<text x="{w - 24}" y="112" text-anchor="end" fill="{BL}" class="lt">Bullish FVG</text>',
           f'<line x1="96" x2="{w - 20}" y1="109" y2="109" stroke="{BL}" stroke-width="1" stroke-dasharray="2 3"/>',
           f'<text x="{w - 24}" y="134" text-anchor="end" fill="{BL}" class="st">CE 50%</text>']
    # three candles of the impulse
    for x, o, c, hi, lo, col in [(70, 150, 128, 122, 160, UP), (96, 128, 70, 64, 132, UP), (122, 72, 58, 50, 96, UP)]:
        out.append(f'<line x1="{x}" x2="{x}" y1="{hi}" y2="{lo}" stroke="{col}" stroke-width="1.6"/>')
        out.append(f'<rect x="{x - 7}" y="{min(o, c)}" width="14" height="{abs(o - c)}" fill="{col}"/>')
    out.append(f'<text x="70" y="176" text-anchor="middle" fill="{GR}" class="st">1</text>'
               f'<text x="96" y="176" text-anchor="middle" fill="{GR}" class="st">2</text>'
               f'<text x="122" y="176" text-anchor="middle" fill="{GR}" class="st">3</text>')
    out.append(f'<path d="{_path([(122, 58), (165, 44), (205, 80), (245, 112), (270, 104), (300, 66), (340, 40), (395, 22)])}" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="245" cy="112" r="3.4" fill="{OR}"/><text x="238" y="136" text-anchor="end" fill="{OR}" class="pt">Entry</text>')
    out.append(f'<line x1="220" x2="300" y1="152" y2="152" stroke="{DN}" stroke-width="1.4"/><text x="305" y="156" fill="{DN}" class="lt">SL</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def tl_break_retest(w=420, h=190, caption=""):
    """Falling trendline touched 3 times, price breaks above with a strong close, retests the line from above, then rises."""
    X = lambda i: 24 + i * (w - 48) / 10
    Y = lambda v: h - 22 - v * (h - 44) / 100
    tl = lambda i: 88 - i * 6.5
    pts = [(0, tl(0)), (1, 60), (2, tl(2) - 1), (3, 46), (4, tl(4) - 1), (5, 36), (6, tl(6) + 22), (7, tl(7) + 2), (8, 70), (9, 66), (10, 90)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<path d="M{X(0):.1f},{Y(tl(0)):.1f} L{X(10):.1f},{Y(tl(10)):.1f}" stroke="{DN}" stroke-width="1.8"/>',
           f'<path d="{_path([(X(i), Y(v)) for i, v in pts])}" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linejoin="round"/>',
           f'<text x="{X(0.3):.1f}" y="{Y(tl(0.3)) - 8:.1f}" fill="{DN}" class="lt">Trendline ចុះ</text>']
    for k, i in enumerate([0, 2, 4], 1):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(tl(i) - (0 if i == 0 else 1)):.1f}" r="3.4" fill="{DN}"/>')
    out.append(f'<circle cx="{X(6):.1f}" cy="{Y(tl(6) + 22):.1f}" r="3.4" fill="{UP}"/><text x="{X(6) - 6:.1f}" y="{Y(tl(6) + 22) - 9:.1f}" text-anchor="middle" fill="{UP}" class="pt">Break</text>')
    out.append(f'<circle cx="{X(7):.1f}" cy="{Y(tl(7) + 2):.1f}" r="3.4" fill="{OR}"/><text x="{X(7):.1f}" y="{Y(tl(7) + 2) + 30:.1f}" text-anchor="middle" fill="{OR}" class="pt">Retest</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def vp_reactions(w=420, h=210, caption=""):
    """Profile on the right with VAH, POC, VAL. Price comes up to the POC from below and gets rejected; another leg tags VAL and bounces."""
    vals = [5, 8, 14, 24, 38, 54, 70, 88, 74, 58, 42, 30, 20, 12, 7, 4]
    top, bot = 14, h - 16
    rh = (bot - top) / len(vals)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, v in enumerate(vals):
        col = GOLD if i == 7 else (BL if 3 <= i <= 11 else "#C7C7CC")
        out.append(f'<rect x="{w - 16 - v * 0.75:.1f}" y="{top + i * rh + 1:.1f}" width="{v * 0.75:.1f}" height="{rh - 2:.1f}" rx="2" fill="{col}" fill-opacity=".55"/>')
    yvah, ypoc, yval = top + 3 * rh, top + 7.5 * rh, top + 12 * rh
    for y, t, col in [(yvah, "VAH", DN), (ypoc, "POC", GOLD), (yval, "VAL", UP)]:
        out.append(f'<line x1="16" x2="{w - 16}" y1="{y:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="1.3" stroke-dasharray="5 4"/>')
        out.append(f'<text x="20" y="{y - 4:.1f}" fill="{col}" class="lt">{t}</text>')
    pts = [(55, yval + 26), (90, ypoc + 30), (120, ypoc + 2), (140, ypoc + 34), (175, yval - 2), (200, yval + 8), (220, yval - 34),
           (250, yvah + 6), (268, yvah - 12), (290, yvah + 22)]
    out.append(f'<path d="{_path(pts)}" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<text x="120" y="{ypoc - 10:.1f}" text-anchor="middle" fill="{GOLD}" class="pt">①</text>')
    out.append(f'<text x="200" y="{yval + 24:.1f}" text-anchor="middle" fill="{UP}" class="pt">②</text>')
    out.append(f'<text x="268" y="{yvah - 18:.1f}" text-anchor="middle" fill="{DN}" class="pt">③</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=28, part="PART 6 · Combining the Disciplines",
    title_km="Setup ការ Trade មាស", title_en="Gold Trading Setups: From Idea to a Testable Plan",
    intro="""Chapter 26 ផ្ដល់<b>ទិស</b> (bias)។ Chapter 27 បង្រៀនការបញ្ចូលភស្តុតាង (<span class='en-term'>confluence</span>)។
ជំពូកនេះប្រមូលអ្វីៗទាំងអស់ទៅជា <span class='en-term'>setup</span> ជាក់លាក់ ប្រាំបួនប្រភេទ ដែលអ្នក trade មាសប្រើញឹកញាប់។
Setup នីមួយៗមាន: <b>បរិបទ</b> · <b>កន្លែង</b> · <b>trigger</b> · <b>SL</b> · <b>TP</b> · <b>ពេលដែល idea ខុស</b>។
យើងក៏និយាយត្រង់ៗផងដែរថា setup ណាខ្លះ<b>មិនបានល្អ</b> ពេលក្រុម XAU.KH សាកល្បងលើទិន្នន័យពិត។ Setup ល្អ = <b>បានសាកល្បង</b> មិនមែន "មើលទៅស្អាត"។""",
    sections=[
        ("Setup មួយត្រូវមានអ្វីខ្លះ?", """
<p>Setup មិនមែនជារូបភាពស្អាតមួយលើ chart ទេ។ វាគឺជា<b>ច្បាប់</b>ដែលអ្នកអាចសរសេរ ធ្វើតាមម្ដងទៀត និងសាកល្បងបាន។
បើអ្នកមិនអាចសរសេរ setup ជាប្រយោគច្បាស់ៗ នោះអ្នកមិនទាន់មាន setup ទេ។</p>
""" + flow([("Context", "bias HTF", BL), ("Location", "zone / level", GOLD), ("Trigger", "សញ្ញាចូល", UP),
            ("SL", "idea ខុសនៅណា", DN), ("TP", "គោលដៅ liquidity", PU), ("Review", "កត់ត្រា · វាស់", GR)],
           caption="ផ្នែកទាំង 6 នៃ setup ពេញលេញ · ខ្វះមួយ = ការទាយ") + """
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>សំណួរ</th></tr>
<tr><td><b>Context</b></td><td>Daily / 4H ឡើង ធ្លាក់ ឬ range? (Ch 26)</td></tr>
<tr><td><b>Location</b></td><td>តម្លៃនៅ zone ណា? liquidity · FVG · OB · VAH/VAL/POC · trendline</td></tr>
<tr><td><b>Trigger</b></td><td>អ្វីប្រាប់ "ឥឡូវ"? ទៀនបិទ · MSS · absorption</td></tr>
<tr><td><b>SL</b></td><td>បើតម្លៃទៅដល់ទីនេះ idea <b>ខុស</b></td></tr>
<tr><td><b>TP</b></td><td>Liquidity ឬ level ផ្ទុយទិសជិតបំផុត · R:R ≥ 1:2</td></tr></table>
<div class='box tip'>💡 គ្រប់ឧទាហរណ៍ក្នុងជំពូកនេះប្រើ convention របស់ XAU.KH: មាសប្រហែល <b>$4,000+</b> · $1 = <b>10 pips</b> · 0.01 lot = 1 oz → តម្លៃដើរ $1 = <b>$1</b> ចំណេញ/ខាត។</div>
"""),
        ("Setup 1 · Liquidity Sweep Reversal", """
<p>តម្លៃ<b>យក stop</b> នៅក្រោម equal lows (<span class='en-term'>SSL</span>) ឬលើ equal highs (<span class='en-term'>BSL</span>) រួច<b>ត្រឡប់វិញ</b>យ៉ាងលឿន។
វាជា setup ត្រឡប់ទិស ដូច្នេះត្រូវការ<b>ភស្តុតាងខ្លាំង</b>: displacement + <span class='en-term'>MSS</span>។</p>
""" + zigzag([72, 46, 60, 34, 50, 33, 46, 16, 58, 48, 82], {3: ("EQL", OR), 5: ("EQL", OR), 7: ("Sweep", OR), 8: ("MSS ↑", UP), 9: ("Entry", BL)},
             lines=[(34, 3, 6, "SSL", OR, True), (50, 4, 9, "", UP, False)],
             caption="Equal lows = SSL → wick យកក្រោម → បិទលើ LH ចុងក្រោយ (MSS) → ចូលនៅ pullback (FVG / OB តូច)") + """
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>ច្បាប់</th></tr>
<tr><td>Context</td><td>Sweep នៅ <b>discount</b> ក្នុង HTF ឡើង (ឬ premium ក្នុង HTF ធ្លាក់)</td></tr>
<tr><td>Trigger</td><td>ទៀន <b>បិទ</b>ត្រឡប់ចូលលើ SSL + MSS ដោយ displacement លើ 5m/15m</td></tr>
<tr><td>SL</td><td>ក្រោម wick នៃ sweep (+ spread)</td></tr>
<tr><td>TP</td><td>BSL / swing high ផ្ទុយទិស · POC</td></tr></table>
<div class='box warn'>⚠️ Sweep គ្មាន displacement ច្រើនតែជា <span class='en-term'>run</span> (តម្លៃបន្តដើរ)។ កុំ "ចាប់កាំបិតធ្លាក់" ត្រឹមតែឃើញ wick។</div>
"""),
        ("Setup 2 · BOS Continuation", """
<p>ក្នុង trend ស្អាត តម្លៃបំបែក swing ចុងក្រោយ (<span class='en-term'>BOS</span>) ដោយទៀនបិទខ្លាំង។ យើង trade <b>តាម trend</b> មិនប្រឆាំងវា។
នេះជា setup ដែលស្រួលយល់បំផុតសម្រាប់អ្នកចាប់ផ្ដើម។</p>
""" + zigzag([14, 42, 28, 60, 44, 80, 64, 94], {2: ("HL", UP), 3: ("BOS", UP), 4: ("HL", UP), 5: ("BOS", UP), 6: ("Entry", BL)},
             lines=[(60, 3, 6, "", UP, True)],
             caption="HH-HL ស្អាត · BOS ដោយទៀនបិទ · ចូលនៅ HL ថ្មី ឬភ្លាមក្រោយការបិទ") + """
<div class='box ok'>✅ <b>លទ្ធផលសាកល្បងរបស់ XAU.KH</b> (មាស 2 ឆ្នាំ រួមថ្លៃ spread): <b>4H breakout + ទៀនបិទខ្លាំង + trend ស្អាត + Day Meter ≥ 70%</b>
ឈ្នះប្រហែល <b>78%</b> ជាមធ្យម <b>+0.56R</b> ក្នុងមួយ trade។ នេះជា setup ដែលក្រុមចាត់ទុកថា <b>proven</b> ក្នុងការសាកល្បង។
លទ្ធផលអតីតកាល <b>មិនធានា</b>អនាគតទេ។</div>
<div class='box tip'>💡 សញ្ញា XAU.KH ក្នុង 🚨 <b>Signals</b> ផ្អែកលើគំនិតស្រដៀងនេះ: 15m បិទហួសខ្សែ <b>TARGET</b> + ការវិនិច្ឆ័យ 4H (💎 A+ / ⭐ B+) + ពិនិត្យទិសផ្ទុយ។
ក្នុងការសាកល្បង វាឈ្នះប្រហែល <b>58%</b> (+0.15R) ប្រហែល 15 ដង/ខែ ប៉ុន្តែ<b>មិនទាន់ proven</b>: live record នៅ 📈 <b>Proof</b> ជាអ្នកសម្រេច។</div>
"""),
        ("Setup 3 · FVG Retracement", """
<p>ចលនាខ្លាំង (displacement) ទុក <span class='en-term'>Fair Value Gap</span> (ចន្លោះរវាង high ទៀន 1 និង low ទៀន 3)។
តម្លៃច្រើនតែត្រឡប់មក "បំពេញ" ផ្នែកខ្លះនៃ gap មុនបន្តទិសដើម។</p>
""" + fvg_retrace(caption="ទៀន 1-2-3 បង្កើត FVG · តម្លៃត្រឡប់មកប៉ះ CE (50%) · SL ក្រោមបាតនៃ FVG / swing") + """
<ul><li><b>FVG ល្អ</b>: កើតពី displacement ដែល<b>បំបែក structure</b> ស្របទិស HTF</li>
<li><b>FVG ខ្សោយ</b>: នៅកណ្ដាល range · ប្រឆាំង trend · ត្រូវបានបំពេញម្ដងរួចហើយ</li>
<li>ចូល: limit នៅគែម FVG ឬ CE · ឬរង់ចាំ trigger LTF ក្នុង FVG (Chapter 29)</li></ul>
<div class='box warn'>⚠️ Limit order ក្នុង FVG ប្រហែល<b>មិនបាន fill</b> ពេលតម្លៃរត់ខ្លាំង ហើយពេលខ្លះតម្លៃឆ្លងកាត់ FVG ទាំងស្រុង។ SL ត្រូវតែនៅកន្លែង idea ខុស។</div>
"""),
        ("Setup 4 · Order Block Entry", """
<p><span class='en-term'>Order Block</span> = ទៀនផ្ទុយទិសចុងក្រោយ មុន displacement ដែលបំបែក structure។ គំនិត: តម្លៃត្រឡប់មក OB ហើយមានប្រតិកម្មម្ដងទៀត។</p>
""" + zigzag([60, 40, 48, 30, 26, 70, 56, 33, 66, 86], {4: ("Bullish OB", BL), 5: ("Displacement", UP), 7: ("Retest OB", OR)},
             lines=[(30, 3, 9, "OB zone", BL, True)],
             caption="ទៀនចុះចុងក្រោយមុនការឡើងខ្លាំង = Bullish OB · តម្លៃត្រឡប់មកតំបន់នោះ") + """
<div class='box warn'>⚠️ <b>ការពិតពីការសាកល្បង:</b> ក្រុម XAU.KH បានសាកល្បង <b>OB limit + SL ក្រោម OB</b> និង<b>ទិញ Demand / លក់ Supply ពេលទៀនត្រឡប់</b> លើមាស។
លទ្ធផល<b>ខាត</b> (ប្រហែល −0.15R សម្រាប់ Demand/Supply) បន្ទាប់ពីគិតថ្លៃ spread។ ដូច្នេះយើងប្រើ OB ជា <b>key level</b> (កន្លែងសម្គាល់) មិនមែនជាហេតុផលចូលតែម្នាក់ឯងទេ។</div>
<div class='box tip'>💡 ប្រើ OB ឱ្យមានប្រយោជន៍: (1) ជា<b>កន្លែង</b>ដើម្បីរង់ចាំ trigger · (2) ជាកន្លែងដាក់ SL ការពារ · (3) ជាគោលដៅ TP ផ្ទុយទិស។</div>
"""),
        ("Setup 5 · Trendline Breakout and Retest", """
<p>Trendline ដែលប៉ះ 3 ដងឡើង ត្រូវបានមនុស្សច្រើនមើលឃើញ។ ពេលតម្លៃ<b>បិទឆ្លង</b>ខ្សែដោយ displacement វាអាចជាសញ្ញាថា structure កំពុងប្ដូរ។</p>
""" + tl_break_retest(caption="Trendline ចុះ ប៉ះ 3 ដង → ទៀនបិទឆ្លងខ្លាំង → retest ខ្សែពីលើ → ឡើងបន្ត") + """
<table style='break-inside:avoid'><tr><th>វិធីចូល</th><th>គុណសម្បត្តិ</th><th>គុណវិបត្តិ</th></tr>
<tr><td>ចូលភ្លាមក្រោយទៀនបិទ</td><td>មិនខកខាន breakout ខ្លាំង</td><td>SL ធំជាង</td></tr>
<tr><td>រង់ចាំ retest</td><td>SL តូច · R:R ល្អ</td><td>Breakout ខ្លាំង <b>ច្រើនតែមិនត្រឡប់មក</b></td></tr></table>
<div class='box tip'>💡 ក្នុងការសាកល្បងរបស់ក្រុម ការរង់ចាំ retest ក្រោយ breakout <b>អាក្រក់ជាង</b>ការចូលភ្លាម ព្រោះ breakout ល្អបំផុតច្រើនតែមិនត្រឡប់មកវិញ។ មើលបន្ថែមក្នុង Chapter 29។</div>
"""),
        ("Setup 6 · POC Rejection", """
<p><span class='en-term'>POC</span> (Point of Control) = តម្លៃដែលមាន volume ច្រើនបំផុតក្នុង profile។ វាជា "តម្លៃយុត្តិធម៌" (<span class='en-term'>fair value</span>)។
ពេលតម្លៃមកដល់ POC ពីខាងក្រោម ក្នុង bias ចុះ ហើយ<b>មិនអាចទទួលយក</b>នៅលើវាបាន នោះជា POC rejection។</p>
""" + vp_reactions(caption="① POC rejection (មិនបិទលើ POC) · ② VAL bounce · ③ VAH rejection · profile ពី volume ពិត") + """
<ul><li>Trigger: wick ប៉ះ POC · ទៀនបិទត្រឡប់ក្រោម · LTF MSS ចុះ</li>
<li>SL: លើ POC + buffer (ឬលើ swing high ដែលបង្កើតនៅ POC)</li>
<li>TP: VAL ឬ low ផ្ទុយទិស</li></ul>
<div class='box warn'>⚠️ POC ជា "មេដែក" ផងដែរ: ក្នុង range តម្លៃច្រើនតែវិលជុំវិញ POC ច្រើនដង។ បើតម្លៃ<b>បិទ និងនៅលើ</b> POC ច្រើនទៀន = <b>acceptance</b> មិនមែន rejection ទេ។</div>
"""),
        ("Setup 7 · VAH និង VAL Reactions", """
<p><span class='en-term'>Value Area</span> (VAH–VAL) គ្របដណ្ដប់ប្រហែល 70% នៃ volume។ គែមរបស់វាជាកន្លែងដែលទីផ្សារសម្រេចថា "<b>ទទួលយក</b> ឬ <b>បដិសេធ</b>"។</p>
<table style='break-inside:avoid'><tr><th>ស្ថានការណ៍</th><th>ការអាន</th><th>Setup</th></tr>
<tr><td>ប៉ះ VAH ហើយត្រឡប់ចូល value</td><td>Rejection</td><td>Sell ទៅ POC / VAL</td></tr>
<tr><td>ប៉ះ VAL ហើយត្រឡប់ចូល value</td><td>Rejection</td><td>Buy ទៅ POC / VAH</td></tr>
<tr><td>បិទក្រៅ VAH/VAL ហើយនៅក្រៅ</td><td>Acceptance</td><td>Trade តាមទិស breakout</td></tr>
<tr><td>បើកក្រៅ value ហើយត្រឡប់ចូល</td><td>"80% rule" (ល្បី)</td><td>គោលដៅគែមម្ខាងទៀត · <b>មិនមែនច្បាប់ដាច់ខាត</b></td></tr></table>
""" + flow([("ដល់ VAH/VAL", "កន្លែង", GOLD), ("ទៀនបិទ", "ចូលវិញ ឬនៅក្រៅ?", BL), ("Rejection", "trade ទៅ POC", UP), ("Acceptance", "ប្ដូរ idea", DN)],
           caption="សំណួរតែមួយនៅគែម value: តម្លៃត្រូវបានទទួលយក ឬបដិសេធ?") + """
<div class='box warn'>⚠️ VP ត្រូវការ <b>volume ពិត</b> (COMEX GC futures · Chapter 25)។ Tick volume របស់ MT5 មិនមែន volume ពិតទេ។ បើយកកម្រិតពី GC ត្រូវកែ <span class='en-term'>basis</span> មុនដាក់លើ MT5។</div>
"""),
        ("Setup 8 · Order Flow Absorption", """
<p><span class='en-term'>Absorption</span> = អ្នក trade aggressive ទិញ (ឬលក់) ខ្លាំង ប៉ុន្តែតម្លៃ<b>មិនដើរ</b> ព្រោះមាន limit orders ធំកំពុង "ស្រូប"។
នៅកម្រិតសំខាន់ វាអាចជាសញ្ញាដំបូងនៃការត្រឡប់។</p>
""" + bars([("1", -380, DN), ("2", -450, DN), ("3", -520, DN), ("4", -300, DN), ("5", 260, UP), ("6", 640, UP)],
           caption="ឧទាហរណ៍សម្រាប់ពន្យល់ (មិនមែនទិន្នន័យពិត): delta 5m នៅ VAL · លក់ខ្លាំង (−) តែតម្លៃមិនធ្លាក់ = absorption → delta ប្ដូរជា (+)") + """
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>អ្វីដែលត្រូវឃើញ</th></tr>
<tr><td>1. Location</td><td>VAL / SSL / zone HTF (មិនមែនកណ្ដាល range)</td></tr>
<tr><td>2. Absorption</td><td>Delta អវិជ្ជមានធំ ប៉ុន្តែ low មិនថ្មី ឬថ្មីតិចតួច</td></tr>
<tr><td>3. Confirmation</td><td>Delta ប្ដូរជាវិជ្ជមាន + ទៀនបិទលើ + LTF MSS</td></tr>
<tr><td>4. Risk</td><td>SL ក្រោម low នៃ absorption · TP ទៅ POC</td></tr></table>
<div class='box warn'>⚠️ Setup នេះ<b>ត្រូវការ feed COMEX</b> (footprint / delta)។ បើអ្នកមានតែ MT5 សូម<b>រំលង</b> setup នេះ ហើយប្រើ setup ផ្សេង។</div>
"""),
        ("Setup 9 · Multi-Confirmation Gold Setup", """
<p>នេះជាការបញ្ចូល Chapter 26–27: ភស្តុតាងពី <b>family ផ្សេងគ្នា</b> នៅកន្លែងតែមួយ ហើយបញ្ចប់ដោយ trigger និង risk ច្បាស់។</p>
""" + flow([("Bias", "4H ឡើង", BL), ("Location", "SSL + VAL", GOLD), ("Timing", "London / NY", PU), ("Trigger", "Sweep + MSS 5m", UP)],
           caption="ឧទាហរណ៍: Bias + Location + Timing + Trigger = 4 family · គ្មានការរាប់ពីរដង") + """
<div class='box ok'>✅ <b>ឧទាហរណ៍គណនា:</b> 4H ឡើង។ ក្នុងម៉ោង London តម្លៃ sweep SSL ក្រោម 4,058 ដែលនៅជិត VAL ម្សិលមិញ រួចបិទឡើងលើ LH 5m (MSS)។<br>
Buy <b>4,061</b> · SL <b>4,053</b> ($8 = <b>80 pips</b>) · TP POC <b>4,079</b> ($18 = <b>180 pips</b>)។ R:R = 18 ÷ 8 = <b>1:2.25</b> ✅<br>
ជាមួយ 0.01 lot: ហានិភ័យ <b>$8</b> · គោលដៅ <b>$18</b>។ ជាមួយ 0.05 lot: ហានិភ័យ $40 · គោលដៅ $90។</div>
<div class='box warn'>⚠️ សូម្បីតែ setup ពេញលេញបែបនេះ ក៏<b>ខាតបាន</b>ដែរ។ ការសម្រេចចិត្តល្អ ≠ លទ្ធផលល្អគ្រប់ដង។ ចំណុចសំខាន់គឺ risk ថេរ និងការធ្វើតាមច្បាប់ដដែលៗ។</div>
"""),
        ("តារាងសង្ខេប និងលទ្ធផលសាកល្បង", """
<p>លទ្ធផលពីការសាកល្បងរបស់ក្រុម XAU.KH លើមាស 2 ឆ្នាំ (រួមថ្លៃ spread) ដូចដែលបានបង្ហាញក្នុងមេរៀនខ្លី Chapter 28:</p>
""" + bars([("4H breakout", 0.56, UP), ("XAU.KH signal", 0.15, BL), ("Demand/Supply", -0.15, DN)], unit="R",
           caption="R ជាមធ្យមក្នុងមួយ trade · 4H breakout = proven · សញ្ញា XAU.KH = មិនទាន់ proven · Demand/Supply reversal = ខាត") + """
<table style='break-inside:avoid'><tr><th>Setup</th><th>ប្រភេទ</th><th>Trigger សំខាន់</th></tr>
<tr><td>Liquidity sweep</td><td>ត្រឡប់ទិស</td><td>Displacement + MSS</td></tr>
<tr><td>BOS continuation</td><td>តាម trend</td><td>ទៀនបិទឆ្លង swing</td></tr>
<tr><td>FVG retracement</td><td>តាម trend</td><td>ត្រឡប់មក FVG + LTF trigger</td></tr>
<tr><td>Order block</td><td>Key level</td><td>ប្រើជាកន្លែង មិនមែនហេតុផលតែម្នាក់ឯង</td></tr>
<tr><td>Trendline break</td><td>ប្ដូរ structure</td><td>បិទឆ្លងដោយ displacement</td></tr>
<tr><td>POC / VAH / VAL</td><td>Value</td><td>Rejection ឬ acceptance</td></tr>
<tr><td>Absorption</td><td>ត្រឡប់ទិស</td><td>Delta ធំ តម្លៃមិនដើរ (COMEX)</td></tr></table>
<div class='box tip'>💡 Setup ដែល "ល្បី" លើអ៊ីនធឺណិត ជាច្រើនមើលទៅល្អលើ screenshot តែខាតពេលសាកល្បងរួមថ្លៃ។ Chapter 35 បង្រៀនអ្នកពីរបៀប<b>សាកល្បងខ្លួនឯង</b>។</div>
"""),
    ],
    summary=["Setup = Context + Location + Trigger + SL + TP + Review · សរសេរបាន ធ្វើតាមម្ដងទៀតបាន សាកល្បងបាន",
             "Sweep reversal ត្រូវការ displacement + MSS · BOS continuation trade តាម trend ហើយស្រួលបំផុត",
             "FVG / OB / trendline / POC / VAH / VAL ជា<b>កន្លែង</b> · ត្រូវការ trigger និង SL ច្បាស់",
             "Absorption ត្រូវការ volume ពិត (COMEX) · tick volume MT5 មិនគ្រប់គ្រាន់",
             "ក្នុងការសាកល្បង 4H breakout = proven · OB / Demand-Supply reversal = ខាត · គ្មាន setup ណាធានាចំណេញ"],
    exercise=["ជ្រើស setup មួយពីជំពូកនេះ ហើយសរសេរច្បាប់ទាំង 6 ផ្នែក (Context · Location · Trigger · SL · TP · Review) ជាប្រយោគច្បាស់ៗ។",
              "Sell 4,112 នៅ POC rejection · SL 4,119 · TP VAL 4,094។ គិត pips និង R:R និងប្រាក់ចំណេញ/ខាតជាមួយ 0.02 lot។",
              "រកក្នុង 📊 Analysis pictures ឬ /check នូវឧទាហរណ៍មួយនៃ BOS continuation និងមួយនៃ liquidity sweep។ តើ trigger នៅឯណា?",
              "តាមដាន 🚨 Signals 10 ដងបន្ទាប់។ កត់ត្រាថា setup នីមួយៗជាប្រភេទណា ហើយប្រៀបធៀបជាមួយលទ្ធផលនៅ 📈 Proof។"],
)
