"""XAU.KH Academy lessons (the owner's 45-chapter map). Khmer-first, English trading terms, phone-short.
Each lesson: ch, title, body (Telegram HTML), quiz (question, options, correct index, explanation), chart (None or
an analysis-picture focus for the "look at today's chart" part).
"""

LESSONS = [
    # ---------------- PART 0 — INTRODUCTION
    dict(ch=1, part="PART 0 · Introduction", title="ការធ្វើដំណើរជាអ្នក Trade · The Trading Journey",
         body="""<b>Trading គឺជាអ្វី?</b> ការទិញ/លក់ក្នុងរយៈពេលខ្លី ដើម្បីចំណេញពីចលនាតម្លៃ។
• <b>Investing</b> = កាន់យូរ (ឆ្នាំ) · <b>Trading</b> = ម៉ោង/ថ្ងៃ មានច្បាប់ · <b>Gambling</b> = ចូលដោយអារម្មណ៍ គ្មានផែនការ
• អ្នកជំនាញ <b>មិនទាយ</b> ទីផ្សារទេ។ ពួកគេ <b>រង់ចាំ setup</b> ការពារ <b>risk</b> ហើយ <b>កត់ត្រា</b>គ្រប់ trade
• ការពិត: អ្នកជំនាញក៏ខាតដែរ (30–40% នៃ trade)។ អ្វីដែលធ្វើឱ្យចំណេញ គឺ <b>ខាតតូច ចំណេញធំ</b>
• <b>ឈ្នះ 100%</b> មិនមានទេ។ អ្នកណានិយាយបែបនោះ កំពុងលក់អ្វីមួយ

<b>របៀបរៀន:</b> អានមួយមេរៀនក្នុងមួយថ្ងៃ · ឆ្លើយ quiz · មើលចំណុចដូចគ្នានៅលើ chart ពិត (/check)""",
         quiz=("អ្វីដែលធ្វើឱ្យអ្នក trade ជំនាញចំណេញ?",
               ["ឈ្នះគ្រប់ trade", "ខាតតូច ចំណេញធំ និងមានច្បាប់", "Trade ច្រើនជាងគេ", "ប្រើ lot ធំ"], 1,
               "អ្នកជំនាញក៏ខាតដែរ ប៉ុន្តែខាតតូច ចំណេញធំ ហើយធ្វើតាមច្បាប់។"), chart=None),
    dict(ch=2, part="PART 0 · Introduction", title="ស្គាល់ទីផ្សារមាស · The Gold Market",
         body="""<b>XAU</b> = មាស 1 អោន (oz) · <b>XAUUSD</b> = តម្លៃមាស 1 អោន គិតជាដុល្លារ
• <b>Spot</b> (broker CFD ដូច Exness) ≠ <b>Futures</b> (COMEX GC) · តម្លៃខុសគ្នាបន្តិច
• <b>អ្វីធ្វើឱ្យមាសឡើង/ចុះ?</b>
  – ដុល្លារ (DXY) ឡើង → មាសតែងតែ <b>ចុះ</b> 📉
  – ការប្រាក់/ទិន្នផល US 10y ឡើង → មាស <b>ចុះ</b>
  – អតិផរណា (CPI) ខ្ពស់ / សង្គ្រាម / ភ័យខ្លាច → មាស <b>ឡើង</b> (safe haven)
• អ្នកចូលរួម: ធនាគារកណ្ដាល ធនាគារ មូលនិធិ (ធំ) និង retail ដូចយើង (តូច)

👉 រាល់ព្រឹក <b>Daily Outlook</b> ក្នុង 📊 Analysis បង្ហាញ DXY / 10y / VIX សម្រាប់ថ្ងៃនោះ""",
         quiz=("ពេលដុល្លារ (DXY) ឡើងខ្លាំង មាសតែងតែ...", ["ឡើង", "ចុះ", "មិនប្រែប្រួល", "ឡើង 2 ដង"], 1,
               "មាសគិតជាដុល្លារ។ ដុល្លារខ្លាំង → មាសថ្លៃសម្រាប់អ្នកទិញផ្សេង → មាសតែងតែចុះ។"), chart=None),
    # ---------------- PART 1 — FOUNDATIONS
    dict(ch=3, part="PART 1 · Foundations", title="Platform: TradingView & MetaTrader 5",
         body="""• <b>TradingView</b> = មើល chart គូរ level វិភាគ · <b>MT5</b> = បើក/បិទ order ពិតជាមួយ broker
• <b>Market Watch</b>: រក symbol <b>XAUUSD</b> (Exness អាចជា <b>XAUUSDm</b>)
• <b>Candlestick chart</b> ល្អជាង line chart ព្រោះឃើញ Open High Low Close
• <b>Timeframe</b>: M1 M5 M15 M30 H1 H4 D1 · ទៀន 1 = រយៈពេល 1 timeframe
• Setting ល្អ: ពណ៌ទៀន 2 ពណ៌ច្បាស់ · បិទ indicator ច្រើនពេក · ម៉ោង GMT+7

💡 យើងប្រើ <b>4H</b> សម្រាប់សញ្ញា 🖕 និង <b>15m/5m</b> សម្រាប់ analysis/entry""",
         quiz=("Platform មួយណាសម្រាប់បើក order ពិតជាមួយ broker?", ["TradingView", "MetaTrader 5", "Telegram", "Excel"], 1,
               "MT5 ភ្ជាប់ជាមួយ broker ដើម្បីបើក/បិទ order។ TradingView សម្រាប់វិភាគ។"), chart=None),
    dict(ch=4, part="PART 1 · Foundations", title="តម្លៃ: Bid Ask Spread Pip Lot · Understanding Price",
         body="""• <b>Bid</b> = តម្លៃលក់ · <b>Ask</b> = តម្លៃទិញ · <b>Spread</b> = Ask − Bid (ថ្លៃរបស់ broker)
• មាស: <b>1 pip = $0.10</b> · ឧ. 4,000.00 → 4,010.00 = <b>100 pips</b>
• <b>Lot</b>: 1.00 lot = 100 oz · <b>0.01 lot = 1 oz</b> → តម្លៃរត់ $1 = ចំណេញ/ខាត <b>$1</b>
• <b>Leverage/Margin</b>: ខ្ចីប្រាក់ពី broker ដើម្បីបើក lot ធំ · leverage ខ្ពស់ ≠ risk តូច
• <b>Swap</b> = ថ្លៃកាន់ order ឆ្លងយប់ · <b>Commission</b> = ថ្លៃក្នុងមួយ lot (account ខ្លះ)

<b>គណនា P/L:</b> ចម្ងាយ ($) × oz · ឧ. SL $22 × 0.01 lot (1 oz) = <b>−$22</b>
👉 សញ្ញា 🖕 របស់យើងបង្ហាញ "💰 0.01 lot: SL −$22" ជានិច្ច""",
         quiz=("តម្លៃមាសរត់ពី 4,000 ទៅ 4,010 ជាមួយ 0.01 lot ចំណេញប៉ុន្មាន?", ["$1", "$10", "$100", "$0.10"], 1,
               "0.01 lot = 1 oz។ តម្លៃរត់ $10 × 1 oz = $10 (= 100 pips)។"), chart=None),
    dict(ch=5, part="PART 1 · Foundations", title="ទៀន Candlestick · Reading Candles",
         body="""ទៀន 1 = <b>O</b>pen <b>H</b>igh <b>L</b>ow <b>C</b>lose · <b>Body</b> = Open→Close · <b>Wick</b> = High/Low
• <b>Bullish</b> (បៃតង) បិទលើ Open · <b>Bearish</b> (ក្រហម) បិទក្រោម Open
• <b>Rejection / Pin bar</b>: wick វែង body តូច → តម្លៃត្រូវបានបដិសេធ
• <b>Engulfing</b>: ទៀនធំគ្របទៀនមុនទាំងស្រុង → កម្លាំងប្ដូរទិស
• <b>Inside bar</b>: ទៀននៅក្នុងទៀនមុន → ទីផ្សាររង់ចាំ
• សំខាន់: ទៀនមួយ <b>គ្មានន័យ</b> បើគ្មាន <b>context</b> (នៅ level ណា? trend ណា?)

💡 Pin bar នៅ support ក្នុង uptrend = ខ្លាំង · Pin bar កណ្ដាល range = ខ្សោយ""",
         quiz=("ទៀនមាន wick ក្រោមវែង body តូច នៅ support មានន័យថា...", ["អ្នកលក់ឈ្នះ", "តម្លៃក្រោមត្រូវបានបដិសេធ (buyers ការពារ)", "គ្មានន័យ", "ត្រូវលក់ភ្លាម"], 1,
               "Wick ក្រោមវែង = តម្លៃចុះទៅ ប៉ុន្តែត្រូវបានរុញឡើងវិញ: buyers ការពារ level នោះ។"), chart=None),
    dict(ch=6, part="PART 1 · Foundations", title="Timeframe ពីធំទៅតូច · Multi-Timeframe",
         body="""• <b>HTF</b> (D1 H4) = ទិសធំ · <b>LTF</b> (M15 M5) = ចំណុចចូល
• វិធី <b>Top-down</b>: D1 → H4 → H1 → M30 → M15 (setup) → M5 (confirmation)
• <b>Scalping</b> = នាទី (M1–M5) · <b>Intraday</b> = បិទក្នុងថ្ងៃ (M15–H4) · <b>Swing</b> = ច្រើនថ្ងៃ
• ច្បាប់: ទិស LTF គួរ <b>ស្របនឹង</b> HTF · បើផ្ទុយ = pullback ប្រើ lot តូច
• កំហុសញឹកញាប់: ប្ដូរ timeframe រហូតដល់ឃើញអ្វីដែលខ្លួនចង់ឃើញ ❌

👉 រូបភាព Analysis របស់យើងមាន <b>D 4H 1H 30m 15m 5m</b> ↑↓ នៅខាងលើជានិច្ច""",
         quiz=("15m ឡើង ប៉ុន្តែ D/4H/1H ចុះ។ អ្វីត្រឹមត្រូវ?", ["ទិញ lot ធំ", "ប្រហែលជា pullback: lot តូច ឬរង់ចាំលក់", "មិនសំខាន់", "ប្ដូរទៅ 1m"], 1,
               "ពេល LTF ផ្ទុយ HTF ភាគច្រើនជា pullback។ ការពារ risk ឬរង់ចាំ setup តាមទិសធំ។"), chart=None),
    # ---------------- PART 2 — TECHNICAL ANALYSIS & STRUCTURE
    dict(ch=7, part="PART 2 · Technical Analysis", title="Support & Resistance",
         body="""• <b>Support</b> = កម្រិតដែលអ្នកទិញការពារ · <b>Resistance</b> = កម្រិតដែលអ្នកលក់ការពារ
• <b>Supply/Demand zone</b> = តំបន់ (មិនមែនបន្ទាត់តែមួយ) ដែលតម្លៃរត់ចេញលឿន
• <b>Strong level</b>: ប៉ះច្រើនដង + រត់ចេញខ្លាំង · <b>Fresh</b> (មិនទាន់ប៉ះ) ខ្លាំងជាង <b>tested</b>
• <b>Breakout</b> = បិទទៀនឆ្លង level · <b>False breakout</b> = ឆ្លងតែ wick ហើយត្រឡប់ចូល
• Level ដែលបែក → ប្ដូរតួនាទី (support ក្លាយជា resistance)

👉 Daily Outlook មាន <b>Resistance / Pivot / Support</b> រាល់ព្រឹក""",
         quiz=("តម្លៃឆ្លង resistance តែ wick ហើយទៀនបិទក្រោមវិញ ហៅថា...", ["Breakout ពិត", "False breakout", "Support", "Trend"], 1,
               "Breakout ពិតត្រូវ <b>បិទទៀន</b> ឆ្លង level។ ឆ្លងតែ wick = false breakout។"), chart=None),
    dict(ch=8, part="PART 2 · Technical Analysis", title="Trend & Trendline",
         body="""• <b>Uptrend</b> = <b>HH</b> (Higher High) + <b>HL</b> (Higher Low) · <b>Downtrend</b> = <b>LH</b> + <b>LL</b>
• <b>Trendline</b> ត្រឹមត្រូវ: ភ្ជាប់យ៉ាងតិច 2–3 swing low (uptrend) ឬ swing high (downtrend)
• <b>Channel</b> = trendline + បន្ទាត់ស្របម្ខាងទៀត
• <b>Dynamic S/R</b>: EMA 20/50 ដើរតួជា support/resistance ក្នុង trend
• <b>Trap</b>: trendline បែកតែមួយទៀន ≠ trend ប្ដូរ · រង់ចាំ structure (BOS/CHOCH)

👉 រូប Analysis សរសេរ <b>HH HL LH LL</b> លើ swing និងមាន EMA ពណ៌ទឹកក្រូច/ខៀវ""",
         quiz=("Uptrend មានលក្ខណៈ...", ["LH + LL", "HH + HL", "HH + LL", "គ្មាន swing"], 1,
               "Uptrend = ខ្ពស់ថ្មីខ្ពស់ជាងមុន (HH) និងទាបថ្មីខ្ពស់ជាងមុន (HL)។"), chart="structure"),
    dict(ch=9, part="PART 2 · Technical Analysis", title="Market Structure: BOS · CHOCH · MSS",
         body="""• <b>Swing high/low</b> = កំពូល/បាតដែលបញ្ជាក់រួច
• <b>External structure</b> = swing ធំ (ចុង range) · <b>Internal</b> = swing តូចនៅក្នុង range
• <b>BOS</b> (Break of Structure) = <b>បិទទៀន</b>ឆ្លង swing ក្នុងទិសដដែល → trend បន្ត
• <b>CHOCH / MSS</b> = បិទឆ្លង swing <b>ផ្ទុយ</b>ទិស → trend អាចប្ដូរ
• <b>Displacement</b> = ទៀនធំ រហ័ស ពេលបែក → ខ្លាំងជាង
• <b>Invalidation</b>: setup ខុសពេលតម្លៃបិទឆ្លង swing ដែលការពារវា

👉 រកមើល <b>CHOCH ↑ / BOS</b> លើរូប chart ថ្ងៃនេះ ខាងក្រោម""",
         quiz=("Downtrend ហើយទៀនបិទលើ swing high ចុងក្រោយ ហៅថា...", ["BOS ចុះ", "CHOCH (អាចប្ដូរទិសឡើង)", "Liquidity", "FVG"], 1,
               "ការបែក structure ផ្ទុយទិស trend = CHOCH/MSS: សញ្ញាដំបូងថា trend អាចប្ដូរ។"), chart="structure"),
    dict(ch=10, part="PART 2 · Technical Analysis", title="Price Action: Impulse · Correction · Retest",
         body="""• <b>Impulse</b> = ចលនាខ្លាំងតាមទិស trend · <b>Correction</b> = ថយក្រោយយឺតៗ
• <b>Consolidation</b> (range តូច) → <b>Expansion</b> (រត់ខ្លាំង) · វដ្តនេះកើតឡើងរហូត
• <b>Rejection</b> = តម្លៃប៉ះ level ហើយត្រូវរុញចេញ · <b>Acceptance</b> = បិទទៀនច្រើនហួស level
• <b>Breakout + Retest</b> = បែក level ហើយត្រឡប់មកប៉ះម្ដងទៀត មុនបន្ត
• មើល <b>របៀប</b>ដែលតម្លៃមកដល់ level: លឿនខ្លាំង (impulse) ឬយឺត (correction)

💡 សញ្ញា 🖕 4H របស់យើង = <b>expansion</b> បន្ទាប់ពី range 30 ទៀន 4H""",
         quiz=("តម្លៃបិទទៀនជាច្រើនហួស level ហើយនៅទីនោះ ហៅថា...", ["Rejection", "Acceptance", "Correction", "Spread"], 1,
               "Acceptance = ទីផ្សារទទួលយកតម្លៃថ្មី (បិទទៀនហួស និងនៅបាន)។"), chart=None),
]
