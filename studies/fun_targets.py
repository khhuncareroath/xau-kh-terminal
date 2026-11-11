"""🎰 Fun Scalp with TP1/TP2/TP3 (11 Nov 2026). Same entries as the live funscalp.py (4H structure direction, 15m FVG dip,
5m close back over the previous candle + EMA20, SL under the last 6 candles, $3-12, 2 a day, one at a time, 3 h max),
different ways to take profit. Next-candle open entry, $0.40 cost. Run: python studies/fun_targets.py"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd
import research as R
from engine import atr
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
n = len(df)
a = atr(df).to_numpy()
e20 = pd.Series(c).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))
day = np.array((df.index - pd.Timedelta(hours=18)).date)
PER_DAY = 2


def exit_legs(j0, j_end, sg, stop, legs, trail):
    """legs: [(fraction, R target)], ascending. After the k-th target the stop moves to trail[k] (in R, 0 = entry).
    Returns (R after cost, exit index, number of targets hit)."""
    en = o[j0]
    risk = (en - stop) * sg
    lv = lambda r: en + sg * r * risk
    st, got, left, k = stop, 0.0, 1.0, 0
    for j in range(j0, j_end + 1):
        if (l[j] <= st) if sg > 0 else (h[j] >= st):
            px = st if (j == j0 or k) else (min(st, o[j]) if sg > 0 else max(st, o[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk, j, k
        while k < len(legs) and ((h[j] >= lv(legs[k][1])) if sg > 0 else (l[j] <= lv(legs[k][1]))):
            got += legs[k][0] * legs[k][1]; left -= legs[k][0]
            if trail[k] is not None:
                st = lv(trail[k])
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk, j, k
    return got + left * (c[j_end] - en) * sg / risk - R.COST / risk, j_end, k


PLANS = {
    "A  one target 2R (old)":                 ([(1, 2)], [None]),
    "B  ½ TP1 → rest TP3, SL→entry (LIVE)":   ([(.5, 1), (.5, 3)], [0, None]),
    "C  ½ TP1 → rest TP2, SL→entry":          ([(.5, 1), (.5, 2)], [0, None]),
    "D  ⅓ TP1 · ⅓ TP2 · ⅓ TP3, SL trails":    ([(1/3, 1), (1/3, 2), (1/3, 3)], [0, 1, None]),
    "E  ⅓ each, SL→entry only":               ([(1/3, 1), (1/3, 2), (1/3, 3)], [0, 0, None]),
    "F  one target 1R":                       ([(1, 1)], [None]),
    "G  one target 3R":                       ([(1, 3)], [None]),
    "H  ½ TP1 → rest TP3, SL stays (no BE)":  ([(.5, 1), (.5, 3)], [None, None]),
}

for name, (legs, trail) in PLANS.items():
    out, busy, used, hits = [], -1, {}, []
    for i in range(300, n - 2):
        sg = 1 if b4[i] == "bull" else -1 if b4[i] == "bear" else 0
        if not sg or i <= busy or used.get(day[i], 0) >= PER_DAY:
            continue
        sw = R.scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1
        risk = (o[j0] - sw) * sg
        if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1]:
            continue
        r, j, k = exit_legs(j0, min(j0 + R.SCALP_HOLD, n - 1), sg, sw, legs, trail)
        busy = j
        used[day[i]] = used.get(day[i], 0) + 1
        out.append((df.index[j0], r, "long" if sg > 0 else "short")); hits.append(k)
    jd = R.judge(out, split)
    rr = np.array([x[1] for x in out]); hk = np.array(hits)
    eq = np.cumsum(rr); dd = (np.maximum.accumulate(eq) - eq).max()
    streak = mx = 0
    for v in rr:
        streak = streak + 1 if v < 0 else 0; mx = max(mx, streak)
    print(f"{name:40} n={len(rr)} ({len(rr) / 24:.0f}/mo) avg {rr.mean():+.3f}R t={jd['t_stat']:+.1f} "
          f"older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f} | "
          f"TP1 {100 * (hk >= 1).mean():.0f}% TP2 {100 * (hk >= 2).mean():.0f}% TP3 {100 * (hk >= 3).mean():.0f}% | "
          f"in profit {100 * (rr > 0).mean():.0f}% | worst run {mx} losses, max drop {dd:.1f}R | quarters {jd['positive_quarters']}"
          f" | {'PROVEN' if jd['proven'] else 'not proven'}")
