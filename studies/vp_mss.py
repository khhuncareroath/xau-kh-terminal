"""📊 Volume Turn: 15m close back at the POC (live vp_turn) vs sweep -> 5m MSS confirmation (owner, 12 Nov 2026).

Setup is the SAME for every version (research.vp_shape / vp_turn): the last finished session's volume profile is P shaped
(POC in the top 45% -> buy) or b shaped (bottom 45% -> sell), the 4H swing does NOT already point that way, the day has
not used 70%+ of a normal day, stop risk <= 0.6%. Only the ENTRY trigger in the next session changes:

  BASE   live rule: price touches the POC, a 15m candle closes back (within 1 h), market entry; SL beyond the value
         area / touch extreme.
  MSS-x  price touches the POC, then a 5m liquidity SWEEP against the trade, then a 5m MSS back (close beyond the last
         5m swing before the sweep extreme, second.find logic); SL beyond the sweep extreme + 0.1 x 5m ATR (max $25).
         sweep reference:  H = the 5m low/high of the hour before the POC touch (second.py),
                           V = the value-area edge (VAL for a buy, VAH for a sell).
         entry:            M = market on the next 5m candle, L = limit at the MSS level (retest, valid 30 min).
4 MSS versions were chosen BEFORE running. Exits identical for all: single target 2R, max 8 h, closed by 24:00 Cambodia,
no new entry 00:00-06:00 Cambodia, $0.40 cost, one trade per session. Latency: 1 candle (the loop runs every 5 min).
Run: python studies/vp_mss.py   (needs the 2-year spot CSV at /home/claude/spot/xau_5m.csv.gz, from the spot-data branch)
"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd
import research as R
import second as S
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C, V = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close", "Volume"))
A5 = S.atr5(H, L, C)
idx = df.index; n = len(df)
kh = idx.tz_convert("Asia/Phnom_Penh")
khday = np.array(kh.date)
khhr = kh.hour.to_numpy()
hr = idx.hour + idx.minute / 60
date = (idx - pd.Timedelta(hours=18)).date
sess = np.where((hr >= 18) | (hr < 2), 0, np.where(hr < 7, 1, np.where(hr < 12, 2, -1)))
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))
groups = {}
for i, (d, s_) in enumerate(zip(date, sess)):
    if s_ >= 0:
        groups.setdefault((d, s_), []).append(i)
order = sorted(groups)
days = sorted(set(date)); dpos = {d: np.where(date == d)[0] for d in days}
drng = {d: H[dpos[d]].max() - L[dpos[d]].min() for d in days}; dix = {d: k for k, d in enumerate(days)}


def day_used(i):
    dd = date[i]; kk = dix[dd]
    if kk < 10:
        return 0
    adr = np.median([drng[x] for x in days[max(0, kk - 20):kk]])
    pp = dpos[dd][dpos[dd] <= i]
    return (H[pp].max() - L[pp].min()) / adr


def end_bar(j0):
    """8 h, but closed on the last candle before 24:00 Cambodia."""
    j = min(j0 + 96, n - 1)
    while j > j0 and khday[j] != khday[j0]:
        j -= 1
    return j


def trade(j0, sg, en, stop, rr, limit=False):
    """Single target rr x risk. limit=True: entry price en (filled on bar j0, stop on the fill candle counts)."""
    if khhr[j0] < 6:
        return None
    risk = (en - stop) * sg
    if risk <= 0.5 or risk > en * 0.006:
        return None
    tgt = en + sg * rr * risk
    jend = end_bar(j0)
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            px = stop if (limit or j == j0) else (min(stop, O[j]) if sg > 0 else max(stop, O[j]))
            return (idx[j0], (px - en) * sg / risk - R.COST / risk, "long" if sg > 0 else "short", risk)
        if (j > j0 or not limit) and ((H[j] >= tgt) if sg > 0 else (L[j] <= tgt)):
            return (idx[j0], rr - R.COST / risk, "long" if sg > 0 else "short", risk)
    return (idx[j0], (C[jend] - en) * sg / risk - R.COST / risk, "long" if sg > 0 else "short", risk)


def setups(th=0.55):
    for g0, g1 in zip(order[:-1], order[1:]):
        prev, nxt = np.array(groups[g0]), groups[g1]
        if len(prev) < 30 or len(nxt) < 4:
            continue
        poc, val, vah, lo, hi = R._vp(H, L, C, V, prev)
        pos = (poc - lo) / (hi - lo) if hi > lo else 0.5
        if th > pos > 1 - th:
            continue
        sg = 1 if pos >= th else -1
        yield sg, poc, val, vah, nxt


def against4h(j, sg):
    return b4[j - 1] != ("bull" if sg > 0 else "bear")


def base(rr=2.0, lat=1):
    out = []
    for sg, poc, val, vah, nxt in setups():
        wrong = val if sg > 0 else vah
        touched = None
        for i in nxt:
            if touched is None and ((L[i] <= poc) if sg > 0 else (H[i] >= poc)):
                touched = i; continue
            if touched is None or i - touched > 12 or idx[i].minute % 15 != 10:
                continue
            if (C[i] > poc) if sg > 0 else (C[i] < poc):
                j0 = i + lat
                if j0 >= n or day_used(i) >= 0.7 or not against4h(j0, sg):
                    break
                ext = L[touched:i + 1].min() if sg > 0 else H[touched:i + 1].max()
                stop = min(wrong, ext - 0.5) if sg > 0 else max(wrong, ext + 0.5)
                t = trade(j0, sg, O[j0], stop, rr)
                if t:
                    out.append(t)
                break
    return out


def mss(ref="H", entry="M", rr=2.0, swing=S.SWING_BARS):
    out = []
    for sg, poc, val, vah, nxt in setups():
        jt = next((i for i in nxt if ((L[i] <= poc) if sg > 0 else (H[i] >= poc))), None)
        if jt is None or jt < 20:
            continue
        last = nxt[-1]
        # sweep level: hour-before-touch extreme (second.find) or the value-area edge
        lvl = (L[jt - 12:jt].min() if sg > 0 else H[jt - 12:jt].max()) if ref == "H" else (val if sg > 0 else vah)
        ext = jext = None; plan = None
        for j in range(jt, last + 1):
            if ext is None:
                if (L[j] < lvl) if sg > 0 else (H[j] > lvl):
                    ext, jext = (L[j] if sg > 0 else H[j]), j
                continue
            if (L[j] < ext) if sg > 0 else (H[j] > ext):
                ext, jext = (L[j] if sg > 0 else H[j]), j; continue
            seg = slice(max(jt - 6, jext - swing), jext)
            key = H[seg].max() if sg > 0 else L[seg].min()
            if (C[j] > key) if sg > 0 else (C[j] < key):
                plan = (j, key, ext - sg * 0.1 * A5[j]); break
        if plan is None:
            continue
        j, key, stop = plan
        if abs(key - stop) > S.MAX_RISK or day_used(j) >= 0.7 or not against4h(j + 1, sg):
            continue
        if entry == "M":
            t = trade(j + 1, sg, O[j + 1], stop, rr) if j + 1 < n else None
        else:
            tgt1 = key + sg * rr * abs(key - stop)
            t = None
            for k in range(j + 1, min(j + 1 + S.RETEST_BARS, n)):
                if (L[k] <= key) if sg > 0 else (H[k] >= key):
                    t = trade(k, sg, key, stop, rr, limit=True); break
                if (H[k] >= tgt1) if sg > 0 else (L[k] <= tgt1):
                    break
        if t:
            out.append(t)
    return out


def show(name, tr):
    if len(tr) < 15:
        print(f"  {name:34} n={len(tr)} (too few)"); return
    jd = R.judge([(t, r, s) for t, r, s, _ in tr], split)
    r = np.array([x[1] for x in tr])
    print(f"  {name:34} n={len(r):4d} ({len(r) / 24:3.1f}/mo) win {100 * (r > 0).mean():3.0f}% avg {r.mean():+.3f}R "
          f"total {r.sum():+5.1f}R t={jd['t_stat']:+.1f} older {jd['older_70pct']['avg_R']:+.2f} "
          f"newest {jd['newest_30pct']['avg_R']:+.2f} ({jd['newest_30pct']['trades']}) q {jd['positive_quarters']} "
          f"SL ${np.median([x[3] for x in tr]):.1f}{' · PROVEN' if jd['proven'] else ''}")


if __name__ == "__main__":
    print("research.vp_turn as coded (15 min latency, session-end exit):", len(R.vp_turn(df)))
    print("== same setup, same exits (2R, 8 h, by 24:00 KH) ==")
    B = base(); show("BASE 15m close at POC (live)", B)
    show("BASE with 15 min latency", base(lat=3))
    res = {}
    for ref in ("H", "V"):
        for en in ("M", "L"):
            res[ref + en] = mss(ref, en); show(f"MSS sweep {ref} entry {en}", res[ref + en])
    # overlap with the live trades: same session?
    bs = {pd.Timestamp(t).floor("6h") for t, *_ in B}
    for k, tr in res.items():
        both = [x for x in tr if pd.Timestamp(x[0]).floor("6h") in bs]
        only = [x for x in tr if pd.Timestamp(x[0]).floor("6h") not in bs]
        print(f"  {k}: {len(both)} in a session where BASE also traded, {len(only)} new sessions "
              f"({np.mean([x[1] for x in only]) if only else 0:+.2f}R on the new ones)")
    print("== robustness of each MSS version (target 1.5 / 2.5R, swing 6 / 12 candles) ==")
    for ref in ("H", "V"):
        for en in ("M", "L"):
            for kw in ({"rr": 1.5}, {"rr": 2.5}, {"swing": 6}, {"swing": 12}):
                show(f"MSS {ref}{en} {kw}", mss(ref, en, **kw))
    print("== BASE robustness ==")
    for rr in (1.5, 2.5):
        show(f"BASE rr {rr}", base(rr=rr))
