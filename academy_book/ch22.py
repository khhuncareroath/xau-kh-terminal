from academy_pdf import zigzag, flow, bars

UP, DN, BL, OR, GR, GOLD, PU = "#34C759", "#FF3B30", "#0A84FF", "#FF9500", "#8E8E93", "#E0A100", "#AF52DE"


def _wrap(svg, caption):
    return '<div class="fig">' + svg + (f'<div class="cap">{caption}</div>' if caption else "") + "</div>"


def ladders(books, w=420, rh=19, caption=""):
    """One or two order-book ladders side by side. books = [(title, rows)], rows top to bottom =
    (price, bid_size, ask_size, mark) where sizes may be 0 (empty) and mark is '' or a short label shown in orange."""
    n = len(books)
    rows = max(len(r) for _, r in books)
    h = 46 + rows * rh
    cw = (w - 10) / n
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    for k, (title, rs) in enumerate(books):
        x0 = 5 + k * cw
        pw = 64                                # price column
        side = (cw - pw - 16) / 2              # bid / ask column width
        xb, xp, xa = x0 + 6, x0 + 6 + side, x0 + 6 + side + pw
        vmax = max(max(b, a) for _, b, a, _ in rs) or 1
        out.append(f'<text x="{x0 + cw / 2:.1f}" y="15" text-anchor="middle" fill="#1C1C1E" class="bt">{title}</text>')
        out.append(f'<text x="{xb + side / 2:.1f}" y="32" text-anchor="middle" fill="{BL}" class="st">Bid (ទិញ)</text>')
        out.append(f'<text x="{xp + pw / 2:.1f}" y="32" text-anchor="middle" fill="{GR}" class="st">Price</text>')
        out.append(f'<text x="{xa + side / 2:.1f}" y="32" text-anchor="middle" fill="{DN}" class="st">Ask (លក់)</text>')
        for i, (p, b, a, mark) in enumerate(rs):
            y = 38 + i * rh
            out.append(f'<rect x="{xp:.1f}" y="{y:.1f}" width="{pw}" height="{rh - 3}" rx="3" fill="#F2F2F7"/>')
            out.append(f'<text x="{xp + pw / 2:.1f}" y="{y + rh - 7:.1f}" text-anchor="middle" fill="#1C1C1E" class="lt">{p}</text>')
            if b:
                bw = b / vmax * (side - 22)
                out.append(f'<rect x="{xp - 3 - bw:.1f}" y="{y + 1:.1f}" width="{bw:.1f}" height="{rh - 5}" rx="3" fill="{BL}" fill-opacity=".25"/>')
                out.append(f'<text x="{xp - 6:.1f}" y="{y + rh - 7:.1f}" text-anchor="end" fill="{BL}" class="lt">{b}</text>')
            if a:
                aw = a / vmax * (side - 22)
                out.append(f'<rect x="{xa + 3:.1f}" y="{y + 1:.1f}" width="{aw:.1f}" height="{rh - 5}" rx="3" fill="{DN}" fill-opacity=".22"/>')
                out.append(f'<text x="{xa + 6:.1f}" y="{y + rh - 7:.1f}" fill="{DN}" class="lt">{a}</text>')
            if mark:
                out.append(f'<text x="{(xb + 2) if not b else (xa + side - 2):.1f}" y="{y + rh - 7:.1f}" text-anchor="{"start" if not b else "end"}" fill="{OR}" class="st">{mark}</text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


def matching(w=420, h=160, caption=""):
    """Aggressive (market) order meets passive (limit) order -> a trade, on both sides."""
    out = [f'<svg viewBox="0 0 {w} {h}" class="dia">']
    boxes = [(14, 16, "Market BUY", "aggressive · ទិញភ្លាម", UP), (14, 86, "Market SELL", "aggressive · លក់ភ្លាម", DN),
             (290, 16, "Limit SELL @ Ask", "passive · រង់ចាំ", DN), (290, 86, "Limit BUY @ Bid", "passive · រង់ចាំ", BL)]
    for x, y, t, s, c in boxes:
        out.append(f'<rect x="{x}" y="{y}" width="116" height="48" rx="10" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="1.4"/>')
        out.append(f'<text x="{x + 58}" y="{y + 21}" text-anchor="middle" fill="#1C1C1E" class="bt">{t}</text>')
        out.append(f'<text x="{x + 58}" y="{y + 38}" text-anchor="middle" fill="{GR}" class="st">{s}</text>')
    out.append(f'<rect x="166" y="46" width="88" height="58" rx="12" fill="{GOLD}" fill-opacity=".15" stroke="{GOLD}" stroke-width="1.4"/>')
    out.append(f'<text x="210" y="70" text-anchor="middle" fill="#1C1C1E" class="bt">Trade</text>')
    out.append(f'<text x="210" y="88" text-anchor="middle" fill="{GR}" class="st">ប្រតិបត្តិ</text>')
    for (x1, y1, x2, y2) in [(132, 40, 164, 62), (288, 40, 256, 62), (132, 110, 164, 90), (288, 110, 256, 90)]:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#8E8E93" stroke-width="1.6"/>')
    out.append(f'<text x="210" y="{h - 8}" text-anchor="middle" fill="{GR}" class="st">ទិញ 1 lot = មានអ្នកលក់ 1 lot ជានិច្ច · អ្វីដែលខុសគ្នាគឺ <tspan fill="{OR}">អ្នកណាប្រញាប់</tspan></text>')
    out.append("</svg>")
    return _wrap("".join(out), caption)


CH = dict(
    ch=22, part="PART 5 · Order Flow Intelligence",
    title_km="មូលដ្ឋានគ្រឹះ Order Flow", title_en="Order Flow Foundations: Orders · Bid/Ask · Liquidity · Order Book",
    intro="""Part 4 បានបង្រៀនថា volume <b>ច្រើនប៉ុណ្ណា</b> ត្រូវបានជួញដូរ និង<b>នៅតម្លៃណា</b>។ Part 5 ចូលជ្រៅមួយកម្រិតទៀត:
<b>អ្នកណា</b>ជាអ្នកចាប់ផ្ដើម trade នោះ? អ្នកទិញដែលប្រញាប់ ឬអ្នកលក់ដែលប្រញាប់?
នេះហើយជា <span class='en-term'>Order Flow</span>។ ជំពូកនេះពន្យល់ពីមូលដ្ឋាន: ប្រភេទ order, <span class='en-term'>Bid</span> និង <span class='en-term'>Ask</span>,
<span class='en-term'>liquidity</span>, របៀបដែល order ត្រូវបានប្រតិបត្តិ និងរបៀបអាន <span class='en-term'>order book</span>។
គោលដៅមិនមែនឱ្យអ្នកក្លាយជា scalper ភ្លាមៗទេ ប៉ុន្តែឱ្យអ្នក<b>យល់ថាហេតុអ្វីតម្លៃផ្លាស់ទី</b>។""",
    sections=[
        ("Order Flow ជាអ្វី?", """
<p><span class='en-term'>Order flow</span> គឺជាការសិក្សាពី <b>orders ដែលកំពុងហូរចូលទីផ្សារ</b>: ទិញ ឬលក់, ទំហំប៉ុណ្ណា, ប្រញាប់ ឬរង់ចាំ, និងនៅតម្លៃណា។
Chart ទៀនប្រាប់យើងពី<b>លទ្ធផល</b> (តម្លៃបានទៅណា)។ Order flow ព្យាយាមបង្ហាញ<b>មូលហេតុ</b> (អ្នកណារុញ)។</p>
<table><tr><th>ឧបករណ៍</th><th>ប្រាប់អ្វី</th><th>ឧទាហរណ៍</th></tr>
<tr><td>Price chart</td><td>តម្លៃទៅណា</td><td>ទៀន 15m, structure (Chapter 9)</td></tr>
<tr><td>Volume</td><td>សកម្មភាពច្រើនឬតិច</td><td>Volume bar, Volume Profile (Part 4)</td></tr>
<tr><td><b>Order flow</b></td><td>ភាគីណាប្រញាប់ · កម្លាំងនៅតម្លៃនីមួយៗ</td><td>Bid/Ask volume, Footprint, Delta (Chapter 23–24)</td></tr></table>
""" + flow([("Orders", "ទិញ · លក់", BL), ("Matching", "ផ្គូផ្គង", GOLD), ("Trade", "volume", OR), ("Price", "ផ្លាស់ទី", UP)],
           caption="Order flow មើលផ្នែកខាងឆ្វេង (orders) · chart ទៀនបង្ហាញតែផ្នែកខាងស្ដាំ (price)") + """
<div class='box tip'>💡 គិតដូចផ្សារ: chart ប្រាប់ថាតម្លៃត្រីឡើង។ Order flow ប្រាប់ថា<b>មានអ្នកទិញច្រើននាក់ប្រញាប់ទិញ</b> ខណៈអ្នកលក់មានត្រីតិច។</div>
"""),
        ("Buyers និង Sellers: រឿងដែលមនុស្សច្រើនយល់ខុស", """
<p>មនុស្សច្រើននិយាយថា "តម្លៃឡើងព្រោះ<b>អ្នកទិញច្រើនជាងអ្នកលក់</b>"។ តាមពិត រាល់ trade នីមួយៗ មាន<b>អ្នកទិញម្នាក់ និងអ្នកលក់ម្នាក់</b>ជានិច្ច។
បើអ្នកទិញ 1 lot មានន័យថាមាននរណាម្នាក់លក់ 1 lot ឱ្យអ្នក។ ដូច្នេះ volume ទិញ = volume លក់ <b>ជានិច្ច</b>។</p>
<p>អ្វីដែលខុសគ្នាគឺ<b>ភាពប្រញាប់</b> (<span class='en-term'>aggression</span>):</p>
<ul><li><span class='en-term'>Aggressive</span> (សកម្ម) = អ្នកដែល<b>មិនចង់រង់ចាំ</b> · ទទួលយកតម្លៃដែលមានឥឡូវ · ប្រើ market order</li>
<li><span class='en-term'>Passive</span> (អកម្ម) = អ្នកដែល<b>រង់ចាំ</b>តម្លៃរបស់ខ្លួន · ដាក់ limit order ក្នុង order book</li></ul>
""" + matching(caption="Aggressive order ផ្គូផ្គងជាមួយ passive order → trade មួយកើតឡើង") + """
<div class='box ok'>✅ ការនិយាយត្រឹមត្រូវគឺ: តម្លៃឡើងនៅពេល <b>aggressive buyers</b> ស៊ីអស់ limit sell orders នៅតម្លៃមួយ ហើយត្រូវឡើងទៅរកអ្នកលក់នៅតម្លៃខ្ពស់បន្ទាប់។</div>
"""),
        ("Market Orders និង Limit Orders", """
<p>ក្នុង MT5 នៅពេលអ្នកចុច <b>Buy</b> ឬ <b>Sell</b> ភ្លាមៗ អ្នកកំពុងប្រើ <span class='en-term'>market order</span>។
នៅពេលអ្នកដាក់ <span class='en-term'>Buy Limit</span> ឬ <span class='en-term'>Sell Limit</span> អ្នកកំពុងរង់ចាំតម្លៃមកដល់អ្នក។</p>
<table><tr><th></th><th>Market order</th><th>Limit order</th></tr>
<tr><td>ល្បឿន</td><td>ប្រតិបត្តិភ្លាម</td><td>រង់ចាំ · អាចមិនបានប្រតិបត្តិ</td></tr>
<tr><td>តម្លៃ</td><td>មិនធានា (អាចមាន slippage)</td><td>ធានាតម្លៃ ឬល្អជាង</td></tr>
<tr><td>តួនាទី</td><td><b>យក</b> liquidity (taker)</td><td><b>ផ្ដល់</b> liquidity (maker)</td></tr>
<tr><td>ទិញនៅ</td><td>Ask</td><td>Bid ឬទាបជាង</td></tr>
<tr><td>លក់នៅ</td><td>Bid</td><td>Ask ឬខ្ពស់ជាង</td></tr></table>
<p><b>Stop orders</b> គឺពិសេស: <span class='en-term'>Buy Stop</span>, <span class='en-term'>Sell Stop</span> និង <span class='en-term'>Stop Loss</span>
រង់ចាំក្នុងប្រព័ន្ធ ប៉ុន្តែពេលតម្លៃប៉ះ វា<b>ក្លាយជា market order</b>។ ដូច្នេះ Stop Loss របស់អ្នក ពេលត្រូវប៉ះ គឺជា aggressive order។</p>
<div class='box tip'>💡 នេះជាមូលហេតុដែល <b>liquidity sweep</b> (Chapter 12) មានកម្លាំង: ពេលតម្លៃប៉ះកន្លែងដែល stop orders ច្រើនប្រមូលផ្ដុំ
stops ទាំងនោះក្លាយជា market orders ក្នុងពេលតែមួយ ហើយផ្ដល់ liquidity ដល់អ្នកធំដែលចង់ចូលទិសផ្ទុយ។</div>
"""),
        ("Bid, Ask និង Bid/Ask Volume", """
<p>នៅពេលណាក៏ដោយ មានតម្លៃពីរ (Chapter 4):</p>
<ul><li><span class='en-term'>Bid</span> = តម្លៃខ្ពស់បំផុតដែលអ្នកទិញ (limit buy) កំពុងរង់ចាំ · អ្នក <b>Sell</b> ភ្លាមនឹងលក់នៅ Bid</li>
<li><span class='en-term'>Ask</span> = តម្លៃទាបបំផុតដែលអ្នកលក់ (limit sell) កំពុងរង់ចាំ · អ្នក <b>Buy</b> ភ្លាមនឹងទិញនៅ Ask</li>
<li><span class='en-term'>Spread</span> = Ask − Bid · ឧ. Bid 4,120.10 · Ask 4,120.30 → spread $0.20 = <b>2 pips</b></li></ul>
<p>ពីនេះ យើងអាចបែងចែក volume ជាពីរ:</p>
<table><tr><th>ពាក្យ</th><th>អត្ថន័យ</th><th>បង្ហាញថា</th></tr>
<tr><td><span class='en-term'>Ask volume</span> (buy volume)</td><td>Trades ដែលកើតនៅ <b>Ask</b></td><td>Market <b>buy</b> (buyers aggressive)</td></tr>
<tr><td><span class='en-term'>Bid volume</span> (sell volume)</td><td>Trades ដែលកើតនៅ <b>Bid</b></td><td>Market <b>sell</b> (sellers aggressive)</td></tr></table>
""" + bars([("09:00", 420, BL), ("", 610, DN), ("09:05", 380, BL), (" ", 290, DN), ("09:10", 300, BL), ("  ", 720, DN)],
           caption="ឧទាហរណ៍ (លេខសម្មតិ): ខៀវ = Ask volume (market buy) · ក្រហម = Bid volume (market sell) · ទៀន 09:10 sellers aggressive ខ្លាំង") + """
<div class='box warn'>⚠️ ពាក្យ "Bid volume" ងាយច្រឡំ: វា<b>មិនមែន</b>ជា volume របស់អ្នកទិញទេ។ វាជា volume ដែល<b>ប៉ះ Bid</b> ពោលគឺអ្នក<b>លក់</b> aggressive។
ចងចាំ: <b>Ask = buyers ប្រញាប់ · Bid = sellers ប្រញាប់</b>។</div>
"""),
        ("តម្លៃផ្លាស់ទីយ៉ាងដូចម្ដេច?", """
<p>ឧបមាថា Ask មាន limit sell នៅកម្រិតនីមួយៗ: 5 lots នៅ 4,120.30 · 8 lots នៅ 4,120.40 · 12 lots នៅ 4,120.50។
ស្រាប់តែមាន <b>market buy 20 lots</b> ចូលមក:</p>
""" + ladders([("មុន market buy 20", [("4,120.60", 0, 9, ""), ("4,120.50", 0, 12, ""), ("4,120.40", 0, 8, ""), ("4,120.30", 0, 5, "Ask →"),
                                       ("4,120.10", 6, 0, "← Bid"), ("4,120.00", 10, 0, ""), ("4,119.90", 7, 0, "")]),
               ("ក្រោយ market buy 20", [("4,120.60", 0, 9, ""), ("4,120.50", 0, 5, "Ask →"), ("4,120.40", 0, 0, "អស់"), ("4,120.30", 0, 0, "អស់"),
                                        ("4,120.10", 6, 0, "← Bid"), ("4,120.00", 10, 0, ""), ("4,119.90", 7, 0, "")])],
              caption="Market buy 20 ស៊ី 5 + 8 + 7 lots · Ask ឡើងពី 4,120.30 ទៅ 4,120.50 · តម្លៃមធ្យមដែលទិញបាន ≈ 4,120.41") + """
<ul><li>កម្រិត 4,120.30 និង 4,120.40 ត្រូវបាន<b>ស៊ីអស់</b> · Ask ថ្មីឡើងទៅ 4,120.50</li>
<li>តម្លៃមធ្យម = (5×0.30 + 8×0.40 + 7×0.50) ÷ 20 → <b>4,120.41</b> មិនមែន 4,120.30 ទេ · ភាពខុសគ្នានេះជា <span class='en-term'>slippage</span></li>
<li>បើបន្ទាប់មក sellers ចូលមកបន្ថែម limit sell នៅ 4,120.40 វិញ តម្លៃអាចត្រឡប់ចុះ · តម្លៃគឺជាការប្រកួតរវាង aggressive និង passive រហូត</li></ul>
<div class='box tip'>💡 ច្បាប់ចងចាំ: <b>Aggressive orders ផ្លាស់ទីតម្លៃ · Passive orders បញ្ឈប់តម្លៃ</b>។ Support/Resistance (Chapter 7) គឺជាកន្លែងដែល passive orders ធំៗរង់ចាំ។</div>
"""),
        ("Liquidity និង Execution", """
<p><span class='en-term'>Liquidity</span> (ក្នុងន័យ execution) = <b>ចំនួន limit orders ដែលរង់ចាំ</b>នៅជិតតម្លៃបច្ចុប្បន្ន។
Liquidity ច្រើន = order ធំអាចប្រតិបត្តិបានដោយតម្លៃផ្លាស់ទីតិច។ Liquidity តិច = តម្លៃ "លោត" ងាយ។</p>
<table><tr><th>ពេល</th><th>Liquidity</th><th>អ្វីដែលអ្នកឃើញក្នុង MT5</th></tr>
<tr><td>London / New York (Chapter 16)</td><td>ច្រើន</td><td>Spread តូច · fill ល្អ</td></tr>
<tr><td>ចន្លោះ NY បិទ → Asia បើក (ព្រឹកព្រលឹមម៉ោងកម្ពុជា)</td><td>តិច</td><td>Spread ធំ · តម្លៃលោត</td></tr>
<tr><td>ព័ត៌មានធំ (NFP, CPI, FOMC)</td><td>ស្ទើរបាត់មួយភ្លែត</td><td>Spread ពង្រីក · slippage ធំ</td></tr></table>
""" + zigzag([40, 44, 41, 45, 42, 90, 74, 80, 70],
             {4: ("មុន news", BL), 5: ("លោត", DN), 6: ("ត្រឡប់", OR)},
             lines=[(62, 0, 4, "SL របស់អ្នក (Sell)", DN, True)],
             caption="ព័ត៌មានចេញ: limit orders ដកចេញ · តម្លៃលោតរំលង SL · SL ប្រតិបត្តិនៅតម្លៃអាក្រក់ជាង (slippage)") + """
<p><b>គណនា slippage</b>: SL Sell ដាក់នៅ 4,100.00 ប៉ុន្តែពេល news fill នៅ 4,101.50 → អាក្រក់ជាង $1.50 = <b>15 pips</b>។
ជាមួយ 0.01 lot (1 oz) នោះជាការខាតបន្ថែម <b>$1.50</b>។ ជាមួយ 0.10 lot វាក្លាយជា $15។</p>
<div class='box warn'>⚠️ Stop Loss <b>មិនមែនតម្លៃធានា</b>ទេ។ វាជា market order ដែលរង់ចាំ។ ពេល liquidity តិច វាអាចប្រតិបត្តិអាក្រក់ជាងកម្រិតដែលអ្នកដាក់។
មើល <b>📰 News</b> ក្នុង group មុនចូល trade ហើយកាត់បន្ថយ lot ឬជៀសវាងពេលព័ត៌មានធំ។</div>
"""),
        ("ការយល់ដឹងពី Order Book (DOM)", """
<p><span class='en-term'>Order book</span> ឬ <span class='en-term'>DOM</span> (Depth of Market) = បញ្ជី <b>limit orders</b> ដែលកំពុងរង់ចាំនៅតម្លៃនីមួយៗ:
limit buy នៅខាង Bid និង limit sell នៅខាង Ask។ វាបង្ហាញ<b>បំណង</b> (intent) របស់ passive traders មុនពេល trade កើតឡើង។</p>
""" + ladders([("Order book (ឧទាហរណ៍)", [("4,121.00", 0, 64, "round number"), ("4,120.80", 0, 14, ""), ("4,120.60", 0, 9, ""),
                                         ("4,120.40", 0, 11, "Ask →"), ("4,120.20", 13, 0, "← Bid"), ("4,120.00", 58, 0, "round number"),
                                         ("4,119.80", 12, 0, ""), ("4,119.60", 8, 0, "")])],
              caption="Limit orders ធំៗច្រើនប្រមូលនៅលេខមូល (4,120 · 4,121) · វាអាចបញ្ឈប់តម្លៃមួយភ្លែត ឬត្រូវគេស៊ីអស់") + """
<p><b>របៀបអាន:</b></p>
<ul><li>កម្រិតដែលមាន size <b>ធំខុសប្លែក</b> = កន្លែងដែល passive traders ចង់ការពារ · អាចដើរតួជា S/R រយៈខ្លី</li>
<li>មើលថា size នោះ<b>ត្រូវគេស៊ី</b> (ស្រកបន្តិចម្ដងៗ ដោយសារ trades) ឬ<b>ត្រូវដកចេញ</b> (បាត់ភ្លាមៗ មុនតម្លៃមកដល់)</li>
<li>ពេលកម្រិតធំត្រូវគេស៊ីអស់ ហើយតម្លៃឆ្លងហួស ជារឿយៗតម្លៃរត់លឿនទៅកម្រិតបន្ទាប់</li></ul>
<div class='box warn'>⚠️ <b>ដែនកំណត់:</b> limit orders អាច<b>ដកចេញ</b>បានគ្រប់ពេល ដោយមិនចំណាយអ្វី។ Order ធំមួយនៅលើ book អាចជា<b>ការបោក</b>
(<span class='en-term'>spoofing</span>, ខុសច្បាប់ប៉ុន្តែនៅតែកើតមាន) ឬជា<b>iceberg</b> ដែលបង្ហាញតែផ្នែកតូច (Chapter 24)។
Order book ប្រាប់ពី<b>បំណង</b> · Trades (Chapter 23) ប្រាប់ពី<b>សកម្មភាពពិត</b>។</div>
"""),
        ("Order Flow សម្រាប់មាស: ទិន្នន័យមកពីណា?", """
<p>នេះជាចំណុចសំខាន់សម្រាប់អ្នក trade មាសក្នុង MT5 (យើងនឹងពន្យល់លម្អិតក្នុង Chapter 25):</p>
<table style="break-inside: avoid"><tr><th></th><th>XAUUSD ក្នុង MT5 (broker CFD)</th><th>COMEX Gold Futures (GC)</th></tr>
<tr><td>ទីផ្សារ</td><td>Broker ផ្ដល់តម្លៃ · គ្មានទីផ្សារកណ្ដាល</td><td>Exchange កណ្ដាល (CME Group)</td></tr>
<tr><td>Volume</td><td>Tick volume (Chapter 18)</td><td>Real volume (contracts)</td></tr>
<tr><td>Order book</td><td>MT5 DOM បង្ហាញតែ quotes របស់ broker (បើមាន)</td><td>Order book ពិតរបស់ exchange</td></tr>
<tr><td>Bid/Ask volume ពិត</td><td>គ្មាន</td><td>មាន (ត្រូវការ data feed)</td></tr></table>
<ul><li>តម្លៃ spot XAUUSD និង GC futures ដើរ<b>ស្របគ្នា</b> ប៉ុន្តែមានគម្លាតតម្លៃ (futures ច្រើនខ្ពស់ជាងបន្តិច ដោយសារការប្រាក់ និងពេលផុតកំណត់)</li>
<li>ដូច្នេះ order flow ពិតសម្រាប់មាស ត្រូវមើលលើ <b>futures</b> ហើយបកប្រែកម្រិតតម្លៃមក chart MT5 ដោយប្រុងប្រយ័ត្ន</li>
<li>Indicator ណាដែលអះអាងថាបង្ហាញ "order flow ពិត" ពី tick volume របស់ broker គឺជាការ<b>ប៉ាន់ស្មាន</b>ប៉ុណ្ណោះ</li></ul>
<div class='box tip'>💡 អ្នកមិនចាំបាច់មាន order flow software ដើម្បី trade ជាមួយ XAU.KH ទេ។ ការយល់គំនិតនេះជួយឱ្យអ្នកយល់ <b>ហេតុអ្វី</b>
sweep, order block និង FVG ដំណើរការ ហើយអាចអាន 📊 <b>Analysis</b> និង 🚨 <b>Signals</b> បានច្បាស់ជាងមុន។</div>
"""),
        ("ភ្ជាប់ Order Flow ជាមួយអ្វីដែលអ្នកបានរៀន", """
<p>គំនិតជាច្រើនក្នុង Part 2–4 អាចពន្យល់ដោយ order flow:</p>
<table style="break-inside: avoid"><tr><th>គំនិត</th><th>ក្នុងភាសា order flow</th></tr>
<tr><td>Liquidity sweep (Ch 12)</td><td>Stop orders ក្លាយជា market orders · អ្នកធំប្រើវាជា liquidity ចូលទិសផ្ទុយ</td></tr>
<tr><td>Displacement / FVG (Ch 9, 13)</td><td>Aggressive orders ធំ ស៊ី liquidity ច្រើនកម្រិតលឿន · ទុកចន្លោះដែល trade តិច</td></tr>
<tr><td>Order Block (Ch 14)</td><td>តំបន់ដែលអ្នកធំបានចូល · ពេលត្រឡប់មក អាចមាន passive orders រង់ចាំម្ដងទៀត</td></tr>
<tr><td>LVN / HVN (Ch 19)</td><td>LVN = ឆ្លងលឿន (aggressive) · HVN = ប្រកួតយូរ (passive ច្រើន)</td></tr></table>
""" + flow([("Stops", "ប្រមូលលើ high", OR), ("Sweep", "stops → market", DN), ("Absorb", "អ្នកធំលក់ចូល", PU), ("Reverse", "MSS + FVG", UP)],
           caption="Sweep ពីទស្សនៈ order flow: buy stops ផ្ដល់ liquidity ឱ្យអ្នកលក់ធំ → តម្លៃបង្វិល") + """
<div class='box ok'>✅ ពេលអ្នកឃើញ <b>🚨 Signal</b> ដែលចូលក្រោយ sweep អ្នកដឹងហើយថា: ក្នុងពេល sweep stops ជាច្រើនបានក្លាយជា market orders
ហើយភាគីផ្ទុយបានប្រើ liquidity នោះ។ ប៉ុន្តែគ្មានអ្វីធានាទេ · SL នៅតែចាំបាច់ជានិច្ច។</div>
"""),
        ("កំហុសញឹកញាប់", """
<ul><li>❌ គិតថា "អ្នកទិញច្រើនជាងអ្នកលក់" (ចំនួនទិញ = ចំនួនលក់ជានិច្ច · មើល<b>ភាពប្រញាប់</b>)</li>
<li>❌ ច្រឡំ Bid volume ថាជា volume អ្នកទិញ (វាជា market <b>sell</b>)</li>
<li>❌ ជឿ order ធំលើ order book 100% (អាចដកចេញ ឬជា spoof)</li>
<li>❌ គិតថា Stop Loss ធានាតម្លៃ (វាក្លាយជា market order · អាចមាន slippage)</li>
<li>❌ ប្រើ "order flow indicator" លើ tick volume របស់ broker ហើយគិតថាជាទិន្នន័យ exchange</li>
<li>❌ ចូល trade ធំពេល news ដោយសារ "តម្លៃរត់លឿន" ខណៈ liquidity ស្ទើរគ្មាន</li></ul>
"""),
    ],
    summary=["Order flow = សិក្សា orders ដែលហូរចូល: អ្នកណាប្រញាប់ (aggressive) អ្នកណារង់ចាំ (passive)",
             "Market order យក liquidity (ទិញនៅ Ask លក់នៅ Bid) · Limit order ផ្ដល់ liquidity · Stop ក្លាយជា market order",
             "Ask volume = market buy · Bid volume = market sell",
             "Aggressive orders ផ្លាស់ទីតម្លៃ · Passive orders បញ្ឈប់តម្លៃ · liquidity តិច = slippage",
             "Order book បង្ហាញបំណង (អាចដកចេញ) · មាស MT5 គ្មាន order book ពិត · ទិន្នន័យពិតមកពី COMEX futures"],
    exercise=["ក្នុង MT5 បើក XAUUSD ហើយកត់ត្រា Bid, Ask និង spread (គិតជា pips) នៅម៉ោង 10:00, 15:00 និង 20:30 ម៉ោងកម្ពុជា។ ពេលណា spread ធំជាងគេ?",
              "Ask មាន 4 lots នៅ 4,125.20 · 6 lots នៅ 4,125.30 · 10 lots នៅ 4,125.40។ Market buy 12 lots: Ask ថ្មីនៅណា? តម្លៃមធ្យមប៉ុន្មាន?",
              "ពន្យល់ដោយពាក្យរបស់អ្នក: ហេតុអ្វីបានជា liquidity sweep ផ្ដល់ “liquidity” ដល់អ្នកធំ?",
              "មើល <b>📰 News</b> សប្ដាហ៍នេះ ហើយកំណត់ម៉ោងដែលអ្នកនឹងមិនដាក់ trade ថ្មី ដោយសារ liquidity អាចតិច។"],
)
