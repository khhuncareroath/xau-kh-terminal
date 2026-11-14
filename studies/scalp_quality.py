"""⚡ Scalp quality-only (owner, 14 Nov 2026): first scalp of the day, + 1H agrees. Run: python studies/scalp_quality.py"""
import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd, research as R
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz',index_col=0,parse_dates=True)); split=df.index[int(len(df)*.7)]
b1=R._bias(df,"1H",pd.Timedelta(hours=1))
T=R.wide_scalp(df)
X=pd.DataFrame([dict(t=t,R=r,d="bull" if s=="long" else "bear") for t,r,s in T]); X["new"]=X.t>=split
X["day"]=(X.t-pd.Timedelta(hours=18)).dt.date; X["n"]=X.groupby("day").cumcount()
X["h1"]=[b1[df.index.searchsorted(t)-1]==d for t,d in zip(X.t,X.d)]
def show(nm,S):
    j=R.judge([(t,r) for t,r in zip(S.t,S.R)],split)
    print(f"{nm:24s} {len(S)} ({len(S)/24:.1f}/mo) {100*(S.R>0).mean():.0f}% win {S.R.mean():+.3f}R old {S[~S.new].R.mean():+.2f} new {S[S.new].R.mean():+.2f} total {S.R.sum():+.0f}R q {j['positive_quarters']} proven {j['proven']}")
show("all (live)",X); show("first of day",X[X.n==0]); show("first 2 of day",X[X.n<2]); show("first of day + 1H",X[(X.n==0)&X.h1]); show("1H agrees",X[X.h1])
print("per day:",X.groupby("day").size().value_counts().sort_index().to_dict())
