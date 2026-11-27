from academy_pdf import zigzag, flow, bars, twolines

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def process_matrix(w=420, h=210, caption=""):
    """2x2: process (followed rules or not) x outcome (win or loss)."""
    cells = [("ដំណើរការល្អ + ឈ្នះ", "✅ Trade ល្អ · បន្ត", UP, 0, 0),
             ("ដំណើរការល្អ + ខាត", "✅ Trade ល្អ · ថ្លៃធម្មតា", UP, 1, 0),
             ("បំពានច្បាប់ + ឈ្នះ", "⚠️ គ្រោះថ្នាក់បំផុត · សំណាង", OR, 0, 1),
             ("បំពានច្បាប់ + ខាត", "❌ មេរៀនច្បាស់", DN, 1, 1)]
    x0, y0, cw, chh = 74, 30, (w - 84) / 2, (h - 44) / 2
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<text x="{x0 + cw / 2:.1f}" y="20" text-anchor="middle" fill="{GR}" class="lt">ឈ្នះ · Win</text>',
           f'<text x="{x0 + 1.5 * cw:.1f}" y="20" text-anchor="middle" fill="{GR}" class="lt">ខាត · Loss</text>',
           f'<text x="66" y="{y0 + chh / 2 + 4:.1f}" text-anchor="end" fill="{GR}" class="lt">តាមច្បាប់</text>',
           f'<text x="66" y="{y0 + 1.5 * chh + 4:.1f}" text-anchor="end" fill="{GR}" class="lt">បំពាន</text>']
    for t, sub, col, c, r in cells:
        x, y = x0 + c * cw, y0 + r * chh
        out.append(f'<rect x="{x + 3:.1f}" y="{y + 3:.1f}" width="{cw - 6:.1f}" height="{chh - 6:.1f}" rx="10" fill="{col}" fill-opacity=".12" stroke="{col}"/>')
        out.append(f'<text x="{x + cw / 2:.1f}" y="{y + chh / 2 - 4:.1f}" text-anchor="middle" fill="#1C1C1E" class="bt">{t}</text>')
        out.append(f'<text x="{x + cw / 2:.1f}" y="{y + chh / 2 + 16:.1f}" text-anchor="middle" fill="{col}" class="st">{sub}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=37, part="PART 9 · Strategy Development & Testing",
    title_km="កំណត់ហេតុជួញដូរ និងការវាស់លទ្ធផល", title_en="Trading Journal & Performance: Structure · Screenshots · Grading · Weekly & Monthly Review · Mistakes · Improvement",
    intro="""ការចងចាំរបស់មនុស្ស<b>មិនស្មោះត្រង់</b>ទេ។ យើងចាំ trade ឈ្នះធំៗ ហើយភ្លេចការបំពានច្បាប់តូចៗ ដែលកើតឡើងម្ដងហើយម្ដងទៀត។
<span class='en-term'>Trading journal</span> (កំណត់ហេតុជួញដូរ) ប្ដូរ "អារម្មណ៍" ឱ្យទៅជា<b>ទិន្នន័យ</b>។ វាជាឧបករណ៍ដែលភ្ជាប់គ្រប់ជំពូកមុនៗ:
backtest (Chapter 35) និង forward test (Chapter 36) សុទ្ធតែជា journal មួយប្រភេទ។ ជំពូកនេះបង្ហាញពី<b>របៀបរៀបចំ</b> journal
<b>របៀបដាក់ពិន្ទុ</b> trade និង<b>របៀបពិនិត្យ</b>ប្រចាំសប្ដាហ៍ និងប្រចាំខែ ដើម្បីដឹងថាអ្នកពិតជាកំពុងប្រសើរឡើងឬអត់។""",
    sections=[
        ("ហេតុអ្វីត្រូវមាន Journal?", """
<p>អ្នក trade ដែលគ្មាន journal ធ្វើកំហុសដដែលៗ ដោយមិនដឹងខ្លួន។ Journal ឆ្លើយសំណួរដែលចងចាំមិនអាចឆ្លើយបាន:</p>
<ul><li>Setup ណាដែលពិតជាផ្ដល់លទ្ធផលល្អសម្រាប់<b>ខ្ញុំ</b>?</li>
<li>ម៉ោងណា (Asia · London · NY) ដែលខ្ញុំ trade ល្អ ឬអាក្រក់?</li>
<li>កំហុសអ្វីដែលធ្វើឱ្យខ្ញុំខាតច្រើនជាងគេ?</li>
<li>តើខ្ញុំធ្វើតាមច្បាប់ប៉ុន្មានភាគរយ?</li></ul>
""" + flow([("Trade", "តាម plan", BL), ("កត់ត្រា", "ភ្លាមៗ", GOLD), ("ពិនិត្យ", "សប្ដាហ៍ · ខែ", PU), ("កែតម្រូវ", "មួយចំណុច", UP)],
           caption="វដ្ដនៃការរីកចម្រើន · គ្មានការកត់ត្រា = គ្មានការពិនិត្យ = គ្មានការកែ") + """
<div class='box tip'>💡 Journal មិនមែនសម្រាប់កត់តែលុយទេ។ វាកត់<b>ការសម្រេចចិត្ត</b>។ លុយជាលទ្ធផល ការសម្រេចចិត្តជាអ្វីដែលអ្នកគ្រប់គ្រងបាន។</div>
"""),
        ("Journal Structure: រចនាសម្ព័ន្ធ", """
<p>ចាប់ផ្ដើម<b>សាមញ្ញ</b>។ Spreadsheet សៀវភៅ ឬកម្មវិធីណាក៏បាន ឱ្យតែអ្នកកត់<b>រាល់ trade</b>។ ជួរឈរសំខាន់ៗ:</p>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>ជួរឈរ</th><th>ឧទាហរណ៍</th></tr>
<tr><td>ពេលវេលា</td><td>ថ្ងៃ · ម៉ោង · session</td><td>27 Nov · 15:20 · London</td></tr>
<tr><td>Setup</td><td>ឈ្មោះ setup · timeframe · ទិស</td><td>Sweep + CHOCH · 15m · Buy</td></tr>
<tr><td>Plan</td><td>Entry · SL · TP</td><td>4,050 · 4,040 · 4,080</td></tr>
<tr><td>Risk</td><td>Lot · risk % · $</td><td>0.05 · 1% · $50</td></tr>
<tr><td>លទ្ធផល</td><td>Exit · $ · <b>R</b></td><td>4,080 · +$150 · +3R</td></tr>
<tr><td>ដំណើរការ</td><td>តាមច្បាប់? · grade · កំហុស</td><td>បាទ · A · —</td></tr>
<tr><td>ចិត្ត</td><td>អារម្មណ៍ 1–5 · កំណត់</td><td>3 · ស្ងប់</td></tr>
<tr><td>រូប</td><td>Screenshot មុន / ក្រោយ</td><td>ឈ្មោះ file</td></tr></table>
<p>ពិនិត្យ: 0.05 lot = 5 oz · តម្លៃផ្លាស់ $10 (SL) = ខាត $50 · ឡើង $30 (TP) = ចំណេញ $150 = <b>3R</b>។</p>
<div class='box tip'>💡 MT5 មាន history នៃគ្រប់ trade (tab <b>History</b>) ដែលអាចចុចស្ដាំ ហើយទាញ <b>Report</b> ចេញបាន។ ប្រើវាដើម្បីផ្ទៀងផ្ទាត់តម្លៃ fill · ប៉ុន្តែ MT5 មិនដឹង<b>ហេតុផល</b> និង<b>អារម្មណ៍</b>របស់អ្នកទេ។ នោះជាការងាររបស់ journal។</div>
<div class='box ok'>✅ ក្នុង <b>XAU.KH App</b> (/app) មានផ្ទាំង 📒 <b>Journal</b> សម្រាប់តាមដាន signal ដូចជាកំណត់ហេតុ។ សម្រាប់ trade ផ្ទាល់ខ្លួន spreadsheet សាមញ្ញក៏គ្រប់គ្រាន់ដែរ។</div>
"""),
        ("Screenshot Documentation: ថតរូបទុក", """
<p>រូបភាពមួយប្រាប់ច្រើនជាងពាក្យរាប់សិប។ ថត<b>ពីរដង</b>សម្រាប់ trade នីមួយៗ:</p>
<ul><li><b>មុន (Before)</b>: chart timeframe ចូល ជាមួយ entry · SL · TP គូររួច + chart HTF (4H/1H) សម្រាប់បរិបទ</li>
<li><b>ក្រោយ (After)</b>: chart ដដែលពេល trade បិទ ដើម្បីមើលថាតម្លៃពិតជាដើរយ៉ាងណា</li></ul>
""" + zigzag([72, 50, 62, 36, 50, 46], {3: ("Sweep", OR)},
             lines=[(80, 3, 5, "TP", UP, True), (48, 3, 5, "Entry", BL, False), (18, 3, 5, "SL", DN, True)],
             caption="រូប <b>មុន</b>: plan ច្បាស់ មុនចុចប៊ូតុង") + zigzag([72, 50, 62, 36, 50, 46, 62, 56, 80], {3: ("Sweep", OR), 8: ("TP ✓", UP)},
             lines=[(80, 3, 8, "", UP, True), (48, 3, 8, "Entry", BL, False), (18, 3, 8, "SL", DN, True)],
             caption="រូប <b>ក្រោយ</b>: ឃើញផ្លូវតម្លៃពេញលេញ") + """
<p>ដាក់ឈ្មោះ file ឱ្យរកងាយ: <span class='en-term'>2026-11-27_XAU_15m_buy_A_before.png</span>។</p>
<div class='box tip'>💡 រូប 📊 <b>Analysis</b> ឬលទ្ធផល <b>/check</b> ក្នុង group ពេលអ្នកចូល អាចភ្ជាប់ជាបរិបទ (structure · តំបន់) ក្នុង journal បាន។</div>
"""),
        ("Trade Grading: ដាក់ពិន្ទុ Trade", """
<p>ដាក់ពិន្ទុលើ<b>ដំណើរការ</b> (process) មិនមែនលើលទ្ធផលទេ។ Trade មួយអាចឈ្នះដោយសំណាង ឬខាតទោះធ្វើត្រូវគ្រប់យ៉ាង។</p>
<table style='break-inside:avoid'><tr><th>Grade</th><th>អត្ថន័យ</th><th>ឧទាហរណ៍</th></tr>
<tr><td style='color:#34C759'><b>A</b></td><td>តាមច្បាប់ 100%</td><td>Setup ពេញ · SL/TP តាម plan · risk 1%</td></tr>
<tr><td style='color:#E0A100'><b>B</b></td><td>ខុសតូចមួយ</td><td>ចូលយឺត 2 នាទី · TP តិចជាង plan បន្តិច</td></tr>
<tr><td style='color:#FF3B30'><b>C</b></td><td>បំពានច្បាប់សំខាន់</td><td>គ្មាន SL · ផ្លាស់ SL ឱ្យឆ្ងាយ · revenge · lot ធំ · ក្រៅម៉ោង</td></tr></table>
""" + process_matrix(caption="ដំណើរការ × លទ្ធផល · trade ឈ្នះដោយបំពានច្បាប់ បង្រៀនទម្លាប់អាក្រក់") + """
<div class='box warn'>⚠️ Trade <b>C ដែលឈ្នះ</b> គឺគ្រោះថ្នាក់ជាងគេ ព្រោះខួរក្បាលរៀនថា "បំពានច្បាប់ក៏បានលុយ"។ ថ្ងៃណាមួយ ការបំពានដដែលនោះនឹងយកគណនីអ្នក។</div>
"""),
        ("Weekly Review: ពិនិត្យប្រចាំសប្ដាហ៍", """
<p>ជ្រើសពេលថេរមួយ (ឧ. ថ្ងៃសៅរ៍ព្រឹក ពេលទីផ្សារបិទ) ប្រហែល 30 នាទី:</p>
""" + flow([("ប្រមូល", "Trade ទាំងអស់", BL), ("រាប់ grade", "A · B · C", GOLD), ("រក", "Setup ល្អ · កំហុស", PU), ("គោលដៅ", "1 ចំណុច/សប្ដាហ៍", UP)],
           caption="Weekly review: ខ្លី · ទៀងទាត់ · ផ្ដោតលើមួយចំណុច") + """
<table style='break-inside:avoid'><tr><th>Grade</th><th>ចំនួន</th><th>លទ្ធផល</th></tr>
<tr><td>A</td><td>5</td><td>+2, −1, +2, −1, +1.5 = <b>+3.5R</b></td></tr>
<tr><td>B</td><td>2</td><td>−1, +1 = <b>0R</b></td></tr>
<tr><td>C</td><td>1</td><td>ផ្លាស់ SL → <b>−1.5R</b></td></tr>
<tr><td><b>សរុប</b></td><td>8</td><td><b>+2R</b> · rule adherence 5/8 ≈ 63%</td></tr></table>
<p>ឧទាហរណ៍<b>បង្កើតឡើងសម្រាប់រៀន</b>: trade C តែមួយបានស៊ី 1.5R។ បើគ្មានវា សប្ដាហ៍នេះនឹងបាន <b>+3.5R</b>។ គោលដៅសប្ដាហ៍ក្រោយ:
"<b>មិនផ្លាស់ SL ឱ្យឆ្ងាយ</b>"។</p>
<div class='box tip'>💡 សួរ 3 សំណួររាល់សប្ដាហ៍: (1) អ្វីដែលខ្ញុំធ្វើបានល្អ? (2) កំហុសអ្វីដែលកើតឡើងច្រើនជាង 1 ដង? (3) ចំណុច<b>មួយ</b>ដែលខ្ញុំនឹងកែ?</div>
"""),
        ("Monthly Review: ពិនិត្យប្រចាំខែ", """
<p>ប្រចាំខែ មើល<b>លេខ</b> ព្រោះមាន trade គ្រប់គ្រាន់ជាងប្រចាំសប្ដាហ៍:</p>
<table style='break-inside:avoid'><tr><th>វាស់</th><th>ខែនេះ</th><th>ខែមុន</th><th>Backtest</th></tr>
<tr><td>ចំនួន trade</td><td>32</td><td>41</td><td>~30</td></tr>
<tr><td>Win rate</td><td>47%</td><td>39%</td><td>48%</td></tr>
<tr><td>Average R</td><td>+0.22R</td><td>−0.08R</td><td>+0.44R</td></tr>
<tr><td>Max DD</td><td>−5R</td><td>−9R</td><td>−7R</td></tr>
<tr><td>Rule adherence</td><td>84%</td><td>66%</td><td>—</td></tr></table>
<p>បំបែកលទ្ធផលតាម <b>session</b> និងតាម <b>setup</b> ដើម្បីរកកន្លែងដែលអ្នកខ្លាំង និងខ្សោយ:</p>
""" + bars([("Asia", -0.2, DN), ("London", 0.4, UP), ("New York", 0.3, UP), ("ក្បែរព័ត៌មាន", -0.5, DN)], unit="R",
           caption="Average R តាម session ក្នុងមួយខែ (<b>ឧទាហរណ៍</b>) · ជំហានបន្ទាប់: ពិចារណាឈប់ trade Asia និងម៉ោងព័ត៌មាន") + """
<div class='box warn'>⚠️ ក្រុមដែលមានតែ 5–8 trades តូចពេកសម្រាប់សន្និដ្ឋាន (Chapter 35)។ ប្រើវាជា "សញ្ញាឱ្យតាមដាន" មិនមែនជាការសម្រេចចុងក្រោយទេ។</div>
"""),
        ("Identifying Repeated Mistakes: រកកំហុសដដែលៗ", """
<p>ដាក់ <span class='en-term'>tag</span> កំហុសនៅគ្រប់ trade B និង C។ ប្រើបញ្ជីថេរ ដើម្បីរាប់បាន:</p>
<p><span class='en-term'>Early entry</span> · <span class='en-term'>Moved SL</span> · <span class='en-term'>FOMO</span> · <span class='en-term'>Revenge</span> ·
<span class='en-term'>Over-lot</span> · <span class='en-term'>News</span> · <span class='en-term'>Outside hours</span> · <span class='en-term'>Early exit</span></p>
""" + bars([("Early entry", 6, DN), ("FOMO", 4, OR), ("Moved SL", 3, OR), ("News", 2, GOLD), ("Over-lot", 1, GOLD)],
           caption="ចំនួន tag កំហុសក្នុងមួយខែ (<b>ឧទាហរណ៍</b>) · កែកំហុសធំជាងគេមុនសិន") + """
<p>បន្ទាប់មកគណនា<b>ថ្លៃ</b>នៃកំហុស: បូក R នៃ trade ដែលមាន tag នីមួយៗ។ ឧ. "Early entry: 6 trades = −4R"។ លេខនេះធ្វើឱ្យកំហុស<b>មើលឃើញ</b> និងពិបាកមិនអើពើ។</p>
<div class='box ok'>✅ ដំណោះស្រាយគួរតែជា<b>ច្បាប់ជាក់លាក់</b>: "Early entry" → "ចូលតែក្រោយទៀន 15m <b>បិទ</b> បញ្ជាក់"។ "News" → "មិនចូល 15 នាទីមុន/ក្រោយព័ត៌មាន high-impact ក្នុង 📰 News"។</div>
"""),
        ("Measuring Improvement: វាស់ការរីកចម្រើន", """
<p>ការរីកចម្រើនពិតប្រាកដ<b>យឺត</b> ហើយមើលឃើញតែក្នុងរយៈពេលខែ មិនមែនពី trade មួយទៅ trade មួយទេ។ តាមដានពីរប្រភេទ:</p>
<ul><li><b>Process metrics</b> (អ្នកគ្រប់គ្រងបាន): rule adherence % · ចំនួន trade C · ការគោរព max loss/ថ្ងៃ</li>
<li><b>Outcome metrics</b> (អាស្រ័យលើទីផ្សារផង): average R · profit factor · drawdown</li></ul>
""" + twolines([60, 68, 72, 80, 85, 88], [-0.15, -0.05, 0.05, 0.10, 0.08, 0.20], "Rule adherence %", "Average R",
               ca=BL, cb=UP, caption="6 ខែ (<b>ឧទាហរណ៍</b>) · ពេល process ប្រសើរឡើង លទ្ធផលច្រើនតែតាមក្រោយ ប៉ុន្តែមិនមែនរាល់ខែទេ") + """
<table style='break-inside:avoid'><tr><th>ប្រៀបធៀប (ឧទាហរណ៍)</th><th>Average R</th></tr>
<tr><td>Trade grade A</td><td style='color:#34C759'><b>+0.35R</b></td></tr>
<tr><td>Trade grade C</td><td style='color:#FF3B30'><b>−0.60R</b></td></tr></table>
<p>បើ trade A របស់អ្នកមាន average R ល្អជាង trade C យ៉ាងច្បាស់ (ក្រោយ trade គ្រប់គ្រាន់) នោះជា<b>ភស្តុតាង</b>ផ្ទាល់ខ្លួនថា ការធ្វើតាមច្បាប់មានតម្លៃ។</p>
<div class='box warn'>⚠️ ខែខាតមួយមិនមែនមានន័យថាអ្នកមិនរីកចម្រើនទេ។ បើ rule adherence កើនឡើង អ្នកកំពុងទៅផ្លូវត្រូវ ទោះលទ្ធផលខែនោះអវិជ្ជមានក៏ដោយ។</div>
"""),
        ("Journal ជាមួយ XAU.KH", """
<ul><li>📈 <b>Proof</b> ជាគំរូនៃ journal ស្មោះត្រង់: គ្រប់ signal ត្រូវកត់ ទាំងឈ្នះ និងខាត គ្មានការលុប។ Journal របស់អ្នកគួរតែស្មោះត្រង់ដូចគ្នា។</li>
<li>🚨 <b>Signals</b>: បើអ្នកតាម signal ចូរកត់តម្លៃ fill របស់អ្នក និងថាតើអ្នកធ្វើតាម SL/TP ឬអត់។ លទ្ធផលរបស់អ្នកអាចខុសពី Proof ដោយសារការចូលយឺត ឬការបិទមុន។</li>
<li>📒 <b>Journal</b> ក្នុង XAU.KH App (/app) ជួយតាមដាន signal ដូចជាកំណត់ហេតុ។</li>
<li>📰 <b>News</b>: tag trade ដែលនៅក្បែរព័ត៌មានធំ ដើម្បីដឹងថាវាជួយ ឬធ្វើឱ្យខូចលទ្ធផលរបស់អ្នក។</li></ul>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ កត់តែ trade ឈ្នះ ឬលុប trade "ឆ្កួតៗ" ចោល</li>
<li>❌ កត់ត្រាតែលុយ ($) ដោយគ្មាន R · grade · ហេតុផល</li>
<li>❌ កត់ក្រោយច្រើនថ្ងៃ ពេលចងចាំបានបាត់</li>
<li>❌ កត់ប៉ុន្តែមិនដែលពិនិត្យ</li>
<li>❌ កែ 5 ចំណុចក្នុងពេលតែមួយ ដូច្នេះមិនដឹងថាអ្វីជួយ</li>
<li>❌ វាស់ការរីកចម្រើនតែលើលទ្ធផលខែមួយ</li></ul>
"""),
    ],
    summary=["Journal ប្ដូរអារម្មណ៍ឱ្យទៅជាទិន្នន័យ · កត់គ្រប់ trade ភ្លាមៗ",
             "រចនាសម្ព័ន្ធ: ពេល · setup · plan · risk · R · grade · អារម្មណ៍ · រូបមុន/ក្រោយ",
             "Grade ដំណើរការ (A · B · C) មិនមែនលទ្ធផល · C ដែលឈ្នះ គឺគ្រោះថ្នាក់បំផុត",
             "Weekly: រកកំហុសមួយ ហើយកែមួយ · Monthly: លេខ តាម session និង setup",
             "Tag កំហុស គណនាថ្លៃជា R · វាស់ការរីកចម្រើនតាម rule adherence និង average R ប្រចាំខែ"],
    exercise=["បង្កើត journal spreadsheet ដែលមានជួរឈរទាំងអស់ក្នុងផ្នែកទី 2 ហើយកត់ trade 10 ចុងក្រោយរបស់អ្នក (ឬពី MT5 History)។",
              "ដាក់ grade A/B/C និង tag កំហុសសម្រាប់ trade ទាំង 10។ តើកំហុសណាកើតឡើងច្រើនជាងគេ ហើយវាមានថ្លៃប៉ុន្មាន R?",
              "Trade 0.02 lot · SL $8 · TP $20 · ឈ្នះ។ គណនាចំណេញជា $ និងជា R។",
              "ធ្វើ weekly review លើកដំបូងរបស់អ្នកដោយប្រើ 3 សំណួរ ហើយសរសេរគោលដៅមួយសម្រាប់សប្ដាហ៍ក្រោយ។"],
)
