"""XAU.KH Strategy Radar: live updates of OUR strategy between signals, so the channel is never silent for long and
members can follow the setup as it builds (the trade signal itself still waits for the closed 4H candle).

The picture: 15m candles of the last ~20 hours, the 4H BUY / SELL lines, and the Day Meter on the right
(how much of a normal day gold has moved: 70% = 🖕 COMBO zone, 100% = 🖕🖕 PREMIUM zone), with a status:
  WAITING   price inside the lines, day quiet           -> no setup, follow the trend
  🖕 READY  day in the COMBO zone: a 4H close beyond a line would be a COMBO signal
  🖕🖕 READY day in the PREMIUM zone: a 4H close beyond a line would be a PREMIUM swing

Posted by session.py (radar_post) only at moments that matter:
  1. the day crosses 70% (COMBO zone) or 100% (PREMIUM zone): once each per day
  2. a 4H candle just closed and the channel has been quiet for 90+ minutes (08:00-24:00 local)
No new rules: it only shows where our tested strategy stands right now."""
import os
import time

import numpy as np
import pandas as pd

import research
from ict import resample

BG, PANEL, GRID, INK, MUT, UP, DN, GOLD, PREM = "#0A0A0C", "#111114", "#1C1C21", "#EDEDF2", "#7C7C85", "#2BD07B", "#FF4D4D", "#E3B04B", "#FFD60A"


def status(df, lines):
    price = float(df["Close"].iloc[-1])
    upper, lower = lines[0], lines[1]
    used = research.day_used(df, df.index[-1] + pd.Timedelta(minutes=5)) or 0.0
    zone = 2 if used >= research.PREMIUM_USED else 1 if used >= research.COMBO_USED else 0
    d4 = resample(df, "4H")
    hi30, lo30 = d4["High"].rolling(30).max().shift(1), d4["Low"].rolling(30).min().shift(1)
    tr = 0
    for k in range(len(d4) - 1):   # completed 4H candles only: last breakout direction = trend
        c = d4["Close"].iloc[k]
        tr = 1 if c > hi30.iloc[k] else -1 if c < lo30.iloc[k] else tr
    near = min(upper - price, price - lower)
    return {"price": price, "upper": upper, "lower": lower, "used": used, "zone": zone, "trend": tr,
            "to_buy": upper - price, "to_sell": price - lower, "near": near}


def finger_marks(df, d15):
    """(position in d15, 1 or 2) for the 15m candles where the trading day crossed 70% (🖕) / 100% (🖕🖕) of a normal
    day. Only real crossings on a candle in view (not a day that was already past the level when the chart starts);
    if one candle jumps past both levels, only 🖕🖕 is shown."""
    res = {}
    prev = research.day_used(df, d15.index[0]) or 0.0 if len(d15) else 0.0
    td = (d15.index - pd.Timedelta(hours=18)).date
    for i, t in enumerate(d15.index):
        if i and td[i] != td[i - 1]:
            prev = 0.0
        u = research.day_used(df, t + pd.Timedelta(minutes=15)) or 0.0   # day range at this candle's close
        for lvl, f in ((research.COMBO_USED, 1), (research.PREMIUM_USED, 2)):
            if prev < lvl <= u:
                res[i] = max(res.get(i, 0), f)
        prev = u
    return sorted(res.items())


def chart(df, lines, path, local=None, title="Strategy Radar"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    from proof import _finger
    plt.rcParams["font.family"] = "DejaVu Sans"
    st = status(df, lines)
    d = resample(df, "15m").tail(80)
    N = len(d)
    fig = plt.figure(figsize=(12, 6.8), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.05, 0.09, 0.70, 0.70]); mt = fig.add_axes([0.80, 0.09, 0.15, 0.70])
    for a_ in (ax, mt):
        a_.set_facecolor(PANEL); a_.set_xticks([])
        for sp in a_.spines.values(): sp.set_visible(False)
        a_.tick_params(colors=MUT, labelsize=8, length=0)
    ax.grid(axis="y", color=GRID, lw=0.6)
    for i, (o_, h_, l_, c_) in enumerate(d[["Open", "High", "Low", "Close"]].to_numpy()):
        col = "#2E9E68" if c_ >= o_ else "#C24545"
        ax.plot([i, i], [l_, h_], color=col, lw=0.8)
        ax.add_patch(Rectangle((i - 0.32, min(o_, c_)), 0.64, max(abs(c_ - o_), 0.05), color=col, lw=0))
    lo, hi = float(d["Low"].min()), float(d["High"].max())
    p = st["price"]; span = max(hi - lo, p * 0.004)
    # show a line only if it is reasonably close, otherwise an arrow with the distance
    ylo, yhi = lo - span * 0.12, hi + span * 0.12
    for y, col, word, dist in ((st["upper"], UP, "BUY above", st["to_buy"]), (st["lower"], DN, "SELL below", st["to_sell"])):
        if y - span * 0.6 < hi and y + span * 0.6 > lo:
            ylo, yhi = min(ylo, y - span * 0.05), max(yhi, y + span * 0.05)
    ax.set_ylim(ylo, yhi); ax.set_xlim(-1, N + 9)
    for y, col, word, dist in ((st["upper"], UP, "4H BUY above", st["to_buy"]), (st["lower"], DN, "4H SELL below", st["to_sell"])):
        if ylo < y < yhi:
            ax.plot([0, N + 8], [y, y], color=col, lw=1.3, ls=(0, (6, 3)))
            ax.text(1, y, f" {word} {y:,.2f}  ({f'{dist:,.1f} away' if dist > 0 else 'price is past it: waiting for the 4H close'})",
                    color=col, fontsize=8.5, fontweight="bold", va="center",
                    bbox=dict(boxstyle="round,pad=0.25", fc=PANEL, ec="none"))
        else:
            yy = yhi - span * 0.04 if col == UP else ylo + span * 0.04
            ax.text(N + 8, yy, f"{word} {y:,.2f} {'↑' if col == UP else '↓'} {dist:,.0f} away", color=col, fontsize=8,
                    ha="right", va="top" if col == UP else "bottom", fontweight="bold")
    # 🖕 on the 15m candle where the day crossed 70% (COMBO zone), 🖕🖕 where it crossed 100% (PREMIUM zone)
    for i, f in finger_marks(df, d):
        y = float(d["High"].iloc[i]) + span * 0.045
        for q in range(f):
            _finger(ax, i + (q - (f - 1) / 2) * 1.6, y, 0.12)
        ax.text(i, y + span * 0.05, "PREMIUM" if f == 2 else "COMBO", color=PREM if f == 2 else GOLD, fontsize=6.5,
                fontweight="bold", ha="center", va="bottom")
        yhi = max(yhi, y + span * 0.12); ax.set_ylim(ylo, yhi)
    ax.axhline(p, color=INK, lw=0.6, alpha=0.4)
    ax.annotate(f"{p:,.2f}", xy=(N - 1, p), xytext=(N + 1, p), color=BG, fontsize=8, fontweight="bold", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc=INK, ec="none"))
    tr = st["trend"]
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color=GOLD, alpha=0.035, fontsize=72, fontweight="bold",
            ha="center", va="center", zorder=0)
    # Day Meter
    mt.set_xlim(0, 1); mt.set_ylim(0, 1.5); mt.set_yticks([])
    for y0, y1, col, al in ((0, 0.7, MUT, 0.18), (0.7, 1.0, GOLD, 0.35), (1.0, 1.5, PREM, 0.40)):
        mt.add_patch(Rectangle((0.30, y0), 0.40, y1 - y0, color=col, alpha=al, lw=0))
    u = min(st["used"], 1.48)
    mt.add_patch(Rectangle((0.30, 0), 0.40, u, color=PREM if st["zone"] == 2 else GOLD if st["zone"] == 1 else INK, alpha=0.85, lw=0))
    mt.plot([0.22, 0.78], [u, u], color=INK, lw=1.5)
    mt.text(0.5, u + 0.03, f"{st['used'] * 100:.0f}%", color=INK, fontsize=12, fontweight="bold", ha="center", va="bottom")
    mt.text(0.82, 0.70, "70%", color=GOLD, fontsize=7, va="center"); mt.text(0.82, 1.0, "100%", color=PREM, fontsize=7, va="center")
    _finger(mt, 0.14, 0.85, 0.11)
    _finger(mt, 0.09, 1.25, 0.11); _finger(mt, 0.19, 1.25, 0.11)
    mt.text(0.5, -0.06, "DAY METER\nhow much of a normal\nday gold has moved", color=MUT, fontsize=7, ha="center", va="top",
            transform=mt.transData, linespacing=1.3)
    # header
    if st["zone"] == 2:
        head, col, nf = "PREMIUM ZONE · a 4H close beyond a line = PREMIUM SWING", PREM, 2
    elif st["zone"] == 1:
        head, col, nf = "COMBO ZONE · a 4H close beyond a line = COMBO signal", GOLD, 1
    else:
        head, col, nf = "WAITING · day still quiet, no setup yet", MUT, 0
    stamp = local(time.time()) if local else ""
    fig.text(0.05, 0.94, "XAU.KH", color=GOLD, fontsize=15, fontweight="bold")
    fig.text(0.14, 0.94, f"{title.upper()}  ·  15m  ·  {stamp}", color=INK, fontsize=13, fontweight="bold")
    fig.patches.append(FancyBboxPatch((0.05, 0.815), 0.70, 0.075, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, fc=PANEL, ec=col, lw=1.2))
    fig.text(0.065, 0.852, head, color=col, fontsize=10.5, fontweight="bold", va="center")
    trend_txt = "4H trend: UP (last breakout was a BUY)" if tr > 0 else "4H trend: DOWN (last breakout was a SELL)" if tr < 0 else "4H trend: none yet"
    fig.text(0.80, 0.852, trend_txt.split(" (")[0], color=UP if tr > 0 else DN if tr < 0 else MUT, fontsize=10, fontweight="bold", va="center")
    if nf:
        fa = fig.add_axes([0.66, 0.822, 0.08, 0.06]); fa.set_xlim(0, 3); fa.set_ylim(0, 1); fa.axis("off"); fa.set_zorder(5)
        for q in range(nf):
            _finger(fa, 2.5 - q * 0.9, 0.5, 0.13)
    fig.text(0.05, 0.03, "A live read of our tested strategy, not a signal. The signal comes only when a 4H candle CLOSES beyond a line.",
             color=MUT, fontsize=7.5)
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path, st


KM_TREND = {1: "ទំនោរឡើង", -1: "ទំនោរចុះ", 0: "មិនទាន់មានទំនោរ"}


def caption(st, why, next_close_local):
    tr = st["trend"]
    z = st["zone"]
    zone_line = ("🖕🖕 <b>PREMIUM zone</b>: a 4H close beyond a line now = PREMIUM SWING (77% in test)" if z == 2 else
                 "🖕 <b>COMBO zone</b>: a 4H close beyond a line now = COMBO signal (68% in test)" if z == 1 else
                 "◽ Day still quiet: a breakout now would be a Normal signal (half size)")
    side = ("BUY" if st["to_buy"] < st["to_sell"] else "SELL")
    dist = min(st["to_buy"], st["to_sell"])
    head = {"combo": "🖕 <b>COMBO ZONE OPEN</b>", "premium": "🖕🖕 <b>PREMIUM ZONE OPEN</b>", "4h": "📡 <b>STRATEGY RADAR</b>"}[why]
    lines = [f"{head} · Gold <b>{st['price']:,.2f}</b>",
             f"📏 Day Meter <b>{st['used'] * 100:.0f}%</b> of a normal day · {zone_line}",
             (f"🎯 Closest: <b>{side}</b> line {st['upper'] if side == 'BUY' else st['lower']:,.2f} · {dist:,.1f} away" if dist > 0 else
              f"🔥 Price is already {'above the BUY' if side == 'BUY' else 'below the SELL'} line "
              f"{st['upper'] if side == 'BUY' else st['lower']:,.2f}: if the 4H candle CLOSES there → ✅ {side} signal"),
             f"{'📈' if tr > 0 else '📉' if tr < 0 else '↔'} 4H trend {'UP' if tr > 0 else 'DOWN' if tr < 0 else 'none'} · {KM_TREND[tr]}",
             f"⏰ Next 4H close <b>{next_close_local}</b>",
             "<i>Follow along, don't enter early · តាមដាន កុំចូលមុនពេល</i>"]
    return "\n".join(lines)
