from academy_pdf import flow

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def candles(cs, marks=None, levels=None, caption="", w=420, h=180):
    """Candlestick diagram. cs = [(open, high, low, close)] in 0-100. marks = {index: (text, colour)} above/below the candle.
    levels = [(y, text, colour)] dashed horizontal lines."""
    marks, levels = marks or {}, levels or []
    n = len(cs)
    step = (w - 40) / n
    X = lambda i: 20 + (i + .5) * step
    Y = lambda v: h - 22 - v * (h - 44) / 100
    bw = min(step * .55, 34)
    s = [f'<div class="fig"><svg viewBox="0 0 {w} {h}" class="dia">']
    for y, t, col in levels:
        s.append(f'<line x1="12" x2="{w - 12}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        s.append(f'<text x="14" y="{Y(y) - 4:.1f}" class="lt" fill="{col}">{t}</text>')
    for i, (o, hi, lo, c) in enumerate(cs):
        col = UP if c > o else DN if c < o else GR
        s.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.8"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        s.append(f'<rect x="{X(i) - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 2):.1f}" rx="2" fill="{col}"/>')
    for i, (t, col) in marks.items():
        hi = cs[i][1]
        s.append(f'<text x="{X(i):.1f}" y="{max(Y(hi) - 6, 12):.1f}" text-anchor="middle" class="pt" fill="{col}">{t}</text>')
    s.append("</svg>")
    if caption:
        s.append(f'<div class="cap">{caption}</div>')
    s.append("</div>")
    return "".join(s)


def _ohlc():
    w, h = 420, 200
    s = [f'<div class="fig"><svg viewBox="0 0 {w} {h}" class="dia">']
    for cx, col, o, c, name in [(110, UP, 140, 80, "Bullish"), (300, DN, 80, 140, "Bearish")]:
        s.append(f'<text x="{cx}" y="20" text-anchor="middle" class="bt" fill="{col}">{name}</text>')
        s.append(f'<line x1="{cx}" x2="{cx}" y1="36" y2="180" stroke="{col}" stroke-width="2"/>')
        s.append(f'<rect x="{cx - 20}" y="80" width="40" height="60" rx="3" fill="{col}"/>')
        for y, t in [(40, "High"), (o + 4, "Open"), (c + 4, "Close"), (183, "Low")]:
            s.append(f'<text x="{cx - 28}" y="{y}" text-anchor="end" class="lt" fill="#1C1C1E">{t}</text>')
        s.append(f'<text x="{cx + 28}" y="62" class="st" fill="#6E6E73">Upper wick</text>')
        s.append(f'<text x="{cx + 28}" y="114" class="st" fill="#6E6E73">Body</text>')
        s.append(f'<text x="{cx + 28}" y="164" class="st" fill="#6E6E73">Lower wick</text>')
    s.append('</svg><div class="cap">Bullish: Open នៅក្រោម Close នៅលើ · Bearish: Open នៅលើ Close នៅក្រោម</div></div>')
    return "".join(s)


CH = dict(
    ch=5, part="PART 1 · Foundations",
    title_km="ស្គាល់ទៀន Candlestick", title_en="Understanding Candlesticks",
    intro="""ទៀន (<span class='en-term'>candlestick</span>) គឺជា<b>ភាសា</b>នៃ chart។ ទៀននីមួយៗប្រាប់រឿងខ្លីមួយ:
តើអ្នកទិញ (<span class='en-term'>buyers</span>) ឬអ្នកលក់ (<span class='en-term'>sellers</span>) ឈ្នះក្នុងរយៈពេលនោះ ហើយឈ្នះខ្លាំងប៉ុណ្ណា?
ក្នុងជំពូកនេះ អ្នកនឹងរៀនអាន <b>Open High Low Close</b>, body និង wick, ហើយស្គាល់ទៀនសំខាន់ៗ:
<b>rejection, pin bar, engulfing, inside bar</b>។ ចំណុចសំខាន់បំផុត: ទៀនមួយគ្រាប់<b>គ្មានន័យ</b>ទេ បើយើងមិនមើលថាវានៅ<b>កន្លែងណា</b>។""",
    sections=[
        ("Open, High, Low និង Close", """
<p>ទៀនមួយគ្រាប់សង្ខេបតម្លៃ<b>ទាំង 4</b> ក្នុងរយៈពេលមួយ timeframe (ឧ. 15 នាទីនៅ M15):</p>
<table><tr><th>តម្លៃ</th><th>អត្ថន័យ</th></tr>
<tr><td><span class='en-term'>Open</span></td><td>តម្លៃនៅពេលទៀនចាប់ផ្ដើម</td></tr>
<tr><td><span class='en-term'>High</span></td><td>តម្លៃខ្ពស់បំផុតក្នុងរយៈពេលនោះ</td></tr>
<tr><td><span class='en-term'>Low</span></td><td>តម្លៃទាបបំផុតក្នុងរយៈពេលនោះ</td></tr>
<tr><td><span class='en-term'>Close</span></td><td>តម្លៃនៅពេលទៀនបិទ (សំខាន់បំផុត)</td></tr></table>
""" + _ohlc() + """
<div class='box tip'>💡 ទៀនដែលកំពុងរត់ (ទៀនចុងក្រោយ) <b>មិនទាន់មាន Close</b> ទេ។ វាអាចប្ដូរពណ៌ និងរូបរាងរហូតដល់វិនាទីចុងក្រោយ។
ដូច្នេះយើងវិនិច្ឆ័យទៀនតែ<b>បន្ទាប់ពីវាបិទ</b>។</div>
"""),
        ("ទៀន Bullish និង Bearish", """
<ul><li><b>Bullish</b> (បៃតង): Close <b>ខ្ពស់ជាង</b> Open → buyers ឈ្នះក្នុងរយៈពេលនោះ។</li>
<li><b>Bearish</b> (ក្រហម): Close <b>ទាបជាង</b> Open → sellers ឈ្នះ។</li>
<li><b>Doji</b>: Close ស្ទើរតែស្មើ Open → គ្មាននរណាឈ្នះ ទីផ្សារស្ទាក់ស្ទើរ។</li></ul>
""" + candles([(30, 62, 26, 58), (58, 64, 30, 34), (45, 60, 32, 46)], marks={0: ("Bullish", UP), 1: ("Bearish", DN), 2: ("Doji", GR)},
              caption="ពណ៌ប្រាប់ថានរណាឈ្នះ · ទំហំ body ប្រាប់ថាឈ្នះខ្លាំងប៉ុណ្ណា") + """
<div class='box warn'>⚠️ ទៀនបៃតងមួយគ្រាប់ <b>មិនមែន</b>មានន័យថាត្រូវ BUY ទេ។ ក្នុង downtrend ខ្លាំង ទៀនបៃតងច្រើនតែជា pullback តូចៗប៉ុណ្ណោះ។</div>
"""),
        ("Body និង Wick: អានកម្លាំង", """
<p><span class='en-term'>Body</span> (តួ) បង្ហាញ<b>ការឈ្នះពិត</b> ពី Open ទៅ Close។ <span class='en-term'>Wick</span> (ក្បាល/កន្ទុយ ឬ shadow)
បង្ហាញកន្លែងដែលតម្លៃ<b>បានទៅ</b> ប៉ុន្តែ<b>មិនអាចនៅបាន</b>។</p>
""" + candles([(20, 82, 18, 80), (40, 50, 34, 44), (60, 92, 54, 62), (60, 66, 16, 64)],
              marks={0: ("Body ធំ", UP), 1: ("Body តូច", GR), 2: ("Wick លើវែង", DN), 3: ("Wick ក្រោមវែង", UP)},
              caption="Body ធំ = កម្លាំងច្បាស់ · Body តូច = ស្ទាក់ស្ទើរ · Wick វែង = ការបដិសេធ") + """
<table><tr><th>រូបរាង</th><th>អត្ថន័យ</th></tr>
<tr><td>Body ធំ wick តូច</td><td>ភាគីមួយគ្រប់គ្រងទាំងស្រុង (<span class='en-term'>momentum</span>)</td></tr>
<tr><td>Body តូច wick ទាំងសងខាង</td><td>ស្ទាក់ស្ទើរ ទីផ្សាររង់ចាំ</td></tr>
<tr><td>Wick <b>លើ</b>វែង</td><td>តម្លៃខ្ពស់ត្រូវបានបដិសេធ: sellers រុញចុះវិញ</td></tr>
<tr><td>Wick <b>ក្រោម</b>វែង</td><td>តម្លៃទាបត្រូវបានបដិសេធ: buyers រុញឡើងវិញ</td></tr></table>
"""),
        ("Rejection Candle: ការបដិសេធតម្លៃ", """
<p><span class='en-term'>Rejection candle</span> គឺជាទៀនដែលមាន wick វែង ឆ្ពោះទៅកាន់ level មួយ ហើយបិទ<b>ឆ្ងាយ</b>ពី level នោះ។
វាប្រាប់ថាតម្លៃបានសាកល្បង level ហើយ<b>ត្រូវបានរុញត្រឡប់</b>។</p>
""" + candles([(70, 74, 52, 56), (56, 60, 42, 46), (46, 50, 34, 40), (40, 44, 12, 42), (42, 58, 40, 56), (56, 70, 54, 68)],
              marks={3: ("Rejection", UP)}, levels=[(20, "Support", BL)],
              caption="Wick ក្រោមវែងចាក់ចូល support ហើយបិទខ្ពស់វិញ = buyers ការពារ level") + """
<div class='box tip'>💡 Rejection កាន់តែមានន័យ បើ wick <b>វែងជាង body 2 ដង</b> ឡើងទៅ ហើយកើតឡើងនៅ level សំខាន់ (support, resistance, Asia high/low)។
នៅរូប 📊 Analysis សញ្ញា <b>$$</b> (liquidity sweep) ច្រើនតែជា wick rejection ប្រភេទនេះ (Chapter 12)។</div>
"""),
        ("Pin Bar", """
<p><span class='en-term'>Pin bar</span> គឺជា rejection candle ប្រភេទច្បាស់មួយ: <b>body តូច</b> នៅចុងម្ខាង និង <b>wick វែងមួយ</b> នៅម្ខាងទៀត
(ដូចម្ជុល)។</p>
<ul><li><b>Bullish pin bar</b> (ឬ <span class='en-term'>hammer</span>): wick ក្រោមវែង body នៅខាងលើ → buyers បដិសេធតម្លៃទាប។</li>
<li><b>Bearish pin bar</b> (ឬ <span class='en-term'>shooting star</span>): wick លើវែង body នៅខាងក្រោម → sellers បដិសេធតម្លៃខ្ពស់។</li></ul>
""" + candles([(30, 44, 26, 40), (40, 56, 36, 52), (52, 66, 48, 62), (62, 94, 58, 60), (60, 62, 44, 46), (46, 48, 30, 34)],
              marks={3: ("Bearish pin", DN)}, levels=[(88, "Resistance", DN)],
              caption="Bearish pin bar នៅ resistance បន្ទាប់ពីតម្លៃឡើង") + """
<table><tr><th>លក្ខណៈ Pin bar ល្អ</th><th>ហេតុអ្វី</th></tr>
<tr><td>Wick ≥ 2–3 ដងនៃ body</td><td>ការបដិសេធច្បាស់</td></tr>
<tr><td>Body នៅចុងម្ខាង (1/3)</td><td>បិទឆ្ងាយពី level</td></tr>
<tr><td>Wick ចាក់ហួស level ឬ swing ចាស់</td><td>បានយក stop/liquidity</td></tr>
<tr><td>ទៀនបន្ទាប់បញ្ជាក់ទិស</td><td>មិនមែនការបដិសេធបណ្ដោះអាសន្ន</td></tr></table>
"""),
        ("Engulfing Candle", """
<p><span class='en-term'>Engulfing</span> កើតឡើងនៅពេល <b>body</b> នៃទៀនថ្មី <b>គ្របដណ្ដប់</b> body នៃទៀនមុនទាំងស្រុង ក្នុងទិសផ្ទុយ។
វាបង្ហាញថាភាគីម្ខាងទៀតបាន<b>ដណ្ដើមការគ្រប់គ្រង</b>យ៉ាងលឿន។</p>
""" + candles([(80, 84, 62, 66), (66, 70, 50, 54), (54, 58, 40, 44), (44, 46, 34, 38), (36, 66, 34, 62), (62, 76, 60, 74)],
              marks={4: ("Bullish engulfing", UP)}, levels=[(32, "Support", BL)],
              caption="ទៀនបៃតងទី 2 គ្រប body ក្រហមទី 1 ទាំងស្រុង នៅ support") + """
<ul><li><b>Bullish engulfing</b>: ទៀនក្រហមតូច ហើយទៀនបៃតងធំគ្រប → សញ្ញាឡើង (ល្អបំផុតនៅ support ក្នុង uptrend)។</li>
<li><b>Bearish engulfing</b>: ទៀនបៃតងតូច ហើយទៀនក្រហមធំគ្រប → សញ្ញាធ្លាក់ (ល្អបំផុតនៅ resistance ក្នុង downtrend)។</li></ul>
<div class='box tip'>💡 Engulfing ដែលធំខ្លាំង និងបំបែក swing តូចមួយ ជាប់ទាក់ទងនឹង <b>displacement</b> និង <b>CHOCH</b> ដែលអ្នកនឹងរៀននៅ Chapter 9។</div>
"""),
        ("Inside Bar", """
<p><span class='en-term'>Inside bar</span> គឺជាទៀនដែល High និង Low ទាំងមូលនៅ<b>ក្នុង</b>ជួរនៃទៀនមុន (ហៅថា <span class='en-term'>mother bar</span>)។
វាបង្ហាញថាទីផ្សារ<b>សម្រាក និងប្រមូលកម្លាំង</b> (<span class='en-term'>consolidation</span>)។</p>
""" + candles([(48, 56, 44, 52), (50, 82, 32, 76), (70, 74, 52, 58), (58, 68, 50, 64), (64, 94, 62, 90)],
              marks={1: ("Mother", BL), 4: ("Breakout", UP)},
              levels=[(82, "Mother high", BL), (32, "Mother low", GR)],
              caption="Inside bars នៅក្នុងជួរ mother bar · រង់ចាំការបិទទៀនបំបែកចេញ") + """
<div class='box warn'>⚠️ Inside bar ខ្លួនឯង<b>មិនប្រាប់ទិស</b>ទេ។ ការបំបែកចេញអាចទៅទាំងលើ ឬក្រោម ហើយជួនកាលបំបែកមិនពិត (fake breakout)។
ប្រើវាតែជាមួយទិសនៃ timeframe ធំ និង level ច្បាស់។</div>
"""),
        ("អានទៀនក្នុង Context: កន្លែងសំខាន់ជាងរូបរាង", """
<p>ទៀនដូចគ្នាអាចមានន័យខុសគ្នាទាំងស្រុង អាស្រ័យលើ<b>កន្លែង</b>ដែលវាកើត។ មុននឹងជឿទៀនមួយ សួរសំណួរ 3 នេះ:</p>
""" + flow([("Trend", "HTF ទិសណា?", BL), ("Level", "នៅ S/R ឬ swing?", GOLD), ("Candle", "Rejection/Engulfing?", OR), ("Confirm", "ទៀនបន្ទាប់ស្រប", UP)],
           caption="Context ជាមុន ទៀនជាក្រោយ") + """
<table><tr><th>ទៀន</th><th>Context ល្អ</th><th>Context ខ្សោយ</th></tr>
<tr><td>Bullish pin bar</td><td>នៅ support ក្នុង uptrend</td><td>កណ្ដាល range គ្មាន level</td></tr>
<tr><td>Bearish engulfing</td><td>នៅ resistance ក្នុង downtrend</td><td>ប្រឆាំង trend ខ្លាំងនៅ HTF</td></tr>
<tr><td>Inside bar breakout</td><td>បំបែកតាមទិស HTF</td><td>មុនព័ត៌មានធំ</td></tr></table>
<div class='box ok'>✅ ទៀនមួយគឺជា<b>ភស្តុតាង</b> មិនមែនជាហេតុផលតែមួយគត់ក្នុងការចូល trade ទេ។ យើងនឹងបញ្ចូលវាជាមួយ structure, liquidity និង level
ក្នុង <b>Confluence Framework</b> (Chapter 27)។</div>
"""),
        ("ទៀនលើ Timeframe ផ្សេងៗ និងកំហុសញឹកញាប់", """
<p>ទៀន H1 មួយគ្រាប់ = ទៀន M15 ចំនួន 4។ Pin bar លើ H1 អាចមើលទៅដូចជាទៀនធ្លាក់ 2 គ្រាប់ ហើយឡើង 2 គ្រាប់លើ M15។ ទៀននៅ
<b>timeframe ធំ</b> មានទម្ងន់ច្រើនជាង ព្រោះវាតំណាងឱ្យការជួញដូរច្រើនជាង។</p>
<ul><li>❌ វិនិច្ឆ័យទៀនមុនពេលវាបិទ</li>
<li>❌ ទន្ទេញឈ្មោះលំនាំ 30 ប្រភេទ ប៉ុន្តែមិនមើល level និង trend</li>
<li>❌ យក pin bar លើ M1 មកប្រឆាំងនឹង trend H4</li>
<li>❌ ចូលភ្លាមៗលើ wick វែងពេលព័ត៌មាន (wick ពេលព័ត៌មានច្រើនតែមិនមានន័យ)</li></ul>
<div class='box tip'>💡 លំហាត់ល្អ: ប្រើ <b>/check</b> ក្នុង group ដើម្បីទទួលរូប chart ពិត ហើយរកទៀន rejection ឬ engulfing នៅជិត level ដែលបានគូរ។</div>
"""),
    ],
    summary=["ទៀន = Open High Low Close · វិនិច្ឆ័យតែក្រោយទៀនបិទ",
             "Body ធំ = កម្លាំង · Wick វែង = ការបដិសេធតម្លៃ",
             "Pin bar = wick វែងមួយ body តូច · Engulfing = body ថ្មីគ្រប body មុន",
             "Inside bar = សម្រាក/ប្រមូលកម្លាំង · រង់ចាំការបំបែក",
             "Context (trend + level) សំខាន់ជាងរូបរាងទៀន"],
    exercise=["បើក chart មាស H1: រក pin bar 2 និង engulfing 2 ក្នុង 3 ថ្ងៃចុងក្រោយ។ តើវានៅ level ឬនៅកណ្ដាល?",
              "ទៀន M15 មួយ: Open 4,052, High 4,058, Low 4,040, Close 4,055។ តើវាជាទៀនប្រភេទអ្វី? Wick ណាវែង?",
              "រក inside bar មួយលើ H4 ហើយមើលថាវាបំបែកទៅទិសណា។ ស្របនឹង trend D1 ឬអត់?",
              "ប្រើ /check ក្នុង group ហើយពិពណ៌នាទៀន 3 គ្រាប់ចុងក្រោយ (ពណ៌ body wick)។"],
)
