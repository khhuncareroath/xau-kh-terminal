"""Do the gold rules work on crypto? (BTC / ETH USDT-M perpetuals, 5m, Jan 2020 - today, Binance public archive)

Same proof rules as gold (research.judge: 30+ trades, +0.10R, t >= 2, newest 30% positive with 10+ trades, 60% of
quarters positive). Everything is chosen on BTC; ETH is run UNCHANGED as a second out-of-sample check.
Costs: 0.12% of price per round trip (taker 0.05% x 2 + 0.02% slippage) PLUS the real funding paid/received while the
trade is open. Alert delay 15 min (3 candles) like gold. "Day" = UTC day (07:00 Cambodia).
Gold's $ settings are converted with the 20-day median daily range (ADR): gold's 0.55% stop was ~0.4 ADR, the scalp
stop range $3-12 was ~0.06-0.23 ADR, the volume-plan risk cap 0.6% was ~0.45 ADR.

Tests were written down BEFORE running (to keep the number of tries small):
  brk_*      4H breakout of the last 30 4H candles (gold's proven signal) with gold's filters and exits
  swing_*    the same breakout held up to 5 days (classic trend following)
  scalp      gold's live ⚡ scalp: 24 h after a 4H breakout, 5m dip into a 15m FVG + confirmation, clean 4H, 1H agrees,
             first of the day, TP 2R, 3 h
  vp_turn    gold's 📊 volume turn: last session's P/b profile against the 4H, pullback to the POC, 15m close back, 2R
  funding_*  crypto only: funding in its top / bottom 5% of 90 days after a 3-day move the same way -> fade it
  oi_*       crypto only: open interest 24 h change in its bottom 5% (flush, price down) -> buy; top 5% + price up -> sell
Run: python studies/crypto_rules.py  (needs data/crypto from studies/crypto_data.py)
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import atr  # noqa: E402
from ict import structure, swings  # noqa: E402
from research import fvg_15m_state, judge, scalp_trigger  # noqa: E402

DATA = os.environ.get("CRYPTO_DATA", os.path.join(ROOT, "data", "crypto"))
COST_PCT = 0.0012
LAT = 3
AGG = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum", "TakerBuy": "sum"}


def load(sym):
    df = pd.read_csv(os.path.join(DATA, f"{sym}_5m.csv.gz"), index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True)
    fu = pd.read_csv(os.path.join(DATA, f"{sym}_funding.csv.gz"), index_col=0, parse_dates=True)
    fu.index = pd.to_datetime(fu.index, utc=True)
    oi = None
    p = os.path.join(DATA, f"{sym}_oi.csv.gz")
    if os.path.exists(p):
        oi = pd.read_csv(p, index_col=0, parse_dates=True)
        oi.index = pd.to_datetime(oi.index, utc=True)
    return df, fu["funding"], oi


def rs(df, rule):
    return df.resample(rule, origin="epoch").agg(AGG).dropna()


class Ctx:
    """Everything a rule needs, computed once per symbol."""

    def __init__(self, df, fu, oi):
        self.df, self.fu, self.oi = df, fu, oi
        self.o, self.h, self.l, self.c = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
        self.n = len(df)
        self.ix = df.index
        day = df.index.floor("D")
        self.day = day
        g = pd.DataFrame({"h": self.h, "l": self.l}, index=day).groupby(level=0).agg(h=("h", "max"), l=("l", "min"))
        rng = g["h"] - g["l"]
        adr = rng.rolling(20, min_periods=10).median().shift(1)        # previous 20 UTC days only
        self.adr = adr.reindex(day).to_numpy()
        # range of today so far (UTC day), causal
        s = pd.Series(self.h, index=df.index).groupby(day).cummax().to_numpy()
        t = pd.Series(self.l, index=df.index).groupby(day).cummin().to_numpy()
        self.today_rng = s - t
        self.d4 = rs(df, "4h")
        self.a4 = atr(self.d4).to_numpy()
        self.f_t, self.f_v = fu.index, fu.cumsum().to_numpy()

    def funding_paid(self, t0, t1):
        """Sum of funding rates charged between t0 and t1 (a long pays a positive rate)."""
        ti, fv = self.f_t, self.f_v
        a = ti.searchsorted(t0, side="right"); b = ti.searchsorted(t1, side="right")
        lo = fv[a - 1] if a > 0 else 0.0
        hi = fv[b - 1] if b > 0 else 0.0
        return float(hi - lo)

    def _cost(self, j0, j, sg, risk):
        en = self.o[j0]
        return (COST_PCT * en + sg * self.funding_paid(self.ix[j0], self.ix[j]) * en) / risk

    def run_trade(self, j0, j_end, sg, stop, tgt):
        o, h, l, c = self.o, self.h, self.l, self.c
        en = o[j0]; risk = (en - stop) * sg
        if risk <= 0:
            return None, j0
        for j in range(j0, j_end + 1):
            if (l[j] <= stop) if sg > 0 else (h[j] >= stop):
                px = stop if j == j0 else (min(stop, o[j]) if sg > 0 else max(stop, o[j]))
                return (px - en) * sg / risk - self._cost(j0, j, sg, risk), j
            if (h[j] >= tgt) if sg > 0 else (l[j] <= tgt):
                return (tgt - en) * sg / risk - self._cost(j0, j, sg, risk), j
        return (c[j_end] - en) * sg / risk - self._cost(j0, j_end, sg, risk), j_end

    def run_scaled(self, j0, j_end, sg, stop, tp1=1.0, tp2=3.0, part=0.5):
        o, h, l, c = self.o, self.h, self.l, self.c
        en = o[j0]; risk = (en - stop) * sg
        if risk <= 0:
            return None, j0
        lv = lambda r: en + sg * r * risk  # noqa: E731
        st, got, left, hit1 = stop, 0.0, 1.0, False
        for j in range(j0, j_end + 1):
            if (l[j] <= st) if sg > 0 else (h[j] >= st):
                px = st if (j == j0 or hit1) else (min(st, o[j]) if sg > 0 else max(st, o[j]))
                return got + left * (px - en) * sg / risk - self._cost(j0, j, sg, risk), j
            if not hit1 and ((h[j] >= lv(tp1)) if sg > 0 else (l[j] <= lv(tp1))):
                got, left, hit1, st = got + part * tp1, left - part, True, en
            if hit1 and ((h[j] >= lv(tp2)) if sg > 0 else (l[j] <= lv(tp2))):
                return got + left * tp2 - self._cost(j0, j, sg, risk), j
        return got + left * (c[j_end] - en) * sg / risk - self._cost(j0, j_end, sg, risk), j_end

    def bias(self, rule, delay):
        d = rs(self.df, rule)
        ev = structure(d, atr(d).to_numpy(), swings(d))
        out = np.array([None] * self.n, dtype=object)
        for e in ev:
            k = int(self.ix.searchsorted(d.index[e["i"]] + delay))
            if k < self.n:
                out[k:] = e["dir"]
        return out


def breakouts(x):
    """Every 4H close beyond the last 30 4H candles, with gold's tested features attached."""
    d4 = x.d4
    H, L, C, O = (d4[k].to_numpy() for k in ("High", "Low", "Close", "Open"))
    V, B = d4["Volume"].to_numpy(), d4["TakerBuy"].to_numpy()
    hi30 = d4["High"].rolling(30).max().shift(1).to_numpy()
    lo30 = d4["Low"].rolling(30).min().shift(1).to_numpy()
    out = []
    for k in range(31, len(d4)):
        sg = 1 if C[k] > hi30[k] else -1 if C[k] < lo30[k] else 0
        if not sg or not np.isfinite(x.a4[k]):
            continue
        t_close = d4.index[k] + pd.Timedelta(hours=4)
        i = int(x.ix.searchsorted(t_close)) - 1
        j0 = i + 1 + LAT
        if j0 + 2 >= x.n or not np.isfinite(x.adr[i]) or x.adr[i] <= 0:
            continue
        rng = H[k] - L[k]
        cl = ((C[k] - L[k]) / rng if sg > 0 else (H[k] - C[k]) / rng) if rng > 0 else 0.5
        w = C[k - 30:k + 1]
        path = np.abs(np.diff(w)).sum()
        er = abs(w[-1] - w[0]) / path if path > 0 else 0
        out.append(dict(k=k, i=i, j0=j0, sg=sg, cl=cl, er=er, used=x.today_rng[i] / x.adr[i],
                        delta=sg * (2 * B[k] - V[k]) / V[k] if V[k] > 0 else 0.0, a4=x.a4[k]))
    return out


def brk(x, bks, filt, stop_k=0.4, swing=False):
    out, busy = [], -1
    for b in bks:
        if b["j0"] <= busy or not filt(b):
            continue
        j0, sg = b["j0"], b["sg"]
        if swing:
            stop = x.o[j0] - sg * 2 * b["a4"]
            r, j = x.run_trade(j0, min(j0 + 5 * 288, x.n - 1), sg, stop, x.o[j0] + sg * 6 * b["a4"])
        else:
            stop = x.o[j0] - sg * stop_k * x.adr[b["i"]]
            r, j = x.run_scaled(j0, min(j0 + 144, x.n - 1), sg, stop)
        if r is not None:
            out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
            busy = j
    return out


CLEAN = lambda b: b["er"] > 0.30                                          # noqa: E731
APLUS_BPLUS = lambda b: b["er"] > 0.30 and b["cl"] >= 0.7 and b["used"] >= 0.7   # noqa: E731  (gold live A+/B+)


def scalp(x, bks):
    o, h, l, c, n = x.o, x.h, x.l, x.c, x.n
    a = atr(x.df).to_numpy()
    e20 = pd.Series(c).ewm(span=20).mean().to_numpy()
    fd, flo, fhi = fvg_15m_state(x.df)
    b1 = x.bias("1h", pd.Timedelta(hours=1))
    act = np.zeros(n)
    for b in bks:
        act[b["i"] + 3:min(b["i"] + 24 * 12, n)] = b["sg"]
    erk = {b["k"]: b["er"] for b in bks}
    c4 = x.d4["Close"].to_numpy()
    k4 = x.d4.index
    out, busy, used = [], -1, set()
    for i in range(300, n - 2):
        sg = int(act[i])
        if sg == 0 or i <= busy or x.day[i] in used:
            continue
        sw = scalp_trigger(o, h, l, c, e20, a, fd, flo, fhi, i, sg)
        if sw is None:
            continue
        j0 = i + 1
        risk = (o[j0] - sw) * sg
        if not np.isfinite(x.adr[i]) or not 0.06 * x.adr[i] <= risk <= 0.23 * x.adr[i]:
            continue
        k = int(k4.searchsorted(x.ix[i] - pd.Timedelta(hours=4), side="right")) - 1   # last closed 4H candle
        if k < 31:
            continue
        w = c4[k - 30:k + 1]; path = np.abs(np.diff(w)).sum()
        if path <= 0 or abs(w[-1] - w[0]) / path <= 0.30:
            continue
        if b1[i] != ("bull" if sg > 0 else "bear"):
            used.add(x.day[i])            # as live: the day's first valid setup decides the day
            continue
        r, j = x.run_trade(j0, min(j0 + 36, n - 1), sg, sw, o[j0] + sg * 2 * risk)
        if r is None:
            continue
        busy = j; used.add(x.day[i])
        out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
    _ = erk
    return out


def _vp(h, l, c, v, ix, step):
    lo, hi = l[ix].min(), h[ix].max()
    bins = np.arange(lo, hi + step, step)
    vol = np.zeros(len(bins))
    tp = (h[ix] + l[ix] + c[ix]) / 3
    np.add.at(vol, np.clip(((tp - bins[0]) / step).astype(int), 0, len(bins) - 1), np.maximum(v[ix], 1e-9))
    p = int(vol.argmax()); a = b = p; acc, tot = vol[p], vol.sum()
    while acc < 0.7 * tot:
        up = vol[b + 1] if b + 1 < len(vol) else -1
        dn = vol[a - 1] if a > 0 else -1
        if up >= dn:
            b += 1; acc += up
        else:
            a -= 1; acc += dn
    return bins[p], bins[a], bins[b], lo, hi


def vp_turn(x, th=0.55, rr=2.0):
    o, h, l, c = x.o, x.h, x.l, x.c
    v = x.df["Volume"].to_numpy()
    ny = x.ix.tz_convert("America/New_York")
    hr = ny.hour + ny.minute / 60
    nyday = (ny - pd.Timedelta(hours=18)).date
    sess = np.where((hr >= 18) | (hr < 2), 0, np.where(hr < 7, 1, np.where(hr < 12, 2, -1)))
    key = pd.Series(list(zip(nyday, sess)))
    groups = {}
    for i, (kk, s_) in enumerate(zip(key, sess)):
        if s_ >= 0:
            groups.setdefault(kk, []).append(i)
    order = sorted(groups)
    b4 = x.bias("4h", pd.Timedelta(hours=4))
    out = []
    for g0, g1 in zip(order[:-1], order[1:]):
        prev, nxt = np.array(groups[g0]), groups[g1]
        if len(prev) < 30 or len(nxt) < 4:
            continue
        step = c[prev[-1]] * 0.0002
        poc, val, vah, lo, hi = _vp(h, l, c, v, prev, step)
        pos = (poc - lo) / (hi - lo) if hi > lo else 0.5
        if th > pos > 1 - th:
            continue
        sg, wrong = (1, val) if pos >= th else (-1, vah)
        touched = None
        for i in nxt:
            if touched is None and ((l[i] <= poc) if sg > 0 else (h[i] >= poc)):
                touched = i
                continue
            if touched is None or i - touched > 12 or x.ix[i].minute % 15 != 10:
                continue
            if (c[i] > poc) if sg > 0 else (c[i] < poc):
                j0 = i + 1 + LAT
                adr = x.adr[i]
                if j0 + 1 >= x.n or not np.isfinite(adr) or x.today_rng[i] / adr >= 0.7:
                    break
                if b4[i] == ("bull" if sg > 0 else "bear"):     # 4H already agrees: not a turn
                    break
                ext = l[touched:i + 1].min() if sg > 0 else h[touched:i + 1].max()
                stop = min(wrong, ext - step) if sg > 0 else max(wrong, ext + step)
                risk = abs(o[j0] - stop)
                if risk > 0.45 * adr:
                    break
                r, j = x.run_trade(j0, min(nxt[-1] + 36, x.n - 1), sg, stop, o[j0] + sg * rr * risk)
                if r is not None:
                    out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
                break
    return out


def _fade(x, times, sgs, stop_k=0.5, rr=2.0, hold_h=48):
    out, busy = [], -1
    for t, sg in zip(times, sgs):
        i = int(x.ix.searchsorted(t)) - 1
        j0 = i + 1 + LAT
        if i < 0 or j0 + 2 >= x.n or j0 <= busy or not np.isfinite(x.adr[i]):
            continue
        stop = x.o[j0] - sg * stop_k * x.adr[i]
        r, j = x.run_trade(j0, min(j0 + hold_h * 12, x.n - 1), sg, stop, x.o[j0] + sg * rr * stop_k * x.adr[i])
        if r is not None:
            out.append((x.ix[j0], r, "long" if sg > 0 else "short"))
            busy = j
    return out


def funding_fade(x, side):
    f = x.fu
    pct = f.rolling(270, min_periods=150).rank(pct=True)
    px = pd.Series(x.c, index=x.ix)
    ret3 = px.reindex(f.index, method="ffill") / px.shift(864).reindex(f.index, method="ffill") - 1
    if side == "short":
        m = (pct >= 0.95) & (ret3 > 0)
    else:
        m = (pct <= 0.05) & (ret3 < 0)
    t = f.index[m.fillna(False).to_numpy()]
    return _fade(x, t, [-1 if side == "short" else 1] * len(t))


def oi_signal(x, side):
    if x.oi is None or len(x.oi) < 1000:
        return []
    oi = x.oi["sum_open_interest"].resample("1h").last().dropna()
    ch = oi.pct_change(24)
    pct = ch.rolling(24 * 90, min_periods=24 * 30).rank(pct=True)
    px = pd.Series(x.c, index=x.ix).resample("1h").last().reindex(oi.index, method="ffill")
    r24 = px.pct_change(24)
    m = ((pct <= 0.05) & (r24 < 0)) if side == "flush_long" else ((pct >= 0.95) & (r24 > 0))
    t = oi.index[m.fillna(False).to_numpy()] + pd.Timedelta(hours=1)
    keep, last = [], None
    for tt in t:                     # one signal per 24 h
        if last is None or tt - last >= pd.Timedelta(hours=24):
            keep.append(tt); last = tt
    return _fade(x, keep, [1 if side == "flush_long" else -1] * len(keep))


def per_year(tr):
    y = {}
    for t, r, *_ in tr:
        y.setdefault(t.year, []).append(r)
    return {k: {"n": len(v), "avg_R": round(float(np.mean(v)), 3)} for k, v in sorted(y.items())}


def study(sym):
    df, fu, oi = load(sym)
    x = Ctx(df, fu, oi)
    split = df.index[0] + 0.7 * (df.index[-1] - df.index[0])
    bks = breakouts(x)
    tests = {
        "brk_all": lambda: brk(x, bks, lambda b: True),
        "brk_clean": lambda: brk(x, bks, CLEAN),
        "brk_aplus_bplus (gold live rule)": lambda: brk(x, bks, APLUS_BPLUS),
        "brk_aplus_only (day 100%+)": lambda: brk(x, bks, lambda b: APLUS_BPLUS(b) and b["used"] >= 1.0),
        "brk_aplus_bplus stop 0.3 ADR": lambda: brk(x, bks, APLUS_BPLUS, 0.3),
        "brk_aplus_bplus stop 0.5 ADR": lambda: brk(x, bks, APLUS_BPLUS, 0.5),
        "brk_aplus_bplus + delta agrees": lambda: brk(x, bks, lambda b: APLUS_BPLUS(b) and b["delta"] > 0),
        "brk_aplus_bplus + delta against": lambda: brk(x, bks, lambda b: APLUS_BPLUS(b) and b["delta"] <= 0),
        "swing_all": lambda: brk(x, bks, lambda b: True, swing=True),
        "swing_clean": lambda: brk(x, bks, CLEAN, swing=True),
        "scalp (gold live rule)": lambda: scalp(x, bks),
        "vp_turn (gold live rule)": lambda: vp_turn(x),
        "funding_fade_short": lambda: funding_fade(x, "short"),
        "funding_fade_long": lambda: funding_fade(x, "long"),
        "oi_flush_long": lambda: oi_signal(x, "flush_long"),
        "oi_crowded_short": lambda: oi_signal(x, "crowded_short"),
    }
    res = {"symbol": sym, "from": str(df.index[0]), "to": str(df.index[-1]), "split": str(split),
           "breakouts": len(bks), "tests": {}}
    for name, fn in tests.items():
        tr = fn()
        j = judge(tr, split) if tr else {"all": {"trades": 0}, "proven": False, "verdict": "no trades"}
        months = max(1.0, (df.index[-1] - df.index[0]).days / 30.4)
        j["per_month"] = round(len(tr) / months, 2)
        j["total_R"] = round(float(sum(r for _, r, *_ in tr)), 1)
        j["per_year"] = per_year(tr)
        res["tests"][name] = j
        a = j["all"]
        print(f"{sym:8s} {name:36s} n={a.get('trades', 0):4d} win={a.get('win_rate_pct')} avg={a.get('avg_R')} "
              f"old={j.get('older_70pct', {}).get('avg_R')} new={j.get('newest_30pct', {}).get('avg_R')} "
              f"t={j.get('t_stat')} proven={j['proven']}", flush=True)
    return res


def markdown(all_res):
    lines = ["# Crypto test results (generated by studies/crypto_rules.py)", ""]
    for res in all_res:
        lines += [f"## {res['symbol']} · {res['from'][:10]} to {res['to'][:10]} · newest 30% from {res['split'][:10]}", "",
                  "| Test | Trades | /month | Win | Avg R | Older / newest | t | Quarters + | Proven |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, j in res["tests"].items():
            a, o, nw = j["all"], j.get("older_70pct", {}), j.get("newest_30pct", {})
            lines.append(f"| {name} | {a.get('trades', 0)} | {j['per_month']} | {a.get('win_rate_pct')}% | {a.get('avg_R')} | "
                         f"{o.get('avg_R')} / {nw.get('avg_R')} ({nw.get('trades')}) | {j.get('t_stat')} | "
                         f"{j.get('positive_quarters')} | {'YES' if j['proven'] else 'no'} |")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    syms = sys.argv[1:] or ["BTCUSDT", "ETHUSDT"]
    allr = [study(s) for s in syms]
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "crypto_results.json"), "w") as f:
        json.dump(allr, f, indent=1, default=str)
    with open(os.path.join(here, "CRYPTO_RESULTS.md"), "w") as f:
        f.write(markdown(allr))
