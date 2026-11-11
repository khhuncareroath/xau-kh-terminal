"""Robustness check for best_setup.py: neighbours of the chosen thresholds, tiers as separate sets, quarters, luck test.
Run after best_setup.py (reads /home/claude/best_setup_features.csv)."""
import numpy as np
import pandas as pd

X = pd.read_csv("/home/claude/best_setup_features.csv", parse_dates=["t"])
X["t"] = pd.to_datetime(X.t, utc=True)
rng = np.random.default_rng(7)


def st(s):
    r = s.r.to_numpy()
    if len(r) < 3:
        return f"n={len(r)}"
    t = r.mean() / r.std(ddof=1) * np.sqrt(len(r))
    o, n = s[s.old].r, s[~s.old].r
    q = s.groupby(s.t.dt.year.astype(str) + "Q" + ((s.t.dt.month - 1) // 3 + 1).astype(str)).r.agg(["count", "mean"])
    q = q[q["count"] >= 3]
    return (f"n={len(r):3d} ({len(r) / 24:.1f}/mo) win {100 * (r > 0).mean():.0f}% avg {r.mean():+.2f}R t {t:.1f} | "
            f"older {o.mean():+.2f} ({len(o)}) newest {n.mean():+.2f} ({len(n)}, {100 * (n > 0).mean():.0f}% win) | "
            f"+quarters {int((q['mean'] > 0).sum())}/{len(q)} | worst streak {streak(r)}")


def streak(r):
    m = s = 0
    for v in r:
        s = s + 1 if v <= 0 else 0
        m = max(m, s)
    return m


print("Neighbours of strong close (closeloc) x clean trend (er), Day Meter >= 0.7: avg R all (n) / newest")
for cl in (0, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8):
    line = []
    for er in (0.2, 0.255, 0.3, 0.35):
        s = X[(X.meter >= 0.7) & (X.er > er) & (X.closeloc >= cl)]
        line.append(f"{s.r.mean():+.2f}({len(s)})/{s[~s.old].r.mean():+.2f}")

    print(f"close>={cl:<4}  " + "  ".join(line))
print("\nSame with Day Meter >= 1.0")
for cl in (0, 0.5, 0.6, 0.7, 0.8):
    line = []
    for er in (0.2, 0.255, 0.3, 0.35):
        s = X[(X.meter >= 1.0) & (X.er > er) & (X.closeloc >= cl)]
        line.append(f"{s.r.mean():+.2f}({len(s)})/{s[~s.old].r.mean():+.2f}")
    print(f"close>={cl:<4}  " + "  ".join(line))

B = (X.meter >= 0.7) & (X.er > 0.255)
designs = {
    "CURRENT  A+ = meter>=1.0": B & (X.meter >= 1.0),
    "NEW      A+ = strong close>=0.7 + er>0.30": B & (X.closeloc >= 0.7) & (X.er > 0.30),
    "NEW2     A+ = strong close>=0.7": B & (X.closeloc >= 0.7),
    "NEW3     A+ = meter>=1.0 OR (close>=0.7 & er>0.30)": B & ((X.meter >= 1.0) | ((X.closeloc >= 0.7) & (X.er > 0.30))),
    "NEW4     A+ = meter>=1.0 AND close>=0.5": B & (X.meter >= 1.0) & (X.closeloc >= 0.5),
}
print("\nALL B-or-better (meter>=0.7, er>0.255):", st(X[B]))
for name, a in designs.items():
    print(f"\n{name}\n   A+ : {st(X[a])}\n   B+ : {st(X[B & ~a])}")
print("\nskipped (not B):", st(X[~B]))

# luck: does 'strong close' beat a random subset of the same size inside B?
a = B & (X.closeloc >= 0.7) & (X.er > 0.30)
real = X[a].r.mean()
pool = X[B].r.to_numpy()
sims = np.array([rng.choice(pool, a.sum(), replace=False).mean() for _ in range(20000)])
print(f"\nLuck test: A+ NEW avg {real:+.3f} vs random same-size picks from B: p = {(sims >= real).mean():.3f}")
a = B & (X.meter >= 1.0)
real = X[a].r.mean()
sims = np.array([rng.choice(pool, a.sum(), replace=False).mean() for _ in range(20000)])
print(f"Luck test: A+ CURRENT avg {real:+.3f} vs random same-size picks from B: p = {(sims >= real).mean():.3f}")
