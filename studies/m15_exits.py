"""Same M15 entries (saved 2-year replay), different exits. 12 Nov 2026. Hold until midnight Cambodia / 8h like live."""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R
from levels import to_ny
df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
split = df.index[int(len(df) * 0.7)]
rows = {}
for f in sorted(glob.glob("/tmp/m15_[a-f].json")):
    for r in json.load(open(f)): rows[r["t"]] = r
X = [r for r in rows.values() if r["kind"] == "break"]
kh = df.index.tz_convert("Asia/Phnom_Penh")

def run(r, legs, be=True, use_zone=False):
    sg = 1 if r["dir"] == "bull" else -1
    en, st = r["entry"], r["stop"]; risk = abs(en - st); j0 = r["j0"]
    mid = kh[j0].normalize() + pd.Timedelta(days=1)
    jend = min(j0 + 96, len(df) - 1)
    while jend > j0 and kh[jend] >= mid: jend -= 1
    tg = [r["tp1p"], r["tp2p"]] if use_zone else [en + sg * x * risk for _, x in legs]
    stop, got, left, k = st, 0.0, 1.0, 0
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            return got + left * (stop - en) * sg / risk - .4 / risk
        while k < len(legs) and ((H[j] >= tg[k]) if sg > 0 else (L[j] <= tg[k])):
            got += legs[k][0] * abs(tg[k] - en) / risk; left -= legs[k][0]
            if be: stop = en
            k += 1
        if left <= 1e-9: return got - .4 / risk
    return got + left * (C[jend] - en) * sg / risk - .4 / risk

PL = {"LIVE zone TP1/TP2, half + BE": ([(.5, 0), (.5, 0)], True, True),
      "half 1R + BE, rest 2R": ([(.5, 1), (.5, 2)], True, False),
      "half 1R + BE, rest 3R": ([(.5, 1), (.5, 3)], True, False),
      "half 1.5R + BE, rest 3R": ([(.5, 1.5), (.5, 3)], True, False),
      "one target 2R": ([(1, 2)], False, False),
      "one target 3R": ([(1, 3)], False, False),
      "LIVE zones, no BE": ([(.5, 0), (.5, 0)], False, True)}
for tier in ("A+", "all"):
    print("==", tier)
    for name, (legs, be, z) in PL.items():
        tr = [(pd.Timestamp(r["t"]), run(r, legs, be, z)) for r in X if tier == "all" or r["tier"] == tier]
        jd = R.judge(tr, split); rr = np.array([x[1] for x in tr])
        print(f"{name:32} n={len(rr)} avg {rr.mean():+.3f}R profit {100*(rr>0).mean():.0f}% t={jd['t_stat']:+.1f} "
              f"older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f} q {jd['positive_quarters']}")
