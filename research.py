"""Research models: retested every day by backtest.py on all saved history, so an idea is promoted only when the
data proves it. A model is "proven" when it has at least 30 trades, at least +0.10R per trade after costs,
and the newest 30% of the data (never used to choose anything) is also positive with at least 10 trades.

Models:
  sweep_htf     liquidity sweep + structure shift on 5m, only WITH the 4H and Daily trend, entry at market when
                the alert arrives (15 min delay), stop beyond the sweep (at least 1 ATR), target 1.5R.
  value_80      "80% rule": open outside yesterday's value area, two 30m closes back inside, trade to the far edge.
  acceptance    two 30m closes beyond yesterday's value edge (after a real break), trade the continuation.
"""
import numpy as np
import pandas as pd

from engine import atr
from ict import order_block, resample, structure, swings
from levels import profile, trade_dates

COST, LAT = 0.4, 3


def _bias(df5, tf, delta):
    d = resample(df5, tf)
    ev = structure(d, atr(d).to_numpy(), swings(d))
    out = np.array([None] * len(df5), dtype=object)
    for e in ev:
        k = int(df5.index.searchsorted(d.index[e["i"]] + delta))
        if k < len(df5):
            out[k:] = e["dir"]
    return out


def _run_trade(o, h, l, c, j0, j_end, sg, stop, tgt):
    en = o[j0]
    risk = (en - stop) * sg
    if risk <= 0.5:
        return None, j0
    for j in range(j0, j_end + 1):
        if (l[j] <= stop) if sg > 0 else (h[j] >= stop):
            px = stop if j == j0 else (min(stop, o[j]) if sg > 0 else max(stop, o[j]))
            return (px - en) * sg / risk - COST / risk, j
        if (h[j] >= tgt) if sg > 0 else (l[j] <= tgt):
            return (tgt - en) * sg / risk - COST / risk, j
    return (c[j_end] - en) * sg / risk - COST / risk, j_end


def sweep_htf(df, cands_fn):
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    b4 = _bias(df, "4H", pd.Timedelta(hours=4))
    bD = _bias(df, "D", pd.Timedelta(hours=24))
    out, busy, n = [], -1, len(df)
    for x in cands_fn(df, "current"):
        i, sg, d = x["i"], x["sgn"], x["dir"]
        if i <= busy or b4[i] != d or bD[i] != d:
            continue
        j0 = i + 1 + LAT
        if j0 + 1 >= n or ((c[i + 1:j0] - x["extreme"]) * sg < 0).any():
            continue
        stop = x["stop"]
        if (o[j0] - stop) * sg < a[i]:
            stop = o[j0] - sg * a[i]
        if (o[j0] - stop) * sg > 3 * a[i]:
            continue
        tgt = o[j0] + sg * 1.5 * (o[j0] - stop) * sg
        r, j = _run_trade(o, h, l, c, j0, min(j0 + 144, n - 1), sg, stop, tgt)
        if r is not None:
            out.append((df.index[j0], r))
            busy = j
    return out


def value_models(df):
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a5 = atr(df).to_numpy()
    dates = trade_dates(df.index)
    days = list(pd.unique(dates))
    pos = np.arange(len(df))
    res = {"value_80": [], "acceptance": []}
    for k in range(1, len(days)):
        pr = profile(df[dates == days[k - 1]])
        idx = pos[dates == days[k]]
        if pr is None or len(idx) < 30 or pr["vah"] <= pr["val"]:
            continue
        vah, val, width, end = pr["vah"], pr["val"], pr["vah"] - pr["val"], idx[-1]
        c30 = df["Close"].iloc[idx].resample("30min").last().dropna()
        open_px = o[idx[0]]
        if open_px > vah or open_px < val:
            ins = (c30 >= val) & (c30 <= vah)
            for m in range(1, len(c30)):
                if ins.iloc[m] and ins.iloc[m - 1]:
                    j0 = int(df.index.searchsorted(c30.index[m] + pd.Timedelta(minutes=30))) + LAT
                    if j0 < end:
                        sg = -1 if open_px > vah else 1
                        r, _ = _run_trade(o, h, l, c, j0, end, sg, (vah + a5[j0]) if sg < 0 else (val - a5[j0]), val if sg < 0 else vah)
                        if r is not None:
                            res["value_80"].append((df.index[j0], r))
                    break
        for m in range(1, len(c30)):
            up = c30.iloc[m] > vah and c30.iloc[m - 1] > vah
            dn = c30.iloc[m] < val and c30.iloc[m - 1] < val
            if (up or dn) and not (open_px > vah and up) and not (open_px < val and dn):
                j0 = int(df.index.searchsorted(c30.index[m] + pd.Timedelta(minutes=30))) + LAT
                if j0 < end:
                    sg = 1 if up else -1
                    edge = vah if up else val
                    r, _ = _run_trade(o, h, l, c, j0, end, sg, edge - sg * a5[j0], edge + sg * width)
                    if r is not None:
                        res["acceptance"].append((df.index[j0], r))
                break
    return res


def judge(trades, split_t):
    r = np.array([x[1] for x in trades])
    te = np.array([x[1] for x in trades if x[0] >= split_t])
    tr = np.array([x[1] for x in trades if x[0] < split_t])
    f = lambda z: {"trades": len(z), "win_rate_pct": round(100 * float((z > 0).mean())) if len(z) else None,
                   "avg_R": round(float(z.mean()), 3) if len(z) else None}
    out = {"all": f(r), "older_70pct": f(tr), "newest_30pct": f(te)}
    out["proven"] = bool(len(r) >= 30 and r.mean() >= 0.10 and len(te) >= 10 and te.mean() > 0)
    if out["proven"]:
        out["verdict"] = "Proven so far: positive overall and on the newest data. Eligible for trade alerts."
    elif len(r) < 30:
        out["verdict"] = f"Not enough trades yet ({len(r)} of 30 needed)."
    elif r.mean() < 0.10:
        out["verdict"] = f"No edge: {r.mean():+.2f}R per trade after costs."
    else:
        out["verdict"] = "Positive overall but not on the newest data: probably luck so far."
    return out


DESCRIBE = {"sweep_htf": "Sweep + structure shift, only with the 4H and Daily trend, market entry, 1.5R target",
            "value_80": "Volume profile 80% rule: back inside yesterday's value, target the far edge",
            "acceptance": "Volume profile acceptance: two 30m closes beyond yesterday's value, trade the continuation"}


def run_all(df, cands_fn, split_t):
    models = {"sweep_htf": sweep_htf(df, cands_fn), **value_models(df)}
    return {k: {"description": DESCRIBE[k], **judge(v, split_t)} for k, v in models.items()}
