from academy_pdf import bars, flow, zigzag

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"

CH = dict(
    ch=6, part="PART 1 · Foundations",
    title_km="ស្គាល់ Timeframe", title_en="Understanding Timeframes: Top-down · Multi-Timeframe",
    intro="""Chart មាសដូចគ្នា ប៉ុន្តែនៅ <b>D1</b> អាចជា uptrend ខណៈ <b>M5</b> កំពុងធ្លាក់។ តើមួយណាត្រឹមត្រូវ?
ចម្លើយ: <b>ទាំងពីរត្រឹមត្រូវ</b> ប៉ុន្តែវាប្រាប់រឿងខុសគ្នា។ ជំពូកនេះបង្រៀនអ្នកពី <b>Higher</b> និង <b>Lower Timeframe</b>,
វិធី <span class='en-term'>Top-down / Multi-timeframe analysis</span>, ភាពខុសគ្នារវាង <b>scalping, intraday</b> និង <b>swing</b>,
របៀបជ្រើស timeframe ដែលសមនឹងជីវិតអ្នក និងរបៀបជៀសវាង<b>ការច្រឡំ timeframe</b> ដែលធ្វើឱ្យអ្នកចាប់ផ្ដើមខាតច្រើន។""",
    sections=[
        ("Higher Timeframe និង Lower Timeframe", """
<p><span class='en-term'>HTF</span> (Higher Timeframe) ដូចជា D1 និង H4 បង្ហាញ<b>រូបភាពធំ</b>។ <span class='en-term'>LTF</span> (Lower Timeframe)
ដូចជា M15 និង M5 បង្ហាញ<b>លម្អិត</b>។ ពាក្យ "ធំ" ឬ "តូច" គឺ<b>ធៀប</b>គ្នា: សម្រាប់អ្នក scalp នៅ M1, M15 គឺជា HTF។</p>
<table><tr><th></th><th>HTF (D1 · H4)</th><th>LTF (M15 · M5)</th></tr>
<tr><td>បង្ហាញ</td><td>ទិសដៅធំ level ធំ</td><td>ចំណុចចូល លម្អិត</td></tr>
<tr><td>Noise</td><td>តិច</td><td>ច្រើន</td></tr>
<tr><td>សញ្ញា</td><td>យឺត តែគួរឱ្យទុកចិត្តជាង</td><td>លឿន តែខុសញឹកញាប់</td></tr>
<tr><td>SL</td><td>ធំ ($10–$40+)</td><td>តូច ($2–$8)</td></tr></table>
<div class='box tip'>💡 ចងចាំ: <b>HTF សម្រេចទិស · LTF សម្រេចពេលចូល</b>។</div>
"""),
        ("រូបភាពធំ និងរូបភាពតូច", """
<p>សូមមើលឧទាហរណ៍: នៅ H4 មាសកំពុងឡើង (HH HL)។ ប៉ុន្តែនៅក្នុងជើងធ្លាក់មួយនៃ H4 នោះ M15 បង្ហាញ downtrend តូចមួយ (LH LL)។</p>
""" + zigzag([10, 45, 30, 72, 50, 92], {1: ("HH", UP), 2: ("HL", UP), 3: ("HH", UP), 4: ("HL ?", OR), 5: ("HH", UP)},
             caption="H4: uptrend · ជើងធ្លាក់ពី HH ទៅ HL គឺជា pullback") + zigzag([90, 70, 80, 58, 66, 44, 52, 30, 48, 62], {1: ("LL", DN), 2: ("LH", DN), 3: ("LL", DN), 4: ("LH", DN), 5: ("LL", DN), 7: ("HL H4", UP)},
             caption="M15 ក្នុងជើង pullback ដដែល: មើលទៅដូច downtrend តែវាគ្រាន់តែជា pullback នៃ H4") + """
<div class='box warn'>⚠️ អ្នកដែលមើលតែ M15 នឹងគិតថា "ធ្លាក់ហើយ ត្រូវ SELL" ហើយ SELL នៅ<b>បាត</b>នៃ pullback H4 ពេល buyers ធំៗកំពុងរង់ចាំទិញ។</div>
"""),
        ("Multi-Timeframe Analysis: វិធី Top-down", """
<p><span class='en-term'>Top-down analysis</span> គឺមើលពី timeframe <b>ធំទៅតូច</b> ជាលំដាប់ ដើម្បីឱ្យ LTF តែងតែនៅក្នុងបរិបទនៃ HTF:</p>
""" + flow([("D1", "ទិសធំ · level ធំ", BL), ("H4", "Bias · structure", GOLD), ("H1 / M30", "Zone ចូល", OR), ("M15", "Setup", UP),
            ("M5", "Confirmation", UP)], caption="Top-down: D1 → H4 → H1/M30 → M15 → M5") + """
<table><tr><th>ជំហាន</th><th>សំណួរ</th></tr>
<tr><td>D1</td><td>Trend ធំទៅណា? Level សំខាន់នៅឯណា (high/low ម្សិលមិញ សប្ដាហ៍មុន)?</td></tr>
<tr><td>H4</td><td>Structure ឡើង ឬធ្លាក់? Bias របស់ខ្ញុំថ្ងៃនេះគឺ BUY ឬ SELL?</td></tr>
<tr><td>H1 / M30</td><td>តម្លៃនៅជិត zone ណាដែលខ្ញុំចង់ trade?</td></tr>
<tr><td>M15</td><td>មាន setup ឬអត់ (rejection, CHOCH, sweep)?</td></tr>
<tr><td>M5</td><td>មានការបញ្ជាក់ ហើយ SL ដាក់ត្រង់ណា?</td></tr></table>
<div class='box ok'>✅ រូប 📊 Analysis របស់ XAU.KH មានជួរ <b>D 4H 1H 30m 15m 5m</b> ជាមួយព្រួញ ↑↓ នៅខាងលើជានិច្ច។ វាជា top-down
ដែលបានធ្វើរួច: មើលថា timeframe ប៉ុន្មានស្របគ្នា មុននឹងសម្រេច។</div>
"""),
        ("ពេល Timeframe ស្របគ្នា និងពេលផ្ទុយគ្នា", """
<table><tr><th>ស្ថានភាព</th><th>អត្ថន័យ</th><th>អ្វីត្រូវធ្វើ</th></tr>
<tr><td>HTF ↑ · LTF ↑</td><td>ស្របគ្នា (alignment)</td><td>រក BUY តាម pullback · ឱកាសល្អបំផុត</td></tr>
<tr><td>HTF ↑ · LTF ↓</td><td>LTF កំពុង pullback</td><td>រង់ចាំ LTF ត្រឡប់ឡើង (CHOCH ↑) នៅ zone HTF</td></tr>
<tr><td>HTF ↓ · LTF ↑</td><td>LTF កំពុង pullback</td><td>រង់ចាំ LTF ត្រឡប់ចុះ ដើម្បី SELL</td></tr>
<tr><td>HTF ចំហៀង (range)</td><td>គ្មានទិសច្បាស់</td><td>Trade តែនៅគែម range ឬកុំ trade</td></tr></table>
""" + bars([("6/6 ស្រប", 6, UP), ("5/6", 5, UP), ("4/6", 4, OR), ("3/6 ចែកគ្នា", 3, DN)], h=160,
           caption="ចំនួន timeframe (D 4H 1H 30m 15m 5m) ដែលស្របនឹងទិសរបស់អ្នក · កាន់តែច្រើន កាន់តែច្បាស់") + """
<div class='box warn'>⚠️ ការស្របគ្នា <b>មិនធានា</b>ការឈ្នះទេ។ វាគ្រាន់តែធ្វើឱ្យ trade របស់អ្នកដើរ<b>តាមខ្យល់</b> ជំនួសឱ្យប្រឆាំងនឹងខ្យល់។</div>
"""),
        ("Scalping · Intraday · Swing", """
<p>Style នៃការ trade នីមួយៗប្រើ timeframe ខុសគ្នា ហើយត្រូវការពេល និងចិត្តខុសគ្នា:</p>
<table><tr><th></th><th>Scalping</th><th>Intraday</th><th>Swing</th></tr>
<tr><td>កាន់ trade</td><td>នាទី</td><td>ម៉ោង (បិទក្នុងថ្ងៃ)</td><td>ច្រើនថ្ងៃ</td></tr>
<tr><td>Timeframe ចូល</td><td>M1–M5</td><td>M15–H1</td><td>H4–D1</td></tr>
<tr><td>Timeframe ទិស</td><td>M15–H1</td><td>H4–D1</td><td>D1–W1</td></tr>
<tr><td>SL មាស (ប្រហែល)</td><td>$2–$6</td><td>$5–$15</td><td>$15–$50+</td></tr>
<tr><td>ពេលមើល chart</td><td>ច្រើន ត្រូវផ្ដោតខ្លាំង</td><td>មធ្យម</td><td>តិច</td></tr>
<tr><td>ថ្លៃ spread/swap</td><td>Spread សំខាន់ខ្លាំង</td><td>Spread មធ្យម</td><td>Swap សំខាន់</td></tr></table>
""" + bars([("Scalp", 4, DN), ("Intraday", 10, OR), ("Swing", 30, BL)], unit="$", h=160,
           caption="ឧទាហរណ៍ SL ធម្មតា (ដុល្លារ) · SL ធំ = lot តូចជាង សម្រាប់ risk ដូចគ្នា") + """
<div class='box tip'>💡 សញ្ញា ⭐ របស់ XAU.KH ផ្អែកលើ <b>4H</b> (intraday ទៅ swing) ហើយសញ្ញា 🚨 M15 គឺជា intraday/scalp។ នៅក្នុងសញ្ញានីមួយៗ
"💰 0.01 lot: SL −$…" ជួយអ្នកដឹងថា style នោះត្រូវការ SL ធំប៉ុណ្ណា។</div>
"""),
        ("ជ្រើស Timeframe ដែលសមនឹងអ្នក", """
<p>Timeframe "ល្អបំផុត" គឺជាមួយដែល<b>សមនឹងជីវិត និងចិត្តរបស់អ្នក</b> មិនមែនមួយដែលអ្នកដទៃប្រើទេ:</p>
<ul><li><b>ធ្វើការពេញម៉ោង</b> មើល chart បានតែល្ងាច → intraday H1/M15 ជុំវិញម៉ោង London/New York (ល្ងាចនៅកម្ពុជា) ឬ swing H4។</li>
<li><b>មានពេលច្រើន</b> ផ្ដោតបាន → intraday M15/M5។</li>
<li><b>អ្នកចាប់ផ្ដើមដំបូង</b> → ចាប់ផ្ដើម <b>M15 ជាមួយ bias H4</b>។ M1 លឿនពេក ហើយ noise ច្រើនពេក។</li></ul>
""" + flow([("ពេលវេលា", "មើល chart ប៉ុន្មានម៉ោង?", BL), ("គណនី", "SL ធំប៉ុណ្ណាអាចទ្រាំ?", GOLD), ("ចិត្ត", "រង់ចាំបានយូរប៉ុណ្ណា?", OR), ("ជ្រើស", "HTF + LTF មួយគូ", UP)],
           caption="សំណួរ 3 មុនពេលជ្រើស timeframe") + """
<div class='box ok'>✅ ជ្រើស <b>គូមួយ</b> (ឧ. H4 + M15 ឬ H1 + M5) ហើយប្រើវាឱ្យជាប់លាប់យ៉ាងតិច 1–2 ខែ ដើម្បីឱ្យលទ្ធផលក្នុង journal អាចវាស់បាន។</div>
"""),
        ("Timeframe និងម៉ោង Session", """
<p>Timeframe តូច ប្រែប្រួលខ្លាំងតាមម៉ោង។ សម្រាប់មាស (ម៉ោងកម្ពុជា ប្រហាក់ប្រហែល):</p>
<table><tr><th>Session</th><th>ម៉ោងកម្ពុជា</th><th>ចរិត M5/M15</th></tr>
<tr><td>Asia</td><td>ព្រឹក ដល់ រសៀល</td><td>Range តូច · noise · ទៀនតូចៗ</td></tr>
<tr><td>London</td><td>រសៀល ដល់ ល្ងាច</td><td>ចលនាចាប់ផ្ដើម · sweep Asia high/low</td></tr>
<tr><td>New York</td><td>យប់</td><td>ចលនាធំ · ព័ត៌មានអាមេរិក</td></tr></table>
<p>ម៉ោងពិតប្រាកដប្ដូរតាមរដូវ (summer/winter) ហើយនឹងរៀនលម្អិតនៅ Chapter 16 និង 31។ ចំណុចសំខាន់: <b>pattern ដូចគ្នាលើ M5 ក្នុងម៉ោង Asia
ខ្សោយជាងក្នុងម៉ោង London ឬ New York</b>។</p>
"""),
        ("ជៀសវាងការច្រឡំ Timeframe", """
<p>កំហុសធំបំផុតមួយរបស់អ្នកចាប់ផ្ដើម គឺ<b>ប្ដូរ timeframe រហូតដល់ឃើញអ្វីដែលខ្លួនចង់ឃើញ</b>:</p>
""" + flow([("ចង់ BUY", "មើល H4: ធ្លាក់", DN), ("ប្ដូរ H1", "នៅធ្លាក់", DN), ("ប្ដូរ M5", "ឃើញឡើង!", OR), ("BUY", "ប្រឆាំងទិសធំ", DN)],
           caption="❌ \"Timeframe shopping\": រកភស្តុតាងសម្រាប់ការសម្រេចចិត្តដែលបានធ្វើរួច") + """
<ul><li>✅ សម្រេច bias នៅ HTF <b>មុន</b> ហើយសរសេរវាចុះ (ឧ. "H4 bearish ថ្ងៃនេះ")។</li>
<li>✅ ប្រើ timeframe ត្រឹម <b>2–3</b> ប៉ុណ្ណោះ: មួយសម្រាប់ទិស មួយសម្រាប់ zone មួយសម្រាប់ entry។</li>
<li>✅ SL និង TP ត្រូវ<b>សមស្រប</b>នឹង timeframe: entry M5 មិនគួរមាន TP ទៅ level D1 ឆ្ងាយ $80 ទេ។</li>
<li>✅ បើ HTF និង LTF ផ្ទុយគ្នា ហើយអ្នកមិនច្បាស់ → <b>មិន trade</b> ក៏ជាការសម្រេចចិត្តដ៏ល្អមួយ។</li></ul>
<div class='box tip'>💡 មុន trade វាយ <b>/check</b> ក្នុង group ដើម្បីមើលការស្របគ្នានៃ D 4H 1H 30m 15m 5m ភ្លាមៗ។</div>
"""),
    ],
    summary=["HTF (D1 H4) សម្រេចទិស · LTF (M15 M5) សម្រេចពេលចូល",
             "Top-down: D1 → H4 → H1/M30 → M15 → M5",
             "LTF ផ្ទុយ HTF ភាគច្រើនជា pullback: រង់ចាំ LTF ត្រឡប់មកតាមទិសធំ",
             "Scalp (M1–M5) · Intraday (M15–H1) · Swing (H4–D1) · SL ខុសគ្នា",
             "ជ្រើសគូ timeframe មួយ ប្រើឱ្យជាប់លាប់ · កុំ \"timeframe shopping\""],
    exercise=["ធ្វើ top-down លើមាសថ្ងៃនេះ: សរសេរទិស D1, H4, H1, M15 ហើយសម្រេច bias មួយ។",
              "ធៀបលទ្ធផលរបស់អ្នកជាមួយជួរ D 4H 1H 30m 15m 5m នៅរូប 📊 Analysis ចុងក្រោយ។ ស្របគ្នាប៉ុន្មាន?",
              "តើ style មួយណា (scalp, intraday, swing) សមនឹងម៉ោងរបស់អ្នក? ហេតុអ្វី?",
              "រកករណីមួយដែល M15 ផ្ទុយនឹង H4។ តាមដានថាតើវាជា pullback ឬការប្ដូរទិសពិត។"],
)
