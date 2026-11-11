"""Daily pips report (🏆 Proof): every trade that closed in the trading day that just ended, wins AND losses.

Posted once, a few minutes after the New York close (17:00 NY), only if at least one trade closed that day.
Pips = gross result in price x 10 (1 pip = $0.10), so a half closed at TP1 + half at entry counts the TP1 half.
State: pips_state.json.  Run every cycle:  python pips_report.py
"""
import json
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tg import local, send, send_photo

NY = ZoneInfo("America/New_York")
STATE = "pips_state.json"
NAMES = {"splus": "S+ setup", "model": "4H breakout", "scalp": "Combo scalp", "plan": "Plan", "late": "Late plan", "post-news": "After news"}
RES = {"win": "TP2", "tp1": "TP1 + BE", "loss": "SL", "timed out": "Time exit"}


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def pips(a):
    risk = abs(a["entry"] - a["stop"])
    r = a.get("R_gross", a.get("R"))
    return round((r or 0) * risk * 10)


def trading_day(ts):
    """New York trading day (18:00-17:00) a unix time belongs to, as a date."""
    return (datetime.fromtimestamp(ts, NY) + timedelta(hours=6)).date()


def card(rows, total, day, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from signal_card import BG, CARD, INK, MUT, UP, DN, BLUE, _fonts
    plt.rcParams["font.family"] = _fonts()
    h = 4.2 + 0.42 * len(rows)
    fig = plt.figure(figsize=(7.2, h), dpi=150, facecolor=BG)
    Y = lambda inch: 1 - inch / h
    fig.text(0.06, Y(0.45), "XAU.KH", color=BLUE, fontsize=13, fontweight="bold", va="center")
    fig.text(0.94, Y(0.45), day, color=MUT, fontsize=10, va="center", ha="right")
    fig.text(0.06, Y(0.95), "DAILY PIPS REPORT · wins AND losses", color=MUT, fontsize=9.5, va="center")
    fig.text(0.06, Y(1.75), f"{total:+,} pips", color=UP if total >= 0 else DN, fontsize=40, fontweight="bold", va="center")
    w = sum(1 for r in rows if r[3] > 0)
    fig.text(0.06, Y(2.5), f"{len(rows)} trades · {w} won · {len(rows) - w} lost", color=INK, fontsize=11, va="center")
    fig.patches.append(FancyBboxPatch((0.04, Y(3.0 + 0.42 * len(rows))), 0.92, (0.42 * len(rows) + 0.3) / h,
                                      boxstyle="round,pad=0,rounding_size=0.02", transform=fig.transFigure, fc=CARD, ec="none"))
    for k, (side, name, res, p) in enumerate(rows):
        y = Y(3.05 + 0.42 * k)
        col = UP if side == "BUY" else DN
        fig.text(0.07, y, f" {side} ", color="white", fontsize=9, fontweight="bold", va="center",
                 bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"))
        fig.text(0.20, y, name, color=INK, fontsize=10, va="center")
        fig.text(0.62, y, res, color=MUT, fontsize=10, va="center")
        fig.text(0.93, y, f"{p:+,}", color=UP if p > 0 else DN if p < 0 else MUT, fontsize=11, fontweight="bold",
                 va="center", ha="right")
    fig.text(0.06, Y(h - 0.35), "Every closed trade is listed. 1 pip = $0.10 · not financial advice", color=MUT,
             fontsize=7.5, va="center")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


def main():
    now = time.time()
    ny = datetime.fromtimestamp(now, NY)
    if not (17 <= ny.hour < 18 and ny.minute >= 5) or ny.weekday() == 5:
        print("pips report: not the time"); return
    day = trading_day(now - 3600)          # the day that just closed
    st = jl(STATE, {})
    if st.get("day") == str(day):
        print("pips report: already sent"); return
    log = jl("alerts_log.json", [])
    done = [a for a in log if a.get("status") in RES and a.get("R") is not None and a.get("kind") in NAMES
            and trading_day(a.get("closed_at") or a.get("filled_at") or a["created"]) == day]
    st = {"day": str(day), "t": now}
    if not done:
        json.dump(st, open(STATE, "w")); print("pips report: no closed trades today"); return
    rows = [("BUY" if a["dir"] == "bull" else "SELL", NAMES[a["kind"]], RES[a["status"]], pips(a)) for a in done]
    total = sum(r[3] for r in rows)
    text = "\n".join([f"📊 <b>XAU.KH DAILY PIPS REPORT</b> · {day:%a %d %b}", "",
                      f"{'🔥' if total > 0 else '🧊'} Total: <b>{total:+,} pips</b> · {len(rows)} trades", ""]
                     + [f"{'✅' if p > 0 else '❌' if p < 0 else '⚪'} {s} · {n} ({r}): <b>{p:+,} pips</b>" for s, n, r, p in rows]
                     + ["", "<i>Every trade is listed, wins and losses · លទ្ធផលពិតទាំងអស់</i>"])
    try:
        mid = send_photo(card(rows, total, f"{day:%a %d %b %Y}", "pips_report.png"), text[:1024], "Daily pips proof")
    except Exception as e:
        print("pips card failed:", e)
        mid = None
    if not mid:
        mid = send(text, "Daily pips proof")
    if mid:
        json.dump(st, open(STATE, "w"))
        print("pips report sent", total)


if __name__ == "__main__":
    main()
