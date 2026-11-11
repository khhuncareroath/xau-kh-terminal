"""Owner's mentor model, 1-2 setups a day (11 Nov 2026, night):
HTF key level (Daily / 4H / 1H FVG + OB, previous-day high/low, Asia high/low) -> price taps it -> LTF confirmation on
15m or 5m (optional liquidity sweep, then MSS with displacement) -> LIMIT at the OB, SL under the OB (mentor) or under
the sweep, TP 2R, max 2 trades a day, one at a time, out after 8 h. Every zone can be used up to twice.
Variants are judged on the OLDER 70%; the NEWEST 30% is the check.  Run: python studies/ltf_ict.py
"""
import itertools
import sys

sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd

import ict
import splus
from engine import atr
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
IDX, N = df.index, len(df)
COST, LIMIT_BARS, HOLD_BARS = 0.4, 24, 96

zD, bD = splus._zones(df, "D", 30)
z4, b4 = splus._zones(df, "4H", 15)
z1, _ = splus._zones(df, "1H", 5)
dD = ict.resample(df, "D")
aD = atr(dD).to_numpy()
liq = []
for i in range(1, len(dD)):   # previous day high / low: liquidity, price swept there -> reverse
    t0 = dD.index[i]; t1 = t0 + pd.Timedelta(hours=24); w = 0.08 * aD[i - 1]
    if not np.isfinite(w):
        continue
    ph, pl = dD["High"].iloc[i - 1], dD["Low"].iloc[i - 1]
    liq += [dict(dir="bear", lo=ph - w, hi=ph + w, t0=t0, t1=t1, tf="PDH"), dict(dir="bull", lo=pl - w, hi=pl + w, t0=t0, t1=t1, tf="PDL")]
day = (IDX - pd.Timedelta(hours=18)).date
asia = df[(IDX.hour >= 19) | (IDX.hour < 2)]
for d, g in asia.groupby((asia.index - pd.Timedelta(hours=18)).date):
    if len(g) < 30:
        continue
    t0 = pd.Timestamp(d, tz=IDX.tz) + pd.Timedelta(hours=26); t1 = t0 + pd.Timedelta(hours=15)
    w = 0.1 * (g.High.max() - g.Low.min())
    liq += [dict(dir="bear", lo=g.High.max() - w, hi=g.High.max() + w, t0=t0, t1=t1, tf="AsiaH"),
            dict(dir="bull", lo=g.Low.min() - w, hi=g.Low.min() + w, t0=t0, t1=t1, tf="AsiaL")]
ZONES = {"D+4H": zD + z4, "D+4H+1H": zD + z4 + z1, "all+liquidity": zD + z4 + z1 + liq}


def bars(tf):
    d = df if tf == "5m" else ict.resample(df, tf)
    o, h, l, c = (d[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    a = atr(d).to_numpy()
    n = len(d)
    sh, sl = np.full(n, np.nan), np.full(n, np.nan)
    lh = ll = np.nan
    for j in range(n):
        k = j - 2
        if k >= 2:
            if h[k] == h[k - 2:k + 3].max():
                lh = h[k]
            if l[k] == l[k - 2:k + 3].min():
                ll = l[k]
        sh[j], sl[j] = lh, ll
    step = pd.Timedelta(minutes=5 if tf == "5m" else 15)
    return dict(o=o, h=h, l=l, c=c, a=a, sh=sh, sl=sl, t=d.index, end=d.index + step, n=n, win=72 if tf == "5m" else 24)


BARS = {tf: bars(tf) for tf in ("15m", "5m")}


def setups(zones, tf, sweep, disp, entry, slm):
    B = BARS[tf]; o, h, l, c, a, sh, sl, t, n = B["o"], B["h"], B["l"], B["c"], B["a"], B["sh"], B["sl"], B["t"], B["n"]
    out = []
    for z in zones:
        sg = 1 if z["dir"] == "bull" else -1
        j, j1, used = max(int(t.searchsorted(z["t0"])), 1), min(int(t.searchsorted(z["t1"])), n), 0
        while j < j1 and used < 2:
            inside = l[j] <= z["hi"] and h[j] >= z["lo"]
            if not (inside and ((c[j - 1] > z["hi"]) if sg > 0 else (c[j - 1] < z["lo"]))):
                j += 1; continue
            tap, ext, swept, found = j, (l[j] if sg > 0 else h[j]), not sweep, None
            for k in range(tap, min(tap + B["win"], n)):
                ext = min(ext, l[k]) if sg > 0 else max(ext, h[k])
                if not swept:
                    ref = sl[k - 1] if sg > 0 else sh[k - 1]
                    swept = bool(np.isfinite(ref) and ((l[k] < ref) if sg > 0 else (h[k] > ref)))
                    continue
                lvl = sh[k - 1] if sg > 0 else sl[k - 1]
                if not np.isfinite(lvl) or (c[k] - lvl) * sg <= 0 or k == tap:
                    continue
                if np.abs(c[max(0, k - 2):k + 1] - o[max(0, k - 2):k + 1]).max() < disp * a[k]:
                    continue
                q = next((q for q in range(k - 1, max(tap - 2, k - 12), -1) if ((c[q] < o[q]) if sg > 0 else (c[q] > o[q]))), None)
                if q is None:
                    break
                top, bot = (h[q], l[q]) if sg > 0 else (l[q], h[q])
                en = float(top if entry == "OB edge" else (top + bot) / 2)
                stop = float((bot if slm == "under OB" else ext) - sg * 0.1 * a[k])
                found = dict(t=B["end"][k], sg=sg, entry=en, stop=stop, risk=(en - stop) * sg,
                             bias=splus._bias_at(bD, B["end"][k]) == z["dir"] or splus._bias_at(b4, B["end"][k]) == z["dir"])
                break
            used += 1
            if found:
                out.append(found)
            j = (int(t.searchsorted(found["t"])) if found else tap) + 1
    return sorted(out, key=lambda s: s["t"])


def trade(ss, bias, rr=2.0, per_day=2):
    out, busy, count = [], None, {}
    for s in ss:
        if bias and not s["bias"]:
            continue
        if not 1.5 <= s["risk"] <= 20 or (busy is not None and s["t"] < busy):
            continue
        dk = (s["t"] - pd.Timedelta(hours=18)).date()
        if count.get(dk, 0) >= per_day:
            continue
        sg, en, st = s["sg"], s["entry"], s["stop"]
        i5 = int(IDX.searchsorted(s["t"]))
        j0 = next((j for j in range(i5, min(i5 + LIMIT_BARS, N)) if ((L[j] <= en) if sg > 0 else (H[j] >= en))), None)
        if j0 is None:
            continue
        if (L[j0] <= st) if sg > 0 else (H[j0] >= st):   # same candle filled and stopped
            r, jx = -1.0, j0
        else:
            tgt, jend, r, jx = en + sg * rr * s["risk"], min(j0 + HOLD_BARS, N - 1), None, min(j0 + HOLD_BARS, N - 1)
            for j in range(j0 + 1, jend + 1):
                if (L[j] <= st) if sg > 0 else (H[j] >= st):
                    r, jx = -1.0, j; break
                if (H[j] >= tgt) if sg > 0 else (L[j] <= tgt):
                    r, jx = rr, j; break
            if r is None:
                r = (C[jend] - en) * sg / s["risk"]
        out.append((IDX[j0], r - COST / s["risk"], s["risk"]))
        busy = IDX[jx]; count[dk] = count.get(dk, 0) + 1
    return out


def st(tr):
    r = np.array([x[1] for x in tr]); old = np.array([x[0] < split for x in tr])
    if len(r) < 10:
        return None
    tt = r.mean() / r.std(ddof=1) * np.sqrt(len(r))
    days = (IDX[-1] - IDX[0]).days * 5 / 7
    return dict(n=len(r), per_day=round(len(r) / days, 2), win=round(100 * (r > 0).mean()), R=round(r.mean(), 3), t=round(tt, 2),
                old_R=round(r[old].mean(), 3), new_R=round(r[~old].mean(), 3) if (~old).sum() else None,
                new_win=round(100 * (r[~old] > 0).mean()) if (~old).sum() else None, sl=round(float(np.median([x[2] for x in tr])), 1))


rows = []
for zn, tf, sweep, disp, entry, slm, bias in itertools.product(ZONES, ("15m", "5m"), (True, False), (0.4, 0.6), ("OB edge", "OB 50%"),
                                                                ("under OB", "under sweep"), (True, False)):
    s = st(trade(setups(ZONES[zn], tf, sweep, disp, entry, slm), bias))
    if s:
        rows.append(dict(zones=zn, tf=tf, sweep=sweep, disp=disp, entry=entry, sl=slm, bias=bias, **{("SL$" if k == "sl" else k): v for k, v in s.items()}))
        print(rows[-1], flush=True)
G = pd.DataFrame(rows)
G.to_csv("/home/claude/ltf_ict_grid.csv", index=False)
pd.set_option("display.width", 250)
print(f"\n{len(G)} variants. Avg R per trade: median {G.R.median():+.3f}, older median {G.old_R.median():+.3f}, newest median {G.new_R.median():+.3f}")
print("variants with >= 1 trade a day:", (G.per_day >= 1).sum(), " of those positive on BOTH halves:", ((G.per_day >= 1) & (G.old_R > 0) & (G.new_R > 0)).sum())
print("\nTop 10 picked on OLDER data:\n", G.sort_values("old_R", ascending=False).head(10).to_string(index=False))
print("\nMentor version (all levels, SL under OB, OB edge, sweep, bias):\n",
      G[(G.zones == "all+liquidity") & (G.sl == "under OB") & (G.entry == "OB edge") & G.sweep & G.bias].to_string(index=False))
