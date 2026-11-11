"""Can the bot 'analyze along' the wide scalp to avoid losers? (11 Nov 2026). Features at each scalp entry, one filter at
a time, chosen only if it helps on BOTH the older 70% and the newest 30%.  Run: python studies/scalp_filters.py"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd
import research as R
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
tr = R.wide_scalp(df)
combo = {t for t, *_ in R.trend_combo(df)}
intr = R.trend_intraday(df)
b4 = R._bias(df, "4H", pd.Timedelta(hours=4)); b1 = R._bias(df, "1H", pd.Timedelta(hours=1))
b15 = R._bias(df, "15m", pd.Timedelta(minutes=15))
rows = []
for t, r, side in tr:
    i = int(df.index.searchsorted(t)); want = "bull" if side == "long" else "bear"
    br = max((x for x in intr if x[0] <= t and x[2] == side), key=lambda x: x[0], default=None)
    age = (t - br[0]).total_seconds() / 3600 if br else 99
    rows.append(dict(t=t, R=r, strong=any(abs((t - c).total_seconds()) < 24 * 3600 and c <= t for c in combo),
                     b4=b4[i] == want, b1=b1[i] == want, b15=b15[i] == want, age=age,
                     meter=R.day_used(df, t) or 0, er=R.efficiency(df, t) or 0,
                     hour=t.tz_convert("Asia/Phnom_Penh").hour, n_today=0))
X = pd.DataFrame(rows); X["old"] = X.t < split
day = (X.t - pd.Timedelta(hours=18)).dt.date
X["second"] = X.groupby(day).cumcount() > 0
prev = X.R.shift(1); X["after_loss"] = (prev <= 0) & (day == day.shift(1))


def st(name, m):
    s = X[m]; o, n = s[s.old].R, s[~s.old].R
    print(f"{name:40} n={len(s):4d} ({len(s) / 24:4.1f}/mo) win {100 * (s.R > 0).mean():.0f}% avg {s.R.mean():+.3f} "
          f"| older {o.mean():+.2f} newest {n.mean():+.2f} | {'✅ both better' if o.mean() > X[X.old].R.mean() and n.mean() > X[~X.old].R.mean() else ''}")


st("ALL wide scalps", X.R == X.R)
st("💎 strong breakout window", X.strong); st("normal breakout window", ~X.strong)
st("4H structure agrees", X.b4); st("4H against", ~X.b4)
st("1H agrees", X.b1); st("15m agrees", X.b15)
st("4H + 1H agree", X.b4 & X.b1)
st("Day Meter >= 70%", X.meter >= 0.7); st("Day Meter < 70%", X.meter < 0.7)
st("clean trend ER > 0.30", X.er > 0.30)
st("within 6 h of the breakout", X.age <= 6); st("6-24 h after", X.age > 6)
st("first scalp of the day", ~X.second); st("second scalp of the day", X.second)
st("skip 2nd after a loss same day", ~(X.second & X.after_loss))
st("Cambodia 13-24h", X.hour >= 13); st("Cambodia 06-13h", (X.hour >= 6) & (X.hour < 13)); st("Cambodia 00-06h", X.hour < 6)
r = X.R.to_numpy(); s = m = 0
for v in r:
    s = s + 1 if v <= 0 else 0; m = max(m, s)
print("longest losing streak (all):", m)
X.to_csv("/home/claude/scalp_feat.csv", index=False)
