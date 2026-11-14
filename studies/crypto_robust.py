"""Round 2 (written before running): are the two leads from crypto_rules.py real or luck?

Leads: swing_clean (4H breakout, clean 4H trend, held up to 5 days: BTC +0.19R t 1.8, ETH +0.20R t 2.0) and
funding_fade_short (BTC +0.24R t 2.2 PROVEN, but ETH -0.03R). 16 tests were run in round 1, so one pass on one coin is
what luck alone gives about half the time. A real edge should stay positive for nearby settings, on BOTH coins, on
BOTH halves, and with lower (maker) fees too.
Run: python studies/crypto_robust.py
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crypto_rules as cr  # noqa: E402


def swing(x, bks, er=0.30, stop_atr=2.0, tgt_r=3.0, days=5, scaled=False):
    out, busy = [], -1
    for b in bks:
        if b["j0"] <= busy or b["er"] <= er:
            continue
        j0, sg = b["j0"], b["sg"]
        stop = x.o[j0] - sg * stop_atr * b["a4"]
        j_end = min(j0 + days * 288, x.n - 1)
        if scaled:
            r, j = x.run_scaled(j0, j_end, sg, stop, 1.0, tgt_r)
        else:
            r, j = x.run_trade(j0, j_end, sg, stop, x.o[j0] + sg * tgt_r * stop_atr * b["a4"])
        if r is not None:
            out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
            busy = j
    return out


def fund_short(x, pct_cut=0.95, stop_k=0.5, rr=2.0, hold_h=48):
    f = x.fu
    pct = f.rolling(270, min_periods=150).rank(pct=True)
    px = pd.Series(x.c, index=x.ix)
    ret3 = px.reindex(f.index, method="ffill") / px.shift(864).reindex(f.index, method="ffill") - 1
    t = f.index[((pct >= pct_cut) & (ret3 > 0)).fillna(False).to_numpy()]
    return cr._fade(x, t, [-1] * len(t), stop_k, rr, hold_h)


def summary(tr, split):
    if len(tr) < 10:
        return {"n": len(tr)}
    j = cr.judge(tr, split)
    return {"n": len(tr), "avg": j["all"]["avg_R"], "old": j["older_70pct"]["avg_R"], "new": j["newest_30pct"]["avg_R"],
            "t": j["t_stat"], "proven": j["proven"], "by_dir": j.get("by_direction")}


def grid(x, split, fn, params):
    keys = list(params)
    rows = []
    for vals in itertools.product(*params.values()):
        kw = dict(zip(keys, vals))
        s = summary(fn(**kw), split)
        rows.append({"params": kw, **s})
    ok = [r for r in rows if r.get("old") is not None]
    both = sum(1 for r in ok if r["old"] > 0 and r["new"] > 0)
    return {"versions": len(rows), "positive_both_halves": both, "median_avg_R": round(float(np.median([r["avg"] for r in ok])), 3) if ok else None,
            "proven": sum(1 for r in ok if r["proven"]), "rows": rows}


def run(sym):
    df, fu, oi = cr.load(sym)
    x = cr.Ctx(df, fu, oi)
    split = df.index[0] + 0.7 * (df.index[-1] - df.index[0])
    bks = cr.breakouts(x)
    res = {}
    for cost in (0.0012, 0.0006):
        cr.COST_PCT = cost
        tag = "taker 0.12%" if cost > 0.001 else "maker 0.06%"
        res[f"swing grid ({tag})"] = grid(x, split, lambda **k: swing(x, bks, **k),
                                          {"er": [0.25, 0.30, 0.35], "stop_atr": [1.5, 2.0, 2.5], "tgt_r": [2.0, 3.0, 4.0],
                                           "days": [3, 5, 7]})
        res[f"swing scaled half 1R + BE ({tag})"] = grid(x, split, lambda **k: swing(x, bks, scaled=True, **k),
                                                          {"er": [0.30], "stop_atr": [1.5, 2.0, 2.5], "tgt_r": [3.0], "days": [5]})
        res[f"funding short grid ({tag})"] = grid(x, split, lambda **k: fund_short(x, **k),
                                                  {"pct_cut": [0.90, 0.95, 0.97], "stop_k": [0.4, 0.5, 0.7], "rr": [1.5, 2.0, 3.0],
                                                   "hold_h": [24, 48, 72]})
    cr.COST_PCT = 0.0012
    for k, v in res.items():
        print(f"{sym} {k:40s} versions={v['versions']} both_halves+={v['positive_both_halves']} "
              f"median={v['median_avg_R']} proven={v['proven']}", flush=True)
    return res


if __name__ == "__main__":
    out = {s: run(s) for s in (sys.argv[1:] or ["BTCUSDT", "ETHUSDT"])}
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "crypto_robust.json"), "w"), indent=1, default=str)
    lines = ["# Crypto round 2: robustness of the two leads (studies/crypto_robust.py)", "",
             "| Coin | Grid | Versions | Positive on both halves | Median avg R | Proven |", "|---|---|---|---|---|---|"]
    for s, res in out.items():
        for k, v in res.items():
            lines.append(f"| {s} | {k} | {v['versions']} | {v['positive_both_halves']} | {v['median_avg_R']} | {v['proven']} |")
    open(os.path.join(here, "CRYPTO_ROBUST.md"), "w").write("\n".join(lines) + "\n")
