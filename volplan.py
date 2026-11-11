"""📊 Volume confirmation in 📈 Signals (owner, 12 Nov 2026: "combo volume, entry in low timeframe, no separate signal").

When research.vp_turn fires (last session's volume profile shows a NEW side in control while the 4H has not turned yet,
price pulls back to that profile's POC and a 15m candle closes back = the low-timeframe entry), it is posted in 📈 Signals
in the SAME format as the M15 A+ signal, marked 📊 Volume, with the reason in 🧠 Setup Analysis.
Tested 2 years (closed by 24:00 Cambodia): 122 trades, 48% win, +0.26R, proven. Tracked as its own model ("vp_turn")
so the Friday live-vs-test check can judge it honestly. Runs after live_models.py.
"""
import json
import os
import time

import pandas as pd

import research

ON = os.environ.get("VOLUME_SIGNALS", "on") != "off"
STATE = "volplan_state.json"


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def main():
    if not ON:
        return
    lm = jl("live_models.json", {})
    sigs = [s for s in lm.get("signals", []) if s.get("model") == "vp_turn"]
    if not sigs:
        print("volume plan: nothing"); return
    s = sigs[-1]
    st = jl(STATE, {})
    key = f"vp_turn|{s['trigger_time']}"
    if key in st.get("sent", []):
        return
    now = time.time()
    t = pd.Timestamp(s["trigger_time"])
    if now - t.timestamp() > 12 * 60:
        print("volume plan: too late", t); return
    kh = pd.Timestamp(now, unit="s", tz="Asia/Phnom_Penh")
    skip = None
    if kh.hour < 6:
        skip = "no signals 00:00-06:00 Cambodia"
    log = jl("alerts_log.json", [])
    if any(a.get("kind") == "m15" and a.get("status") in ("pending", "filled") for a in log):
        skip = "an M15 signal is still open"
    day = kh.strftime("%Y-%m-%d")
    if any(a.get("model") == "vp_turn" and pd.Timestamp(a["created"], unit="s", tz="Asia/Phnom_Penh").strftime("%Y-%m-%d") == day
           for a in log):
        skip = "already one today"
    try:
        import setupidea
        if setupidea._news_near(now):
            skip = "big news within 15 min"
    except Exception:
        pass
    st.setdefault("sent", []).append(key)
    st["sent"] = st["sent"][-50:]
    json.dump(st, open(STATE, "w"))
    if skip:
        print("volume plan skipped:", skip); return
    send_signal(s, now, kh)


def send_signal(s, now, kh):
    from tg import fmt, local, log_alert, msg_link, send, send_photo
    bull = s["dir"] == "bull"
    sg = 1 if bull else -1
    side = "BUY" if bull else "SELL"
    entry, stop, tp = float(s["entry"]), float(s["stop"]), float(s["target"])
    risk = abs(entry - stop)
    hold_s = int(min(8 * 3600, ((kh.normalize() + pd.Timedelta(days=1)) - kh).total_seconds()))
    cap = "\n".join([
        f"{'🟢' if bull else '🔴'} <b>XAU/USD — {side} | 💎 A+ · 📊 Volume</b>",
        f"📍 Entry: <b>{fmt(entry)}</b>",
        f"🛑 SL: <b>{fmt(stop)}</b>",
        f"🎯 TP: <b>{fmt(tp)}</b> (2R)",
        f"🧩 Confirmations: volume profile + 15m close back at the POC",
        f"⏱ Timeframe: M15 · closes by 24:00 · −${risk:,.0f} at SL (0.01 lot)",
    ])
    title = f"{side} idea"
    mid = None
    try:
        import signal_card
        from engine import load, closed
        from levels import to_ny
        d5 = closed(to_ny(load("5m", "20d")))
        signal_card.make(d5, {"dir": s["dir"], "entry": entry, "stop": stop, "tp1": None, "target": tp},
                         "volume_card.png", tier="setup_a", status="LIVE", stamp=local(now), tf_label="15m · volume",
                         hold_note="closes by 24:00")
        mid = send_photo("volume_card.png", cap, title)
    except Exception as e:
        print("volume card failed, text:", e)
    if not mid:
        mid = send(cap, title)
    if not mid:
        return
    log_alert({"id": f"vp_turn|{s['trigger_time']}", "kind": "m15", "model": "vp_turn", "dir": s["dir"], "entry": entry,
               "stop": stop, "target": tp, "rr": round(abs(tp - entry) / risk, 2), "created": now, "valid_until": now + 900,
               "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now,
               "fill": entry, "max_hold_s": hold_s, "tier": "A+"})
    print("volume signal sent", side, entry, stop, tp)
    try:   # 🔎 why, in Setup Analysis
        prof = profile_text(bull)
        link = msg_link(mid if isinstance(mid, int) else None, title)
        lines = [f"🔎 <b>WHY THIS {side} · {fmt(entry)}</b> (📊 volume)", "",
                 f"1️⃣ Last session's volume profile: {prof} · {'អ្នកទិញ' if bull else 'អ្នកលក់'}ឈ្នះ session មុន",
                 f"2️⃣ The 4H has not turned yet, so this is a NEW move starting (tested: these work best) · ចលនាថ្មី",
                 f"3️⃣ Price pulled back to the POC (most traded price) and a 15m candle closed back {'above' if bull else 'below'} it "
                 f"· ទៀន 15m បិទត្រឡប់",
                 f"🛑 Wrong if price goes {'below' if bull else 'above'} {fmt(stop)} (beyond the value area) · 🎯 TP {fmt(tp)} (2R)",
                 "📊 Tested 2 years: 122 trades, 48% win, +0.26R a trade",
                 *([f"<a href=\"{link}\">📈 Signal</a>"] if link else [])]
        send("\n".join(lines), "Setup reason", silent=True)
    except Exception as e:
        print("volume reason failed:", e)


def profile_text(bull):
    return ("P shape: most volume traded near the TOP, buyers won" if bull else
            "b shape: most volume traded near the BOTTOM, sellers won")


if __name__ == "__main__":
    main()
