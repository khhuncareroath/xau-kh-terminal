from academy_pdf import flow, bars
from academy_book.ch24 import gbars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def markets(w=420, h=196, caption=""):
    """Where gold trades: OTC spot (London), COMEX futures, and the CFD broker the member uses in MT5."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    boxes = [(10, 14, 190, "Spot OTC (London · LBMA)", "ធនាគារ · គ្មាន exchange កណ្ដាល", GOLD),
             (220, 14, 190, "COMEX Futures (GC · MGC)", "exchange កណ្ដាល · volume ពិត", BL),
             (115, 112, 190, "Broker CFD · XAUUSD", "តម្លៃពី liquidity providers", PU)]
    for x, y, bw, t, s, c in boxes:
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="54" rx="10" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="1.4"/>')
        out.append(f'<text x="{x + bw / 2}" y="{y + 23}" text-anchor="middle" fill="#1C1C1E" class="bt">{t}</text>')
        out.append(f'<text x="{x + bw / 2}" y="{y + 42}" text-anchor="middle" fill="{GR}" class="st">{s}</text>')
    out.append(f'<path d="M202,41 L218,41" stroke="#8E8E93" stroke-width="1.6"/><text x="210" y="90" text-anchor="middle" fill="{OR}" class="st">↔ arbitrage</text>')
    for x1, y1, x2, y2 in [(105, 70, 165, 110), (315, 70, 255, 110)]:
        out.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#8E8E93" stroke-width="1.6" fill="none"/>')
        out.append(f'<circle cx="{x2}" cy="{y2}" r="2.6" fill="#8E8E93"/>')
    out.append(f'<text x="210" y="186" text-anchor="middle" fill="{GR}" class="st">អ្នកឃើញតម្លៃនៅ MT5 · Order flow ពិត (Bid/Ask volume) មានតែនៅ <tspan fill="{BL}">COMEX</tspan></text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


# Real data from the repo: weekly median of (COMEX GC=F close - spot XAUUSD close) at the same 5-minute time,
# data/gc_5m.csv.gz vs the spot-data branch (xau_5m.csv.gz), 21 Aug - 20 Nov 2026. Labels = week ending (Sunday).
BASIS = [("23/8", 57), ("30/8", 56), ("6/9", 47), ("13/9", 44), ("20/9", 40), ("27/9", 37), ("4/10", 32), ("11/10", 26),
         ("18/10", 23), ("25/10", 18), ("1/11", 13), ("8/11", 10), ("15/11", 8), ("22/11", 3)]
# Average 5m volume by Cambodia time (3-hour blocks), scaled so the busiest block = 100. Same period.
HOURS = ["00-03", "03-06", "06-09", "09-12", "12-15", "15-18", "18-21", "21-24"]
FUT_V = [57, 21, 39, 32, 41, 42, 87, 100]
SPOT_V = [67, 33, 57, 53, 59, 57, 81, 100]


CH = dict(
    ch=25, part="PART 5 · Order Flow Intelligence",
    title_km="Order Flow និងមាស: ការពិតអំពីទិន្នន័យ", title_en="Order Flow and Gold: COMEX Data · Futures vs XAUUSD · Data Limits",
    intro="""Chapter 22–24 បានបង្រៀនឧបករណ៍ order flow: <span class='en-term'>footprint</span>, <span class='en-term'>delta</span>,
<span class='en-term'>CVD</span>, <span class='en-term'>DOM</span>។ ប៉ុន្តែឧបករណ៍ទាំងនេះល្អ<b>លុះត្រាតែទិន្នន័យល្អ</b>។
សម្រាប់មាស មានបញ្ហាពិសេសមួយ: តម្លៃដែលអ្នក trade ក្នុង MT5 (<span class='en-term'>XAUUSD CFD</span>) <b>មិនមែន</b>ជាទីផ្សារដែលមាន order flow ពិតទេ។
ជំពូកនេះពន្យល់ថា order flow មាសពិតនៅឯណា (<span class='en-term'>COMEX</span>), របៀបប្រៀបធៀបវាជាមួយ XAUUSD,
និងរបៀបជៀសវាងការសន្និដ្ឋានខុសពីទិន្នន័យមិនល្អ។ ជំពូកនេះប្រើ<b>ទិន្នន័យពិត</b>ពីប្រព័ន្ធ XAU.KH ខ្លះ · យើងសរសេរប្រាប់ច្បាស់ក្រោមរូបនីមួយៗ។""",
    sections=[
        ("មាសត្រូវបានជួញដូរនៅឯណា?", """
<p>មាសមិនមានទីផ្សារតែមួយទេ។ មានកន្លែងធំៗបី ដែលតម្លៃដើរ<b>ស្របគ្នា</b> ប៉ុន្តែទិន្នន័យខុសគ្នាទាំងស្រុង:</p>
""" + markets(caption="ទីផ្សារមាសទាំងបី · arbitrage (ទិញថោកម្ខាង លក់ថ្លៃម្ខាង) រក្សាតម្លៃឱ្យជិតគ្នាជានិច្ច") + """
<table style="break-inside: avoid"><tr><th>ទីផ្សារ</th><th>Volume ពិត?</th><th>Bid/Ask volume?</th><th>Order book?</th></tr>
<tr><td>Spot OTC (London)</td><td>គ្មានសាធារណៈ</td><td>គ្មាន</td><td>គ្មានកណ្ដាល</td></tr>
<tr><td><b>COMEX futures</b></td><td><b>មាន</b></td><td><b>មាន</b> (data feed)</td><td><b>មាន</b></td></tr>
<tr><td>Broker CFD (MT5)</td><td>Tick volume ប៉ុណ្ណោះ</td><td>គ្មាន</td><td>Quotes របស់ broker</td></tr></table>
<div class='box tip'>💡 ដូច្នេះ ពេលនរណាម្នាក់និយាយថា "order flow របស់មាស" វាគួរតែមកពី <b>COMEX gold futures</b>។ បើវាមកពី MT5 វាជាការ<b>ប៉ាន់ស្មាន</b>។</div>
"""),
        ("អាន Order Flow របស់ Gold Futures", """
<p><span class='en-term'>COMEX</span> (ផ្នែកមួយនៃ <span class='en-term'>CME Group</span>) មាន contract មាសសំខាន់ពីរ:</p>
<table style="break-inside: avoid"><tr><th></th><th>GC (Gold)</th><th>MGC (Micro Gold)</th><th>XAUUSD ក្នុង MT5</th></tr>
<tr><td>ទំហំ</td><td>100 oz</td><td>10 oz</td><td>1 lot = 100 oz · 0.01 lot = 1 oz</td></tr>
<tr><td>Tick តូចបំផុត</td><td>$0.10 (= 1 pip)</td><td>$0.10</td><td>$0.01 (broker ភាគច្រើន)</td></tr>
<tr><td>តម្លៃ tick មួយ</td><td>$10 / contract</td><td>$1 / contract</td><td>0.01 lot: $1 move = $1</td></tr>
<tr><td>ប្រៀបធៀប</td><td>≈ 1 lot</td><td>≈ 0.10 lot</td><td></td></tr></table>
<ul><li>Futures មាន<b>ថ្ងៃផុតកំណត់</b>។ Contract ដែលមាន volume ច្រើនជាងគេ ហៅថា <span class='en-term'>front month</span> ឬ <span class='en-term'>active contract</span>
(ច្រើនជា Feb, Apr, Jun, Aug, Dec)</li>
<li>មុនផុតកំណត់ អ្នក trade ប្ដូរទៅ contract បន្ទាប់ ហៅថា <span class='en-term'>roll</span>។ Footprint, VP និង CVD ត្រូវមើលលើ contract ដែល<b>សកម្ម</b></li>
<li>CME Globex បើកស្ទើរ 23 ម៉ោងក្នុងមួយថ្ងៃ (អាទិត្យ–សុក្រ) ហើយឈប់សម្រាកប្រហែល 1 ម៉ោងជារៀងរាល់ថ្ងៃ (ប្រហែល 04:00–06:00 ម៉ោងកម្ពុជា អាស្រ័យ daylight saving)</li></ul>
""" + gbars(HOURS, FUT_V, SPOT_V, "COMEX futures volume", "Spot volume (Dukascopy)", ca=BL, cb=GOLD, unit="",
            caption="ទិន្នន័យពិត 21 Aug – 20 Nov 2026 · volume មធ្យមក្នុងទៀន 5m តាមម៉ោងកម្ពុជា (100 = ប្លុកសកម្មបំផុត) · "
                    "ទាំងពីរខ្ពស់បំផុត 18:00–24:00 (London + New York) · ស្ងាត់បំផុត 03:00–06:00") + """
<div class='box ok'>✅ រូបនេះបង្ហាញថា volume របស់ futures និង spot មាន<b>រាងប្រហាក់ប្រហែលគ្នា</b>ក្នុងមួយថ្ងៃ · ដូច្នេះការប្រើ volume futures
សម្រាប់ VWAP និង Volume Profile លើតម្លៃ spot គឺសមហេតុផល។ ប៉ុន្តែកម្រិតលម្អិត (ទៀននីមួយៗ) វាមិនដូចគ្នាទាំងស្រុងទេ។</div>
"""),
        ("យល់ពីទិន្នន័យ COMEX: Volume · Open Interest · COT", """
<p>ក្រៅពី footprint, COMEX ផ្ដល់ទិន្នន័យសាធារណៈបីប្រភេទដែលមានប្រយោជន៍:</p>
<ul><li><span class='en-term'>Volume</span> = ចំនួន contracts ដែលបានជួញដូរ (ពិត មិនមែន tick volume)</li>
<li><span class='en-term'>Open Interest (OI)</span> = ចំនួន contracts ដែល<b>នៅបើក</b> · ប្រកាសរៀងរាល់ថ្ងៃ</li>
<li><span class='en-term'>COT report</span> (Commitments of Traders, ដោយ <span class='en-term'>CFTC</span>) = ក្រុមនីមួយៗ long/short ប៉ុន្មាន ·
ទិន្នន័យថ្ងៃ<b>អង្គារ</b> ប្រកាសថ្ងៃ<b>សុក្រ</b> 15:30 ម៉ោង New York</li></ul>
<table style="break-inside: avoid"><tr><th>តម្លៃ</th><th>OI</th><th>ការអានទូទៅ</th></tr>
<tr><td>↑</td><td>↑</td><td>Longs ថ្មីចូល · ការឡើងមានកម្លាំង</td></tr>
<tr><td>↑</td><td>↓</td><td>Shorts បិទ (short covering) · ការឡើងអាចខ្សោយជាង</td></tr>
<tr><td>↓</td><td>↑</td><td>Shorts ថ្មីចូល · ការធ្លាក់មានកម្លាំង</td></tr>
<tr><td>↓</td><td>↓</td><td>Longs បិទ (long liquidation)</td></tr></table>
""" + bars([("Long", 127.4, UP), ("Short", 15.1, DN), ("Net", 112.3, BL)], unit="k",
           caption="ទិន្នន័យពិតពី cot.json: COT ថ្ងៃ 10 Nov 2026 · Managed money (មូលនិធិធំ) នៅលើ COMEX gold · ពាន់ contracts") + """
<p>ឧទាហរណ៍ខាងលើ: មូលនិធិធំមាន long ប្រហែល 127k និង short ប្រហែល 15k contracts → <b>net long ប្រហែល 112k</b>។
មានន័យថា ពួកគេភាគច្រើនភ្នាល់ថាមាសឡើង។ ប៉ុន្តែពេល net long ខ្ពស់ខ្លាំង ក៏មាន<b>ហានិភ័យ</b>: បើពួកគេចាប់ផ្ដើមលក់ចេញ តម្លៃអាចធ្លាក់លឿន។</p>
<div class='box tip'>💡 ក្នុង group: ផ្ទាំង <b>COT</b> លេចឡើងក្នុងកាត 🌅 Daily Outlook (ជាមួយ 📰 News និង macro) ហើយក្នុងរបាយការណ៍លទ្ធផលប្រចាំសប្ដាហ៍។
COT ជា<b>បរិបទប្រចាំសប្ដាហ៍</b> · វាមិនមែនជាឧបករណ៍កំណត់ពេលចូល trade ទេ ហើយទិន្នន័យវាចាស់ 3 ថ្ងៃរួចហើយពេលប្រកាស។</div>
"""),
        ("ប្រៀបធៀប Futures ជាមួយ XAUUSD: Basis", """
<p>តម្លៃ futures និងតម្លៃ spot មិនស្មើគ្នាទេ។ គម្លាតនេះហៅថា <span class='en-term'>basis</span>:
<b>Basis = តម្លៃ futures − តម្លៃ spot</b>។ ជាទូទៅ futures <b>ខ្ពស់ជាង</b> spot ដោយសារថ្លៃកាន់មាសរហូតដល់ថ្ងៃផុតកំណត់
(ការប្រាក់ និងការរក្សាទុក ហៅថា <span class='en-term'>cost of carry</span>)។</p>
""" + bars([(l, v, GOLD) for l, v in BASIS], unit="",
           caption="ទិន្នន័យពិតរបស់ XAU.KH: basis មធ្យម (median) ប្រចាំសប្ដាហ៍ (GC=F − spot XAUUSD) គិតជា $ · សប្ដាហ៍បញ្ចប់ 23/8 ដល់ 22/11/2026 "
                   "(សប្ដាហ៍ចុងក្រោយមិនពេញ) · basis ថយពី ~$57 មក ~$3 ពេល contract ខិតជិតផុតកំណត់") + """
<ul><li>Basis <b>ប្រែប្រួល</b>: វាតូចទៅៗ ពេល contract ខិតជិតផុតកំណត់ (ដូចរូបខាងលើ) ហើយអាច<b>លោតធំឡើងវិញ</b>ពេល roll ទៅ contract បន្ទាប់</li>
<li>វាក៏ប្រែប្រួលតាមអត្រាការប្រាក់ និងតម្រូវការមាសរូបវ័ន្ត · ក្នុងទិន្នន័យខាងលើ ក៏មានពេលខ្លីៗដែល basis ក្រោមសូន្យដែរ</li>
<li>Broker នីមួយៗក៏មានតម្លៃ XAUUSD ខុសគ្នាបន្តិច (spread និង liquidity providers)</li></ul>
<p><b>បកប្រែកម្រិត futures មក MT5:</b> កម្រិត spot ≈ កម្រិត futures − basis <b>នាពេលបច្ចុប្បន្ន</b>។
ឧ. POC លើ GC = 4,138.0 ហើយ basis ឥឡូវ = +$12.0 → កម្រិតក្នុង MT5 ≈ <b>4,126.0</b>។ ពិនិត្យ basis ជាថ្មីរាល់ថ្ងៃ (កុំប្រើលេខចាស់)។</p>
""" + flow([("GC level", "4,138.0", BL), ("Basis ឥឡូវ", "+$12.0", OR), ("Spot level", "≈ 4,126.0", GOLD), ("MT5", "ពិនិត្យជាមួយ chart", UP)],
           caption="ការបកប្រែកម្រិតពី futures មក XAUUSD (ឧទាហរណ៍) · 12 dollars = 120 pips · កំហុស basis អាចធ្វើឱ្យ SL ខុសទីតាំងទាំងស្រុង") + """
<div class='box ok'>✅ ប្រព័ន្ធ XAU.KH គិតរឿងនេះជំនួសអ្នករួចហើយ: តម្លៃ live ជាតម្លៃ <b>spot XAUUSD</b> (តម្លៃដែលអ្នក trade) ហើយប្រើតែ <b>volume</b> របស់ COMEX
សម្រាប់ VWAP និង Volume Profile។ ដូច្នេះកម្រិតក្នុង 📊 Analysis, /check និង 🚨 Signals គឺជាកម្រិត spot រួចហើយ។</div>
"""),
        ("ដែនកំណត់នៃទិន្នន័យ Spot CFD", """
<p>ក្នុង MT5, XAUUSD គឺជា <span class='en-term'>CFD</span> (Contract for Difference) ដែល broker ផ្ដល់។ ទិន្នន័យរបស់វាមានដែនកំណត់ច្បាស់:</p>
<table style="break-inside: avoid"><tr><th>ទិន្នន័យ</th><th>អ្វីដែល MT5 ផ្ដល់</th><th>បញ្ហា</th></tr>
<tr><td>Volume</td><td><span class='en-term'>Tick volume</span> = ចំនួនដងតម្លៃប្ដូរ</td><td>មិនមែនចំនួន oz ឬ contracts ទេ</td></tr>
<tr><td>Bid/Ask volume</td><td>គ្មាន</td><td>មិនអាចគណនា delta ពិត ឬ footprint</td></tr>
<tr><td>DOM</td><td>Quotes របស់ broker (បើមាន)</td><td>មិនមែន order book ទីផ្សារទាំងមូល</td></tr>
<tr><td>តម្លៃ</td><td>Feed របស់ broker នីមួយៗ</td><td>ខុសគ្នាបន្តិចតាម broker · spread ធំពេល news</td></tr></table>
<ul><li>Tick volume ច្រើនតែ<b>ទាក់ទង</b>នឹងសកម្មភាពពិត (ម៉ោងរវល់ = tick ច្រើន) ដូចដែលបានរៀនក្នុង Chapter 18 ·
ដូច្នេះវាប្រើបានសម្រាប់ "ម៉ោងណារវល់" ឬរាង Volume Profile ប្រហាក់ប្រហែល</li>
<li>ប៉ុន្តែវា<b>មិនប្រាប់</b>ថាអ្នកណាប្រញាប់ (buyer ឬ seller) និងទំហំប៉ុណ្ណា</li></ul>
<div class='box warn'>⚠️ Indicator ក្នុង MT5 ដែលមានឈ្មោះ "Delta", "Footprint" ឬ "Order Flow" សម្រាប់ XAUUSD CFD ភាគច្រើន<b>ប៉ាន់ស្មាន</b>ពីចលនាតម្លៃ ឬ tick ·
វាអាចមើលទៅស្អាត ប៉ុន្តែវាមិនមែនជាទិន្នន័យ exchange ទេ។</div>
"""),
        ("ជៀសវាងការសន្និដ្ឋានខុសពី Tick Volume", """
<p>កំហុសធំបំផុតក្នុង order flow សម្រាប់មាស គឺ<b>ហៅការប៉ាន់ស្មានថាជាការពិត</b>។ ឧទាហរណ៍ទូទៅ:</p>
<table style="break-inside: avoid"><tr><th>ការសន្និដ្ឋានខុស</th><th>ការពិត</th></tr>
<tr><td>"ទៀនបិទឡើង = buyers ឈ្នះ ដូច្នេះ delta វិជ្ជមាន"</td><td>ទៀនបិទឡើងអាចមាន market sell ច្រើនជាង market buy (absorption)</td></tr>
<tr><td>"Tick volume ធំ = អ្នកធំចូល"</td><td>Tick ធំអាចមកពី spread ញ័រ ឬព័ត៌មាន មិនមែន size ធំ</td></tr>
<tr><td>"Broker A មាន volume ធំជាង B"</td><td>Broker នីមួយៗរាប់ tick ខុសគ្នា · មិនអាចប្រៀបធៀបបាន</td></tr>
<tr><td>"Indicator delta ក្នុង MT5 បង្ហាញ divergence"</td><td>ជា divergence នៃ<b>ការប៉ាន់ស្មាន</b> មិនមែន delta ពិត</td></tr></table>
""" + bars([("CVD labels", 49, GR), ("Flow 3/3", 51.7, GR), ("Flow 2/3", 50.5, GR), ("បោះកាក់", 50, OR)], unit="%",
           caption="ការសាកល្បងពិតរបស់ XAU.KH (studies/RESULTS.md): % ដែលតម្លៃទៅតាមទិសសញ្ញា $10 មុន · ស្លាក CVD លើ 15m (2 ឆ្នាំ) និង "
                   "flow verdict (delta 1h, delta 30 នាទី, តម្លៃធៀប VWAP) · ទាំងអស់នៅជិត 50% = មិនខុសពីបោះកាក់") + """
<p>យើងបានសាកល្បងគំនិត order flow ដែលប្រើ delta <b>ប៉ាន់ស្មាន</b>ពីទៀន (ទាំង CVD divergence និងការរួមបញ្ចូល delta ជាមួយ VWAP)។
លទ្ធផល: នៅពេលប្រើ<b>តែឯង</b> ពួកវា<b>មិនបានប្រសើរជាងបោះកាក់</b>ទេ។ នេះមិនមែនមានន័យថា order flow គ្មានប្រយោជន៍ទេ
តែមានន័យថា <b>ការប៉ាន់ស្មានពីទៀន មិនអាចជំនួសទិន្នន័យ Bid/Ask ពិតបានទេ</b> ហើយវាត្រូវការទីតាំង និង structure ជាមួយ។</p>
<div class='box tip'>💡 ចំណុចល្អ: ការសាកល្បងបែបនេះហើយ ដែលជួយ XAU.KH សម្រេចថាអ្វីគួរដាក់ក្នុង 🚨 Signals និងអ្វីត្រូវទុកត្រឹមជាព័ត៌មាន។
លទ្ធផលពិតរបស់ signals ត្រូវបានកត់ត្រាក្នុង 📈 Proof។</div>
"""),
        ("គុណភាពទិន្នន័យ និង Feed យឺត", """
<p>ទោះជាប្រើទិន្នន័យ futures ក៏ដោយ ត្រូវប្រយ័ត្ន<b>គុណភាព</b> និង<b>ល្បឿន</b>របស់ data:</p>
<ul><li><b>Feed ឥតគិតថ្លៃ ច្រើនតែយឺត</b> (delayed) · ឧ. ទិន្នន័យ intraday របស់ Yahoo GC=F ជាធម្មតាយឺតប្រហែល 10 នាទី ·
Footprint real-time ត្រូវការ data feed ពី exchange ដែលច្រើនតែមានថ្លៃប្រចាំខែ</li>
<li><b>ទៀនបាត់ ឬទៀនស្ទួន</b>: feed ខ្លះខកទៀនខ្លះ ពេលអ៊ីនធឺណិតដាច់ ឬពេល server រវល់</li>
<li><b>ម៉ោង (timezone)</b>: data ខ្លះជាម៉ោង UTC ខ្លះជាម៉ោង New York · ច្រឡំម៉ោង = ច្រឡំ session (Asia, London, NY)</li>
<li><b>Roll gap</b>: chart futures ជាប់គ្នា (continuous) អាចមានគម្លាតតម្លៃពេល roll ពី contract មួយទៅ contract បន្ទាប់</li>
<li><b>ប្រវត្តិខ្លី</b>: feed ឥតគិតថ្លៃ ច្រើនផ្ដល់ទៀន 5m ត្រឹមប្រហែល 60 ថ្ងៃ</li></ul>
""" + flow([("Spot prices", "XAUUSD 5m", GOLD), ("Futures vol", "COMEX · 5m", BL), ("Checks", "time · gaps", OR), ("Levels", "VWAP · VP", UP)],
           caption="របៀបដែល XAU.KH ប្រើទិន្នន័យ: តម្លៃ spot + volume futures នៅម៉ោង 5 នាទីដូចគ្នា → ពិនិត្យ → គណនាកម្រិត") + """
<div class='box warn'>⚠️ ពេលណាមួយ XAU.KH ធ្លាក់ទៅប្រើ feed បម្រុង (Yahoo futures) ទិន្នន័យអាចយឺតប្រហែល 10 នាទី ហើយជាតម្លៃ futures ។
ដូច្នេះ ពិនិត្យតម្លៃក្នុង MT5 របស់អ្នកជានិច្ចមុនចូល · បើតម្លៃបានរត់ហួសកម្រិតចូលឆ្ងាយហើយ កុំដេញតាម។</div>
"""),
        ("Checklist: ប្រើ Order Flow មាសដោយស្មោះត្រង់", """
<table style="break-inside: avoid"><tr><th>សំណួរ</th><th>ចម្លើយល្អ</th></tr>
<tr><td>ទិន្នន័យមកពីណា?</td><td>COMEX futures (GC/MGC) · មិនមែន tick volume របស់ broker</td></tr>
<tr><td>Real-time ឬយឺត?</td><td>ដឹងច្បាស់ថាយឺតប៉ុន្មាន</td></tr>
<tr><td>Contract មួយណា?</td><td>Active / front month · ដឹងថ្ងៃ roll</td></tr>
<tr><td>Basis ឥឡូវប៉ុន្មាន?</td><td>វាស់ថ្មីរាល់ថ្ងៃ មុនបកប្រែកម្រិតមក MT5</td></tr>
<tr><td>Delta ពិត ឬប៉ាន់ស្មាន?</td><td>ដឹងច្បាស់ · បើប៉ាន់ស្មាន ប្រើត្រឹមជាព័ត៌មាន</td></tr>
<tr><td>នៅទីតាំងល្អឬទេ?</td><td>OB · FVG · VAL/VAH · Swing ជាមួយ HTF bias</td></tr></table>
<div class='box ok'>✅ អ្នក<b>មិនចាំបាច់</b>មាន footprint ឬ data feed បង់ប្រាក់ ដើម្បី trade មាសនៅ MT5 ទេ។ ការយល់ពីដែនកំណត់ទាំងនេះ
ការពារអ្នកពីការជឿ indicator ឬ "គ្រូ" ដែលអះអាងថាឃើញ "order flow ពិត" នៅលើ CFD។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ហៅ tick volume ក្នុង MT5 ថា "order flow" ឬ "real volume"</li>
<li>❌ យកកម្រិតពី chart futures មកដាក់ក្នុង MT5 ផ្ទាល់ ដោយមិនដក basis</li>
<li>❌ ប្រើ basis ចាស់ (វាប្ដូររាល់ថ្ងៃ ហើយលោតពេល roll)</li>
<li>❌ មើល footprint លើ contract ដែល volume តិច (មិនមែន front month)</li>
<li>❌ ភ្លេចថា feed ឥតគិតថ្លៃយឺត ហើយចូល trade តាមលេខដែលចាស់ 10 នាទី</li>
<li>❌ ប្រើ COT (ប្រចាំសប្ដាហ៍) ដើម្បីកំណត់ពេលចូល trade ក្នុងមួយថ្ងៃ</li></ul>
"""),
    ],
    summary=["Order flow ពិតសម្រាប់មាស = COMEX gold futures (GC 100 oz · MGC 10 oz · tick $0.10) មិនមែន XAUUSD CFD",
             "COMEX ផ្ដល់ volume ពិត, open interest និង COT (ទិន្នន័យអង្គារ ប្រកាសសុក្រ) · COT ជាបរិបទប្រចាំសប្ដាហ៍",
             "Basis = futures − spot · ប្រែប្រួលរាល់ថ្ងៃ និងលោតពេល roll · កម្រិត spot ≈ កម្រិត futures − basis ឥឡូវ",
             "MT5 មានតែ tick volume និង quotes របស់ broker · delta ប៉ាន់ស្មានពីទៀន ក្នុងការសាកល្បងរបស់យើង ≈ បោះកាក់",
             "ពិនិត្យ data: យឺតប៉ុន្មាន, contract ណា, timezone, ទៀនបាត់ · XAU.KH ប្រើតម្លៃ spot + volume COMEX"],
    exercise=["POC លើ chart GC = 4,152.5 ហើយ basis ថ្ងៃនេះ = +$9.5។ កម្រិតប្រហាក់ប្រហែលក្នុង MT5 គឺប៉ុន្មាន? គម្លាតនោះស្មើនឹងប៉ុន្មាន pips?",
              "តម្លៃមាសឡើង $40 ក្នុងមួយសប្ដាហ៍ ប៉ុន្តែ open interest ធ្លាក់ចុះ។ ការឡើងនេះទំនងជាមកពីអ្វី? វាខ្លាំង ឬខ្សោយ?",
              "Indicator មួយក្នុង MT5 បង្ហាញ \"delta divergence\" លើ XAUUSD។ សរសេរសំណួរ 3 ដែលអ្នកគួរសួរមុនជឿវា។",
              "រកផ្ទាំង COT ក្នុងកាត 🌅 Daily Outlook ចុងក្រោយក្នុង group។ មូលនិធិធំ net long ឬ net short? ហេតុអ្វីវាមិនមែនជាសញ្ញាចូល trade?"],
)
