"""🧱 Signal INSIDE an opposite zone (owner, 12 Nov 2026: the 12:15 crazy SELL sat inside a big demand / HTF bull array).
arrays.opposite() already reports `inside` but nothing used it. For each signal: is the entry inside an active
opposite zone, and on which timeframe? Compared on the older 70% and newest 30%.
M15: 369 replayed live signals (/tmp/m15_*.json). Fun Scalp: live entries (studies/second_chance.py builders).
Run: python studies/inside_zone.py"""
import sys, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import arrays
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
TFS = ("15m", "30m", "1H", "4H", "D")
Z = {}
for tf in TFS:
    zs = arrays.zones(df, tf)
    Z[tf] = (np.array([z["dir"] == "bull" for z in zs]), np.array([z["lo"] for z in zs]), np.array([z["hi"] for z in zs]),
             np.array([z["t0"].value for z in zs]), np.array([z["t1"].value for z in zs]))


def inside(t, en, sg):
    """Timeframes whose active OPPOSITE zone contains the entry, and the zone size in $."""
    out = {}
    for tf, (bull, lo, hi, t0, t1) in Z.items():
        m = (bull == (sg < 0)) & (t0 <= t.value) & (t.value < t1) & (lo <= en) & (en <= hi)
        if m.any():
            out[tf] = float((hi[m] - lo[m]).max())
    return out


def line(name, s):
    if not len(s):
        return print(f"  {name:38s}    0")
    o, n = s[~s.new].R, s[s.new].R
    t = s.R.mean() / s.R.std(ddof=1) * np.sqrt(len(s)) if len(s) > 2 else 0
    print(f"  {name:38s} {len(s):4d} {100*(s.R>0).mean():3.0f}% {s.R.mean():+.3f}R t{t:5.1f} | old {o.mean():+.2f} ({len(o)}) new {n.mean():+.2f} ({len(n)}) | sum {s.R.sum():+.0f}R")


def study(name, X):
    X = X.copy(); X["new"] = X.t >= split
    print(f"\n== {name}")
    line("all", X)
    line("inside ANY opposite zone", X[X.ins.map(len) > 0])
    line("not inside", X[X.ins.map(len) == 0])
    for grp, tfs in (("inside 4H or D", ("4H", "D")), ("inside 1H-D", ("1H", "4H", "D")), ("inside 15m/30m only", None)):
        if tfs:
            m = X.ins.map(lambda d: any(k in d for k in tfs))
        else:
            m = X.ins.map(lambda d: len(d) > 0 and not any(k in d for k in ("1H", "4H", "D")))
        line(grp, X[m]); line("  -> skipping those leaves", X[~m])


M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
rows = []
for r in M:
    t = df.index[r["j0"]]
    sg = 1 if r["dir"] == "bull" else -1
    rows.append(dict(t=t, R=r["R"], ins=inside(t, r["entry"], sg), tier=r["tier"]))
study("📈 M15 signals (live, with the 0.5R other-side rule)", pd.DataFrame(rows))

sys.argv = ["x"]
src = open('/home/claude/xau-kh-terminal/studies/second_chance.py').read()
pre, post = src.split("# --- wide scalp")
fun_part = "# --- wide scalp" + post.split("q, qR = fun_sigs")[0]
exec(pre.split("# --- M15 ---")[0]); exec(fun_part)
for nm, (sigs, Rs) in (("🎰 Fun 🔥 QUALITY", fun_sigs(True, 3)), ("🎰 Fun 🎲 CRAZY", fun_sigs(False, 4))):
    rows = []
    for (t, s, j0), r in zip(sigs, Rs):
        sg = 1 if s["dir"] == "bull" else -1
        rows.append(dict(t=t, R=r, ins=inside(t, s["entry"], sg)))
    study(nm, pd.DataFrame(rows))
