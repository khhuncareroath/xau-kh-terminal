"""⏳ Second chance (second.py) on all three signal types, 2 years (owner, 12 Nov 2026).
Uses second.find / fill / grade, the exact functions the live bot runs.
M15: the 369 replayed live signals (studies/m15_replay.py -> /tmp/m15_a.json, m15_b.json).
⚡ Scalp: research.wide_scalp entries. 🎰 Fun Scalp: live entries (4H direction, 15m FVG dip), other-side check 0.5R,
QUALITY = clean trend 3 a day, CRAZY = choppy trend 4 a day (the live tiers share 4 a day; close enough to judge).
Run: python studies/second_chance.py"""
import sys, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import second as S2, research as R

df = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
A = S2.atr5(H, L, C)
N = len(df)


def chance(sig, j0, hold_h, wait_h=S2.WAIT_H):
    sg = 1 if sig["dir"] == "bull" else -1
    tp1, tp2 = S2.targets(sig)
    p = S2.find(O, H, L, C, A, j0, sg, tp1, last=N - 100, wait_bars=wait_h * 12)
    if p is None or p["skip"]:
        return None
    k, _ = S2.fill(O, H, L, C, p, sg, tp1, last=N - 100)
    return None if k is None else S2.grade(O, H, L, C, sg, p["level"], p["stop"], tp1, tp2, k, hold_h * 12)


def report(name, sigs, base_R, hold_h, waits=(3, 6)):
    print(f"\n== {name}: {len(sigs)} signals, base {np.mean(base_R):+.3f}R, total {np.sum(base_R):+.0f}R")
    out = {}
    for w in waits:
        tr = []
        for (t, sig, j0) in sigs:
            x = chance(sig, j0, hold_h, w)
            if x is not None:
                tr.append((t, x, sig["dir"]))
        if len(tr) < 5:
            print(f"  wait {w}h: {len(tr)} re-entries"); continue
        jd = R.judge(tr, split); r = np.array([x[1] for x in tr])
        print(f"  wait {w}h: {len(r)} re-entries ({len(r)/24:.1f}/mo) {100*(r>0).mean():.0f}% win {r.mean():+.3f}R t {jd['t_stat']} "
              f"| older {jd['older_70pct']['avg_R']} ({jd['older_70pct']['trades']}) newest {jd['newest_30pct']['avg_R']} ({jd['newest_30pct']['trades']}) "
              f"| q+ {jd['positive_quarters']} | total {np.sum(base_R):+.0f} -> {np.sum(base_R)+r.sum():+.0f}R{' · PROVEN' if jd['proven'] else ''}")
        out[w] = tr
    return out


# --- M15 ---
M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
m15 = [(pd.Timestamp(r["t"]), {"dir": r["dir"], "entry": r["entry"], "stop": r["stop"], "tp1": r["tp1p"], "target": r["tp2p"]}, r["j0"]) for r in M]
report("📈 M15 signal", m15, [r["R"] for r in M], 8)

# --- wide scalp (entry / stop / 2R target rebuilt from the trade list) ---
from levels import to_ny
dny = to_ny(df)
e20 = pd.Series(C).ewm(span=20).mean().to_numpy()
fd, flo, fhi = R.fvg_15m_state(dny)
from engine import atr
a_ = atr(dny).to_numpy()
ws = R.wide_scalp(dny)
sc, scR = [], []
for t, r, side in ws:
    j0 = int(dny.index.searchsorted(t)); sg = 1 if side == "long" else -1
    sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, j0 - 1, sg)
    if sw is None:
        continue
    en = O[j0]; risk = (en - sw) * sg
    sc.append((t, {"dir": "bull" if sg > 0 else "bear", "entry": en, "stop": sw, "target": en + sg * R.SCALP_RR * risk}, j0))
    scR.append(r)
report("⚡ Scalp", sc, scR, 3)

# --- fun scalp (live entries, other side within 0.5R skipped) ---
import arrays
b4 = R._bias(dny, "4H", pd.Timedelta(hours=4))
day = np.array((dny.index - pd.Timedelta(hours=18)).date)
Z = {}
for tf in ("15m", "30m", "1H", "4H", "D"):
    zs = arrays.zones(dny, tf)
    Z[tf] = (np.array([z["dir"] == "bull" for z in zs]), np.array([z["lo"] for z in zs]), np.array([z["hi"] for z in zs]),
             np.array([z["t0"].value for z in zs]), np.array([z["t1"].value for z in zs]))


def edge(t, en, sg, risk):
    best, tv = 99.0, t.value
    for bull, lo, hi, t0, t1 in Z.values():
        m = (bull == (sg < 0)) & (t0 <= tv) & (tv < t1)
        for lv in (lo[m], hi[m]):
            d = (lv - en) * sg / risk; d = d[d > 0.05]
            if len(d): best = min(best, float(d.min()))
    return best


def fun_run(j0, sg, stop):
    en = O[j0]; risk = (en - stop) * sg; legs = (1, 1.5, 2); lv = lambda x: en + sg * x * risk
    st, got, left, k = stop, 0.0, 1.0, 0
    jend = min(j0 + R.SCALP_HOLD, N - 1)
    for j in range(j0, jend + 1):
        if (L[j] <= st) if sg > 0 else (H[j] >= st):
            px = st if (j == j0 or k) else (min(st, O[j]) if sg > 0 else max(st, O[j]))
            return got + left * (px - en) * sg / risk - R.COST / risk, j
        while k < 3 and ((H[j] >= lv(legs[k])) if sg > 0 else (L[j] <= lv(legs[k]))):
            got += legs[k] / 3; left -= 1 / 3
            if k == 0: st = en
            k += 1
        if left <= 1e-9:
            return got - R.COST / risk, j
    return got + left * (C[jend] - en) * sg / risk - R.COST / risk, jend


def fun_sigs(clean_wanted, per_day):
    out, outR, busy, used = [], [], -1, {}
    for i in range(300, N - 40):
        sg = 1 if b4[i] == "bull" else -1 if b4[i] == "bear" else 0
        if not sg or i <= busy or used.get(day[i], 0) >= per_day:
            continue
        sw = R.scalp_trigger(O, H, L, C, e20, a_, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1; risk = (O[j0] - sw) * sg
        if not R.SCALP_RISK[0] <= risk <= R.SCALP_RISK[1]:
            continue
        clean = (R.efficiency(dny, dny.index[j0]) or 0) > R.CHOP_ER
        if clean != clean_wanted or edge(dny.index[j0], O[j0], sg, risk) <= 0.5:
            continue
        r, j = fun_run(j0, sg, sw)
        busy = j; used[day[i]] = used.get(day[i], 0) + 1
        en = O[j0]
        out.append((dny.index[j0], {"dir": "bull" if sg > 0 else "bear", "entry": en, "stop": sw, "tp1": en + sg * risk, "target": en + sg * 2 * risk}, j0))
        outR.append(r)
    return out, outR


q, qR = fun_sigs(True, 3)
report("🎰 Fun Scalp 🔥 QUALITY", q, qR, 3)
cz, czR = fun_sigs(False, 4)
report("🎰 Fun Scalp 🎲 CRAZY", cz, czR, 3)
