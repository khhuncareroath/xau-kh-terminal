"""🤬 COMBO SCALP live detector: small-SL 5m entries after a 🖕 COMBO / 🖕🖕 PREMIUM 4H breakout.

Same rule as research.combo_scalp (tested 2 years: 120 trades, 50% win, +0.28-0.33R, SL ~$7, TP 2R):
  - only for 12 hours after a COMBO/PREMIUM breakout signal, only in its direction
  - the newest CLOSED 5m candle dipped into a fresh 15m fair value gap and closed back beyond the previous candle
    and the 5m EMA20
  - SL under the last 6 candles (- 0.1 ATR), $3-12; TP 2R; out after 3 hours; first one per trading day only
Speed matters (with a 10-15 min delay the edge mostly disappears), so loop.py runs this FIRST in every cycle, 20 s
after each 5-minute close, and it only looks at the candle that just closed.  Run:  python scalp.py
"""
import json
import time

import numpy as np
import pandas as pd

import research
from engine import atr, load
from levels import to_ny
from tg import fmt, local, log_alert, send, send_photo

STATE = "scalp_state.json"
WINDOW_S = 12 * 3600
MAX_LATE_S = 180          # the candle must have closed less than 3 minutes ago


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def active_breakout(now):
    """The COMBO/PREMIUM breakout signal whose 12-hour scalp window is open, or None."""
    for a in reversed(jl("alerts_log.json", [])):
        if a.get("kind") != "model":
            continue
        if now - a["created"] > WINDOW_S:
            return None
        if a.get("tier") in ("combo", "premium") and now - a["created"] >= 15 * 60:
            return a
    return None


def main():
    now = time.time()
    br = active_breakout(now)
    if not br:
        print("scalp: no COMBO breakout window open"); return
    log = jl("alerts_log.json", [])
    if any(a.get("kind") == "scalp" and a["status"] in ("pending", "filled") for a in log):
        print("scalp: a scalp trade is still open"); return
    try:
        from notify import news_soon
        if news_soon(jl("news.json", {}), now=now):
            print("scalp: high-impact news soon, holding"); return
    except Exception as e:
        print("scalp: news check failed:", e)
    want = pd.Timestamp((int(now) // 300) * 300 - 300, unit="s", tz="UTC")   # start of the candle that just closed
    for attempt in range(3):   # the price feed can need a few seconds to publish the new candle
        df = load("5m", "20d")
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        df = df[df.index + pd.Timedelta(minutes=5) <= pd.Timestamp(time.time(), unit="s", tz="UTC")]   # closed candles only
        if df.index[-1] >= want or attempt == 2:
            break
        import os
        try:
            os.remove("data/cache/twelvedata.json")   # force a fresh download next time
        except OSError:
            pass
        time.sleep(25)
    now = time.time()
    df = to_ny(df)
    i = len(df) - 1
    close_t = df.index[i].tz_convert("UTC").timestamp() + 300
    if now - close_t > MAX_LATE_S:
        print(f"scalp: newest closed candle is {int(now - close_t)} s old, too late for a fast entry"); return
    sg = 1 if br["dir"] == "bull" else -1
    day = str((df.index[i] - pd.Timedelta(hours=18)).date())
    st = jl(STATE, {})
    if st.get("day") == day:
        print("scalp: today's scalp already sent"); return
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    e20 = pd.Series(c).ewm(span=20).mean().to_numpy()
    fd, flo, fhi = research.fvg_15m_state(df)
    sw = research.scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
    if sw is None:
        print("scalp: no trigger on the", df.index[i], "candle"); return
    entry = float(c[i])
    risk = (entry - sw) * sg
    if not research.SCALP_RISK[0] <= risk <= research.SCALP_RISK[1]:
        print(f"scalp: stop ${risk:.1f} outside the tested ${research.SCALP_RISK[0]:.0f}-{research.SCALP_RISK[1]:.0f}"); return
    tgt = entry + sg * research.SCALP_RR * risk
    bull = sg > 0
    bt = (jl("backtest.json", {}).get("models", {}).get("combo_scalp") or {}).get("all") or {}
    side = "BUY" if bull else "SELL"
    caption = "\n".join(x for x in [
        f"🤬 <b>XAU/USD — {side} | COMBO SCALP</b> (small SL)",
        f"🇰🇭 <b>{'ទិញ' if bull else 'លក់'}ឥឡូវ</b> · ចូល {fmt(entry)} · SL {fmt(sw)} · TP {fmt(tgt)} · lot តូច",
        f"📍 Entry: <b>{fmt(entry)}</b> (now)",
        f"🛑 SL: <b>{fmt(sw)}</b> ({risk * 10:,.0f} pips)",
        f"🎯 TP: <b>{fmt(tgt)}</b> (+{risk * research.SCALP_RR * 10:,.0f} pips) = 2R",
        f"💰 0.01 lot: SL −${risk:,.1f} · TP +${risk * research.SCALP_RR:,.1f} · 0.01 lot per ${risk * 200:,.0f} of account (0.5% risk)",
        (f"📊 Tested 2 years: {bt.get('trades')} trades · {bt.get('win_rate_pct')}% win · small-size setup" if bt.get("trades") else
         "📊 Tested 2 years: 120 trades · 50% win · small-size setup"),
        f"⏱ 5m entry in the direction of the 🖕 {fmt(br['entry'])} breakout · closes within 3 h",
        "⚡ Fast setup: enter now or skip · ចូលឥឡូវ ឬរំលង · risk 0.25–0.5%",
    ] if x)
    mid = None
    try:
        import signal_card
        signal_card.make(df, {"dir": "bull" if bull else "bear", "entry": entry, "stop": sw, "tp1": None, "target": tgt},
                         "scalp_card.png", tier="scalp", status="LIVE", win_rate=bt.get("win_rate_pct") or 50,
                         trades=bt.get("trades") or 120, stamp=local(now), tf_label="COMBO scalp · 5m entry",
                         bars=80, hold_note="closes within 3 h")
        mid = send_photo("scalp_card.png", caption, f"{side} scalp")
    except Exception as e:
        print("scalp card failed:", e)
    if not mid:
        mid = send(caption, f"{side} scalp")
    if not mid:
        return
    json.dump({"day": day, "t": now}, open(STATE, "w"))
    log_alert({"id": f"scalp|{df.index[i]}", "kind": "scalp", "model": "combo_scalp", "dir": "bull" if bull else "bear",
               "entry": entry, "stop": float(sw), "target": float(tgt), "rr": research.SCALP_RR, "created": now,
               "valid_until": now + 300, "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None,
               "status": "filled", "filled_at": now, "fill": entry, "max_hold_s": research.SCALP_HOLD * 300,
               "tier": "scalp", "parent": br.get("id")})
    print("scalp sent", side, entry, sw, tgt)


if __name__ == "__main__":
    main()
