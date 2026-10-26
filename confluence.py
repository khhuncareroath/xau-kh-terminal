"""Confluence engine: merges ICT levels (prior day, sessions, midnight open), VWAP and
volume-profile levels into scored zones, detects liquidity sweeps and value-area
acceptance, and writes the reasons in plain language.

Run AFTER levels.py:   python confluence.py   ->  confluence.json

Optional: create anchors.json to add your own fixed-range profiles (like the ones you
draw on TradingView). Times are New York time:
  {"anchors": [{"name": "Range A", "start": "2026-10-20 18:00"}]}

These are analysis ideas, not signals. Entries still need your own confirmation.
"""
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from engine import atr, load
from levels import NY, profile, to_ny, trade_dates

# (text in level name, source family, weight). First match wins, so order matters.
FAMILY = [
    ("Prev day high", "ICT liquidity", 3), ("Prev day low", "ICT liquidity", 3),
    ("Prev day close", "ICT reference", 1), ("Midnight open", "ICT reference", 1.5),
    ("VWAP +2s", "VWAP", 1), ("VWAP -2s", "VWAP", 1),
    ("VWAP +1s", "VWAP", 1.5), ("VWAP -1s", "VWAP", 1.5), ("VWAP", "VWAP", 2),
    ("POC", "Volume profile", 3), ("VAH", "Volume profile", 3), ("VAL", "Volume profile", 3),
    ("HVN", "Volume profile", 1.5),
    (" high", "ICT session liquidity", 2), (" low", "ICT session liquidity", 2),
]


def classify(name):
    for key, fam, w in FAMILY:
        if key in name:
            return fam, w * (0.7 if name.startswith("Today") else 1.0)
    return None


def cluster(items, tol):
    items = sorted(items, key=lambda x: x["price"])
    groups, cur = [], []
    for it in items:
        if cur and it["price"] - cur[0]["price"] > tol:
            groups.append(cur)
            cur = []
        cur.append(it)
    if cur:
        groups.append(cur)
    return groups


def find_sweeps(df, levels, sessions, lookback=72):
    """A sweep = price pushed through a liquidity level recently but closed back on the other side."""
    eligible = {"Prev day high", "Prev day low"}
    for s, r in sessions.items():
        if r["status"] == "complete":
            eligible |= {f"{s} high", f"{s} low"}
    recent, close, out = df.tail(lookback), float(df["Close"].iloc[-1]), []
    for name in eligible:
        p = levels.get(name)
        if p is None:
            continue
        if name.endswith("high") and recent["High"].max() > p + 0.3 and close < p:
            out.append({"level": name, "price": p, "type": "swept above, closed back below",
                        "meaning": "buy-side liquidity was taken; bearish if structure shifts down"})
        if name.endswith("low") and recent["Low"].min() < p - 0.3 and close > p:
            out.append({"level": name, "price": p, "type": "swept below, closed back above",
                        "meaning": "sell-side liquidity was taken; bullish if structure shifts up"})
    return out


def profile_state(today_df, prof, price):
    if prof is None or today_df is None or len(today_df) < 6:
        return None
    vah, val = prof["vah"], prof["val"]
    open_px = float(today_df["Open"].iloc[0])
    c30 = today_df["Close"].resample("30min").last().dropna()
    state = {"open": round(open_px, 2), "open_type":
             "above yesterday's value" if open_px > vah else "below yesterday's value" if open_px < val else "inside yesterday's value"}
    # "80% rule": a popular profile idea (not verified for gold; we will backtest it)
    if open_px > vah or open_px < val:
        inside = [(val <= c <= vah) for c in c30]
        for i in range(len(inside) - 1):
            if inside[i] and inside[i + 1]:
                target = val if open_px > vah else vah
                state["rule_80"] = (f"Opened outside value, then two 30m closes back inside: the 80% rule says a move "
                                    f"toward {target} is common. Treat as an idea to test, not a promise.")
                break
    if len(c30) >= 2:
        a, b = c30.iloc[-2], c30.iloc[-1]
        if a > vah and b > vah:
            state["acceptance"] = f"Two 30m closes above VAH {vah}: buyers accepted higher prices."
        elif a < val and b < val:
            state["acceptance"] = f"Two 30m closes below VAL {val}: sellers accepted lower prices."
    return state


def zone_reasons(z, prev, swept):
    names = [m["name"] for m in z["sources"]]
    r = [f"{len(names)} level(s) agree across {len(z['families'])} source type(s): "
         + ", ".join(f"{m['name']} {m['price']}" for m in z["sources"])]
    if z["location"]:
        r.append(f"Zone sits in the {z['location']} half of yesterday's range.")
    if any("POC" in n for n in names):
        r.append("POC = the price with the most traded volume; price is often pulled back to it.")
    if any(("VAH" in n or "VAL" in n) for n in names):
        r.append("Value-area edge: acceptance beyond it can start a trend, rejection often sends price back through value.")
    if any("2s" in n for n in names):
        r.append("VWAP 2-sigma band: statistically stretched, so mean reversion toward VWAP is common but not guaranteed.")
    if any(" OB" in n for n in names):
        r.append("Order block: the last opposite candle before a move that broke structure; price often reacts when it returns.")
    if any("FVG" in n for n in names):
        r.append("Fair value gap: a spot price moved through too fast; it often returns to rebalance before continuing.")
    hit = [s for s in swept if s["level"] in names]
    if hit:
        r.append(f"{hit[0]['level']} was just swept ({hit[0]['type']}), which strengthens this zone.")
    return r


def main():
    lv = json.load(open("levels.json"))
    price = lv["price"]
    df = to_ny(load("5m", "30d"))
    df = df[df["Volume"] >= 0]
    dates = trade_dates(df.index)
    days = sorted(set(dates))
    today_df = df[dates == days[-1]]
    atr5 = float(atr(df).iloc[-1])
    levels = {x["name"]: x["price"] for x in lv["ladder"]}

    if os.path.exists("anchors.json"):
        for a in json.load(open("anchors.json")).get("anchors", []):
            sub = df[df.index >= pd.Timestamp(a["start"], tz=NY)]
            p = profile(sub) if len(sub) else None
            if p:
                levels.update({f"{a['name']} POC": p["poc"], f"{a['name']} VAH": p["vah"], f"{a['name']} VAL": p["val"]})

    items = []
    for name, p in levels.items():
        c = classify(name)
        if c:
            items.append({"name": name, "price": p, "family": c[0], "w": c[1]})

    if os.path.exists("ict.json"):   # order blocks and fair value gaps from ict.py become zone sources
        ict = json.load(open("ict.json"))
        for tf, w in (("5m", 1.5), ("15m", 2), ("1H", 3)):
            t = ict["timeframes"].get(tf, {})
            for z in t.get("order_blocks", []):
                if z["status"] != "invalid":
                    items.append({"name": f"{tf} {z['dir']} OB", "price": round((z["lo"] + z["hi"]) / 2, 2), "family": "ICT PD array", "w": w + 0.5})
            for z in t.get("fvgs", []):
                items.append({"name": f"{tf} {z['dir']} FVG", "price": round((z["lo"] + z["hi"]) / 2, 2), "family": "ICT PD array", "w": w})

    prev, mid50 = lv.get("prev_day"), None
    if prev:
        mid50 = (prev["high"] + prev["low"]) / 2
    sweeps = find_sweeps(df, levels, lv["sessions"])
    tol = max(2.5, 2 * atr5)

    zones = []
    for g in cluster(items, tol):
        if len(g) < 2 and max(m["w"] for m in g) < 3:
            continue
        lo, hi = min(m["price"] for m in g), max(m["price"] for m in g)
        fams = sorted({m["family"] for m in g})
        score = sum(sum(sorted((m["w"] for m in g if m["family"] == fm), reverse=True)[:2]) for fm in fams) + 2 * (len(fams) - 1)  # top 2 per source type, so crowded zones are not over-rated
        mid = (lo + hi) / 2
        if abs(mid - price) > 60:
            continue
        z = {"low": round(lo - 0.5, 2), "high": round(hi + 0.5, 2), "mid": round(mid, 2),
             "score": round(score, 1), "rating": "A" if score >= 12 else "B" if score >= 8 else "C",
             "families": fams, "sources": [{"name": m["name"], "price": m["price"]} for m in g],
             "role": "price inside zone" if lo - 0.5 <= price <= hi + 0.5 else "support" if mid < price else "resistance",
             "distance": round(mid - price, 2),
             "location": None if mid50 is None else ("premium" if mid > mid50 else "discount")}
        z["reasons"] = zone_reasons(z, prev, sweeps)
        zones.append(z)
    zones.sort(key=lambda z: -z["mid"])

    def target_for(side):
        pool = [z for z in zones if z["rating"] in ("A", "B") and (z["mid"] > price if side == "up" else z["mid"] < price)]
        pool.sort(key=lambda z: abs(z["mid"] - price))
        return pool[0] if pool else None

    playbooks = []
    for role, side in (("support", "up"), ("resistance", "down")):
        best = sorted([z for z in zones if z["role"] == role and z["rating"] in ("A", "B")],
                      key=lambda z: (-z["score"], abs(z["distance"])))[:2]
        for z in best:
            t = target_for(side)
            buf = round(max(1.0, atr5), 2)
            if role == "support":
                text = (f"IF price trades into {z['low']}-{z['high']} and rejects it (a sweep below that closes back above), "
                        f"look for longs toward {t['mid'] if t else 'the next zone'}. Idea is invalid on a 5m close below {round(z['low'] - buf, 2)}.")
            else:
                text = (f"IF price trades into {z['low']}-{z['high']} and rejects it (a sweep above that closes back below), "
                        f"look for shorts toward {t['mid'] if t else 'the next zone'}. Idea is invalid on a 5m close above {round(z['high'] + buf, 2)}.")
            playbooks.append({"zone": f"{z['low']}-{z['high']}", "rating": z["rating"], "text": text,
                              "note": "Confirm with your own ICT entry (structure shift, FVG). The setup tracker in ict.json shows the engine's own view."})

    prof_prev = lv.get("profile_prev_day")
    result = {
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "price": price, "atr_5m": round(atr5, 2), "zones": zones, "sweeps": sweeps,
        "profile_state": profile_state(today_df, prof_prev, price),
        "fast_move_zones": [{"price": p, "meaning": "low-volume node: price often moves through quickly"}
                            for p in (prof_prev or {}).get("lvn", [])],
        "playbooks": playbooks,
        "disclaimer": "Analysis ideas based on futures volume, not signals or advice.",
    }
    with open("confluence.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"{len(zones)} zones, {len(sweeps)} sweeps, {len(playbooks)} playbooks")
    for z in zones:
        print(f"  {z['rating']} {z['low']}-{z['high']} {z['role']} ({', '.join(m['name'] for m in z['sources'])})")


if __name__ == "__main__":
    main()
