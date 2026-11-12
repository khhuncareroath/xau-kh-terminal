"""📊 FLOW verdict (owner, 12 Nov 2026: a TradingView panel that says if order flow agrees with an entry).
Free data only: delta = volume of up-closing candles minus down-closing ones (on OANDA it is tick count; here Dukascopy
volume), measured on 5m. Three readings for a direction d (+1 buy / -1 sell):
  1. DELTA 1h: sum of signed volume over the last 12 candles has the sign of d
  2. CVD slope: the last 6 candles' delta has the sign of d (pressure building now)
  3. VALUE: price is on d's side of the session VWAP (buyers / sellers in control of the day)
AGREE = 2-3 of 3 agree, AGAINST = 2-3 disagree.
Tests: (a) at every 5m candle, does an AGREE-BUY / AGREE-SELL move $5 / $10 its way first more than 50%?
       (b) the 369 replayed M15 signals: R when the flow agrees vs is against at the entry.
Run: python studies/flow_verdict.py"""
import sys, json
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd

df = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
split = df.index[int(len(df) * 0.7)]
O, H, L, C, V = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close", "Volume"))
side = np.sign(C - O); side = pd.Series(side).replace(0, np.nan).ffill().fillna(0).to_numpy()
dv = side * V
d1h = pd.Series(dv).rolling(12).sum().to_numpy()
d30 = pd.Series(dv).rolling(6).sum().to_numpy()
ny = df.index.tz_convert("America/New_York")
sess = ((ny - pd.Timedelta(hours=18)).normalize()).asi8
tp = (H + L + C) / 3
g = pd.DataFrame({"pv": tp * V, "v": V, "s": sess})
vwap = (g.groupby("s").pv.cumsum() / g.groupby("s").v.cumsum().replace(0, np.nan)).to_numpy()


def verdict(i, d):
    votes = [np.sign(d1h[i]) == d, np.sign(d30[i]) == d, np.sign(C[i] - vwap[i]) == d if np.isfinite(vwap[i]) else False]
    k = sum(votes)
    return "agree" if k >= 2 else "against"


def first(i, d, usd):
    p = C[i]
    for k in range(i + 1, min(i + 289, len(C))):
        up, dn = H[k] >= p + usd, L[k] <= p - usd
        if up and dn: return None
        if up: return d > 0
        if dn: return d < 0
    return None


print("(a) every 5m candle (every 3rd, 2 years): does the flow direction move its way first?")
rng = range(300, len(C) - 300, 3)
for usd in (5, 10):
    res = {"all3": [], "two": []}
    for i in rng:
        votes = [np.sign(d1h[i]), np.sign(d30[i]), np.sign(C[i] - vwap[i]) if np.isfinite(vwap[i]) else 0]
        s = sum(votes)
        if s == 0: continue
        d = 1 if s > 0 else -1
        w = first(i, d, usd)
        if w is None: continue
        res["all3" if abs(s) == 3 else "two"].append((df.index[i] >= split, w))
    for k, v in res.items():
        a = np.array(v)
        print(f"  ${usd}: flow {'3 of 3' if k=='all3' else '2 of 3'} agree -> went that way first {100*a[:,1].mean():.1f}% "
              f"(older {100*a[~a[:,0].astype(bool),1].mean():.1f}% / newest {100*a[a[:,0].astype(bool),1].mean():.1f}%), n={len(a)}")

print("\n(b) the 369 replayed M15 signals:")
M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
X = pd.DataFrame([dict(t=df.index[r["j0"]], R=r["R"], v=verdict(r["j0"] - 1, 1 if r["dir"] == "bull" else -1)) for r in M])
X["new"] = X.t >= split
for k, s in X.groupby("v"):
    t = s.R.mean() / s.R.std(ddof=1) * np.sqrt(len(s))
    print(f"  flow {k:8s} {len(s):4d} {100*(s.R>0).mean():3.0f}% win {s.R.mean():+.3f}R t{t:4.1f} | older {s[~s.new].R.mean():+.2f} ({(~s.new).sum()}) newest {s[s.new].R.mean():+.2f} ({s.new.sum()})")
