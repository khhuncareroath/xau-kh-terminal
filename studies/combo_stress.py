exec(open('/tmp/claude-0/-home-claude/68392953-2940-53f1-a9e8-1bce111706d0/scratchpad/combo_scale.py').read().split("for trig in")[0])
def J(tr): 
    j=R.judge([x[:3] for x in tr],split); return f"n={j['all']['trades']} win={j['all']['win_rate_pct']}% avgR={j['all']['avg_R']:+.3f} t={j['t_stat']} new={j['newest_30pct']['avg_R']} proven={j['proven']}"
print("BASE fvg 2R delay5     ", J(run2("fvg",("fixed",2.0))))
print("delay 10min            ", J(run2("fvg",("fixed",2.0),lat=2)))
print("delay 15min            ", J(run2("fvg",("fixed",2.0),lat=3)))
for rmin,rmax in ((2,10),(4,15),(3,20)):
    print(f"SL range ${rmin}-{rmax}        ", J(run2("fvg",("fixed",2.0),rmin=rmin,rmax=rmax)))
print("max 1/day              ", J(run2("fvg",("fixed",2.0),maxday=1)))
print("TP 2.5R                ", J(run2("fvg",("fixed",2.5))))
R.COST=0.7; print("cost $0.70             ", J(run2("fvg",("fixed",2.0)))); R.COST=0.4
# luck test: same windows, random 5m bars with FVG-touch removed (any bar, same direction, same stop rule)
rng=np.random.default_rng(3); real=np.mean([x[1] for x in run2("fvg",("fixed",2.0))])
cand=[i for i in range(300,n-50) if act[i]!=0]
means=[]
for _ in range(300):
    rs=[]
    for i in rng.choice(cand,198,replace=False):
        sg=int(act[i]); j0=i+1; sw=l[i-5:i+1].min()-0.1*a[i] if sg>0 else h[i-5:i+1].max()+0.1*a[i]
        risk=(o[j0]-sw)*sg
        if risk<3 or risk>12: continue
        r,_=R._run_trade(o,h,l,c,j0,min(j0+36,n-1),sg,sw,o[j0]+sg*2*risk)
        if r is not None: rs.append(r)
    means.append(np.mean(rs))
means=np.array(means)
print(f"LUCK: real {real:+.3f} vs random entries in same direction & windows: mean {means.mean():+.3f}, top5% {np.percentile(means,95):+.3f}, p={(means>=real).mean():.3f}")
