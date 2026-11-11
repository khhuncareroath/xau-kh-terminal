"""⚡ Scalp: 2 vs 3 vs 4 a day, and a 36 h window (12 Nov 2026). Same entries/exits as live wide_scalp."""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
trig = R.trend_intraday(df)
for name, hours, pd_ in (("LIVE 24h · 2/day", 24, 2), ("24h · 3/day", 24, 3), ("24h · 4/day", 24, 4),
                         ("36h · 2/day", 36, 2), ("36h · 3/day", 36, 3), ("48h · 3/day", 48, 3)):
    tr = R._scalp(df, trig, hours, pd_, 1, clean=True)
    jd = R.judge(tr, split); rr = np.array([x[1] for x in tr])
    st = mx = 0
    for v in rr: st = st + 1 if v < 0 else 0; mx = max(mx, st)
    print(f"{name:18} n={len(rr)} ({len(rr)/24:.1f}/mo) win {100*(rr>0).mean():.0f}% avg {rr.mean():+.3f}R t={jd['t_stat']:+.1f} "
          f"older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f} q {jd['positive_quarters']} "
          f"worst run {mx}{' · PROVEN' if jd['proven'] else ''}")
