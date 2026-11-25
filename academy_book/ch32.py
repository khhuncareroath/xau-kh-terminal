from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def equity_paths(w=420, h=200, caption=""):
    """Same 14 trades (5 wins at 2R, one 7-loss streak) at 1%, 5% and 10% risk, on ONE shared $ scale."""
    seq = "WLWLLLLLLLWLWW"
    series = []
    for r, col in [(1, UP), (5, OR), (10, DN)]:
        e, vals = 1000.0, [1000.0]
        for s in seq:
            e = e * (1 + 2 * r / 100) if s == "W" else e * (1 - r / 100)
            vals.append(e)
        series.append((r, col, vals))
    lo, hi = 550, 1350
    n = len(seq) + 1
    X = lambda i: 44 + i * (w - 64) / (n - 1)
    Y = lambda v: h - 30 - (v - lo) / (hi - lo) * (h - 62)
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for v in (600, 800, 1000, 1200):
        out.append(f'<line x1="40" x2="{w - 16}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#E5E5EA"/>')
        out.append(f'<text x="36" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{GR}" class="st">${v:,}</text>')
    out.append(f'<rect x="{X(3):.1f}" y="22" width="{X(10) - X(3):.1f}" height="{h - 52}" fill="{DN}" fill-opacity=".06"/>')
    out.append(f'<text x="{(X(3) + X(10)) / 2:.1f}" y="{h - 14}" text-anchor="middle" fill="{DN}" class="st">ខាត 7 ដងជាប់គ្នា</text>')
    for r, col, vals in series:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>')
    x0 = 46
    for r, col, vals in series:
        low = min(vals)
        out.append(f'<rect x="{x0}" y="10" width="12" height="4" fill="{col}"/><text x="{x0 + 16}" y="16" fill="{col}" class="lt">risk {r}% · low ${low:,.0f}</text>')
        x0 += 122
    out.append("</svg>")
    return _wrap("".join(out), caption)


def limit_ladder(w=420, h=150, caption=""):
    """Daily and weekly loss limits as a ladder on a $1,000 account."""
    rows = [("ខាត 1 trade", "1%", "$10", UP, 0.10), ("Max daily loss", "3%", "$30", OR, 0.30),
            ("Max weekly loss", "6%", "$60", DN, 0.60), ("Drawdown → ពិនិត្យប្រព័ន្ធ", "10%", "$100", PU, 1.0)]
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for i, (t, pct, usd, col, frac) in enumerate(rows):
        y = 14 + i * 32
        bw = 30 + frac * (w - 270)
        out.append(f'<rect x="150" y="{y}" width="{bw:.1f}" height="22" rx="5" fill="{col}" fill-opacity=".22" stroke="{col}"/>')
        out.append(f'<text x="142" y="{y + 15}" text-anchor="end" fill="#1C1C1E" class="st">{t}</text>')
        out.append(f'<text x="{150 + bw + 6:.1f}" y="{y + 15}" fill="{col}" class="lt">{pct} = {usd}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=32, part="PART 8 · Risk Management",
    title_km="ការពារដើមទុន", title_en="Capital Protection: Risk per Trade · Lot Size · Loss Limits · Drawdown · Risk of Ruin",
    intro="""ចាប់ពីជំពូកនេះ យើងចូល <b>PART 8: Risk Management</b>។ អ្នកអាចមាន setup ល្អបំផុត ប៉ុន្តែបើ lot ធំពេក
ការខាត<b>ពីរបីដងជាប់គ្នា</b> (ដែលកើតឡើងចំពោះ trader គ្រប់រូប) អាចបំផ្លាញគណនីបាន។ ជំពូកនេះបង្រៀន
<span class='en-term'>risk per trade</span> · <span class='en-term'>position sizing</span> · រូបមន្ត<b>គណនា lot</b> ·
<span class='en-term'>max daily / weekly loss</span> · <span class='en-term'>drawdown</span> · <span class='en-term'>risk of ruin</span>
និងរបៀប<b>ការពារគណនីតូច</b>។ គោលដៅទី 1 របស់ trader មិនមែនរកលុយទេ គឺ<b>នៅរស់ក្នុងទីផ្សារ</b>។""",
    sections=[
        ("Risk per Trade · ហានិភ័យក្នុងមួយ Trade", """
<p><span class='en-term'>Risk per trade</span> គឺជាចំនួនលុយដែលអ្នក<b>ព្រមខាត</b> ប្រសិនបើ trade នោះប៉ះ SL។ យើងគិតវាជា <b>% នៃគណនី</b> មិនមែនជាចំនួនលុយថេរទេ
ដូច្នេះពេលគណនីធំ risk ធំតាម ហើយពេលគណនីតូច risk តូចតាម។</p>
<table style='break-inside:avoid'><tr><th>Risk / trade</th><th>គណនី $1,000</th><th>គណនី $5,000</th><th>កម្រិត</th></tr>
<tr><td><b>0.5%</b></td><td>$5</td><td>$25</td><td style='color:#34C759'>ប្រុងប្រយ័ត្ន</td></tr>
<tr><td><b>1%</b></td><td>$10</td><td>$50</td><td style='color:#34C759'>ស្តង់ដារ · ណែនាំ</td></tr>
<tr><td><b>2%</b></td><td>$20</td><td>$100</td><td style='color:#FF9500'>អតិបរមា</td></tr>
<tr><td><b>5%+</b></td><td>$50+</td><td>$250+</td><td style='color:#FF3B30'>គ្រោះថ្នាក់</td></tr></table>
<div class='box tip'>💡 Risk គឺ<b>ចម្ងាយ SL × lot</b>។ SL ឆ្ងាយមិនមែនមានន័យថា risk ធំទេ បើអ្នកកាត់ lot ឱ្យតូចតាម។ នេះជាមូលហេតុដែលយើង<b>ដាក់ SL មុន</b> (Chapter 30) ហើយ<b>គណនា lot ក្រោយ</b>។</div>
"""),
        ("Position Sizing · គណនា Lot", """
<p>ចងចាំ XAU.KH conventions: <b>0.01 lot = 1 oz</b> · តម្លៃប្ដូរ <b>$1 = 10 pips</b> · 0.01 lot ចំណេញ/ខាត <b>$1</b> ក្នុងមួយ $1 នៃចលនា។ ដូច្នេះ 1.00 lot = $100 ក្នុងមួយ $1។</p>
""" + flow([("Account", "ឧ. $5,000", BL), ("Risk %", "1% = $50", OR), ("SL $", "ចម្ងាយ ឧ. $20", DN), ("Lot", "50 ÷ (20×100)", UP)],
           caption="ជំហានគណនា lot · SL មកពី structure មិនមែនមកពី lot") + """
<div class='box ok'>✅ <b>រូបមន្ត:</b> Lot = (Account × Risk%) ÷ (SL $ × 100)<br>
ឧ. $5,000 × 1% = <b>$50</b> · SL $20 → 50 ÷ 2,000 = <b>0.025</b> → បង្គត់<b>ចុះ</b> = <b>0.02 lot</b> (risk ពិត $40 = 0.8%)</div>
<table style='break-inside:avoid'><tr><th>Account</th><th>Risk 1%</th><th>SL $10 (100 pips)</th><th>SL $20 (200 pips)</th><th>SL $30 (300 pips)</th></tr>
<tr><td>$1,000</td><td>$10</td><td>0.01</td><td>0.005 → ⚠️</td><td>0.003 → ⚠️</td></tr>
<tr><td>$2,000</td><td>$20</td><td>0.02</td><td>0.01</td><td>0.006 → ⚠️</td></tr>
<tr><td>$5,000</td><td>$50</td><td>0.05</td><td>0.02</td><td>0.01</td></tr>
<tr><td>$10,000</td><td>$100</td><td>0.10</td><td>0.05</td><td>0.03</td></tr></table>
<div class='box warn'>⚠️ <b>បង្គត់ចុះជានិច្ច</b> មិនបង្គត់ឡើង។ ⚠️ = lot ដែលគណនាបាន តូចជាង 0.01 (ទំហំតូចបំផុតនៃ broker ភាគច្រើន) → មើលផ្នែក "គណនីតូច" ខាងក្រោម។</div>
"""),
        ("ឧទាហរណ៍ពេញលេញ: ពី Signal ដល់ Lot", """
<p>ឧបមាថា 🚨 <b>Signals</b> ក្នុង group ផ្ដល់ setup ទិញ: Entry <b>4,082</b> · SL <b>4,067</b> · TP <b>4,112</b>។ គណនីរបស់អ្នក <b>$3,000</b> · risk <b>1%</b>។</p>
<table style='break-inside:avoid'><tr><th>ជំហាន</th><th>គណនា</th><th>លទ្ធផល</th></tr>
<tr><td>1. Risk $</td><td>3,000 × 1%</td><td><b>$30</b></td></tr>
<tr><td>2. ចម្ងាយ SL</td><td>4,082 − 4,067</td><td><b>$15</b> = 150 pips</td></tr>
<tr><td>3. Lot</td><td>30 ÷ (15 × 100)</td><td><b>0.02 lot</b></td></tr>
<tr><td>4. ពិនិត្យ risk</td><td>0.02 × 100 × 15</td><td>$30 ✅</td></tr>
<tr><td>5. ចំណេញបើដល់ TP</td><td>0.02 × 100 × 30</td><td>$60 = <b>2R</b></td></tr></table>
<div class='box tip'>💡 Signal ផ្ដល់ <b>entry · SL · TP</b> ដូចគ្នាសម្រាប់មនុស្សគ្រប់គ្នា។ ប៉ុន្តែ <b>lot ជារបស់អ្នក</b>: វាអាស្រ័យលើទំហំគណនី និង risk % របស់អ្នក។ កុំចម្លង lot របស់អ្នកដទៃ។ ពិនិត្យលទ្ធផលកន្លងមកក្នុង 📈 <b>Proof</b> ដើម្បីដឹងថាការខាតជាប់គ្នាក៏កើតឡើងដែរ។</div>
"""),
        ("Max Daily Loss និង Max Weekly Loss", """
<p>ច្បាប់ risk per trade ការពារ trade <b>មួយ</b>។ ប៉ុន្តែអ្នកក៏ត្រូវការ<b>ដែនកំណត់</b>សម្រាប់មួយថ្ងៃ និងមួយសប្ដាហ៍ ដើម្បីកុំឱ្យថ្ងៃអាក្រក់មួយក្លាយជាសប្ដាហ៍អាក្រក់។</p>
""" + limit_ladder(caption="ឧទាហរណ៍ដែនកំណត់លើគណនី $1,000 ជាមួយ risk 1% / trade") + """
<ul><li><span class='en-term'>Max daily loss</span> ប្រហែល <b>2–3%</b>: ដល់ហើយ → <b>បិទ MT5</b> · ត្រឡប់មកថ្ងៃស្អែក</li>
<li><span class='en-term'>Max weekly loss</span> ប្រហែល <b>5–6%</b>: ដល់ហើយ → ឈប់រហូតដល់សប្ដាហ៍ក្រោយ · អាន journal</li>
<li>ដែនកំណត់គិតលើ<b>ការខាតដែលបិទរួច</b> (realized) + ការខាតនៃ trade ដែលកំពុងបើក</li>
<li>សរសេរដែនកំណត់<b>មុន</b>ថ្ងៃចាប់ផ្ដើម (ផែនការថ្ងៃ · Chapter 31) មិនមែនពេលកំពុងខាត</li></ul>
<div class='box warn'>⚠️ ការសម្រេចចិត្តអាក្រក់បំផុតកើតឡើង<b>ក្រោយ</b>ការខាត។ ដែនកំណត់ប្រចាំថ្ងៃ គឺការសម្រេចចិត្តដែលអ្នកធ្វើពេល<b>ចិត្តស្ងប់</b> ដើម្បីការពារខ្លួនអ្នកពេល<b>ចិត្តក្ដៅ</b>។</div>
"""),
        ("Drawdown · ការធ្លាក់ពីកំពូល", """
<p><span class='en-term'>Drawdown</span> (DD) គឺការធ្លាក់ចុះនៃគណនី ពី<b>កំពូលខ្ពស់បំផុត</b> (peak) ទៅ<b>បាត</b> (trough) មុនពេលបង្កើតកំពូលថ្មី។
<span class='en-term'>Max drawdown</span> គឺ DD ធំបំផុតដែលធ្លាប់កើត។</p>
""" + zigzag([20, 55, 45, 78, 60, 66, 38, 50, 44, 72, 86, 80], {3: ("Peak $1,200", UP), 8: ("Trough $960", DN), 10: ("Peak ថ្មី", UP)},
             lines=[(78, 3, 8, "DD = −20%", DN, True)],
             caption="Equity curve: DD = (1,200 − 960) ÷ 1,200 = 20% · DD បញ្ចប់ពេលគណនីលើស peak ចាស់") + """
<p>ចំណុចសំខាន់បំផុត: ការខាតមិនស្មើគ្នាជាមួយការចំណេញដើម្បីយកវិញទេ។ ខាតកាន់តែច្រើន ត្រូវការ<b>ចំណេញកាន់តែច្រើនជាងនេះ</b>ដើម្បីត្រឡប់មកចំណុចដើម។</p>
""" + bars([("−10%", 11.1, UP), ("−20%", 25, GOLD), ("−30%", 42.9, OR), ("−50%", 100, DN), ("−75%", 300, PU)], unit="%",
           caption="ចំណេញដែលត្រូវការដើម្បីយក drawdown វិញ (គណនា: DD ÷ (100 − DD))") + """
<div class='box tip'>💡 ខាត 50% ត្រូវការចំណេញ <b>100%</b> ដើម្បីត្រឡប់មកវិញ។ ដូច្នេះការការពារកុំឱ្យ DD ធំ<b>ងាយជាង</b>ការព្យាយាមយកវាវិញ។</div>
"""),
        ("Risk % និងការខាតជាប់គ្នា", """
<p>មើល trade ដូចគ្នា 14 ដង (ឈ្នះ 5 ដងនៅ <b>2R</b> · មានការខាត <b>7 ដងជាប់គ្នា</b>) ប៉ុន្តែប្រើ risk % ខុសគ្នា។ គ្រប់ខ្សែប្រើ<b>មាត្រដ្ឋានដូចគ្នា</b>។</p>
""" + equity_paths(caption="ឧទាហរណ៍គណនា (មិនមែនលទ្ធផលពិត) · គណនី $1,000 · risk គិតជា % នៃគណនីបច្ចុប្បន្ន") + """
<table style='break-inside:avoid'><tr><th>Risk / trade</th><th>ខាត 10 ដងជាប់គ្នា</th><th>DD ក្នុងឧទាហរណ៍ខាងលើ</th></tr>
<tr><td><b>1%</b></td><td>−9.6%</td><td style='color:#34C759'>−6.8%</td></tr>
<tr><td><b>2%</b></td><td>−18.3%</td><td></td></tr>
<tr><td><b>5%</b></td><td>−40.1%</td><td style='color:#FF9500'>−30%</td></tr>
<tr><td><b>10%</b></td><td>−65.1%</td><td style='color:#FF3B30'>−52%</td></tr></table>
<div class='box warn'>⚠️ ប្រព័ន្ធ<b>ដដែល</b> setup <b>ដដែល</b>។ ភាពខុសគ្នាតែមួយគឺ risk %។ ជាមួយ risk 1% អ្នកនៅតែស្ងប់ចិត្ត និងអាច trade តាមផែនការបន្ត។ ជាមួយ 10% គណនីបាត់ពាក់កណ្ដាល ហើយអារម្មណ៍នឹងបំផ្លាញការសម្រេចចិត្តបន្ទាប់។</div>
"""),
        ("Risk of Ruin · ហានិភ័យបាត់គណនី", """
<p><span class='en-term'>Risk of ruin</span> គឺជាឱកាសដែលគណនីធ្លាក់ដល់កម្រិតដែលអ្នក<b>មិនអាច trade បន្តបាន</b> (ឧ. −50% ឬបាត់ទាំងអស់)។ វាអាស្រ័យលើ 3 យ៉ាង:</p>
<ul><li><b>Win rate</b> (% ឈ្នះ) និង <b>R:R</b> (ចំណេញមធ្យម ធៀបការខាតមធ្យម)</li>
<li><b>Risk %</b> ក្នុងមួយ trade ← អ្នកគ្រប់គ្រងបាន 100%</li>
<li>ចំនួន trade (ឱកាសនៃការខាតជាប់គ្នាកើនឡើងតាមចំនួន trade)</li></ul>
<p>តារាងខាងក្រោមជា<b>ការគណនាគណិតវិទ្យា</b> (សន្មតថា trade នីមួយៗឯករាជ្យពីគ្នា): ឱកាសដែលយ៉ាងហោចណាស់មានការខាត <b>N ដងជាប់គ្នា</b> មួយដង ក្នុង <b>100 trades</b>។</p>
<table style='break-inside:avoid'><tr><th>Win rate</th><th>ខាត 4+ ជាប់</th><th>ខាត 5+ ជាប់</th><th>ខាត 6+ ជាប់</th><th>ខាត 8+ ជាប់</th></tr>
<tr><td>40%</td><td>~100%</td><td>~98%</td><td>~87%</td><td>~49%</td></tr>
<tr><td>50%</td><td>~97%</td><td>~81%</td><td>~55%</td><td>~17%</td></tr>
<tr><td>60%</td><td>~80%</td><td>~46%</td><td>~21%</td><td>~4%</td></tr></table>
<div class='box ok'>✅ សេចក្ដីសន្និដ្ឋាន: ការខាត 5–8 ដងជាប់គ្នា គឺ<b>ធម្មតា</b> មិនមែនកម្រទេ។ ដូច្នេះ risk % ត្រូវតូចល្មម ដើម្បីឱ្យការខាត 10 ដងជាប់គ្នា<b>មិនបំផ្លាញ</b>គណនី។ ជាមួយ 1% អ្នកនៅសល់ ~90% · ជាមួយ 10% អ្នកនៅសល់ ~35%។</div>
"""),
        ("ការពារគណនីតូច · Protecting Small Accounts", """
<p>គណនីតូច ($100–$500) ជួបបញ្ហាពិសេស: ទោះប្រើ lot តូចបំផុត <b>0.01</b> ក៏ risk អាចលើស 2% រួចហើយ។</p>
<table style='break-inside:avoid'><tr><th>គណនី</th><th>0.01 lot · SL $15</th><th>Risk %</th><th>ស្ថានភាព</th></tr>
<tr><td>$200</td><td>$15</td><td>7.5%</td><td style='color:#FF3B30'>❌ ធំពេក</td></tr>
<tr><td>$500</td><td>$15</td><td>3%</td><td style='color:#FF9500'>⚠️ ខ្ពស់</td></tr>
<tr><td>$1,000</td><td>$15</td><td>1.5%</td><td style='color:#34C759'>✅ អាចទទួលយកបាន</td></tr>
<tr><td>$1,500</td><td>$15</td><td>1%</td><td style='color:#34C759'>✅ ល្អ</td></tr></table>
""" + flow([("Cent account", "lot តូចជាង 0.01", BL), ("SL តឹងជាង", "តាម structure", OR), ("Trade តិច", "តែ setup A+", UP), ("ថែមដើមទុន", "ពីប្រាក់ចំណូល", GOLD)],
           caption="ជម្រើសសម្រាប់គណនីតូច · កុំបង្កើន risk ដើម្បី 'លឿន'") + """
<ul><li><span class='en-term'>Cent account</span>: broker ខ្លះមានគណនី cent ដែលទំហំតូចជាង 0.01 lot ស្តង់ដារ · ពិនិត្យលក្ខខណ្ឌ broker របស់អ្នកក្នុង MT5</li>
<li>កុំ<b>បង្រួម SL</b> ឱ្យខុស structure ដើម្បីតែអាចប្រើ 0.01 lot បាន (Chapter 30) · បើ SL ត្រឹមត្រូវធំពេក → <b>រំលង trade</b></li>
<li>គោលដៅនៃគណនីតូច = <b>រៀន និងបង្កើតវិន័យ</b> មិនមែនធ្វើឱ្យធំលឿនទេ</li></ul>
<div class='box warn'>⚠️ "គណនីតូច ចាំបាច់ risk ធំ ទើបធំលឿន" គឺជាគំនិតដែលបំផ្លាញគណនីតូចច្រើនបំផុត។ គណនី $200 ដែល risk 10% នឹង<b>ប្រឈម</b>នឹងការបាត់ទាំងអស់ក្នុងការខាតជាប់គ្នាធម្មតាមួយ។</div>
"""),
        ("Checklist មុនចុច Buy / Sell និងកំហុសញឹកញាប់", """
<table style='break-inside:avoid'><tr><th>✔</th><th>សំណួរ</th></tr>
<tr><td>1</td><td>SL ដាក់តាម structure រួចហើយឬនៅ?</td></tr>
<tr><td>2</td><td>Risk $ = Account × Risk% (≤ 1–2%)?</td></tr>
<tr><td>3</td><td>Lot = Risk $ ÷ (SL $ × 100) · បង្គត់ចុះ?</td></tr>
<tr><td>4</td><td>Trade ដែលបើកស្រាប់ + trade នេះ នៅក្រោម max daily loss?</td></tr>
<tr><td>5</td><td>ថ្ងៃនេះ/សប្ដាហ៍នេះ មិនទាន់ដល់ដែនកំណត់ខាត?</td></tr>
<tr><td>6</td><td>គ្មានព័ត៌មានធំក្នុង 15 នាទីខាងមុខ? (📰 News · Chapter 31)</td></tr></table>
<ul><li>❌ ជ្រើស lot មុន ហើយដាក់ SL ឱ្យ "សម" នឹង lot</li>
<li>❌ ប្រើ lot ដដែលរាល់ trade ទោះ SL ខុសគ្នា (SL $10 និង $30 = risk ខុសគ្នា 3 ដង)</li>
<li>❌ បង្កើន lot ក្រោយខាត ដើម្បី "យកវិញលឿន"</li>
<li>❌ ភ្លេចថាការខាតពិតអាចធំជាង SL ពេល slippage (Chapter 31)</li>
<li>❌ គ្មានដែនកំណត់ប្រចាំថ្ងៃ · trade រហូតដល់ "ចិត្តស្ងប់វិញ"</li></ul>
"""),
    ],
    summary=["Risk per trade 0.5–1% (អតិបរមា 2%) · គិតជា % នៃគណនី",
             "Lot = (Account × Risk%) ÷ (SL $ × 100) · SL មុន lot ក្រោយ · បង្គត់ចុះ",
             "Max daily loss ~2–3% · Max weekly loss ~5–6% · ដល់ហើយ = ឈប់",
             "Drawdown ធំ ត្រូវការចំណេញធំជាងដើម្បីយកវិញ (−50% → +100%)",
             "ការខាត 5–8 ដងជាប់គ្នាគឺធម្មតា · គណនីតូចត្រូវ trade តិច និងមិនបង្កើន risk"],
    exercise=["គណនី $4,000 · risk 1% · Entry ទិញ 4,105 · SL 4,089។ គណនា risk $, ចម្ងាយ SL ជា pips និង lot។",
              "គណនី $800 · SL ដែលត្រឹមត្រូវគឺ $25។ ជាមួយ 0.01 lot តើ risk ជាប៉ុន្មាន %? អ្នកគួរធ្វើអ្វី?",
              "គណនីឡើងដល់ $2,500 រួចធ្លាក់មក $2,000។ Drawdown ប៉ុន្មាន %? ត្រូវចំណេញប៉ុន្មាន % ទើបត្រឡប់ដល់ $2,500?",
              "សរសេរច្បាប់ risk ផ្ទាល់ខ្លួនរបស់អ្នក: risk / trade · max daily loss · max weekly loss · អ្វីដែលអ្នកនឹងធ្វើពេលដល់ដែនកំណត់។"],
)
