import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from ict import resample
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
o,h,l,c=(df[k].to_numpy() for k in ("Open","High","Low","Close")); n=len(df)
d4=resample(df,"4H")
closes=[int(df.index.searchsorted(t+pd.Timedelta(hours=4)))-1+1+R.LAT for t in d4.index[31:]]
closes=np.array([j for j in closes if j+150<n])
rng=np.random.default_rng(7)
def rand_trades(m, stop_pct, tp1, hold, du_min=None, trials=1000, same_dir=None):
    pool=closes
    if du_min is not None:
        pool=np.array([j for j in closes if (R.day_used(df, df.index[j]) or 0)>=du_min])
    res=[]
    for _ in range(trials):
        js=rng.choice(pool, m, replace=False); sg=rng.choice([-1,1], m) if same_dir is None else rng.permutation(same_dir)[:m]
        rs=[]
        for j,s in zip(js,sg):
            r,_,_=R._run_scaled(o,h,l,c,j,min(j+hold,n-1),s,o[j]*(1-s*stop_pct),tp1,3.0)
            if r is not None: rs.append(r)
        res.append(np.mean(rs))
    return np.array(res)
for name, fn, sp, hold, du in (("trend_intraday", R.trend_intraday, 0.0055, 144, None),
                                ("trend_combo", R.trend_combo, 0.0055, 144, 0.7),
                                ("trend_premium", R.trend_premium, 0.0065, 1440, 1.0)):
    tr=fn(df); real=np.mean([x[1] for x in tr]); dirs=np.array([1 if x[2]=='long' else -1 for x in tr])
    rnd=rand_trades(len(tr), sp, 0.75, hold, du, trials=400 if hold<1000 else 200, same_dir=dirs)
    p=(rnd>=real).mean()
    print(f"{name:15} real avgR {real:+.3f} | random same exits & same buy/sell mix: mean {rnd.mean():+.3f}, best 5% {np.percentile(rnd,95):+.3f} | luck chance p={p:.3f}")
