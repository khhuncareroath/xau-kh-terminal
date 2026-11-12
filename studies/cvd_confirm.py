"""📉 CVD divergence as a HELPER for the live M15 signal (owner, 12 Nov 2026). Not a signal of its own.
For each replayed M15 signal (studies/m15_replay.py output, /tmp/m15_a.json + m15_b.json): did cvd.py show a divergence
the SAME way (agree) or the OTHER way (against) in the hours before the signal? A version counts only if the difference
holds in the older 70% AND the newest 30%. Run: python studies/cvd_confirm.py"""
import sys, json, itertools
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
import cvd, research as R

df = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
split = df.index[int(len(df) * 0.7)]
S = pd.DataFrame(json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json')))
S["t"] = pd.to_datetime(S["t"], utc=True)
S["new"] = S["t"] >= split
print(len(S), "signals", round(S.R.mean(), 3), "R")


def tag(ev, hours):
    E = pd.DataFrame(ev)
    out = []
    for t, d in zip(S.t, S.dir):
        w = E[(E.t <= t) & (E.t > t - pd.Timedelta(hours=hours))] if len(E) else E
        same, opp = (w.dir == d).any(), (w.dir != d).any()
        out.append("both" if same and opp else "agree" if same else "against" if opp else "none")
    return out


def line(g):
    o, n = g[~g.new].R, g[g.new].R
    t = g.R.mean() / g.R.std(ddof=1) * np.sqrt(len(g)) if len(g) > 2 else 0
    return f"{len(g):4d} {100*(g.R>0).mean():3.0f}% {g.R.mean():+.3f}R t{t:4.1f} | old {o.mean():+.2f} ({len(o)}) new {n.mean():+.2f} ({len(n)})"


rows = []
for rule, anchor, hours in itertools.product(["5min", "15min"], ["W", "D"], [2, 4, 8, 12]):
    ev = cvd.events(df, rule, anchor)
    S["c"] = tag(ev, hours)
    print(f"\n== {rule} anchor {anchor}, last {hours} h  ({len(ev)} labels)")
    for k in ["agree", "against", "both", "none"]:
        g = S[S.c == k]
        if len(g):
            print(f"  {k:8s}", line(g))
    a, x = S[S.c.isin(["agree"])], S[S.c.isin(["against", "both"])]
    rest = S[~S.c.isin(["against", "both"])]
    rows.append((rule, anchor, hours, a[~a.new].R.mean() - S[~S.new].R.mean(), a[a.new].R.mean() - S[S.new].R.mean(),
                 x[~x.new].R.mean() - S[~S.new].R.mean(), x[x.new].R.mean() - S[S.new].R.mean(), len(a), len(x), rest.R.mean()))
T = pd.DataFrame(rows, columns=["tf", "anchor", "h", "agree_old", "agree_new", "against_old", "against_new", "n_agree", "n_against", "skip_against_avgR"])
print("\nDifference vs all signals (R per trade), both halves must point the same way:")
print(T.round(3).to_string(index=False))
S.to_pickle("/tmp/cvd_sig.pkl")
