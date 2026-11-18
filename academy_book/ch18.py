from academy_pdf import bars, flow

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def pv(data, vols, notes=None, vnotes=None, lines=None, w=420, h=230, caption=""):
    """Candles on top + volume bars underneath (the way MT5 shows Volumes in a sub-window).
    data = [(open, high, low, close)] in 0-100 · vols = [0-100] · notes = {i: (text, colour, 'top'|'bottom')}
    vnotes = {i: (text, colour)} written above a volume bar · lines = [(y, from_i, to_i, text, colour)]."""
    notes, vnotes, lines = notes or {}, vnotes or {}, lines or []
    n = len(data)
    step = (w - 60) / n
    X = lambda i: 20 + (i + .5) * step
    pt, pb = 18, h * .60            # price panel
    vt, vb = h * .68, h - 14        # volume panel
    Y = lambda v: pb - v * (pb - pt) / 100
    V = lambda v: vb - v * (vb - vt - 12) / 100
    out = ['<div class="fig">', f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="14" x2="{w - 14}" y1="{vb:.1f}" y2="{vb:.1f}" stroke="#C7C7CC"/>',
           f'<text x="{w - 14}" y="{vt + 2:.1f}" text-anchor="end" fill="{GR}" class="st">Volume</text>']
    for (y, a, b, t, col) in lines:
        out.append(f'<line x1="{X(a) - step * .4:.1f}" x2="{X(b) + step * .4:.1f}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        if t:
            out.append(f'<text x="{X(a) - step * .4 + 2:.1f}" y="{Y(y) - 5:.1f}" fill="{col}" class="lt">{t}</text>')
    for i, (o, hi, lo, c) in enumerate(data):
        cx, bw = X(i), step * .56
        col = UP if c >= o else DN
        out.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.5"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 1.5):.1f}" rx="1.5" fill="{col}"/>')
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{V(vols[i]):.1f}" width="{bw:.1f}" height="{vb - V(vols[i]):.1f}" rx="1.5" fill="{col}" fill-opacity=".55"/>')
        if i in notes:
            t, ncol, pos = notes[i]
            ty = Y(hi) - 7 if pos == "top" else Y(lo) + 15
            out.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{ncol}" class="lt">{t}</text>')
        if i in vnotes:
            t, ncol = vnotes[i]
            out.append(f'<text x="{cx:.1f}" y="{V(vols[i]) - 4:.1f}" text-anchor="middle" fill="{ncol}" class="lt">{t}</text>')
    out.append("</svg>")
    if caption:
        out.append(f'<div class="cap">{caption}</div>')
    out.append("</div>")
    return "".join(out)


CH = dict(
    ch=18, part="PART 4 · Volume Profile",
    title_km="មូលដ្ឋានគ្រឹះនៃ Volume", title_en="Volume Foundations: Tick vs Real Volume",
    intro="""ជំពូកនេះចាប់ផ្ដើម <b>PART 4 (Volume Profile)</b>។ រហូតមកដល់ពេលនេះ យើងបានអានតែ<b>តម្លៃ</b> (structure, liquidity, FVG, OB)។
<span class='en-term'>Volume</span> បន្ថែមវិមាត្រទីពីរ: វាប្រាប់យើងថា ចលនាតម្លៃមួយមាន<b>សកម្មភាពច្រើន ឬតិច</b>ប៉ុណ្ណា។
ប៉ុន្តែសម្រាប់មាស មានបញ្ហាសំខាន់មួយ: មាស <span class='en-term'>spot</span> (XAUUSD) <b>គ្មាន volume កណ្ដាលពិតប្រាកដទេ</b>។
ដូច្នេះ មុនប្រើ Volume Profile (Chapter 19–21) យើងត្រូវយល់ថា volume ដែលយើងឃើញមកពីណា វាប្រាប់អ្វី ហើយ<b>មិន</b>អាចប្រាប់អ្វី។""",
    sections=[
        ("Volume វាស់អ្វី?", """
<p><span class='en-term'>Volume</span> គឺជា<b>បរិមាណនៃការជួញដូរ</b>ដែលបានកើតឡើងក្នុងរយៈពេលមួយ (ឧ. ក្នុងទៀន 5m មួយ)។
ក្នុងទីផ្សារ <span class='en-term'>futures</span> វាគឺជាចំនួន <span class='en-term'>contracts</span> ដែលបានទិញលក់។
រាល់ការជួញដូរមួយ មាន<b>អ្នកទិញម្នាក់</b> និង<b>អ្នកលក់ម្នាក់</b> ជានិច្ច។</p>
""" + flow([("អ្នកទិញ", "BUY 1 contract", UP), ("ជួបគ្នា", "trade កើតឡើង", BL), ("អ្នកលក់", "SELL 1 contract", DN), ("Volume +1", "រាប់ក្នុងទៀន", GOLD)],
           caption="Trade មួយ = អ្នកទិញ + អ្នកលក់ · volume រាប់ចំនួនដែលបានជួញដូរ មិនមែនទិស") + """
<div class='box warn'>⚠️ ការយល់ខុសញឹកញាប់: "volume ខ្ពស់ = អ្នកទិញច្រើន"។ <b>មិនពិតទេ</b>។ ទិញ 1,000 contracts មានន័យថាលក់ 1,000 contracts ដែរ។
Volume ប្រាប់ពី<b>កម្លាំង ឬការចាប់អារម្មណ៍</b> (activity) មិនមែនប្រាប់ថាខាងណាឈ្នះទេ។ ទិសដៅ យើងត្រូវអានពី<b>តម្លៃ</b> (ទៀនបិទនៅណា)។</div>
<p>អ្វីដែល volume អាចជួយយើងបាន:</p>
<ul><li>ចលនាមួយមាន<b>ការចូលរួម</b>ច្រើនឬតិច (ពិត ឬខ្សោយ)</li>
<li>តម្លៃណាដែលទីផ្សារ<b>ទទួលយក</b> (ជួញដូរច្រើន) និងតម្លៃណាដែល<b>បដិសេធ</b> (ជួញដូរតិច) → មូលដ្ឋាននៃ Volume Profile</li>
<li>ម៉ោងណាដែលទីផ្សារ<b>សកម្ម</b> ម៉ោងណាស្ងាត់</li></ul>
"""),
        ("Tick Volume និង Real Volume", """
<p>មាន volume ពីរប្រភេទដែលអ្នក trade មាសជួបប្រទះ:</p>
<table><tr><th></th><th>Tick Volume</th><th>Real (Traded) Volume</th></tr>
<tr><td>វាស់អ្វី</td><td>ចំនួនដង<b>ដែលតម្លៃប្ដូរ</b> (ticks) ក្នុងទៀន</td><td>ចំនួន <b>contracts</b> ដែលបានជួញដូរពិត</td></tr>
<tr><td>ប្រភព</td><td>Broker (MT5) · តម្លៃ quote របស់ broker</td><td>Exchange កណ្ដាល ឧ. <b>COMEX</b> (gold futures)</td></tr>
<tr><td>មាស</td><td><span class='en-term'>XAUUSD</span> spot / CFD</td><td><span class='en-term'>GC</span> (100 oz) · <span class='en-term'>MGC</span> micro (10 oz)</td></tr>
<tr><td>ដូចគ្នាគ្រប់ broker?</td><td><b>ទេ</b> · broker នីមួយៗខុសគ្នា</td><td>បាទ/ចាស · ទិន្នន័យតែមួយពី exchange</td></tr>
<tr><td>ក្នុង MT5</td><td>Volumes (default)</td><td>ជាធម្មតា<b>មិនមាន</b>សម្រាប់ XAUUSD CFD</td></tr></table>
""" + flow([("Tick 1", "4,120.10", GR), ("Tick 2", "4,120.30", GR), ("Tick 3", "4,120.20", GR), ("Tick volume = 3", "មិនដឹងទំហំ", OR)],
           caption="Tick volume រាប់ “ចំនួនដងប្ដូរតម្លៃ” · មិនដឹងថា order នីមួយៗធំ ឬតូច") + """
<p><b>ហេតុអ្វី tick volume នៅតែមានប្រយោជន៍?</b> ពេលទីផ្សារសកម្ម (ព័ត៌មាន, London/NY open) មានការជួញដូរច្រើន
ដូច្នេះតម្លៃប្ដូរញឹកញាប់ → tick volume ឡើង។ ពេលស្ងាត់ តម្លៃប្ដូរតិច → tick volume ធ្លាក់។
ដូច្នេះ tick volume ជាទូទៅ<b>ដើរស្របទិសដៅ</b>ជាមួយ real volume (ខ្ពស់ពេលណា ទាបពេលណា) ប៉ុន្តែ<b>មិនមែនជាលេខដូចគ្នា</b>ទេ។</p>
<div class='box tip'>💡 ក្នុង <b>MT5</b>: Insert → Indicators → Volumes → <b>Volumes</b>។ វានឹងបង្ហាញ tick volume ក្រោម chart។
បើ broker របស់អ្នកមានជម្រើស "Real volume" សម្រាប់មាស ត្រូវពិនិត្យថាវាពិតជាមានទិន្នន័យ (ច្រើនតែស្មើសូន្យសម្រាប់ CFD)។</div>
"""),
        ("ហេតុអ្វីមាស Spot គ្មាន Volume កណ្ដាល?", """
<p>មាស spot ត្រូវបានជួញដូរ <span class='en-term'>OTC</span> (Over-The-Counter) គឺរវាងធនាគារ និង dealer ដោយផ្ទាល់ (មជ្ឈមណ្ឌលធំគឺ London)
មិនមែនតាម exchange តែមួយទេ។ គ្មានកន្លែងណាមួយដែលរាប់ការជួញដូរ<b>ទាំងអស់</b>ទេ។ Broker របស់អ្នកឃើញតែ orders នៃអតិថិជនរបស់ខ្លួន និង quote ពី liquidity provider។</p>
<ul><li><b>Spot XAUUSD (MT5)</b> → tick volume របស់ broker តែប៉ុណ្ណោះ</li>
<li><b>COMEX gold futures (GC)</b> → real volume ពី exchange · នេះជាប្រភព volume ដែលអ្នកវិភាគច្រើនប្រើសម្រាប់មាស</li>
<li>XAU.KH ប្រើទិន្នន័យ <b>gold futures</b> ជាជំនួយសម្រាប់ volume ពេល<b>ចាំបាច់</b> ដូចបានសរសេរក្នុងមេរៀនខ្លី</li></ul>
<div class='box warn'>⚠️ តម្លៃ futures <b>ខុសពី</b>តម្លៃ spot បន្តិច (ហៅថា <span class='en-term'>basis</span>) ជាធម្មតាពីរបីដុល្លារ ទៅច្រើនដុល្លារ អាស្រ័យលើខែ contract និងអត្រាការប្រាក់។
បើអ្នកយកកម្រិតពី futures chart មកប្រើលើ XAUUSD ត្រូវ<b>កែតម្រូវ</b>ភាពខុសគ្នានេះជាមុនសិន។</div>
"""),
        ("ហេតុអ្វី Volume សំខាន់?", """
<p>តម្លៃប្រាប់យើងថា<b>អ្វី</b>បានកើតឡើង។ Volume ប្រាប់យើងថា<b>មានមនុស្សប៉ុណ្ណា</b>ចូលរួមក្នុងរឿងនោះ។
គំនិតនេះមកពី <span class='en-term'>Richard Wyckoff</span> ហៅថា <span class='en-term'>Effort vs Result</span> (កម្លាំង និងលទ្ធផល):</p>
<ul><li><b>Effort (កម្លាំង)</b> = volume</li>
<li><b>Result (លទ្ធផល)</b> = ចម្ងាយដែលតម្លៃផ្លាស់ទី</li>
<li>Effort និង Result <b>ស្របគ្នា</b> → ចលនាមានសុខភាពល្អ · <b>មិនស្របគ្នា</b> → ប្រយ័ត្ន ការផ្លាស់ប្ដូរអាចនឹងមកដល់</li></ul>
<p>នេះជាទិន្នន័យពិតពី repo XAU.KH: volume មធ្យមក្នុងទៀន 5m នៃ <b>gold futures</b> តាម session (ម៉ោងកម្ពុជា) ចាប់ពី 21 Aug ដល់ 17 Nov 2026:</p>
""" + bars([("Asia 06–14", 399, GOLD), ("London 14–19", 466, BL), ("New York 19–01", 1082, DN)],
           caption="Volume មធ្យម / ទៀន 5m (contracts) · gold futures · 21 Aug – 17 Nov 2026 · ម៉ោង NY សកម្មជាង Asia ជាង 2 ដង") + """
<div class='box tip'>💡 នេះពន្យល់ថាហេតុអ្វីចលនាធំៗនៃមាសច្រើនកើតនៅម៉ោង London និង New York (Chapter 16) ហើយហេតុអ្វី breakout នៅម៉ោង Asia ស្ងាត់ៗ ច្រើនតែមិនទៅឆ្ងាយ។
ទិន្នន័យនេះជារយៈពេលប្រហែល 3 ខែប៉ុណ្ណោះ: ទំហំពិតប្រែប្រួលតាមខែ និងព័ត៌មាន។</div>
"""),
        ("ទំនាក់ទំនង Volume និងតម្លៃ (១): និន្នាការ", """
<p>ក្នុងនិន្នាការដែលមានសុខភាពល្អ volume ច្រើនតែ<b>កើនឡើង</b>ពេលតម្លៃដើរតាមទិសនិន្នាការ ហើយ<b>ធ្លាក់ចុះ</b>ពេល pullback:</p>
""" + pv([(20, 30, 18, 28), (28, 40, 26, 38), (38, 40, 31, 33), (33, 36, 30, 34), (34, 52, 33, 50), (50, 62, 48, 60), (60, 61, 53, 55), (55, 58, 52, 56), (56, 76, 55, 74), (74, 86, 72, 84)],
         [55, 70, 30, 25, 75, 80, 32, 28, 85, 90],
         notes={2: ("pullback", GR, "bottom"), 6: ("pullback", GR, "bottom")},
         caption="ឡើង + volume ខ្ពស់ · pullback + volume ទាប = និន្នាការឡើងរឹងមាំ") + """
""" + pv([(20, 30, 18, 28), (28, 44, 26, 42), (42, 44, 37, 39), (39, 54, 38, 52), (52, 54, 47, 49), (49, 62, 48, 60), (60, 61, 56, 57), (57, 67, 56, 65), (65, 70, 63, 66), (66, 67, 50, 52)],
         [85, 78, 40, 62, 35, 48, 30, 36, 22, 80],
         notes={8: ("ខ្សោយ", OR, "top"), 9: ("ធ្លាក់", DN, "bottom")},
         vnotes={9: ("volume ↑", DN)},
         caption="តម្លៃនៅតែធ្វើ high ថ្មី ប៉ុន្តែ volume ធ្លាក់បន្តិចម្ដងៗ = អ្នកទិញអស់កម្លាំង → ទៀនធ្លាក់ volume ខ្ពស់") + """
<table><tr><th>តម្លៃ</th><th>Volume</th><th>អត្ថន័យទូទៅ</th></tr>
<tr><td>ឡើង</td><td>ឡើង ↑</td><td>ការចូលរួមខ្លាំង · ចលនាគួរឱ្យទុកចិត្ត</td></tr>
<tr><td>ឡើង</td><td>ធ្លាក់ ↓</td><td>ចូលរួមតិចឡើងៗ · ការឡើងអាចខ្សោយ</td></tr>
<tr><td>ធ្លាក់</td><td>ឡើង ↑</td><td>សម្ពាធលក់ខ្លាំង</td></tr>
<tr><td>ធ្លាក់</td><td>ធ្លាក់ ↓</td><td>ការធ្លាក់ខ្សោយ · ច្រើនជា pullback</td></tr></table>
"""),
        ("ទំនាក់ទំនង Volume និងតម្លៃ (២): Breakout និង Climax", """
<p><b>Breakout ជាមួយ volume ខ្ពស់</b> មានឱកាសពិតច្រើនជាង breakout ដែល volume ទាប។ Breakout volume ទាប ច្រើនតែជា
<span class='en-term'>liquidity sweep</span> ឬ <span class='en-term'>fakeout</span> (Chapter 12, 17)។</p>
""" + pv([(40, 50, 38, 46), (46, 52, 40, 42), (42, 50, 40, 48), (48, 52, 42, 44), (44, 51, 41, 47), (47, 70, 46, 68), (68, 80, 66, 78), (78, 82, 70, 74), (74, 88, 73, 86)],
         [40, 35, 38, 30, 34, 95, 80, 45, 70],
         lines=[(52, 0, 8, "Range high", GOLD)],
         notes={5: ("Breakout", UP, "top")}, vnotes={5: ("volume ខ្ពស់", UP)},
         caption="បិទលើ range high ជាមួយ displacement + volume ខ្ពស់ = breakout ដែលគួរឱ្យទុកចិត្តជាង") + """
<p><span class='en-term'>Climax volume</span> (volume ខ្ពស់ខុសធម្មតា) នៅ<b>ចុងនិន្នាការ</b>វែងមួយ ជួនកាលបង្ហាញថាអ្នកចុងក្រោយបានចូលអស់ហើយ (buying climax / selling climax)។
ទៀនមាន wick វែង + volume ធំបំផុត ក្រោយការធ្លាក់យូរ ច្រើនជា<b>សញ្ញាព្រមាន</b>ថាការធ្លាក់អាចនឹងយឺត។</p>
""" + pv([(88, 90, 78, 80), (80, 82, 68, 70), (70, 72, 60, 62), (62, 64, 50, 52), (52, 54, 42, 44), (44, 46, 14, 38), (38, 48, 36, 46), (46, 52, 42, 50), (50, 58, 48, 56)],
         [40, 45, 50, 55, 60, 100, 55, 40, 38],
         notes={5: ("Selling climax", OR, "bottom")}, vnotes={5: ("volume ធំបំផុត", OR)},
         caption="ក្រោយការធ្លាក់យូរ: wick វែងខាងក្រោម + volume ធំបំផុត → អ្នកលក់អាចអស់កម្លាំង") + """
<div class='box warn'>⚠️ Climax <b>មិនមែន</b>សញ្ញាទិញភ្លាមៗទេ។ តម្លៃអាចធ្លាក់បន្តទៀត។ យើងនៅតែត្រូវការ <b>MSS / CHOCH</b> (Chapter 9) មុននឹងគិតពីទិសផ្ទុយ។</div>
"""),
        ("Volume ពេលព័ត៌មាន", """
<p>ពេល 📰 <b>News</b> ធំៗ (CPI, NFP, FOMC) ចេញ volume លោតខ្ពស់បំផុតក្នុងប៉ុន្មាននាទី។ ទៀនដំបូងអាចមាន volume ច្រើនជាងទៀនធម្មតាច្រើនដង
ហើយតម្លៃអាចទៅទាំងពីរទិសក្នុងពេលតែមួយ (ម៉ោង 20:30 កម្ពុជា សម្រាប់ទិន្នន័យ US ភាគច្រើន)។</p>
<ul><li>Volume ខ្ពស់ពេលព័ត៌មាន <b>មិនបញ្ជាក់</b>ទិសដៅទេ: វាគ្រាន់តែបង្ហាញថាមនុស្សទាំងអស់កំពុង react</li>
<li><span class='en-term'>Spread</span> ច្រើនតែរីកធំ និងមាន <span class='en-term'>slippage</span> ពេលនោះ</li>
<li>ទៀនព័ត៌មានធ្វើឱ្យ Volume Profile នៃថ្ងៃនោះ "ធ្ងន់" នៅតំបន់មួយ: ត្រូវចងចាំនៅពេលអាន profile (Chapter 19)</li></ul>
<div class='box tip'>💡 XAU.KH មិនផ្ញើ 🚨 Signals នៅពេលព័ត៌មានធំទេ។ មើល 📰 News ក្នុង group មុនពេល trade រៀងរាល់ថ្ងៃ។</div>
"""),
        ("ដែនកំណត់នៃ Volume របស់ Broker", """
<p>មុនទុកចិត្ត volume ខ្លាំងពេក ត្រូវដឹងពីចំណុចខ្សោយរបស់វា:</p>
<table><tr><th>ដែនកំណត់</th><th>ហេតុអ្វីសំខាន់</th></tr>
<tr><td>Tick volume ខុសគ្នាតាម broker</td><td>Broker A និង B អាចបង្ហាញ "volume spike" នៅទៀនខុសគ្នា</td></tr>
<tr><td>មិនដឹងទំហំ order</td><td>Order 0.01 lot និង 100 lots រាប់ជា tick តែមួយដូចគ្នា</td></tr>
<tr><td>មិនបង្ហាញទិស</td><td>Volume = ទិញ = លក់ · ត្រូវអានតម្លៃដើម្បីដឹងទិស</td></tr>
<tr><td>Futures ≠ Spot</td><td>Basis ខុសគ្នា · ការប្ដូរ contract (<span class='en-term'>roll</span>) ធ្វើឱ្យ volume ផ្លាស់ទៅខែបន្ទាប់</td></tr>
<tr><td>ម៉ោងបើក/បិទ និងថ្ងៃឈប់សម្រាក</td><td>ទៀនដំបូងនៃសប្ដាហ៍ ឬថ្ងៃបុណ្យ US អាចមាន volume ខុសធម្មតា</td></tr>
<tr><td>ព័ត៌មាន</td><td>Volume spike មួយអាចធ្វើឱ្យ profile ខុសរូបរាង</td></tr></table>
""" + flow([("តម្លៃ", "structure ជាមុន", BL), ("ទីតាំង", "liquidity / zone", PU), ("Volume", "បញ្ជាក់ ឬព្រមាន", GOLD), ("សម្រេច", "trade ឬរង់ចាំ", UP)],
           caption="Volume ជា<b>ជំនួយ</b>ទីបី · មិនមែនសញ្ញាចូល trade ដោយខ្លួនឯង") + """
<div class='box warn'>⚠️ កុំសន្និដ្ឋានធំពី<b>ទៀនមួយ</b>ដែលមាន tick volume ខ្ពស់។ មើលលំនាំ (pattern) លើទៀនច្រើន និងប្រៀបធៀបជាមួយ structure ជានិច្ច។</div>
"""),
        ("ការអនុវត្តក្នុង MT5 និងក្នុង Group", """
<ul><li><b>MT5</b>: បន្ថែម <b>Volumes</b> ក្រោម chart XAUUSD 15m · សង្កេតមើលម៉ោង 14:00 (London) និង 19:30–20:30 (NY + News) ប្រៀបធៀបនឹងម៉ោង Asia</li>
<li>📊 <b>Analysis</b>: bar ខៀវតូចៗនៅគែមស្ដាំនៃរូប = <b>volume តាមតម្លៃ</b> (Volume Profile) ហើយបន្ទាត់ <b>POC</b> = តម្លៃដែលជួញដូរច្រើនបំផុត (Chapter 19)</li>
<li><b>/check</b>: មើល structure និងកម្រិតជិតតម្លៃ ហើយសួរខ្លួនឯងថា "ចលនានេះមាន volume គាំទ្រឬទេ?"</li>
<li><b>Signals</b> ដែលមានស្លាក <b>📊 Volume</b> ប្រើ Volume Profile ជាផ្នែកនៃច្បាប់ · 📈 <b>Proof</b> បង្ហាញលទ្ធផលពិតទាំងឈ្នះទាំងខាត</li></ul>
<p><b>កំហុសញឹកញាប់:</b></p>
<ul><li>❌ គិតថា volume ខ្ពស់ = អ្នកទិញឈ្នះ</li>
<li>❌ ប្រៀបធៀប tick volume រវាង broker ពីរ</li>
<li>❌ ប្រើកម្រិតពី futures ដោយមិនកែ basis</li>
<li>❌ ចូល trade ព្រោះ "volume spike" តែមួយ ដោយគ្មាន structure</li></ul>
"""),
    ],
    summary=["Volume = បរិមាណជួញដូរ · ទិញម្នាក់ = លក់ម្នាក់ · volume បង្ហាញកម្លាំង មិនមែនទិស",
             "Tick volume (MT5) = ចំនួនដងប្ដូរតម្លៃ · Real volume = contracts ពី exchange (COMEX GC)",
             "មាស spot ជា OTC · គ្មាន volume កណ្ដាល · futures volume ជាជំនួយ (ប្រយ័ត្ន basis)",
             "Effort vs Result: ឡើង + volume ↑ = ខ្លាំង · ឡើង + volume ↓ = ខ្សោយ · climax = ព្រមាន",
             "Volume ជាជំនួយទីបី ក្រោយ structure និងទីតាំង · កុំសន្និដ្ឋានពីទៀនតែមួយ"],
    exercise=["បន្ថែម Volumes ក្នុង MT5 លើ XAUUSD 15m។ កត់ត្រា tick volume មធ្យមនៅម៉ោង Asia (08:00–12:00) និង NY (20:00–23:00) រយៈពេល 3 ថ្ងៃ។",
              "រក breakout ពីរ: មួយមាន volume ខ្ពស់ មួយមាន volume ទាប។ តើមួយណាទៅបានឆ្ងាយជាង?",
              "រកកន្លែងមួយដែលតម្លៃធ្វើ high ថ្មី ប៉ុន្តែ volume ធ្លាក់។ តើបន្ទាប់មកមានអ្វីកើតឡើង?",
              "បើករូប 📊 Analysis ចុងក្រោយក្នុង group ហើយរក bar volume profile និងបន្ទាត់ POC។"],
)
