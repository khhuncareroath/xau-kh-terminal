"""Backtest: replays the ict.py idea (liquidity sweep -> structure shift -> retest of OB/FVG) bar by bar on past
5m gold futures data, using ONLY information that existed at each moment, and measures what really happened.

Run:  python backtest.py            -> backtest.json
      (the workflow runs it once a day; it takes about a minute)

What it simulates, step by step, for every sweep in the data:
  1. A key level is swept (prior-day/session high or low, or a 15m/1H swing) and price closes back inside.
  2. Within MAX_SHIFT bars, price closes beyond the last swing in the new direction (the structure shift).
  3. A retest zone exists (order block, else a fresh fair value gap). Entry = zone midpoint, stop beyond the sweep
     extreme, target = nearest swing at least 1.5R away. Same formulas as ict.py.
  4. LATENCY: the alert reaches people LAT bars later (Yahoo delay + 15-minute schedule). If the idea died in
     that gap, no alert. The limit order is live from then until EXPIRE bars, or until the target is hit first
     (a "missed" trade, it ran without us).
  5. After a fill: stop first if both are touched in one candle (conservative), cost is charged on every trade.

Two rule sets are compared:
  current: exactly what notify.py alerts today (R:R >= 1.5).
  v2:      targets only at swings that are still untaken (real resting liquidity), stop no wider than
           MAX_RISK_ATR x ATR, and no alert if price is already more than half the risk past the entry.

Then every trade is tagged with factors (1H bias, session, displacement, zone type, ...) and the report shows which
factors actually helped. The best filter is chosen on the first 70% of the data and tested on the last 30%,
so you can see whether it holds on data it never saw. Small samples mislead: read the n column.
"""
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from engine import atr, load_history
from ict import order_block, resample, session_vwap, structure, swings
from levels import to_ny, trade_dates

COST = float(os.environ.get("BT_COST", 0.4))            # points per round trip: spread + slippage
LAT = int(os.environ.get("BT_LATENCY_BARS", 3))         # 3 x 5m = 15 min from signal to people
EXPIRE = int(os.environ.get("BT_EXPIRE_BARS", 24))      # order valid 2 hours
MAX_SHIFT = 48                                          # structure shift must come within 4h of the sweep
MAX_HOLD = 144                                          # close at market after 12h
MIN_RR = 1.5
MAX_RISK_ATR = float(os.environ.get("BT_MAX_RISK_ATR", 3.0))
FVG_MIN = 0.25


# ---------- causal building blocks ----------

def causal_fvgs(df, a):
    """Fair value gaps known at bar i (the third candle). Fill status is checked later, as of the moment we use it."""
    h, l = df["High"].to_numpy(), df["Low"].to_numpy()
    out = []
    for i in range(2, len(df)):
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= FVG_MIN * a[i]:
            out.append({"dir": "bull", "i": i - 1, "known": i, "lo": float(h[i - 2]), "hi": float(l[i])})
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= FVG_MIN * a[i]:
            out.append({"dir": "bear", "i": i - 1, "known": i, "lo": float(h[i]), "hi": float(l[i - 2])})
    return out


def level_pools(df):
    """Prior-day high/low (live all day) and Asia/London highs/lows (live after the session ends). (price, side, name, start, end)"""
    ny_h = df.index.hour
    dates = trade_dates(df.index)
    out, days = [], pd.unique(dates)
    pos = np.arange(len(df))
    for k, d in enumerate(days):
        m = dates == d
        idx = pos[m]
        if not len(idx):
            continue
        s, e = idx[0], idx[-1]
        if k > 0:
            pm = dates == days[k - 1]
            out.append((float(df["High"][pm].max()), "buy-side", "Prev day high", s, e))
            out.append((float(df["Low"][pm].min()), "sell-side", "Prev day low", s, e))
        hh = ny_h[m]
        for name, sel, end_h in (("Asia", (hh >= 18) | (hh < 2), 2), ("London", (hh >= 2) & (hh < 5), 5)):
            if sel.any():
                after = idx[(hh >= end_h) & (hh < 17)]
                if len(after):
                    sub = df.iloc[idx[sel]]
                    out.append((float(sub["High"].max()), "buy-side", f"{name} high", after[0], e))
                    out.append((float(sub["Low"].min()), "sell-side", f"{name} low", after[0], e))
    return out


def swing_pools(df):
    out = []
    for tf, delta in (("15m", pd.Timedelta(minutes=15)), ("1H", pd.Timedelta(hours=1))):
        d = resample(df, tf)
        for conf, _, kind, p in swings(d):
            start = int(df.index.searchsorted(d.index[conf] + delta))
            out.append((p, "buy-side" if kind == "H" else "sell-side", f"{tf} swing {'high' if kind == 'H' else 'low'}",
                        start, min(start + 576, len(df) - 1)))
    return out


def find_sweeps(df, a, pools):
    """First time price pierces each pool; if that candle closes back inside, it is a sweep (same rule as ict.py)."""
    h, l, c = df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy()
    best = {}
    rank = lambda nm: 1 if nm.startswith("1H swing") else 2 if nm.startswith("15m swing") else 0
    for p, side, name, s, e in pools:
        if s >= len(df) - 1 or e <= s:
            continue
        j0 = s
        buf = 0.1 * np.nan_to_num(a[j0:e + 1], nan=1.0)
        hit = (h[j0:e + 1] > p + buf) if side == "buy-side" else (l[j0:e + 1] < p - buf)
        if not hit.any():
            continue
        j = j0 + int(np.argmax(hit))
        if (side == "buy-side" and c[j] < p) or (side == "sell-side" and c[j] > p):
            x = {"i": j, "side": side, "level": p, "name": name, "extreme": float(h[j] if side == "buy-side" else l[j])}
            k = (j, side)
            if k not in best or rank(name) < rank(best[k]["name"]):
                best[k] = x
    return sorted(best.values(), key=lambda s: s["i"])


def htf_bias_series(df5):
    """1H structure bias as known at each 5m bar (a 1H event is only known once that hour has closed)."""
    d = resample(df5, "1H")
    a = atr(d).to_numpy()
    ev = structure(d, a, swings(d))
    bias = np.array([None] * len(df5), dtype=object)
    for e in ev:
        k = int(df5.index.searchsorted(d.index[e["i"]] + pd.Timedelta(hours=1)))
        if k < len(df5):
            bias[k:] = e["dir"]
    return bias


def session_of(ts):
    h = ts.hour
    return "London" if 2 <= h < 5 else "New York" if 7 <= h < 11 else "Asia" if (h >= 18 or h < 2) else "Off-hours"


# ---------- building candidate ideas ----------

def candidates(df, rules):
    a = atr(df).to_numpy()
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    sw = swings(df)
    ev = structure(df, a, sw)
    fv = causal_fvgs(df, a)
    sweeps = find_sweeps(df, a, level_pools(df) + swing_pools(df))
    hb = htf_bias_series(df)
    vw, _ = session_vwap(df)
    vw = vw.to_numpy()
    ev_by_dir = {"bull": [e for e in ev if e["dir"] == "bull"], "bear": [e for e in ev if e["dir"] == "bear"]}
    out = []
    for s in sweeps:
        d = "bull" if s["side"] == "sell-side" else "bear"
        e = next((x for x in ev_by_dir[d] if x["i"] > s["i"]), None)
        if e is None or e["i"] - s["i"] > MAX_SHIFT or e["i"] + LAT + 1 >= len(df):
            continue
        i = e["i"]
        zone = order_block(df, e)
        kind = "OB"
        if zone is None:
            kind = "FVG"
            for g in fv:
                if g["dir"] == d and s["i"] <= g["i"] <= i and g["known"] <= i:
                    seg = c[g["known"] + 1:i + 1]
                    filled = (seg < g["lo"]).any() if d == "bull" else (seg > g["hi"]).any()
                    if not filled:
                        zone = g
                        break
        if zone is None:
            continue
        entry = (zone["lo"] + zone["hi"]) / 2
        stop = s["extreme"] - max(0.5, 0.3 * a[i]) if d == "bull" else s["extreme"] + max(0.5, 0.3 * a[i])
        risk = abs(entry - stop)
        if risk <= 0 or (d == "bull" and entry <= stop) or (d == "bear" and entry >= stop):
            continue
        known = [(conf, idx, k, p) for conf, idx, k, p in sw if conf <= i]
        if rules == "v2":   # only swings nobody has run yet: real resting liquidity
            pool = []
            for conf, idx, k, p in known:
                if d == "bull" and k == "H" and p > entry and h[idx + 1:i + 1].max(initial=-1e9) < p:
                    pool.append(p)
                if d == "bear" and k == "L" and p < entry and l[idx + 1:i + 1].min(initial=1e9) > p:
                    pool.append(p)
        else:
            pool = [p for conf, idx, k, p in known if (k == "H" and p > entry) or (k == "L" and p < entry)]
            pool = [p for p in pool if (p > entry) == (d == "bull")]
        pool = [p for p in pool if abs(p - entry) >= MIN_RR * risk]
        target = (min(pool) if d == "bull" else max(pool)) if pool else (entry + 2 * risk if d == "bull" else entry - 2 * risk)
        rr = abs(target - entry) / risk
        if rr < MIN_RR:
            continue
        risk_atr = risk / a[i] if a[i] > 0 else 99
        if rules == "v2" and risk_atr > MAX_RISK_ATR:
            continue
        sgn = 1 if d == "bull" else -1
        out.append({"i": i, "sweep_i": s["i"], "dir": d, "entry": entry, "stop": stop, "target": target, "risk": risk, "rr": rr,
                    "extreme": s["extreme"], "sgn": sgn,
                    "f": {"direction": d,
                          "1H bias": "agrees" if hb[i] == d else "against" if hb[i] in ("bull", "bear") else "none",
                          "session": session_of(df.index[i]),
                          "displacement": "yes" if e["displacement"] else "no",
                          "zone": kind,
                          "swept level": "prior day / session" if not s["name"].split()[0] in ("15m", "1H") else s["name"].split()[0] + " swing",
                          "VWAP side": "agrees" if (c[i] - vw[i]) * sgn > 0 else "against",
                          "stop size": "tight (<1.5 ATR)" if risk_atr < 1.5 else "normal (1.5-3 ATR)" if risk_atr <= 3 else "wide (>3 ATR)",
                          "R:R": "1.5-2" if rr < 2 else "2-3" if rr < 3 else "3+"}})
    return out


# ---------- simulating what people could actually do ----------

def simulate(df, cands, rules):
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    n, trades, busy_until = len(df), [], -1
    for x in cands:
        i, sg, en, st, tg = x["i"], x["sgn"], x["entry"], x["stop"], x["target"]
        if i <= busy_until:
            continue    # one idea at a time, like notify.py
        t_act = i + 1 + LAT
        # the blind gap between signal and alert: did the idea die, or run, before anyone saw it?
        blind = slice(i + 1, t_act)
        if ((c[blind] - x["extreme"]) * sg < 0).any():
            continue    # voided before the alert: notify.py would not send it
        if ((h[blind] >= tg) if sg > 0 else (l[blind] <= tg)).any():
            trades.append({**x, "result": "missed", "R": 0.0, "t": t_act})
            busy_until = t_act
            continue
        if rules == "v2" and (c[t_act - 1] - en) * sg > 0.5 * x["risk"]:
            trades.append({**x, "result": "skipped: price already ran", "R": 0.0, "t": t_act})
            busy_until = t_act
            continue
        fill_j, fill_px, res = None, None, None
        for j in range(t_act, min(t_act + EXPIRE, n)):
            touch = l[j] <= en if sg > 0 else h[j] >= en
            if touch:
                fill_j = j
                fill_px = min(en, o[j]) if sg > 0 else max(en, o[j])
                break
            if (h[j] >= tg) if sg > 0 else (l[j] <= tg):
                res = "missed"
                busy_until = j
                break
        if fill_j is None:
            trades.append({**x, "result": res or "expired", "R": 0.0, "t": t_act})
            busy_until = max(busy_until, min(t_act + EXPIRE, n - 1))
            continue
        exit_px, outcome, j = None, None, fill_j
        while j < min(fill_j + MAX_HOLD, n):
            stop_hit = l[j] <= st if sg > 0 else h[j] >= st
            if stop_hit:   # a gap through the stop fills at the open; on the fill candle, never better than the fill
                exit_px = (min(st, o[j]) if sg > 0 else max(st, o[j])) if j > fill_j else (min(st, fill_px) if sg > 0 else max(st, fill_px))
                outcome = "loss"
                break
            if j > fill_j and ((h[j] >= tg) if sg > 0 else (l[j] <= tg)):
                exit_px, outcome = tg, "win"
                break
            j += 1
        if outcome is None:
            if j >= n:
                continue   # still open at the end of the data: not counted
            exit_px, outcome = c[j - 1], "timed out"
        r = (exit_px - fill_px) * sg / x["risk"] - COST / x["risk"]
        trades.append({**x, "result": outcome, "R": round(float(r), 3), "t": fill_j})
        busy_until = j
    return trades


def stats(ts):
    filled = [t for t in ts if t["result"] in ("win", "loss", "timed out")]
    if not filled:
        return {"alerts": len(ts), "filled": 0}
    R = np.array([t["R"] for t in filled])
    eq = np.cumsum(R)
    gains, losses = R[R > 0].sum(), -R[R < 0].sum()
    return {"alerts": len(ts), "filled": len(filled), "fill_rate_pct": round(100 * len(filled) / len(ts)),
            "missed": sum(t["result"] == "missed" for t in ts), "expired": sum(t["result"] == "expired" for t in ts),
            "win_rate_pct": round(100 * float((R > 0).mean())), "avg_R": round(float(R.mean()), 3),
            "total_R": round(float(R.sum()), 2), "profit_factor": round(float(gains / losses), 2) if losses > 0 else None,
            "max_drawdown_R": round(float((np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max()), 2)}


def factor_table(ts):
    filled = [t for t in ts if t["result"] in ("win", "loss", "timed out")]
    out = {}
    for f in (filled[0]["f"] if filled else {}):
        rows = {}
        for t in filled:
            rows.setdefault(t["f"][f], []).append(t["R"])
        out[f] = {k: {"n": len(v), "win_rate_pct": round(100 * float(np.mean(np.array(v) > 0))), "avg_R": round(float(np.mean(v)), 3)}
                  for k, v in sorted(rows.items())}
    return out


def choose_filter(train, test, min_n=12):
    """Try every single factor value and every pair on the training part; keep the one with the best average R
    (with at least min_n trades). Then report how that same filter did on the unseen test part."""
    filled = [t for t in train if t["result"] in ("win", "loss", "timed out")]
    if len(filled) < min_n:
        return None
    conds = sorted({(f, v) for t in filled for f, v in t["f"].items()})
    best = None
    def avg(ts, cs):
        r = [t["R"] for t in ts if all(t["f"][f] == v for f, v in cs)]
        return (np.mean(r) if len(r) >= min_n else None), len(r)
    for k1, a1 in enumerate(conds):
        for cs in [(a1,)] + [(a1, a2) for a2 in conds[k1 + 1:] if a2[0] != a1[0]]:
            m, n = avg(filled, cs)
            if m is not None and (best is None or m > best[0]):
                best = (m, n, cs)
    if best is None:
        return None
    tf = [t for t in test if t["result"] in ("win", "loss", "timed out") and all(t["f"][f] == v for f, v in best[2])]
    tr = np.array([t["R"] for t in tf])
    return {"filter": {f: v for f, v in best[2]}, "train_trades": best[1], "train_avg_R": round(float(best[0]), 3),
            "test_trades": len(tf), "test_avg_R": round(float(tr.mean()), 3) if len(tf) else None,
            "test_win_rate_pct": round(100 * float((tr > 0).mean())) if len(tf) else None}


def verdict(s, flt):
    if not s.get("filled"):
        return "No filled trades in the sample: nothing to judge yet."
    if s["filled"] < 30:
        v = f"Only {s['filled']} filled trades: too few to trust either way. Keep collecting history."
    elif s["avg_R"] > 0.1:
        v = f"Positive so far: {s['avg_R']:+.2f}R per trade after costs over {s['filled']} trades."
    elif s["avg_R"] > -0.05:
        v = f"About break-even after costs ({s['avg_R']:+.2f}R per trade over {s['filled']} trades): no proven edge yet."
    else:
        v = f"Losing after costs ({s['avg_R']:+.2f}R per trade over {s['filled']} trades): do not promote these alerts as an edge."
    if flt and flt.get("test_avg_R") is not None:
        held = flt["test_avg_R"] > 0 and flt["test_trades"] >= 8
        if flt["test_trades"] < 8:
            v += f" The best filter on older data ({flt['filter']}) has only {flt['test_trades']} trades in the newer data: too few to confirm."
        elif held:
            v += f" Best filter {flt['filter']} held up on unseen data ({flt['test_avg_R']:+.2f}R over {flt['test_trades']} trades)."
        else:
            v += f" The best filter on older data ({flt['filter']}) failed on newer data ({flt['test_avg_R']:+.2f}R over {flt['test_trades']} trades), so it was likely luck."
    return v


def main():
    df = to_ny(load_history())
    df = df[df["Volume"] >= 0]
    res = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "data": {"bars": len(df), "from": str(df.index[0]), "to": str(df.index[-1]), "symbol": "GC=F (COMEX gold futures)"},
           "settings": {"cost_points": COST, "latency_min": 5 * LAT, "order_valid_min": 5 * EXPIRE, "min_rr": MIN_RR,
                        "max_risk_atr_v2": MAX_RISK_ATR}, "rules": {}}
    split_t = df.index[int(len(df) * 0.7)]
    for rules in ("current", "v2"):
        ts = simulate(df, candidates(df, rules), rules)
        train = [t for t in ts if df.index[t["i"]] < split_t]
        test = [t for t in ts if df.index[t["i"]] >= split_t]
        s = stats(ts)
        flt = choose_filter(train, test)
        res["rules"][rules] = {"summary": s, "factors": factor_table(ts), "best_filter": flt, "verdict": verdict(s, flt),
                               "recent": [{"time": str(df.index[t["i"]]), "dir": t["dir"], "entry": round(t["entry"], 2),
                                           "stop": round(t["stop"], 2), "target": round(t["target"], 2), "rr": round(t["rr"], 2),
                                           "result": t["result"], "R": t["R"]} for t in ts[-25:]]}
        print(f"[{rules}] {s}")
        print("  ", res["rules"][rules]["verdict"])
    with open("backtest.json", "w") as f:
        json.dump(res, f, indent=2, default=str)


if __name__ == "__main__":
    main()
