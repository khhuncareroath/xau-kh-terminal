exec(open("newsplay.py").read().split("\nfor k in (1.2")[0])
import research as R
ev=events(1.2,3)
evt=np.array([idx[e['i']].value for e in ev])
for name in ("trend_intraday","trend_combo","trend_premium"):
    tr=getattr(R,name)(df)
    near=[];far=[];after=[]
    for x in tr:
        t=x[0].value
        d=(evt-t)/6e10  # minutes until event (positive = event later)
        if ((d>0)&(d<=240)).any(): near.append(x)        # news within the next 4h of entry
        elif ((d<=0)&(d>-120)).any(): after.append(x)     # entry within 2h after news
        else: far.append(x)
    for lab,z in (("news in next 4h",near),("just after news",after),("no news",far)):
        r=np.array([v[1] for v in z]); 
        print(f"{name:15} {lab:16} n={len(r):3} win={100*(r>0).mean() if len(r) else 0:3.0f}% avgR={r.mean() if len(r) else 0:+.3f}")
