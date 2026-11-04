"""XAU.KH Signal Proof: one picture with every intraday signal of the last ~2 weeks, wins AND losses.

The signals are found by running the exact live rules (research.py, the same code the backtest and live_models.py
use, with the 15-minute alert delay and the $0.40 cost) on the recent candles. Each signal gets an XAU.KH pin on the
chart (a flag pin) and its result as gold bars on the strip below. A signal that was also really sent to the channel is
marked LIVE. This is our own design (flag pins + gold-bar strip), not a copy of any indicator.

Used by session.py: the Friday weekly proof and one quiet-hours check-in a day. Run alone to make proof.png."""
import time

import numpy as np
import pandas as pd

import research
from ict import resample

TIERS = {   # model: (short name, tier, ring colour)
    "trend_premium": ("Premium Swing", "PREMIUM", "#FFD60A"),
    "trend_intraday": ("4H Breakout", "TESTED", "#E3B04B"),
    "vp_shape": ("Volume Plan", "PLAN", "#5AC8FA"),
    "range_extreme": ("Day Range Snap", "EXPERIMENTAL", "#BF5AF2"),
}
TIER_KM = {"TESTED": "បានសាកល្បង", "PLAN": "ផែនការ", "EXPERIMENTAL": "សាកល្បង"}


def replay(df):
    """Every trade of the three intraday models on df: entry/exit index, side, stop, target(s), R, status."""
    trades = []
    real_t, real_s = research._run_trade, research._run_scaled
    cur = {}

    def rec_t(o, h, l, c, j0, j_end, sg, stop, tgt):
        r, j = real_t(o, h, l, c, j0, j_end, sg, stop, tgt)
        if r is not None:
            hit = (h[j] >= tgt) if sg > 0 else (l[j] <= tgt)
            stp = (l[j] <= stop) if sg > 0 else (h[j] >= stop)
            st = "loss" if stp else "win" if hit else ("open" if j >= len(o) - 1 and j_end >= len(o) - 1 else "time")
            trades.append({"model": cur["m"], "j0": j0, "j": j, "sg": sg, "entry": float(o[j0]), "stop": float(stop),
                           "tgt": float(tgt), "R": float(r), "status": st})
        return r, j

    def rec_s(o, h, l, c, j0, j_end, sg, stop, tp1_r, tp2_r, part=0.5):
        r, j, hit1 = real_s(o, h, l, c, j0, j_end, sg, stop, tp1_r, tp2_r, part)
        if r is not None:
            en = float(o[j0]); risk = abs(en - stop); tp2 = en + sg * tp2_r * risk
            full = (h[j] >= tp2) if sg > 0 else (l[j] <= tp2)
            stp = not hit1 and ((l[j] <= stop) if sg > 0 else (h[j] >= stop))
            st = ("win" if full else "loss" if stp else "open" if j >= len(o) - 1 and j_end >= len(o) - 1
                  else "tp1" if hit1 else "time")
            trades.append({"model": cur["m"], "j0": j0, "j": j, "sg": sg, "entry": en, "stop": float(stop),
                           "tgt": tp2, "tp1": en + sg * tp1_r * risk, "R": float(r), "status": st})
        return r, j, hit1

    research._run_trade, research._run_scaled = rec_t, rec_s
    try:
        for m in TIERS:
            cur["m"] = m
            before = len(trades)
            try:
                res = getattr(research, m)(df)
            except Exception as e:
                print("proof replay", m, "failed:", e)
                continue
            keep = {x[0] for x in res}   # filtered models (premium) record every parent trade: keep only the returned ones
            trades[before:] = [t for t in trades[before:] if df.index[t["j0"]] in keep]
    finally:
        research._run_trade, research._run_scaled = real_t, real_s
    prem = {(t["j0"], t["sg"]) for t in trades if t["model"] == "trend_premium"}
    trades = [t for t in trades if not (t["model"] == "trend_intraday" and (t["j0"], t["sg"]) in prem)]   # live sends one
    return sorted(trades, key=lambda t: t["j0"])


def _live_match(t, df, log):
    t0 = df.index[t["j0"]].timestamp()
    for a in log or []:
        if a.get("model") == t["model"] and abs(a.get("created", 0) - t0) < 40 * 60 and \
                (a.get("dir") == "bull") == (t["sg"] > 0):
            return True
    return False


_EMOJI = {}


def _emoji(ax, x, y, zoom, name="finger"):
    """Draws an XAU.KH mark from assets/<name>.png (Noto Color Emoji, OFL licence) at data point (x, y):
    finger = 🖕 COMBO / 🖕🖕 PREMIUM, angry = 🤬 smaller tested setup you can trade yourself (small size)."""
    import os
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    try:
        if name not in _EMOJI:
            import matplotlib.image as mpimg
            _EMOJI[name] = mpimg.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", f"{name}.png"))
        ax.add_artist(AnnotationBbox(OffsetImage(_EMOJI[name], zoom=zoom), (x, y), frameon=False, zorder=8))
    except Exception as e:
        print("emoji mark failed:", e)


def _finger(ax, x, y, zoom):
    _emoji(ax, x, y, zoom, "finger")


def _ingot(ax, x, y0, h, w, fc, ec, alpha=1.0, z=5):
    """A gold bar (trapezoid ingot): XAU.KH's result token. h > 0 grows up from y0, h < 0 hangs below."""
    from matplotlib.patches import Polygon
    top = y0 + h
    inset = w * 0.22
    pts = [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2 - inset, top), (x - w / 2 + inset, top)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.0, alpha=alpha, zorder=z, joinstyle="round"))
    # shine line on the top face
    ax.plot([x - w / 2 + inset * 1.3, x + w / 2 - inset * 1.3], [top - h * 0.18] * 2, color="#FFFFFF", alpha=0.35 * alpha, lw=0.8, zorder=z + 1)


def proof_chart(df, path="proof.png", days=10, bt=None, log=None, local=None):
    """Draws the XAU.KH 'Gold Vault' proof picture: flag pins on the chart, every result stacked as gold bars below
    (1 bar = 0.5R won; a red bar = a loss). Returns (path, list of trades shown)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD = "#0A0A0C", "#111114", "#1C1C21", "#EDEDF2", "#7C7C85", "#2BD07B", "#FF4D4D", "#E3B04B"
    trades = replay(df)
    start = df.index[-1] - pd.Timedelta(days=days)
    shown = [t for t in trades if df.index[t["j0"]] >= start]
    for t in shown:
        t["live"] = _live_match(t, df, log)
        t["combo"] = False
        if t["model"] == "trend_intraday":
            try:
                t["combo"] = (research.day_used(df, df.index[t["j0"]]) or 0) >= research.COMBO_USED
            except Exception:
                pass
    d1 = resample(df[df.index >= start], "1H")
    N = len(d1)
    pos = lambda j: int(np.clip(d1.index.searchsorted(df.index[j], side="right") - 1, 0, N - 1))
    fig = plt.figure(figsize=(13, 8.0), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.05, 0.31, 0.92, 0.47]); st_ax = fig.add_axes([0.05, 0.075, 0.92, 0.21], sharex=ax)
    for a_ in (ax, st_ax):
        a_.set_facecolor(PANEL); a_.set_xticks([])
        for sp in a_.spines.values(): sp.set_visible(False)
        a_.tick_params(colors=MUT, labelsize=8, length=0)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_xlim(-1, N + 1)
    for i, (o_, h_, l_, c_) in enumerate(d1[["Open", "High", "Low", "Close"]].to_numpy()):
        col = "#36614D" if c_ >= o_ else "#6E3838"
        ax.plot([i, i], [l_, h_], color=col, lw=0.7)
        ax.add_patch(Rectangle((i - 0.32, min(o_, c_)), 0.64, max(abs(c_ - o_), 0.05), color=col, lw=0))
    lo, hi = float(d1["Low"].min()), float(d1["High"].max()); rng = hi - lo
    ax.set_ylim(lo - rng * 0.12, hi + rng * 0.14)
    tday = (d1.index - pd.Timedelta(hours=18)).date
    last_lab = -99
    for k in range(1, N):
        if tday[k] != tday[k - 1]:
            for a_ in (ax, st_ax):
                a_.axvline(k - 0.5, color=GRID, lw=0.8)
            if k - last_lab >= 8:
                st_ax.text(k, -1.75, (pd.Timestamp(tday[k]) + pd.Timedelta(days=1)).strftime("%a %d"), color=MUT,
                           fontsize=7, ha="left", va="top")
                last_lab = k
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color=GOLD, alpha=0.035, fontsize=84, fontweight="bold",
            ha="center", va="center", zorder=0)
    # flag pins: a pole from the entry and a pennant in the tier colour with B / S
    for t in shown:
        x0, x1 = pos(t["j0"]), pos(t["j"])
        name, tier, ring = TIERS[t["model"]]
        res_col = INK if t["status"] == "open" else UP if t["R"] > 0 else DN
        ex = float(df["Close"].iloc[t["j"]]) if t["status"] in ("time", "open") else \
            t["tgt"] if t["status"] == "win" else t["entry"] if t["status"] == "tp1" else t["stop"]
        ax.plot([x0, max(x1, x0 + 0.6)], [t["entry"], ex], color=res_col, lw=1.8, alpha=0.95, zorder=4, solid_capstyle="round")
        ax.scatter([max(x1, x0 + 0.6)], [ex], s=14, color=res_col, zorder=5)
        ax.plot([x0 - 0.9, x0 + 0.9], [t["stop"], t["stop"]], color=DN, lw=0.9, alpha=0.55, zorder=3)
        sg = t["sg"]; pole = rng * 0.11
        y_top = t["entry"] - sg * pole
        ax.plot([x0, x0], [t["entry"], y_top], color=ring, lw=1.1, zorder=5)
        fh = rng * 0.045; fw = 3.2
        yb = y_top if sg > 0 else y_top - fh      # pennant hangs off the far end of the pole
        ax.add_patch(Polygon([(x0, yb), (x0, yb + fh), (x0 + fw, yb + fh / 2)], closed=True, fc=ring, ec="none", zorder=6))
        ax.text(x0 + 1.0, yb + fh / 2, "B" if sg > 0 else "S", color=BG, fontsize=6.5, fontweight="bold", ha="center",
                va="center", zorder=7)
        if t["model"] in ("vp_shape", "range_extreme"):   # 🤬 = smaller tested setup (plan / experimental)
            _emoji(ax, x0 + 4.6, yb + fh / 2, 0.14, "angry")
        n_f = 2 if t["model"] == "trend_premium" else 1 if t.get("combo") else 0
        if n_f:   # the XAU.KH mark: one finger = COMBO, two = PREMIUM
            for q in range(n_f):
                _finger(ax, x0 + 4.6 + q * 2.6, yb + fh / 2, 0.15)
        tags = (["PREMIUM"] if n_f == 2 else ["COMBO"] if n_f == 1 else []) + (["LIVE"] if t.get("live") else [])
        if tags:
            ax.text(x0, yb - rng * 0.012 if sg > 0 else yb + fh + rng * 0.012, " · ".join(tags), color=GOLD, fontsize=6.3,
                    fontweight="bold", ha="left", va="top" if sg > 0 else "bottom", zorder=7)
    # GOLD BAR STRIP: each win stacks gold bars (1 bar = 0.5R), a loss hangs one red bar per 0.5R lost
    st_ax.set_ylim(-1.9, 4.4); st_ax.axhline(0, color=GOLD, lw=0.6, alpha=0.35)
    st_ax.text(0, 4.25, "GOLD BAR STRIP · 1 bar = 0.5R · gold = won · red = lost · every result, nothing hidden",
               color=MUT, fontsize=7, va="top")
    unit = 0.34
    for t in shown:
        x = pos(t["j0"]); r = t["R"]
        if t["status"] == "open":
            _ingot(st_ax, x, 0.05, unit * 0.9, 2.2, "none", INK, alpha=0.8)
            st_ax.text(x, unit + 0.15, "open", color=INK, fontsize=6.5, ha="center", va="bottom", fontweight="bold")
            continue
        k = max(1, int(round(abs(r) / 0.5)))
        for q in range(min(k, 6)):
            if r > 0:
                _ingot(st_ax, x, 0.05 + q * (unit + 0.06), unit, 3.0, GOLD, "#8A6A22")
            else:
                _ingot(st_ax, x, -0.05 - q * (unit + 0.06), -unit, 3.0, "#B3393B", "#5A1C1D")
        top = 0.05 + min(k, 6) * (unit + 0.06)
        st_ax.text(x, top + 0.05 if r > 0 else -top - 0.05, f"{r:+.1f}R", color=GOLD if r > 0 else DN, fontsize=7,
                   ha="center", va="bottom" if r > 0 else "top", fontweight="bold")
    st_ax.set_yticks([])
    # header: XAU.KH vault cards
    closed = [t for t in shown if t["status"] != "open"]
    W = sum(t["R"] > 0 for t in closed); tot = sum(t["R"] for t in closed)
    models = (bt or {}).get("models", {})
    pr = (models.get("trend_premium") or {}).get("all") or {}
    cb = (models.get("trend_combo") or {}).get("all") or {}
    stamp = local(time.time()) if local else ""
    fig.text(0.05, 0.955, "XAU.KH", color=GOLD, fontsize=16, fontweight="bold")
    fig.text(0.128, 0.955, f"SIGNAL PROOF  ·  last {days} days  ·  {stamp}", color=INK, fontsize=14, fontweight="bold")
    cards = [(f"{W}/{len(closed)}" if closed else "–", "signals won", INK, 0),
             (f"{tot:+.1f}R" if closed else "–", "total result", UP if tot > 0 else DN if tot < 0 else MUT, 0),
             (f"{cb.get('win_rate_pct', '–')}%", f"COMBO intraday · 2 yrs · {cb.get('trades', '')} trades", GOLD, 1),
             (f"{pr.get('win_rate_pct', '–')}%", f"PREMIUM swing · 2 yrs · {pr.get('trades', '')} trades", "#FFD60A", 2)]
    cw = 0.92 / len(cards)
    for k_, (big, small, col, nf) in enumerate(cards):
        cx = 0.05 + k_ * cw
        fig.patches.append(FancyBboxPatch((cx, 0.815), cw - 0.012, 0.105, boxstyle="round,pad=0,rounding_size=0.012",
                                          transform=fig.transFigure, fc=PANEL, ec=GRID, lw=1))
        fig.text(cx + 0.015, 0.868, big, color=col, fontsize=17, fontweight="bold", va="center")
        fig.text(cx + 0.015, 0.832, small, color=MUT, fontsize=7.5, va="center")
        if nf:
            fa = fig.add_axes([cx + cw - 0.075, 0.83, 0.06, 0.075]); fa.set_xlim(0, 3); fa.set_ylim(0, 1); fa.axis("off"); fa.set_zorder(5)
            for q in range(nf):
                _finger(fa, 2.4 - q * 1.0, 0.5, 0.16)
    # legend
    lx = 0.05
    for m, (name, tier, ring) in TIERS.items():
        fig.patches.append(Polygon([(lx, 0.027), (lx, 0.047), (lx + 0.011, 0.037)], closed=True, transform=fig.transFigure, fc=ring))
        fig.text(lx + 0.015, 0.037, f"{name} ({tier.lower()})", color=INK, fontsize=7.5, va="center")
        lx += 0.16
    fig.text(0.05, 0.012, "flag = entry · line = entry → exit · red dash = SL · 1 finger = COMBO · 2 fingers = PREMIUM · angry face = smaller setup (small size) · same rules as live, 15-min delay + costs", color=MUT, fontsize=7, va="center")
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path, shown


def caption(shown, bt=None, days=10):
    closed = [t for t in shown if t["status"] != "open"]
    W = sum(t["R"] > 0 for t in closed); tot = sum(t["R"] for t in closed)
    a = ((bt or {}).get("models", {}).get("trend_intraday") or {}).get("all") or {}
    lines = ["🧾 <b>SIGNAL PROOF · last %d days</b>" % days]
    if closed:
        lines.append(f"{len(closed)} signals · <b>{W} won</b> · {len(closed) - W} lost · <b>{tot:+.1f}R</b>")
    else:
        lines.append("No closed signals in this window: the rules waited.")
    best = max(closed, key=lambda t: t["R"], default=None)
    worst = min(closed, key=lambda t: t["R"], default=None)
    if best and best["R"] > 0:
        lines.append(f"🏆 Best: {TIERS[best['model']][0]} {'BUY' if best['sg'] > 0 else 'SELL'} {best['entry']:,.2f} → {best['R']:+.1f}R")
    if worst and worst["R"] < 0:
        lines.append(f"❌ Worst: {TIERS[worst['model']][0]} {'BUY' if worst['sg'] > 0 else 'SELL'} {worst['entry']:,.2f} → {worst['R']:+.1f}R")
    if a:
        lines.append(f"📚 4H Breakout over 2 years: {a.get('win_rate_pct')}% win · {a.get('avg_R', 0):+.2f}R per trade")
    lines += ["💡 <i>ចាញ់ក៏បង្ហាញ ឈ្នះក៏បង្ហាញ · losses are shown too: that's the proof.</i>",
              "<i>R = result in risk units (+1R = you made what you risked). Same rules as live, delay and costs included.</i>"]
    return "\n".join(lines)


def make(df, path="proof.png", days=10, bt=None, log=None, local=None):
    path, shown = proof_chart(df, path, days, bt, log, local)
    return path, caption(shown, bt, days), shown


if __name__ == "__main__":
    import json
    from engine import load
    from levels import to_ny
    from tg import local as _local
    d = to_ny(load("5m", "20d")).iloc[:-1]
    try:
        b = json.load(open("backtest.json"))
    except Exception:
        b = {}
    p, txt, s = make(d, "proof.png", bt=b, local=_local)
    print(txt)
