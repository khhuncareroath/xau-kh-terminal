exec(open('/tmp/claude-0/-home-claude/68392953-2940-53f1-a9e8-1bce111706d0/scratchpad/combo_stress.py').read().split('print("BASE')[0])
for cost in (0.4,0.7,1.0):
    R.COST=cost
    for tp in (("fixed",2.0),("fixed",1.5),("scaled",1.0,3.0)):
        print(f"first pullback only, cost ${cost}, {tp}:", J(run2("fvg",tp,maxday=1)))
R.COST=0.7
tr=run2("fvg",("fixed",2.0),maxday=1); r=np.array([x[1] for x in tr])
s=m=0
for v in r: s=s+1 if v<=0 else 0; m=max(m,s)
print("max losing streak", m, "per week", len(r)/((idx[-1]-idx[0]).days/7))
