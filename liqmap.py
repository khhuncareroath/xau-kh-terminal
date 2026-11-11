"""15m liquidity map, the way ICT/SMC mentors read the chart (IRL -> ERL), from closed candles only.

Top-down: Daily -> 4H -> 1H -> 30m -> 15m bias (direction of the last structure break), 5m for confirmation.
On 15m:
  - external swings (5 bars each side) form the DEALING RANGE: range high = buy-side external liquidity (ELQ / ERL),
    range low = sell-side ELQ; the middle = equilibrium (EQ): above = premium, below = discount
  - internal swings (2 bars each side) inside the range = internal liquidity (ILQ / IRL), with unfilled 15m FVGs
  - a SWEEP ($$) = a wick beyond a swing level and a close back inside (stops taken, no acceptance)
  - BOS / CHOCH on internal structure; EMA 20 / 50 / 200 as trend context
  - draw on liquidity: after sell-side liquidity is swept and structure turns up, price usually seeks the buy-side
    ELQ (and the opposite). That is a tendency, not a promise.
  - 5m confirmation: the latest 5m structure break and whether it agrees with the 15m idea.

build(df5) -> dict used by analysis_card (drawing) and text() (the post).
"""
import numpy as np
import pandas as pd

import ict
from engine import atr

EXT_N, INT_N = 5, 2


def _sw(d, n):
    h, l = d["High"].to_numpy(), d["Low"].to_numpy()
    out = []
    for i in range(n, len(d) - n):
        if h[i] == h[i - n:i + n + 1].max():
            out.append((i, "H", float(h[i])))
        if l[i] == l[i - n:i + n + 1].min():
            out.append((i, "L", float(l[i])))
    return out


def _bias(d):
    if len(d) < 30:
        return None
    ev = ict.structure(d, atr(d).to_numpy(), ict.swings(d))
    return ev[-1]["dir"] if ev else None


def _state(d, sw, i_from):
    """For each swing level: taken (closed beyond), swept (wick beyond, close back) or untaken, after it formed."""
    h, l, c = d["High"].to_numpy(), d["Low"].to_numpy(), d["Close"].to_numpy()
    out = []
    for i, kind, p in sw:
        if i < i_from:
            continue
        st, at = "untaken", None
        for j in range(i + 1, len(d)):
            if kind == "H":
                if c[j] > p:
                    st, at = "taken", j
                    break
                if h[j] > p and st == "untaken":
                    st, at = "swept", j
            else:
                if c[j] < p:
                    st, at = "taken", j
                    break
                if l[j] < p and st == "untaken":
                    st, at = "swept", j
        out.append({"i": i, "kind": kind, "price": p, "state": st, "at": at})
    return out


_DAILY = {"t": 0, "bias": None}


def _daily_bias(df5):
    """Daily structure needs ~6 months of daily candles; the live 5m feed only holds ~20 days (the D pill was always
    blank). Uses Yahoo daily candles, cached 6 hours; falls back to the 5m data if that fails."""
    import time
    if time.time() - _DAILY["t"] < 6 * 3600 and _DAILY["bias"] is not None:
        return _DAILY["bias"]
    try:
        from engine import _yahoo
        d = _yahoo("1d", "6mo")
        b = _bias(d)
        if b:
            _DAILY.update(t=time.time(), bias=b)
            return b
    except Exception as e:
        print("daily bias download failed:", e)
    return _bias(ict.resample(df5, "D"))


def build(df5, bars=96):
    d = ict.resample(df5, "15m").tail(400)
    price = float(d["Close"].iloc[-1])
    n = len(d)
    top = {"D": _daily_bias(df5), "4H": _bias(ict.resample(df5, "4H")), "1H": _bias(ict.resample(df5, "1H")),
           "30m": _bias(df5.resample("30min").agg(ict.AGG).dropna()), "15m": _bias(d), "5m": _bias(df5.tail(600))}
    # dealing range: last external swing high and low that are still above / below price
    ext = _state(d, _sw(d, EXT_N), 0)
    alive = lambda x: x["state"] != "taken"           # a level price already closed through is no longer liquidity
    highs = [x for x in ext if x["kind"] == "H" and x["price"] > price and alive(x)]
    lows = [x for x in ext if x["kind"] == "L" and x["price"] < price and alive(x)]
    hh, ll = d["High"].to_numpy(), d["Low"].to_numpy()
    if highs:
        rh = (highs[-1]["i"], "H", highs[-1]["price"])
    else:
        j = max(range(max(0, n - bars), n), key=lambda k: hh[k]); rh = (j, "H", float(hh[j]))
    lows_after = [x for x in lows if x["i"] >= rh[0] - 2 * bars]
    if lows_after:
        rl = (lows_after[-1]["i"], "L", lows_after[-1]["price"])
    else:   # leg low since the range high (not yet a confirmed swing)
        j = min(range(rh[0], n), key=lambda k: ll[k]); rl = (j, "L", float(ll[j]))
    if rl[2] >= price:
        j = min(range(max(0, n - bars), n), key=lambda k: ll[k]); rl = (j, "L", float(ll[j]))
    eq = (rh[2] + rl[2]) / 2
    start = min(rh[0], rl[0])
    # internal liquidity inside the range, after the range started
    inner = [x for x in _state(d, _sw(d, INT_N), start) if rl[2] < x["price"] < rh[2]]
    ilq_up = sorted([x for x in inner if x["kind"] == "H" and x["state"] != "taken" and x["price"] > price], key=lambda x: x["price"])[:2]
    ilq_dn = sorted([x for x in inner if x["kind"] == "L" and x["state"] != "taken" and x["price"] < price], key=lambda x: -x["price"])[:2]
    sweeps = sorted([x for x in inner if x["state"] == "swept"], key=lambda x: x["at"])[-3:]
    # also sweeps of the external range edges
    for x in ext:   # sweeps of external swings (stops taken, close back inside) in the recent window
        if x["state"] == "swept" and x["at"] is not None and x["at"] >= n - 2 * bars:
            sweeps.append(x)
    sweeps = sorted(sweeps, key=lambda x: x["at"])[-3:]
    a15 = atr(d).to_numpy()
    ev = ict.structure(d, a15, ict.swings(d))
    last = ev[-1] if ev else None
    fv = [z for z in ict.find_fvgs(d, a15) if z.get("status") not in ("filled",)] if hasattr(ict, "find_fvgs") else []
    c = d["Close"]
    ema = {k: float(c.ewm(span=k).mean().iloc[-1]) for k in (20, 50, 200)}
    # draw on liquidity
    recent_ss = [s for s in sweeps if s["kind"] == "L" and s["at"] is not None and s["at"] >= n - 24]
    recent_bs = [s for s in sweeps if s["kind"] == "H" and s["at"] is not None and s["at"] >= n - 24]
    draw, why = None, ""
    if last and last["dir"] == "bull" and (recent_ss or price < eq):
        draw = "up"
        why = ("sell-side liquidity was swept, then 15m structure turned up" if recent_ss else
               "15m structure is up and price is in discount")
    elif last and last["dir"] == "bear" and (recent_bs or price > eq):
        draw = "down"
        why = ("buy-side liquidity was swept, then 15m structure turned down" if recent_bs else
               "15m structure is down and price is in premium")
    target = (ilq_up[0]["price"] if ilq_up else rh[2]) if draw == "up" else (ilq_dn[0]["price"] if ilq_dn else rl[2]) if draw == "down" else None
    # mentor-style triggers: BUY on a 15m close above the nearest internal high, SELL below the nearest internal low
    up_lv = [x["price"] for x in ilq_up] + [rh[2]]
    dn_lv = [x["price"] for x in ilq_dn] + [rl[2]]
    gap = max(3.0, 0.8 * float(atr(d).iloc[-1]))      # a target must be a real move away from the trigger
    trig_buy, trig_sell = up_lv[0], dn_lv[0]
    tgt_buy = next((x for x in up_lv[1:] if x - trig_buy >= gap), None)
    tgt_sell = next((x for x in dn_lv[1:] if trig_sell - x >= gap), None)
    if tgt_buy is None:      # nothing left inside the range: aim at the 50% of the range above, as mentors do
        tgt_buy = trig_buy + max(gap, (rh[2] - rl[2]) * 0.25)
    if tgt_sell is None:
        tgt_sell = trig_sell - max(gap, (rh[2] - rl[2]) * 0.25)
    ob = None
    if last:
        try:
            ob = ict.order_block(d, last)
        except Exception:
            ob = None
    return {"trig_buy": trig_buy, "tgt_buy": tgt_buy, "trig_sell": trig_sell, "tgt_sell": tgt_sell, "ob": ob,
            "price": price, "top": top, "rh": rh[2], "rl": rl[2], "rh_i": rh[0], "rl_i": rl[0], "eq": eq,
            "zone": "premium" if price > eq else "discount", "ilq_up": ilq_up, "ilq_dn": ilq_dn, "sweeps": sweeps,
            "last": last, "fvgs": fv[-4:], "ema": ema, "draw": draw, "why": why, "target": target, "d15": d}


W = {"bull": "Bull ↑", "bear": "Bear ↓", None: "Range ↔"}


def text(m, fmt=lambda x: f"{x:,.2f}"):
    """The breakdown post: top-down, dealing range, ELQ / ILQ, sweeps, structure, IRL -> ERL idea, 5m confirmation."""
    t = m["top"]
    p = m["price"]
    out = ["🧠 <b>15m LIQUIDITY MAP · ICT / SMC</b> · Gold <b>" + fmt(p) + "</b>", "",
           "<b>Top-down · ពីធំទៅតូច</b>",
           " · ".join(f"{k} {W[t[k]]}" for k in ("D", "4H", "1H", "30m", "15m")),
           "",
           "<b>Dealing range (15m)</b>",
           f"• High <b>{fmt(m['rh'])}</b> = buy-side <b>ELQ</b> (stops above)",
           f"• Low <b>{fmt(m['rl'])}</b> = sell-side <b>ELQ</b> (stops below)",
           f"• EQ (50%) <b>{fmt(m['eq'])}</b> · price is in <b>{m['zone']}</b> "
           + ("(cheap: better to buy)" if m["zone"] == "discount" else "(expensive: better to sell)"),
           "  <i>ELQ = liquidity ខាងក្រៅ (ចុង range) · ILQ = liquidity ខាងក្នុង</i>", ""]
    il = ([f"above {fmt(x['price'])}" + (" ($$ swept)" if x["state"] == "swept" else "") for x in m["ilq_up"]] +
          [f"below {fmt(x['price'])}" + (" ($$ swept)" if x["state"] == "swept" else "") for x in m["ilq_dn"]])
    if il:
        out += ["<b>Internal liquidity (ILQ / IRL)</b>", "• " + " · ".join(il)]
    if m["fvgs"]:
        z = m["fvgs"][-1]
        out.append(f"• Latest 15m FVG ({z['dir']}) <b>{fmt(z['lo'])}–{fmt(z['hi'])}</b> = IRL, price often fills it")
    if m["sweeps"]:
        s = m["sweeps"][-1]
        t_ = m["d15"].index[s["at"]].strftime("%H:%M") if s.get("at") is not None else ""
        out.append(f"• $$ Last sweep: {'buy' if s['kind'] == 'H' else 'sell'}-side at <b>{fmt(s['price'])}</b> {t_}"
                   f" ({'buyers trapped' if s['kind'] == 'H' else 'sellers trapped'})")
    out.append("")
    if m["last"]:
        e = m["last"]
        out += ["<b>Structure</b>",
                f"• 15m {e['type'].replace('MSS', 'CHOCH')} {e['dir']} at <b>{fmt(e['level'])}</b>"
                + (" with displacement" if e.get("displacement") else "")]
    em = m["ema"]
    out.append(f"• EMA 20 {fmt(em[20])} · 50 {fmt(em[50])} · 200 {fmt(em[200])}: price "
               + ("above all (strong up)" if p > max(em.values()) else "below all (strong down)" if p < min(em.values()) else "mixed"))
    out.append("")
    if m["draw"]:
        up = m["draw"] == "up"
        htf = [t[k] for k in ("D", "4H", "1H")]
        against = sum(1 for b in htf if b == ("bear" if up else "bull"))
        warn = (f"⚠️ <b>Counter-trend</b>: {against} of D/4H/1H point the other way. This is likely a pullback: "
                f"small size, quick targets, or wait for a {'SELL' if up else 'BUY'} setup at {'premium' if up else 'discount'}."
                f"\n  <i>ទិសធំផ្ទុយ: lot តូច ឬរង់ចាំ</i>") if against >= 2 else \
               "✅ <b>With the trend</b>: higher timeframes agree."
        out += ["<b>Draw on liquidity · គោលដៅ liquidity</b>", warn,
                f"• {m['why'].capitalize()} → next target <b>{fmt(m['target'])}</b>, then ELQ <b>{fmt(m['rh'] if up else m['rl'])}</b>",
                f"• 5m confirmation: {W[t['5m']]} " + ("✅ agrees" if t["5m"] == ("bull" if up else "bear") else "⏳ not yet: wait for a 5m CHOCH"),
                f"• Wrong if 15m closes {'below' if up else 'above'} <b>{fmt(m['rl'] if up else m['rh'])}</b>",
                f"📌 <i>{'Bias ឡើង: រង់ចាំ 5m CHOCH ឡើងក្នុង discount ទើបរកទិញ' if up else 'Bias ធ្លាក់: រង់ចាំ 5m CHOCH ធ្លាក់ក្នុង premium ទើបរកលក់'} · គោលដៅ {fmt(m['target'])}</i>"]
    else:
        out += ["<b>Draw on liquidity</b>",
                f"• No clear draw yet. Inside the range: ILQ above and below are the first magnets.",
                "📌 <i>មិនទាន់ច្បាស់: រង់ចាំ sweep + CHOCH មុនសិន</i>"]
    out += ["", "<i>Analysis, not a signal · tested entries come only in 📈 Signals</i>"]
    return "\n".join(out)
