"""Lesson from the 12 Nov 06:30 A+ SELL (owner: "it nearly hit SL; maybe demand / FVG / OB below pushed it up").
Tags on the 2-year M15 replay (breakouts), checked in BOTH halves:
 room   = distance from entry to the recent extreme in the trade direction (lowest low of the last 12 h for a SELL,
          highest high for a BUY), in R. Small room = selling right into old lows (demand) = owner's idea.
 used   = Day Meter (how much of a normal day's range is already used)
 hour   = Cambodia hour of entry (06-08 = Asia open, thin market)
Run: python studies/m15_lesson.py"""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
H, L = df.High.to_numpy(), df.Low.to_numpy()
rows = {}
for f in sorted(glob.glob("/tmp/m15_[a-f].json")):
    for r in json.load(open(f)): rows[r["t"]] = r
X = pd.DataFrame([r for r in rows.values() if r["kind"] == "break"])
X["t"] = pd.to_datetime(X.t, utc=True).dt.tz_convert("America/New_York")
X["old"] = X.t < split
room, used, hk = [], [], []
for _, r in X.iterrows():
    j = int(r.j0); sg = 1 if r.dir == "bull" else -1
    risk = abs(r.entry - r.stop)
    ext = H[j - 144:j].max() if sg > 0 else L[j - 144:j].min()
    room.append((ext - r.entry) * sg / risk)
    try: used.append(R.day_used(df, df.index[j]) or np.nan)
    except Exception: used.append(np.nan)
    hk.append(df.index[j].tz_convert("Asia/Phnom_Penh").hour)
X["room"], X["used"], X["hk"] = room, used, hk

def st(name, s):
    if len(s) < 12: print(f"  {name:38} n={len(s)} (too few)"); return
    print(f"  {name:38} n={len(s):4d} win {100*(s.R>0).mean():.0f}% avg {s.R.mean():+.3f}R | older {s[s.old].R.mean():+.2f} "
          f"newest {s[~s.old].R.mean():+.2f}")
for tier in ("A+", "all"):
    S = X if tier == "all" else X[X.tier == tier]
    print("==", tier); st("all", S)
    for lo, hi in ((-99, 0.5), (0.5, 1), (1, 2), (2, 99)):
        st(f"room to 12h extreme {lo}..{hi} R", S[(S.room > lo) & (S.room <= hi)])
    for lo, hi in ((0, .5), (.5, .8), (.8, 1.2), (1.2, 9)):
        st(f"Day Meter {lo}..{hi}", S[(S.used > lo) & (S.used <= hi)])
    st("Cambodia 06-08 (Asia open)", S[(S.hk >= 6) & (S.hk < 8)])
    st("Cambodia 08-14", S[(S.hk >= 8) & (S.hk < 14)])
    st("Cambodia 14-24", S[S.hk >= 14])
X.to_pickle("/tmp/m15_tags.pkl")
