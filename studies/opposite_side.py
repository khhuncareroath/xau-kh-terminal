"""👀 Check the OTHER side before firing (owner, 12 Nov 2026): demand / supply / FVG / OB on 15m, 30m, 1H, 4H and Daily
that could stop the move before TP1 or push price back to the SL. And: can B+ be upgraded instead of removed?

Zones per timeframe (FVG >= 0.2 ATR, order block of a displacement break), active from the candle after they form until
a close through them or their lifetime ends (15m 2 d, 30m 3 d, 1H 5 d, 4H 15 d, D 40 d). For each replayed M15 signal
(London/NY + Asia, A+ and B+): the nearest OPPOSITE zone edge ahead (in R) and whether the entry sits INSIDE an opposite
zone. Then: TP1 before that edge / skip when it is too close / skip when inside. A rule counts only if it helps in both
the older 70% and the newest 30%.
Run: python studies/opposite_side.py"""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import research as R, ict
from engine import atr
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
kh = df.index.tz_convert("Asia/Phnom_Penh")
TF = {"15m": ("15min", 2), "30m": ("30min", 3), "1H": ("1h", 5), "4H": (None, 15), "D": (None, 40)}


def zones(tf):
    rule, life = TF[tf]
    d = ict.resample(df, tf) if rule is None else df.resample(rule).agg(ict.AGG).dropna()
    span = {"15m": 15, "30m": 30, "1H": 60, "4H": 240, "D": 1440}[tf]
    span = pd.Timedelta(minutes=span)
    a = atr(d).to_numpy()
    o, h, l, c = (d[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    raw = []
    for i in range(2, len(d)):
        if not np.isfinite(a[i]):
            continue
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= 0.2 * a[i]:
            raw.append(("bull", h[i - 2], l[i], i))
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= 0.2 * a[i]:
            raw.append(("bear", h[i], l[i - 2], i))
    sw = ict.swings(d, 3)
    for e in ict.structure(d, a, sw):
        ob = ict.order_block(d, e)
        if ob and e["displacement"]:
            raw.append((ob["dir"], ob["lo"], ob["hi"], e["i"]))
    out = []
    for dr, lo, hi, i in raw:
        if i + 1 >= len(d):
            continue
        after = c[i + 1:]
        bad = np.where(after < lo)[0] if dr == "bull" else np.where(after > hi)[0]
        t0 = d.index[i] + span
        t1 = d.index[i + 1 + bad[0]] + span if len(bad) else t0 + pd.Timedelta(days=life)
        out.append((dr, float(lo), float(hi), t0, min(t1, t0 + pd.Timedelta(days=life)), tf))
    return out


ZS = {tf: zones(tf) for tf in TF}
print({k: len(v) for k, v in ZS.items()}, "zones")

rows = {}
for f in sorted(glob.glob("/tmp/m15_[a-f].json")) + sorted(glob.glob("/tmp/m15_asiab_*.json")):
    for r in json.load(open(f)):
        if r["kind"] == "break":
            rows[r["t"]] = r
X = pd.DataFrame(rows.values())
X["t"] = pd.to_datetime(X.t, utc=True).dt.tz_convert("America/New_York")
X["old"] = X.t < split
X["sg"] = np.where(X.dir == "bull", 1, -1)
X["risk"] = (X.entry - X.stop).abs()
X["tp1R"] = (X.tp1p - X.entry).abs() / X.risk
print(X.tier.value_counts().to_dict(), "signals")


def opp(r, tfs):
    want = "bear" if r.sg > 0 else "bull"
    best, inside = None, None
    for tf in tfs:
        for dr, lo, hi, t0, t1, _ in ZS[tf]:
            if dr != want or not (t0 <= r.t < t1):
                continue
            if lo <= r.entry <= hi:
                inside = inside or tf
            for lv in (lo, hi):
                dd = (lv - r.entry) * r.sg / r.risk
                if dd > 0.05 and (best is None or dd < best):
                    best = dd
    return (best if best is not None else 99), inside


def grade(r, tp1):
    sg, en, st, tp2 = r.sg, r.entry, r.stop, r.tp2p
    risk = r.risk; j0 = int(r.j0)
    mid = kh[j0].normalize() + pd.Timedelta(days=1); jend = min(j0 + 96, len(df) - 1)
    while jend > j0 and kh[jend] >= mid:
        jend -= 1
    stop, got, left, hit = st, 0.0, 1.0, False
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            return got + left * (stop - en) * sg / risk - .4 / risk
        if not hit and ((H[j] >= tp1) if sg > 0 else (L[j] <= tp1)):
            got, left, hit, stop = .5 * abs(tp1 - en) / risk, .5, True, en
        if hit and ((H[j] >= tp2) if sg > 0 else (L[j] <= tp2)):
            return got + left * abs(tp2 - en) / risk - .4 / risk
    return got + left * (C[jend] - en) * sg / risk - .4 / risk


X["R0"] = [grade(r, r.tp1p) for _, r in X.iterrows()]


def st(name, s, col):
    if len(s) < 15:
        print(f"    {name:46} n={len(s)} few"); return
    r = s[col]
    jd = R.judge(list(zip(s.t, r)), split)
    print(f"    {name:46} n={len(s):3d} ({len(s) / 24:4.1f}/mo) win {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R "
          f"t={jd['t_stat']:+.1f} | older {r[s.old].mean():+.2f} newest {r[~s.old].mean():+.2f} | total {r.sum():+.0f}R"
          f"{' · PROVEN' if jd['proven'] else ''}")


SETS = {"4H+D": ("4H", "D"), "1H-D": ("1H", "4H", "D"), "30m-D": ("30m", "1H", "4H", "D"), "15m-D": ("15m", "30m", "1H", "4H", "D")}
for sname, tfs in SETS.items():
    e = X.apply(lambda r: opp(r, tfs), axis=1)
    X["ed"] = [x[0] for x in e]
    X["ins"] = [x[1] is not None for x in e]
    X["R_tp"] = [grade(r, r.entry + r.sg * max(r.ed - 0.1, 0.3) * r.risk) if r.ed < r.tp1R else r.R0 for _, r in X.iterrows()]
    print(f"== opposite zones on {sname}")
    for tier in ("A+", "B+"):
        S = X[X.tier == tier]
        print(f"  {tier}")
        st("as now", S, "R0")
        st("TP1 before the opposite edge", S, "R_tp")
        st("skip if opposite edge within 0.5R", S[S.ed > 0.5], "R0")
        st("skip if opposite edge within 1R", S[S.ed > 1.0], "R0")
        st("skip if entry INSIDE an opposite zone", S[~S.ins], "R0")
        st("  (the ones inside an opposite zone)", S[S.ins], "R0")
        st("TP1 before edge + skip inside", S[~S.ins], "R_tp")
        st("TP1 before edge + skip within 0.5R", S[S.ed > 0.5], "R_tp")
X.to_pickle("/tmp/opp.pkl")

# ---- the chosen rule, A+ and B+ together: all timeframes 15m-D; opposite edge within 0.5R -> not sent; else TP1 before it
X = pd.read_pickle("/tmp/opp.pkl")   # last loop left ed / R_tp for 15m-D
S = X[X.ed > 0.5]
print("== CHOSEN: 15m-D, skip within 0.5R, TP1 before the edge · A+ and B+ together")
st("A+ and B+", S, "R_tp")
st("  A+", S[S.tier == "A+"], "R_tp"); st("  B+", S[S.tier == "B+"], "R_tp")
st("compare: A+ only, as live this morning", X[X.tier == "A+"], "R0")
