"""⏳ SECOND CHANCE: one re-entry after a signal gets swept (owner, 12 Nov 2026; studies/m15_ltf_confirm.py).

The normal signal is NOT changed. After it goes out, the bot watches the closed 5m candles:
  1. SWEEP: price takes the liquidity against the signal = the 5m high (for a SELL) / low (for a BUY) of the hour
     before the signal. The sweep extreme keeps updating while price pushes further.
  2. MSS: a 5m close back through the last 5m swing made before the sweep extreme (the low of the 8 candles before it
     for a SELL, the high for a BUY).
  3. ENTRY: a LIMIT at that broken level (the retest), valid 30 min. SL just beyond the sweep extreme (+0.1 x 5m ATR,
     max $25). TP1 = the signal's TP1 (or its 1R), TP2 = the signal's final target; half at TP1, SL to entry.
     Not sent if TP1 is less than 0.5R from the limit, or if price already reached TP1 before the fill.
Only within WAIT_H hours of the signal, one second chance per signal.
Tested on 369 replayed M15 signals (2 years): all 24 versions positive; the live code (studies/second_replay.py)
52 re-entries, 54% win, +0.47R, t 2.05, 5 of 7 quarters, newest 30% only 14 trades +0.07R: NOT fully proven -> small size 0.25-0.5%, labelled testing,
counted apart (kind "second"). SECOND_CHANCE=off stops it.  Run:  python second.py
"""
import json
import os
import time

import numpy as np
import pandas as pd

LIQ_BARS = 12        # liquidity = the 5m high / low of the hour before the signal
WAIT_H = 6           # the sweep + MSS must come within 6 h of the signal
SWING_BARS = 8       # MSS level = extreme of the 8 candles before the sweep extreme
RETEST_BARS = 6      # the limit is valid 30 min
MAX_RISK, MIN_RISK = 25.0, 0.5
KINDS = {"m15": 8, "scalp": 3, "fun": 3}   # which signals get a second chance -> hold hours of the re-entry
COST = 0.4


def atr5(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]
    return pd.Series(np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])).rolling(n).mean().to_numpy()


def find(o, h, l, c, a, j0, sg, tp1, last=None, liq_bars=LIQ_BARS, wait_bars=None, swing_bars=SWING_BARS):
    """First sweep + MSS after signal bar j0 (the first candle after the signal). Returns dict(j, level, stop) or None.
    Only closed candles up to `last` are used, so it can run live (no look-ahead)."""
    wait_bars = wait_bars or WAIT_H * 12
    last = len(c) - 1 if last is None else last
    if j0 - liq_bars < 0:
        return None
    lvl = h[j0 - liq_bars:j0].max() if sg < 0 else l[j0 - liq_bars:j0].min()
    ext = jext = None
    for j in range(j0, min(j0 + wait_bars, last + 1)):
        if ext is None:
            if (h[j] > lvl) if sg < 0 else (l[j] < lvl):
                ext, jext = (h[j] if sg < 0 else l[j]), j
            continue
        if (h[j] > ext) if sg < 0 else (l[j] < ext):
            ext, jext = (h[j] if sg < 0 else l[j]), j
            continue
        seg = slice(max(j0 - 6, jext - swing_bars), jext)
        key = l[seg].min() if sg < 0 else h[seg].max()
        if (c[j] < key) if sg < 0 else (c[j] > key):
            st = ext - sg * 0.1 * a[j]
            risk = abs(key - st)
            if not MIN_RISK < risk <= MAX_RISK or (tp1 - key) * sg < 0.5 * risk:
                return {"j": j, "level": float(key), "stop": float(st), "skip": "risk or TP1 too close"}
            return {"j": j, "level": float(key), "stop": float(st), "skip": None}
    return None


def fill(o, h, l, c, plan, sg, tp1, last=None):
    """Retest fill of the limit after the MSS candle: (fill bar or None, why)."""
    last = len(c) - 1 if last is None else last
    for k in range(plan["j"] + 1, min(plan["j"] + 1 + RETEST_BARS, last + 1)):
        if (h[k] >= plan["level"]) if sg < 0 else (l[k] <= plan["level"]):
            return k, "filled"
        if (l[k] <= tp1) if sg < 0 else (h[k] >= tp1):
            return None, "missed"
    return None, "waiting" if plan["j"] + RETEST_BARS > last else "expired"


def grade(o, h, l, c, sg, en, st, tp1, tp2, jin, hold_bars):
    """Same exits as track.py: half at TP1, SL to entry, rest at TP2, closed after hold; fill-candle stop counts."""
    risk = abs(en - st)
    n = len(c)
    if (h[jin] >= st) if sg < 0 else (l[jin] <= st):
        return -1 - COST / risk
    jend = min(jin + hold_bars, n - 1)
    stop, got, left, hit1 = st, 0.0, 1.0, False
    for j in range(jin + 1, jend + 1):
        if (l[j] <= stop) if sg > 0 else (h[j] >= stop):
            return got + left * (stop - en) * sg / risk - COST / risk
        if not hit1 and ((h[j] >= tp1) if sg > 0 else (l[j] <= tp1)):
            got, left, hit1, stop = got + 0.5 * abs(tp1 - en) / risk, 0.5, True, en
        if hit1 and ((h[j] >= tp2) if sg > 0 else (l[j] <= tp2)):
            return got + left * abs(tp2 - en) / risk - COST / risk
    return got + left * (c[jend] - en) * sg / risk - COST / risk


def targets(sig):
    """TP1 / TP2 of the re-entry from the original signal: its TP1 (or its 1R) and its final target."""
    sg = 1 if sig["dir"] == "bull" else -1
    tp1 = sig.get("tp1") or sig["entry"] + sg * abs(sig["entry"] - sig["stop"])
    return float(tp1), float(sig["target"])


def simulate(df, sig, j0, hold_h):
    """Backtest helper: the R of the second chance for one signal (None = no second chance)."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr5(h, l, c)
    sg = 1 if sig["dir"] == "bull" else -1
    tp1, tp2 = targets(sig)
    p = find(o, h, l, c, a, j0, sg, tp1)
    if p is None or p["skip"]:
        return None
    k, why = fill(o, h, l, c, p, sg, tp1)
    if k is None:
        return None
    return grade(o, h, l, c, sg, p["level"], p["stop"], tp1, tp2, k, hold_h * 12)


# ---------------------------------------------------------------- live -----------------------------------------------
STATE = "second_state.json"


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def main():
    if os.environ.get("SECOND_CHANCE", "on") == "off":
        print("second: off"); return
    now = time.time()
    log = jl("alerts_log.json", [])
    st = jl(STATE, {})
    parents = [a for a in log if a.get("kind") == "m15" and a.get("model") == "setup_idea" and a["id"] not in st
               and now - a["created"] <= WAIT_H * 3600 + RETEST_BARS * 300]
    if not parents:
        print("second: no recent M15 signal to watch"); return
    if any(a.get("kind") == "second" and a["status"] in ("pending", "filled") for a in log):
        print("second: a second chance is still open"); return
    from engine import closed, load
    from tg import fmt, local, log_alert, msg_link, send, send_photo
    df = load("5m", "5d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = closed(df)
    o, h, l, c = (df[k].to_numpy(float) for k in ("Open", "High", "Low", "Close"))
    a5 = atr5(h, l, c)
    last = len(df) - 1
    starts = np.asarray((df.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1), dtype="int64")
    changed = False
    for sig in parents:
        sg = 1 if sig["dir"] == "bull" else -1
        j0 = int(np.searchsorted(starts, (int(sig["created"]) // 300) * 300))   # first 5m candle after the signal
        if j0 > last:
            continue
        tp1, tp2 = targets(sig)
        p = find(o, h, l, c, a5, j0, sg, tp1, last=last)
        expired = now - sig["created"] > WAIT_H * 3600
        if p is None:
            if expired:
                st[sig["id"]] = "no sweep + MSS"; changed = True
            continue
        changed = True
        if p["skip"]:
            st[sig["id"]] = p["skip"]; print("second:", sig["id"], p["skip"]); continue
        k, why = fill(o, h, l, c, p, sg, tp1, last=last)
        if why != "waiting":
            st[sig["id"]] = f"MSS seen late ({why})"; print("second:", sig["id"], st[sig["id"]]); continue
        close_t = int(starts[p["j"]]) + 300
        loc = pd.Timestamp(now, unit="s", tz="Asia/Phnom_Penh")
        if loc.hour < 6:
            st[sig["id"]] = "00-06 Cambodia: no new trades"; continue
        try:
            from notify import news_soon
            if news_soon(jl("news.json", {}), mins=15, now=now):
                st[sig["id"]] = "big news within 15 min"; print("second: news, skipped"); continue
        except Exception as e:
            print("second: news check failed:", e)
        en, sl = p["level"], p["stop"]
        risk = abs(en - sl)
        bull = sg > 0
        side = "BUY" if bull else "SELL"
        hold_s = int(min(8 * 3600, ((loc.normalize() + pd.Timedelta(days=1)) - loc).total_seconds()))   # closed by 24:00
        link = msg_link(sig.get("msg_id"), f"{side} {fmt(sig['entry'])}")
        cap = "\n".join(x for x in [
            f"⏳ <b>XAU/USD — {side} | SECOND CHANCE</b> · testing",
            f"📍 Limit entry: <b>{fmt(en)}</b> (retest, valid 30 min)",
            f"🛑 SL: <b>{fmt(sl)}</b>",
            f"🎯 TP1: <b>{fmt(tp1)}</b>",
            f"🎯 TP2: <b>{fmt(tp2)}</b>",
            f"🧹 Price swept the {'low' if bull else 'high'} first, then a 5m candle closed back {'above' if bull else 'below'} "
            f"{fmt(en)} (MSS). Re-entry for the {side} {fmt(sig['entry'])}" + (f" ({link})" if link else "") + ".",
            f"⏱ M5 entry · closes by 24:00 · −${risk:,.0f} at SL (0.01 lot) · small size 0.25–0.5%",
            "<i>Tested 2 years: +0.47R a trade, 54% win, but few recent trades, so the live record decides. · "
            "ឱកាសទីពីរ ទំហំតូច</i>",
        ] if x)
        title = f"{side} second chance"
        mid = None
        try:
            import signal_card
            signal_card.make(df, {"dir": "bull" if bull else "bear", "entry": en, "stop": sl, "tp1": tp1, "target": tp2},
                             "second_card.png", tier="second", status="LIMIT", stamp=local(now), tf_label="5m re-entry",
                             bars=80, hold_note="limit 30 min · by 24:00")
            mid = send_photo("second_card.png", cap, title)
        except Exception as e:
            print("second card failed, text:", e)
        if not mid:
            mid = send(cap, title)
        if not mid:
            continue   # not sent: try again next cycle
        st[sig["id"]] = "sent"
        log_alert({"id": f"second|{sig['id']}", "kind": "second", "model": "second_chance", "dir": sig["dir"],
                   "entry": en, "stop": sl, "tp1": tp1, "target": tp2, "part": 0.5, "rr": round(abs(tp2 - en) / risk, 2),
                   "created": now, "seen_to": close_t, "valid_until": close_t + RETEST_BARS * 300, "miss_at": "tp1",
                   "price_at_alert": float(c[last]), "msg_id": mid if isinstance(mid, int) else None, "status": "pending",
                   "max_hold_s": hold_s, "tier": "second", "parent": sig["id"]})
        print("second sent", side, en, sl, tp1, tp2)
        break
    if changed:
        json.dump(st, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
