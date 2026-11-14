"""ANAJAK lessons (RANGES, MARKET STRUCTURE, BOOTCAMP PDFs) turned into exact rules and tested like everything else.
Written down BEFORE running. Same data, costs (0.12% + funding), 15-min delay and judge as studies/crypto_rules.py.
Their checklist asks for reward:risk of at least 1:2, so every trade must have 2R of room to its final target.

  dev_4h        RANGE DEVIATION: range = high/low of the last 30 closed 4H candles. A 4H candle sweeps the range high
                (trades above it) and CLOSES back inside -> short. SL above the sweep high + 0.1 x 4H ATR. Half off at the
                range middle (eQ, stop to entry), rest at the other edge. Max 5 days. Mirror for the low.
  dev_4h_oi     same, only when open interest did NOT rise during the sweep candle (their "fakeout: OI does not keep
                rising"; OI history starts Dec 2021)
  dev_1d        same idea on daily candles: range = last 20 closed days, the day sweeps and closes back inside, max 10 days
  monday_dev    MONDAY RANGE: Monday (UTC) high/low/mid. Tue-Sun, a 4H candle sweeps Monday's high (low) and closes back
                inside -> short (long), SL beyond the sweep + 0.1 ATR, half at the Monday mid, rest at the other side,
                out by Sunday's close. One trade per side per week.
  brk_confirmed CLEAN BREAKOUT (their "volume up, delta up, OI up"): the swing breakout (4H close beyond 30 candles,
                clean trend) only when the breakout candle's volume > its 20-candle average, delta is the breakout's way
                and OI rose during the candle. Held like the swing (SL 2 ATR, TP 3R, 5 days).
  brk_unconfirmed  the same breakouts without all three confirmations (the comparison)
Run: python studies/crypto_anajak.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crypto_rules as cr  # noqa: E402
from engine import atr  # noqa: E402


def oi_change(x, t0, t1):
    if x.oi is None:
        return None
    s = x.oi["sum_open_interest"]
    a = s.index.searchsorted(t0); b = s.index.searchsorted(t1) - 1
    if a >= len(s) or b < 0 or b <= a or s.index[a] - t0 > pd.Timedelta(minutes=30):
        return None
    return float(s.iloc[b] / s.iloc[a] - 1)


def deviation(x, bars, lookback, hold_days, oi_filter=False, mid_part=0.5):
    """Generic range deviation on candles `bars` (4H or 1D) of x.df."""
    H, L, C = (bars[k].to_numpy() for k in ("High", "Low", "Close"))
    A = atr(bars).to_numpy()
    step = bars.index[1] - bars.index[0]
    out, busy = [], -1
    for k in range(lookback + 1, len(bars)):
        hi = H[k - lookback:k].max(); lo = L[k - lookback:k].min()
        for sg, swept, back in ((-1, H[k] > hi, C[k] < hi), (1, L[k] < lo, C[k] > lo)):
            if not (swept and back) or not np.isfinite(A[k]):
                continue
            t_close = bars.index[k] + step
            if oi_filter:
                ch = oi_change(x, bars.index[k], t_close)
                if ch is None or ch > 0:
                    continue
            i = int(x.ix.searchsorted(t_close)) - 1
            j0 = i + 1 + cr.LAT
            if j0 + 2 >= x.n or j0 <= busy:
                continue
            en = x.o[j0]
            stop = (H[k] + 0.1 * A[k]) if sg < 0 else (L[k] - 0.1 * A[k])
            risk = (en - stop) * sg
            far = lo if sg < 0 else hi
            mid = (hi + lo) / 2
            if risk <= 0 or (far - en) * sg < 2 * risk or (mid - en) * sg <= 0:
                continue
            r, j = run_two(x, j0, min(j0 + hold_days * 288, x.n - 1), sg, stop, mid, far, mid_part)
            if r is not None:
                out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
                busy = j
    return out


def run_two(x, j0, j_end, sg, stop, t1, t2, part=0.5):
    """Half at t1 (stop to entry), rest at t2. Stop first when one candle touches both."""
    o, h, l, c = x.o, x.h, x.l, x.c
    en = o[j0]; risk = (en - stop) * sg
    st, got, left, hit1 = stop, 0.0, 1.0, False
    for j in range(j0, j_end + 1):
        if (l[j] <= st) if sg > 0 else (h[j] >= st):
            px = st if (j == j0 or hit1) else (min(st, o[j]) if sg > 0 else max(st, o[j]))
            return got + left * (px - en) * sg / risk - x._cost(j0, j, sg, risk), j
        if not hit1 and ((h[j] >= t1) if sg > 0 else (l[j] <= t1)):
            got, left, hit1, st = got + part * (t1 - en) * sg / risk, left - part, True, en
        if hit1 and ((h[j] >= t2) if sg > 0 else (l[j] <= t2)):
            return got + left * (t2 - en) * sg / risk - x._cost(j0, j, sg, risk), j
    return got + left * (c[j_end] - en) * sg / risk - x._cost(j0, j_end, sg, risk), j_end


def monday_dev(x):
    d4 = x.d4
    H, L, C = (d4[k].to_numpy() for k in ("High", "Low", "Close"))
    A = x.a4
    day = d4.index.floor("D")
    out, busy, done = [], -1, set()
    mon = {}
    for t, h_, l_ in zip(day, H, L):
        if t.weekday() == 0:
            m = mon.setdefault(t, [h_, l_]); m[0] = max(m[0], h_); m[1] = min(m[1], l_)
    for k in range(len(d4)):
        t = day[k]
        if t.weekday() == 0:
            continue
        monday = t - pd.Timedelta(days=t.weekday())
        if monday not in mon or not np.isfinite(A[k]):
            continue
        hi, lo = mon[monday]; mid = (hi + lo) / 2
        week_end = monday + pd.Timedelta(days=7)
        for sg, swept, back in ((-1, H[k] > hi, C[k] < hi), (1, L[k] < lo, C[k] > lo)):
            if not (swept and back) or (monday, sg) in done:
                continue
            i = int(x.ix.searchsorted(d4.index[k] + pd.Timedelta(hours=4))) - 1
            j0 = i + 1 + cr.LAT
            j_end = min(int(x.ix.searchsorted(week_end)) - 1, x.n - 1)
            if j0 + 2 >= x.n or j0 <= busy or j0 >= j_end:
                continue
            en = x.o[j0]
            stop = (H[k] + 0.1 * A[k]) if sg < 0 else (L[k] - 0.1 * A[k])
            risk = (en - stop) * sg
            far = lo if sg < 0 else hi
            if risk <= 0 or (far - en) * sg < 2 * risk or (mid - en) * sg <= 0:
                continue
            done.add((monday, sg))
            r, j = run_two(x, j0, j_end, sg, stop, mid, far)
            if r is not None:
                out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
                busy = j
    return out


def confirmed_breakouts(x, bks, want):
    d4 = x.d4
    v = d4["Volume"].to_numpy()
    vavg = d4["Volume"].rolling(20).mean().shift(1).to_numpy()
    out, busy = [], -1
    for b in bks:
        if b["er"] <= 0.30 or b["j0"] <= busy:
            continue
        k = b["k"]
        ch = oi_change(x, d4.index[k], d4.index[k] + pd.Timedelta(hours=4))
        if ch is None:
            continue                       # only where OI history exists, so both groups cover the same years
        conf = v[k] > vavg[k] and b["delta"] > 0 and ch > 0
        if conf != want:
            continue
        j0, sg = b["j0"], b["sg"]
        stop = x.o[j0] - sg * 2 * b["a4"]
        r, j = x.run_trade(j0, min(j0 + 5 * 288, x.n - 1), sg, stop, x.o[j0] + sg * 6 * b["a4"])
        if r is not None:
            out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
            busy = j
    return out


def study(sym):
    df, fu, oi = cr.load(sym)
    x = cr.Ctx(df, fu, oi)
    split = df.index[0] + 0.7 * (df.index[-1] - df.index[0])
    split_oi = oi.index[0] + 0.7 * (oi.index[-1] - oi.index[0]) if oi is not None else split
    d1 = cr.rs(df, "1D")
    bks = cr.breakouts(x)
    tests = {
        "dev_4h (range deviation, 30 x 4H)": (lambda: deviation(x, x.d4, 30, 5), split),
        "dev_4h_oi (+ OI did not rise)": (lambda: deviation(x, x.d4, 30, 5, oi_filter=True), split_oi),
        "dev_1d (range deviation, 20 days)": (lambda: deviation(x, d1, 20, 10), split),
        "monday_dev (Monday range deviation)": (lambda: monday_dev(x), split),
        "brk_confirmed (volume + delta + OI up)": (lambda: confirmed_breakouts(x, bks, True), split_oi),
        "brk_unconfirmed (same years, not all 3)": (lambda: confirmed_breakouts(x, bks, False), split_oi),
    }
    res = {"symbol": sym, "from": str(df.index[0]), "to": str(df.index[-1]), "split": str(split), "tests": {}}
    for name, (fn, sp) in tests.items():
        tr = fn()
        j = cr.judge(tr, sp) if tr else {"all": {"trades": 0}, "proven": False}
        months = max(1.0, ((df.index[-1] - (oi.index[0] if "OI" in name or "brk" in name else df.index[0])).days) / 30.4)
        j["per_month"] = round(len(tr) / months, 2)
        j["total_R"] = round(float(sum(r for _, r, *_ in tr)), 1)
        j["per_year"] = cr.per_year(tr)
        res["tests"][name] = j
        a = j["all"]
        print(f"{sym:8s} {name:42s} n={a.get('trades', 0):4d} win={a.get('win_rate_pct')} avg={a.get('avg_R')} "
              f"old={j.get('older_70pct', {}).get('avg_R')} new={j.get('newest_30pct', {}).get('avg_R')} "
              f"t={j.get('t_stat')} proven={j['proven']}", flush=True)
    return res


if __name__ == "__main__":
    allr = [study(s) for s in (sys.argv[1:] or ["BTCUSDT", "ETHUSDT"])]
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(allr, open(os.path.join(here, "crypto_anajak.json"), "w"), indent=1, default=str)
    md = cr.markdown(allr).replace("# Crypto test results (generated by studies/crypto_rules.py)",
                                   "# ANAJAK lesson rules on crypto (generated by studies/crypto_anajak.py)")
    open(os.path.join(here, "CRYPTO_ANAJAK.md"), "w").write(md)
