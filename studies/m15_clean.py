"""Does the 'clean 4H trend' filter (efficiency > CHOP_ER, the one that made both scalps work) help the M15 signal?
Uses the saved 2-year replay of the live M15 signal (studies/m15_replay.py output). 11 Nov 2026."""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
rows = {}
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "/tmp/m15_[a-f].json")):
    for r in json.load(open(f)):
        rows[r["t"]] = r
X = pd.DataFrame([r for r in rows.values() if r["kind"] == "break"])
X["t"] = pd.to_datetime(X.t, utc=True).dt.tz_convert("America/New_York")
X = X.sort_values("t")
X["er"] = [R.efficiency(df, t) or 0 for t in X.t]
X["old"] = X.t < split


def st(name, m):
    s = X[m]
    tr = [(t, r) for t, r in zip(s.t, s.R)]
    jd = R.judge(tr, split)
    print(f"{name:34} n={len(s):4d} ({len(s) / 24:4.1f}/mo) win {100 * (s.R > 0).mean():.0f}% avg {s.R.mean():+.3f}R "
          f"t={jd['t_stat']:+.1f} | older {s[s.old].R.mean():+.2f} newest {s[~s.old].R.mean():+.2f} | q {jd['positive_quarters']}"
          f"{' · PROVEN' if jd['proven'] else ''}")


for tier in ("all", "A+", "B+"):
    m = X.R == X.R if tier == "all" else X.tier == tier
    st(f"{tier}", m)
    st(f"{tier} + clean trend", m & (X.er > R.CHOP_ER))
    st(f"{tier} + choppy (skipped)", m & (X.er <= R.CHOP_ER))
for cut in (0.2, 0.25, 0.35, 0.4):
    st(f"all, efficiency > {cut}", X.er > cut)
