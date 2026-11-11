"""Strategy Edge Auditor (11 Nov 2026, night). Takes the mentor's LTF setups (studies/ltf_ict.py rules: HTF level ->
15m sweep + MSS -> limit at the OB) and asks WHY they fail, trade by trade:
  * MFE / MAE: best and worst move after the fill, in $ and in R (R = the mentor's stop under the OB)
  * stop hunt or wrong direction: of the trades stopped under the OB, how many later reached +2R anyway
  * 4 stop models on the SAME entries, each sized to the same $ risk (results in R, so 1R = the same money):
      A under the OB (mentor) · B under the sweep · C ATR (1.5 x 15m ATR) · D structural (beyond the HTF zone far edge)
  * costs in R, and the result by market regime (trend quality, Day Meter, session, with / against the 4H trend)
Run: python studies/edge_auditor.py
"""
import sys

sys.path.insert(0, '/home/claude/xau-kh-terminal')
src = open('/home/claude/xau-kh-terminal/studies/ltf_ict.py').read().split("rows = []")[0]
exec(src)   # data, zones, bars, setups(), helpers

import research as R
HOLD = 96   # 8 h of 5m candles


def setups_full(zones, tf="15m", sweep=True, disp=0.6):
    """Same detection as ltf_ict.setups (OB edge entry), plus the facts each stop model needs."""
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
                en, buf = float(top), 0.1 * a[k]
                far = z["lo"] if sg > 0 else z["hi"]
                found = dict(t=B["end"][k], sg=sg, entry=en, tf=z["tf"], atr=float(a[k]),
                             stops={"A under OB": float(bot - sg * buf), "B under sweep": float(ext - sg * buf),
                                    "C ATR x1.5": float(en - sg * 1.5 * a[k]), "D beyond HTF zone": float(min(far, ext) - sg * buf if sg > 0 else max(far, ext) - sg * buf)},
                             bias=splus._bias_at(bD, B["end"][k]) == z["dir"] or splus._bias_at(b4, B["end"][k]) == z["dir"])
                break
            used += 1
            if found:
                out.append(found)
            j = (int(t.searchsorted(found["t"])) if found else tap) + 1
    return sorted(out, key=lambda s: s["t"])


def run_stop(sg, en, stop, j0, rr=2.0):
    risk = (en - stop) * sg
    if risk <= 0.5:
        return None
    tgt, jend = en + sg * rr * risk, min(j0 + HOLD, N - 1)
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            return -1.0 - COST / risk
        if j > j0 and ((H[j] >= tgt) if sg > 0 else (L[j] <= tgt)):
            return rr - COST / risk
    return (C[jend] - en) * sg / risk - COST / risk


rows, busy, count = [], None, {}
er4 = None
for s in setups_full(ZONES["all+liquidity"]):
    if not s["bias"]:
        continue
    rA = (s["entry"] - s["stops"]["A under OB"]) * s["sg"]
    if not 1.5 <= rA <= 20 or (busy is not None and s["t"] < busy):
        continue
    dk = (s["t"] - pd.Timedelta(hours=18)).date()
    if count.get(dk, 0) >= 2:
        continue
    sg, en = s["sg"], s["entry"]
    i5 = int(IDX.searchsorted(s["t"]))
    j0 = next((j for j in range(i5, min(i5 + LIMIT_BARS, N)) if ((L[j] <= en) if sg > 0 else (H[j] >= en))), None)
    if j0 is None:
        continue
    jend = min(j0 + HOLD, N - 1)
    path_hi, path_lo = H[j0:jend + 1], L[j0:jend + 1]
    fav = (path_hi - en) if sg > 0 else (en - path_lo)
    adv = (en - path_lo) if sg > 0 else (path_hi - en)
    mfe, mae = float(fav.max()), float(adv.max())
    # first-touch direction test: did price go $10 your way before $10 against?
    hit_f = np.argmax(fav >= 10) if (fav >= 10).any() else 10 ** 9
    hit_a = np.argmax(adv >= 10) if (adv >= 10).any() else 10 ** 9
    stopA = s["stops"]["A under OB"]
    a_hit = np.argmax(adv >= rA) if (adv >= rA).any() else None
    later_2r = bool(a_hit is not None and (fav[a_hit:] >= 2 * rA).any())
    res = {m: run_stop(sg, en, st, j0) for m, st in s["stops"].items()}
    t = IDX[j0]
    rows.append(dict(t=t, old=t < split, side="long" if sg > 0 else "short", tf=s["tf"], riskA=rA, mfe_R=mfe / rA, mae_R=mae / rA,
                     mfe=mfe, mae=mae, dir_ok=hit_f < hit_a, dir_known=min(hit_f, hit_a) < 10 ** 9, stoppedA=a_hit is not None,
                     hunted=later_2r, costR=COST / rA, **{f"R_{m}": v for m, v in res.items()},
                     **{f"risk_{m}": (en - st) * sg for m, st in s["stops"].items()},
                     meter=R.day_used(df, t) or 0, er=R.efficiency(df, t) or 0, hour=t.hour,
                     with4h=splus._bias_at(b4, t) == ("bull" if sg > 0 else "bear")))
    busy = IDX[min(j0 + HOLD, N - 1)] if res["A under OB"] is None else IDX[j0 + 1]
    count[dk] = count.get(dk, 0) + 1

X = pd.DataFrame(rows)
X.to_csv("/home/claude/edge_audit.csv", index=False)
pd.set_option("display.width", 220)
n = len(X)
print(f"MENTOR SETUPS AUDITED: {n} trades over 2 years ({n / (len(set(X.t.dt.date))):.1f} on trading days with a setup)\n")

print("1) WHERE DOES IT BREAK?")
print(f"   median stop under the OB ${X.riskA.median():.1f} · cost ${COST} = {X.costR.median():.2f}R per trade (median), "
      f"{(X.costR > 0.1).mean() * 100:.0f}% of trades pay > 0.10R in cost")
k = X[X.dir_known]
print(f"   direction: price went $10 YOUR way before $10 against in {k.dir_ok.mean() * 100:.0f}% of trades ({len(k)})")
st = X[X.stoppedA]
print(f"   stopped under the OB: {len(st)} ({len(st) / n * 100:.0f}%); of those, {st.hunted.mean() * 100:.0f}% later reached +2R "
      f"(= stop hunt), {100 - st.hunted.mean() * 100:.0f}% never did (= wrong direction)")
print(f"   MFE median {X.mfe_R.median():.2f}R (${X.mfe.median():.1f}) · MAE median {X.mae_R.median():.2f}R (${X.mae.median():.1f})")
print(f"   reached +2R at any time in 8 h: {(X.mfe_R >= 2).mean() * 100:.0f}% · moved 1R against at some point: {(X.mae_R >= 1).mean() * 100:.0f}%")

print("\n2) SAME ENTRIES, 4 STOP MODELS (TP = 2 x that stop; every model risks the same $, so R = same money)")
for m in ("A under OB", "B under sweep", "C ATR x1.5", "D beyond HTF zone"):
    r = X[f"R_{m}"].dropna(); rk = X[f"risk_{m}"]
    o, nw = X[X.old][f"R_{m}"].dropna(), X[~X.old][f"R_{m}"].dropna()
    tt = r.mean() / r.std(ddof=1) * np.sqrt(len(r))
    print(f"   {m:18} SL ${rk.median():5.1f} · stopped {(r < 0).mean() * 100:3.0f}% · win {(r > 0).mean() * 100:3.0f}% · "
          f"avg {r.mean():+.3f}R (older {o.mean():+.2f} / newest {nw.mean():+.2f}) t {tt:+.1f} · cost {(COST / rk).median():.2f}R")

print("\n3) BY MARKET REGIME (stop model A, mentor)")
def g(name, m):
    r = X[m]["R_A under OB"]
    return f"   {name:34} {len(r):4d} trades · win {(r > 0).mean() * 100:3.0f}% · avg {r.mean():+.3f}R"
print(g("clean 4H trend (ER > 0.30)", X.er > 0.30)); print(g("choppy / ranging (ER <= 0.30)", X.er <= 0.30))
print(g("day moving (Day Meter >= 70%)", X.meter >= 0.7)); print(g("quiet day (< 70%)", X.meter < 0.7))
print(g("WITH the 4H structure", X.with4h)); print(g("AGAINST the 4H structure", ~X.with4h))
print(g("London 02-08 NY", (X.hour >= 2) & (X.hour < 8))); print(g("New York 08-12 NY", (X.hour >= 8) & (X.hour < 12)))
print(g("Asia / late", (X.hour >= 12) | (X.hour < 2)))
for lvl in sorted(X.tf.unique()):
    print(g(f"level: {lvl}", X.tf == lvl))
print(g("BEST COMBO: clean trend + moving day + with 4H", (X.er > 0.30) & (X.meter >= 0.7) & X.with4h))
