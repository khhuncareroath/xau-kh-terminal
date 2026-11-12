"""⏳ Wait for 5m confirmation after the M15 signal (owner, 12 Nov 2026, after the morning SELL swept the high, hit the
SL, then fell). Instead of entering at the signal: wait on 5m for a liquidity SWEEP against the signal (price takes the
5m high / low of the last LIQ_BARS before the signal), then CONFIRMATION back the signal's way, enter, SL beyond the sweep.

Confirmation: MSS = a 5m close beyond the last swing low (sell) / high (buy) made before the sweep extreme;
              CISD = a 5m close beyond the open of the first candle of the run into the sweep extreme.
Entry: market at the confirming close, or a limit retest at the broken level (waits RETEST bars).
SL: sweep extreme + 0.1 x 5m ATR (max $25). Targets: the signal's own TP1 / TP2 prices (half at TP1, SL to entry),
skipped if TP1 is less than 0.5R away. 8 h max, $0.40 cost. Window: WAIT hours after the signal.
Signals that never sweep + confirm are not traded (0R): that is the cost of waiting.
Input: the 369 replayed live signals (studies/m15_replay.py -> /tmp/m15_a.json, /tmp/m15_b.json).
Run: python studies/m15_ltf_confirm.py"""
import sys, json, itertools
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd

df = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
pc = np.r_[C[0], C[:-1]]
ATR = pd.Series(np.maximum.reduce([H - L, abs(H - pc), abs(L - pc)])).rolling(14).mean().to_numpy()
split = df.index[int(len(df) * 0.7)]
S = pd.DataFrame(json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json')))
S["t"] = pd.to_datetime(S["t"], utc=True)
S["new"] = S["t"] >= split
N = len(df)


def grade(sg, en, st, tp1, tp2, j0):
    risk = abs(en - st)
    jend = min(j0 + 96, N - 1)
    stop, got, left, hit1 = st, 0.0, 1.0, False
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            return got + left * (stop - en) * sg / risk - 0.4 / risk
        if not hit1 and ((H[j] >= tp1) if sg > 0 else (L[j] <= tp1)):
            got, left, hit1, stop = got + 0.5 * abs(tp1 - en) / risk, 0.5, True, en
        if hit1 and ((H[j] >= tp2) if sg > 0 else (L[j] <= tp2)):
            return got + left * abs(tp2 - en) / risk - 0.4 / risk
    return got + left * (C[jend] - en) * sg / risk - 0.4 / risk


def wait_trade(r, liq_bars, wait_h, conf, entry, retest=6):
    sg = 1 if r.dir == "bull" else -1
    j0 = int(r.j0)
    # liquidity against the signal: for a SELL the 5m high of the last liq_bars (incl. the signal candle area)
    lvl = H[j0 - liq_bars:j0].max() if sg < 0 else L[j0 - liq_bars:j0].min()
    jmax = min(j0 + wait_h * 12, N - 100)
    swept, ext, jext = False, None, None
    for j in range(j0, jmax):
        if not swept:
            if (H[j] > lvl) if sg < 0 else (L[j] < lvl):
                swept, ext, jext = True, (H[j] if sg < 0 else L[j]), j
            continue
        # keep tracking the sweep extreme
        if (H[j] > ext) if sg < 0 else (L[j] < ext):
            ext, jext = (H[j] if sg < 0 else L[j]), j
            continue
        if conf == "mss":
            seg = slice(max(j0 - 6, jext - 8), jext)
            key = L[seg].min() if sg < 0 else H[seg].max()
        else:   # cisd: open of the first candle of the run into the extreme
            k = jext
            while k > j0 - 6 and ((C[k] > O[k]) if sg < 0 else (C[k] < O[k])):
                k -= 1
            key = O[min(k + 1, jext)]
        if (C[j] < key) if sg < 0 else (C[j] > key):
            st = ext + sg * -1 * 0.1 * ATR[j]
            if entry == "market":
                en, jin = C[j], j + 1
            else:
                en, jin = key, None
                for k in range(j + 1, min(j + 1 + retest, N - 100)):
                    if (H[k] >= key) if sg < 0 else (L[k] <= key):
                        jin = k
                        break
                    if (L[k] <= r.tp1p) if sg < 0 else (H[k] >= r.tp1p):
                        break
                if jin is None:
                    return None
            risk = abs(en - st)
            if risk <= 0.5 or risk > 25 or (r.tp1p - en) * sg < 0.5 * risk:
                return None
            if entry == "retest" and ((H[jin] >= st) if sg < 0 else (L[jin] <= st)):
                return -1 - 0.4 / risk
            return grade(sg, en, st, r.tp1p, r.tp2p, jin + (0 if entry == "market" else 1))
    return None


def show(name, R, base):
    R = pd.Series(R, index=S.index)
    taken = R.dropna()
    tot = R.fillna(0)
    t = taken.mean() / taken.std(ddof=1) * np.sqrt(len(taken)) if len(taken) > 2 else 0
    o, n = taken[~S.new[taken.index]], taken[S.new[taken.index]]
    print(f"{name:34s} {len(taken):4d} trades {100*(taken>0).mean():3.0f}% win {taken.mean():+.3f}R t{t:4.1f} "
          f"| old {o.mean():+.2f} new {n.mean():+.2f} | total {tot.sum():+6.1f}R (old {tot[~S.new].sum():+.1f} / new {tot[S.new].sum():+.1f})")
    return R


print(f"{len(S)} live signals. Baseline (enter at the signal): {100*(S.R>0).mean():.0f}% win {S.R.mean():+.3f}R, "
      f"total {S.R.sum():+.1f}R (old {S.R[~S.new].sum():+.1f} / new {S.R[S.new].sum():+.1f})\n")
best = {}
for liq, wait_h, conf, entry in itertools.product([6, 12, 24], [2, 4], ["mss", "cisd"], ["market", "retest"]):
    R = [wait_trade(r, liq, wait_h, conf, entry) for r in S.itertuples()]
    best[(liq, wait_h, conf, entry)] = show(f"liq {liq*5}m wait {wait_h}h {conf} {entry}", R, S.R)

# what about the signals that DID sweep: how did the normal entry do on those?
R = best[(12, 4, "mss", "market")]
sw = R.notna()
print(f"\nSignals that later swept + confirmed (liq 60m, 4h, mss): {sw.sum()}; normal entry on them {S.R[sw].mean():+.3f}R, "
      f"waiting {R[sw].mean():+.3f}R. Signals that never swept: {(~sw).sum()}, normal entry {S.R[~sw].mean():+.3f}R (missed by waiting)")


# ---- Second chance (owner's morning case): KEEP the normal entry, ADD a re-entry after sweep + MSS ----
def sl_hit_bar(r):
    sg = 1 if r.dir == "bull" else -1
    for j in range(int(r.j0), min(int(r.j0) + 96, N - 1)):
        if (L[j] <= r.stop) if sg > 0 else (H[j] >= r.stop):
            return j
    return None


def reentry(r, liq, wait_h, entry, after_sl):
    if after_sl:
        jsl = sl_hit_bar(r)
        if jsl is None:
            return None
    x = wait_trade(r, liq, wait_h, "mss", entry)
    return x


print("\nSECOND CHANCE: normal signal + a re-entry after a 5m sweep + MSS (both counted)")
for liq, wait_h, entry, after_sl in itertools.product([6, 12, 24], [4, 6], ["market", "retest"], [False, True]):
    add = pd.Series([reentry(r, liq, wait_h, entry, after_sl) for r in S.itertuples()], index=S.index)
    a = add.dropna()
    if len(a) < 3:
        continue
    t = a.mean() / a.std(ddof=1) * np.sqrt(len(a))
    o, n = a[~S.new[a.index]], a[S.new[a.index]]
    tot = S.R.sum() + a.sum()
    print(f"liq {liq*5:3d}m wait {wait_h}h {entry:6s} {'only after SL hit' if after_sl else 'any time       '}: "
          f"{len(a):3d} re-entries ({len(a)/24:.1f}/mo) {100*(a>0).mean():3.0f}% win {a.mean():+.2f}R t{t:4.1f} "
          f"old {o.mean():+.2f} ({len(o)}) new {n.mean():+.2f} ({len(n)}) | total {S.R.sum():+.0f} -> {tot:+.0f}R")
