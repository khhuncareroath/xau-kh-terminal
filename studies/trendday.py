import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd, itertools
import research as R
from engine import atr
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
o,h,l,c=(df[k].to_numpy() for k in ("Open","High","Low","Close")); n=len(df); idx=df.index
split=idx[int(n*0.7)]
a=atr(df).to_numpy()
e20=pd.Series(c).ewm(span=20).mean().to_numpy()
day=np.array((idx-pd.Timedelta(hours=18)).date)
g=pd.DataFrame({"d":day,"h":h,"l":l,"o":o})
dh=g.groupby("d")["h"].cummax().to_numpy(); dl=g.groupby("d")["l"].cummin().to_numpy()
dopen=g.groupby("d")["o"].transform("first").to_numpy()
rng=g.groupby("d").agg(H=("h","max"),L=("l","min")); rng=(rng.H-rng.L)
adr=rng.shift(1).rolling(20,min_periods=10).median()
adr_b=pd.Series(day).map(adr).to_numpy()
used=(dh-dl)/adr_b
b1=R._bias(df,"1H",pd.Timedelta(hours=1)); b1=np.where(b1=='bull',1,np.where(b1=='bear',-1,0))
hm=idx.hour*60+idx.minute
# 15m bullish/bearish FVG zones (causal): gap between bar k-2 high and bar k low on 15m candles
d15=df.resample("15min").agg({"Open":"first","High":"max","Low":"min","Close":"last"}).dropna()
fv_lo=np.full(n,np.nan); fv_hi=np.full(n,np.nan); fv_dir=np.zeros(n)
H15,L15=d15.High.to_numpy(),d15.Low.to_numpy()
for k in range(2,len(d15)):
    t=d15.index[k]+pd.Timedelta(minutes=15)
    i=idx.searchsorted(t)
    if i>=n: break
    if L15[k]>H15[k-2]: fv_lo[i:i+24]=H15[k-2]; fv_hi[i:i+24]=L15[k]; fv_dir[i:i+24]=1
    elif H15[k]<L15[k-2]: fv_lo[i:i+24]=H15[k]; fv_hi[i:i+24]=L15[k-2]; fv_dir[i:i+24]=-1
def run(umin=0.7, move=0.4, trig="ema", rmin=3, rmax=12, tp=("scaled",1.0,3.0), lat=1, hold=36, win=(120,720), maxday=2):
    out=[]; busy=-1; cnt={}
    for i in range(300,n-hold-5):
        if i<=busy or not (win[0]<=hm[i]<win[1]): continue
        if not np.isfinite(used[i]) or used[i]<umin: continue
        sg=1 if c[i]-dopen[i]>move*adr_b[i] else -1 if dopen[i]-c[i]>move*adr_b[i] else 0
        if sg==0 or b1[i]!=sg: continue
        if trig=="ema":
            touched=(l[i-3:i+1].min()<=e20[i]) if sg>0 else (h[i-3:i+1].max()>=e20[i])
        else:
            touched=fv_dir[i]==sg and ((l[i-3:i+1].min()<=fv_hi[i]) if sg>0 else (h[i-3:i+1].max()>=fv_lo[i]))
        if not touched: continue
        conf=(c[i]>h[i-1] and c[i]>e20[i]) if sg>0 else (c[i]<l[i-1] and c[i]<e20[i])
        if not conf: continue
        if cnt.get(day[i],0)>=maxday: continue
        j0=i+lat
        sw=l[i-5:i+1].min()-0.1*a[i] if sg>0 else h[i-5:i+1].max()+0.1*a[i]
        risk=(o[j0]-sw)*sg
        if risk<rmin or risk>rmax: continue
        if tp[0]=="scaled":
            r,j,_=R._run_scaled(o,h,l,c,j0,min(j0+hold,n-1),sg,sw,tp[1],tp[2])
        else:
            r,j=R._run_trade(o,h,l,c,j0,min(j0+hold,n-1),sg,sw,o[j0]+sg*tp[1]*risk)
        if r is None: continue
        busy=j; cnt[day[i]]=cnt.get(day[i],0)+1
        out.append((idx[j0],r,'long' if sg>0 else 'short',risk))
    return out
grid=list(itertools.product([0.5,0.7,1.0],[0.3,0.5],["ema","fvg"],[("scaled",1.0,3.0),("fixed",1.5),("fixed",2.0)]))
res=[]
for umin,move,trig,tp in grid:
    tr=run(umin,move,trig,tp=tp)
    old=np.array([x[1] for x in tr if x[0]<split]); new=np.array([x[1] for x in tr if x[0]>=split])
    if len(old)<30: continue
    res.append((old.mean(),umin,move,trig,tp,len(old),old.mean(),(old>0).mean(),len(new),new.mean() if len(new) else 0,(new>0).mean() if len(new) else 0,np.median([x[3] for x in tr])))
res.sort(reverse=True)
print("variants tried:",len(res))
for r in res[:8]+res[-3:]:
    _,u,m,t,tp,no,ro,wo,nn,rn,wn,sl=r
    print(f"used>={u} move>={m} {t:3} {str(tp):22} OLD n={no:3} avgR={ro:+.3f} win={wo*100:.0f}% | NEW n={nn:3} avgR={rn:+.3f} win={wn*100:.0f}% | SL ${sl:.1f}")
best=res[0]
print("BEST picked on OLD only:",best[1:5])
for lat in (1,2,3):
    tr=run(best[1],best[2],best[3],tp=best[4],lat=lat); j=R.judge([x[:3] for x in tr],split)
    print(f"  delay {lat*5}min: n={j['all']['trades']} win={j['all']['win_rate_pct']}% avgR={j['all']['avg_R']:+.3f} t={j['t_stat']} new30={j['newest_30pct']} q={j['positive_quarters']} proven={j['proven']}")
