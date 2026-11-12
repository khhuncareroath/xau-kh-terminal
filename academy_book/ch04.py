from academy_pdf import bars, flow, zigzag

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def _bid_ask():
    """Bid and Ask quotes with the spread between them, and which side each order uses."""
    w, h = 420, 190
    s = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
         f'<rect x="60" y="62" width="300" height="46" fill="{GOLD}" fill-opacity=".14"/>',
         f'<line x1="60" x2="360" y1="62" y2="62" stroke="{BL}" stroke-width="2.4"/>',
         f'<line x1="60" x2="360" y1="108" y2="108" stroke="{DN}" stroke-width="2.4"/>',
         f'<text x="66" y="54" class="pt" fill="{BL}">Ask 4,060.30</text>',
         f'<text x="66" y="126" class="pt" fill="{DN}">Bid 4,060.00</text>',
         f'<text x="210" y="90" text-anchor="middle" class="bt" fill="{GOLD}">Spread = $0.30 = 3 pips</text>',
         f'<text x="354" y="54" text-anchor="end" class="st" fill="#1C1C1E">BUY បើកនៅ Ask · SELL បិទនៅ Ask</text>',
         f'<text x="354" y="126" text-anchor="end" class="st" fill="#1C1C1E">SELL បើកនៅ Bid · BUY បិទនៅ Bid</text>',
         f'<text x="210" y="160" text-anchor="middle" class="st" fill="#6E6E73">Chart MT5 គូរដោយ Bid · បើក "Show Ask line" ដើម្បីឃើញ Ask</text>',
         "</svg>"]
    return f'<div class="fig">{"".join(s)}<div class="cap">តម្លៃពីរជានិច្ច: Ask (ទិញ) ខាងលើ · Bid (លក់) ខាងក្រោម</div></div>'


CH = dict(
    ch=4, part="PART 1 · Foundations",
    title_km="ស្គាល់តម្លៃ និងការគណនា", title_en="Understanding Price: Bid · Ask · Spread · Pip · Lot",
    intro="""ជំពូកនេះគឺជា<b>គណិតវិទ្យានៃ trading</b>។ មុននឹងបើក order ណាមួយ អ្នកត្រូវដឹងថា: តើខ្ញុំទិញនៅតម្លៃណា?
ថ្លៃប៉ុន្មាន? បើតម្លៃរត់ $1 ខ្ញុំចំណេញ ឬខាតប៉ុន្មាន? ហើយ broker ទុកលុយប៉ុន្មានជា margin? អ្នកដែលមិនដឹងចម្លើយទាំងនេះ
កំពុង trade ដោយបិទភ្នែក។ យើងនឹងរៀន <b>Bid, Ask, Spread, Pip, Point, Lot, Contract Specification, Leverage, Margin,
Swap, Commission</b> និង<b>ការគណនាចំណេញ/ខាត</b> ជាមួយឧទាហរណ៍មាសពិតៗ។""",
    sections=[
        ("Bid និង Ask: តម្លៃពីរ", """
<p>នៅពេលណាក៏ដោយ broker ផ្ដល់តម្លៃ<b>ពីរ</b>សម្រាប់មាស:</p>
<ul><li><span class='en-term'>Ask</span> = តម្លៃដែលអ្នក<b>ទិញ</b>បាន (ខ្ពស់ជាង)។</li>
<li><span class='en-term'>Bid</span> = តម្លៃដែលអ្នក<b>លក់</b>បាន (ទាបជាង)។</li></ul>
""" + _bid_ask() + """
<table><tr><th>Order</th><th>បើកនៅ</th><th>បិទនៅ (SL/TP ប៉ះនៅ)</th></tr>
<tr><td><b style='color:#34C759'>BUY</b></td><td>Ask</td><td>Bid</td></tr>
<tr><td><b style='color:#FF3B30'>SELL</b></td><td>Bid</td><td>Ask</td></tr></table>
<div class='box warn'>⚠️ ដោយសារ chart គូរដោយ <b>Bid</b>: SL របស់ <b>SELL</b> អាចត្រូវប៉ះ ទោះបីអ្នកឃើញទៀនមិនទាន់ដល់ SL ក៏ដោយ ព្រោះ Ask ខ្ពស់ជាង Bid
មួយ spread។ ពិសេសពេល spread ធំ។ បើក <b>Show Ask line</b> (Chapter 3) ដើម្បីឃើញវា។</div>
"""),
        ("Spread: ថ្លៃដែលអ្នកបង់រាល់ trade", """
<p><span class='en-term'>Spread</span> = Ask − Bid។ ពេលអ្នកបើក BUY អ្នកទិញនៅ Ask តែ order របស់អ្នកត្រូវបានវាយតម្លៃនៅ Bid។ ដូច្នេះ
<b>ភ្លាមៗបន្ទាប់ពីបើក</b> order គឺខាតប្រហែលមួយ spread រួចហើយ។ នេះជាថ្លៃចូលទីផ្សារ។</p>
<div class='box tip'>💡 ឧទាហរណ៍: spread $0.30 (3 pips) ជាមួយ 0.01 lot (1 oz) = ថ្លៃ <b>$0.30</b>។ ជាមួយ 0.10 lot (10 oz) = <b>$3</b>។</div>
<p>Spread <b>មិនថេរ</b>ទេ។ វាផ្លាស់ប្ដូរតាមម៉ោង និងព្រឹត្តិការណ៍:</p>
""" + bars([("ម៉ោងសកម្ម", 1, UP), ("ម៉ោងស្ងាត់", 2, OR), ("ព័ត៌មានធំ", 6, DN), ("បើកផ្សារថ្ងៃច័ន្ទ", 5, DN)], unit="×", h=170,
           caption="ឧទាហរណ៍<b>ប្រៀបធៀប</b>ប៉ុណ្ណោះ (spread ម៉ោងសកម្ម = 1×) · លេខពិតអាស្រ័យលើ broker និងគណនី") + """
<div class='box warn'>⚠️ Spread ធំពេលព័ត៌មាន (CPI, NFP, FOMC) និងពេលទីផ្សារទើបបើក។ Scalp ដែលមាន SL តូច អាចត្រូវប៉ះដោយ spread តែម្ដង។
មើលការព្រមានក្នុង 📰 News មុនព័ត៌មានធំ។</div>
"""),
        ("Pip និង Point", """
<p>XAU.KH ប្រើខ្នាតដូចគ្នាគ្រប់កន្លែង (សញ្ញា 🚨 Signals, 📈 Proof, រូប 📊 Analysis):</p>
<table><tr><th>ខ្នាត</th><th>ចម្ងាយតម្លៃ</th><th>ឧទាហរណ៍</th></tr>
<tr><td><span class='en-term'>Point</span> (ខ្ទង់តូចបំផុត)</td><td>$0.01</td><td>4,060.00 → 4,060.01</td></tr>
<tr><td><span class='en-term'>Pip</span></td><td><b>$0.10</b> = 10 points</td><td>4,060.00 → 4,060.10</td></tr>
<tr><td>$1</td><td><b>10 pips</b></td><td>4,060.00 → 4,061.00</td></tr>
<tr><td>$10</td><td><b>100 pips</b></td><td>4,060.00 → 4,070.00</td></tr></table>
<p>នៅលើ MT5 មាសជាធម្មតាមាន<b>ខ្ទង់ទសភាគ 2</b> (Digits = 2) ដូច្នេះ point មួយ = $0.01។ Broker ខ្លះប្រើ 3 ខ្ទង់ (point = $0.001)។
ពិនិត្យនៅ <span class='en-term'>Specification</span>។</p>
<div class='box warn'>⚠️ អ្នកខ្លះ ឬ broker ខ្លះហៅ $1 ថា "pip" ឬ $0.01 ថា "pip"។ ពេលអាន signal ពីកន្លែងណាក៏ដោយ សូមគិតជា<b>ចម្ងាយតម្លៃ ($)</b>
ជាមុន ព្រោះវាមិនច្រឡំ: SL $5 គឺ SL $5 ជានិច្ច។</div>
"""),
        ("Lot: ទំហំ Order", """
<p><span class='en-term'>Lot</span> គឺជាទំហំ order។ សម្រាប់មាស <b>1.00 lot = 100 oz</b> (contract size 100)។ Lot កាន់តែធំ
តម្លៃនីមួយៗដែលរត់ កាន់តែមានឥទ្ធិពលលើគណនី:</p>
""" + bars([("0.01 lot", 1, UP), ("0.05 lot", 5, UP), ("0.10 lot", 10, OR), ("0.50 lot", 50, DN), ("1.00 lot", 100, DN)], h=180,
           caption="ចំណេញ ឬខាត (ដុល្លារ) ពេលតម្លៃមាសរត់ $1 (= 10 pips)") + """
<table><tr><th>Lot</th><th>ទម្ងន់មាស</th><th>តម្លៃរត់ $1</th><th>តម្លៃរត់ $10</th></tr>
<tr><td>0.01</td><td>1 oz</td><td>$1</td><td>$10</td></tr>
<tr><td>0.10</td><td>10 oz</td><td>$10</td><td>$100</td></tr>
<tr><td>1.00</td><td>100 oz</td><td>$100</td><td>$1,000</td></tr></table>
<div class='box tip'>💡 មាសអាចរត់ $10–$30 ក្នុងមួយម៉ោងពេលទីផ្សារសកម្ម ឬព័ត៌មាន។ នេះជាមូលហេតុដែល lot តូចៗ (0.01–0.05) គឺសមរម្យសម្រាប់គណនីតូច។
សញ្ញា 🚨 របស់ XAU.KH បង្ហាញ "💰 0.01 lot: SL −$…" ដើម្បីឱ្យអ្នកឃើញហានិភ័យជាដុល្លារភ្លាមៗ។</div>
"""),
        ("Contract Specification: អានឯកសារបច្ចេកទេស", """
<p>នៅ MT5: Market Watch → ចុចកណ្ដុរស្ដាំលើ XAUUSD → <span class='en-term'>Specification</span>។ អ្នកនឹងឃើញព័ត៌មានដូចខាងក្រោម
(លេខអាចខុសគ្នាតាម broker):</p>
<table><tr><th>វាល</th><th>ឧទាហរណ៍</th><th>អត្ថន័យ</th></tr>
<tr><td>Contract size</td><td>100</td><td>1 lot = 100 oz</td></tr>
<tr><td>Digits</td><td>2</td><td>តម្លៃមាន 2 ខ្ទង់ទសភាគ</td></tr>
<tr><td>Tick size / Tick value</td><td>0.01 / $1</td><td>តម្លៃរត់ $0.01 ជាមួយ 1 lot = $1</td></tr>
<tr><td>Minimal volume · Volume step</td><td>0.01 · 0.01</td><td>Lot តូចបំផុត និងជំហានបន្ថែម</td></tr>
<tr><td>Stops level</td><td>0 ឬច្រើនជាង</td><td>ចម្ងាយអប្បបរមារវាងតម្លៃ និង SL/TP</td></tr>
<tr><td>Swap long / short</td><td>ខុសៗគ្នា</td><td>ថ្លៃកាន់ BUY / SELL ឆ្លងយប់</td></tr>
<tr><td>Sessions</td><td>ច័ន្ទ–សុក្រ</td><td>ម៉ោង trade (មានការផ្អាកខ្លីប្រចាំថ្ងៃ)</td></tr></table>
<div class='box ok'>✅ ពិនិត្យ Specification <b>ម្ដង</b>នៅពេលចាប់ផ្ដើមប្រើ broker ឬប្រភេទគណនីថ្មី។ បើ contract size មិនមែន 100 ទេ ការគណនាទាំងអស់ក្នុងជំពូកនេះត្រូវកែតាម។</div>
"""),
        ("Leverage និង Margin", """
<p><span class='en-term'>Leverage</span> អនុញ្ញាតឱ្យអ្នកបើក order ធំជាងលុយដែលត្រូវដាក់។ លុយដែល broker "ចាក់សោ" ទុកដើម្បីបើក order ហៅថា
<span class='en-term'>Margin</span>:</p>
<div class='box tip'>💡 <b>Margin = តម្លៃមាស × oz ÷ Leverage</b>។ ឧ. 0.01 lot (1 oz) នៅ $4,000: leverage 1:100 → <b>$40</b> · 1:500 → <b>$8</b>។</div>
""" + flow([("Balance", "លុយក្នុងគណនី", BL), ("Equity", "Balance ± P/L ឥឡូវ", GOLD), ("Margin", "លុយត្រូវចាក់សោ", OR), ("Free Margin", "Equity − Margin", UP)],
           caption="ពាក្យទាំង 4 នៅផ្ទាំង Trade ក្នុង MT5") + """
<ul><li><span class='en-term'>Margin Level</span> = Equity ÷ Margin × 100%។ បើវាធ្លាក់ទាបពេក broker ផ្ញើ <span class='en-term'>Margin Call</span>
ហើយនៅកម្រិត <span class='en-term'>Stop Out</span> broker នឹង<b>បិទ order ដោយស្វ័យប្រវត្តិ</b>។ កម្រិតទាំងនេះខុសគ្នាតាម broker។</li></ul>
<div class='box warn'>⚠️ សំខាន់ណាស់: Leverage <b>មិនប្ដូរ</b>ចំណេញ/ខាតក្នុង $1 ទេ។ 0.01 lot នៅតែ $1 ក្នុងមួយ $1 ទោះ 1:100 ឬ 1:1000។ Leverage ខ្ពស់គ្រាន់តែ
<b>អនុញ្ញាតឱ្យបើក lot ធំជាងមុន</b> ដែលជាផ្លូវលឿនបំផុតក្នុងការបំផ្លាញគណនី។ ហានិភ័យពិតត្រូវបានកំណត់ដោយ <b>lot និង SL</b>។</div>
"""),
        ("Swap និង Commission", """
<ul><li><span class='en-term'>Swap</span> (rollover) = ថ្លៃ ឬការប្រាក់ ពេលអ្នកកាន់ order <b>ឆ្លងយប់</b> (ឆ្លងម៉ោងបិទថ្ងៃរបស់ server)។ វាគិតក្នុងមួយ lot
ក្នុងមួយយប់ ហើយ swap BUY និង SELL ខុសគ្នា។ Broker ជាច្រើនគិត swap <b>បីដង</b>នៅយប់មួយក្នុងសប្ដាហ៍ (ជាទូទៅថ្ងៃពុធ) ដើម្បីគ្របដណ្ដប់ចុងសប្ដាហ៍។</li>
<li><span class='en-term'>Commission</span> = ថ្លៃគិតក្នុងមួយ lot នៅលើគណនីប្រភេទខ្លះ (ដែលច្រើនតែមាន spread តូចជាង)។ គណនីស្តង់ដារច្រើនតែគ្មាន commission
ប៉ុន្តែ spread ធំជាង។</li></ul>
<table><tr><th>ថ្លៃ</th><th>ពេលណា</th><th>ឧទាហរណ៍ជាមួយ 0.01 lot</th></tr>
<tr><td>Spread</td><td>រាល់ trade</td><td>$0.30 spread → $0.30</td></tr>
<tr><td>Commission</td><td>រាល់ trade (គណនីខ្លះ)</td><td>ឧ. $7 / lot → $0.07</td></tr>
<tr><td>Swap</td><td>កាន់ឆ្លងយប់</td><td>មើល Swap long/short ក្នុង Specification</td></tr></table>
<div class='box tip'>💡 Scalp និង intraday ដែលបិទក្នុងថ្ងៃ ភាគច្រើនមិនប៉ះ swap។ Trade 4H ដែលកាន់ច្រើនថ្ងៃ គួរគិតបញ្ចូល swap។</div>
"""),
        ("គណនាចំណេញ និងខាត (P/L)", """
<div class='box ok'>✅ <b>P/L = ចម្ងាយតម្លៃ ($) × lot × 100</b> (ឬ = ចម្ងាយ × oz)</div>
""" + zigzag([30, 38, 34, 46, 42, 58, 54, 70], {},
             lines=[(80, 0, 7, "TP 4,068", UP, True), (14, 0, 7, "SL 4,042", DN, True), (30, 0, 7, "Entry", BL, False)],
             caption="ឧទាហរណ៍ BUY: Entry 4,050 · SL 4,042 · TP 4,068") + """
<table><tr><th>ករណី</th><th>ការគណនា</th><th>លទ្ធផល</th></tr>
<tr><td>BUY 0.02 lot · 4,050 → TP 4,068</td><td>$18 × 0.02 × 100</td><td style='color:#34C759'><b>+$36</b></td></tr>
<tr><td>BUY 0.02 lot · 4,050 → SL 4,042</td><td>$8 × 0.02 × 100</td><td style='color:#FF3B30'><b>−$16</b></td></tr>
<tr><td>SELL 0.05 lot · 4,080 → 4,071</td><td>$9 × 0.05 × 100</td><td style='color:#34C759'><b>+$45</b></td></tr>
<tr><td>SELL 0.01 lot · 4,080 → 4,102</td><td>$22 × 1 oz</td><td style='color:#FF3B30'><b>−$22</b></td></tr></table>
<p>ក្នុងឧទាហរណ៍ BUY ខាងលើ ហានិភ័យ = $8 ហើយចំណេញគោលដៅ = $18។ សមាមាត្រ <span class='en-term'>Risk:Reward</span> = 1 : 2.25។
ការគណនានេះមិនទាន់ដក spread និង commission ទេ។</p>
"""),
        ("ពី Risk ទៅ Lot: គណនាទំហំ Order", """
<p>អ្នកជំនាញមិនជ្រើស lot តាមអារម្មណ៍ទេ។ ពួកគេចាប់ផ្ដើមពី<b>ចំនួនលុយដែលព្រមខាត</b> ហើយគណនា lot ថយក្រោយ:</p>
""" + flow([("Risk $", "ឧ. 1% = $10", BL), ("SL ($)", "ចម្ងាយ entry → SL", DN), ("Lot", "Risk ÷ (SL × 100)", GOLD), ("បង្គត់ចុះ", "តាម volume step", UP)],
           caption="Lot = Risk ($) ÷ (ចម្ងាយ SL $ × 100)") + """
<table><tr><th>Risk</th><th>SL</th><th>ការគណនា</th><th>Lot</th></tr>
<tr><td>$10</td><td>$5</td><td>10 ÷ (5 × 100)</td><td><b>0.02</b></td></tr>
<tr><td>$10</td><td>$8</td><td>10 ÷ 800 = 0.0125</td><td><b>0.01</b> (បង្គត់ចុះ)</td></tr>
<tr><td>$20</td><td>$4</td><td>20 ÷ 400</td><td><b>0.05</b></td></tr>
<tr><td>$5</td><td>$22</td><td>5 ÷ 2,200 = 0.002</td><td><b>តូចជាង 0.01</b> → កុំ trade</td></tr></table>
<div class='box warn'>⚠️ ជួរចុងក្រោយសំខាន់ណាស់: បើ lot តូចបំផុត (0.01) នៅតែធ្វើឱ្យខាតលើស risk ដែលអ្នកកំណត់ នោះ trade នេះ<b>ធំពេក</b>សម្រាប់គណនីអ្នក។
កុំកាត់ SL ឱ្យខ្លី ដើម្បីបញ្ចូល lot។ ការគ្រប់គ្រង risk លម្អិតនៅ Chapter 32។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ គិតថា leverage ខ្ពស់ = risk ទាប (ផ្ទុយពីការពិត បើវាធ្វើឱ្យបើក lot ធំ)</li>
<li>❌ ភ្លេចថា SELL បិទនៅ <b>Ask</b> ហើយដាក់ SL ជិតពេក</li>
<li>❌ ច្រឡំ pip, point និង $ ហើយបើក lot ធំជាងដែលគ្រោង 10 ដង</li>
<li>❌ មិនដឹង SL ជាដុល្លារ មុនពេលចុច BUY/SELL</li>
<li>❌ Trade ពេលព័ត៌មានធំ ដោយមិនគិតពី spread ដែលរីកធំ</li></ul>
<div class='box ok'>✅ ទម្លាប់ល្អ: មុនរាល់ trade និយាយឱ្យឮថា "<b>បើខុស ខ្ញុំខាត $… បើត្រូវ ខ្ញុំចំណេញ $…</b>"។ បើអ្នកនិយាយមិនចេញ កុំចុច។</div>
"""),
    ],
    summary=["BUY បើកនៅ Ask បិទនៅ Bid · SELL បើកនៅ Bid បិទនៅ Ask · Spread = Ask − Bid",
             "1 pip = $0.10 · $1 = 10 pips · 1 point = $0.01 (Digits 2)",
             "1.00 lot = 100 oz · 0.01 lot = 1 oz → $1 ផ្លាស់ទី = $1",
             "Margin = តម្លៃ × oz ÷ Leverage · leverage មិនប្ដូរ P/L ក្នុង $1 ទេ",
             "P/L = ចម្ងាយ $ × lot × 100 · Lot = Risk ÷ (SL $ × 100)"],
    exercise=["Ask = 4,071.45, Bid = 4,071.20។ តើ spread ប៉ុន្មានដុល្លារ និងប៉ុន្មាន pips?",
              "SELL 0.03 lot នៅ 4,090 ហើយ TP នៅ 4,075។ តើចំណេញប៉ុន្មាន? (មិនគិត spread)",
              "គណនី $500, risk 2%, SL $6។ តើគួរប្រើ lot ប៉ុន្មាន?",
              "យក signal 🚨 ចុងក្រោយក្នុង group: គណនា SL និង TP ជាដុល្លារ សម្រាប់ 0.02 lot ហើយធៀបនឹងលទ្ធផលក្នុង 📈 Proof។"],
)
