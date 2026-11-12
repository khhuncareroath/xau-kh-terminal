"""🎰 Fun Scalp + the other-side check (owner, 12 Nov 2026: "same for fun scalp but on lower timeframes too; fire more but
quality"). Live entries (4H direction, 15m FVG dip, 5m close back), live exits (⅓ at 1R / 1.5R / 2R, SL to entry after
TP1), 3h max. Opposite zones (arrays.py detection) on 5m, 15m, 30m, 1H, 4H, D.
Variants: (a) skip when an opposite edge is within k R; (b) targets squeezed to end just before the edge;
(c) "fire more": let CHOPPY-trend trades through when the path is clear, or allow 4 a day.
Run: python studies/fun_opposite.py"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R, arrays
from engine import atr
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
n = len(df); idx = df.index
a_ = atr(df).to_numpy()
e20 = pd.Series(C).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))
day = np.array((idx - pd.Timedelta(hours=18)).date)

arrays.TF["5m"] = ("5min", 1, 5)
Z = {}
for tf in ("5m", "15m", "30m", "1H", "4H", "D"):
    zs = arrays.zones(df, tf)
    Z[tf] = dict(bull=np.array([z["dir"] == "bull" for z in zs]), lo=np.array([z["lo"] for z in zs]),
                 hi=np.array([z["hi"] for z in zs]), t0=np.array([z["t0"].value for z in zs]),
                 t1=np.array([z["t1"].value for z in zs]))
print({k: len(v["lo"]) for k, v in Z.items()}, "zones")


def edge(t, en, sg, risk, tfs):
    best = 99.0
    tv = t.value
    for tf in tfs:
        z = Z[tf]
        m = (z["bull"] == (sg < 0)) & (z["t0"] <= tv) & (tv < z["t1"])
        if not m.any():
            continue
        for lv in (z["lo"][m], z["hi"][m]):
            d = (lv - en) * sg / risk
            d = d[d > 0.05]
            if len(d):
                best = min(best, float(d.min()))
    return best


def run(j0, j_end, sg, stop, legs):
    en = O[j0]; risk = (en - stop) * sg
    lv = lambda r: en + sg * r * risk
    st, got, left, k = stop, 0.0, 1.0, 0
    for j in range(j0, j_end + 1):
        if (L[j] <= st) if sg > 0 else (H[j] >= st):
            px = st if (j == j0 or k) else (min(st, O[j]) if sg > 0 else max(st, O[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk, j
        while k < 3 and ((H[j] >= lv(legs[k])) if sg > 0 else (L[j] <= lv(legs[k]))):
            got += legs[k] / 3; left -= 1 / 3
            if k == 0:
                st = en
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk, j
    return got + left * (C[j_end] - en) * sg / risk - R.COST / risk, j_end


# candidates once (entry, stop, clean flag, edge distances per tf set)
SETS = {"15m-D": ("15m", "30m", "1H", "4H", "D"), "5m-D": ("5m", "15m", "30m", "1H", "4H", "D")}
cand = []
for i in range(300, n - 40):
    sg = 1 if b4[i] == "bull" else -1 if b4[i] == "bear" else 0
    if not sg:
        continue
    sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, i, sg)
    if sw is None:
        continue
    j0 = i + 1; risk = (O[j0] - sw) * sg
    if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1]:
        continue
    clean = (R.efficiency(df, idx[j0]) or 0) > R.CHOP_ER
    ed = {k: edge(idx[j0], O[j0], sg, risk, v) for k, v in SETS.items()}
    cand.append(dict(i=i, j0=j0, sg=sg, sw=sw, clean=clean, ed=ed))
print(len(cand), "candidate entries")


def sim(ok, squeeze=None, per_day=3):
    out, busy, used = [], -1, {}
    for c in cand:
        i = c["i"]
        if i <= busy or used.get(day[i], 0) >= per_day or not ok(c):
            continue
        legs = (1, 1.5, 2)
        if squeeze:
            e = c["ed"][squeeze]
            if e < 2.1:
                top = max(e - 0.1, 1.0)
                legs = (top / 2, top * 0.75, top)
        r, j = run(c["j0"], min(c["j0"] + R.SCALP_HOLD, n - 1), c["sg"], c["sw"], legs)
        busy = j
        used[day[i]] = used.get(day[i], 0) + 1
        out.append((idx[c["j0"]], r))
    return out


def rep(name, tr):
    jd = R.judge(tr, split); r = np.array([x[1] for x in tr])
    print(f"  {name:52} n={len(r):4d} ({len(r) / 24:4.1f}/mo) profit {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R "
          f"t={jd['t_stat']:+.1f} | older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f} | "
          f"total {r.sum():+.0f}R{' · PROVEN' if jd['proven'] else ''}")


rep("LIVE: clean trend", sim(lambda c: c["clean"]))
if 0:
    for s in SETS:
        print(f"== other side on {s}")
        for k in (0.5, 0.8, 1.0):
            rep(f"clean + skip if edge within {k}R", sim(lambda c, k=k, s=s: c["clean"] and c["ed"][s] > k))
        rep("clean + targets end before the edge", sim(lambda c: c["clean"], squeeze=s))
        rep("clean + skip 0.8R + targets before edge", sim(lambda c, s=s: c["clean"] and c["ed"][s] > 0.8, squeeze=s))
        print("   -- fire more --")
        rep("clean, OR choppy with a clear path (edge > 2R)", sim(lambda c, s=s: c["clean"] or c["ed"][s] > 2))
        rep("clean, OR choppy with edge > 1.5R, skip 0.8R", sim(lambda c, s=s: (c["clean"] or c["ed"][s] > 1.5) and c["ed"][s] > 0.8))
        rep("clean + skip 0.8R, 4 a day", sim(lambda c, s=s: c["clean"] and c["ed"][s] > 0.8, per_day=4))
        rep("clean + skip 0.8R + squeeze, 4 a day", sim(lambda c, s=s: c["clean"] and c["ed"][s] > 0.8, squeeze=s, per_day=4))
print("== combos (fire more with quality)")
rep("clean & 15m-D edge>0.5R  OR  choppy & 5m-D edge>2R",
    sim(lambda c: (c["clean"] and c["ed"]["15m-D"] > 0.5) or (not c["clean"] and c["ed"]["5m-D"] > 2)))
rep("clean & 15m-D edge>0.5R  OR  choppy & 5m-D edge>2.5R",
    sim(lambda c: (c["clean"] and c["ed"]["15m-D"] > 0.5) or (not c["clean"] and c["ed"]["5m-D"] > 2.5)))
rep("same, 4 a day",
    sim(lambda c: (c["clean"] and c["ed"]["15m-D"] > 0.5) or (not c["clean"] and c["ed"]["5m-D"] > 2), per_day=4))
rep("  (only the choppy-but-clear-path ones)", sim(lambda c: (not c["clean"]) and c["ed"]["5m-D"] > 2))
