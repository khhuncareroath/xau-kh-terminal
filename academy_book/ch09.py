from academy_pdf import zigzag

UP, DN, BL, OR = "#34C759", "#FF3B30", "#0A84FF", "#FF9500"

CH = dict(
    ch=9, part="PART 2 · Technical Analysis & Market Structure",
    title_km="រចនាសម្ព័ន្ធទីផ្សារ", title_en="Market Structure: Swing · BOS · CHOCH · MSS",
    intro="""<b>រចនាសម្ព័ន្ធទីផ្សារ (Market Structure)</b> គឺជាផែនទីនៃចលនាតម្លៃ។ វាប្រាប់យើងថា
តើទីផ្សារកំពុង<b>ឡើង</b> <b>ធ្លាក់</b> ឬ<b>នៅចំហៀង</b> ហើយនៅពេលណាដែលទិសដៅនោះ<b>ចាប់ផ្ដើមផ្លាស់ប្ដូរ</b>។
គ្រប់វិធីសាស្ត្រដែលអ្នកនឹងរៀនបន្ទាប់ (ICT, Liquidity, Order Block, FVG) សុទ្ធតែផ្អែកលើមូលដ្ឋាននេះ។
បើអ្នកអាន structure មិនច្បាស់ អ្វីៗផ្សេងទៀតនឹងក្លាយជាការទាយ។""",
    sections=[
        ("Swing High និង Swing Low", """
<p><span class='en-term'>Swing High</span> គឺជាកំពូលមួយដែលមានទៀននៅសងខាង<b>ទាបជាង</b>វា។
<span class='en-term'>Swing Low</span> គឺជាបាតមួយដែលមានទៀននៅសងខាង<b>ខ្ពស់ជាង</b>វា។
ជាទូទៅ អ្នក trade ប្រើទៀនយ៉ាងតិច <b>២ គ្រាប់</b> នៅសងខាង ដើម្បីបញ្ជាក់ថា swing នោះពិតជាត្រូវបានបង្កើតរួចរាល់។</p>
""" + zigzag([30, 55, 40, 78, 52, 66, 35, 48], {1: ("SH", DN), 2: ("SL", UP), 3: ("SH", DN), 4: ("SL", UP), 5: ("SH", DN), 6: ("SL", UP)},
            caption="SH = Swing High (កំពូល) · SL = Swing Low (បាត)") + """
<div class='box tip'>💡 Swing មួយត្រូវបាន <b>បញ្ជាក់</b> តែក្រោយពេលទៀនបន្ទាប់បានបិទរួច។ កុំហៅកំពូលដែលកំពុងបង្កើតថា swing high មុនពេលវាត្រូវបានបញ្ជាក់។</div>
"""),
        ("និន្នាការ: HH · HL · LH · LL", """
<p>នៅពេលយើងភ្ជាប់ swing ទាំងអស់ យើងឃើញ<b>លំនាំ</b>មួយ:</p>
<ul><li><b>Uptrend (និន្នាការឡើង)</b> = <span class='en-term'>HH</span> (Higher High: កំពូលថ្មីខ្ពស់ជាងមុន) + <span class='en-term'>HL</span> (Higher Low: បាតថ្មីខ្ពស់ជាងមុន)</li>
<li><b>Downtrend (និន្នាការធ្លាក់)</b> = <span class='en-term'>LH</span> (Lower High) + <span class='en-term'>LL</span> (Lower Low)</li>
<li><b>Range (ចំហៀង)</b> = កំពូល និងបាតនៅកម្រិតប្រហាក់ប្រហែលគ្នា</li></ul>
""" + zigzag([10, 40, 25, 60, 45, 82, 64, 95], {1: ("HH", UP), 2: ("HL", UP), 3: ("HH", UP), 4: ("HL", UP), 5: ("HH", UP), 6: ("HL", UP)},
            caption="Uptrend: កំពូលនិងបាតថ្មី ខ្ពស់ជាងមុនជានិច្ច") + zigzag([92, 62, 76, 44, 58, 24, 38, 8], {1: ("LL", DN), 2: ("LH", DN), 3: ("LL", DN), 4: ("LH", DN), 5: ("LL", DN), 6: ("LH", DN)},
            caption="Downtrend: កំពូលនិងបាតថ្មី ទាបជាងមុនជានិច្ច")),
        ("Internal និង External Structure", """
<p><span class='en-term'>External structure</span> (រចនាសម្ព័ន្ធខាងក្រៅ) គឺជា swing <b>ធំៗ</b> ដែលកំណត់ព្រំដែននៃ range (ឬ dealing range)។
<span class='en-term'>Internal structure</span> (រចនាសម្ព័ន្ធខាងក្នុង) គឺជា swing <b>តូចៗ</b> ដែលកើតឡើងនៅក្នុង range នោះ។</p>
""" + zigzag([20, 90, 70, 80, 55, 66, 40, 52, 28, 45], {1: ("External High", DN), 8: ("External Low", UP), 3: ("ih", OR), 5: ("ih", OR), 4: ("il", OR), 6: ("il", OR)},
            lines=[(90, 1, 9, "ERL", DN, True), (28, 1, 9, "ERL", UP, True)], caption="ih/il = internal high/low (IRL) · ERL = external range liquidity") + """
<div class='box tip'>💡 ក្នុង <b>15m</b> អ្នកអាចឃើញ internal structure ឡើង ខណៈពេលដែល external structure (4H) នៅតែធ្លាក់។ នេះជាមូលហេតុដែលយើងត្រូវមើល <b>Top-down</b> ជានិច្ច (Chapter 6)។</div>
"""),
        ("BOS: Break of Structure", """
<p><span class='en-term'>BOS</span> កើតឡើងនៅពេលដែលតម្លៃ<b>បិទទៀន</b>ឆ្លងកាត់ swing ក្នុង<b>ទិសដៅដដែល</b>នៃនិន្នាការ។
វាជាសញ្ញាថានិន្នាការ<b>កំពុងបន្ត</b>។</p>
""" + zigzag([15, 50, 32, 70, 52, 88], {1: ("HH", UP), 2: ("HL", UP), 3: ("HH", UP), 4: ("HL", UP)},
            lines=[(50, 1, 3, "BOS ↑", UP, True), (70, 3, 5, "BOS ↑", UP, True)], caption="BOS ↑: បិទទៀនលើ HH ចាស់ = uptrend បន្ត") + """
<div class='box warn'>⚠️ <b>ត្រូវតែជាការបិទទៀន (candle close)</b> មិនមែនត្រឹមតែ wick ទេ។ Wick ដែលឆ្លងហួស ហើយបិទត្រឡប់មកវិញ ជាញឹកញាប់គឺជា <b>liquidity sweep</b> (Chapter 12) មិនមែន BOS ទេ។</div>
"""),
        ("CHOCH និង MSS: ការផ្លាស់ប្ដូរលក្ខណៈ", """
<p><span class='en-term'>CHOCH</span> (Change of Character) ឬ <span class='en-term'>MSS</span> (Market Structure Shift)
កើតឡើងនៅពេលដែលតម្លៃបិទទៀនឆ្លងកាត់ swing ក្នុង<b>ទិសដៅផ្ទុយ</b>ពីនិន្នាការ។
ឧទាហរណ៍ ក្នុង downtrend បើតម្លៃបិទលើ <b>LH ចុងក្រោយ</b> នោះជា CHOCH ឡើង។ វាជាសញ្ញា<b>ដំបូង</b>ដែលនិន្នាការអាចនឹងផ្លាស់ប្ដូរ។</p>
""" + zigzag([90, 60, 74, 42, 56, 22, 40, 33, 70], {1: ("LL", DN), 2: ("LH", DN), 3: ("LL", DN), 4: ("LH", DN), 5: ("LL", DN)},
            lines=[(56, 4, 8, "CHOCH ↑", UP, False)], caption="Downtrend → តម្លៃបិទលើ LH ចុងក្រោយ = CHOCH ឡើង") + """
<table><tr><th></th><th>BOS</th><th>CHOCH / MSS</th></tr>
<tr><td>ទិសដៅ</td><td>ដូចនិន្នាការ</td><td>ផ្ទុយនិន្នាការ</td></tr>
<tr><td>អត្ថន័យ</td><td>និន្នាការបន្ត</td><td>និន្នាការអាចផ្លាស់ប្ដូរ</td></tr>
<tr><td>ការប្រើ</td><td>រក entry តាមនិន្នាការ</td><td>ត្រៀមខ្លួនសម្រាប់ទិសថ្មី (រង់ចាំការបញ្ជាក់)</td></tr></table>
"""),
        ("Displacement: កម្លាំងនៃការបំបែក", """
<p><span class='en-term'>Displacement</span> គឺជាទៀនធំៗ និងលឿន ដែលបំបែក structure។ BOS ឬ CHOCH ដែលមាន displacement
<b>គួរឱ្យទុកចិត្តជាង</b> ការបំបែកដោយទៀនតូចៗយឺតៗ ព្រោះវាបង្ហាញថាមានអ្នកជួញដូរធំៗចូលរួម។ Displacement ច្រើនតែទុក
<span class='en-term'>FVG</span> (Chapter 13) នៅពីក្រោយ។</p>
<div class='box tip'>💡 នៅលើរូបភាព Analysis របស់ XAU.KH ពាក្យ <b>"with displacement"</b> មានន័យថាការបំបែកនោះមានទៀនដែលធំជាង ATR។</div>
"""),
        ("Continuation ឬ Reversal?", """
<ul><li><b>Continuation (បន្ត)</b>: HTF និង LTF ស្របគ្នា + BOS ក្នុងទិសដូចគ្នា → រក entry តាមទិសនោះ</li>
<li><b>Reversal (បង្វិល)</b>: ត្រូវការ <b>liquidity sweep</b> + <b>CHOCH ជាមួយ displacement</b> + ការបញ្ជាក់លើ timeframe តូច</li>
<li>CHOCH តែមួយនៅលើ 5m ខណៈ 4H នៅតែខ្លាំង ជាញឹកញាប់គ្រាន់តែជា <b>pullback</b> ប៉ុណ្ណោះ</li></ul>
"""),
        ("Structural Invalidation: ពេលដែល idea ខុស", """
<p>រាល់ idea ត្រូវមាន<b>ចំណុចខុស</b>ច្បាស់លាស់។ សម្រាប់ទិញក្នុង uptrend ចំណុចខុសគឺ <b>HL ចុងក្រោយ</b>: បើតម្លៃបិទក្រោមវា
រចនាសម្ព័ន្ធឡើងត្រូវបានបំបែក។ សម្រាប់លក់ក្នុង downtrend ចំណុចខុសគឺ <b>LH ចុងក្រោយ</b>។ នេះក៏ជាកន្លែងដែល
<span class='en-term'>Structural Stop Loss</span> (Chapter 30) ត្រូវដាក់ផងដែរ។</p>
"""),
        ("ឧទាហរណ៍លើ chart ពិតរបស់មាស", """
<p>រូបខាងក្រោមគឺជារូប Analysis 15m ពិតរបស់ XAU.KH។ សូមរក <b>HH HL LH LL</b>, បន្ទាត់ <b>CHOCH / BOS</b>
និងជួរ <b>D 4H 1H 30m 15m 5m</b> នៅខាងលើ ដើម្បីមើលថា timeframe ណាស្របគ្នា។</p>
{img:chart}
<div class='cap'>XAU.KH 15m analysis · structure, ELQ / ILQ, CHOCH, EQ 50%</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ហៅ wick ថា BOS (ត្រូវការការ<b>បិទទៀន</b>)</li>
<li>❌ គូរ swing រាល់ទៀនតូចៗ (ត្រូវការ swing ដែល<b>បញ្ជាក់រួច</b>)</li>
<li>❌ មើលតែ 5m ហើយភ្លេច 4H / Daily</li>
<li>❌ Trade CHOCH ភ្លាមៗ ដោយគ្មានការបញ្ជាក់ ឬគ្មាន liquidity sweep មុន</li>
<li>❌ ប្ដូរ timeframe រហូតដល់ឃើញ structure ដែលខ្លួនចង់ឃើញ</li></ul>
"""),
    ],
    summary=["Uptrend = HH + HL · Downtrend = LH + LL",
             "BOS = បិទទៀនឆ្លង swing ក្នុងទិសដូចគ្នា → និន្នាការបន្ត",
             "CHOCH / MSS = បិទទៀនឆ្លង swing ផ្ទុយទិស → និន្នាការអាចផ្លាស់ប្ដូរ",
             "Displacement ធ្វើឱ្យការបំបែកគួរឱ្យទុកចិត្តជាង",
             "តែងតែកំណត់ចំណុចខុស (invalidation) មុនចូល trade"],
    exercise=["បើក chart មាស 15m ហើយសម្គាល់ swing high/low ចំនួន 6 ចុងក្រោយ។",
              "តើ structure 15m ឥឡូវជា uptrend, downtrend ឬ range?",
              "រក BOS ឬ CHOCH ចុងក្រោយ ហើយកំណត់ថាវាមាន displacement ឬអត់។",
              "ផ្ទៀងផ្ទាត់ជាមួយ <b>/check</b> ក្នុង group XAU.KH។"],
)
