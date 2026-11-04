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
ICON = {"win": "✅", "tp1": "✅", "loss": "❌", "expired": "⌛", "missed": "🏃", "timed out": "⏹"}
TRADED = ("win", "tp1", "loss", "timed out")
COST = 0.4   # $ per trade, same as research.COST (Exness standard spread is about $0.24)


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
        elif a["status"] == "filled" and a.get("tp1"):
            # scale-out: half at TP1 (stop moves to entry), rest to TP2 -- same rules as research._run_scaled
            part, hit1 = a.get("part", 0.5), a.get("hit1", False)
            r1, r2 = abs(a["tp1"] - a["fill"]) / risk, abs(a["target"] - a["fill"]) / risk
            st = a["fill"] if hit1 else a["stop"]
            banked = part * r1 if hit1 else 0.0
            left = 1 - part if hit1 else 1.0
            if (l <= st) if sg > 0 else (h >= st):
                px = st if hit1 else (min(st, o) if sg > 0 else max(st, o))
                a.update(status="tp1" if hit1 else "loss", closed=t, exit=px, R=round(banked + left * (px - a["fill"]) * sg / risk, 2))
                return
            if not hit1 and ((h >= a["tp1"]) if sg > 0 else (l <= a["tp1"])):
                a.update(hit1=True, tp1_at=t)
                hit1, banked, left = True, part * r1, 1 - part
            if hit1 and ((h >= a["target"]) if sg > 0 else (l <= a["target"])):
                a.update(status="win", closed=t, exit=a["target"], R=round(banked + left * r2, 2))
                return
            if t - a["filled_at"] >= a.get("max_hold_s", MAX_HOLD_S):
                a.update(status="timed out", closed=t, exit=c, R=round(banked + left * (c - a["fill"]) * sg / risk, 2))
                return
        elif a["status"] == "filled":
            if (l <= a["stop"]) if sg > 0 else (h >= a["stop"]):
                px = min(a["stop"], o) if sg > 0 else max(a["stop"], o)
                a.update(status="loss", closed=t, exit=px, R=round((px - a["fill"]) * sg / risk, 2))
                return
            if (h >= a["target"]) if sg > 0 else (l <= a["target"]):
                a.update(status="win", closed=t, exit=a["target"], R=round(a["rr"], 2))
                return
            if t - a["filled_at"] >= a.get("max_hold_s", MAX_HOLD_S):
                a.update(status="timed out", closed=t, exit=c, R=round((c - a["fill"]) * sg / risk, 2))
                return


def reply_text(a):
    t = _reply_text(a)
    return ("Watch idea result. If traded as planned: " + t) if a.get("kind") == "watch" else t


def _reply_text(a):
    s = a["status"]
    sg = 1 if a["dir"] == "bull" else -1
    pips = lambda px: f"{(px - a['entry']) * sg * 1:+,.1f} លេខ"
    if s == "win":
        return f"🏆 <b>TP{'2' if a.get('tp1') else ''} hit</b> {pips(a['target'])} · ដល់ TP"
    if s == "tp1":
        return f"✅ <b>Closed in profit</b>: TP1 {pips(a['tp1'])}, rest at entry · ឈ្នះ"
    if s == "loss":
        return f"❌ <b>SL hit</b> {pips(a['exit'])} · ប៉ះ SL"
    if s == "expired":
        return "⚪ <b>Expired</b>: price never reached the entry. No trade."
    if s == "missed":
        return "⚪ <b>Missed</b>: price left without the entry. No trade."
    hrs = round(a.get("max_hold_s", MAX_HOLD_S) / 3600)
    return f"⏱ <b>Closed after {hrs // 24} days</b> at {fmt(a['exit'])} ({pips(a['exit'])})" if hrs >= 48 else \
        f"⏱ <b>Closed after {hrs} h</b> at {fmt(a['exit'])} ({pips(a['exit'])})"


def summary(log):
    out = _summary([a for a in log if a.get("kind") != "late"])   # ⚠️ late-plan warnings: shown apart, not in the record
    for kind in ("setup", "watch", "post-news", "model", "plan", "late"):
        sub = [a for a in log if a.get("kind") == kind]
        if sub:
            out["by_kind"] = out.get("by_kind", {})
            out["by_kind"][kind] = {k: v for k, v in _summary(sub).items() if k not in ("recent", "note", "time")}
    return out


def _summary(log):
    done = [a for a in log if a["status"] in ICON]
    traded = [a for a in done if a["status"] in TRADED]
    R = [a["R"] for a in traded]
    return {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "alerts": len(log), "open": sum(a["status"] in ("pending", "filled") for a in log),
            "traded": len(traded), "wins": sum(a["R"] > 0 for a in traded), "losses": sum(a["R"] <= 0 for a in traded),
            "no_trade": sum(a["status"] in ("expired", "missed") for a in done),
            "win_rate_pct": round(100 * sum(r > 0 for r in R) / len(R)) if R else None,
            "total_R": round(sum(R), 2), "avg_R": round(sum(R) / len(R), 2) if R else None,
            "note": "Every alert ever sent is counted. R is after a $0.40 spread/commission per trade, like the backtest. Small samples mislead.",
            "recent": [{k: a.get(k) for k in ("kind", "dir", "entry", "stop", "target", "rr", "zone", "status", "R", "created", "closed", "event", "factors")}
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
            before, had_tp1 = a["status"], a.get("hit1", False)
            step(a, bars)
            if a["status"] in TRADED and "R_gross" not in a and a.get("R") is not None:   # same cost as the backtest
                risk = abs(a["entry"] - a["stop"]) or 1
                a["R_gross"], a["R"] = a["R"], round(a["R"] - COST / risk, 2)
            if a.get("hit1") and not had_tp1:
                send(f"🎯 <b>TP1 hit</b> {(a['tp1'] - a['fill']) * (1 if a['dir'] == 'bull' else -1) * 1:+,.1f} លេខ · close half, "
                     f"move SL to {fmt(a['fill'])}\nបិទពាក់កណ្ដាល ប្ដូរ SL មកចំណុចចូល", "TP1", reply_to=a.get("msg_id"))
            if a["status"] != before and a["status"] in ICON:
                send(reply_text(a), "Result", reply_to=a.get("msg_id"))
                print("resolved", a["id"], a["status"], a.get("R"))
    json.dump(log, open("alerts_log.json", "w"), indent=1)
    s = summary(log)
    json.dump(s, open("results.json", "w"), indent=2)
    print(f"track: {s['alerts']} alerts, {s['traded']} traded, win rate {s['win_rate_pct']}, total {s['total_R']}R")


if __name__ == "__main__":
    main()
