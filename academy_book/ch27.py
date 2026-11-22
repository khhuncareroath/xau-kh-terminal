from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def trend_sweep(w=420, h=190, caption=""):
    """Rising trendline touched 3 times, a wick sweeps the stops under it, then price displaces up (MSS)."""
    X = lambda i: 24 + i * (w - 48) / 10
    Y = lambda v: h - 22 - v * (h - 44) / 100
    tl = lambda i: 8 + i * 6.2           # trendline value at step i
    pts = [(0, tl(0)), (1, 30), (2, tl(2) + 1), (3, 40), (4, tl(4) + 1), (5, 52), (6, tl(6) + 1), (7, 62), (8, tl(8) - 26),
           (9, 74), (10, 90)]
    path = " ".join(f"{'M' if k == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for k, (i, v) in enumerate(pts))
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<path d="M{X(0):.1f},{Y(tl(0)):.1f} L{X(10):.1f},{Y(tl(10)):.1f}" stroke="{BL}" stroke-width="1.8"/>',
           f'<rect x="{X(6.4):.1f}" y="{Y(tl(8)) :.1f}" width="{X(9) - X(6.4):.1f}" height="{Y(tl(8) - 22) - Y(tl(8)):.1f}" fill="{OR}" fill-opacity=".10"/>',
           f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linejoin="round"/>',
           f'<line x1="{X(7):.1f}" x2="{X(9.4):.1f}" y1="{Y(62):.1f}" y2="{Y(62):.1f}" stroke="{UP}" stroke-width="1.6"/>',
           f'<text x="{X(7) + 6:.1f}" y="{Y(62) - 5:.1f}" fill="{UP}" class="lt">MSS ↑</text>',
           f'<text x="{X(1.2):.1f}" y="{Y(tl(1.2)) + 18:.1f}" fill="{BL}" class="lt">Trendline</text>']
    for k, i in enumerate([2, 4, 6], 1):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(tl(i) + 1):.1f}" r="3.4" fill="{BL}"/>')
        out.append(f'<text x="{X(i):.1f}" y="{Y(tl(i) + 1) + 17:.1f}" text-anchor="middle" fill="{BL}" class="pt">{k}</text>')
    out.append(f'<circle cx="{X(8):.1f}" cy="{Y(tl(8) - 26):.1f}" r="3.4" fill="{OR}"/>')
    out.append(f'<text x="{X(8) + 8:.1f}" y="{Y(tl(8) - 26) + 4:.1f}" fill="{OR}" class="pt">Sweep</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def ict_vp(w=420, h=200, caption=""):
    """Older profile on the right with VAL; a new bullish FVG/OB zone (left) sits on that same VAL = two independent reasons."""
    vals = [6, 10, 16, 28, 44, 60, 78, 92, 80, 62, 46, 30, 18, 10, 6, 4]
    top, bot = 14, h - 14
    rh = (bot - top) / len(vals)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, v in enumerate(vals):
        col = GOLD if i == 7 else (BL if 3 <= i <= 10 else "#C7C7CC")
        out.append(f'<rect x="{w - 16 - v * 0.7:.1f}" y="{top + i * rh + 1:.1f}" width="{v * 0.7:.1f}" height="{rh - 2:.1f}" rx="2" fill="{col}" fill-opacity=".55"/>')
    yval = top + 11 * rh
    ypoc = top + 7.5 * rh
    out.append(f'<line x1="16" x2="{w - 16}" y1="{ypoc:.1f}" y2="{ypoc:.1f}" stroke="{GOLD}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    out.append(f'<text x="240" y="{ypoc - 4:.1f}" fill="{GOLD}" class="lt">POC = គោលដៅ TP</text>')
    out.append(f'<line x1="16" x2="{w - 16}" y1="{yval:.1f}" y2="{yval:.1f}" stroke="{UP}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    out.append(f'<text x="250" y="{yval + 14:.1f}" fill="{UP}" class="lt">VAL ម្សិលមិញ</text>')
    out.append(f'<rect x="120" y="{yval - 9:.1f}" width="110" height="20" rx="4" fill="{UP}" fill-opacity=".18" stroke="{UP}"/>')
    out.append(f'<text x="175" y="{yval + 5:.1f}" text-anchor="middle" fill="#1C1C1E" class="st">Bullish FVG / OB</text>')
    pts = [(20, ypoc - 40), (60, ypoc - 10), (95, yval - 2), (140, yval + 4), (165, yval - 30), (195, yval - 14), (235, ypoc - 6)]
    out.append('<path d="' + " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<text x="20" y="{bot - 4}" fill="#6E6E73" class="st">ICT zone (ថ្ងៃនេះ) + VAL (ថ្ងៃមុន) = ភស្តុតាងពីរប្រភពខុសគ្នា</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=27, part="PART 6 · Combining the Disciplines",
    title_km="ក្របខ័ណ្ឌ Confluence: បញ្ចូលភស្តុតាងឱ្យត្រឹមត្រូវ", title_en="The Confluence Framework: Combining Evidence Without Double-Counting",
    intro="""Chapter 26 ប្រាប់អ្នកពី<b>ទិស</b> (bias)។ ជំពូកនេះប្រាប់ពីរបៀបរក<b>កន្លែង</b> និង<b>ពេល</b>ដែលល្អ ដោយបញ្ចូលឧបករណ៍ច្រើនជាមួយគ្នា។
<span class='en-term'>Confluence</span> មានន័យថា ភស្តុតាងពី<b>ប្រភពផ្សេងគ្នា</b> ចង្អុលទៅទិសដូចគ្នា នៅកន្លែងដូចគ្នា។
ប៉ុន្តែមានអន្ទាក់ធំមួយ: <b>ការរាប់ភស្តុតាងតែមួយពីរដង</b> (<span class='en-term'>double-counting</span>) ដែលធ្វើឱ្យអ្នកជឿជាក់ខ្លាំងពេក។
យើងនឹងរៀនការបញ្ចូលគ្នាប្រាំយ៉ាង ច្បាប់រាប់ភស្តុតាង និងពេលដែល confluence <b>មិនគ្រប់គ្រាន់</b>។""",
    sections=[
        ("Confluence ពិតគឺជាអ្វី?", """
<p>ឧបករណ៍នីមួយៗ<b>វាស់រឿងមួយ</b>។ ដើម្បីដឹងថាភស្តុតាងពីរឯករាជ្យឬអត់ យើងដាក់ឧបករណ៍ជា<b>ក្រុម</b> (<span class='en-term'>family</span>):</p>
<table style='break-inside:avoid'><tr><th>Family</th><th>វាស់អ្វី</th><th>ឧបករណ៍</th></tr>
<tr><td><b>Context</b></td><td>ទិសធំ</td><td>HTF structure · bias (Ch 26)</td></tr>
<tr><td><b>Location</b></td><td>កន្លែងសំខាន់</td><td>Liquidity · FVG · OB · VAH/VAL/POC · trendline</td></tr>
<tr><td><b>Timing</b></td><td>ពេលសកម្ម</td><td>Kill zone London 14:00–17:00 · NY 19:00–22:00 (winter)</td></tr>
<tr><td><b>Participation</b></td><td>អ្នកចូលរួមពិត</td><td>Volume · delta · CVD (COMEX)</td></tr>
<tr><td><b>Trigger</b></td><td>ការបញ្ជាក់ចុងក្រោយ</td><td>MSS + displacement លើ LTF</td></tr>
<tr><td><b>Macro</b></td><td>កម្លាំងខាងក្រៅ</td><td>DXY · yields · 📰 News</td></tr></table>
""" + flow([("Context", "ទិស HTF", BL), ("Location", "កន្លែងណា", GOLD), ("Trigger", "LTF MSS", UP), ("Risk", "SL · R:R", DN)],
           caption="Confluence ល្អ = ភស្តុតាងពី family ផ្សេងៗគ្នា ហើយបញ្ចប់ដោយ risk ច្បាស់") + """
<div class='box tip'>💡 សំណួរសាកល្បង: "<b>បើឧបករណ៍ A ត្រូវ តើឧបករណ៍ B ត្រូវដោយស្វ័យប្រវត្តិឬទេ?</b>" បើត្រូវ វាជាភស្តុតាង<b>តែមួយ</b> មិនមែនពីរទេ។</div>
"""),
        ("ICT + Market Structure", """
<p>Setup ICT (sweep, FVG, OB) មានន័យតែនៅក្នុង<b>បរិបទ structure</b>។ ករណីល្អបំផុត: តម្លៃ sweep SSL នៅ discount ក្នុង HTF ឡើង
បន្ទាប់មកបង្កើត <span class='en-term'>MSS</span> ដោយ displacement ហើយទុក FVG សម្រាប់ចូល។</p>
""" + zigzag([70, 40, 58, 34, 46, 18, 54, 44, 68, 82], {3: ("SSL", UP), 4: ("LH", DN), 5: ("Sweep", OR), 6: ("MSS ↑", UP), 7: ("FVG entry", BL), 8: ("BOS", UP)},
             lines=[(46, 4, 7, "", UP, False), (34, 3, 6, "", OR, True)],
             caption="Sweep SSL → បិទលើ LH ចុងក្រោយ (MSS) → ត្រឡប់មក FVG → បន្តឡើង") + """
<table style='break-inside:avoid'><tr><th>Bullish FVG នៅ...</th><th>គុណភាព</th></tr>
<tr><td>HTF ឡើង + discount + ក្រោយ sweep SSL</td><td>✅ ស្របជាមួយ structure</td></tr>
<tr><td>HTF ឡើង + premium (ក្រោយ BSL ត្រូវបានយក)</td><td>⚠️ ថ្លៃ · គោលដៅខ្លី</td></tr>
<tr><td>Daily ធ្លាក់ + premium</td><td>❌ ប្រឆាំង trend · គុណភាពទាប</td></tr></table>
"""),
        ("ICT + Trendlines", """
<p>Trendline (Chapter 8) ដែលស្អាត និងប៉ះ <b>3 ដង</b> ឡើងទៅ ត្រូវបានអ្នក trade ជាច្រើនមើលឃើញ។ ពួកគេដាក់ stop នៅ<b>ក្រោមខ្សែ</b>
ដូច្នេះវាក្លាយជា <span class='en-term'>trendline liquidity</span>។ ICT មើលវាជាគោលដៅ: តម្លៃអាច sweep ក្រោមខ្សែ រួចត្រឡប់ឡើងវិញ។</p>
""" + trend_sweep(caption="ប៉ះខ្សែ 3 ដង → wick sweep stops ក្រោមខ្សែ (ផ្ទៃពណ៌ទឹកក្រូច) → MSS ឡើង = trendline liquidity sweep") + """
<ul><li><b>Sweep + ត្រឡប់ + MSS</b> → trend ដើមអាចបន្ត (ដូចរូប)</li>
<li><b>បំបែកដោយ displacement + បិទក្រោម + retest ពីក្រោម</b> → structure អាចផ្លាស់ប្ដូរពិតប្រាកដ</li></ul>
<div class='box warn'>⚠️ <b>Double-counting លាក់កំបាំង:</b> trendline ឡើងត្រូវបានគូរ<b>តាម HL</b> ដូច្នេះ "ប៉ះ trendline" និង "uptrend structure" ច្រើនតែជា
<b>ភស្តុតាងតែមួយ</b>។ Trendline ផ្ដល់តម្លៃបន្ថែម តែពេលវាប្រាប់<b>កន្លែង liquidity</b> ដែល structure មិនបានប្រាប់។</div>
<div class='box tip'>💡 Trendline ជារបស់ប្រធានបទ (subjective)។ គូរឱ្យដូចគ្នាជានិច្ច (body ឬ wick) ហើយផ្ដល់ទម្ងន់ទៅ trendline នៅ <b>4H / Daily</b> ច្រើនជាង 5m។</div>
"""),
        ("ICT + Volume Profile", """
<p>FVG និង OB ប្រាប់ពី<b>ភាពមិនស្មើនៃតម្លៃ</b> (price imbalance)។ Volume Profile ប្រាប់ពីកន្លែងដែល volume ត្រូវបាន<b>ទទួលយក</b>។
ពេលតំបន់ ICT ថ្មី ធ្លាក់ចំកម្រិត VP ចាស់ នោះជាភស្តុតាងពីរប្រភពខុសគ្នា។</p>
""" + ict_vp(caption="Bullish FVG/OB ចំ VAL ម្សិលមិញ · POC ប្រើជាគោលដៅ take profit") + """
<table style='break-inside:avoid'><tr><th>ការបញ្ចូលគ្នា</th><th>ឯករាជ្យ?</th><th>ហេតុផល</th></tr>
<tr><td>OB/FVG + VAL/VAH ថ្ងៃមុន</td><td>✅ ភាគច្រើនមែន</td><td>បង្កើតពីចលនា និងថ្ងៃខុសគ្នា</td></tr>
<tr><td>FVG + <span class='en-term'>LVN</span></td><td>⚠️ ច្រើនតែទេ</td><td>ចលនាលឿនតែមួយ បង្កើតទាំង FVG និង LVN</td></tr>
<tr><td>POC ជាគោលដៅ</td><td>✅ ប្រើសម្រាប់ TP</td><td>តម្លៃច្រើនតែត្រឡប់ទៅ "តម្លៃយុត្តិធម៌"</td></tr></table>
<div class='box warn'>⚠️ VP ត្រូវការ volume ពិត (COMEX futures · Chapter 25)។ បើប្រើ VP ពី GC ត្រូវដក <span class='en-term'>basis</span> មុនដាក់កម្រិតលើ MT5។</div>
"""),
        ("Volume Profile + Order Flow", """
<p>VP ប្រាប់ "<b>កន្លែងណា</b>"។ Order flow ប្រាប់ "<b>កំពុងកើតអ្វី</b>" នៅកន្លែងនោះ <b>ឥឡូវនេះ</b>។ ឧទាហរណ៍ bias ចុះ តម្លៃឡើងមកដល់ <b>VAH</b>:</p>
""" + bars([("1", 420, UP), ("2", 380, UP), ("3", 510, UP), ("4", 300, UP), ("5", -250, DN), ("6", -600, DN)],
           caption="ឧទាហរណ៍សម្រាប់ពន្យល់ (មិនមែនទិន្នន័យពិត): delta ទៀន 5m នៅ VAH · ទិញខ្លាំង (+) ប៉ុន្តែតម្លៃមិនឡើង = absorption → delta ប្ដូរជា (−)") + """
<table style='break-inside:avoid'><tr><th>នៅ VAH (bias ចុះ)</th><th>ការអាន</th></tr>
<tr><td>Delta វិជ្ជមានធំ ប៉ុន្តែតម្លៃនៅស្ងៀម</td><td><span class='en-term'>Absorption</span> · អ្នកលក់ limit កំពុងទទួល</td></tr>
<tr><td>តម្លៃ high ថ្មី · CVD មិនឡើង</td><td><span class='en-term'>Delta divergence</span> · ការទិញខ្សោយ</td></tr>
<tr><td>បិទលើ VAH + delta វិជ្ជមាន + នៅលើ</td><td><b>Acceptance</b> · bias ចុះអាចខុស</td></tr></table>
<div class='box warn'>⚠️ បើអ្នកគ្មាន feed COMEX ទេ <b>រំលង</b> layer នេះ។ កុំប្រើ tick volume របស់ MT5 ដូចជា bid/ask volume ពិត (Chapter 25)។</div>
"""),
        ("Liquidity + Displacement", """
<p>Sweep តែម្នាក់ឯង គ្រាន់តែប្រាប់ថា stop ត្រូវបានយក។ តម្លៃអាច<b>បន្តដើរ</b>ទៅមុខទៀត (នោះជា <span class='en-term'>run</span> មិនមែន sweep ទេ)។
<span class='en-term'>Displacement</span> ក្រោយ sweep បង្ហាញថា ភាគីម្ខាងទៀតបានចូលពិតប្រាកដ។</p>
""" + zigzag([62, 40, 52, 32, 26, 30, 22, 26, 12], {4: ("Sweep?", OR), 8: ("ធ្លាក់បន្ត", DN)},
             lines=[(32, 3, 7, "SSL", OR, True)],
             caption="ករណី A: យក SSL ប៉ុន្តែគ្មាន displacement ឡើង → ទៀនតូចៗ → ធ្លាក់បន្ត (run)") + zigzag(
    [62, 40, 52, 32, 18, 64, 54, 82], {4: ("Sweep", OR), 5: ("Displacement", UP), 6: ("FVG", BL)},
    lines=[(52, 2, 6, "MSS ↑", UP, False)],
    caption="ករណី B: យក SSL → ទៀនធំឡើងបិទលើ structure ហើយទុក FVG = sweep ពិត") + """
<table style='break-inside:avoid'><tr><th>Displacement ពិត ជាទូទៅមាន...</th></tr>
<tr><td>✅ ទៀន body ធំ (ធំជាង ATR) និង wick តូច</td></tr>
<tr><td>✅ បិទឆ្លង swing (MSS / BOS) មិនមែនត្រឹម wick</td></tr>
<tr><td>✅ ទុក FVG នៅពីក្រោយ</td></tr>
<tr><td>✅ ច្រើនតែកើតក្នុង kill zone ឬក្រោយព័ត៌មាន</td></tr></table>
"""),
        ("បញ្ចូលភស្តុតាងដោយមិនរាប់ពីរដង", """
<p>ការរាប់ពីរដង ធ្វើឱ្យ trade ធម្មតាមើលទៅដូចជា "A+"។ ឧទាហរណ៍ទូទៅ:</p>
<table style='break-inside:avoid'><tr><th>មើលទៅដូចជាច្រើនហេតុផល</th><th>ការពិត</th></tr>
<tr><td>EMA 20 + EMA 50 + MACD + RSI</td><td>Momentum <b>តែមួយ</b> វាស់ 4 ដង</td></tr>
<tr><td>FVG + OB នៅទៀនដដែល</td><td>ចលនា<b>តែមួយ</b></td></tr>
<tr><td>Trendline តាម HL + uptrend</td><td>Structure <b>តែមួយ</b></td></tr>
<tr><td>FVG + LVN ពីចលនាលឿនតែមួយ</td><td>ចលនា<b>តែមួយ</b></td></tr>
<tr><td>VWAP + EMA + 1H trend ស្របគ្នា</td><td>Trend filter ដែលច្រើនតែស្របគ្នារួចហើយ</td></tr></table>
""" + bars([("រាប់ធម្មតា", 6, GR), ("Family ពិត", 2, BL)],
           caption="ឧទាហរណ៍សម្រាប់ពន្យល់: setup មួយមើលទៅមាន 6 ហេតុផល ប៉ុន្តែមកពីតែ 2 family (Momentum + Location)") + """
<div class='box tip'>💡 <b>មេរៀនពីទិន្នន័យ XAU.KH:</b> ក្នុងការសាកល្បងរបស់ក្រុម VWAP + EMA + 1H trend បានស្របគ្នារួចហើយលើប្រហែល <b>97%</b> នៃសញ្ញា ⭐។
ការបន្ថែមវាជាលក្ខខណ្ឌ មិនបានបន្ថែម edge ទេ ព្រោះវាប្រាប់រឿងដែលយើងដឹងរួចហើយ។</div>
<div class='box ok'>✅ <b>ច្បាប់:</b> family នីមួយៗរាប់បាន<b>អតិបរមា 1 ពិន្ទុ</b>។ ហេតុផល <b>2–3 ឯករាជ្យ</b> + risk ច្បាស់ = គ្រប់គ្រាន់។</div>
"""),
        ("Confluence Scorecard: Gate និង Point", """
<p>ដាក់លក្ខខណ្ឌជាពីរប្រភេទ: <b>Gate</b> (ត្រូវតែមាន · បើខ្វះ = គ្មាន trade) និង <b>Point</b> (បន្ថែមគុណភាព)។</p>
""" + flow([("Gate 1", "មិនផ្ទុយ bias", BL), ("Gate 2", "គ្មាន 📰 ជិតៗ", DN), ("Points", "≥ 2 family", GOLD), ("Gate 3", "Trigger + R:R", UP)],
           caption="ឆ្លងកាត់ Gate ទាំង 3 ហើយមាន Point ពី family យ៉ាងតិច 2 → ទើបពិចារណា trade") + """
<table style='break-inside:avoid'><tr><th>ប្រភេទ</th><th>សំណួរ</th><th>ពិន្ទុ</th></tr>
<tr><td>Gate</td><td>Trade មិនផ្ទុយ bias Chapter 26?</td><td>ត្រូវតែ ✅</td></tr>
<tr><td>Gate</td><td>គ្មានព័ត៌មាន high-impact ក្នុង 30 នាទី?</td><td>ត្រូវតែ ✅</td></tr>
<tr><td>Point · Location</td><td>នៅ zone HTF (liquidity / OB / FVG / VP level)?</td><td>+1</td></tr>
<tr><td>Point · Timing</td><td>ក្នុង kill zone?</td><td>+1</td></tr>
<tr><td>Point · Participation</td><td>Order flow / volume បញ្ជាក់? (បើមានទិន្នន័យ)</td><td>+1</td></tr>
<tr><td>Point · Macro</td><td>DXY / yields ស្របទិស?</td><td>+1</td></tr>
<tr><td>Gate</td><td>LTF MSS + displacement · SL ក្រោយ invalidation · R:R ≥ 1:2</td><td>ត្រូវតែ ✅</td></tr></table>
<div class='box tip'>💡 ក្នុង group សញ្ញា 🚨 <b>Signals</b> មានការវិនិច្ឆ័យផ្ទាល់ខ្លួន (💎 A+ / ⭐ B+) តាមច្បាប់របស់ប្រព័ន្ធ។ Scorecard នេះសម្រាប់ការវិភាគ<b>របស់អ្នកផ្ទាល់</b>។
ប្រៀបធៀបការវិភាគរបស់អ្នកជាមួយ 📊 <b>Analysis</b> ហើយមើលលទ្ធផលពិតនៅ 📈 <b>Proof</b>។</div>
"""),
        ("ពេលដែល Confluence មិនគ្រប់គ្រាន់", """
<p>Setup អាចមានហេតុផលល្អៗជាច្រើន ប៉ុន្តែនៅតែ<b>មិនគួរ trade</b>:</p>
<ul><li>📰 ព័ត៌មានធំកំពុងមកដល់ (CPI, NFP, FOMC)</li>
<li>កម្រិត HTF ផ្ទុយទិស នៅ<b>ជិតពេក</b> → R:R តូច</li>
<li>Stop loss ធំពេកសម្រាប់គណនីរបស់អ្នក (Chapter 32)</li>
<li>តម្លៃបានរត់ឆ្ងាយពី zone រួចហើយ → ការដេញ (<span class='en-term'>chasing</span>)</li>
<li>អ្នកបន្ថែមហេតុផល <b>បន្ទាប់ពី</b>សម្រេចចិត្តរួច (<span class='en-term'>confirmation bias</span>)</li></ul>
<div class='box ok'>✅ ឧទាហរណ៍: Buy 4,072 · SL 4,064 ($8 = <b>80 pips</b>) · មាន 4 family ស្របគ្នា។ ប៉ុន្តែ 4H bearish FVG នៅ 4,084 ($12 = 120 pips)។
R:R = 12 ÷ 8 = <b>1.5</b> តូចជាង 1:2 → <b>រំលង</b> ឬរង់ចាំតម្លៃឆ្លង FVG នោះសិន។ ជាមួយ 0.01 lot: ហានិភ័យ $8 · គោលដៅ $12។</div>
<div class='box warn'>⚠️ Confluence បង្កើន<b>គុណភាព</b> នៃការសម្រេចចិត្ត មិនមែន<b>ភាពប្រាកដ</b>ទេ។ Trade ដែលមាន confluence ពេញលេញ ក៏នៅតែខាតបាន ហើយនោះជារឿងធម្មតា។
ការពារខ្លួនដោយ risk ថេរក្នុង trade នីមួយៗ មិនមែនដោយការរក "setup ល្អឥតខ្ចោះ" ទេ។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ដាក់ indicator 5 ប្រភេទដែលវាស់ momentum ដូចគ្នា ហើយហៅថា confluence</li>
<li>❌ រាប់ FVG និង OB នៅទៀនដដែលជា 2 ហេតុផល</li>
<li>❌ ចូលភ្លាមៗពេលឃើញ sweep ដោយមិនរង់ចាំ displacement និង MSS</li>
<li>❌ ប្រើ "order flow" ពី tick volume MT5</li>
<li>❌ មិនអើពើ R:R ព្រោះ "confluence ច្រើនណាស់"</li>
<li>❌ បន្ថែមលក្ខខណ្ឌរហូតដល់ស្ទើរតែគ្មាន trade (ហើយលទ្ធផលមិនល្អជាងមុន)</li></ul>
"""),
    ],
    summary=["Confluence = ភស្តុតាងពី family ផ្សេងគ្នា (Context · Location · Timing · Participation · Trigger · Macro)",
             "ICT ល្អបំផុតនៅក្នុងបរិបទ structure · trendline និង VP ផ្ដល់តម្លៃពេលវាប្រាប់កន្លែង liquidity ឬ value ថ្មី",
             "Sweep ត្រូវការ displacement + MSS · VP + Order flow = កន្លែង + អ្វីកំពុងកើតឥឡូវ",
             "Family នីមួយៗ អតិបរមា 1 ពិន្ទុ · 2–3 ហេតុផលឯករាជ្យ + risk ច្បាស់ = គ្រប់គ្រាន់",
             "Gate (bias · news · trigger + R:R) ត្រូវតែឆ្លង · confluence មិនធានាការឈ្នះ"],
    exercise=["យក setup ចុងក្រោយរបស់អ្នក ហើយសរសេរហេតុផលទាំងអស់។ ដាក់វាតាម family នីមួយៗ។ តើមានប៉ុន្មាន family ពិតប្រាកដ?",
              "រក trendline 4H ដែលប៉ះ 3 ដងលើមាស។ តើ stop នៅក្រោម (ឬលើ) ខ្សែនោះ ត្រូវបាន sweep រួចហើយឬនៅ?",
              "Buy 4,090 · SL 4,081 · កម្រិតផ្ទុយជិតបំផុត 4,105។ គិត pips និង R:R។ តើឆ្លង Gate 3 ទេ?",
              "ប្រើ Scorecard លើ 🚨 Signal បន្ទាប់ក្នុង group ហើយប្រៀបធៀបពិន្ទុរបស់អ្នកជាមួយលទ្ធផលនៅ 📈 Proof។"],
)
