from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"

# A made-up sequence of 40 trade results (in R), only to draw an equity curve for learning.
DEMO_R = [1, -1, 2, -1, -1, 1, 3, -1, -1, -1, -1, 2, 1, -1, 3, -1, 2, -1, -1, 1,
          -1, -1, -1, -1, -1, 3, 1, 2, -1, 3, -1, 1, -1, 2, 1, -1, -1, 3, -1, 2]


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def _dd(rs):
    eq, peak, best = [0], 0, (0, 0, 0)          # best = (depth, peak_index, trough_index)
    pi = 0
    for r in rs:
        eq.append(eq[-1] + r)
        i = len(eq) - 1
        if eq[i] > peak:
            peak, pi = eq[i], i
        if peak - eq[i] > best[0]:
            best = (peak - eq[i], pi, i)
    return eq, best


def equity_curve(rs, w=420, h=200, caption=""):
    """Cumulative R line with the biggest peak-to-trough drop shaded."""
    eq, (depth, a, b) = _dd(rs)
    lo, hi = min(eq), max(eq)
    X = lambda i: 34 + i * (w - 50) / (len(eq) - 1)
    Y = lambda v: h - 24 - (v - lo) * (h - 50) / (hi - lo or 1)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="34" x2="{w - 16}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#C7C7CC"/>',
           f'<text x="28" y="{Y(0) + 4:.1f}" text-anchor="end" fill="{GR}" class="st">0R</text>',
           f'<text x="28" y="{Y(hi) + 4:.1f}" text-anchor="end" fill="{GR}" class="st">{hi:+g}R</text>',
           f'<rect x="{X(a):.1f}" y="{Y(eq[a]):.1f}" width="{X(b) - X(a):.1f}" height="{Y(eq[b]) - Y(eq[a]):.1f}" fill="{DN}" fill-opacity=".10"/>']
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(eq))
               + f'" fill="none" stroke="{BL}" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{X(a):.1f}" cy="{Y(eq[a]):.1f}" r="4" fill="{UP}"/>')
    out.append(f'<text x="{X(a):.1f}" y="{Y(eq[a]) - 8:.1f}" text-anchor="middle" fill="{UP}" class="lt">Peak</text>')
    out.append(f'<circle cx="{X(b):.1f}" cy="{Y(eq[b]):.1f}" r="4" fill="{DN}"/>')
    out.append(f'<text x="{X(b):.1f}" y="{Y(eq[b]) + 16:.1f}" text-anchor="middle" fill="{DN}" class="lt">Trough</text>')
    out.append(f'<text x="{(X(a) + X(b)) / 2:.1f}" y="{(Y(eq[a]) + Y(eq[b])) / 2 + 4:.1f}" text-anchor="middle" fill="{DN}" class="pt">−{depth:g}R</text>')
    out.append(f'<text x="{w - 16}" y="{h - 6}" text-anchor="end" fill="{GR}" class="st">trade ទី 1 → {len(rs)}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def split_bar(w=420, h=96, caption=""):
    """Data timeline split into the older 70% (build/tune) and the newest 30% (test once)."""
    cut = 12 + 0.7 * (w - 24)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="12" y="22" width="{cut - 14:.1f}" height="40" rx="9" fill="{BL}" fill-opacity=".14" stroke="{BL}"/>',
           f'<rect x="{cut + 2:.1f}" y="22" width="{w - 14 - cut:.1f}" height="40" rx="9" fill="{OR}" fill-opacity=".14" stroke="{OR}"/>',
           f'<text x="{(12 + cut) / 2:.1f}" y="40" text-anchor="middle" fill="{BL}" class="bt">70% ចាស់ (in-sample)</text>',
           f'<text x="{(12 + cut) / 2:.1f}" y="55" text-anchor="middle" fill="#1C1C1E" class="st">ជ្រើស · កែច្បាប់នៅទីនេះ</text>',
           f'<text x="{(cut + w - 12) / 2:.1f}" y="40" text-anchor="middle" fill="{OR}" class="bt">30% ថ្មី</text>',
           f'<text x="{(cut + w - 12) / 2:.1f}" y="55" text-anchor="middle" fill="#1C1C1E" class="st">សាកតែម្ដង</text>',
           f'<text x="12" y="80" fill="{GR}" class="st">ចាស់ ←</text>',
           f'<text x="{w - 12}" y="80" text-anchor="end" fill="{GR}" class="st">→ ថ្មីបំផុត</text>',
           "</svg>"]
    return _wrap("".join(out), caption)


_EQ, (_DEPTH, _A, _B) = _dd(DEMO_R)

CH = dict(
    ch=35, part="PART 9 · Strategy Development & Testing",
    title_km="ការសាកល្បងលើអតីតកាល", title_en="Backtesting: Sample Size · Win Rate · Expectancy · Profit Factor · Drawdown · Bias · Costs",
    intro="""Chapter 34 បានជួយអ្នកសរសេរ strategy ជាច្បាប់ច្បាស់។ ឥឡូវសំណួរសំខាន់: <b>តើច្បាប់ទាំងនោះធ្លាប់ដំណើរការទេ?</b>
<span class='en-term'>Backtesting</span> គឺការអនុវត្តច្បាប់<b>ដដែល</b>លើទិន្នន័យចាស់ ហើយកត់<b>គ្រប់ trade</b> (ល្អ និងអាក្រក់)
ដើម្បីវាស់ <span class='en-term'>win rate</span> · <span class='en-term'>average R</span> · <span class='en-term'>expectancy</span> ·
<span class='en-term'>profit factor</span> និង <span class='en-term'>drawdown</span>។ Backtest ល្អមិនធានាអនាគតទេ ប៉ុន្តែ backtest
<b>អាក្រក់</b> ឬ<b>មិនស្មោះត្រង់</b> ប្រាប់អ្នកមុនពេលបាត់លុយពិត។""",
    sections=[
        ("Backtest ជាអ្វី? ហេតុអ្វីត្រូវធ្វើ?", """
<p>Backtest ឆ្លើយសំណួរ 3: <b>(1)</b> ច្បាប់មាន edge ឬអត់? <b>(2)</b> ការខាតជាប់គ្នា និង drawdown ធំប៉ុណ្ណា? <b>(3)</b> តើខ្ញុំអាចទ្រាំវាបានទេ?</p>
""" + flow([("ច្បាប់", "Chapter 34", BL), ("ទិន្នន័យ", "ចាស់ · គ្រប់ស្ថានភាព", GR), ("កត់គ្រប់ trade", "មិនជ្រើស", GOLD), ("គណនា", "WR · R · PF · DD", PU), ("សម្រេច", "បន្ត ឬបោះចោល", UP)],
           caption="ដំណើរការ backtest · ជំហានទី 3 ជាជំហានដែលមនុស្សភាគច្រើនបោកខ្លួនឯង") + """
<div class='box tip'>💡 XAU.KH ធ្វើបែបនេះមុនផ្ញើសញ្ញាណាមួយ។ កំណត់ត្រាស្រាវជ្រាវ (studies/RESULTS.md) បង្ហាញទាំង idea ដែល<b>ជាប់</b> និង idea ជាច្រើនដែល<b>ធ្លាក់</b> (ឧ. ICT order-block limit entries 62 versions · trend-day pullback 36 versions: <b>បោះចោល</b>)។</div>
<div class='box warn'>⚠️ Backtest = <b>អតីតកាល</b>។ ទីផ្សារប្ដូរ។ លទ្ធផលល្អក្នុង backtest គ្រាន់តែជា "សិទ្ធិ" ឱ្យទៅ forward test (Chapter 36) មិនមែនការធានាចំណេញទេ។</div>
"""),
        ("Manual Backtesting ក្នុង MT5", """
<p><span class='en-term'>Manual backtest</span> = អ្នករំកិល chart ចាស់<b>មួយទៀនម្ដងៗ</b> ហើយសម្រេចចិត្តដូចជា trade ពិត។ វាយឺត ប៉ុន្តែបង្រៀនភ្នែក និងបង្ហាញថាច្បាប់ច្បាស់ឬអត់។</p>
<ol><li>បើក chart <b>XAUUSD</b> នៅ timeframe នៃ strategy (ឧ. 4H / 15m)</li>
<li>បិទ <span class='en-term'>Auto Scroll</span> ហើយរំកិលទៅថ្ងៃចាប់ផ្ដើម (ឧ. 6 ខែមុន)</li>
<li>ចុច <b>F12</b> ដើម្បីរំកិលទៅមុខ<b>មួយទៀន</b> · កុំមើលផ្នែកខាងស្ដាំ (អនាគត)</li>
<li>ពេលលក្ខខណ្ឌពេញ: កត់ entry · SL · TP · ម៉ោង <b>មុន</b>រំកិលបន្ត</li>
<li>រំកិលបន្តរហូតដល់ SL / TP / time exit · កត់លទ្ធផលជា <b>R</b></li>
<li>ធ្វើម្ដងទៀតរហូតដល់ចុងទិន្នន័យ · <b>គ្រប់ trade</b> ត្រូវកត់</li></ol>
<table style='break-inside:avoid'><tr><th>#</th><th>ថ្ងៃ · ម៉ោង</th><th>ទិស</th><th>Entry</th><th>SL</th><th>TP</th><th>លទ្ធផល</th><th>កំណត់</th></tr>
<tr><td>1</td><td>03 Jun 15:00</td><td>Buy</td><td>4,050</td><td>4,040</td><td>4,080</td><td>+2R</td><td>London</td></tr>
<tr><td>2</td><td>05 Jun 19:00</td><td>Sell</td><td>4,112</td><td>4,124</td><td>4,076</td><td>−1R</td><td>ក្រោយ CPI</td></tr></table>
<div class='box tip'>💡 ច្បាប់ដែលត្រូវ<b>រៀបចំយ៉ាងយូរ</b>ក្នុងការសម្រេច "បាទ ឬទេ" ពេល backtest = ច្បាប់មិនទាន់ច្បាស់គ្រប់គ្រាន់។ ត្រឡប់ទៅកែវានៅ Chapter 34។ <span class='en-term'>Strategy Tester</span> ក្នុង MT5 ប្រើសម្រាប់ច្បាប់ដែលសរសេរជាកម្មវិធី (EA) ប៉ុណ្ណោះ។</div>
"""),
        ("Historical Data: ទិន្នន័យអតីតកាល", """
<p>លទ្ធផល backtest ល្អបាន ត្រឹមតែទិន្នន័យដែលអ្នកប្រើ។ ពិនិត្យ 4 ចំណុច:</p>
<ul><li><b>រយៈពេល</b>: យ៉ាងតិចច្រើនខែ · ល្អជាងគឺ 1–2 ឆ្នាំ (ការស្រាវជ្រាវ XAU.KH ប្រើ 5m មាស <b>2 ឆ្នាំ</b>)</li>
<li><b>ស្ថានភាពទីផ្សារ</b>: ត្រូវមានទាំង trend ឡើង · trend ចុះ · range · ខែព័ត៌មានធំ</li>
<li><b>គុណភាព</b>: ទៀនបាត់ · gap · ទិន្នន័យ broker ខុសគ្នាបន្តិច · history 5m ក្នុង MT5 អាចមានកំណត់</li>
<li><b>កម្រិតតម្លៃ</b>: មាសធ្លាប់នៅ $2,000 ហើយឥឡូវ $4,000+ · SL $10 មានន័យខុសគ្នា → គិត SL ជា <b>%</b> ឬ ATR</li></ul>
""" + zigzag([20, 34, 28, 46, 40, 58, 52, 56, 50, 57, 49, 55, 40, 46, 30, 36, 18], {3: ("Trend ↑", UP), 8: ("Range", OR), 14: ("Trend ↓", DN)},
             caption="ទិន្នន័យល្អមានស្ថានភាពច្រើនប្រភេទ · strategy ដែលសាកតែលើ trend ឡើង នឹងភ្ញាក់ផ្អើលពេល range") + """
<div class='box warn'>⚠️ កុំ backtest តែ 2–3 សប្ដាហ៍ចុងក្រោយ ដែលអ្នកនៅចាំ។ អ្នកនឹងដឹងលទ្ធផលមុន (look-ahead bias ក្នុងក្បាល)។</div>
"""),
        ("Sample Size: ត្រូវការ trade ប៉ុន្មាន?", """
<p><span class='en-term'>Sample size</span> = ចំនួន trade ក្នុង backtest។ Trade តិច = លទ្ធផលអាចកើតដោយ<b>សំណាង</b>។ ក្រាហ្វខាងក្រោមជា<b>ការគណនាគណិតវិទ្យា</b> (មិនមែនទិន្នន័យទីផ្សារ):
ប្រសិនបើ win rate ពិតគឺ 50% តើលទ្ធផលដែលអ្នកឃើញអាច<b>ខុស</b>ពី 50% ប៉ុន្មាន?</p>
""" + bars([("10 trades", 31, DN), ("30 trades", 18, OR), ("100 trades", 10, GOLD), ("300 trades", 5.7, UP)], unit="%",
           caption="ចន្លោះ ± ប្រហែល 95% នៃ win rate ដែលឃើញ ពេល win rate ពិត = 50% (binomial · 1.96×√(0.25/n))") + """
<ul><li><b>10 trades</b>: អ្នកអាចឃើញ 20% ឬ 80% ទោះ strategy ពិតជា 50% · <b>គ្មានន័យ</b></li>
<li><b>30 trades</b>: អប្បបរមាដើម្បីចាប់ផ្ដើមនិយាយ</li>
<li><b>100+ trades</b>: ចាប់ផ្ដើមទុកចិត្តបាន</li></ul>
<div class='box tip'>💡 ហេតុនេះហើយបានជា XAU.KH ប្រើទិន្នន័យ 2 ឆ្នាំ ហើយ setup ដែលមាន trade តិចពេក (ឧ. 7–14 trades/ក្រុម) ត្រូវបានកត់ថា "<b>no clear difference</b>" មិនមែន "ល្អ" ទេ។</div>
"""),
        ("Win Rate និង Average R", """
<p><span class='en-term'>Win rate</span> = trade ឈ្នះ ÷ trade សរុប។ <span class='en-term'>Average R</span> = R សរុប ÷ trade សរុប។
<b>R</b> = ចំនួនដែលអ្នកប្រថុយក្នុង trade មួយ (SL)។ ការគិតជា R ធ្វើឱ្យលទ្ធផលមិនពឹងលើទំហំ lot។</p>
<table style='break-inside:avoid'><tr><th>Trade</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>10</th></tr>
<tr><td>R</td><td style='color:#34C759'>+3</td><td style='color:#FF3B30'>−1</td><td style='color:#34C759'>+1</td><td style='color:#FF3B30'>−1</td><td style='color:#FF3B30'>−1</td><td style='color:#34C759'>+2</td><td style='color:#FF3B30'>−1</td><td style='color:#34C759'>+3</td><td style='color:#FF3B30'>−1</td><td style='color:#34C759'>+1.5</td></tr></table>
<table style='break-inside:avoid'><tr><th>វាស់</th><th>គណនា</th><th>លទ្ធផល</th></tr>
<tr><td>Win rate</td><td>5 ÷ 10</td><td><b>50%</b></td></tr>
<tr><td>Avg win</td><td>(3+1+2+3+1.5) ÷ 5</td><td><b>2.1R</b></td></tr>
<tr><td>Avg loss</td><td>5 ÷ 5</td><td><b>1R</b></td></tr>
<tr><td>Average R</td><td>(+10.5 − 5) ÷ 10</td><td><b>+0.55R</b></td></tr></table>
<div class='box warn'>⚠️ ឧទាហរណ៍នេះ<b>បង្កើតឡើងសម្រាប់រៀន</b> ហើយមានតែ 10 trades: យោងតាមផ្នែកមុន វា<b>តិចពេក</b>សម្រាប់សន្និដ្ឋាន។</div>
<div class='box tip'>💡 Win rate តែម្នាក់ឯង<b>គ្មានន័យ</b>។ 80% win ជាមួយ win តូចៗ អាចខាត។ 40% win ជាមួយ win ធំ អាចចំណេញ។ សូមមើល expectancy ខាងក្រោម។</div>
"""),
        ("Expectancy និង Profit Factor", """
<p><span class='en-term'>Expectancy</span> = ចំណេញមធ្យមក្នុងមួយ trade (ជា R):<br>
<b>E = (Win% × Avg win) − (Loss% × Avg loss)</b><br>
ឧទាហរណ៍មុន: 0.5 × 2.1 − 0.5 × 1 = <b>+0.55R</b> (ស្មើ average R)។</p>
""" + bars([("80% · win 0.2R", -0.04, DN), ("50% · win 1R", 0, GR), ("65% · win 0.8R", 0.17, GOLD), ("40% · win 2.5R", 0.40, UP)], unit="R",
           caption="Expectancy នៃ strategy គំរូ 4 (avg loss 1R · មុនថ្លៃ spread) · win rate ខ្ពស់ ≠ ចំណេញ") + """
<p><span class='en-term'>Profit Factor</span> (PF) = ចំណេញសរុប ÷ ខាតសរុប។ ឧទាហរណ៍មុន: 10.5R ÷ 5R = <b>2.1</b>។</p>
<table style='break-inside:avoid'><tr><th>PF</th><th>អត្ថន័យ</th></tr>
<tr><td>&lt; 1.0</td><td>ខាត · បោះចោល ឬកែ</td></tr>
<tr><td>1.0 – 1.3</td><td>ស្ដើង · ថ្លៃ spread ឬ slippage បន្តិចអាចធ្វើឱ្យខាត</td></tr>
<tr><td>&gt; 1.3</td><td>គួរឱ្យចាប់អារម្មណ៍ (ប្រសិនបើ sample ធំ និងរួមថ្លៃ)</td></tr>
<tr><td>&gt; 3 ជាមួយ trade តិច</td><td>⚠️ គួរសង្ស័យ: សំណាង ឬ overfitting</td></tr></table>
"""),
        ("Maximum Drawdown", """
<p><span class='en-term'>Maximum Drawdown</span> (Max DD) = ការធ្លាក់ធំបំផុត ពី<b>កំពូល</b> (peak) នៃ equity ទៅ<b>បាត</b> (trough) បន្ទាប់។ វាប្រាប់ថា
"ពេលអាក្រក់បំផុត ខ្ញុំត្រូវទ្រាំប៉ុណ្ណា?"</p>
""" + equity_curve(DEMO_R, caption=f"Equity curve នៃ 40 trades <b>បង្កើតសម្រាប់រៀន</b> · ចុងក្រោយ {_EQ[-1]:+g}R · Max DD = −{_DEPTH:g}R (trade ទី {_A} → {_B})") + f"""
<p>ជាមួយ risk <b>1%</b>/trade · Max DD −{_DEPTH:g}R ≈ <b>−{_DEPTH:g}%</b> នៃគណនី។ ជាមួយ risk 3% ≈ <b>−{3 * _DEPTH:g}%</b>។ ទោះ strategy ដដែល ការឈឺចាប់ខុសគ្នាខ្លាំង។</p>
<table style='break-inside:avoid'><tr><th>ខាត</th><th>−10%</th><th>−20%</th><th>−30%</th><th>−50%</th></tr>
<tr><td>ត្រូវចំណេញវិញ</td><td>+11.1%</td><td>+25%</td><td>+42.9%</td><td>+100%</td></tr></table>
<div class='box warn'>⚠️ Max DD ក្នុង backtest <b>មិនមែនជាពិដាន</b>ទេ។ Live អាចមាន drawdown ធំជាង។ ត្រៀមខ្លួនសម្រាប់ប្រហែល <b>1.5–2 ដង</b> នៃ Max DD ដែលឃើញ ហើយកត់ផងដែរ<b>ការខាតជាប់គ្នាវែងបំផុត</b> (Chapter 33)។</div>
"""),
        ("Look-ahead Bias និង Overfitting", """
<p><span class='en-term'>Look-ahead bias</span> = ប្រើព័ត៌មានដែល<b>មិនទាន់ដឹង</b>នៅពេលសម្រេចចិត្ត។ វាធ្វើឱ្យ backtest ល្អពេក។ ឧទាហរណ៍:</p>
<ul><li>ចូលនៅ "high នៃថ្ងៃ" ឬ swing ដែល<b>ទើបតែបញ្ជាក់</b>ក្រោយ 2 ទៀន</li>
<li>ប្រើតម្លៃ<b>បិទ</b>នៃទៀន ពេលទៀននោះមិនទាន់បិទ</li>
<li>ដឹងលទ្ធផលព័ត៌មានមុន · ឃើញ chart ខាងស្ដាំ</li></ul>
""" + zigzag([30, 45, 58, 78, 64, 52, 60, 44], {3: ("SH ?", OR), 5: ("ដឹងនៅទីនេះ", BL)},
             lines=[(78, 3, 7, "", OR, True)],
             caption="Swing high បញ្ជាក់តែក្រោយទៀនបន្ទាប់បិទ · លក់នៅកំពូលផ្ទាល់ក្នុង backtest = look-ahead bias") + """
<p><span class='en-term'>Overfitting</span> = កែច្បាប់ (លេខ · filter) រហូតដល់វាល្អឥតខ្ចោះលើទិន្នន័យចាស់ ប៉ុន្តែគ្រាន់តែ "ចាំ" សំឡេងរំខាន។ ដំណោះស្រាយ: ចែកទិន្នន័យ។</p>
""" + split_bar(caption="ជ្រើស និងកែច្បាប់តែលើ 70% ចាស់ · បន្ទាប់មកសាកលើ 30% ថ្មី <b>តែម្ដង</b>") + """
<table style='break-inside:avoid'><tr><th>ឧទាហរណ៍ពិត (studies/RESULTS.md)</th><th>លទ្ធផល</th><th>សម្រេច</th></tr>
<tr><td>Trend-day pullback · 36 versions · ជ្រើសល្អបំផុតលើ 70% ចាស់</td><td>30% ថ្មី: ប្រហែល 0R</td><td>❌ បោះចោល</td></tr>
<tr><td>ICT OB limit entries · 62 versions</td><td>Best-on-older → −0.42R លើថ្មី</td><td>❌ បោះចោល</td></tr>
<tr><td>TP1 0.75R → 1R</td><td>ល្អជាងទាំងចាស់ និងថ្មី</td><td>✅ ប្រើ</td></tr>
<tr><td>ខ្សែ TARGET ប៉ះ 71%</td><td>ខ្សែ<b>ចៃដន្យ</b>ចម្ងាយដូចគ្នា 77%</td><td>គ្មាន edge</td></tr></table>
<div class='box tip'>💡 ជួរចុងក្រោយជាមេរៀនធំ: លេខ "71%" ស្ដាប់ទៅល្អ ប៉ុន្តែប្រៀបធៀបជាមួយ<b>ការចៃដន្យ</b> វាគ្មានអ្វីពិសេសទេ។ តែងតែសួរ: "បើខ្ញុំ trade ចៃដន្យ តើបានប៉ុន្មាន?"</div>
"""),
        ("Spread · Commission · Slippage", """
<p>Backtest ដែលគ្មានថ្លៃ = backtest មិនពិត។ Trade នីមួយៗបង់: <span class='en-term'>spread</span> (ចន្លោះ bid/ask) · <span class='en-term'>commission</span> (តាមប្រភេទគណនី) ·
<span class='en-term'>slippage</span> (តម្លៃបំពេញខុសពីតម្លៃចង់បាន ជាពិសេសពេលព័ត៌មាន)។</p>
<p>ឧទាហរណ៍: ថ្លៃសរុប <b>$0.40</b> ក្នុង 1 oz (0.01 lot) = 4 pips (ដូចការស្រាវជ្រាវ XAU.KH)។ ថ្លៃនេះស៊ី R ខុសគ្នាតាមទំហំ SL:</p>
""" + bars([("SL $20", 0.02, UP), ("SL $10", 0.04, GOLD), ("SL $5", 0.08, OR), ("SL $3", 0.13, DN)], unit="R",
           caption="ថ្លៃ $0.40/trade គិតជា R · SL តូច = ថ្លៃធំជាងក្នុងមួយ R") + """
<div class='box warn'>⚠️ Strategy scalp ដែលមាន expectancy <b>+0.10R</b> មុនថ្លៃ ជាមួយ SL $3 → <b>−0.03R</b> ក្រោយថ្លៃ = ខាត។ ហេតុនេះហើយ SL តូចៗ មិនមែនតែងតែ "ល្អជាង" ទេ។</div>
<div class='box ok'>✅ សាកថ្លៃ<b>ខ្ពស់ជាង</b>ធម្មតាផង។ ក្នុង RESULTS.md COMBO scalp: <b>+0.33R</b> ជាមួយថ្លៃ $0.40 និង <b>+0.28R</b> ជាមួយ $0.70។ Strategy ដែលនៅវិជ្ជមានពេលថ្លៃកើន = រឹងមាំជាង។</div>
"""),
        ("សម្រេចចិត្តក្រោយ Backtest", """
<p>ពេលបញ្ចប់ backtest ពិនិត្យបញ្ជីនេះ។ ត្រូវការ<b>បាទ</b>គ្រប់ជួរ មុនទៅ forward test (Chapter 36):</p>
<table style='break-inside:avoid'><tr><th>លក្ខខណ្ឌ</th><th>បាទ / ទេ</th></tr>
<tr><td>Trade ≥ 30 (ល្អ 100+)</td><td>☐</td></tr>
<tr><td>Expectancy &gt; 0 <b>ក្រោយ</b>ថ្លៃ spread · commission · slippage</td><td>☐</td></tr>
<tr><td>Profit factor &gt; 1.3</td><td>☐</td></tr>
<tr><td>វិជ្ជមានទាំង 70% ចាស់ និង 30% ថ្មី</td><td>☐</td></tr>
<tr><td>ប្ដូរលេខបន្តិច (ឧ. 30 → 25 / 35 ទៀន) នៅតែវិជ្ជមាន</td><td>☐</td></tr>
<tr><td>Max DD × 2 ជាមួយ risk របស់ខ្ញុំ = ខ្ញុំទ្រាំបាន</td><td>☐</td></tr>
<tr><td>គ្មាន look-ahead bias · កត់គ្រប់ trade</td><td>☐</td></tr></table>
""" + flow([("Backtest ជាប់", "បញ្ជីពេញ", UP), ("Forward test", "Demo 30+ trade", PU), ("Live តូច", "0.01 · risk ទាប", GOLD), ("ពិនិត្យ", "ប្រៀបធៀប backtest", BL)],
           caption="Backtest គ្រាន់តែជាជំហានទីមួយ · Chapter 36 បន្ត") + """
<ul><li>❌ ជ្រើសតែ trade ល្អ (cherry-picking) · ❌ លុប trade "ចម្លែក"</li>
<li>❌ កែច្បាប់ពាក់កណ្ដាល backtest ហើយមិនចាប់ផ្ដើមឡើងវិញ</li>
<li>❌ សន្និដ្ឋានពី 10–15 trades · ❌ ភ្លេចថ្លៃ</li></ul>
"""),
    ],
    summary=["Backtest = អនុវត្តច្បាប់ដដែលលើទិន្នន័យចាស់ ហើយកត់គ្រប់ trade",
             "Sample size: យ៉ាងតិច 30 · ល្អ 100+ · trade តិច = សំណាង",
             "Expectancy = (Win% × Avg win) − (Loss% × Avg loss) · win rate តែម្នាក់ឯងគ្មានន័យ",
             "Profit factor > 1.3 · Max DD ក្នុង live អាចធំជាង backtest",
             "ការពារ look-ahead bias + overfitting (70/30) · ដាក់ថ្លៃ spread · commission · slippage ជានិច្ច"],
    exercise=["យក Trading Plan ពី Chapter 34 ហើយធ្វើ manual backtest ក្នុង MT5 (F12) លើមាស 3 ខែចុងក្រោយ។ កត់គ្រប់ trade ក្នុងតារាង។",
              "Trade 20: ឈ្នះ 9 (avg win 1.8R) · ខាត 11 (avg loss 1R)។ គណនា win rate · expectancy · profit factor។ Sample នេះគ្រប់គ្រាន់ទេ?",
              "Strategy មាន expectancy +0.12R មុនថ្លៃ · SL មធ្យម $4 · ថ្លៃ $0.40/trade។ Expectancy ក្រោយថ្លៃជាប៉ុន្មាន?",
              "គូរ equity curve ពីលទ្ធផល backtest របស់អ្នក ហើយរក Max DD និងការខាតជាប់គ្នាវែងបំផុត។ ប្រៀបធៀបជាមួយ live record ក្នុង 📈 Proof ដើម្បីមើលថា drawdown ពិតមើលទៅដូចម្ដេច។"],
)
