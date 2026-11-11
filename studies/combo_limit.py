exec(open('/tmp/claude-0/-home-claude/68392953-2940-53f1-a9e8-1bce111706d0/scratchpad/combo_scale.py').read().split("def run2")[0])
# list of 15m FVGs with the bar index at which they become known
fvgs=[]
for k in range(2,len(d15)):
    i=idx.searchsorted(d15.index[k]+pd.Timedelta(minutes=15))
    if i>=n-60: break
    if L15[k]>H15[k-2]: fvgs.append((i,1,H15[k-2],L15[k]))
    elif H15[k]<L15[k-2]: fvgs.append((i,-1,H15[k],L15[k-2]))
def run3(edge="near", tp=2.0, place_lat=2, valid=24, rmin=3, rmax=12, maxday=1, hold=36, buf=0.1):
    out=[]; busy=-1; cnt={}
    for i,sg,lo,hi in fvgs:
        if act[i]!=sg: continue
        p=i+place_lat
        if p<=busy or cnt.get(day[i],0)>=maxday: continue
        en=(hi if sg>0 else lo) if edge=="near" else (lo+hi)/2
        sl=(lo-buf*a[i]) if sg>0 else (hi+buf*a[i])
        risk=(en-sl)*sg
        if risk<rmin or risk>rmax: continue
        tgt=en+sg*tp*risk
        if ((c[p-1]-en)*sg)<=0: continue       # price already at/through the entry when the order goes in: skip
        fill=None
        for j in range(p, min(p+valid,n-1)):
            if (h[j]>=tgt) if sg>0 else (l[j]<=tgt): break    # ran to target without us
            if (l[j]<=en) if sg>0 else (h[j]>=en): fill=j; break
        if fill is None: continue
        res=None
        for j in range(fill, min(fill+hold,n-1)):
            if (l[j]<=sl) if sg>0 else (h[j]>=sl): res=-1.0; break
            if j>fill and ((h[j]>=tgt) if sg>0 else (l[j]<=tgt)): res=tp; break
        if res is None: res=(c[j]-en)*sg/risk
        res-=R.COST/risk
        busy=j; cnt[day[i]]=cnt.get(day[i],0)+1; out.append((idx[fill],res,'long' if sg>0 else 'short',risk))
    return out
def J(tr):
    j=R.judge([x[:3] for x in tr],split); return f"n={j['all']['trades']} win={j['all']['win_rate_pct']}% avgR={j['all']['avg_R']:+.3f} t={j['t_stat']} old={j['older_70pct']['avg_R']} new={j['newest_30pct']['avg_R']} q={j['positive_quarters']} SL=${np.median([x[3] for x in tr]) if tr else 0:.1f} proven={j['proven']}"
for edge in ("near","mid"):
    for tp in (1.5,2.0,3.0):
        for md in (1,2):
            print(f"limit {edge:4} TP{tp} max{md}/day:", J(run3(edge,tp,maxday=md)))
print("placement delay 15min:", J(run3("near",2.0,place_lat=3)))
print("placement delay 25min:", J(run3("near",2.0,place_lat=5)))
