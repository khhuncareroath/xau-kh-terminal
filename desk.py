"""XAU.KH desk note: professional gold analysis in basic English + Khmer.

Built only from what the engine measured (ict.json, confluence.json, levels.json, live candles), so every number is
real. Reads like a bank desk note, in short simple sentences:
  1) Big picture (Daily / 4H / 1H bias, premium or discount of the 4H range)
  2) Structure (latest BOS / MSS and whether it had displacement)
  3) Liquidity (stops already taken, stops still waiting = targets)
  4) Key zones (fair value gaps and order blocks nearest above and below)
  5) XAU.KH quant (4H signal lines, Day Meter, VWAP)
  6) Plan (main scenario, other scenario, where the idea is wrong) + Khmer summary

note(...)        -> full note for the Analysis section (sessions)
trade_note(...)  -> the same thinking, centred on one signal, for Setup Analysis
quick(...)       -> 1-2 lines for random updates
"""
from datetime import datetime

import pandas as pd

BIAS_W = {"bull": "up ↑", "bear": "down ↓"}
BIAS_KM = {"bull": "ឡើង", "bear": "ចុះ"}
LIQ_NAMES = ("Prev day high", "Prev day low", "Asia high", "Asia low", "London high", "London low")


def f(x):
    return f"{x:,.2f}"


def _bias(ict, tf):
    return ((ict.get("timeframes") or {}).get(tf) or {}).get("bias")


def _events(ict, tf):
    return ((ict.get("timeframes") or {}).get(tf) or {}).get("last_events") or []


def _arrays(ict, price):
    """Nearest unfilled FVG / order block below (support) and above (resistance) price."""
    below, above = [], []
    for tf in ("15m", "1H", "4H"):
        t = (ict.get("timeframes") or {}).get(tf) or {}
        for kind, key in (("FVG", "fvgs"), ("OB", "order_blocks")):
            for z in t.get(key) or []:
                if z.get("status") in ("filled", "broken", "invalid"):
                    continue
                lo, hi = float(z["lo"]), float(z["hi"])
                item = {"tf": tf, "kind": kind, "dir": z["dir"], "lo": lo, "hi": hi}
                if z["dir"] == "bull" and hi <= price * 1.0005:
                    below.append(item)
                elif z["dir"] == "bear" and lo >= price * 0.9995:
                    above.append(item)
    below.sort(key=lambda z: price - z["hi"])
    above.sort(key=lambda z: z["lo"] - price)
    return below[:2], above[:2]


def _liquidity(lv, price):
    lad = {x["name"]: float(x["price"]) for x in lv.get("ladder", []) if x.get("price")}
    gap = price * 0.0012   # ignore levels price is sitting on (e.g. the session that is still forming)
    up = sorted([(p, n) for n, p in lad.items() if n in LIQ_NAMES and p > price + gap])
    dn = sorted([(p, n) for n, p in lad.items() if n in LIQ_NAMES and p < price - gap], reverse=True)
    return up, dn, lad


def _swept_today(ict):
    out = []
    today = datetime.now().date()
    for s in ict.get("sweeps") or []:
        try:
            t = pd.Timestamp(s["time"])
            if (pd.Timestamp.now(tz=t.tz) - t).total_seconds() > 20 * 3600:
                continue
        except Exception:
            pass
        out.append(s)
    return out[-2:]


def _ev_line(e, tf):
    what = "MSS (trend change)" if e["type"] == "MSS" else "BOS (trend continues)"
    side = "buyers" if e["dir"] == "bull" else "sellers"
    disp = " with strong candles (displacement)" if e.get("displacement") else " but with weak candles"
    return f"{tf}: {e['dir']} {what} at <b>{f(e['level'])}</b>{disp} → {side} broke a level."


def facts(ict, conf, lv, df, lines, day_used=None):
    price = float(df["Close"].iloc[-1])
    upper, lower = float(lines[0]), float(lines[1])
    rng = upper - lower
    pos = (price - lower) / rng if rng > 0 else 0.5
    below, above = _arrays(ict, price)
    up_liq, dn_liq, lad = _liquidity(lv, price)
    b = {tf: _bias(ict, tf) for tf in ("D", "4H", "1H", "15m")}
    votes = sum(1 if b[tf] == "bull" else -1 if b[tf] == "bear" else 0 for tf in ("D", "4H", "1H"))
    lean = "bull" if votes >= 2 else "bear" if votes <= -2 else None
    return dict(price=price, upper=upper, lower=lower, pos=pos, mid=lower + rng / 2, below=below, above=above,
                up_liq=up_liq, dn_liq=dn_liq, lad=lad, bias=b, lean=lean, swept=_swept_today(ict),
                ev15=(_events(ict, "15m") or [None])[-1], ev1h=(_events(ict, "1H") or [None])[-1], day_used=day_used)


def _zone(z):
    return f"{z['tf']} {'bull' if z['dir'] == 'bull' else 'bear'} {z['kind']} <b>{f(z['lo'])}–{f(z['hi'])}</b>"


def _sections(F, breakout=False):
    p = F["price"]
    out = []
    # 1) big picture
    b = F["bias"]
    bt = " · ".join(f"{tf} {BIAS_W.get(b[tf], 'mixed ↔')}" for tf in ("D", "4H", "1H"))
    who = {"bull": "Buyers are in control.", "bear": "Sellers are in control.", None: "No clear side. Be patient."}[F["lean"]]
    zone = "discount (cheap)" if F["pos"] < 0.45 else "premium (expensive)" if F["pos"] > 0.55 else "the middle (fair price)"
    good = ("Breakout trades leave the range, so this matters less now." if breakout else
            "Better to buy than to sell here." if F["pos"] < 0.45 else "Better to sell than to buy here." if F["pos"] > 0.55
            else "No edge in the middle. Wait for an edge.")
    out += ["<b>1) Big picture · រូបភាពធំ</b>",
            f"• {bt}. {who}",
            f"• 4H range {f(F['lower'])} – {f(F['upper'])}. Price is in <b>{zone}</b> ({F['pos'] * 100:.0f}% of the range). {good}",
            f"  <i>ពាក់កណ្ដាល {f(F['mid'])}: ក្រោម = ថោក (រកទិញ) · លើ = ថ្លៃ (រកលក់)</i>", ""]
    # 2) structure
    ev = [x for x in ((F["ev15"], "15m"), (F["ev1h"], "1H")) if x[0]]
    if ev:
        out += ["<b>2) Structure · រចនាសម្ព័ន្ធ</b>"] + [f"• {_ev_line(e, tf)}" for e, tf in ev]
        out += ["  <i>BOS = បំបែកទៅទិសដដែល · MSS = ប្ដូរទិស</i>", ""]
    # 3) liquidity
    liq = ["<b>3) Liquidity · កន្លែងដែល stop ដេក</b>"]
    for s in F["swept"]:
        liq.append(f"• Taken: {'sell' if s['side'] == 'sell-side' else 'buy'}-side stops at {s['name']} <b>{f(s['level'])}</b> ✅ "
                   f"({'sellers were trapped, good for buyers' if s['side'] == 'sell-side' else 'buyers were trapped, good for sellers'})")
    if F["up_liq"]:
        liq.append("• Stops above (buy-side, magnet up): " + " · ".join(f"{n} <b>{f(x)}</b>" for x, n in F["up_liq"][:2]))
    if F["dn_liq"]:
        liq.append("• Stops below (sell-side, magnet down): " + " · ".join(f"{n} <b>{f(x)}</b>" for x, n in F["dn_liq"][:2]))
    liq.append("  <i>តម្លៃច្រើនតែរត់ទៅយក stop មុន រួចទើបដើរពិត</i>")
    out += liq + [""]
    # 4) zones
    if F["below"] or F["above"]:
        out += ["<b>4) Key zones (FVG / OB) · តំបន់សំខាន់</b>"]
        if F["below"]:
            out.append("• Buy zone below: " + " · ".join(_zone(z) for z in F["below"]))
        if F["above"]:
            out.append("• Sell zone above: " + " · ".join(_zone(z) for z in F["above"]))
        out += ["  <i>FVG = ចន្លោះតម្លៃដែលរត់លឿន · OB = ទៀនចុងក្រោយមុនចលនាធំ</i>", ""]
    # 5) quant
    q = ["<b>5) XAU.KH quant · ទិន្នន័យសាកល្បង</b>",
         f"• 4H signal: BUY if a 4H candle closes above <b>{f(F['upper'])}</b> ({F['upper'] - p:+,.1f}) · "
         f"SELL if it closes below <b>{f(F['lower'])}</b> ({F['lower'] - p:+,.1f})"]
    du = F.get("day_used")
    if du is not None:
        q.append(f"• Day Meter <b>{du * 100:.0f}%</b> of a normal day: "
                 + ("🖕🖕 PREMIUM zone (big day, breakouts tested 77% win)" if du >= 1.0 else
                    "🖕 COMBO zone (breakouts tested 68% win)" if du >= 0.7 else
                    "quiet day (breakouts only ~50/50, smaller size)"))
    vw = F["lad"].get("VWAP")
    if vw:
        q.append(f"• VWAP <b>{f(vw)}</b>: price {'above → intraday buyers stronger' if p > vw else 'below → intraday sellers stronger'}")
    out += q + [""]
    return out


def _plan(F):
    p = F["price"]
    lean = F["lean"]
    if lean is None:
        lean = "bull" if F["pos"] < 0.35 else "bear" if F["pos"] > 0.65 else None
    up_t = [x for x, _ in F["up_liq"]][:2]
    dn_t = [x for x, _ in F["dn_liq"]][:2]
    if lean == "bull":
        z = F["below"][0] if F["below"] else None
        inv = z["lo"] if z else (dn_t[0] if dn_t else p * 0.995)
        main = (f"🟢 <b>Main</b>: price dips into {_zone(z)} and holds → buyers aim for "
                if z else "🟢 <b>Main</b>: buyers stay in control → aim for ") + \
               (" then ".join(f"<b>{f(x)}</b>" for x in up_t) or f"<b>{f(F['upper'])}</b>") + "."
        alt = f"🔴 <b>Other</b>: a 15m close below <b>{f(inv)}</b> → buy idea is wrong, sellers aim for " + \
              (" then ".join(f"<b>{f(x)}</b>" for x in dn_t) or f"<b>{f(F['lower'])}</b>") + "."
        km = (f"សរុប: ទិសដៅធំ <b>ឡើង</b>។ រង់ចាំតម្លៃធ្លាក់មក {f(z['lo'])}–{f(z['hi'])} ហើយឈរបាន ទើបរកទិញ។ "
              if z else "សរុប: ទិសដៅធំ <b>ឡើង</b>។ ")+ f"បើបិទក្រោម {f(inv)} គំនិតទិញខុស។"
    elif lean == "bear":
        z = F["above"][0] if F["above"] else None
        inv = z["hi"] if z else (up_t[0] if up_t else p * 1.005)
        main = (f"🔴 <b>Main</b>: price pulls up into {_zone(z)} and fails → sellers aim for "
                if z else "🔴 <b>Main</b>: sellers stay in control → aim for ") + \
               (" then ".join(f"<b>{f(x)}</b>" for x in dn_t) or f"<b>{f(F['lower'])}</b>") + "."
        alt = f"🟢 <b>Other</b>: a 15m close above <b>{f(inv)}</b> → sell idea is wrong, buyers aim for " + \
              (" then ".join(f"<b>{f(x)}</b>" for x in up_t) or f"<b>{f(F['upper'])}</b>") + "."
        km = (f"សរុប: ទិសដៅធំ <b>ចុះ</b>។ រង់ចាំតម្លៃឡើងមក {f(z['lo'])}–{f(z['hi'])} ហើយធ្លាក់វិញ ទើបរកលក់។ "
              if z else "សរុប: ទិសដៅធំ <b>ចុះ</b>។ ") + f"បើបិទលើ {f(inv)} គំនិតលក់ខុស។"
    else:
        hi_ = up_t[0] if up_t else F["upper"]
        lo_ = dn_t[0] if dn_t else F["lower"]
        main = f"↔ <b>Range</b>: no clear side. Sellers defend near <b>{f(hi_)}</b>, buyers near <b>{f(lo_)}</b>."
        alt = "⏳ Best trade may be no trade. Wait for the 4H signal or a clean sweep + structure shift."
        km = f"សរុប: ទីផ្សារ <b>ចំហៀង</b>។ កុំបង្ខំចូល។ រង់ចាំនៅជិត {f(hi_)} ឬ {f(lo_)} ឬរង់ចាំសញ្ញា 4H។"
    return ["<b>6) Plan · ផែនការ</b>", main, alt, "", f"📌 {km}"]


def note(ict, conf, lv, df, lines, title, day_used=None):
    F = facts(ict, conf, lv, df, lines, day_used)
    head = [f"🏦 <b>GOLD DESK NOTE · {title}</b>", f"Gold <b>{f(F['price'])}</b>", ""]
    tail = ["", "<i>Analysis = education. Trades only in 📈 Signals · ការវិភាគ = ការសិក្សា</i>"]
    return "\n".join(head + _sections(F) + _plan(F) + tail)


def trade_note(ict, conf, lv, df, lines, sig, stamp, day_used=None, tested=None):
    """Setup Analysis for one signal: why, what supports it, what is against it, what makes it fail."""
    F = facts(ict, conf, lv, df, lines, day_used)
    bull = sig["dir"] == "bull"
    side = "BUY" if bull else "SELL"
    pro, con = [], []
    b = F["bias"]
    agree = [tf for tf in ("D", "4H", "1H") if b[tf] == ("bull" if bull else "bear")]
    against = [tf for tf in ("D", "4H", "1H") if b[tf] == ("bear" if bull else "bull")]
    if agree:
        pro.append(f"Trend agrees on {', '.join(agree)}.")
    if against:
        con.append(f"Trend is the other way on {', '.join(against)}.")
    if day_used is not None:
        (pro if day_used >= 0.7 else con).append(
            f"Day Meter {day_used * 100:.0f}%: " + ("the day is moving, breakouts work better." if day_used >= 0.7
                                                    else "quiet day, breakouts often fail. Use half size."))
    ef = sig.get("efficiency")
    if ef is not None:
        (pro if ef > 0.255 else con).append(
            f"Trend quality {ef:.2f}: " + ("clean trend. COMBO in a clean trend won about 70% in testing."
                                           if ef > 0.255 else "choppy market, breakouts were weaker in testing."))
    vw = F["lad"].get("VWAP")
    if vw:
        ((pro if (F["price"] > vw) == bull else con)
         .append(f"Price is {'above' if F['price'] > vw else 'below'} VWAP {f(vw)}."))
    liq = F["up_liq"] if bull else F["dn_liq"]
    if liq:
        pro.append(f"Stops are waiting at {liq[0][1]} {f(liq[0][0])}: a magnet for this trade.")
    opp = F["above"] if bull else F["below"]
    if opp and abs((opp[0]["lo"] if bull else opp[0]["hi"]) - sig["entry"]) < abs(sig.get("tp1", sig["target"]) - sig["entry"]):
        con.append(f"{_zone(opp[0])} is before TP1: price may slow there.")
    out = [f"🔍 <b>SETUP ANALYSIS · {side} {f(sig['entry'])}</b> · {stamp}", "",
           "<b>Why this trade · ហេតុអ្វីចូល</b>",
           f"• A 4H candle closed {'above the highest high' if bull else 'below the lowest low'} of the last 30 4H candles "
           f"(<b>{f(sig.get('level') or (F['upper'] if bull else F['lower']))}</b>). {'Buyers' if bull else 'Sellers'} broke a 5-day range.",
           f"  <i>ទៀន 4H បិទ{'លើ' if bull else 'ក្រោម'}កម្រិតខ្ពស់/ទាបបំផុត 5 ថ្ងៃ = {'អ្នកទិញ' if bull else 'អ្នកលក់'}ឈ្នះ</i>"]
    if tested:
        out.append(f"• Tested 2 years: {tested}")
    out += ["", "<b>✅ For the trade</b>"] + [f"• {x}" for x in pro or ["Only the breakout itself."]]
    out += ["", "<b>⚠️ Against the trade</b>"] + [f"• {x}" for x in con or ["Nothing major."]]
    out += ["", "<b>❌ The trade is wrong if</b>",
            f"• Price hits SL <b>{f(sig['stop'])}</b>. No moving the stop further. · ប៉ះ SL = ចេញ មិនពន្យារ"]
    if sig.get("tp1"):
        out.append(f"• At TP1 <b>{f(sig['tp1'])}</b>: close half, move SL to entry. Then the trade is free. · TP1 = ការពារ")
    out += [""] + _sections(F, breakout=True)[:-1] + ["", f"📌 {_km_trade(bull, F, sig, pro, con)}"]
    return "\n".join(out)


def _km_trade(bull, F, sig, pro, con):
    s = "ទិញ" if bull else "លក់"
    q = "ល្អ" if len(pro) > len(con) else "មធ្យម ប្រើ lot តូច" if len(pro) == len(con) else "ខ្សោយ ប្រើ lot តូច ឬរំលង"
    return f"សរុប: សញ្ញា{s} 4H ។ គុណភាព setup: <b>{q}</b>។ ចូល {f(sig['entry'])} · SL {f(sig['stop'])} · គោលដៅ {f(sig['target'])}។"


def quick(ict, lv, df, lines):
    """1-2 lines of desk context for random updates."""
    F = facts(ict, {}, lv, df, lines)
    out = []
    e = F["ev15"]
    if e:
        out.append(f"🧭 15m {'buyers' if e['dir'] == 'bull' else 'sellers'} broke {f(e['level'])} ({e['type']})"
                   + (" with strong candles" if e.get("displacement") else ""))
    zone = "discount (cheap)" if F["pos"] < 0.45 else "premium (expensive)" if F["pos"] > 0.55 else "middle of the range"
    tgt = (F["up_liq"][0] if F["lean"] == "bull" and F["up_liq"] else F["dn_liq"][0] if F["lean"] == "bear" and F["dn_liq"] else None)
    out.append(f"💧 Price in {zone}" + (f" · next stops: {tgt[1]} {f(tgt[0])}" if tgt else ""))
    return out
