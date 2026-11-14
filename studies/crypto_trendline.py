"""Trendlines (ANAJAK's main chart tool: "BTC hit our rising trendline support", "broke below the trendline").
Written down BEFORE running. Same data, costs (0.12% + funding), 15-min delay and judge as studies/crypto_rules.py.

Automatic trendline, no hindsight: on closed candles, the last two CONFIRMED swing lows (a low with n candles on each
side higher; known only n candles later) that rise make a support line; the last two confirmed swing highs that fall
make a resistance line. The line counts only while no candle has closed beyond it since its second point.
  tl_bounce   candle's low touches the support line (within 0.1 ATR) and closes above it -> buy. SL below the line by
              0.5 ATR (or below the candle low if lower). TP 3R, max 5 days (4H) / 10 days (1D). Mirror for resistance.
  tl_break    first close beyond the line -> trade the break. SL on the other side of the line by 0.5 ATR, TP 3R.
Pivots: n = 5 on 4H, n = 3 on daily. Run: python studies/crypto_trendline.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crypto_rules as cr  # noqa: E402
from engine import atr  # noqa: E402


def lines(bars, n):
    """For every closed candle k: (support value or nan, resistance value or nan), using pivots known before k."""
    H, L, C = (bars[k].to_numpy() for k in ("High", "Low", "Close"))
    m = len(bars)
    sup, res = np.full(m, np.nan), np.full(m, np.nan)
    lows, highs = [], []
    for k in range(m):
        p = k - n                               # pivot p is confirmed when candle k closes
        if p >= n:
            if L[p] == L[p - n:k + 1].min():
                lows.append(p)
            if H[p] == H[p - n:k + 1].max():
                highs.append(p)
        if len(lows) >= 2:
            i1, i2 = lows[-2], lows[-1]
            if L[i2] > L[i1]:
                f = lambda j: L[i1] + (L[i2] - L[i1]) * (j - i1) / (i2 - i1)  # noqa: E731
                if all(C[j] >= f(j) for j in range(i2, k)):
                    sup[k] = f(k)
        if len(highs) >= 2:
            i1, i2 = highs[-2], highs[-1]
            if H[i2] < H[i1]:
                g = lambda j: H[i1] + (H[i2] - H[i1]) * (j - i1) / (i2 - i1)  # noqa: E731
                if all(C[j] <= g(j) for j in range(i2, k)):
                    res[k] = g(k)
    return sup, res


def trendline(x, bars, n, hold_days, mode):
    H, L, C = (bars[k].to_numpy() for k in ("High", "Low", "Close"))
    A = atr(bars).to_numpy()
    sup, res = lines(bars, n)
    step = bars.index[1] - bars.index[0]
    out, busy = [], -1
    for k in range(len(bars)):
        if not np.isfinite(A[k]):
            continue
        sigs = []
        if np.isfinite(sup[k]):
            s = sup[k]
            if mode == "bounce" and L[k] <= s + 0.1 * A[k] and C[k] > s:
                sigs.append((1, min(s - 0.5 * A[k], L[k] - 0.1 * A[k])))
            if mode == "break" and C[k] < s:
                sigs.append((-1, s + 0.5 * A[k]))
        if np.isfinite(res[k]):
            r = res[k]
            if mode == "bounce" and H[k] >= r - 0.1 * A[k] and C[k] < r:
                sigs.append((-1, max(r + 0.5 * A[k], H[k] + 0.1 * A[k])))
            if mode == "break" and C[k] > r:
                sigs.append((1, r - 0.5 * A[k]))
        for sg, stop in sigs[:1]:
            i = int(x.ix.searchsorted(bars.index[k] + step)) - 1
            j0 = i + 1 + cr.LAT
            if j0 + 2 >= x.n or j0 <= busy:
                continue
            risk = (x.o[j0] - stop) * sg
            if risk <= 0:
                continue
            rr, j = x.run_trade(j0, min(j0 + hold_days * 288, x.n - 1), sg, stop, x.o[j0] + sg * 3 * risk)
            if rr is not None:
                out.append((x.ix[j0], rr, "long" if sg > 0 else "short"))
                busy = j
    return out


def study(sym):
    df, fu, oi = cr.load(sym)
    x = cr.Ctx(df, fu, oi)
    split = df.index[0] + 0.7 * (df.index[-1] - df.index[0])
    d1 = cr.rs(df, "1D")
    tests = {"tl_bounce 4H": lambda: trendline(x, x.d4, 5, 5, "bounce"),
             "tl_break 4H": lambda: trendline(x, x.d4, 5, 5, "break"),
             "tl_bounce 1D": lambda: trendline(x, d1, 3, 10, "bounce"),
             "tl_break 1D": lambda: trendline(x, d1, 3, 10, "break")}
    res = {"symbol": sym, "from": str(df.index[0]), "to": str(df.index[-1]), "split": str(split), "tests": {}}
    months = max(1.0, (df.index[-1] - df.index[0]).days / 30.4)
    for name, fn in tests.items():
        tr = fn()
        j = cr.judge(tr, split) if tr else {"all": {"trades": 0}, "proven": False}
        j["per_month"] = round(len(tr) / months, 2)
        j["total_R"] = round(float(sum(r for _, r, *_ in tr)), 1)
        j["per_year"] = cr.per_year(tr)
        res["tests"][name] = j
        a = j["all"]
        print(f"{sym:8s} {name:14s} n={a.get('trades', 0):4d} win={a.get('win_rate_pct')} avg={a.get('avg_R')} "
              f"old={j.get('older_70pct', {}).get('avg_R')} new={j.get('newest_30pct', {}).get('avg_R')} "
              f"t={j.get('t_stat')} proven={j['proven']}", flush=True)
    return res


if __name__ == "__main__":
    allr = [study(s) for s in (sys.argv[1:] or ["BTCUSDT", "ETHUSDT"])]
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(allr, open(os.path.join(here, "crypto_trendline.json"), "w"), indent=1, default=str)
    open(os.path.join(here, "CRYPTO_TRENDLINE.md"), "w").write(
        cr.markdown(allr).replace("# Crypto test results (generated by studies/crypto_rules.py)",
                                  "# Trendlines on crypto (generated by studies/crypto_trendline.py)"))
