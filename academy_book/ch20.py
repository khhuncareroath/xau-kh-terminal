from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def profile(rows, poc=None, va=None, marks=None, w=420, rh=17, caption=""):
    """Horizontal volume-at-price histogram (same look as Chapter 19). rows = [(price, volume)] top to bottom."""
    marks = marks or {}
    h = 24 + len(rows) * rh
    vmax = max(v for _, v in rows)
    x0, wmax = 68, 190
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    if va:
        ys = [12 + i * rh for i, (p, _) in enumerate(rows) if va[0] <= p <= va[1]]
        out.append(f'<rect x="8" y="{min(ys) - 1}" width="{w - 16}" height="{max(ys) - min(ys) + rh + 2}" rx="6" fill="{BL}" fill-opacity=".07"/>')
    for i, (p, v) in enumerate(rows):
        y = 12 + i * rh
        inva = va and va[0] <= p <= va[1]
        col = GOLD if p == poc else (BL if inva else "#AEAEB2")
        out.append(f'<text x="{x0 - 8}" y="{y + rh - 5}" text-anchor="end" fill="#3A3A3C" class="lt">{p:,}</text>')
        out.append(f'<rect x="{x0}" y="{y + 2}" width="{max(v / vmax * wmax, 2):.1f}" height="{rh - 4}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{x0 + v / vmax * wmax + 5:.1f}" y="{y + rh - 5}" fill="{GR}" class="st">{v}</text>')
        if p in marks:
            t, mc = marks[p]
            out.append(f'<text x="{w - 14}" y="{y + rh - 5}" text-anchor="end" fill="{mc}" class="lt">{t}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def _side_profile(out, x_right, Y, prof, poc_v, scale=3.2, va=None, col=BL, bh=8):
    """Draws a small profile whose bars grow LEFT from x_right. prof = {level 0-100: volume}."""
    for v, q in prof.items():
        inva = va is None or va[0] <= v <= va[1]
        c = GOLD if v == poc_v else (col if inva else "#C7C7CC")
        bw = q * scale
        out.append(f'<rect x="{x_right - bw:.1f}" y="{Y(v) - bh / 2:.1f}" width="{bw:.1f}" height="{bh}" rx="2" fill="{c}" fill-opacity="{1 if v == poc_v else .6}"/>')


# One shared teaching price path (not real data): a range low, an impulse up, then a new range high.
PATH = [30, 36, 28, 34, 26, 33, 29, 35, 31, 44, 58, 66, 76, 72, 80, 74, 78, 73, 79, 75, 77]


def range_compare(w=420, h=200, caption=""):
    """Same price path, two different profile windows -> two different POCs."""
    top, bot = 16, h - 26
    Y = lambda v: bot - v * (bot - top) / 100
    n = len(PATH)
    X = lambda i: 16 + i * 250 / (n - 1)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{X(12):.1f}" y="{top - 6}" width="{X(n - 1) - X(12) + 4:.1f}" height="{bot - top + 12}" rx="6" fill="{OR}" fill-opacity=".08"/>']
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(PATH))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    # A: whole window profile (two humps, POC low because the low range lasted longer)
    full = {84: 2, 78: 10, 74: 12, 70: 6, 64: 3, 58: 2, 50: 1, 44: 2, 38: 6, 34: 12, 30: 16, 26: 8}
    _side_profile(out, w - 80, Y, full, 30, scale=4.3, bh=5.5)
    out.append(f'<text x="{w - 80 - 16 * 4.3 - 4:.1f}" y="{Y(30) + 4:.1f}" text-anchor="end" fill="{GOLD}" class="lt">POC A</text>')
    # B: only the last part (orange window)
    last = {84: 3, 78: 14, 74: 16, 70: 5}
    _side_profile(out, w - 10, Y, last, 74, scale=3.9, col=OR, bh=5.5)
    out.append(f'<text x="{w - 12}" y="{Y(74) + 22:.1f}" text-anchor="end" fill="{OR}" class="lt">POC B</text>')
    out.append(f'<text x="{w - 116}" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">A = ទាំងអស់</text>')
    out.append(f'<text x="{w - 34}" y="{h - 8}" text-anchor="middle" fill="{OR}" class="st">B = ផ្ទៃទឹកក្រូច</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def fixed_range(w=420, h=200, caption=""):
    """Fixed Range VP from the swing low to the swing high of one impulse leg: the LVN shows where the leg was fast."""
    top, bot = 16, h - 26
    Y = lambda v: bot - v * (bot - top) / 100
    pts = [40, 30, 22, 28, 24, 30, 26, 46, 62, 70, 80, 76, 82, 78, 70, 64]
    n = len(pts)
    X = lambda i: 16 + i * 260 / (n - 1)
    a, b = 4, 12
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<rect x="{X(a):.1f}" y="{Y(82) - 4:.1f}" width="{X(b) - X(a):.1f}" height="{Y(24) - Y(82) + 8:.1f}" rx="6" fill="{PU}" fill-opacity=".08" stroke="{PU}" stroke-dasharray="4 3"/>']
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    for i, t in [(a, "ចាប់ផ្ដើម"), (b, "បញ្ចប់")]:
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(pts[i]):.1f}" r="3.4" fill="{PU}"/>')
    out.append(f'<text x="{X(a):.1f}" y="{Y(24) + 18:.1f}" text-anchor="middle" fill="{PU}" class="st">ចាប់ផ្ដើម (swing low)</text>')
    out.append(f'<text x="{X(b):.1f}" y="{Y(82) - 9:.1f}" text-anchor="middle" fill="{PU}" class="st">បញ្ចប់ (swing high)</text>')
    prof = {82: 6, 78: 13, 74: 9, 68: 3, 62: 2, 56: 1, 50: 1, 44: 2, 38: 4, 32: 9, 28: 14, 24: 7}
    _side_profile(out, w - 12, Y, prof, 28, scale=4.2, col=PU, bh=6.5)
    out.append(f'<text x="{w - 12 - 14 * 4.2 - 4:.1f}" y="{Y(28) + 4:.1f}" text-anchor="end" fill="{GOLD}" class="lt">POC</text>')
    out.append(f'<text x="{w - 26}" y="{Y(53) + 4:.1f}" text-anchor="end" fill="{DN}" class="lt">LVN</text>')
    out.append(f'<text x="{w - 12 - 13 * 4.2 - 4:.1f}" y="{Y(78) + 4:.1f}" text-anchor="end" fill="{BL}" class="lt">HVN</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def sessions(w=420, h=210, caption=""):
    """Three session blocks (Asia, London, New York), each with its own small profile and POC."""
    top, bot = 28, h - 22
    Y = lambda v: bot - v * (bot - top) / 100
    blocks = [("Asia", 10, 140, [40, 46, 38, 44, 36, 42, 38, 45, 40], {50: 3, 46: 8, 42: 12, 38: 7, 34: 2}, 42, GR),
              ("London", 145, 275, [40, 34, 28, 36, 52, 60, 56, 64, 58], {66: 3, 62: 9, 58: 11, 54: 6, 46: 2, 38: 2, 30: 3}, 58, BL),
              ("New York", 280, 410, [58, 66, 72, 68, 76, 70, 74, 69, 73], {78: 4, 74: 9, 70: 12, 66: 6, 60: 2}, 70, OR)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for name, x0, x1, pts, prof, poc, col in blocks:
        out.append(f'<rect x="{x0}" y="{top - 14}" width="{x1 - x0}" height="{bot - top + 26}" rx="8" fill="{col}" fill-opacity=".06"/>')
        out.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{top - 1}" text-anchor="middle" fill="{col}" class="lt">{name}</text>')
        X = lambda i: x0 + 6 + i * (x1 - x0 - 58) / (len(pts) - 1)
        out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
                   + '" fill="none" stroke="#1C1C1E" stroke-width="2" stroke-linejoin="round"/>')
        _side_profile(out, x1 - 4, Y, prof, poc, scale=3.4, col=col)
        out.append(f'<line x1="{x0 + 4}" x2="{x1 - 4}" y1="{Y(poc):.1f}" y2="{Y(poc):.1f}" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        out.append(f'<text x="{x0 + 6}" y="{bot + 12}" fill="{GOLD}" class="st">POC</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def developing(w=420, h=200, caption=""):
    """Price path with the developing POC drawn as a step line that moves as the session goes on."""
    top, bot = 16, h - 26
    Y = lambda v: bot - v * (bot - top) / 100
    pts = [30, 34, 28, 33, 30, 36, 42, 50, 56, 52, 58, 62, 58, 64, 60, 66, 62, 64]
    dpoc = [30, 30, 30, 31, 31, 31, 31, 31, 31, 31, 52, 56, 56, 58, 60, 60, 60, 61]
    n = len(pts)
    X = lambda i: 20 + i * (w - 60) / (n - 1)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
               + '" fill="none" stroke="#1C1C1E" stroke-width="2.2" stroke-linejoin="round"/>')
    step = []
    for i, v in enumerate(dpoc):
        step.append(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}")
        if i < n - 1:
            step.append(f"L{X(i + 1):.1f},{Y(v):.1f}")
    out.append(f'<path d="{" ".join(step)}" fill="none" stroke="{GOLD}" stroke-width="2.4"/>')
    out.append(f'<text x="{X(3):.1f}" y="{Y(31) + 16:.1f}" text-anchor="middle" fill="{GOLD}" class="lt">dPOC ដើម session</text>')
    out.append(f'<text x="{X(10) + 6:.1f}" y="{Y(36):.1f}" fill="{UP}" class="lt">POC លោតឡើង ↑</text>')
    out.append(f'<text x="{X(n - 1):.1f}" y="{Y(49):.1f}" text-anchor="end" fill="{GOLD}" class="lt">dPOC ចុងក្រោយ</text>')
    out.append(f'<text x="{w / 2:.0f}" y="{h - 7}" text-anchor="middle" fill="{GR}" class="st">ពេលវេលាក្នុង session →</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


# Teaching example (not real data): a 4-week composite profile with $10 rows, total = 100.
COMP = [(4200, 2), (4190, 5), (4180, 11), (4170, 14), (4160, 7), (4150, 2), (4140, 1), (4130, 3), (4120, 9), (4110, 16), (4100, 13), (4090, 8), (4080, 6), (4070, 3)]
FINE = [(4134, 1), (4133, 3), (4132, 2), (4131, 6), (4130, 4), (4129, 7), (4128, 3), (4127, 5), (4126, 1), (4125, 2)]
COARSE = [(4130, 16), (4125, 18)]

CH = dict(
    ch=20, part="PART 4 · Volume Profile",
    title_km="ប្រភេទ Volume Profile", title_en="Types of Volume Profile: Fixed · Session · Visible · Developing · Composite",
    intro="""ក្នុង Chapter 19 យើងបានរៀនពាក្យគន្លឹះ: <span class='en-term'>POC</span>, <span class='en-term'>Value Area</span>,
<span class='en-term'>VAH</span>, <span class='en-term'>VAL</span>, <span class='en-term'>HVN</span> និង <span class='en-term'>LVN</span>។
ប៉ុន្តែមានសំណួរសំខាន់មួយដែលយើងមិនទាន់ឆ្លើយ: profile នោះ<b>គណនាពីពេលណា ដល់ពេលណា?</b>
ទិន្នន័យដូចគ្នា ប៉ុន្តែ<b>ចន្លោះពេល</b> (range) ខុសគ្នា ផ្ដល់ POC ខុសគ្នាទាំងស្រុង។
ជំពូកនេះបង្រៀន 5 ប្រភេទ: <span class='en-term'>Fixed Range</span>, <span class='en-term'>Session</span>, <span class='en-term'>Visible Range</span>,
<span class='en-term'>Developing</span> និង <span class='en-term'>Composite</span> ហើយរបៀប<b>ជ្រើសរើស</b>ប្រភេទដែលត្រូវនឹងរបៀប trade របស់អ្នក។""",
    sections=[
        ("ហេតុអ្វីប្រភេទ Profile សំខាន់?", """
<p>Volume Profile គ្រាន់តែជាការបូក volume តាមតម្លៃ។ អ្វីដែលធ្វើឱ្យប្រភេទនីមួយៗខុសគ្នា គឺ<b>ទៀនណាខ្លះ</b>ដែលត្រូវបានយកមកបូក។
ប្ដូរចន្លោះពេល = ប្ដូរ POC, VAH, VAL ទាំងអស់។</p>
""" + range_compare(caption="តម្លៃដូចគ្នា: Profile A (ទាំងអស់) មាន POC នៅ range ខាងក្រោម · Profile B (តែផ្នែកចុងក្រោយ) មាន POC នៅខាងលើ") + """
<ul><li>Profile <b>A</b> គ្របទាំងអស់: range ខាងក្រោមមានរយៈពេលយូរជាង ដូច្នេះ POC នៅទីនោះ</li>
<li>Profile <b>B</b> គ្របតែផ្នែកចុងក្រោយ: វាមិន "ដឹង" ពី range ខាងក្រោមទេ ដូច្នេះ POC នៅខាងលើ</li>
<li>ពីរ profile នេះ<b>ត្រឹមត្រូវទាំងពីរ</b>។ វាគ្រាន់តែឆ្លើយសំណួរខុសគ្នា</li></ul>
<div class='box tip'>💡 មុនពេលនិយាយថា "POC នៅ 4,130" ត្រូវនិយាយជានិច្ចថា <b>POC នៃអ្វី?</b> (session មុន? ថ្ងៃម្សិលមិញ? 5 ថ្ងៃ? swing ចុងក្រោយ?)។
បើគ្មានចម្លើយនេះ លេខ POC គ្មានន័យច្បាស់ទេ។</div>
"""),
        ("Fixed Range Volume Profile (FRVP)", """
<p><span class='en-term'>Fixed Range Volume Profile</span> = អ្នក<b>ជ្រើសចំណុចចាប់ផ្ដើម និងចំណុចបញ្ចប់ខ្លួនឯង</b> ហើយ profile គណនាតែទៀននៅចន្លោះនោះ។
វាជាឧបករណ៍ដែលបត់បែនបំផុត ព្រោះអ្នកអាចវាស់ចលនាណាមួយដែលអ្នកចាប់អារម្មណ៍។</p>
""" + fixed_range(caption="FRVP ពី swing low ដល់ swing high នៃ impulse មួយ: POC នៅមូលដ្ឋាន · LVN នៅកណ្ដាល (ផ្នែករត់លឿន) · HVN នៅកំពូល") + """
<p><b>ការប្រើញឹកញាប់:</b></p>
<ul><li><b>វាស់ impulse leg មួយ</b> (swing low → swing high): រក LVN នៅកណ្ដាល ដែលច្រើនត្រូវនឹង displacement / FVG (Chapter 13)</li>
<li><b>វាស់ range មួយ</b> (ពីការចាប់ផ្ដើម range ដល់ឥឡូវ): រក POC នៃ range ដើម្បីដឹងតម្លៃ "យុត្តិធម៌" នៃ range នោះ</li>
<li><b>វាស់ចាប់ពីព្រឹត្តិការណ៍មួយ</b> (ឧ. ចាប់ពីទៀន NFP ឬ CPI · មើល 📰 News): មើលថា volume ក្រោយ news ទទួលយកតម្លៃណា</li></ul>
<div class='box warn'>⚠️ ចំណុចខ្សោយ: FRVP អាស្រ័យលើ<b>ការជ្រើសរើសរបស់អ្នក</b>។ ជ្រើសចំណុចចាប់ផ្ដើមខុស 2-3 ទៀន អាចប្ដូរ POC។
ច្បាប់ល្អ: ចាប់ផ្ដើម និងបញ្ចប់នៅ <b>swing ច្បាស់</b> (Chapter 9) មិនមែននៅកន្លែងដែល "មើលទៅស្អាត" ទេ។</div>
"""),
        ("Session Volume Profile", """
<p><span class='en-term'>Session Volume Profile</span> = profile មួយសម្រាប់ session នីមួយៗ (Asia, London, New York) ឬមួយសម្រាប់មួយថ្ងៃ trade ពេញ។
វាប្រាប់ថា ក្នុង session នីមួយៗ ទីផ្សារទទួលយកតម្លៃណា។</p>
""" + sessions(caption="Session នីមួយៗមាន profile និង POC ផ្ទាល់ខ្លួន · POC ផ្លាស់ឡើងពី Asia → London → New York") + """
<p>Session ដែលកូដ XAU.KH ប្រើ (ម៉ោង New York · ម៉ោងកម្ពុជាក្នុងរដូវរងារ ពេល New York មិនប្ដូរម៉ោង DST):</p>
<table><tr><th>Session</th><th>ម៉ោង New York</th><th>ម៉ោងកម្ពុជា (រដូវរងារ)</th></tr>
<tr><td>Asia</td><td>18:00 – 02:00</td><td>06:00 – 14:00</td></tr>
<tr><td>London</td><td>02:00 – 07:00</td><td>14:00 – 19:00</td></tr>
<tr><td>New York</td><td>07:00 – 12:00</td><td>19:00 – 00:00</td></tr></table>
<div class='box tip'>💡 ក្នុងរដូវក្ដៅ (ខែមីនា–វិច្ឆិកា) New York ប្ដូរម៉ោង (DST) ដូច្នេះម៉ោងកម្ពុជា<b>មុន 1 ម៉ោង</b> (ឧ. London 13:00 – 18:00)។
ថ្ងៃ trade មាសចាប់ផ្ដើម 18:00 New York មិនមែនពាក់កណ្ដាលអធ្រាត្រទេ។</div>
<ul><li><b>ល្អសម្រាប់ intraday</b>: profile នៃ session មុន ផ្ដល់កម្រិតថ្មីៗ (POC, VAH, VAL) សម្រាប់ session បន្ទាប់</li>
<li><b>រាង</b>នៃ profile session មុន (P, b, D · Chapter 21) ប្រាប់ថាភាគីណាឈ្នះ session នោះ</li>
<li>Model 📊 <b>Volume</b> ក្នុង 🚨 Signals ប្រើ profile នៃ <b>session មុន</b> និង POC របស់វា</li></ul>
"""),
        ("Visible Range Volume Profile", """
<p><span class='en-term'>Visible Range Volume Profile</span> = profile នៃ<b>ទៀនទាំងអស់ដែលអ្នកឃើញលើអេក្រង់</b>ឥឡូវនេះ។
ពេលអ្នក zoom ចូល zoom ចេញ ឬ scroll chart profile ក៏ប្ដូរតាម។</p>
<table><tr><th>ចំណុចល្អ</th><th>ចំណុចខ្សោយ</th></tr>
<tr><td>រហ័ស: មិនចាំបាច់គូរ ឬជ្រើសអ្វី</td><td>ប្ដូររាល់ពេល zoom / scroll</td></tr>
<tr><td>ល្អសម្រាប់មើលទិដ្ឋភាពទូទៅលឿនៗ</td><td>អ្នក trade ពីរនាក់ មើលកម្រិតខុសគ្នា ព្រោះ zoom ខុសគ្នា</td></tr>
<tr><td>បង្ហាញ HVN/LVN ធំៗក្នុងអ្វីដែលអ្នកកំពុងវិភាគ</td><td>មិនអាចកត់ត្រា ឬប្រៀបធៀបពីថ្ងៃមួយទៅថ្ងៃមួយបាន</td></tr></table>
<div class='box warn'>⚠️ កុំយក POC នៃ Visible Range មកធ្វើជាកម្រិត entry ដោយមិនដឹងថាអេក្រង់គ្របរយៈពេលប៉ុន្មាន។
បើ scroll បន្តិច POC អាចលោតទៅកន្លែងផ្សេង។ ប្រើវាដើម្បី<b>មើល</b> ហើយប្រើ Session ឬ Fixed Range ដើម្បី<b>កត់ត្រាកម្រិត</b>។</div>
"""),
        ("Developing Volume Profile និង Developing POC", """
<p><span class='en-term'>Developing Volume Profile</span> = profile ដែល<b>កំពុងសាងសង់</b>ក្នុង session បច្ចុប្បន្ន។
រាល់ទៀនថ្មី volume ត្រូវបានបន្ថែម ហើយ POC អាចផ្លាស់ទី។ ខ្សែបង្ហាញទីតាំង POC តាមពេលហៅថា <span class='en-term'>Developing POC (dPOC)</span>។</p>
""" + developing(caption="dPOC (ខ្សែមាស) នៅនឹងនៅដើម session បន្ទាប់មកលោតឡើង ពេលទីផ្សារចាប់ផ្ដើមទទួលយកតម្លៃខ្ពស់ជាង") + """
<ul><li>dPOC <b>ឡើង</b>តាមតម្លៃ = ទីផ្សារកំពុង<b>ទទួលយក</b>តម្លៃខ្ពស់ជាង (value កំពុងផ្លាស់ឡើង)</li>
<li>តម្លៃឡើង ប៉ុន្តែ dPOC <b>នៅនឹង</b>ខាងក្រោម = ចលនាឡើងនៅមិនទាន់ត្រូវបានទទួលយក · អាចត្រឡប់មក POC វិញ</li>
<li>dPOC <b>លោតចុះឡើង</b>ច្រើនដង = session គ្មានភាគីគ្រប់គ្រងច្បាស់ (balance)</li></ul>
<div class='box warn'>⚠️ POC "ពិត" នៃ session ដឹងបានតែ<b>ក្រោយ session បិទ</b>។ ក្នុងអំឡុង session dPOC គ្រាន់តែជាស្ថានភាពបណ្ដោះអាសន្ន។
កុំគិតថា dPOC ម៉ោង 08:00 គឺជា POC ចុងក្រោយ។ ការផ្លាស់ទីនៃ value ពីថ្ងៃមួយទៅថ្ងៃមួយ (volume migration) នឹងរៀនក្នុង Chapter 21។</div>
"""),
        ("Composite Volume Profile", """
<p><span class='en-term'>Composite Volume Profile</span> = profile មួយដែលបូក volume នៃ<b>ច្រើនថ្ងៃ ច្រើនសប្ដាហ៍ ឬច្រើនខែ</b>ចូលគ្នា។
វាបង្ហាញកម្រិតធំៗ ដែលទីផ្សារទទួលយកក្នុងរយៈពេលវែង។</p>
""" + profile(COMP, poc=4110, va=(4090, 4180),
              marks={4170: ("HVN ខាងលើ", BL), 4140: ("LVN ↯", DN), 4110: ("POC 4,110", GOLD)},
              caption="ឧទាហរណ៍ composite 4 សប្ដាហ៍ (ជួរ $10): HVN ពីរ (4,110 និង 4,170) បំបែកដោយ LVN 4,140 · ឧទាហរណ៍សម្រាប់រៀន មិនមែនទិន្នន័យពិត") + """
<ul><li>Composite ច្រើនមាន<b>ច្រើន HVN</b> (ឧ. range ខាងក្រោម និង range ខាងលើ) ដែលបំបែកដោយ LVN</li>
<li>LVN ធំក្នុង composite (ឧ. 4,140) = តំបន់ដែលតម្លៃធ្លាប់រត់ឆ្លងលឿន · ពេលត្រឡប់មក អាចរត់ឆ្លងលឿនម្ដងទៀត ឬច្រានចេញ</li>
<li>ល្អសម្រាប់ <b>swing trade</b> និងសម្រាប់កំណត់<b>គោលដៅធំ</b> (TP) មិនមែនសម្រាប់ entry ច្បាស់លាស់ក្នុង 5m ទេ</li></ul>
<div class='box tip'>💡 រូប 📊 <b>Analysis</b> និង <b>/check</b> របស់ XAU.KH គូរ profile នៃ <b>5 ថ្ងៃចុងក្រោយ</b>។ វាជា composite ខ្លីមួយ:
វែងគ្រប់គ្រាន់ដើម្បីបង្ហាញ HVN/LVN សំខាន់ៗ ប៉ុន្តែខ្លីគ្រប់គ្រាន់ដើម្បីនៅជិតតម្លៃបច្ចុប្បន្ន។</div>
"""),
        ("Settings សំខាន់: Row Size និង Value Area %", """
<p>ទោះប្រភេទណាក៏ដោយ profile មាន settings ពីរដែលប្ដូររូបរាងខ្លាំង:</p>
<p><b>1. <span class='en-term'>Row size</span> (ទំហំជួរតម្លៃ)</b>: volume ត្រូវបានដាក់ក្នុង "ធុង" តម្លៃ។ ជួរតូច = លម្អិតខ្លាំង តែរញ៉េរញ៉ៃ · ជួរធំ = រលោង តែបាត់ព័ត៌មាន។</p>
""" + profile(FINE, poc=4129, marks={4131: ("POC ទីពីរ?", PU), 4129: ("POC", GOLD)}, rh=15,
              caption="ជួរ $1: volume ដូចគ្នា ប៉ុន្តែឃើញ 'ធ្មេញ' ច្រើន · ពិបាកដឹងថា 4,129 ឬ 4,131 សំខាន់ជាង") + """
""" + profile(COARSE, poc=4125, marks={4125: ("POC 4,125–4,129", GOLD)}, rh=22,
              caption="ជួរ $5: volume ដូចគ្នា រួមជា 2 ជួរ (4,125–4,129 និង 4,130–4,134) · សាមញ្ញ ប៉ុន្តែបាត់ព័ត៌មានលម្អិតទាំងអស់") + """
<table><tr><th>ប្រភេទ</th><th>Row size ដែលសមរម្យសម្រាប់មាស (គំនិតចាប់ផ្ដើម)</th></tr>
<tr><td>Session / Developing</td><td>$0.50 – $1 (5 – 10 pips)</td></tr>
<tr><td>Fixed Range លើ impulse មួយ</td><td>$1 – $2</td></tr>
<tr><td>Composite ច្រើនសប្ដាហ៍</td><td>$5 – $10 (50 – 100 pips)</td></tr></table>
<p><b>2. <span class='en-term'>Value Area %</span></b>: ស្តង់ដារ <b>70%</b> (Chapter 19)។ ទុក 70% ដដែល ដើម្បីឱ្យកម្រិតរបស់អ្នកប្រៀបធៀបបានជាមួយអ្នកដទៃ។</p>
<div class='box tip'>💡 នេះជា<b>ចំណុចចាប់ផ្ដើម</b> មិនមែនច្បាប់ទេ។ ពេលមាសប្រែប្រួលខ្លាំង (ថ្ងៃ news) ជួរធំបន្តិចច្រើនមើលច្បាស់ជាង។</div>
"""),
        ("ជ្រើសរើស Profile ឱ្យត្រូវ", """
<p>គ្មានប្រភេទណា "ល្អបំផុត" ទេ។ ប្រភេទត្រឹមត្រូវ = ប្រភេទដែលត្រូវនឹង<b>រយៈពេល trade</b> និង<b>សំណួរ</b>របស់អ្នក:</p>
<table><tr><th>របៀប trade / សំណួរ</th><th>ប្រភេទ Profile</th></tr>
<tr><td>Scalp / intraday: "កម្រិតណាសំខាន់សម្រាប់ session នេះ?"</td><td><b>Session VP</b> នៃ session មុន + <b>Developing</b></td></tr>
<tr><td>Day trade: "ម្សិលមិញទីផ្សារទទួលយកអ្វី?"</td><td><b>Session VP</b> មួយថ្ងៃពេញ</td></tr>
<tr><td>Swing: "តំបន់ធំៗនៅឯណា?"</td><td><b>Composite</b> (1 – 4 សប្ដាហ៍ ឬច្រើនជាង)</td></tr>
<tr><td>"Impulse នេះរត់លឿននៅឯណា?"</td><td><b>Fixed Range</b> ពី swing ទៅ swing</td></tr>
<tr><td>មើលលឿនៗ មិនកត់ត្រា</td><td><b>Visible Range</b></td></tr></table>
""" + flow([("Composite", "តំបន់ធំ", PU), ("Session មុន", "POC·VAH·VAL", BL), ("Developing", "value ថ្ងៃនេះ", GOLD), ("Fixed Range", "leg entry", UP)],
           caption="Top-down ជាមួយ Volume Profile: ពីធំ ទៅតូច ដូចការមើល timeframe ក្នុង Chapter 9") + """
<div class='box ok'>✅ ឧទាហរណ៍: Composite បង្ហាញ HVN ធំនៅ 4,110 · Session London ម្សិលមិញមាន POC 4,128 · ថ្ងៃនេះ dPOC កំពុងឡើងលើ 4,135។
អ្នកដឹងថា: value កំពុងផ្លាស់ឡើង ហើយ 4,128 គឺជាកម្រិតដំបូងដែល pullback អាចត្រូវបានទិញ (ត្រូវការ structure បញ្ជាក់ជានិច្ច)។</div>
"""),
        ("Volume Profile ក្នុង MT5 និងកំហុសញឹកញាប់", """
<p>MT5 <b>មិនមាន</b> Volume Profile ជា indicator ដើមទេ (Chapter 19)។ បើអ្នកដំឡើង indicator ពី MQL5 Market ឬ CodeBase សូមពិនិត្យ:</p>
<ul><li>វាគាំទ្រប្រភេទណាខ្លះ (Session, Fixed Range, Composite...)</li>
<li>វាប្រើ <b>tick volume</b> របស់ broker (Chapter 18) · កម្រិតអាចខុសបន្តិចពី profile របស់ broker ផ្សេង ឬពី futures</li>
<li><b>ម៉ោង server</b> របស់ broker: broker ជាច្រើនប្រើម៉ោង GMT+2 / GMT+3 ដូច្នេះ "ថ្ងៃ" និង "session" របស់ indicator អាចមិនត្រូវនឹងម៉ោង New York</li></ul>
<div class='box warn'>⚠️ <b>កំហុសញឹកញាប់:</b><br>
❌ ប្រើ POC ដោយមិនដឹងថាវាជា POC នៃរយៈពេលណា<br>
❌ ប្រៀបធៀប Session POC របស់អ្នក ជាមួយ POC 5 ថ្ងៃលើរូប 📊 Analysis ហើយគិតថាមួយណា "ខុស"<br>
❌ ប្ដូរ Fixed Range រហូតដល់ POC ធ្លាក់ត្រង់កន្លែងដែលអ្នកចង់បាន (នេះជាការបញ្ឆោតខ្លួនឯង)<br>
❌ ប្រើ Composite 6 ខែ ដើម្បីរក entry 5m<br>
❌ ចាត់ទុក dPOC ពាក់កណ្ដាល session ជាកម្រិតចុងក្រោយ</div>
"""),
    ],
    summary=["ប្រភេទ profile = <b>ចន្លោះពេល</b>ដែលបូក volume · ចន្លោះខុស = POC ខុស · សួរជានិច្ច \"POC នៃអ្វី?\"",
             "<b>Fixed Range</b> = អ្នកជ្រើសចាប់ផ្ដើម/បញ្ចប់ (swing ទៅ swing) · <b>Visible Range</b> = អ្វីដែលឃើញលើអេក្រង់",
             "<b>Session</b> = Asia / London / New York · ល្អសម្រាប់ intraday · model 📊 Volume ប្រើ session មុន",
             "<b>Developing</b> = profile កំពុងសាងសង់ · dPOC ផ្លាស់ទី · POC ពិតដឹងតែក្រោយ session បិទ",
             "<b>Composite</b> = ច្រើនថ្ងៃ/សប្ដាហ៍ · តំបន់ធំសម្រាប់ swing · ជ្រើសតាមរយៈពេល trade ពីធំទៅតូច"],
    exercise=["ពីឧទាហរណ៍ Composite (ជួរ $10) តម្លៃឥឡូវ 4,150។ តើ HVN ខាងលើ និង POC នៅឆ្ងាយប៉ុន្មាន $ និងប៉ុន្មាន pips? បើ trade 0.01 lot ចលនាទៅ POC ស្មើប៉ុន្មាន $?",
              "សរសេរម៉ោងកម្ពុជានៃ session London និង New York សម្រាប់ថ្ងៃនេះ (គិតថា New York កំពុងប្រើម៉ោងរដូវរងារ ឬរដូវក្ដៅ)។",
              "លើ MT5 របស់អ្នក គូរ Fixed Range (ឬកត់ត្រាដោយដៃ) លើ impulse ចុងក្រោយនៃ 15m។ តើ LVN ត្រូវនឹង FVG ណាមួយទេ?",
              "បើករូប 📊 Analysis ថ្ងៃនេះ ហើយប្រៀបធៀប POC 5 ថ្ងៃ ជាមួយតម្លៃបច្ចុប្បន្ន។ ពន្យល់ថាហេតុអ្វី POC នៃ session ចុងក្រោយអាចនៅកន្លែងផ្សេង។"],
)
