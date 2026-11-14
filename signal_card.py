"""XAU.KH signal card: one clean image per signal for the Signals section.

Top: pair, BUY/SELL, tier (B+ / A+ / NORMAL) and status pills.
Middle: 15m chart with market structure (HH / HL / LH / LL), the broken 4H level, and the trade drawn as
zones with Entry / SL / TP1 / TP2 price tags on the right.
Bottom: dark price box (Entry, SL, TP1, TP2 with pips; 1 pip = $0.10) and the tested win rate.

make(df, sig, path, ...) where df = 5m candles (any tz, newest last) and
sig = {"dir": "bull"|"bear", "entry", "stop", "tp1", "target", "level"(optional broken 4H line)}.
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BG, CARD, INK, MUT, GRID = "#F2F2F7", "#FFFFFF", "#1C1C1E", "#8E8E93", "#E5E5EA"
UP, DN, BLUE, PURP, DARK = "#34C759", "#FF3B30", "#007AFF", "#AF52DE", "#1C1C1E"
TIERS = {"premium": ("A+ SETUP", PURP), "combo": ("B+ SETUP", BLUE), "normal": ("NORMAL · half size", MUT),
         "plan": ("PLAN · small size", "#FF9500"), "scalp": ("SCALP · small SL", "#FF9500"),
         "splus": ("S+ SETUP · small size", "#30B0C7"), "setup": ("SETUP · from analysis", "#FF9500"),
         "setup_a": ("A+ · M15 SETUP", PURP), "setup_b": ("B+ · M15 SETUP", BLUE),
         "fun": ("FUN SCALP · 🔥 quality", "#FF2D55"),
         "fun_crazy": ("FUN SCALP · crazy gamble", "#AF52DE"),
         "second": ("SECOND CHANCE · testing", "#FF9500")}


def _fonts():
    import matplotlib.font_manager as fm
    fam = ["DejaVu Sans"]
    for f in ("Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf"):
        p = os.path.join(HERE, "assets", "fonts", f)
        if os.path.exists(p):
            fm.fontManager.addfont(p)
            fam = ["Inter"]
    k = os.path.join(HERE, "assets", "fonts", "KantumruyPro.ttf")   # Khmer letters fall back to this font (shaped correctly)
    if os.path.exists(k):
        fm.fontManager.addfont(k)
        fam.append("Kantumruy Pro")
    return fam


def pips(a, b):
    return (b - a) * 10


def _pivots(h, l, k=5):
    """Swing highs / lows (k bars each side), labelled HH/LH and HL/LL against the previous one."""
    out, last_h, last_l = [], None, None
    for i in range(k, len(h) - k):
        if h[i] == max(h[i - k:i + k + 1]):
            out.append((i, h[i], "HH" if last_h is not None and h[i] > last_h else "LH" if last_h is not None else "H", 1))
            last_h = h[i]
        if l[i] == min(l[i - k:i + k + 1]):
            out.append((i, l[i], "HL" if last_l is not None and l[i] > last_l else "LL" if last_l is not None else "L", -1))
            last_l = l[i]
    return [p for p in out if p[2] not in ("H", "L")]


def _pill(fig, x, y, text, fg, bg, fs=10.5, pad=0.012, h=0.032):
    from matplotlib.patches import FancyBboxPatch
    t = fig.text(x + pad, y, text, color=fg, fontsize=fs, fontweight="bold", va="center", ha="left", zorder=5)
    fig.canvas.draw()
    bb = t.get_window_extent().transformed(fig.transFigure.inverted())
    w = bb.width + 2 * pad
    fig.patches.append(FancyBboxPatch((x, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.016",
                                      transform=fig.transFigure, fc=bg, ec="none", zorder=4))
    return x + w + 0.012


def make(df, sig, path, tier="combo", status="LIVE", win_rate=None, trades=None, stamp="", tf_label="4H breakout",
         bars=110, hold_note="closes within 12 h"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams["font.family"] = _fonts()

    bull = sig["dir"] == "bull"
    side_col = UP if bull else DN
    d = df.resample("15min").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna().tail(bars)
    o, h, l, c = (d[k].to_numpy(float) for k in ("Open", "High", "Low", "Close"))
    n = len(d)
    e, sl, tp1, tp2 = sig["entry"], sig["stop"], sig.get("tp1"), sig["target"]
    tpm = sig.get("tp_mid")   # 🎰 three targets: TP1 / TP2 (tp_mid) / TP3 (target)

    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor=BG)
    # ---- header
    fig.text(0.055, 0.952, "XAU/USD", color=INK, fontsize=21, fontweight="bold", va="center")
    x = _pill(fig, 0.30, 0.952, "BUY" if bull else "SELL", "white", side_col, fs=12)
    name, tcol = TIERS.get(tier, TIERS["combo"])
    x = _pill(fig, x, 0.952, name, "white", tcol, fs=10)
    live = status.upper().startswith(("LIVE", "LIMIT"))
    _pill(fig, x, 0.952, status, BLUE if live else "white", "#E3EEFF" if live else (UP if "TP" in status.upper() else DN), fs=9.5)
    fig.text(0.945, 0.952, "XAU.KH", color=BLUE, fontsize=14, fontweight="bold", va="center", ha="right")
    fig.text(0.055, 0.915, f"{tf_label}  ·  15m chart  ·  {stamp}", color=MUT, fontsize=9.5, va="center")

    # ---- chart card
    fig.patches.append(FancyBboxPatch((0.035, 0.355), 0.93, 0.535, boxstyle="round,pad=0,rounding_size=0.025",
                                      transform=fig.transFigure, fc=CARD, ec="none", zorder=0))
    ax = fig.add_axes([0.06, 0.375, 0.76, 0.5])
    ax.set_facecolor(CARD)
    ax.set_zorder(3)
    ext = int(n * 0.28)                                  # empty space on the right where the trade is drawn
    for i in range(n):
        col = UP if c[i] >= o[i] else DN
        ax.vlines(i, l[i], h[i], color=col, lw=0.8, alpha=0.9)
        ax.add_patch(Rectangle((i - 0.33, min(o[i], c[i])), 0.66, max(abs(c[i] - o[i]), 0.05), fc=col, ec=col, lw=0.4))
    cs = pd.Series(c)
    ax.plot(range(n), cs.ewm(span=21).mean(), color="#FF9500", lw=1.0, alpha=0.8)
    ax.plot(range(n), cs.ewm(span=50).mean(), color=BLUE, lw=1.0, alpha=0.6)

    # structure labels (last few swings only, so the chart stays clean)
    for i, p, lab, sgn in _pivots(h, l)[-7:]:
        good = lab in ("HH", "HL")
        ax.annotate(lab, (i, p), xytext=(0, 9 * sgn), textcoords="offset points", ha="center",
                    va="bottom" if sgn > 0 else "top", fontsize=7.5, fontweight="bold", color=UP if good else DN)

    # broken 4H level
    lvl = sig.get("level")
    if lvl:
        ax.hlines(lvl, 0, n + ext, color=INK, lw=0.9, ls=(0, (4, 3)), alpha=0.55)
        ax.text(2, lvl, f"4H 30-candle {'high' if bull else 'low'} broken  {lvl:,.2f}", fontsize=7.5, color=INK, alpha=0.75,
                va="bottom" if bull else "top", fontweight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

    # trade zones
    x0, x1 = n - 1, n + ext
    ax.add_patch(Rectangle((x0, min(e, tp2)), x1 - x0, abs(tp2 - e), fc=UP, alpha=0.10, ec="none"))
    ax.add_patch(Rectangle((x0, min(e, sl)), x1 - x0, abs(e - sl), fc=DN, alpha=0.10, ec="none"))
    lines = ([(tp2, "TP3", UP), (tpm, "TP2", UP)] if tpm else [(tp2, "TP2" if tp1 else "TP", UP)]) + [(tp1, "TP1", UP), (e, "Entry", INK), (sl, "SL", DN)]
    for y, lab, col in lines:
        if y is None:
            continue
        ax.hlines(y, x0, x1, color=col, lw=1.3 if lab == "Entry" else 1.0, ls="-" if lab in ("Entry", "SL") else (0, (5, 2)))
        ax.text(x1 - 0.5, y, lab, color=col, fontsize=8, fontweight="bold", ha="right",
                va="bottom" if (lab != "SL") == bull else "top")
    ax.annotate("", xy=(x0 + ext * 0.45, tp2), xytext=(x0 + ext * 0.45, e),
                arrowprops=dict(arrowstyle="-|>", color=side_col, lw=1.6, alpha=0.8))

    lo = min(l.min(), sl, tp2) ; hi = max(h.max(), sl, tp2)
    pad = (hi - lo) * 0.06
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_xlim(-1, x1 + 0.5)
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", labelsize=7.5, colors=MUT, length=0)
    ax.set_yticks([])
    ax.grid(axis="y", color=GRID, lw=0.6)
    days = [i for i in range(1, n) if d.index[i].date() != d.index[i - 1].date()]
    ax.set_xticks(days); ax.set_xticklabels([d.index[i].strftime("%d %b") for i in days], fontsize=7.5, color=MUT)
    ax.tick_params(axis="x", length=0)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color=BLUE, alpha=0.04, fontsize=64, fontweight="bold",
            ha="center", va="center")

    # right-side price tags (in figure space, beside the chart)
    tag = fig.add_axes([0.82, 0.375, 0.13, 0.5], sharey=ax)
    tag.axis("off")
    tag.set_zorder(3)
    ys = sorted([(y, lab, col) for y, lab, col in lines if y is not None], key=lambda t: -t[0])
    gap = (hi - lo) * 0.055
    placed = []
    for y, lab, col in ys:                              # keep the tags from overlapping
        yy = y if not placed or placed[-1] - y >= gap else placed[-1] - gap
        placed.append(yy)
        tag.text(0.08, yy, f"{y:,.2f}", color="white", fontsize=8.5, fontweight="bold", va="center", ha="left",
                 bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.5", fc=col, ec="none"))
    last = c[-1]
    tag.text(0.08, last, f"{last:,.2f}", color=INK, fontsize=7.5, va="center", ha="left",
             bbox=dict(boxstyle="round,pad=0.3", fc="#E5E5EA", ec="none")) if all(abs(last - p) > gap for p in placed) else None

    # ---- dark price box
    fig.patches.append(FancyBboxPatch((0.035, 0.03), 0.93, 0.305, boxstyle="round,pad=0,rounding_size=0.025",
                                      transform=fig.transFigure, fc=DARK, ec="none", zorder=0))
    fig.text(0.075, 0.298, "XAU/USD", color="white", fontsize=15, fontweight="bold", va="center")
    _pill(fig, 0.25, 0.298, "BUY" if bull else "SELL", side_col, "#2C2C2E", fs=10.5)
    fig.text(0.925, 0.298, status, color="#0A84FF" if live else (UP if "TP" in status.upper() else DN), fontsize=11,
             fontweight="bold", va="center", ha="right")
    rows = [("Entry", f"{e:,.2f}", ""), ("Stop loss", f"{sl:,.2f}", f"(−{abs(pips(e, sl)):,.0f})")]
    if tp1 and tpm:
        rows += [("TP1 · close ⅓, SL to entry", f"{tp1:,.2f}", f"(+{abs(pips(e, tp1)):,.0f})"),
                 ("TP2 · close ⅓", f"{tpm:,.2f}", f"(+{abs(pips(e, tpm)):,.0f})"),
                 ("TP3", f"{tp2:,.2f}", f"(+{abs(pips(e, tp2)):,.0f})")]
    else:
        if tp1:
            rows.append(("TP1 · close half, SL to entry", f"{tp1:,.2f}", f"(+{abs(pips(e, tp1)):,.0f})"))
        rows.append(("TP2" if tp1 else "Target", f"{tp2:,.2f}", f"(+{abs(pips(e, tp2)):,.0f})"))
    y, step = (0.252, 0.036) if len(rows) > 4 else (0.247, 0.044)
    for k, (a, b, p) in enumerate(rows):
        fig.text(0.075, y, a, color="#AEAEB2", fontsize=10.5, va="center")
        fig.text(0.925, y, f"{b}  {p}".rstrip(), color="white", fontsize=11.5, fontweight="bold", va="center", ha="right")
        if k < len(rows) - 1:
            fig.add_artist(plt.Line2D([0.075, 0.925], [y - step / 2, y - step / 2], color="#38383A", lw=0.8))
        y -= step
    foot = ("Setup idea from analysis · not a tested signal" if tier == "setup" else
            "M15 setup graded by the 4H · live record in Proof" if tier in ("setup_a", "setup_b") else
            "Fun scalp · 1 a day · 2-yr test +0.38R, 69% win" if tier == "fun" else
            "Crazy fun scalp · LOST −0.11R a trade in testing · cent account" if tier == "fun_crazy" else
            "Re-entry after a sweep · 2-yr test +0.47R, testing" if tier == "second" else
            f"Tested 2 years: {win_rate}% win · {trades} trades" if win_rate else "Tested rules only") + f"  ·  {hold_note}"
    fig.text(0.075, 0.068, foot, color="#AEAEB2", fontsize=9, va="center")
    fig.text(0.075, 0.045, ("Small size: risk 0.25–0.5%" if tier in ("scalp", "plan", "splus", "setup", "setup_b", "fun", "fun_crazy", "second") else "Risk 0.5–1% per trade")
             + " · pips: 1 pip = $0.10 · not financial advice", color="#636366",
             fontsize=7.5, va="center")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path
