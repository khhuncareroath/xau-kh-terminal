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

LESSONS += [
    # ---------------- PART 5 — ORDER FLOW
    dict(ch=22, part="PART 5 · Order Flow", title="Order Flow Foundations",
         body="""• <b>Order flow</b> = មើល <b>អ្នកណាកំពុងទិញ/លក់</b> និងកម្លាំងប៉ុណ្ណា
• <b>Market order</b> = ទិញ/លក់ភ្លាម (aggressive) · <b>Limit order</b> = រង់ចាំតម្លៃ (passive)
• Market buy ស៊ី limit sell នៅ <b>Ask</b> · Market sell ស៊ី limit buy នៅ <b>Bid</b>
• <b>Order book / DOM</b> = បញ្ជី limit orders នៅតម្លៃនីមួយៗ
• តម្លៃឡើងពេល market buy <b>ច្រើនជាង</b> limit sell ដែលនៅសល់
• មាស CFD (Exness) <b>គ្មាន</b> order book ពិត · order flow ពិតមកពី <b>COMEX futures</b>""",
         quiz=("តម្លៃឡើងព្រោះ...", ["Limit buy ច្រើន", "Market buy ស៊ី limit sell អស់ ហើយត្រូវឡើងរក sellers បន្ទាប់", "Spread ធំ", "ម៉ោង"], 1,
               "Aggressive buyers (market buy) ស៊ី orders លក់អស់នៅតម្លៃមួយ → តម្លៃឡើងទៅរកបន្ទាប់។"), chart=None),
    dict(ch=23, part="PART 5 · Order Flow", title="Footprint · Delta · Imbalance",
         body="""• <b>Footprint chart</b> = ទៀនដែលបង្ហាញ <b>Bid × Ask</b> volume នៅតម្លៃនីមួយៗ
• <b>Delta</b> = Ask volume − Bid volume · វិជ្ជមាន = buyers aggressive · អវិជ្ជមាន = sellers
• <b>Imbalance</b> = ម្ខាងច្រើនជាង 3× (diagonal) · <b>Stacked imbalances</b> 3+ ជាប់គ្នា = កម្លាំងខ្លាំង
• Stacked imbalance ច្រើនតែក្លាយជា <b>support/resistance</b>
• ត្រូវការ data futures (COMEX GC) និង platform ពិសេស (ATAS, Sierra, Quantower)""",
         quiz=("Delta វិជ្ជមានធំមានន័យថា...", ["Sellers aggressive", "Buyers aggressive (market buy ច្រើន)", "គ្មាន volume", "តម្លៃត្រូវចុះ"], 1,
               "Delta = Ask − Bid volume។ វិជ្ជមាន = market buy ច្រើនជាង។"), chart=None),
    dict(ch=24, part="PART 5 · Order Flow", title="Absorption · Exhaustion · CVD",
         body="""• <b>Absorption</b> = market sell ច្រើន ប៉ុន្តែតម្លៃ <b>មិនចុះ</b> → limit buyers ធំ "ស្រូប"
• <b>Exhaustion</b> = volume ថយចុះនៅចុង move → កម្លាំងអស់
• <b>Delta divergence</b> = តម្លៃធ្វើ high ថ្មី ប៉ុន្តែ delta ខ្សោយ → move អាចអស់
• <b>CVD</b> (Cumulative Volume Delta) = delta បូកបន្ត · មើលទិស aggression
• <b>Iceberg</b> = order ធំលាក់ (ឃើញតែផ្នែកតូច) · ពិបាករកឃើញពិតប្រាកដ
• <b>Pulling/Stacking</b> = limit orders ដកចេញ/ដាក់បន្ថែមក្នុង DOM (អាចបោក)""",
         quiz=("Market sell ច្រើនណាស់ ប៉ុន្តែតម្លៃមិនចុះ ហៅថា...", ["Exhaustion", "Absorption", "Breakout", "Spread"], 1,
               "Absorption = limit buyers ធំស្រូប market sell ទាំងអស់ ដូច្នេះតម្លៃមិនចុះ។"), chart=None),
    dict(ch=25, part="PART 5 · Order Flow", title="Order Flow & Gold: ការពិត",
         body="""• Order flow ពិតសម្រាប់មាស = <b>COMEX GC futures</b> មិនមែន XAUUSD CFD
• XAUUSD (Exness) ≈ GC ប៉ុន្តែតម្លៃខុសគ្នាបន្តិច (basis) · tick volume ≠ real volume
• <b>COT report</b> (រាល់សប្ដាហ៍) = មូលនិធិធំ long/short ប៉ុណ្ណា
• Data delay: feed ឥតគិតថ្លៃ ច្រើនតែយឺត · footprint ត្រូវការ data real-time បង់ប្រាក់
• កំហុសធំ: មើល tick volume ក្នុង MT5 ហើយហៅថា "order flow" ❌

💡 ក្រុមយើងប្រើ futures volume សម្រាប់ VP/VWAP និង COT ក្នុង Daily Outlook""",
         quiz=("Order flow ពិតសម្រាប់មាសមកពី...", ["MT5 tick volume", "COMEX gold futures (GC)", "Telegram", "RSI"], 1,
               "Futures មាន exchange កណ្ដាល និង volume ពិត។ CFD broker មិនមាន។"), chart=None),
    # ---------------- PART 6 — COMBINING
    dict(ch=26, part="PART 6 · Combining", title="Building a Market Bias · ទិសដៅថ្ងៃ",
         body="""<b>ជំហាន bias រាល់ថ្ងៃ:</b>
1️⃣ <b>HTF</b>: Weekly/Daily ទិសអ្វី? (structure)
2️⃣ <b>Liquidity</b>: BSL/SSL ណាជិតជាង? តម្លៃ​ទើបតែ sweep ម្ខាងណា?
3️⃣ <b>Premium/Discount</b>: តម្លៃនៅថ្លៃ ឬថោក ក្នុង dealing range?
4️⃣ <b>Volume Profile</b>: នៅលើ/ក្រោម value? POC នៅណា?
5️⃣ <b>Macro</b>: DXY / yields / ព័ត៌មានថ្ងៃនេះ
→ <b>Bullish</b>, <b>Bearish</b> ឬ <b>Neutral</b> (រង់ចាំ)

💡 Bias មិនមែនជា entry · វាប្រាប់ថា <b>ទិសណា</b>ដែលត្រូវរក setup""",
         quiz=("Bias ប្រាប់អ្នក...", ["ចំណុចចូលច្បាស់", "ទិសណាដែលត្រូវរក setup", "ចំណេញប៉ុន្មាន", "Lot ប៉ុន្មាន"], 1,
               "Bias = ទិសដែលពេញចិត្ត។ Entry ត្រូវការ setup និង confirmation។"), chart="structure"),
    dict(ch=27, part="PART 6 · Combining", title="Confluence ដោយមិនរាប់ពីរដង",
         body="""• <b>Confluence</b> = ភស្តុតាងពីប្រភព <b>ផ្សេងគ្នា</b> ចង្អុលទិសដូចគ្នា
• ល្អ: ICT (liquidity) + Structure + VP + Macro = 4 ប្រភពផ្សេង
• <b>Double-counting</b> ❌: EMA 20 + EMA 50 + MACD + RSI = ប្រភពតែមួយ (momentum) រាប់ 4 ដង
• FVG + OB នៅកន្លែងដូចគ្នា ច្រើនតែជា <b>ចលនាតែមួយ</b> មិនមែន 2 ហេតុផល
• Confluence ច្រើន <b>មិនធានា</b> ឈ្នះ · យើងបានឃើញ: VWAP+EMA+1H ស្របគ្នាលើ 97% នៃសញ្ញា 🖕 រួចហើយ (មិនបន្ថែម edge)

💡 ច្បាប់: 2–3 ហេតុផល <b>ឯករាជ្យ</b> + risk ច្បាស់ = គ្រប់គ្រាន់""",
         quiz=("មួយណាជា double-counting?", ["Liquidity + Volume Profile", "EMA 20 + EMA 50 + RSI ទាំងអស់ momentum", "Structure + Macro", "HTF + session"], 1,
               "Indicator momentum ច្រើនវាស់រឿងតែមួយ។ វាមិនមែនជា confluence ពិតទេ។"), chart=None),
    dict(ch=28, part="PART 6 · Combining", title="Gold Setups + លទ្ធផលសាកល្បងពិត",
         body="""យើងបានសាកល្បង setup ល្បីៗលើមាស 2 ឆ្នាំ (រួមថ្លៃ spread):
• ✅ <b>4H breakout + Day Meter ≥70%</b> (🖕 COMBO): ឈ្នះ ~68%
• ✅ <b>ដូចគ្នា ≥100%</b> (🖕🖕 PREMIUM): ឈ្នះ ~70%
• 🤬 <b>15m FVG pullback ក្រោយ COMBO</b> (SL ~$7): ឈ្នះ 50% ត្រង់ 2R
• 🤬 <b>POC រាង P/b</b>: ~49% · +0.14R (មិនទាន់ proven)
• ❌ Liquidity sweep reversal តែឯង · OB limit + SL តូច · VWAP fade · News spike · momentum candle
• ❌ ច្រើនរបស់អ្នកដទៃ ល្អលើ screenshot តែខាតពេលសាកល្បង

💡 មេរៀន: setup ល្អ = <b>បានសាកល្បង</b> មិនមែន "មើលទៅស្អាត" · Chapter 35 បង្រៀនសាកល្បងខ្លួនឯង""",
         quiz=("Setup ដែលល្អពិតគឺ...", ["មើលទៅស្អាតលើ screenshot", "បានសាកល្បងលើទិន្នន័យច្រើន រួមថ្លៃ", "មាន indicator ច្រើន", "គ្រូនិយាយថាល្អ"], 1,
               "មានតែការសាកល្បង (backtest + forward test) ទើបបង្ហាញថា setup មាន edge ពិត។"), chart=None),
]

LESSONS += [
    # ---------------- PART 7 — EXECUTION
    dict(ch=29, part="PART 7 · Execution", title="Entry Techniques · វិធីចូល",
         body="""• <b>Market entry</b> = ចូលភ្លាម (សញ្ញា 🖕 របស់យើង: ចូលក្នុង 15 នាទី)
• <b>Limit entry</b> = ដាក់ order រង់ចាំតម្លៃត្រឡប់មក (ប្រហែលមិនបាន fill)
• <b>Stop entry</b> = ចូលពេលតម្លៃឆ្លង level (breakout)
• <b>Confirmation entry</b> = រង់ចាំទៀនបិទ / CHOCH 5m មុនចូល (យឺតតែសុវត្ថិភាពជាង)
• <b>Avoid late entries</b>: បើតម្លៃរត់ទៅជិត TP1 រួចហើយ → <b>រំលង</b> កុំដេញ
• Timing: ជៀសវាង 15 នាទីមុន/ក្រោយព័ត៌មានធំ និងម៉ោងបិទទីផ្សារ

💡 យើងបានសាកល្បង: រង់ចាំ retest ក្រោយ breakout <b>អាក្រក់ជាង</b> ចូលភ្លាម (breakout ខ្លាំងមិនត្រឡប់មកវិញ)""",
         quiz=("សញ្ញាចេញ ប៉ុន្តែតម្លៃរត់ជិត TP1 រួចហើយ។ គួរ...", ["ដេញចូលភ្លាម", "រំលង រង់ចាំសញ្ញាបន្ទាប់", "ចូល lot ធំ", "ផ្លាស់ SL"], 1,
               "ចូលយឺត = RR អាក្រក់។ រំលងល្អជាងដេញ។"), chart=None),
    dict(ch=30, part="PART 7 · Execution", title="Stop Loss & Take Profit",
         body="""• <b>Structural SL</b> = ក្រោយ swing/OB ដែលការពារ idea · <b>Volatility SL</b> = តាម ATR
• SL ត្រូវនៅកន្លែងដែល <b>idea ខុស</b> មិនមែនកន្លែងដែល "ខាតតិច"
• <b>RR</b> (Risk:Reward) = TP ÷ SL · ឧ. SL $22, TP $66 = 1:3
• <b>Partial profit</b>: បិទពាក់កណ្ដាលនៅ TP1 · <b>Break-even</b>: ប្ដូរ SL មកចំណុចចូល
• <b>Trailing stop</b> = SL ដើរតាមតម្លៃ
• ❌ <b>កុំ</b> ផ្លាស់ SL ឆ្ងាយទៀតពេលតម្លៃមករក

💡 សញ្ញា 🖕: SL 0.55% (~$22) · TP1 1R បិទពាក់កណ្ដាល + BE · TP2 3R · SL តូចជាងនេះ <b>ខាត</b>ពេលសាកល្បង""",
         quiz=("ពេលតម្លៃជិតដល់ SL អ្នកគួរ...", ["ផ្លាស់ SL ឆ្ងាយទៀត", "ទុកឱ្យ SL ធ្វើការងារ", "បន្ថែម lot", "លុប SL"], 1,
               "SL គឺជាចំណុចដែល idea ខុស។ ផ្លាស់ឆ្ងាយ = ខាតធំ។"), chart=None),
    dict(ch=31, part="PART 7 · Execution", title="Sessions & News · ព័ត៌មានធំ",
         body="""• <b>CPI</b> (អតិផរណា) · <b>NFP</b> (ការងារ, ថ្ងៃសុក្រទី 1) · <b>FOMC</b> (ការប្រាក់) = ព័ត៌មានធំបំផុត
• ម៉ោងកម្ពុជា: US data ភាគច្រើន <b>20:30</b> (winter) · FOMC <b>02:00</b> យប់
• ពេលព័ត៌មាន: spread <b>ធំ</b> · តម្លៃលោត $10–30 · SL អាច <b>slip</b> (ចេញអាក្រក់ជាង)
• ច្បាប់: <b>កុំបើកថ្មី 15 នាទីមុន/ក្រោយ</b>
• Plan ថ្ងៃ: ពិនិត្យ calendar ព្រឹក (Daily Outlook) → ដឹងម៉ោងគ្រោះថ្នាក់

💡 យើងសាកល្បង "trade ក្រោយព័ត៌មាន" 98 ដង: ឈ្នះតែ 19% · ដូច្នេះ bot មិនផ្ញើសញ្ញាពេលព័ត៌មាន""",
         quiz=("CPI ចេញម៉ោង 20:30។ ពេលណាមិនគួរបើក trade ថ្មី?", ["20:15–20:45", "08:00", "12:00", "គ្មាន"], 0,
               "15 នាទីមុន និងក្រោយព័ត៌មានធំ spread ធំ និងតម្លៃលោត។"), chart=None),
    # ---------------- PART 8 — RISK
    dict(ch=32, part="PART 8 · Risk", title="Capital Protection · គណនា Lot",
         body="""<b>រូបមន្ត:</b> Lot = (Account × Risk%) ÷ (SL $ × 100)
ឧ. Account $1,000 · Risk 1% = $10 · SL $22 → 10 ÷ 2,200 = <b>0.0045 lot</b>
→ 0.01 lot = $22 risk = 2.2% · Account តូចពេកសម្រាប់ 1%
• Account <b>តូច</b> ($100–500): ប្រើ <b>Cent account</b> ឬ risk ច្រើនជាងគោល = គ្រោះថ្នាក់
• <b>Max daily loss</b> 2–3% · <b>Max weekly</b> 5–6% → ឈប់
• <b>Drawdown</b> = ធ្លាក់ពីកំពូលគណនី · 10 ខាតជាប់ × 10% risk = គណនីបាត់ ❌

💡 ប្រើ <b>Scale Up</b> លើ website ដើម្បីគណនា lot ដោយស្វ័យប្រវត្តិ""",
         quiz=("Account $2,000 risk 1% SL $20។ Lot ប្រហែល...", ["0.01", "0.10", "1.00", "0.50"], 0,
               "$2,000 × 1% = $20 ÷ ($20 × 100) = 0.01 lot។"), chart=None),
    dict(ch=33, part="PART 8 · Risk", title="Risk Discipline · ខាតជាប់គ្នា",
         body="""• ឈ្នះ 68% ក៏នៅតែមាន <b>ខាត 3–4 ដងជាប់គ្នា</b> ពីរបីដងក្នុងមួយឆ្នាំ: <b>ធម្មតា</b>
• <b>Overtrading</b> = trade ពេលគ្មាន setup · <b>Revenge trading</b> = trade ដើម្បីយកលុយវិញ ❌
• <b>Overleverage</b> = lot ធំពេក → ខាតម្ដងបាត់ច្រើន
• <b>Correlated risk</b> = បើក 3 order មាសទិសដូចគ្នា = risk 3 ដង
• ក្រោយខាត 2 ដងជាប់: <b>ឈប់ថ្ងៃនោះ</b> · ពិនិត្យ journal
• Capital preservation មុន profit: គណនីនៅរស់ = មានឱកាស

💡 ទំព័រ Scale Up: ក្រោយខាត risk ធ្លាក់ពាក់កណ្ដាលដោយស្វ័យប្រវត្តិ""",
         quiz=("ខាត 2 ដងជាប់ ហើយខឹង។ អ្វីល្អ?", ["បើក lot ធំដើម្បីយកវិញ", "ឈប់សម្រាប់ថ្ងៃនោះ ពិនិត្យ journal", "Trade រាល់ setup", "លុប SL"], 1,
               "Revenge trading ជាមូលហេតុធំនៃការបាត់គណនី។ ឈប់ ហើយពិនិត្យ។"), chart=None),
]

LESSONS += [
    # ---------------- PART 9 — STRATEGY & TESTING
    dict(ch=34, part="PART 9 · Strategy", title="Building a Strategy · សរសេរច្បាប់",
         body="""Strategy ល្អ = <b>ច្បាប់ច្បាស់</b> ដែលមនុស្ស 2 នាក់អនុវត្តបានដូចគ្នា
• <b>Entry</b>: លក្ខខណ្ឌអ្វីខ្លះ? (ឧ. 4H បិទលើ high 30 ទៀន + Day Meter ≥70%)
• <b>Exit</b>: SL ណា? TP ណា? បិទពេលណា? (ឧ. 12 ម៉ោង)
• <b>Filter</b>: ពេលណាមិន trade? (ព័ត៌មាន, ថ្ងៃស្ងាត់, ចុងសប្ដាហ៍)
• <b>Invalidation</b>: អ្វីធ្វើឱ្យ idea ខុស?
• <b>No-trade conditions</b>: សរសេរពួកវាផងដែរ!
• <b>Trading plan</b> = strategy + risk + ម៉ោង + journal

❌ "ទិញពេលមើលទៅល្អ" មិនមែនជាច្បាប់ទេ""",
         quiz=("មួយណាជាច្បាប់ strategy ល្អ?", ["ទិញពេលមើលទៅឡើង", "ទិញពេល 4H បិទលើ high 30 ទៀន និង Day Meter ≥70%", "ទិញពេលគ្រូនិយាយ", "ទិញពេលបាត់បង់"], 1,
               "ច្បាប់ល្អវាស់បាន និងអនុវត្តដូចគ្នាគ្រប់ពេល។"), chart=None),
    dict(ch=35, part="PART 9 · Strategy", title="Backtesting · សាកល្បងលើអតីតកាល",
         body="""• <b>Backtest</b> = អនុវត្តច្បាប់លើទិន្នន័យចាស់ គ្រប់ trade (មិនជ្រើសតែល្អ)
• <b>Sample size</b>: យ៉ាងតិច 30, ល្អ 100+ trade
• <b>Win rate</b> · <b>Average R</b> · <b>Expectancy</b> = ចំណេញមធ្យមក្នុងមួយ trade (R)
• <b>Profit factor</b> = ចំណេញសរុប ÷ ខាតសរុប (&gt;1.3 ល្អ) · <b>Max drawdown</b>
• <b>Look-ahead bias</b> ❌ = ប្រើទិន្នន័យដែលមិនទាន់ដឹងនៅពេលនោះ
• ដាក់ <b>spread + commission + slippage</b> ជានិច្ច
• ចែក <b>70% ចាស់ / 30% ថ្មី</b>: ជ្រើសច្បាប់លើចាស់ សាកលើថ្មី

💡 យើងធ្វើបែបនេះគ្រប់សញ្ញា · លទ្ធផលពេញនៅក្នុង studies/RESULTS.md""",
         quiz=("Look-ahead bias គឺ...", ["Trade ច្រើនពេក", "ប្រើទិន្នន័យអនាគតដែលមិនទាន់ដឹងនៅពេលនោះ", "Spread", "ខាតជាប់"], 1,
               "Backtest ត្រឹមត្រូវប្រើតែព័ត៌មានដែលមាននៅពេលសម្រេចចិត្ត។"), chart=None),
    dict(ch=36, part="PART 9 · Strategy", title="Forward Testing · Demo",
         body="""• <b>Forward test</b> = អនុវត្តច្បាប់លើទីផ្សារពិត (demo ឬ lot តូច) ក្រោយ backtest
• កត់ត្រា: entry ពិត vs រំពឹង · slippage · spread · អារម្មណ៍
• ប្រៀបធៀប: live win rate ជិត backtest ទេ? (ត្រូវការ 30+ trade មុនសន្និដ្ឋាន)
• <b>Consistency</b> = លទ្ធផលស្រដៀងគ្នារាល់ខែ
• <b>កុំកែច្បាប់</b> ក្រោយខាត 2–3 ដង · កែតែពេលមានភស្តុតាងច្រើន

💡 🏆 Proof របស់យើង = forward test ជាសាធារណៈ (ឈ្នះ និងខាតទាំងអស់)""",
         quiz=("ក្រោយខាត 3 ដងជាប់ក្នុង forward test គួរ...", ["ប្ដូរច្បាប់ភ្លាម", "បន្តតាមច្បាប់ ពិនិត្យក្រោយ 30+ trade", "ឈប់ trade ជារៀងរហូត", "បង្កើន lot"], 1,
               "3 trade ជា sample តូចពេក។ ខាត 3 ជាប់កើតឡើងធម្មតា ទោះ strategy ល្អក៏ដោយ។"), chart=None),
    dict(ch=37, part="PART 9 · Strategy", title="Trading Journal · កំណត់ហេតុ",
         body="""<b>កត់ត្រាគ្រប់ trade:</b> ថ្ងៃ · setup · entry/SL/TP · lot · លទ្ធផល (R) · រូប chart មុន/ក្រោយ · អារម្មណ៍
• <b>Trade grade</b>: A (តាមច្បាប់ទាំងអស់) · B · C (បំពានច្បាប់)
• <b>Weekly review</b>: setup ណាល្អ? កំហុសអ្វីដដែលៗ?
• <b>Monthly review</b>: win rate · avg R · drawdown · ប្រៀបធៀបខែមុន
• Trade ខាតតាមច្បាប់ = <b>ល្អ</b> · Trade ឈ្នះបំពានច្បាប់ = <b>អាក្រក់</b>

💡 ប្រើ <b>Journal</b> លើ website XAU.KH (ឥតគិតថ្លៃ)""",
         quiz=("Trade ឈ្នះ ប៉ុន្តែបំពានច្បាប់ (គ្មាន SL) គឺ...", ["Trade ល្អ", "Trade អាក្រក់ (grade C) ទោះឈ្នះ", "មិនសំខាន់", "ធ្វើម្ដងទៀត"], 1,
               "លទ្ធផលមួយដងជាសំណាង។ ការធ្វើតាមច្បាប់ទើបនាំចំណេញយូរ។"), chart=None),
    # ---------------- PART 10 — PROFESSIONAL
    dict(ch=38, part="PART 10 · Professional", title="Trading Psychology · ចិត្តសាស្ត្រ",
         body="""• <b>Fear</b> → មិនហ៊ានចូល / បិទលឿនពេក · <b>Greed</b> → lot ធំ / មិនយក TP
• <b>Patience</b>: ថ្ងៃខ្លះគ្មាន setup = ថ្ងៃល្អ (មិនខាត)
• <b>Discipline</b> = ធ្វើតាមច្បាប់ ទោះអារម្មណ៍និយាយផ្សេង
• <b>Confidence ≠ Overconfidence</b>: ក្រោយឈ្នះ 5 ដង កុំបង្កើន lot ភ្លាម
• <b>ទទួលយកការខាត</b>: ខាត 1R ជាថ្លៃធ្វើជំនួញ មិនមែនបរាជ័យ
• <b>Routine</b>: ព្រឹកអាន Outlook → កំណត់ bias → រង់ចាំសញ្ញា → journal

💡 <i>No setup = no risk. Waiting is a position too.</i>""",
         quiz=("ឈ្នះ 5 ដងជាប់ ហើយមានទំនុកចិត្តខ្លាំង។ គួរ...", ["បង្កើន lot 5 ដង", "បន្ត risk ដដែល តាមច្បាប់", "Trade គ្មាន SL", "Trade ច្រើនជាងមុន"], 1,
               "Overconfidence ក្រោយឈ្នះជាប់ ធ្វើឱ្យខាតធំ។ Risk ដដែលជានិច្ច។"), chart=None),
    dict(ch=39, part="PART 10 · Professional", title="Professional Analysis · Scenario",
         body="""• <b>Pre-market</b>: Outlook (macro + news) → HTF bias → key levels → liquidity
• <b>Scenario planning</b>: "<b>ប្រសិនបើ</b> បិទលើ X → ទិញ ទៅ Y · <b>ប្រសិនបើ</b> បិទក្រោម Z → លក់"
• មាន <b>2 scenario</b> ជានិច្ច · ទីផ្សារជ្រើស មិនមែនយើង
• <b>Regime</b>: Trend (ធ្វើតាម breakout) · Range (ទិញបាត លក់កំពូល) · Volatile (lot តូច ឬឈប់)
• <b>Post-market review</b>: scenario ណាកើតឡើង? ហេតុអ្វី?

👉 Analysis របស់យើង = TARGET BUY / TARGET SELL ពីរ scenario រាល់ session""",
         quiz=("អ្នកជំនាញរៀបចំ...", ["Scenario តែមួយដែលខ្លួនជឿ", "Scenario ពីរ (ប្រសិនបើ... នោះ...)", "គ្មានផែនការ", "ទាយទិស"], 1,
               "ពីរ scenario ធ្វើឱ្យអ្នកត្រៀមខ្លួនទោះទីផ្សារទៅទិសណាក៏ដោយ។"), chart="structure"),
    dict(ch=40, part="PART 10 · Professional", title="Gold Scalping · ការពិត",
         body="""• Scalping = trade M1–M5 · ចំណេញតូច ច្រើនដង
• <b>Spread/commission</b> ស៊ីចំណេញ: SL $5 + spread $0.30 = ថ្លៃ 6% នៃ risk រាល់ trade
• <b>Slippage</b> ពេលរត់លឿន · <b>Delay</b> សញ្ញា 10 នាទី = setup បាត់
• យើងសាកល្បង scalping SL តូចច្រើនរយវិធី: <b>ភាគច្រើនខាត</b> លើមាស
• Scalping ធ្វើការ <b>តែ</b>ក្នុង context ខ្លាំង: ឧ. 🤬 COMBO SCALP ក្រោយ 🖕 breakout (50% @ 2R)
• មិនសមស្រប: ពេលព័ត៌មាន · ម៉ោងស្ងាត់ · ពេលខឹង · account តូចពេក

💡 Scalp ត្រូវ <b>ចូលភ្លាម ឬរំលង</b>""",
         quiz=("ហេតុអ្វី scalping SL តូចពិបាកចំណេញលើមាស?", ["មាសមិនរត់", "Spread/noise ធម្មតាប៉ះ SL តូចញឹកញាប់", "គ្មាន broker", "ច្បាប់ហាម"], 1,
               "Noise ធម្មតារបស់មាស និងថ្លៃ spread ធ្វើឱ្យ SL តូចត្រូវប៉ះញឹកញាប់។"), chart=None),
    dict(ch=41, part="PART 10 · Professional", title="Your Trading System · Playbook",
         body="""<b>Playbook</b> = សៀវភៅច្បាប់ផ្ទាល់ខ្លួន:
1. Setup 1–3 ដែលបាន <b>សាកល្បង</b> (មិនច្រើនពេក)
2. Risk framework: % ក្នុង trade · max ថ្ងៃ/សប្ដាហ៍
3. ម៉ោង trade និងម៉ោងមិន trade
4. Benchmark: win rate/avg R ដែលរំពឹង (ពី backtest)
5. Checklist មុនចូល
6. Review ប្រចាំសប្ដាហ៍ → កែលម្អបន្តិចម្ដងៗ
• Data/technology: chart ល្អ · VPS (EA) · internet

💡 ប្រព័ន្ធ XAU.KH = 🖕 COMBO · 🖕🖕 PREMIUM · 🤬 Scalp · risk 0.5–1% · Proof សាធារណៈ""",
         quiz=("Playbook ល្អគួរមាន setup ប៉ុន្មាន?", ["50+", "1–3 ដែលបានសាកល្បង", "គ្មាន", "រាល់ indicator"], 1,
               "Setup តិចដែលបានសាកល្បង ងាយធ្វើតាម និងវាស់បាន។"), chart=None),
    # ---------------- PART 11 — EXAMS
    dict(ch=42, part="PART 11 · Exams", title="Exam 1: Chart Reading",
         body="""<b>លំហាត់:</b> មើលរូប chart ថ្ងៃនេះខាងក្រោម ហើយឆ្លើយក្នុងចិត្ត (ឬ comment ក្នុង 💬 General):
1. Structure 15m: ឡើង ចុះ ឬ range? CHOCH/BOS ចុងក្រោយនៅណា?
2. BSL / SSL (ELQ) នៅណា? មាន $$ sweep ទេ?
3. FVG និង OB ណាដែលនៅមិនទាន់បំពេញ?
4. POC នៅណា? តម្លៃនៅលើ ឬក្រោម?
5. Premium ឬ Discount?
6. Top-down D → 5m ស្របគ្នាទេ?

✅ ផ្ទៀងផ្ទាត់ចម្លើយ: វាយ <b>/check</b>""",
         quiz=("ពេលតម្លៃនៅលើ EQ 50% នៃ dealing range វាស្ថិតក្នុង...", ["Discount", "Premium", "POC", "FVG"], 1,
               "លើ EQ = premium (ថ្លៃ)។ ក្រោម EQ = discount (ថោក)។"), chart="liquidity"),
    dict(ch=43, part="PART 11 · Exams", title="Exam 2: Trade Planning",
         body="""<b>លំហាត់ (account $1,000 · risk 1%):</b>
1. សរសេរ scenario <b>BUY</b> និង <b>SELL</b> ពី chart ថ្ងៃនេះ (ប្រើ TARGET BUY/SELL)
2. Entry condition: ទៀនអ្វីបិទឆ្លងអ្វី?
3. SL នៅណា (structure)? ចម្ងាយ $ ប៉ុន្មាន?
4. Lot = $10 ÷ (SL $ × 100) = ?
5. TP1 / TP2 · RR ប៉ុន្មាន?
6. Invalidation: អ្វីធ្វើឱ្យ idea ខុស?

💡 ប្រៀបធៀបជាមួយ session analysis ក្នុង 📊 Analysis""",
         quiz=("Account $1,000 risk 1% SL $10។ Lot ត្រឹមត្រូវ?", ["0.01", "0.10", "1.00", "0.05"], 0,
               "$1,000 × 1% = $10 ÷ ($10 × 100) = 0.01 lot។"), chart=None),
    dict(ch=44, part="PART 11 · Exams", title="Exam 3: Backtest Project",
         body="""<b>Project:</b>
1. ជ្រើស strategy មួយដែលមានច្បាប់ច្បាស់ (ពី Chapter 34)
2. ប្រើ TradingView <b>Replay</b> លើមាស 3–6 ខែចុងក្រោយ
3. កត់គ្រប់ trade ដែលត្រូវលក្ខខណ្ឌ (ទាំងល្អ ទាំងអាក្រក់) ក្នុង Journal
4. គណនា: ចំនួន trade · win rate · avg R · max drawdown · ខាតជាប់វែងបំផុត
5. សរសេរ: ចំណុចខ្សោយអ្វី? ពេលណាវាមិនដំណើរការ?

💡 ច្បាប់មាស: 30+ trade មុនសន្និដ្ឋាន · ដាក់ spread ផង""",
         quiz=("Backtest ត្រឹមត្រូវកត់ត្រា...", ["តែ trade ឈ្នះ", "គ្រប់ trade ដែលត្រូវលក្ខខណ្ឌ ទាំងឈ្នះ និងខាត", "តែ trade ធំៗ", "គ្មាន"], 1,
               "ជ្រើសតែ trade ល្អ = cherry-picking។ លទ្ធផលនឹងបោកខ្លួនឯង។"), chart=None),
    dict(ch=45, part="PART 11 · Exams", title="Final Capstone 🎓",
         body="""<b>ការប្រឡងចុងក្រោយ:</b>
1. ✍️ Market analysis ពេញលេញ (top-down + liquidity + VP + macro)
2. 📋 Trading plan: setup · risk · ម៉ោង · no-trade rules
3. 🧮 Risk calculation សម្រាប់ account របស់អ្នក
4. 🧪 Demo 30 trade តាមច្បាប់
5. 📓 Journal ពេញលេញ + review
6. 📈 Performance: win rate · avg R · drawdown · អ្វីត្រូវកែ

🎓 អបអរ! អ្នកបានបញ្ចប់ <b>XAU.KH Academy</b> 45 ជំពូក
💬 Share លទ្ធផល demo របស់អ្នកក្នុង General · សញ្ញា និង analysis បន្តរាល់ថ្ងៃ""",
         quiz=("មុនប្រើលុយពិតច្រើន អ្នកគួរ...", ["ប្រើ lot ធំភ្លាម", "Demo/lot តូច 30+ trade តាមច្បាប់ និង journal", "រង់ចាំសំណាង", "ចម្លងអ្នកដទៃ"], 1,
               "Forward test តាមច្បាប់ និង journal បង្ហាញថាអ្នកអនុវត្តបានពិត មុន risk លុយច្រើន។"), chart=None),
]
