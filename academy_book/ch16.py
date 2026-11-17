from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def timeline(w=420, h=168, caption=""):
    """One trading day in Cambodia time (winter, US standard time): sessions, ICT kill zones and key clock times."""
    x0, x1 = 26, w - 14
    X = lambda hr: x0 + ((hr - 6) % 24) * (x1 - x0) / 24          # 06:00 Cambodia = start of the trading day
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<text x="{x0}" y="18" class="lt" fill="#6E6E73">Session</text>',
           f'<text x="{x0}" y="78" class="lt" fill="#6E6E73">Kill zone (ICT)</text>']
    for a, b, t, col in [(6, 14, "Asia", GOLD), (14, 19, "London", BL), (19, 24, "New York", DN), (0, 5, "ស្ងាត់", GR)]:
        xa, xb = X(a), X(a) + ((b - a) % 24 or 24) * (x1 - x0) / 24
        out.append(f'<rect x="{xa:.1f}" y="26" width="{xb - xa - 1:.1f}" height="30" rx="6" fill="{col}" fill-opacity=".18" stroke="{col}"/>')
        out.append(f'<text x="{(xa + xb) / 2:.1f}" y="46" text-anchor="middle" fill="{col}" class="bt">{t}</text>')
    xb = X(5)
    out.append(f'<rect x="{xb:.1f}" y="26" width="{(x1 - xb):.1f}" height="30" rx="3" fill="#1C1C1E" fill-opacity=".75"/>')
    for a, b, t, col in [(8, 12, "Asia KZ", GOLD), (14, 17, "LDN KZ", BL), (19, 22, "NY KZ", DN), (22, 24, "LC", PU)]:
        xa, xc = X(a), X(a) + (b - a) * (x1 - x0) / 24
        out.append(f'<rect x="{xa:.1f}" y="86" width="{xc - xa - 1:.1f}" height="22" rx="5" fill="{col}" fill-opacity=".85"/>')
        out.append(f'<text x="{(xa + xc) / 2:.1f}" y="101" text-anchor="middle" fill="white" class="lt">{t}</text>')
    for hr in range(6, 30, 2):
        x = X(hr % 24)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="114" y2="119" stroke="#8E8E93"/>')
        out.append(f'<text x="{x:.1f}" y="131" text-anchor="middle" fill="#6E6E73" class="st">{hr % 24:02d}</text>')
    for hr, t, col in [(12, "NY 00:00", GR), (20.5, "20:30 US news", DN)]:
        x = X(hr)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="62" y2="112" stroke="{col}" stroke-width="1.3" stroke-dasharray="3 3"/>')
        out.append(f'<text x="{x:.1f}" y="152" text-anchor="middle" fill="{col}" class="lt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=16, part="PART 3 · ICT: Inner Circle Trader Concepts",
    title_km="ពេលវេលា និង Session របស់ ICT", title_en="ICT Time & Sessions: Kill Zones · Judas Swing · Daily Bias",
    intro="""ក្នុងជំពូកមុនៗ យើងរៀនថា<b>កន្លែងណា</b>ដែលតម្លៃអាចប្រតិកម្ម (liquidity, FVG, OB, premium/discount)។ ជំពូកនេះឆ្លើយសំណួរទីពីរ:
<b>ពេលណា?</b> មាសជួញដូរស្ទើរតែ 24 ម៉ោង ប៉ុន្តែមិនមែនគ្រប់ម៉ោងសកម្មដូចគ្នាទេ។ យើងនឹងរៀន <span class='en-term'>Asian</span>,
<span class='en-term'>London</span> និង <span class='en-term'>New York session</span>, <span class='en-term'>kill zones</span>,
<span class='en-term'>Judas swing</span>, របៀបបង្កើត <span class='en-term'>daily bias</span> និងរបៀបប្ដូរម៉ោងទាំងអស់មកជា<b>ម៉ោងកម្ពុជា</b>
(រួមទាំងពេល <span class='en-term'>Daylight Saving Time</span>)។ យើងក៏នឹងបង្ហាញលេខពិតពីទិន្នន័យ និងការសាកល្បងរបស់ XAU.KH ផងដែរ
ដើម្បីឱ្យអ្នកដឹងថា អ្វីជា "ទម្លាប់" ហើយអ្វីមិនមែនជាច្បាប់។""",
    sections=[
        ("ហេតុអ្វីពេលវេលាសំខាន់? ផែនទីម៉ោងកម្ពុជា", """
<p>តម្លៃមាសផ្លាស់ទីដោយសារមានអ្នកទិញ និងអ្នកលក់ចូលទីផ្សារ។ នៅពេលធនាគារ និង fund ធំៗនៅ London និង New York ចាប់ផ្ដើមធ្វើការ
<b>volume</b> កើនឡើង ហើយចលនាធំៗច្រើនតែកើតឡើង។ ពេលទីផ្សារស្ងាត់ តម្លៃច្រើនតែដើរយឺត និងនៅក្នុង range តូច។
ICT ហៅគំនិតនេះថា <span class='en-term'>"Time and Price"</span>: setup ល្អ = <b>កន្លែងត្រឹមត្រូវ</b> + <b>ពេលត្រឹមត្រូវ</b>។</p>
""" + bars([("Asia", 4.4, GOLD), ("London", 5.5, BL), ("NY ព្រឹក", 13.3, DN), ("NY ល្ងាច", 6.8, GR)], unit="k",
           caption="Volume មធ្យមក្នុង 1 ម៉ោង (gold futures, ពាន់ contracts) · ទិន្នន័យ XAU.KH 21 Aug – 13 Nov 2026") + """
<p>ក្នុងទិន្នន័យ 12 សប្ដាហ៍នេះ ម៉ោងបើក <b>New York</b> មាន volume ប្រហែល <b>2–3 ដង</b> នៃម៉ោងផ្សេងទៀត។
ទំហំចលនាមធ្យមក្នុង 1 ម៉ោង ក៏ធំជាងដែរ: ប្រហែល <b>$24</b> (NY ព្រឹក) ធៀបនឹង <b>$14–16</b> (Asia, London, NY ល្ងាច)។</p>
<div class='box tip'>💡 លេខនេះមកពីរយៈពេលខ្លី (12 សប្ដាហ៍) ដែលមាសឡើងចុះខ្លាំង។ វាបង្ហាញ<b>លំនាំទូទៅ</b> មិនមែនការធានាថាថ្ងៃនីមួយៗនឹងដូចគ្នាទេ។
គួរឱ្យចាប់អារម្មណ៍: ក្នុងគំរូនេះ London មិនសកម្មជាង Asia ច្រើនទេ ទោះបីសៀវភៅជាច្រើននិយាយថា London សកម្មជាងក៏ដោយ។ ដូច្នេះ<b>ត្រូវផ្ទៀងផ្ទាត់ជានិច្ច</b>។</div>
<p><b>ផែនទីម៉ោងកម្ពុជា:</b> ICT កំណត់ម៉ោងទាំងអស់តាម<b>ម៉ោង New York (ET)</b>។ កម្ពុជាប្រើ UTC+7 ហើយ<b>មិនប្ដូរម៉ោង</b>ទេ។ ក្នុងរដូវរងារ (winter) កម្ពុជាលឿនជាង New York <b>12 ម៉ោង</b>។
រូបខាងក្រោមបង្ហាញថ្ងៃជួញដូរមួយ គិតពី 06:00 ព្រឹក ដល់ 06:00 ព្រឹកថ្ងៃបន្ទាប់។</p>
""" + timeline(caption="ម៉ោងកម្ពុជា (winter) · KZ = kill zone · LC = London close · ប្រអប់ខ្មៅ 05:00–06:00 = daily break") + """
<table style='break-inside:avoid'><tr><th>Session</th><th>ម៉ោង New York</th><th>កម្ពុជា (winter)</th><th>កម្ពុជា (summer)</th></tr>
<tr><td>🌏 Asia</td><td>18:00–02:00</td><td>06:00–14:00</td><td>05:00–13:00</td></tr>
<tr><td>Asian KZ</td><td>20:00–00:00</td><td>08:00–12:00</td><td>07:00–11:00</td></tr>
<tr><td>🇬🇧 London</td><td>02:00–07:00</td><td>14:00–19:00</td><td>13:00–18:00</td></tr>
<tr><td>London KZ</td><td>02:00–05:00</td><td>14:00–17:00</td><td>13:00–16:00</td></tr>
<tr><td>🇺🇸 New York</td><td>07:00–12:00</td><td>19:00–00:00</td><td>18:00–23:00</td></tr>
<tr><td>New York KZ</td><td>07:00–10:00</td><td>19:00–22:00</td><td>18:00–21:00</td></tr>
<tr><td>London Close</td><td>10:00–12:00</td><td>22:00–00:00</td><td>21:00–23:00</td></tr></table>
<div class='box tip'>💡 សាលា ICT ខ្លះប្រើម៉ោងខុសគ្នាបន្តិច (ឧ. NY KZ ពី 19:30 ម៉ោងកម្ពុជា)។ ភាពខុសគ្នា 30 នាទី មិនសំខាន់ទេ។ អ្វីសំខាន់គឺដឹងថា
<b>ពេលណាទីផ្សារភ្ញាក់</b> និងពេលណាវាស្ងាត់។ Session ក្នុងតារាងនេះ ដូចគ្នានឹងម៉ោងដែល bot XAU.KH ប្រើ។</div>
"""),
        ("Asian Session: ប្រមូលកម្លាំង", """
<p><span class='en-term'>Asian session</span> (06:00–14:00 ម៉ោងកម្ពុជា winter) ជាម៉ោងដែលទីផ្សារ Tokyo, Hong Kong, Shanghai និង Singapore សកម្ម។
សម្រាប់មាស ជាធម្មតាវាមាន <b>range តូចជាង</b> NY ហើយច្រើនតែដើរចំហៀង។ ICT ចាត់ទុក Asia ជាដំណាក់កាល<b>ប្រមូល</b>
(<span class='en-term'>accumulation</span>) ដែលបង្កើត liquidity ទាំងសងខាង។</p>
<ul><li><span class='en-term'>Asia High</span> = កំពូលនៃ session → មាន <span class='en-term'>buy stops</span> (BSL) នៅពីលើ</li>
<li><span class='en-term'>Asia Low</span> = បាតនៃ session → មាន <span class='en-term'>sell stops</span> (SSL) នៅពីក្រោម</li>
<li>ពេល London បើក តម្លៃច្រើនតែមក "យក" កម្រិតមួយក្នុងចំណោមកម្រិតទាំងពីរនេះ</li></ul>
<div class='box warn'>⚠️ Asia មិនតែងតែស្ងាត់ទេ។ ព័ត៌មានពីចិន ជប៉ុន អូស្ត្រាលី ឬព្រឹត្តិការណ៍ភូមិសាស្ត្រនយោបាយ អាចធ្វើឱ្យមាសរត់ខ្លាំងក្នុងម៉ោង Asia។
ក្នុងទិន្នន័យ XAU.KH ខាងលើ ម៉ោង 08:00–10:00 ម៉ោងកម្ពុជា (Asian KZ) ក៏សកម្មគួរសម។</div>
<div class='box tip'>💡 XAU.KH គូរ <b>Asia box</b> (Asia high/low) លើរូប Analysis ក្នុងម៉ោង London និង NY។ ការសិក្សារបស់ bot លើទិន្នន័យ spot 2 ឆ្នាំ:
តម្លៃដើរហួស box ចម្ងាយ<b>មួយកម្ពស់ box</b> ប្រហែល <b>36%</b> នៃថ្ងៃ (ខាងណាមួយ) ហើយ<b>ពីរកម្ពស់</b> ប្រហែល <b>11%</b>។ ទិសនៃ swing មិនបានទាយថាខាងណាទេ។</div>
"""),
        ("London Session: ការបើកដ៏សំខាន់", """
<p><span class='en-term'>London session</span> (14:00–19:00 winter) ជាពេលដែលទីផ្សារ Europe បើក។ <span class='en-term'>London kill zone</span>
(14:00–17:00) ជាម៉ោងដែល ICT រំពឹងថានឹងមាន <b>ចលនាដំបូងដ៏ពិត</b> នៃថ្ងៃ។ លំនាំដែល ICT បង្រៀនញឹកញាប់:</p>
<ul><li>London ច្រើនតែ <b>sweep Asia high ឬ Asia low</b> មុន ហើយបន្ទាប់មកដើរទៅទិសផ្ទុយ</li>
<li>ក្នុងថ្ងៃខ្លះ London បង្កើត <b>high ឬ low នៃថ្ងៃ</b> (ICT ហៅថា "London sets the high/low of the day")</li>
<li>ក្នុងថ្ងៃនិន្នាការខ្លាំង London ចាប់ផ្ដើមចលនា ហើយ NY បន្តវា</li></ul>
""" + zigzag([50, 62, 44, 58, 48, 56, 30, 52, 72, 66, 88],
             {1: ("Asia H", GOLD), 2: ("Asia L", GOLD), 6: ("Sweep", DN), 10: ("NY", UP)},
             lines=[(62, 0, 5, "", GOLD, True), (44, 0, 10, "SSL", GOLD, True)],
             caption="Asia បង្កើត range → London kill zone sweep Asia low (យក SSL) → ត្រឡប់ឡើង → NY បន្ត") + """
<div class='box warn'>⚠️ "London ច្រើនតែ sweep Asia" គឺជា<b>ការសង្កេតរបស់ ICT</b> មិនមែនស្ថិតិដែលយើងបានបញ្ជាក់ទេ។ ថ្ងៃខ្លះ London មិនប៉ះ Asia high/low ទាល់តែសោះ
ហើយថ្ងៃខ្លះវា sweep រួចបន្តទិសដដែល។ ត្រូវរង់ចាំ <span class='en-term'>MSS</span> ជាមួយ displacement (Chapter 9) ជានិច្ច។</div>
"""),
        ("New York Session និង London Close", """
<p><span class='en-term'>New York session</span> (19:00–00:00 winter) ជាម៉ោង<b>សកម្មបំផុត</b>សម្រាប់មាស ព្រោះ London និង New York បើកព្រមគ្នា
(<span class='en-term'>overlap</span>) ហើយព័ត៌មានសេដ្ឋកិច្ចអាមេរិកចេញនៅពេលនេះ។</p>
<table style='break-inside:avoid'><tr><th>ព្រឹត្តិការណ៍</th><th>ម៉ោង NY</th><th>កម្ពុជា (winter / summer)</th></tr>
<tr><td>NY kill zone ចាប់ផ្ដើម</td><td>07:00</td><td>19:00 / 18:00</td></tr>
<tr><td>📰 ព័ត៌មាន US (CPI, NFP, ...)</td><td>08:30</td><td>20:30 / 19:30</td></tr>
<tr><td>ផ្សារភាគហ៊ុន NYSE បើក</td><td>09:30</td><td>21:30 / 20:30</td></tr>
<tr><td>London close (KZ)</td><td>10:00–12:00</td><td>22:00–00:00 / 21:00–23:00</td></tr>
<tr><td>📰 FOMC (ការប្រកាសការប្រាក់)</td><td>14:00</td><td>02:00 / 01:00 (យប់)</td></tr></table>
<ul><li><b>NY kill zone</b>: ចលនាខ្លាំងៗជុំវិញព័ត៌មាន 20:30 · ច្រើនតែមាន Judas swing មុនព័ត៌មាន ឬភ្លាមៗបន្ទាប់ពីព័ត៌មាន</li>
<li><span class='en-term'>London close</span>: trader Europe បិទ position ពេលបិទការងារ → ចលនាអាចថយក្រោយ (retrace) ពីទិសដែលបានដើរពេញមួយថ្ងៃ</li>
<li>ក្រោយ 00:00 ម៉ោងកម្ពុជា ទីផ្សារស្ងាត់វិញ · spread អាចធំនៅជុំវិញ <b>daily break</b> (05:00–06:00 winter)</li></ul>
<div class='box warn'>⚠️ មុន និងក្រោយព័ត៌មានធំ spread និង slippage អាចធំខ្លាំង ហើយតម្លៃអាចរត់ $10–30 ក្នុងប៉ុន្មាននាទី។ ពិនិត្យ 📰 News ក្នុង group មុនរៀងរាល់ session។</div>
"""),
        ("Session Liquidity: គោលដៅដែលមើលឃើញ", """
<p>កម្រិតខ្ពស់ និងទាបនៃ session នីមួយៗ ជាកន្លែងដែល trader ជាច្រើនដាក់ <span class='en-term'>stop loss</span> (Chapter 12)។ ដូច្នេះវាក្លាយជា
<span class='en-term'>session liquidity</span>: គោលដៅដែលតម្លៃអាចទាក់ទាញទៅ។</p>
<table style='break-inside:avoid'><tr><th>កម្រិត</th><th>ឈ្មោះខ្លី</th><th>ប្រើយ៉ាងម៉េច</th></tr>
<tr><td>Asia High / Low</td><td>AH / AL</td><td>គោលដៅ sweep ពេល London / NY</td></tr>
<tr><td>London High / Low</td><td>LH / LL</td><td>គោលដៅ ឬកម្រិត sweep ពេល NY</td></tr>
<tr><td>Previous Day High / Low</td><td>PDH / PDL</td><td>Liquidity ធំជាង · ច្រើនតែជា draw on liquidity</td></tr>
<tr><td>Previous Week High / Low</td><td>PWH / PWL</td><td>Liquidity ធំបំផុតសម្រាប់សប្ដាហ៍</td></tr></table>
""" + zigzag([40, 55, 35, 50, 42, 70, 60, 92, 74, 80],
             {1: ("AH", GOLD), 2: ("AL", GOLD), 5: ("LDN H", BL), 7: ("Sweep", DN)},
             lines=[(86, 0, 5, "PDH · BSL", DN, True), (55, 1, 6, "", GOLD, True)],
             caption="ឧទាហរណ៍: London បំបែក Asia high → NY ឡើងទៅយក PDH (buy stops ពីលើ high ម្សិលមិញ)") + """
<div class='box tip'>💡 មុនចូល session នីមួយៗ សួរខ្លួនឯង: "liquidity ណាដែល<b>នៅមិនទាន់ត្រូវយក</b>?" កម្រិតដែលនៅជិត និងមិនទាន់ប៉ះ ច្រើនតែជាគោលដៅ
(ឬជា TP) ប្រសើរជាងកម្រិតដែលទើបតែត្រូវ sweep រួច។</div>
"""),
        ("Judas Swing: ការបោកដំបូង", """
<p><span class='en-term'>Judas swing</span> គឺជា<b>ចលនាបោក</b>នៅដើម session: តម្លៃរត់ទៅទិសមួយ (ច្រើនតែ sweep Asia high/low ឬ PDH/PDL)
ធ្វើឱ្យ trader ជឿថាទិសនោះពិត ហើយបន្ទាប់មក<b>ត្រឡប់</b>ទៅទិសពិតនៃថ្ងៃ។ ឈ្មោះនេះមកពី "Judas" អ្នកក្បត់។</p>
""" + zigzag([60, 66, 56, 64, 58, 80, 70, 52, 44, 30, 36, 18],
             {1: ("AH", GOLD), 2: ("AL", GOLD), 5: ("Judas ↑", OR), 7: ("MSS ↓", DN), 11: ("ទិសពិត", DN)},
             lines=[(66, 0, 4, "BSL", GOLD, True), (56, 2, 8, "", GOLD, True)],
             caption="Bias ចុះ: ដើម London តម្លៃរត់ឡើងហួស Asia high (Judas) → MSS ចុះ → ចលនាពិតធ្លាក់") + """
<p>ជំហានដើម្បីសម្គាល់ Judas swing:</p>
""" + flow([("Bias", "HTF ចុះ ឬឡើង", BL), ("Kill zone", "ដើម London/NY", GOLD), ("Sweep", "ផ្ទុយ bias", OR), ("MSS", "+ displacement", UP)],
           caption="Judas swing មានន័យ តែពេលវារត់ផ្ទុយ bias ហើយត្រឡប់ដោយ MSS ច្បាស់") + """
<div class='box warn'>⚠️ <b>ការសាកល្បងពិតរបស់ XAU.KH</b> (2 ឆ្នាំ, ទិន្នន័យ 5m): ការ trade ផ្ទុយពី sweep នៃ range ព្រឹកព្រលឹម (Asia) ដោយគ្មានការបញ្ជាក់
<b>ខាតក្នុងគ្រប់ version</b> ដែលបានសាកល្បង។ នៅព្រឹក Asia sweep ច្រើនតែជា<b>ការចាប់ផ្ដើមនៃចលនា</b> មិនមែនការបោកទេ។
មានន័យថា: មិនមែនរាល់ sweep សុទ្ធតែជា Judas swing ទេ។ អ្នកដឹងថាវាជា Judas តែ<b>ក្រោយ</b> MSS ប៉ុណ្ណោះ។</div>
"""),
        ("Daily Bias: ទិសដែលរំពឹងសម្រាប់ថ្ងៃ", """
<p><span class='en-term'>Daily bias</span> គឺជាចម្លើយលើសំណួរ: "ថ្ងៃនេះ តម្លៃទំនងជាចង់ទៅយក liquidity ខាង<b>លើ</b> ឬខាង<b>ក្រោម</b>?"
ICT បង្កើត bias នៅមុនម៉ោង London ដោយប្រើជំហានទាំងនេះ:</p>
""" + flow([("Daily / 4H", "structure ឡើង/ចុះ", BL), ("Draw on liq.", "PDH / PDL / PWH", GOLD), ("P / D", "តម្លៃនៅ premium?", PU),
            ("Opens", "Daily · NY 00:00", GR), ("📰 News", "ថ្ងៃនេះមានអ្វី?", DN), ("Bias", "+ ចំណុចខុស", UP)],
           caption="ជំហានបង្កើត daily bias មុន London · ត្រូវមានចំណុចដែលបញ្ជាក់ថា bias ខុស") + """
<ul><li><span class='en-term'>Midnight open</span> (00:00 New York = <b>12:00 ថ្ងៃត្រង់</b> ម៉ោងកម្ពុជា winter): ICT ប្រើជាខ្សែបែងចែក · bias ឡើង → រកទិញក្រោមខ្សែនេះ · bias ចុះ → រកលក់លើវា</li>
<li><span class='en-term'>Daily open</span>: តម្លៃបើកនៃថ្ងៃជួញដូរ (18:00 NY = 06:00 ម៉ោងកម្ពុជា winter)</li>
<li>បើ structure HTF និង draw on liquidity មិនស្របគ្នា → <b>គ្មាន bias</b> ក៏ជាចម្លើយត្រឹមត្រូវដែរ</li></ul>
<div class='box warn'>⚠️ <b>ស្មោះត្រង់ជាមួយលេខ:</b> XAU.KH បានសាកល្បង bias top-down (D / 4H / 1H) លើការប្រកាស session <b>1,405</b> ដង ក្នុង 2 ឆ្នាំ។
វាត្រូវជាមួយទិសដែលមាសដើរ $10 មុន ប្រហែល <b>50%</b> ប៉ុណ្ណោះ (ដូចបោះកាក់)។ ដូច្នេះ bias គឺជា<b>ផែនទី</b> សម្រាប់ជ្រើសថាត្រូវរកអ្វី និងកុំធ្វើអ្វី
មិនមែនការទាយទិសដែលអាចចូល trade ភ្លាមៗបានទេ។ ត្រូវរង់ចាំការបញ្ជាក់នៅលើ timeframe តូចជានិច្ច។</div>
"""),
        ("ទម្លាប់តាមថ្ងៃនៃសប្ដាហ៍", """
<p>ICT បង្រៀនគំនិតខ្លះអំពី<b>ថ្ងៃនីមួយៗ</b>ក្នុងសប្ដាហ៍។ ទាំងនេះជា<b>គំនិត (ideas)</b> មិនមែនច្បាប់ ហើយយើងមិនទាន់បានបញ្ជាក់វាជាស្ថិតិទេ:</p>
<table style='break-inside:avoid'><tr><th>ថ្ងៃ</th><th>គំនិត ICT</th><th>ចំណាំសម្រាប់មាស</th></tr>
<tr><td>ច័ន្ទ</td><td>ច្រើនតែយឺត · បង្កើត range ដំបូងនៃសប្ដាហ៍</td><td>មើល gap ពេលបើកព្រឹកច័ន្ទ</td></tr>
<tr><td>អង្គារ</td><td>ច្រើនតែបង្កើត high ឬ low នៃសប្ដាហ៍</td><td>តែជាការសង្កេត</td></tr>
<tr><td>ពុធ</td><td>អាចបង្កើត high/low នៃសប្ដាហ៍ ឬបន្តទិស</td><td>ពេលខ្លះមាន FOMC (យប់ពុធ → ព្រឹកព្រហស្បតិ៍)</td></tr>
<tr><td>ព្រហស្បតិ៍</td><td>ពេលខ្លះ reverse ទិសសប្ដាហ៍</td><td>ព័ត៌មាន US ច្រើន</td></tr>
<tr><td>សុក្រ</td><td>បិទ position មុនចុងសប្ដាហ៍ · retrace</td><td>NFP សុក្រដំបូងនៃខែ (20:30 winter)</td></tr></table>
""" + bars([("ច័ន្ទ", 76, GR), ("អង្គារ", 80, GR), ("ពុធ", 96, BL), ("ព្រហ.", 85, GR), ("សុក្រ", 81, GR)], unit="$",
           caption="ទំហំ range មធ្យម (median) ក្នុង 1 ថ្ងៃ គិតជា $ · gold futures · 12 សប្ដាហ៍ 21 Aug – 13 Nov 2026") + """
<div class='box tip'>💡 ក្នុងគំរូ 12 សប្ដាហ៍នេះ ថ្ងៃពុធមាន range ធំជាងគេ ហើយច័ន្ទតូចជាងគេ។ ប៉ុន្តែមានតែប្រហែល <b>12 ថ្ងៃ</b> សម្រាប់ថ្ងៃនីមួយៗ
ដែលតិចពេកដើម្បីសន្និដ្ឋានជាច្បាប់។ សូមប្រើវាដើម្បី<b>រៀបចំខ្លួន</b> (ឧ. ថ្ងៃមានព័ត៌មានធំ → កាត់ lot) មិនមែនដើម្បីទាយទិស។</div>
"""),
        ("Daylight Saving Time និងការប្ដូរម៉ោងកម្ពុជា", """
<p>អាមេរិក និងអង់គ្លេសប្ដូរម៉ោង 2 ដងក្នុងមួយឆ្នាំ (<span class='en-term'>DST</span>) ប៉ុន្តែកម្ពុជាមិនប្ដូរទេ។ ដូច្នេះម៉ោង session ក្នុងម៉ោងកម្ពុជា<b>ផ្លាស់ទី 1 ម៉ោង</b>។</p>
<table style='break-inside:avoid'><tr><th></th><th>New York → កម្ពុជា</th><th>London → កម្ពុជា</th></tr>
<tr><td>Winter (ម៉ោងស្តង់ដារ)</td><td><b>+12 ម៉ោង</b></td><td>+7 ម៉ោង</td></tr>
<tr><td>Summer (DST)</td><td><b>+11 ម៉ោង</b></td><td>+6 ម៉ោង</td></tr></table>
<table style='break-inside:avoid'><tr><th>ឆ្នាំ</th><th>US DST (summer)</th><th>UK DST (summer)</th></tr>
<tr><td>2026</td><td>8 មីនា – 1 វិច្ឆិកា</td><td>29 មីនា – 25 តុលា</td></tr>
<tr><td>2027</td><td>14 មីនា – 7 វិច្ឆិកា</td><td>28 មីនា – 31 តុលា</td></tr></table>
<p><b>ឧទាហរណ៍:</b> ព័ត៌មាន CPI ចេញ 08:30 ម៉ោង New York។ ក្នុងខែវិច្ឆិកា (winter): 08:30 + 12 = <b>20:30</b> ម៉ោងកម្ពុជា។
ក្នុងខែមិថុនា (summer): 08:30 + 11 = <b>19:30</b> ម៉ោងកម្ពុជា។</p>
<div class='box warn'>⚠️ <b>សប្ដាហ៍ចម្លែក:</b> ក្នុងខែមីនា (2–3 សប្ដាហ៍) និងចុងខែតុលា/ដើមវិច្ឆិកា (1 សប្ដាហ៍) អាមេរិក និងអង់គ្លេសប្ដូរម៉ោង<b>មិនព្រមគ្នា</b>។
ក្នុងពេលនោះ ម៉ោង New York ប្រើតារាង summer ឬ winter ខុសពី London។ ពិនិត្យម៉ោងព័ត៌មានក្នុង 📰 News ជានិច្ច (ម៉ោងទាំងអស់គិតជាម៉ោងកម្ពុជារួចហើយ)។</div>
<div class='box tip'>💡 ម៉ោងនៅលើ <b>MT5</b> គឺជា<b>ម៉ោង server របស់ broker</b> (ច្រើនតែ GMT+2 ឬ GMT+3) មិនមែនម៉ោងកម្ពុជាទេ។ ដើម្បីដឹងភាពខុសគ្នា
ប្រៀបធៀបម៉ោងក្នុង Market Watch ជាមួយនាឡិការបស់អ្នក ហើយចងចាំលេខនោះ (ឧ. កម្ពុជា = server + 4 ឬ + 5 ម៉ោង)។</div>
"""),
        ("ការអនុវត្តក្នុង Group XAU.KH និងកំហុសញឹកញាប់", """
<ul><li>📊 <b>Analysis</b> ចេញ <b>30 នាទីមុន</b> session នីមួយៗ: Asia ~05:30, London ~13:30, New York ~19:00 ម៉ោងកម្ពុជា (winter) · ប្រើវាជាផែនទីមុន kill zone</li>
<li>វាយ <b>/check</b> ដើម្បីមើល bias និងកម្រិតសំខាន់ (Asia high/low, PDH/PDL) ភ្លាមៗ</li>
<li>🚨 <b>Signals</b> អាចចេញក្នុង session ណាមួយ · ពិនិត្យថាវាចេញក្នុង kill zone ឬម៉ោងស្ងាត់ ហើយមើលលទ្ធផលពិតនៅ 📈 <b>Proof</b></li>
<li>📰 <b>News</b> ប្រាប់ម៉ោងព័ត៌មានជាម៉ោងកម្ពុជា · កុំបើក trade ថ្មីប៉ុន្មាននាទីមុនព័ត៌មានធំ</li></ul>
<p><b>កំហុសញឹកញាប់:</b></p>
<ul><li>❌ ចាត់ទុក kill zone ជា "ម៉ោងចូល trade" ដោយមិនមើល structure និង liquidity</li>
<li>❌ ភ្លេចប្ដូរម៉ោងពេល DST ហើយរង់ចាំ London នៅម៉ោងខុស</li>
<li>❌ ហៅរាល់ sweep ថា Judas swing មុនពេលមាន MSS</li>
<li>❌ បង្ខំ bias រាល់ថ្ងៃ · ថ្ងៃខ្លះ "គ្មាន bias" = មិន trade</li>
<li>❌ Trade ពេលងងុយ ឬអស់កម្លាំង · ជ្រើស session <b>មួយ</b> ដែលស្របនឹងជីវិតរបស់អ្នក</li></ul>
<div class='box ok'>✅ <b>ការសាកល្បងរបស់ XAU.KH:</b> ការកំណត់ trade តែម៉ោង London/NY <b>មិនបានធ្វើឱ្យលទ្ធផលល្អជាង</b>ក្នុង model ICT ដែលបានសាកល្បង (trade តិចជាង តែមិនចំណេញជាង)។
ពេលវេលាជួយ<b>ផ្ដោតការយកចិត្តទុកដាក់</b> ប៉ុន្តែវាមិនបង្កើត edge ដោយខ្លួនឯងទេ។</div>
"""),
    ],
    summary=["Asia (06–14) ប្រមូល range · London (14–19) ច្រើនតែ sweep Asia · New York (19–00) សកម្មបំផុត · ម៉ោងកម្ពុជា winter",
             "Kill zones: Asia 08–12 · London 14–17 · NY 19–22 · London close 22–00 (summer ដកចេញ 1 ម៉ោង)",
             "Session liquidity: AH/AL, London H/L, PDH/PDL, PWH/PWL ជាគោលដៅ និងកន្លែង sweep",
             "Judas swing = sweep ផ្ទុយ bias ដើម session · បញ្ជាក់ដោយ MSS ប៉ុណ្ណោះ",
             "Daily bias = ផែនទី មិនមែនការទាយ · ពិនិត្យ DST និងម៉ោង server MT5 ជានិច្ច"],
    exercise=["សរសេរម៉ោងកម្ពុជានៃ London KZ និង NY KZ សម្រាប់សប្ដាហ៍នេះ (winter ឬ summer?)។ ម៉ោង server MT5 របស់អ្នកខុសពីកម្ពុជាប៉ុន្មានម៉ោង?",
              "ថ្ងៃនេះ សម្គាល់ Asia high/low និង PDH/PDL លើ chart 15m។ តើ London sweep កម្រិតណាមួយទេ? មាន MSS បន្ទាប់ឬអត់?",
              "បង្កើត daily bias តាមជំហាន 6 មុន London ហើយសរសេរចំណុចដែលបង្ហាញថា bias ខុស។ ពេលល្ងាច ពិនិត្យលទ្ធផល។",
              "ប្រៀបធៀប bias របស់អ្នកជាមួយ <b>/check</b> និងរូប 📊 Analysis។ កត់ត្រារយៈពេល 2 សប្ដាហ៍ ដើម្បីដឹងថាវាត្រូវប៉ុន្មានដង។"],
)
