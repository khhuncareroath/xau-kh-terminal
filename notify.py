"""Best-setup alert, v2. Sends ONE idea when it passes every gate, then track.py grades it and replies with the result.

Hard gates (any one fails -> no alert):
  * setup tracker at "shift confirmed" or "retest in play", with entry/stop/target and R:R >= MIN_RR
  * the idea is fresh: structure shift less than ALERT_EXPIRE_MIN ago, and the data is not stale
  * price has NOT already run more than half the risk past the entry (the stale-entry problem),
    and is not already near the stop
  * stop no wider than MAX_RISK_ATR x the 5m ATR (no 18-point stops on a 5-point market)
  * no high-impact USD news within 60 minutes (postnews.py handles the reaction afterwards)
  * at least MIN_FACTORS of the 7 factors below

The 7 factors are shown openly in the alert ("5 of 7"), and the backtest line tells people how these rules
really did on past data. Env: MIN_RR (1.5), MIN_FACTORS (3), MAX_RISK_ATR (3), ALERT_EXPIRE_MIN (120),
ALERT_COOLDOWN_H (3), SITE_URL, DISPLAY_TZ. Analysis ideas, not signals or advice."""
import json
import re
import os
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from ai_analyst import explain
from tg import SITE, esc, fmt, local, log_alert, send

MIN_RR = float(os.environ.get("MIN_RR", 1.5))
MIN_FACTORS = int(os.environ.get("MIN_FACTORS", 3))
MAX_RISK_ATR = float(os.environ.get("MAX_RISK_ATR", 3.0))
EXPIRE_MIN = float(os.environ.get("ALERT_EXPIRE_MIN", 120))
COOLDOWN = float(os.environ.get("ALERT_COOLDOWN_H", 3)) * 3600
STALE_MIN = 40
MODE = os.environ.get("ALERT_MODE", "auto")   # auto: trade-style only if backtest.json proves the rules; else "watch" posts
from engine import live_source
TV = ("https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD" if live_source() == "spot"
      else "https://www.tradingview.com/chart/?symbol=COMEX%3AGC1%21")
NY = ZoneInfo("America/New_York")


def jl(n):
    try:
        return json.load(open(n))
    except Exception:
        return {}


def ts(s):
    return datetime.fromisoformat(str(s)).timestamp()


def news_soon(news, mins=60, now=None):
    now = now or time.time()
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        try:
            m = (ts(e["time"].replace("Z", "+00:00")) - now) / 60
        except Exception:
            continue
        if -15 <= m <= mins:
            return f"{e['title']} in {max(0, round(m))} min"
    return None


def kill_zone(now):
    h = datetime.fromtimestamp(now, NY).hour
    return "London" if 2 <= h < 5 else "New York" if 7 <= h < 11 else None


def factors(st, ict, conf, lv, macro, now):
    d = st["dir"]
    h1 = ((ict.get("timeframes") or {}).get("1H") or {}).get("bias")
    vw = next((x["price"] for x in lv.get("ladder", []) if x["name"] == "VWAP"), None)
    price = ict.get("price")
    lo, hi = st["zone"]
    zone_hit = next((z for z in conf.get("zones", []) if z.get("rating") in ("A", "B") and z["low"] <= hi + 1 and z["high"] >= lo - 1), None)
    kz = kill_zone(now)
    m = macro.get("score")
    return [
        ("1H trend agrees", h1 == d, f"1H structure is {h1 or 'unclear'}"),
        ("Displacement", bool(st.get("displacement")), "the shift candle was strong" if st.get("displacement") else "the shift was weak"),
        ("VWAP side", vw is not None and price is not None and ((price > vw) == (d == "bull")), f"price {'above' if price and vw and price > vw else 'below'} VWAP {vw}"),
        ("Confluence zone", zone_hit is not None, f"overlaps {zone_hit['rating']} zone {zone_hit['low']}-{zone_hit['high']}" if zone_hit else "no A/B zone at the entry"),
        ("Kill zone", kz is not None, f"{kz} window" if kz else "outside London/New York windows"),
        ("Stop size", (st.get("risk_atr") or 99) <= MAX_RISK_ATR * 0.67, f"stop is {st.get('risk_atr')} ATR"),
        ("Dollar/yields", m is not None and m != 0 and ((m > 0) == (d == "bull")), (macro.get("verdict") or "macro unknown").lower()),
    ]


def backtest_line(bt, rules):
    s = (((bt or {}).get("rules") or {}).get(rules) or {}).get("summary") or {}
    n = s.get("filled", 0)
    if not n:
        return None
    days = ""
    try:
        days = f"{(ts(bt['data']['to']) - ts(bt['data']['from'])) / 86400:.0f} days, "
    except Exception:
        pass
    tail = " Sample still small." if n < 30 else ""
    return (f"Backtest ({days}same rules, with 15 min alert delay and costs): {n} trades, "
            f"{s['win_rate_pct']}% hit target, {s['avg_R']:+.2f}R per trade.{tail}")


def gate_setup(st, ict, now):
    """Returns (ok, reason). These are the checks that would have stopped the stale posts."""
    if (st.get("stage") or 0) not in (2, 3) or not st.get("dir"):
        return False, "no live setup"
    if not all(st.get(k) for k in ("entry", "stop", "target", "zone")):
        return False, "setup has no retest zone"
    if (st.get("rr") or 0) < MIN_RR:
        return False, f"R:R {st.get('rr')} below {MIN_RR}"
    if st.get("shift_time") and (now - ts(st["shift_time"])) / 60 > EXPIRE_MIN:
        return False, "setup is older than the order window"
    if ict.get("last_bar") and (now - ts(ict["last_bar"])) / 60 > STALE_MIN:
        return False, "data is stale (market closed or feed delayed)"
    sg = 1 if st["dir"] == "bull" else -1
    risk = abs(st["entry"] - st["stop"])
    ran = (ict["price"] - st["entry"]) * sg / risk
    if ran > 0.5:
        return False, f"price already {ran:.1f}R past the entry"
    if ran < -0.7:
        return False, "price is already close to the stop"
    if (st.get("risk_atr") or 0) > MAX_RISK_ATR:
        return False, f"stop is {st['risk_atr']} ATR wide (max {MAX_RISK_ATR})"
    return True, ""


def spot_line(entry):
    sp = jl("spot.json")
    if not sp.get("basis") or time.time() - sp.get("t", 0) > 3600:
        return None
    return f"Spot XAUUSD ≈ futures − {sp['basis']:.1f} (entry ≈ {fmt(entry - sp['basis'])})"


PLAIN = {"breakout_cisd": {
    "bull": "Gold broke above its 1-week range, then swept sellers' stops and flipped back up (CISD). Entry with the stop under the sweep.",
    "bear": "Gold broke below its 1-week range, then swept buyers' stops and flipped back down (CISD). Entry with the stop above the sweep."},
    "trend_tight": {
    "bull": "Gold just closed a 4-hour candle above its highest price of the past week. Breakouts like this often run further.",
    "bear": "Gold just closed a 4-hour candle below its lowest price of the past week. Breakdowns like this often run further."},
    "trend_buy": {
    "bull": "Gold just closed a 4-hour candle above its highest price of the past week. Breakouts like this often run further.",
    "bear": ""},
    "trend_breakout": {
    "bull": "Gold just closed a 4-hour candle above its highest price of the past week. Breakouts like this often run further.",
    "bear": "Gold just closed a 4-hour candle below its lowest price of the past week. Breakdowns like this often run further."}}


def model_alert(lm, state, now):
    """Trade alert for a research model that backtest.json marks as proven (see research.py for the rules).
    Entry is at the current price, as the backtest assumes. ALERT_MODE=watch turns these off. Returns True if sent."""
    if MODE == "watch":
        return False
    sigs = [s for s in lm.get("signals", []) if s.get("proven") and s.get("model") not in PLAN_MODELS]
    import research
    trend = [m for m in research.TREND_PREFERENCE if any(s["model"] == m for s in sigs)]
    if trend:                                                # same breakout: alert only the preferred proven version
        sigs = [s for s in sigs if s["model"] not in research.TREND_PREFERENCE or s["model"] == trend[0]]
    if not sigs or (now - ts(lm.get("last_bar", "1970-01-01T00:00:00+00:00"))) / 60 > STALE_MIN:
        return False
    s = max(sigs, key=lambda x: (x.get("backtest") or {}).get("avg_R") or 0)
    key = f"model|{s['model']}|{s['trigger_time']}"
    if key in state.get("model_keys", []):
        return False
    import research
    # PREMIUM SWING: the same breakout on a big day is sent as the 5-day swing version (wider SL, holds up to 5 days)
    models_bt = jl("backtest.json").get("models", {})
    premium = False
    if s["model"] in research.TREND_PREFERENCE and (models_bt.get("trend_premium") or {}).get("proven"):
        tt = next((x for x in lm.get("signals", []) if x.get("model") == "trend_tight" and x.get("dir") == s["dir"]
                   and x.get("trigger_time") == s.get("trigger_time")), None)
        du_ = (tt or {}).get("day_used") if tt else None
        if tt and du_ is not None and du_ >= research.PREMIUM_USED:
            s, premium = tt, True
            key = f"model|trend_premium|{s['trigger_time']}"
            if key in state.get("model_keys", []):
                return False
    bull = s["dir"] == "bull"
    b = (models_bt.get("trend_premium") or {}).get("all") if premium else (s.get("backtest") or {})
    side = ((jl("backtest.json").get("models", {}).get(s["model"], {}).get("by_direction") or {}).get("long" if bull else "short") or {})
    hold_h = research.MAX_HOLD_H.get(s["model"], 24)
    out = []
    pips = lambda px: f"{(px - s['entry']) * (1 if bull else -1) * 1:+,.1f} លេខ"
    why_short = {"bull": "4H breakout: a 4H candle closed above this week's high. Big moves often start like this.",
                 "bear": "4H breakdown: a 4H candle closed below this week's low. Big drops often start like this."}
    du = s.get("day_used") if s["model"] in research.TREND_PREFERENCE else None
    strong = du is not None and du >= research.COMBO_USED
    eff = s.get("efficiency")
    if not premium and du is not None and not strong:
        # COMBO only (owner's choice, 11 Nov 2026): quiet-day breakouts were ~50/50 (+0.02R) → skip and say why
        state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
        json.dump(state, open("notify_state.json", "w"))
        send(f"⏭ <b>4H {'BUY' if bull else 'SELL'} breakout skipped</b> at {fmt(s['entry'])}\n"
             f"Quiet day: only {du * 100:.0f}% of a normal day has moved (COMBO needs 70%). "
             f"Quiet-day breakouts were about 50/50 in 2 years of testing, so we only send COMBO.\n"
             f"<i>ថ្ងៃស្ងាត់ = មិនផ្ញើសញ្ញា · យើងផ្ញើតែ 🖕 COMBO</i>", "Setup skipped")
        print("model skipped: quiet day", key)
        return False
    cb = (jl("backtest.json").get("models", {}).get("trend_combo") or {}).get("all") or {}
    combo_line = None
    if premium:
        combo_line = (f"🖕🖕 <b>PREMIUM SWING</b>: 4H breakout on a big day ({du * 100:.0f}% of a normal day already moved). "
                      f"Rare: about 1 every 1–2 weeks. Hold 1–5 days · ឱកាសល្អ កាន់ 1–5 ថ្ងៃ")
    elif du is not None:
        combo_line = (f"🖕 <b>STRONG COMBO</b>: 4H breakout + the day is already moving ({du * 100:.0f}% of a normal day)."
                      + (f" Tested: {cb['trades']} trades · {cb['win_rate_pct']}% win." if cb.get("trades") else "")
                      if strong else
                      f"◽ <b>Normal</b>: quiet day so far ({du * 100:.0f}% of a normal day). Quiet-day breakouts were about "
                      f"50/50 in testing → half size (0.5%) or skip · ថ្ងៃស្ងាត់ ប្រើ lot តូច")
    if LANG != "km":
        out += [f"{'🟢' if bull else '🔴'} <b>GOLD {'BUY' if bull else 'SELL'} NOW · {'ទិញ' if bull else 'លក់'}ឥឡូវ</b>  ✅ tested"
                + ("  🖕🖕 PREMIUM" if premium else "  🖕 COMBO" if strong else ""), "",
                f"Entry  <b>{fmt(s['entry'])}</b>",
                f"SL       <b>{fmt(s['stop'])}</b>  ({pips(s['stop'])})",
                *([f"TP1    <b>{fmt(s['tp1'])}</b>  ({pips(s['tp1'])}) · close half, SL to entry",
                   f"TP2    <b>{fmt(s['target'])}</b>  ({pips(s['target'])})"] if s.get("tp1") else
                  [f"TP     <b>{fmt(s['target'])}</b>  ({pips(s['target'])})"]),
                "",
                esc(why_short["bull" if bull else "bear"] if s["model"] in ("trend_tight", "trend_breakout", "trend_buy", "trend_intraday")
                    else PLAIN.get(s["model"], {}).get("bull" if bull else "bear", s["description"] + ".")),
                (f"Tested 2 years: {b.get('trades')} trades · {b.get('win_rate_pct')}% win" if b.get("trades") else None),
                combo_line,
                (f"⚠️ {'Buys' if bull else 'Sells'} are the weaker side: use a smaller size." if side.get("trades") and side["avg_R"] < 0.1
                 and s["model"] != "trend_buy" else None),
                ("<i>Intraday: everything closes within 12 h. SL ~$22 is the tested minimum for this signal: use a smaller lot. "
                 "បិទក្នុងថ្ងៃ · ប្រើ lot តូច</i>") if s["model"] == "trend_intraday" else
                ("<i>Swing trade, 1–5 days: wide SL on purpose, use a smaller lot · SL ធំ ប្រើ lot តូច</i>")
                if s["model"] in ("trend_tight", "trend_breakout", "trend_buy") else None,
                f"⏰ Enter within 15 min · holds up to {hold_h // 24} days" if hold_h >= 48 else f"⏰ Enter within 15 min · closes within {hold_h} h",
                "", "<i>Risk 0.5–1% of your account · ប្រើហានិភ័យ 0.5–1% ប៉ុណ្ណោះ</i>"]
    else:
        out += [f"{'🟢' if bull else '🔴'} <b>មាស · {'ទិញ' if bull else 'លក់'}ឥឡូវ</b>",
                f"ចូល <b>{fmt(s['entry'])}</b>", f"SL <b>{fmt(s['stop'])}</b>",
                *([f"TP1 <b>{fmt(s['tp1'])}</b> → បិទពាក់កណ្ដាល ប្ដូរ SL មកចំណុចចូល", f"TP2 <b>{fmt(s['target'])}</b>"] if s.get("tp1")
                  else [f"TP <b>{fmt(s['target'])}</b>"]),
                "<i>ប្រើហានិភ័យ 0.5–1% នៃគណនីប៉ុណ្ណោះ។</i>"]
    # 1) 📈 Signals: one clean card + short caption (the explanation goes to 🔍 Setup Analysis)
    tier = "premium" if premium else "combo" if strong else "normal" if du is not None else "combo"
    pp = lambda px: f"{abs(px - s['entry']) * 10:,.0f}"
    st_ = cb if (strong and not premium and cb.get("trades")) else (b or {}) if (premium or du is None or strong) else {}
    wr = st_.get("win_rate_pct")   # quiet-day (normal) breakouts were ~50/50: no win rate is promised
    caption = "\n".join(l for l in [
        f"{'🟢' if bull else '🔴'} <b>XAU/USD — {'BUY' if bull else 'SELL'}</b> | "
        + ("🖕🖕 PREMIUM SWING" if premium else "🖕 COMBO" if strong else "◽ NORMAL · half size" if du is not None else "4H BREAKOUT"),
        f"🇰🇭 <b>{'ទិញ' if bull else 'លក់'}មាសឥឡូវ</b> · ចូល {fmt(s['entry'])} · SL {fmt(s['stop'])} · "
        + (f"TP1 {fmt(s['tp1'])} (បិទពាក់កណ្ដាល) · TP2 {fmt(s['target'])}" if s.get("tp1") else f"TP {fmt(s['target'])}"),
        f"📍 Entry: <b>{fmt(s['entry'])}</b>",
        f"🛑 SL: <b>{fmt(s['stop'])}</b> ({pp(s['stop'])} pips)",
        *([f"🎯 TP1: <b>{fmt(s['tp1'])}</b> (+{pp(s['tp1'])}) → close half, SL to entry",
           f"🎯 TP2: <b>{fmt(s['target'])}</b> (+{pp(s['target'])})"] if s.get("tp1") else
          [f"🎯 TP: <b>{fmt(s['target'])}</b> (+{pp(s['target'])})"]),
        (f"📊 Win rate: {wr}% (tested 2 years, {st_.get('trades')} trades)" if wr else
         "📊 Quiet day: about 50/50 in testing → half size or skip" if du is not None else None),
        # real money per 0.01 lot (1 oz: $1 move = $1), so members size by dollars, not by a "small SL"
        f"💰 0.01 lot: SL −${abs(s['entry'] - s['stop']):,.0f}"
        + (f" · TP1 +${abs(s['tp1'] - s['entry']) * 0.5:,.0f} (half) · TP2 +${abs(s['target'] - s['entry']) * 0.5:,.0f} (half)" if s.get("tp1")
           else f" · TP +${abs(s['target'] - s['entry']):,.0f}")
        + f" · use 0.01 lot per ${abs(s['entry'] - s['stop']) * 100:,.0f} of account (1% risk)",
        f"⏱ 4H breakout · " + (f"hold up to {hold_h // 24} days" if hold_h >= 48 else f"closes within {hold_h} h"),
        "⏰ Enter within 15 min · risk 0.5–1% · ចូលក្នុង 15 នាទី",
    ] if l)
    mid = None
    try:
        import signal_card
        from engine import load
        from levels import to_ny
        d5 = to_ny(load("5m", "20d")).iloc[:-1]
        from ict import resample as _rs
        import pandas as _pd
        d4_ = _rs(d5, "4H")
        done_ = d4_[d4_.index + _pd.Timedelta(hours=4) <= d5.index[-1] + _pd.Timedelta(minutes=5)].iloc[:-1].tail(30)
        up_, lo_ = float(done_["High"].max()), float(done_["Low"].min())   # the line the breakout candle closed through
        signal_card.make(d5, {"dir": s["dir"], "entry": s["entry"], "stop": s["stop"], "tp1": s.get("tp1"),
                              "target": s["target"], "level": up_ if bull else lo_},
                         "signal_card.png", tier=tier, status="LIVE", win_rate=wr, trades=st_.get("trades"),
                         stamp=local(now), hold_note=f"hold up to {hold_h // 24} days" if hold_h >= 48 else f"closes within {hold_h} h")
        from tg import send_photo
        mid = send_photo("signal_card.png", caption, ("BUY" if bull else "SELL") + " now")
    except Exception as e:
        print("signal card failed, sending text:", e)
    if not mid:
        mid = send(caption, ("BUY" if bull else "SELL") + " now")
    if not mid:
        return False
    state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
    json.dump(state, open("notify_state.json", "w"))
    log_alert({"id": key, "kind": "model", "model": s["model"], "dir": s["dir"], "entry": s["entry"], "stop": s["stop"],
               "target": s["target"], "rr": s["rr"], "created": now, "valid_until": now + 900, "price_at_alert": s["entry"],
               "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now, "fill": s["entry"],
               "max_hold_s": hold_h * 3600, "tier": tier, **({"tp1": s["tp1"], "part": s.get("part", 0.5)} if s.get("tp1") else {})})
    print("sent", key)
    # 2) 🔍 Setup Analysis: the professional breakdown (ICT + quant), separate from the clean signal feed
    try:
        import desk
        import session
        from engine import load
        from levels import to_ny
        from tg import msg_link, send_photo
        link = msg_link(mid, ("BUY" if bull else "SELL") + " now")
        d = to_ny(load("5m", "20d")).iloc[:-1]
        lines_ = session.breakout_lines(d)
        tested = (f"{st_.get('trades')} trades · {wr}% win" + (" (🖕🖕 PREMIUM)" if premium else " (🖕 COMBO)" if strong else "")) if wr else None
        text = desk.trade_note(jl("ict.json"), jl("confluence.json"), jl("levels.json"), d, lines_,
                               dict(s, level=up_ if bull else lo_) if "up_" in dir() else s, local(now), day_used=du, tested=tested)
        if link:
            text += f'\n\n👉 <a href="{link}">Open the signal · មើលសញ្ញា</a>'
        session.chart(d, jl("confluence.json"), jl("levels.json"), lines_, "signal_chart.png",
                      f"Gold · {'BUY' if bull else 'SELL'} setup · {local(now)}",
                      position={"dir": s["dir"], "entry": s["entry"], "stop": s["stop"], "tp1": s.get("tp1"), "tp2": s["target"]})
        pm = send_photo("signal_chart.png", f"🔍 <b>Setup analysis · {'BUY' if bull else 'SELL'} {fmt(s['entry'])}</b>", "Setup analysis")
        send(text, "Setup analysis", reply_to=pm if isinstance(pm, int) else None)
    except Exception as e:
        print("setup analysis failed:", e)
    return True


LANG = os.environ.get("BOT_LANG", "en")   # en, km, or both
if LANG == "both":   # English messages already carry Khmer labels inline; no second full block
    LANG = "en"
STRONG = 5   # factors needed to call an idea "strong"


def _swept_level(st):
    m = re.search(r"at (\d{3,5}(?:\.\d+)?) was swept", " ".join(st.get("reasons", [])))
    return float(m.group(1)) if m else st.get("sweep_extreme")


def plain_story(st, fs, lang="en"):
    """The why, in words a beginner understands. No jargon, three short lines at most."""
    bull = st["dir"] == "bull"
    lvl = _swept_level(st)
    h1 = next((g for a, g, _ in fs if a == "1H trend agrees"), None)
    if lang == "km":
        a = (f"តម្លៃបានធ្លាក់ក្រោម {fmt(lvl)} (កន្លែងដែលអ្នកលក់ដាក់ stop) រួចឡើងវិញ។ អ្នកទិញកំពុងគ្រប់គ្រង។" if bull else
             f"តម្លៃបានឡើងលើ {fmt(lvl)} (កន្លែងដែលអ្នកទិញដាក់ stop) រួចធ្លាក់វិញ។ អ្នកលក់កំពុងគ្រប់គ្រង។")
        b = "និន្នាការ 1 ម៉ោង ស្របគ្នា។" if h1 else f"⚠️ និន្នាការ 1 ម៉ោង {'ចុះ' if bull else 'ឡើង'} — គំនិតនេះខ្សោយជាង។"
    else:
        a = (f"Price dipped below {fmt(lvl)}, where sellers keep their stops, then bounced back up. Buyers took control." if bull else
             f"Price spiked above {fmt(lvl)}, where buyers keep their stops, then fell back. Sellers took control.")
        b = "The 1-hour trend agrees." if h1 else f"⚠️ The 1-hour trend is {'down' if bull else 'up'}, so this idea is weaker."
    return [a, b]


def strength(n_ok, n):
    return "●" * n_ok + "○" * (n - n_ok)


def setup_message(mode, st, ict, fs, valid_until, summ, ai):
    """Telegram text for the sweep -> shift -> retest idea. mode: watch (default) or signal (only once proven)."""
    bull = st["dir"] == "bull"
    n_ok, n = sum(1 for _, g, _ in fs if g), len(fs)
    lo, hi = st["zone"]
    tested = (f"{summ['filled']} past trades, {summ['avg_R']:+.2f}R each" if summ.get("filled") else "not tested yet")
    out = []
    if LANG in ("en", "both"):
        if mode == "watch":
            head = f"👀 <b>GOLD · WATCH {'BUY' if bull else 'SELL'} ZONE</b>"
            note = f"<i>Not a trade signal. This setup has not made money in testing ({tested}). Use it as a map only.</i>"
            zone_word = "Watch zone"
        else:
            head = f"{'🟢' if bull else '🔴'} <b>GOLD · {'BUY' if bull else 'SELL'} SETUP</b>"
            note = f"<i>Tested: {tested}. Risk a small part of your account. Not financial advice.</i>"
            zone_word = "Entry zone"
        out += [head, "",
                f"Price now   <b>{fmt(ict['price'])}</b>",
                f"{zone_word}  <b>{fmt(lo)} – {fmt(hi)}</b>",
                f"Wrong if {'below' if bull else 'above'}  <b>{fmt(st['stop'])}</b>",
                f"Target      <b>{fmt(st['target'])}</b>",
                f"⏰ Good until {local(valid_until)}", "",
                "<b>Why</b>", *[esc(x) for x in plain_story(st, fs)],
                f"Strength {strength(n_ok, n)} {n_ok}/{n}" + (" · strong" if n_ok >= STRONG else ""), "",
                note]
    if LANG in ("km", "both"):
        if out:
            out += ["", "— ខ្មែរ —"]
        out += [f"{'👀' if mode == 'watch' else '🟢' if bull else '🔴'} <b>មាស · {'តំបន់តាមដាន' if mode == 'watch' else 'ការរៀបចំ'} {'ទិញ' if bull else 'លក់'}</b>",
                f"តម្លៃឥឡូវ <b>{fmt(ict['price'])}</b>",
                f"តំបន់ <b>{fmt(lo)} – {fmt(hi)}</b>",
                f"ខុសបើ{'ធ្លាក់ក្រោម' if bull else 'ឡើងលើ'} <b>{fmt(st['stop'])}</b>",
                f"គោលដៅ <b>{fmt(st['target'])}</b>",
                f"⏰ រហូតដល់ {local(valid_until)}",
                *[esc(x) for x in plain_story(st, fs, "km")],
                f"កម្លាំង {strength(n_ok, n)} {n_ok}/{n}",
                "<i>" + ("មិនមែនសញ្ញាជួញដូរទេ។ ប្រើជាផែនទីប៉ុណ្ណោះ។" if mode == "watch" else "មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។") + "</i>"]
    if ai and LANG != "km":
        out.insert(out.index("<b>Why</b>") + 1, esc(ai)) if "<b>Why</b>" in out else None
    out.append(SITE or TV)
    return out


PLAN_MODELS = ("vp_shape", "vp_late")   # range_extreme removed 11 Nov: counter-trend, not proven (t 1.95), 0/2 live          # promising but not yet proven: sent as "plan trade", small risk, results posted
WATCH_ALERTS = os.environ.get("WATCH_ALERTS", "off") == "on"   # old ICT watch ideas lost money in testing: off


def plan_alert(lm, state, now):
    """Plan trade from a candidate model (all nearby settings positive in testing, not yet past the proof bar)."""
    if MODE == "watch":
        return False
    sigs = [s for s in lm.get("signals", []) if s.get("model") in PLAN_MODELS]   # stays a plan trade (0.5%) until live results confirm
    if not sigs or (now - ts(lm.get("last_bar", "1970-01-01T00:00:00+00:00"))) / 60 > STALE_MIN:
        return False
    s = sigs[0]
    key = f"plan|{s['model']}|{s['trigger_time']}"
    if key in state.get("model_keys", []):
        return False
    bull = s["dir"] == "bull"
    pips = lambda px: f"{(px - s['entry']) * (1 if bull else -1) * 1:+,.1f} លេខ"
    exp = s["model"] == "range_extreme"
    if s["model"] == "vp_late":   # ⚠️ warning only: the levels + the honest odds, never an official signal
        lt = (jl("backtest.json").get("models", {}).get("vp_late") or {}).get("all") or {}
        msg = "\n".join([
            f"⚠️ <b>LATE PLAN · {'BUY' if bull else 'SELL'} {fmt(s['entry'])}</b> · not an official signal", "",
            f"Entry  <b>{fmt(s['entry'])}</b>",
            f"SL       <b>{fmt(s['stop'])}</b>  ({pips(s['stop'])})",
            f"TP       <b>{fmt(s['target'])}</b>  ({pips(s['target'])})", "",
            f"The 15m candle confirmed the plan at the POC, but gold already moved a lot today, so the move may be done.",
            (f"Tested 2 years: {lt['trades']} trades · only {lt['win_rate_pct']}% win · {lt['avg_R']:+.2f}R per trade (losing)"
             if lt.get("trades") else "Tested 2 years: only 39% win, losing overall"),
            "", "<i>Skip it, or tiny size: 0.25% max · ហានិភ័យខ្ពស់ ប្រើ lot តូចបំផុត ឬរំលង</i>"])
        mid = send(msg, ("BUY" if bull else "SELL") + " late plan")
        if not mid:
            return False
        state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
        json.dump(state, open("notify_state.json", "w"))
        log_alert({"id": key, "kind": "late", "model": s["model"], "dir": s["dir"], "entry": s["entry"], "stop": s["stop"],
                   "target": s["target"], "rr": s.get("rr"), "created": now, "valid_until": now + 900, "price_at_alert": s["entry"],
                   "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now, "fill": s["entry"],
                   "max_hold_s": 8 * 3600})
        print("late plan sent", key)
        return True
    if exp:
        reason = {"bull": "Day Range extreme: gold stretched 3 steps below the day open in an uptrend and a 15m candle closed back. Target: the day open.",
                  "bear": "Day Range extreme: gold stretched 3 steps above the day open in a downtrend and a 15m candle closed back. Target: the day open."}
    else:
      reason = {"bull": "P-shape volume profile (buyers in control). Price pulled back to the POC (busiest price) and a 15m candle closed above it.",
                "bear": "b-shape volume profile (sellers in control). Price pulled back to the POC (busiest price) and a 15m candle closed below it."}
    msg = "\n".join([
        f"{'🟢' if bull else '🔴'} <b>GOLD {'BUY' if bull else 'SELL'} NOW · {'ទិញ' if bull else 'លក់'}ឥឡូវ</b>  "
        + ("🤬 🔷 <i>EXPERIMENTAL</i>" if exp else "🤬 🟡 <i>plan trade · small size</i>"), "",
        f"Entry  <b>{fmt(s['entry'])}</b>",
        f"SL       <b>{fmt(s['stop'])}</b>  ({pips(s['stop'])})",
        *([f"TP1    <b>{fmt(s['tp1'])}</b>  ({pips(s['tp1'])}) · close half, SL to entry",
           f"TP2    <b>{fmt(s['target'])}</b>  ({pips(s['target'])}) · the day open"] if s.get("tp1") else
          [f"TP       <b>{fmt(s['target'])}</b>  ({pips(s['target'])})"]), "",
        reason["bull" if bull else "bear"],
        ((lambda a: f"Tested 2 years: {a.get('trades')} trades, {a.get('win_rate_pct')}% win, {a.get('avg_R', 0):+.2f}R · "
                    f"not proven yet · closes by noon New York")((jl("backtest.json").get("models", {}).get("range_extreme") or {}).get("all") or {})
         if exp else
         "Tested 2 years: 50% win, +0.18R per trade · Day Range < 70% used · closes within 8 h"),
        "", ("<i>Experimental: risk 0.25% max · ហានិភ័យ 0.25% ប៉ុណ្ណោះ</i>" if exp else "<i>Plan trade: risk 0.5% max · ហានិភ័យ 0.5% ប៉ុណ្ណោះ</i>")])
    mid = send(msg, ("BUY" if bull else "SELL") + " plan")
    if not mid:
        return False
    state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
    json.dump(state, open("notify_state.json", "w"))
    log_alert({"id": key, "kind": "plan", "model": s["model"], "dir": s["dir"], "entry": s["entry"], "stop": s["stop"],
               "target": s["target"], "rr": s.get("rr"), "created": now, "valid_until": now + 900, "price_at_alert": s["entry"],
               "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now, "fill": s["entry"],
               "max_hold_s": (12 if exp else 8) * 3600, **({"tp1": s["tp1"], "part": s.get("part", 0.5)} if s.get("tp1") else {})})
    print("plan sent", key)
    try:   # the trade on a chart with support / resistance, as a reply
        import session
        from engine import load
        from levels import to_ny
        from tg import send_photo
        d = to_ny(load("5m", "20d")).iloc[:-1]
        session.trade_chart(d, jl("levels.json"), s, "plan_chart.png")
        send_photo("plan_chart.png", "Where to enter, where your risk is (SL) and the support / resistance around it.",
                   "Plan chart", reply_to=mid if isinstance(mid, int) else None)
    except Exception as e:
        print("plan chart failed:", e)
    return True


def main():
    ict, conf, lv, q, news, macro, bt, state = (jl(n) for n in ("ict.json", "confluence.json", "levels.json", "quality.json",
                                                                  "news.json", "macro.json", "backtest.json", "notify_state.json"))
    now = time.time()
    if q.get("grade") == "Avoid":
        print("quality is Avoid, no alert"); return
    ns = news_soon(news, now=now)
    if ns:
        print("high-impact news soon, holding alerts:", ns); return
    lm = jl("live_models.json")
    if model_alert(lm, state, now) or plan_alert(lm, state, now):
        return
    if not WATCH_ALERTS:
        print("watch alerts off"); return
    st = ict.get("setup") or {}
    ok, why = gate_setup(st, ict, now)
    if not ok:
        print("no alert:", why); return
    fs = factors(st, ict, conf, lv, macro, now)
    n_ok = sum(1 for _, good, _ in fs if good)
    if n_ok < MIN_FACTORS:
        print(f"no alert: only {n_ok} of {len(fs)} factors"); return
    key = f"setup|{st['dir']}|{st.get('sweep_time')}"
    rank = st["stage"]
    upgrade = state.get("key") == key and rank > state.get("rank", 0)
    if state.get("key") == key and not upgrade:
        print("already alerted"); return
    if not upgrade and now - state.get("t", 0) < COOLDOWN and n_ok <= state.get("factors", 0):
        print("cooldown, not clearly better than the last alert"); return

    mode = MODE if MODE in ("watch", "signal") else bt.get("alert_mode", "watch")
    bull = st["dir"] == "bull"
    sg = 1 if bull else -1
    valid_until = ts(st["shift_time"]) + EXPIRE_MIN * 60 if st.get("shift_time") else now + EXPIRE_MIN * 60
    if upgrade:   # same idea, price is now in the retest zone: short reply to the first alert
        msg = (f"⏱ <b>Retest in play</b> · price {fmt(ict['price'])} is in the zone {fmt(st['zone'][0])}–{fmt(st['zone'][1])}. "
               f"Same plan: entry {fmt(st['entry'])}, stop {fmt(st['stop'])}, target {fmt(st['target'])}.")
        if send(msg, "Retest in play", reply_to=state.get("msg_id") if isinstance(state.get("msg_id"), int) else None):
            state.update({"rank": rank, "t": now}); json.dump(state, open("notify_state.json", "w"))
        return

    facts = {"direction": "buy" if bull else "sell", "stage": st.get("label"), "swept": f"{st.get('sweep_name')} (extreme {st.get('sweep_extreme')})",
             "entry": st["entry"], "stop": st["stop"], "target": st["target"], "rr": st["rr"], "zone": st["zone"],
             "price_now": ict.get("price"), "reasons": st.get("reasons"),
             "factors": [{"name": a, "ok": b, "detail": c} for a, b, c in fs], "backtest": backtest_line(bt, ict.get("rules", "current"))}
    ai = explain(facts)
    summ = (((bt.get("rules") or {}).get(ict.get("rules", "current")) or {}).get("summary") or {})
    lines = setup_message(mode, st, ict, fs, valid_until, summ, ai)
    mid = send("\n".join(l for l in lines if l), ("Watch" if mode == "watch" else "BUY" if bull else "SELL") + " idea")
    if mid:
        json.dump({"key": key, "rank": rank, "factors": n_ok, "t": now, "msg_id": mid, "model_keys": state.get("model_keys", [])},
                  open("notify_state.json", "w"))
        log_alert({"id": key, "kind": "watch" if mode == "watch" else "setup", "dir": st["dir"], "entry": st["entry"], "stop": st["stop"], "target": st["target"],
                   "rr": st["rr"], "zone": st["zone"], "factors": n_ok, "created": now, "valid_until": valid_until,
                   "price_at_alert": ict["price"], "msg_id": mid if isinstance(mid, int) else None, "status": "pending"})
        print("sent", key)


if __name__ == "__main__":
    main()
