"""🎯 S+ SETUP: the owner's ICT / SMC model (HTF zone -> 15m liquidity sweep + MSS -> limit on the OB / CISD retest).

Rules (identical in the backtest and live, closed candles only):
  1. Key levels: Daily + 4H fair value gaps and order blocks (OB = last opposite candle before a structure break with
     displacement), active from the close of the candle that made them until a close beyond the far edge (or 30 / 15 days).
  2. Price comes into a zone from outside (a 15m candle trades into it after closing outside).
  3. Within 6 hours on 15m: a liquidity sweep (a low below the last confirmed 15m swing low; mirror for sells), then an
     MSS: a 15m close beyond the last confirmed 15m swing high with a candle body >= 0.6 ATR (displacement).
  4. HTF bias: the Daily OR 4H structure (last break) points the same way.
  5. Order: LIMIT at the last opposite 15m candle before the MSS (OB / CISD level), valid 2 hours.
     SL beyond the sweep extreme + 0.1 ATR(15m), $2-20. TP = 3R. Out after 12 hours.
Tested 11 Nov 2026 (2 years spot gold, $0.40 cost, setups in time order): 96 trades (~4 a month), 42% win, +0.29R per
trade, newest 30% +0.34R, t 1.67 (NOT yet proven: needs 2), positive in 6 of 7 quarters, longs +0.13R / shorts +0.51R,
median SL ~$10. Positive in every setting tried (+0.12 to +0.38R). Owner's choice: live at SMALL SIZE until proven. Without the HTF bias, market entries, FVG entries,
London/NY-only or a volume-profile filter: no edge (studies/RESULTS.md).

python splus.py  -> live: posts a new S+ limit order in 📈 Signals (card + caption) and logs it for track.py.
"""
import json
import time

import numpy as np
import pandas as pd

import ict
from engine import atr

DISP, WIN15, MAX_RISK, MIN_RISK, LIMIT_BARS, HOLD_BARS, RR = 0.6, 24, 20.0, 2.0, 24, 144, 3.0
COST = 0.4
STATE = "splus_state.json"
TRIES = {"trades": 96, "win_rate_pct": 42, "avg_R": 0.29}


def _zones(df, tf, life_days):
    d = ict.resample(df, tf)
    a = atr(d).to_numpy()
    span = pd.Timedelta(hours=4) if tf == "4H" else pd.Timedelta(hours=24)
    o, h, l, c = (d[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    raw = []
    for i in range(2, len(d)):
        if not np.isfinite(a[i]):
            continue
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= 0.2 * a[i]:
            raw.append(("bull", h[i - 2], l[i], i))
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= 0.2 * a[i]:
            raw.append(("bear", h[i], l[i - 2], i))
    sw = ict.swings(d, 3)
    events = ict.structure(d, a, sw)
    for e in events:
        ob = ict.order_block(d, e)
        if ob and e["displacement"]:
            raw.append((ob["dir"], ob["lo"], ob["hi"], e["i"]))
    out = []
    for dr, lo, hi, i in raw:
        after = c[i + 1:]
        bad = np.where(after < lo)[0] if dr == "bull" else np.where(after > hi)[0]
        t0 = d.index[i] + span
        t1 = d.index[i + 1 + bad[0]] + span if len(bad) else t0 + pd.Timedelta(days=life_days)
        out.append(dict(dir=dr, lo=float(lo), hi=float(hi), t0=t0, t1=min(t1, t0 + pd.Timedelta(days=life_days)), tf=tf))
    ev = {e["i"]: e["dir"] for e in events}
    cur, vals = None, []
    for i in range(len(d)):
        cur = ev.get(i, cur)
        vals.append(cur)
    return out, pd.Series(vals, index=d.index + span, dtype=object)


def _bias_at(b, t):
    k = b.index.searchsorted(t, side="right") - 1
    return b.iloc[k] if k >= 0 else None


def setups(df):
    """All S+ setups in df (5m candles, closed only). Each: t (time the MSS 15m candle closed), sg, entry (limit),
    stop, target, risk, tf (zone timeframe), zone, bias_ok."""
    zD, bD = _zones(df, "D", 30)
    z4, b4 = _zones(df, "4H", 15)
    d15 = ict.resample(df, "15m")
    o, h, l, c = (d15[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a15 = atr(d15).to_numpy()
    n, t15 = len(d15), d15.index
    end15 = t15 + pd.Timedelta(minutes=15)
    sh, sl = np.full(n, np.nan), np.full(n, np.nan)
    lh = ll = np.nan
    for j in range(n):
        k = j - 2
        if k >= 2:
            if h[k] == h[k - 2:k + 3].max():
                lh = h[k]
            if l[k] == l[k - 2:k + 3].min():
                ll = l[k]
        sh[j], sl[j] = lh, ll
    out = []
    for z in sorted(zD + z4, key=lambda z: z["t0"]):
        sg = 1 if z["dir"] == "bull" else -1
        j0, j1 = int(t15.searchsorted(z["t0"])), int(t15.searchsorted(z["t1"]))
        tap = None
        for j in range(max(j0, 1), min(j1, n)):
            inside = l[j] <= z["hi"] and h[j] >= z["lo"]
            if inside and ((c[j - 1] > z["hi"]) if sg > 0 else (c[j - 1] < z["lo"])):
                tap = j
                break
        if tap is None:
            continue
        ext, swept = (l[tap] if sg > 0 else h[tap]), False
        for j in range(tap, min(tap + WIN15, n)):
            ext = min(ext, l[j]) if sg > 0 else max(ext, h[j])
            if not swept:
                ref = sl[j - 1] if sg > 0 else sh[j - 1]
                swept = bool(np.isfinite(ref) and ((l[j] < ref) if sg > 0 else (h[j] > ref)))
                continue
            lvl = sh[j - 1] if sg > 0 else sl[j - 1]
            if not np.isfinite(lvl) or (c[j] - lvl) * sg <= 0:
                continue
            body = np.abs(c[max(0, j - 2):j + 1] - o[max(0, j - 2):j + 1]).max()
            if body < DISP * a15[j]:
                continue
            ob = None
            for q in range(j - 1, max(tap - 1, j - 12), -1):
                if (c[q] < o[q]) if sg > 0 else (c[q] > o[q]):
                    ob = float(h[q] if sg > 0 else l[q])
                    break
            if ob is None:
                break
            stop = float(ext - sg * 0.1 * a15[j])
            risk = (ob - stop) * sg
            t = end15[j]
            want = "bull" if sg > 0 else "bear"
            out.append(dict(t=t, sg=sg, entry=ob, stop=stop, risk=risk, target=ob + sg * RR * risk, tf=z["tf"],
                            zone=(z["lo"], z["hi"]), bias_ok=_bias_at(bD, t) == want or _bias_at(b4, t) == want,
                            sweep=float(ext), mss=float(lvl)))
            break
    return sorted(out, key=lambda s: s["t"])


def backtest(df):
    """Trades (entry time, R after costs, 'long'/'short') with the live rules, for research.judge / backtest.json."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    idx, n = df.index, len(df)
    out, busy = [], None
    for s in setups(df):
        if not s["bias_ok"] or not MIN_RISK <= s["risk"] <= MAX_RISK:
            continue
        if busy is not None and s["t"] < busy:
            continue
        sg, en, st = s["sg"], s["entry"], s["stop"]
        i5 = int(idx.searchsorted(s["t"]))
        j0 = next((j for j in range(i5, min(i5 + LIMIT_BARS, n)) if ((l[j] <= en) if sg > 0 else (h[j] >= en))), None)
        if j0 is None:
            continue
        risk, tgt = s["risk"], s["target"]
        jend = min(j0 + HOLD_BARS, n - 1)
        r, jx = None, jend
        for j in range(j0, jend + 1):
            if (l[j] <= st) if sg > 0 else (h[j] >= st):
                r, jx = (st - en) * sg / risk, j
                break
            if (h[j] >= tgt) if sg > 0 else (l[j] <= tgt):
                r, jx = RR, j
                break
        if r is None:
            r = (c[jend] - en) * sg / risk
        out.append((idx[j0], r - COST / risk, "long" if sg > 0 else "short"))
        busy = idx[jx]
    return out


# ------------------------------------------------------------------ live
def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def main():
    import os
    if os.environ.get("SPLUS") != "on":   # owner, 11 Nov 2026: ONE signal model (A+ / B+); S+ kept for later, off
        print("splus: off (one-model mode)"); return
    from engine import load
    from levels import to_ny
    from tg import fmt, local, log_alert, send, send_photo
    now = time.time()
    df = load("5m", "20d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = df[df.index + pd.Timedelta(minutes=5) <= pd.Timestamp(now, unit="s", tz="UTC")]   # closed candles only
    df = to_ny(df[df["Volume"] >= 0])
    fresh = [s for s in setups(df) if s["bias_ok"] and now - s["t"].timestamp() <= 20 * 60
             and MIN_RISK <= s["risk"] <= MAX_RISK]
    if not fresh:
        print("splus: no new S+ setup"); return
    s = fresh[-1]
    st = jl(STATE, {"keys": []})
    key = f"splus|{s['t']}"
    if key in st["keys"]:
        print("splus: already sent", key); return
    log = jl("alerts_log.json", [])
    if any(a.get("kind") == "splus" and a["status"] in ("pending", "filled") for a in log):
        print("splus: an S+ order is still open"); return
    sg, en, sl_, tp = s["sg"], s["entry"], s["stop"], s["target"]
    last = df.iloc[int(df.index.searchsorted(s["t"])):]
    if len(last) and (((last["Low"] <= en).any()) if sg > 0 else ((last["High"] >= en).any())):
        print("splus: price already came back to the entry before the alert: skipped (no late entries)"); return
    try:
        from notify import news_soon
        why = news_soon(jl("news.json", {}), mins=120, now=now)
        if why:
            print("splus: high-impact news within the order window:", why); return
    except Exception as e:
        print("splus: news check failed:", e)
    bull = sg > 0
    side = "BUY" if bull else "SELL"
    risk = s["risk"]
    bt = (jl("backtest.json", {}).get("models", {}).get("ict_splus") or {}).get("all") or TRIES
    valid_until = now + 2 * 3600
    zone = f"{'Daily' if s['tf'] == 'D' else '4H'} {'demand' if bull else 'supply'} zone {fmt(s['zone'][0])}–{fmt(s['zone'][1])}"
    caption = "\n".join([
        f"🎯 <b>XAU/USD — {side} LIMIT | S+ SETUP</b> (small SL)",
        f"🇰🇭 <b>{'ទិញ' if bull else 'លក់'} LIMIT</b> · ចូល {fmt(en)} · SL {fmt(sl_)} · TP {fmt(tp)} · មិនដល់ក្នុង 2 ម៉ោង = មិនចូល",
        f"📍 Entry (limit): <b>{fmt(en)}</b>",
        f"🛑 SL: <b>{fmt(sl_)}</b> ({risk * 10:,.0f} pips)",
        f"🎯 TP: <b>{fmt(tp)}</b> (+{risk * RR * 10:,.0f} pips) = 3R",
        f"💰 0.01 lot: SL −${risk:,.1f} · TP +${risk * RR:,.1f}",
        f"⏳ Valid until <b>{local(valid_until)}</b>. Not filled = no trade.",
        f"🧠 {zone} → liquidity swept at {fmt(s['sweep'])} → 15m MSS above {fmt(s['mss'])} → limit on the OB retest"
        if bull else
        f"🧠 {zone} → liquidity swept at {fmt(s['sweep'])} → 15m MSS below {fmt(s['mss'])} → limit on the OB retest",
        f"📊 Tested 2 years: {bt.get('trades')} trades · {bt.get('win_rate_pct')}% win · {bt.get('avg_R', 0):+.2f}R per trade "
        f"(3R wins pay for the losses)",
        "⚖️ <b>Small size: risk 0.25–0.5%</b> until live results prove it · lot តូច · ការអប់រំ មិនមែនដំបូន្មាន",
    ])
    mid = None
    try:
        import signal_card
        signal_card.make(df, {"dir": "bull" if bull else "bear", "entry": en, "stop": sl_, "tp1": None, "target": tp},
                         "splus_card.png", tier="splus", status="LIMIT", win_rate=bt.get("win_rate_pct"),
                         trades=bt.get("trades"), stamp=local(now), tf_label="S+ · Daily/4H zone · 15m MSS",
                         bars=96, hold_note="limit valid 2 h · closes within 12 h")
        mid = send_photo("splus_card.png", caption, f"{side} limit")
    except Exception as e:
        print("splus card failed:", e)
    if not mid:
        mid = send(caption, f"{side} limit")
    if not mid:
        return
    st["keys"] = (st["keys"] + [key])[-50:]
    json.dump(st, open(STATE, "w"))
    log_alert({"id": key, "kind": "splus", "model": "ict_splus", "dir": "bull" if bull else "bear", "entry": en,
               "stop": sl_, "target": tp, "rr": RR, "created": now, "valid_until": valid_until,
               "price_at_alert": float(df["Close"].iloc[-1]), "msg_id": mid if isinstance(mid, int) else None,
               "status": "pending", "max_hold_s": 12 * 3600, "tier": "splus"})
    print("splus sent", side, en, sl_, tp)


if __name__ == "__main__":
    main()
