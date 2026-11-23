from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def order_map(w=420, h=200, caption=""):
    """Current price in the middle; the four pending order types placed above and below it."""
    mid = h / 2
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="20" x2="{w - 20}" y1="{mid}" y2="{mid}" stroke="#1C1C1E" stroke-width="2"/>',
           f'<text x="{w / 2:.0f}" y="{mid - 6}" text-anchor="middle" fill="#1C1C1E" class="pt">តម្លៃឥឡូវ 4,060</text>']
    rows = [(30, "Sell Limit", "លក់ពេលឡើងមកដល់", DN, 70), (62, "Buy Stop", "ទិញពេលឆ្លងឡើង", UP, 240),
            (h - 62, "Buy Limit", "ទិញពេលធ្លាក់មកដល់", UP, 70), (h - 30, "Sell Stop", "លក់ពេលឆ្លងចុះ", DN, 240)]
    for y, t, sub, col, x in rows:
        out.append(f'<line x1="{x - 50}" x2="{x + 110}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        out.append(f'<text x="{x - 48}" y="{y - 5}" fill="{col}" class="lt">{t}</text>')
        out.append(f'<text x="{x + 108}" y="{y - 5}" text-anchor="end" fill="#6E6E73" class="st">{sub}</text>')
    out.append(f'<text x="{w - 22}" y="22" text-anchor="end" fill="{GR}" class="st">លើតម្លៃ ↑</text>')
    out.append(f'<text x="{w - 22}" y="{h - 10}" text-anchor="end" fill="{GR}" class="st">ក្រោមតម្លៃ ↓</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def timeline(w=420, h=150, caption=""):
    """24h Phnom Penh clock: Asia (quiet), London kill zone, NY kill zone, daily break."""
    X = lambda hr: 16 + hr * (w - 32) / 24
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="{X(0):.1f}" x2="{X(24):.1f}" y1="70" y2="70" stroke="#C7C7CC" stroke-width="2"/>']
    for a, b, t, col, y in [(7, 14, "Asia · ស្ងាត់", GR, 40), (14, 17, "London", BL, 40), (19, 22, "NY", UP, 40), (4, 6, "Break", DN, 100)]:
        out.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="22" rx="5" fill="{col}" fill-opacity=".22" stroke="{col}"/>')
        out.append(f'<text x="{(X(a) + X(b)) / 2:.1f}" y="{y + 15}" text-anchor="middle" fill="#1C1C1E" class="st">{t}</text>')
    out.append(f'<rect x="{X(19.3):.1f}" y="100" width="{X(20.2) - X(19.3):.1f}" height="22" rx="5" fill="{OR}" fill-opacity=".3" stroke="{OR}"/>')
    out.append(f'<text x="{X(19.3) - 4:.1f}" y="115" text-anchor="end" fill="{OR}" class="st">📰 20:30 (ច្រើនតែ US data)</text>')
    for hr in range(0, 25, 4):
        out.append(f'<text x="{X(hr):.1f}" y="{142}" text-anchor="middle" fill="{GR}" class="st">{hr:02d}:00</text>')
        out.append(f'<line x1="{X(hr):.1f}" x2="{X(hr):.1f}" y1="66" y2="74" stroke="{GR}"/>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def late_entry(w=420, h=180, caption=""):
    """Entry zone vs TP1: price already travelled most of the way -> skip."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    lv = [(40, "TP1 4,080", UP), (100, "", GR), (140, "Entry 4,060", BL), (166, "SL 4,052", DN)]
    for y, t, col in lv:
        if t:
            out.append(f'<line x1="20" x2="{w - 20}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
            out.append(f'<text x="{w - 22}" y="{y - 4}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    out.append(f'<rect x="20" y="40" width="{w - 40}" height="50" fill="{DN}" fill-opacity=".08"/>')
    out.append(f'<text x="30" y="70" fill="{DN}" class="st">តំបន់ "យឺតពេក" (ហួសពាក់កណ្ដាលទៅ TP1)</text>')
    pts = [(30, 150), (70, 138), (100, 150), (140, 116), (180, 124), (230, 78), (260, 86), (300, 62)]
    out.append('<path d="' + " ".join(f"{'M' if k == 0 else 'L'}{x},{y}" for k, (x, y) in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="100" cy="150" r="3.4" fill="{BL}"/><text x="100" y="135" text-anchor="middle" fill="{BL}" class="pt">✓ ទាន់</text>')
    out.append(f'<circle cx="300" cy="62" r="3.4" fill="{DN}"/><text x="335" y="58" text-anchor="middle" fill="{DN}" class="pt">✗ ដេញ</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=29, part="PART 7 · Trade Execution",
    title_km="បច្ចេកទេសចូល Trade", title_en="Entry Techniques: Market, Limit, Stop, Confirmation and Refined Entries",
    intro="""Chapter 28 ប្រាប់ពី <span class='en-term'>setup</span>: <b>កន្លែង</b>និង<b>ហេតុផល</b>។ ជំពូកនេះចាប់ផ្ដើម PART 7 ហើយប្រាប់ពី<b>របៀប</b>ចូលពិតប្រាកដ។
Setup ដូចគ្នា តែវិធីចូលខុសគ្នា អាចផ្ដល់លទ្ធផលខុសគ្នាខ្លាំង: SL ធំ ឬតូច · បាន fill ឬខកខាន · R:R ល្អ ឬអាក្រក់។
យើងនឹងរៀន order ប្រាំប្រភេទ ពេលវេលាចូល និងច្បាប់សំខាន់មួយ: <b>កុំដេញតម្លៃ</b>។ គ្រប់ឧទាហរណ៍ប្រើ <b>MT5</b>។""",
    sections=[
        ("ការចូលជាផ្នែកមួយនៃផែនការ", """
<p>មុនចុចប៊ូតុង អ្នកត្រូវដឹងរួចហើយនូវ: <b>ចូលនៅណា</b> · <b>SL នៅណា</b> · <b>TP នៅណា</b> · <b>lot ប៉ុន្មាន</b>។
វិធីចូលត្រូវបានជ្រើសរើស<b>មុន</b>តម្លៃមកដល់ មិនមែនពេលអារម្មណ៍ឡើងខ្លាំង។</p>
""" + flow([("Setup", "Ch 28", BL), ("ជ្រើស order", "market/limit/stop", GOLD), ("SL + lot", "Ch 30 · 32", DN), ("ចុច · កត់ត្រា", "journal", UP)],
           caption="លំដាប់ត្រឹមត្រូវ: setup → វិធីចូល → risk → ប្រតិបត្តិ") + """
<table style='break-inside:avoid'><tr><th>ប្រភេទ</th><th>ពេលណាចូល</th><th>MT5</th></tr>
<tr><td><b>Market</b></td><td>ភ្លាមៗ តម្លៃបច្ចុប្បន្ន</td><td>Buy / Sell</td></tr>
<tr><td><b>Limit</b></td><td>តម្លៃត្រឡប់មកល្អជាងឥឡូវ</td><td>Buy Limit / Sell Limit</td></tr>
<tr><td><b>Stop</b></td><td>តម្លៃឆ្លងកម្រិតមួយ</td><td>Buy Stop / Sell Stop</td></tr>
<tr><td><b>Confirmation</b></td><td>ក្រោយទៀនបិទ ឬ MSS</td><td>Market ក្រោយការបញ្ជាក់</td></tr>
<tr><td><b>Refined</b></td><td>ចូលលើ timeframe តូចជាង</td><td>Limit ឬ market លើ LTF</td></tr></table>
"""),
        ("Market Entry · ចូលភ្លាម", """
<p><span class='en-term'>Market order</span> ចូលភ្លាមនៅតម្លៃបច្ចុប្បន្ន។ <b>Buy</b> ចូលនៅតម្លៃ <span class='en-term'>Ask</span> · <b>Sell</b> ចូលនៅតម្លៃ <span class='en-term'>Bid</span>។
ដូច្នេះអ្នកចាប់ផ្ដើមដោយ "ខាត" spread បន្តិចជានិច្ច។</p>
<ul><li>✅ ប្រាកដថាបានចូល · ល្អសម្រាប់ breakout ខ្លាំង</li>
<li>⚠️ <span class='en-term'>Slippage</span>: ពេលទីផ្សារលឿន (📰 News) តម្លៃ fill អាចខុសពីតម្លៃដែលអ្នកឃើញ</li>
<li>⚠️ Spread ធំពេលបើកទីផ្សារ ម៉ោង break ឬព័ត៌មាន</li></ul>
<div class='box ok'>✅ ឧទាហរណ៍: Bid 4,060.00 · Ask 4,060.30 → spread $0.30 = <b>3 pips</b>។ Buy 0.01 lot ចូលនៅ 4,060.30។
តម្លៃ Bid ត្រូវឡើងដល់ 4,060.30 ទើប break-even។ ខាតដំបូង = $0.30។</div>
<div class='box tip'>💡 សញ្ញា ⭐ ក្នុង 🚨 <b>Signals</b> ជាប្រភេទ market entry: ចូល<b>ក្នុងរយៈពេល 15 នាទី</b>ក្រោយសញ្ញាចេញ។ បើយឺតជាងនេះ មើលផ្នែក "ការចូលយឺត" ខាងក្រោម។</div>
"""),
        ("Limit Entry · រង់ចាំតម្លៃល្អជាង", """
<p><span class='en-term'>Limit order</span> = ទិញ<b>ថោកជាង</b> ឬលក់<b>ថ្លៃជាង</b>តម្លៃបច្ចុប្បន្ន។ ប្រើសម្រាប់ចូលនៅ zone (FVG · OB · VAL) ដែលអ្នកគ្រោងទុក។</p>
""" + order_map(caption="Order រង់ចាំទាំង 4 លើ MT5 · Limit = តម្លៃត្រឡប់មករក · Stop = តម្លៃឆ្លងកាត់") + """
<table style='break-inside:avoid'><tr><th>គុណសម្បត្តិ</th><th>គុណវិបត្តិ</th></tr>
<tr><td>តម្លៃចូលល្អ · SL តូច · R:R ធំ</td><td>ប្រហែល<b>មិនបាន fill</b> (តម្លៃមិនមកដល់)</td></tr>
<tr><td>មិនចាំបាច់អង្គុយមើលអេក្រង់</td><td>Fill ពេលតម្លៃ<b>រត់ឆ្លងកាត់</b> zone (ស្ទើរតែខាតភ្លាម)</td></tr>
<tr><td>គ្មាន slippage (fill នៅតម្លៃ limit ឬល្អជាង)</td><td>ងាយធ្វើការចូលដែល "ចាប់កាំបិត" ប្រឆាំងនឹង momentum</td></tr></table>
<div class='box warn'>⚠️ ការពិតពីការសាកល្បងរបស់ក្រុម XAU.KH: <b>OB limit + SL ក្រោម OB</b> លើមាស ផ្ដល់លទ្ធផល<b>ខាត</b>។ Limit entry មិនមែនអាក្រក់ទេ ប៉ុន្តែ zone តែម្នាក់ឯងមិនគ្រប់គ្រាន់ (Chapter 28)។</div>
"""),
        ("Stop Entry · ចូលពេលឆ្លងកម្រិត", """
<p><span class='en-term'>Buy Stop</span> ដាក់<b>លើ</b>តម្លៃ · <span class='en-term'>Sell Stop</span> ដាក់<b>ក្រោម</b>តម្លៃ។ វាចូលតែពេលតម្លៃបង្ហាញ momentum ឆ្លងកម្រិត ដូចជា high នៃ range ឬ swing។</p>
""" + zigzag([40, 62, 44, 63, 46, 62, 50, 64, 84, 78, 92], {7: ("Buy Stop", BL), 8: ("Fill", UP)},
             lines=[(66, 1, 6, "Range high", BL, True), (44, 2, 9, "SL", DN, False)],
             caption="Buy Stop លើ range high + buffer តូច → fill តែពេលតម្លៃឆ្លងពិត · SL ក្រោម range ឬ HL") + """
<ul><li>✅ មិនចាំបាច់ទាយ · ចូលតែពេល momentum ពិតបង្ហាញខ្លួន</li>
<li>⚠️ <b>Fake breakout</b>: តម្លៃឆ្លងបន្តិច fill រួចត្រឡប់វិញ (ជា liquidity sweep · Chapter 28)</li>
<li>⚠️ Slippage ធំ ប្រសិនបើ stop order ត្រូវបាន fill ពេលព័ត៌មានចេញ</li></ul>
<div class='box tip'>💡 ដាក់ buffer បន្តិច (ឧ. $0.50–$1 = 5–10 pips) លើ high ដើម្បីជៀសវាង fill ដោយ wick តូច និង spread។ ទំហំ buffer អាស្រ័យលើ volatility នៅពេលនោះ។</div>
"""),
        ("Confirmation Entry · រង់ចាំការបញ្ជាក់", """
<p>មិនចូលភ្លាមនៅពេលតម្លៃដល់ zone ទេ។ រង់ចាំ<b>ភស្តុតាង</b>ថាតម្លៃមានប្រតិកម្មពិត: <b>ទៀនបិទ</b>ត្រឡប់ · <span class='en-term'>CHOCH</span> / MSS លើ 5m · ឬ displacement។</p>
""" + zigzag([80, 52, 64, 40, 50, 28, 40, 34, 56, 46, 70], {5: ("ដល់ zone", OR), 6: ("LH", DN), 8: ("CHOCH 5m", UP), 9: ("Entry", BL)},
             lines=[(40, 6, 9, "", UP, True), (28, 5, 9, "", DN, False)],
             caption="ដល់ zone → មិនចូលទេ → រង់ចាំបិទលើ LH ចុងក្រោយ (CHOCH) → ចូលនៅ pullback · SL ក្រោម low") + """
<table style='break-inside:avoid'><tr><th></th><th>Limit នៅ zone</th><th>Confirmation</th></tr>
<tr><td>តម្លៃចូល</td><td>ល្អបំផុត</td><td>យឺតជាង (ថ្លៃជាង)</td></tr>
<tr><td>SL</td><td>តូច</td><td>ធំជាងបន្តិច ឬស្មើ</td></tr>
<tr><td>Trade ខុសដែលចៀសបាន</td><td>តិច</td><td><b>ច្រើន</b> (zone ដែលបរាជ័យមិនផ្ដល់ CHOCH)</td></tr>
<tr><td>Trade ល្អដែលខកខាន</td><td>តិច</td><td>ខ្លះ (តម្លៃរត់ដោយគ្មាន pullback)</td></tr></table>
<div class='box ok'>✅ សម្រាប់អ្នកចាប់ផ្ដើម confirmation entry ច្រើនតែ<b>សុវត្ថិភាពជាង</b> ព្រោះវាបង្ខំឱ្យអ្នករង់ចាំ ហើយកាត់បន្ថយ trade ប្រឆាំង momentum។</div>
"""),
        ("Refined Entry · ចូលលើ Timeframe តូច", """
<p><span class='en-term'>Refined entry</span> = setup លើ 4H/1H ប៉ុន្តែចូលលើ 5m/1m ដើម្បីបាន<b>SL តូចជាង</b>។ ហានិភ័យជាប្រាក់ដដែល ប៉ុន្តែ R:R ធំជាង។</p>
""" + bars([("1H entry SL", 120, OR), ("5m refined SL", 50, BL)], unit=" pips",
           caption="ឧទាហរណ៍ setup ដូចគ្នា: SL $12 (120 pips) លើ 1H ធៀបនឹង SL $5 (50 pips) លើ 5m · TP ដដែល $30") + """
<table style='break-inside:avoid'><tr><th></th><th>1H entry</th><th>5m refined</th></tr>
<tr><td>SL</td><td>$12 = 120 pips</td><td>$5 = 50 pips</td></tr>
<tr><td>TP</td><td>$30</td><td>$30</td></tr>
<tr><td>R:R</td><td>1 : 2.5</td><td>1 : 6</td></tr>
<tr><td>Risk $10 → lot</td><td>≈ 0.008 → <b>0.01</b> (ហានិភ័យពិត $12)</td><td>0.02 (ហានិភ័យ $10)</td></tr></table>
<div class='box warn'>⚠️ R:R ធំលើក្រដាស ≠ ល្អជាងជានិច្ច។ SL តូចត្រូវបាន<b>ប៉ះញឹកញាប់ជាង</b> ដោយ noise និង spread របស់មាស ហើយអ្នកខកខាន trade ច្រើនជាង។
វាស់ក្នុង journal របស់អ្នក មុនសន្និដ្ឋាន។ កុំបង្កើន lot ហួសច្បាប់ risk ដោយសារតែ SL តូច (Chapter 32)។</div>
"""),
        ("ពេលវេលាចូល · Entry Timing", """
<p>កន្លែងល្អ ប៉ុន្តែពេលអាក្រក់ អាចធ្វើឱ្យ setup ល្អខាតបាន។ ម៉ោងខាងក្រោមជាម៉ោងកម្ពុជា (រដូវរងា · ម៉ោងអាចប្ដូរ 1 ម៉ោងតាម daylight saving)។</p>
""" + timeline(caption="Kill zone London 14:00–17:00 · NY 19:00–22:00 · break ប្រចាំថ្ងៃប្រហែល 04:00–06:00 · ទិន្នន័យ US ច្រើនតែ 20:30") + """
<ul><li>✅ ចូលក្នុង <b>kill zone</b> ពេល liquidity ច្រើន និង spread តូច</li>
<li>⛔ ជៀសវាង <b>15–30 នាទី មុន និងក្រោយ</b> ព័ត៌មានធំ (CPI · NFP · FOMC) · មើល 📰 <b>News</b></li>
<li>⛔ ជៀសវាងជិតម៉ោង break ប្រចាំថ្ងៃ: spread ធំ តម្លៃលោតខុសធម្មតា</li>
<li>⚠️ ថ្ងៃសុក្រយប់ ជិតបិទទីផ្សារ: ហានិភ័យ <span class='en-term'>gap</span> ថ្ងៃចន្ទ</li></ul>
<div class='box tip'>💡 ម៉ោងព័ត៌មានពិតប្រាកដប្រែប្រួល។ ពិនិត្យ 📰 News ក្នុង group រៀងរាល់ព្រឹក មុនរៀបចំផែនការ។</div>
"""),
        ("ជៀសវាងការចូលយឺត · Avoiding Late Entries", """
<p>ការចូលយឺតបំផ្លាញ R:R។ SL នៅកន្លែងដដែល (កន្លែង idea ខុស) ប៉ុន្តែ TP ខិតមកជិត ដូច្នេះអ្នកប្រថុយ<b>ច្រើន</b>ដើម្បីបាន<b>តិច</b>។</p>
""" + late_entry(caption="Entry 4,060 · SL 4,052 · TP1 4,080 · បើតម្លៃនៅ 4,074 រួចហើយ ការចូលនៅពេលនោះ = ដេញ") + """
<table style='break-inside:avoid'><tr><th>ចូលនៅ</th><th>SL $</th><th>TP1 $</th><th>R:R</th></tr>
<tr><td>4,060 (ទាន់ពេល)</td><td>8</td><td>20</td><td><b>1 : 2.5</b> ✅</td></tr>
<tr><td>4,068 (យឺត)</td><td>16</td><td>12</td><td>1 : 0.75 ⚠️</td></tr>
<tr><td>4,074 (ដេញ)</td><td>22</td><td>6</td><td>1 : 0.27 ❌</td></tr></table>
<div class='box ok'>✅ <b>ច្បាប់សាមញ្ញ:</b> បើតម្លៃបានដើរ<b>ហួសពាក់កណ្ដាល</b>ផ្លូវទៅ TP1 រួចហើយ ឬ R:R ពីតម្លៃបច្ចុប្បន្នតូចជាង 1:1 → <b>រំលង</b>។ សញ្ញាបន្ទាប់នឹងមកដល់។</div>
<div class='box tip'>💡 ក្នុងការសាកល្បងរបស់ក្រុម ការរង់ចាំ <b>retest</b> ក្រោយ breakout ខ្លាំង <b>អាក្រក់ជាង</b>ការចូលភ្លាម ព្រោះ breakout ល្អច្រើនតែមិនត្រឡប់មក។
ដូច្នេះ "ចូលទាន់ពេល ឬរំលង" ល្អជាង "រង់ចាំ ហើយដេញពេលក្រោយ"។</div>
"""),
        ("ជ្រើសវិធីចូលណា? · Checklist", """
""" + flow([("ប្រភេទ Setup", "ជាអ្វី?", BL), ("Breakout", "market / stop", UP), ("Pullback", "limit / confirm", GOLD), ("ពិនិត្យ", "news · R:R", DN)],
           caption="ប្រភេទ setup ជួយជ្រើសវិធីចូល") + """
<table style='break-inside:avoid'><tr><th>Setup (Ch 28)</th><th>វិធីចូលសមរម្យ</th></tr>
<tr><td>BOS continuation · 4H breakout</td><td>Market ក្រោយទៀនបិទ ឬ Buy/Sell Stop</td></tr>
<tr><td>FVG retracement · OB</td><td>Confirmation នៅក្នុង zone ឬ limit (ដឹងហានិភ័យ)</td></tr>
<tr><td>Liquidity sweep reversal</td><td>Confirmation (MSS) → entry នៅ pullback</td></tr>
<tr><td>POC / VAH / VAL</td><td>Confirmation (ទៀនបិទត្រឡប់ចូល value)</td></tr></table>
<div class='box ok'>✅ <b>Checklist មុនចុច:</b> ① setup ត្រូវច្បាប់ ② វិធីចូលបានគ្រោងទុក ③ គ្មាន 📰 ក្នុង 30 នាទី ④ spread ធម្មតា ⑤ SL + TP + lot បានគិតរួច ⑥ R:R ≥ 1:2 ពីតម្លៃចូលពិត</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ដេញតម្លៃបន្ទាប់ពីឃើញទៀនធំ ("FOMO")</li>
<li>❌ ដាក់ limit order ហើយភ្លេចវា រហូតដល់វា fill ពេលព័ត៌មានចេញ</li>
<li>❌ ច្រឡំ Buy Limit និង Buy Stop លើ MT5 (fill ភ្លាមនៅតម្លៃខុស)</li>
<li>❌ ចូលភ្លាមពេលតម្លៃប៉ះ zone ដោយគ្មាន trigger</li>
<li>❌ ប្ដូរ refined entry ទៅជាហេតុផលបង្កើន lot ហួស risk</li>
<li>❌ មិនគិត spread ពេលគណនា R:R</li></ul>
<div class='box tip'>💡 មុន trade ពិត សាកល្បង order ទាំង 4 ប្រភេទនៅលើ<b>គណនី demo MT5</b> ដើម្បីឱ្យដៃស្គាល់ប៊ូតុង។</div>
"""),
    ],
    summary=["វិធីចូលត្រូវបានជ្រើសរើស<b>មុន</b>តម្លៃមកដល់ · ជាផ្នែកមួយនៃផែនការ",
             "Market = ប្រាកដថាចូល (spread · slippage) · Limit = តម្លៃល្អ តែអាចមិន fill ឬ fill ពេលរត់ឆ្លង",
             "Stop = ចូលពេលឆ្លងកម្រិត (ប្រយ័ត្ន fake breakout) · Confirmation = យឺតជាង តែចៀស zone ដែលបរាជ័យ",
             "Refined entry បន្ថយ SL តែប៉ះញឹកជាង · ចូលក្នុង kill zone · ជៀសព័ត៌មាន និងម៉ោង break",
             "ហួសពាក់កណ្ដាលទៅ TP1 ឬ R:R &lt; 1:1 → រំលង · កុំដេញ"],
    exercise=["បើក MT5 demo ហើយដាក់ Buy Limit · Sell Limit · Buy Stop · Sell Stop មួយៗ។ សរសេរថាតើ order នីមួយៗនឹង fill ពេលណា។",
              "Sell entry 4,095 · SL 4,103 · TP1 4,079។ តម្លៃឥឡូវ 4,086។ គិត R:R ពីតម្លៃឥឡូវ។ តើគួរចូល ឬរំលង?",
              "Setup 1H: SL $10 · TP $25។ លើ 5m អ្នករកបាន SL $4។ ជាមួយ risk $8 គិត lot និង R:R សម្រាប់ទាំងពីរ។",
              "កត់ត្រាម៉ោងនៃ 🚨 Signals ក្នុងមួយសប្ដាហ៍។ តើភាគច្រើនចេញក្នុង London ឬ NY kill zone? តើមានប៉ុន្មានដែលជិត 📰 News?"],
)
