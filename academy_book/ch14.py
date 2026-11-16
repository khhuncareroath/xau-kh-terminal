from academy_pdf import zigzag, flow
from academy_book.ch12 import candles

UP, DN, BL, OR, GR, GOLD = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100"

# Bullish OB sketch: down move, last down candle (OB), displacement up through the swing high, retest of the OB, continuation.
BULL_OB = [(55, 62, 52, 60), (60, 66, 56, 58), (58, 60, 44, 46), (46, 49, 30, 33), (33, 60, 32, 58),
           (58, 80, 56, 78), (78, 82, 64, 66), (66, 68, 47, 52), (52, 74, 46, 72), (72, 92, 70, 90)]
BEAR_OB = [(100 - o, 100 - lo, 100 - hi, 100 - c) for (o, hi, lo, c) in BULL_OB]


def refine(w=420, h=200, caption=""):
    """One bearish candle (bullish OB) with the full range, the refined open-to-low part and the mean threshold."""
    hi, op, cl, lo = 4038.0, 4036.5, 4032.2, 4031.0
    top, bot = 30, 175
    Y = lambda p: top + (hi - p) * (bot - top) / (hi - lo)
    mt = (op + lo) / 2
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">']
    out.append(f'<rect x="110" y="{Y(op):.1f}" width="{w - 130}" height="{Y(lo) - Y(op):.1f}" fill="{UP}" fill-opacity=".12"/>')
    out.append(f'<line x1="140" x2="140" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{DN}" stroke-width="2"/>')
    out.append(f'<rect x="126" y="{Y(op):.1f}" width="28" height="{Y(cl) - Y(op):.1f}" rx="2" fill="{DN}"/>')
    out.append(f'<line x1="188" x2="188" y1="{Y(cl) + 2:.1f}" y2="{top - 14}" stroke="{UP}" stroke-width="2"/>')
    out.append(f'<rect x="174" y="{top - 8}" width="28" height="{Y(cl) - top + 8:.1f}" rx="2" fill="{UP}"/>')
    out.append(f'<text x="188" y="{Y(cl) + 18:.1f}" text-anchor="middle" fill="{UP}" class="lt">Displacement</text>')
    # left bracket: full range
    out.append(f'<path d="M104,{Y(hi):.1f} h-8 V{Y(lo):.1f} h8" fill="none" stroke="{GR}" stroke-width="1.4"/>')
    out.append(f'<text x="88" y="{(Y(hi) + Y(lo)) / 2 - 4:.1f}" text-anchor="end" fill="{GR}" class="lt">OB ពេញ</text>')
    out.append(f'<text x="88" y="{(Y(hi) + Y(lo)) / 2 + 12:.1f}" text-anchor="end" fill="{GR}" class="lt">High→Low</text>')
    # right bracket: refined
    out.append(f'<path d="M222,{Y(op):.1f} h8 V{Y(lo):.1f} h-8" fill="none" stroke="{UP}" stroke-width="1.4"/>')
    out.append(f'<text x="238" y="{Y(op) + 14:.1f}" fill="{UP}" class="bt">Refined: Open → Low</text>')
    out.append(f'<line x1="110" x2="{w - 20}" y1="{Y(mt):.1f}" y2="{Y(mt):.1f}" stroke="{BL}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{w - 24}" y="{Y(mt) - 5:.1f}" text-anchor="end" fill="{BL}" class="lt">Mean Threshold 50%</text>')
    out.append(f'<text x="{w - 24}" y="{Y(lo) + 16:.1f}" text-anchor="end" fill="{GR}" class="lt">Low 4,031.00</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=14, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="តំបន់បញ្ជាទិញលក់ (Order Block)", title_en="Order Blocks: Bullish · Bearish · Breaker · Mitigation",
    intro="""ក្នុង Chapter 13 យើងបានរៀនពី <span class='en-term'>FVG</span> ដែល displacement ទុកនៅពីក្រោយ។ ជំពូកនេះនិយាយពី
<b>ទៀនដែលនៅមុន displacement</b> នោះ គឺ <span class='en-term'>Order Block (OB)</span>។ OB គឺជាគំនិត ICT ដែលល្បីបំផុត
ហើយក៏ជាគំនិតដែលត្រូវគេ<b>ប្រើខុស</b>ច្រើនបំផុតដែរ។ អ្នកនឹងរៀនរក OB ឱ្យត្រូវ, កែលម្អ (refine) វា, ស្គាល់ <b>Breaker</b> និង
<b>Mitigation block</b>, ដឹងថាពេលណា OB <b>លែងមានសុពលភាព</b> ហើយសំខាន់បំផុត ប្រើវាជាមួយ <b>liquidity</b> មិនមែនប្រើតែឯង។""",
    sections=[
        ("Order Block គឺជាអ្វី?", """
<p><span class='en-term'>Order Block</span> គឺជា<b>ទៀនផ្ទុយទិសចុងក្រោយ</b> មុនចលនាខ្លាំង (displacement) ដែល<b>បំបែក structure</b>។
គំនិត ICT គឺថា អ្នកជួញដូរធំៗ (ធនាគារ មូលនិធិ) មិនអាចបញ្ចូល order ធំទាំងអស់ក្នុងពេលតែមួយបានទេ។ ពួកគេចាប់ផ្ដើមចូលនៅតំបន់នោះ
ហើយ order ខ្លះ<b>នៅសល់</b>។ ពេលតម្លៃត្រឡប់មកវិញ តំបន់នោះអាចមានការទិញ ឬលក់ម្ដងទៀត។</p>
""" + flow([("ទៀនផ្ទុយទិស", "ទៀនចុងក្រោយ", GR), ("Displacement", "ទៀនធំ លឿន", BL), ("BOS / CHOCH", "បំបែក structure", OR), ("Retest", "ត្រឡប់មក OB", UP)],
           caption="OB ពិតត្រូវមានទាំង 3 ជំហានដំបូង · ជំហានទី 4 ជាកន្លែងដែល trader រង់ចាំ") + """
<div class='box tip'>💡 គំនិត "order នៅសល់" គឺជា<b>ការពន្យល់</b>របស់ ICT មិនមែនជាអ្វីដែលយើងអាចមើលឃើញផ្ទាល់ទេ។ យើងមិនដឹងច្បាស់ថាអ្នកណាទិញ ឬលក់។
អ្វីដែលយើងឃើញពិតប្រាកដ គឺ<b>តម្លៃ</b>ប្រតិកម្មនៅតំបន់នោះ ឬមិនប្រតិកម្ម។</div>
"""),
        ("Bullish Order Block", """
<p><span class='en-term'>Bullish OB</span> គឺជា<b>ទៀនចុះ (ក្រហម) ចុងក្រោយ</b> មុនចលនាឡើងខ្លាំង ដែលបិទទៀនលើ swing high (BOS ↑)។
វាស្ថិតនៅ<b>ក្រោម</b>តម្លៃ ហើយអាចដើរតួជា <b>support</b> ពេលតម្លៃថយចុះមកវិញ។</p>
""" + candles(BULL_OB, zones=[(49, 30, 3, 9, UP, "Bullish OB", "below")], lines=[(66, 1, 5, "BOS ↑", OR, True)],
              notes={3: ("OB", UP, "bottom"), 4: ("Disp.", BL, "top"), 7: ("Retest", BL, "bottom")},
              caption="ទៀនក្រហមចុងក្រោយ (OB) → displacement បំបែក high → តម្លៃត្រឡប់មកប៉ះ OB ហើយឡើងបន្ត") + """
<ul><li>គូរប្រអប់ពី <b>High</b> ដល់ <b>Low</b> នៃទៀនក្រហមនោះ (ឬ Open → Low សម្រាប់ refined, មើលផ្នែកទី 6)</li>
<li>បើមានទៀនក្រហមច្រើនជាប់គ្នា ប្រើ<b>ទៀនចុងក្រោយ</b> ឬរួមទាំងក្រុមជាតំបន់តែមួយ</li>
<li>ច្រើនតែមាន <b>FVG</b> នៅពីលើ OB ដោយសារ displacement</li></ul>
"""),
        ("Bearish Order Block", """
<p><span class='en-term'>Bearish OB</span> គឺផ្ទុយពីនេះ: <b>ទៀនឡើង (បៃតង) ចុងក្រោយ</b> មុនចលនាធ្លាក់ខ្លាំង ដែលបិទទៀនក្រោម swing low (BOS ↓)។
វាស្ថិតនៅ<b>លើ</b>តម្លៃ ហើយអាចដើរតួជា <b>resistance</b>។</p>
""" + candles(BEAR_OB, zones=[(70, 51, 3, 9, DN, "Bearish OB", "above")], lines=[(34, 1, 5, "BOS ↓", OR, True, "below")],
              notes={3: ("OB", DN, "top"), 7: ("Retest", BL, "top")},
              caption="ទៀនបៃតងចុងក្រោយ (OB) → displacement បំបែក low → តម្លៃឡើងប៉ះ OB ហើយធ្លាក់បន្ត") + """
<table style='break-inside:avoid'><tr><th></th><th>Bullish OB</th><th>Bearish OB</th></tr>
<tr><td>ទៀន</td><td>ទៀនចុះចុងក្រោយ</td><td>ទៀនឡើងចុងក្រោយ</td></tr>
<tr><td>បន្ទាប់មក</td><td>Displacement ឡើង + BOS ↑</td><td>Displacement ធ្លាក់ + BOS ↓</td></tr>
<tr><td>ទីតាំង</td><td>ក្រោមតម្លៃ</td><td>លើតម្លៃ</td></tr>
<tr><td>តួនាទី</td><td>Support · តំបន់រក BUY</td><td>Resistance · តំបន់រក SELL</td></tr>
<tr><td>ល្អបំផុតនៅ</td><td>Discount (Chapter 15)</td><td>Premium (Chapter 15)</td></tr></table>
"""),
        ("OB ដែលមានសុពលភាព (Validity)", """
<p>ស្ទើរតែគ្រប់ចលនាមានទៀនផ្ទុយទិសនៅពីមុខ។ ដូច្នេះ<b>មិនមែនគ្រប់ទៀន</b>ជា OB ទេ។ ប្រើតារាងនេះជាតម្រង:</p>
<table style='break-inside:avoid'><tr><th>កត្តា</th><th>✅ OB ល្អ</th><th>❌ OB ខ្សោយ</th></tr>
<tr><td>Displacement</td><td>ទៀនធំ លឿន ចេញពី OB</td><td>ចលនាយឺតៗ ទៀនតូចៗ</td></tr>
<tr><td>Structure</td><td>បំបែក BOS / CHOCH ដោយការបិទទៀន</td><td>មិនបំបែកអ្វីទាំងអស់</td></tr>
<tr><td>FVG</td><td>មាន FVG នៅក្បែរ</td><td>គ្មាន imbalance</td></tr>
<tr><td>Liquidity</td><td>OB បានបោស SSL / BSL មុន</td><td>គ្មាន sweep</td></tr>
<tr><td>HTF</td><td>ស្របនឹង 4H / 1H bias</td><td>ផ្ទុយ HTF</td></tr>
<tr><td>ស្ថានភាព</td><td>ថ្មី (fresh) មិនទាន់ប៉ះ</td><td>ប៉ះច្រើនដងរួច</td></tr>
<tr><td>ទីតាំង</td><td>Bullish ក្នុង discount · Bearish ក្នុង premium</td><td>នៅកណ្ដាល range</td></tr></table>
<div class='box ok'>✅ OB ដែលមាន ✅ ច្រើន គួរឱ្យតាមដាន។ OB ដែលមាន ✅ តែមួយពីរ ល្អបំផុតគឺ<b>រំលង</b>។ Chart មួយត្រូវការ OB សំខាន់តែ 1–2 ប៉ុណ្ណោះ។</div>
"""),
        ("Invalidation: ពេល OB លែងប្រើបាន", """
<p>OB មួយ<b>បរាជ័យ</b> នៅពេលតម្លៃ<b>បិទទៀន</b>ឆ្លងកាត់វាទាំងស្រុង។ ចំពោះ bullish OB គឺបិទទៀនក្រោម <b>Low</b> របស់វា។
ចំពោះ bearish OB គឺបិទទៀនលើ <b>High</b> របស់វា។</p>
<table style='break-inside:avoid'><tr><th>អ្វីដែលកើតឡើង</th><th>អត្ថន័យ</th></tr>
<tr><td>Wick ប៉ះ OB ហើយ reject</td><td>OB ការពារបាន ✅</td></tr>
<tr><td>បិទទៀនក្នុង OB ប៉ុន្តែលើ Mean Threshold</td><td>នៅមានសុពលភាព ប៉ុន្តែកំពុងខ្សោយ</td></tr>
<tr><td>បិទទៀនក្រោម Mean Threshold ច្រើនដង</td><td>សញ្ញាព្រមាន ⚠️</td></tr>
<tr><td>បិទទៀនឆ្លងកាត់ OB ទាំងមូល</td><td>បរាជ័យ ❌ · អាចក្លាយជា Breaker</td></tr></table>
<div class='box warn'>⚠️ ពេល OB បរាជ័យ <b>កុំ</b>ផ្លាស់ SL ចុះទៅក្រោមទៀត ដើម្បី "ផ្ដល់ឱកាស" ដល់វា។ Idea ខុសហើយ។ ចេញ ហើយរង់ចាំ setup ថ្មី។
នេះក៏ជាហេតុផលដែល SL ត្រូវនៅ<b>ក្រោយ OB</b> ជាមួយ buffer (spread មាសអាចពង្រីកពេលព័ត៌មាន)។</div>
"""),
        ("Refined Order Block: កែលម្អតំបន់ឱ្យតូច", """
<p>OB លើ 4H អាចធំ $10–$20 (100–200 pips)។ SL ក្រោយតំបន់ធំបែបនេះ គឺឆ្ងាយណាស់។ Trader ខ្លះ<b>កែលម្អ (refine)</b> OB ដោយ 2 វិធី:</p>
""" + refine(caption="Bullish OB: High 4,038.00 · Open 4,036.50 · Close 4,032.20 · Low 4,031.00 · Mean Threshold (Open→Low) = 4,033.75") + """
<ul><li><b>វិធីទី 1 · ប្រើតែផ្នែកខ្លះនៃទៀន</b>: Bullish OB ប្រើ <b>Open → Low</b> · Bearish OB ប្រើ <b>Open → High</b> ហើយមើល <span class='en-term'>Mean Threshold</span> (50%)</li>
<li><b>វិធីទី 2 · ចុះ timeframe</b>: ក្នុងប្រអប់ OB 4H រក OB តូចជាងនៅលើ 15m ឬ 5m</li></ul>
""" + flow([("4H OB", "តំបន់ធំ $12", BL), ("ចុះ 15m", "មើលខាងក្នុង OB", OR), ("Refined OB", "តំបន់ $3–$4", UP), ("SL តូចជាង", "តែប៉ះងាយជាង", DN)],
           caption="Refine ធ្វើឱ្យ SL តូច ប៉ុន្តែតម្លៃអាចប៉ះ SL ញឹកញាប់ជាង ឬមិនមកដល់ entry") + """
<div class='box warn'>⚠️ Refine មិនមែនជា "ល្បិចឈ្នះ" ទេ។ SL តូចជាង = ឱកាសប៉ះ SL ខ្ពស់ជាង។ XAU.KH បានសាកល្បងលើមាស ហើយឃើញថា
<b>limit order នៅ OB តែឯង ជាមួយ SL តូច</b> ខាតក្នុងរយៈពេលវែង។ ប្រើ OB ជា<b>តំបន់មើល</b> ហើយរង់ចាំការបញ្ជាក់ (CHOCH លើ LTF)។</div>
"""),
        ("Breaker Block: OB ដែលបរាជ័យ ហើយប្ដូរទិស", """
<p><span class='en-term'>Breaker Block</span> គឺជា OB ដែល<b>បរាជ័យ</b> បន្ទាប់ពីតម្លៃ<b>បោស liquidity</b> រួច។
ឧទាហរណ៍ <b>Bearish Breaker</b>: តម្លៃបង្កើត high ថ្មី (sweep BSL) បន្ទាប់មកធ្លាក់ខ្លាំង ហើយបិទទៀនក្រោម bullish OB ដែលបានរុញតម្លៃឡើងទៅ high នោះ។
OB ចាស់នោះឥឡូវក្លាយជា <b>resistance</b>។</p>
""" + candles([(50, 54, 46, 48), (48, 50, 34, 36), (36, 62, 35, 60), (60, 76, 58, 74), (74, 76, 60, 62), (62, 84, 60, 66),
               (66, 68, 40, 42), (42, 44, 22, 25), (25, 46, 23, 44), (44, 47, 30, 32), (32, 34, 12, 15)],
              zones=[(50, 34, 1, 5, UP, ""), (50, 34, 7, 10, DN, "Breaker", "above")], lines=[(76, 3, 6, "BSL", DN, True)],
              notes={1: ("OB", UP, "bottom"), 5: ("Sweep", DN, "top"), 7: ("បិទក្រោម", DN, "bottom")},
              caption="Bullish OB (បៃតង) → sweep BSL → បិទទៀនក្រោម OB → OB ក្លាយជា Bearish Breaker (ក្រហម) → តម្លៃឡើងប៉ះ ហើយធ្លាក់") + """
<ul><li><b>Bullish Breaker</b> គឺផ្ទុយ: sweep SSL (low ថ្មី) → ឡើងខ្លាំង → បិទទៀនលើ bearish OB → OB នោះក្លាយជា support</li>
<li>Breaker ល្អត្រូវការ: <b>sweep</b> + <b>displacement</b> + <b>ការបិទទៀន</b>ឆ្លងកាត់ OB</li>
<li>គំនិតនេះស្រដៀងនឹង IFVG (Chapter 13) និង support ក្លាយជា resistance (Chapter 7)</li></ul>
"""),
        ("Mitigation Block: ខុសពី Breaker យ៉ាងណា?", """
<p><span class='en-term'>Mitigation Block</span> ក៏ជា OB ដែលបរាជ័យដែរ ប៉ុន្តែ<b>គ្មាន sweep</b>។ តម្លៃ<b>មិនអាច</b>បង្កើត high ថ្មីបាន (បង្កើត LH)
រួចធ្លាក់បំបែក low។ ពេលតម្លៃត្រឡប់មកតំបន់នោះ អ្នកដែលទិញខុសនៅទីនោះ ចង់ "ដោះស្រាយ" (mitigate) ដោយចេញនៅ breakeven
ដូច្នេះអាចមានការលក់ម្ដងទៀត។ ICT ប្រើពាក្យ "mitigation" ក្នុងន័យទូទៅផងដែរ: តម្លៃត្រឡប់មកប៉ះ OB ណាមួយ។</p>
""" + zigzag([30, 70, 45, 86, 20, 46, 8], {3: ("HH · sweep", DN), 2: ("Low", UP), 4: ("បែក Low", DN)},
             lines=[(45, 2, 6, "Breaker", DN, True)], caption="Breaker: high ថ្មីបោស BSL មុន រួចបំបែក low") + zigzag(
    [30, 76, 45, 64, 20, 46, 8], {1: ("High", DN), 3: ("LH · មិនដល់", OR), 2: ("Low", UP), 4: ("បែក Low", DN)},
    lines=[(45, 2, 6, "Mitigation", OR, True)], caption="Mitigation: បរាជ័យបង្កើត high ថ្មី (LH) រួចបំបែក low") + """
<table style='break-inside:avoid'><tr><th></th><th>Breaker</th><th>Mitigation Block</th></tr>
<tr><td>មុនបែក</td><td>បង្កើត high/low ថ្មី (sweep)</td><td>មិនដល់ high/low ចាស់ (LH / HL)</td></tr>
<tr><td>Liquidity</td><td>បានបោសរួច</td><td>មិនទាន់បោស</td></tr>
<tr><td>ការប្រើ</td><td>តំបន់ retest ក្រោយ reversal</td><td>តំបន់ retest ក្រោយ structure ខ្សោយ</td></tr></table>
"""),
        ("OB + Liquidity: ការផ្សំដែលមានន័យ", """
<p>OB ដែល<b>ខ្លួនវាផ្ទាល់បានបោស liquidity</b> ជាញឹកញាប់មានន័យជាង OB ធម្មតា។ ឧទាហរណ៍: equal lows (SSL) ត្រូវបានបោស ដោយទៀនក្រហមមួយ
ហើយទៀននោះក្លាយជា OB ពេលតម្លៃឡើងខ្លាំង និងបំបែក high។ គោលដៅធម្មជាតិគឺ <b>BSL</b> ខាងលើ។</p>
""" + candles([(60, 64, 52, 54), (54, 58, 45, 50), (50, 54, 44, 52), (52, 56, 45, 48), (48, 50, 30, 34), (34, 62, 33, 60),
               (60, 78, 58, 76), (76, 78, 56, 58), (58, 60, 47, 52), (52, 80, 50, 78), (78, 94, 76, 92)],
              zones=[(50, 30, 4, 8, UP, "")], lines=[(44.5, 0, 4, "SSL · equal lows", UP, True, "below"), (90, 7, 10, "BSL · គោលដៅ", DN, True)],
              notes={4: ("Sweep + OB", UP, "bottom"), 6: ("BOS", OR, "top"), 8: ("Retest", BL, "bottom")},
              caption="OB ដែលបោស SSL → displacement + BOS → retest OB → តម្លៃឆ្ពោះទៅ BSL") + """
""" + flow([("Liquidity", "SSL ត្រូវបោស", OR), ("OB", "ទៀនដែលបោស", UP), ("BOS + FVG", "displacement", BL), ("Target", "BSL / ERL", DN)],
           caption="ពី liquidity មួយ ទៅ liquidity មួយទៀត (IRL → ERL · Chapter 11)") + """
<div class='box tip'>💡 សួរខ្លួនឯងជានិច្ច: "OB នេះបានយក liquidity ណាមួយហើយឬនៅ? ហើយ liquidity ណាជាគោលដៅបន្ទាប់?" បើឆ្លើយមិនបាន OB នោះទំនងជាមិនសំខាន់។</div>
"""),
        ("ផែនការ Trade ជាលេខ និងការអនុវត្តក្នុង Group", """
<p>ឧទាហរណ៍ BUY ជាមួយ Bullish OB ក្នុងរូប refine ខាងលើ (HTF ឡើង, OB បានបោស SSL, មាន BOS + FVG):</p>
<table style='break-inside:avoid'><tr><th>ផ្នែក</th><th>កម្រិត</th><th>ចម្ងាយ</th></tr>
<tr><td>Entry (Mean Threshold)</td><td>4,033.75</td><td>–</td></tr>
<tr><td>Stop Loss (ក្រោម Low 4,031 + buffer)</td><td>4,029.00</td><td>$4.75 = 47.5 pips</td></tr>
<tr><td>Target (BSL ខាងលើ)</td><td>4,052.00</td><td>$18.25 = 182.5 pips</td></tr></table>
<ul><li>នៅ <b>0.01 lot</b> (1 oz): ខាតប្រហែល <b>$4.75</b> ឬចំណេញប្រហែល <b>$18.25</b> (មិនរាប់ spread) · RR ≈ 1 : 3.8</li>
<li>RR ល្អ <b>មិនធានា</b>ការឈ្នះ · ពេលខ្លះតម្លៃមិនមកដល់ Mean Threshold ហើយ trade មិនកើត</li>
<li>បើតម្លៃបិទទៀនក្រោម 4,031 មុនពេលចូល → OB បរាជ័យ · លុប order</li></ul>
<ul><li>❌ ហៅគ្រប់ទៀនក្រហមថា OB ដោយគ្មាន displacement ឬ BOS</li>
<li>❌ BUY នៅ bullish OB ខណៈ 4H កំពុងធ្លាក់ ហើយតម្លៃនៅ premium</li>
<li>❌ ប្រើ OB ដដែលជាលើកទី 3 ទី 4 (OB ចាស់ខ្សោយជាង)</li>
<li>❌ ដាក់ SL ចំ Low របស់ OB ដោយគ្មាន buffer</li></ul>
<div class='box tip'>💡 ក្នុង group XAU.KH: វាយ <b>/check</b> ដើម្បីមើល bias និង level មុនពេលពិចារណា OB ណាមួយ។ មើលរូប 📊 Analysis ដើម្បីរកថា OB / FVG ណាស្ថិតក្នុង discount ឬ premium។
ពេលមាន 🚨 Signal សូមសាកមើលថាវានៅជិត OB ណា ហើយផ្ទៀងផ្ទាត់លទ្ធផលពិត (ទាំងឈ្នះ ទាំងខាត) នៅ 📈 Proof។</div>
"""),
    ],
    summary=["Bullish OB = ទៀនចុះចុងក្រោយ មុន displacement ឡើងដែលបំបែក structure · Bearish OB = ផ្ទុយ",
             "OB ល្អ = displacement + BOS + FVG + sweep + ស្រប HTF + fresh + នៅ discount/premium ត្រឹមត្រូវ",
             "OB បរាជ័យ ពេលទៀនបិទឆ្លងកាត់វាទាំងមូល · Refine = Open→Low/High ឬចុះ LTF (SL តូច ប៉ះងាយ)",
             "Breaker = OB បរាជ័យក្រោយ sweep · Mitigation block = OB បរាជ័យដោយគ្មាន sweep (LH / HL)",
             "OB ជាតំបន់មើល មិនមែនច្បាប់ចូលតែឯង · ប្រើជាមួយ liquidity និង structure ជានិច្ច"],
    exercise=["នៅលើ chart មាស 1H រក bullish OB 2 និង bearish OB 2 ក្នុងសប្ដាហ៍នេះ។ តើនីមួយៗមាន displacement និង BOS ឬអត់?",
              "ប្រើតារាង Validity ដាក់ពិន្ទុ OB ទាំង 4។ គណនា Mean Threshold របស់ OB ដែលមានពិន្ទុខ្ពស់បំផុត។",
              "រក Breaker ឬ Mitigation block មួយ។ តើមាន sweep មុនពេល OB បរាជ័យឬអត់?",
              "ប្រៀបធៀបជាមួយរូប 📊 Analysis ថ្ងៃនេះ ហើយផ្ទៀងផ្ទាត់ bias ជាមួយ /check។"],
)
