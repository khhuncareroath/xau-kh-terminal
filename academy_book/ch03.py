from academy_pdf import flow

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"

# A small made-up price path (open, high, low, close) used by the inline diagrams below.
_OHLC = [(40, 52, 36, 50), (50, 58, 46, 55), (55, 57, 41, 44), (44, 49, 34, 37), (37, 48, 33, 46),
         (46, 62, 44, 60), (60, 66, 52, 54), (54, 70, 53, 68)]


def _fig(svg, caption):
    return f'<div class="fig">{svg}<div class="cap">{caption}</div></div>'


def _chart_types():
    """Same 8 periods drawn three ways: line, OHLC bars, candlesticks."""
    w, h, pw = 420, 170, 130
    Y = lambda v: h - 22 - v * (h - 50) / 80
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for k, name in enumerate(["Line chart", "Bar chart (OHLC)", "Candlestick"]):
        x0 = 10 + k * (pw + 10)
        out.append(f'<rect x="{x0}" y="6" width="{pw}" height="{h - 12}" rx="8" fill="#F7F7FA"/>')
        out.append(f'<text x="{x0 + pw / 2}" y="22" text-anchor="middle" class="lt" fill="#1C1C1E">{name}</text>')
        step = (pw - 20) / len(_OHLC)
        X = lambda i: x0 + 10 + (i + .5) * step
        if k == 0:
            d = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(c[3]):.1f}" for i, c in enumerate(_OHLC))
            out.append(f'<path d="{d}" fill="none" stroke="{BL}" stroke-width="2.2"/>')
        for i, (o, hi, lo, c) in enumerate(_OHLC):
            col = UP if c >= o else DN
            if k == 1:
                out.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.8"/>')
                out.append(f'<line x1="{X(i) - 4:.1f}" x2="{X(i):.1f}" y1="{Y(o):.1f}" y2="{Y(o):.1f}" stroke="{col}" stroke-width="1.8"/>')
                out.append(f'<line x1="{X(i):.1f}" x2="{X(i) + 4:.1f}" y1="{Y(c):.1f}" y2="{Y(c):.1f}" stroke="{col}" stroke-width="1.8"/>')
            if k == 2:
                out.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.3"/>')
                top, bot = Y(max(o, c)), Y(min(o, c))
                out.append(f'<rect x="{X(i) - 4.5:.1f}" y="{top:.1f}" width="9" height="{max(bot - top, 1.5):.1f}" rx="1.5" fill="{col}"/>')
    out.append("</svg>")
    return _fig("".join(out), "ទិន្នន័យដូចគ្នា គូរ 3 របៀប · Candlestick បង្ហាញ Open High Low Close ច្បាស់ជាងគេ")


def _candle_anatomy():
    w, h = 420, 190
    s = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for cx, col, o, c, name in [(120, UP, 130, 70, "Bullish (ឡើង)"), (300, DN, 70, 130, "Bearish (ធ្លាក់)")]:
        s.append(f'<line x1="{cx}" x2="{cx}" y1="30" y2="165" stroke="{col}" stroke-width="2"/>')
        s.append(f'<rect x="{cx - 18}" y="70" width="36" height="60" rx="3" fill="{col}"/>')
        s.append(f'<text x="{cx}" y="20" text-anchor="middle" class="bt" fill="{col}">{name}</text>')
        s.append(f'<text x="{cx + 26}" y="34" class="lt" fill="#1C1C1E">High</text>')
        s.append(f'<text x="{cx + 26}" y="168" class="lt" fill="#1C1C1E">Low</text>')
        s.append(f'<text x="{cx - 26}" y="{c + 4}" text-anchor="end" class="lt" fill="#1C1C1E">Close</text>')
        s.append(f'<text x="{cx - 26}" y="{o + 4}" text-anchor="end" class="lt" fill="#1C1C1E">Open</text>')
        s.append(f'<text x="{cx + 26}" y="104" class="st" fill="#6E6E73">Body (តួ)</text>')
        s.append(f'<text x="{cx + 26}" y="54" class="st" fill="#6E6E73">Wick (ក្បាល)</text>')
    s.append("</svg>")
    return _fig("".join(s), "ទៀនមួយគ្រាប់ = 4 តម្លៃ · លម្អិតនៅ Chapter 5")


def _mt5_layout():
    w, h = 420, 230
    s = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
         f'<rect x="8" y="8" width="{w - 16}" height="20" rx="5" fill="#E5E5EA"/>',
         '<text x="16" y="22" class="st" fill="#1C1C1E">File · View · Insert · Charts · Tools · Window · Help</text>']
    boxes = [(8, 34, 120, 92, BL, "Market Watch", "បញ្ជីតម្លៃ · Ctrl+M"),
             (8, 132, 120, 50, OR, "Navigator", "Account · Ctrl+N"),
             (134, 34, w - 142, 148, GOLD, "", ""),
             (8, 188, w - 16, 34, UP, "Toolbox", "Trade · History · Journal · Ctrl+T")]
    for x, y, bw, bh, col, t, sub in boxes:
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="7" fill="{col}" fill-opacity=".10" stroke="{col}" stroke-width="1.3"/>')
        if t:
            s.append(f'<text x="{x + 8}" y="{y + 15}" class="bt" fill="{col}">{t}</text>')
            s.append(f'<text x="{x + 8}" y="{y + 29}" class="st" fill="#6E6E73">{sub}</text>')
    for i, sym in enumerate(["XAUUSD", "EURUSD", "USDJPY"]):
        s.append(f'<text x="16" y="{78 + i * 15}" class="st" fill="#1C1C1E">{sym}</text>')
    s.append(f'<text x="142" y="49" class="bt" fill="{GOLD}">Chart · XAUUSD, M15</text>')
    Y = lambda v: 172 - v * 1.4
    for i, (o, hi, lo, c) in enumerate(_OHLC * 2):
        cx = 150 + i * 16
        col = UP if c >= o else DN
        s.append(f'<line x1="{cx}" x2="{cx}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.2"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        s.append(f'<rect x="{cx - 4}" y="{top:.1f}" width="8" height="{max(bot - top, 1.5):.1f}" fill="{col}"/>')
    s.append("</svg>")
    return _fig("".join(s), "ផ្ទាំង MT5 លើកុំព្យូទ័រ (គំនូរសាមញ្ញ) · Market Watch · Navigator · Chart · Toolbox")


def _tf_blocks():
    """One H1 candle = four M15 candles."""
    w, h = 420, 170
    m15 = [(40, 58, 36, 55), (55, 62, 48, 50), (50, 66, 47, 64), (64, 72, 60, 70)]
    Y = lambda v: h - 24 - v * 1.6
    s = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
         f'<text x="110" y="18" text-anchor="middle" class="bt" fill="{BL}">M15 · 4 ទៀន</text>',
         f'<text x="280" y="18" text-anchor="middle" class="bt" fill="{GOLD}">H1 · 1 ទៀន</text>']
    for i, (o, hi, lo, c) in enumerate(m15):
        cx = 50 + i * 40
        col = UP if c >= o else DN
        s.append(f'<line x1="{cx}" x2="{cx}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.6"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        s.append(f'<rect x="{cx - 10}" y="{top:.1f}" width="20" height="{max(bot - top, 2):.1f}" rx="2" fill="{col}"/>')
        s.append(f'<text x="{cx}" y="{h - 6}" text-anchor="middle" class="st" fill="#6E6E73">{["14:00", "14:15", "14:30", "14:45"][i]}</text>')
    s.append(f'<path d="M222,{Y(55):.1f} l26,0 m-6,-5 l6,5 l-6,5" stroke="{GR}" stroke-width="1.8" fill="none"/>')
    s.append(f'<line x1="280" x2="280" y1="{Y(72):.1f}" y2="{Y(36):.1f}" stroke="{UP}" stroke-width="2"/>')
    s.append(f'<rect x="260" y="{Y(70):.1f}" width="40" height="{Y(40) - Y(70):.1f}" rx="3" fill="{UP}"/>')
    s.append(f'<text x="280" y="{h - 6}" text-anchor="middle" class="st" fill="#6E6E73">14:00–15:00</text>')
    s.append(f'<text x="308" y="{Y(70) + 4:.1f}" class="st" fill="#1C1C1E">Close = M15 ចុងក្រោយ</text>')
    s.append(f'<text x="308" y="{Y(40) + 4:.1f}" class="st" fill="#1C1C1E">Open = M15 ទីមួយ</text>')
    s.append("</svg>")
    return _fig("".join(s), "High H1 = High ខ្ពស់បំផុតនៃ M15 ទាំង 4 · Low H1 = Low ទាបបំផុត")


CH = dict(
    ch=3, part="PART 1 · Foundations",
    title_km="ស្គាល់ Platform សម្រាប់ Trade", title_en="Understanding Trading Platforms",
    intro="""មុននឹងអាន chart ឬបើក order យើងត្រូវស្គាល់<b>ឧបករណ៍</b>ជាមុនសិន។ Platform គឺជាកម្មវិធីដែលបង្ហាញតម្លៃមាស
គូរ chart និងភ្ជាប់អ្នកទៅកាន់ broker។ ក្នុងជំពូកនេះ អ្នកនឹងរៀនពី <b>MetaTrader 5 (MT5)</b> ដែល XAU.KH ណែនាំ
ស្គាល់ <b>TradingView</b> ជាឧបករណ៍មើល chart ការរក symbol <b>XAUUSD</b> ក្នុង <b>Market Watch</b>
ការប្ដូរ <b>timeframe</b> និងការរៀបចំ chart ឱ្យស្អាត ងាយអាន។ គោលដៅ: ចប់ជំពូកនេះ អ្នកអាចបើក chart មាសបានត្រឹមត្រូវ
ដោយមិនច្រឡំ symbol ឬម៉ោង។""",
    sections=[
        ("Platform គឺជាអ្វី? Chart Tool និង Trading Platform", """
<p>Platform មាន<b>តួនាទីពីរ</b>ដែលអ្នកចាប់ផ្ដើមដំបូងច្រើនតែច្រឡំ:</p>
<ul><li><b>មើល និងវិភាគ chart</b>: បង្ហាញតម្លៃ គូរ level គូរ trendline។</li>
<li><b>បើក និងបិទ order ពិត</b>: ផ្ញើបញ្ជាទិញ/លក់ទៅ broker ហើយបង្ហាញចំណេញ/ខាតក្នុងគណនី។</li></ul>
""" + flow([("អ្នក", "សម្រេចចិត្ត BUY/SELL", BL), ("MT5", "ផ្ញើ order", GOLD), ("Broker", "ប្រតិបត្តិ order", OR), ("គណនី", "P/L · Balance", UP)],
           caption="Order ពិតធ្វើដំណើរពី MT5 ទៅ broker · Platform គ្រាន់តែជា \"ផ្លូវ\"") + """
<p><b>MT5</b> ធ្វើបានទាំងពីរ: មើល chart និងបើក order ជាមួយ broker។ <span class='en-term'>TradingView</span>
ជាកម្មវិធីមើល chart មួយទៀតដែលមនុស្សជាច្រើនប្រើសម្រាប់វិភាគ។ អ្នកមិនចាំបាច់ប្រើទាំងពីរទេ។</p>
<div class='box ok'>✅ XAU.KH ណែនាំ <b>MT5</b> ព្រោះ chart និង order នៅកន្លែងតែមួយ ហើយតម្លៃដែលអ្នកឃើញ គឺជាតម្លៃពិតរបស់ broker អ្នក
ដែល SL/TP របស់អ្នកនឹងត្រូវប៉ះ។ សញ្ញា 🚨 Signals របស់យើងប្រើតម្លៃ XAUUSD ដែលអ្នកអាចវាយបញ្ចូលក្នុង MT5 ភ្លាមៗ។</div>
"""),
        ("MetaTrader 5 និង TradingView: ប្រៀបធៀប", """
<table><tr><th></th><th>MetaTrader 5</th><th>TradingView</th></tr>
<tr><td>តួនាទីសំខាន់</td><td>Trade ពិត + chart</td><td>Chart និងការវិភាគ</td></tr>
<tr><td>តម្លៃ</td><td>ពី broker របស់អ្នកផ្ទាល់</td><td>ពីប្រភពទិន្នន័យរបស់វា (អាចខុសពី broker បន្តិច)</td></tr>
<tr><td>Order ពិត</td><td>បាន ជាមួយ broker ណាមួយដែលគាំទ្រ MT5</td><td>អាស្រ័យលើការភ្ជាប់ broker</td></tr>
<tr><td>ឧបករណ៍</td><td>ទូរស័ព្ទ · កុំព្យូទ័រ · web</td><td>ទូរស័ព្ទ · កុំព្យូទ័រ · web</td></tr>
<tr><td>Demo account</td><td>មាន (បើកពី broker)</td><td>Paper trading</td></tr></table>
<div class='box warn'>⚠️ តម្លៃមាសនៅ chart ផ្សេងៗអាចខុសគ្នា ពីរបីសេន ដល់ច្រើនដុល្លារ (ពិសេស chart futures)។ ពេលដាក់ SL/TP
សូម<b>ប្រើតម្លៃនៅ MT5 របស់ broker អ្នក</b>ជានិច្ច មិនមែនតម្លៃពី chart ផ្សេងទេ។</div>
<div class='box tip'>💡 XAU.KH មិនមែនជាដៃគូ ឬភ្នាក់ងាររបស់ platform ឬ broker ណាមួយទេ។ ជ្រើសរើស broker ដែលមានអាជ្ញាប័ណ្ណ ហើយសាកល្បងជាមួយ
<b>demo account</b> ជាមុន។</div>
"""),
        ("ស្គាល់ផ្ទាំង MT5 លើកុំព្យូទ័រ", """
<p>ពេលបើក MT5 លើកុំព្យូទ័រ អ្នកនឹងឃើញផ្ទាំងសំខាន់ៗ <b>4</b>:</p>
""" + _mt5_layout() + """
<table><tr><th>ផ្ទាំង</th><th>ប្រើសម្រាប់</th><th>Shortcut</th></tr>
<tr><td><span class='en-term'>Market Watch</span></td><td>បញ្ជី symbol និងតម្លៃ Bid/Ask ផ្ទាល់</td><td>Ctrl+M</td></tr>
<tr><td><span class='en-term'>Navigator</span></td><td>គណនី indicator និង EA</td><td>Ctrl+N</td></tr>
<tr><td><span class='en-term'>Chart</span></td><td>ក្រាហ្វតម្លៃ គូរ level</td><td>—</td></tr>
<tr><td><span class='en-term'>Toolbox</span></td><td>Order កំពុងបើក (Trade) ប្រវត្តិ (History) Journal</td><td>Ctrl+T</td></tr>
<tr><td><span class='en-term'>Data Window</span></td><td>បង្ហាញ Open High Low Close នៃទៀនដែល mouse ចង្អុល</td><td>Ctrl+D</td></tr></table>
"""),
        ("MT5 លើទូរស័ព្ទ", """
<p>សមាជិកភាគច្រើន trade លើទូរស័ព្ទ។ កម្មវិធី MT5 (Android / iPhone) មានផ្ទាំងសំខាន់ៗនៅខាងក្រោមអេក្រង់:</p>
""" + flow([("Quotes", "តម្លៃ · រក symbol", BL), ("Chart", "ក្រាហ្វ · timeframe", GOLD), ("Trade", "Order · P/L", UP), ("History", "Trade ចាស់ៗ", GR)],
           caption="ផ្ទាំងសំខាន់ៗ 4 នៃ MT5 mobile (មាន Messages និង Settings ផងដែរ)") + """
<ul><li><b>Quotes</b>: ចុច <b>+</b> ដើម្បីបន្ថែម symbol · ចុចលើ XAUUSD ដើម្បីបើក chart ឬ trade។</li>
<li><b>Chart</b>: ចុចលើ chart ម្ដង ដើម្បីបង្ហាញម៉ឺនុយ timeframe (M1 … MN) និង indicator។</li>
<li><b>Trade</b>: មើល Balance, Equity, Margin និង order ដែលកំពុងបើក។ ចុចយូរលើ order ដើម្បីកែ SL/TP ឬបិទ។</li>
<li><b>History</b>: មើលលទ្ធផល trade ចាស់ៗ សម្រាប់កត់ត្រាក្នុង journal (Chapter 37)។</li></ul>
<div class='box tip'>💡 លើទូរស័ព្ទ អេក្រង់តូច ដូច្នេះកុំដាក់ indicator ច្រើន។ ប្រើ chart ស្អាតៗ ហើយមើលរូប 📊 Analysis ក្នុង group សម្រាប់ level ដែលបានគូររួច។</div>
"""),
        ("Market Watch និង Symbol", """
<p><span class='en-term'>Symbol</span> គឺជាឈ្មោះកូដនៃទ្រព្យដែលអ្នក trade។ មាសធៀបនឹងដុល្លារ គឺ <b>XAUUSD</b>។ ប៉ុន្តែ broker ខ្លះបន្ថែម
<span class='en-term'>suffix</span> (អក្សរបន្ទាប់) ទៅតាមប្រភេទគណនី:</p>
<table><tr><th>ឈ្មោះ symbol ដែលអាចឃើញ</th><th>អត្ថន័យ</th></tr>
<tr><td><b>XAUUSD</b></td><td>ឈ្មោះស្តង់ដារ</td></tr>
<tr><td>XAUUSDm · XAUUSD.r · XAUUSD+ …</td><td>XAUUSD ដូចគ្នា តែសម្រាប់ប្រភេទគណនីផ្សេង</td></tr>
<tr><td>GOLD</td><td>Broker ខ្លះប្រើឈ្មោះនេះជំនួស XAUUSD</td></tr>
<tr><td>XAUEUR · XAUJPY</td><td><b>មិនមែន</b>មាសធៀបដុល្លារទេ · កុំប្រើ</td></tr></table>
<p><b>របៀបរក:</b> ក្នុង Market Watch ចុចកណ្ដុរស្ដាំ → <span class='en-term'>Symbols</span> (ឬ Ctrl+U) → វាយ "XAU" → ជ្រើស → <b>Show</b>។
លើទូរស័ព្ទ: Quotes → <b>+</b> → វាយ "XAU"។</p>
<div class='box warn'>⚠️ ត្រូវប្រាកដថា symbol ដែលអ្នកមើលក្នុង chart គឺ<b>ដូចគ្នា</b>នឹង symbol ដែលអ្នកបើក order។ ការមើល XAUUSD តែបើក order លើ symbol
ផ្សេង គឺជាកំហុសដែលកើតឡើងពិតៗ។</div>
<div class='box tip'>💡 ចុចកណ្ដុរស្ដាំលើ XAUUSD → <span class='en-term'>Specification</span> ដើម្បីមើល contract size, lot អប្បបរមា, ម៉ោង trade និង swap។
យើងនឹងអានវានៅ Chapter 4។</div>
"""),
        ("Candlestick Chart: ហេតុអ្វីយើងប្រើវា", """
<p>MT5 អាចគូរ chart បាន 3 របៀប: <span class='en-term'>Bar chart</span> (Alt+1), <span class='en-term'>Candlestick</span> (Alt+2) និង
<span class='en-term'>Line chart</span> (Alt+3)។</p>
""" + _chart_types() + """
<p><b>Line chart</b> ភ្ជាប់តែតម្លៃបិទ (Close) ដូច្នេះវាលាក់ព័ត៌មានសំខាន់ៗ។ <b>Candlestick</b> បង្ហាញតម្លៃទាំង 4 នៃរយៈពេលនីមួយៗ:</p>
""" + _candle_anatomy() + """
<ul><li><b>ទៀនពណ៌បៃតង (bullish)</b>: Close ខ្ពស់ជាង Open = តម្លៃឡើងក្នុងរយៈពេលនោះ។</li>
<li><b>ទៀនពណ៌ក្រហម (bearish)</b>: Close ទាបជាង Open = តម្លៃធ្លាក់។</li>
<li><b>Wick</b> (ក្បាល/កន្ទុយ) បង្ហាញថាតម្លៃបានទៅដល់ទីនោះ ប៉ុន្តែត្រូវគេរុញត្រឡប់វិញ។</li></ul>
<div class='box ok'>✅ រាល់រូប 📊 Analysis និង /check របស់ XAU.KH ប្រើ candlestick ដូចគ្នានឹង MT5។</div>
"""),
        ("Timeframe: ទៀនមួយ = រយៈពេលប៉ុន្មាន?", """
<p><span class='en-term'>Timeframe</span> គឺជារយៈពេលនៃទៀន<b>មួយគ្រាប់</b>។ នៅ M15 ទៀនមួយ = 15 នាទី។ នៅ H4 ទៀនមួយ = 4 ម៉ោង។</p>
""" + _tf_blocks() + """
<table><tr><th>កូដ</th><th>ទៀនមួយ</th><th>XAU.KH ប្រើសម្រាប់</th></tr>
<tr><td>MN · W1 · D1</td><td>ខែ · សប្ដាហ៍ · ថ្ងៃ</td><td>ទិសដៅធំ និង level ធំៗ</td></tr>
<tr><td>H4</td><td>4 ម៉ោង</td><td>Bias និងសញ្ញា ⭐</td></tr>
<tr><td>H1 · M30</td><td>1 ម៉ោង · 30 នាទី</td><td>រចនាសម្ព័ន្ធកណ្ដាល</td></tr>
<tr><td>M15</td><td>15 នាទី</td><td>រូប 📊 Analysis</td></tr>
<tr><td>M5 · M1</td><td>5 នាទី · 1 នាទី</td><td>ចំណុច entry (ឃើញ noise ច្រើន)</td></tr></table>
<p>លើកុំព្យូទ័រ ប្ដូរ timeframe ពីរបារខាងលើ ឬចុចកណ្ដុរស្ដាំលើ chart → <span class='en-term'>Timeframes</span>។ MT5 មាន timeframe ច្រើនជាង 20
ប៉ុន្តែអ្នកត្រូវការតែ<b>ពីរបី</b>ប៉ុណ្ណោះ។</p>
<div class='box tip'>💡 Timeframe ធំ = ទិសដៅធំ និងគួរឱ្យទុកចិត្តជាង។ Timeframe តូច = លម្អិត តែមាន noise ច្រើន។ របៀបប្រើជាមួយគ្នា (top-down) នៅ Chapter 6។</div>
"""),
        ("ធ្វើដំណើរលើ Chart និង Setting", """
<p>Chart ដែលស្អាត ជួយឱ្យអ្នកឃើញតម្លៃច្បាស់ ហើយកាត់បន្ថយកំហុស។ Shortcut ដែលមានប្រយោជន៍លើ MT5 កុំព្យូទ័រ:</p>
<table><tr><th>ធ្វើអ្វី</th><th>របៀប</th></tr>
<tr><td>Zoom ចូល / ចេញ</td><td>ចុច <b>+</b> / <b>−</b> ឬរមូរកង់កណ្ដុរ</td></tr>
<tr><td>រំកិល chart ទៅអតីតកាល</td><td>អូសដោយកណ្ដុរ ឬចុចព្រួញ ← →</td></tr>
<tr><td>ទៅទៀនចុងក្រោយ</td><td>ចុច <b>End</b> · បើក <span class='en-term'>Auto Scroll</span></td></tr>
<tr><td>Crosshair (វាស់តម្លៃ/ចម្ងាយ)</td><td>ចុចកង់កណ្ដុរ ឬ Ctrl+F</td></tr>
<tr><td>ការកំណត់ chart</td><td>ចុច <b>F8</b> (Properties)</td></tr></table>
""" + flow([("F8 Properties", "បើកការកំណត់", BL), ("Colors", "ទៀន 2 ពណ៌ច្បាស់", UP), ("Show", "បិទ Grid · Ask line", GOLD), ("Template", "Save ទុកប្រើវិញ", OR)],
           caption="រៀបចំ chart ម្ដង ហើយ save ជា template") + """
<ul><li><b>បើក Show Ask line</b>: MT5 គូរ chart ដោយតម្លៃ <b>Bid</b>។ Ask line បង្ហាញតម្លៃដែលអ្នកទិញ (Chapter 4)។</li>
<li><b>បិទ Grid</b> និង indicator ដែលមិនប្រើ ដើម្បីឱ្យឃើញតម្លៃច្បាស់។</li>
<li><b>Chart shift</b>: ទុកចន្លោះទំនេរនៅខាងស្ដាំ ដើម្បីឃើញទៀនថ្មី និង level ខាងមុខ។</li></ul>
<div class='box warn'>⚠️ Chart ដែលពោរពេញដោយ indicator 5–6 មិនធ្វើឱ្យអ្នកឆ្លាតជាងទេ។ វាច្រើនតែផ្ដល់សញ្ញាផ្ទុយគ្នា ហើយធ្វើឱ្យស្ទាក់ស្ទើរ។</div>
"""),
        ("ម៉ោង Server និងម៉ោងកម្ពុជា", """
<p>MT5 បង្ហាញម៉ោងទៀនតាម<b>ម៉ោង server របស់ broker</b> មិនមែនម៉ោងទូរស័ព្ទអ្នកទេ។ Broker ជាច្រើនប្រើ GMT+2 ឬ GMT+3 ខណៈពេលដែលកម្ពុជា
គឺ <b>GMT+7</b>។ ដូច្នេះម៉ោងលើ chart អាចយឺតជាងម៉ោងកម្ពុជា ប្រហែល 4–5 ម៉ោង ឬច្រើនជាងនេះ អាស្រ័យលើ broker និងរដូវ។</p>
<table><tr><th>ឧទាហរណ៍</th><th>ម៉ោង server</th><th>ម៉ោងកម្ពុជា</th></tr>
<tr><td>Server GMT+2</td><td>10:00</td><td>15:00 (+5)</td></tr>
<tr><td>Server GMT+3</td><td>10:00</td><td>14:00 (+4)</td></tr>
<tr><td>Server GMT+0</td><td>10:00</td><td>17:00 (+7)</td></tr></table>
<div class='box tip'>💡 របៀបពិនិត្យ: មើលម៉ោងនៅ Market Watch (ម៉ោង server) ធៀបនឹងម៉ោងទូរស័ព្ទ ហើយចងចាំលេខខុសគ្នា។
ម៉ោង session និងព័ត៌មានក្នុង group XAU.KH (📰 News) តែងតែសរសេរជា<b>ម៉ោងកម្ពុជា</b>។</div>
"""),
        ("ជំហានដំបូង និងកំហុសញឹកញាប់", """
<p><b>Checklist មុនពេល trade ដំបូង:</b></p>
<ul><li>☐ ដំឡើង MT5 ហើយបើក <b>demo account</b></li>
<li>☐ រក XAUUSD ត្រឹមត្រូវ (រួមទាំង suffix) ក្នុង Market Watch</li>
<li>☐ ប្ដូរទៅ candlestick, បិទ grid, បើក Ask line, save template</li>
<li>☐ សាកប្ដូរ timeframe D1 → H4 → M15 → M5</li>
<li>☐ ដឹងពីលេខខុសគ្នារវាងម៉ោង server និងម៉ោងកម្ពុជា</li></ul>
<p><b>កំហុសញឹកញាប់:</b></p>
<ul><li>❌ ប្រៀបធៀបតម្លៃពី chart មួយ ទៅ SL នៅ broker មួយទៀត</li>
<li>❌ បើក order លើ symbol ខុស (XAUEUR ជំនួស XAUUSD)</li>
<li>❌ ច្រឡំម៉ោង server ជាម៉ោងកម្ពុជា ហើយ trade ចំម៉ោងព័ត៌មាន</li>
<li>❌ Trade លុយពិតភ្លាមៗ មុនពេលស្គាល់ប៊ូតុងក្នុង platform</li></ul>
<div class='box ok'>✅ ចំណាយពេល 1–2 សប្ដាហ៍លើ demo ដើម្បីស្គាល់ platform ឱ្យស្ទាត់ គឺមិនខាតពេលទេ។ វាការពារកំហុស "ចុចខុស" ដែលខាតលុយពិត។</div>
"""),
    ],
    summary=["MT5 = chart + order ពិតជាមួយ broker · XAU.KH ណែនាំ MT5",
             "ប្រើតម្លៃ XAUUSD នៅ MT5 របស់ broker អ្នកសម្រាប់ SL/TP ជានិច្ច",
             "Market Watch: រក XAUUSD (ឬ XAUUSDm, GOLD …) · ពិនិត្យ Specification",
             "Candlestick បង្ហាញ Open High Low Close · timeframe = រយៈពេលនៃទៀនមួយ",
             "Chart ស្អាត + ដឹងម៉ោង server ធៀបនឹងម៉ោងកម្ពុជា (GMT+7)"],
    exercise=["បើក MT5 demo ហើយរក symbol មាសរបស់ broker អ្នក។ តើវាឈ្មោះអ្វីពិតប្រាកដ?",
              "ចុចកណ្ដុរស្ដាំ (ឬចុចលើ symbol លើទូរស័ព្ទ) → Specification។ តើ contract size និង lot អប្បបរមាប៉ុន្មាន?",
              "ម៉ោង server របស់ broker អ្នកខុសពីម៉ោងកម្ពុជាប៉ុន្មានម៉ោង?",
              "បើក chart M15 ធៀបនឹងរូប 📊 Analysis ចុងក្រោយក្នុង group។ តើតម្លៃខុសគ្នាប៉ុន្មានសេន?"],
)
