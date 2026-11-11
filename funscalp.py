"""🎰 FUN SCALP (owner, 11 Nov 2026): fast scalps for members who want to gamble on CENT accounts, in their own topic
(🎰 Fun Scalp), never in 📈 Signals.

Rule (same 5m entry as the tested scalp, but WITHOUT waiting for a 4H breakout):
  - direction = the 4H structure (last 4H break up or down)
  - the newest CLOSED 5m candle dipped into a fresh 15m fair value gap and closed back beyond the previous candle and
    the 5m EMA20 (research.scalp_trigger) · SL under the last 6 candles $3-12 · TP 2R · out after 3 h
  - up to FUN_PER_DAY a day (default 2), one open at a time, any hour, not 15 min around big news
HONEST: 2 years (studies/scalp_more.py): ~40 a month, 40% win, +0.03R per trade = about BREAK-EVEN (3 a day: 0R,
4 a day: slightly losing). It is a gamble: cent account, tiny lot. Every result is replied and counted.
FUN_SCALP=off stops it.  Run every cycle right after scalp.py:  python funscalp.py
"""
import json
import os
import time

import pandas as pd

import research
from engine import atr, load
from levels import to_ny
from tg import fmt, local, log_alert, send, send_photo

STATE = "funscalp_state.json"
PER_DAY = int(os.environ.get("FUN_PER_DAY", 2))
MAX_LATE_S = 180


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def main():
    if os.environ.get("FUN_SCALP", "on") == "off":
        print("fun scalp: off"); return
    now = time.time()
    log = jl("alerts_log.json", [])
    if any(a.get("kind") == "fun" and a["status"] in ("pending", "filled") for a in log):
        print("fun scalp: one is still open"); return
    try:
        from notify import news_soon
        if news_soon(jl("news.json", {}), mins=15, now=now):
            print("fun scalp: big news soon"); return
    except Exception as e:
        print("fun scalp: news check failed:", e)
    df = load("5m", "20d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = df[df.index + pd.Timedelta(minutes=5) <= pd.Timestamp(time.time(), unit="s", tz="UTC")]   # closed candles only
    df = to_ny(df)
    i = len(df) - 1
    if now - (df.index[i].tz_convert("UTC").timestamp() + 300) > MAX_LATE_S:
        print("fun scalp: newest candle too old for a fast entry"); return
    day = str((df.index[i] - pd.Timedelta(hours=18)).date())
    st = jl(STATE, {})
    n_today = st.get("count", 0) if st.get("day") == day else 0
    if n_today >= PER_DAY:
        print("fun scalp: daily limit reached"); return
    b4 = research._bias(df, "4H", pd.Timedelta(hours=4))[i]
    sg = 1 if b4 == "bull" else -1 if b4 == "bear" else 0
    if not sg:
        print("fun scalp: no 4H direction"); return
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    e20 = pd.Series(c).ewm(span=20).mean().to_numpy()
    fd, flo, fhi = research.fvg_15m_state(df)
    sw = research.scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
    if sw is None:
        print("fun scalp: no trigger"); return
    entry = float(c[i])
    risk = (entry - sw) * sg
    if not research.SCALP_RISK[0] <= risk <= research.SCALP_RISK[1]:
        print(f"fun scalp: stop ${risk:.1f} outside ${research.SCALP_RISK[0]:.0f}-{research.SCALP_RISK[1]:.0f}"); return
    tgt = entry + sg * research.SCALP_RR * risk
    bull = sg > 0
    side = "BUY" if bull else "SELL"
    caption = "\n".join([
        f"🎰 <b>FUN SCALP — {side}</b>",
        f"📍 Entry: <b>{fmt(entry)}</b>",
        f"🛑 SL: <b>{fmt(sw)}</b>",
        f"🎯 TP: <b>{fmt(tgt)}</b> (2R)",
        f"⏱ M5 · with the 4H · closes within 3 h · −${risk:,.0f} at SL (0.01 lot)",
        "<i>🎲 Gamble for fun: cent account, tiny lot · ~break-even in 2-year test · ភ្នាល់លេង គណនី cent ប៉ុណ្ណោះ</i>",
    ])
    title = f"{side} fun scalp"
    mid = None
    try:
        import signal_card
        signal_card.make(df, {"dir": "bull" if bull else "bear", "entry": entry, "stop": float(sw), "tp1": None, "target": tgt},
                         "fun_card.png", tier="fun", status="LIVE", stamp=local(now), tf_label="fun scalp · 5m",
                         bars=80, hold_note="closes within 3 h")
        mid = send_photo("fun_card.png", caption, title)
    except Exception as e:
        print("fun card failed:", e)
    if not mid:
        mid = send(caption, title)
    if not mid:
        return
    json.dump({"day": day, "count": n_today + 1, "t": now}, open(STATE, "w"))
    log_alert({"id": f"fun|{df.index[i]}", "kind": "fun", "model": "fun_scalp", "dir": "bull" if bull else "bear",
               "entry": entry, "stop": float(sw), "target": float(tgt), "rr": research.SCALP_RR, "created": now,
               "valid_until": now + 300, "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None,
               "status": "filled", "filled_at": now, "fill": entry, "max_hold_s": research.SCALP_HOLD * 300, "tier": "fun"})
    print("fun scalp sent", side, entry, sw, tgt)


if __name__ == "__main__":
    main()
