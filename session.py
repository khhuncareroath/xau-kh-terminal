"""Session briefings and heads-up alerts for Telegram. Runs every cycle after ict.py and confluence.py.

1. Briefing with a chart photo, 30 minutes before each session (New York time):
     Asia 17:30 (Sun-Thu), London 01:30 (Mon-Fri), New York 07:00 (Mon-Fri).
   Direction, key levels, the exact breakout lines of the trend model, what to look for, and the risks.
2. Intraday areas: the nearest SELL area above and BUY area below (day highs/lows, value area, VWAP bands, A/B zones).
   A 🟠 "getting close" alert at 0.12%, then a reply when the area held (reached its first target) or broke
   (15m close 0.25% beyond). Study on 2 years of spot data: these levels held 44-62% of the time with no stable
   edge, so the alerts teach where to look and where the idea is wrong; they are never BUY/SELL signals.
3. Heads-up: when price comes within HEADS_UP_PCT of the trend model's breakout line, one early warning
   ("if the 4H candle closes beyond X at 16:00, the signal triggers"), once per line per day.

Everything here describes the market and the rules; the trade signal itself still comes from notify.py, and only
from a proven model. Env: BOT_LANG (en, km, both), DISPLAY_TZ, SITE_URL."""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from engine import atr, live_source, load
from ict import resample
from levels import to_ny
from tg import SITE, esc, fmt, local, send, send_photo

NY = ZoneInfo("America/New_York")
LANG = os.environ.get("BOT_LANG", "en")
if LANG == "both":   # English messages already carry Khmer labels inline; no second full block
    LANG = "en"
HEADS_UP_PCT = 0.0025          # 0.25% of price, about $10 at $3,900
SESSIONS = [("Asia", 17, 30, (6, 0, 1, 2, 3)), ("London", 1, 30, (0, 1, 2, 3, 4)), ("New York", 7, 0, (0, 1, 2, 3, 4))]
KM_SESSION = {"Asia": "អាស៊ី", "London": "ឡុងដ៍", "New York": "ញូវយ៉ក"}
STATE = "session_state.json"


def jl(n, d=None):
    try:
        return json.load(open(n))
    except Exception:
        return {} if d is None else d


# ---------- economy: how the big US events usually move gold ----------
EVENT_RULES = [   # (keywords in the event title, plain explanation)
    (("cpi", "pce", "inflation", "ppi"), "Inflation data. Hotter than forecast → the Fed stays strict → yields and the dollar rise → gold usually falls. Cooler → gold usually rises."),
    (("non-farm", "nonfarm", "employment change", "payroll"), "US jobs report. More jobs than forecast → strong economy, strong dollar → gold usually falls. Weak jobs → gold usually rises."),
    (("unemployment rate",), "Unemployment rate. Higher than forecast → weaker economy → rate cuts more likely → gold usually rises."),
    (("jobless claims", "unemployment claims"), "Weekly jobless claims. More claims → weaker jobs market → gold usually rises a little."),
    (("fomc", "federal funds", "fed chair", "powell", "interest rate decision"), "Federal Reserve. A tougher (hawkish) tone or fewer cuts → dollar up → gold down. A softer (dovish) tone → gold up. The press conference often moves gold more than the decision."),
    (("gdp",), "Economic growth (GDP). Stronger than forecast → dollar up → gold usually falls."),
    (("ism", "pmi"), "Business surveys (PMI). Strong numbers → dollar up → gold usually falls. Weak → gold usually rises."),
    (("retail sales",), "Consumer spending. Strong sales → dollar up → gold usually falls."),
    (("jolts", "job openings"), "Job openings. More openings → tight jobs market → Fed stays strict → gold usually falls."),
    (("consumer confidence", "consumer sentiment"), "Consumer mood. Usually a small effect on gold, unless inflation expectations inside it jump."),
    (("election",), "Elections. Uncertainty often helps gold as a safe haven; the result can move the dollar strongly."),
]


def explain_event(title):
    t = title.lower()
    return next((txt for keys, txt in EVENT_RULES if any(k in t for k in keys)), "Big US event: expect fast moves and wider spreads around the release.")


def economy_lines(macro, news, start_utc, hours, max_events=3):
    """What moves gold right now: dollar, bond yields, and the big events in the window, explained plainly."""
    out = []
    d, y = macro.get("dxy") or {}, macro.get("us10y") or {}
    if d.get("last") is not None:
        dir_d = "up" if d.get("chg_pct", 0) > 0.05 else "down" if d.get("chg_pct", 0) < -0.05 else "flat"
        out.append(f"US dollar {d['last']} ({d.get('chg_pct', 0):+.2f}% today, {d.get('chg_5d_pct', 0):+.2f}% this week): "
                   + ("a stronger dollar usually pushes gold down." if dir_d == "up" else "a weaker dollar usually helps gold." if dir_d == "down"
                      else "little pressure on gold today."))
    if y.get("last") is not None:
        dir_y = "up" if y.get("chg_bp", 0) > 2 else "down" if y.get("chg_bp", 0) < -2 else "flat"
        out.append(f"US 10-year yield {y['last']:.2f}% ({y.get('chg_bp', 0):+.0f} bp today): "
                   + ("higher yields make gold, which pays no interest, less attractive." if dir_y == "up" else
                      "falling yields usually support gold." if dir_y == "down" else "steady, no big push either way."))
    if macro.get("score") is not None and macro.get("gold_chg_pct") is not None:
        g = macro["gold_chg_pct"]
        if (macro["score"] > 0 and g < -0.3) or (macro["score"] < 0 and g > 0.3):
            out.append("Gold is moving against the dollar and yields today: that move is driven by something else (flows, safe-haven demand) and can reverse.")
    for t, title in news_in(news, start_utc, hours)[:max_events]:
        out.append(f"{title} at {local(t.timestamp())}: {explain_event(title)}")
    return out


# ---------- the facts every message uses ----------

def direction(ict, lv, price):
    """Same score as the website: D 25, 4H 25, 1H 20, 15m 10, VWAP side 10, vs yesterday's close 10."""
    tf = ict.get("timeframes") or {}
    b = lambda k: 1 if (tf.get(k) or {}).get("bias") == "bull" else -1 if (tf.get(k) or {}).get("bias") == "bear" else 0
    lad = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    vw, pc = lad.get("VWAP"), lad.get("Prev day close")
    score = 25 * b("D") + 25 * b("4H") + 20 * b("1H") + 10 * b("15m") + (10 * np.sign(price - vw) if vw else 0) + (10 * np.sign(price - pc) if pc else 0)
    word = "Up" if score >= 50 else "Leaning up" if score >= 20 else "Sideways" if score > -20 else "Leaning down" if score > -50 else "Down"
    return int(score), word, {k: b(k) for k in ("D", "4H", "1H")}


def breakout_lines(df):
    """The trend model's trigger: a 4H close above the highest high / below the lowest low of the previous 30
    completed 4H candles. Returns (upper, lower, next 4H close time, ATR of 4H)."""
    d4 = resample(df, "4H")
    done = d4.iloc[:-1]                      # the last 4H candle is still forming
    upper, lower = float(done["High"].tail(30).max()), float(done["Low"].tail(30).min())
    next_close = d4.index[-1] + pd.Timedelta(hours=4)
    return upper, lower, next_close, float(atr(d4).iloc[-2])


def zones_near(conf, price):
    zs = [z for z in conf.get("zones", []) if z.get("rating") in ("A", "B")]
    res = sorted([z for z in zs if z["low"] > price], key=lambda z: z["low"])[:2]
    sup = sorted([z for z in zs if z["high"] < price], key=lambda z: -z["high"])[:2]
    ins = next((z for z in zs if z["low"] <= price <= z["high"]), None)
    return res, sup, ins


def news_in(news, start, hours):
    out = []
    for e in news.get("events", []):
        t = datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        if e.get("impact") == "High" and start <= t <= start + timedelta(hours=hours):
            out.append((t, e["title"]))
    return out


# ---------- intraday map: the nearest areas where buyers/sellers usually show up today ----------
INTRA_LEVELS = ("Prev day high", "Prev day low", "Prev VAH", "Prev VAL")   # fixed for the whole day
NAMES = {"Prev day high": "yesterday's high", "Prev day low": "yesterday's low", "Prev VAH": "yesterday's value high",
         "Prev VAL": "yesterday's value low", "Asia high": "Asia high", "Asia low": "Asia low", "A zone": "strong zone"}
KW = {"Up": "ឡើង", "Leaning up": "ទំនោរឡើង", "Sideways": "ចំហៀង", "Leaning down": "ទំនោរចុះ", "Down": "ចុះ"}
INTRADAY_ALERTS = os.environ.get("INTRADAY_ALERTS", "off") == "on"   # 🟠 push alerts: off by default (too noisy)
INTRA_MAX_PCT = 0.009          # look up to 0.9% away (about $35)
NEAR_PCT = 0.0012              # "getting close" alert at 0.12% (about $5)
INVAL_PCT = 0.0025             # the idea is wrong 0.25% (about $10) beyond the area
# 2-year spot study (session.py docstring): sessions' highs/lows held ~44-62% of the time without a trend edge.
HISTORY_NOTE = "Levels like this held about half the time over 2 years of data, so this is a place to watch, not a trade on its own."


def intraday_areas(lv, conf, price):
    """Nearest SELL area above and BUY area below: named day levels plus A/B zones, merged when within $3."""
    fixed = INTRA_LEVELS + (("Asia high", "Asia low") if 1 <= datetime.now(NY).hour < 17 else ())   # Asia range is final after 01:00 NY
    pts = [(x["price"], x["price"], x["name"]) for x in lv.get("ladder", []) if x["name"] in fixed]
    pts += [(z["low"], z["high"], "A zone") for z in conf.get("zones", []) if z.get("rating") == "A" and z["high"] - z["low"] <= 6]
    out = {}
    for side, sel in (("SELL", [p for p in pts if price < p[0] <= price * (1 + INTRA_MAX_PCT)]),
                      ("BUY", [p for p in pts if price * (1 - INTRA_MAX_PCT) <= p[1] < price])):
        if not sel:
            continue
        near = (lambda p: p[0]) if side == "SELL" else (lambda p: -p[1])
        sel.sort(key=near)
        lo, hi = sel[0][0], sel[0][1]
        grp = [sel[0]]
        lo0, hi0 = lo, hi
        for p in sel[1:]:                                          # merge only levels within $3 of the nearest one
            if p[0] <= hi0 + 3 and p[1] >= lo0 - 3:
                grp.append(p); lo, hi = min(lo, p[0]), max(hi, p[1])
        names = list(dict.fromkeys(NAMES.get(n, n) for _, _, n in grp))
        edge = lo if side == "SELL" else hi                       # where price arrives first
        inval = hi * (1 + INVAL_PCT) if side == "SELL" else lo * (1 - INVAL_PCT)
        vw = next((x["price"] for x in lv.get("ladder", []) if x["name"] == "VWAP"), None)
        tgt = vw if vw and ((side == "SELL" and vw < edge - 5) or (side == "BUY" and vw > edge + 5)) else \
            edge - 2 * abs(inval - edge) if side == "SELL" else edge + 2 * abs(inval - edge)
        out[side] = {"side": side, "lo": round(lo, 2), "hi": round(hi, 2), "edge": round(edge, 2), "names": names,
                     "inval": round(inval, 2), "target": round(tgt, 2), "target_name": "VWAP" if tgt == vw else "2x the risk",
                     "dist": round(abs(edge - price), 1), "strength": len(names)}
    return out


def area_line(a):
    rng = fmt(a["lo"]) if a["hi"] - a["lo"] < 0.5 else f"{fmt(a['lo'])}–{fmt(a['hi'])}"
    s = a["side"] == "SELL"
    return (f"{'🔴 SELL' if s else '🟢 BUY'} area <b>{rng}</b> ({a['dist']:,.1f} {'above' if s else 'below'}) · {esc(', '.join(a['names']))}\n"
            f"   Works if price pokes {'above' if s else 'below'} it and a 15m candle closes back {'below' if s else 'above'}. "
            f"Wrong if price holds {'above' if s else 'below'} <b>{fmt(a['inval'])}</b>. First target {fmt(a['target'])} ({a['target_name']}).")


def _trend_word(b, side):
    agree = sum(1 for k in ("4H", "1H") if b[k] == (1 if side == "BUY" else -1))
    against = sum(1 for k in ("4H", "1H") if b[k] == (-1 if side == "BUY" else 1))
    return ("with the 4H and 1H trend (better odds)" if agree == 2 else "against the 4H and 1H trend (weaker, quick target only)"
            if against == 2 else "the 4H and 1H trends are mixed")


def intraday_alerts(df, lv, conf, ict, state, news):
    """'Getting close' alerts for today's areas, then a follow-up reply: held (reached target) or broke (closed beyond)."""
    price = float(df["Close"].iloc[-1])
    hi5, lo5 = float(df["High"].iloc[-1]), float(df["Low"].iloc[-1])
    d15 = resample(df, "15m")
    c15 = float(d15["Close"].iloc[-2]) if len(d15) > 2 else price     # last completed 15m close
    st = state.setdefault("intraday", {})
    tally = state.setdefault("intraday_tally", {"held": 0, "broke": 0})
    now = time.time()
    # 1) follow up on areas already alerted
    for k, a in list(st.items()):
        if a.get("status") != "watching":
            continue
        if not INTRADAY_ALERTS:          # alerts switched off: close quietly, no more messages
            a["status"] = "expired"
            continue
        s = a["side"] == "SELL"
        res = None
        h_, l_ = hi5, lo5
        since = df[df.index >= pd.Timestamp(a["t"] - 300, unit="s", tz="UTC")]
        if len(since):
            if not a.get("touched"):
                hit = since[since["High"] >= a["edge"]] if s else since[since["Low"] <= a["edge"]]
                if len(hit):
                    a["touched"], a["touch_t"] = True, hit.index[0].timestamp()
            if a.get("touched"):
                after = since[since.index >= pd.Timestamp(a.get("touch_t", a["t"]), unit="s", tz="UTC")]
                h_ = float(after["High"].max()) if len(after) else hi5
                l_ = float(after["Low"].min()) if len(after) else lo5
        if (s and c15 > a["inval"]) or (not s and c15 < a["inval"]):
            res = ("broke", f"❌ <b>{a['side']} area broke</b> at {fmt(price)}: a 15m candle closed {'above' if s else 'below'} "
                            f"{fmt(a['inval'])}. A {'sell' if s else 'buy'} from the area would be stopped out. The move {'up' if s else 'down'} may continue.")
        elif a.get("touched") and ((s and l_ <= a["target"]) or (not s and h_ >= a["target"])):
            res = ("held", f"✅ <b>{a['side']} area held</b>: price reached the first target {fmt(a['target'])} from the area.")
        elif now - a["t"] > 8 * 3600:
            res = ("expired", None)
        if res:
            a["status"] = res[0]
            if res[0] in tally:
                tally[res[0]] += 1
                alog = jl("areas_log.json", [])
                alog.append({"side": a["side"], "lo": a["lo"], "hi": a["hi"], "names": a["names"], "inval": a["inval"],
                             "target": a["target"], "alerted": a["t"], "closed": now, "result": res[0]})
                json.dump(alog[-300:], open("areas_log.json", "w"), indent=1)
                t = tally["held"] + tally["broke"]
                msg = res[1] + f"\n<i>Live record of these areas: {tally['held']} held, {tally['broke']} broke ({t} total).</i>"
                send(msg, f"Area {res[0]}", reply_to=a.get("msg_id"))
    # 2) new "getting close" alerts
    if not INTRADAY_ALERTS or now - state.get("intraday_last", 0) < 20 * 60:
        return
    score, word, b = direction(ict, lv, price)
    day = datetime.now(NY).strftime("%Y-%m-%d")
    ev = [x for x in news_in(news, datetime.now(timezone.utc), 1)]
    for side, a in intraday_areas(lv, conf, price).items():
        key = f"{day}|{side}|{round(a['edge'])}"
        if key in st or a["dist"] > price * NEAR_PCT:
            continue
        strong = a["strength"] >= 2 or "strong zone" in a["names"]           # several levels agree, or a top-rated zone
        if not strong or "against" in _trend_word(b, side):                # essential only: skip weak or counter-trend areas
            continue
        s = side == "SELL"
        risk = abs(a["inval"] - a["edge"])
        risks = [f"Might stop out if price keeps pushing {'up' if s else 'down'}: a 15m close {'above' if s else 'below'} {fmt(a['inval'])} "
                 f"means a breakout, not a reversal (about {risk:,.0f} points of risk)."]
        if ev:
            risks.append(f"News within the hour ({esc(ev[0][1])}): levels often break on news.")
        en = [f"🟠 <b>Getting close to a {side} area</b> · gold {fmt(price)}",
              area_line(a),
              f"Trend: {_trend_word(b, side)}.",
              "", "<b>What would confirm it</b>",
              f"• Price spikes {'above' if s else 'below'} the area, then a 15m candle closes back {'below' if s else 'above'} {fmt(a['edge'])}.",
              "• Even better: the 5m chart shifts direction (a CISD) and leaves a gap (FVG) to retest.",
              "", "<b>⚠️ Risk</b>", *[f"• {x}" for x in risks],
              "", f"<i>{HISTORY_NOTE} Wait for the confirmation, risk 0.5–1% only. Not a signal.</i>"]
        km = [f"🟠 <b>ជិតដល់តំបន់{'លក់' if s else 'ទិញ'}</b> · មាស {fmt(price)}",
              f"តំបន់ {fmt(a['lo'])}–{fmt(a['hi'])} · ខុស បើបិទ{'លើ' if s else 'ក្រោម'} {fmt(a['inval'])}",
              f"រង់ចាំទៀន 15m បិទត្រឡប់{'ក្រោម' if s else 'លើ'} {fmt(a['edge'])} សិន។ មិនមែនសញ្ញាទេ។"]
        msg = "\n".join(km) if LANG == "km" else "\n".join(en) + ("\n\n" + "\n".join(km) if LANG == "both" else "")
        mid = send(msg, f"Near {side} area")
        if mid or not os.environ.get("TELEGRAM_TOKEN"):
            st[key] = {**a, "t": now, "status": "watching", "msg_id": mid if isinstance(mid, int) else None,
                       "touched": (s and hi5 >= a["edge"]) or (not s and lo5 <= a["edge"])}
            state["intraday_last"] = now
            print("intraday alert", key)
            break                                    # one at a time
    state["intraday"] = {k: v for k, v in st.items() if now - v["t"] < 3 * 86400}


# ---------- chart image ----------

def _trendlines(d1):
    """Lines through the last two confirmed 1H swing highs and the last two swing lows (what a trader would draw)."""
    from ict import swings
    sw = swings(d1)
    hs = [(idx, p) for _, idx, k, p in sw if k == "H"][-2:]
    ls = [(idx, p) for _, idx, k, p in sw if k == "L"][-2:]
    return [(pts, kind) for pts, kind in ((hs, "res"), (ls, "sup")) if len(pts) == 2 and pts[1][0] - pts[0][0] >= 3]


def chart(df, conf, lv, lines, path, title, position=None, scenarios=True):
    """1H chart for Telegram. position: dict(dir, entry, stop, tp1, tp2) draws the live trade like TradingView's
    position tool. scenarios: draws the planned BUY and SELL positions at the trend model's trigger lines."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    d1 = resample(df, "1H").tail(72)
    upper, lower, next_close, _ = lines
    BG, CARD, INK, MUT, UP, DN, GOLD, BLUE = "#000000", "#1C1C1E", "#F5F5F7", "#8E8E93", "#30D158", "#FF453A", "#E3B04B", "#0A84FF"
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD)
    N = len(d1)
    RIGHT = 16                                   # room on the right for the plan boxes
    price = float(df["Close"].iloc[-1])
    lo_y, hi_y = float(d1["Low"].min()), float(d1["High"].max())
    pad = (hi_y - lo_y) * 0.08
    view_lo, view_hi = lo_y - pad, hi_y + pad

    def plan_box(x0, x1, en, st, t1, t2, sg, label, alpha=1.0):
        """green = profit area to TP2, red = risk to the stop, dashed TP1 line."""
        ax.add_patch(Rectangle((x0, min(en, t2)), x1 - x0, abs(t2 - en), color=UP, alpha=0.16 * alpha, lw=0))
        ax.add_patch(Rectangle((x0, min(en, st)), x1 - x0, abs(en - st), color=DN, alpha=0.22 * alpha, lw=0))
        for y, col, txt, ls in ((en, INK, f"{label} entry {en:,.2f}", "-"), (st, DN, f"SL {st:,.2f}", "-"),
                                (t1, UP, f"TP1 {t1:,.2f} (close half)", "--"), (t2, UP, f"TP2 {t2:,.2f}", "-")):
            ax.plot([x0, x1], [y, y], color=col, lw=1.1, ls=ls, alpha=alpha)
            ax.text(x1 + 0.2, y, txt, color=col, va="center", fontsize=7.5, fontweight="bold", alpha=alpha)

    # zones
    for z in conf.get("zones", []):
        if z.get("rating") in ("A", "B") and z["high"] > view_lo - pad and z["low"] < view_hi + pad:
            col = DN if z["low"] > price else UP if z["high"] < price else GOLD
            ax.axhspan(z["low"], z["high"], xmax=N / (N + RIGHT + 12), color=col, alpha=0.12 if z["rating"] == "A" else 0.06, lw=0)
    # key levels
    lad = {k["name"]: k["price"] for k in lv.get("ladder", [])}
    for name in ("Prev day high", "Prev day low", "Asia high", "Asia low"):
        p = lad.get(name)
        if p and view_lo < p < view_hi:
            ax.plot([0, N], [p, p], color=MUT, lw=0.8, ls=(0, (2, 3)))
            ax.text(N - 0.5, p, f"{name} {p:,.2f} ", color=MUT, va="bottom", ha="right", fontsize=7.5)
    tls = _trendlines(d1)
    # candles
    for i, r in enumerate(d1.itertuples()):
        col = UP if r.Close >= r.Open else DN
        ax.vlines(i, r.Low, r.High, color=col, lw=0.9)
        ax.add_patch(Rectangle((i - 0.32, min(r.Open, r.Close)), 0.64, max(abs(r.Close - r.Open), 0.05), color=col, lw=0))
    # trigger lines and planned positions
    risk = lambda en: en * 0.0065
    if position:
        sg = 1 if position["dir"] == "bull" else -1
        en, st = position["entry"], position["stop"]
        t1, t2 = position.get("tp1") or en + sg * 0.75 * abs(en - st), position["tp2"]
        view_lo, view_hi = min(view_lo, st, t2, en) - pad / 3, max(view_hi, st, t2, en) + pad / 3
        plan_box(N - 1, N + RIGHT - 6, en, st, t1, t2, sg, "BUY" if sg > 0 else "SELL")
    elif scenarios:
        for lvl, sg, lab, col in ((upper, 1, "BUY", UP), (lower, -1, "SELL", DN)):
            if abs(lvl - price) > price * 0.03:
                continue                          # too far away to matter this session
            st, t1, t2 = lvl - sg * risk(lvl), lvl + sg * 0.75 * risk(lvl), lvl + sg * 3 * risk(lvl)
            view_lo, view_hi = min(view_lo, st, lvl, t2) - pad / 3, max(view_hi, st, lvl, t2) + pad / 3
            ax.plot([0, N + RIGHT - 6], [lvl, lvl], color=col, lw=1.3, ls="--")
            ax.text(0.5, lvl, f" {lab} line: a 4H close {'above' if sg > 0 else 'below'} {lvl:,.2f} triggers the signal",
                    color=col, va="bottom" if sg > 0 else "top", fontsize=8.5, fontweight="bold")
            plan_box(N + 1, N + RIGHT - 6, lvl, st, t1, t2, sg, f"if {lab}", alpha=0.75)
    # trendlines through the last two swings, extended until they leave the view
    for (p1, p2), kind in tls:
        (i1, y1), (i2, y2) = p1, p2
        slope = (y2 - y1) / (i2 - i1)
        col = DN if kind == "res" else UP
        xs = np.linspace(i1, N + 2, 200)
        ys = y1 + slope * (xs - i1)
        keep = (ys >= view_lo) & (ys <= view_hi)
        if keep.sum() < 2:
            continue
        ax.plot(xs[keep], ys[keep], color=col, lw=1.6, alpha=0.9)
        ax.scatter([i1, i2], [y1, y2], color=col, s=18, zorder=5)
        xl, yl = xs[keep][-1], ys[keep][-1]
        ax.text(xl, yl, " resistance trendline" if kind == "res" else " support trendline", color=col, fontsize=7.5,
                va="bottom" if kind == "res" else "top", clip_on=True)
    # last price
    ax.plot([0, N + RIGHT - 6], [price, price], color=INK, lw=0.8, alpha=0.5)
    ax.text(N - 1, price, f" {price:,.2f} ", color=BG, va="center", ha="right", fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=INK, ec="none"))
    ax.set_xlim(-1, N + RIGHT + 8)
    ax.set_ylim(view_lo, view_hi)
    ticks = list(range(0, N, 12))
    ax.set_xticks(ticks, [d1.index[i].tz_convert(local_tz()).strftime("%a %H:%M") for i in ticks], color=MUT, fontsize=8)
    ax.tick_params(axis="y", colors=MUT, labelsize=8)
    ax.yaxis.tick_right()
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(axis="y", color="#2C2C2E", lw=0.6)
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold", loc="left", pad=10)
    fig.text(0.01, 0.01, "XAU.KH · 1H spot XAUUSD · red/green boxes = stop / profit area · dashed = TP1 (close half, stop to entry)"
             " · plans are rules, not promises", color=MUT, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def local_tz():
    return ZoneInfo(os.environ.get("DISPLAY_TZ", "Asia/Phnom_Penh"))


# ---------- messages ----------

def briefing_text(name, ict, conf, lv, news, df, lines, start_utc, macro=None):
    """Short and scannable: direction, one SELL area, one BUY area, the big signal lines, at most 2 risks, 1 macro line."""
    price = float(df["Close"].iloc[-1])
    score, word, b = direction(ict, lv, price)
    upper, lower, next_close, _ = lines
    areas = intraday_areas(lv, conf, price)
    ev = news_in(news, start_utc, 6)
    vol = float(atr(df).iloc[-1] / atr(df).rolling(288 * 20, min_periods=288).median().iloc[-1])
    arrow = "↑" if score >= 20 else "↓" if score <= -20 else "↔"
    head = {"Asia": "🌏", "London": "🇬🇧", "New York": "🇺🇸"}[name]
    plan = []
    for k in ("SELL", "BUY"):
        if k in areas:
            x = areas[k]
            plan.append(f"{'🔴 Sell លក់' if k == 'SELL' else '🟢 Buy ទិញ'} near <b>{fmt(x['edge'])}</b> ({esc(x['names'][0])})\n"
                        f"    wrong if {'above' if k == 'SELL' else 'below'} {fmt(x['inval'])} · ខុស បើ{'ឡើងលើ' if k == 'SELL' else 'ធ្លាក់ក្រោម'}")
    risks = []
    if ev:
        risks.append(f"📰 {esc(ev[0][1])} at {local(ev[0][0].timestamp())}: fast moves, wider spreads")
    if vol >= 1.3:
        risks.append(f"Market is {vol:.1f}x more volatile than normal: use a smaller lot")
    if abs(score) < 20 and len(risks) < 2:
        risks.append("No clear direction: don't force trades")
    eco = economy_lines(macro or {}, {}, start_utc, 0)[:1]
    en = [f"{head} <b>{name.upper()} SESSION · សម័យ{KM_SESSION[name]}</b>", f"Gold · មាស <b>{fmt(price)}</b>",
          f"Direction · ទិសដៅ: <b>{word} {arrow}</b> ({KW[word]})",
          "", "<b>🎯 Plan · ផែនការ</b>", *plan,
          "<i>Enter only after a 15m candle closes back away from the level.\nចូលតែក្រោយទៀន 15m បិទត្រឡប់មកវិញ។</i>",
          "", f"⚡ <b>Big signal · សញ្ញាធំ</b>\n4H close above {fmt(upper)} = BUY ទិញ\n4H close below {fmt(lower)} = SELL លក់",
          *(["", "<b>⚠️ Risk · ហានិភ័យ</b>", *risks] if risks else []),
          *(["", f"🏛 {esc(eco[0])}"] if eco else [])]
    if LANG in ("km", "both"):
        kw = {"Up": "ឡើង", "Leaning up": "ទំនោរឡើង", "Sideways": "ចំហៀង", "Leaning down": "ទំនោរចុះ", "Down": "ចុះ"}[word]
        km = [f"{head} <b>សម័យ {KM_SESSION[name]}</b> · មាស <b>{fmt(price)}</b>", f"ទិសដៅ: <b>{kw} {arrow}</b>",
              *[f"{'🔴 លក់' if k == 'SELL' else '🟢 ទិញ'} ជិត <b>{fmt(areas[k]['edge'])}</b> · ខុស បើ{'លើ' if k == 'SELL' else 'ក្រោម'} {fmt(areas[k]['inval'])}"
                for k in ("SELL", "BUY") if k in areas],
              f"⚡ 4H បិទលើ {fmt(upper)} = ទិញ · ក្រោម {fmt(lower)} = លក់",
              *([f"⚠️ {esc(ev[0][1])} ម៉ោង {local(ev[0][0].timestamp())}"] if ev else [])]
        en = km if LANG == "km" else en + ["", *km]
    return "\n".join(en)


def heads_up(df, lines, state):
    price = float(df["Close"].iloc[-1])
    upper, lower, next_close, _ = lines
    day = datetime.now(NY).strftime("%Y-%m-%d")
    sent = state.setdefault("heads_up", {})
    for side, level in (("BUY", upper), ("SELL", lower)):
        dist = (level - price) if side == "BUY" else (price - level)
        key = f"{day}|{side}|{level:.2f}"
        if 0 < dist <= price * HEADS_UP_PCT and key not in sent:
            en = (f"⚡ <b>Heads up · possible {side} · ត្រៀម{'ទិញ' if side == 'BUY' else 'លក់'}</b>\nGold {fmt(price)} is <b>{dist:,.1f} points</b> from the week's "
                  f"{'high' if side == 'BUY' else 'low'} <b>{fmt(level)}</b>.\nIf the 4H candle closing at <b>{local(next_close.timestamp())}</b> "
                  f"finishes {'above' if side == 'BUY' else 'below'} it, the bot sends a {side} signal.\n"
                  f"<i>Get ready, don't enter yet. Breakouts sometimes fail: wait for the close.\nត្រៀមខ្លួន តែកុំទាន់ចូល។ ចាំទៀនបិទសិន។</i>")
            km = (f"⚡ <b>ត្រៀមខ្លួន · អាច{'ទិញ' if side == 'BUY' else 'លក់'}</b>\nមាសនៅឆ្ងាយ {dist:,.1f} ពី {fmt(level)}។ "
                  f"បើ 4H បិទ{'លើ' if side == 'BUY' else 'ក្រោម'}វានៅម៉ោង {local(next_close.timestamp())} បូតនឹងផ្ញើសញ្ញា។")
            msg = km if LANG == "km" else en + ("\n\n" + km if LANG == "both" else "")
            if send(msg, f"Heads up {side}"):
                sent[key] = time.time()
                print("heads-up sent", key)
    state["heads_up"] = {k: v for k, v in sent.items() if time.time() - v < 3 * 86400}


PULSE_HOURS_NY = {3, 4, 9, 10, 11, 12}      # on the hour during London (02-05) and New York (08-12), between the preps


def pulse_text(ict, conf, lv, news, df, lines, macro):
    price = float(df["Close"].iloc[-1])
    hour_ago = float(df["Close"].iloc[-13]) if len(df) > 13 else price
    score, word, b = direction(ict, lv, price)
    areas = intraday_areas(lv, conf, price)
    nx = sorted([(datetime.fromisoformat(e["time"].replace("Z", "+00:00")), e["title"]) for e in news.get("events", [])
                 if e.get("impact") == "High" and datetime.fromisoformat(e["time"].replace("Z", "+00:00")) > datetime.now(timezone.utc)])[:1]
    arrow = "↑" if score >= 20 else "↓" if score <= -20 else "↔"
    lines_en = [f"⏱ <b>GOLD · មាស {fmt(price)}</b> ({price - hour_ago:+,.1f} in 1h) · {local(time.time())}",
                f"Direction · ទិសដៅ: <b>{word} {arrow}</b> ({KW[word]})",
                *[f"{'🔴 Sell លក់' if k == 'SELL' else '🟢 Buy ទិញ'} near <b>{fmt(areas[k]['edge'])}</b> · wrong if "
                  f"{'above' if k == 'SELL' else 'below'} {fmt(areas[k]['inval'])}" for k in ("SELL", "BUY") if k in areas],
                *([f"📰 Next news · ព័ត៌មានបន្ទាប់: {esc(nx[0][1])} at {local(nx[0][0].timestamp())}"] if nx else [])]
    if LANG in ("km", "both"):
        kw = {"Up": "ឡើង", "Leaning up": "ទំនោរឡើង", "Sideways": "ចំហៀង", "Leaning down": "ទំនោរចុះ", "Down": "ចុះ"}[word]
        km = [f"⏱ <b>មាស {fmt(price)}</b> ({price - hour_ago:+,.1f} ក្នុង 1 ម៉ោង)", f"ទិសដៅ: <b>{kw} {arrow}</b>"]
        lines_en = km if LANG == "km" else lines_en + ["", *km]
    return "\n".join(x for x in lines_en if x)


def pulse_worth(state, ict, lv, df, lines):
    """Send the hourly pulse only when it tells something new: direction changed, a big move, or a line is close."""
    price = float(df["Close"].iloc[-1])
    _, word, _ = direction(ict, lv, price)
    last = state.get("pulse_last") or {}
    state["pulse_last"] = {"word": word, "price": price}
    hour_ago = float(df["Close"].iloc[-13]) if len(df) > 13 else price
    upper, lower = lines[0], lines[1]
    if last.get("word") and last["word"] != word:
        return f"direction changed to {word}"
    if abs(price - hour_ago) >= price * 0.004:
        return "big move in the last hour"
    if min(upper - price, price - lower) <= price * 0.004:
        return "near a 4H signal line"
    if not last:
        return "first pulse"
    return None


def due_pulse(state, now_utc):
    now_ny = now_utc.astimezone(NY)
    if now_ny.weekday() > 4 or now_ny.hour not in PULSE_HOURS_NY or now_ny.minute >= 10:
        return None
    key = now_ny.strftime("%Y-%m-%d %H")
    return None if key in state.get("pulsed", {}) else key


def due_session(state, now_utc):
    now_ny = now_utc.astimezone(NY)
    for name, hh, mm, days in SESSIONS:
        if now_ny.weekday() not in days:
            continue
        at = now_ny.replace(hour=hh, minute=mm, second=0, microsecond=0)
        key = f"{at:%Y-%m-%d}|{name}"
        if at <= now_ny < at + timedelta(minutes=25) and key not in state.get("briefed", {}):
            start = at + timedelta(minutes=30)
            return name, key, start.astimezone(timezone.utc)
    return None


def weekly_report(df, log, alog, bt, week_start):
    """Friday proof report: every real signal of the week with its result, the live record vs the backtest, area results."""
    ws = week_start.timestamp()
    price = float(df["Close"].iloc[-1])
    wk = df[df.index >= week_start]
    w_open = float(wk["Open"].iloc[0]) if len(wk) else price
    models = [a for a in log if a.get("kind") == "model"]
    week = [a for a in models if a.get("created", 0) >= ws]
    done = [a for a in models if a.get("status") in ("win", "tp1", "loss", "timed out")]
    RES = {"win": "✅ TP2 reached", "tp1": "✅ TP1, rest at entry", "loss": "❌ stop hit", "timed out": "⏱ closed after time limit",
           "filled": "⏳ still open", "pending": "⏳ waiting"}
    out = [f"📊 <b>WEEKLY PROOF · លទ្ធផលប្រចាំសប្តាហ៍ · week of {week_start.astimezone(local_tz()):%d %b}</b>",
           f"Gold {fmt(w_open)} → {fmt(price)} ({price - w_open:+,.1f} this week)", "", "<b>Real BUY/SELL signals this week · សញ្ញាពិតសប្តាហ៍នេះ</b>"]
    if week:
        for a in week:
            r = f" ({a['R']:+.2f}R)" if a.get("R") is not None else ""
            out.append(f"• {local(a['created'])} {datetime.fromtimestamp(a['created'], local_tz()):%a} "
                       f"{'BUY' if a['dir'] == 'bull' else 'SELL'} {fmt(a['entry'])}: {RES.get(a['status'], a['status'])}{r}")
        wR = [a["R"] for a in week if a.get("R") is not None]
        if wR:
            out.append(f"Week total: <b>{sum(wR):+.2f}R</b> from {len(wR)} closed trade(s).")
    else:
        out.append("• None. No clean 4H breakout this week, so the bot stayed out. No signal is better than a bad one.")
    m = (bt.get("models") or {}).get("trend_tight", {}).get("all") or {}
    out += ["", "<b>Live record since launch · កំណត់ត្រាពិតទាំងអស់</b>"]
    if done:
        R = [a["R"] for a in done]
        out.append(f"{len(done)} closed · {sum(r > 0 for r in R)} won · {round(100 * sum(r > 0 for r in R) / len(R))}% · "
                   f"{sum(R):+.2f}R total ({sum(R) / len(R):+.2f}R per trade)")
    else:
        out.append("No closed signals yet.")
    if m:
        out.append(f"Backtest for comparison: {m.get('trades')} trades, {m.get('win_rate_pct')}% won, {m.get('avg_R', 0):+.2f}R per trade.")
    aw = [x for x in alog if x.get("closed", 0) >= ws]
    if aw:
        h = sum(x["result"] == "held" for x in aw)
        out += ["", f"<b>🟠 Watch areas this week</b>: {h} held, {len(aw) - h} broke."]
        if alog:
            H = sum(x["result"] == "held" for x in alog)
            out.append(f"All time: {H} of {len(alog)} held ({round(100 * H / len(alog))}%).")
    out += ["", "<i>R = profit measured in risk units: +1R means you made what you risked. "
                "1 week is a small sample; judge the record over months.</i>"]
    if LANG in ("km", "both"):
        km = [f"📊 <b>លទ្ធផលប្រចាំសប្តាហ៍</b>", f"សញ្ញាពិតសប្តាហ៍នេះ: {len(week)}",
              (f"កំណត់ត្រាផ្ទាល់: {len(done)} ការជួញដូរ, {sum(a['R'] for a in done):+.2f}R" if done else "មិនទាន់មានការជួញដូរបិទ")]
        out = km if LANG == "km" else out + ["", *km]
    return "\n".join(out)


def site_file(df, lv, conf, ict, news, macro, state):
    """intraday.json for the website: today's areas, what moves gold, area record."""
    price = float(df["Close"].iloc[-1])
    _, word, b = direction(ict, lv, price)
    areas = intraday_areas(lv, conf, price)
    for k, a in areas.items():
        a["trend"] = _trend_word(b, k)
        a["strong"] = a["strength"] >= 2 or "strong zone" in a["names"]
    alog = jl("areas_log.json", [])
    json.dump({"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "price": round(price, 2), "direction": word,
               "areas": areas, "economy": economy_lines(macro, news, datetime.now(timezone.utc), 24, 4),
               "area_record": {"held": sum(x["result"] == "held" for x in alog), "broke": sum(x["result"] == "broke" for x in alog)},
               "area_recent": alog[-10:][::-1], "history_note": HISTORY_NOTE}, open("intraday.json", "w"), indent=1)


def main():
    state = jl(STATE)
    ict, conf, lv, news, macro = jl("ict.json"), jl("confluence.json"), jl("levels.json"), jl("news.json"), jl("macro.json")
    df = to_ny(load("5m", "20d"))
    df = df[df["Volume"] >= 0].iloc[:-1]
    if (time.time() - df.index[-1].timestamp()) / 60 > 40 and not os.environ.get("XAU_SIM"):
        print("session: data is stale, nothing sent"); return
    lines = breakout_lines(df)
    heads_up(df, lines, state)
    try:
        intraday_alerts(df, lv, conf, ict, state, news)
    except Exception as e:
        print("intraday alerts failed:", e)
    due = due_session(state, datetime.now(timezone.utc)) if not os.environ.get("SESSION_FORCE") else \
        (os.environ["SESSION_FORCE"], "forced|" + os.environ["SESSION_FORCE"], datetime.now(timezone.utc))
    if due:
        name, key, start = due
        text = briefing_text(name, ict, conf, lv, news, df, lines, start, macro)
        path = "session_chart.png"
        chart(df, conf, lv, lines, path, f"Gold · {name} session prep · {local(time.time())}")
        if len(text) <= 1024:
            mid = send_photo(path, text, f"{name} session")
        else:   # Telegram captions are limited: photo with the headline, then the full briefing as a reply
            mid = send_photo(path, text.split("\n\n")[0], f"{name} session")
            if mid:
                send(text, f"{name} session", reply_to=mid)
        if mid or not os.environ.get("TELEGRAM_TOKEN"):
            state.setdefault("briefed", {})[key] = time.time()
            state["briefed"] = {k: v for k, v in state["briefed"].items() if time.time() - v < 7 * 86400}
        print("session briefing:", name)
    pk = due_pulse(state, datetime.now(timezone.utc)) if not due else None
    if pk:
        why = pulse_worth(state, ict, lv, df, lines)
        if not why:
            state.setdefault("pulsed", {})[pk] = time.time()
            print("pulse skipped: nothing new")
        elif send(pulse_text(ict, conf, lv, news, df, lines, macro).replace("\n", f"\n🔔 {why[0].upper() + why[1:]}\n", 1), "Gold pulse") or not os.environ.get("TELEGRAM_TOKEN"):
            state.setdefault("pulsed", {})[pk] = time.time()
            state["pulsed"] = {k: v for k, v in state["pulsed"].items() if time.time() - v < 3 * 86400}
            print("pulse sent", pk)
    try:
        site_file(df, lv, conf, ict, news, macro, state)
    except Exception as e:
        print("intraday.json failed:", e)
    now_ny = datetime.now(NY)
    wkey = now_ny.strftime("%G-W%V")
    if (now_ny.weekday() == 4 and now_ny.hour == 16 and now_ny.minute >= 30 and wkey not in state.get("weekly_report", {})) \
            or os.environ.get("WEEKLY_FORCE"):
        start = (now_ny - timedelta(days=(now_ny.weekday() + 1) % 7)).replace(hour=18, minute=0, second=0, microsecond=0)
        if start > now_ny:
            start -= timedelta(days=7)
        msg = weekly_report(df, jl("alerts_log.json", []), jl("areas_log.json", []), jl("backtest.json"), start)
        if send(msg, "Weekly proof") or not os.environ.get("TELEGRAM_TOKEN"):
            state.setdefault("weekly_report", {})[wkey] = time.time()
            print("weekly report sent")
    wk = datetime.now(NY).strftime("%G-W%V")
    if due and due[0] == "Asia" and datetime.now(NY).weekday() == 6 and wk not in state.get("weekly", {}):
        ev = [(datetime.fromisoformat(e["time"].replace("Z", "+00:00")), e["title"]) for e in news.get("events", []) if e.get("impact") == "High"]
        ev = sorted(x for x in ev if x[0] > datetime.now(timezone.utc))
        if ev:
            body = ["🏛 <b>THE WEEK FOR GOLD · big US events</b>", ""]
            for t, title in ev[:8]:
                body += [f"<b>{local(t.timestamp())} {t.astimezone(local_tz()):%a}</b> · {esc(title)}", f"   {esc(explain_event(title))}"]
            body += ["", "<i>Rules of thumb, not promises: the surprise versus the forecast matters more than the number itself.</i>"]
            if send("\n".join(body), "Week ahead"):
                state.setdefault("weekly", {})[wk] = time.time()
    json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
