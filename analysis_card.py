"""XAU.KH analysis card: the clean, light chart for 📊 Analysis posts and /check (same style as signal_card).

15m candles with structure (HH/HL/LH/LL), EMA 21/50, 15m + 1H fair value gaps (unfilled), liquidity levels
(previous day high/low, Asia high/low), the 4H signal lines, the plan zone (POC) if there is one, and a Day Meter bar.
Header: trend pills + one-line "what to do". Bottom dark box: the key numbers.

make(df, ict, lv, lines, path, title, used=None, plan=None, todo="", trend=0) -> path
"""
import numpy as np
import pandas as pd

import signal_card as sc
from signal_card import BG, CARD, INK, MUT, GRID, UP, DN, BLUE, DARK, _pill, _pivots, _fonts

LIQ = ("Prev day high", "Prev day low", "Asia high", "Asia low")


def make(df, ict, lv, lines, path, title, used=None, plan=None, todo="", trend=0, bars=96, scenarios=None, liq=None, setup=None):
    if setup:   # a side blocked by demand / supply gets no trigger line and no arrow on the chart
        bb, sb = setup["BUY"].get("blocked"), setup["SELL"].get("blocked")
        if liq:   # the chart draws the setup's own trigger lines (moved past demand / supply when needed)
            liq = dict(liq, trig_buy=None if bb else setup["BUY"]["trig"], trig_sell=None if sb else setup["SELL"]["trig"])
        scenarios = ([] if bb else [(setup["BUY"]["trig"], setup["BUY"]["tp1"], "#34C759")]) + \
                    ([] if sb else [(setup["SELL"]["trig"], setup["SELL"]["tp1"], "#FF3B30")])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams["font.family"] = _fonts()

    d = df.resample("15min").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna().tail(bars)
    o, h, l, c = (d[k].to_numpy(float) for k in ("Open", "High", "Low", "Close"))
    n = len(d)
    price = float(c[-1])
    upper, lower = float(lines[0]), float(lines[1])

    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor=BG)
    fig.text(0.055, 0.952, "XAU/USD", color=INK, fontsize=21, fontweight="bold", va="center")
    tr_txt, tr_col = ("4H UP", UP) if trend > 0 else ("4H DOWN", DN) if trend < 0 else ("4H RANGE", MUT)
    x = _pill(fig, 0.30, 0.952, tr_txt, "white", tr_col, fs=11)
    if used is not None:
        zt, zc = (("A+ ZONE", "#AF52DE") if used >= 1.0 else ("B+ ZONE", BLUE) if used >= 0.7 else ("QUIET DAY", MUT))
        _pill(fig, x, 0.952, zt, "white", zc, fs=10)
    fig.text(0.945, 0.952, "XAU.KH", color=BLUE, fontsize=14, fontweight="bold", va="center", ha="right")
    if liq:   # top-down row: D 4H 1H 30m 15m 5m
        xx = 0.055
        for k in ("D", "4H", "1H", "30m", "15m", "5m"):
            b = liq["top"].get(k)
            xx = _pill(fig, xx, 0.912, f"{k} {'↑' if b == 'bull' else '↓' if b == 'bear' else '↔'}", "white",
                       UP if b == "bull" else DN if b == "bear" else MUT, fs=8.5, h=0.026) - 0.004
        fig.text(0.945, 0.912, title.split("·")[-1].strip(), color=MUT, fontsize=8.5, va="center", ha="right")
    else:
        fig.text(0.055, 0.915, title, color=MUT, fontsize=9.5, va="center")

    fig.patches.append(FancyBboxPatch((0.035, 0.30), 0.93, 0.59, boxstyle="round,pad=0,rounding_size=0.025",
                                      transform=fig.transFigure, fc=CARD, ec="none", zorder=0))
    ax = fig.add_axes([0.06, 0.32, 0.74, 0.555])
    ax.set_zorder(3)
    ax.set_facecolor(CARD)
    ext = int(n * 0.22)
    lo_v = min(l.min(), price - (upper - lower) * 0.02)
    hi_v = max(h.max(), price + (upper - lower) * 0.02)
    for (_, y1, _) in (scenarios or [])[:2]:   # keep both if/then paths on the chart
        if abs(y1 - price) < price * 0.02:
            lo_v, hi_v = min(lo_v, y1), max(hi_v, y1)
    pad = (hi_v - lo_v) * 0.06
    ylo, yhi = lo_v - pad, hi_v + pad
    show = lambda y: ylo + pad * 0.3 <= y <= yhi - pad * 0.3
    ax.set_ylim(ylo, yhi)

    # fair value gaps (unfilled), drawn from their time to the right edge
    t0 = d.index[0]
    for tf in ("15m", "1H"):
        for z in ((ict.get("timeframes") or {}).get(tf) or {}).get("fvgs") or []:
            if z.get("status") in ("filled", "broken"):
                continue
            try:
                zt = pd.Timestamp(z["time"])
                xi = max(0, int(d.index.searchsorted(zt.tz_convert(d.index.tz) if zt.tzinfo else zt)))
            except Exception:
                xi = 0
            if not (show(z["lo"]) and show(z["hi"])):
                continue
            col = UP if z["dir"] == "bull" else DN
            ax.add_patch(Rectangle((xi, z["lo"]), n + ext - xi, z["hi"] - z["lo"], fc=col, alpha=0.08, ec="none", zorder=1))
            ax.text(n + ext - 0.5, (z["lo"] + z["hi"]) / 2, f"{tf} FVG", color=col, fontsize=6.5, ha="right", va="center", alpha=0.8, clip_on=True)

    for i in range(n):
        col = UP if c[i] >= o[i] else DN
        ax.vlines(i, l[i], h[i], color=col, lw=0.8, zorder=3)
        ax.add_patch(Rectangle((i - 0.33, min(o[i], c[i])), 0.66, max(abs(c[i] - o[i]), 0.05), fc=col, ec=col, lw=0.4, zorder=3))
    cs = pd.Series(c)
    ax.plot(range(n), cs.ewm(span=21).mean(), color="#FF9500", lw=1.0, alpha=0.8, zorder=2)
    ax.plot(range(n), cs.ewm(span=50).mean(), color=BLUE, lw=1.0, alpha=0.55, zorder=2)
    for i, p, lab, sgn in _pivots(h, l)[-7:]:
        ax.annotate(lab, (i, p), xytext=(0, 9 * sgn), textcoords="offset points", ha="center",
                    va="bottom" if sgn > 0 else "top", fontsize=7.5, fontweight="bold",
                    color=UP if lab in ("HH", "HL") else DN, zorder=4)

    # mentor-style liquidity map: dealing range box, EQ, ELQ edges, ILQ dashed lines, $$ sweeps
    if liq:
        tx = lambda i15: int(d.index.searchsorted(liq["d15"].index[min(i15, len(liq["d15"]) - 1)]))
        x0 = max(0, min(tx(liq["rh_i"]), tx(liq["rl_i"])))
        if show(liq["rh"]) or show(liq["rl"]):
            ax.add_patch(Rectangle((x0, liq["rl"]), n + ext - x0, liq["rh"] - liq["rl"], fc="none", ec=INK, lw=0.8,
                                   alpha=0.35, zorder=2))
        for y, lab in ((liq["rh"], "ELQ buy-side"), (liq["rl"], "ELQ sell-side")):
            if show(y):
                ax.text(x0 + 1, y, lab, fontsize=7, color=INK, fontweight="bold", va="bottom" if "buy" in lab else "top",
                        zorder=4, clip_on=True)
        if show(liq["eq"]):
            ax.hlines(liq["eq"], x0, n + ext, color=INK, lw=0.6, ls=(0, (1, 2)), alpha=0.5, zorder=2)
            ax.text(x0 + 1, liq["eq"], "EQ 50%", fontsize=6.5, color=MUT, va="bottom", zorder=4, clip_on=True)
        for z in liq["ilq_up"] + liq["ilq_dn"]:
            if show(z["price"]):
                xs = tx(z["i"])
                ax.hlines(z["price"], xs, n + ext * 0.5, color="#FF9500", lw=0.9, ls=(0, (3, 2)), zorder=2)
                ax.text(xs, z["price"], "ILQ", fontsize=6.5, color="#FF9500", fontweight="bold",
                        va="bottom" if z["kind"] == "H" else "top", zorder=4, clip_on=True)
        for z in liq["sweeps"]:
            if z.get("at") is not None and show(z["price"]):
                xs = tx(z["at"])
                ax.text(xs, z["price"], r"\$\$", fontsize=8, color="#FF9500", fontweight="bold", ha="center",
                        va="bottom" if z["kind"] == "H" else "top", zorder=5, clip_on=True)

    if liq:
        e = liq.get("last")
        if e and show(e["level"]):
            col = UP if e["dir"] == "bull" else DN
            xs = max(0, tx(e["i"]) - 6)
            ax.hlines(e["level"], xs, tx(e["i"]), color=col, lw=1.2, zorder=4)
            ax.text(xs, e["level"], ("CHOCH" if e["type"] == "MSS" else "BOS") + (" ↑" if e["dir"] == "bull" else " ↓"),
                    fontsize=7.5, color=col, fontweight="bold", va="bottom" if e["dir"] == "bull" else "top", zorder=5, clip_on=True)
        ob = liq.get("ob")
        if ob and show(ob["lo"]) and show(ob["hi"]):
            col = UP if ob["dir"] == "bull" else DN
            xs = tx(ob["i"])
            ax.add_patch(Rectangle((xs, ob["lo"]), n + ext * 0.5 - xs, max(ob["hi"] - ob["lo"], 0.3), fc=col, alpha=0.13,
                                   ec=col, lw=0.6, zorder=1))
            ax.text(xs + 0.5, (ob["lo"] + ob["hi"]) / 2, "OB", fontsize=7, color=col, fontweight="bold", va="center", zorder=5, clip_on=True)
        for y, lab, col in ((liq.get("trig_buy"), "BUY close >", UP), (liq.get("trig_sell"), "SELL close <", DN)):
            if y and show(y):
                ax.hlines(y, n - 8, n + ext, color=col, lw=1.4, zorder=4)
                ax.text(n + ext - 0.5, y, f"{lab} {y:,.0f}", fontsize=7, color="white", fontweight="bold", ha="right",
                        va="bottom" if col == UP else "top", zorder=6, clip_on=True,
                        bbox=dict(boxstyle="round,pad=0.2", fc=col, ec="none"))

    if setup:   # demand / supply that the setup respects: labelled boxes on the right
        for key, col, word in (("demand", UP, "DEMAND"), ("supply", DN, "SUPPLY")):
            side_ = "SELL" if key == "demand" else "BUY"
            zs_ = [setup[side_]["broke"]] if setup[side_].get("broke") else (setup.get(key) or [])[:1]
            for z in zs_:
                if show(z["lo"]) or show(z["hi"]):
                    ax.add_patch(Rectangle((n - 14, z["lo"]), ext + 14, max(z["hi"] - z["lo"], 0.4), fc=col, alpha=0.16,
                                           ec=col, lw=0.9, zorder=2))
                    ax.text(n - 13.5, (z["lo"] + z["hi"]) / 2, f"{word} {z['tf']}", fontsize=7, color=col,
                            fontweight="bold", va="center", zorder=6, clip_on=True)

    # liquidity + 4H lines
    lad = {x["name"]: float(x["price"]) for x in lv.get("ladder", []) if x.get("price")}
    for name in LIQ:
        y = lad.get(name)
        if y and show(y):
            ax.hlines(y, 0, n + ext, color=MUT, lw=0.7, ls=(0, (2, 3)), zorder=2)
            ax.text(1, y, f"{name} {y:,.2f}  · stops", fontsize=6.8, color=MUT, va="bottom", zorder=4, clip_on=True)
    for y, lab, col in ((upper, "4H BUY above", UP), (lower, "4H SELL below", DN)):
        if show(y):
            ax.hlines(y, 0, n + ext, color=col, lw=1.2, ls=(0, (6, 3)), zorder=2)
            ax.text(1, y, f"{lab} {y:,.2f}", fontsize=7.5, color=col, fontweight="bold", va="bottom" if col == UP else "top",
                    zorder=4, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    if plan and plan.get("side") and plan.get("edge") and show(plan["edge"]):
        y = plan["edge"]
        col = DN if plan["side"] == "SELL" else UP
        ax.add_patch(Rectangle((n - 1, y - 0.6), ext + 1, 1.2, fc=col, alpha=0.5, ec="none", zorder=2))
        ax.text(n + ext - 0.5, y, f"PLAN {plan['side']} POC {y:,.2f}", color=col, fontsize=7, fontweight="bold",
                ha="right", va="bottom", zorder=4)

    ax.set_xlim(-1, n + ext)
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", labelsize=7.5, colors=MUT, length=0)
    ax.grid(axis="y", color=GRID, lw=0.6)
    days = [i for i in range(1, n) if d.index[i].date() != d.index[i - 1].date()]
    ax.set_xticks(days); ax.set_xticklabels([d.index[i].strftime("%d %b") for i in days], fontsize=7.5, color=MUT)
    ax.tick_params(axis="x", length=0)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.annotate(f" {price:,.2f} ", (n - 1, price), xytext=(n + 1, price), fontsize=8, color="white",
                fontweight="bold", va="center", bbox=dict(boxstyle="round,pad=0.3", fc=INK, ec="none"), zorder=5)
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color=BLUE, alpha=0.04, fontsize=64, fontweight="bold",
            ha="center", va="center")

    # volume profile of the last ~5 days (Aizen-style): bars on the right edge, POC + value area
    vp = None
    try:
        src = df[df.index >= df.index[-1] - pd.Timedelta(days=5)]
        if "Volume" in src and src["Volume"].sum() > 0:
            step = 1.0
            mids = ((src["High"] + src["Low"]) / 2 / step).round() * step
            prof = src["Volume"].groupby(mids).sum().sort_index()
            prof = prof[(prof.index >= ylo) & (prof.index <= yhi)]
            if len(prof) > 10:
                poc = float(prof.idxmax())
                order = prof.sort_values(ascending=False)
                va = order[order.cumsum() <= order.sum() * 0.7].index
                vah, val = float(va.max()), float(va.min())
                width = ext * 0.9
                for y, v in prof.items():
                    inva = val <= y <= vah
                    ax.add_patch(Rectangle((n + ext - width * v / prof.max(), y - step * 0.45), width * v / prof.max(), step * 0.9,
                                           fc=BLUE if inva else "#C7C7CC", alpha=0.25 if inva else 0.18, ec="none", zorder=1))
                ax.hlines(poc, 0, n + ext, color=BLUE, lw=0.9, alpha=0.7, zorder=2)
                ax.text(n + ext - 0.5, poc, f"POC {poc:,.0f}", color=BLUE, fontsize=6.8, fontweight="bold", ha="right",
                        va="bottom", zorder=4, clip_on=True)
                vp = (poc, vah, val)
    except Exception as e:
        print("volume profile failed:", e)

    # two scenarios (mentor-chart style): where price likely goes if it holds / if it breaks
    if scenarios:
        for (y0, y1, col) in scenarios[:2]:
            if show(y1):
                ax.annotate("", xy=(n + ext * 0.55, y1), xytext=(n - 1, y0),
                            arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5, ls=(0, (4, 2)), alpha=0.85), zorder=5)

    # Day Meter bar on the right
    if used is not None:
        bx = fig.add_axes([0.875, 0.32, 0.05, 0.555])
        bx.set_zorder(3)
        bx.set_xlim(0, 1); bx.set_ylim(0, 1.5)
        bx.axis("off")
        bx.add_patch(Rectangle((0.15, 0), 0.7, 1.5, fc="#F2F2F7", ec="none"))
        v = min(used, 1.5)
        bx.add_patch(Rectangle((0.15, 0), 0.7, v, fc="#AF52DE" if used >= 1 else BLUE if used >= 0.7 else "#C7C7CC", ec="none"))
        for yv, lab in ((0.7, "70%"), (1.0, "100%")):
            bx.hlines(yv, 0.05, 0.95, color=INK, lw=0.8)
            bx.text(0.5, yv + 0.02, lab, ha="center", va="bottom", fontsize=6.5, color=INK)
        bx.text(0.5, -0.05, f"{used * 100:.0f}%", ha="center", va="top", fontsize=9, fontweight="bold", color=INK)
        fig.text(0.90, 0.885, "Day\nMeter", ha="center", va="top", fontsize=7, color=MUT)

    # dark box: what to do + key numbers
    fig.patches.append(FancyBboxPatch((0.035, 0.03), 0.93, 0.25, boxstyle="round,pad=0,rounding_size=0.025",
                                      transform=fig.transFigure, fc=DARK, ec="none", zorder=0))
    fig.text(0.075, 0.245, "What to do · setup ideas, not tested signals · small size 0.25–0.5%" if setup else
             "What to do · the map shows both paths, it does not predict", color="#AEAEB2", fontsize=9.5, va="center")
    import textwrap
    fig.text(0.075, 0.212, "\n".join(textwrap.wrap(todo or "Wait for a signal.", 62)[:2]), color="white", fontsize=11.5,
             fontweight="bold", va="top", linespacing=1.4)
    rows = []
    if setup:
        for side, col in (("BUY", UP), ("SELL", DN)):
            p_ = setup[side]
            wt = " ✓ trend" if side == setup.get("with_trend") else ""
            if p_.get("blocked"):
                z = p_["blocked"]
                rows.append((f"TARGET {side}: none · {'supply above' if side == 'BUY' else 'demand below'} ({z['tf']})",
                             f"wait · {z['lo']:,.0f}–{z['hi']:,.0f}", "#8E8E93"))
            else:
                brk = (" supply" if side == "BUY" else " demand") if p_.get("broke") else ""
                rows.append((f"TARGET {side}: 15m close {'above' if side == 'BUY' else 'below'}{brk}{wt}",
                             f"{p_['trig']:,.2f} · SL {p_['stop']:,.0f} · TP {p_['tp1']:,.0f} / {p_['tp2']:,.0f}", col))
        for key, side, col, word in (("BUY_DZ", "BUY", UP, "demand"), ("SELL_SZ", "SELL", DN, "supply")):
            q = setup.get(key)
            if q:
                rows.append((f"{side} at {word} {q['zone']['lo']:,.0f}–{q['zone']['hi']:,.0f}: 15m close back {'above' if side == 'BUY' else 'below'}",
                             f"{q['edge']:,.2f} · SL {q['stop']:,.0f} · TP {q['tp1']:,.0f} / {q['tp2']:,.0f}", col))
        liq = dict(liq or {}, trig_buy=None, trig_sell=None)
    if liq:
        if liq.get("trig_buy"):
            rows.append(("If a 15m candle closes above", f"{liq['trig_buy']:,.2f}" + (f" → {liq['tgt_buy']:,.0f}" if liq.get("tgt_buy") else ""), UP))
        if liq.get("trig_sell"):
            rows.append(("If a 15m candle closes below", f"{liq['trig_sell']:,.2f}" + (f" → {liq['tgt_sell']:,.0f}" if liq.get("tgt_sell") else ""), DN))
    rows = [("NEXT SIGNAL · 4H close: BUY above / SELL below", f"{upper:,.0f} / {lower:,.0f}", "#FFD60A")] + rows
    if plan and plan.get("side") and plan.get("edge"):
        rows.append((f"Plan {plan['side']} at POC", f"{plan['edge']:,.2f}", "#FF9500"))
    y, dy, fa, fb = (0.152, 0.027, 8.8, 9.8) if len(rows) > 3 else (0.135, 0.034, 10, 11)
    for a_, b_, col in rows:
        fig.text(0.075, y, a_, color="#AEAEB2", fontsize=fa, va="center")
        fig.text(0.925, y, b_, color=col, fontsize=fb, fontweight="bold", va="center", ha="right")
        y -= dy
    fig.text(0.075, 0.045, ("" if len(rows) > 3 else "Setup idea, not a tested A+/B+ signal · small size 0.25–0.5%") if setup else
             "Analysis, not a signal · entries come only in 📈 Signals".replace("📈 ", ""), color="#636366",
             fontsize=7.5, va="center")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path
