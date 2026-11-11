exec(open('/tmp/claude-0/-home-claude/68392953-2940-53f1-a9e8-1bce111706d0/scratchpad/momind.py').read().split("def run(")[0])
from ict import resample
d4=resample(df,"4H"); a4=atr(d4).to_numpy()
tr=R.trend_combo(df)
feats=[]
for t,r,dd in tr:
    sg=1 if dd=='long' else -1
    i=int(idx.searchsorted(t))-1-R.LAT        # last 5m bar of the breakout 4H candle (entry j0 = i+1+LAT)
    k=int(d4.index.searchsorted(t-pd.Timedelta(hours=4,minutes=20)))
    body=abs(d4.Close.iloc[k]-d4.Open.iloc[k])/a4[k] if a4[k]>0 else np.nan
    closepos=((d4.Close.iloc[k]-d4.Low.iloc[k])/(d4.High.iloc[k]-d4.Low.iloc[k]) if sg>0 else (d4.High.iloc[k]-d4.Close.iloc[k])/(d4.High.iloc[k]-d4.Low.iloc[k])) if d4.High.iloc[k]>d4.Low.iloc[k] else np.nan
    feats.append(dict(t=t,r=r,old=t<split,
        body=body, closepos=closepos,
        vwap=(c[i]-vwap[i])*sg>0, ema50=(c[i]-ema[50][i])*sg>0, ema200=(c[i]-ema[200][i])*sg>0,
        h1=b1[i]==sg,
        mom5=((c[i]-o[i])*sg>=1.0*a[i]),       # last 5m candle strong in the trade direction
        sess=180<=hm[i]<720))
F=pd.DataFrame(feats)
def rep(lab,mask):
    for part,pm in (("old",F.old),("new",~F.old)):
        z=F.r[mask&pm]; zz=F.r[~mask&pm]
        print(f"{lab:38} {part}: WITH n={len(z):3} win={100*(z>0).mean():3.0f}% avgR={z.mean():+.3f} | WITHOUT n={len(zz):3} win={100*(zz>0).mean():3.0f}% avgR={zz.mean():+.3f}")
print("all COMBO:", len(F), "win", round(100*(F.r>0).mean()), "avgR", round(F.r.mean(),3))
rep("strong 4H breakout candle (body>=1 ATR)", F.body>=1.0)
rep("4H candle closes near its extreme (top 25%)", F.closepos>=0.75)
rep("price on the right side of VWAP", F.vwap)
rep("price beyond EMA50 (5m)", F.ema50)
rep("price beyond EMA200 (5m)", F.ema200)
rep("1H structure agrees", F.h1)
rep("last 5m candle strong (momentum)", F.mom5)
rep("London/NY hours", F.sess)
rep("ALL his confirmations (VWAP+EMA200+1H)", F.vwap&F.ema200&F.h1)
