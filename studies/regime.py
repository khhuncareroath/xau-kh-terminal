import sys; sys.path.insert(0,'/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from engine import atr
from ict import resample
from levels import to_ny
df=to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split=df.index[int(len(df)*0.7)]
d4=resample(df,"4H"); c4=d4['Close']; h4=d4['High']; l4=d4['Low']
er=(c4-c4.shift(30)).abs()/(c4.diff().abs().rolling(30).sum())          # efficiency: 1 = straight trend, 0 = chop
tr=pd.concat([h4-l4,(h4-c4.shift()).abs(),(l4-c4.shift()).abs()],axis=1).max(axis=1)
up=h4.diff(); dn=-l4.diff()
pdm=np.where((up>dn)&(up>0),up,0.0); ndm=np.where((dn>up)&(dn>0),dn,0.0)
atr14=tr.ewm(alpha=1/14).mean()
pdi=100*pd.Series(pdm,index=d4.index).ewm(alpha=1/14).mean()/atr14; ndi=100*pd.Series(ndm,index=d4.index).ewm(alpha=1/14).mean()/atr14
adx=(100*(pdi-ndi).abs()/(pdi+ndi)).ewm(alpha=1/14).mean()
width=(h4.rolling(30).max()-l4.rolling(30).min())/atr14     # range width in ATRs: small = tight squeeze
feats={"efficiency":er,"ADX":adx,"range/ATR":width}
def at(series, t):   # value of the 4H candle that just closed before entry t
    k=d4.index.searchsorted(t-pd.Timedelta(hours=4,minutes=20))
    return series.iloc[max(0,min(k,len(series)-1))]
for name, fn in (("trend_intraday",R.trend_intraday),("trend_combo",R.trend_combo)):
    trd=fn(df)
    for fname,s in feats.items():
        v=np.array([at(s,x[0]) for x in trd]); r=np.array([x[1] for x in trd]); old=np.array([x[0]<split for x in trd])
        qs=np.nanpercentile(v[old],[33,67])
        lo=v<=qs[0]; mid=(v>qs[0])&(v<=qs[1]); hi=v>qs[1]
        def g(mask): 
            return f"{r[mask].mean():+.3f}({mask.sum()})"
        print(f"{name:14} {fname:10} low third old {g(lo&old)} new {g(lo&~old)} | mid old {g(mid&old)} new {g(mid&~old)} | high old {g(hi&old)} new {g(hi&~old)}")
print("----")
trd=R.trend_intraday(df)
v=np.array([at(er,x[0]) for x in trd]); r=np.array([x[1] for x in trd]); old=np.array([x[0]<split for x in trd])
du=np.array([(R.day_used(df,x[0]) or 0) for x in trd])
th=np.nanpercentile(v[old],33); print("threshold (picked on old 70%)", round(th,3))
for lab,m in (("normal day & choppy",(du<0.7)&(v<=th)),("normal day & trending",(du<0.7)&(v>th)),("COMBO & choppy",(du>=0.7)&(v<=th)),("COMBO & trending",(du>=0.7)&(v>th))):
    for part,pm in (("old",old),("new",~old)):
        z=r[m&pm]; print(f"{lab:24} {part} n={len(z):3} win={100*(z>0).mean() if len(z) else 0:3.0f}% avgR={z.mean() if len(z) else 0:+.3f}")
