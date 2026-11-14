"""💎 Quality-only signals (owner, 14 Nov 2026: "when it hits SL the group looks bad quality, I want only the very
quality signals"). Pre-set filters, each must beat the base on BOTH the older 70% and the newest 30%:
  F1 1H structure agrees · F2 Daily structure agrees · F3 London/NY hours only (02-12 NY) · F4 no opposite 15m-D zone
  within 1.0R ahead (live rule is 0.5R) · F5 small stop (risk <= median) · F6 A+ only (M15)
📈 M15: 369 replayed live signals (/tmp/m15_a.json + b). ⚡ Scalp: research.wide_scalp trades.
Run: python studies/quality_filters.py"""
import sys, json, itertools
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R, arrays
from levels import to_ny
from engine import atr

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
b1 = R._bias(df, "1H", pd.Timedelta(hours=1))
bD = R._bias(df, "D", pd.Timedelta(days=1))
Z = {}
for tf in ("15m", "30m", "1H", "4H", "D"):
    zs = arrays.zones(df, tf)
    Z[tf] = (np.array([z["dir"] == "bull" for z in zs]), np.array([z["lo"] for z in zs]), np.array([z["hi"] for z in zs]),
             np.array([z["t0"].value for z in zs]), np.array([z["t1"].value for z in zs]))


def opp_dist(t, en, sg, risk):
    best = 99.0
    for bull, lo, hi, t0, t1 in Z.values():
        m = (bull == (sg < 0)) & (t0 <= t.value) & (t.value < t1)
        for lv in (lo[m], hi[m]):
            d = (lv - en) * sg / risk; d = d[d > 0.05]
            if len(d): best = min(best, float(d.min()))
    return best


def feats(t, j0, sg, en, risk):
    d = "bull" if sg > 0 else "bear"
    hr = t.hour + t.minute / 60
    return dict(F1=b1[j0 - 1] == d, F2=bD[j0 - 1] == d, F3=2 <= hr < 12, F4=opp_dist(t, en, sg, risk) > 1.0, risk=risk)


def line(name, s, base_o, base_n):
    if len(s) < 8:
        return print(f"  {name:34s} {len(s):4d}")
    o, n = s[~s.new].R, s[s.new].R
    t = s.R.mean() / s.R.std(ddof=1) * np.sqrt(len(s))
    both = (o.mean() > base_o) and (n.mean() > base_n)
    print(f"  {name:34s} {len(s):4d} ({len(s)/24:4.1f}/mo) {100*(s.R>0).mean():3.0f}% win {s.R.mean():+.3f}R t{t:4.1f} | "
          f"old {o.mean():+.2f} ({len(o)}) new {n.mean():+.2f} ({len(n)}) | total {s.R.sum():+5.0f}R {'✓ both' if both else ''}")


def study(name, X, extra=()):
    X = X.copy(); X["new"] = X.t >= split
    X["F5"] = X.risk <= X.risk.median()
    bo, bn = X[~X.new].R.mean(), X[X.new].R.mean()
    print(f"\n== {name}"); line("BASE (as live)", X, -9, -9)
    fl = ["F1", "F2", "F3", "F4", "F5"] + list(extra)
    names = {"F1": "1H agrees", "F2": "Daily agrees", "F3": "London/NY only", "F4": "no opposite zone <1R",
             "F5": "small stop", "F6": "A+ only"}
    for f in fl:
        line(names[f], X[X[f]], bo, bn)
    for a, b in itertools.combinations(fl, 2):
        line(f"{names[a]} + {names[b]}", X[X[a] & X[b]], bo, bn)
    return X


M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
rows = []
for r in M:
    j0 = r["j0"]; t = df.index[j0]; sg = 1 if r["dir"] == "bull" else -1
    f = feats(t, j0, sg, r["entry"], r["risk"]); f.update(t=t, R=r["R"], F6=r["tier"] == "A+")
    rows.append(f)
study("📈 M15 signal", pd.DataFrame(rows), ["F6"])

e20 = pd.Series(C).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
a_ = atr(df).to_numpy()
rows = []
for t, r, side in R.wide_scalp(df):
    j0 = int(df.index.searchsorted(t)); sg = 1 if side == "long" else -1
    sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, j0 - 1, sg)
    if sw is None: continue
    f = feats(t, j0, sg, O[j0], (O[j0] - sw) * sg); f.update(t=t, R=r)
    rows.append(f)
study("⚡ Scalp", pd.DataFrame(rows))
