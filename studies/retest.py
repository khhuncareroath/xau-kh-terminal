import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from ict import resample
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
o,h,l,c=(df[k].to_numpy() for k in ("Open","High","Low","Close")); n=len(df); idx=df.index
split=idx[int(n*0.7)]
d4=resample(df,"4H")
hi30=d4["High"].rolling(30).max().shift(1).to_numpy(); lo30=d4["Low"].rolling(30).min().shift(1).to_numpy(); c4=d4["Close"].to_numpy()
sigs=[]
for k in range(31,len(d4)):
    sg=1 if c4[k]>hi30[k] else -1 if c4[k]<lo30[k] else 0
    if not sg: continue
    i=int(idx.searchsorted(d4.index[k]+pd.Timedelta(hours=4)))-1
    if i+R.LAT+2>=n: continue
    sigs.append((i, sg, hi30[k] if sg>0 else lo30[k], c4[k]))
def sim(f=None, window=48, stop_pct=0.0055, tp1=0.75, tp2=3.0, hold=144, du_min=None):
    out=[]; busy=-1; stops=[]; mae=[]
    for i,sg,L,C in sigs:
        j0=i+1+R.LAT
        if j0<=busy: continue
        if du_min is not None and (R.day_used(df, idx[j0]) or 0)<du_min: continue
        if f is None:
            fill=j0; en=o[j0]
        else:
            en=C - sg*f*abs(C-L)          # limit: f=0.5 halfway back, f=1 full retest of the broken level
            fill=None
            for j in range(j0, min(j0+window, n-1)):
                if (l[j]<=en) if sg>0 else (h[j]>=en): fill=j; break
            if fill is None: continue
        stop=en*(1-sg*stop_pct); risk=abs(en-stop)
        # run scaled from fill with entry price en (limit fill)
        st=stop; got=0; left=1; hit1=False; res=None; jend=min(fill+hold,n-1); worst=0
        for j in range(fill, jend+1):
            worst=max(worst, (en-(l[j] if sg>0 else h[j]))*sg)
            if (l[j]<=st) if sg>0 else (h[j]>=st):
                res=got+left*(st-en)*sg/risk; break
            if not hit1 and ((h[j]>=en+sg*tp1*risk) if sg>0 else (l[j]<=en+sg*tp1*risk)):
                got+=0.5*tp1; left=0.5; hit1=True; st=en
            if hit1 and ((h[j]>=en+sg*tp2*risk) if sg>0 else (l[j]<=en+sg*tp2*risk)):
                res=got+left*tp2; break
        if res is None: res=got+left*(c[jend]-en)*sg/risk; j=jend
        res-=R.COST/risk
        busy=j; out.append((idx[fill],res,'long' if sg>0 else 'short')); stops.append(risk); mae.append(worst)
    return out, np.array(stops), np.array(mae)
def show(name, *a, **k):
    tr,st,mae=sim(*a,**k); r=np.array([x[1] for x in tr]); j=R.judge(tr,split)
    print(f"{name:34} n={len(r):3} win={100*(r>0).mean():3.0f}% avgR={r.mean():+.3f} totR={r.sum():+6.1f} t={j['t_stat']:+.2f} new30={j['newest_30pct']['avg_R']:+.3f} q={j['positive_quarters']} SL=${np.median(st):.1f} avg-heat=${np.median(mae):.1f} proven={j['proven']}")
show("NOW: market entry, SL 0.55%")
for f in (0.3,0.5,0.8,1.0):
    for w in (24,48):
        for sp in (0.0025,0.0035,0.0055):
            show(f"retest {int(f*100)}% {w*5//60}h SL {sp*100:.2f}%", f, w, sp)
