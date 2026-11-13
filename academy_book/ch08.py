from academy_pdf import zigzag, flow
from academy_book.ch07 import _scene

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"


def _ema_fig(caption, w=420, h=190):
    """A made-up uptrend path with a smooth moving average under it: pullbacks touch the average and bounce."""
    pts = [12, 22, 18, 30, 26, 38, 33, 46, 41, 54, 48, 62, 56, 70, 64, 78, 72, 86]
    ema, a = [], 2 / (5 + 1)
    for v in pts:
        ema.append(v if not ema else ema[-1] + a * (v - ema[-1]))
    n = len(pts)
    X = lambda i: 20 + i * (w - 40) / (n - 1)
    Y = lambda v: h - 20 - v * (h - 40) / 100
    d1 = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
    d2 = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v - 3):.1f}" for i, v in enumerate(ema))
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<path d="{d2}" fill="none" stroke="{OR}" stroke-width="2.6" stroke-linejoin="round"/>',
           f'<path d="{d1}" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>',
           f'<rect x="24" y="12" width="12" height="4" fill="{OR}"/><text x="41" y="18" class="lt" fill="{OR}">EMA (ខ្សែមធ្យម)</text>',
           f'<rect x="170" y="12" width="12" height="4" fill="#1C1C1E"/><text x="187" y="18" class="lt" fill="#1C1C1E">តម្លៃ</text>']
    for i in (6, 10, 14):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(pts[i]):.1f}" r="3.4" fill="{UP}"/>')
    out.append("</svg>")
    out.append(f'<div class="cap">{caption}</div></div>')
    return "".join(out)


CH = dict(
    ch=8, part="PART 2 · Technical Analysis & Market Structure",
    title_km="និន្នាការ និងបន្ទាត់និន្នាការ", title_en="Trends & Trendlines · Channels · Dynamic S/R",
    intro="""ពាក្យចាស់មួយក្នុង trading និយាយថា <b>"The trend is your friend"</b> (និន្នាការជាមិត្តរបស់អ្នក)។
ការ trade <b>តាមទិស</b>និន្នាការ ជាទូទៅងាយស្រួលជាងការ trade ប្រឆាំងនឹងវា។ ប៉ុន្តែដើម្បីធ្វើបែបនេះបាន
យើងត្រូវដឹងថា<b>និន្នាការគឺជាអ្វី</b> គូរ <span class='en-term'>trendline</span> ឱ្យត្រឹមត្រូវ
ស្គាល់ <span class='en-term'>channel</span> និង <span class='en-term'>dynamic support/resistance</span>
ហើយមិនជាប់<b>អន្ទាក់</b>នៃការបែក trendline ក្លែងក្លាយ។""",
    sections=[
        ("Uptrend និង Downtrend", """
<p><span class='en-term'>Trend</span> (និន្នាការ) គឺជាទិសដៅទូទៅនៃតម្លៃក្នុងរយៈពេលមួយ។ តម្លៃមិនដែលដើរត្រង់ទេ។
វាដើរជា<b>រលក</b>: រត់ទៅមុខ (<span class='en-term'>impulse</span>) រួចថយក្រោយបន្តិច (<span class='en-term'>pullback</span>) រួចរត់ទៅមុខម្ដងទៀត។</p>
<ul><li><b>Uptrend (ឡើង)</b>: រលកឡើង<b>វែង</b>ជាងរលកថយ។ អ្នកទិញគ្រប់គ្រង។</li>
<li><b>Downtrend (ធ្លាក់)</b>: រលកធ្លាក់<b>វែង</b>ជាងរលកឡើង។ អ្នកលក់គ្រប់គ្រង។</li>
<li><b>Range / Sideways (ចំហៀង)</b>: គ្មានភាគីណាឈ្នះ។ តម្លៃលោតរវាង support និង resistance (Chapter 7)។</li></ul>
""" + flow([("Impulse", "រត់ទៅមុខ", UP), ("Pullback", "ថយក្រោយ", OR), ("Impulse", "រត់ទៅមុខ", UP), ("Pullback", "ថយក្រោយ", OR)],
           caption="Trend = រលក impulse និង pullback ឆ្លាស់គ្នា") + """
<div class='box tip'>💡 Trend <b>អាស្រ័យលើ timeframe</b>។ មាសអាចឡើងលើ Daily ធ្លាក់លើ 1H ហើយនៅចំហៀងលើ 5m ក្នុងពេលតែមួយ។
ពេលនិយាយថា "trend" ត្រូវបញ្ជាក់ timeframe ជានិច្ច (ឧ. "4H uptrend")។</div>
"""),
        ("Higher High និង Higher Low", """
<p>វិធីច្បាស់ជាងគេដើម្បីកំណត់ uptrend គឺមើល <b>swing</b>:</p>
<ul><li><span class='en-term'>HH</span> (Higher High) = កំពូលថ្មី <b>ខ្ពស់ជាង</b>កំពូលមុន</li>
<li><span class='en-term'>HL</span> (Higher Low) = បាតថ្មី <b>ខ្ពស់ជាង</b>បាតមុន</li></ul>
""" + zigzag([10, 40, 25, 60, 45, 82, 64, 95], {1: ("HH", UP), 2: ("HL", UP), 3: ("HH", UP), 4: ("HL", UP), 5: ("HH", UP), 6: ("HL", UP)},
             caption="Uptrend: HH + HL · ឧ. 4,010 → 4,030 → 4,022 → 4,045 → 4,036 → 4,062") + """
<p>ដរាបណាតម្លៃនៅតែបង្កើត HH និង HL uptrend នៅតែ<b>ល្អ</b>។ <b>HL ចុងក្រោយ</b> ជាចំណុចសំខាន់ជាងគេ:
បើតម្លៃបិទទៀនក្រោម HL ចុងក្រោយ uptrend ត្រូវបានរំខាន (យើងនឹងហៅវាថា <span class='en-term'>CHOCH</span> នៅ Chapter 9)។</p>
<div class='box ok'>✅ ក្នុង uptrend កន្លែងល្អសម្រាប់រកការ<b>ទិញ</b> គឺពេល pullback ចុះមកបង្កើត <b>HL</b> មិនមែនពេលតម្លៃកំពុងរត់ឡើងខ្លាំងនៅកំពូលទេ។</div>
"""),
        ("Lower High និង Lower Low", """
<p>Downtrend ដូចគ្នា ប៉ុន្តែបញ្ច្រាស:</p>
<ul><li><span class='en-term'>LH</span> (Lower High) = កំពូលថ្មី <b>ទាបជាង</b>កំពូលមុន</li>
<li><span class='en-term'>LL</span> (Lower Low) = បាតថ្មី <b>ទាបជាង</b>បាតមុន</li></ul>
""" + zigzag([92, 62, 76, 44, 58, 24, 38, 8], {1: ("LL", DN), 2: ("LH", DN), 3: ("LL", DN), 4: ("LH", DN), 5: ("LL", DN), 6: ("LH", DN)},
             caption="Downtrend: LH + LL · កន្លែងរកការលក់ = pullback ឡើងទៅបង្កើត LH") + """
<table><tr><th></th><th>Uptrend</th><th>Downtrend</th><th>Range</th></tr>
<tr><td>Swing</td><td>HH + HL</td><td>LH + LL</td><td>កំពូល/បាតស្មើៗគ្នា</td></tr>
<tr><td>រកការ</td><td>ទិញនៅ HL</td><td>លក់នៅ LH</td><td>ទិញ S · លក់ R ឬរង់ចាំ</td></tr>
<tr><td>ចំណុចខុស</td><td>បិទក្រោម HL ចុងក្រោយ</td><td>បិទលើ LH ចុងក្រោយ</td><td>បិទក្រៅ range</td></tr></table>
<div class='box tip'>💡 នៅលើរូប <b>📊 Analysis</b> XAU.KH អក្សរ <b>HH HL LH LL</b> ត្រូវបានសរសេរលើ swing នីមួយៗរួចជាស្រេច
ហើយជួរ <b>D 4H 1H 30m 15m 5m</b> ↑↓ ខាងលើ ប្រាប់ទិស trend នៃ timeframe នីមួយៗ។</div>
"""),
        ("របៀបគូរ Trendline ឱ្យត្រឹមត្រូវ", """
<p><span class='en-term'>Trendline</span> គឺជាបន្ទាត់ទ្រេតដែលភ្ជាប់ swing ក្នុង trend។ វិធាន:</p>
<ul><li><b>Uptrend</b>: ភ្ជាប់ <b>swing low</b> (HL) ពីក្រោម។ <b>Downtrend</b>: ភ្ជាប់ <b>swing high</b> (LH) ពីលើ។</li>
<li>ត្រូវការ <b>2 ចំណុច</b> ដើម្បីគូរ ប៉ុន្តែ trendline ត្រូវបាន<b>បញ្ជាក់</b>ពេលតម្លៃប៉ះ និងលោតចេញនៅចំណុចទី <b>3</b>។</li>
<li>ប្រើ swing ដែល<b>បញ្ជាក់រួច</b> (ច្បាស់ៗ) មិនមែនទៀនតូចៗគ្រប់គ្រាប់ទេ។</li>
<li>គូរលើ wick ឬ body ក៏បាន ប៉ុន្តែ<b>ដូចគ្នាជានិច្ច</b>។ កុំកាត់តួទៀនច្រើនពេក។</li>
<li>កុំ<b>បង្ខំ</b> trendline។ បើត្រូវរំកិលបន្ទាត់ច្រើនដងទើបវាត្រូវ នោះវាមិនមែនជា trendline ល្អទេ។</li></ul>
""" + _scene([20, 45, 28, 58, 38, 72, 48, 85, 70],
             labels={2: ("1", UP, "b"), 4: ("2", UP, "b"), 6: ("3 បញ្ជាក់", UP, "b")},
             segs=[(0, 18, 8, 58, "Trendline ↑", BL, False)],
             caption="ចំណុច 1 និង 2 គូរបន្ទាត់ · ចំណុច 3 បញ្ជាក់ថា trendline មានសុពលភាព") + """
<div class='box tip'>💡 មុំរបស់ trendline សំខាន់។ Trendline <b>ចោតពេក</b> (ឡើងលឿនខ្លាំង) ងាយបែកណាស់ ព្រោះតម្លៃមិនអាចរត់លឿនបែបនោះរហូតបានទេ។
Trendline ដែលមានមុំ<b>មធ្យម</b> ជាទូទៅស្ថិតស្ថេរជាង។</div>
"""),
        ("Trendline Break: បែកមិនមែនមានន័យថាប្ដូរទិសភ្លាមទេ", """
<p>នៅពេលតម្លៃ<b>បិទទៀន</b>ឆ្លងកាត់ trendline វាប្រាប់ថា<b>ល្បឿន</b>នៃ trend បានថយចុះ។ ប៉ុន្តែវា<b>មិនទាន់</b>បញ្ជាក់ថា trend ប្ដូរទិសទេ។
បន្ទាប់ពីបែក trendline តម្លៃអាច:</p>
<ul><li>ធ្លាក់ចុះពិតប្រាកដ (trend ប្ដូរ)</li>
<li>ដើរចំហៀង (range) មួយរយៈ</li>
<li>បន្ត trend ដដែល ប៉ុន្តែក្នុងមុំយឺតជាងមុន</li></ul>
""" + _scene([15, 40, 25, 55, 38, 70, 40, 55, 30, 42, 22],
             labels={4: ("HL", UP, "b"), 6: ("Break", OR, "b"), 7: ("Retest", OR, "a"), 8: ("បិទក្រោម HL", DN, "b")},
             segs=[(0, 12, 6, 51, "", BL, False), (6, 51, 8, 64, "", BL, True), (4, 38, 10, 38, "", DN, True)],
             caption="បែក trendline → retest ពីក្រោម → បិទក្រោម HL ចុងក្រោយ = ទើបមានការបញ្ជាក់") + flow(
    [("Break", "បិទទៀនឆ្លងបន្ទាត់", OR), ("Retest", "ប៉ះបន្ទាត់ពីម្ខាងទៀត", OR), ("Structure", "បែក HL / LH", DN), ("ពិចារណា", "ទិសថ្មី", BL)],
    caption="ជំហានបញ្ជាក់: កុំលក់ភ្លាមៗពេលឃើញ trendline បែកតែមួយទៀន") + """
<div class='box warn'>⚠️ <b>Structure សំខាន់ជាង trendline</b>។ Trendline ជាបន្ទាត់ដែលយើងគូរដោយដៃ (មនុស្សពីរនាក់អាចគូរខុសគ្នា)។
HH/HL/LH/LL គឺជាការពិតលើ chart។ ពេលទាំងពីរប្រាប់ផ្ទុយគ្នា ទុកចិត្ត structure។</div>
"""),
        ("Trend Channel", """
<p><span class='en-term'>Channel</span> (ឆានែល) បង្កើតឡើងដោយ trendline មួយ និងបន្ទាត់<b>ស្រប</b>មួយទៀតនៅម្ខាង។
ក្នុង uptrend channel trendline នៅខាងក្រោម (ភ្ជាប់ HL) ហើយបន្ទាត់ស្របនៅខាងលើ (ប៉ះ HH)។</p>
""" + _scene([18, 46, 30, 58, 42, 70, 54, 82, 66],
             labels={1: ("HH", DN, "a"), 3: ("HH", DN, "a"), 5: ("HH", DN, "a"), 2: ("HL", UP, "b"), 4: ("HL", UP, "b"), 6: ("HL", UP, "b")},
             segs=[(0, 18, 8, 66, "", UP, False), (0, 40, 8, 88, "", DN, True), (0, 29, 8, 77, "", GR, True)],
             caption="Uptrend channel: បន្ទាត់ក្រោម = support ទ្រេត · បន្ទាត់លើ = resistance ទ្រេត · ប្រផេះ = កណ្ដាល") + """
<ul><li>ពាក់កណ្ដាលខាងក្រោមនៃ channel = តំបន់<b>ថោក</b> សម្រាប់រកការទិញក្នុង uptrend។</li>
<li>បន្ទាត់ខាងលើ = តំបន់ដែលអាចយក <b>Take Profit</b>។ មិនមែនជាកន្លែងល្អសម្រាប់ទិញថ្មីទេ។</li>
<li>បើតម្លៃ<b>មិនអាចឡើងដល់</b>បន្ទាត់ខាងលើ (ឈប់នៅកណ្ដាល) ជាសញ្ញាថា trend កំពុង<b>ខ្សោយ</b>។</li></ul>
<div class='box warn'>⚠️ កុំ<b>លក់</b>នៅបន្ទាត់ខាងលើនៃ uptrend channel ដោយគ្មានហេតុផលបន្ថែម។ នោះគឺជាការ trade ប្រឆាំង trend។</div>
"""),
        ("Dynamic Support និង Resistance", """
<p>Support/Resistance មិនចាំបាច់ជាបន្ទាត់ផ្ដេកជានិច្ចទេ។ <b>Dynamic S/R</b> គឺជា level ដែល<b>ផ្លាស់ទីតាមតម្លៃ</b>:
trendline, បន្ទាត់ channel និង <span class='en-term'>Moving Average</span> ជាពិសេស <span class='en-term'>EMA</span>
(Exponential Moving Average)។</p>
""" + _ema_fig("ក្នុង uptrend ល្អ pullback ច្រើនតែមកប៉ះ EMA ហើយលោតចេញ (ចំណុចបៃតង)") + """
<ul><li>អ្នក trade ជាច្រើនប្រើ <b>EMA 20</b> (ខ្លី) និង <b>EMA 50</b> (មធ្យម)។ រូប <b>📊 Analysis</b> របស់ XAU.KH គូរ <b>EMA 21 និង EMA 50</b>។</li>
<li>តម្លៃនៅ<b>លើ</b> EMA ទាំងពីរ ហើយ EMA 21 នៅលើ EMA 50 → ភស្តុតាង uptrend។ បញ្ច្រាសសម្រាប់ downtrend។</li>
<li>ក្នុង trend ខ្លាំង pullback ច្រើនតែឈប់នៅជិត EMA 20/21 ។ ក្នុង trend ខ្សោយ វាអាចចុះដល់ EMA 50។</li>
<li>ក្នុង <b>range</b> តម្លៃកាត់ EMA ចុះឡើងរហូត ហើយ EMA ស្ទើរតែ<b>ដេក</b>។ ពេលនោះ EMA មិនមានប្រយោជន៍ជា S/R ទេ។</li></ul>
<div class='box tip'>💡 នៅលើ MT5 អ្នកអាចបន្ថែម EMA តាម <b>Insert → Indicators → Trend → Moving Average</b> ហើយជ្រើស Method = <b>Exponential</b>។</div>
"""),
        ("Trendline Traps និងសញ្ញាក្លែងក្លាយ", """
<p>Trendline មើលទៅងាយ ប៉ុន្តែមានអន្ទាក់ច្រើន:</p>
""" + _scene([20, 42, 28, 54, 38, 64, 41, 70, 58, 84],
             labels={6: ("Fake break", DN, "b")},
             segs=[(0, 18, 9, 63, "", BL, False)],
             caption="បន្ទាត់ខៀវ = trendline · ទៀន wick ធ្លាក់ក្រោម trendline → ទៀនបន្ទាប់ត្រឡប់ឡើងវិញ → trend បន្ត · អ្នកលក់ភ្លាមៗជាប់អន្ទាក់") + """
<table><tr><th>អន្ទាក់</th><th>របៀបការពារ</th></tr>
<tr><td>បែកតែ wick ឬទៀនតែមួយ</td><td>រង់ចាំទៀន<b>បិទ</b> + retest + បែក structure</td></tr>
<tr><td>Trendline ចោតពេក</td><td>រំពឹងថាវានឹងបែក · មើល trendline ធំជាង</td></tr>
<tr><td>គូរបន្ទាត់ឱ្យត្រូវនឹងគំនិតខ្លួនឯង</td><td>ប្រើតែ swing ច្បាស់ៗ · សួរថា អ្នកដទៃនឹងគូរដូចគ្នាទេ?</td></tr>
<tr><td>Trendline លើ 1m / 5m តែប៉ុណ្ណោះ</td><td>ពិនិត្យ trend លើ 1H / 4H មុន (Top-down)</td></tr>
<tr><td>បែកនៅពេលព័ត៌មាន</td><td>មើល <b>📰 News</b> · ចលនាដំបូងអាចបង្វិលវិញលឿន</td></tr></table>
<div class='box warn'>⚠️ នៅជិត trendline ជាញឹកញាប់មាន <b>Stop Loss</b> ច្រើនរបស់អ្នកដែលទិញតាម trendline។ តម្លៃអាចចុះទៅយក stops ទាំងនោះ ហើយត្រឡប់ឡើងវិញ
(ដូច false breakout ក្នុង Chapter 7)។ ដាក់ SL របស់អ្នកក្រោម <b>HL</b> មិនមែនចំក្រោម trendline ទេ។</div>
"""),
        ("ដាក់វាចូលគ្នា: Trend + Level + Structure", """
<p>Setup ល្អ ច្រើនតែមានហេតុផលច្រើនស្របគ្នា (<span class='en-term'>confluence</span>)។ ឧទាហរណ៍សម្រាប់ការទិញ:</p>
""" + flow([("Trend 4H ↑", "HH + HL", UP), ("Pullback", "ចុះមក HL", OR), ("Confluence", "3 ហេតុផលជួបគ្នា", BL), ("Trigger", "ទៀនបញ្ជាក់ 15m", UP)],
           caption="Trend ធំ → pullback → ប៉ះតំបន់ដែលមានហេតុផលច្រើន → រង់ចាំការបញ្ជាក់") + """
<div class='box ok'>✅ ឧទាហរណ៍: 4H uptrend។ តម្លៃចុះមក 4,040 ដែលជាកន្លែង trendline, EMA 50 និង Demand zone ជួបគ្នា។ ទៀន 15m បិទឡើងខ្លាំង។
ទិញ <b>0.01 lot</b> នៅ 4,043 · SL 4,033 ក្រោម HL ($10 = 100 pips → ហានិភ័យ $10) · TP 4,063 ($20 = 200 pips → ចំណេញ $20)។
Confluence <b>មិនធានា</b>ថាឈ្នះទេ ប៉ុន្តែវាធ្វើឱ្យ idea មានហេតុផលច្បាស់ និងចំណុចខុសច្បាស់។</div>
<p>នៅ XAU.KH សញ្ញា <b>🚨 Signals</b> ត្រូវបានផ្ញើតែពេល trend នៃ timeframe ស្របគ្នា និងគ្មាន Demand/Supply រាំងនៅជិត។
សូមប្រើ <b>/check</b> ដើម្បីមើល trend បច្ចុប្បន្ន មុនពេលសម្រេចចិត្តដោយខ្លួនឯង។</p>
"""),
    ],
    summary=["Uptrend = HH + HL · Downtrend = LH + LL · ត្រូវបញ្ជាក់ timeframe ជានិច្ច",
             "Trendline: 2 ចំណុចដើម្បីគូរ · ចំណុចទី 3 ដើម្បីបញ្ជាក់ · កុំបង្ខំ",
             "Trendline បែក = trend យឺត មិនទាន់ប្ដូរ · រង់ចាំ retest + បែក structure",
             "Channel និង EMA (20/50) ជា dynamic support/resistance",
             "Structure សំខាន់ជាង trendline · SL ក្រោម HL មិនមែនក្រោមបន្ទាត់"],
    exercise=["បើក chart មាស 4H និងសម្គាល់ HH HL ឬ LH LL ចំនួន 6 ចុងក្រោយ។ តើ trend 4H ជាអ្វី?",
              "គូរ trendline មួយដែលមានការប៉ះយ៉ាងតិច 3 ដង លើ 1H ហើយគូរបន្ទាត់ស្របដើម្បីបង្កើត channel។",
              "បន្ថែម EMA 21 និង EMA 50 លើ MT5 ហើយសង្កេតថា pullback ចុងក្រោយឈប់នៅ EMA ណា។",
              "ប្រៀបធៀបជាមួយជួរ D 4H 1H 30m 15m 5m លើរូប 📊 Analysis ឬ /check ថ្ងៃនេះ។"],
)
