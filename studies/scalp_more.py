"""More scalps? (11 Nov 2026, owner: '2-3 a month is too few'). The same 5m scalp entry (research.scalp_trigger: dip into a
fresh 15m FVG, close back beyond the previous candle and EMA20, SL under the last 6 candles $3-12, TP 2R, 3 h) after
LOOSER triggers. Chosen on the older 70%, checked on the newest 30%.  Run: python studies/scalp_more.py"""
import json
import sys

sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd

import research as R
from engine import atr
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
n = len(df)
split = df.index[int(n * 0.7)]
o, h, l, c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
a = atr(df).to_numpy()
e20 = pd.Series(c).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
day = np.array((df.index - pd.Timedelta(hours=18)).date)
loc_h = np.array(df.index.tz_convert("Asia/Phnom_Penh").hour)


def run(act, per_day=1, night=True):
    out, busy, used = [], -1, {}
    for i in range(300, n - 2):
        sg = int(act[i])
        if sg == 0 or i <= busy or used.get(day[i], 0) >= per_day or (not night and loc_h[i] < 6):
            continue
        sw = R.scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1
        risk = (o[j0] - sw) * sg
        if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1]:
            continue
        r, j = R._run_trade(o, h, l, c, j0, min(j0 + R.SCALP_HOLD, n - 1), sg, sw, o[j0] + sg * R.SCALP_RR * risk)
        if r is None:
            continue
        busy = j
        used[day[i]] = used.get(day[i], 0) + 1
        out.append((df.index[j0], r, "long" if sg > 0 else "short"))
    return out


def windows(trades, hours=12):
    act = np.zeros(n)
    for t, _, d in trades:
        i = int(df.index.searchsorted(t))
        act[i + 3:min(i + hours * 12, n)] = 1 if d == "long" else -1
    return act


def bias(tf):
    b = R._bias(df, tf, pd.Timedelta(hours=4 if tf == "4H" else 1))
    return np.array([1 if x == "bull" else -1 if x == "bear" else 0 for x in b])


def st(name, tr):
    r = np.array([x[1] for x in tr]); old = np.array([x[0] < split for x in tr])
    if len(r) < 10:
        print(f"{name:52} n={len(r)}"); return
    t = r.mean() / r.std(ddof=1) * np.sqrt(len(r))
    j = R.judge(tr, split)
    print(f"{name:52} n={len(r):4d} ({len(r) / 24:4.1f}/mo) win {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R t {t:+.1f} "
          f"| older {r[old].mean():+.2f} newest {r[~old].mean():+.2f} | {j['positive_quarters']} proven={j['proven']}")


combo = R.trend_combo(df)
intr = R.trend_intraday(df)
b4, b1 = bias("4H"), bias("1H")
du_ok = [t for t in intr if (R.day_used(df, t[0]) or 0) >= 0.7]
st("A  now: after A+/B+ breakout (12h)", run(windows(combo)))
st("A2 same, up to 2 a day", run(windows(combo), 2))
st("A3 same, window 24h", run(windows(combo, 24)))
st("B  after ANY 4H breakout (12h)", run(windows(intr)))
st("C  after 4H breakout + Day Meter 70% (12h)", run(windows(du_ok)))
st("D  whenever 4H structure points that way", run(b4))
st("E  4H + 1H structure agree", run(np.where(b4 == b1, b4, 0)))
st("E2 same, up to 2 a day", run(np.where(b4 == b1, b4, 0), 2))
st("E3 same, no night (00-06 Cambodia)", run(np.where(b4 == b1, b4, 0), 1, night=False))
st("F  4H+1H agree OR A+/B+ window", run(np.where(windows(combo) != 0, windows(combo), np.where(b4 == b1, b4, 0))))
try:   # G: after the live M15 signals (replay), same direction, 8 h
    rp = json.load(open('/tmp/m15_e.json')) + json.load(open('/tmp/m15_f.json'))
    act = np.zeros(n)
    for x in rp:
        i = int(df.index.searchsorted(pd.Timestamp(x["t"])))
        act[i + 1:min(i + 96, n)] = 1 if x["dir"] == "bull" else -1
    st("G  after an M15 A+/B+ signal (8h)", run(act))
except Exception as e:
    print("G skipped:", e)
