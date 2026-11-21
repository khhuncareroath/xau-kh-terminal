from academy_pdf import flow, bars, twolines
from academy_book.ch22 import ladders

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def pd_panel(price, delta, labels=None, line=None, w=420, h=210, caption="", dlabel="Delta"):
    """Price path on top, one delta bar per point underneath. price = [0-100]; delta = numbers (+/-).
    labels = {index: (text, colour)}; line = (y, text, colour) a dashed level on the price panel."""
    labels = labels or {}
    n = len(price)
    ph, top = 118, 10                       # price panel height
    X = lambda i: 50 + i * (w - 72) / (n - 1)
    Y = lambda v: top + ph - v * (ph - 16) / 100 - 6
    dz = top + ph + 16 + (h - top - ph - 24) / 2   # zero line of the delta panel
    dmax = max(abs(d) for d in delta) or 1
    ds = (h - top - ph - 30) / 2 / dmax
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<text x="6" y="{top + 10}" fill="{GR}" class="st">Price</text>',
           f'<text x="6" y="{dz - 4:.1f}" fill="{GR}" class="st">{dlabel}</text>',
           f'<line x1="26" x2="{w - 10}" y1="{dz:.1f}" y2="{dz:.1f}" stroke="#C7C7CC"/>',
           f'<line x1="26" x2="{w - 10}" y1="{top + ph + 6}" y2="{top + ph + 6}" stroke="#E5E5EA"/>']
    if line:
        y, t, col = line
        out.append(f'<line x1="26" x2="{w - 10}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        out.append(f'<text x="{w - 12}" y="{Y(y) + 13:.1f}" text-anchor="end" fill="{col}" class="lt">{t}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(price))
    out.append(f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linejoin="round"/>')
    bw = (w - 72) / n * 0.55
    for i, d in enumerate(delta):
        hh = abs(d) * ds
        y0 = dz - hh if d >= 0 else dz
        out.append(f'<rect x="{X(i) - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(hh, 1):.1f}" rx="2" fill="{UP if d >= 0 else DN}"/>')
    for i, (t, col) in labels.items():
        up = i == 0 or price[i] >= price[i - 1]
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(price[i]):.1f}" r="3.2" fill="{col}"/>')
        anc = "end" if X(i) > w - 60 else "start" if X(i) < 70 else "middle"
        out.append(f'<text x="{X(i):.1f}" y="{Y(price[i]) + (-9 if up else 17):.1f}" text-anchor="{anc}" fill="{col}" class="pt">{t}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def gbars(labels, a, b, la, lb, ca=BL, cb=GOLD, w=420, h=170, caption="", unit=""):
    """Grouped bars: two series side by side for each label (values >= 0)."""
    n = len(labels)
    vmax = max(max(a), max(b)) or 1
    base = h - 24
    sc = (h - 62) / vmax
    gw = (w - 30) / n
    bw = gw * 0.34
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="20" y="10" width="12" height="8" rx="2" fill="{ca}"/><text x="37" y="18" class="lt" fill="{ca}">{la}</text>',
           f'<rect x="{w / 2:.0f}" y="10" width="12" height="8" rx="2" fill="{cb}"/><text x="{w / 2 + 17:.0f}" y="18" class="lt" fill="{cb}">{lb}</text>',
           f'<line x1="14" x2="{w - 14}" y1="{base}" y2="{base}" stroke="#C7C7CC"/>']
    for i, lab in enumerate(labels):
        cx = 15 + (i + .5) * gw
        for k, (v, col) in enumerate([(a[i], ca), (b[i], cb)]):
            x = cx - bw - 1 if k == 0 else cx + 1
            out.append(f'<rect x="{x:.1f}" y="{base - v * sc:.1f}" width="{bw:.1f}" height="{max(v * sc, 1):.1f}" rx="2" fill="{col}"/>')
            if unit is not None and n <= 8:
                out.append(f'<text x="{x + bw / 2:.1f}" y="{base - v * sc - 4:.1f}" text-anchor="middle" fill="{col}" class="st">{v:g}{unit}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h - 8}" text-anchor="middle" fill="#6E6E73" class="st">{lab}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def edge_rows(w=420, h=150, caption=""):
    """Top rows of two up-candles' footprints: a 'finished auction' (exhaustion) vs strong buying at the high."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    sets = [("Exhaustion ✓", [("4,131.0", 0, 2), ("4,130.5", 6, 9), ("4,130.0", 22, 31), ("4,129.5", 48, 95)], DN,
             "Ask នៅកំពូលស្ទើរសូន្យ"),
            ("Buyers នៅខ្លាំង", [("4,131.0", 18, 96), ("4,130.5", 30, 140), ("4,130.0", 41, 120), ("4,129.5", 50, 88)], UP,
             "Ask ធំរហូតដល់កំពូល")]
    for k, (title, rows, col, note) in enumerate(sets):
        x0 = 12 + k * 206
        out.append(f'<text x="{x0 + 96}" y="17" text-anchor="middle" fill="{col}" class="bt">{title}</text>')
        for i, (p, b, a) in enumerate(rows):
            y = 26 + i * 23
            out.append(f'<text x="{x0 + 50}" y="{y + 15}" text-anchor="end" fill="{GR}" class="st">{p}</text>')
            out.append(f'<rect x="{x0 + 56}" y="{y}" width="122" height="19" rx="3" fill="#F7F7FA"'
                       + (f' stroke="{col}" stroke-width="1.6"' if i == 0 else "") + "/>")
            out.append(f'<text x="{x0 + 106}" y="{y + 14}" text-anchor="end" fill="#3A3A3C" class="lt">{b}</text>')
            out.append(f'<text x="{x0 + 117}" y="{y + 14}" text-anchor="middle" fill="{GR}" class="st">×</text>')
            out.append(f'<text x="{x0 + 128}" y="{y + 14}" fill="#3A3A3C" class="lt">{a}</text>')
        out.append(f'<text x="{x0 + 117}" y="{h - 12}" text-anchor="middle" fill="{col}" class="st">{note}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


# Real data: COMEX gold futures 5m (data/gc_5m.csv.gz), week of 9-13 Nov 2026, closes every 2 h, and the
# candle-estimated CVD of cvd.delta() reset at the start of that week (thousands of contracts).
WK_PX = [4064, 4133, 4125, 4131, 4095, 4106, 4118, 4134, 4130, 4111, 4146, 4150, 4148, 4138, 4120, 4132, 4121, 4096, 4082, 4060,
         4050, 4026, 4037, 4040, 4046, 4053, 4054, 4066, 4067, 4058, 4052, 4046, 4013, 4000, 3994, 3994, 3984, 3991, 3988, 3985,
         3970, 3949, 3950, 3895, 3875, 3878, 3889, 3882, 3885, 3912, 3924, 3908, 3902, 3906, 3897, 3885, 3877, 3889, 3879, 3886]
WK_CVD = [-1.3, 9.2, 10.0, 11.2, 4.0, 6.9, 8.9, 9.7, 12.7, 10.9, 31.4, 29.5, 30.3, 29.4, 27.6, 29.2, 27.7, 18.7, 17.0, 12.2, 11.4,
          2.5, 8.1, 8.3, 8.7, 12.7, 14.0, 18.8, 16.3, 14.5, 14.1, 10.4, -0.5, -7.8, -8.8, -9.0, -9.7, -9.0, -10.3, -9.9, -11.4,
          -14.4, -12.9, -36.3, -51.3, -48.8, -41.0, -45.0, -43.6, -41.9, -40.7, -43.1, -47.0, -48.6, -49.7, -50.5, -54.2, -56.7,
          -62.7, -61.7]


CH = dict(
    ch=24, part="PART 5 · Order Flow Intelligence",
    title_km="Order Flow កម្រិតខ្ពស់", title_en="Advanced Order Flow: Absorption · Exhaustion · Delta Divergence · CVD · DOM",
    intro="""ក្នុង Chapter 23 អ្នកបានរៀនអាន footprint: <span class='en-term'>Bid × Ask</span>, <span class='en-term'>delta</span> និង
<span class='en-term'>imbalance</span>។ ជំពូកនេះទៅមួយជំហានទៀត: យើងរៀនអាន<b>ពេលដែល order flow និងតម្លៃមិនស្របគ្នា</b>។
នោះហើយជាកន្លែងដែលព័ត៌មានសំខាន់បំផុតលាក់ខ្លួន: <span class='en-term'>absorption</span>, <span class='en-term'>exhaustion</span>,
<span class='en-term'>delta divergence</span>, <span class='en-term'>CVD</span>, <span class='en-term'>iceberg orders</span>,
<span class='en-term'>pulling/stacking</span> និង <span class='en-term'>DOM</span>។
លេខក្នុងរូបភាគច្រើនជា<b>ឧទាហរណ៍សម្រាប់រៀន</b> · រូបណាដែលប្រើទិន្នន័យពិត យើងសរសេរប្រាប់ច្បាស់។""",
    sections=[
        ("Absorption: អ្នកធំស្រូប", """
<p><span class='en-term'>Absorption</span> (ការស្រូប) កើតឡើងពេល <b>aggressive orders ច្រើនណាស់</b> វាយចូលកម្រិតមួយ
ប៉ុន្តែតម្លៃ<b>មិនរំកិល</b>។ មូលហេតុ: មាន <b>passive limit orders ធំ</b> នៅកម្រិតនោះ ដែលទទួលយក (ស្រូប) market orders ទាំងអស់។</p>
""" + pd_panel([80, 66, 52, 38, 26, 22, 24, 21, 23, 22, 34, 50, 64],
               [-40, -55, -60, -70, -90, -150, -170, -160, -140, 30, 80, 95, 70],
               labels={5: ("Absorption", BL), 12: ("Reversal", UP)}, line=(22, "Support 4,100", BL),
               caption="Delta អវិជ្ជមានធំខ្លាំង (sellers វាយ) ប៉ុន្តែតម្លៃឈប់ធ្លាក់នៅ 4,100 → limit buyers ស្រូប → sellers អស់កម្លាំង → តម្លៃឡើង") + """
<p><b>សញ្ញាសម្គាល់ absorption ខាងទិញ</b> (bullish absorption):</p>
<ul><li>Volume <b>ធំខុសប្លែក</b> នៅកម្រិតតែមួយ ឬជួរតូចមួយ</li>
<li>Delta <b>អវិជ្ជមានធំ</b> (market sell ច្រើន) ប៉ុន្តែទៀន<b>តូច</b> ឬមាន wick ក្រោមវែង</li>
<li>តម្លៃ<b>មិនបិទក្រោម</b>កម្រិតនោះ ទោះ sellers វាយច្រើនដង</li>
<li>កើតនៅ<b>ទីតាំងសំខាន់</b>: VAL, Order Block, Swing Low ឬលេខមូល</li></ul>
<div class='box tip'>💡 Absorption ខាងលក់ (bearish) គឺផ្ទុយ: delta <b>វិជ្ជមានធំ</b> នៅ resistance ប៉ុន្តែតម្លៃមិនឡើង ព្រោះ limit sellers ធំស្រូប market buy។</div>
<div class='box warn'>⚠️ Absorption <b>មិនមែនជា entry ភ្លាមៗ</b>ទេ។ Limit buyers ធំអាចត្រូវគេស៊ីអស់ ហើយតម្លៃធ្លាក់ទម្លុះ។
រង់ចាំភស្តុតាងថា sellers <b>អស់កម្លាំង</b> ហើយតម្លៃចាប់ផ្ដើមបង្វិល (ឧ. MSS លើ 5m ដូច Chapter 9)។</div>
"""),
        ("Exhaustion: កម្លាំងអស់", """
<p><span class='en-term'>Exhaustion</span> (ការអស់កម្លាំង) ខុសពី absorption។ នៅទីនេះ<b>គ្មាន</b>អ្នកណាមកបញ្ឈប់តម្លៃទេ
គឺ aggressive buyers (ឬ sellers) <b>អស់អ្នកចូលថ្មី</b>។ តម្លៃនៅតែធ្វើ high ថ្មី ប៉ុន្តែដោយ volume និង delta <b>ថយចុះ</b>ម្ដងហើយម្ដងទៀត។</p>
""" + pd_panel([20, 45, 36, 62, 54, 76, 70, 84, 80, 60, 40],
               [120, 140, -30, 95, -25, 60, -20, 25, -40, -110, -130],
               labels={1: ("Push 1", UP), 3: ("Push 2", OR), 5: ("Push 3", OR), 7: ("Push 4", DN)},
               caption="ជំរុញឡើងម្ដងៗ delta តូចជាងមុន (140 → 95 → 60 → 25) · ចុងក្រោយគ្មានអ្នកទិញថ្មី → តម្លៃធ្លាក់ត្រឡប់") + """
<p>នៅក្នុង footprint, exhaustion ច្រើនបង្ហាញនៅ<b>ចុងទៀន</b>: លេខ Ask នៅកំពូលនៃទៀនឡើង<b>តូចបំផុត</b> (ឧ. 0 ឬ 2 contracts)។
អ្នកខ្លះហៅថា <span class='en-term'>finished auction</span>: ការដេញថ្លៃបានបញ្ចប់ ព្រោះគ្មានអ្នកចង់ទិញថ្លៃជាងនេះ។</p>
""" + edge_rows(caption="ជួរខាងលើនៃទៀនឡើងពីរ (ឧទាហរណ៍) · ឆ្វេង: Ask ថយចុះដល់ 2 នៅកំពូល = exhaustion · ស្ដាំ: Ask នៅធំ = buyers នៅមាន") + """
<table style="break-inside: avoid"><tr><th></th><th>Absorption</th><th>Exhaustion</th></tr>
<tr><td>Volume នៅចុង move</td><td><b>ធំ</b></td><td><b>តូច</b> (ស្ងាត់)</td></tr>
<tr><td>មូលហេតុ</td><td>Passive orders ធំបញ្ឈប់</td><td>Aggressive orders អស់</td></tr>
<tr><td>Delta</td><td>ធំ ប៉ុន្តែតម្លៃមិនទៅ</td><td>ថយចុះម្ដងៗ</td></tr>
<tr><td>ឧទាហរណ៍ចិត្តសាស្ត្រ</td><td>ជញ្ជាំង</td><td>ឡានអស់សាំង</td></tr></table>
"""),
        ("Buying Pressure និង Selling Pressure", """
<p><span class='en-term'>Buying pressure</span> = កម្លាំងរបស់ <b>aggressive buyers</b> · <span class='en-term'>Selling pressure</span> = កម្លាំងរបស់
<b>aggressive sellers</b>។ ចាំថា ចំនួនទិញ = ចំនួនលក់ជានិច្ច (Chapter 22)។ "Pressure" មិនមែនជាចំនួនអ្នកទិញច្រើនជាងទេ
គឺជា<b>អ្នកណាប្រញាប់ជាង</b> និង<b>ប្រញាប់ប៉ុណ្ណា</b>។</p>
<table style="break-inside: avoid"><tr><th>រង្វាស់</th><th>Buying pressure ខ្លាំង</th></tr>
<tr><td>Delta នៃទៀន</td><td>វិជ្ជមានធំ ជាប់គ្នាច្រើនទៀន</td></tr>
<tr><td>Delta % (Delta ÷ Volume)</td><td>ខ្ពស់ (ឧ. លើស 25–30%)</td></tr>
<tr><td>Imbalance</td><td>Stacked buy imbalances (Chapter 23)</td></tr>
<tr><td>ល្បឿន</td><td>តម្លៃឆ្លងច្រើនកម្រិតលឿន (displacement)</td></tr>
<tr><td>Pullback</td><td>Delta អវិជ្ជមានតូច · តម្លៃមិនធ្លាក់ជ្រៅ</td></tr></table>
""" + bars([("1", 180, UP), ("2", 240, UP), ("3", 150, UP), ("4", -40, DN), ("5", -25, DN), ("6", 210, UP), ("7", 160, UP)],
           caption="Delta នៃ 7 ទៀនក្នុង trend ឡើង (ឧទាហរណ៍) · pullback (4–5) មាន delta អវិជ្ជមាន<b>តូច</b> = selling pressure ខ្សោយ") + """
<div class='box ok'>✅ ការអានល្អ: ក្នុង trend ឡើងដែលមានសុខភាពល្អ delta វិជ្ជមានធំពេលឡើង ហើយ delta អវិជ្ជមាន<b>តូច</b>ពេល pullback។
បើ pullback ចាប់ផ្ដើមមាន delta អវិជ្ជមាន<b>ធំជាង</b>ពេលឡើង នោះ selling pressure កំពុងកើនឡើង។</div>
"""),
        ("Delta Divergence", """
<p><span class='en-term'>Delta divergence</span> = តម្លៃ និង delta <b>និយាយរឿងខុសគ្នា</b>។ ឧទាហរណ៍ពេញនិយម:
តម្លៃធ្វើ <span class='en-term'>Higher High</span> ប៉ុន្តែ delta នៃទៀននោះ<b>ខ្សោយជាង</b> high មុន ឬថែមទាំង<b>អវិជ្ជមាន</b>។</p>
""" + pd_panel([30, 55, 70, 58, 48, 62, 78, 64, 46, 32],
               [60, 130, 170, -60, -40, 50, -35, -90, -120, -80],
               labels={2: ("High 1", OR), 6: ("High 2 (HH)", DN)},
               caption="High 2 ខ្ពស់ជាង High 1 ប៉ុន្តែ delta នៅ High 2 អវិជ្ជមាន (−35 ធៀបនឹង +170) → buyers មិនបានរុញ high ថ្មីនោះ") + """
<table style="break-inside: avoid"><tr><th>តម្លៃ</th><th>Delta</th><th>ការអាន</th></tr>
<tr><td>Higher High</td><td>ខ្សោយជាង ឬ −</td><td><b>Bearish divergence</b> · buyers ខ្សោយ · ប្រហែលជា sweep នៃ buy stops</td></tr>
<tr><td>Lower Low</td><td>ខ្សោយជាង ឬ +</td><td><b>Bullish divergence</b> · sellers ខ្សោយ · ប្រហែលជា sweep នៃ sell stops</td></tr></table>
<div class='box tip'>💡 Delta divergence នៅលើ swing high ច្រើនកើតឡើងជាមួយ <b>liquidity sweep</b> (Chapter 12): តម្លៃទម្លុះ high ដោយ stops
ក្លាយជា market buy (Chapter 22) ប៉ុន្តែគ្មាន buyers ថ្មីបន្ត។ បើបន្ទាប់មាន MSS ចុះ នោះ story កាន់តែច្បាស់។</div>
<div class='box warn'>⚠️ ក្នុង trend ខ្លាំង divergence អាចកើតច្រើនដង ហើយតម្លៃនៅតែបន្ត។ Divergence តែមួយ<b>មិនគ្រប់គ្រាន់</b>សម្រាប់ trade បញ្ច្រាស trend ទេ។</div>
"""),
        ("Cumulative Volume Delta (CVD)", """
<p><span class='en-term'>CVD</span> = delta នៃទៀននីមួយៗ <b>បូកបន្តគ្នា</b>។ វាបង្ហាញទិសនៃ aggression ក្នុងរយៈពេលវែងជាងទៀនមួយ។
CVD ច្រើនត្រូវ <b>reset</b> (ចាប់ផ្ដើមពី 0) នៅដើម session, ដើមថ្ងៃ ឬដើមសប្ដាហ៍។</p>
<table style="break-inside: avoid"><tr><th>ទៀន</th><th>Delta</th><th>CVD</th></tr>
<tr><td>1</td><td>+120</td><td>+120</td></tr><tr><td>2</td><td>+80</td><td>+200</td></tr>
<tr><td>3</td><td>−50</td><td>+150</td></tr><tr><td>4</td><td>+90</td><td>+240</td></tr>
<tr><td>5</td><td>−200</td><td>+40</td></tr></table>
""" + twolines(WK_PX, WK_CVD, "COMEX gold (តម្លៃ)", "CVD ប៉ាន់ស្មាន",
               caption="ទិន្នន័យពិត: COMEX gold futures 5m សប្ដាហ៍ 9–13 Nov 2026 (ចំណុចរៀងរាល់ 2 ម៉ោង) · CVD ប៉ាន់ស្មានពីទៀន (cvd.py) reset ដើមសប្ដាហ៍ · "
                       "ខ្សែទាំងពីរមានមាត្រដ្ឋានរៀងៗខ្លួន · តម្លៃពី ~4,150 ធ្លាក់ដល់ ~3,880 ហើយ CVD ធ្លាក់ស្របគ្នា") + """
<ul><li><b>CVD ស្របនឹងតម្លៃ</b> (ដូចរូបខាងលើ) = aggressive sellers កំពុងដឹកនាំ · move មាន "កម្លាំងពិត"</li>
<li><b>CVD divergence</b> = តម្លៃធ្វើ high/low ថ្មី ប៉ុន្តែ CVD មិនធ្វើ · គំនិតដូចផ្នែក 4 ប៉ុន្តែលើច្រើនទៀន</li></ul>
<p>XAU.KH មានម៉ូឌុល CVD ផ្ទាល់ខ្លួន (cvd.py) ដែលដាក់ស្លាកបួនប្រភេទ:</p>
<table style="break-inside: avoid"><tr><th>តម្លៃ</th><th>CVD</th><th>ស្លាក</th></tr>
<tr><td>Lower Low</td><td>Higher Low</td><td>EXH bull · selling exhaustion</td></tr>
<tr><td>Higher Low</td><td>Lower Low</td><td>ABS bull · selling absorbed</td></tr>
<tr><td>Higher High</td><td>Lower High</td><td>EXH bear · buying exhaustion</td></tr>
<tr><td>Lower High</td><td>Higher High</td><td>ABS bear · buying absorbed</td></tr></table>
<div class='box warn'>⚠️ <b>ការពិតពីការសាកល្បងរបស់យើង</b>: លើទិន្នន័យ 15m រយៈពេល 2 ឆ្នាំ ស្លាក CVD ទាំងនេះ<b>តែឯង</b> មានតម្លៃទៅតាមទិសស្លាក $10 មុន
ប្រហែល <b>49%</b> នៃពេល · ស្មើនឹងបោះកាក់។ ដូច្នេះ XAU.KH ប្រើ CVD ត្រឹមជា<b>ព័ត៌មាន</b> មិនមែនជា signal ទេ។
ហេតុផលមួយ: delta របស់យើងត្រូវ<b>ប៉ាន់ស្មាន</b>ពីទៀន (បិទឡើង = ទិញ · បិទចុះ = លក់) ព្រោះគ្មាន Bid/Ask volume ពិត (Chapter 25)។</div>
"""),
        ("Iceberg Orders និងដែនកំណត់នៃការរកឃើញ", """
<p><span class='en-term'>Iceberg order</span> = limit order ធំ ដែលបង្ហាញលើ DOM <b>តែផ្នែកតូចមួយ</b>។ ពេលផ្នែកនោះត្រូវគេស៊ីអស់
វា <b>បំពេញឡើងវិញ</b> (refill) ដោយស្វ័យប្រវត្តិ។ អ្នកធំប្រើវាដើម្បីលាក់ទំហំពិតរបស់ខ្លួន។</p>
""" + gbars(["T1", "T2", "T3", "T4", "T5", "T6"], [20, 20, 20, 20, 20, 20], [20, 40, 60, 80, 100, 120],
            "ឃើញលើ DOM", "បានស៊ីសរុប", ca=BL, cb=DN,
            caption="Iceberg limit sell នៅ 4,125.0 (ឧទាហរណ៍) · DOM បង្ហាញតែ 20 contracts ជានិច្ច · តែតាមពិតបានលក់ 120 contracts ហើយតម្លៃមិនឡើងហួស") + """
<p><b>របៀបសង្ស័យថាមាន iceberg:</b> volume ដែល<b>បានជួញដូរ</b>នៅតម្លៃមួយ (មើលក្នុង footprint ឬ <span class='en-term'>Time &amp; Sales</span>)
<b>ធំជាងច្រើនដង</b> នូវ size ដែលបង្ហាញលើ DOM ហើយ size នោះត្រឡប់មកវិញម្ដងហើយម្ដងទៀត។ វាជាប្រភេទមួយនៃ absorption (ផ្នែក 1)។</p>
<div class='box warn'>⚠️ <b>ដែនកំណត់</b>:
<ul><li>យើងដឹងតែ<b>ក្រោយ</b>ពីវាត្រូវគេស៊ីរួចហើយ · មិនអាចឃើញទំហំដែលនៅសល់ទេ</li>
<li>Algorithm ជាច្រើនបំបែក order ធំជាផ្នែកតូចៗ តាមរបៀបផ្សេង · មើលទៅដូច iceberg តែមិនមែន ឬផ្ទុយមកវិញ</li>
<li>Tool "iceberg detector" គ្រាន់តែ<b>ទាយ</b>ពីលំនាំ · វាអាចខុសបាន</li>
<li>ត្រូវការទិន្នន័យ exchange real-time (futures) · <b>មិនអាចរកឃើញលើ XAUUSD CFD ក្នុង MT5 ទេ</b></li></ul></div>
"""),
        ("Liquidity Pulling និង Stacking", """
<p>Limit orders លើ DOM មិនឋិតឋេរទេ។ <span class='en-term'>Pulling</span> = limit orders ត្រូវ<b>ដកចេញ</b>ពេលតម្លៃខិតជិត ·
<span class='en-term'>Stacking</span> = limit orders ត្រូវ<b>ដាក់បន្ថែម</b>ជាបន្តបន្ទាប់។</p>
""" + ladders([("មុន", [("4,121.0", 0, 60, ""), ("4,120.8", 0, 12, ""), ("4,120.6", 0, 10, "Ask →"), ("4,120.4", 11, 0, "← Bid"),
                        ("4,120.2", 14, 0, ""), ("4,120.0", 55, 0, "")]),
               ("15 វិនាទីក្រោយ", [("4,121.0", 0, 6, "pulled"), ("4,120.8", 0, 8, ""), ("4,120.6", 0, 9, ""), ("4,120.4", 25, 0, ""),
                                  ("4,120.2", 38, 0, "stacked"), ("4,120.0", 70, 0, "")])],
              caption="Limit sellers 60 នៅ 4,121.0 ត្រូវដកចេញ (pulled) · limit buyers ខាងក្រោមកើនឡើង (stacked) → ផ្លូវឡើងទំនេរជាង (ឧទាហរណ៍)") + """
<ul><li><b>Pulling នៅខាងលក់</b> ពេលតម្លៃខិតជិត = sellers មិនចង់ការពារកម្រិតនោះ · តម្លៃអាចឆ្លងបានស្រួល</li>
<li><b>Stacking នៅខាងទិញ</b> ក្រោមតម្លៃ = buyers ចង់ការពារ · ប៉ុន្តែពួកគេអាចដកចេញវិញនៅពេលណាក៏បាន</li>
<li>Order ធំៗដែលបង្ហាញ ហើយដកចេញភ្លាមៗពេលតម្លៃមកដល់ អាចជា <span class='en-term'>spoofing</span> (ខុសច្បាប់ ប៉ុន្តែនៅតែកើតមាន)</li></ul>
<div class='box tip'>💡 ច្បាប់មាស: <b>DOM = បំណង</b> · <b>Trades = ការពិត</b>។ ទុកចិត្តអ្វីដែលបានជួញដូរ (footprint, delta) ច្រើនជាងអ្វីដែលគ្រាន់តែបង្ហាញលើ book។</div>
"""),
        ("Depth of Market (DOM)", """
<p><span class='en-term'>DOM</span> (ឬ <span class='en-term'>order book</span>, <span class='en-term'>price ladder</span>) បង្ហាញ limit orders ដែលកំពុងរង់ចាំ
នៅតម្លៃនីមួយៗ (Chapter 22)។ អ្នក trade order flow ជំនាញអាន DOM <b>រួមជាមួយ</b> trades ដែលកើតឡើងពិត។</p>
<table style="break-inside: avoid"><tr><th>អ្វីដែលឃើញលើ DOM</th><th>អាចមានន័យ</th><th>ប្រុងប្រយ័ត្ន</th></tr>
<tr><td>Size ធំខុសប្លែកនៅកម្រិតមួយ</td><td>កម្រិតការពារ · S/R រយៈខ្លី</td><td>អាចដកចេញ / spoof</td></tr>
<tr><td>Size ធំត្រូវស៊ីបន្តិចម្ដងៗ</td><td>Absorption កំពុងកើត</td><td>បើស៊ីអស់ → breakout លឿន</td></tr>
<tr><td>Size បំពេញឡើងវិញរហូត</td><td>Iceberg?</td><td>ដឹងតែក្រោយ</td></tr>
<tr><td>Book ស្ដើង (size តូច)</td><td>តម្លៃអាចរត់លឿន</td><td>Slippage ខ្ពស់ (ពេល 📰 News)</td></tr></table>
<div class='box warn'>⚠️ <b>DOM ក្នុង MT5 សម្រាប់ XAUUSD</b>: broker CFD ភាគច្រើនបង្ហាញ <b>quotes របស់ broker ផ្ទាល់</b> (ឬ liquidity providers របស់គេ)
មិនមែន order book របស់ exchange ទេ។ វាមិនអាចប្រើវិភាគ pulling, stacking ឬ iceberg ដូចក្នុង futures បានទេ។ យើងនឹងពន្យល់លម្អិតក្នុង Chapter 25។</div>
"""),
        ("Workflow: ដាក់វាទាំងអស់ចូលគ្នា", """
<p>Order flow កម្រិតខ្ពស់ក៏នៅតែជា<b>ឧបករណ៍បញ្ជាក់</b>នៅទីតាំងល្អ ដូចដែលបានរៀនក្នុង Chapter 23។</p>
""" + flow([("Bias", "HTF structure", PU), ("Location", "OB · FVG · VAL", GOLD), ("Read", "absorb · exhaust", BL),
            ("Confirm", "MSS · CVD", UP), ("Risk", "SL · RR", DN)],
           caption="ទិសដៅ → ទីតាំង → អាន order flow នៅទីតាំងនោះ → ការបញ្ជាក់ដោយ structure → គ្រប់គ្រងហានិភ័យ") + """
<p><b>ឧទាហរណ៍គំនិត (លក់):</b> Daily bias ចុះ · តម្លៃឡើងមក sweep Asia High ដែលស្របនឹង bearish FVG លើ 1H · នៅ high ថ្មីនោះ delta <b>ខ្សោយ</b>
(delta divergence) ហើយ Ask នៅកំពូលស្ទើរសូន្យ (exhaustion) · ទៀន 5m បិទ MSS ចុះ → ទើបពិចារណាលក់ ជាមួយ SL លើ high ដែលបាន sweep។
នៅពេល 🚨 <b>Signal</b> ក្នុង group ចូលក្រោយ sweep អ្នកអាចស្រមៃឃើញ story បែបនេះនៅខាងក្នុងទៀន។</p>
<div class='box ok'>✅ ល្អ: មើល order flow នៅ<b>ចំណុចសម្រេចចិត្ត</b> ២–៣ កន្លែងប៉ុណ្ណោះក្នុងមួយថ្ងៃ (កម្រិតដែលអ្នកបានគូសពីមុន ឬមើលក្នុងរូប 📊 <b>Analysis</b>)។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ ច្រឡំ absorption (volume <b>ធំ</b> · តម្លៃមិនទៅ) ជាមួយ exhaustion (volume <b>តូច</b> · កម្លាំងអស់)</li>
<li>❌ ចូលបញ្ច្រាស trend ភ្លាមៗ ពេលឃើញ delta divergence តែមួយ</li>
<li>❌ គិតថា CVD divergence ជា signal ដែលឈ្នះច្រើន (ការសាកល្បងរបស់យើង: ស្មើនឹងបោះកាក់ពេលប្រើតែឯង)</li>
<li>❌ ជឿ size ធំលើ DOM 100% (pulling / spoofing)</li>
<li>❌ យក DOM ឬ tick volume របស់ broker CFD មកអានដូចទិន្នន័យ exchange</li></ul>
"""),
    ],
    summary=["Absorption = aggressive orders ច្រើន ប៉ុន្តែតម្លៃមិនទៅ · passive orders ធំស្រូប · volume ធំ",
             "Exhaustion = high/low ថ្មីដោយ delta និង volume ថយចុះ · Ask/Bid ស្ទើរសូន្យនៅចុងទៀន (finished auction)",
             "Delta divergence = តម្លៃ HH/LL តែ delta ខ្សោយ · CVD = delta បូកបន្ត · ប្រើជាព័ត៌មាន មិនមែន signal តែឯង",
             "Iceberg = order ធំលាក់ size · ដឹងតែក្រោយ · Pulling/Stacking = book ប្ដូររហូត · DOM = បំណង, Trades = ការពិត",
             "ទាំងអស់នេះត្រូវការទិន្នន័យ futures ពិត · ប្រើតែនៅទីតាំងល្អ ជាមួយ MSS និង SL ជានិច្ច"],
    exercise=["ទៀន 5m នៅ VAL: volume ធំជាងមធ្យម 3 ដង · delta = −420 · ទៀនបិទជិត open ហើយមាន wick ក្រោមវែង។ វាជា absorption ឬ exhaustion? ហេតុអ្វី?",
              "បំពេញ CVD: delta នៃ 6 ទៀន = +60, +90, −30, −150, +40, −80។ CVD ចុងក្រោយប៉ុន្មាន? (reset ពី 0)",
              "តម្លៃធ្វើ Lower Low នៅ 4,088 ប៉ុន្តែ delta នៃទៀននោះ = +35 ធៀបនឹង −210 នៅ low មុន។ សរសេរការអាន និងអ្វីដែលអ្នកនឹងរង់ចាំមុនទិញ។",
              "ពន្យល់ដោយពាក្យរបស់អ្នក ហេតុអ្វី DOM របស់ XAUUSD ក្នុង MT5 មិនអាចប្រើរក iceberg បាន។"],
)
