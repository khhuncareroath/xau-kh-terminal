from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def confidence_curve(w=420, h=200, caption=""):
    """Concept drawing: decision quality rises with confidence, then falls when confidence becomes overconfidence."""
    x0, x1, yb, yt = 40, w - 20, h - 34, 38
    pts = []
    for i in range(41):
        t = i / 40
        q = 1 - ((t - 0.5) / 0.5) ** 2
        pts.append((x0 + t * (x1 - x0), yb - q * (yb - yt)))
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    zx = [x0, x0 + (x1 - x0) * 0.3, x0 + (x1 - x0) * 0.7, x1]
    zones = [("ភ័យ · Fear", DN), ("ទំនុកចិត្ត · Confidence", UP), ("Overconfidence", OR)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, col) in enumerate(zones):
        out.append(f'<rect x="{zx[i]:.1f}" y="{yt - 8}" width="{zx[i + 1] - zx[i]:.1f}" height="{yb - yt + 8}" fill="{col}" fill-opacity=".08"/>')
        out.append(f'<text x="{(zx[i] + zx[i + 1]) / 2:.1f}" y="{yb + 18}" text-anchor="middle" fill="{col}" class="lt">{t}</text>')
    out.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" stroke="#C7C7CC"/>')
    out.append(f'<line x1="{x0}" y1="{yt - 8}" x2="{x0}" y2="{yb}" stroke="#C7C7CC"/>')
    out.append(f'<text x="{x0 - 6}" y="{yt + 4}" text-anchor="end" fill="{GR}" class="st">ល្អ</text>')
    out.append(f'<text x="{x0 - 6}" y="{yb - 2}" text-anchor="end" fill="{GR}" class="st">អន់</text>')
    out.append(f'<path d="{path}" fill="none" stroke="#1C1C1E" stroke-width="2.4"/>')
    out.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{yt - 16}" text-anchor="middle" fill="#1C1C1E" class="st">គុណភាពនៃការសម្រេចចិត្ត</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def emotion_check(w=420, h=118, caption=""):
    """A 1-5 emotion scale with what to do at each level."""
    levels = [("1", "ស្ងប់", "Trade តាម plan", UP), ("2", "ធម្មតា", "Trade តាម plan", UP),
              ("3", "រំភើបបន្តិច", "ពិនិត្យ checklist ពីរដង", GOLD),
              ("4", "ខឹង · ភ័យ", "ឈប់ 15 នាទី", OR), ("5", "ខ្លាំងណាស់", "បិទ MT5 ថ្ងៃនេះ", DN)]
    cw = (w - 20) / 5
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (n, t, act, col) in enumerate(levels):
        x = 10 + i * cw
        out.append(f'<rect x="{x + 3:.1f}" y="10" width="{cw - 6:.1f}" height="{h - 20}" rx="10" fill="{col}" fill-opacity=".13" stroke="{col}"/>')
        out.append(f'<text x="{x + cw / 2:.1f}" y="36" text-anchor="middle" fill="{col}" class="pt">{n}</text>')
        out.append(f'<text x="{x + cw / 2:.1f}" y="60" text-anchor="middle" fill="#1C1C1E" class="bt">{t}</text>')
        words = act.split(" ")
        half = (len(words) + 1) // 2
        for j, line in enumerate([" ".join(words[:half]), " ".join(words[half:])]):
            out.append(f'<text x="{x + cw / 2:.1f}" y="{82 + j * 15}" text-anchor="middle" fill="#6E6E73" class="st">{line}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=38, part="PART 10 · Professional Trading Development",
    title_km="ចិត្តសាស្ត្រជួញដូរ", title_en="Trading Psychology: Fear & Greed · Patience · Discipline · Confidence · Emotional Control · Losses · Routine",
    intro="""អ្នកបានរៀន structure, liquidity, volume, risk និង journal រួចហើយ។ ប៉ុន្តែការដឹង និងការ<b>ធ្វើ</b>ជារឿងពីរខុសគ្នា។
អ្នក trade ជាច្រើនដឹងច្បាប់ច្បាស់ ប៉ុន្តែនៅពេលតម្លៃមាសរត់ $20 ក្នុងប៉ុន្មាននាទី ពួកគេភ្លេចអស់។
<span class='en-term'>Trading psychology</span> (ចិត្តសាស្ត្រជួញដូរ) គឺជាជំនាញក្នុងការធ្វើតាមផែនការ<b>ទោះអារម្មណ៍និយាយផ្សេង</b>។
ជំពូកនេះពន្យល់ពីអារម្មណ៍សំខាន់ៗ ផលប៉ះពាល់របស់វាលើ trade និង<b>វិធីជាក់ស្ដែង</b>ដើម្បីគ្រប់គ្រងវា។
គោលដៅមិនមែនធ្វើជាមនុស្សគ្មានអារម្មណ៍ទេ។ គោលដៅគឺកុំឱ្យអារម្មណ៍ជាអ្នក<b>ចុចប៊ូតុង</b>។""",
    sections=[
        ("ហេតុអ្វីចិត្តសាស្ត្រសំខាន់?", """
<p>Strategy មួយមានប្រយោជន៍ តែពេលអ្នកធ្វើវា<b>ដដែលៗ</b>បាន។ បើអ្នកធ្វើតាមច្បាប់ 7 trade ហើយបំពាន 3 trade
លទ្ធផលរបស់អ្នកមិនមែនជាលទ្ធផលនៃ strategy ទៀតទេ វាជាលទ្ធផលនៃ<b>អារម្មណ៍</b>។
Backtest (Chapter 35) បង្ហាញពីអ្វីដែល strategy អាចធ្វើបាន។ ចិត្តសាស្ត្រកំណត់ថាតើ<b>អ្នក</b>អាចទទួលបានវាឬអត់។</p>
""" + flow([("ព្រឹត្តិការណ៍", "តម្លៃរត់ · ខាត", BL), ("អារម្មណ៍", "ភ័យ · លោភ", OR), ("សកម្មភាព", "បំពានច្បាប់", DN), ("លទ្ធផល", "ខាតធំ", DN)],
           caption="វដ្ដអាក្រក់: អារម្មណ៍មិនមែនជាបញ្ហា · <b>សកម្មភាព</b>ដោយអារម្មណ៍ ទើបជាបញ្ហា") + """
<div class='box tip'>💡 អ្នកមិនអាចបញ្ឈប់អារម្មណ៍មិនឱ្យកើតឡើងបានទេ។ ប៉ុន្តែអ្នកអាចដាក់<b>ចន្លោះ</b>មួយរវាងអារម្មណ៍ និងសកម្មភាព។ ចន្លោះនោះគឺ <b>trading plan</b> និង <b>checklist</b> របស់អ្នក។</div>
"""),
        ("Fear និង Greed: ភ័យ និងលោភ", """
<p>អារម្មណ៍ពីរដែលខ្លាំងជាងគេក្នុងការ trade គឺ <span class='en-term'>Fear</span> (ភ័យ) និង <span class='en-term'>Greed</span> (លោភ)។
វាលេចឡើងជាលំនាំដដែលៗនៅលើ chart:</p>
""" + zigzag([20, 45, 35, 70, 60, 92, 55, 66, 30, 18], {1: ("សង្ឃឹម", BL), 3: ("រំភើប", GOLD), 5: ("លោភ", OR), 6: ("បដិសេធ", PU), 8: ("ភ័យ", DN), 9: ("បោះបង់", DN)},
            caption="វដ្ដអារម្មណ៍ទូទៅ: ទិញនៅកំពូលដោយលោភ · លក់នៅបាតដោយភ័យ") + """
<table style='break-inside:avoid'><tr><th>អារម្មណ៍</th><th>អាកប្បកិរិយា</th><th>ច្បាប់ការពារ</th></tr>
<tr><td style='color:#FF3B30'><b>Fear</b></td><td>មិនហ៊ានចូល setup ល្អ · បិទ trade ឈ្នះលឿនពេក · ផ្លាស់ SL ចេញ</td><td>Risk តូចល្មម (1%) ដើម្បីការខាតមិនធ្វើឱ្យភ័យ</td></tr>
<tr><td style='color:#FF9500'><b>Greed</b></td><td>Lot ធំ · មិនយក TP · ដេញតម្លៃ (<span class='en-term'>FOMO</span>) · trade ច្រើនពេក</td><td>Lot គណនាពីរូបមន្ត · TP ដាក់មុនចូល · max trade/ថ្ងៃ</td></tr></table>
<div class='box warn'>⚠️ <span class='en-term'>FOMO</span> (Fear Of Missing Out) គឺជាការលាយគ្នានៃភ័យ និងលោភ: ឃើញមាសឡើង $15 ហើយចូលទិញនៅកំពូល ព្រោះខ្លាចខកខាន។ ទីផ្សារមាសមានឱកាសថ្មីរាល់ថ្ងៃ។ ការខកខាន trade មួយ មិនធ្វើឱ្យអ្នកខាតលុយទេ។</div>
"""),
        ("Patience: ការអត់ធ្មត់", """
<p><span class='en-term'>Patience</span> មានពីរប្រភេទ:</p>
<ul><li><b>អត់ធ្មត់រង់ចាំ entry</b>: រង់ចាំតម្លៃមកដល់ zone និងទៀនបញ្ជាក់ មិនមែនចូលមុន</li>
<li><b>អត់ធ្មត់កាន់ trade</b>: ទុក trade ដំណើរការរហូតដល់ SL ឬ TP តាម plan មិនមែនបិទព្រោះភ័យ</li></ul>
<p>ថ្ងៃខ្លះគ្មាន setup ណាត្រូវតាម checklist ទាល់តែសោះ។ ថ្ងៃនោះ ការមិន trade គឺជា<b>ការសម្រេចចិត្តល្អ</b>។
<i>"No setup = no risk."</i></p>
""" + bars([("Trade A", 3, UP), ("Trade B", 4, GOLD), ("Trade C", 5, DN)], unit=" trade",
           caption="<b>ឧទាហរណ៍</b>សប្ដាហ៍មួយ: 12 trade ប៉ុន្តែមានតែ 3 ជា grade A · trade ផ្សេងទៀតកើតពីការអត់ធ្មត់មិនបាន") + """
<div class='box ok'>✅ ពេលរង់ចាំ ចូរកំណត់ <b>Alert</b> នៅលើ MT5 នៅ zone សំខាន់ ហើយចាកចេញពីអេក្រង់។ ការអង្គុយមើលទៀនរាល់នាទី ធ្វើឱ្យអ្នកចង់ចុចប៊ូតុង។</div>
"""),
        ("Discipline: វិន័យ", """
<p><span class='en-term'>Discipline</span> មានន័យថា ធ្វើតាមច្បាប់<b>នៅពេលដែលពិបាកបំផុត</b>: ក្រោយខាត 3 ដងជាប់ ក្រោយឈ្នះធំ ឬពេលមាន news ខ្លាំង។
វិន័យមិនមែនជាលក្ខណៈពីកំណើតទេ វាជា<b>ប្រព័ន្ធ</b>ដែលអ្នករៀបចំ:</p>
<ul><li>សរសេរច្បាប់ជាក់លាក់ (Chapter 34) មិនមែន "trade ឱ្យល្អ"</li>
<li>ដាក់ SL និង TP <b>ពេលបើក order</b> មិនមែនក្រោយ</li>
<li>កំណត់ <b>max loss ប្រចាំថ្ងៃ</b> (ឧ. 2R) ហើយបិទ MT5 ពេលដល់</li>
<li>Grade trade រាល់ថ្ងៃក្នុង journal (Chapter 37) ដើម្បីឃើញថាអ្នកធ្វើតាមច្បាប់ប៉ុន្មាន %</li></ul>
""" + bars([("Trade 1", 0.02, BL), ("Trade 2", 0.04, OR), ("Trade 3", 0.08, DN), ("Trade 4", 0.16, DN)], unit=" lot",
           caption="<b>Revenge trading</b>: បង្កើន lot ទ្វេដងក្រោយខាតនីមួយៗ ដើម្បី \"យកលុយមកវិញ\"") + """
<p>គណនាជាមួយ SL $10 (100 pips): 0.02 lot ខាត $20 · 0.04 ខាត $40 · 0.08 ខាត $80 · 0.16 ខាត $160។
ខាត 4 ដងជាប់ = <b>$300</b> ឬ <b>30%</b> នៃគណនី $1,000។ ជាមួយ risk 1% ថេរ ($10 រាល់ trade) ខាត 4 ដងជាប់ = $40 ប៉ុណ្ណោះ។</p>
<div class='box warn'>⚠️ ការខាត 4 ដងជាប់ កើតឡើងធម្មតាសម្រាប់ strategy ណាក៏ដោយ។ អ្វីដែលបំផ្លាញគណនីមិនមែនការខាតនោះទេ គឺ<b>ប្រតិកម្ម</b>ចំពោះការខាត។</div>
"""),
        ("Confidence ទល់នឹង Overconfidence", """
<p><span class='en-term'>Confidence</span> (ទំនុកចិត្ត) មកពី<b>ភស្តុតាង</b>: backtest, forward test និង journal ដែលបង្ហាញថា setup របស់អ្នកមាន edge។
<span class='en-term'>Overconfidence</span> (ជឿជាក់ហួសហេតុ) មកពី<b>លទ្ធផលថ្មីៗ</b>: ឈ្នះ 5 ដងជាប់ ហើយគិតថា "ខ្ញុំយល់ទីផ្សារហើយ"។</p>
""" + confidence_curve(caption="គំនិតសាមញ្ញ (មិនមែនទិន្នន័យ): ភ័យពេក ឬជឿពេក ទាំងពីរធ្វើឱ្យការសម្រេចចិត្តអន់") + """
<table style='break-inside:avoid'><tr><th>Confidence</th><th>Overconfidence</th></tr>
<tr><td>Risk ដដែល 1% ទោះឈ្នះ ឬខាត</td><td>បង្កើន lot ភ្លាមក្រោយឈ្នះជាប់</td></tr>
<tr><td>ចូលតែ setup ក្នុង plan</td><td>Trade setup ថ្មីដែលមិនដែល test</td></tr>
<tr><td>ទទួលយកថា trade នីមួយៗអាចខាត</td><td>រំកិល SL ព្រោះ "ប្រាកដថាវានឹងត្រឡប់"</td></tr>
<tr><td>បង្កើន risk តាមផែនការ ក្រោយ 50–100 trade</td><td>បង្កើន risk ក្រោយ 1 សប្ដាហ៍ល្អ</td></tr></table>
<div class='box tip'>💡 ក្រោយឈ្នះជាប់ច្រើនដង ជាពេលដែលត្រូវ<b>ប្រុងប្រយ័ត្នបំផុត</b>។ សួរខ្លួនឯង: "តើ trade នេះនៅតែជា grade A ដែរឬទេ បើខ្ញុំទើបតែខាត 3 ដង?"</div>
"""),
        ("Emotional Control: គ្រប់គ្រងអារម្មណ៍", """
<p>ជំហានដំបូងគឺ<b>ដឹងខ្លួន</b>។ មុនបើក trade នីមួយៗ ចូរដាក់ពិន្ទុអារម្មណ៍ខ្លួនឯងពី 1 ដល់ 5 ហើយកត់ក្នុង journal:</p>
""" + emotion_check(caption="Emotion check មុនរាល់ trade · ពិន្ទុ 4–5 = គ្មាន trade") + """
<p>ពេលអារម្មណ៍ខ្លាំង ប្រើលំដាប់នេះ:</p>
""" + flow([("ដឹងខ្លួន", "ខ្ញុំកំពុងខឹង", OR), ("ឈប់", "ដកដៃពី mouse", GOLD), ("ពិនិត្យ", "checklist", BL), ("សម្រេច", "តាមច្បាប់", UP)],
           caption="Stop · Check · Act: ឱ្យច្បាប់សម្រេចចិត្ត មិនមែនអារម្មណ៍") + """
<div class='box ok'>✅ សញ្ញារាងកាយក៏សំខាន់: ងងុយគេង ឃ្លាន ឈឺ ឬមានបញ្ហាគ្រួសារ ធ្វើឱ្យការសម្រេចចិត្តអន់។ ថ្ងៃបែបនេះ trade lot តូចជាងមុន ឬកុំ trade។</div>
"""),
        ("Accepting Losses: ទទួលយកការខាត", """
<p>ការខាតគឺជា<b>ថ្លៃធ្វើជំនួញ</b> ដូចហាងលក់ដូរត្រូវបង់ថ្លៃជួល។ Strategy ដែលមាន win rate 50% ក៏ខាតពាក់កណ្ដាលនៃ trade ដែរ។
អ្វីដែលសំខាន់គឺ<b>ទំហំ</b>ការខាតតូច (1R) ហើយការឈ្នះធំជាង (2R ឬច្រើនជាង)។</p>
""" + bars([("1", -1, DN), ("2", -1, DN), ("3", 2, UP), ("4", -1, DN), ("5", 2, UP), ("6", -1, DN), ("7", -1, DN), ("8", 2, UP), ("9", -1, DN), ("10", 2, UP)], unit="R",
           caption="<b>ឧទាហរណ៍</b> 10 trade: ខាត 6 · ឈ្នះ 4 (2R) · សរុប = −6R + 8R = <b>+2R</b>") + """
<p>ក្នុងឧទាហរណ៍ខាងលើ អ្នកខាត<b>ច្រើនដងជាង</b>ឈ្នះ ប៉ុន្តែនៅតែវិជ្ជមាន ព្រោះ R:R ល្អ និងការខាតនីមួយៗតូច។
បើអ្នករំកិល SL ដើម្បីជៀសវាងការខាតតែម្ដង ហើយ trade នោះខាត 4R ជំនួស 1R លទ្ធផលសរុបប្រែទៅជាអវិជ្ជមាន។</p>
<div class='box tip'>💡 មុនចុច Buy ឬ Sell ចូរនិយាយក្នុងចិត្ត: <b>"ខ្ញុំទទួលយកការខាត $10 នេះរួចហើយ"</b>។ បើអ្នកមិនអាចនិយាយបែបនោះដោយស្ងប់ទេ lot របស់អ្នកធំពេក។</div>
"""),
        ("Building a Repeatable Routine: ទម្លាប់ប្រចាំថ្ងៃ", """
<p>ទម្លាប់ (<span class='en-term'>routine</span>) កាត់បន្ថយការសម្រេចចិត្តដោយអារម្មណ៍ ព្រោះអ្នកធ្វើរឿងដដែលៗតាមលំដាប់ដដែល។
ខាងក្រោមជាគំរូមួយដែលអ្នកអាចកែតាមម៉ោងរបស់អ្នក:</p>
""" + flow([("Outlook", "📰 News · bias", BL), ("Levels", "HTF zone", PU), ("Plan", "2 scenario", GOLD), ("Emotion", "ពិន្ទុ 1–5", OR),
            ("រង់ចាំ", "Alert · 🚨", BL), ("Trade", "តាម checklist", UP), ("Journal", "រូប · grade", PU), ("បិទ", "ឈប់តាមម៉ោង", GR)],
           caption="Routine 8 ជំហាន: មុនទីផ្សារ · អំឡុងពេល · ក្រោយទីផ្សារ") + """
<table style='break-inside:avoid'><tr><th>ពេល</th><th>ធ្វើអ្វី</th><th>នៅ XAU.KH</th></tr>
<tr><td>មុនទីផ្សារ</td><td>អានព័ត៌មាន កំណត់ bias និង level</td><td>📰 News · 📊 Analysis</td></tr>
<tr><td>អំឡុងពេល</td><td>រង់ចាំ zone · ពិនិត្យ checklist · emotion check</td><td>/check · 🚨 Signals</td></tr>
<tr><td>ក្រោយទីផ្សារ</td><td>Journal · grade · screenshot · ពិនិត្យ</td><td>📈 Proof (ជាគំរូនៃការកត់ស្មោះត្រង់)</td></tr></table>
<div class='box ok'>✅ កំណត់<b>ម៉ោងឈប់</b>ច្បាស់លាស់ (ឧ. ក្រោយ NY open 2 ម៉ោង) និងច្បាប់ "ឈប់ពេលឈ្នះ 2R ឬខាត 2R ក្នុងមួយថ្ងៃ"។ ទម្លាប់ល្អមានចំណុចបញ្ចប់។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ Revenge trading: បង្កើន lot ដើម្បីយកការខាតមកវិញ</li>
<li>❌ FOMO: ដេញតម្លៃក្រោយវារត់រួច</li>
<li>❌ រំកិល SL ចេញឆ្ងាយ ព្រោះមិនចង់ខាត</li>
<li>❌ បង្កើន risk ក្រោយឈ្នះជាប់ពីរបីដង</li>
<li>❌ Trade ពេលនឿយហត់ ខឹង ឬមិនសូវស្រួលខ្លួន</li>
<li>❌ មើលចំណេញ/ខាតជា $ រាល់វិនាទី ជំនួសការមើល plan</li>
<li>❌ គ្មានម៉ោងឈប់ trade រហូតដល់យប់ជ្រៅ</li></ul>
"""),
    ],
    summary=["Fear → មិនហ៊ាន/បិទលឿន · Greed → lot ធំ/FOMO · ការពារដោយ risk 1% និង plan",
             "Patience: គ្មាន setup = គ្មាន risk · ប្រើ Alert ជំនួសការអង្គុយមើល",
             "Discipline ជាប្រព័ន្ធ: ច្បាប់សរសេរ · SL/TP ពេលបើក · max loss ប្រចាំថ្ងៃ",
             "Confidence មកពីភស្តុតាង · Overconfidence មកពីលទ្ធផលថ្មីៗ · risk ដដែលជានិច្ច",
             "ការខាត 1R ជាថ្លៃធ្វើជំនួញ · Emotion check 1–5 · routine ដែលមានចំណុចបញ្ចប់"],
    exercise=["សរសេរ trade 3 ចុងក្រោយដែលអ្នកបំពានច្បាប់។ តើអារម្មណ៍អ្វី (fear, greed, FOMO, revenge) នៅពីក្រោយ trade នីមួយៗ?",
              "គណនា: គណនី $1,000 · SL $10 · lot 0.03 ខាត 3 ដងជាប់។ ខាតប៉ុន្មាន $ និងប៉ុន្មាន %? បើប្រើ risk 1% វិញ lot គួរប៉ុន្មាន?",
              "សរសេរ routine ប្រចាំថ្ងៃរបស់អ្នក 6–8 ជំហាន រួមទាំងម៉ោងចាប់ផ្ដើម និងម៉ោងឈប់។",
              "ពេញមួយសប្ដាហ៍ ដាក់ពិន្ទុអារម្មណ៍ 1–5 មុនរាល់ trade ក្នុង journal ហើយប្រៀបធៀប grade នៃ trade ពេលពិន្ទុ 1–2 និង 3–5។"],
)
