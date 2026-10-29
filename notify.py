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
TV = "https://www.tradingview.com/chart/?symbol=COMEX%3AGC1%21"
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


def main():
    ict, conf, lv, q, news, macro, bt, state = (jl(n) for n in ("ict.json", "confluence.json", "levels.json", "quality.json",
                                                                  "news.json", "macro.json", "backtest.json", "notify_state.json"))
    now = time.time()
    if q.get("grade") == "Avoid":
        print("quality is Avoid, no alert"); return
    ns = news_soon(news, now=now)
    if ns:
        print("high-impact news soon, holding alerts:", ns); return
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
    lines = [
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
    mid = send("\n".join(l for l in lines if l), f"{'BUY' if bull else 'SELL'} idea")
    if mid:
        json.dump({"key": key, "rank": rank, "factors": n_ok, "t": now, "msg_id": mid}, open("notify_state.json", "w"))
        log_alert({"id": key, "kind": "setup", "dir": st["dir"], "entry": st["entry"], "stop": st["stop"], "target": st["target"],
                   "rr": st["rr"], "zone": st["zone"], "factors": n_ok, "created": now, "valid_until": valid_until,
                   "price_at_alert": ict["price"], "msg_id": mid if isinstance(mid, int) else None, "status": "pending"})
        print("sent", key)


if __name__ == "__main__":
    main()
