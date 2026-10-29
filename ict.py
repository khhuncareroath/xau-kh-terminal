"""ICT engine (v2: sweeps use prior-day/session levels and 15m/1H swings, exports a chart block): swings, market structure shifts (MSS/BOS), order blocks, fair value gaps,
liquidity sweeps, and a setup tracker (waiting -> swept -> shift confirmed -> retest -> void).

Run after levels.py:   python ict.py   ->  ict.json

Rules are mechanical versions of the concepts, so they will not match every chart
a human draws. Compare the output with your own markings and tell me the differences.
These are analysis ideas, not signals.
"""
import json
import os
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from engine import atr, load
from levels import to_ny

N = 2            # swing strength: bars on each side
FVG_MIN = 0.25   # minimum gap size in ATRs
LOOKBACK = 96    # bars (8h of 5m) in which a sweep still counts
TARGETS = os.environ.get("XAU_RULES", "current")   # "v2" = target only swings that are still untaken (see backtest.json)
RULES = {"15m": "15min", "1H": "1h", "4H": "4h", "D": "24h"}  # 24h bins start 18:00 New York (futures day)


def resample(df, tf):
    if tf == "5m":
        return df
    kw = {"offset": "2h"} if tf == "4H" else {"offset": "18h"} if tf == "D" else {}
    return df.resample(RULES[tf], **kw).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()


def swings(df, n=N):
    h, l, out = df["High"].to_numpy(), df["Low"].to_numpy(), []
    for i in range(n, len(df) - n):
        if np.argmax(h[i - n:i + n + 1]) == n:
            out.append((i + n, i, "H", float(h[i])))
        if np.argmin(l[i - n:i + n + 1]) == n:
            out.append((i + n, i, "L", float(l[i])))
    return sorted(out)


def structure(df, a, sw):
    """A close beyond the last confirmed swing is a break. First break against the trend = MSS, with it = BOS."""
    o, c = df["Open"].to_numpy(), df["Close"].to_numpy()
    ev, trend, k, last_h, last_l = [], None, 0, None, None
    for i in range(len(df)):
        while k < len(sw) and sw[k][0] <= i:
            _, idx, kind, p = sw[k]
            if kind == "H":
                last_h = (idx, p)
            else:
                last_l = (idx, p)
            k += 1
        for d, ref in (("bull", last_h), ("bear", last_l)):
            if ref and ((d == "bull" and c[i] > ref[1]) or (d == "bear" and c[i] < ref[1])):
                typ = "MSS" if trend not in (None, d) else "BOS"
                lo = max(i - 2, 0)
                ev.append({"i": i, "type": typ, "dir": d, "level": round(ref[1], 2), "swing_idx": ref[0],
                           "displacement": bool(np.abs(c[lo:i + 1] - o[lo:i + 1]).max() >= a[i])})
                trend = d
                if d == "bull":
                    last_h = None
                else:
                    last_l = None
                break
    return ev


def order_block(df, e):
    """Last opposite candle before the move that broke structure."""
    o, c, h, l = (df[k].to_numpy() for k in ("Open", "Close", "High", "Low"))
    i, s = e["i"], max(e["swing_idx"], 0)
    if i - s < 1:
        return None
    seg = range(s, i)
    if e["dir"] == "bull":
        start = min(seg, key=lambda j: l[j])
        for j in range(i - 1, start - 1, -1):
            if c[j] < o[j]:
                return {"dir": "bull", "i": j, "lo": float(l[j]), "hi": float(h[j])}
    else:
        start = max(seg, key=lambda j: h[j])
        for j in range(i - 1, start - 1, -1):
            if c[j] > o[j]:
                return {"dir": "bear", "i": j, "lo": float(l[j]), "hi": float(h[j])}
    return None


def zone_status(df, z, start):
    c, h, l = (df[k].to_numpy()[start + 1:] for k in ("Close", "High", "Low"))
    if len(c) == 0:
        return "fresh"
    if z["dir"] == "bull":
        return "invalid" if (c < z["lo"]).any() else "tested" if (l <= z["hi"]).any() else "fresh"
    return "invalid" if (c > z["hi"]).any() else "tested" if (h >= z["lo"]).any() else "fresh"


def find_fvgs(df, a):
    h, l, c = (df[k].to_numpy() for k in ("High", "Low", "Close"))
    out = []
    for i in range(2, len(df)):
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= FVG_MIN * a[i]:
            g = {"dir": "bull", "i": i - 1, "lo": float(h[i - 2]), "hi": float(l[i])}
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= FVG_MIN * a[i]:
            g = {"dir": "bear", "i": i - 1, "lo": float(h[i]), "hi": float(l[i - 2])}
        else:
            continue
        later_c, later_h, later_l = c[i + 1:], h[i + 1:], l[i + 1:]
        if g["dir"] == "bull":
            g["status"] = "filled" if (later_c < g["lo"]).any() else "partial" if (later_l <= g["hi"]).any() else "open"
        else:
            g["status"] = "filled" if (later_c > g["hi"]).any() else "partial" if (later_h >= g["lo"]).any() else "open"
        out.append(g)
    return out


LEVEL_WORD = re.compile(r"\b(high|low)\b", re.I)


def htf_pools(keep, d5):
    """Swing highs/lows on 15m and 1H are the liquidity that matters. 5m swings (10 minutes wide) are too small:
    every wiggle would count as a sweep."""
    out = []
    for tf, delta in (("15m", pd.Timedelta(minutes=15)), ("1H", pd.Timedelta(hours=1))):
        d, sw = keep[tf][0], keep[tf][2]
        for conf, _, kind, p in sw:
            start = int(d5.index.searchsorted(d.index[conf] + delta))   # first 5m bar after the swing was confirmed
            out.append((p, "buy-side" if kind == "H" else "sell-side", f"{tf} swing {'high' if kind == 'H' else 'low'}", start - 1))
    return out


def find_sweeps(df, a, extra, levels):
    """Price pokes through a key level and closes back inside = liquidity sweep.
    Key levels: prior-day and completed-session highs/lows from levels.json, plus 15m and 1H swings."""
    h, l, c, n = df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy(), len(df)
    pools = list(extra)
    for name, p in levels.items():
        m = LEVEL_WORD.search(name)
        if m and not name.startswith("Today") and "VW" not in name:
            pools.append((p, "buy-side" if m.group(1).lower() == "high" else "sell-side", name, 0))
    out = []
    for p, side, name, start in pools:
        for j in range(max(start + 1, n - LOOKBACK), n):
            buf = 0.1 * a[j]
            if side == "buy-side" and h[j] > p + buf:
                if c[j] < p:
                    out.append({"i": j, "side": side, "level": round(p, 2), "name": name, "extreme": float(h[j])})
                break
            if side == "sell-side" and l[j] < p - buf:
                if c[j] > p:
                    out.append({"i": j, "side": side, "level": round(p, 2), "name": name, "extreme": float(l[j])})
                break
    rank = lambda nm: 1 if nm.startswith("1H swing") else 2 if nm.startswith("15m swing") else 0   # named levels first
    best = {}
    for x in out:   # one sweep per bar and side, so a 1H and a 15m swing at the same price do not count twice
        k = (x["i"], x["side"])
        if k not in best or rank(x["name"]) < rank(best[k]["name"]):
            best[k] = x
    return sorted(best.values(), key=lambda s: s["i"])


def session_vwap(df):
    """VWAP and its standard deviation, restarting at 18:00 New York like the futures day."""
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    v = df["Volume"].clip(lower=0).fillna(0)
    day = np.asarray((df.index - pd.Timedelta(hours=18)).date)
    cv, cpv, cpv2 = v.groupby(day).cumsum(), (v * tp).groupby(day).cumsum(), (v * tp * tp).groupby(day).cumsum()
    m = (cpv / cv).where(cv > 0, tp)
    var = (cpv2 / cv - m ** 2).where(cv > 0, 0).clip(lower=0)
    return m, np.sqrt(var)


def setup(df, a, events, obs, fvgs, sweeps, htf_bias, sw):
    n, c = len(df), df["Close"].to_numpy()
    base = {"stage": 0, "label": "Waiting for a sweep", "dir": None, "reasons": []}
    if not sweeps:
        return base
    s = sweeps[-1]
    d = "bull" if s["side"] == "sell-side" else "bear"
    why = [f"{s['name']} at {s['level']} was swept and price closed back inside ({s['side']} liquidity taken)."]
    marks = {"sweep": {"i": s["i"], "price": s["level"]}}
    brk = [e for e in events if e["dir"] == d and e["i"] > s["i"]]
    if not brk:
        return {"stage": 1, "label": "Sweep happened, waiting for a structure shift", "dir": d, "reasons": why, "marks": marks}
    e = brk[0]
    marks["mss"] = {"i": e["i"], "level": e["level"]}
    why.append(f"Price closed beyond {e['level']}: a {d} structure shift right after the sweep.")
    if (c[e["i"] + 1:] < s["extreme"]).any() if d == "bull" else (c[e["i"] + 1:] > s["extreme"]).any():
        return {"stage": 4, "label": "Idea void: price took out the sweep extreme", "dir": d, "reasons": why, "marks": marks}
    zone = obs.get(e["i"]) or next((g for g in fvgs if g["dir"] == d and s["i"] <= g["i"] <= e["i"] and g["status"] != "filled"), None)
    if zone is None:
        return {"stage": 2, "label": "Shift confirmed, no clear retest zone", "dir": d, "reasons": why, "marks": marks}
    kind = "order block" if "status" not in zone or zone.get("kind") == "ob" else "fair value gap"
    why.append(f"Retest zone: {kind} {round(zone['lo'], 2)}-{round(zone['hi'], 2)}.")
    marks["zone"] = {"i": zone["i"], "lo": round(zone["lo"], 2), "hi": round(zone["hi"], 2), "kind": "ob" if kind == "order block" else "fvg"}
    pad = 0.2 * a[-1]
    inside = zone["lo"] - pad <= c[-1] <= zone["hi"] + pad
    entry = (zone["lo"] + zone["hi"]) / 2
    buf = max(0.5, 0.3 * a[-1])
    stop = s["extreme"] - buf if d == "bull" else s["extreme"] + buf
    risk = abs(entry - stop)
    h, l = df["High"].to_numpy(), df["Low"].to_numpy()
    if TARGETS == "v2":   # only swings nobody has run yet: real resting liquidity
        tgt_pool = [p for _, idx, k, p in sw if (k == "H" and p > entry and h[idx + 1:].max(initial=-1e9) < p)
                    or (k == "L" and p < entry and l[idx + 1:].min(initial=1e9) > p)]
    else:
        tgt_pool = [p for _, _, k, p in sw if (k == "H" and p > entry) or (k == "L" and p < entry)]
    pool = [p for p in tgt_pool if (p > entry) == (d == "bull") and abs(p - entry) >= 1.5 * risk]   # a target next to the entry is not worth taking
    target = (min(pool) if d == "bull" else max(pool)) if pool else (entry + 2 * risk if d == "bull" else entry - 2 * risk)
    if htf_bias:
        why.append(f"1H structure is {htf_bias}: " + ("agrees." if htf_bias == d else "this goes against it, so treat as lower quality."))
    return {"stage": 3 if inside else 2, "label": "Price is in the retest zone" if inside else "Shift confirmed, waiting for the retest",
            "dir": d, "zone": [round(zone["lo"], 2), round(zone["hi"], 2)], "entry": round(entry, 2), "stop": round(stop, 2),
            "target": round(float(target), 2), "rr": round(abs(target - entry) / risk, 2) if risk else None, "reasons": why,
            "sweep_time": str(df.index[s["i"]]), "shift_time": str(df.index[e["i"]]), "sweep_extreme": round(s["extreme"], 2),
            "sweep_name": s["name"], "displacement": e["displacement"], "risk_atr": round(risk / a[-1], 2) if a[-1] else None,
            "note": "Idea to confirm with your own entry model, not a signal.", "marks": marks}


def main():
    df = to_ny(load("5m", "59d"))
    lv = json.load(open("levels.json")) if os.path.exists("levels.json") else {}
    levels = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    price = float(df["Close"].iloc[-1])
    out = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "price": round(price, 2),
           "last_bar": str(df.index[-1]), "atr_5m": round(float(atr(df).iloc[-1]), 2), "rules": TARGETS, "timeframes": {}}
    keep = {}
    for tf in ("5m", "15m", "1H", "4H", "D"):
        d = resample(df, tf)
        d = d.tail(900) if tf == "5m" else d
        a = atr(d).to_numpy()
        sw = swings(d)
        ev = structure(d, a, sw)
        obs = {}
        for e in ev:
            ob = order_block(d, e)
            if ob:
                ob["status"], ob["kind"] = zone_status(d, ob, ob["i"]), "ob"
                obs[e["i"]] = ob
        fv = find_fvgs(d, a)
        keep[tf] = (d, a, sw, ev, obs, fv)
        last = ev[-1] if ev else None
        near = sorted([g for g in fv if g["status"] != "filled"], key=lambda g: abs((g["lo"] + g["hi"]) / 2 - price))[:3]
        fmt = lambda z: {**{k: (round(v, 2) if isinstance(v, float) else v) for k, v in z.items() if k not in ("i", "kind")},
                         "time": str(d.index[z["i"]])}
        out["timeframes"][tf] = {
            "bias": last["dir"] if last else "mixed",
            "last_events": [{"type": e["type"], "dir": e["dir"], "level": e["level"], "time": str(d.index[e["i"]]),
                             "displacement": e["displacement"]} for e in ev[-3:]],
            "order_blocks": [fmt(o) for o in list(obs.values())[-3:] if o["status"] != "invalid"],
            "fvgs": [fmt(g) for g in near]}
    d5, a5, sw5, ev5, obs5, fv5 = keep["5m"]
    sweeps = find_sweeps(d5, a5, htf_pools(keep, d5), levels)
    out["sweeps"] = [{k: v for k, v in s.items() if k != "i"} | {"time": str(d5.index[s["i"]])} for s in sweeps[-3:]]
    # judge each of the last three sweeps and follow the most advanced idea that is still alive (a later, unrelated sweep must not hide it)
    cands = [setup(d5, a5, ev5, obs5, fv5, sweeps[:k], out["timeframes"]["1H"]["bias"], sw5) for k in range(max(1, len(sweeps) - 2), len(sweeps) + 1)] or \
            [setup(d5, a5, ev5, obs5, fv5, [], out["timeframes"]["1H"]["bias"], sw5)]
    out["setup"] = max(reversed(cands), key=lambda x: x["stage"] if x["stage"] < 4 else -1)
    if len(d5) >= 60:   # last 60 five-minute bars, VWAP bands and setup markers, for the chart in the app
        off, w = len(d5) - 60, d5.tail(60)
        vm, vs = session_vwap(df)
        vm, vs = vm.reindex(w.index), vs.reindex(w.index)
        rel = {k: {**{kk: vv for kk, vv in m.items() if kk != "i"}, "i": m["i"] - off}
               for k, m in out["setup"].pop("marks", {}).items() if m["i"] - off >= 0}
        out["chart"] = {"tf": "5m", "times": [t.strftime("%m-%d %H:%M") for t in w.index], "ts": [int(t.timestamp()) for t in w.index],
                        "candles": [[round(float(r.Open), 2), round(float(r.High), 2), round(float(r.Low), 2), round(float(r.Close), 2),
                                     round(float(r.Volume), 1)] for r in w.itertuples()],
                        "vwap": [round(float(x), 2) for x in vm], "sd": [round(float(x), 2) for x in vs], "marks": rel}
    out["setup"].pop("marks", None)
    out["disclaimer"] = "Mechanical analysis ideas, not signals or advice."
    with open("ict.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("setup:", out["setup"]["stage"], out["setup"]["label"])
    for tf, v in out["timeframes"].items():
        print(f"  {tf}: bias {v['bias']}, {len(v['order_blocks'])} OB, {len(v['fvgs'])} open FVG")


if __name__ == "__main__":
    main()
