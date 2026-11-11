"""📐 SETUP IDEA: the mentor-style session plan in 📊 Analysis, and the alert when price confirms it.

Owner, 11 Nov 2026: "set-up ideas in Analysis, clear Khmer + English like my mentor, details on the picture; when price
goes the planned way, send the setup signal."

Each session (Asia / London / New York) the analysis post becomes ONE setup idea, built from the 15m liquidity map
(liqmap.py, closed candles only):
  Swing bias (4H) · Internal bias (15m) · LTF (5m) · Swing High / Swing Low (15m dealing range)
  🟢 TARGET BUY : wait for a 15m close ABOVE the nearest internal high  -> buy, SL under the pullback low, TP1 the
                  next liquidity (target zone), TP2 2R
  🔴 TARGET SELL: wait for a 15m close BELOW the nearest internal low   -> sell, mirror
watch() runs every cycle: when a CLOSED 15m candle confirms one side (within the idea's 8 hours, not 15 min around big
news, not chased), it sends "📐 SETUP · BUY/SELL" with entry / SL / TP and logs it for track.py, so every result is
replied (TP / SL) and counted in 🏆 Proof. The other side is cancelled. Max 2 setup alerts a day.

HONEST LABEL: these are analysis ideas, not tested signals. The 11 Nov 2026 tests (studies/RESULTS.md) found these
trigger lines alone near 50/50 (+0.0R), so every alert says "small size 0.25-0.5%" and the live record decides.
Off with the repo variable SETUP_IDEAS=off.  SETUP_TOPIC=setups sends the alerts to 🔎 Setup Analysis instead of 📈 Signals.
"""
import json
import os
import time

import numpy as np
import pandas as pd

from engine import atr

STATE = "setup_idea.json"
SL_MIN, SL_MAX = 4.0, 15.0        # $ stop range: below 4 the spread decides, above 15 it is not a 15m setup
VALID_H = 8                       # an idea lives one session
MAX_PER_DAY = 2
ON = os.environ.get("SETUP_IDEAS", "on") != "off"
TOPIC = os.environ.get("SETUP_TOPIC", "signals")
BW = {"bull": ("Bullish ↑", "ឡើង"), "bear": ("Bearish ↓", "ធ្លាក់"), None: ("Range ↔", "ចំហៀង")}


def jl(n, d=None):
    try:
        return json.load(open(n))
    except Exception:
        return {} if d is None else d


def _levels(entry, stop, sg, zone):
    risk = (entry - stop) * sg
    tp1 = zone if zone is not None and (zone - entry) * sg >= risk else entry + sg * risk          # at least 1R
    tp1 = min(tp1, entry + 2 * risk) if sg > 0 else max(tp1, entry - 2 * risk)
    tp2 = entry + sg * max(2 * risk, abs(tp1 - entry) + 0.5 * risk)
    return round(tp1, 2), round(tp2, 2)


def _side(m, sg, a15):
    """Planned trade for one side (the stop is re-measured when the candle really closes)."""
    trig = m["trig_buy"] if sg > 0 else m["trig_sell"]
    zone = m["tgt_buy"] if sg > 0 else m["tgt_sell"]
    prot = [x["price"] for x in (m["ilq_dn"] if sg > 0 else m["ilq_up"])]   # the level that must hold after the break
    base = (prot[0] if prot else (m["rl"] if sg > 0 else m["rh"])) - sg * 0.1 * a15
    risk = min(max((trig - base) * sg, SL_MIN), SL_MAX)
    stop = trig - sg * risk
    tp1, tp2 = _levels(trig, stop, sg, zone)
    return {"trig": round(trig, 2), "stop": round(stop, 2), "zone": round(zone, 2), "tp1": tp1, "tp2": tp2}


def build(df):
    import liqmap
    m = liqmap.build(df)
    a15 = float(atr(m["d15"]).iloc[-1])
    t = m["top"]
    idea = {"t": time.time(), "valid_until": time.time() + VALID_H * 3600, "price": round(m["price"], 2),
            "swing": t.get("4H"), "internal": t.get("15m"), "ltf": t.get("5m"), "daily": t.get("D"), "h1": t.get("1H"),
            "rh": round(m["rh"], 2), "rl": round(m["rl"], 2), "eq": round(m["eq"], 2), "zone": m["zone"],
            "BUY": _side(m, 1, a15), "SELL": _side(m, -1, a15), "done": {}, "atr15": a15}
    sw = idea["swing"]
    idea["with_trend"] = "BUY" if sw == "bull" else "SELL" if sw == "bear" else None
    return idea, m


def caption(idea, name, signal_line=None, day_meter=None):
    """Mentor format, short: bias, swing high/low, TARGET BUY / SELL. SL, TP and everything else are on the picture."""
    W = {"bull": ("Bullish", "លំហូរទីផ្សារឡើង"), "bear": ("Bearish", "លំហូរទីផ្សារធ្លាក់"), None: ("Range", "ទីផ្សារចំហៀង")}
    n = lambda x: f"{x:.0f}"
    b, s = idea["BUY"], idea["SELL"]
    head = {"Asia": "🌏", "London": "🇬🇧", "New York": "🇺🇸"}.get(name, "📐")
    return "\n".join([
        f"{head} <b>XAU/USD · {name}</b>", "",
        f"Swing : <b>{W[idea['swing']][0]}</b> ({W[idea['swing']][1]})",
        f"Internal : <b>{W[idea['internal']][0]}</b>",
        f"LTF Structure : <b>{W[idea['ltf']][0]}</b>",
        f"Swing Low Price: <b>{n(idea['rl'])}</b>",
        f"Swing High Price: <b>{n(idea['rh'])}</b>", "",
        f"🟢 <b>TARGET BUY</b> : រង់ចាំតម្លៃទីផ្សារបិទលើតម្លៃ <b>{n(b['trig'])}</b> (ទិញជាលក្ខណៈ Pullback នៃ Structure · Target Zone High: <b>{n(b['tp1'])}</b>)",
        f"🔻 <b>TARGET SELL</b> : រង់ចាំតម្លៃទីផ្សារបិទក្រោមតម្លៃ <b>{n(s['trig'])}</b> (Target Zone Low: <b>{n(s['tp1'])}</b>)"])


# ------------------------------------------------------------------ picture

def chart(idea, m, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams["font.family"] = "DejaVu Sans"
    try:
        import signal_card
        plt.rcParams["font.family"] = signal_card._fonts()
    except Exception:
        pass
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD = "#0B0B0D", "#141418", "#22222A", "#ECECF1", "#8A8A94", "#2BD07B", "#FF4D4D", "#E3B04B"
    d = m["d15"].tail(80)
    off = len(m["d15"]) - len(d)
    N = len(d)
    o, h, l, c = (d[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    b, s = idea["BUY"], idea["SELL"]
    ys = [l.min(), h.max(), b["tp2"], s["tp2"], b["stop"], s["stop"]]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.06
    fig = plt.figure(figsize=(12, 7.6), dpi=150, facecolor=BG)
    ax = fig.add_axes([0.04, 0.09, 0.78, 0.74], facecolor=PANEL)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(color=GRID, lw=0.6); ax.tick_params(colors=MUT, labelsize=8)
    ax.yaxis.tick_right()
    X0, X1 = N + 2, N + 26          # plan boxes to the right of the last candle
    ax.set_xlim(-1, X1 + 1); ax.set_ylim(lo - pad, hi + pad)
    for i in range(N):
        col = UP if c[i] >= o[i] else DN
        ax.plot([i, i], [l[i], h[i]], color=col, lw=0.8, zorder=3)
        ax.add_patch(Rectangle((i - 0.33, min(o[i], c[i])), 0.66, max(abs(c[i] - o[i]), 0.05), color=col, lw=0, zorder=3))
    lab = lambda x, y, t, col, ha="left", va="center", fs=8, bold=True: ax.text(
        x, y, t, color=col, fontsize=fs, fontweight="bold" if bold else "normal", ha=ha, va=va, zorder=8,
        bbox=dict(boxstyle="round,pad=0.25", fc=PANEL, ec="none", alpha=0.9))
    # dealing range: swing high / low and EQ
    for y, t_, col in ((idea["rh"], f"SWING HIGH {idea['rh']:,.2f} · buy-side liquidity", MUT),
                       (idea["rl"], f"SWING LOW {idea['rl']:,.2f} · sell-side liquidity", MUT)):
        ax.axhline(y, color=col, lw=1.0, ls=(0, (6, 4)), zorder=2)
        lab(0, y, t_, col, va="bottom" if y == idea["rh"] else "top", fs=7.5)
    ax.axhline(idea["eq"], color=GRID, lw=1.0, zorder=1)
    lab(N * 0.12, idea["eq"], f"EQ 50% {idea['eq']:,.2f}", MUT, fs=7, bold=False)
    # internal liquidity and sweeps
    for x in (m["ilq_up"] + m["ilq_dn"]):
        i = x["i"] - off
        if 0 <= i < N:
            ax.plot([i, N - 1], [x["price"]] * 2, color=GOLD, lw=0.8, ls=":", zorder=2)
            ax.text(i, x["price"], "$", color=GOLD, fontsize=8, ha="center", va="center", fontweight="bold", zorder=6)
    for z in (m.get("fvgs") or [])[-3:]:
        i = z.get("i", N - 20) - off
        if i < N:
            ax.add_patch(Rectangle((max(i, 0), z["lo"]), N - max(i, 0), z["hi"] - z["lo"],
                                   color=UP if z["dir"] == "bull" else DN, alpha=0.10, lw=0, zorder=1))
            lab(N - 1, (z["lo"] + z["hi"]) / 2, "FVG", UP if z["dir"] == "bull" else DN, ha="right", fs=6.5)
    e = m.get("last")
    if e and 0 <= e["i"] - off < N:
        i = e["i"] - off
        name = e["type"].replace("MSS", "CHOCH")
        ax.plot([max(0, i - 8), i], [e["level"]] * 2, color=INK, lw=1.0)
        lab(i, e["level"], f"{name} {'↑' if e['dir'] == 'bull' else '↓'}", INK, ha="center",
            va="bottom" if e["dir"] == "bull" else "top", fs=7.5)
    # the two plans side by side on the right: BUY box, then SELL box; each trigger line runs into its own box
    boxes = {"BUY": (X0, X0 + 11), "SELL": (X0 + 13, X1)}
    for side, p, col, sg in (("BUY", b, UP, 1), ("SELL", s, DN, -1)):
        x0, x1 = boxes[side]
        ax.plot([0, x1], [p["trig"]] * 2, color=col, lw=1.6, zorder=4)
        wt = " · with trend" if side == idea["with_trend"] else " · counter-trend" if idea["with_trend"] else ""
        lab(N * 0.42, p["trig"], f"TARGET {side}: 15m close {'above' if sg > 0 else 'below'} {p['trig']:,.2f}{wt}",
            col, va="bottom" if sg > 0 else "top", fs=8.5)
        ax.add_patch(Rectangle((x0, min(p["trig"], p["tp2"])), x1 - x0, abs(p["tp2"] - p["trig"]), color=col, alpha=0.14, lw=0, zorder=2))
        ax.add_patch(Rectangle((x0, min(p["trig"], p["stop"])), x1 - x0, abs(p["trig"] - p["stop"]), fc="none",
                               ec=MUT, alpha=0.5, lw=0, zorder=2, hatch="////"))
        for y, t_, cc, ty in ((p["tp2"], f"TP2 {p['tp2']:,.2f}", col, p["tp2"]), (p["tp1"], f"TP1 {p['tp1']:,.2f}", col, p["tp1"]),
                              (p["stop"], f"SL {p['stop']:,.2f}", INK, (p["stop"] + p["trig"]) / 2)):
            ax.plot([x0, x1], [y, y], color=cc if "TP" in t_ else MUT, lw=1.0, ls="-" if "TP" in t_ else "--", zorder=4)
            ax.text((x0 + x1) / 2, ty, t_, color=cc, fontsize=7.2, fontweight="bold", ha="center",
                    va=("bottom" if sg > 0 else "top") if "TP2" in t_ else "center", zorder=8,
                    bbox=dict(boxstyle="round,pad=0.2", fc=PANEL, ec="none", alpha=0.85))
        ax.text((x0 + x1) / 2, p["trig"] + sg * (abs(p["tp1"] - p["trig"]) * 0.45), f"{side}\nafter the\n15m close",
                color=col, fontsize=7, fontweight="bold", ha="center", va="center", zorder=5)
    price = float(c[-1])
    ax.annotate(f"{price:,.2f}", xy=(N - 1, price), xytext=(N - 0.2, price), color=BG, fontsize=8, fontweight="bold",
                va="center", bbox=dict(boxstyle="round,pad=0.3", fc=INK, ec="none"), zorder=9)
    step = max(1, N // 6)
    ax.set_xticks(range(0, N, step))
    ax.set_xticklabels([d.index[i].tz_convert("Asia/Phnom_Penh").strftime("%H:%M") for i in range(0, N, step)])
    ax.text(0.5, 0.5, "XAU.KH", transform=ax.transAxes, color=GOLD, alpha=0.04, fontsize=80, fontweight="bold",
            ha="center", va="center", zorder=0)
    # header + bias pills
    fig.text(0.04, 0.95, title, color=INK, fontsize=15, fontweight="bold", va="center")
    fig.text(0.04, 0.905, "15m setup idea · wait for the candle CLOSE beyond a TARGET line, then the bot sends the setup",
             color=MUT, fontsize=9, va="center")
    pills = [("Daily", idea["daily"]), ("Swing 4H", idea["swing"]), ("1H", idea["h1"]), ("Internal 15m", idea["internal"]),
             ("LTF 5m", idea["ltf"])]
    x = 0.87
    fig.text(x, 0.83, "TOP-DOWN", color=MUT, fontsize=8, fontweight="bold")
    for k, (n_, bias) in enumerate(pills):
        col = UP if bias == "bull" else DN if bias == "bear" else MUT
        y = 0.79 - k * 0.055
        fig.patches.append(FancyBboxPatch((x, y - 0.018), 0.118, 0.036, boxstyle="round,pad=0.004", fc=PANEL, ec=col, lw=1,
                                          transform=fig.transFigure, figure=fig))
        fig.text(x + 0.007, y, n_, color=MUT, fontsize=7.5, va="center")
        fig.text(x + 0.112, y, {"bull": "BULL ↑", "bear": "BEAR ↓", None: "RANGE"}[bias], color=col, fontsize=7.5,
                 fontweight="bold", va="center", ha="right")
    y = 0.79 - 5 * 0.055 - 0.02
    zone = "DISCOUNT (cheap)" if idea["zone"] == "discount" else "PREMIUM (expensive)"
    for t_, col in ((f"Price in {zone}", GOLD),
                    (f"With-trend side: {idea['with_trend'] or 'none'}", UP if idea["with_trend"] == "BUY" else DN if idea["with_trend"] == "SELL" else MUT),
                    ("$ = internal liquidity", GOLD), ("Shaded = TP zone", INK), ("Hatched = SL zone", MUT)):
        fig.text(x, y, t_, color=col, fontsize=7.5, va="center"); y -= 0.035
    fig.text(0.04, 0.035, "Setup idea from analysis, not a tested A+/B+ signal · small size 0.25–0.5% · no entry 15 min "
             "around big news · every result is shown in Proof", color=MUT, fontsize=8, va="center")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


# ------------------------------------------------------------------ post + watch

def post(df, name, signal_line=None, day_meter=None, draw=None):
    """Builds and posts the session's setup idea in 📊 Analysis. Returns the message id (or None).
    draw(idea, path): the session's analysis card (owner's preferred picture); chart() is the fallback."""
    from tg import local, send, send_photo
    idea, m = build(df)
    path = None
    if draw:
        try:
            path = draw(idea, "setup_idea.png")
        except Exception as e:
            print("setup card failed, dark chart:", e)
    if not path:
        path = chart(idea, m, "setup_idea.png", f"XAU/USD · {name.upper()} SETUP IDEA · {local(time.time())}")
    cap = caption(idea, name, signal_line, day_meter)
    mid = send_photo(path, cap, f"{name} session")
    if not mid:
        mid = send(cap, f"{name} session")
    idea["msg_id"] = mid if isinstance(mid, int) else None
    idea["session"] = name
    st = jl(STATE)
    st["idea"] = idea
    json.dump(st, open(STATE, "w"), indent=1, default=str)
    return mid


def _news_near(now):
    for e in jl("news.json").get("events", []):
        if e.get("impact") != "High":
            continue
        try:
            t = pd.Timestamp(e["time"]).timestamp()
        except Exception:
            continue
        if -15 * 60 <= t - now <= 15 * 60:
            return e.get("title", "news")
    return None


def watch(df):
    """Every cycle: did a CLOSED 15m candle confirm the active idea? Then send the setup. Returns True if sent."""
    if not ON:
        return False
    st = jl(STATE)
    idea = st.get("idea")
    now = time.time()
    if not idea or now > idea.get("valid_until", 0) or len(idea.get("done", {})) >= 1:
        return False
    import ict
    d5 = df.iloc[:-1]                                              # the newest 5m candle is still forming
    d15 = ict.resample(d5, "15m")
    end = d5.index[-1] + pd.Timedelta(minutes=5)
    d15 = d15[d15.index + pd.Timedelta(minutes=15) <= end]          # closed 15m candles only
    if len(d15) < 10:
        return False
    last_t = d15.index[-1]
    if (last_t + pd.Timedelta(minutes=15)).timestamp() < idea["t"]:   # candle closed before the idea was posted
        return False
    if now - (last_t + pd.Timedelta(minutes=15)).timestamp() > 20 * 60:   # stale data: never alert late
        return False
    day = pd.Timestamp(now, unit="s", tz="America/New_York") - pd.Timedelta(hours=18)
    dk = day.strftime("%Y-%m-%d")
    if st.get("count", {}).get(dk, 0) >= MAX_PER_DAY:
        return False
    cl = float(d15["Close"].iloc[-1])
    for side, sg in (("BUY", 1), ("SELL", -1)):
        p = idea[side]
        if (cl - p["trig"]) * sg <= 0:
            continue
        key = f"{side}|{last_t}"
        if st.get("last_key") == key:
            return False
        st["last_key"] = key
        news = _news_near(now)
        if news:
            idea["done"][side] = "news"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            print("setup: confirmed but big news within 15 min, skipped:", news)
            return False
        a15 = float(atr(d15).iloc[-1])
        entry = float(d5["Close"].iloc[-1])
        recent = d15.iloc[-6:]
        struct = float(recent["Low"].min()) if sg > 0 else float(recent["High"].max())   # the pullback that must hold
        risk = min(max((entry - (struct - sg * 0.1 * a15)) * sg, SL_MIN), SL_MAX)
        stop = round(entry - sg * risk, 2)
        tp1, tp2 = _levels(entry, stop, sg, p["zone"])
        if (entry - p["trig"]) * sg > 0.8 * risk:                  # already ran away: do not chase
            idea["done"][side] = "chased"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            from tg import send, fmt
            send(f"⏭ <b>{side} setup skipped</b>: the 15m candle closed {'above' if sg > 0 else 'below'} {fmt(p['trig'])}, "
                 f"but price is already {abs(entry - p['trig']):,.1f} away (too late, do not chase).\n"
                 f"<i>តម្លៃទៅឆ្ងាយហើយ កុំដេញតាម</i>", "Setup skipped")
            return False
        sent = _send(idea, side, sg, entry, stop, tp1, tp2, last_t, p)
        if sent:
            idea["done"][side] = "sent"
            other = "SELL" if side == "BUY" else "BUY"
            idea["done"].setdefault(other, "cancelled")
            st.setdefault("count", {})[dk] = st.get("count", {}).get(dk, 0) + 1
            st["count"] = dict(list(st["count"].items())[-10:])
        json.dump(st, open(STATE, "w"), indent=1, default=str)
        return bool(sent)
    return False


def _send(idea, side, sg, entry, stop, tp1, tp2, t15, p):
    from tg import fmt, local, log_alert, msg_link, send, send_photo
    bull = sg > 0
    risk = abs(entry - stop)
    pp = lambda px: f"{abs(px - entry) * 10:,.0f}"
    link = msg_link(idea.get("msg_id"), f"{idea.get('session', '')} session")
    wt = idea.get("with_trend")
    cap = "\n".join(x for x in [
        f"📐 <b>XAU/USD — {side} | SETUP</b> (from the {idea.get('session', '')} analysis)",
        f"🇰🇭 <b>{'ទិញ' if bull else 'លក់'}</b> · ចូល {fmt(entry)} · SL {fmt(stop)} · TP1 {fmt(tp1)} (បិទពាក់កណ្ដាល) · TP2 {fmt(tp2)} · lot តូច",
        f"✅ 15m candle closed {'above' if bull else 'below'} <b>{fmt(p['trig'])}</b> (TARGET {side})",
        f"📍 Entry: <b>{fmt(entry)}</b>",
        f"🛑 SL: <b>{fmt(stop)}</b> ({pp(stop)} pips) · under the {'pullback low' if bull else 'pullback high'}",
        f"🎯 TP1: <b>{fmt(tp1)}</b> (+{pp(tp1)}) → close half, SL to entry",
        f"🎯 TP2: <b>{fmt(tp2)}</b> (+{pp(tp2)})",
        f"💰 0.01 lot: SL −${risk:,.1f} · 0.01 lot per ${risk * 200:,.0f} of account (0.5% risk)",
        ("✅ With the 4H trend" if side == wt else "⚠️ Against the 4H trend: smaller size or skip" if wt else None),
        "⏱ Closes within 8 h · enter now or skip",
        "<i>Setup idea from analysis, not a tested A+/B+ signal · risk 0.25–0.5% · result shown in 🏆 Proof</i>",
        (f"<a href=\"{link}\">📊 See the analysis</a>" if link else None),
    ] if x)
    title = f"{side} idea" if TOPIC == "signals" else f"{side} setup triggered"
    mid = None
    try:
        import signal_card
        from engine import load
        from levels import to_ny
        d5 = to_ny(load("5m", "20d")).iloc[:-1]
        signal_card.make(d5, {"dir": "bull" if bull else "bear", "entry": entry, "stop": stop, "tp1": tp1, "target": tp2,
                              "level": p["trig"]}, "setup_card.png", tier="setup", status="LIVE", stamp=local(time.time()),
                         tf_label="15m setup", hold_note="closes within 8 h")
        mid = send_photo("setup_card.png", cap, title)
    except Exception as e:
        print("setup card failed, text:", e)
    if not mid:
        mid = send(cap, title)
    if not mid:
        return None
    now = time.time()
    log_alert({"id": f"setup|{side}|{t15}", "kind": "setup", "model": "setup_idea", "dir": "bull" if bull else "bear",
               "entry": entry, "stop": stop, "target": tp2, "tp1": tp1, "part": 0.5, "rr": round(abs(tp2 - entry) / risk, 2),
               "created": now, "valid_until": now + 900, "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None,
               "status": "filled", "filled_at": now, "fill": entry, "max_hold_s": 8 * 3600, "tier": "setup",
               "zone": f"TARGET {side} {p['trig']}"})
    print("setup sent", side, entry, stop, tp1, tp2)
    return mid
