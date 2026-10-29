"""Track record: grades every idea that went out (alerts_log.json) against real candles, replies to the original
Telegram message with the result, and writes results.json, the public scorecard for the site.

Rules (same as backtest.py, so live and backtest numbers are comparable):
  pending  -> filled when price touches the entry before "valid until"
  pending  -> missed when the target is reached before the entry fills (no trade, not a win)
  pending  -> expired when the order window ends unfilled (no trade)
  filled   -> win at target, loss at stop (stop first if one candle touches both), or closed after 12h
R is gross, before spread and commission. Run every cycle after ict.py:  python track.py
"""
import json
import time
from datetime import datetime, timezone

from engine import load
from tg import fmt, send

MAX_HOLD_S = 12 * 3600
ICON = {"win": "✅", "loss": "❌", "expired": "⌛", "missed": "🏃", "timed out": "⏹"}


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def step(a, bars):
    """Moves one alert forward through new closed candles. bars: list of (t, o, h, l, c)."""
    sg = 1 if a["dir"] == "bull" else -1
    risk = abs(a["entry"] - a["stop"])
    for t, o, h, l, c in bars:
        if t < a.get("seen_to", a["created"]):
            continue
        a["seen_to"] = t + 300
        if a["status"] == "pending":
            if t >= a["valid_until"]:
                a.update(status="expired", closed=t, R=0.0)
                return
            touch = l <= a["entry"] if sg > 0 else h >= a["entry"]
            if touch:
                a.update(status="filled", filled_at=t, fill=a["entry"])
                if (l <= a["stop"]) if sg > 0 else (h >= a["stop"]):
                    a.update(status="loss", closed=t, exit=a["stop"], R=-1.0)
                    return
                continue
            if (h >= a["target"]) if sg > 0 else (l <= a["target"]):
                a.update(status="missed", closed=t, R=0.0)
                return
        elif a["status"] == "filled":
            if (l <= a["stop"]) if sg > 0 else (h >= a["stop"]):
                px = min(a["stop"], o) if sg > 0 else max(a["stop"], o)
                a.update(status="loss", closed=t, exit=px, R=round((px - a["fill"]) * sg / risk, 2))
                return
            if (h >= a["target"]) if sg > 0 else (l <= a["target"]):
                a.update(status="win", closed=t, exit=a["target"], R=round(a["rr"], 2))
                return
            if t - a["filled_at"] >= MAX_HOLD_S:
                a.update(status="timed out", closed=t, exit=c, R=round((c - a["fill"]) * sg / risk, 2))
                return


def reply_text(a):
    s = a["status"]
    if s == "win":
        return f"{ICON[s]} <b>Target hit</b> at {fmt(a['target'])}: +{a['R']}R"
    if s == "loss":
        return f"{ICON[s]} <b>Stopped</b> at {fmt(a['exit'])}: {a['R']}R"
    if s == "expired":
        return f"{ICON[s]} <b>Expired</b>: price never came back to {fmt(a['entry'])}. No trade."
    if s == "missed":
        return f"{ICON[s]} <b>No fill</b>: price reached the target without touching the entry. No trade, not counted as a win."
    return f"{ICON[s]} <b>Closed after 12h</b> at {fmt(a['exit'])}: {a['R']:+}R"


def summary(log):
    done = [a for a in log if a["status"] in ICON]
    traded = [a for a in done if a["status"] in ("win", "loss", "timed out")]
    R = [a["R"] for a in traded]
    return {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "alerts": len(log), "open": sum(a["status"] in ("pending", "filled") for a in log),
            "traded": len(traded), "wins": sum(a["status"] == "win" for a in traded), "losses": sum(a["status"] == "loss" for a in traded),
            "no_trade": sum(a["status"] in ("expired", "missed") for a in done),
            "win_rate_pct": round(100 * sum(r > 0 for r in R) / len(R)) if R else None,
            "total_R": round(sum(R), 2), "avg_R": round(sum(R) / len(R), 2) if R else None,
            "note": "Every alert ever sent is counted. R is before spread and commission. Small samples mislead.",
            "recent": [{k: a.get(k) for k in ("kind", "dir", "entry", "stop", "target", "rr", "status", "R", "created", "closed")}
                       for a in log[-30:]][::-1]}


def main():
    log = jl("alerts_log.json", [])
    live = [a for a in log if a["status"] in ("pending", "filled")]
    if live:
        df = load("5m", "5d")
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        bars = [(int(t.timestamp()), float(r.Open), float(r.High), float(r.Low), float(r.Close))
                for t, r in zip(df.index[:-1], df.iloc[:-1].itertuples())]   # last candle is still forming
        for a in live:
            before = a["status"]
            step(a, bars)
            if a["status"] != before and a["status"] in ICON:
                send(reply_text(a), "Result", reply_to=a.get("msg_id"))
                print("resolved", a["id"], a["status"], a.get("R"))
    json.dump(log, open("alerts_log.json", "w"), indent=1)
    s = summary(log)
    json.dump(s, open("results.json", "w"), indent=2)
    print(f"track: {s['alerts']} alerts, {s['traded']} traded, win rate {s['win_rate_pct']}, total {s['total_R']}R")


if __name__ == "__main__":
    main()
