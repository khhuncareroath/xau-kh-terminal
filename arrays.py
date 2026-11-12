"""👀 The other side: active demand / supply (FVGs and order blocks) on 15m, 30m, 1H, 4H and Daily, any width.

Same detection as studies/opposite_side.py (the test the live rule comes from): FVG >= 0.2 ATR of its timeframe, order
block of a displacement structure break; active from the close of the candle that made it until a close through it
or its lifetime ends (15m 2 d, 30m 3 d, 1H 5 d, 4H 15 d, D 40 d).
"""
import numpy as np
import pandas as pd

import ict
from engine import atr

TF = {"15m": ("15min", 2, 15), "30m": ("30min", 3, 30), "1H": ("1h", 5, 60), "4H": (None, 15, 240), "D": (None, 40, 1440)}


def zones(df, tf):
    rule, life, mins = TF[tf]
    d = ict.resample(df, tf) if rule is None else df.resample(rule).agg(ict.AGG).dropna()
    span = pd.Timedelta(minutes=mins)
    a = atr(d).to_numpy()
    h, l, c = (d[k].to_numpy() for k in ("High", "Low", "Close"))
    raw = []
    for i in range(2, len(d)):
        if not np.isfinite(a[i]):
            continue
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= 0.2 * a[i]:
            raw.append(("bull", h[i - 2], l[i], i))
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= 0.2 * a[i]:
            raw.append(("bear", h[i], l[i - 2], i))
    try:
        for e in ict.structure(d, a, ict.swings(d, 3)):
            ob = ict.order_block(d, e)
            if ob and e["displacement"]:
                raw.append((ob["dir"], ob["lo"], ob["hi"], e["i"]))
    except Exception as e:
        print("arrays: order blocks", tf, "failed:", e)
    out = []
    for dr, lo, hi, i in raw:
        if i + 1 >= len(d):
            continue
        after = c[i + 1:]
        bad = np.where(after < lo)[0] if dr == "bull" else np.where(after > hi)[0]
        t0 = d.index[i] + span
        t1 = d.index[i + 1 + bad[0]] + span if len(bad) else t0 + pd.Timedelta(days=life)
        out.append(dict(dir=dr, lo=float(lo), hi=float(hi), t0=t0, t1=min(t1, t0 + pd.Timedelta(days=life)), tf=tf))
    return out


def opposite(df, entry, sg, risk, now=None, tfs=("15m", "30m", "1H", "4H", "D")):
    """Nearest edge of an active zone of the OTHER side ahead of the entry (for a SELL: a bull zone's top or bottom
    below the entry). Returns {dist_r, edge, tf, lo, hi, inside} or None. inside = the entry sits in such a zone."""
    now = now if now is not None else df.index[-1] + pd.Timedelta(minutes=5)
    want = "bear" if sg > 0 else "bull"
    best, inside = None, None
    for tf in tfs:
        try:
            zs = zones(df, tf)
        except Exception as e:
            print("arrays", tf, "failed:", e)
            continue
        for z in zs:
            if z["dir"] != want or not (z["t0"] <= now < z["t1"]):
                continue
            if z["lo"] <= entry <= z["hi"]:
                inside = inside or tf
            for lv in (z["lo"], z["hi"]):
                d = (lv - entry) * sg / risk
                if d > 0.05 and (best is None or d < best["dist_r"]):
                    best = {"dist_r": round(d, 2), "edge": round(lv, 2), "tf": tf, "lo": round(z["lo"], 2), "hi": round(z["hi"], 2)}
    if best:
        best["inside"] = inside
    return best
