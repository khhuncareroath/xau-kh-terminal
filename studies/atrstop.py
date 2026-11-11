import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd, inspect
import research as R
from engine import atr
from ict import resample
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split=df.index[int(len(df)*0.7)]
src=inspect.getsource(R.trend_breakout)
src=src.replace("clock=False):","clock=False, stop_fn=None):").replace(
 "        stop = o[j0] - sg * 2 * a4[k] if stop_pct is None else o[j0] * (1 - sg * stop_pct)",
 "        stop = o[j0] - sg * stop_fn(k, j0, i) if stop_fn else (o[j0] - sg * 2 * a4[k] if stop_pct is None else o[j0] * (1 - sg * stop_pct))")
ns=vars(R).copy(); exec(src, ns); tb=ns['trend_breakout']
o=df['Open'].to_numpy()
d4=resample(df,"4H"); a4=atr(d4).to_numpy()
d1=resample(df,"1H"); a1=atr(d1).to_numpy(); t1=d1.index
a1_at=lambda i: a1[max(0,int(t1.searchsorted(df.index[i]))-1)]
def run(stop_fn=None, stop_pct=None, hold=144, clock=True, tp1=0.75, tp2=3.0):
    return tb(df, scaled=True, stop_pct=stop_pct, tp1=tp1, tp2=tp2, hold_bars=hold, clock=clock, stop_fn=stop_fn)
def show(name, tr):
    j=R.judge(tr, split); r=np.array([x[1] for x in tr])
    combo=[x for x in tr if (R.day_used(df,x[0]) or 0)>=0.7]; rc=np.array([x[1] for x in combo])
    print(f"{name:26} n={len(r):3} win={100*(r>0).mean():3.0f}% avgR={r.mean():+.3f} totR={r.sum():+6.1f} t={j['t_stat']:+.2f} new30={j['newest_30pct']['avg_R']:+.3f} q={j['positive_quarters']} proven={j['proven']} | COMBO n={len(rc)} win={100*(rc>0).mean():.0f}% avgR={rc.mean():+.3f}")
show("NOW fixed 0.55%", run(stop_pct=0.0055))
for p in (0.0035,0.0045,0.0075):
    show(f"fixed {p*100:.2f}%", run(stop_pct=p))
for k in (0.5,0.75,1.0,1.5):
    show(f"ATR4H x{k}", run(stop_fn=lambda kk,j0,i,k=k: k*a4[kk]))
for k in (1.0,1.5,2.0,3.0):
    show(f"ATR1H x{k}", run(stop_fn=lambda kk,j0,i,k=k: k*a1_at(i)))
