"""🔄 Flip inside the zone (owner, 12 Nov 2026): when the M15 signal is blocked because the entry sits INSIDE an opposite
zone (a SELL inside a bull array), trade WITH the zone instead, after confirmation: 5m sweep of the hour's low + MSS
up (second.find with the direction flipped), entry at the retest (or market), SL beyond the sweep, TP1 1R, TP2 = the
nearest zone of the signal's side (the bear key level) if 1.5-4R away, else 2R. 8 h max, $0.40.
Run: python studies/flip_zone.py"""
import sys, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import second as S2, research as R, arrays
from levels import to_ny

raw = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
df = to_ny(raw)
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
A = S2.atr5(H, L, C); N = len(df)
Z = {}
for tf in ("15m", "30m", "1H", "4H", "D"):
    zs = arrays.zones(df, tf)
    Z[tf] = (np.array([z["dir"] == "bull" for z in zs]), np.array([z["lo"] for z in zs]), np.array([z["hi"] for z in zs]),
             np.array([z["t0"].value for z in zs]), np.array([z["t1"].value for z in zs]))


def zone_of(t, en, want_bull, mode):
    """mode 'inside': any active zone of that side containing en. mode 'ahead': nearest edge of that side beyond en."""
    best = None
    for tf, (bull, lo, hi, t0, t1) in Z.items():
        m = (bull == want_bull) & (t0 <= t.value) & (t.value < t1)
        if mode == "inside":
            if (m & (lo <= en) & (en <= hi)).any():
                return tf
        else:
            for arr in (lo[m], hi[m]):
                d = arr[arr > en] if want_bull is False else arr[arr < en]   # placeholder, set below
    return best


def inside(t, en, sg):
    return zone_of(t, en, sg < 0, "inside")


def key_level(t, en, fs):
    """Nearest edge of a zone AGAINST the flip trade ahead of it (for a flip BUY: the nearest bear zone's low above en)."""
    best = None
    for tf, (bull, lo, hi, t0, t1) in Z.items():
        m = (bull == (fs < 0)) & (t0 <= t.value) & (t.value < t1)
        for arr in (lo[m], hi[m]):
            d = (arr - en) * fs
            d = d[d > 0]
            if len(d) and (best is None or d.min() < best):
                best = float(d.min())
    return None if best is None else en + fs * best


M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
rows = []
for r in M:
    j0 = r["j0"]; t = df.index[j0]; sg = 1 if r["dir"] == "bull" else -1
    if not inside(t, r["entry"], sg):
        continue
    fs = -sg
    for entry_mode in ("retest", "market"):
        for tp_mode in ("1R/2R", "1R/key"):
            # flip: placeholder TP1 far enough to pass find()'s 0.5R check; real targets set after the stop is known
            p = S2.find(O, H, L, C, A, j0, fs, r["entry"] + fs * 1e6, last=N - 100)
            res = None
            if p and not p["skip"]:
                en, st = p["level"], p["stop"]
                if entry_mode == "market":
                    en, k = C[p["j"]], p["j"] + 1
                    st_ok = (en - st) * fs > S2.MIN_RISK
                else:
                    k, why = S2.fill(O, H, L, C, p, fs, en + fs * 1e6, last=N - 100)
                    st_ok = k is not None
                if st_ok:
                    risk = abs(en - st)
                    tp1 = en + fs * risk
                    kl = key_level(t, en, fs)
                    tp2 = en + fs * 2 * risk
                    if tp_mode == "1R/key" and kl is not None and 1.5 * risk <= abs(kl - en) <= 4 * risk:
                        tp2 = kl - fs * 0.1 * risk
                    res = S2.grade(O, H, L, C, fs, en, st, tp1, tp2, k, 96) if risk <= S2.MAX_RISK else None
            rows.append(dict(t=t, mode=f"{entry_mode} {tp_mode}", R=res, sigR=r["R"]))
X = pd.DataFrame(rows); X["new"] = X.t >= split
n_in = X.t.nunique()
print(f"{n_in} M15 signals were inside an opposite zone (original trade on them: {X.drop_duplicates('t').sigR.mean():+.3f}R)")
for mode, g in X.groupby("mode"):
    s = g.dropna()
    if len(s) < 3:
        print(mode, len(s)); continue
    jd = R.judge([(a, b) for a, b in zip(s.t, s.R)], split)
    print(f"  flip {mode:16s} {len(s):3d} trades ({len(s)/24:.1f}/mo) {100*(s.R>0).mean():3.0f}% win {s.R.mean():+.3f}R t {jd['t_stat']} "
          f"| older {jd['older_70pct']['avg_R']} ({jd['older_70pct']['trades']}) newest {jd['newest_30pct']['avg_R']} ({jd['newest_30pct']['trades']}) "
          f"| q+ {jd['positive_quarters']}{' · PROVEN' if jd['proven'] else ''}")
