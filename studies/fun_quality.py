"""🎰 Fun Scalp 🔥 QUALITY, quality-only (owner, 14 Nov 2026: "fewer signals is fine, only quality").
Live entries (clean 4H trend, 15m FVG dip, other-side check), 4 a day as live (CRAZY is off, so QUALITY gets all 4).
Pre-set filters, must beat the base on BOTH halves: 1H agrees · Daily agrees · London/NY only · no opposite zone
within 1.0R (live 0.5R) · small stop · and caps of 1 / 2 a day (first ones of the day).
Run: python studies/fun_quality.py"""
import sys, itertools
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np, pandas as pd
src = open('/home/claude/xau-kh-terminal/studies/second_chance.py').read()
exec(src.split("# --- M15 ---")[0])
exec("# --- wide scalp" + src.split("# --- wide scalp")[1].split("q, qR = fun_sigs")[0])
qf = open('/home/claude/xau-kh-terminal/studies/quality_filters.py').read()
b1 = R._bias(dny, "1H", pd.Timedelta(hours=1)); bD = R._bias(dny, "D", pd.Timedelta(days=1))
exec("def line" + qf.split("def line")[1].split("def study")[0])

rows = []
for cap in (4, 2, 1):
    sigs, Rs = fun_sigs(True, cap)
    for (t, s, j0), r in zip(sigs, Rs):
        sg = 1 if s["dir"] == "bull" else -1; risk = abs(s["entry"] - s["stop"]); d = s["dir"]; hr = t.hour + t.minute / 60
        rows.append(dict(cap=cap, t=t, R=r, F1=b1[j0 - 1] == d, F2=bD[j0 - 1] == d, F3=2 <= hr < 12,
                         F4=edge(t, s["entry"], sg, risk) > 1.0, risk=risk))
X = pd.DataFrame(rows); X["new"] = X.t >= split
names = {"F1": "1H agrees", "F2": "Daily agrees", "F3": "London/NY only", "F4": "no opposite zone <1R", "F5": "small stop"}
for cap in (4, 2, 1):
    S = X[X.cap == cap].copy(); S["F5"] = S.risk <= S.risk.median()
    if cap == 4:
        bo, bn = S[~S.new].R.mean(), S[S.new].R.mean()
    print(f"\n== 🔥 QUALITY, max {cap} a day")
    line("as is", S, bo if cap != 4 else -9, bn if cap != 4 else -9)
    for f in names:
        line(names[f], S[S[f]], bo, bn)
    for a, b in itertools.combinations(names, 2):
        line(f"{names[a]} + {names[b]}", S[S[a] & S[b]], bo, bn)
    full = (S.R <= -0.9).mean()
    print(f"  (full SL {100*full:.0f}% of trades)")

print("\nresearch.judge:")
for cap, f, nm in ((1, None, "max 1 a day"), (1, "F1", "max 1 a day + 1H agrees"), (2, None, "max 2 a day"), (2, "F1", "max 2 a day + 1H agrees")):
    S = X[(X.cap == cap) & (X[f] if f else True)]
    j = R.judge([(t, r) for t, r in zip(S.t, S.R)], split)
    print(f"  {nm:26s} {len(S)} t {j['t_stat']} older {j['older_70pct']['avg_R']} newest {j['newest_30pct']['avg_R']} ({j['newest_30pct']['trades']}) q {j['positive_quarters']} proven {j['proven']}")
