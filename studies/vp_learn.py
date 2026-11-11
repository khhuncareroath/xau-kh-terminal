"""📊 Volume-profile setup (vp_shape) + 🐢 8:30 Cambodia Turtle Soup: what makes them better? (12 Nov 2026)

Part 1 vp_shape (P shape -> buy the pullback to the previous session's POC; b shape -> sell it). Each trade gets tags
(session, 4H trend agrees, clean 4H trend, how lopsided the profile is, buy/sell, risk) and results are split by tag.
A tag is only "a lesson" if it helps on BOTH the older 70% and the newest 30%.
Part 2 Turtle Soup at 8:30 Cambodia (Asia session): which range, and does the sweep FADE or CONTINUE?
Run: python studies/vp_learn.py
"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd
import research as R
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C, V = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close", "Volume"))
n = len(df)
pos_of = {t: k for k, t in enumerate(df.index)}
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))


def report(name, tr):
    if len(tr) < 15:
        print(f"  {name:40} n={len(tr)} (too few)"); return
    jd = R.judge([(t, r) for t, r, *_ in tr], split)
    r = np.array([x[1] for x in tr])
    print(f"  {name:40} n={len(r):4d} win {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R t={jd['t_stat']:+.1f} "
          f"older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f} q {jd['positive_quarters']}"
          f"{' · PROVEN' if jd['proven'] else ''}")


print("=== PART 1: volume profile (vp_shape, live settings) ===")
for rr in (1.5, 2.0):
    base = R.vp_shape(df, rr=rr)
    tag = []
    for t, r, side in base:
        j = pos_of[t]; sg = 1 if side == "long" else -1
        hr = t.hour
        ses = "Asia" if (hr >= 18 or hr < 2) else "London" if hr < 7 else "New York"
        er = R.efficiency(df, t) or 0
        tag.append(dict(t=t, r=r, side=side, ses=ses, with4h=b4[j - 1] == ("bull" if sg > 0 else "bear"),
                        clean=er > R.CHOP_ER))
    T = pd.DataFrame(tag)
    print(f"-- target {rr}R")
    report("ALL (live)", base)
    for col, vals in (("ses", ("Asia", "London", "New York")), ("side", ("long", "short")),
                      ("with4h", (True, False)), ("clean", (True, False))):
        for v in vals:
            s = T[T[col] == v]
            report(f"{col} = {v}", list(zip(s.t, s.r)))
    s = T[T.with4h & T.clean]; report("with 4H AND clean trend", list(zip(s.t, s.r)))
for th in (0.6, 0.65, 0.7):
    report(f"more lopsided profile (POC in top/bottom {round((1 - th) * 100)}%)", R.vp_shape(df, th=th))

print("\n=== PART 2: Turtle Soup at 8:30 Cambodia (Asia) ===")
kh = df.index.tz_convert("Asia/Phnom_Penh")
starts = np.where((kh.hour == 8) & (kh.minute == 30))[0]


def soup(ref, fade=True, tp=1.2, trend=None):
    out = []
    for s in starts:
        if ref == "1h":
            r0 = s - 12
        elif ref == "asia-open":           # from 06:00 Cambodia (when our signals start) to 08:30
            r0 = s - 30
        else:                              # the US session before: 19:30-04:00 Cambodia, i.e. the last NY high/low
            r0 = s - 13 * 12 - 6
        if r0 < 300:
            continue
        hi, lo = H[r0:s].max(), L[r0:s].min()
        for i in range(s, min(s + 24, n - 50)):
            hit = None
            for sw, lvl in ((-1, hi), (1, lo)):        # sw = direction if it FADES the sweep
                if (H[i] > lvl and C[i] < lvl) if sw < 0 else (L[i] < lvl and C[i] > lvl):
                    hit = (sw, lvl)
            if not hit:
                continue
            sw, lvl = hit
            sg = sw if fade else -sw
            if trend and b4[i] != ("bull" if sg > 0 else "bear"):
                break
            j0 = i + 1; en = O[j0]
            if fade:
                stop = (H[i] + 0.5) if sg < 0 else (L[i] - 0.5)
            else:                                       # continuation: the sweep candle's other end
                stop = (L[i] - 0.5) if sg > 0 else (H[i] + 0.5)
            risk = (en - stop) * sg
            if not 2 <= risk <= 15:
                break
            tgt = en + sg * tp * risk
            res = None
            for j in range(j0, j0 + 48):
                if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
                    res = -1.0; break
                if (H[j] >= tgt) if sg > 0 else (L[j] <= tgt):
                    res = tp; break
            if res is None:
                res = (C[j] - en) * sg / risk
            out.append((df.index[j0], res - 0.4 / risk))
            break
    return out


for ref, refn in (("1h", "1h before 8:30"), ("asia-open", "06:00-08:30 range"), ("ny", "last New York session")):
    for fade in (True, False):
        for tp in (1.2, 2.0):
            report(f"{refn} · {'FADE (video)' if fade else 'CONTINUE'} · {tp}R", soup(ref, fade, tp))
    report(f"{refn} · FADE · 1.2R · with 4H", soup(ref, True, 1.2, "with"))
