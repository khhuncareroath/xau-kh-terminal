from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def dealing_range(w=420, h=210, caption=""):
    """Dealing range box: premium (top half), EQ 50%, discount (bottom half), with a price path inside."""
    x0, x1, top, bot = 60, w - 20, 26, h - 26
    mid = (top + bot) / 2
    pts = [(x0, bot - 4), (x0 + 50, top + 4), (x0 + 95, mid + 30), (x0 + 140, top + 34), (x0 + 190, bot - 30), (x0 + 240, mid - 12), (x0 + 290, bot - 50)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.0f},{y:.0f}" for i, (x, y) in enumerate(pts))
    return "".join([
        '<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
        f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{mid - top}" fill="{DN}" fill-opacity=".08"/>',
        f'<rect x="{x0}" y="{mid}" width="{x1 - x0}" height="{bot - mid}" fill="{UP}" fill-opacity=".08"/>',
        f'<line x1="{x0}" x2="{x1}" y1="{top}" y2="{top}" stroke="{DN}" stroke-width="1.6"/>',
        f'<line x1="{x0}" x2="{x1}" y1="{bot}" y2="{bot}" stroke="{UP}" stroke-width="1.6"/>',
        f'<line x1="{x0}" x2="{x1}" y1="{mid}" y2="{mid}" stroke="{GR}" stroke-width="1.4" stroke-dasharray="5 4"/>',
        f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>',
        f'<text x="{x0 - 6}" y="{top + 4}" text-anchor="end" fill="{DN}" class="lt">4,060</text>',
        f'<text x="{x0 - 6}" y="{mid + 4}" text-anchor="end" fill="{GR}" class="lt">4,030</text>',
        f'<text x="{x0 - 6}" y="{bot + 4}" text-anchor="end" fill="{UP}" class="lt">4,000</text>',
        f'<text x="{x1 - 6}" y="{top + 16}" text-anchor="end" fill="{DN}" class="bt">Premium (ថ្លៃ)</text>',
        f'<text x="{x1 - 6}" y="{mid - 6}" text-anchor="end" fill="{GR}" class="lt">EQ 50%</text>',
        f'<text x="{x1 - 6}" y="{bot - 8}" text-anchor="end" fill="{UP}" class="bt">Discount (ថោក)</text>',
        f'<text x="{x0 + 50}" y="{top - 7}" text-anchor="middle" fill="{DN}" class="lt">Swing High</text>',
        f'<text x="{x0 + 4}" y="{bot + 16}" text-anchor="start" fill="{UP}" class="lt">Swing Low</text>',
        "</svg>", f'<div class="cap">{caption}</div>' if caption else "", "</div>"])


CH = dict(
    ch=11, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="មូលដ្ឋានគ្រឹះ ICT", title_en="ICT Foundations: Liquidity · Dealing Range · Context",
    intro="""ចាប់ពីជំពូកនេះ យើងចូលដល់ <b>PART 3: ICT</b>។ ICT គឺជារបៀបមើលទីផ្សារតាមរយៈ <b>liquidity</b>: កន្លែងដែល orders និង
Stop Loss របស់មនុស្សច្រើនកំពុងដេក។ គំនិតនេះពន្យល់ថា <b>ហេតុអ្វី</b>បានជាតម្លៃមាសឆ្លង high ចាស់បន្តិច ហើយធ្លាក់ភ្លាម
ឬធ្លាក់ក្រោម support ហើយឡើងវិញ។ ជំពូកនេះជា<b>ផែនទី</b>សម្រាប់ PART 3 ទាំងមូល: អ្នកនឹងរៀនពាក្យមូលដ្ឋាន
របៀបគូរ <span class='en-term'>dealing range</span> និងការយល់ខុសដែលអ្នកចាប់ផ្ដើមជាច្រើនធ្លាក់ចូល។""",
    sections=[
        ("ICT គឺជាអ្វី?", """
<p><span class='en-term'>ICT</span> មកពីឈ្មោះ <b>Inner Circle Trader</b> ដែលជាឈ្មោះរបស់គ្រូបង្រៀន trading អាមេរិកម្នាក់ (Michael J. Huddleston)
ដែលបានចែករំលែកគំនិតរបស់គាត់ជាសាធារណៈតាមអ៊ីនធឺណិត។ ICT មិនមែនជា indicator ឬ robot ទេ។ វាជា<b>ក្របខ័ណ្ឌគិត</b> (framework) ដែលសួរថា:</p>
<ul><li><b>កន្លែងណា</b>មាន liquidity? (Stop Loss និង pending orders នៅលើ high និងក្រោម low)</li>
<li>តម្លៃទំនងជារត់ទៅរក liquidity <b>ណាមុន</b>?</li>
<li>តើតម្លៃនៅ<b>ថ្លៃ</b> (premium) ឬ<b>ថោក</b> (discount) ក្នុង range បច្ចុប្បន្ន?</li>
<li>តើ<b>ម៉ោង</b>ណាដែលចលនាពិតច្រើនកើតឡើង? (Chapter 16)</li></ul>
<div class='box tip'>💡 ពាក្យជាច្រើនដែលអ្នកឃើញលើរូប 📊 Analysis របស់ XAU.KH ដូចជា <b>ELQ, ILQ, $$, EQ 50%, FVG, OB</b> សុទ្ធតែមកពីភាសា ICT។
បន្ទាប់ពី PART 3 អ្នកនឹងអានរូបទាំងនោះបានគ្រប់បន្ទាត់។</div>
"""),
        ("គំនិតស្ថាប័ន (Institutional Trading)", """
<p>ធនាគារ និងមូលនិធិធំៗ (Chapter 2) ត្រូវការទិញ ឬលក់មាស<b>ច្រើនណាស់</b>។ ពួកគេមិនអាចចុចទិញ 5,000 lot ភ្លាមៗបានទេ ព្រោះ
វានឹងរុញតម្លៃឡើងខ្លាំងមុនពួកគេទិញគ្រប់។ ពួកគេត្រូវការ<b>អ្នកលក់ច្រើន</b>នៅពេលតែមួយ: នោះហើយជា <span class='en-term'>liquidity</span>។</p>
""" + flow([("Retail ដាក់ SL", "ក្រោម low ច្បាស់", GR), ("តម្លៃធ្លាក់ទៅ", "ប៉ះ SL ទាំងនោះ", DN),
            ("SL = Sell", "អ្នកធំទិញបាន", BL), ("តម្លៃឡើង", "ទិសពិត", UP)],
           caption="គំនិត ICT: Stop Loss របស់អ្នកទិញ (sell orders) ផ្ដល់ liquidity ឱ្យអ្នកធំ BUY") + """
<ul><li>Stop Loss របស់អ្នក <b>BUY</b> = ការ<b>លក់</b>ពេលវាប៉ះ · Stop Loss របស់អ្នក <b>SELL</b> = ការ<b>ទិញ</b>ពេលវាប៉ះ</li>
<li>ដូច្នេះ កន្លែងដែលមាន SL ច្រើន = កន្លែងដែលអ្នកធំអាចបំពេញ order ធំបាន</li></ul>
<div class='box warn'>⚠️ យើង<b>មិនអាចឃើញ</b> orders របស់ធនាគារដោយផ្ទាល់ទេ។ ICT គឺជា<b>គំរូពន្យល់</b> (model) ដែលជួយឱ្យយើងគិតជាប្រព័ន្ធ មិនមែនជាការដឹងច្បាស់ពីអ្វីដែលអ្នកធំកំពុងធ្វើទេ។</div>
"""),
        ("ការវិភាគផ្អែកលើ Liquidity", """
<p>Liquidity ដេកនៅកន្លែងដែល trader ភាគច្រើនគិតដូចគ្នា:</p>
<ul><li><span class='en-term'>BSL</span> (Buy-side liquidity) = <b>លើ</b> swing high, equal highs, high ថ្ងៃមុន/សប្ដាហ៍មុន</li>
<li><span class='en-term'>SSL</span> (Sell-side liquidity) = <b>ក្រោម</b> swing low, equal lows, low ថ្ងៃមុន/សប្ដាហ៍មុន</li></ul>
""" + zigzag([45, 80, 55, 79, 40, 60, 20, 50, 88, 70], {1: ("EQH", DN), 3: ("EQH", DN), 6: ("SSL", UP), 8: ("Sweep $$", DN)},
            lines=[(80, 1, 7, "BSL $$", DN, True), (20, 4, 9, "SSL $$", UP, True)],
            caption="Equal highs (EQH) = BSL ច្បាស់ · តម្លៃរត់ឡើងបោសយក BSL ($$) ហើយធ្លាក់វិញ") + """
<div class='box tip'>💡 នៅលើរូប Analysis XAU.KH សញ្ញា <b>$$</b> បង្ហាញកន្លែងដែល liquidity ត្រូវបានបោសយករួច (sweep)។ Chapter 12 នឹងពន្យល់ BSL, SSL និង sweep ឱ្យលម្អិត។</div>
"""),
        ("ពី Liquidity មួយ ទៅ Liquidity មួយទៀត: IRL → ERL", """
<p>គំនិតមូលដ្ឋានមួយទៀតរបស់ ICT: តម្លៃដើរពី liquidity <b>ខាងក្នុង</b> range ទៅ liquidity <b>ខាងក្រៅ</b> range ហើយត្រឡប់មកវិញ។</p>
<table style='break-inside:avoid'><tr><th>ពាក្យ</th><th>ពេញ</th><th>ឧទាហរណ៍</th></tr>
<tr><td><b>ERL / ELQ</b></td><td>External Range Liquidity</td><td>Swing high និង swing low ចុង range (BSL/SSL)</td></tr>
<tr><td><b>IRL / ILQ</b></td><td>Internal Range Liquidity</td><td>FVG, OB, internal high/low នៅក្នុង range</td></tr></table>
""" + flow([("IRL", "FVG / OB ខាងក្នុង", OR), ("ERL", "បោស high/low", DN), ("IRL", "ថយមក FVG ថ្មី", OR), ("ERL", "គោលដៅបន្ទាប់", DN)],
           caption="វដ្ត: IRL → ERL → IRL → ERL ...") + """
<div class='box ok'>✅ ការប្រើជាក់ស្ដែង: បើតម្លៃទើបបោស ERL ខាងលើ (high ចាស់) គោលដៅបន្ទាប់ទំនងជា IRL ខាងក្រោម (FVG)។ បើតម្លៃទើបប៉ះ FVG ក្នុង discount គោលដៅទំនងជា ERL ខាងលើ។ "ទំនង" មិនមែន "ច្បាស់" ទេ។</div>
"""),
        ("Dealing Range: ចន្លោះដែលតម្លៃកំពុងដើរ", """
<p><span class='en-term'>Dealing range</span> គឺជាចន្លោះរវាង <b>swing high</b> និង <b>swing low</b> សំខាន់ ដែលតម្លៃកំពុងដើរនៅក្នុង។
ពាក់កណ្ដាលរបស់វា (<span class='en-term'>Equilibrium, EQ 50%</span>) ចែក range ជាពីរ:</p>
""" + dealing_range(caption="Dealing range 4,000 – 4,060 · EQ = 4,030") + """
<ul><li><span class='en-term'>Premium</span> (ពាក់កណ្ដាលលើ) = តម្លៃ<b>ថ្លៃ</b> → កន្លែងល្អសម្រាប់គិត <b>SELL</b></li>
<li><span class='en-term'>Discount</span> (ពាក់កណ្ដាលក្រោម) = តម្លៃ<b>ថោក</b> → កន្លែងល្អសម្រាប់គិត <b>BUY</b></li>
<li>រូបមន្ត EQ: (High + Low) ÷ 2 → (4,060 + 4,000) ÷ 2 = <b>4,030</b></li></ul>
<div class='box tip'>💡 ដូចការទិញទំនិញ: អ្នកចង់ទិញពេល<b>បញ្ចុះតម្លៃ</b> មិនមែនពេលថ្លៃបំផុតទេ។ BUY ក្នុង discount និង SELL ក្នុង premium។ Chapter 15 នឹងពន្យល់លម្អិត។
រូប 📊 Analysis របស់ XAU.KH គូរប្រអប់ dealing range និងបន្ទាត់ <b>EQ 50%</b> ឱ្យរួចជាស្រេច។</div>
"""),
        ("របៀបគូរ Dealing Range", """
""" + flow([("ជ្រើស TF", "4H ឬ 1H", BL), ("រក swing", "high + low បញ្ជាក់រួច", OR), ("គូរប្រអប់", "high → low", GR), ("ដាក់ EQ", "50%", GOLD)],
           caption="4 ជំហាន គូរ dealing range") + """
<ul><li>ប្រើ swing ដែល<b>បានបញ្ជាក់រួច</b> (Chapter 9) ហើយដែលនាំទៅដល់ BOS ចុងក្រោយ</li>
<li>ក្នុង uptrend: ពី <b>swing low</b> ដែលចាប់ផ្ដើម impulse ទៅ <b>swing high</b> ថ្មីបំផុត</li>
<li>ក្នុង downtrend: ពី <b>swing high</b> ដែលចាប់ផ្ដើម impulse ទៅ <b>swing low</b> ថ្មីបំផុត</li>
<li>ពេលតម្លៃបិទហួសចុង range (BOS) → គូរ range <b>ថ្មី</b></li></ul>
<div class='box warn'>⚠️ Range លើ 5m និង range លើ 4H អាចផ្ទុយគ្នា។ តម្លៃអាចនៅ discount លើ 5m ប៉ុន្តែនៅ premium លើ 4H។ ចាប់ផ្ដើមពី <b>HTF</b> (Chapter 6)។</div>
"""),
        ("ពាក្យ ICT ដែលអ្នកនឹងរៀនបន្ទាប់", """
<table style='break-inside:avoid'><tr><th>ពាក្យ</th><th>អត្ថន័យខ្លី</th><th>ជំពូក</th></tr>
<tr><td><b>BSL / SSL</b></td><td>Liquidity លើ high / ក្រោម low</td><td>12</td></tr>
<tr><td><b>Sweep ($$)</b></td><td>តម្លៃបោសយក liquidity ហើយត្រឡប់</td><td>12</td></tr>
<tr><td><b>FVG</b></td><td>ចន្លោះតម្លៃដែល displacement ទុកនៅពីក្រោយ</td><td>13</td></tr>
<tr><td><b>Order Block (OB)</b></td><td>ទៀនចុងក្រោយមុន displacement</td><td>14</td></tr>
<tr><td><b>Premium / Discount</b></td><td>ពាក់កណ្ដាលលើ / ក្រោម dealing range</td><td>15</td></tr>
<tr><td><b>Killzones</b></td><td>ម៉ោងដែលចលនាសំខាន់ៗច្រើនកើត</td><td>16</td></tr></table>
"""),
        ("ការយល់ខុសទូទៅអំពី ICT", """
<table style='break-inside:avoid'><tr><th>❌ ការយល់ខុស</th><th>✅ ការពិត</th></tr>
<tr><td>"អ្នកធំបោកយើងគ្រប់ចលនា"</td><td>ចលនាជាច្រើនគ្រាន់តែជាការទិញលក់ធម្មតា។ Sweep មានពិត ប៉ុន្តែមិនមែនគ្រប់ wick ទេ។</td></tr>
<tr><td>"OB/FVG គ្រប់កន្លែងដំណើរការ"</td><td>OB និង FVG ច្រើនត្រូវបំបែក។ ពួកវាមានន័យតែនៅក្នុង <b>context</b> (HTF + liquidity + ម៉ោង)។</td></tr>
<tr><td>"ICT ឈ្នះ 90%"</td><td>គ្មានវិធីណាឈ្នះរហូតទេ។ លទ្ធផលអាស្រ័យលើវិន័យ និងការគ្រប់គ្រង risk។</td></tr>
<tr><td>"គូរប្រអប់កាន់តែច្រើន កាន់តែល្អ"</td><td>Chart ពេញដោយប្រអប់ ធ្វើឱ្យច្រឡំ។ Level <b>2–3</b> ដែលសំខាន់ គ្រប់គ្រាន់។</td></tr>
<tr><td>"ICT ជំនួស structure"</td><td>ICT ឈរលើ structure (Chapter 9) និង price action (Chapter 10)។</td></tr></table>
<div class='box warn'>⚠️ XAU.KH បានសាកល្បងលើមាស: ការចូល <b>OB តែឯង ជាមួយ SL តូច</b> មិនបានផ្ដល់លទ្ធផលល្អទេ។ យើងប្រើ ICT ជាចម្បងសម្រាប់ <b>analysis និង context</b>
(កន្លែងណាជា liquidity, តម្លៃនៅ premium ឬ discount) ហើយបញ្ជាក់ entry ជាមួយ structure និង volume។</div>
"""),
        ("ICT ល្អ = Context", """
<p>មុននឹងប្រើ setup ICT ណាមួយ សួរខ្លួនឯង 4 សំណួរ:</p>
<ol><li><b>HTF bias</b>: 4H / Daily ឡើង ឬធ្លាក់?</li>
<li><b>Liquidity</b>: liquidity ណាត្រូវបានបោសរួច ហើយមួយណាជាគោលដៅបន្ទាប់?</li>
<li><b>Dealing range</b>: តម្លៃនៅ premium ឬ discount?</li>
<li><b>ម៉ោង</b>: តើឥឡូវជា London / New York ឬម៉ោងស្ងាត់?</li></ol>
<div class='box ok'>✅ បើចម្លើយទាំង 4 ស្របគ្នា setup មានគុណភាពខ្ពស់ជាង។ បើវាផ្ទុយគ្នា ការ<b>មិន trade</b> ជាជម្រើសល្អ។
វាយ <b>/check</b> ក្នុង group ដើម្បីមើល bias និង level បច្ចុប្បន្ន ហើយមើលការព្រមាន 📰 News មុនម៉ោងព័ត៌មាន។</div>
"""),
    ],
    summary=["ICT = ក្របខ័ណ្ឌមើលទីផ្សារតាម liquidity មិនមែន indicator",
             "Stop Loss និង orders ដេកលើ high (BSL) និងក្រោម low (SSL)",
             "តម្លៃច្រើនតែដើរពី IRL (FVG/OB) ទៅ ERL (high/low) ហើយត្រឡប់",
             "Dealing range: BUY ក្នុង discount · SELL ក្នុង premium · EQ = 50%",
             "ICT ល្អ = context (HTF + liquidity + range + ម៉ោង) មិនមែនប្រអប់ច្រើន"],
    exercise=["គូរ dealing range លើ chart មាស 4H ហើយគណនា EQ 50%។",
              "តើតម្លៃឥឡូវនៅ premium ឬ discount នៃ range នោះ?",
              "សម្គាល់ BSL និង SSL ដែលជិតតម្លៃបំផុត។ មួយណាទំនងជាគោលដៅមុន?",
              "ប្រៀបធៀបជាមួយ dealing range លើរូប 📊 Analysis ថ្ងៃនេះ។"],
)
