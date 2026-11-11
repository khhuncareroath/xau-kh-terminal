"""🎰 Can a filter lift Fun Scalp above break-even? (11 Nov 2026). Live entries + live exits (⅓ at 1R / 1.5R / 2R, SL to
entry after TP1). One filter at a time; a filter counts only if it helps on BOTH the older 70% and the newest 30%.
Run: python studies/fun_filters.py"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
sys.path.insert(0, '/home/claude/xau-kh-terminal/studies')
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
b1 = R._bias(df, "1H", pd.Timedelta(hours=1))
day = np.array((df.index - pd.Timedelta(hours=18)).date)
hour_kh = np.array(df.index.tz_convert("Asia/Phnom_Penh").hour)
LEGS, TRAIL = [(1/3, 1), (1/3, 1.5), (1/3, 2)], [0, 0, None]


def run(j0, j_end, sg, stop):
    en = o[j0]; risk = (en - stop) * sg
    lv = lambda r: en + sg * r * risk
    st, got, left, k = stop, 0.0, 1.0, 0
    for j in range(j0, j_end + 1):
        if (l[j] <= st) if sg > 0 else (h[j] >= st):
            px = st if (j == j0 or k) else (min(st, o[j]) if sg > 0 else max(st, o[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk, j
        while k < 3 and ((h[j] >= lv(LEGS[k][1])) if sg > 0 else (l[j] <= lv(LEGS[k][1]))):
            got += LEGS[k][0] * LEGS[k][1]; left -= LEGS[k][0]
            if TRAIL[k] is not None:
                st = lv(TRAIL[k])
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk, j
    return got + left * (c[j_end] - en) * sg / risk - R.COST / risk, j_end


def sim(ok, per_day=2):
    """ok(i, sg, j0) -> bool. Same daily cap / one-at-a-time rules as live."""
    out, busy, used = [], -1, {}
    for i in range(300, n - 2):
        sg = 1 if b4[i] == "bull" else -1 if b4[i] == "bear" else 0
        if not sg or i <= busy or used.get(day[i], 0) >= per_day:
            continue
        sw = R.scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1
        risk = (o[j0] - sw) * sg
        if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1] or not ok(i, sg, j0):
            continue
        r, j = run(j0, min(j0 + R.SCALP_HOLD, n - 1), sg, sw)
        busy = j
        used[day[i]] = used.get(day[i], 0) + 1
        out.append((df.index[j0], r, "long" if sg > 0 else "short"))
    return out


_er = {}
def er(j0):
    if j0 not in _er:
        _er[j0] = R.efficiency(df, df.index[j0])
    return _er[j0]


base = None
def show(name, ok, per_day=2):
    global base
    tr = sim(ok, per_day)
    jd = R.judge(tr, split)
    r = np.array([x[1] for x in tr])
    o_, n_ = jd['older_70pct']['avg_R'], jd['newest_30pct']['avg_R']
    if base is None:
        base = (o_, n_)
    both = o_ > base[0] and n_ > base[1]
    print(f"{name:44} n={len(r):4d} ({len(r) / 24:4.1f}/mo) profit {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R t={jd['t_stat']:+.1f} "
          f"| older {o_:+.2f} newest {n_:+.2f} | q {jd['positive_quarters']} {'✅ both better' if both else ''}"
          f"{' · PROVEN' if jd['proven'] else ''}")


show("LIVE (no filter)", lambda i, sg, j0: True)
show("clean 4H trend (efficiency > 0.30)", lambda i, sg, j0: (er(j0) or 0) > R.CHOP_ER)
show("1H structure agrees too", lambda i, sg, j0: b1[i] == ("bull" if sg > 0 else "bear"))
show("clean trend + 1H agrees", lambda i, sg, j0: (er(j0) or 0) > R.CHOP_ER and b1[i] == ("bull" if sg > 0 else "bear"))
show("London + NY only (14:00-02:00 KH)", lambda i, sg, j0: hour_kh[i] >= 14 or hour_kh[i] < 2)
show("skip dead hours (03:00-08:00 KH)", lambda i, sg, j0: not 3 <= hour_kh[i] < 8)
show("clean trend + London/NY", lambda i, sg, j0: (er(j0) or 0) > R.CHOP_ER and (hour_kh[i] >= 14 or hour_kh[i] < 2))
show("clean trend, 3 a day", lambda i, sg, j0: (er(j0) or 0) > R.CHOP_ER, per_day=3)
