"""💎💎 Max quality (owner, 14 Nov 2026: "only quality, I don't care about the amount"). Strictest versions that still
pass: better than the current live rule on BOTH halves, newest 30% >= 10 trades, research.judge proven.
M15: live replay with the 1.0R rule (/tmp/m15_q_*.json). Scalp / Fun: first of the day (+ 1H) as live now.
Run: python studies/max_quality.py"""
import sys, json, itertools
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
b1 = R._bias(df, "1H", pd.Timedelta(hours=1)); bD = R._bias(df, "D", pd.Timedelta(days=1))
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))


def show(nm, S, base=None):
    if len(S) < 15:
        return print(f"  {nm:40s} {len(S)} (too few)")
    j = R.judge([(t, r) for t, r in zip(S.t, S.R)], split)
    o, n = S[~S.new].R.mean(), S[S.new].R.mean()
    ok = base is None or (o > base[0] and n > base[1] and S.new.sum() >= 10 and j["proven"])
    print(f"  {nm:40s} {len(S):3d} ({len(S)/24:3.1f}/mo) {100*(S.R>0).mean():3.0f}% win · full SL {100*(S.R<=-0.9).mean():3.0f}% · "
          f"{S.R.mean():+.3f}R old {o:+.2f} new {n:+.2f} ({S.new.sum()}) q {j['positive_quarters']} {'✓ PASSES' if ok else ''}")


def add(X):
    X["new"] = X.t >= split
    X["day"] = (X.t - pd.Timedelta(hours=18)).dt.date
    X["n"] = X.groupby("day").cumcount()
    j = [df.index.searchsorted(t) - 1 for t in X.t]
    X["h1"] = [b1[k] == d for k, d in zip(j, X.d)]; X["hD"] = [bD[k] == d for k, d in zip(j, X.d)]
    X["h4"] = [b4[k] == d for k, d in zip(j, X.d)]
    hr = X.t.dt.hour + X.t.dt.minute / 60; X["ny"] = (hr >= 2) & (hr < 12)
    return X


# 📈 M15 (live now: 1.0R rule)
M = json.load(open('/tmp/m15_q_a.json')) + json.load(open('/tmp/m15_q_b.json'))
X = add(pd.DataFrame([dict(t=df.index[r["j0"]], R=r["R"], d=r["dir"], ap=r["tier"] == "A+", tp1=r["tp1"]) for r in M]))
base = (X[~X.new].R.mean(), X[X.new].R.mean())
print("== 📈 M15 (live: other side 1.0R)")
show("live now", X)
for nm, m in [("first of the day", X.n == 0), ("A+ only", X.ap), ("1H agrees", X.h1), ("Daily agrees", X.hD),
              ("first of day + 1H", (X.n == 0) & X.h1), ("first of day + Daily", (X.n == 0) & X.hD),
              ("first of day + A+", (X.n == 0) & X.ap), ("1H + Daily", X.h1 & X.hD), ("first + 1H + Daily", (X.n == 0) & X.h1 & X.hD)]:
    show(nm, X[m], base)

# ⚡ Scalp (live now: first of day + 1H)
T = R.wide_scalp(df)
X = add(pd.DataFrame([dict(t=t, R=r, d="bull" if s == "long" else "bear") for t, r, s in T]))
L = X[(X.n == 0) & X.h1]; base = (L[~L.new].R.mean(), L[L.new].R.mean())
print("\n== ⚡ Scalp (live: first of day + 1H)")
show("live now", L)
for nm, m in [("+ Daily", L.hD), ("+ London/NY", L.ny)]:
    show(nm, L[m], base)

# 🎰 Fun 🔥: see studies/fun_quality.py (1 a day + 1H live; + Daily: 98, 70%, +0.42R, older +0.32 / newest +0.82 (20):
# the same win rate on fewer trades, within noise -> not changed)
