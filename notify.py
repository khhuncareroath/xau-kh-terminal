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
    sigs = [s for s in lm.get("signals", []) if s.get("proven")]
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
    bull = s["dir"] == "bull"
    b = s.get("backtest") or {}
    side = ((jl("backtest.json").get("models", {}).get(s["model"], {}).get("by_direction") or {}).get("long" if bull else "short") or {})
    hold_h = research.MAX_HOLD_H.get(s["model"], 24)
    out = []
    if LANG in ("en", "both"):
        out += [f"{'🟢' if bull else '🔴'} <b>GOLD · {'BUY' if bull else 'SELL'} NOW</b>", "",
                f"Entry       <b>{fmt(s['entry'])}</b> (market price)",
                f"Stop loss   <b>{fmt(s['stop'])}</b>",
                *([f"TP1         <b>{fmt(s['tp1'])}</b>  → close half, move stop to {fmt(s['entry'])}",
                   f"TP2         <b>{fmt(s['target'])}</b>  (rest of the trade)"] if s.get("tp1") else
                  [f"Target      <b>{fmt(s['target'])}</b>  (1:{s['rr']})"]),
                f"⏰ Enter within 15 min · trade lasts up to {hold_h // 24} days" if hold_h >= 48 else f"⏰ Enter within 15 min · trade lasts up to {hold_h} hours", "",
                "<b>Why</b>", esc(PLAIN.get(s["model"], {}).get("bull" if bull else "bear", s["description"] + ".")),
                esc(f"Tested on 2 years of spot gold: {b.get('trades')} trades, {b.get('win_rate_pct')}% were profitable, "
                    f"{b.get('avg_R'):+.2f}R per trade after costs.") if b.get("trades") else "",
                (f"⚠️ {'Buy' if bull else 'Sell'} signals from this model averaged {side['avg_R']:+.2f}R ({side['trades']} trades): "
                 + ("the weaker side, consider a smaller size." if side["avg_R"] < 0.1 else "the stronger side.")) if side.get("trades") and s["model"] != "trend_buy" else None,
                "", "<i>Risk a small, fixed part of your account (0.5–1%). Losses will happen. Not financial advice. "
                "The result will be posted as a reply.</i>"]
    if LANG in ("km", "both"):
        if out:
            out += ["", "— ខ្មែរ —"]
        out += [f"{'🟢' if bull else '🔴'} <b>មាស · {'ទិញ' if bull else 'លក់'} ឥឡូវ</b>",
                f"ចូល <b>{fmt(s['entry'])}</b> (តម្លៃទីផ្សារ)", f"Stop loss <b>{fmt(s['stop'])}</b>",
                *([f"TP1 <b>{fmt(s['tp1'])}</b> → បិទពាក់កណ្ដាល ហើយប្ដូរ stop មកចំណុចចូល", f"TP2 <b>{fmt(s['target'])}</b>"] if s.get("tp1")
                  else [f"គោលដៅ <b>{fmt(s['target'])}</b>"]),
                "<i>ប្រើហានិភ័យតិច (0.5–1% នៃគណនី)។ មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។</i>"]
    out.append(TV)
    mid = send("\n".join(l for l in out if l is not None), ("BUY" if bull else "SELL") + " now")
    if not mid:
        return False
    state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
    json.dump(state, open("notify_state.json", "w"))
    log_alert({"id": key, "kind": "model", "model": s["model"], "dir": s["dir"], "entry": s["entry"], "stop": s["stop"],
               "target": s["target"], "rr": s["rr"], "created": now, "valid_until": now + 900, "price_at_alert": s["entry"],
               "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now, "fill": s["entry"],
               "max_hold_s": hold_h * 3600, **({"tp1": s["tp1"], "part": s.get("part", 0.5)} if s.get("tp1") else {})})
    print("sent", key)
    return True


LANG = os.environ.get("BOT_LANG", "en")   # en, km, or both
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


def main():
    ict, conf, lv, q, news, macro, bt, state = (jl(n) for n in ("ict.json", "confluence.json", "levels.json", "quality.json",
                                                                  "news.json", "macro.json", "backtest.json", "notify_state.json"))
    now = time.time()
    if q.get("grade") == "Avoid":
        print("quality is Avoid, no alert"); return
    ns = news_soon(news, now=now)
    if ns:
        print("high-impact news soon, holding alerts:", ns); return
    if model_alert(jl("live_models.json"), state, now):
        return
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
    mid = send("\n".join(l for l in lines if l), ("BUY" if bull else "SELL") + " now")
    if not mid:
        return False
    state["model_keys"] = (state.get("model_keys", []) + [key])[-50:]
    json.dump(state, open("notify_state.json", "w"))
    log_alert({"id": key, "kind": "model", "model": s["model"], "dir": s["dir"], "entry": s["entry"], "stop": s["stop"],
               "target": s["target"], "rr": s["rr"], "created": now, "valid_until": now + 900, "price_at_alert": s["entry"],
               "msg_id": mid if isinstance(mid, int) else None, "status": "pending"})
    print("sent", key)
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
    if model_alert(jl("live_models.json"), state, now):
        return
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
    if mode == "watch":
        lines = [
            f"👀 <b>XAU.KH · Watch · {'Bullish' if bull else 'Bearish'} structure</b> · gold futures",
            esc(f"{st.get('sweep_name')} swept, then structure shifted {'up' if bull else 'down'}."),
            f"Zone to watch <code>{fmt(st['zone'][0])} – {fmt(st['zone'][1])}</code> · idea invalid {'below' if bull else 'above'} {fmt(st['stop'])}",
            f"Next liquidity {fmt(st['target'])} · price now {fmt(ict['price'])} · until {local(valid_until)}",
            f"<b>Factors {n_ok}/{len(fs)}</b>: " + " ".join(f"{'✅' if g else '▫️'}{esc(a)}" for a, g, _ in fs),
            spot_line(st["entry"]),
            "<b>Why:</b> " + esc(ai if ai else " ".join(st.get("reasons", []))),
            "<i>Map, not a trade signal: in testing this setup has not shown an edge yet"
            + (f" ({summ['filled']} trades, {summ['avg_R']:+.2f}R each)" if summ.get("filled") else "") + ". Use your own plan and risk.</i>",
            TV, SITE,
        ]
    else:
        lines = None
    lines = lines or [
        f"{'🟢' if bull else '🔴'} <b>XAU.KH · {'BUY' if bull else 'SELL'} idea</b> · gold futures",
        esc(st.get("label", "")),
        f"Entry <code>{fmt(st['entry'])}</code> · zone {fmt(st['zone'][0])}–{fmt(st['zone'][1])}",
        f"Stop <code>{fmt(st['stop'])}</code> · Target <code>{fmt(st['target'])}</code> · R:R 1:{st['rr']}",
        f"Valid until {local(valid_until)} · price now {fmt(ict['price'])}",
        f"<b>Factors {n_ok}/{len(fs)}</b>: " + " ".join(f"{'✅' if g else '▫️'}{esc(a)}" for a, g, _ in fs),
        spot_line(st["entry"]),
        "<b>Why:</b> " + esc(ai if ai else " ".join(st.get("reasons", []))),
        esc(backtest_line(bt, ict.get("rules", "current")) or ""),
        "<i>Idea to confirm with your own entry model, not financial advice. The result will be posted as a reply.</i>",
        TV, SITE,
    ]
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
