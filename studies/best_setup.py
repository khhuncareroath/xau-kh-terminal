"""Best setup study (11 Nov 2026, owner: "combine everything, find the best setup, split into A+ and B+").

Every 4H breakout traded the live way (SL 0.55%, half at 1R + stop to entry, rest 3R, closed within 12 h), with every
ingredient tested so far attached as a feature. Rules are chosen on the OLDER 70% only, then checked on the NEWEST 30%.
Run:  python studies/best_setup.py  (needs the 2-year spot CSV at /home/claude/spot/xau_5m.csv.gz, from the spot-data branch)
"""
import itertools
import sys

sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd

import research as R
from engine import atr
from ict import resample
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
d4 = resample(df, "4H")
c4, h4, l4, o4 = d4["Close"], d4["High"], d4["Low"], d4["Open"]
a4 = atr(d4)
dd = resample(df, "D")
ema20d = dd["Close"].ewm(span=20).mean()
d1 = resample(df, "1H")
ema50h = d1["Close"].ewm(span=50).mean()


def k4(t):
    return max(0, min(int(d4.index.searchsorted(t - pd.Timedelta(hours=4, minutes=20))), len(d4) - 1))


trades = R.trend_intraday(df)
rows = []
for t, r, side in trades:
    k = k4(t)
    sg = 1 if side == "long" else -1
    rng = h4.iloc[k] - l4.iloc[k]
    hi30 = h4.iloc[k - 30:k].max(); lo30 = l4.iloc[k - 30:k].min()
    kd = max(0, int(dd.index.searchsorted(t)) - 1)          # yesterday's daily candle (closed)
    kh = max(0, int(d1.index.searchsorted(t)) - 1)
    # how many breakouts the same way in the last 5 days (first breakout vs late continuation)
    prev = [x for x in trades if t - pd.Timedelta(days=5) <= x[0] < t and x[2] == side]
    rows.append(dict(
        t=t, r=r, side=side, old=t < split,
        meter=R.day_used(df, t) or 0,
        er=R.efficiency(df, t) or 0,
        body=abs(c4.iloc[k] - o4.iloc[k]) / rng if rng > 0 else 0,                  # breakout candle body / range
        closeloc=((c4.iloc[k] - l4.iloc[k]) / rng if sg > 0 else (h4.iloc[k] - c4.iloc[k]) / rng) if rng > 0 else 0,
        beyond=(c4.iloc[k] - hi30) / a4.iloc[k] if sg > 0 else (lo30 - c4.iloc[k]) / a4.iloc[k],  # stretch past the level, ATRs
        candle_atr=rng / a4.iloc[k],                                                  # size of the breakout candle
        atr_reg=a4.iloc[k] / a4.iloc[max(0, k - 120):k].median(),                     # volatility vs last ~3 weeks
        daily_ema=sg * np.sign(dd["Close"].iloc[kd] - ema20d.iloc[kd]),               # +1 = with the daily EMA20
        h1_ema=sg * np.sign(d1["Close"].iloc[kh] - ema50h.iloc[kh]),
        hour=t.hour,
        dow=t.dayofweek,
        repeat=len(prev),
    ))
X = pd.DataFrame(rows)
X.to_csv("/home/claude/best_setup_features.csv", index=False)
old, new = X[X.old], X[~X.old]


def stat(s):
    r = s.r.to_numpy()
    if len(r) < 3:
        return dict(n=len(r), win=np.nan, R=np.nan, t=np.nan)
    return dict(n=len(r), win=round(100 * (r > 0).mean()), R=round(r.mean(), 3), t=round(r.mean() / r.std(ddof=1) * np.sqrt(len(r)), 2))


print("ALL breakouts", stat(X), "older", stat(old), "newest", stat(new))

# 1) one ingredient at a time: thirds on the older data
feats = ["meter", "er", "body", "closeloc", "beyond", "candle_atr", "atr_reg", "repeat"]
print("\nONE INGREDIENT (thirds cut on older data): older avgR(n) | newest avgR(n)")
for f in feats:
    q = np.nanpercentile(old[f], [33, 67])
    parts = []
    for name, m in (("low", lambda s: s[f] <= q[0]), ("mid", lambda s: (s[f] > q[0]) & (s[f] <= q[1])), ("high", lambda s: s[f] > q[1])):
        a, b = stat(old[m(old)]), stat(new[m(new)])
        parts.append(f"{name} {a['R']:+.2f}({a['n']}) | {b['R']:+.2f}({b['n']})")
    print(f"{f:11} cuts {q[0]:.2f}/{q[1]:.2f}   " + "   ".join(parts))
for f in ["daily_ema", "h1_ema", "side"]:
    print(f, {v: (stat(old[old[f] == v])["R"], stat(new[new[f] == v])["R"], len(X[X[f] == v])) for v in sorted(X[f].unique())})
X["sess"] = pd.cut(X.hour, [-1, 1, 7, 12, 17, 24], labels=["Asia-late", "London", "NY", "NY-pm", "Asia"])
old, new = X[X.old], X[~X.old]
print("session", {v: (stat(old[old.sess == v])["R"], stat(new[new.sess == v])["R"], len(X[X.sess == v])) for v in X.sess.cat.categories})

# 2) combinations: grid of thresholds on the strongest ingredients, chosen on older data only
grid = dict(meter=[0, 0.5, 0.7, 0.85, 1.0, 1.2], er=[0, 0.2, 0.255, 0.3, 0.35],
            closeloc=[0, 0.5, 0.7], beyond=[-9, 0, 0.25], atr_reg=[0, 0.8, 1.0], repeat=[99, 2, 1])
res = []
for vals in itertools.product(*grid.values()):
    p = dict(zip(grid, vals))
    m = lambda s: (s.meter >= p["meter"]) & (s.er > p["er"]) & (s.closeloc >= p["closeloc"]) & (s.beyond >= p["beyond"]) \
        & (s.atr_reg >= p["atr_reg"]) & (s.repeat <= p["repeat"])
    a, b, c = stat(old[m(old)]), stat(new[m(new)]), stat(X[m(X)])
    res.append({**p, "old_n": a["n"], "old_R": a["R"], "old_t": a["t"], "new_n": b["n"], "new_R": b["R"], "new_win": b["win"],
                "all_n": c["n"], "all_win": c["win"], "all_R": c["R"], "all_t": c["t"]})
G = pd.DataFrame(res)
G.to_csv("/home/claude/best_setup_grid.csv", index=False)
print(f"\n{len(G)} combinations tested")
for lo, hi in ((60, 9999), (35, 60)):
    s = G[(G.old_n >= lo) & (G.old_n < hi)].sort_values("old_t", ascending=False).head(12)
    print(f"\nBest by older-data t-stat, older trades {lo}-{hi}:")
    print(s.to_string(index=False))
print("\nNewest-30% result across ALL combos (is selection on older data any better than random?):")
print("median newest R, all combos:", G[G.new_n >= 10].new_R.median(),
      " top-20 by older t:", G[G.old_n >= 35].sort_values("old_t", ascending=False).head(20).new_R.median())
