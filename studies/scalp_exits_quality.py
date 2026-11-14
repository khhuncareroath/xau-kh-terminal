"""⚡ Scalp exits for fewer full SL hits (owner, 14 Nov 2026: SL hits make the group look bad).
Same wide_scalp entries; exits: live 2R all-in · half at 1R + SL to entry, rest 2R · half 1R + BE, rest 3R ·
thirds 1/1.5/2R (BE after the first) · all at 1.5R. Reports full-loss %, no-loss %, R. With and without the 1.0R other-side filter.
Run: python studies/scalp_exits_quality.py"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R, arrays
from levels import to_ny
from engine import atr
exec(open('/home/claude/xau-kh-terminal/studies/quality_filters.py').read().split("def feats")[0].split("b1 = R._bias")[0])
Z = {}
for tf in ("15m", "30m", "1H", "4H", "D"):
    zs = arrays.zones(df, tf)
    Z[tf] = (np.array([z["dir"] == "bull" for z in zs]), np.array([z["lo"] for z in zs]), np.array([z["hi"] for z in zs]),
             np.array([z["t0"].value for z in zs]), np.array([z["t1"].value for z in zs]))
src = open('/home/claude/xau-kh-terminal/studies/quality_filters.py').read()
exec("def opp_dist" + src.split("def opp_dist")[1].split("def feats")[0])
N = len(df)


def run(j0, sg, stop, legs, be=True):
    en = O[j0]; risk = (en - stop) * sg; lv = [en + sg * x * risk for x, _ in legs]
    st, got, left, k = stop, 0.0, 1.0, 0
    jend = min(j0 + R.SCALP_HOLD, N - 1)
    for j in range(j0, jend + 1):
        if (L[j] <= st) if sg > 0 else (H[j] >= st):
            px = st if (j == j0 or k) else (min(st, O[j]) if sg > 0 else max(st, O[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk
        while k < len(legs) and ((H[j] >= lv[k]) if sg > 0 else (L[j] <= lv[k])):
            got += legs[k][0] * legs[k][1]; left -= legs[k][1]
            if k == 0 and be: st = en
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk
    return got + left * (C[jend] - en) * sg / risk - R.COST / risk


e20 = pd.Series(C).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
a_ = atr(df).to_numpy()
E = []
for t, r, side in R.wide_scalp(df):
    j0 = int(df.index.searchsorted(t)); sg = 1 if side == "long" else -1
    sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, j0 - 1, sg)
    if sw is None: continue
    E.append((t, j0, sg, sw, opp_dist(t, O[j0], sg, (O[j0] - sw) * sg) > 1.0, r))
VAR = {"live: all at 2R": [(2, 1.0)], "half 1R + BE, rest 2R": [(1, .5), (2, .5)], "half 1R + BE, rest 3R": [(1, .5), (3, .5)],
       "thirds 1/1.5/2R + BE": [(1, 1/3), (1.5, 1/3), (2, 1/3)], "all at 1.5R": [(1.5, 1.0)], "all at 1R": [(1, 1.0)]}
for flt in (False, True):
    print(f"\n== ⚡ Scalp {'+ no opposite zone <1R' if flt else '(all, as live)'}")
    for name, legs in VAR.items():
        rs = np.array([run(j0, sg, sw, legs, be=len(legs) > 1) for (t, j0, sg, sw, f4, r) in E if f4 or not flt])
        ts = np.array([t >= split for (t, j0, sg, sw, f4, r) in E if f4 or not flt])
        print(f"  {name:24s} {len(rs)} | full SL {100*(rs <= -0.9).mean():3.0f}% · no loss {100*(rs > -0.1).mean():3.0f}% · "
              f"{rs.mean():+.3f}R (old {rs[~ts].mean():+.2f} / new {rs[ts].mean():+.2f}) total {rs.sum():+.0f}R")
