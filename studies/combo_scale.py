exec(open('/tmp/claude-0/-home-claude/68392953-2940-53f1-a9e8-1bce111706d0/scratchpad/trendday.py').read().split("grid=list")[0])
combo=R.trend_combo(df)
act=np.zeros(n)
for t,r_,d in combo:
    i=idx.searchsorted(t); act[i+3:min(i+144,n)]=1 if d=='long' else -1
def run2(trig="ema", tp=("fixed",1.5), lat=1, rmin=3, rmax=12, maxday=2, hold=36):
    out=[]; busy=-1; cnt={}
    for i in range(300,n-hold-5):
        sg=int(act[i])
        if sg==0 or i<=busy: continue
        if trig=="ema":
            touched=(l[i-3:i+1].min()<=e20[i]) if sg>0 else (h[i-3:i+1].max()>=e20[i])
        else:
            touched=fv_dir[i]==sg and ((l[i-3:i+1].min()<=fv_hi[i]) if sg>0 else (h[i-3:i+1].max()>=fv_lo[i]))
        conf=(c[i]>h[i-1] and c[i]>e20[i]) if sg>0 else (c[i]<l[i-1] and c[i]<e20[i])
        if not (touched and conf) or cnt.get(day[i],0)>=maxday: continue
        j0=i+lat; sw=l[i-5:i+1].min()-0.1*a[i] if sg>0 else h[i-5:i+1].max()+0.1*a[i]
        risk=(o[j0]-sw)*sg
        if risk<rmin or risk>rmax: continue
        if tp[0]=="scaled": r,j,_=R._run_scaled(o,h,l,c,j0,min(j0+hold,n-1),sg,sw,tp[1],tp[2])
        else: r,j=R._run_trade(o,h,l,c,j0,min(j0+hold,n-1),sg,sw,o[j0]+sg*tp[1]*risk)
        if r is None: continue
        busy=j; cnt[day[i]]=cnt.get(day[i],0)+1; out.append((idx[j0],r,'long' if sg>0 else 'short',risk))
    return out
for trig in ("ema","fvg"):
    for tp in (("fixed",1.5),("fixed",2.0),("scaled",1.0,3.0)):
        tr=run2(trig,tp); j=R.judge([x[:3] for x in tr],split)
        print(f"{trig} {str(tp):22} n={j['all']['trades']} win={j['all']['win_rate_pct']}% avgR={j['all']['avg_R']:+.3f} t={j['t_stat']} old={j['older_70pct']['avg_R']} new={j['newest_30pct']['avg_R']} q={j['positive_quarters']} SL=${np.median([x[3] for x in tr]):.1f} proven={j['proven']}")
