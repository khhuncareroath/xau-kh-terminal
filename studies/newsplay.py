import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from research import _run_trade, _run_scaled, judge, COST, LAT, _bias
from engine import atr
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
o,h,l,c=(df[k].to_numpy() for k in ("Open","High","Low","Close"))
a=atr(df).to_numpy(); n=len(df); idx=df.index
split=idx[int(n*0.7)]
hm=idx.hour*60+idx.minute
bD=_bias(df,"D",pd.Timedelta(hours=24)); b4=_bias(df,"4H",pd.Timedelta(hours=4))

def events(k=2.5, react=3, times=(510,600,840)):
    ev=[]
    for i in np.where(np.isin(hm,times) & (idx.dayofweek<5))[0]:
        if i<24 or i+react+40>=n: continue
        pre=np.median(h[i-12:i]-l[i-12:i])   # normal 5m range in the hour before
        rh=h[i:i+react].max(); rl=l[i:i+react].min()
        if pre<=0 or (rh-rl) < k*react*pre or (rh-rl) < o[i]*0.0015: continue
        ev.append(dict(i=i, rh=rh, rl=rl, dir=1 if c[i+react-1]>o[i] else -1, react=react))
    return ev

def s_cont(ev, tp1=1.0, tp2=2.0, hold=48, stop_frac=1.0):
    out=[]; busy=-1
    for e in ev:
        i,r,sg=e['i'],e['react'],e['dir']
        j0=i+r+LAT-1
        if j0<=busy: continue
        ext = e['rl'] if sg>0 else e['rh']
        stop = o[j0] - sg*abs(o[j0]-ext)*stop_frac
        if (o[j0]-stop)*sg <= 0.5: continue
        res, j, _ = _run_scaled(o,h,l,c,j0,min(j0+hold,n-1),sg,stop,tp1,tp2)
        if res is None: continue
        busy=j; out.append((idx[j0],res,'bull' if sg>0 else 'bear'))
    return out

def s_pullback(ev, fib=0.5, inval=0.786, window=15, tp2_ext=0.618, hold=48):
    out=[]; busy=-1
    for e in ev:
        i,r,sg=e['i'],e['react'],e['dir']
        start=o[i]; ext=e['rh'] if sg>0 else e['rl']; leg=abs(ext-start)
        entry=ext - sg*fib*leg; stop=ext - sg*inval*leg - sg*0.5
        tp1=ext; tp2=ext+sg*tp2_ext*leg
        j0=i+r+LAT-1
        if j0<=busy: continue
        fill=None
        for j in range(j0, min(j0+window, n-1)):
            if (sg>0 and h[j]>tp1) or (sg<0 and l[j]<tp1): break       # left without us
            if (sg>0 and l[j]<=entry) or (sg<0 and h[j]>=entry): fill=j; break
        if fill is None: continue
        risk=(entry-stop)*sg
        if risk<=0.5: continue
        # simulate from fill bar with entry price = entry
        res=None; half=False; sl=stop
        for j in range(fill, min(fill+hold, n-1)):
            if (l[j]<=sl) if sg>0 else (h[j]>=sl):
                res=(0.5*(tp1-entry)*sg/risk if half else (sl-entry)*sg/risk); break
            if not half and ((h[j]>=tp1) if sg>0 else (l[j]<=tp1)):
                half=True; sl=entry
            if half and ((h[j]>=tp2) if sg>0 else (l[j]<=tp2)):
                res=0.5*(tp1-entry)*sg/risk+0.5*(tp2-entry)*sg/risk; break
        if res is None:
            px=c[min(fill+hold,n-1)-1]; res=(0.5*(tp1-entry)*sg/risk+0.5*(px-entry)*sg/risk) if half else (px-entry)*sg/risk
        res-=COST/risk
        busy=fill+hold; out.append((idx[fill],res,'bull' if sg>0 else 'bear'))
    return out

def s_fade(ev, window=12, rr=2.0, hold=48):
    out=[]; busy=-1
    for e in ev:
        i,r,sg=e['i'],e['react'],e['dir']
        for j in range(i+r, min(i+r+window, n-1)):
            if (c[j]-o[i])*sg < 0:     # closed back beyond the pre-news price: the first move failed
                j0=j+LAT
                if j0<=busy or j0>=n-1: break
                ext=e['rh'] if sg>0 else e['rl']; s2=-sg
                stop=max(ext, h[i:j0].max()) if s2<0 else min(ext, l[i:j0].min())
                risk=(o[j0]-stop)*s2
                if risk<=0.5: break
                res,jj=_run_trade(o,h,l,c,j0,min(j0+hold,n-1),s2,stop,o[j0]+s2*rr*risk)
                if res is not None: busy=jj; out.append((idx[j0],res,'bull' if s2>0 else 'bear'))
                break
    return out

def s_lean(ev, pct=0.004, rr=2.0, hold=24, bias=bD):
    out=[]; busy=-1
    for e in ev:
        i=e['i']; j0=i-3
        sg=bias[j0]
        if j0<=busy: continue
        sg=1 if sg=='bull' else -1 if sg=='bear' else 0
        if sg==0: continue
        stop=o[j0]-sg*o[j0]*pct
        res,jj=_run_trade(o,h,l,c,j0,min(j0+hold,n-1),sg,stop,o[j0]+sg*rr*o[j0]*pct)
        if res is not None: busy=jj; out.append((idx[j0],res,'bull' if sg>0 else 'bear'))
    return out

def show(name, tr):
    j=judge(tr, split)
    print(f"{name:42} n={j['all']['trades']:4} win={j['all']['win_rate_pct']}% avgR={j['all']['avg_R']:+.3f} t={j['t_stat']:+.2f} new30={j['newest_30pct']['avg_R']} q={j['positive_quarters']} proven={j['proven']}")
    return j

for k in (1.2,1.6,2.0,3.0):
  for react in (3,6):
    ev=events(k,react)
    print(f"--- k={k} react={react*5}min events={len(ev)}")
    show("continuation 1R/2R", s_cont(ev))
    show("continuation 1R/3R stop half", s_cont(ev,1,3,stop_frac=0.5))
    show("pullback 50% (postnews model)", s_pullback(ev))
    show("pullback 61.8%", s_pullback(ev,fib=0.618))
    show("fade failed move 2R", s_fade(ev))
    show("lean before (daily bias) 2R", s_lean(ev))
