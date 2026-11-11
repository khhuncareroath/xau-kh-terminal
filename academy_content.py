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

LESSONS += [
    # ---------------- PART 3 — ICT
    dict(ch=11, part="PART 3 · ICT", title="ICT Foundations · គោលគំនិត ICT",
         body="""<b>ICT</b> (Inner Circle Trader) = វិធីមើលទីផ្សារតាម <b>liquidity</b>: តម្លៃរត់ទៅរក stop/orders
• គំនិតមូលដ្ឋាន: អ្នកធំត្រូវការ <b>liquidity</b> (orders ច្រើន) ដើម្បីបើក position ធំ
• តម្លៃរត់ពី <b>liquidity មួយ → liquidity មួយទៀត</b> (ពី IRL ទៅ ERL)
• <b>Dealing range</b> = ចន្លោះ swing high និង swing low ដែលតម្លៃកំពុងដើរ
• ការយល់ខុស: ICT មិនមែន "អ្នកធំបោកយើង" គ្រប់ចលនាទេ · OB/FVG ទាំងអស់ <b>មិនមែន</b>ដំណើរការទាំងអស់
• ICT ល្អ = <b>context</b> (HTF + liquidity + time) មិនមែនគូរប្រអប់ច្រើន

💡 យើងបានសាកល្បង: OB entry SL តូចតែឯង <b>ខាត</b> លើមាស · ICT ល្អសម្រាប់ <b>analysis</b> និង <b>context</b>""",
         quiz=("ក្នុង ICT តម្លៃភាគច្រើនរត់ទៅរក...", ["Indicator", "Liquidity (កន្លែងដែល stop/orders ដេក)", "លេខមូល", "ព័ត៌មាន"], 1,
               "ICT មើលថាតម្លៃរត់ពី liquidity មួយទៅមួយទៀត ព្រោះអ្នកធំត្រូវការ orders ច្រើន។"), chart="liquidity"),
    dict(ch=12, part="PART 3 · ICT", title="Liquidity: BSL · SSL · Sweeps",
         body="""• <b>BSL</b> (Buy-side liquidity) = stop របស់អ្នកលក់ + buy stop <b>លើ</b> swing high
• <b>SSL</b> (Sell-side liquidity) = stop របស់អ្នកទិញ <b>ក្រោម</b> swing low
• កន្លែងល្អ: <b>Equal highs/lows</b>, Prev day high/low, Prev week high/low, Asia/London high/low
• <b>ELQ</b> = liquidity ខាងក្រៅ (ចុង range) · <b>ILQ</b> = ខាងក្នុង range
• <b>Sweep / Raid</b> ($$) = wick ឆ្លង level ហើយ <b>បិទត្រឡប់ចូល</b> → stop ត្រូវបានយក
• Sweep + <b>CHOCH</b> ទិសផ្ទុយ = setup reversal ដ៏ល្បី

👉 Chart ថ្ងៃនេះ: រក <b>ELQ</b> ពីរចុង, <b>ILQ</b> (ទឹកក្រូច) និង <b>$$</b>""",
         quiz=("SSL (Sell-side liquidity) ស្ថិតនៅ...", ["លើ swing high", "ក្រោម swing low", "នៅ POC", "នៅ EMA"], 1,
               "SSL = stop loss របស់អ្នកទិញ ដែលដាក់ក្រោម swing low។"), chart="liquidity"),
    dict(ch=13, part="PART 3 · ICT", title="Fair Value Gap · FVG · IFVG",
         body="""• <b>FVG</b> = ចន្លោះតម្លៃដែលទៀន 3 គ្រាប់ទុក (wick ទៀន 1 និង 3 មិនប៉ះគ្នា) ពេលរត់លឿន
• <b>Bullish FVG</b> (ក្រោមតម្លៃ) = support · <b>Bearish FVG</b> (លើតម្លៃ) = resistance
• <b>Displacement</b> = ទៀនធំដែលបង្កើត FVG · FVG ពី displacement ខ្លាំងជាង
• <b>CE</b> (Consequent encroachment) = 50% នៃ FVG · តម្លៃច្រើនតែប៉ះត្រឹម CE
• <b>Mitigated</b> = តម្លៃមកបំពេញ · <b>IFVG</b> = FVG ដែលបែក ក្លាយជាទិសផ្ទុយ
• FVG ខ្សោយ: តូចពេក, ផ្ទុយ HTF, នៅកណ្ដាល range

👉 Chart ថ្ងៃនេះ: ប្រអប់ពណ៌ <b>FVG</b> · សញ្ញា 🤬 COMBO SCALP ប្រើ 15m FVG""",
         quiz=("FVG កើតឡើងពេល...", ["ទៀន 3 គ្រាប់ wick ទៀន 1 និង 3 មិនប៉ះគ្នា", "ទៀន doji", "តម្លៃនៅ POC", "Spread ធំ"], 0,
               "FVG = ចន្លោះដែលទៀនទី 1 និងទី 3 មិនត្រួតគ្នា ពេលតម្លៃរត់លឿន។"), chart="fvg"),
    dict(ch=14, part="PART 3 · ICT", title="Order Block · Breaker · Mitigation",
         body="""• <b>Bullish OB</b> = ទៀនចុះចុងក្រោយ មុនចលនាឡើងខ្លាំងដែល <b>បែក structure</b>
• <b>Bearish OB</b> = ទៀនឡើងចុងក្រោយ មុនចលនាចុះខ្លាំង
• <b>Breaker</b> = OB ដែលបរាជ័យ (តម្លៃបែកឆ្លង) ក្លាយជាតំបន់ទិសផ្ទុយ
• <b>Mitigation block</b> = OB ដែលតម្លៃត្រឡប់មកប៉ះ ដើម្បី "ដោះស្រាយ" orders ចាស់
• OB ល្អ: មាន <b>displacement</b> + <b>BOS</b> + FVG នៅក្បែរ + ស្រប HTF
• OB ខុស (invalid): បិទទៀនឆ្លងហួស OB

⚠️ យើងសាកល្បង 62 វិធី: limit order នៅ OB + SL តូច <b>ខាត</b> លើមាស · OB = តំបន់មើល មិនមែនច្បាប់ចូលតែឯង""",
         quiz=("Bullish Order Block គឺ...", ["ទៀនឡើងធំណាមួយ", "ទៀនចុះចុងក្រោយ មុនចលនាឡើងខ្លាំងដែលបែក structure", "Wick វែង", "កម្រិត POC"], 1,
               "Bullish OB = ទៀនចុះចុងក្រោយ មុន displacement ឡើងដែល BOS។"), chart="fvg"),
    dict(ch=15, part="PART 3 · ICT", title="Premium & Discount · EQ · OTE",
         body="""• <b>Dealing range</b> = swing low → swing high · <b>EQ</b> (Equilibrium) = 50%
• លើ EQ = <b>Premium</b> (ថ្លៃ: រកលក់) · ក្រោម EQ = <b>Discount</b> (ថោក: រកទិញ)
• <b>Fibonacci</b>: 0.5 = EQ · <b>OTE</b> (Optimal Trade Entry) = 0.62–0.79
• ច្បាប់: uptrend → ទិញក្នុង <b>discount</b> · downtrend → លក់ក្នុង <b>premium</b>
• កុំទិញក្នុង premium ក្នុង range (ថ្លៃពេក) · ប្រើជាមួយ structure ជានិច្ច

💡 ករណីលើកលែង: <b>breakout</b> (ដូចសញ្ញា 🖕) ចាកចេញពី range ដូច្នេះ premium/discount សំខាន់តិច

👉 Chart ថ្ងៃនេះ: បន្ទាត់ <b>EQ 50%</b>""",
         quiz=("ក្នុង uptrend គួររកទិញនៅតំបន់...", ["Premium (លើ EQ)", "Discount (ក្រោម EQ)", "នៅ high ចុងក្រោយ", "កន្លែងណាក៏បាន"], 1,
               "ទិញថោក (discount) ក្នុង uptrend ផ្ដល់ RR ល្អជាង។"), chart="pd"),
    dict(ch=16, part="PART 3 · ICT", title="Sessions & Kill Zones (ម៉ោងកម្ពុជា)",
         body="""<b>ម៉ោងកម្ពុជា (រដូវរងារ/winter):</b>
• 🌏 <b>Asia</b> 07:00–14:00 · range តូច បង្កើត liquidity
• 🇬🇧 <b>London</b> 14:00–19:00 · <b>Kill zone</b> 14:00–17:00 · ច្រើនតែ sweep Asia high/low
• 🇺🇸 <b>New York</b> 19:30–00:00 · <b>Kill zone</b> 19:30–22:00 · ព័ត៌មាន US 20:30
• (រដូវក្ដៅ/summer US DST: ម៉ោងលឿន 1 ម៉ោង)
• <b>Judas swing</b> = ចលនាបោកដំបូងនៃ session (sweep) មុនទិសពិត
• <b>Daily bias</b> = ទិសដែលរំពឹងសម្រាប់ថ្ងៃ (ពី HTF + liquidity)

👉 Analysis របស់យើងចេញមុន session នីមួយៗ: Asia · London · New York""",
         quiz=("London kill zone (ម៉ោងកម្ពុជា winter) ប្រហែល...", ["07:00–09:00", "14:00–17:00", "23:00–02:00", "12:00–13:00"], 1,
               "London បើកប្រហែល 14:00–15:00 ម៉ោងកម្ពុជា (winter)។ Kill zone = ម៉ោងសកម្មបំផុត។"), chart=None),
    dict(ch=17, part="PART 3 · ICT", title="Advanced ICT: PO3 · SMT · OTE · Turtle Soup",
         body="""• <b>PO3</b> (Power of Three) = <b>A</b>ccumulation (Asia) → <b>M</b>anipulation (sweep/Judas) → <b>D</b>istribution (ចលនាពិត)
• <b>SMT divergence</b> = មាស vs ប្រាក់ (XAG) ឬ DXY ធ្វើ high/low មិនដូចគ្នា → សញ្ញាខ្សោយ
• <b>OTE</b> = ចូលនៅ 62–79% retracement បន្ទាប់ពី displacement
• <b>Turtle Soup</b> = sweep high/low ចាស់ ហើយត្រឡប់ → ចូលទិសផ្ទុយ
• ច្បាប់មាស: <b>កុំដាក់ concept ច្រើនពេកលើ chart តែមួយ</b> · 2–3 concept ស្របគ្នាគ្រប់គ្រាន់

⚠️ Concept ល្អ ≠ ចំណេញ · ត្រូវសាកល្បង (backtest) ជានិច្ច · Chapter 35 នឹងបង្រៀន""",
         quiz=("PO3 គឺ...", ["Accumulation → Manipulation → Distribution", "Buy → Sell → Buy", "RSI 3 ដង", "3 lots"], 0,
               "Power of Three: ប្រមូល (Asia) → បោក (sweep) → រត់ពិត (distribution)។"), chart=None),
    # ---------------- PART 4 — VOLUME PROFILE
    dict(ch=18, part="PART 4 · Volume Profile", title="Volume Foundations",
         body="""• <b>Volume</b> = ចំនួន contracts/ticks ដែលបានជួញដូរ · បង្ហាញ <b>កម្លាំង</b> ពីក្រោយចលនា
• <b>Tick volume</b> (broker/MT5) = ចំនួនការប្ដូរតម្លៃ · <b>Real volume</b> = COMEX futures
• មាស spot <b>គ្មាន</b> volume កណ្ដាលពិត · យើងប្រើ futures volume ជាជំនួយ
• ចលនាឡើង + volume ខ្ពស់ = ខ្លាំង · ចលនាឡើង + volume ទាប = ខ្សោយ (អាចត្រឡប់)
• កំណត់: tick volume រវាង broker ខុសគ្នា · កុំសន្និដ្ឋានធំពីវាតែឯង""",
         quiz=("Volume ក្នុង MT5 សម្រាប់មាស spot ជា...", ["Real volume ពី exchange", "Tick volume (ចំនួនការប្ដូរតម្លៃ)", "ចំនួនអ្នក trade", "លុយសរុប"], 1,
               "Spot gold គ្មាន exchange កណ្ដាល។ MT5 បង្ហាញ tick volume។"), chart=None),
    dict(ch=19, part="PART 4 · Volume Profile", title="Volume Profile: POC · VAH · VAL",
         body="""• <b>Volume Profile</b> = volume តាម <b>តម្លៃ</b> (bar ផ្ដេក) មិនមែនតាមពេល
• <b>POC</b> (Point of Control) = តម្លៃដែល volume ច្រើនបំផុត = "តម្លៃយុត្តិធម៌"
• <b>Value Area</b> = 70% នៃ volume · <b>VAH</b> = កំពូល · <b>VAL</b> = បាត
• <b>HVN</b> (High volume node) = តម្លៃយឺត/ឈប់ · <b>LVN</b> (Low volume node) = តម្លៃរត់លឿនឆ្លង
• តម្លៃច្រើនតែត្រឡប់មក <b>POC</b> · VAH/VAL = S/R

👉 Chart ថ្ងៃនេះ: bar ខៀវខាងស្ដាំ = volume profile 5 ថ្ងៃ · បន្ទាត់ <b>POC</b>""",
         quiz=("POC គឺ...", ["តម្លៃខ្ពស់បំផុត", "តម្លៃដែលមាន volume ច្រើនបំផុត", "តម្លៃបើក", "EMA 200"], 1,
               "Point of Control = តម្លៃដែលជួញដូរច្រើនបំផុត។"), chart="vp"),
    dict(ch=20, part="PART 4 · Volume Profile", title="ប្រភេទ Volume Profile",
         body="""• <b>Session VP</b> = តាម session (Asia/London/NY) · ល្អសម្រាប់ intraday
• <b>Fixed Range VP</b> = អ្នកជ្រើសចន្លោះខ្លួនឯង (ឧ. ពី swing low ដល់ swing high)
• <b>Visible Range VP</b> = អ្វីដែលឃើញលើអេក្រង់
• <b>Developing VP</b> = POC ផ្លាស់ទីតាមពេល (ឃើញ value ផ្លាស់ទី)
• <b>Composite VP</b> = ច្រើនថ្ងៃ/សប្ដាហ៍ · level ធំ
• ជ្រើស: intraday → Session · swing → Composite

💡 សញ្ញា 🤬 Plan របស់យើងប្រើ <b>Session VP</b> (រាង P/b) និង POC""",
         quiz=("ចង់ trade intraday ប្រើ VP ប្រភេទណាល្អ?", ["Composite 1 ឆ្នាំ", "Session VP", "គ្មាន", "Weekly"], 1,
               "Intraday ត្រូវការ level ថ្មីៗ: Session VP (Asia/London/NY)។"), chart=None),
    dict(ch=21, part="PART 4 · Volume Profile", title="Advanced VP: Acceptance · Shapes",
         body="""• <b>Acceptance</b> = តម្លៃនៅក្នុង value area ថ្មី · <b>Rejection</b> = ប៉ះហើយចេញលឿន (LVN)
• <b>Value migration</b>: value ឡើងរាល់ថ្ងៃ = uptrend · ចុះ = downtrend
• <b>Poor high/low</b> = កំពូល/បាតរាបស្មើ (មិនទាន់បញ្ចប់) → ច្រើនតែត្រូវយកវិញ
• <b>Single prints</b> = តំបន់ volume តូចខ្លាំង → តម្លៃច្រើនតែត្រឡប់មកបំពេញ
• <b>រាង</b>: <b>P</b> = buyers គ្រប់គ្រង · <b>b</b> = sellers គ្រប់គ្រង · <b>D</b> = តុល្យភាព
• VP + Structure: POC នៅក្បែរ OB/FVG = តំបន់ខ្លាំង

💡 រាង P/b ធ្វើការល្អ <b>មុនពេល</b> ថ្ងៃរត់ច្រើន (Day Meter &lt; 70%) · យើងបានសាកល្បងហើយ""",
         quiz=("Profile រាង b មានន័យថា...", ["Buyers គ្រប់គ្រង", "Sellers គ្រប់គ្រង (volume នៅបាត)", "តុល្យភាព", "គ្មានន័យ"], 1,
               "b-shape = volume ប្រមូលនៅខាងក្រោម: sellers បានរុញ និងគ្រប់គ្រង។"), chart=None),
]
