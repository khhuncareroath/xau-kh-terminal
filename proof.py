"""XAU.KH Signal Proof: one picture with every intraday signal of the last ~2 weeks, wins AND losses.

The signals are found by running the exact live rules (research.py, the same code the backtest and live_models.py
use, with the 15-minute alert delay and the $0.40 cost) on the recent candles. Each signal gets an XAU.KH pin on the
chart and a result pill on the "proof strip" at the bottom. A signal that was also really sent to the channel is
marked LIVE. This is our own design (tier rings + result pills), not a copy of any indicator.

Used by session.py: the Friday weekly proof and one quiet-hours check-in a day. Run alone to make proof.png."""
import time

import numpy as np
import pandas as pd

import research
from ict import resample

TIERS = {   # model: (short name, tier, ring colour)
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
            try:
                getattr(research, m)(df)
            except Exception as e:
                print("proof replay", m, "failed:", e)
    finally:
        research._run_trade, research._run_scaled = real_t, real_s
    return sorted(trades, key=lambda t: t["j0"])


def _live_match(t, df, log):
    t0 = df.index[t["j0"]].timestamp()
    for a in log or []:
        if a.get("model") == t["model"] and abs(a.get("created", 0) - t0) < 40 * 60 and \
                (a.get("dir") == "bull") == (t["sg"] > 0):
            return True
    return False


def proof_chart(df, path="proof.png", days=10, bt=None, log=None, local=None):
    """Draws the proof picture. Returns (path, caption text, list of trades shown)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, PANEL, GRID, INK, MUT, UP, DN = "#0B0B0D", "#121215", "#1E1E22", "#E8E8ED", "#7C7C85", "#2BD07B", "#FF4D4D"
    trades = replay(df)
    start = df.index[-1] - pd.Timedelta(days=days)
    shown = [t for t in trades if df.index[t["j0"]] >= start]
    for t in shown:
        t["live"] = _live_match(t, df, log)
    d1 = resample(df[df.index >= start], "1H")
    N = len(d1)
    pos = lambda j: int(np.clip(d1.index.searchsorted(df.index[j], side="right") - 1, 0, N - 1))
    fig = plt.figure(figsize=(13, 7.4), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.045, 0.30, 0.70, 0.56]); st_ax = fig.add_axes([0.045, 0.08, 0.70, 0.17], sharex=ax)
    sb = fig.add_axes([0.77, 0.08, 0.21, 0.78])
    for a_ in (ax, st_ax, sb):
        a_.set_facecolor(PANEL); a_.set_xticks([])
        for sp in a_.spines.values(): sp.set_visible(False)
        a_.tick_params(colors=MUT, labelsize=8, length=0)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_xlim(-1, N + 1)
    for i, (o_, h_, l_, c_) in enumerate(d1[["Open", "High", "Low", "Close"]].to_numpy()):
        col = "#3A6F55" if c_ >= o_ else "#7A3A3A"
        ax.plot([i, i], [l_, h_], color=col, lw=0.7)
        ax.add_patch(Rectangle((i - 0.32, min(o_, c_)), 0.64, max(abs(c_ - o_), 0.05), color=col, lw=0))
    lo, hi = float(d1["Low"].min()), float(d1["High"].max()); rng = hi - lo
    ax.set_ylim(lo - rng * 0.08, hi + rng * 0.10)
    # day separators + weekday labels
    tday = (d1.index - pd.Timedelta(hours=18)).date
    last_lab = -99
    for k in range(1, N):
        if tday[k] != tday[k - 1]:
            for a_ in (ax, st_ax):
                a_.axvline(k - 0.5, color=GRID, lw=0.8)
            if k - last_lab >= 8:   # trading day named by the day it mostly trades (Sunday 18:00 open = Monday)
                st_ax.text(k, -1.55, (pd.Timestamp(tday[k]) + pd.Timedelta(days=1)).strftime("%a %d"), color=MUT,
                           fontsize=7, ha="left", va="top")
                last_lab = k
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color="#FFFFFF", alpha=0.025, fontsize=80, fontweight="bold",
            ha="center", va="center", zorder=0)
    # signal pins: tier ring + direction, a line from entry to exit coloured by the result
    for t in shown:
        x0, x1 = pos(t["j0"]), pos(t["j"])
        name, tier, ring = TIERS[t["model"]]
        good = t["R"] > 0
        res_col = UP if good else DN if t["status"] != "open" else INK
        ex = float(df["Close"].iloc[t["j"]]) if t["status"] in ("time", "open") else \
            t["tgt"] if t["status"] == "win" else t["entry"] if t["status"] == "tp1" else t["stop"]
        ax.plot([x0, max(x1, x0 + 0.6)], [t["entry"], ex], color=res_col, lw=1.6, alpha=0.9, zorder=4)
        ax.plot([x0 - 0.8, x0 + 0.8], [t["stop"], t["stop"]], color=DN, lw=0.8, alpha=0.6, zorder=3)
        y_pin = t["entry"] - t["sg"] * rng * 0.07
        ax.plot([x0, x0], [t["entry"], y_pin], color=ring, lw=0.8, zorder=4)
        ax.scatter([x0], [y_pin], s=150, facecolor=PANEL, edgecolor=ring, linewidths=1.8, zorder=6)
        ax.text(x0, y_pin, "▲" if t["sg"] > 0 else "▼", color=UP if t["sg"] > 0 else DN, fontsize=6.5,
                ha="center", va="center", zorder=7, fontweight="bold")
        if t.get("live"):
            ax.text(x0, y_pin - t["sg"] * rng * 0.035, "LIVE", color=ring, fontsize=6, ha="center",
                    va="top" if t["sg"] > 0 else "bottom", fontweight="bold", zorder=7)
    # proof strip: one result pill per signal, height = R
    st_ax.set_ylim(-1.6, 3.4); st_ax.axhline(0, color=MUT, lw=0.6, alpha=0.6)
    st_ax.text(0, 3.2, "PROOF STRIP · every signal's result in R (risk units) · wins AND losses", color=MUT, fontsize=7, va="top")
    for t in shown:
        x = pos(t["j0"]); r = max(-1.3, min(3.1, t["R"]))
        col = INK if t["status"] == "open" else UP if t["R"] > 0 else DN
        st_ax.add_patch(FancyBboxPatch((x - 0.9, min(0, r)), 1.8, max(abs(r), 0.08), boxstyle="round,pad=0,rounding_size=0.4",
                                       fc=col, ec=TIERS[t["model"]][2], lw=1.0, alpha=0.9, mutation_aspect=0.25))
        st_ax.text(x, r + (0.12 if r >= 0 else -0.12), "open" if t["status"] == "open" else f"{t['R']:+.1f}",
                   color=col, fontsize=6.5, ha="center", va="bottom" if r >= 0 else "top", fontweight="bold")
    st_ax.set_yticks([])
    # scoreboard
    sb.set_xlim(0, 1); sb.set_ylim(0, 1); sb.set_yticks([])
    closed = [t for t in shown if t["status"] != "open"]
    W = sum(t["R"] > 0 for t in closed); tot = sum(t["R"] for t in closed)
    sb.text(0.07, 0.95, f"LAST {days} DAYS", color=MUT, fontsize=8, fontweight="bold")
    sb.text(0.07, 0.87, f"{W} / {len(closed)} won" if closed else "no closed signals", color=INK, fontsize=17, fontweight="bold")
    sb.text(0.07, 0.82, f"{tot:+.1f}R total" if closed else "", color=UP if tot > 0 else DN if tot < 0 else MUT,
            fontsize=12, fontweight="bold")
    y = 0.72
    models = (bt or {}).get("models", {})
    for m, (name, tier, ring) in TIERS.items():
        mine = [t for t in closed if t["model"] == m]
        opn = sum(t["model"] == m and t["status"] == "open" for t in shown)
        a = (models.get(m) or {}).get("all") or {}
        sb.scatter([0.11], [y + 0.012], s=70, facecolor=PANEL, edgecolor=ring, linewidths=1.8)
        sb.text(0.20, y, name, color=INK, fontsize=9.5, fontweight="bold", va="bottom")
        sb.text(0.20, y - 0.035, tier, color=ring, fontsize=7, fontweight="bold", va="bottom")
        sb.text(0.20, y - 0.075, (f"{len(mine)} here · {sum(t['R'] > 0 for t in mine)} won · {sum(t['R'] for t in mine):+.1f}R"
                                  if mine else "none closed in this window") + (f" · {opn} open" if opn else ""),
                color=INK, fontsize=7.5, va="bottom")
        if a:
            sb.text(0.20, y - 0.11, f"2 yrs: {a.get('trades')} trades · {a.get('win_rate_pct')}% · {a.get('avg_R', 0):+.2f}R",
                    color=MUT, fontsize=7, va="bottom")
        y -= 0.19
    sb.text(0.07, 0.10, "Ring = tier   ▲ BUY ▼ SELL\nLine = entry → exit\nRed dash = SL", color=MUT, fontsize=7, va="bottom",
            linespacing=1.5)
    sb.text(0.07, 0.03, "Same rules as live · 15-min delay\n+ costs included", color=MUT, fontsize=6.5, va="bottom")
    stamp = local(time.time()) if local else ""
    fig.text(0.045, 0.94, f"XAU.KH · Signal Proof · {stamp}", color=INK, fontsize=15, fontweight="bold")
    fig.text(0.045, 0.905, "Every intraday signal on the chart, wins and losses, nothing hidden", color="#E3B04B", fontsize=10.5)
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
