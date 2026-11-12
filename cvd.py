"""CVD divergence: our own build of the "exhaustion / absorption" idea (owner, 12 Nov 2026).

Separate module: it never decides a signal. The bot only asks "does CVD agree with this signal, is it against, or is
there nothing?" and the answer is used only if studies/cvd_confirm.py proves it helps (see studies/RESULTS.md).

How it works (written from the public description of the idea, not from anyone's code):
1. Delta per small candle: its volume counts as BUYING when it closes up and SELLING when it closes down (if flat: the
   same side as the previous candle). Live volume = COMEX futures (engine.py), history = Dukascopy spot volume.
2. CVD = running total of delta, reset at the start of each anchor period (default: the trading week, New York time).
3. Swing highs / lows on the chart timeframe: LEFT candles before and RIGHT candles after (confirmed RIGHT candles later,
   closed candles only, so nothing repaints).
4. Each new swing is compared with the last few swings of the same kind in the same anchor period (never across a reset),
   skipping a pair if a more extreme swing sits between them. CVD at a swing = its extreme within 1 candle either side.
5. Four labels:
     price lower low,  CVD higher low   -> EXH bull (selling exhaustion: look for buys)
     price higher low, CVD lower low    -> ABS bull (selling absorbed: look for buys)
     price higher high, CVD lower high  -> EXH bear (buying exhaustion: look for sells)
     price lower high, CVD higher high  -> ABS bear (buying absorbed: look for sells)
   Filters: price difference >= MIN_PX x ATR, CVD difference >= MIN_CVD x the anchor period's CVD range so far,
   price swing between the two points >= MIN_SWING x ATR.
"""
import numpy as np
import pandas as pd

LEFT, RIGHT = 5, 2
MIN_BARS, MAX_BARS, LOOKBACK = 5, 100, 4
MIN_PX, MIN_CVD, MIN_SWING = 0.1, 0.05, 0.5
AGG = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}


def delta(df):
    """Signed volume per candle: + when it closed up, - when down, flat candles keep the previous side."""
    side = np.sign(df["Close"] - df["Open"]).replace(0, np.nan).ffill().fillna(0)
    return side * df["Volume"]


def anchor_key(idx, anchor="W"):
    """Anchor period of each timestamp (New York time; the gold week opens Sunday 18:00 NY)."""
    ny = idx.tz_convert("America/New_York") + pd.Timedelta(hours=6)   # 18:00 NY -> 00:00 of the next day
    if anchor == "D":
        return ny.normalize()
    return (ny - pd.to_timedelta(ny.weekday, unit="D")).normalize()


def cvd_candles(df_small, rule="15min", anchor="W"):
    """Price candles on `rule` plus CVD open / high / low / close built from the small candles."""
    d = delta(df_small)
    key = anchor_key(df_small.index, anchor)
    cum = d.groupby(key).cumsum()
    start = cum - d                                    # CVD before each small candle
    g = pd.DataFrame({"co": start, "ch": np.maximum(cum, start), "cl": np.minimum(cum, start), "cc": cum,
                      "key": key}, index=df_small.index)
    px = df_small.resample(rule).agg(AGG).dropna()
    cv = g.resample(rule).agg({"co": "first", "ch": "max", "cl": "min", "cc": "last", "key": "first"}).dropna()
    out = px.join(cv, how="inner")
    return out


def _atr(d, n=14):
    pc = d["Close"].shift()
    tr = pd.concat([d["High"] - d["Low"], (d["High"] - pc).abs(), (d["Low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def divergences(d, left=LEFT, right=RIGHT, min_px=MIN_PX, min_cvd=MIN_CVD, min_swing=MIN_SWING):
    """All divergence events on candles from cvd_candles(). Each event is known at `t` (close of the confirming candle)."""
    h, l = d["High"].to_numpy(), d["Low"].to_numpy()
    ch, cl = d["ch"].to_numpy(), d["cl"].to_numpy()
    key = d["key"].to_numpy()
    a = _atr(d).to_numpy()
    idx = d.index
    span = idx[1] - idx[0] if len(idx) > 1 else pd.Timedelta(minutes=15)
    # CVD range of the anchor period so far (for the strength filter)
    rng = (d.groupby("key")["ch"].cummax() - d.groupby("key")["cl"].cummin()).to_numpy()
    highs, lows, ev = [], [], []
    n = len(d)
    for i in range(left, n - right):
        c = i + right                                  # confirmed at the close of candle c
        if not np.isfinite(a[c]):
            continue
        for kind, arr, carr, pivots in (("high", h, ch, highs), ("low", l, cl, lows)):
            win = arr[i - left:i + right + 1]
            is_piv = arr[i] == (win.max() if kind == "high" else win.min())
            if not is_piv:
                continue
            lo_, hi_ = max(0, i - 1), min(n, i + 2)
            cv = carr[lo_:hi_].max() if kind == "high" else carr[lo_:hi_].min()
            new = (i, arr[i], cv, key[i])
            for p in reversed(pivots[-LOOKBACK:]):
                j, pp, pc, pk = p
                if pk != key[i] or not (MIN_BARS <= i - j <= MAX_BARS):
                    continue
                between = arr[j + 1:i]
                if len(between) and ((kind == "high" and between.max() > max(pp, arr[i])) or
                                     (kind == "low" and between.min() < min(pp, arr[i]))):
                    continue                           # a bigger swing in between: do not jump over it
                swing = (pp - l[j:i + 1].min()) if kind == "high" else (h[j:i + 1].max() - pp)
                if swing < min_swing * a[c]:
                    continue
                dpx, dcv = arr[i] - pp, cv - pc
                if abs(dpx) < min_px * a[c] or abs(dcv) < min_cvd * max(rng[c], 1e-9):
                    continue
                lab = None
                if kind == "high":
                    if dpx > 0 and dcv < 0: lab = ("EXH", "bear")
                    elif dpx < 0 and dcv > 0: lab = ("ABS", "bear")
                else:
                    if dpx < 0 and dcv > 0: lab = ("EXH", "bull")
                    elif dpx > 0 and dcv < 0: lab = ("ABS", "bull")
                if lab:
                    ev.append({"t": idx[c] + span, "pivot_t": idx[i], "kind": lab[0], "dir": lab[1],
                               "price": float(arr[i]), "from_t": idx[j], "from_price": float(pp)})
                    break                              # one signal per new pivot
            pivots.append(new)
    return ev


def events(df_small, rule="15min", anchor="W", **kw):
    return divergences(cvd_candles(df_small, rule, anchor), **kw)


def check(df_small, direction, now=None, hours=4, rule="15min"):
    """What CVD says about a signal in `direction` ("bull"/"bear"): "agree", "against", "both" or None."""
    now = now or df_small.index[-1]
    ev = [e for e in events(df_small.loc[now - pd.Timedelta(days=8):now], rule)
          if now - pd.Timedelta(hours=hours) <= e["t"] <= now]
    same = any(e["dir"] == direction for e in ev)
    opp = any(e["dir"] != direction for e in ev)
    return "both" if same and opp else "agree" if same else "against" if opp else None
