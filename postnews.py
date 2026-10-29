"""Post-news reaction: after a high-impact USD release (FOMC, CPI, NFP...), measures how gold actually reacted and,
only if the reaction is clean, publishes a pullback plan with entry zone, stop, invalidation, TP1/TP2 and expiry.

Why it waits: the first minutes after a release are spread-blowouts and whipsaws. The engine lets 15 minutes of
candles close, then judges the move. It does not trade the headline number itself.

The plan (continuation after a pullback), for an up move from the pre-release price to the reaction high:
  entry zone = 50%-61.8% retracement of that leg, invalidation = a 5m close beyond 78.6%,
  stop just beyond that, TP1 = the reaction extreme, TP2 = the next liquidity level beyond it.
Five factors are checked and shown ("4 of 5"). With fewer than PN_MIN_FACTORS (3), a short "no clean setup" card
is posted instead of levels, so members still know what happened.

Not backtested yet: there are only a few releases per month, so treat it as experimental until track.py has
graded enough of them. Run every cycle after ict.py:  python postnews.py
"""
import json
import os
import re
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ai_analyst import explain
from engine import atr, load
from tg import esc, fmt, local, log_alert, send

MIN_FACTORS = int(os.environ.get("PN_MIN_FACTORS", 3))
REACT_MIN = 15          # minutes of candles to judge the reaction
LATEST_MIN = 90         # after this, the release is old news: no plan
PLAN_VALID_MIN = 75     # plan expires this long after the release (or before the next high-impact event)
INVERSE = ("unemployment", "jobless", "claims")   # higher number = weaker USD = usually better for gold


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def num(s):
    m = re.search(r"-?\d+(\.\d+)?", str(s or "").replace(",", ""))
    return float(m.group()) if m else None


def surprise(evts):
    """+1 gold-bullish surprise, -1 gold-bearish, 0 in line, None if no actual figure in the feed."""
    votes = []
    for e in evts:
        a, f = num(e.get("actual")), num(e.get("forecast"))
        if a is None or f is None:
            continue
        if a == f:
            votes.append(0)
            continue
        usd_up = (a > f) != any(w in e["title"].lower() for w in INVERSE)
        votes.append(-1 if usd_up else 1)
    return None if not votes else int(np.sign(sum(votes)))


def releases(news, now):
    """High-impact events grouped by release time, released between REACT_MIN and LATEST_MIN minutes ago."""
    by_t = {}
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        t = datetime.fromisoformat(e["time"].replace("Z", "+00:00")).timestamp()
        by_t.setdefault(t, []).append(e)
    return [(t, ev) for t, ev in sorted(by_t.items()) if REACT_MIN * 60 <= now - t <= LATEST_MIN * 60], sorted(by_t)


def analyse(df, t0, evts, ict, levels, now, next_high):
    """Pure function of the candles: returns the card dict. df: 5m UTC candles, closed bars only."""
    T = pd.Timestamp(t0, unit="s", tz="UTC")
    pre = df[df.index < T]
    win = df[(df.index >= T) & (df.index < T + pd.Timedelta(minutes=REACT_MIN))]
    after = df[df.index >= T]
    if len(pre) < 20 or len(win) < REACT_MIN // 5:
        return None
    a_pre = float(atr(pre).iloc[-1])
    p0 = float(pre["Close"].iloc[-1])
    c_w = float(win["Close"].iloc[-1])
    move = c_w - p0
    up = move > 0
    sg = 1 if up else -1
    price = float(after["Close"].iloc[-1])
    hi_w, lo_w = float(win["High"].max()), float(win["Low"].min())
    two_way = (hi_w - p0) >= a_pre and (p0 - lo_w) >= a_pre
    card = {"title": " + ".join(e["title"] for e in evts), "t": t0, "p0": round(p0, 2), "move": round(move, 2),
            "atr": round(a_pre, 2), "price": round(price, 2), "dir": "bull" if up else "bear"}
    if abs(move) < a_pre:
        card.update(stage="no plan", why=f"Gold moved only {abs(move):.1f} points in {REACT_MIN} minutes (less than one normal 5m range): no clear reaction.")
        return card
    # the reaction leg, measured on everything since the release (the extreme can extend after 15 min)
    ext = float(after["High"].max()) if up else float(after["Low"].min())
    base = min(p0, lo_w) if up else max(p0, hi_w)
    size = abs(ext - base)
    lvl = lambda r: ext - sg * r * size
    zone = sorted([round(lvl(0.5), 2), round(lvl(0.618), 2)])
    entry = round(lvl(0.559), 2)
    inval = round(lvl(0.786), 2)
    stop = round(inval - sg * max(0.5, 0.3 * a_pre), 2)
    tp1 = round(ext, 2)
    beyond = sorted([p for n, p in levels if (p - ext) * sg > 0.3 * a_pre], key=lambda p: abs(p - ext))
    tp2 = round(beyond[0] if beyond else ext + sg * 0.5 * size, 2)
    rr = round(abs(tp1 - entry) / abs(entry - stop), 2)
    sur = surprise(evts)
    h1 = ((ict.get("timeframes") or {}).get("1H") or {}).get("bias")
    held = (price - (base + ext) / 2) * sg > 0
    fs = [("Data surprise agrees", sur == sg, "no actual figure in the feed" if sur is None else "in line" if sur == 0 else
           ("surprise favored gold" if sur > 0 else "surprise favored the dollar")),
          ("Strong impulse", abs(move) >= 2 * a_pre, f"{abs(move):.1f} pts = {abs(move) / a_pre:.1f}x the normal 5m range"),
          ("One-way reaction", not two_way, "both sides were run first (whipsaw)" if two_way else "clean one-way move"),
          ("1H trend agrees", h1 == card["dir"], f"1H structure is {h1 or 'unclear'}"),
          ("Move is holding", held, "price still holds the upper half of the move" if held and up else
           "price still holds the lower half of the move" if held else "more than half the move is already given back")]
    n_ok = sum(1 for _, g, _ in fs if g)
    valid_until = min(t0 + PLAN_VALID_MIN * 60, (next_high - 300) if next_high else 1e12)
    card.update(zone=zone, entry=entry, stop=stop, inval=inval, tp1=tp1, tp2=tp2, rr=rr, factors=fs, n_ok=n_ok,
                valid_until=valid_until, next_high=next_high)
    if (price - inval) * sg < 0:
        card.update(stage="no plan", why="Price already closed beyond the 78.6% retracement: the reaction failed.")
    elif n_ok < MIN_FACTORS:
        card.update(stage="no plan", why=f"Only {n_ok} of {len(fs)} factors: the reaction is not clean enough to plan a trade.")
    elif rr < 1.2:
        card.update(stage="no plan", why=f"Reward to TP1 is only 1:{rr}: not worth the risk.")
    elif now >= valid_until:
        card.update(stage="no plan", why="The plan window has already closed.")
    else:
        card["stage"] = "plan live"
    return card


def render(c, ai):
    head = f"📰 <b>XAU.KH · After the news</b>\n<b>{esc(c['title'])}</b> · released {local(c['t'])}"
    react = f"Gold {'+' if c['move'] > 0 else ''}{c['move']:.1f} pts in {REACT_MIN} min (from {fmt(c['p0'])}) · now {fmt(c['price'])}"
    if c["stage"] != "plan live":
        lines = [head, react, "Lean: <b>no plan</b>. " + esc(c["why"])]
        if c.get("factors"):
            lines.append(f"Factors {c['n_ok']}/{len(c['factors'])}: " + " ".join(f"{'✅' if g else '▫️'}{esc(a)}" for a, g, _ in c["factors"]))
        lines.append("<i>Volatility stays high after releases. Waiting is a position.</i>")
        return "\n".join(lines)
    bull = c["dir"] == "bull"
    lines = [head, react,
             f"{'🟢' if bull else '🔴'} <b>Lean: {'BUY' if bull else 'SELL'} the pullback</b> · factors {c['n_ok']}/{len(c['factors'])}",
             f"Entry zone <code>{fmt(c['zone'][0])} – {fmt(c['zone'][1])}</code> (limit {fmt(c['entry'])})"
             + (" · <b>price is in the zone now</b>" if (c["price"] - c["zone"][1 if bull else 0]) * (1 if bull else -1) <= 0 else ""),
             f"Stop <code>{fmt(c['stop'])}</code> · Invalidation: 5m close {'below' if bull else 'above'} {fmt(c['inval'])}",
             f"TP1 <code>{fmt(c['tp1'])}</code> (1:{c['rr']}) · TP2 <code>{fmt(c['tp2'])}</code>",
             f"Expires {local(c['valid_until'])}" + (" (before the next high-impact event)" if c.get("next_high") and c["valid_until"] < c["t"] + PLAN_VALID_MIN * 60 else ""),
             " ".join(f"{'✅' if g else '▫️'}{esc(a)}" for a, g, _ in c["factors"]),
             "<b>Why:</b> " + esc(ai or "; ".join(f"{a}: {d}" for a, g, d in c["factors"]) + "."),
             "<i>Experimental post-news model, not yet backtested. Idea only, not financial advice. Result posted as a reply.</i>"]
    return "\n".join(lines)


def main():
    news, ict, lv, state = jl("news.json", {}), jl("ict.json", {}), jl("levels.json", {}), jl("postnews_state.json", {})
    now = time.time()
    todo, all_t = releases(news, now)
    todo = [(t, ev) for t, ev in todo if str(int(t)) not in state]
    if not todo:
        print("postnews: no fresh release to judge"); return
    df = load("5m", "5d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = df.tz_convert("UTC").iloc[:-1]
    levels = [(x["name"], x["price"]) for x in lv.get("ladder", []) if x["name"] in
              ("Prev day high", "Prev day low", "Asia high", "Asia low", "London high", "London low", "Prev VAH", "Prev VAL", "Prev POC")]
    for t0, evts in todo:
        nxt = next((t for t in all_t if t > t0 + 60), None)
        c = analyse(df, t0, evts, ict, levels, now, nxt if nxt and nxt - t0 < PLAN_VALID_MIN * 60 else None)
        if c is None:
            print("postnews: not enough candles yet for", evts[0]["title"]); continue
        ai = None
        if c["stage"] == "plan live":
            ai = explain({k: v for k, v in c.items() if k not in ("t", "valid_until", "next_high")} |
                         {"factors": [{"name": a, "ok": g, "detail": d} for a, g, d in c["factors"]]})
        mid = send(render(c, ai), "After the news")
        state[str(int(t0))] = {"stage": c["stage"], "msg_id": mid if isinstance(mid, int) else None}
        if c["stage"] == "plan live" and mid:
            log_alert({"id": f"news|{int(t0)}", "kind": "post-news", "dir": c["dir"], "entry": c["entry"], "stop": c["stop"],
                       "target": c["tp1"], "tp2": c["tp2"], "rr": c["rr"], "zone": c["zone"], "factors": c["n_ok"], "created": now,
                       "valid_until": c["valid_until"], "price_at_alert": c["price"], "msg_id": mid if isinstance(mid, int) else None,
                       "status": "pending", "event": c["title"]})
        print("postnews:", c["title"], c["stage"])
    json.dump(state, open("postnews_state.json", "w"), indent=1)


if __name__ == "__main__":
    main()
