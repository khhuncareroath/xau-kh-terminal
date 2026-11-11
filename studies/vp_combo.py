"""📊 Volume profile as a CONFIRMATION inside the existing signals (owner, 12 Nov 2026: "combo volume, entry in low
timeframe, no separate signal; strong A+ / B+ and strong fun scalp, more signals but keep the standard").

For every trade we look at the volume profile of the LAST FINISHED session (Asia 18-02, London 02-07, New York 07-12, NY
time, same as research.vp_shape): P shape (POC in the top 45%) = buyers won, b shape (bottom 45%) = sellers won, else D.
Tags: vol_agree = the shape points the same way as the trade; vol_against = the opposite way.
Also: is the entry at a volume level (within $3 of the POC / VAL / VAH)?
Checked on: the M15 replay (A+ and B+), and the Fun Scalp entries (clean-trend ones AND the choppy ones we now skip).
Run: python studies/vp_combo.py
"""
import sys, glob, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
sys.path.insert(0, '/home/claude/xau-kh-terminal/studies')
import numpy as np
import pandas as pd
import research as R
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C, V = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close", "Volume"))
n = len(df)
idx = df.index
hr = idx.hour + idx.minute / 60
date = (idx - pd.Timedelta(hours=18)).date
sess = np.where((hr >= 18) | (hr < 2), 0, np.where(hr < 7, 1, np.where(hr < 12, 2, -1)))

# profile of each finished session, available from the first candle after it ends
prof_at = np.array([None] * n, dtype=object)
groups = {}
for i, (d, s) in enumerate(zip(date, sess)):
    if s >= 0:
        groups.setdefault((d, s), []).append(i)
last = None
order = sorted(groups)
ends = {groups[g][-1]: g for g in order}
cur = None
for i in range(n):
    prof_at[i] = cur
    if i in ends and len(groups[ends[i]]) >= 30:
        ix = np.array(groups[ends[i]])
        poc, val, vah, lo, hi = R._vp(H, L, C, V, ix)
        pos = (poc - lo) / (hi - lo) if hi > lo else 0.5
        cur = dict(poc=poc, val=val, vah=vah, shape=1 if pos >= 0.55 else -1 if pos <= 0.45 else 0)
pos_of = {t: k for k, t in enumerate(idx)}


def tag(t, sg, price):
    j = pos_of.get(t)
    p = prof_at[j] if j is not None else None
    if not p:
        return "none", False
    rel = "agree" if p["shape"] == sg else "against" if p["shape"] == -sg else "D"
    near = min(abs(price - p[k]) for k in ("poc", "val", "vah")) <= 3
    return rel, near


def report(name, rs, ts):
    if len(rs) < 15:
        print(f"  {name:44} n={len(rs)} (too few)"); return
    jd = R.judge(list(zip(ts, rs)), split)
    r = np.array(rs)
    print(f"  {name:44} n={len(r):4d} ({len(r) / 24:4.1f}/mo) win {100 * (r > 0).mean():.0f}% avg {r.mean():+.3f}R t={jd['t_stat']:+.1f} "
          f"older {jd['older_70pct']['avg_R']:+.2f} newest {jd['newest_30pct']['avg_R']:+.2f}{' · PROVEN' if jd['proven'] else ''}")


def split_by(name, items):
    """items: list of (t, R, rel, near)"""
    print(f"-- {name}")
    report("all", [x[1] for x in items], [x[0] for x in items])
    for rel in ("agree", "D", "against"):
        s = [x for x in items if x[2] == rel]
        report(f"volume {rel}", [x[1] for x in s], [x[0] for x in s])
    s = [x for x in items if x[3]]
    report("entry at a volume level (POC/VAL/VAH ±$3)", [x[1] for x in s], [x[0] for x in s])
    s = [x for x in items if x[2] != "against"]
    report("volume NOT against", [x[1] for x in s], [x[0] for x in s])


# 1) M15 replay
rows = {}
for f in sorted(glob.glob("/tmp/m15_[a-f].json")):
    for r in json.load(open(f)):
        rows[r["t"]] = r
M = [r for r in rows.values() if r["kind"] == "break"]
for tier in ("A+", "B+"):
    items = []
    for r in M:
        if r["tier"] != tier:
            continue
        t = pd.Timestamp(r["t"]).tz_convert("America/New_York")
        sg = 1 if r["dir"] == "bull" else -1
        rel, near = tag(idx[r["j0"] - 1], sg, r["entry"])
        items.append((t, r["R"], rel, near))
    split_by(f"📈 M15 {tier} (replay)", items)

# 2) Fun scalp entries, live exits (⅓ at 1 / 1.5 / 2R)
from engine import atr
a_ = atr(df).to_numpy()
e20 = pd.Series(C).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(df)
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))
day = np.array((idx - pd.Timedelta(hours=18)).date)
LEGS = [(1/3, 1), (1/3, 1.5), (1/3, 2)]


def run(j0, j_end, sg, stop):
    en = O[j0]; risk = (en - stop) * sg
    lv = lambda r: en + sg * r * risk
    st, got, left, k = stop, 0.0, 1.0, 0
    for j in range(j0, j_end + 1):
        if (L[j] <= st) if sg > 0 else (H[j] >= st):
            px = st if (j == j0 or k) else (min(st, O[j]) if sg > 0 else max(st, O[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk, j
        while k < 3 and ((H[j] >= lv(LEGS[k][1])) if sg > 0 else (L[j] <= lv(LEGS[k][1]))):
            got += LEGS[k][0] * LEGS[k][1]; left -= LEGS[k][0]
            if k == 0:
                st = en
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk, j
    return got + left * (C[j_end] - en) * sg / risk - R.COST / risk, j_end


def fun(ok, per_day=3):
    out, busy, used = [], -1, {}
    for i in range(300, n - 2):
        sg = 1 if b4[i] == "bull" else -1 if b4[i] == "bear" else 0
        if not sg or i <= busy or used.get(day[i], 0) >= per_day:
            continue
        sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1
        risk = (O[j0] - sw) * sg
        if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1]:
            continue
        rel, near = tag(idx[i], sg, C[i])
        er = R.efficiency(df, idx[j0]) or 0
        if not ok(er > R.CHOP_ER, rel, near):
            continue
        r, j = run(j0, min(j0 + R.SCALP_HOLD, n - 1), sg, sw)
        busy = j
        used[day[i]] = used.get(day[i], 0) + 1
        out.append((idx[j0], r, rel, near))
    return out


print("-- 🎰 Fun Scalp")
for name, ok in (("LIVE: clean trend", lambda c, r, nr: c),
                 ("clean trend + volume NOT against", lambda c, r, nr: c and r != "against"),
                 ("clean trend + volume agrees", lambda c, r, nr: c and r == "agree"),
                 ("clean OR volume agrees (more signals)", lambda c, r, nr: c or r == "agree"),
                 ("choppy (skipped now) + volume agrees", lambda c, r, nr: (not c) and r == "agree"),
                 ("choppy + entry at a volume level", lambda c, r, nr: (not c) and nr),
                 ("no filter", lambda c, r, nr: True)):
    tr = fun(ok)
    report(name, [x[1] for x in tr], [x[0] for x in tr])
