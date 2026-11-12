"""Owner, 12 Nov 2026: "it went up against the SL, there must be an HTF array that pushed it".
The 06:30 SELL (entry 3982, TP1 3964.5) sold INSIDE a 4H bull FVG (3964-3995) and 1H bull FVG (3957-3995); price turned
at 3969, the top of a DAILY bull order block (3896-3969) = bottom of a Daily bull FVG. The bot only looks at zones up to
$20 wide (15m, 1H, 4H) and skips Daily ones, so it did not see these.
Test: for every replayed A+ (London/NY + Asia), the nearest active 4H/Daily zone EDGE of the opposite side ahead of the
entry (for a SELL: the nearest bull-zone top or bottom below entry), in R. Does an edge before TP1 hurt?
Run: python studies/htf_arrays.py"""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R, splus
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
Z = []
for tf, life in (("1H", 5), ("4H", 15), ("D", 40)):
    zs, _ = splus._zones(df, tf, life)
    Z += zs
print(len(Z), "zones")
A = pd.read_pickle("/tmp/asia.pkl"); A = A[A.kind == "break"].assign(ses="Asia")
M = pd.read_pickle("/tmp/m15_tags.pkl"); M = M[M.tier == "A+"].assign(ses="LDN/NY")
X = pd.concat([A, M], ignore_index=True)
X["t"] = pd.to_datetime(X.t)

def edge(r, tfs, wide_only=False):
    sg = 1 if r.dir == "bull" else -1; t = r.t; risk = abs(r.entry - r.stop)
    want = "bear" if sg > 0 else "bull"
    best = None
    for z in Z:
        if z["tf"] not in tfs or z["dir"] != want or not (z["t0"] <= t <= z["t1"]):
            continue
        if wide_only and z["hi"] - z["lo"] <= 20:
            continue
        for lv in (z["lo"], z["hi"]):
            d = (lv - r.entry) * sg / risk
            if d > 0.05 and (best is None or d < best[0]):
                best = (d, z["tf"])
    return best

def st(n, s):
    if len(s) < 12: print(f"  {n:44} n={len(s)} few"); return
    jd = R.judge(list(zip(s.t, s.R)), split)
    print(f"  {n:44} n={len(s):3d} win {100*(s.R>0).mean():.0f}% avg {s.R.mean():+.3f}R t={jd['t_stat']:+.1f} | older {s[s.old].R.mean():+.2f} newest {s[~s.old].R.mean():+.2f} | TP1 {100*s.tp1.mean():.0f}%")

for name, tfs, wide in (("4H + Daily zones", ("4H", "D"), False), ("Daily zones", ("D",), False),
                        ("4H/D zones wider than $20 (bot ignores)", ("4H", "D"), True), ("1H/4H/D", ("1H", "4H", "D"), False)):
    e = X.apply(lambda r: edge(r, tfs, wide), axis=1)
    X["ed"] = [x[0] if x else 99 for x in e]
    X["tp1R"] = (X.tp1p - X.entry).abs() / (X.entry - X.stop).abs()
    print("==", name)
    st("all A+", X)
    st("opposite edge BEFORE TP1", X[X.ed < X.tp1R])
    st("opposite edge within 1R", X[X.ed <= 1])
    st("no opposite edge before TP1", X[X.ed >= X.tp1R])

# --- fix instead of skip: take TP1 AT the 4H/D edge (half off + SL to entry there), keep TP2 ---------------------------
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
kh = df.index.tz_convert("Asia/Phnom_Penh")
def grade(r, tp1):
    sg = 1 if r.dir == "bull" else -1; en, st, tp2 = r.entry, r.stop, r.tp2p; risk = abs(en - st); j0 = int(r.j0)
    mid = kh[j0].normalize() + pd.Timedelta(days=1); jend = min(j0 + 96, len(df) - 1)
    while jend > j0 and kh[jend] >= mid: jend -= 1
    stop, got, left, hit = st, 0.0, 1.0, False
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop): return got + left * (stop - en) * sg / risk - .4 / risk
        if not hit and ((H[j] >= tp1) if sg > 0 else (L[j] <= tp1)): got, left, hit, stop = .5 * abs(tp1 - en) / risk, .5, True, en
        if hit and ((H[j] >= tp2) if sg > 0 else (L[j] <= tp2)): return got + left * abs(tp2 - en) / risk - .4 / risk
    return got + left * (C[jend] - en) * sg / risk - .4 / risk
e = X.apply(lambda r: edge(r, ("4H", "D")), axis=1)
X["ed"] = [x[0] if x else 99 for x in e]
X["tp1R"] = (X.tp1p - X.entry).abs() / (X.entry - X.stop).abs()
blk = X.ed < X.tp1R
X["R_base"] = [grade(r, r.tp1p) for _, r in X.iterrows()]
X["R_fix"] = [grade(r, r.entry + (1 if r.dir == "bull" else -1) * max(r.ed - 0.1, 0.3) * abs(r.entry - r.stop)) if b else r.R_base
              for (_, r), b in zip(X.iterrows(), blk)]
for col in ("R_base", "R_fix"):
    s = X.assign(R=X[col]); print("==", col); st("all A+", s); st("the blocked ones", s[blk])
s = X[~blk].assign(R=X.R_base[~blk]); print("== skip blocked"); st("A+ without them", s)
