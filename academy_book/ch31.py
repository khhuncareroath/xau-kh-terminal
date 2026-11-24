from academy_pdf import zigzag, flow

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def day_clock(w=420, h=190, caption=""):
    """24h Phnom Penh clock (winter): sessions on top, red no-trade windows around news below."""
    X = lambda hr: 16 + hr * (w - 32) / 24
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">',
           f'<line x1="{X(0):.1f}" x2="{X(24):.1f}" y1="78" y2="78" stroke="#C7C7CC" stroke-width="2"/>']
    for a, b, t, col in [(7, 14, "Asia · ស្ងាត់", GR), (14, 17, "London", BL), (19, 22, "NY", UP)]:
        out.append(f'<rect x="{X(a):.1f}" y="40" width="{X(b) - X(a):.1f}" height="24" rx="5" fill="{col}" fill-opacity=".2" stroke="{col}"/>')
        out.append(f'<text x="{(X(a) + X(b)) / 2:.1f}" y="56" text-anchor="middle" fill="#1C1C1E" class="st">{t}</text>')
    out.append(f'<text x="{X(0) + 2:.1f}" y="24" fill="{GR}" class="st">ម៉ោងកម្ពុជា · រដូវរងា</text>')
    for a, b, t in [(20.25, 20.75, "20:30 · CPI/NFP"), (1.75, 2.75, "02:00 · FOMC")]:
        out.append(f'<rect x="{X(a):.1f}" y="92" width="{X(b) - X(a):.1f}" height="22" rx="4" fill="{DN}" fill-opacity=".28" stroke="{DN}"/>')
        anchor, tx = ("end", X(a) - 4) if a > 12 else ("start", X(b) + 4)
        out.append(f'<text x="{tx:.1f}" y="107" text-anchor="{anchor}" fill="{DN}" class="st">⛔ {t}</text>')
    out.append(f'<rect x="{X(4):.1f}" y="122" width="{X(6) - X(4):.1f}" height="22" rx="4" fill="{GR}" fill-opacity=".2" stroke="{GR}"/>')
    out.append(f'<text x="{X(6) + 4:.1f}" y="137" fill="{GR}" class="st">Break · spread ធំ</text>')
    for hr in range(0, 25, 4):
        out.append(f'<text x="{X(hr):.1f}" y="{h - 12}" text-anchor="middle" fill="{GR}" class="st">{hr:02d}:00</text>')
        out.append(f'<line x1="{X(hr):.1f}" x2="{X(hr):.1f}" y1="74" y2="82" stroke="{GR}"/>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def spread_band(w=420, h=180, caption=""):
    """Bid/Ask band: thin most of the time, wide around the news minute, then thin again; price gap through a stop."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    xs = list(range(20, w - 19, 20))
    mid = [100, 98, 101, 99, 100, 99, 100, 70, 128, 90, 112, 104, 108, 106, 110, 108, 109, 111, 110, 112]
    spr = [3, 3, 3, 3, 3, 4, 8, 22, 26, 18, 10, 5, 4, 3, 3, 3, 3, 3, 3, 3]
    n = min(len(xs), len(mid))
    ask = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]},{mid[i] - spr[i]}" for i in range(n))
    bid = " ".join(f"L{xs[i]},{mid[i] + spr[i]}" for i in reversed(range(n)))
    out.append(f'<path d="{ask} {bid} Z" fill="{OR}" fill-opacity=".25" stroke="{OR}" stroke-width="1"/>')
    out.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{xs[i]},{mid[i]}" for i in range(n))
               + '" fill="none" stroke="#1C1C1E" stroke-width="1.6"/>')
    out.append(f'<line x1="{xs[6]}" x2="{xs[6]}" y1="20" y2="{h - 26}" stroke="{DN}" stroke-dasharray="4 3"/>')
    out.append(f'<text x="{xs[6] - 4}" y="30" text-anchor="end" fill="{DN}" class="lt">📰 20:30</text>')
    out.append(f'<text x="{xs[1]}" y="80" fill="{GR}" class="st">spread តូច</text>')
    out.append(f'<text x="{xs[8] + 8}" y="40" fill="{OR}" class="st">spread ពង្រីក</text>')
    out.append(f'<text x="{xs[14]}" y="135" fill="{GR}" class="st">ត្រឡប់ធម្មតា</text>')
    out.append(f'<rect x="20" y="{h - 18}" width="12" height="6" fill="{OR}" fill-opacity=".4"/><text x="38" y="{h - 11}" fill="#6E6E73" class="st">ចន្លោះ Bid – Ask (spread)</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=31, part="PART 7 · Trade Execution",
    title_km="Session និងព័ត៌មាន", title_en="Trading Sessions & News: Planning the Day, CPI · NFP · FOMC, Spread and Slippage",
    intro="""មាសប្រតិកម្ម<b>ខ្លាំងបំផុត</b>ចំពោះព័ត៌មានសេដ្ឋកិច្ចអាមេរិក។ ក្នុងរយៈពេលប៉ុន្មាននាទី តម្លៃអាចលោត $10–$30
spread អាចពង្រីក ហើយ SL អាច<b>ត្រូវ fill អាក្រក់ជាង</b>ដែលអ្នកបានដាក់។ ជំពូកនេះបង្រៀនពីរបៀប<b>រៀបចំថ្ងៃ trade</b> ·
អាន <span class='en-term'>economic calendar</span> · យល់ពី <span class='en-term'>CPI</span> <span class='en-term'>NFP</span> <span class='en-term'>FOMC</span> ·
ហេតុអ្វី spread និង slippage កើតឡើង និង<b>ពេលណាត្រូវនៅក្រៅទីផ្សារ</b>។ គោលដៅមិនមែន "ទាយព័ត៌មាន" ទេ គឺ<b>ការពារខ្លួន</b>ពីវា។""",
    sections=[
        ("រៀបចំថ្ងៃ Trade · Planning a Trading Day", """
<p>Trader ដែលល្អ ដឹង<b>មុន</b>ថាថ្ងៃនេះមានព្រឹត្តិការណ៍អ្វីខ្លះ និងម៉ោងណាគ្រោះថ្នាក់។ ផែនការប្រចាំថ្ងៃមិនចាំបាច់វែងទេ ត្រឹមតែ 10 នាទីពេលព្រឹកក៏គ្រប់គ្រាន់។</p>
""" + flow([("Calendar", "📰 ព័ត៌មានថ្ងៃនេះ", DN), ("ម៉ោងគ្រោះថ្នាក់", "សម្គាល់ ⛔", OR), ("HTF bias", "D1 · 4H · /check", BL), ("Level សំខាន់", "PDH · PDL · zone", GOLD),
            ("Kill zone", "London · NY", UP), ("ច្បាប់ risk", "ខាតអតិបរមា/ថ្ងៃ", PU), ("Trade", "តាមផែនការ", BL), ("Review", "journal ល្ងាច", GR)],
           caption="ផែនការប្រចាំថ្ងៃ 8 ជំហាន · ធ្វើមុនបើក MT5 មិនមែនក្រោយ") + """
<div class='box tip'>💡 ក្នុង group XAU.KH: 📰 <b>News</b> (និង Daily Outlook ពេលព្រឹក) ប្រាប់ព្រឹត្តិការណ៍ធំៗ · 📊 <b>Analysis</b> និង <b>/check</b> ប្រាប់ structure និង level · ប្រើវាជាជំហាន 1–4។</div>
"""),
        ("ម៉ោង Session និងម៉ោងព័ត៌មាន", """
<p>ម៉ោងខាងក្រោមជាម៉ោងកម្ពុជា ក្នុង<b>រដូវរងា</b> (ពេលអាមេរិកមិនប្រើ DST)។ ក្នុងរដូវក្ដៅ ម៉ោងទាំងនេះ<b>មុន 1 ម៉ោង</b> (ឧ. ព័ត៌មាន US 19:30 · FOMC 01:00) (Chapter 16)។</p>
""" + day_clock(caption="ព័ត៌មាន US ភាគច្រើន 20:30 (ក្នុង NY kill zone) · FOMC 02:00 យប់ · ម៉ោង break ប្រចាំថ្ងៃ spread ធំ") + """
<table style='break-inside:avoid'><tr><th>ពេលវេលា (រដូវរងា)</th><th>អ្វីកើតឡើង</th><th>សម្រាប់ trader</th></tr>
<tr><td>07:00–14:00</td><td>Asia · ចលនាតូច</td><td>សម្គាល់ high/low Asia</td></tr>
<tr><td>14:00–17:00</td><td>London បើក</td><td>Kill zone ទី 1</td></tr>
<tr><td>20:30</td><td>ទិន្នន័យ US (CPI · NFP · ...)</td><td>⛔ 15–30 នាទីមុន/ក្រោយ</td></tr>
<tr><td>19:00–22:00</td><td>New York</td><td>Kill zone ទី 2 · liquidity ច្រើនបំផុត</td></tr>
<tr><td>02:00 (យប់ពុធ)</td><td>FOMC</td><td>⛔ កុំទុក trade បើកដោយមិនដឹង</td></tr></table>
"""),
        ("Economic Calendar · ប្រតិទិនសេដ្ឋកិច្ច", """
<p><span class='en-term'>Economic calendar</span> បង្ហាញព្រឹត្តិការណ៍សេដ្ឋកិច្ចតាមម៉ោង។ ក្នុង <b>MT5</b> មាន tab <span class='en-term'>Calendar</span> ក្នុង Toolbox។
ព្រឹត្តិការណ៍នីមួយៗមានជួរដូចខាងក្រោម:</p>
<table style='break-inside:avoid'><tr><th>ជួរ</th><th>អត្ថន័យ</th></tr>
<tr><td><b>Time</b></td><td>ម៉ោងចេញ (ពិនិត្យថាជាម៉ោងតំបន់ណា · MT5 ច្រើនតែបង្ហាញម៉ោង server)</td></tr>
<tr><td><b>Currency</b></td><td>រូបិយប័ណ្ណ · សម្រាប់មាស <b>USD</b> សំខាន់បំផុត</td></tr>
<tr><td><b>Impact</b></td><td>កម្រិតសំខាន់: ទាប · មធ្យម · <b style='color:#FF3B30'>ខ្ពស់</b></td></tr>
<tr><td><b>Previous</b></td><td>លេខលើកមុន</td></tr>
<tr><td><b>Forecast</b></td><td>លេខដែលទីផ្សាររំពឹង</td></tr>
<tr><td><b>Actual</b></td><td>លេខពិតដែលទើបចេញ</td></tr></table>
<div class='box ok'>✅ គោលការណ៍សំខាន់: ទីផ្សារប្រតិកម្មចំពោះ<b>ភាពខុសគ្នា</b>រវាង <b>Actual</b> និង <b>Forecast</b> (surprise) មិនមែនចំពោះលេខខ្លួនឯងទេ។ លេខ "ល្អ" តែដូចការរំពឹង ជាញឹកញាប់មានប្រតិកម្មតិច។</div>
<div class='box warn'>⚠️ សម្រាប់មាស ផ្ដោតលើព្រឹត្តិការណ៍ USD <b>Impact ខ្ពស់</b>។ ពិនិត្យថា calendar របស់អ្នកបង្ហាញម៉ោង<b>កម្ពុជា</b> ឬម៉ោង server មុនរៀបចំផែនការ។</div>
"""),
        ("CPI · NFP · FOMC: ព័ត៌មានធំបំផុតសម្រាប់មាស", """
<table style='break-inside:avoid'><tr><th>ព័ត៌មាន</th><th>វាស់អ្វី</th><th>ពេលណា (កម្ពុជា · រដូវរងា)</th></tr>
<tr><td><b>CPI</b></td><td>អតិផរណា (តម្លៃទំនិញ)</td><td>ម្ដងក្នុងមួយខែ · 20:30</td></tr>
<tr><td><b>NFP</b></td><td>ការងារថ្មី + អត្រាគ្មានការងារ</td><td>ច្រើនតែថ្ងៃសុក្រដំបូងនៃខែ · 20:30</td></tr>
<tr><td><b>FOMC</b></td><td>ការសម្រេចការប្រាក់របស់ Fed</td><td>8 ដងក្នុងមួយឆ្នាំ · 02:00 យប់ (+ សន្និសីទ 02:30)</td></tr></table>
<p>ទំនាក់ទំនងទូទៅ (Chapter 2): លេខដែល<b>ខ្លាំងជាងការរំពឹង</b> (អតិផរណាខ្ពស់ · ការងារច្រើន) ធ្វើឱ្យទីផ្សាររំពឹងការប្រាក់ខ្ពស់ → USD និង yield ឡើង → មាស<b>ច្រើនតែធ្លាក់</b>។ លេខ<b>ខ្សោយជាង</b>ការរំពឹង → មាស<b>ច្រើនតែឡើង</b>។</p>
""" + flow([("Actual > Forecast", "CPI ខ្ពស់ · NFP ខ្លាំង", OR), ("ការប្រាក់ ↑?", "ទីផ្សាររំពឹង", BL), ("USD · Yield ↑", "ប្រាក់ដុល្លារខ្លាំង", PU), ("មាស ↓ (ច្រើនតែ)", "មិនមែនជានិច្ច", DN)],
           caption="ខ្សែសង្វាក់ប្រតិកម្មទូទៅ · លទ្ធផលពិតអាស្រ័យលើបរិបទ និងការរំពឹងទុករបស់ទីផ្សារ") + """
<div class='box warn'>⚠️ ទំនាក់ទំនងនេះ<b>មិនមែនច្បាប់ដាច់ខាត</b>ទេ។ ពេលខ្លះមាសឡើងទោះ CPI ខ្ពស់ (ឧ. ពេលភ័យខ្លាចសេដ្ឋកិច្ច ឬ geopolitics)។ ហើយលោតទៅទិសមួយ រួចត្រឡប់ទិសផ្ទុយក្នុងប៉ុន្មាននាទី។ ដូច្នេះ <b>កុំ trade ដោយទាយលេខ</b>។</div>
"""),
        ("ការប្រកាសការប្រាក់ · Interest Rate Announcements", """
<p>ការប្រាក់ (interest rate) ប៉ះពាល់មាសខ្លាំង ព្រោះមាស<b>មិនផ្ដល់ការប្រាក់</b>។ ពេលការប្រាក់ខ្ពស់ ការកាន់មាសមាន "ថ្លៃឱកាស" ខ្ពស់ជាង។</p>
<ul><li><b>FOMC statement</b> (02:00): ការសម្រេច ដំឡើង · កាត់ · ឬរក្សាការប្រាក់</li>
<li><b>Press conference</b> (02:30): ប្រធាន Fed ពន្យល់ · ជាញឹកញាប់បង្កើតចលនាទី 2 ខ្លាំងជាងទី 1</li>
<li><b>Dot plot</b> (4 ដងក្នុងមួយឆ្នាំ): ការព្យាករការប្រាក់ទៅមុខរបស់សមាជិក Fed</li>
<li>ធនាគារកណ្ដាលផ្សេង (ECB · BoE · BoJ) ក៏ប៉ះពាល់ USD និងមាសដែរ ប៉ុន្តែតិចជាង Fed</li></ul>
""" + zigzag([50, 52, 49, 51, 80, 30, 66, 22, 40, 34], {4: ("02:00", OR), 5: ("", DN), 6: ("02:30", OR), 7: ("", DN)},
             lines=[(62, 0, 3, "range មុន FOMC", GR, True)],
             caption="ឧទាហរណ៍លំនាំ (មិនមែនទិន្នន័យពិត): ស្ងាត់មុន → លោតពីរទិស ពេល statement → ចលនាទី 2 ពេល press conference") + """
<div class='box tip'>💡 ទីផ្សារជាញឹកញាប់ "ដឹងមុន" ការសម្រេចការប្រាក់រួចហើយ។ អ្វីដែលធ្វើឱ្យលោត គឺ<b>ពាក្យពេចន៍</b>អំពីអនាគត (hawkish = តឹង · dovish = ធូរ)។</div>
"""),
        ("ភាពលោតពេលព័ត៌មាន · News Volatility", """
<p>នៅវិនាទីដែលព័ត៌មានចេញ algorithm និងស្ថាប័នធំៗ trade ក្នុងពេលតែមួយ។ លទ្ធផលគឺ<b>ទៀនធំ</b> · <span class='en-term'>whipsaw</span> (លោតឡើងចុះទាំងពីរទិស) · និង liquidity sweep នៃ SL ទាំងសងខាង។</p>
""" + zigzag([50, 51, 49, 50, 88, 18, 60, 44, 70, 64, 76], {4: ("Spike ↑", UP), 5: ("Sweep ↓", DN), 8: ("ទិសពិត?", BL)},
             lines=[(66, 0, 3, "SL អ្នកលក់", DN, True), (34, 0, 3, "SL អ្នកទិញ", UP, True)],
             caption="Whipsaw: ប៉ះ SL ទាំងអ្នកទិញ និងអ្នកលក់ មុនតម្លៃជ្រើសទិស") + """
<ul><li>ទៀន 1m ដំបូងអាចធំជាងទៀន 1H ធម្មតា</li>
<li>Structure លើ timeframe តូច (1m · 5m) <b>គ្មានន័យ</b>ក្នុងនាទីដំបូង</li>
<li>Pending order (limit · stop) ដែលនៅជិតតម្លៃ អាចត្រូវ fill ភ្លាមៗ ដោយមិនចង់បាន</li></ul>
"""),
        ("Spread Expansion និង Slippage", """
<p><span class='en-term'>Spread</span> = Ask − Bid។ ពេលធម្មតា spread មាសតូច (ឧ. $0.30 = 3 pips · អាស្រ័យលើ broker)។ ពេលព័ត៌មាន broker និង liquidity provider ដក order ចេញ ដូច្នេះ spread
<b>ពង្រីកច្រើនដង</b>មួយភ្លែត។</p>
""" + spread_band(caption="ឧទាហរណ៍លំនាំ: spread ពង្រីកជុំវិញនាទីព័ត៌មាន រួចត្រឡប់ធម្មតាវិញ") + """
<p><span class='en-term'>Slippage</span> = តម្លៃដែល order ត្រូវ fill <b>ខុស</b>ពីតម្លៃដែលអ្នកចង់បាន។ SL គឺជា order ប្រភេទ stop: ពេលតម្លៃលោតរំលង SL វាត្រូវ fill នៅ<b>តម្លៃល្អបន្ទាប់ដែលមាន</b>។</p>
<table style='break-inside:avoid'><tr><th>ឧទាហរណ៍ (ទិញ 0.01 lot)</th><th>តម្លៃ</th><th>ខាត</th></tr>
<tr><td>Entry</td><td>4,070</td><td></td></tr>
<tr><td>SL ដែលបានដាក់</td><td>4,050</td><td>$20 (ផែនការ)</td></tr>
<tr><td>Fill ពិតពេល NFP (slippage $4 = 40 pips)</td><td>4,046</td><td><b style='color:#FF3B30'>$24</b></td></tr></table>
<div class='box warn'>⚠️ ពេលព័ត៌មាន ការខាតពិតអាច<b>ធំជាង 1R</b>។ Spread ធំក៏អាចប៉ះ SL ទាំងដែល chart (Bid) មិនទាន់ដល់ SL ដែរ (ជាពិសេស position លក់ ព្រោះ SL លក់ប្រើតម្លៃ Ask)។</div>
"""),
        ("ពេលណាត្រូវនៅក្រៅទីផ្សារ · When to Stay Out", """
<p>ការមិន trade ក៏ជាការសម្រេចចិត្តមួយដែរ ហើយជាញឹកញាប់ជាការសម្រេចចិត្តល្អបំផុត។</p>
<table style='break-inside:avoid'><tr><th>ស្ថានភាព</th><th>ច្បាប់</th></tr>
<tr><td>CPI · NFP · FOMC · ព័ត៌មាន USD impact ខ្ពស់</td><td>⛔ កុំបើកថ្មី <b>15 នាទីមុន និងក្រោយ</b> (FOMC: យូរជាងនេះ)</td></tr>
<tr><td>Trade បើកស្រាប់ មុនព័ត៌មាន</td><td>បិទ · យកចំណេញខ្លះ · ឬ SL នៅ BE · ដឹងថា slippage អាចកើត</td></tr>
<tr><td>ម៉ោង break ប្រចាំថ្ងៃ · ថ្ងៃឈប់សម្រាកអាមេរិក</td><td>Liquidity តិច · spread ធំ · ចលនាចម្លែក</td></tr>
<tr><td>ថ្ងៃសុក្រយប់ ជិតបិទទីផ្សារ</td><td>ហានិភ័យ <span class='en-term'>gap</span> ពេលបើកថ្ងៃចន្ទ</td></tr>
<tr><td>ក្រោយខាតដល់ការខាតអតិបរមាប្រចាំថ្ងៃ</td><td>ឈប់ · ត្រឡប់មកថ្ងៃស្អែក (Chapter 32)</td></tr>
<tr><td>Structure មិនច្បាស់ · HTF និង LTF ប្រឆាំងគ្នា</td><td>រង់ចាំ · គ្មាន setup = គ្មាន trade</td></tr></table>
<div class='box tip'>💡 ក្រុម XAU.KH បានសាកល្បង "trade ក្រោយព័ត៌មាន" <b>98 ដង</b>: ឈ្នះតែ <b>19%</b>។ ដោយហេតុនេះ bot <b>មិនផ្ញើ</b> 🚨 Signals ក្នុងចន្លោះពេលព័ត៌មានធំ។</div>
"""),
        ("ក្រោយព័ត៌មាន: ត្រឡប់ចូលដោយសុវត្ថិភាព", """
""" + flow([("រង់ចាំ", "15–30 នាទី", GR), ("Spread", "ត្រឡប់ធម្មតា?", OR), ("Structure ថ្មី", "15m · 5m BOS/CHOCH", BL), ("ច្បាប់ធម្មតា", "SL · R:R · lot", UP)],
           caption="មិនដេញទៀនព័ត៌មាន · រង់ចាំទីផ្សារបង្កើត structure ថ្មី រួចប្រើច្បាប់ដដែល") + """
<ul><li>High និង Low នៃទៀនព័ត៌មាន ច្រើនតែក្លាយជា <b>liquidity</b> ដែលតម្លៃត្រឡប់មករកពេលក្រោយ</li>
<li>បើ ATR ធំជាងធម្មតា → SL ត្រូវឆ្ងាយជាង → <b>lot ត្រូវតូចជាង</b> (Chapter 30 · 32)</li>
<li>ថ្ងៃ FOMC ការសម្រេចចិត្តពិតច្រើនតែបង្ហាញខ្លួនក្នុង session London/NY <b>ថ្ងៃបន្ទាប់</b></li></ul>
<div class='box ok'>✅ ប្រសិនបើអ្នកមិនប្រាកដ សូមរង់ចាំ 🚨 Signals បន្ទាប់ ឬពិនិត្យ <b>/check</b>។ ទីផ្សារមាសបើក ~23 ម៉ោងក្នុងមួយថ្ងៃ: ឱកាសថ្មីមកជានិច្ច។</div>
"""),
        ("ផែនការប្រចាំសប្ដាហ៍ និងកំហុសញឹកញាប់", """
<p>ថ្ងៃចន្ទព្រឹក មើល calendar ទាំងសប្ដាហ៍ ហើយសម្គាល់ថ្ងៃ "គ្រោះថ្នាក់"។ ឧទាហរណ៍សប្ដាហ៍មួយ (គំរូ):</p>
<table style='break-inside:avoid'><tr><th>ថ្ងៃ</th><th>ព្រឹត្តិការណ៍ (ឧទាហរណ៍)</th><th>ផែនការ</th></tr>
<tr><td>ចន្ទ</td><td>គ្មានព័ត៌មានធំ</td><td>Trade ធម្មតា · សម្គាល់ high/low សប្ដាហ៍មុន</td></tr>
<tr><td>អង្គារ</td><td>CPI 20:30</td><td>London ធម្មតា · ⛔ 20:15–20:45</td></tr>
<tr><td>ពុធ</td><td>FOMC 02:00 (យប់ពុធ)</td><td>បិទ trade មុនចូលគេង</td></tr>
<tr><td>ព្រហស្បតិ៍</td><td>ក្រោយ FOMC</td><td>រង់ចាំ structure ថ្មី · lot តូច</td></tr>
<tr><td>សុក្រ</td><td>NFP 20:30</td><td>⛔ ជុំវិញ 20:30 · កុំទុក trade ឆ្លងចុងសប្ដាហ៍ដោយមិនគិត</td></tr></table>
<ul><li>❌ Trade ពេលព័ត៌មាន ដោយទាយលេខ</li>
<li>❌ ទុក pending order ជិតតម្លៃ មុនព័ត៌មាន</li>
<li>❌ ភ្លេចប្ដូរម៉ោងពេល DST</li>
<li>❌ លុប SL ចោល "ដើម្បីកុំឱ្យ spread ប៉ះ"</li>
<li>❌ ដេញទៀនធំដំបូងក្រោយព័ត៌មាន</li></ul>
"""),
    ],
    summary=["រៀបចំថ្ងៃ: calendar → ម៉ោងគ្រោះថ្នាក់ → bias → level → kill zone → risk",
             "CPI · NFP 20:30 · FOMC 02:00 (រដូវរងា · ម៉ោងកម្ពុជា) · រដូវក្ដៅមុន 1 ម៉ោង",
             "ទីផ្សារប្រតិកម្មចំពោះ Actual ធៀប Forecast · ទំនាក់ទំនងជាមួយមាសមិនដាច់ខាត",
             "ពេលព័ត៌មាន: whipsaw · spread ពង្រីក · slippage → ការខាតអាចធំជាង 1R",
             "កុំបើកថ្មី 15 នាទីមុន/ក្រោយព័ត៌មានធំ · គ្មាន setup ច្បាស់ = គ្មាន trade"],
    exercise=["បើក tab Calendar ក្នុង MT5 ហើយរកព្រឹត្តិការណ៍ USD impact ខ្ពស់ទាំងអស់សប្ដាហ៍នេះ។ ប្ដូរម៉ោងទៅម៉ោងកម្ពុជា។",
              "NFP ចេញ 20:30។ សរសេរចន្លោះពេលដែលអ្នកនឹងមិនបើក trade ថ្មី។ បើអ្នកមាន trade បើកពី 19:40 តើអ្នកនឹងធ្វើអ្វីមុន 20:15?",
              "ទិញ 0.02 lot នៅ 4,088 · SL 4,070។ ពេលព័ត៌មាន SL ត្រូវ fill នៅ 4,066។ គណនា slippage ជា pips និងការខាតសរុបជា $។",
              "សប្ដាហ៍នេះ សង្កេតតម្លៃក្នុង 📰 News ពេល CPI ឬ NFP (ដោយ<b>មិន trade</b>): កត់ត្រាទៀន 1m ដំបូង · ទិសដំបូង · ទិសក្រោយ 30 នាទី។"],
)
