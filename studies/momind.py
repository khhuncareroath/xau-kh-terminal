import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd, itertools
import research as R
from engine import atr
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
o,h,l,c,v=(df[k].to_numpy() for k in ("Open","High","Low","Close","Volume")); n=len(df); idx=df.index
split=idx[int(n*0.7)]
a=atr(df).to_numpy()
day=np.array((idx-pd.Timedelta(hours=18)).date)
# session VWAP (trading day), EMA 50/200
tp=(h+l+c)/3; g=pd.DataFrame({"d":day,"pv":tp*np.maximum(v,1e-9),"v":np.maximum(v,1e-9)})
vwap=(g.groupby("d")["pv"].cumsum()/g.groupby("d")["v"].cumsum()).to_numpy()
ema={k:pd.Series(c).ewm(span=k).mean().to_numpy() for k in (50,200)}
b1=R._bias(df,"1H",pd.Timedelta(hours=1)); b1=np.where(b1=='bull',1,np.where(b1=='bear',-1,0))
hm=idx.hour*60+idx.minute
def run(line="vwap", body_k=1.2, look=6, htf=True, tp=2.0, lat=1, rmax=12, hold=36, sess=True):
    L=vwap if line=="vwap" else ema[int(line)]
    out=[]; busy=-1
    for i in range(300,n-hold-3):
        if i<=busy: continue
        if sess and not (180<=hm[i]<720): continue      # London + NY (NY time 03:00-12:00)
        body=c[i]-o[i]
        sg=1 if body>=body_k*a[i] else -1 if -body>=body_k*a[i] else 0
        if not sg: continue
        if sg>0 and not (c[i]>L[i] and c[i]>h[i-look:i].max()): continue
        if sg<0 and not (c[i]<L[i] and c[i]<l[i-look:i].min()): continue
        if htf and b1[i]!=sg: continue
        j0=i+lat; sl=l[i]-0.1*a[i] if sg>0 else h[i]+0.1*a[i]
        risk=(o[j0]-sl)*sg
        if risk<2 or risk>rmax: continue
        r,j=R._run_trade(o,h,l,c,j0,min(j0+hold,n-1),sg,sl,o[j0]+sg*tp*risk)
        if r is None: continue
        busy=j; out.append((idx[j0],r,'long' if sg>0 else 'short',risk))
    return out
rows=[]
for line,bk,look,htf,tp in itertools.product(("vwap","50","200"),(1.0,1.5,2.0),(6,12),(True,False),(1.5,2.0)):
    tr=run(line,bk,look,htf,tp)
    old=np.array([x[1] for x in tr if x[0]<split]); new=np.array([x[1] for x in tr if x[0]>=split])
    if len(old)<30: continue
    rows.append((old.mean(),line,bk,look,htf,tp,len(old),(old>0).mean(),len(new),new.mean(),(new>0).mean(),np.median([x[3] for x in tr])))
rows.sort(key=lambda r:-r[0])
print("variants",len(rows),"median OLD",round(np.median([r[0] for r in rows]),3),"median NEW",round(np.median([r[9] for r in rows]),3))
for r in rows[:8]:
    print(f"line={r[1]:4} body>={r[2]}ATR break{r[3]} htf={r[4]!s:5} TP{r[5]} OLD n={r[6]} {r[0]:+.3f} win {r[7]*100:.0f}% | NEW n={r[8]} {r[9]:+.3f} win {r[10]*100:.0f}% | SL ${r[11]:.1f}")
b=rows[0]; tr=run(*b[1:6]); j=R.judge([x[:3] for x in tr],split); print("BEST on OLD:", j['all'], 't',j['t_stat'],'new',j['newest_30pct'],j['positive_quarters'],j['proven'])
for lat in (2,3): t2=run(*b[1:6],lat=lat); print(" delay",lat*5,"min:", R.judge([x[:3] for x in t2],split)['all'])
