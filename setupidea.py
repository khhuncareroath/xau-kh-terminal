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
SL_MIN, SL_MAX = 5.0, 15.0        # $ stop range: below 4 the spread decides, above 15 it is not a 15m setup
ZONE_MAX = 20.0                   # $: wider zones are areas, not levels
VALID_H = 8                       # an idea lives one session
MAX_PER_DAY = 2
ZONE_SIGNALS = os.environ.get("ZONE_SIGNALS", "off") == "on"   # 11 Nov 2026 replay: zone reactions -0.15R (138) -> notes only
NOTES_PER_DAY = 1                 # "setup seen, not sent" notes in Setup Analysis: at most 1 a day (owner: too many messages)
MIN_CONF = int(os.environ.get("SETUP_MIN_CONF", 4))   # confirmations needed (of 7) before a setup becomes a signal
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


def zones(df, price, m=None):
    """Active demand (fully below price) and supply (fully above): the 15m FVGs drawn on the analysis card (open or
    partly filled, from liqmap) + the 15m order block of the last structure break + 1H / 4H FVGs and order blocks
    that price has not closed through (splus.py detection). Returns (demand, supply), nearest first."""
    import splus
    now = df.index[-1]
    out = []
    if m:
        out += [dict(dir=z["dir"], lo=float(z["lo"]), hi=float(z["hi"]), tf="15m FVG") for z in (m.get("fvgs") or [])]
        ob = m.get("ob")
        if ob:
            out.append(dict(dir=ob["dir"], lo=float(ob["lo"]), hi=float(ob["hi"]), tf="15m OB"))
    for tf, life in (("1H", 5), ("4H", 15)):   # Daily zones are too wide for a 15m setup
        try:
            zs, _ = splus._zones(df, tf, life)
        except Exception as e:
            print("zones", tf, "failed:", e)
            continue
        out += [dict(z, tf=tf) for z in zs if z["t0"] <= now <= z["t1"]]
    out = [z for z in out if z["hi"] - z["lo"] <= ZONE_MAX]
    dem = sorted([z for z in out if z["dir"] == "bull" and z["hi"] <= price], key=lambda z: -z["hi"])   # fully below
    sup = sorted([z for z in out if z["dir"] == "bear" and z["lo"] >= price], key=lambda z: z["lo"])    # fully above
    return dem, sup


def _room(p, sg, opp, a15=3.0):
    """Mentor rule: never SELL into demand / BUY into supply. If a demand zone holds the SELL trigger or sits within
    1R under it, the SELL waits for a 15m close BELOW that demand (broken demand = supply), SL just above the zone;
    zones in a row are chained. TP1 then stops before the next demand. Mirror for BUY and supply."""
    risk = abs(p["trig"] - p["stop"])
    trig, broke, chained = p["trig"], None, 0
    for z in opp:                                        # nearest first, at most 2 zones in a row
        if chained >= 2:
            break
        near, far = (z["hi"], z["lo"]) if sg < 0 else (z["lo"], z["hi"])
        if (far - trig) * sg <= 0:
            continue                                     # between price and the trigger: closing past the trigger breaks it
        if (near - trig) * sg <= 0 or abs(near - trig) < risk:
            trig, broke, chained = far, z, chained + 1   # trigger moves past the zone
        else:
            break
    if broke:
        back = broke["lo"] if sg > 0 else broke["hi"]    # SL beyond the broken zone
        r = min(max(abs(trig - back) + 0.1 * a15, SL_MIN), SL_MAX)
        p.update(trig=round(trig, 2), stop=round(trig - sg * r, 2),
                 broke={"tf": broke["tf"], "lo": round(broke["lo"], 2), "hi": round(broke["hi"], 2)})
        p["tp1"], p["tp2"] = _levels(p["trig"], p["stop"], sg, p["zone"] if (p["zone"] - p["trig"]) * sg > 0 else None)
        risk = r
    for z in opp:                                        # the next zone ahead: take profit before it
        near = z["hi"] if sg < 0 else z["lo"]
        if (near - p["trig"]) * sg <= 0:
            continue
        if (p["tp1"] - near) * sg > 0 and abs(near - p["trig"]) >= risk:
            p["tp1"] = round(near, 2)
            p["tp2"] = round(p["trig"] + sg * max(2 * risk, abs(p["tp1"] - p["trig"]) + 0.5 * risk), 2)
            p["before"] = {"tf": z["tf"], "lo": round(z["lo"], 2), "hi": round(z["hi"], 2)}
        break
    return p


def _reaction(z, sg, a15, price):
    """Mentor setup at a key zone: price trades INTO the demand, then a 15m candle closes back ABOVE it (buyers
    defended it) -> BUY, SL under the zone. Mirror for supply. Only zones within $40 of price."""
    edge, far = (z["hi"], z["lo"]) if sg > 0 else (z["lo"], z["hi"])
    if abs(price - edge) > 40:
        return None
    r = min(max(abs(edge - far) + 0.1 * a15, SL_MIN), SL_MAX)
    stop = edge - sg * r
    tp1, tp2 = _levels(edge, stop, sg, None)
    return {"edge": round(edge, 2), "stop": round(stop, 2), "tp1": tp1, "tp2": tp2,
            "zone": {"tf": z["tf"], "lo": round(z["lo"], 2), "hi": round(z["hi"], 2)}}


def build(df):
    import liqmap
    m = liqmap.build(df)
    a15 = float(atr(m["d15"]).iloc[-1])
    t = m["top"]
    dem, sup = zones(df, m["price"], m)
    idea = {"t": time.time(), "valid_until": time.time() + VALID_H * 3600, "price": round(m["price"], 2),
            "swing": t.get("4H"), "internal": t.get("15m"), "ltf": t.get("5m"), "daily": t.get("D"), "h1": t.get("1H"),
            "rh": round(m["rh"], 2), "rl": round(m["rl"], 2), "eq": round(m["eq"], 2), "zone": m["zone"],
            "BUY": _room(_side(m, 1, a15), 1, sup, a15), "SELL": _room(_side(m, -1, a15), -1, dem, a15), "done": {}, "atr15": a15,
            "demand": [{k: (round(z[k], 2) if k in ("lo", "hi") else z[k]) for k in ("lo", "hi", "tf")} for z in dem[:2]],
            "supply": [{k: (round(z[k], 2) if k in ("lo", "hi") else z[k]) for k in ("lo", "hi", "tf")} for z in sup[:2]]}
    for side in ("BUY", "SELL"):
        if idea[side].get("blocked"):
            idea["done"][side] = "blocked"
    # the SAME zone gives both outcomes: a close below the demand = SELL (broken), a tap + close back above = BUY
    pick = lambda side, zs, sg: (idea[side].get("broke") or
                                 next((z for z in zs if abs(m["price"] - (z["hi"] if sg > 0 else z["lo"])) >= max(5.0, a15)), None))
    dz, sz = pick("SELL", dem, 1), pick("BUY", sup, -1)
    idea["zone_signals"] = ZONE_SIGNALS
    idea["BUY_DZ"] = _reaction(dz, 1, a15, m["price"]) if dz else None     # buy the demand, with confirmation
    idea["SELL_SZ"] = _reaction(sz, -1, a15, m["price"]) if sz else None   # sell the supply, with confirmation
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
        f"🟢 <b>TARGET BUY</b> : រង់ចាំតម្លៃទីផ្សារបិទលើតម្លៃ <b>{n(b['trig'])}</b> ("
        + (f"បំបែក Supply {n(b['broke']['lo'])}–{n(b['broke']['hi'])} · " if b.get("broke") else "ទិញជាលក្ខណៈ Pullback នៃ Structure · ")
        + f"Target Zone High: <b>{n(b['tp1'])}</b>)",
        f"🔻 <b>TARGET SELL</b> : រង់ចាំតម្លៃទីផ្សារបិទក្រោមតម្លៃ <b>{n(s['trig'])}</b> ("
        + (f"បំបែក Demand {n(s['broke']['lo'])}–{n(s['broke']['hi'])} · " if s.get("broke") else "")
        + f"Target Zone Low: <b>{n(s['tp1'])}</b>)",
        *([f"🟢 <b>BUY at Demand</b> : បើតម្លៃចូល Demand <b>{n(idea['BUY_DZ']['zone']['lo'])}–{n(idea['BUY_DZ']['zone']['hi'])}</b> "
           f"ហើយទៀន 15m បិទត្រឡប់លើ <b>{n(idea['BUY_DZ']['edge'])}</b> ទើបទិញ (SL ក្រោម Demand)"] if idea.get("BUY_DZ") and idea.get("zone_signals") else []),
        *([f"🔻 <b>SELL at Supply</b> : បើតម្លៃចូល Supply <b>{n(idea['SELL_SZ']['zone']['lo'])}–{n(idea['SELL_SZ']['zone']['hi'])}</b> "
           f"ហើយទៀន 15m បិទត្រឡប់ក្រោម <b>{n(idea['SELL_SZ']['edge'])}</b> ទើបលក់ (SL លើ Supply)"] if idea.get("SELL_SZ") and idea.get("zone_signals") else [])])


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
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD = "#F2F2F7", "#FFFFFF", "#E5E5EA", "#1C1C1E", "#8E8E93", "#34C759", "#FF3B30", "#C9971C"
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
    if not idea or now > idea.get("valid_until", 0) or "sent" in idea.get("done", {}).values():
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
    loc = pd.Timestamp(now, unit="s", tz="Asia/Phnom_Penh")
    if loc.hour < 6:   # 2-year replay: closing by midnight Cambodia was as good or better (+0.086R vs +0.070R): no new trades at night
        return False
    cl = float(d15["Close"].iloc[-1])
    if _watch_zones(idea, st, d5, d15, cl, now, dk):
        return True
    for side, sg in (("BUY", 1), ("SELL", -1)):
        p = idea[side]
        if side in idea.get("done", {}) or (cl - p["trig"]) * sg <= 0:   # blocked / skipped sides stay off
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
        if p.get("broke"):   # broken demand / supply: the SL sits beyond that zone
            struct = p["broke"]["lo"] if sg > 0 else p["broke"]["hi"]
        risk = min(max((entry - (struct - sg * 0.1 * a15)) * sg, SL_MIN), SL_MAX)
        stop = round(entry - sg * risk, 2)
        tp1, tp2 = _levels(entry, stop, sg, p["zone"])
        if p.get("before"):   # demand / supply ahead: take profit before it
            near = p["before"]["hi"] if sg < 0 else p["before"]["lo"]
            if (tp1 - near) * sg > 0:
                tp1 = round(near, 2)
            if abs(near - entry) < risk:   # price moved closer to the zone: no room left
                idea["done"][side] = "blocked"
                json.dump(st, open(STATE, "w"), indent=1, default=str)
                print("setup: no room before the", "demand" if sg < 0 else "supply", "zone")
                return False
        if (entry - p["trig"]) * sg > 0.8 * risk:                  # already ran away: do not chase
            idea["done"][side] = "chased"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            from tg import send, fmt
            send(f"⏭ <b>{side} setup skipped</b>: the 15m candle closed {'above' if sg > 0 else 'below'} {fmt(p['trig'])}, "
                 f"but price is already {abs(entry - p['trig']):,.1f} away (too late, do not chase).\n"
                 f"<i>តម្លៃទៅឆ្ងាយហើយ កុំដេញតាម</i>", "Setup skipped")
            return False
        if not _gate(idea, side, sg, d5, d15, entry, f"15m close {'above' if sg > 0 else 'below'} {p['trig']:,.2f}",
                     clear=not p.get("before")):
            idea["done"][side] = "weak"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
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


def _note(text, title="Setup not sent"):
    """'Seen, not sent' notes go to 🔎 Setup Analysis, at most NOTES_PER_DAY a day (silent)."""
    from tg import send
    day = (pd.Timestamp(time.time(), unit="s", tz="America/New_York") - pd.Timedelta(hours=18)).strftime("%Y-%m-%d")
    n = jl("setup_notes.json")
    if n.get("day") != day:
        n = {"day": day, "count": 0}
    if n["count"] >= NOTES_PER_DAY:
        print("setup note skipped (daily cap):", text[:60])
        return
    send(text, title, silent=True)
    n["count"] += 1
    json.dump(n, open("setup_notes.json", "w"))


def checks(idea, sg, d5, d15, entry, reaction=False, clear=True):
    """The confirmation checklist, from closed candles at the moment of the setup. Returns [(ok, English, Khmer)]."""
    import liqmap
    want = "bull" if sg > 0 else "bear"
    a15 = float(atr(d15).iloc[-1])
    o, c = float(d15["Open"].iloc[-1]), float(d15["Close"].iloc[-1])
    b15, b5 = liqmap._bias(d15.tail(400)), liqmap._bias(d5.tail(600))
    lo8, hi8 = float(d15["Low"].iloc[-8:].min()), float(d15["High"].iloc[-8:].max())
    lo_prev, hi_prev = float(d15["Low"].iloc[-28:-8].min()), float(d15["High"].iloc[-28:-8].max())
    swept = (lo8 < lo_prev) if sg > 0 else (hi8 > hi_prev)
    disc = (entry < idea["eq"]) if sg > 0 else (entry > idea["eq"])
    news = _news_near(time.time() + 45 * 60) or _news_near(time.time())
    side = "BUY" if sg > 0 else "SELL"
    return [
        (idea.get("swing") == want, f"4H swing trend {'up' if sg > 0 else 'down'}", "និន្នាការ 4H ត្រូវទិស"),
        (idea.get("h1") == want, f"1H structure {'up' if sg > 0 else 'down'}", "Structure 1H ត្រូវទិស"),
        (b15 == want, f"15m structure turned {'up' if sg > 0 else 'down'} (BOS / CHOCH)", "15m BOS/CHOCH ត្រូវទិស"),
        (b5 == want, f"5m confirmation {'up' if sg > 0 else 'down'}", "5m បញ្ជាក់"),
        (abs(c - o) >= 0.6 * a15 and (c - o) * sg > 0, "strong 15m candle (displacement)", "ទៀន 15m ខ្លាំង"),
        (swept, f"liquidity swept {'below' if sg > 0 else 'above'} first ($$)", "បោស liquidity មុន"),
        ((disc, f"entry from {'discount' if sg > 0 else 'premium'} (good price)", f"ចូលពី {'discount' if sg > 0 else 'premium'}")
         if reaction else
         (clear, f"clear path: no {'supply' if sg > 0 else 'demand'} before TP1", f"គ្មាន {'Supply' if sg > 0 else 'Demand'} រាំងមុន TP1")),
    ] + ([(False, "big news soon: wait", "ព័ត៌មានធំជិតមកដល់")] if news else [])


def htf_break(d5, sg, hours=12):
    """The tested 4H rule as a helper for M15: did a 4H candle in the last `hours` close beyond the 1-week high / low
    in this direction, with a strong close and a clean 4H trend? (research.py A+/B+ conditions, without the Day Meter.)"""
    import ict
    import research
    d4 = ict.resample(d5, "4H")
    end = d5.index[-1] + pd.Timedelta(minutes=5)
    d4 = d4[d4.index + pd.Timedelta(hours=4) <= end]
    if len(d4) < 35:
        return None
    hi30, lo30 = d4["High"].rolling(30).max().shift(1), d4["Low"].rolling(30).min().shift(1)
    for k in range(len(d4) - 1, len(d4) - 1 - max(1, hours // 4), -1):
        c = float(d4["Close"].iloc[k])
        if (c > hi30.iloc[k]) if sg > 0 else (c < lo30.iloc[k]):
            t = d4.index[k] + pd.Timedelta(hours=4, minutes=20)
            cl = research.close_location(d5, t, "bull" if sg > 0 else "bear")
            er = research.efficiency(d5, t)
            if (cl is None or cl >= research.STRONG_CLOSE) and (er is None or er > research.CHOP_ER):
                return {"time": str(d4.index[k] + pd.Timedelta(hours=4)), "level": round(float(hi30.iloc[k] if sg > 0 else lo30.iloc[k]), 2)}
    return None


def grade(idea, sg, score, brk):
    """4H judges the M15 setup. A+ = with the 4H trend AND (6+ confirmations OR a fresh tested 4H breakout the same way).
    B+ = with the 4H trend and MIN_CONF+. Against the 4H trend or too few confirmations = None (not sent)."""
    with4h = idea.get("swing") == ("bull" if sg > 0 else "bear")
    if not with4h or score < MIN_CONF:
        return None
    return "A+" if (score >= 6 or brk) else "B+"


def _gate(idea, side, sg, d5, d15, entry, kind, reaction=False, clear=True):
    """True = enough confirmations: send the signal. False = post a short 'not enough' note in 🔎 Setup Analysis."""
    ck = checks(idea, sg, d5, d15, entry, reaction, clear)
    score = sum(1 for ok, *_ in ck if ok)
    brk = htf_break(d5, sg)
    tier = None if any(not ok and "news" in en for ok, en, _ in ck) else grade(idea, sg, score, brk)
    idea.setdefault("checks", {})[side] = {"score": score, "of": len(ck), "list": [[bool(a), b, c] for a, b, c in ck],
                                           "tier": tier, "htf_break": brk}
    if tier:
        return True
    from tg import fmt, send
    why = ("against the 4H trend" if idea.get("swing") != ("bull" if sg > 0 else "bear") else
           f"{score}/{len(ck)} confirmations (needs {MIN_CONF})")
    _note(f"🔎 <b>{side} setup seen, NOT sent</b> · {kind} at {fmt(entry)} · {why}\n"
         + "\n".join(f"{'✅' if ok else '❌'} {en}" for ok, en, _ in ck)
         + f"\n<i>មិនទាន់គ្រប់ការបញ្ជាក់ · មិនផ្ញើសញ្ញា</i>", "Setup not sent")
    print("setup: not enough confirmations", side, score)
    return False


def _watch_zones(idea, st, d5, d15, cl, now, dk):
    """Demand / supply reaction: the zone was tapped (a closed 15m candle traded into it, within the last hour) and the
    newest closed 15m candle closed back beyond it. A close through the far side cancels it (zone broken)."""
    last_t = d15.index[-1]
    since = d15[(d15.index + pd.Timedelta(minutes=15)).map(lambda t: t.timestamp()) >= idea["t"]]
    for key, side, sg in (("BUY_DZ", "BUY", 1), ("SELL_SZ", "SELL", -1)):
        p = idea.get(key)
        if not p or key in idea.get("done", {}):
            continue
        z = p["zone"]
        tap = since[since["Low"] <= z["hi"]] if sg > 0 else since[since["High"] >= z["lo"]]
        if not len(tap):
            continue
        after = since[since.index >= tap.index[0]]
        if ((after["Close"] < z["lo"]) if sg > 0 else (after["Close"] > z["hi"])).any():
            idea["done"][key] = "zone broken"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            continue
        if (cl - p["edge"]) * sg <= 0 or tap.index[-1] < d15.index[-5]:
            continue
        k_ = f"{key}|{last_t}"
        if st.get("last_key") == k_:
            return False
        st["last_key"] = k_
        if _news_near(now):
            idea["done"][key] = "news"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            return False
        a15 = float(atr(d15).iloc[-1])
        entry = float(d5["Close"].iloc[-1])
        far = z["lo"] if sg > 0 else z["hi"]
        risk = min(max((entry - (far - sg * 0.1 * a15)) * sg, SL_MIN), SL_MAX)
        if (entry - p["edge"]) * sg > 0.8 * risk:
            idea["done"][key] = "chased"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            continue
        stop = round(entry - sg * risk, 2)
        tp1, tp2 = _levels(entry, stop, sg, None)
        why = (f"Price came into the {'demand' if sg > 0 else 'supply'} {z['lo']:,.2f}–{z['hi']:,.2f} ({z['tf']}) and a 15m candle "
               f"closed back {'above' if sg > 0 else 'below'} it")
        if not ZONE_SIGNALS:   # tested 2 years: these lose; the zone stays on the chart as a key level
            idea["done"][key] = "note only"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            _note(f"🔎 <b>{side} reaction at the {'demand' if sg > 0 else 'supply'} {z['lo']:,.0f}–{z['hi']:,.0f}</b> "
                  f"(15m close back {'above' if sg > 0 else 'below'})\n<i>Analysis only, not a signal: in 2 years of testing these "
                  f"reaction trades lost (−0.15R each). Signals come from the TARGET lines. · វិភាគប៉ុណ្ណោះ មិនមែនសញ្ញា</i>")
            continue
        if not _gate(idea, side, sg, d5, d15, entry, f"{'demand' if sg > 0 else 'supply'} {z['lo']:,.0f}–{z['hi']:,.0f} reaction", reaction=True):
            idea["done"][key] = "weak"
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            continue
        if _send(idea, side, sg, entry, stop, tp1, tp2, last_t, {"trig": p["edge"]}, why=why):
            idea["done"][key] = "sent"
            st.setdefault("count", {})[dk] = st.get("count", {}).get(dk, 0) + 1
            json.dump(st, open(STATE, "w"), indent=1, default=str)
            return True
    return False


def _send(idea, side, sg, entry, stop, tp1, tp2, t15, p, why=None):
    from tg import fmt, local, log_alert, msg_link, send, send_photo
    bull = sg > 0
    risk = abs(entry - stop)
    pp = lambda px: f"{abs(px - entry) * 10:,.0f}"
    link = msg_link(idea.get("msg_id"), f"{idea.get('session', '')} session")
    wt = idea.get("with_trend")
    ck = idea.get("checks", {}).get(side)
    loc = pd.Timestamp(time.time(), unit="s", tz="Asia/Phnom_Penh")
    hold_s = int(min(8 * 3600, ((loc.normalize() + pd.Timedelta(days=1)) - loc).total_seconds()))   # closed by 24:00 Cambodia
    cap = "\n".join(x for x in [
        f"{'🟢' if bull else '🔴'} <b>XAU/USD — {side} | " + ("💎 A+" if (ck or {}).get("tier") == "A+" else "⭐ B+") + "</b>",
        f"📍 Entry: <b>{fmt(entry)}</b>",
        f"🛑 SL: <b>{fmt(stop)}</b>",
        f"🎯 TP1: <b>{fmt(tp1)}</b>",
        f"🎯 TP2: <b>{fmt(tp2)}</b>",
        (f"🧩 Confirmations: <b>{ck['score']}/{ck['of']}</b>" if ck else None),
        f"⏱ Timeframe: M15 · 4H " + ("trend + breakout" if (ck or {}).get("htf_break") else "trend") + f" · closes by 24:00 · −${risk:,.0f} at SL (0.01 lot)",
    ] if x)
    title = f"{side} idea" if TOPIC == "signals" else f"{side} setup triggered"
    mid = None
    try:
        import signal_card
        from engine import load
        from levels import to_ny
        d5 = to_ny(load("5m", "20d")).iloc[:-1]
        signal_card.make(d5, {"dir": "bull" if bull else "bear", "entry": entry, "stop": stop, "tp1": tp1, "target": tp2,
                              "level": p["trig"]}, "setup_card.png", tier="setup_a" if (ck or {}).get("tier") == "A+" else "setup_b", status="LIVE", stamp=local(time.time()),
                         tf_label="15m setup", hold_note="closes by 24:00")
        mid = send_photo("setup_card.png", cap, title)
    except Exception as e:
        print("setup card failed, text:", e)
    if not mid:
        mid = send(cap, title)
    if not mid:
        return None
    now = time.time()
    log_alert({"id": f"setup|{side}|{'zone' if why else 'break'}|{t15}", "kind": "m15", "model": "setup_idea", "dir": "bull" if bull else "bear",
               "entry": entry, "stop": stop, "target": tp2, "tp1": tp1, "part": 0.5, "rr": round(abs(tp2 - entry) / risk, 2),
               "created": now, "valid_until": now + 900, "price_at_alert": entry, "msg_id": mid if isinstance(mid, int) else None,
               "status": "filled", "filled_at": now, "fill": entry, "max_hold_s": hold_s, "tier": (ck or {}).get("tier") or "setup",
               "zone": f"TARGET {side} {p['trig']}"})
    print("setup sent", side, entry, stop, tp1, tp2)
    try:   # 🔎 the reason recap, separate from the clean signal feed
        ck = idea.get("checks", {}).get(side)
        sl = msg_link(mid if isinstance(mid, int) else None, title)
        recap = "\n".join(x for x in [
            f"🔎 <b>WHY THIS {side} · {fmt(entry)}</b> ({idea.get('session', '')} setup idea)", "",
            f"📍 {why or ('15m candle closed ' + ('above' if bull else 'below') + ' the TARGET ' + side + ' line ' + fmt(p['trig']))}",
            f"🗺 Swing 4H {BW[idea.get('swing')][0]} · 1H {BW[idea.get('h1')][0]} · 15m {BW[idea.get('internal')][0]} · Swing range "
            f"{fmt(idea['rl'])}–{fmt(idea['rh'])}",
            (f"⚖️ 4H judge: <b>{ck.get('tier')}</b> · with the 4H trend"
             + (f" + tested 4H breakout {'above' if bull else 'below'} {fmt(ck['htf_break']['level'])}" if ck.get("htf_break") else "")
             + (" + 6/7 confirmations" if ck["score"] >= 6 else "") if ck else None),
            *([f"🧩 <b>Confirmations {ck['score']}/{ck['of']}</b>"] + [f"{'✅' if ok else '❌'} {en} · {km}" for ok, en, km in ck["list"]]
              if ck else []),
            f"🛑 Wrong if price closes {'below' if bull else 'above'} {fmt(stop)} · 🎯 TP1 {fmt(tp1)} → TP2 {fmt(tp2)}",
            (f"<a href=\"{sl}\">📈 Signal</a>" if sl else None) and ((f"<a href=\"{sl}\">📈 Signal</a>") + (f" · <a href=\"{link}\">📊 Analysis</a>" if link else "")),
        ] if x)
        send(recap, "Setup reason")
    except Exception as e:
        print("setup recap failed:", e)
    return mid
