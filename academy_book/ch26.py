from academy_pdf import zigzag, flow, bars, twolines

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def pd_box(w=420, h=170, caption=""):
    """Dealing range split into premium (top) and discount (bottom) with what each bias looks for."""
    x, y, bw, bh = 24, 14, 150, h - 28
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{x}" y="{y}" width="{bw}" height="{bh / 2}" fill="{DN}" fill-opacity=".10" stroke="{DN}" stroke-width="1.2"/>',
           f'<rect x="{x}" y="{y + bh / 2}" width="{bw}" height="{bh / 2}" fill="{UP}" fill-opacity=".10" stroke="{UP}" stroke-width="1.2"/>',
           f'<line x1="{x}" x2="{x + bw}" y1="{y + bh / 2}" y2="{y + bh / 2}" stroke="#1C1C1E" stroke-width="1.6" stroke-dasharray="5 4"/>',
           f'<text x="{x + bw / 2}" y="{y + 28}" text-anchor="middle" fill="{DN}" class="pt">PREMIUM</text>',
           f'<text x="{x + bw / 2}" y="{y + 46}" text-anchor="middle" fill="#6E6E73" class="st">តំបន់ថ្លៃ</text>',
           f'<text x="{x + bw + 10}" y="{y + bh / 2 + 4}" fill="#1C1C1E" class="lt">EQ 50% (equilibrium)</text>',
           f'<text x="{x + bw / 2}" y="{y + bh / 2 + 30}" text-anchor="middle" fill="{UP}" class="pt">DISCOUNT</text>',
           f'<text x="{x + bw / 2}" y="{y + bh / 2 + 48}" text-anchor="middle" fill="#6E6E73" class="st">តំបន់ថោក</text>',
           f'<text x="{x + bw + 10}" y="{y + 10}" fill="#1C1C1E" class="lt">Range high (swing high)</text>',
           f'<text x="{x + bw + 10}" y="{y + bh}" fill="#1C1C1E" class="lt">Range low (swing low)</text>',
           f'<text x="{x + bw + 14}" y="{y + 40}" fill="{DN}" class="bt">Bias ចុះ → រកលក់នៅទីនេះ</text>',
           f'<text x="{x + bw + 14}" y="{y + bh / 2 + 40}" fill="{UP}" class="bt">Bias ឡើង → រកទិញនៅទីនេះ</text>',
           "</svg>"]
    return _wrap("".join(out), caption)


def profile_ctx(w=420, h=200, caption=""):
    """Yesterday's volume profile (left) with VAH / POC / VAL and three places today's price can be: A above, B inside, C below."""
    vals = [8, 12, 18, 30, 46, 62, 80, 96, 84, 66, 50, 36, 24, 16, 10, 6]
    top, bot = 14, h - 14
    rh = (bot - top) / len(vals)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, v in enumerate(vals):
        inside = 4 <= i <= 11
        col = BL if inside else "#C7C7CC"
        if i == 7:
            col = GOLD
        out.append(f'<rect x="16" y="{top + i * rh + 1:.1f}" width="{v * 1.1:.1f}" height="{rh - 2:.1f}" rx="2" fill="{col}" fill-opacity="{.85 if i == 7 else .55}"/>')
    for i, t, c in [(4, "VAH", DN), (7.5, "POC", GOLD), (12, "VAL", UP)]:
        yy = top + i * rh
        out.append(f'<line x1="16" x2="{w - 16}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{c}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        out.append(f'<text x="140" y="{yy - 4:.1f}" fill="{c}" class="lt">{t}</text>')
    marks = [(2, "A", "លើ VAH និងនៅលើ = ទទួលយកតម្លៃខ្ពស់", UP), (9.5, "B", "ក្នុង Value Area = តុល្យភាព", GR),
             (13.6, "C", "ក្រោម VAL និងនៅក្រោម = ទទួលយកតម្លៃទាប", DN)]
    for i, k, t, c in marks:
        yy = top + i * rh
        out.append(f'<circle cx="200" cy="{yy:.1f}" r="9" fill="{c}"/><text x="200" y="{yy + 4:.1f}" text-anchor="middle" fill="white" class="lt">{k}</text>')
        out.append(f'<text x="216" y="{yy + 4:.1f}" fill="#1C1C1E" class="st">{t}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def outcomes(w=420, h=132, caption=""):
    """The three possible answers of the bias routine."""
    cards = [("Bullish ↑", "រកតែ buy", "នៅ discount · ក្រោយ sweep SSL", UP),
             ("Neutral ↔", "រង់ចាំ", "ភស្តុតាងផ្ទុយគ្នា · គ្មាន trade", GR),
             ("Bearish ↓", "រកតែ sell", "នៅ premium · ក្រោយ sweep BSL", DN)]
    bw = (w - 20 - 2 * 10) / 3
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, a, b, c) in enumerate(cards):
        x = 10 + i * (bw + 10)
        out.append(f'<rect x="{x:.1f}" y="12" width="{bw:.1f}" height="{h - 24}" rx="12" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="1.4"/>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="40" text-anchor="middle" fill="{c}" class="pt">{t}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="68" text-anchor="middle" fill="#1C1C1E" class="bt">{a}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="92" text-anchor="middle" fill="#6E6E73" class="st">{b.split(" · ")[0]}</text>')
        if " · " in b:
            out.append(f'<text x="{x + bw / 2:.1f}" y="108" text-anchor="middle" fill="#6E6E73" class="st">{b.split(" · ")[1]}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=26, part="PART 6 · Combining the Disciplines",
    title_km="ការបង្កើតទិសដៅទីផ្សារ (Market Bias)", title_en="Building a Market Bias: HTF · Liquidity · Volume Profile · Order Flow",
    intro="""នៅ Part 2 ដល់ Part 5 អ្នកបានរៀនវិធីសាស្ត្របួនដាច់ៗពីគ្នា: <b>Market Structure</b>, <b>ICT</b>, <b>Volume Profile</b> និង <b>Order Flow</b>។
Part 6 នេះ យើងបញ្ចូលវាទាំងអស់ជាប្រព័ន្ធតែមួយ។ ជំហានដំបូងគឺ <span class='en-term'>Market Bias</span>:
ចម្លើយលើសំណួរ <b>"ថ្ងៃនេះ ខ្ញុំគួររក buy ឬ sell?"</b>។ ជំពូកនេះបង្រៀនទម្លាប់មួយជំហានម្ដងៗ ដែលអ្នកអាចធ្វើមុន session នីមួយៗ
ហើយវាផ្ដល់ចម្លើយតែបីប៉ុណ្ណោះ: <b>Bullish</b>, <b>Bearish</b> ឬ <b>Neutral</b> រួមជាមួយ<b>ចំណុចដែលបង្ហាញថា bias ខុស</b>។""",
    sections=[
        ("Bias គឺជាអ្វី និងមិនមែនជាអ្វី", """
<p><span class='en-term'>Bias</span> គឺជាទិសដែលយើង<b>ពេញចិត្ត</b> ផ្អែកលើភស្តុតាង។ វាឆ្លើយសំណួរ "រក buy ឬ sell?"
ប៉ុន្តែវា<b>មិនឆ្លើយ</b>ថា "ចូលនៅតម្លៃណា?" ឬ "ចូលពេលណា?" ទេ។ Bias គ្រាន់តែជាជំហានទី 1 ក្នុងចំណោមជំហានបួន:</p>
""" + flow([("Bias", "ទិសណា?", BL), ("Zone", "កន្លែងណា?", GOLD), ("Setup", "លំនាំអ្វី?", PU), ("Trigger", "ពេលណា?", UP)],
           caption="Bias = ជំហានទី 1 · Entry ត្រូវការជំហានទាំង 4 (Chapter 27–29)") + """
<table style='break-inside:avoid'><tr><th>Bias គឺជា...</th><th>Bias មិនមែនជា...</th></tr>
<tr><td>តម្រង (filter) ដែលកាត់ trade ផ្ទុយទិសខ្លាំង</td><td>សញ្ញាចូល trade ភ្លាមៗ</td></tr>
<tr><td>ផែនទីសម្រាប់ session មួយ ឬថ្ងៃមួយ</td><td>ការទាយដែលត្រូវតែត្រូវ</td></tr>
<tr><td>មានចំណុចខុស (invalidation) ច្បាស់</td><td>អារម្មណ៍ ឬការសង្ឃឹម</td></tr>
<tr><td>អាច "Neutral" បាន</td><td>ត្រូវតែមានទិសរាល់ថ្ងៃ</td></tr></table>
<div class='box tip'>💡 Bias ល្អ ជួយអ្នកពីរយ៉ាង: (1) កុំ trade ប្រឆាំងនឹងទិសខ្លាំង និង (2) <b>នៅក្រៅទីផ្សារ</b> នៅថ្ងៃដែលមិនច្បាស់។ ទាំងពីរនេះការពារដើមទុនបាន ទោះអ្នកមិនទាន់ចូល trade ក៏ដោយ។</div>
"""),
        ("ទិសដៅ Higher Timeframe", """
<p>យើងចាប់ផ្ដើមពី timeframe <b>ធំ</b> ទៅ<b>តូច</b> ជានិច្ច (Top-down · Chapter 6)។ Timeframe ធំមានអ្នកចូលរួមធំៗ (មូលនិធិ ធនាគារ)
ហើយ structure របស់វាត្រូវការពេលយូរដើម្បីប្ដូរ។ ទៀន 5m មួយមិនអាចប្ដូរទិស Daily បានទេ។</p>
""" + flow([("Weekly", "ទិសធំ · PWH/PWL", PU), ("Daily", "bias ថ្ងៃនេះ", BL), ("4H", "zone · range", GOLD), ("1H → 15m", "រង់ចាំ setup", UP)],
           caption="Timeframe នីមួយៗមានតួនាទីរបស់វា · កុំប្រើ 5m ដើម្បីកំណត់ bias") + zigzag(
    [10, 38, 24, 55, 40, 72, 44, 84, 64, 70], {1: ("HH", UP), 2: ("HL", UP), 3: ("HH", UP), 4: ("HL", UP), 5: ("HH", UP), 6: ("HL", UP), 7: ("HH", UP), 8: ("pullback", OR)},
    lines=[(44, 6, 9, "", BL, True)],
    caption="Daily ឡើង (HH · HL) · ចលនាធ្លាក់ចុងក្រោយ = pullback ដរាបណាមិនបិទក្រោម HL ចុងក្រោយ (បន្ទាត់ខៀវ)") + """
<table style='break-inside:avoid'><tr><th>Daily</th><th>4H</th><th>ការអាន</th></tr>
<tr><td>ឡើង</td><td>ឡើង</td><td><b>Bullish ខ្លាំង</b> · រកទិញនៅ pullback</td></tr>
<tr><td>ឡើង</td><td>ធ្លាក់ (pullback)</td><td>Bullish ប៉ុន្តែ<b>រង់ចាំ</b> 4H ត្រឡប់ឡើង (MSS) នៅ discount</td></tr>
<tr><td>ធ្លាក់</td><td>ធ្លាក់</td><td><b>Bearish ខ្លាំង</b> · រកលក់នៅ pullback</td></tr>
<tr><td>Range</td><td>ណាមួយ</td><td><b>Neutral</b> · trade តែគែម range ឬរង់ចាំ breakout</td></tr></table>
<div class='box tip'>💡 ពេល Daily និង 4H ផ្ទុយគ្នា កុំជ្រើសមួយណាដែលអ្នក<b>ចូលចិត្ត</b>។ ចាត់ទុកវាជា pullback ក្នុងទិស Daily
រហូតដល់ Daily បិទទៀនបំបែក HL ឬ LH ចុងក្រោយ (CHOCH · Chapter 9)។</div>
"""),
        ("បរិបទប្រចាំថ្ងៃ និងប្រចាំសប្ដាហ៍", """
<p>ក្រៅពី structure យើងត្រូវដឹង<b>កម្រិតសំខាន់</b>ដែលអ្នក trade ទូទាំងពិភពលោកមើលដូចគ្នា:</p>
<ul><li><span class='en-term'>PWH / PWL</span>: high / low នៃសប្ដាហ៍មុន</li>
<li><span class='en-term'>PDH / PDL</span>: high / low នៃថ្ងៃមុន</li>
<li><span class='en-term'>Weekly open</span>: តម្លៃបើកព្រឹកថ្ងៃច័ន្ទ (ប្រហែល 06:00 ម៉ោងកម្ពុជា winter)</li>
<li><span class='en-term'>Daily open</span> (06:00) និង <span class='en-term'>Midnight open</span> (12:00 ថ្ងៃត្រង់ winter · Chapter 16)</li></ul>
""" + zigzag([45, 60, 50, 68, 56, 44, 52, 40, 48], {},
             lines=[(92, 0, 8, "PWH", PU, True), (72, 0, 8, "PDH", DN, True), (36, 0, 8, "PDL", UP, True), (8, 0, 8, "PWL", PU, True)],
             caption="តម្លៃនៅចន្លោះ PDH–PDL ខាងក្នុងសប្ដាហ៍មុន · គោលដៅជិតបំផុតគឺ PDH ឬ PDL") + """
<table style='break-inside:avoid'><tr><th>សំណួរ</th><th>តម្រុយ Bullish</th><th>តម្រុយ Bearish</th></tr>
<tr><td>ទៀនសប្ដាហ៍មុន</td><td>បិទជិត high</td><td>បិទជិត low</td></tr>
<tr><td>តម្លៃ vs weekly open</td><td>នៅលើ</td><td>នៅក្រោម</td></tr>
<tr><td>ម្សិលមិញនៅ PDH</td><td>បិទលើ PDH (acceptance)</td><td>sweep PDH ហើយបិទចូលវិញ (rejection)</td></tr>
<tr><td>ម្សិលមិញនៅ PDL</td><td>sweep PDL ហើយបិទចូលវិញ</td><td>បិទក្រោម PDL</td></tr></table>
<div class='box ok'>✅ ឧទាហរណ៍: PWH 4,138 · PDH 4,112 · តម្លៃឥឡូវ 4,086 · PDL 4,061 · PWL 4,020។ ទៅ PDH = $26 (<b>260 pips</b>)
ទៅ PDL = $25 (<b>250 pips</b>)។ តម្លៃនៅ<b>កណ្ដាល</b> → កម្រិតតែម្នាក់ឯងមិនផ្ដល់ bias ទេ · ត្រូវមើលជំហានបន្ទាប់ (liquidity)។</div>
"""),
        ("Structure និង Liquidity: តម្លៃចង់ទៅណា?", """
<p>ទីផ្សារផ្លាស់ទីពី liquidity មួយទៅ liquidity មួយ (Chapter 12)។ ដើម្បីរក <span class='en-term'>Draw on Liquidity</span> សួរបីសំណួរ:</p>
<ol><li>Liquidity ខាងណា<b>ទើបតែត្រូវបាន sweep</b>? (ឧ. Asia low ត្រូវបានយកនៅដើម London)</li>
<li>Liquidity ខាងណា<b>នៅរង់ចាំ</b>? (<span class='en-term'>BSL</span> លើ equal highs / PDH · <span class='en-term'>SSL</span> ក្រោម equal lows / PDL)</li>
<li>តម្លៃនៅ <b>premium</b> ឬ <b>discount</b> នៃ dealing range?</li></ol>
""" + zigzag([70, 45, 62, 42, 62, 38, 20, 54, 46, 78], {2: ("EQH", DN), 3: ("SSL", UP), 4: ("EQH", DN), 6: ("Sweep SSL", OR), 9: ("យក BSL", UP)},
             lines=[(62, 1, 8, "BSL", DN, True), (40, 1, 6, "", UP, True)],
             caption="SSL ត្រូវបាន sweep រួច → liquidity ដែលនៅសល់គឺ BSL លើ equal highs = draw on liquidity ឡើង") + pd_box(
    caption="Dealing range: យកពី swing low ទៅ swing high នៃ 4H · EQ 50% បែងចែក premium និង discount (Chapter 15)") + """
<div class='box ok'>✅ រូបភាព bias ឡើងល្អ: HTF ឡើង + SSL <b>ទើបតែ</b> ត្រូវបាន sweep + តម្លៃនៅ <b>discount</b> + BSL នៅខាងលើជាគោលដៅ។</div>
<div class='box warn'>⚠️ បើតម្លៃទើបតែ sweep BSL ហើយនៅ premium ខណៈ HTF ឡើង នោះមិនមែនពេលល្អសម្រាប់ទិញទេ (ទិញថ្លៃ)។ រង់ចាំ pullback ទៅ discount។</div>
"""),
        ("បរិបទ Volume Profile", """
<p>Volume Profile របស់<b>ថ្ងៃមុន</b> ឬ<b>សប្ដាហ៍មុន</b> (Chapter 19–21) ប្រាប់ថាតម្លៃណាដែលទីផ្សារ<b>ទទួលយក</b>។
ទីតាំងរបស់តម្លៃថ្ងៃនេះធៀបនឹង <span class='en-term'>Value Area</span> ផ្ដល់តម្រុយ bias:</p>
""" + profile_ctx(caption="Profile ម្សិលមិញ · ផ្ទៃពណ៌ខៀវ = Value Area (≈70% នៃ volume) · ពណ៌មាស = POC") + """
<table style='break-inside:avoid'><tr><th>ទីតាំងតម្លៃ</th><th>អត្ថន័យ</th><th>ទំនោរ bias</th></tr>
<tr><td>A: លើ VAH ហើយ<b>នៅលើ</b></td><td>ទីផ្សារទទួលយកតម្លៃខ្ពស់ (acceptance)</td><td>Bullish</td></tr>
<tr><td>លើ VAH ប៉ុន្តែ<b>ធ្លាក់ចូល</b> VA វិញ</td><td>Breakout បរាជ័យ (rejection)</td><td>អាចវិលទៅ POC ឬ VAL</td></tr>
<tr><td>B: ក្នុង VA</td><td>តុល្យភាព (balance)</td><td>Neutral · trade គែម VAH/VAL</td></tr>
<tr><td>C: ក្រោម VAL ហើយ<b>នៅក្រោម</b></td><td>ទីផ្សារទទួលយកតម្លៃទាប</td><td>Bearish</td></tr></table>
<div class='box warn'>⚠️ Volume Profile ត្រូវការ <b>volume ពិត</b>។ ក្រុម XAU.KH ប្រើ volume របស់ <b>COMEX gold futures</b> សម្រាប់ VP និង VWAP (Chapter 25)។
Profile ពី tick volume ក្នុង MT5 គ្រាន់តែជាការប៉ាន់ស្មាន ហើយត្រូវគិតពី <span class='en-term'>basis</span> (គម្លាតតម្លៃ GC និង XAUUSD) ផងដែរ។</div>
"""),
        ("Order Flow ជាការបញ្ជាក់", """
<p>Order flow <b>មិនមែន</b>សម្រាប់កំណត់ bias ទេ។ វាជាការ<b>បញ្ជាក់</b> នៅពេលតម្លៃមកដល់កម្រិតដែល bias បានសម្គាល់។
Bias ប្រាប់ថា "<b>កន្លែងណា</b>" · Order flow ប្រាប់ថា "<b>ឥឡូវនេះ</b> មាននរណាម្នាក់ការពារកម្រិតនេះឬទេ?"</p>
""" + twolines([10, 30, 22, 46, 36, 56, 48, 64], [12, 40, 30, 56, 44, 50, 38, 42], "តម្លៃ (GC)", "CVD",
               caption="តម្លៃបង្កើត high ថ្មី ប៉ុន្តែ CVD មិនបង្កើត = ការទិញកំពុងខ្សោយ (delta divergence · Chapter 24) · បញ្ជាក់ bias ចុះនៅ premium") + """
<table style='break-inside:avoid'><tr><th>Bias ឡើង · តម្លៃមកដល់ discount</th><th>សញ្ញា Order Flow</th></tr>
<tr><td>✅ បញ្ជាក់</td><td><span class='en-term'>Absorption</span> (លក់ខ្លាំង ប៉ុន្តែតម្លៃមិនធ្លាក់) · delta ប្ដូរជាវិជ្ជមាន · stacked buy imbalance</td></tr>
<tr><td>❌ ផ្ទុយ</td><td>អ្នកលក់រុញឆ្លងកម្រិតដោយ CVD ធ្លាក់ខ្លាំង ហើយតម្លៃមិនត្រឡប់</td></tr></table>
<div class='box warn'>⚠️ Order flow ពិតសម្រាប់មាស មានតែពី <b>COMEX GC / MGC</b> ប៉ុណ្ណោះ (Chapter 25)។ បើអ្នកគ្មាន feed នោះទេ ប្រើការបញ្ជាក់ដោយ<b>តម្លៃ</b>ជំនួស:
<span class='en-term'>MSS + displacement</span> នៅលើ 5m ឬ 15m។ Order flow ជា layer <b>បន្ថែម</b> មិនមែនជាលក្ខខណ្ឌចាំបាច់ទេ។</div>
"""),
        ("Macro និង 📰 News", """
<p>Technical bias អាចត្រូវបាន<b>លុប</b>ក្នុងរយៈពេលប៉ុន្មាននាទី ដោយព័ត៌មានធំ។ ដូច្នេះមុនសម្រេច bias ត្រូវពិនិត្យ macro:</p>
<table style='break-inside:avoid'><tr><th>កត្តា</th><th>ជាទូទៅល្អសម្រាប់មាស</th><th>ជាទូទៅមិនល្អសម្រាប់មាស</th></tr>
<tr><td>ដុល្លារ (<span class='en-term'>DXY</span>)</td><td>ធ្លាក់</td><td>ឡើង</td></tr>
<tr><td>US 10y yield</td><td>ធ្លាក់</td><td>ឡើង</td></tr>
<tr><td>CPI / NFP ធៀប forecast</td><td>ខ្សោយជាង forecast</td><td>ខ្លាំងជាង forecast</td></tr>
<tr><td>ហានិភ័យ (<span class='en-term'>risk-off</span>, VIX ឡើង)</td><td>ច្រើនតែគាំទ្រមាស</td><td>—</td></tr></table>
<p>ពាក្យ "<b>ជាទូទៅ</b>" សំខាន់ណាស់: ទំនាក់ទំនងទាំងនេះ<b>មិនមែនរាល់ពេល</b>ទេ (Chapter 2)។</p>
<div class='box tip'>💡 ក្នុង group: កាត 🌅 <b>Daily Outlook</b> រៀងរាល់ព្រឹក បង្ហាញ Dollar · 10y yield · VIX, ទំនោរ macro និងព័ត៌មានធំៗថ្ងៃនេះ។
ការប្រកាស 📰 <b>News</b> ប្រាប់មុនព្រឹត្តិការណ៍ ដូច្នេះអ្នកដឹងថាម៉ោងណាត្រូវប្រយ័ត្ន។</div>
<div class='box warn'>⚠️ ប្រហែល 30 នាទីមុន និងក្រោយព័ត៌មាន high-impact (CPI, NFP, FOMC) bias ស្ទើរតែគ្មានន័យ: spread ធំ តម្លៃលោតទាំងសងខាង។ អ្នក trade ជាច្រើននៅក្រៅទីផ្សារ។</div>
"""),
        ("Bullish · Bearish · Neutral", """
<p>ក្រោយពិនិត្យគ្រប់ជំហាន អ្នកសម្រេចបានតែចម្លើយមួយក្នុងចំណោមបី:</p>
""" + outcomes(caption="Neutral ក៏ជាចម្លើយត្រឹមត្រូវ · \"គ្មាន trade\" ក៏ជា position មួយដែរ") + """
<p>វិធីងាយមួយ គឺដាក់ពិន្ទុ <b>+1</b> (ឡើង), <b>−1</b> (ចុះ) ឬ <b>0</b> (មិនច្បាស់) ឱ្យកត្តានីមួយៗ:</p>
""" + bars([("Daily", 1, UP), ("4H", 1, UP), ("Liquidity", 1, UP), ("P/D", 0, GR), ("VP", 1, UP), ("Macro", -1, DN)],
           caption="ឧទាហរណ៍សម្រាប់ពន្យល់ (មិនមែនទិន្នន័យពិត): សរុប +3 → Bullish · Macro ផ្ទុយ → lot តូច ឬរង់ចាំព័ត៌មានចប់") + """
<table style='break-inside:avoid'><tr><th>លទ្ធផល</th><th>ការសម្រេច</th></tr>
<tr><td>HTF ស្រប + ពិន្ទុវិជ្ជមានច្បាស់</td><td><b>Bullish</b> · រកតែ buy</td></tr>
<tr><td>HTF ស្រប + ពិន្ទុអវិជ្ជមានច្បាស់</td><td><b>Bearish</b> · រកតែ sell</td></tr>
<tr><td>ពិន្ទុជិត 0 ឬ HTF ផ្ទុយកត្តាផ្សេង</td><td><b>Neutral</b> · រង់ចាំ</td></tr></table>
<div class='box tip'>💡 ពិន្ទុនេះជា<b>ឧបករណ៍គិត</b> មិនមែនរូបមន្តវេទមន្តទេ។ ជំពូកបន្ទាប់ (Chapter 27) បង្ហាញពីរបៀបជៀសវាងការរាប់ភស្តុតាងតែមួយពីរដង។</div>
"""),
        ("Worksheet: Bias មួយទំព័រ និង Invalidation", """
<p>សរសេរ bias របស់អ្នក<b>មុន</b> session ចាប់ផ្ដើម (ឧ. មុន London 14:00 winter)។ ការសរសេរការពារអ្នកពីការប្ដូរគំនិតតាមអារម្មណ៍។</p>
""" + flow([("HTF", "W · D · 4H", BL), ("Levels", "PWH · PDH · PDL", GOLD), ("Liquidity", "sweep ខាងណា?", OR),
            ("Value", "VAH · POC · VAL", PU), ("Macro", "DXY · 📰", DN), ("Bias", "+ invalidation", UP)],
           caption="ជំហាន 6 នៃ worksheet · ប្រើពេល 10–15 នាទី មុន session") + """
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>ឧទាហរណ៍ (សម្រាប់ពន្យល់)</th></tr>
<tr><td>HTF</td><td>Daily HH · HL · 4H pullback មកដល់ discount</td></tr>
<tr><td>Levels</td><td>PDH 4,112 · PDL 4,061</td></tr>
<tr><td>Liquidity</td><td>Asia low 4,071 ត្រូវបាន sweep នៅដើម London · BSL នៅ PDH</td></tr>
<tr><td>Value</td><td>VAL ម្សិលមិញ 4,068 · តម្លៃត្រឡប់ចូល VA វិញ</td></tr>
<tr><td>Macro</td><td>DXY នៅស្ងៀម · ព័ត៌មានធំនៅម៉ោង 20:30</td></tr>
<tr><td><b>Bias</b></td><td><b>Bullish</b> លើ 4,058 · ខុស ពេល 4H បិទក្រោម 4,058 · គោលដៅ PDH 4,112</td></tr></table>
<p>ពី 4,080 ទៅ 4,112 = $32 = <b>320 pips</b> · ជាមួយ 0.01 lot ស្មើនឹង <b>$32</b>។ ប៉ុន្តែនេះជា<b>គោលដៅ</b> មិនមែនការសន្យាទេ។</p>
<p><b>ពេលណាត្រូវប្ដូរ bias?</b> (1) តម្លៃប៉ះចំណុច invalidation (2) ព័ត៌មានធំប្ដូររូបភាព (3) HTF បង្កើត CHOCH ពិតប្រាកដ។
<b>កុំ</b>ប្ដូរដោយសារទៀន 5m តែមួយ។</p>
<div class='box warn'>⚠️ <b>ស្មោះត្រង់ជាមួយលេខ:</b> ដូចបានបង្ហាញក្នុង Chapter 16 XAU.KH បានសាកល្បង bias top-down (D / 4H / 1H) លើការប្រកាស session 1,405 ដង
ហើយវាត្រូវជាមួយទិសដែលមាសដើរ $10 មុន ប្រហែល <b>50%</b> ប៉ុណ្ណោះ។ ដូច្នេះ bias គឺជា<b>ផែនទី</b> មិនមែនសញ្ញាចូល។ ត្រូវរង់ចាំ zone, setup និង trigger ជានិច្ច។</div>
<div class='box tip'>💡 ក្នុង group: វាយ <b>/check</b> ដើម្បីមើល bias D / 4H / 1H និងកម្រិតសំខាន់ ហើយប្រៀបធៀបជាមួយ worksheet របស់អ្នក។
រូប 📊 <b>Analysis</b> បង្ហាញ structure និង liquidity · 🚨 <b>Signals</b> និង 📈 <b>Proof</b> បង្ហាញលទ្ធផលពិត។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ កំណត់ bias ពី 5m ឬ 1m ហើយភ្លេច Daily និង 4H</li>
<li>❌ បង្ខំឱ្យមាន bias រាល់ថ្ងៃ (Neutral ក៏ល្អ)</li>
<li>❌ ចូល trade ភ្លាមៗ ព្រោះ "bias ឡើង" ដោយគ្មាន zone និង trigger</li>
<li>❌ ទិញនៅ premium ក្រោយ BSL ត្រូវបាន sweep រួច ដោយសារ "HTF ឡើង"</li>
<li>❌ មិនសរសេរ invalidation ហើយរក្សា bias ទោះតម្លៃបង្ហាញថាខុស</li>
<li>❌ ប្រើ volume profile ពី tick volume ដូចជាទិន្នន័យពិត</li>
<li>❌ ភ្លេចពិនិត្យ 📰 News មុន session</li></ul>
"""),
    ],
    summary=["Bias = ទិសដែលពេញចិត្ត (រក buy ឬ sell) · មិនមែនសញ្ញាចូល trade",
             "ចាប់ផ្ដើមពី Weekly → Daily → 4H · ប្រើកម្រិត PWH/PWL, PDH/PDL និង opens",
             "Draw on liquidity: ខាងណាត្រូវបាន sweep រួច ខាងណានៅរង់ចាំ · ទិញនៅ discount លក់នៅ premium",
             "Volume Profile ផ្ដល់បរិបទ (acceptance / rejection) · Order flow គ្រាន់តែជាការបញ្ជាក់ (COMEX ប៉ុណ្ណោះ)",
             "ចម្លើយមានតែ Bullish · Bearish · Neutral + invalidation ច្បាស់ · ពិនិត្យ macro និង 📰 News ជានិច្ច"],
    exercise=["រយៈពេល 5 ថ្ងៃ បំពេញ worksheet 6 ជំហាន មុន London (14:00) ហើយសរសេរ bias និង invalidation។",
              "សម្គាល់ PWH, PWL, PDH, PDL និង weekly open លើ chart មាស។ តើតម្លៃឥឡូវជិតកម្រិតណាជាងគេ? គិតចម្ងាយជា pips។",
              "រកថ្ងៃមួយដែលអ្នកគួរតែជ្រើស <b>Neutral</b>។ ហេតុអ្វី? កត្តាណាខ្លះផ្ទុយគ្នា?",
              "ពេលល្ងាច ប្រៀបធៀប bias របស់អ្នកជាមួយ <b>/check</b>, 📊 Analysis និងចលនាពិតរបស់មាស។ កត់ត្រាថាត្រូវ ឬខុស និងមូលហេតុ។"],
)
