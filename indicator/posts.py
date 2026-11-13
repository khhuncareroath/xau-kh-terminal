"""The 7 posts for the 📈 Indicator · ឧបករណ៍ topic (from the owner's doc, 13 Nov 2026). Telegram HTML.
{LINK} = the TradingView script link (indicator/link.txt); until it exists Post 2 says "coming soon"."""

SEP = "\n\n———\n\n"
NO_LINK_KM = "មកដល់ឆាប់ៗ (ប្រើវិធី B សិន)"
NO_LINK_EN = "coming soon (use Option B for now)"

POSTS = [
    # 1 · welcome (pinned)
    "📈 <b>XAU.KH FLOW — Indicator ឥតគិតថ្លៃ សម្រាប់មាស (XAUUSD)</b>\n\n"
    "Indicator នេះបង្ហាញអ្វីដែល orderflow កំពុងធ្វើឥឡូវនេះ៖\n"
    "• <b>នរណាឈ្នះ</b> — អ្នកទិញ ឬអ្នកលក់ (30m · 1H · 4H)\n"
    "• <b>Level សំខាន់ៗ</b> — POC, VAH, VAL, PDH/PDL, DEMAND/SUPPLY\n"
    "• <b>សញ្ញាព្រមាន</b> — Sellers tired, Buyers absorbed, VAL reject …\n"
    "• <b>ផែនការ Trade</b> — Sweep → FLIP ◆◆◆ ជាមួយ Entry, SL, TP\n\n"
    "✅ ឥតគិតថ្លៃ · ប្រើ TradingView Free បាន · Chart 5 នាទី XAUUSD (OANDA)\n"
    "📖 មើល Post 2 ដើម្បីដំឡើង · Post 3 ដើម្បីអាន chart"
    + SEP +
    "📈 <b>XAU.KH FLOW — a free gold (XAUUSD) indicator</b>\n\n"
    "It shows what order flow is doing right now:\n"
    "• <b>Who is winning</b> — buyers or sellers (30m · 1H · 4H)\n"
    "• <b>Key levels</b> — POC, VAH, VAL, PDH/PDL, DEMAND/SUPPLY\n"
    "• <b>Warning signs</b> — Sellers tired, Buyers absorbed, VAL reject …\n"
    "• <b>A trade plan</b> — Sweep → FLIP ◆◆◆ with entry, SL and TP\n\n"
    "✅ Free · works on the free TradingView plan · XAUUSD (OANDA) 5-minute chart\n"
    "📖 Post 2 = install · Post 3 = how to read it",

    # 2 · install
    "🛠 <b>របៀបដំឡើង XAU.KH FLOW</b>\n\n"
    "<b>វិធី A — ងាយបំផុត (តាម link)</b>\n"
    "1. ចុច link៖ {LINK_KM}\n"
    "2. ចូល TradingView (គណនី Free បាន)\n"
    "3. ចុច ⭐ <b>Add to favorites</b> ឬ <b>Add to chart</b>\n"
    "4. បើក chart <b>XAUUSD · OANDA · 5m</b> → Indicators → Favorites → XAU.KH FLOW\n\n"
    "<b>វិធី B — បិទភ្ជាប់កូដ (ត្រូវការកុំព្យូទ័រ)</b>\n"
    "1. ទាញយក file XAU_KH_FLOW_public.pine ពី topic នេះ ហើយបើកជាមួយ Notepad\n"
    "2. TradingView → រូប 🌲 <b>Pine</b> ខាងស្តាំ → ឈ្មោះ script → <b>Create new → Indicator</b>\n"
    "3. លុបកូដគំរូ (Ctrl+A, Delete) → បិទភ្ជាប់ (Ctrl+V)\n"
    "4. ចុច ☁️ <b>Save</b> → ចុច ▷ <b>Add to chart</b>\n\n"
    "📱 នៅលើទូរស័ព្ទ៖ បន្ទាប់ពីដំឡើងម្តង វានៅក្នុង Indicators → Favorites (ឬ My scripts) ដោយស្វ័យប្រវត្តិ។"
    + SEP +
    "🛠 <b>How to install XAU.KH FLOW</b>\n\n"
    "<b>Option A — easiest (link)</b>\n"
    "1. Open: {LINK_EN}\n"
    "2. Log in to TradingView (a free account works)\n"
    "3. Tap ⭐ <b>Add to favorites</b> or <b>Add to chart</b>\n"
    "4. Open <b>XAUUSD · OANDA · 5m</b> → Indicators → Favorites → XAU.KH FLOW\n\n"
    "<b>Option B — paste the code (needs a computer)</b>\n"
    "1. Download XAU_KH_FLOW_public.pine from this topic and open it in Notepad\n"
    "2. TradingView → 🌲 <b>Pine</b> icon on the right → script name → <b>Create new → Indicator</b>\n"
    "3. Delete the sample code (Ctrl+A, Delete) → paste (Ctrl+V)\n"
    "4. ☁️ <b>Save</b> → ▷ <b>Add to chart</b>\n\n"
    "📱 On your phone: once added, it shows under Indicators → Favorites (or My scripts).",

    # 3 · read the chart
    "👀 <b>របៀបអាន XAU.KH FLOW</b>\n\n"
    "<b>Panel (ខាងលើ)</b>\n"
    "• 🟩 \"Buyers in control\" / 🟥 \"Sellers in control\" = ភាគម្ខាងកំពុងឈ្នះ (៣០ នាទីចុងក្រោយ)\n"
    "• 🟧 \"Buyers/Sellers blocked\" = បុកខ្លាំង តែតម្លៃមិនទៅ → ប្រយ័ត្ន\n"
    "• ⬜ \"Two-way · no edge\" = គ្មាននរណាឈ្នះ → រង់ចាំ\n"
    "• 30m · 1H · 4H ▲▼ = ទិសធំៗ។ \"aligned ✓\" = ទាំងអស់យល់ស្រប (ខ្លាំងបំផុត)\n"
    "• \"USD ▲ gold ▼\" = ប្រាក់ដុល្លាប្រឆាំងមាស\n\n"
    "<b>ស្លាកលើ chart</b>\n"
    "• Sellers tired / Buyers tired = ភាគម្ខាងអស់កម្លាំង\n"
    "• Sellers absorbed / Buyers absorbed = មានអ្នកធំទប់ស្ទាត់\n"
    "• VAL reject ▼ / VAH reject ▲ = តេស្តគែម value ហើយត្រូវបានច្រាន\n"
    "• ទៀនមាស + \"ឆុយ\" = ទៀនខ្លាំងខ្លាំង · រង្វង់ = កម្លាំងធំ\n"
    "• Sweep → FLIP ◆◆◆ = ការដំឡើង trade (◆ ច្រើន = orderflow យល់ស្របច្រើន)\n\n"
    "<b>Pane ខាងក្រោម</b>៖ ខ្សែលើ ០ = អ្នកទិញនាំមុខ។ \"healthy\" = ល្អ។ ⚠ ពណ៌លឿង = តម្លៃនិង flow មិនយល់ស្របគ្នា។\n\n"
    "💡 ចុច/ចាប់ស្លាក ឬ Panel ដើម្បីមើលការពន្យល់ពេញលេញ។"
    + SEP +
    "👀 <b>How to read XAU.KH FLOW</b>\n\n"
    "<b>Panel (top)</b>\n"
    "• 🟩 \"Buyers in control\" / 🟥 \"Sellers in control\" = who is winning the last 30 minutes\n"
    "• 🟧 \"Buyers/Sellers blocked\" = pushing hard but price isn't moving → careful\n"
    "• ⬜ \"Two-way · no edge\" = nobody winning → wait\n"
    "• 30m · 1H · 4H ▲▼ = the bigger direction. \"aligned ✓\" = all agree (strongest)\n"
    "• \"USD ▲ gold ▼\" = the dollar is working against gold\n\n"
    "<b>Labels on the chart</b>\n"
    "• Sellers tired / Buyers tired = that side is running out of fuel\n"
    "• Sellers absorbed / Buyers absorbed = someone big is blocking them\n"
    "• VAL reject ▼ / VAH reject ▲ = tested the value edge and got rejected\n"
    "• Gold candle + \"ឆុយ\" = a surge candle · rings = big effort\n"
    "• Sweep → FLIP ◆◆◆ = a trade setup (more ◆ = more order-flow agreement)\n\n"
    "<b>Bottom pane</b>: line above 0 = buyers ahead. \"healthy\" = good. Amber ⚠ = price and flow disagree.\n\n"
    "💡 Tap/hover any label or the panel for the full explanation.",

    # 4 · combo with the bot (+ honest note: the traffic light is being tested)
    "🤝 <b>ប្រើសញ្ញា Bot + Indicator រួមគ្នា</b>\n\n"
    "Bot = គំនិត trade · Indicator = ការពិនិត្យ\n"
    "• 🟢 <b>បៃតង</b>៖ 30m/1H/4H យល់ស្របនឹងសញ្ញា + Entry នៅ level → ចូលហានិភ័យធម្មតា\n"
    "• 🟡 <b>លឿង</b>៖ \"mixed\" ឬ Entry នៅកណ្តាលទទេ → ហានិភ័យពាក់កណ្តាល ឬរង់ចាំ\n"
    "• 🔴 <b>ក្រហម</b>៖ ភាគម្ខាងទៀត \"in control\" + aligned ប្រឆាំង → រំលង\n\n"
    "នៅ Entry (SELL)៖ រក \"Buyers tired/absorbed\" ឬ \"reject ▼\"។ បើ \"Buyers in control\" រុញកាត់ Entry → កុំទប់។\n\n"
    "គ្រប់គ្រង៖ TP1 → បិទពាក់កណ្តាល + SL មក Entry។ ពាក់កណ្តាលទីពីរ៖ ទុកដរាបណាភាគម្ខាងរបស់អ្នកនៅ \"in control\"។\n\n"
    "⚠️ ពេល 30m/1H/4H aligned ស្លាក \"tired\" ប្រឆាំងនិន្នាការច្រើនតែជា bounce តូច — យក profit មិនមែនត្រឡប់ទិសទេ។\n\n"
    "🧪 ច្បាប់ភ្លើង 🟢🟡🔴 នេះជាការណែនាំ មិនទាន់សាកល្បងទេ — យើងកំពុងតាមដានវា ៤ សប្តាហ៍។\n"
    "📖 សៀវភៅណែនាំ PDF (ខ្មែរ)៖ file នៅក្នុង topic នេះ"
    + SEP +
    "🤝 <b>Combining bot signals + the indicator</b>\n\n"
    "Bot = the trade idea · Indicator = the check\n"
    "• 🟢 <b>Green</b>: 30m/1H/4H agree with the signal + entry at a level → normal risk\n"
    "• 🟡 <b>Yellow</b>: \"mixed\" or entry in the middle of nowhere → half risk or wait\n"
    "• 🔴 <b>Red</b>: the other side \"in control\" + aligned against the signal → skip\n\n"
    "At the entry (SELL): look for \"Buyers tired/absorbed\" or \"reject ▼\". If \"Buyers in control\" push through the entry → don't fight it.\n\n"
    "Manage: TP1 → close half + SL to entry. Second half: hold while your side stays \"in control\".\n\n"
    "⚠️ When 30m/1H/4H are aligned, a counter-trend \"tired\" label is usually just a small bounce — take profit, don't reverse.\n\n"
    "🧪 The 🟢🟡🔴 rule is a guide, not tested yet — we are tracking it live for 4 weeks.\n"
    "📖 Full guide PDF (Khmer): the file in this topic",

    # 5 · alerts + phone
    "🔔 <b>ដំឡើង Alert ម្តង ទទួលបានគ្រប់សញ្ញា</b>\n"
    "1. ចុច ⏰ Alert\n"
    "2. Condition៖ <b>XAU.KH FLOW</b> → <b>Any alert() function call</b>\n"
    "3. Trigger៖ <b>Once per bar close</b> → Create\n\n"
    "ឧទាហរណ៍សារ៖ \"XAU.KH · Sellers absorbed at 3926.50 · now: Sellers blocked\"\n\n"
    "📱 <b>នៅលើទូរស័ព្ទ</b>\n"
    "• Settings → Style → Panel location → <b>Flow pane</b> (Panel មិនគ្របឈ្មោះ symbol)\n"
    "• ទាញ pane ខាងក្រោមឡើងបន្តិច (15–20% នៃអេក្រង់)\n"
    "• លុប indicator \"Volume\" របស់ TradingView ឲ្យ chart ស្អាត\n"
    "• ចង់ chart ស្អាតជាងនេះ៖ Style → Look → <b>Clean</b>"
    + SEP +
    "🔔 <b>Set one alert, get every signal</b>\n"
    "1. Tap ⏰ Alert\n"
    "2. Condition: <b>XAU.KH FLOW</b> → <b>Any alert() function call</b>\n"
    "3. Trigger: <b>Once per bar close</b> → Create\n\n"
    "Example message: \"XAU.KH · Sellers absorbed at 3926.50 · now: Sellers blocked\"\n\n"
    "📱 <b>On your phone</b>\n"
    "• Settings → Style → Panel location → <b>Flow pane</b> (so it doesn't cover the symbol name)\n"
    "• Drag the bottom pane up a little (15–20% of the screen)\n"
    "• Remove TradingView's \"Volume\" indicator for a cleaner chart\n"
    "• Want it even cleaner: Style → Look → <b>Clean</b>",

    # 6 · FAQ
    "❓ <b>សំណួរញឹកញាប់</b>\n"
    "• <b>តើត្រូវបង់លុយទេ?</b> ទេ។ ឥតគិតថ្លៃ ហើយដំណើរការលើ TradingView Free។\n"
    "• <b>Timeframe ណា?</b> 5 នាទី XAUUSD (OANDA)។ ទិសធំៗបង្ហាញក្នុង Panel រួចហើយ (30m/1H/4H)។\n"
    "• <b>តើ orderflow នេះពិតទេ?</b> វាជាការប៉ាន់ស្មានពី tick volume (OANDA + broker ២ ផ្សេងទៀត) មិនមែន bid/ask ពិតទេ។ Profile ប្រើ volume ពិត COMEX។\n"
    "• <b>បានបង្ហាញ \"⚠ built for 5m\"?</b> ប្តូរទៅ chart 5 នាទី។\n"
    "• <b>\"D · no setup\"?</b> សម័យមុនជា balance — ថ្ងៃនេះគ្មានការដំឡើង។ នេះជាចម្លើយដែរ។\n"
    "• <b>មានកំហុសក្រហម?</b> ថតអេក្រង់ ហើយផ្ញើមកក្នុង topic នេះ។"
    + SEP +
    "❓ <b>FAQ</b>\n"
    "• <b>Do I need to pay?</b> No. It's free and works on the free TradingView plan.\n"
    "• <b>Which timeframe?</b> 5-minute XAUUSD (OANDA). The bigger picture is already in the panel (30m/1H/4H).\n"
    "• <b>Is this real order flow?</b> It's an estimate from tick volume (OANDA + 2 other brokers), not real bid/ask. The profile uses real COMEX volume.\n"
    "• <b>It says \"⚠ built for 5m\"?</b> Switch to the 5-minute chart.\n"
    "• <b>\"D · no setup\"?</b> The previous session was balanced — no setup today. That's an answer too.\n"
    "• <b>Red error?</b> Take a screenshot and post it in this topic.",

    # 7 · disclaimer + feedback
    "⚠️ <b>សំខាន់មុនប្រើ</b>\n"
    "• Indicator នេះជាឧបករណ៍សិក្សា មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។\n"
    "• គ្មាន indicator ណាត្រូវ 100% ទេ។ លទ្ធផលចាស់មិនធានាលទ្ធផលអនាគតទេ។\n"
    "• ហានិភ័យ 0.5–1% ក្នុងមួយ trade ហើយដាក់ SL ជានិច្ច។\n"
    "• កូដជា open-source (MPL 2.0) — ចែករំលែកបាន សូមរក្សាឈ្មោះ XAU.KH។\n\n"
    "💬 មានមតិ ឬគំនិតកែលម្អ? ផ្ញើក្នុង topic នេះ + រូប chart។"
    + SEP +
    "⚠️ <b>Before you use it</b>\n"
    "• This indicator is an educational tool, not financial advice.\n"
    "• No indicator is right 100% of the time. Past results don't guarantee future results.\n"
    "• Risk 0.5–1% per trade and always use a stop loss.\n"
    "• The code is open-source (MPL 2.0) — share it freely, please keep the XAU.KH credit.\n\n"
    "💬 Feedback or ideas? Post them in this topic with a chart screenshot.",
]

PDF_CAPTION = ("📖 <b>XAU.KH FLOW · សៀវភៅណែនាំ (ខ្មែរ + English)</b>\n"
               "ដំឡើង · អាន chart · ប្រើជាមួយសញ្ញា XAUKHBOT\n"
               "Install · read the chart · combine with XAUKHBOT signals")
PINE_CAPTION = ("📄 <b>XAU_KH_FLOW_public.pine</b> · v1.0\n"
                "កូដ indicator (វិធី B ក្នុង Post 2) · the indicator code (Option B in Post 2)\n"
                "Free · open-source MPL 2.0 · keep the XAU.KH credit")


def post(i, link=None):
    t = POSTS[i]
    return t.replace("{LINK_KM}", link or NO_LINK_KM).replace("{LINK_EN}", link or NO_LINK_EN)
