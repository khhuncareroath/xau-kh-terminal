"""Robustness of the vp_shape lesson: trades NOT with the 4H vs WITH the 4H, every setting (12 Nov 2026)."""
import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd, research as R
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df)*0.7)]; pos={t:k for k,t in enumerate(df.index)}
b4 = R._bias(df,"4H",pd.Timedelta(hours=4))
for th in (0.5,0.55,0.6,0.65):
  for rr in (1.5,2.0,2.5):
    tr=R.vp_shape(df,th=th,rr=rr)
    a=[(t,r) for t,r,s in tr if b4[pos[t]-1]!=("bull" if s=="long" else "bear")]
    w=[(t,r) for t,r,s in tr if b4[pos[t]-1]==("bull" if s=="long" else "bear")]
    ja,jw=R.judge(a,split),R.judge(w,split)
    neutral=sum(1 for t,r,s in tr if b4[pos[t]-1] is None)
    print(f"th {th} rr {rr}: NOT-with-4H n={len(a)} {np.mean([r for _,r in a]):+.2f}R t={ja['t_stat']:+.1f} old {ja['older_70pct']['avg_R']:+.2f} new {ja['newest_30pct']['avg_R']:+.2f} {'PROVEN' if ja['proven'] else ''} | with-4H n={len(w)} {np.mean([r for _,r in w]):+.2f}R | 4H neutral {neutral}")
