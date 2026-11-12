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
PER_DAY = int(os.environ.get("FUN_PER_DAY", 4))   # owner, 12 Nov 2026: "go crazy fire" -> two tiers, 4 a day in total
CRAZY = os.environ.get("FUN_CRAZY", "off") == "on"   # 🎲 choppy-trend scalps too, labelled CRAZY OFF by default: choppy-only tier lost −0.11R, t −3.3 (studies/inside_zone.py). FUN_CRAZY=on brings it back
CLEAN = os.environ.get("FUN_CLEAN", "on") != "off"   # studies/fun_filters.py: clean 4H trend only -> +0.17R (proven) vs 0R
MAX_LATE_S = 180


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def why_post(df, i, sg, entry, sl, tps, fd, flo, fhi, a, e20, mid, quality=True):
    from tg import msg_link
    bull = sg > 0
    side = "BUY" if bull else "SELL"
    lo, hi = float(flo[i]), float(fhi[i])
    du = None
    try:
        du = research.day_used(df, df.index[i] + pd.Timedelta(minutes=5))
    except Exception:
        pass
    link = msg_link(mid if isinstance(mid, int) else None, f"{side} fun scalp")
    lines = [f"🔎 <b>WHY THIS FUN SCALP · {side} {fmt(entry)}</b> · {'🔥 QUALITY' if quality else '🎲 CRAZY'}", "",
             f"1️⃣ 4H trend is {'UP ↑' if bull else 'DOWN ↓'} → only {side}s · និន្នាការ 4H {'ឡើង' if bull else 'ចុះ'}",
             (f"2️⃣ Price dipped into a 15m gap (FVG) {fmt(min(lo, hi))}–{fmt(max(lo, hi))} · តម្លៃ{'ធ្លាក់' if bull else 'ឡើង'}ចូល FVG 15m"
              if lo == lo and hi == hi else "2️⃣ Price dipped into a fresh 15m gap (FVG)"),
             f"3️⃣ The 5m candle closed back {'above' if bull else 'below'} the previous candle and EMA20 {fmt(float(e20[i]))} "
             f"→ {'buyers' if bull else 'sellers'} are back · ទៀន 5m បិទត្រឡប់",
             ("4️⃣ The 4H trend is clean (not choppy) · ទីផ្សារមិនរញ៉េរញ៉ៃ" if quality else
              "4️⃣ 🎲 CRAZY: the 4H trend is choppy, so this is a pure gamble that LOST in testing (−0.11R a trade) · ភ្នាល់សុទ្ធ"),
             "5️⃣ Other side checked: no demand / supply (15m-Daily) right in front · គ្មាន Demand/Supply រាំងនៅជិត",
             f"🛑 SL {fmt(sl)} = {'under' if bull else 'above'} the last 6 candles · 🎯 TP1/2/3 = 1R / 1.5R / 2R",
             *([f"📏 Day Meter {du * 100:.0f}%"] if du is not None else []),
             "<i>🎰 Gamble for fun · cent account</i>"]
    if link:
        lines.append(f"<a href=\"{link}\">🎰 The scalp</a>")
    send("\n".join(lines), "Setup reason", silent=True)


def main():
    if os.environ.get("FUN_SCALP", "on") == "off":
        print("fun scalp: off"); return
    now = time.time()
    log = jl("alerts_log.json", [])
    if any(a.get("kind") == "fun" and a["status"] in ("pending", "filled") for a in log):
        print("fun scalp: one is still open"); return
    if any(a.get("kind") == "scalp" and a["status"] in ("pending", "filled") for a in log):
        print("fun scalp: the ⚡ Scalp already has this trade"); return   # never the same trade in two topics
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
    quality = True   # 🔥 QUALITY = clean 4H trend + other side clear (tested +0.19R); 🎲 CRAZY = choppy trend (about −0.03R)
    if CLEAN:
        er = research.efficiency(df, df.index[i] + pd.Timedelta(minutes=5))
        if er is not None and er <= research.CHOP_ER:
            if not CRAZY:
                print(f"fun scalp: choppy 4H (efficiency {er:.2f}), skipped"); return
            quality = False
    entry = float(c[i])
    risk = (entry - sw) * sg
    if not research.SCALP_RISK[0] <= risk <= research.SCALP_RISK[1]:
        print(f"fun scalp: stop ${risk:.1f} outside ${research.SCALP_RISK[0]:.0f}-{research.SCALP_RISK[1]:.0f}"); return
    opp = None
    if os.environ.get("FUN_OPPOSITE", "on") == "on":   # 👀 other side, 15m-Daily (studies/fun_opposite.py): +0.19R vs +0.17R
        try:
            import arrays
            opp = arrays.opposite(df, entry, sg, risk, now=df.index[i] + pd.Timedelta(minutes=5))
        except Exception as e:
            print("fun scalp: other-side check failed:", e)
        if opp and opp["dist_r"] <= 0.5:
            print(f"fun scalp: {opp['tf']} {'supply' if sg > 0 else 'demand'} {opp['lo']}-{opp['hi']} right in front, skipped"); return
    tp1, tp2, tp3 = (round(entry + sg * k * risk, 2) for k in (1, 1.5, 2))   # owner: TP1→TP2 range split in three
    bull = sg > 0
    side = "BUY" if bull else "SELL"
    caption = "\n".join([
        f"🎰 <b>FUN SCALP — {side}</b> · " + ("🔥 QUALITY" if quality else "🎲 CRAZY"),
        f"📍 Entry: <b>{fmt(entry)}</b>",
        f"🛑 SL: <b>{fmt(sw)}</b>",
        f"🎯 TP1: <b>{fmt(tp1)}</b>",
        f"🎯 TP2: <b>{fmt(tp2)}</b>",
        f"🎯 TP3: <b>{fmt(tp3)}</b>",
    ])
    title = f"{side} fun scalp"
    mid = None
    try:
        import signal_card
        signal_card.make(df, {"dir": "bull" if bull else "bear", "entry": entry, "stop": float(sw), "tp1": tp1, "tp_mid": tp2, "target": tp3},
                         "fun_card.png", tier="fun" if quality else "fun_crazy", status="LIVE", stamp=local(now), tf_label="fun scalp · 5m",
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
               "entry": entry, "stop": float(sw), "target": tp3, "tp1": tp1, "tp_mid": tp2, "part": 1 / 3, "rr": 2.0, "created": now,
               "valid_until": now + 300, "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None,
               "status": "filled", "filled_at": now, "fill": entry, "max_hold_s": research.SCALP_HOLD * 300, "tier": "quality" if quality else "crazy"})
    print("fun scalp sent", side, entry, sw, tp1, tp2, tp3)
    try:   # 🔎 why the bot sent it, in Setup Analysis (the signal itself stays numbers only)
        why_post(df, i, sg, entry, float(sw), (tp1, tp2, tp3), fd, flo, fhi, a, e20, mid, quality)
    except Exception as e:
        print("fun scalp why failed:", e)


if __name__ == "__main__":
    main()
