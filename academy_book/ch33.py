from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def revenge_cycle(w=420, h=210, caption=""):
    """The revenge-trading loop drawn as a circle of 5 nodes, with an exit arrow."""
    import math
    nodes = [("ខាត", "SL ប៉ះ", DN), ("ខឹង · អាម៉ាស់", "ចង់យកវិញ", OR), ("Lot ធំជាង", "គ្មាន setup", PU),
             ("ខាតធំជាង", "DD លឿន", DN), ("ខឹងខ្លាំងជាង", "បាត់ផែនការ", OR)]
    cx, cy, RX, RY = 140, 104, 92, 76
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="none" stroke="#E5E5EA" stroke-width="10"/>']
    for i, (t, sub, col) in enumerate(nodes):
        a = -math.pi / 2 + i * 2 * math.pi / len(nodes)
        x, y = cx + RX * math.cos(a), cy + RY * math.sin(a)
        out.append(f'<rect x="{x - 46:.1f}" y="{y - 17:.1f}" width="92" height="34" rx="9" fill="white" stroke="{col}" stroke-width="1.5"/>')
        out.append(f'<text x="{x:.1f}" y="{y - 2:.1f}" text-anchor="middle" fill="{col}" class="bt">{t}</text>')
        out.append(f'<text x="{x:.1f}" y="{y + 11:.1f}" text-anchor="middle" fill="#6E6E73" class="st">{sub}</text>')
    out.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" fill="{DN}" class="lt">↻ Revenge</text>')
    out.append(f'<path d="M{cx + 48},{cy - 80} C 260,20 320,30 345,{cy - 38}" stroke="{UP}" stroke-width="2" fill="none" stroke-dasharray="5 3"/>')
    out.append(f'<path d="M339,{cy - 44} l6,7 l-9,1" stroke="{UP}" stroke-width="2" fill="none"/>')
    out.append(f'<rect x="300" y="{cy - 32}" width="108" height="66" rx="10" fill="{UP}" fill-opacity=".12" stroke="{UP}"/>')
    for k, line in enumerate(["ច្រកចេញ:", "ឈប់ · បិទ MT5", "សរសេរ journal"]):
        out.append(f'<text x="354" y="{cy - 12 + k * 17}" text-anchor="middle" fill="{"#1C1C1E" if k else UP}" class="{"st" if k else "bt"}">{line}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def risk_ladder(w=420, h=150, caption=""):
    """Risk after consecutive losses: 1% -> 0.5% -> stop for the day; a win resets."""
    steps = [("Trade ធម្មតា", "1%", BL, 1.0), ("ខាត 1", "0.5%", OR, 0.5), ("ខាត 2 ជាប់", "ឈប់ថ្ងៃនេះ", DN, 0.0)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    base = h - 34
    for i, (t, r, col, f) in enumerate(steps):
        x = 30 + i * 128
        hh = 14 + f * 70
        out.append(f'<rect x="{x}" y="{base - hh:.1f}" width="96" height="{hh:.1f}" rx="7" fill="{col}" fill-opacity=".22" stroke="{col}"/>')
        out.append(f'<text x="{x + 48}" y="{base - hh - 7:.1f}" text-anchor="middle" fill="{col}" class="lt">{r}</text>')
        out.append(f'<text x="{x + 48}" y="{base + 18}" text-anchor="middle" fill="#1C1C1E" class="st">{t}</text>')
        if i < 2:
            out.append(f'<path d="M{x + 100},{base - 30} l22,0 m-5,-4 l5,4 l-5,4" stroke="#8E8E93" stroke-width="1.6" fill="none"/>')
    out.append(f'<text x="{w - 14}" y="18" text-anchor="end" fill="{UP}" class="st">ឈ្នះ 1 → ត្រឡប់ទៅ 1% វិញ</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=33, part="PART 8 · Risk Management",
    title_km="វិន័យ Risk ជាអាជីព", title_en="Professional Risk Discipline: Losing Streaks · Overtrading · Revenge · Leverage · Correlation",
    intro="""Chapter 32 បានផ្ដល់<b>លេខ</b> (risk % · lot · ដែនកំណត់)។ ជំពូកនេះនិយាយពី<b>មនុស្ស</b>ដែលត្រូវគោរពលេខទាំងនោះ។
គណនីភាគច្រើនមិនបាត់ដោយសារ trade អាក្រក់មួយទេ គឺដោយសារ<b>ប្រតិកម្មអាក្រក់</b>ក្រោយការខាត:
<span class='en-term'>overtrading</span> · <span class='en-term'>revenge trading</span> · <span class='en-term'>overleveraging</span>
និង <span class='en-term'>correlated risk</span> ដែលលាក់ខ្លួន។ យើងនឹងរៀនថាហេតុអ្វី<b>ការខាតជាប់គ្នាជារឿងធម្មតា</b>
និងច្បាប់ច្បាស់លាស់ដើម្បី<b>រក្សាដើមទុន</b> (capital preservation)។""",
    sections=[
        ("Losing Streaks · ការខាតជាប់គ្នាគឺធម្មតា", """
<p>គ្មានប្រព័ន្ធណាឈ្នះ 100% ទេ។ ទោះ win rate ខ្ពស់ ការខាត<b>ជាប់គ្នា</b>នៅតែកើតឡើង ព្រោះលទ្ធផលនៃ trade នីមួយៗ<b>មិនដឹងមុន</b>។
ការខាត 4 ដងជាប់គ្នា <b>មិនមែនមានន័យថា</b>ប្រព័ន្ធខូចទេ។</p>
""" + bars([("Win 40%", 7.9, DN), ("Win 50%", 6.0, OR), ("Win 60%", 4.6, GOLD), ("Win 70%", 3.5, UP)],
           caption="ការខាតជាប់គ្នាវែងបំផុត (មធ្យម) ក្នុង 100 trades · ការគណនាដោយ simulation សន្មតថា trade ឯករាជ្យ (មិនមែនទិន្នន័យពិត)") + """
<div class='box tip'>💡 អានក្រាហ្វ: ប្រព័ន្ធឈ្នះ <b>60%</b> ជាធម្មតានឹងជួបការខាត<b>ប្រហែល 4–5 ដងជាប់គ្នា</b>យ៉ាងហោចណាស់មួយដង ក្នុងរាល់ 100 trades។ ពិនិត្យ 📈 <b>Proof</b> ក្នុង group: អ្នកនឹងឃើញថាការខាតជាប់គ្នាក៏មានដែរ។ នោះជាការពិត មិនមែនការលាក់។</div>
<div class='box ok'>✅ ត្រៀមខ្លួនមុន: សួរខ្លួនឯងថា "បើខ្ញុំខាត <b>8 ដងជាប់គ្នា</b> តើគណនីខ្ញុំនៅសល់ប៉ុន្មាន?" ជាមួយ risk 1% ≈ <b>−7.7%</b> · ជាមួយ 5% ≈ <b>−33.7%</b>។</div>
"""),
        ("Consecutive Losses: ច្បាប់ក្រោយការខាត", """
<p>ការខាតម្ដងៗ មិនមែនជាបញ្ហាទេ។ បញ្ហាគឺ<b>អ្វីដែលអ្នកធ្វើបន្ទាប់</b>។ Trader អាជីពមាន<b>ច្បាប់សរសេររួច</b>សម្រាប់ការខាតជាប់គ្នា:</p>
""" + risk_ladder(caption="ច្បាប់គំរូ: កាត់ risk ពាក់កណ្ដាលក្រោយខាត · ខាត 2 ដងជាប់ = ឈប់ថ្ងៃនោះ") + """
<ul><li><b>ខាត 1</b>: trade បន្ទាប់ risk <b>ពាក់កណ្ដាល</b> (0.5%)</li>
<li><b>ខាត 2 ជាប់</b>: <b>ឈប់សម្រាប់ថ្ងៃនោះ</b> · ពិនិត្យ journal: ខាតដោយសារទីផ្សារ ឬដោយសារខ្ញុំបំពានច្បាប់?</li>
<li><b>ដល់ max weekly loss</b> (Chapter 32): ឈប់រហូតដល់សប្ដាហ៍ក្រោយ</li>
<li>ឈ្នះម្ដង → ត្រឡប់ទៅ risk ធម្មតា (កុំ<b>បង្កើន</b>លើសធម្មតា)</li></ul>
<div class='box tip'>💡 ទំព័រ <b>Scale Up</b> របស់ XAU.KH ប្រើគំនិតដូចគ្នា: ខាត → ត្រឡប់ទៅជំហាន 1 ជាមួយ risk <b>ពាក់កណ្ដាល</b> · ឈ្នះ → risk ត្រឡប់ធម្មតា។</div>
"""),
        ("Overtrading · Trade ច្រើនពេក", """
<p><span class='en-term'>Overtrading</span> គឺ trade ពេល<b>គ្មាន setup</b> ឬ trade ច្រើនជាងផែនការ។ មូលហេតុញឹកញាប់: ធុញ · ចង់ "ធ្វើអ្វីមួយ" · FOMO · ចង់យកការខាតវិញ។</p>
""" + zigzag([50, 62, 44, 58, 40, 60, 46, 56, 42, 54, 30, 70, 88], {1: ("✕", DN), 2: ("✕", DN), 3: ("✕", DN), 4: ("✕", DN), 5: ("✕", DN), 6: ("✕", DN), 10: ("A+", UP)},
             lines=[(64, 0, 9, "range · គ្មានទិស", GR, True), (38, 0, 9, "", GR, True)],
             caption="✕ = entry ក្នុង range ដោយគ្មាន setup (spread + SL តូចៗ ស៊ីគណនី) · A+ = sweep + CHOCH ច្បាស់") + """
<table style='break-inside:avoid'><tr><th>សញ្ញាព្រមាន</th><th>ដំណោះស្រាយ</th></tr>
<tr><td>Trade ច្រើនជាង 3–4 ដង/ថ្ងៃ (លើសផែនការ)</td><td>កំណត់ចំនួន trade អតិបរមាក្នុងមួយថ្ងៃ</td></tr>
<tr><td>Trade ក្រៅ kill zone · ពេល Asia ស្ងាត់</td><td>Trade តែម៉ោងដែលបានគ្រោង (Chapter 16 · 31)</td></tr>
<tr><td>ចូលដោយមិនបាន checklist</td><td>Checklist មុនចុច (Chapter 32)</td></tr>
<tr><td>មើល chart 1m ច្រើនម៉ោងជាប់</td><td>ដាក់ alert ក្នុង MT5 នៅ level · ចាកចេញពីអេក្រង់</td></tr></table>
<div class='box warn'>⚠️ Trade នីមួយៗមានថ្លៃ: <b>spread</b> · commission · និង<b>ថាមពលចិត្ត</b>។ Trade 10 ដងគុណភាពទាប ច្រើនតែអាក្រក់ជាង trade 2 ដងគុណភាពខ្ពស់។</div>
"""),
        ("Revenge Trading · Trade ដើម្បីសងសឹក", """
<p><span class='en-term'>Revenge trading</span> គឺ trade ភ្លាមៗក្រោយការខាត ដើម្បី "យកលុយវិញ" ពីទីផ្សារ។ វាជាមូលហេតុ<b>ធំបំផុតមួយ</b>នៃការបាត់គណនី ព្រោះវាបង្កើត<b>វដ្ដ</b>:</p>
""" + revenge_cycle(caption="វដ្ដ revenge trading · ច្រកចេញតែមួយគឺ ឈប់ មិនមែន trade បន្ថែម") + """
<ul><li>សញ្ញា: បេះដូងលោតញាប់ · ចង់បើក trade <b>ភ្លាម</b> · គិតតែ "ចំនួនលុយ" មិនមែន setup</li>
<li>សញ្ញា: បង្កើន lot · លុប ឬពង្រីក SL · ប្ដូរទៅ timeframe តូចដើម្បីរក entry</li>
<li>ទីផ្សារ<b>មិនដឹង</b>ថាអ្នកខាត ហើយមិនជំពាក់លុយអ្នកទេ</li></ul>
<div class='box ok'>✅ ច្បាប់ <b>15 នាទី</b>: ក្រោយការខាតណាមួយ ក្រោកពីអេក្រង់ 15 នាទី។ ត្រឡប់មកវិញ ហើយសួរ: "តើ setup នេះនឹងខ្ញុំយកដែរ ប្រសិនបើខ្ញុំទើបតែឈ្នះ?" បើមិនមែន → <b>កុំ trade</b>។</div>
"""),
        ("Overleveraging · ប្រើ Leverage ហួសកម្រិត", """
<p><span class='en-term'>Leverage</span> អនុញ្ញាតឱ្យអ្នកបើក position ធំជាងលុយក្នុងគណនី ដោយដាក់តែ <span class='en-term'>margin</span>។ Leverage ខ្ពស់<b>មិនធ្វើឱ្យ risk ធំដោយខ្លួនឯងទេ</b> ប៉ុន្តែវា<b>អនុញ្ញាត</b>ឱ្យអ្នកបើក lot ធំពេក។</p>
<table style='break-inside:avoid'><tr><th>Lot (មាស ~$4,000)</th><th>ទំហំ (notional)</th><th>Margin @ 1:500</th><th>$1 move =</th><th>$20 ប្រឆាំង =</th></tr>
<tr><td>0.01</td><td>1 oz ≈ $4,000</td><td>≈ $8</td><td>$1</td><td>$20</td></tr>
<tr><td>0.10</td><td>10 oz ≈ $40,000</td><td>≈ $80</td><td>$10</td><td>$200</td></tr>
<tr><td>0.50</td><td>50 oz ≈ $200,000</td><td>≈ $400</td><td>$50</td><td>$1,000</td></tr>
<tr><td>1.00</td><td>100 oz ≈ $400,000</td><td>≈ $800</td><td>$100</td><td>$2,000</td></tr></table>
<div class='box warn'>⚠️ គណនី $1,000 អាចបើក 1.00 lot បាន (margin តែ ~$800) ប៉ុន្តែចលនាប្រឆាំង<b>តែ $10</b> (100 pips) ធម្មតាៗ = <b>−$1,000</b> = គណនីបាត់ ឬ <span class='en-term'>stop out</span>។ Margin ដែល broker អនុញ្ញាត <b>មិនមែន</b>ជាទំហំដែលអ្នកគួរប្រើទេ។</div>
<div class='box tip'>💡 កំណត់ lot ដោយ<b>រូបមន្ត risk</b> (Chapter 32) មិនមែនដោយ "margin នៅសល់ប៉ុន្មាន"។ ពិនិត្យ <span class='en-term'>Margin Level</span> ក្នុង tab Trade របស់ MT5: បើវាធ្លាក់ជិត 100% អ្នកកំពុង overleverage។</div>
"""),
        ("Correlated Risk · Risk ដែលលាក់ខ្លួន", """
<p><span class='en-term'>Correlation</span> មានន័យថាផលិតផលពីរ<b>ផ្លាស់ទីទិសដូចគ្នា</b> (ឬផ្ទុយគ្នា)។ បើអ្នកបើក order ច្រើនដែលជាប់ទាក់ទងគ្នា វាដូចជាបើក trade <b>ធំតែមួយ</b>។</p>
""" + bars([("1 Buy XAU", 1, UP), ("3 Buy XAU", 3, OR), ("Buy XAU+XAG", 2, GOLD), ("Buy XAU+Sell USD", 2, PU)], unit="%",
           caption="Risk សរុបពិត បើ order នីមួយៗ risk 1% · order ដែលជាប់ទាក់ទងគ្នា បូក risk ចូលគ្នា") + """
<ul><li><b>3 order ទិញមាស</b> ក្នុងតំបន់ដូចគ្នា = risk <b>3%</b> មិនមែន 1% ទេ · បើ SL ប៉ះ វាប៉ះទាំងអស់ក្នុងពេលតែមួយ</li>
<li><b>មាស (XAU) និងប្រាក់ (XAG)</b> ច្រើនតែផ្លាស់ទីទិសដូចគ្នា</li>
<li>មាស ច្រើនតែផ្លាស់ទី<b>ផ្ទុយ</b>ពី USD (Chapter 2): ទិញ XAUUSD + លក់ USD លើគូផ្សេង (ឧ. លក់ USDJPY) = ភ្នាល់ "USD ចុះ" <b>ពីរដង</b> · មិនមែនការ "បែងចែក" risk ទេ</li>
<li>ច្បាប់: <b>Risk សរុបនៃ trade ដែលបើកទាំងអស់</b> ≤ max daily loss (ឧ. 2–3%)</li></ul>
<div class='box tip'>💡 ចង់បន្ថែម position (scale in)? បន្ថែមតែក្រោយពេល trade ទី 1 មាន <b>SL នៅ breakeven</b> ដូច្នេះ risk សរុបមិនកើន (Chapter 30)។</div>
"""),
        ("Capital Preservation · រក្សាដើមទុនជាមុន", """
<p>Trader ដែលនៅរស់យូរ គឺអ្នកដែលចាត់ទុក<b>ដើមទុន</b>ជាឧបករណ៍ការងារ។ គ្មានដើមទុន = គ្មានឱកាស។ ទោះអ្នករៀនកាន់តែពូកែ ក៏គ្មានប្រយោជន៍ដែរ បើគណនីបាត់មុន។</p>
""" + flow([("នៅរស់", "DD តូច", UP), ("Trade បន្ត", "ទិន្នន័យច្រើន", BL), ("រៀន · កែ", "journal", GOLD), ("ប្រសើរឡើង", "បន្តិចម្ដងៗ", PU)],
           caption="Capital preservation → អ្នកមានពេលគ្រប់គ្រាន់ដើម្បីពូកែ") + """
<table style='break-inside:avoid'><tr><th>គំនិតអ្នកលេង</th><th>គំនិតអាជីព</th></tr>
<tr><td>"ថ្ងៃនេះត្រូវរកបាន $100"</td><td>"ថ្ងៃនេះត្រូវ trade តាមច្បាប់"</td></tr>
<tr><td>"ខាតហើយ ត្រូវយកវិញថ្ងៃនេះ"</td><td>"ការខាតនេះស្ថិតក្នុង plan · ស្អែកមានឱកាសថ្មី"</td></tr>
<tr><td>"Setup នេះច្បាស់ណាស់ ដាក់ lot ធំ"</td><td>"Risk ដូចគ្នាគ្រប់ trade · ខ្ញុំមិនដឹងលទ្ធផលមុន"</td></tr>
<tr><td>"មិន trade = ខាតឱកាស"</td><td>"មិន trade = ការពារដើមទុន"</td></tr></table>
"""),
        ("ច្បាប់ផ្ទាល់ខ្លួន: Risk Rules Card", """
<p>សរសេរច្បាប់ទាំងនេះលើក្រដាស ហើយដាក់ក្បែរអេក្រង់ ឬ pin ក្នុងទូរស័ព្ទ។ ច្បាប់ដែល<b>សរសេររួច</b> ងាយគោរពជាងច្បាប់ក្នុងក្បាល។</p>
<table style='break-inside:avoid'><tr><th>ច្បាប់</th><th>គំរូ (កែតាមខ្លួនឯង)</th></tr>
<tr><td>Risk / trade</td><td>1% (0.5% ក្រោយខាត)</td></tr>
<tr><td>Trade អតិបរមា / ថ្ងៃ</td><td>3</td></tr>
<tr><td>ខាតជាប់គ្នា</td><td>2 ដង → ឈប់ថ្ងៃនោះ</td></tr>
<tr><td>Max daily / weekly loss</td><td>3% / 6%</td></tr>
<tr><td>Risk សរុប trade បើក</td><td>≤ 2%</td></tr>
<tr><td>ព័ត៌មានធំ</td><td>⛔ 15 នាទីមុន/ក្រោយ (📰 News)</td></tr>
<tr><td>ក្រោយខាត</td><td>ក្រោកពីអេក្រង់ 15 នាទី</td></tr>
<tr><td>Drawdown 10%</td><td>ឈប់ 1 សប្ដាហ៍ · ពិនិត្យប្រព័ន្ធ · demo</td></tr></table>
<div class='box ok'>✅ ច្បាប់ល្អបំផុត គឺច្បាប់ដែលអ្នក<b>គោរពបាន 100%</b>។ ច្បាប់តឹងពេក ដែលអ្នកបំពានរាល់សប្ដាហ៍ អាក្រក់ជាងច្បាប់សាមញ្ញ ដែលអ្នកគោរពជានិច្ច។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ គិតថាការខាត 3–4 ដងជាប់ = ប្រព័ន្ធខូច ហើយប្ដូរវិធីសាស្ត្ររាល់សប្ដាហ៍</li>
<li>❌ Trade បន្តក្រោយដល់ max daily loss "ម្ដងទៀតចុងក្រោយ"</li>
<li>❌ បង្កើន lot ទ្វេដងក្រោយខាត (martingale) ដើម្បីយកវិញ</li>
<li>❌ បើក 3–4 order មាសក្នុងតំបន់តែមួយ ហើយគិតថា risk នៅតែ 1%</li>
<li>❌ ប្រើ lot ធំព្រោះ "margin នៅសល់ច្រើន"</li>
<li>❌ Trade ពេលហត់ ខឹង ឬមានបញ្ហាផ្ទាល់ខ្លួន</li>
<li>❌ មិនកត់ journal ដូច្នេះមិនដឹងថាខាតដោយសារទីផ្សារ ឬដោយសារវិន័យ</li></ul>
"""),
    ],
    summary=["ការខាតជាប់គ្នាគឺធម្មតា · ត្រៀមច្បាប់មុនវាកើត",
             "ខាត 1 → risk ពាក់កណ្ដាល · ខាត 2 ជាប់ → ឈប់ថ្ងៃនោះ",
             "Overtrading និង revenge trading = trade ដោយអារម្មណ៍ មិនមែនដោយ setup",
             "Leverage អនុញ្ញាត lot ធំ ប៉ុន្តែ lot ត្រូវកំណត់ដោយរូបមន្ត risk",
             "Order ដែលជាប់ទាក់ទងគ្នា បូក risk ចូលគ្នា · ដើមទុនជាមុន ចំណេញជាក្រោយ"],
    exercise=["ពិនិត្យ journal ឬ history ក្នុង MT5 របស់អ្នក: តើការខាតជាប់គ្នាវែងបំផុតគឺប៉ុន្មានដង? ក្រោយវា អ្នកបានធ្វើអ្វី?",
              "អ្នកមាន order ទិញមាស 2 (risk 1% ម្នាក់) ហើយឃើញ setup ទិញទី 3។ Risk សរុបជាប៉ុន្មាន? អ្នកគួរធ្វើអ្វី?",
              "គណនី $2,000 · leverage 1:500។ គណនា margin និងការខាត ប្រសិនបើបើក 0.50 lot ហើយតម្លៃទៅប្រឆាំង $15។ វាជាប៉ុន្មាន % នៃគណនី?",
              "សរសេរ <b>Risk Rules Card</b> ផ្ទាល់ខ្លួនរបស់អ្នក (8 ជួរ) ហើយ pin វាក្នុងទូរស័ព្ទ។"],
)
