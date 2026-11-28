from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def scenario_tree(w=420, h=220, caption=""):
    """Current price in the middle; three branches: above the line, below the line, stuck in between."""
    sx, sy = 60, h / 2
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="20" y1="58" x2="{w - 20}" y2="58" stroke="{UP}" stroke-width="1.4" stroke-dasharray="5 4"/>',
           f'<text x="22" y="52" fill="{UP}" class="lt">4,070 · កំពូល range</text>',
           f'<line x1="20" y1="{h - 58}" x2="{w - 20}" y2="{h - 58}" stroke="{DN}" stroke-width="1.4" stroke-dasharray="5 4"/>',
           f'<text x="22" y="{h - 46}" fill="{DN}" class="lt">4,030 · បាត range</text>',
           f'<path d="M20,{sy + 12} L35,{sy - 6} L48,{sy + 4} L{sx},{sy}" fill="none" stroke="#1C1C1E" stroke-width="2.4"/>',
           f'<circle cx="{sx}" cy="{sy}" r="4" fill="#1C1C1E"/>',
           f'<text x="{sx}" y="{sy + 20}" text-anchor="middle" fill="#1C1C1E" class="st">4,050</text>']
    branches = [(f"M{sx},{sy} L150,40 L180,62 L{w - 120},18", "A · បិទលើ 4,070", "Buy → 4,100", UP, 18),
                (f"M{sx},{sy} L130,80 L180,{sy + 18} L240,90 L300,{sy + 14} L{w - 120},{sy - 4}", "C · នៅក្នុង range", "គ្មាន trade", GR, sy - 4),
                (f"M{sx},{sy} L150,{h - 40} L180,{h - 62} L{w - 120},{h - 18}", "B · បិទក្រោម 4,030", "Sell → 4,000", DN, h - 18)]
    for d, t, act, col, ey in branches:
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="{"0" if col != GR else "4 3"}"/>')
        out.append(f'<rect x="{w - 114}" y="{ey - 17}" width="108" height="34" rx="8" fill="{col}" fill-opacity=".12" stroke="{col}"/>')
        out.append(f'<text x="{w - 60}" y="{ey - 3}" text-anchor="middle" fill="{col}" class="st">{t}</text>')
        out.append(f'<text x="{w - 60}" y="{ey + 12}" text-anchor="middle" fill="#1C1C1E" class="st">{act}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=39, part="PART 10 · Professional Trading Development",
    title_km="ការវិភាគទីផ្សារបែបអាជីព", title_en="Professional Market Analysis: Pre-market · Scenario Planning · Multiple Outcomes · Market Regime · Post-market Review",
    intro="""អ្នកចាប់ផ្ដើមច្រើនតែសួរថា <i>"ថ្ងៃនេះមាសឡើង ឬធ្លាក់?"</i>។ អ្នកជំនាញសួរថា <i>"<b>ប្រសិនបើ</b>មាសឡើង ខ្ញុំធ្វើអ្វី? <b>ប្រសិនបើ</b>ធ្លាក់ ខ្ញុំធ្វើអ្វី?"</i>។
ការវិភាគបែបអាជីពមិនមែនជាការ<b>ទាយ</b>ទេ។ វាជាការ<b>រៀបចំខ្លួន</b>សម្រាប់លទ្ធផលច្រើនដែលអាចកើតឡើង។
ជំពូកនេះភ្ជាប់អ្វីដែលអ្នកបានរៀនទាំងអស់ (structure, liquidity, volume profile, market bias ក្នុង Chapter 26, sessions និង news ក្នុង Chapter 31)
ឱ្យទៅជា<b>ដំណើរការប្រចាំថ្ងៃ</b>មួយ: រៀបចំមុនទីផ្សារ → សរសេរ scenario → កំណត់ប្រភេទទីផ្សារ (regime) → ពិនិត្យឡើងវិញក្រោយទីផ្សារ។""",
    sections=[
        ("ការទាយ ទល់នឹង ការរៀបចំ", """
<p>គ្មាននរណាម្នាក់ដឹងច្បាស់ថាតម្លៃមាសនឹងទៅណាទេ។ ទីផ្សារទទួលឥទ្ធិពលពីព័ត៌មាន អ្នកជួញដូរធំៗ និងព្រឹត្តិការណ៍ដែលមិនអាចដឹងមុន។
ដូច្នេះអ្នកជំនាញមិនភ្នាល់លើទិសមួយទេ។ ពួកគេរៀបចំ<b>ផែនការ</b>សម្រាប់ទិសនីមួយៗ ហើយទុកឱ្យ<b>ទីផ្សារជ្រើស</b>។</p>
<table style='break-inside:avoid'><tr><th></th><th>អ្នកទាយ</th><th>អ្នករៀបចំ</th></tr>
<tr><td>សំណួរ</td><td>"ឡើង ឬធ្លាក់?"</td><td>"ប្រសិនបើ... នោះ..."</td></tr>
<tr><td>ពេលតម្លៃទៅផ្ទុយ</td><td>ភ្ញាក់ផ្អើល · រំកិល SL</td><td>ប្ដូរទៅ scenario ទីពីរ</td></tr>
<tr><td>Entry</td><td>ចូលមុន ដោយជំនឿ</td><td>ចូលក្រោយការបញ្ជាក់នៅ level ដែលបានរៀបចំ</td></tr>
<tr><td>អារម្មណ៍</td><td>ចង់ឱ្យខ្លួនឯងត្រូវ</td><td>ចង់ធ្វើតាមផែនការ</td></tr></table>
<div class='box tip'>💡 គោលដៅនៃការវិភាគមិនមែនជាការ "ត្រូវ" ទេ។ គោលដៅគឺ<b>ដឹងមុន</b>ថាអ្នកនឹងធ្វើអ្វី នៅពេលតម្លៃមកដល់ level នីមួយៗ។</div>
"""),
        ("Pre-market Preparation: រៀបចំមុនទីផ្សារ", """
<p>មុន session ដែលអ្នក trade (ជាធម្មតា London ឬ New York) ចំណាយពេល 15–30 នាទី តាមលំដាប់ដដែលរាល់ថ្ងៃ:</p>
""" + flow([("Macro · News", "📰 ព័ត៌មានថ្ងៃនេះ", BL), ("HTF Bias", "Daily · 4H", PU), ("Key Levels", "PDH · PDL · POC", GOLD), ("Liquidity", "EQH · EQL", OR),
            ("Regime", "Trend · Range", GR), ("Scenarios", "A · B · C", UP)],
           caption="Pre-market checklist: ពីរូបធំ ទៅលម្អិត") + """
<ul><li><b>Macro និង News</b>: មានព័ត៌មាន high-impact អ្វីខ្លះថ្ងៃនេះ (CPI, NFP, FOMC)? ម៉ោងប៉ុន្មាន? ពិនិត្យ 📰 News ក្នុង group។</li>
<li><b>HTF Bias</b>: Daily និង 4H structure កំពុងឡើង ធ្លាក់ ឬ range (Chapter 9, 26)?</li>
<li><b>Key Levels</b>: <span class='en-term'>PDH/PDL</span> (Previous Day High/Low), Asia high/low, <span class='en-term'>POC</span> និង value area (Chapter 19–21), order block ឬ FVG សំខាន់ៗ</li>
<li><b>Liquidity</b>: តើ <span class='en-term'>equal highs/lows</span> នៅឯណា? តម្លៃទំនងជាទៅប្រមូល liquidity មុននោះ (Chapter 12)</li></ul>
<div class='box ok'>✅ រូប 📊 Analysis ក្នុង group មាន structure, liquidity និង level សំខាន់ៗរួចហើយ។ ប្រើវាជាចំណុចចាប់ផ្ដើម ប៉ុន្តែគូរ level ដោយខ្លួនឯងលើ MT5 ផង ដើម្បីយល់ពីមូលហេតុ។</div>
"""),
        ("Scenario Planning: រៀបចំ Scenario", """
<p>Scenario ល្អមួយមាន 4 ផ្នែក: <b>លក្ខខណ្ឌ</b> (ប្រសិនបើ...) · <b>entry</b> · <b>invalidation/SL</b> · <b>target</b>។
ឧទាហរណ៍ មាសនៅ 4,050 ក្នុង range 4,030–4,070:</p>
""" + scenario_tree(caption="ពី level ដដែល មានផ្លូវបី · អ្នកមិនចាំបាច់ដឹងថាផ្លូវណា ត្រឹមតែដឹងថាត្រូវធ្វើអ្វីលើផ្លូវនីមួយៗ") + """
<table style='break-inside:avoid'><tr><th>Scenario</th><th>ប្រសិនបើ...</th><th>នោះ...</th></tr>
<tr><td style='color:#34C759'><b>A</b></td><td>ទៀន 15m បិទលើ 4,070 ជាមួយ displacement</td><td>រង់ចាំ retest · Buy · SL 4,060 · TP 4,100 (3R)</td></tr>
<tr><td style='color:#FF3B30'><b>B</b></td><td>ទៀន 15m បិទក្រោម 4,030</td><td>រង់ចាំ retest · Sell · SL 4,040 · TP 4,000 (3R)</td></tr>
<tr><td style='color:#8E8E93'><b>C</b></td><td>តម្លៃនៅចន្លោះ 4,030–4,070</td><td>គ្មាន trade នៅកណ្ដាល · ឬ trade តែគែម range</td></tr></table>
<p>ពិនិត្យលេខ: SL $10 = 100 pips · TP $30 = 300 pips · ជាមួយ 0.01 lot ខាត $10 ឬឈ្នះ $30។</p>
<div class='box tip'>💡 ក្នុង 📊 Analysis របស់ XAU.KH <b>TARGET BUY</b> និង <b>TARGET SELL</b> គឺជា scenario A និង B ដូចខាងលើ។ ពួកវាមិនមែនជាការណែនាំឱ្យចូលទាំងពីរទេ គឺជាផែនការសម្រាប់ទិសនីមួយៗ។</div>
"""),
        ("Multiple Possible Outcomes: លទ្ធផលច្រើន", """
<p>Level សំខាន់មួយ (ឧ. PDH) អាចផ្ដល់លទ្ធផលយ៉ាងហោចណាស់ 3 ប្រភេទ។ ត្រៀមខ្លួនសម្រាប់ទាំងអស់:</p>
""" + zigzag([30, 55, 45, 70, 62, 92], {5: ("បន្ត", UP)}, lines=[(70, 0, 5, "PDH", OR, True)],
            caption="① Breakout: បិទលើ PDH ហើយបន្ត → ធ្វើតាមទិសឡើង") + zigzag([30, 55, 45, 70, 76, 40, 50, 22], {4: ("Sweep", DN), 7: ("ធ្លាក់", DN)}, lines=[(70, 0, 7, "PDH", OR, True)],
            caption="② Sweep & reverse: wick លើ PDH ហើយបិទត្រឡប់ចុះ → liquidity grab (Chapter 12)") + zigzag([30, 55, 45, 69, 52, 68, 50, 66, 54], {3: ("ប៉ះ", GR), 5: ("ប៉ះ", GR), 7: ("ប៉ះ", GR)}, lines=[(70, 0, 8, "PDH", OR, True)],
            caption="③ Chop: ប៉ះម្ដងហើយម្ដងទៀត ដោយគ្មានទិសច្បាស់ → រង់ចាំ") + """
<div class='box warn'>⚠️ កុំចូល trade <b>មុន</b>ដឹងថាលទ្ធផលណាកំពុងកើតឡើង។ ការចូល Sell ភ្លាមនៅ PDH ដោយគិតថាវានឹង sweep អាចខាត បើវាជា breakout។ រង់ចាំ<b>ការបិទទៀន</b>។</div>
"""),
        ("Market Regime Identification: កំណត់ប្រភេទទីផ្សារ", """
<p><span class='en-term'>Market regime</span> គឺជា "អាកាសធាតុ" នៃទីផ្សារ។ Setup ដដែលអាចដំណើរការល្អក្នុង regime មួយ ហើយខាតក្នុង regime មួយទៀត។
ដូច្នេះកំណត់ regime <b>មុន</b>ជ្រើស setup។ សំណួរពីរ:</p>
<ul><li><b>តើមានទិសដៅ?</b> HH/HL ឬ LH/LL ច្បាស់លើ 4H/1H = trend · កំពូលនិងបាតនៅកម្រិតដដែល = range</li>
<li><b>តើចលនាធំប៉ុណ្ណា?</b> ប្រៀបធៀបទំហំទៀន ឬ <span class='en-term'>ATR</span> ថ្ងៃនេះជាមួយថ្ងៃធម្មតា</li></ul>
""" + bars([("ថ្ងៃ 1", 28, GR), ("ថ្ងៃ 2", 32, GR), ("ថ្ងៃ 3", 25, GR), ("ថ្ងៃ 4", 30, GR), ("ថ្ងៃ 5", 75, DN)], unit="$",
           caption="<b>ឧទាហរណ៍</b> Daily range: ថ្ងៃ 5 ធំជាងធម្មតាប្រហែល 2.5 ដង (ឧ. ថ្ងៃ NFP) = volatile regime") + """
<div class='box tip'>💡 Daily range របស់មាសប្រែប្រួលតាមពេល។ កុំប្រើលេខថេរ។ ប្រៀបធៀបថ្ងៃនេះជាមួយ<b>ថ្ងៃថ្មីៗរបស់វាផ្ទាល់</b> (ឧ. ATR 14 ថ្ងៃលើ MT5)។</div>
"""),
        ("Trend · Range · Volatility: វិធី trade តាម Regime", """
""" + zigzag([10, 35, 25, 55, 42, 75, 62, 92], {2: ("HL", UP), 4: ("HL", UP), 6: ("HL", UP)}, caption="Trend: ទិញ pullback ទៅ HL / OB / FVG តាមទិស HTF") + zigzag([25, 75, 28, 74, 26, 76, 27, 73], {1: ("Sell", DN), 2: ("Buy", UP), 3: ("Sell", DN), 4: ("Buy", UP)},
            lines=[(76, 0, 7, "", DN, True), (25, 0, 7, "", UP, True)], caption="Range (បន្ទាត់ក្រហម = Range High · បៃតង = Range Low): Buy នៅបាត · Sell នៅកំពូល · គ្មាន trade នៅកណ្ដាល (EQ)") + """
<table style='break-inside:avoid'><tr><th>Regime</th><th>Setup ល្អ</th><th>ជៀសវាង</th><th>Risk</th></tr>
<tr><td style='color:#34C759'><b>Trend</b></td><td>Pullback · BOS continuation</td><td>Sell ទល់ trend ខ្លាំង</td><td>ធម្មតា (1%)</td></tr>
<tr><td style='color:#0A84FF'><b>Range</b></td><td>Fade គែម · sweep នៃ high/low</td><td>ដេញ breakout នៅកណ្ដាល</td><td>ធម្មតា · TP ខ្លីជាង</td></tr>
<tr><td style='color:#FF3B30'><b>Volatile</b></td><td>រង់ចាំ structure ច្បាស់ក្រោយ news</td><td>ចូលពេល spread ធំ</td><td>តូចជាង (0.5%) ឬឈប់</td></tr>
<tr><td style='color:#8E8E93'><b>Quiet</b></td><td>រង់ចាំ session ចាប់ផ្ដើម</td><td>Trade ពេលទីផ្សារស្ងាត់ (Asia ចុង)</td><td>—</td></tr></table>
<div class='box warn'>⚠️ ពេល volatility ខ្លាំង SL ត្រូវឆ្ងាយជាង ដូច្នេះ <b>lot ត្រូវតូចជាង</b>។ ឧ. គណនី $2,000 · risk 1% = $20: SL $10 → 0.02 lot · SL $20 → 0.01 lot។ បើ SL ត្រូវការ $40 ហើយ lot តូចបំផុត 0.01 = risk $40 (2%) ធំពេក → <b>មិន trade</b>។ Regime ផ្លាស់ ទំហំ lot ក៏ផ្លាស់។</div>
"""),
        ("ពីការវិភាគ ទៅ Trade Plan", """
<p>ការវិភាគត្រូវបញ្ចប់ដោយ<b>ផែនការសរសេរ</b> ខ្លីៗ ដែលអ្នកអានបានក្នុង 30 វិនាទី។ គំរូ:</p>
<div class='box ok'>✅ <b>XAU/USD · ថ្ងៃអង្គារ · London</b><br>
Regime: Range 4,030–4,070 (4H) · ATR ធម្មតា<br>
News: គ្មាន high-impact មុន 19:30<br>
A: បិទ 15m លើ 4,070 → Buy retest · SL 4,060 · TP 4,100<br>
B: បិទ 15m ក្រោម 4,030 → Sell retest · SL 4,040 · TP 4,000<br>
C: នៅកណ្ដាល → គ្មាន trade · ឈប់ 30 នាទីមុន news<br>
Max: 2 trade · ឈប់ពេលខាត 2R</div>
<p>ពេលតម្លៃមកដល់ level សូមប្រើ <b>/check</b> ក្នុង group ដើម្បីផ្ទៀងផ្ទាត់ structure ជាមួយ plan របស់អ្នក។
បើមាន 🚨 Signal ដែលផ្ទុយពី scenario របស់អ្នក នោះជាសញ្ញាឱ្យពិនិត្យឡើងវិញ មិនមែនបើក trade ពីរទិស។</p>
"""),
        ("Post-market Review: ពិនិត្យក្រោយទីផ្សារ", """
<p>ក្រោយ session បិទ ចំណាយពេល 10 នាទីប្រៀបធៀប<b>ផែនការ</b>ជាមួយ<b>អ្វីដែលបានកើតឡើង</b>។ គោលដៅគឺកែលម្អការវិភាគ មិនមែនបន្ទោសខ្លួនឯង។</p>
""" + flow([("Scenario?", "A · B · C", BL), ("ហេតុអ្វី?", "news · liquidity", PU), ("ខ្ញុំធ្វើតាម?", "បាទ · ទេ", GOLD), ("មេរៀន", "មួយចំណុច", UP)],
           caption="Post-market review 4 សំណួរ · រក្សាទុកក្នុង journal ជាមួយ screenshot") + """
<table style='break-inside:avoid'><tr><th>សំណួរ</th><th>ឧទាហរណ៍ចម្លើយ</th></tr>
<tr><td>Scenario ណាកើតឡើង?</td><td>B: បិទក្រោម 4,030 នៅ 16:15 ហើយធ្លាក់ដល់ 4,005</td></tr>
<tr><td>Regime ត្រូវ ឬខុស?</td><td>ត្រូវ: range រហូតដល់ London បន្ទាប់មក breakout</td></tr>
<tr><td>ខ្ញុំធ្វើតាម plan?</td><td>បាទ ប៉ុន្តែចូលយឺត ព្រោះមិនបានដាក់ Alert</td></tr>
<tr><td>មេរៀនមួយ</td><td>ដាក់ Alert នៅគែម range ទាំងពីរ រាល់ថ្ងៃ</td></tr></table>
<div class='box tip'>💡 ថ្ងៃដែលអ្នកមិន trade ក៏ត្រូវ review ដែរ។ "Scenario C កើតឡើង ហើយខ្ញុំមិន trade" = ថ្ងៃដែលអ្នកធ្វើតាមផែនការ<b>បានល្អ</b>។ 📈 Proof ក្នុង group ក៏អាចប្រើប្រៀបធៀបជាមួយ scenario របស់អ្នកបាន។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ មាន scenario តែមួយ ដែលខ្លួនឯងជឿ</li>
<li>❌ Scenario គ្មានលក្ខខណ្ឌច្បាស់ ("ប្រហែលជាឡើង")</li>
<li>❌ ប្រើ setup trend ក្នុងទីផ្សារ range ឬផ្ទុយមកវិញ</li>
<li>❌ មិនពិនិត្យ 📰 News មុន ហើយត្រូវភ្ញាក់ផ្អើលដោយ NFP/CPI</li>
<li>❌ ប្ដូរ plan កណ្ដាល session ដោយគ្មានហេតុផលពី structure</li>
<li>❌ រំលង post-market review ពេលខាត (ពេលដែលត្រូវការវាបំផុត)</li></ul>
"""),
    ],
    summary=["អ្នកជំនាញមិនទាយ · ពួកគេរៀបចំ \"ប្រសិនបើ... នោះ...\"",
             "Pre-market: News → HTF bias → key levels → liquidity → regime → scenarios",
             "Scenario នីមួយៗមាន លក្ខខណ្ឌ · entry · SL · target · តែងតែមាន A · B · C",
             "Regime: Trend (pullback) · Range (គែម) · Volatile (lot តូច ឬឈប់)",
             "Post-market: scenario ណា? ហេតុអ្វី? ធ្វើតាម plan? មេរៀនមួយ"],
    exercise=["ធ្វើ pre-market checklist សម្រាប់ session ថ្ងៃស្អែក: សរសេរ bias Daily/4H, PDH, PDL និង liquidity ពីរកន្លែង។",
              "សរសេរ scenario A, B និង C ពេញលេញ (លក្ខខណ្ឌ · entry · SL · TP) ហើយគណនា R និងលុយសម្រាប់ 0.02 lot។",
              "មើល Daily chart មាស 10 ថ្ងៃចុងក្រោយ។ ថ្ងៃណាជា trend, range ឬ volatile? ប្រៀបធៀបជាមួយ 📰 News នៃថ្ងៃទាំងនោះ។",
              "ក្រោយ session ធ្វើ post-market review 4 សំណួរ ហើយប្រៀបធៀប scenario របស់អ្នកជាមួយ 📊 Analysis ក្នុង group។"],
)
