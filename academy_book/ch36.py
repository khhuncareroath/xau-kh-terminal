from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def expected_range(w=420, h=150, caption=""):
    """Win-rate axis 0-100% with the normal range after 30 trades (50% ± 18%) and two forward results."""
    X = lambda p: 20 + p * (w - 40) / 100
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{X(32):.1f}" y="52" width="{X(68) - X(32):.1f}" height="34" rx="8" fill="{UP}" fill-opacity=".14" stroke="{UP}"/>',
           f'<text x="{X(50):.1f}" y="44" text-anchor="middle" fill="{UP}" class="lt">ចន្លោះធម្មតា 32% – 68% (30 trades)</text>',
           f'<line x1="20" x2="{w - 20}" y1="69" y2="69" stroke="#C7C7CC"/>']
    for p in (0, 25, 50, 75, 100):
        out.append(f'<text x="{X(p):.1f}" y="104" text-anchor="middle" fill="{GR}" class="st">{p}%</text>')
    out.append(f'<line x1="{X(50):.1f}" x2="{X(50):.1f}" y1="56" y2="82" stroke="{BL}" stroke-width="2"/>')
    out.append(f'<text x="{X(50):.1f}" y="122" text-anchor="middle" fill="{BL}" class="lt">Backtest 50%</text>')
    out.append(f'<circle cx="{X(45):.1f}" cy="69" r="6" fill="{GOLD}"/>')
    out.append(f'<text x="{X(45):.1f}" y="140" text-anchor="middle" fill="{GOLD}" class="lt">A: 45% ✓</text>')
    out.append(f'<circle cx="{X(22):.1f}" cy="69" r="6" fill="{DN}"/>')
    out.append(f'<text x="{X(22):.1f}" y="122" text-anchor="middle" fill="{DN}" class="lt">B: 22% ✗</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def fill_gap(w=420, h=150, caption=""):
    """Planned entry vs actual fill for a buy: the fill is a little higher (worse) = slippage."""
    Y = lambda p: 26 + (4051.0 - p) * (h - 60) / 1.4
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="150" y="{Y(4050.40):.1f}" width="180" height="{Y(4050.0) - Y(4050.40):.1f}" fill="{OR}" fill-opacity=".18"/>',
           f'<line x1="70" x2="330" y1="{Y(4050.0):.1f}" y2="{Y(4050.0):.1f}" stroke="{BL}" stroke-width="1.6" stroke-dasharray="5 4"/>',
           f'<line x1="150" x2="330" y1="{Y(4050.40):.1f}" y2="{Y(4050.40):.1f}" stroke="{DN}" stroke-width="1.6"/>',
           f'<text x="64" y="{Y(4050.0) + 4:.1f}" text-anchor="end" fill="{BL}" class="lt">4,050.00</text>',
           f'<text x="144" y="{Y(4050.40) + 4:.1f}" text-anchor="end" fill="{DN}" class="lt">4,050.40</text>',
           f'<text x="336" y="{Y(4050.0) + 4:.1f}" fill="{BL}" class="lt">គម្រោង</text>',
           f'<text x="336" y="{Y(4050.40) + 4:.1f}" fill="{DN}" class="lt">Fill ពិត</text>',
           f'<text x="240" y="{(Y(4050.40) + Y(4050.0)) / 2 + 4:.1f}" text-anchor="middle" fill="{OR}" class="pt">4 pips</text>',
           f'<text x="200" y="{h - 10}" text-anchor="middle" fill="{GR}" class="st">Buy · 0.01 lot · slippage $0.40 = 0.04R ពេល SL $10</text>',
           "</svg>"]
    return _wrap("".join(out), caption)


CH = dict(
    ch=36, part="PART 9 · Strategy Development & Testing",
    title_km="ការសាកល្បងលើទីផ្សារផ្ទាល់", title_en="Forward Testing: Demo · Live Observations · Execution · Consistency · Evaluation · Revision",
    intro="""Chapter 35 បានបង្ហាញថា strategy របស់អ្នក<b>ធ្លាប់</b>ដំណើរការលើទិន្នន័យចាស់។ ប៉ុន្តែ backtest មិនអាចបង្ហាញ
<b>អារម្មណ៍</b> <b>slippage ពិត</b> ឬ<b>ពេលដែលអ្នកមិននៅមុខ chart</b> បានទេ។ <span class='en-term'>Forward testing</span>
គឺការអនុវត្តច្បាប់<b>ដដែល</b>លើទីផ្សារ<b>ផ្ទាល់</b> (ទីផ្សារដែលកំពុងដើរ) ជាមួយ demo ឬ lot តូចបំផុត ហើយកត់ត្រាគ្រប់យ៉ាង។
គោលដៅមិនមែនរកលុយទេ។ គោលដៅគឺ<b>ផ្ទៀងផ្ទាត់</b>ថា លទ្ធផលពិតនៅជិត backtest ហើយ<b>អ្នក</b>អាចធ្វើតាមច្បាប់បាន។""",
    sections=[
        ("Forward Test ជាអ្វី? ហេតុអ្វីត្រូវការ?", """
<p>Backtest សួរថា "ច្បាប់នេះធ្លាប់មាន edge ទេ?"។ Forward test សួរថា "<b>ឥឡូវ</b> ក្នុងទីផ្សារពិត ហើយ<b>ដោយខ្ញុំផ្ទាល់</b> តើវានៅតែដំណើរការទេ?"។
វាជាស្ពានរវាងទិន្នន័យចាស់ និងលុយពិត។</p>
""" + flow([("Backtest", "Chapter 35", BL), ("Demo", "Forward · 30–50+", PU), ("Live តូច", "0.01 · risk ទាប", GOLD), ("បង្កើន risk", "មានភស្តុតាងសិន", UP)],
           caption="ជំហាននីមួយៗត្រូវ \"ជាប់\" មុនឡើងទៅជំហានបន្ទាប់") + """
<table style='break-inside:avoid'><tr><th>អ្វីដែល backtest មើលមិនឃើញ</th><th>អ្វីដែល forward test បង្ហាញ</th></tr>
<tr><td>Spread ពិតនៅម៉ោងនីមួយៗ</td><td>ថ្លៃពិតក្នុង MT5 របស់អ្នក</td></tr>
<tr><td>ការរង់ចាំ · ភាពធុញ · ភាពភ័យ</td><td>តើអ្នកនៅតែធ្វើតាមច្បាប់ទេ?</td></tr>
<tr><td>ពេលអ្នកមិននៅមុខ chart</td><td>Trade ដែលខកខាន (missed trades)</td></tr>
<tr><td>ការសម្រេច "នៅពេលនោះ"</td><td>ច្បាប់ច្បាស់ ឬនៅតែស្រពិចស្រពិល</td></tr></table>
<div class='box warn'>⚠️ Forward test មិនមែនជាការធានាចំណេញទេ។ វាគ្រាន់តែកាត់បន្ថយហានិភ័យនៃការយកលុយពិតទៅសាកច្បាប់ដែលមិនទាន់ត្រៀមរួច។</div>
"""),
        ("Demo Trading ក្នុង MT5", """
<p><span class='en-term'>Demo account</span> = គណនីលុយនិម្មិត ដែលប្រើតម្លៃទីផ្សារផ្ទាល់។ ក្នុង <b>MT5</b>: <b>File → Open an Account</b> → ជ្រើស server របស់ broker → ជ្រើស <b>demo</b>។</p>
<ul><li><b>ទំហំគណនីពិតប្រាកដ</b>: បើអ្នកនឹង trade ពិតជាមួយ $500 ចូរកំណត់ demo $500 មិនមែន $100,000 ទេ</li>
<li><b>Risk ដដែល</b>: ឧ. 1%/trade · lot គណនាដូច Chapter 30</li>
<li><b>ម៉ោងដដែល</b>: trade តែម៉ោងដែល plan អនុញ្ញាត (ឧ. London · NY)</li>
<li><b>ច្បាប់ដដែល</b>: គ្មាន "សាកមើលលេង" ក្រៅ plan</li></ul>
<table style='break-inside:avoid'><tr><th></th><th>Demo</th><th>Live</th></tr>
<tr><td>តម្លៃ</td><td>ផ្លាស់ទីដូចទីផ្សារពិត</td><td>ផ្លាស់ទីដូចទីផ្សារពិត</td></tr>
<tr><td>Fill · slippage</td><td>ជួនកាលល្អជាងពិត</td><td>អាចអាក្រក់ជាង ជាពិសេសពេលព័ត៌មាន</td></tr>
<tr><td>អារម្មណ៍</td><td>ស្ងប់ · ងាយធ្វើតាមច្បាប់</td><td>ភ័យ · លោភ · ចង់សងសឹក</td></tr>
<tr><td>គុណប្រយោជន៍</td><td>សាកច្បាប់ និង routine ដោយមិនបាត់លុយ</td><td>សាកចិត្តខ្លួនឯង</td></tr></table>
<div class='box tip'>💡 Demo $100,000 ជាមួយ lot ធំ បង្រៀនទម្លាប់អាក្រក់: ខាត $500 "មិនឈឺ" ព្រោះវាគ្រាន់តែ 0.5%។ ចូរធ្វើឱ្យ demo <b>មើលទៅដូចគណនីពិតរបស់អ្នក</b>។</div>
"""),
        ("ការកត់ត្រាការសង្កេតផ្ទាល់", """
<p>ក្នុង forward test អ្នកកត់<b>ច្រើនជាង</b>ក្នុង backtest ព្រោះឥឡូវមានព័ត៌មានដែល backtest គ្មាន: spread ពិត ពេលវេលា និងអារម្មណ៍។
កត់<b>មុន</b> <b>កំឡុង</b> និង<b>ក្រោយ</b> trade:</p>
""" + flow([("មុន", "Setup · រូប · plan", BL), ("ចូល", "Fill · spread", GOLD), ("កំឡុង", "អារម្មណ៍ · ការកែ", PU), ("ក្រោយ", "R · តាមច្បាប់?", UP)],
           caption="កត់ភ្លាមៗ ពេលព័ត៌មាននៅថ្មី · កុំរង់ចាំដល់ចុងសប្ដាហ៍") + """
<table style='break-inside:avoid'><tr><th>ពេល</th><th>កត់អ្វី</th></tr>
<tr><td>មុន</td><td>Setup · ហេតុផល · entry/SL/TP <b>គម្រោង</b> · រូប chart</td></tr>
<tr><td>ចូល</td><td>តម្លៃ <b>fill ពិត</b> · spread · ម៉ោង · ព័ត៌មានជិតៗ (📰 News)</td></tr>
<tr><td>កំឡុង</td><td>អារម្មណ៍ 1–5 · តើបានផ្លាស់ SL ឬបិទមុនគម្រោងទេ? ហេតុអ្វី?</td></tr>
<tr><td>ក្រោយ</td><td>លទ្ធផលជា R · ធ្វើតាមច្បាប់ 100% ឬអត់ · មេរៀនមួយ</td></tr></table>
<div class='box tip'>💡 កត់ផងដែរ <b>trade ដែលខកខាន</b> (setup មក ប៉ុន្តែអ្នកមិននៅ ឬស្ទាក់ស្ទើរ) និង<b>ថ្ងៃគ្មាន setup</b>។ បើអ្នកខកខាន trade ឈ្នះច្រើន លទ្ធផលពិតរបស់អ្នកនឹងខុសពី backtest។</div>
"""),
        ("Expected vs Actual Execution", """
<p>ក្នុង backtest អ្នកសន្មត់ថាចូលនៅតម្លៃគម្រោង។ ក្នុងទីផ្សារពិត <span class='en-term'>fill</span> អាចខុសបន្តិច។ ភាពខុសគ្នានេះហៅថា
<span class='en-term'>slippage</span>។ ចងចាំ: មាស <b>$1 = 10 pips</b> ហើយនៅលើ <b>0.01 lot</b> តម្លៃផ្លាស់ $1 = $1។</p>
""" + fill_gap(caption="ឧទាហរណ៍: គម្រោងទិញ 4,050.00 · fill 4,050.40 · ខុស $0.40 = 4 pips") + """
<p>ប្រៀបធៀប<b>ការសន្មត់</b>ក្នុង backtest ជាមួយ<b>អ្វីដែលកើតឡើងពិត</b>:</p>
<table style='break-inside:avoid'><tr><th>វាស់</th><th>Backtest សន្មត់</th><th>Forward ពិត (ឧទាហរណ៍)</th></tr>
<tr><td>ថ្លៃ / trade</td><td>$0.40 (4 pips)</td><td>$0.55 មធ្យម (spread + slippage)</td></tr>
<tr><td>Limit order បំពេញ</td><td>100%</td><td>តម្លៃខ្លះប៉ះត្រឹមតែជិត ហើយត្រឡប់ → មិនបំពេញ</td></tr>
<tr><td>ពេលចូល</td><td>ភ្លាមពេលទៀនបិទ</td><td>យឺត 1–3 នាទី</td></tr>
<tr><td>Trade ចូលបាន</td><td>គ្រប់ setup</td><td>ខកខានខ្លះ (ដេក · ធ្វើការ)</td></tr></table>
""" + bars([("Trade 1", 2, GOLD), ("Trade 2", 0, GR), ("Trade 3", 5, OR), ("Trade 4", 1, GOLD), ("Trade 5 · NFP", 18, DN), ("Trade 6", 3, GOLD)], unit="p",
           caption="Slippage គិតជា pips ក្នុង 6 trades <b>ឧទាហរណ៍</b> · trade ក្បែរព័ត៌មានធំ (NFP) ខុសខ្លាំងជាងគេ") + """
<div class='box warn'>⚠️ បើថ្លៃពិតខ្ពស់ជាង backtest ចូរ<b>គណនា expectancy ឡើងវិញ</b> ជាមួយថ្លៃពិត (Chapter 35)។ Strategy ដែលមាន SL តូច ឈឺខ្លាំងជាងគេ។</div>
"""),
        ("Measuring Consistency: វាស់ភាពស្ថិតស្ថេរ", """
<p><span class='en-term'>Consistency</span> មានពីរផ្នែក: <b>(1) លទ្ធផល</b> (R មិនលោតខ្លាំងពេកពីមួយក្រុមទៅមួយក្រុម) និង
<b>(2) អាកប្បកិរិយា</b> (អ្នកធ្វើតាមច្បាប់រាល់ trade)។ ផ្នែកទី 2 សំខាន់ជាងនៅដំណាក់កាលដំបូង។</p>
<p>វិធីងាយ: ចែក trade ជា<b>ក្រុម 10</b> ហើយមើល average R នៃក្រុមនីមួយៗ:</p>
""" + bars([("1–10", 0.4, UP), ("11–20", -0.1, DN), ("21–30", 0.5, UP), ("31–40", 0.2, UP), ("41–50", 0.3, UP)], unit="R",
           caption="Average R ក្នុងក្រុម 10 trades (<b>ឧទាហរណ៍</b>) · ក្រុមមួយអវិជ្ជមាន គឺធម្មតា · មធ្យមសរុប +0.26R") + """
<p>តើលទ្ធផល forward "ខុស" ពី backtest ឬគ្រាន់តែជាសំណាងល្អ/អាក្រក់? ប្រើចន្លោះ sample size ពី Chapter 35:
បើ backtest win rate 50% ក្រោយ 30 trades អ្នកអាចឃើញប្រហែល <b>32%–68%</b> ដោយចៃដន្យសុទ្ធ។</p>
""" + expected_range(caption="A ស្ថិតក្នុងចន្លោះធម្មតា → បន្ត · B ក្រៅចន្លោះ → ត្រូវស៊ើបមូលហេតុ") + """
<table style='break-inside:avoid'><tr><th>Consistency វាស់</th><th>គោលដៅ</th></tr>
<tr><td>Rule adherence (trade តាមច្បាប់ ÷ សរុប)</td><td>90%+</td></tr>
<tr><td>Risk/trade</td><td>ដដែលរាល់ trade (ឧ. 1%)</td></tr>
<tr><td>ចំនួន trade/សប្ដាហ៍</td><td>ជិតនឹង backtest (មិនច្រើនពេក)</td></tr></table>
"""),
        ("Strategy Evaluation: វាយតម្លៃ", """
<p>ក្រោយ <b>30 trades</b> (ល្អជាង <b>50+</b>) ដាក់លទ្ធផលពីរក្បែរគ្នា។ ឧទាហរណ៍ខាងក្រោម<b>បង្កើតឡើងសម្រាប់រៀន</b>:</p>
<table style='break-inside:avoid'><tr><th>វាស់</th><th>Backtest</th><th>Forward (40 trades)</th><th>វាយតម្លៃ</th></tr>
<tr><td>Win rate</td><td>48%</td><td>45%</td><td>✅ ក្នុងចន្លោះ</td></tr>
<tr><td>Avg win</td><td>2.0R</td><td>1.8R</td><td>⚠️ តិចជាងបន្តិច</td></tr>
<tr><td>Expectancy</td><td>+0.44R</td><td>+0.26R</td><td>✅ នៅវិជ្ជមាន</td></tr>
<tr><td>Profit factor</td><td>1.85</td><td>1.47</td><td>✅ &gt; 1.3</td></tr>
<tr><td>Max DD</td><td>−7R</td><td>−6R</td><td>✅</td></tr>
<tr><td>Rule adherence</td><td>—</td><td>92%</td><td>✅</td></tr></table>
<p>Forward ខ្សោយជាង backtest បន្តិច គឺ<b>ធម្មតា</b> (ថ្លៃពិត · trade ខកខាន)។ សំខាន់គឺវា<b>នៅវិជ្ជមាន</b> និងស្ថិតក្នុងចន្លោះដែលអាចពន្យល់បាន។</p>
<table style='break-inside:avoid'><tr><th>លទ្ធផល</th><th>ជំហានបន្ទាប់</th></tr>
<tr><td>ជិត backtest + rule adherence ខ្ពស់</td><td>✅ ទៅ live តូច (0.01 · risk 0.5–1%)</td></tr>
<tr><td>ខ្សោយជាង ប៉ុន្តែវិជ្ជមាន</td><td>⚠️ ពិនិត្យថ្លៃ · fill · ម៉ោង · បន្ត demo</td></tr>
<tr><td>អវិជ្ជមាន + rule adherence <b>ទាប</b></td><td>🔧 បញ្ហាគឺ<b>ការអនុវត្ត</b> មិនមែន strategy ទេ</td></tr>
<tr><td>អវិជ្ជមានច្បាស់ ក្រោយ 50+ trades តាមច្បាប់</td><td>❌ ឈប់ · ត្រឡប់ទៅ Chapter 34–35</td></tr></table>
<div class='box tip'>💡 មុនវិនិច្ឆ័យ strategy ចូរពិនិត្យខ្លួនឯងសិន: បើអ្នកធ្វើតាមច្បាប់តែ 60% នៃពេលវេលា លទ្ធផលនោះមិនមែនជាលទ្ធផលរបស់ strategy ទេ។</div>
"""),
        ("ពេលណាត្រូវកែ Strategy?", """
<p>ការខាត 2–3 ដងជាប់ <b>មិនមែនជាហេតុផល</b>ទេ។ Strategy ល្អក៏មានការខាតជាប់គ្នាដែរ (Chapter 33):</p>
""" + zigzag([10, 22, 18, 30, 26, 21, 16, 12, 24, 36, 31, 46, 58], {7: ("ខាត 4 ជាប់", DN), 11: ("ងើបវិញ", UP)},
             caption="Equity curve នៃ strategy វិជ្ជមាន (<b>ឧទាហរណ៍</b>) · ការធ្លាក់កណ្ដាលផ្លូវ គឺជាផ្នែកធម្មតា") + """
<p><b>ហេតុផលត្រឹមត្រូវ</b>ដើម្បីកែ:</p>
<ul><li>Sample <b>គ្រប់គ្រាន់</b> (30–50+) ហើយលទ្ធផល<b>ក្រៅចន្លោះធម្មតា</b>ច្បាស់</li>
<li>ថ្លៃពិតខ្ពស់ជាងការសន្មត់ ហើយធ្វើឱ្យ expectancy ជិត 0</li>
<li>ច្បាប់<b>មិនច្បាស់</b>: អ្នកស្ទាក់ស្ទើរញឹកញាប់ពេលសម្រេច "បាទ/ទេ"</li>
<li>ទីផ្សារប្ដូរ: ឧ. volatility កើនខ្លាំង ហើយ SL ថេរ $5 តូចពេកសម្រាប់មាស $4,000+</li></ul>
<p><b>របៀបកែ</b>: ប្ដូរ<b>តែមួយចំណុច</b>ម្ដង → backtest ឡើងវិញ (70/30) → forward test ឡើងវិញ។ កត់ version នីមួយៗ:</p>
<table style='break-inside:avoid'><tr><th>Version</th><th>ការផ្លាស់ប្ដូរ</th><th>ហេតុផល</th><th>លទ្ធផល</th></tr>
<tr><td>v1.0</td><td>ច្បាប់ដើម</td><td>—</td><td>Forward +0.26R</td></tr>
<tr><td>v1.1</td><td>មិន trade 15 នាទីមុន/ក្រោយព័ត៌មាន high-impact</td><td>Slippage ធំពេល NFP · CPI</td><td>កំពុងសាក</td></tr></table>
<div class='box warn'>⚠️ ការកែច្បាប់រាល់សប្ដាហ៍ = អ្នកមិនដែលមាន strategy ទេ។ អ្នកគ្រាន់តែមានទម្លាប់ដេញតាមលទ្ធផលចុងក្រោយ។</div>
"""),
        ("ពី Demo ទៅ Live", """
<p>សូម្បីតែ forward test ល្អ ការផ្លាស់ពី demo ទៅលុយពិតនៅតែលំបាក ព្រោះ<b>អារម្មណ៍</b>ផ្លាស់ប្ដូរ។ ចូរចាត់ទុក live ដំបូងជា<b>ជំហាន forward test ទីពីរ</b>:</p>
<ul><li>ចាប់ផ្ដើមដោយ <b>0.01 lot</b> (1 oz · $1 move = $1) និង risk <b>0.5%</b></li>
<li>ច្បាប់ដដែល · ការកត់ត្រាដដែល · ការវាយតម្លៃដដែល</li>
<li>បង្កើន risk <b>តែក្រោយ</b> 30+ live trades ដែលស្របនឹង demo</li></ul>
<div class='box ok'>✅ ប្រសិនបើ rule adherence របស់អ្នកធ្លាក់ពី 92% (demo) ទៅ 70% (live) នោះគឺជាព័ត៌មានដ៏មានតម្លៃ: បញ្ហាគឺចិត្ត មិនមែន strategy ទេ។ សូមអាន Chapter 33 ឡើងវិញ។</div>
"""),
        ("Forward Testing ជាមួយ XAU.KH", """
<ul><li>📈 <b>Proof</b> = forward test <b>សាធារណៈ</b>របស់ XAU.KH: គ្រប់ signal ត្រូវកត់ ទាំងឈ្នះ ទាំងខាត។ ប្រៀបធៀបវាជាមួយការស្រាវជ្រាវ backtest (studies/RESULTS.md) តាមវិធីដូចក្នុងជំពូកនេះ។</li>
<li>🚨 <b>Signals</b>: បើអ្នកតាម signal ក្នុង demo ចូរកត់<b>តម្លៃ fill របស់អ្នក</b> ធៀបនឹងតម្លៃក្នុង signal។ ការចូលយឺតបង្កើត slippage ដែលអ្នកអាចវាស់បាន។</li>
<li>📰 <b>News</b>: សម្គាល់ trade ណាដែលនៅក្បែរព័ត៌មានធំ ដើម្បីមើលថាវាមានថ្លៃខុសគ្នាទេ។</li>
<li>📊 <b>Analysis</b> និង <b>/check</b>: ថតទុកជាបរិបទ (context) ក្នុងកំណត់ត្រា ដើម្បីដឹងថា structure ពេលនោះជាអ្វី។</li></ul>
<div class='box tip'>💡 Signal ផ្ដល់ entry · SL · TP ដូចគ្នាសម្រាប់មនុស្សគ្រប់គ្នា ប៉ុន្តែ<b>លទ្ធផលរបស់អ្នក</b>អាស្រ័យលើពេលចូល ថ្លៃ broker និង lot។ ហេតុនេះហើយការកត់ត្រាផ្ទាល់ខ្លួនមានសារៈសំខាន់។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ Demo $100,000 ជាមួយ lot ធំ ដែលមិនដូចគណនីពិត</li>
<li>❌ ប្ដូរច្បាប់ក្រោយខាត 2–3 ដង</li>
<li>❌ កត់តែ trade ដែលចូល ហើយភ្លេច trade ខកខាន</li>
<li>❌ មិនកត់តម្លៃ fill ពិត ដូច្នេះមិនដឹងថ្លៃពិត</li>
<li>❌ ចាប់ផ្ដើម live ធំភ្លាម ក្រោយ demo ឈ្នះ 10 trades</li>
<li>❌ បន្ទោស strategy ពេលបញ្ហាពិតគឺការមិនធ្វើតាមច្បាប់</li></ul>
"""),
    ],
    summary=["Forward test = ច្បាប់ដដែល លើទីផ្សារផ្ទាល់ (demo ឬ 0.01 lot) ក្រោយ backtest",
             "Demo ត្រូវមើលទៅដូចគណនីពិត: ទំហំ · risk · ម៉ោង ដដែល",
             "កត់ fill ពិត · spread · slippage · អារម្មណ៍ · trade ខកខាន",
             "វាយតម្លៃក្រោយ 30–50+ trades · ប្រើចន្លោះធម្មតា មិនមែនអារម្មណ៍",
             "កែតែមួយចំណុចម្ដង ពេលមានភស្តុតាង · rule adherence ទាប = បញ្ហាការអនុវត្ត"],
    exercise=["បើក demo ក្នុង MT5 ដែលមានទំហំស្មើគណនីពិតដែលអ្នកមានគម្រោង ហើយកំណត់ risk/trade។",
              "Forward test plan របស់អ្នកឱ្យបាន 30 trades។ កត់ entry គម្រោង និង fill ពិតគ្រប់ trade រួចគណនា slippage មធ្យមជា pips និងជា R។",
              "Backtest win rate 55% · forward 30 trades ឈ្នះ 14។ តើលទ្ធផលនេះស្ថិតក្នុងចន្លោះធម្មតា (±18%) ទេ? អ្នកគួរធ្វើអ្វីបន្ទាប់?",
              "ប្រៀបធៀបទិន្នន័យក្នុង 📈 Proof ជាមួយការសន្មត់ backtest: ការខាតជាប់គ្នាវែងបំផុតគឺប៉ុន្មាន?"],
)
