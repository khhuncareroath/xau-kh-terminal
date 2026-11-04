"""Research models: retested every day by backtest.py on all saved history, so an idea is promoted only when the
data proves it. A model is "proven" when it has at least 30 trades, at least +0.10R per trade after costs,
a t-statistic of 2 or more (unlikely to be luck), a positive newest 30% of the data (never used to choose anything,
at least 10 trades), and positive results in at least 60% of quarters with 5+ trades.

Models:
  sweep_htf     liquidity sweep + structure shift on 5m, only WITH the 4H and Daily trend, entry at market when
                the alert arrives (15 min delay), stop beyond the sweep (at least 1 ATR), target 1.5R.
  value_80      "80% rule": open outside yesterday's value area, two 30m closes back inside, trade to the far edge.
  acceptance    two 30m closes beyond yesterday's value edge (after a real break), trade the continuation.
"""
import numpy as np
import pandas as pd

from engine import atr
from ict import order_block, resample, session_vwap, structure, swings
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


def _run_scaled(o, h, l, c, j0, j_end, sg, stop, tp1_r, tp2_r, part=0.5):
    """Scale-out exit: close `part` at TP1 (tp1_r x risk) and move the stop to the entry; the rest runs to TP2.
    Stop first when one candle touches both. Returns (R after costs, exit index, TP1 reached)."""
    en = o[j0]
    risk = (en - stop) * sg
    if risk <= 0.5:
        return None, j0, False
    lv = lambda r: en + sg * r * risk
    st, got, left, hit1 = stop, 0.0, 1.0, False
    for j in range(j0, j_end + 1):
        if (l[j] <= st) if sg > 0 else (h[j] >= st):
            px = st if (j == j0 or hit1) else (min(st, o[j]) if sg > 0 else max(st, o[j]))
            return got + left * (px - en) * sg / risk - COST / risk, j, hit1
        if not hit1 and ((h[j] >= lv(tp1_r)) if sg > 0 else (l[j] <= lv(tp1_r))):
            got, left, hit1, st = got + part * tp1_r, left - part, True, en
        if hit1 and ((h[j] >= lv(tp2_r)) if sg > 0 else (l[j] <= lv(tp2_r))):
            return got + left * tp2_r - COST / risk, j, hit1
    return got + left * (c[j_end] - en) * sg / risk - COST / risk, j_end, hit1


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
        if pr is None or len(idx) < 2 or pr["vah"] <= pr["val"]:   # (no "short day" filter: a day's length is not known in real time)
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


def _day_index(df):
    """Per trade-day (18:00 New York start) positions, with New York hour of each bar."""
    dates = trade_dates(df.index)
    pos = np.arange(len(df))
    return [(d, pos[dates == d]) for d in pd.unique(dates)], df.index.hour, df.index.minute


def session_breakouts(df):
    """London breakout of the Asia range (18:00-02:00 NY), and New York breakout of its 08:00-08:30 opening range.
    Entry: the 5m close outside the range, executed after the alert delay. Stop: the middle of the range
    (at least 1 ATR). Target: 1.5R. Out by the end of the session (London 05:00, New York 11:30)."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    days, hr, mi = _day_index(df)
    tmin = hr * 60 + mi
    out = {"london_breakout": [], "ny_breakout": []}
    for _, idx in days:
        if len(idx) < 50:
            continue
        t = tmin[idx]
        for name, rng_sel, win_lo, win_hi in (("london_breakout", (t >= 18 * 60) | (t < 120), 120, 300),
                                              ("ny_breakout", (t >= 480) & (t < 510), 510, 690)):
            r = idx[rng_sel]
            if len(r) < 4:
                continue
            top, bot = h[r].max(), l[r].min()
            mid = (top + bot) / 2
            win = idx[(t >= win_lo) & (t < win_hi)]
            if len(win) < 6:
                continue
            for i in win[:-LAT - 1]:
                sg = 1 if c[i] > top else -1 if c[i] < bot else 0
                if not sg:
                    continue
                j0 = i + 1 + LAT
                stop = mid if abs(o[j0] - mid) >= a[i] else o[j0] - sg * a[i]
                if (o[j0] - stop) * sg <= 0 or (o[j0] - stop) * sg > 4 * a[i]:
                    break
                tgt = o[j0] + sg * 1.5 * (o[j0] - stop) * sg
                rr, _ = _run_trade(o, h, l, c, j0, win[-1], sg, stop, tgt)
                if rr is not None:
                    out[name].append((df.index[j0], rr))
                break   # one breakout trade per session
    return out


def trend_pullback(df):
    """Daily and 4H structure agree; during London (02-05) or New York (07-11) price pulls back to session VWAP,
    then a 5m candle closes back in the trend direction. Stop 1.2 ATR beyond VWAP, target 2R, one trade per session."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    vw, _ = session_vwap(df)
    vw = vw.to_numpy()
    b4 = _bias(df, "4H", pd.Timedelta(hours=4))
    bD = _bias(df, "D", pd.Timedelta(hours=24))
    hr = df.index.hour
    sess = np.where((hr >= 2) & (hr < 5), 1, np.where((hr >= 7) & (hr < 11), 2, 0))
    dates = trade_dates(df.index)
    out, used, busy, n = [], set(), -1, len(df)
    for i in range(1, n - LAT - 2):
        if not sess[i] or i <= busy or b4[i] is None or b4[i] != bD[i] or (dates[i], sess[i]) in used:
            continue
        sg = 1 if b4[i] == "bull" else -1
        touched = (l[i - 1] <= vw[i - 1]) if sg > 0 else (h[i - 1] >= vw[i - 1])
        turned = (c[i] > vw[i] and c[i] > o[i]) if sg > 0 else (c[i] < vw[i] and c[i] < o[i])
        if not (touched and turned):
            continue
        j0 = i + 1 + LAT
        stop = vw[i] - sg * 1.2 * a[i]
        risk = (o[j0] - stop) * sg
        if risk <= 0.3 * a[i] or risk > 3 * a[i]:
            continue
        r, j = _run_trade(o, h, l, c, j0, min(j0 + 96, n - 1), sg, stop, o[j0] + sg * 2 * risk)
        if r is not None:
            out.append((df.index[j0], r))
            used.add((dates[i], sess[i]))
            busy = j
    return out


def vwap_fade(df):
    """Price closes beyond the 2-sigma VWAP band in London or New York, then the next candle closes back inside:
    fade toward VWAP. Stop 0.5 ATR beyond the extreme of the stretch; target VWAP (only if at least 1R away)."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    vw, sd = session_vwap(df)
    vw, sd = vw.to_numpy(), sd.to_numpy()
    hr = df.index.hour
    ok = ((hr >= 2) & (hr < 5)) | ((hr >= 7) & (hr < 11))
    out, busy, n = [], -1, len(df)
    for i in range(2, n - LAT - 2):
        if not ok[i] or i <= busy or not np.isfinite(sd[i]) or sd[i] <= 0:
            continue
        up, dn = vw[i - 1] + 2 * sd[i - 1], vw[i - 1] - 2 * sd[i - 1]
        sg = -1 if (c[i - 1] > up and c[i] < vw[i] + 2 * sd[i]) else 1 if (c[i - 1] < dn and c[i] > vw[i] - 2 * sd[i]) else 0
        if not sg:
            continue
        j0 = i + 1 + LAT
        ext = max(h[i - 1], h[i]) if sg < 0 else min(l[i - 1], l[i])
        stop = ext - sg * 0.5 * a[i]
        risk = (o[j0] - stop) * sg
        tgt = vw[i]
        if risk <= 0 or (tgt - o[j0]) * sg < risk:
            continue
        r, j = _run_trade(o, h, l, c, j0, min(j0 + 48, n - 1), sg, stop, tgt)
        if r is not None:
            out.append((df.index[j0], r))
            busy = j
    return out


def trend_breakout(df, buy_only=False, scaled=False, stop_pct=None, tp1=1.0, tp2=3.0):
    """Higher-timeframe trend following: a 4H candle closes above the highest high (or below the lowest low) of the
    previous 30 4H candles (about 1 week). Enter after the alert delay, stop 2 x the 4H ATR away, target 3R,
    out after 5 days at most. Gold trended strongly in 2024-26, so check the long and short results separately."""
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    d4 = resample(df, "4H")
    a4 = atr(d4).to_numpy()
    hi30 = d4["High"].rolling(30).max().shift(1).to_numpy()
    lo30 = d4["Low"].rolling(30).min().shift(1).to_numpy()
    c4 = d4["Close"].to_numpy()
    out, busy_t, n = [], None, len(df)
    for k in range(31, len(d4)):
        sg = 1 if c4[k] > hi30[k] else -1 if c4[k] < lo30[k] else 0
        if buy_only and sg < 0:
            sg = 0
        if not sg or not np.isfinite(a4[k]):
            continue
        t_close = d4.index[k] + pd.Timedelta(hours=4)
        if busy_t is not None and t_close <= busy_t:
            continue
        i = int(df.index.searchsorted(t_close)) - 1     # last 5m candle of that 4H candle
        j0 = i + 1 + LAT
        if j0 + 1 >= n:
            continue
        nr = df.attrs.get("n_real")   # live run (live_models.py pads flat candles after the last real one)
        if nr is not None and (i >= nr or j0 > nr):
            continue                  # the 4H candle has not really closed yet, or the alert delay has not passed
        stop = o[j0] - sg * 2 * a4[k] if stop_pct is None else o[j0] * (1 - sg * stop_pct)
        if scaled:   # half at 1R (stop moves to entry), rest to 3R
            r, j, _ = _run_scaled(o, h, l, c, j0, min(j0 + 5 * 288, n - 1), sg, stop, tp1, tp2)
        else:
            r, j = _run_trade(o, h, l, c, j0, min(j0 + 5 * 288, n - 1), sg, stop, o[j0] + sg * 3 * 2 * a4[k])
        if r is not None:
            out.append((df.index[j0], r, "long" if sg > 0 else "short"))
            busy_t = df.index[j]
    return out


def trend_tight(df):
    """Trend following with a tight stop (0.65% of price, about $25 at $3,900) on the same 4H breakouts, both
    directions: half closed at TP1 = 0.75R (stop moves to entry), rest to TP2 = 3R. On 2 years of spot gold:
    about 170 trades, 69% profitable, about +0.30R per trade (see backtest.json for the current numbers). The stop and
    TP1 were picked on the full sample; an independent walk-forward check found nearby settings (stop 0.55-1%, TP1
    0.5-1.5R) all positive, so it is not a fragile optimum. (TP1 at 1R gave 64% / +0.37R.)"""
    return trend_breakout(df, scaled=True, stop_pct=0.0065, tp1=0.75, tp2=3.0)


def breakout_cisd(df, window_h=12):
    """The member's entry (sweep -> CISD) combined with the proven direction: within 12 hours after a 4H close beyond the
    1-week range, in the London (02-05 NY) or New York (07-11 NY) window, a 5m sweep of a key level against the breakout
    direction followed by a CISD (close beyond the open of the candle run that delivered the sweep) -> market entry after the
    alert delay, stop 0.1 ATR beyond the sweep extreme, target 3R, out after 12 hours.
    Found as the best of about 130 combinations (43 trades, +0.65R, t=2.1), so it starts as research only."""
    from backtest import find_sweeps, level_pools, swing_pools
    o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(df).to_numpy()
    n = len(df)
    d4 = resample(df, "4H")
    hi30 = d4["High"].rolling(30).max().shift(1).to_numpy()
    lo30 = d4["Low"].rolling(30).min().shift(1).to_numpy()
    c4 = d4["Close"].to_numpy()
    brt, brs = [], []
    nr = df.attrs.get("n_real")
    last_real = df.index[nr - 1] if nr else None
    for k in range(31, len(d4)):
        sg = 1 if c4[k] > hi30[k] else -1 if c4[k] < lo30[k] else 0
        if sg and last_real is not None and d4.index[k] + pd.Timedelta(hours=4) > last_real + pd.Timedelta(minutes=5):
            continue                  # live: that 4H candle is still forming
        if sg:
            brt.append((d4.index[k] + pd.Timedelta(hours=4)).value)
            brs.append(sg)
    brt, brs = np.array(brt), np.array(brs)
    hr = df.index.hour
    kz = ((hr >= 2) & (hr < 5)) | ((hr >= 7) & (hr < 11))
    out, busy = [], -1
    for s in find_sweeps(df, a, level_pools(df) + swing_pools(df)):
        i_s = s["i"]
        sg = -1 if s["side"] == "buy-side" else 1
        k = i_s
        while k > 0 and ((c[k - 1] > o[k - 1]) if sg < 0 else (c[k - 1] < o[k - 1])) and i_s - k < 8:
            k -= 1
        cisd = (min(o[k:i_s + 1]) if sg < 0 else max(o[k:i_s + 1])) if i_s - k >= 1 else o[i_s]
        conf = None
        for j in range(i_s + 1, min(i_s + 13, n - 1)):
            if (c[j] - s["extreme"]) * sg < 0:
                break
            if (c[j] < cisd) if sg < 0 else (c[j] > cisd):
                conf = j
                break
        if conf is None or conf <= busy or not kz[conf]:
            continue
        t = df.index[conf].value
        m = (brt <= t) & (brt >= t - window_h * 3600e9)
        if not m.any() or brs[m][-1] != sg:
            continue
        j0 = conf + 1 + LAT
        if j0 + 1 >= n:
            continue
        stop = s["extreme"] - sg * 0.1 * a[conf]
        risk = (o[j0] - stop) * sg
        if risk <= 0.5 or risk > 4 * a[conf]:
            continue
        r, j = _run_trade(o, h, l, c, j0, min(j0 + 144, n - 1), sg, stop, o[j0] + sg * 3 * risk)
        if r is not None:
            out.append((df.index[j0], r, "long" if sg > 0 else "short"))
            busy = j
    return out


def trend_buy(df):
    """The alerted version of trend following: BUY signals only, half closed at 1R with the stop moved to entry,
    the rest held to 3R. Tested on its own so the proof covers exactly what members receive."""
    return trend_breakout(df, buy_only=True, scaled=True)


def judge(trades, split_t):
    r = np.array([x[1] for x in trades], dtype=float)
    te = np.array([x[1] for x in trades if x[0] >= split_t])
    tr = np.array([x[1] for x in trades if x[0] < split_t])
    f = lambda z: {"trades": len(z), "win_rate_pct": round(100 * float((z > 0).mean())) if len(z) else None,
                   "avg_R": round(float(z.mean()), 3) if len(z) else None}
    out = {"all": f(r), "older_70pct": f(tr), "newest_30pct": f(te)}
    # stability: results by quarter, and by direction (gold rose a lot in 2024-26, so longs can look good by luck)
    q = {}
    for t, v, *_ in trades:
        q.setdefault(f"{t.year}-Q{(t.month - 1) // 3 + 1}", []).append(v)
    out["quarters"] = {k: {"trades": len(v), "avg_R": round(float(np.mean(v)), 3)} for k, v in sorted(q.items())}
    side = {}
    for x in trades:
        if len(x) > 2:
            side.setdefault(x[2], []).append(x[1])
    if side:
        out["by_direction"] = {k: {"trades": len(v), "avg_R": round(float(np.mean(v)), 3)} for k, v in side.items()}
    qs = [v for v in out["quarters"].values() if v["trades"] >= 5]
    pos_q = sum(v["avg_R"] > 0 for v in qs)
    out["positive_quarters"] = f"{pos_q} of {len(qs)}"
    enough_q = len(qs) < 4 or pos_q >= 0.6 * len(qs)   # with under 4 quarters of data this check cannot apply yet
    tstat = float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))) if len(r) > 2 and r.std(ddof=1) > 0 else 0.0
    out["t_stat"] = round(tstat, 2)   # how many standard errors above zero; 2+ means unlikely to be luck alone
    out["proven"] = bool(len(r) >= 30 and r.mean() >= 0.10 and tstat >= 2 and len(te) >= 10 and te.mean() > 0 and enough_q)
    if out["proven"]:
        out["verdict"] = "Proven so far: positive overall, on the newest data and in most quarters. Eligible for trade alerts."
    elif len(r) < 30:
        out["verdict"] = f"Not enough trades yet ({len(r)} of 30 needed)."
    elif r.mean() < 0.10:
        out["verdict"] = f"No edge: {r.mean():+.2f}R per trade after costs."
    elif len(te) < 10:
        out["verdict"] = f"Positive so far, but only {len(te)} trades in the newest data (10 needed): waiting for more."
    elif te.mean() <= 0:
        out["verdict"] = "Positive overall but not on the newest data: probably luck so far."
    elif tstat < 2:
        out["verdict"] = f"Positive ({r.mean():+.2f}R) but not statistically clear yet (t={tstat:.1f}, need 2): could still be luck."
    else:
        out["verdict"] = f"Positive overall but only in {pos_q} of {len(qs)} quarters: not stable yet."
    return out


DESCRIBE = {"sweep_htf": "Sweep + structure shift, only with the 4H and Daily trend, market entry, 1.5R target",
            "value_80": "Volume profile 80% rule: back inside yesterday's value, target the far edge",
            "acceptance": "Volume profile acceptance: two 30m closes beyond yesterday's value, trade the continuation",
            "london_breakout": "London breakout of the Asia range, stop at the range middle, 1.5R target",
            "ny_breakout": "New York breakout of the 08:00-08:30 range, stop at the range middle, 1.5R target",
            "trend_pullback": "Daily and 4H trend agree, pullback to VWAP in London or New York, 2R target",
            "vwap_fade": "Fade a 2-sigma VWAP stretch in London or New York, target VWAP",
            "trend_breakout": "4H trend following: close beyond the 1-week high or low, stop 2 x 4H ATR, 3R target",
            "trend_buy": "4H trend following, BUY only: half profit at 1R with the stop moved to entry, rest to 3R",
            "trend_tight": "4H trend following with a tight 0.65% stop: half profit at 0.75R with the stop moved to entry, rest to 3R",
            "breakout_cisd": "After a 4H breakout: sweep + CISD entry in London/New York, stop beyond the sweep, 3R target"}
TREND_PREFERENCE = ["trend_tight", "trend_buy", "trend_breakout"]   # same breakouts: alert only the first proven one
# trend_buy is a child of trend_breakout (same breakouts). When both are proven, notify.py alerts only trend_buy.


MAX_HOLD_H = {"breakout_cisd": 12, "trend_breakout": 120, "trend_buy": 120, "trend_tight": 120, "trend_pullback": 8, "vwap_fade": 4, "sweep_htf": 12}   # others: until the session/day ends (<= 24h)


def run_all(df, cands_fn, split_t):
    models = {"sweep_htf": sweep_htf(df, cands_fn), **value_models(df), **session_breakouts(df),
              "trend_pullback": trend_pullback(df), "vwap_fade": vwap_fade(df), "trend_breakout": trend_breakout(df),
              "trend_buy": trend_buy(df), "trend_tight": trend_tight(df), "breakout_cisd": breakout_cisd(df)}
    return {k: {"description": DESCRIBE[k], **judge(v, split_t)} for k, v in models.items()}
