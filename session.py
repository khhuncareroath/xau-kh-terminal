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
from tg import SITE, esc, fmt, local, log_alert, send, send_photo

NY = ZoneInfo("America/New_York")
LANG = os.environ.get("BOT_LANG", "en")
if LANG == "both":   # English messages already carry Khmer labels inline; no second full block
    LANG = "en"
HEADS_UP_PCT = 0.0025          # 0.25% of price, about $10 at $3,900
SESSIONS = [("Asia", 17, 30, (6, 0, 1, 2, 3)), ("London", 2, 5, (0, 1, 2, 3, 4)), ("New York", 7, 0, (0, 1, 2, 3, 4))]
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
    vx, spx = macro.get("vix") or {}, macro.get("spx") or {}
    if vx.get("last") is not None:
        mood = ("fear is high: safe-haven demand often supports gold" if vx["last"] >= 25 else
                "fear is rising: watch for safe-haven buying in gold" if vx.get("chg_pct", 0) >= 10 else
                "markets are calm: less safe-haven demand" if vx["last"] < 16 else "normal risk mood")
        out.append(f"VIX (fear index) {vx['last']} ({vx.get('chg_pct', 0):+.0f}% today) · S&P 500 {spx.get('chg_pct', 0):+.2f}%: {mood}.")
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


def pre_news(news, state):
    """One calm warning 30 minutes before high-impact USD news (events at the same minute grouped)."""
    now = datetime.now(timezone.utc)
    sent = state.setdefault("pre_news", {})
    groups = {}
    for e in news.get("events", []):
        if e.get("impact") == "High":
            t = datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
            if timedelta(minutes=20) <= t - now <= timedelta(minutes=35):
                groups.setdefault(t, []).append(e["title"])
    for t, titles in sorted(groups.items()):
        key = t.isoformat()
        if key in sent:
            continue
        msg = (f"📰 <b>In {round((t - now).total_seconds() / 60)} min ({local(t.timestamp())})</b>: {esc(', '.join(dict.fromkeys(titles)))}\n"
               f"Big moves likely. No new entries 15 min before → 15 min after.")
        if send(msg, "News soon") or not os.environ.get("TELEGRAM_TOKEN"):
            sent[key] = time.time()
            print("pre-news sent", key)
    state["pre_news"] = {k: v for k, v in sent.items() if time.time() - v < 3 * 86400}


def trend_state(df):
    """Direction of the last 4H breakout (close beyond the previous 30 4H candles): +1 up, -1 down, 0 none yet.
    Test (2 years, daily level trades): with this filter about break-even, without it -0.14R per trade."""
    d4 = resample(df, "4H").iloc[:-1]
    hi, lo = d4["High"].rolling(30).max().shift(1), d4["Low"].rolling(30).min().shift(1)
    for k in range(len(d4) - 1, 30, -1):
        if d4["Close"].iloc[k] > hi.iloc[k]:
            return 1
        if d4["Close"].iloc[k] < lo.iloc[k]:
            return -1
    return 0


def plan_entry(df, a, key, state, c15):
    """Entry in signal style when price came to the with-trend zone and a 15m candle closed back from it.
    Same rules as the one-trade-a-day test (2 years: about break-even with the 4H trend), so it is labelled as a plan
    trade with a small risk, unlike the tested 4H signal. One per trading day, 01:00-12:00 New York only.
    The result is graded by track.py and posted as a reply, like every signal."""
    s = a["side"] == "SELL"
    a["status"] = "entry checked"
    ny = datetime.now(NY)
    day = (ny - timedelta(hours=18)).strftime("%Y-%m-%d")
    if not (1 <= ny.hour < 12) or state.get("plan_day") == day or trend_state(df) != (-1 if s else 1):
        return
    since = df[df.index >= pd.Timestamp(a["touch_t"], unit="s", tz="UTC")]
    ext = float(since["High"].max()) if s else float(since["Low"].min())
    stop = max(a["inval"], ext + 0.5) if s else min(a["inval"], ext - 0.5)
    entry = c15
    risk = abs(stop - entry)
    if risk < 2:
        return
    tp = entry - 2 * risk if s else entry + 2 * risk
    pips = lambda px: f"{(px - entry) * (-1 if s else 1) * 10:+,.0f} pips"
    lvl = a.get("names", ["the level"])[0]
    msg = "\n".join([
        f"{'🔴' if s else '🟢'} <b>GOLD {'SELL' if s else 'BUY'} NOW · {'លក់' if s else 'ទិញ'}ឥឡូវ</b>  <i>(plan trade)</i>", "",
        f"Entry  <b>{fmt(entry)}</b>",
        f"SL       <b>{fmt(stop)}</b>  ({pips(stop)})",
        f"TP       <b>{fmt(tp)}</b>  ({pips(tp)})", "",
        f"Price tested {esc(lvl)} {fmt(a['edge'])} and the 15m closed back {'below' if s else 'above'} · with the 4H trend.",
        "⏰ Closes by 17:00 New York if TP/SL not hit",
        "", "<i>Plan trade, not the tested 4H signal: risk 0.5% max · ហានិភ័យ 0.5% ប៉ុណ្ណោះ</i>"])
    mid = send(msg, ("SELL" if s else "BUY") + " plan", reply_to=a.get("msg_id"))
    if not mid and os.environ.get("TELEGRAM_TOKEN"):
        return
    state["plan_day"] = day
    a["status"] = "entered"
    now = time.time()
    close_ny = ny.replace(hour=17, minute=0, second=0, microsecond=0)
    log_alert({"id": f"plan|{key}", "kind": "plan", "dir": "bear" if s else "bull", "entry": round(entry, 2), "stop": round(stop, 2),
               "target": round(tp, 2), "rr": 2.0, "created": now, "valid_until": now + 900, "price_at_alert": round(entry, 2),
               "msg_id": mid if isinstance(mid, int) else None, "status": "filled", "filled_at": now, "fill": round(entry, 2),
               "max_hold_s": max(1800, int(close_ny.timestamp() - now))})
    print("plan entry sent", key)


def near_level_alert(df, lv, conf, ict, state):
    """Calm 'price is near your level' alert: only the sell/buy levels shown in the session prep, each at most once a
    day, at most one alert an hour, nothing when the big direction is strongly against it.
    If that level then fails (a 15m candle closes past its stop line), ONE reply says what to do now: the next level
    in the same direction, or the flip (old support becomes resistance). Nothing else is sent about it."""
    price = float(df["Close"].iloc[-1])
    now = time.time()
    sent = state.setdefault("near", {})
    d15 = resample(df, "15m")
    c15 = float(d15["Close"].iloc[-2]) if len(d15) > 2 else price            # last completed 15m candle
    for key, a in sent.items():                                               # 1) did an alerted level fail?
        if not isinstance(a, dict) or a.get("status") != "watch":
            continue
        s = a["side"] == "SELL"
        if now - a["t"] > 8 * 3600:
            a["status"] = "expired"
            continue
        if not a.get("touched"):                                               # price reached the zone?
            since = df[df.index >= pd.Timestamp(a["t"] - 300, unit="s", tz="UTC")]
            hit = since[since["High"] >= a["edge"]] if s else since[since["Low"] <= a["edge"]]
            if len(hit):
                a["touched"], a["touch_t"] = True, hit.index[0].timestamp()
        done15 = d15.index[-2] + pd.Timedelta(minutes=15) if len(d15) > 2 else None
        if a.get("touched") and done15 is not None and done15.timestamp() > a["touch_t"] + 300 \
                and ((s and a["inval"] > c15 < a["edge"]) or (not s and a["inval"] < c15 > a["edge"])):
            if os.environ.get("LEVEL_PLAN") == "on":                           # old level entry (break-even in testing): off
                plan_entry(df, a, key, state, c15)
            a["status"] = "entry checked"
            continue
        if (s and c15 > a["inval"]) or (not s and c15 < a["inval"]):
            a["status"] = "failed"
            nxt = intraday_areas(lv, conf, price).get(a["side"])
            flip_stop = a["edge"] * (1 - INVAL_PCT) if s else a["edge"] * (1 + INVAL_PCT)
            msg = [f"↩️ The {'Sell' if s else 'Buy'} level {fmt(a['edge'])} didn't hold. "
                   f"<b>Don't {'sell' if s else 'buy'} here now.</b>", "Next:"]
            if nxt:
                msg.append(f"{'🔴 Sell' if s else '🟢 Buy'} at the next level <b>{fmt(nxt['edge'])}</b> · stop {'above' if s else 'below'} {fmt(nxt['inval'])}")
            msg.append(f"{'🟢 Buy' if s else '🔴 Sell'} if price comes back to <b>{fmt(a['edge'])}</b> and a 15m candle closes "
                       f"{'above' if s else 'below'} it · stop {'below' if s else 'above'} {fmt(flip_stop)}")
            if send("\n".join(msg), "Level failed", reply_to=a.get("msg_id")):
                print("level failed reply", key)
    if now - state.get("near_last", 0) >= 3600:                               # 2) new near-level alert
        score, word, _ = direction(ict, lv, price)
        day = (datetime.now(NY) - timedelta(hours=18)).strftime("%Y-%m-%d")    # trading day starts 18:00 New York
        for k, a in intraday_areas(lv, conf, price).items():
            key = f"{day}|{k}|{a['edge']:.0f}"
            if key in sent or a["dist"] > price * NEAR_PCT:
                continue
            if trend_state(df) != (1 if k == "BUY" else -1):
                continue                                                  # only with the 4H trend (tested: against it loses)
            s = k == "SELL"
            msg = (f"🔔 Gold <b>{fmt(price)}</b> is near the {'🔴 Sell' if s else '🟢 Buy'} level <b>{fmt(a['edge'])}</b> ({a['dist']:,.1f} away)\n"
                   f"Wait for a 15m candle to close back {'below' if s else 'above'} {fmt(a['edge'])} · stop {'above' if s else 'below'} {fmt(a['inval'])}")
            mid = send(msg, f"Near {k}")
            if mid or not os.environ.get("TELEGRAM_TOKEN"):
                sent[key] = {"t": now, "side": k, "edge": a["edge"], "inval": a["inval"], "status": "watch", "names": a["names"],
                             "msg_id": mid if isinstance(mid, int) else None}
                state["near_last"] = now
                print("near-level alert", key)
            break
    state["near"] = {x: v for x, v in sent.items() if now - (v["t"] if isinstance(v, dict) else v) < 3 * 86400}


# ---------- chart image ----------

def _trendlines(d1):
    """Lines through the last two confirmed 1H swing highs and the last two swing lows (what a trader would draw)."""
    from ict import swings
    sw = swings(d1)
    hs = [(idx, p) for _, idx, k, p in sw if k == "H"][-2:]
    ls = [(idx, p) for _, idx, k, p in sw if k == "L"][-2:]
    return [(pts, kind) for pts, kind in ((hs, "res"), (ls, "sup")) if len(pts) == 2 and pts[1][0] - pts[0][0] >= 3]


SESS_WIN = {0: (18, 2), 1: (2, 7), 2: (7, 12)}          # same sessions as research.vp_shape (New York hours)
SESS_NAME = {0: "Asia", 1: "London", 2: "New York"}


def vp_plan(df):
    """The 🟡 plan-trade setup for the current/next session: shape of the last finished session's volume profile.
    Same rules as research.vp_shape (so the prep shows exactly what the bot will trade)."""
    import research
    idx = df.index
    hr = idx.hour + idx.minute / 60
    date = (idx - pd.Timedelta(hours=18)).date
    sess = np.where((hr >= 18) | (hr < 2), 0, np.where(hr < 7, 1, np.where(hr < 12, 2, -1)))
    groups = {}
    for i, (d, s_) in enumerate(zip(date, sess)):
        if s_ >= 0:
            groups.setdefault((d, s_), []).append(i)
    keys = sorted(groups)
    now = datetime.now(NY)
    h = now.hour + now.minute / 60
    cur = 0 if (h >= 18 or h < 2) else 1 if h < 7 else 2 if h < 12 else -1
    if keys and cur >= 0 and keys[-1][1] == cur and (now - timedelta(hours=18)).date() == keys[-1][0]:
        keys = keys[:-1]                                   # that session is still running: use the one before
    if not keys:
        return None
    k = keys[-1]
    ix = np.array(groups[k])
    if len(ix) < 30:
        return None
    hi_, lo_, c_, v_ = (df[c].to_numpy() for c in ("High", "Low", "Close", "Volume"))
    poc, val, vah, lo, hi = research._vp(hi_, lo_, c_, v_, ix)
    pos = (poc - lo) / (hi - lo) if hi > lo else 0.5
    nxt = SESS_NAME[(k[1] + 1) % 3]
    base = {"from": SESS_NAME[k[1]], "for": nxt, "poc": round(float(poc), 2), "val": round(float(val), 2), "vah": round(float(vah), 2)}
    if pos >= 0.55:
        return {**base, "shape": "P", "side": "BUY", "edge": base["poc"], "inval": base["val"]}
    if pos <= 0.45:
        return {**base, "shape": "b", "side": "SELL", "edge": base["poc"], "inval": base["vah"]}
    return {**base, "shape": "D", "side": None}


def plan_areas(df):
    p = vp_plan(df)
    if not p or not p.get("side") or abs(p["edge"] - p["inval"]) > p["edge"] * 0.006:
        return {}
    price = float(df["Close"].iloc[-1])
    return {p["side"]: {"side": p["side"], "edge": p["edge"], "lo": p["edge"], "hi": p["edge"], "inval": p["inval"],
                        "names": ["POC"], "dist": round(abs(p["edge"] - price), 1), "target": None}}


def plan_line(p, price=None):
    if not p:
        return "🟡 <b>PLAN</b>: no data for the last session."
    if not p.get("side"):
        return f"🟡 <b>PLAN</b>: none · {p['from']} profile D-shape (buyers = sellers). Wait."
    s = p["side"] == "SELL"
    risk = abs(p["edge"] - p["inval"])
    if risk > p["edge"] * 0.006:
        return (f"🟡 <b>PLAN</b>: skipped · stop would be ${risk:,.0f} (too big for intraday, over 0.6%). Wait for the ⚡ signal.")
    return (f"🟡 <b>PLAN: {'SELL' if s else 'BUY'} {fmt(p['edge'])}</b> (POC)\n"
            f"{p['from']} {'b-shape: sellers' if s else 'P-shape: buyers'} in control · entry after a 15m close {'below' if s else 'above'} · "
            f"SL {'above' if s else 'below'} pullback (~${risk:,.0f}) · TP 1.5R")


def analysis_chart(df, lv, conf, lines, path, title):
    """Mentor-style picture: 4H context on the left, 15m execution on the right. Yesterday's range, the with-trend
    zone with its position box (entry, stop, 2R target), a dashed projected path, and short structure labels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD = "#0B0B0D", "#121215", "#1E1E22", "#E8E8ED", "#7C7C85", "#2BD07B", "#FF4D4D", "#E3B04B"
    price = float(df["Close"].iloc[-1])
    ts = trend_state(df)
    areas = plan_areas(df)
    side = next(iter(areas), None)
    plan = areas.get(side) if side else None
    lad = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    upper, lower, _, _ = lines
    fig = plt.figure(figsize=(12, 6.2), dpi=150)
    fig.patch.set_facecolor(BG)
    axL = fig.add_axes([0.035, 0.09, 0.33, 0.76]); axR = fig.add_axes([0.43, 0.09, 0.52, 0.76])

    def candles(ax, d, w=0.62):
        for i, (o_, h_, l_, c_) in enumerate(d[["Open", "High", "Low", "Close"]].to_numpy()):
            col = UP if c_ >= o_ else DN
            ax.plot([i, i], [l_, h_], color=col, lw=0.8)
            ax.add_patch(Rectangle((i - w / 2, min(o_, c_)), w, max(abs(c_ - o_), 0.05), color=col, lw=0))

    def style(ax, lo, hi, n, label):
        ax.set_facecolor(PANEL); ax.set_ylim(lo, hi); ax.set_xlim(-1, n)
        ax.grid(axis="y", color=GRID, lw=0.6); ax.set_xticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.tick_params(colors=MUT, labelsize=8, length=0); ax.yaxis.tick_right()
        ax.text(0.01, 0.97, label, transform=ax.transAxes, color=MUT, fontsize=9, va="top", fontweight="bold")

    # ---- left: 4H context
    d4 = resample(df, "4H").tail(42)
    lo4, hi4 = float(d4["Low"].min()), float(d4["High"].max()); p4 = (hi4 - lo4) * 0.06
    style(axL, lo4 - p4, hi4 + p4, len(d4) + 4, "4H · swing (big trend)")
    candles(axL, d4)
    for y, txt, col in ((upper, "BUY signal above", UP), (lower, "SELL signal below", DN)):
        if lo4 - p4 < y < hi4 + p4:
            axL.axhline(y, color=col, lw=0.9, ls=(0, (4, 3)), alpha=0.8)
            axL.text(0.5, y, f" {txt} {y:,.0f}", color=col, fontsize=7.5, va="bottom")
    sc = UP if ts > 0 else DN if ts < 0 else MUT
    fig.text(0.035, 0.865, f" Swing (4H): {'Bullish ↑' if ts > 0 else 'Bearish ↓' if ts < 0 else 'Range'} ", color=sc, fontsize=10.5,
             fontweight="bold", va="bottom", bbox=dict(boxstyle="round,pad=0.3", fc=PANEL, ec=sc, lw=0.8))

    # ---- right: 15m execution
    d = resample(df, "15m").tail(110)
    ys = [float(d["Low"].min()), float(d["High"].max())]
    if plan:
        risk = abs(plan["edge"] - plan["inval"]); tgt = plan["edge"] + (1.5 * risk if side == "BUY" else -1.5 * risk)
        ys += [plan["inval"], tgt]
    lo, hi = min(ys), max(ys); pd_ = (hi - lo) * 0.07
    N = len(d); RIGHT = 30
    style(axR, lo - pd_, hi + pd_, N + RIGHT, "15m · entry")
    candles(axR, d)
    for name, col in (("Prev day high", MUT), ("Prev day low", MUT)):
        y = lad.get(name)
        if y and lo - pd_ < y < hi + pd_:
            axR.plot([0, N + RIGHT - 2], [y, y], color=col, lw=0.8, ls=(0, (2, 3)))
            axR.text(1, y, f"{'Yesterday high' if 'high' in name else 'Yesterday low'} {y:,.2f}", color=col, fontsize=7.5, va="bottom")
    bx = asia_box(df)
    if bx:
        tz_idx = d.index
        m = ((tz_idx - pd.Timedelta(hours=18)).date == (datetime.now(NY) - timedelta(hours=18)).date()) & ((tz_idx.hour >= 18) | (tz_idx.hour < 2))
        xs = np.where(m)[0]
        if len(xs):
            axR.add_patch(Rectangle((xs[0] - 0.5, bx["lo"]), xs[-1] - xs[0] + 1, bx["r"], color=GOLD, alpha=0.08, lw=0.8, ec=GOLD))
            axR.text(xs[0], bx["hi"], " Asia box", color=GOLD, fontsize=7.5, va="bottom")
        for k, txt in (("up1", "POI 1 (1 in 3 days)"), ("dn1", "POI 1 (1 in 3 days)"), ("up2", "POI 2 (1 in 9)"), ("dn2", "POI 2 (1 in 9)")):
            y = bx[k]
            if lo - pd_ < y < hi + pd_:
                axR.plot([0, N + RIGHT - 2], [y, y], color=MUT, lw=0.7, ls=(0, (6, 4)), alpha=0.7)
                axR.text(N - 1, y, f"{txt} {y:,.0f} ", color=MUT, fontsize=7, va="bottom", ha="right")
    axR.axhline(price, color=INK, lw=0.6, alpha=0.4)
    axR.text(N + RIGHT + 0.3, price, f"{price:,.2f}", color=BG, fontsize=8, va="center", ha="left", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.25", fc=INK, ec="none"), clip_on=False, zorder=5)
    if plan:
        bull = side == "BUY"; x0, x1 = N + 3, N + RIGHT - 2
        en, stp = plan["edge"], plan["inval"]
        axR.add_patch(Rectangle((x0, min(en, tgt)), x1 - x0, abs(tgt - en), color=UP, alpha=0.18, lw=0))
        axR.add_patch(Rectangle((x0, min(en, stp)), x1 - x0, abs(en - stp), color=DN, alpha=0.25, lw=0))
        axR.add_patch(Rectangle((0, plan["lo"] - 0.6), N, plan["hi"] - plan["lo"] + 1.2, color=GOLD, alpha=0.12, lw=0))
        for y, txt, col, va in ((tgt, f"Target {tgt:,.2f}", UP, "bottom" if bull else "top"),
                                (en, f"POC {'buy' if bull else 'sell'} zone {en:,.2f}", GOLD, "top" if bull else "bottom"),
                                (stp, f"Stop {stp:,.2f}", DN, "top" if bull else "bottom")):
            axR.plot([x0, x1], [y, y], color=col, lw=1)
            axR.text(x0 + 0.6, y, txt, color=col, fontsize=8, va=va, fontweight="bold")
        # projected path: now -> zone -> target
        px = [N - 1, x0 + 3, x0 + 8, x0 + 13, x1 - 3]
        py = [price, en, en + (tgt - en) * 0.45, en + (tgt - en) * 0.3, tgt]
        axR.plot(px, py, color=INK, lw=1.2, ls=(0, (3, 2)), alpha=0.9)
        axR.annotate("", xy=(px[-1], py[-1]), xytext=(px[-2], py[-2]), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
        tag = f"Plan: {'BUY' if bull else 'SELL'} the pullback to the POC (busiest price) after a 15m close {'above' if bull else 'below'} · TP 1.5R"
    else:
        tag = "No plan this session (D-shape profile or stop too big for intraday). Wait for the 4H signal."
    fig.text(0.035, 0.94, title, color=INK, fontsize=14, fontweight="bold")
    fig.text(0.035, 0.905, tag, color=GOLD, fontsize=10)
    fig.text(0.035, 0.03, "XAU.KH · POC = busiest price of the last session · R = your risk · a plan, not a promise", color=MUT, fontsize=7.5)
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


def trade_chart(df, lv, sig, path):
    """Picture for a plan trade: 15m candles, the entry / SL / TP box with pips, and the support and resistance
    around it (POC, value area high/low of the last session, yesterday's high/low), each labelled in plain words."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD = "#0B0B0D", "#121215", "#1E1E22", "#E8E8ED", "#7C7C85", "#2BD07B", "#FF4D4D", "#E3B04B"
    bull = sig["dir"] == "bull"
    en, sl, tp = sig["entry"], sig["stop"], sig["target"]
    pips = lambda px: f"{(px - en) * (1 if bull else -1) * 10:+,.0f} pips"
    p = vp_plan(df) or {}
    lad = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    d = resample(df, "15m").tail(100)
    lv_ = [("POC · busiest price", p.get("poc"), GOLD, "-"),
           ("VAH · value area high (resistance)", p.get("vah"), DN, (0, (3, 3))),
           ("VAL · value area low (support)", p.get("val"), UP, (0, (3, 3))),
           ("Yesterday high (resistance)", lad.get("Prev day high"), MUT, (0, (1, 3))),
           ("Yesterday low (support)", lad.get("Prev day low"), MUT, (0, (1, 3)))]
    ys = [float(d["Low"].min()), float(d["High"].max()), en, sl, tp]
    lo, hi = min(ys), max(ys); pad = (hi - lo) * 0.08
    lv_ = [x for x in lv_ if x[1] and lo - pad * 3 < x[1] < hi + pad * 3]
    for _, y, _, _ in lv_:
        lo, hi = min(lo, y), max(hi, y)
    pad = (hi - lo) * 0.07
    N, RIGHT = len(d), 26
    fig = plt.figure(figsize=(11, 6.4), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.04, 0.08, 0.84, 0.76]); ax.set_facecolor(PANEL)
    ax.set_ylim(lo - pad, hi + pad); ax.set_xlim(-1, N + RIGHT)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_xticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=MUT, labelsize=8, length=0); ax.yaxis.tick_right()
    for i, (o_, h_, l_, c_) in enumerate(d[["Open", "High", "Low", "Close"]].to_numpy()):
        col = UP if c_ >= o_ else DN
        ax.plot([i, i], [l_, h_], color=col, lw=0.8)
        ax.add_patch(Rectangle((i - 0.31, min(o_, c_)), 0.62, max(abs(c_ - o_), 0.05), color=col, lw=0))
    for name, y, col, ls in lv_:
        ax.plot([0, N + 1], [y, y], color=col, lw=0.9, ls=ls, alpha=0.9)
        ax.text(1, y, f"{name} {y:,.2f}", color=col, fontsize=7.5, va="bottom", alpha=0.95)
    x0, x1 = N + 1, N + RIGHT - 2
    ax.add_patch(Rectangle((x0, min(en, tp)), x1 - x0, abs(tp - en), color=UP, alpha=0.2, lw=0))
    ax.add_patch(Rectangle((x0, min(en, sl)), x1 - x0, abs(en - sl), color=DN, alpha=0.28, lw=0))
    for y, txt, col, va in ((tp, f"TP {tp:,.2f}  ({pips(tp)})", UP, "bottom" if bull else "top"),
                            (en, f"{'BUY' if bull else 'SELL'} entry {en:,.2f}", INK, "bottom" if not bull else "top"),
                            (sl, f"SL {sl:,.2f}  ({pips(sl)})  = your risk", DN, "top" if bull else "bottom")):
        ax.plot([x0, x1], [y, y], color=col, lw=1.2)
        ax.text(x0 + 0.5, y, txt, color=col, fontsize=8.5, va=va, fontweight="bold")
    ax.annotate("", xy=(x1 - 2, tp), xytext=(x0 + 2, en), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, ls="--"))
    fig.text(0.04, 0.93, f"{'🟢' if bull else '🔴'} Gold {'BUY' if bull else 'SELL'} plan".replace("🟢 ", "").replace("🔴 ", ""),
             color=UP if bull else DN, fontsize=15, fontweight="bold")
    fig.text(0.04, 0.885, f"Entry {en:,.2f}  ·  SL {sl:,.2f}  ·  TP {tp:,.2f}  ·  risk 0.5% max", color=INK, fontsize=10.5)
    fig.text(0.04, 0.03, "Green box = profit area to TP · red box = risk to SL · dotted lines = support / resistance", color=MUT, fontsize=8)
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path


MAP_HOUR_LOCAL = 10      # Daily Market Map, weekdays, local time (quiet Asia hours)


def daily_range_stats(df):
    """Median daily high-low range of the last 20 trading days, and today's range so far."""
    day = (df.index - pd.Timedelta(hours=18)).date
    g = df.groupby(day)
    rng = (g["High"].max() - g["Low"].min())
    today = float(rng.iloc[-1])
    adr = float(rng.iloc[-21:-1].median()) if len(rng) > 21 else None
    return adr, today


def market_map(df, lv, lines, path):
    """Full analysis picture: 1H candles of the last ~5 days, swing structure (HH/HL/LH/LL), a 5-day volume profile
    with its POC, key levels, the 4H signal lines and two if/then scenarios. Returns (path, text)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import research
    from ict import swings
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, PANEL, GRID, INK, MUT, UP, DN, GOLD, BLUE = "#0B0B0D", "#121215", "#1E1E22", "#E8E8ED", "#7C7C85", "#2BD07B", "#FF4D4D", "#E3B04B", "#5AC8FA"
    d1 = resample(df, "1H").tail(110)
    price = float(df["Close"].iloc[-1])
    upper, lower, _, _ = lines
    lad = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    wk = df[df.index >= df.index[-1] - pd.Timedelta(days=7)]
    wk_hi, wk_lo = float(wk["High"].max()), float(wk["Low"].min())
    # 5-day volume profile
    last5 = np.where(df.index >= df.index[-1] - pd.Timedelta(days=5))[0]
    H_, L_, C_, V_ = (df[c].to_numpy() for c in ("High", "Low", "Close", "Volume"))
    poc, val, vah, plo, phi = research._vp(H_, L_, C_, V_, last5)
    tp_ = (H_[last5] + L_[last5] + C_[last5]) / 3
    bins = np.arange(np.floor(plo), np.ceil(phi) + 1, 1.0)
    vol, _ = np.histogram(tp_, bins=bins, weights=np.maximum(V_[last5], 1))
    # swing structure on 1H
    sw = swings(d1, 4)                                   # stronger 1H swings (4 candles each side)
    labels, lastH, lastL = [], None, None
    for _, i, k, p in sw:
        if k == "H":
            labels.append((i, p, "HH" if lastH is not None and p > lastH else "LH" if lastH is not None else "H", k)); lastH = p
        else:
            labels.append((i, p, "HL" if lastL is not None and p > lastL else "LL" if lastL is not None else "L", k)); lastL = p
    highs = sorted({p for _, _, k, p in sw if k == "H" and p > price})
    lows = sorted({p for _, _, k, p in sw if k == "L" and p < price}, reverse=True)
    adr, today = daily_range_stats(df)
    gap = 0.3 * (adr or price * 0.012)
    cands = [y for y in (wk_hi, wk_lo, upper, lower, vah, val, poc, lad.get("Prev day high"), lad.get("Prev day low"),
                         *[p for _, _, _, p in sw]) if y]
    up_trig = highs[0] if highs else None
    dn_trig = lows[0] if lows else None
    up_tgt = min((y for y in cands if up_trig and y >= up_trig + gap), default=None)
    dn_tgt = max((y for y in cands if dn_trig and y <= dn_trig - gap), default=None)
    ys = [float(d1["Low"].min()), float(d1["High"].max()), *(y for y in (up_tgt, dn_tgt) if y)]
    lo, hi = min(ys), max(ys); pad = (hi - lo) * 0.06
    fig = plt.figure(figsize=(12, 6.6), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.035, 0.08, 0.72, 0.76]); vp = fig.add_axes([0.755, 0.08, 0.09, 0.76], sharey=ax)
    N, RIGHT = len(d1), 22
    for a_ in (ax, vp):
        a_.set_facecolor(PANEL); a_.grid(axis="y", color=GRID, lw=0.6); a_.set_xticks([])
        for sp in a_.spines.values(): sp.set_visible(False)
        a_.tick_params(colors=MUT, labelsize=8, length=0)
    ax.set_ylim(lo - pad, hi + pad); ax.set_xlim(-1, N + RIGHT); ax.yaxis.tick_left()
    vp.yaxis.tick_right()
    for i, (o_, h_, l_, c_) in enumerate(d1[["Open", "High", "Low", "Close"]].to_numpy()):
        col = UP if c_ >= o_ else DN
        ax.plot([i, i], [l_, h_], color=col, lw=0.8)
        ax.add_patch(Rectangle((i - 0.31, min(o_, c_)), 0.62, max(abs(c_ - o_), 0.05), color=col, lw=0))
    for i, p, t, k in labels[-10:]:
        ax.text(i, p, t, color=(UP if t in ("HH", "HL") else DN if t in ("LH", "LL") else MUT), fontsize=7.5, fontweight="bold",
                ha="center", va="bottom" if k == "H" else "top")
    drawn = []
    for name, y, col, ls in (("4H BUY signal above", upper, UP, (0, (5, 3))), ("4H SELL signal below", lower, DN, (0, (5, 3))),
                             ("Week high", wk_hi, MUT, (0, (1, 3))), ("Week low", wk_lo, MUT, (0, (1, 3))),
                             ("Yesterday high", lad.get("Prev day high"), MUT, (0, (2, 3))), ("Yesterday low", lad.get("Prev day low"), MUT, (0, (2, 3))),
                             ("POC 5 days (busiest price)", poc, GOLD, "-")):
        if y and lo - pad < y < hi + pad and all(abs(y - z) > (hi - lo) * 0.015 for z in drawn):
            drawn.append(y)
            ax.plot([0, N + RIGHT - 1], [y, y], color=col, lw=0.8, ls=ls, alpha=0.85)
            ax.text(1, y, f"{name} {y:,.2f}", color=col, fontsize=7, va="bottom")
    ax.axhspan(val, vah, color=GOLD, alpha=0.05, lw=0)
    vp.barh(bins[:-1], vol, height=1.0, color=BLUE, alpha=0.55, align="edge")
    vp.axhline(poc, color=GOLD, lw=1); vp.set_xticks([]); vp.text(0, 0.995, "volume", transform=vp.transAxes, color=MUT, fontsize=7, va="top")
    ax.axhline(price, color=INK, lw=0.6, alpha=0.4)
    x0 = N - 1
    for trig, tgt, col, word in ((up_trig, up_tgt, UP, "above"), (dn_trig, dn_tgt, DN, "below")):
        if trig and tgt:
            ax.plot([x0, x0 + 6, x0 + 9, x0 + 18], [price, trig, trig - (trig - price) * 0.3, tgt], color=col, lw=1.2, ls=(0, (3, 2)))
            ax.annotate("", xy=(x0 + 18, tgt), xytext=(x0 + 15, tgt + (trig - tgt) * 0.15), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2))
            ax.text(x0 + 17.5, tgt, f"{tgt:,.0f} ", color=col, fontsize=8.5, va="bottom" if col == UP else "top", ha="right", fontweight="bold")
    score_up = sum(1 for _, _, t, _ in labels[-4:] if t in ("HH", "HL")); score_dn = sum(1 for _, _, t, _ in labels[-4:] if t in ("LH", "LL"))
    struct = "Bullish structure (HH + HL)" if score_up >= 3 else "Bearish structure (LH + LL)" if score_dn >= 3 else "Mixed structure (range)"
    fig.text(0.035, 0.94, f"Gold · Daily Market Map · {local(time.time())}", color=INK, fontsize=14, fontweight="bold")
    fig.text(0.035, 0.905, f"{struct}  ·  price {price:,.2f}", color=GOLD, fontsize=10.5)
    fig.text(0.035, 0.03, "HH/HL = higher high / higher low (buyers) · LH/LL = lower high / lower low (sellers) · dashed = if/then scenarios · a map, not a signal",
             color=MUT, fontsize=7.5)
    fig.savefig(path, facecolor=BG); plt.close(fig)
    txt = [f"🗺 <b>DAILY MARKET MAP</b> · Gold <b>{fmt(price)}</b>",
           f"Structure (1H): {struct}",
           *([f"🟢 If price breaks above <b>{fmt(up_trig)}</b> (last swing high) → next target {fmt(up_tgt)}"] if up_trig and up_tgt else []),
           *([f"🔴 If price breaks below <b>{fmt(dn_trig)}</b> (last swing low) → next target {fmt(dn_tgt)}"] if dn_trig and dn_tgt else []),
           f"🟡 POC 5 days (busiest price): {fmt(poc)} · value area {fmt(val)}–{fmt(vah)}",
           *([f"📏 Gold usually moves <b>${adr:,.0f}</b> a day (ADR); today so far ${today:,.0f} ({min(999, round(100 * today / adr))}% used)."
              + (" Most of today's move may be done: careful chasing." if today >= 0.8 * adr else "")] if adr else []),
           "", "<i>A map to read the market, not a signal. Signals come only from ✅ / 🟡 setups.</i>"]
    return path, "\n".join(txt)


def card(df, price, word, score, areas, path, label):
    """Small image for Telegram: a big direction arrow, the price, the last 24h line with the sell and buy levels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Polygon, Circle
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, CARD, INK, MUT, UP, DN, FLAT = "#000000", "#1C1C1E", "#F5F5F7", "#8E8E93", "#30D158", "#FF453A", "#8E8E93"
    col = UP if score >= 20 else DN if score <= -20 else FLAT
    fig = plt.figure(figsize=(8, 4.2), dpi=150)
    fig.patch.set_facecolor(BG)
    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off"); bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.add_patch(FancyBboxPatch((0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0,rounding_size=0.04", fc=CARD, ec="none"))
    # left: arrow badge
    a = fig.add_axes([0.05, 0.30, 0.25, 0.48]); a.axis("off"); a.set_xlim(-1, 1); a.set_ylim(-1, 1); a.set_aspect("equal")
    a.add_patch(Circle((0, 0), 0.95, fc=col, alpha=0.18, ec="none"))
    shape = {1: [(-0.38, -0.05), (0, 0.5), (0.38, -0.05), (0.14, -0.05), (0.14, -0.5), (-0.14, -0.5), (-0.14, -0.05)]}
    pts = shape[1]
    if score <= -20:
        pts = [(x, -y) for x, y in pts]
    elif -20 < score < 20:
        pts = [(y, x) for x, y in pts]                                 # sideways: arrow pointing right
    a.add_patch(Polygon(pts, closed=True, fc=col, ec="none"))
    bg.text(0.175, 0.20, word, color=col, ha="center", va="center", fontsize=17, fontweight="bold")
    bg.text(0.175, 0.11, "direction", color=MUT, ha="center", va="center", fontsize=9)
    # top right: label and price
    bg.text(0.36, 0.85, label, color=MUT, fontsize=10, va="center")
    bg.text(0.36, 0.72, f"{price:,.2f}", color=INK, fontsize=24, fontweight="bold", va="center")
    # right: last 24h with levels
    d = resample(df, "15m").tail(96)
    ax = fig.add_axes([0.36, 0.30, 0.42, 0.32]); ax.set_facecolor(CARD); ax.axis("off")
    y = d["Close"].to_numpy(); x = range(len(y))
    lv_ = [areas[k]["edge"] for k in areas]
    lo, hi = min(list(y) + lv_), max(list(y) + lv_)
    ax.set_ylim(lo - (hi - lo) * 0.08, hi + (hi - lo) * 0.08); ax.set_xlim(0, len(y) + 2)
    ax.plot(x, y, color=INK, lw=1.6)
    ax.fill_between(x, y, lo - (hi - lo) * 0.08, color=INK, alpha=0.05)
    ax.plot([len(y) - 1], [y[-1]], "o", color=INK, ms=5)
    bg.text(0.36, 0.25, "last 24 hours", color=MUT, fontsize=8, va="center")
    # levels list on the right
    yy = 0.62
    for k in ("SELL", "BUY"):
        if k not in areas:
            continue
        c = DN if k == "SELL" else UP
        ax.axhline(areas[k]["edge"], color=c, lw=1, ls=(0, (3, 3)))
        bg.add_patch(FancyBboxPatch((0.80, yy - 0.085), 0.16, 0.17, boxstyle="round,pad=0,rounding_size=0.02", fc=c, alpha=0.15, ec="none"))
        bg.text(0.88, yy + 0.035, f"{'Sell' if k == 'SELL' else 'Buy'} {areas[k]['edge']:,.0f}", color=c, ha="center", va="center", fontsize=11, fontweight="bold")
        bg.text(0.88, yy - 0.04, f"stop {areas[k]['inval']:,.0f}", color=MUT, ha="center", va="center", fontsize=8.5)
        yy -= 0.22
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


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

def session_range(df, name, days=20):
    """Typical high-low range of that session over the last `days` sessions (median, $)."""
    k = {v: k for k, v in SESS_NAME.items()}[name]
    a, b = SESS_WIN[k]
    hr = df.index.hour
    m = ((hr >= a) | (hr < b)) if a > b else ((hr >= a) & (hr < b))
    x = df[m]
    day = (x.index - pd.Timedelta(hours=18)).date
    r = (x.groupby(day)["High"].max() - x.groupby(day)["Low"].min()).tail(days)
    return float(r.median()) if len(r) >= 5 else None


def no_trade_guide(name, p, lv, df):
    """For sessions without a tested setup: usual range, key levels, risk advice. Short and technical."""
    rng = session_range(df, name)
    out = ["", f"🧭 <b>NO SETUP · how to handle {name}</b>"]
    parts = []
    if rng:
        parts.append(f"usual range ~${rng:,.0f}")
    if p:
        parts.append(f"POC {fmt(p['poc'])} · VA {fmt(p['val'])}–{fmt(p['vah'])}")
    if parts:
        out.append("• " + " · ".join(parts))
    out.append("• Trading anyway: <b>0.25% risk</b>, SL outside the VA (range trades were slightly negative in tests)")
    return out


def asia_box(df):
    """Asia range (18:00-02:00 New York) of the current trading day and its POI projections (ZTD-style):
    POI 1 / POI 2 = one / two box-heights beyond the box. 2 years of spot gold: POI 1 reached on 36% of days
    (either side; the swing direction does not predict which), POI 2 on 11%. A map of how far a day stretches."""
    now = datetime.now(NY)
    if not (2 <= now.hour < 17):
        return None
    day = (now - timedelta(hours=18)).date()
    idx = df.index
    m = ((idx - pd.Timedelta(hours=18)).date == day) & ((idx.hour >= 18) | (idx.hour < 2))
    a = df[m]
    if len(a) < 60:
        return None
    hi, lo = float(a["High"].max()), float(a["Low"].min())
    r = hi - lo
    return {"hi": hi, "lo": lo, "r": r, "up1": hi + r, "up2": hi + 2 * r, "dn1": lo - r, "dn2": lo - 2 * r}


def while_you_slept(df, news):
    """Overnight summary for the 06:00 Asia prep: the move since 07:00 New York (London close / NY open),
    the overnight high and low, and the big news that was released."""
    now = datetime.now(NY)
    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if now < start:
        start -= timedelta(days=1)
    x = df[df.index >= start]
    if len(x) < 12:
        return []
    o_, c_ = float(x["Open"].iloc[0]), float(x["Close"].iloc[-1])
    hi_, lo_ = float(x["High"].max()), float(x["Low"].min())
    ev = [e["title"] for e in news.get("events", []) if e.get("impact") == "High"
          and start.astimezone(timezone.utc) <= datetime.fromisoformat(e["time"].replace("Z", "+00:00")) <= now.astimezone(timezone.utc)]
    out = ["", f"🌙 <b>While you slept</b> (New York session): gold {fmt(o_)} → {fmt(c_)} (<b>{c_ - o_:+,.1f}</b>) · "
               f"high {fmt(hi_)} · low {fmt(lo_)}"]
    if ev:
        out.append("📰 Released: " + esc(", ".join(dict.fromkeys(ev))))
    return out


EVENT_DIR = [   # (keywords, what "higher than forecast" usually means for gold): -1 = gold down, +1 = gold up
    (("cpi", "pce", "ppi", "inflation"), -1), (("non-farm", "nonfarm", "payroll", "employment change"), -1),
    (("unemployment rate",), 1), (("jobless claims", "unemployment claims"), 1), (("gdp",), -1), (("ism", "pmi"), -1),
    (("retail sales",), -1), (("jolts", "job openings"), -1), (("average hourly earnings",), -1)]


def macro_card(macro, news, path, cot=None):
    """Picture: one tile per fundamental (value, arrow, effect on gold), the next big news with its two outcomes,
    and which setups the fundamentals favour. Returns (path, short caption) or None without data."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, CARD, INK, MUT, UP, DN, FLAT, GOLD = "#0B0B0D", "#1C1C1E", "#F5F5F7", "#8E8E93", "#30D158", "#FF453A", "#8E8E93", "#E3B04B"
    tiles = []   # (title, value, change text, change dir, effect on gold +1/-1/0)
    d, y, vx, spx = (macro.get(k) or {} for k in ("dxy", "us10y", "vix", "spx"))
    if d.get("last") is not None:
        ch = d.get("chg_pct", 0); dr = 1 if ch > 0.05 else -1 if ch < -0.05 else 0
        tiles.append(("DXY", "US dollar", f"{d['last']}", f"{ch:+.2f}%", dr, -dr))
    if y.get("last") is not None:
        ch = y.get("chg_bp", 0); dr = 1 if ch > 2 else -1 if ch < -2 else 0
        tiles.append(("US10Y", "bond yield", f"{y['last']:.2f}%", f"{ch:+.0f} bp", dr, -dr))
    if vx.get("last") is not None:
        ch = vx.get("chg_pct", 0); dr = 1 if ch >= 5 else -1 if ch <= -5 else 0
        eff = 1 if vx["last"] >= 25 or ch >= 10 else -1 if vx["last"] < 16 and ch <= 0 else 0
        tiles.append(("VIX", "fear index", f"{vx['last']}", f"{ch:+.0f}%", dr, eff))
    if cot and cot.get("net_change") is not None:
        ch = cot["net_change"]; dr = 1 if ch > 0 else -1 if ch < 0 else 0
        tiles.append(("COT", "big funds", f"{'long' if cot['net'] > 0 else 'short'} {abs(cot['net']) / 1000:,.0f}k", f"{ch / 1000:+,.0f}k", dr, dr))
    if not tiles:
        return None
    now = datetime.now(timezone.utc)
    nxt = sorted([(datetime.fromisoformat(e["time"].replace("Z", "+00:00")), e) for e in news.get("events", [])
                  if e.get("impact") == "High" and datetime.fromisoformat(e["time"].replace("Z", "+00:00")) > now], key=lambda x: x[0])[:1]
    fig = plt.figure(figsize=(10, 5.6), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.04, 0.93, "What moves gold today", color=INK, fontsize=17, fontweight="bold", va="center")
    ax.text(0.96, 0.93, local(time.time()), color=MUT, fontsize=10, va="center", ha="right")
    w = 0.92 / len(tiles)
    for k, (code, name, val, chg, dr, eff) in enumerate(tiles):
        x = 0.04 + k * w
        ax.add_patch(FancyBboxPatch((x + 0.006, 0.47), w - 0.012, 0.37, boxstyle="round,pad=0,rounding_size=0.02", fc=CARD, ec="none"))
        cx = x + w / 2
        ax.text(cx, 0.80, code, color=INK, fontsize=13, fontweight="bold", ha="center")
        ax.text(cx, 0.755, name, color=MUT, fontsize=8.5, ha="center")
        ax.text(cx, 0.68, val, color=INK, fontsize=14, fontweight="bold", ha="center")
        ax.text(cx, 0.625, f"{'▲' if dr > 0 else '▼' if dr < 0 else '■'} {chg}", color=MUT,
                fontsize=10, ha="center")
        ec = UP if eff > 0 else DN if eff < 0 else FLAT
        ax.add_patch(FancyBboxPatch((x + 0.02, 0.495), w - 0.04, 0.075, boxstyle="round,pad=0,rounding_size=0.015", fc=ec, alpha=0.18, ec="none"))
        ax.text(cx, 0.532, f"Gold {'↑' if eff > 0 else '↓' if eff < 0 else '–'}", color=ec, fontsize=12, fontweight="bold", ha="center", va="center")
    # next big news with both outcomes
    if nxt:
        t, e = nxt[0]
        sgn = next((v for keys, v in EVENT_DIR if any(kw in e["title"].lower() for kw in keys)), None)
        ax.text(0.04, 0.40, f"Next big news · {local(t.timestamp())} {t.astimezone(local_tz()):%a}", color=MUT, fontsize=9.5)
        ax.text(0.04, 0.355, esc(e["title"]) + (f"   (forecast {e['forecast']})" if e.get("forecast") else ""), color=INK, fontsize=12, fontweight="bold")
        if sgn:
            for j, (lab, g) in enumerate((("Higher than forecast", sgn), ("Lower than forecast", -sgn))):
                x = 0.04 + j * 0.465
                c = UP if g > 0 else DN
                ax.add_patch(FancyBboxPatch((x, 0.17), 0.445, 0.13, boxstyle="round,pad=0,rounding_size=0.02", fc=c, alpha=0.14, ec="none"))
                ax.text(x + 0.02, 0.235, lab, color=INK, fontsize=10.5, va="center")
                ax.text(x + 0.425, 0.235, f"Gold {'↑' if g > 0 else '↓'}  ·  {'BUY' if g > 0 else 'SELL'} setups", color=c, fontsize=11,
                        fontweight="bold", va="center", ha="right")
    tally = sum(t_[5] for t_ in tiles)
    side = "BUY" if tally > 0 else "SELL" if tally < 0 else None
    msg = (f"Fundamentals lean gold {'UP' if tally > 0 else 'DOWN'}: {side} setups have the wind behind them" if side
           else "Fundamentals are mixed: trade the chart setups only")
    ax.text(0.04, 0.075, msg, color=(UP if tally > 0 else DN if tally < 0 else GOLD), fontsize=12, fontweight="bold", va="center")
    ax.text(0.96, 0.075, "usual effect, not a promise", color=MUT, fontsize=8, va="center", ha="right")
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path, f"🏛 <b>Fundamentals</b>: {msg}."


def macro_lean(macro):
    d, y, vx = (macro.get(k) or {} for k in ("dxy", "us10y", "vix"))
    t = 0
    if d.get("chg_pct") is not None:
        t += -1 if d["chg_pct"] > 0.05 else 1 if d["chg_pct"] < -0.05 else 0
    if y.get("chg_bp") is not None:
        t += -1 if y["chg_bp"] > 2 else 1 if y["chg_bp"] < -2 else 0
    if vx.get("last") is not None:
        t += 1 if vx["last"] >= 25 or vx.get("chg_pct", 0) >= 10 else -1 if vx["last"] < 16 and vx.get("chg_pct", 0) <= 0 else 0
    return 1 if t > 0 else -1 if t < 0 else 0


def macro_shift(macro, news, state):
    """New fundamentals card only on a meaningful change since the last card: DXY 0.4%+, US10Y 8bp+, VIX 20%+ or the
    overall lean flipped. Max 2 a day, never within 20 minutes of high-impact news (the news reaction covers that)."""
    snap = state.get("macro_snap")
    d, y, vx = (macro.get(k) or {} for k in ("dxy", "us10y", "vix"))
    if not snap or d.get("last") is None:
        return
    now = datetime.now(timezone.utc)
    near = any(abs((datetime.fromisoformat(e["time"].replace("Z", "+00:00")) - now).total_seconds()) < 1200
               for e in news.get("events", []) if e.get("impact") == "High")
    day = datetime.now(local_tz()).strftime("%Y-%m-%d")
    sent = [t for t in state.get("macro_alerts", []) if t[:10] == day]
    if near or len(sent) >= 2:
        return
    why = []
    if snap.get("dxy") and abs(d["last"] / snap["dxy"] - 1) * 100 >= 0.4:
        why.append(f"DXY (dollar) {'up' if d['last'] > snap['dxy'] else 'down'} {abs(d['last'] / snap['dxy'] - 1) * 100:.1f}%")
    if snap.get("us10y") and y.get("last") is not None and abs(y["last"] - snap["us10y"]) * 100 >= 8:
        why.append(f"US10Y (yield) {'up' if y['last'] > snap['us10y'] else 'down'} {abs(y['last'] - snap['us10y']) * 100:.0f} bp")
    if snap.get("vix") and vx.get("last") is not None and abs(vx["last"] / snap["vix"] - 1) * 100 >= 20:
        why.append(f"VIX (fear) {'up' if vx['last'] > snap['vix'] else 'down'} {abs(vx['last'] / snap['vix'] - 1) * 100:.0f}%")
    lean = macro_lean(macro)
    if lean != snap.get("lean") and lean != 0:
        why.append(f"overall lean flipped to gold {'UP' if lean > 0 else 'DOWN'}")
    if not why:
        return
    mc = macro_card(macro, news, "macro_card.png", jl("cot.json"))
    if mc and (send_photo(mc[0], f"🔄 <b>Fundamentals changed</b>: {esc(', '.join(why))}.\n{mc[1]}", "Fundamentals") or not os.environ.get("TELEGRAM_TOKEN")):
        state["macro_alerts"] = sent + [datetime.now(local_tz()).strftime("%Y-%m-%d %H:%M")]
        state["macro_snap"] = macro_snapshot(macro)
        print("macro shift sent:", why)


def macro_snapshot(macro):
    g = lambda k, f: (macro.get(k) or {}).get(f)
    return {"dxy": g("dxy", "last"), "us10y": g("us10y", "last"), "vix": g("vix", "last"), "lean": macro_lean(macro)}


def briefing_text(name, ict, conf, lv, news, df, lines, start_utc, macro=None):
    """Short: direction, one sell level, one buy level, the big signal lines, the one risk that matters most."""
    price = float(df["Close"].iloc[-1])
    score, word, b = direction(ict, lv, price)
    upper, lower, next_close, _ = lines
    areas = intraday_areas(lv, conf, price)
    ev = news_in(news, start_utc, 6)
    vol = float(atr(df).iloc[-1] / atr(df).rolling(288 * 20, min_periods=288).median().iloc[-1])
    arrow = "↑" if score >= 20 else "↓" if score <= -20 else "↔"
    head = {"Asia": "🌏", "London": "🇬🇧", "New York": "🇺🇸"}[name]
    risk = (f"📰 {esc(ev[0][1])} at {local(ev[0][0].timestamp())}: no new trades 15 min before/after." if ev else
            "⚠️ Gold is moving faster than usual today: use a smaller lot." if vol >= 1.3 else
            "⚠️ No clear direction right now: don't force a trade." if abs(score) < 20 else None)
    ts = trend_state(df)
    lad = {x["name"]: x["price"] for x in lv.get("ladder", [])}
    bw = lambda v: "Bullish ↑" if v > 0 else "Bearish ↓" if v < 0 else "Range"
    struct = f"Swing 4H: {bw(ts)} · Internal 1H: {bw(b['1H'])}"
    rng = f"Yesterday {fmt(lad['Prev day low'])}–{fmt(lad['Prev day high'])}" if lad.get("Prev day high") else None
    out = [f"{head} <b>{name.upper()}</b> · Gold <b>{fmt(price)}</b>", struct + (f" · {rng}" if rng else ""),
           *(while_you_slept(df, news) if name == "Asia" else []),
           "",
           plan_line(plan := vp_plan(df), price),
           f"⚡ <b>4H SIGNAL</b> (69% win): BUY if 4H closes > {fmt(upper)} · SELL < {fmt(lower)}",
           *(no_trade_guide(name, plan, lv, df) if not (plan and plan.get("side")) and min(upper - price, price - lower) > price * 0.004
             else []),
           *([f"📦 Asia box {fmt(bx['lo'])}–{fmt(bx['hi'])} · POI1 {fmt(bx['up1'])} / {fmt(bx['dn1'])} (1 in 3 days)"]
             if name != "Asia" and (bx := asia_box(df)) else []),
           *([risk] if risk else []),
           "", "<i>⚡✅ tested · 🟡 plan = 0.5% risk</i>"]
    if LANG == "km":
        out = [f"{head} <b>សម័យ {KM_SESSION[name]}</b> · មាស <b>{fmt(price)}</b> · {KW[word]} {arrow}",
               *[f"{'🔴 លក់' if k == 'SELL' else '🟢 ទិញ'} <b>{fmt(areas[k]['edge'])}</b> · stop {fmt(areas[k]['inval'])}" for k in ("SELL", "BUY") if k in areas],
               f"⚡ 4H បិទលើ {fmt(upper)} = ទិញ · ក្រោម {fmt(lower)} = លក់"]
    return "\n".join(out)


def heads_up(df, lines, state):
    price = float(df["Close"].iloc[-1])
    upper, lower, next_close, _ = lines
    day = datetime.now(NY).strftime("%Y-%m-%d")
    sent = state.setdefault("heads_up", {})
    for side, level in (("BUY", upper), ("SELL", lower)):
        dist = (level - price) if side == "BUY" else (price - level)
        key = f"{day}|{side}|{level:.2f}"
        if 0 < dist <= price * HEADS_UP_PCT and key not in sent:
            en = (f"⚡ <b>Possible {side}</b>: gold {fmt(price)} is {dist:,.1f} from {fmt(level)}.\n"
                  f"{side} signal if the 4H candle closing at {local(next_close.timestamp())} finishes {'above' if side == 'BUY' else 'below'} it. "
                  f"<i>Don't enter early.</i>")
            km = (f"⚡ <b>ត្រៀមខ្លួន · អាច{'ទិញ' if side == 'BUY' else 'លក់'}</b>\nមាសនៅឆ្ងាយ {dist:,.1f} ពី {fmt(level)}។ "
                  f"បើ 4H បិទ{'លើ' if side == 'BUY' else 'ក្រោម'}វានៅម៉ោង {local(next_close.timestamp())} បូតនឹងផ្ញើសញ្ញា។")
            msg = km if LANG == "km" else en + ("\n\n" + km if LANG == "both" else "")
            if send(msg, f"Heads up {side}"):
                sent[key] = time.time()
                print("heads-up sent", key)
    state["heads_up"] = {k: v for k, v in sent.items() if time.time() - v < 3 * 86400}


PULSE_HOURS_NY = {20, 21, 22, 23, 0, 1, 3, 4, 9, 10, 11, 12}   # Asia, London, New York; sent only if pulse_worth() finds news


def pulse_text(ict, conf, lv, news, df, lines, macro):
    price = float(df["Close"].iloc[-1])
    hour_ago = float(df["Close"].iloc[-13]) if len(df) > 13 else price
    score, word, b = direction(ict, lv, price)
    areas = intraday_areas(lv, conf, price)
    nx = sorted([(datetime.fromisoformat(e["time"].replace("Z", "+00:00")), e["title"]) for e in news.get("events", [])
                 if e.get("impact") == "High" and datetime.fromisoformat(e["time"].replace("Z", "+00:00")) > datetime.now(timezone.utc)])[:1]
    arrow = "↑" if score >= 20 else "↓" if score <= -20 else "↔"
    p = vp_plan(df)
    lv_line = (f"🟡 Plan: {'SELL' if p['side'] == 'SELL' else 'BUY'} {fmt(p['edge'])} (POC) after a 15m close {'below' if p['side'] == 'SELL' else 'above'}"
               if p and p.get("side") and abs(p["edge"] - p["inval"]) <= p["edge"] * 0.006 else "🟡 No plan this session")
    out = [f"⏱ Gold <b>{fmt(price)}</b> ({price - hour_ago:+,.1f} in the last hour) · {word} {arrow}",
           *([lv_line] if lv_line else []),
           *([f"📰 {esc(nx[0][1])} at {local(nx[0][0].timestamp())}"] if nx and (nx[0][0] - datetime.now(timezone.utc)).total_seconds() < 6 * 3600 else [])]
    return "\n".join(out)


def pulse_send(ict, conf, lv, news, df, lines, macro, why):
    text = pulse_text(ict, conf, lv, news, df, lines, macro).replace("\n", f" · 🔔 {why}\n", 1)
    try:
        price = float(df["Close"].iloc[-1])
        sc, wd, _ = direction(ict, lv, price)
        card(df, price, wd, sc, plan_areas(df), "pulse_card.png", f"GOLD · UPDATE · {local(time.time())}")
        return send_photo("pulse_card.png", text, "Gold pulse")
    except Exception as e:
        print("pulse card failed:", e)
        return send(text, "Gold pulse")


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
        return "today's first update"
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
    out = [f"📊 <b>WEEKLY PROOF · week of {week_start.astimezone(local_tz()):%d %b}</b>",
           f"Gold {fmt(w_open)} → {fmt(price)} ({price - w_open:+,.1f} this week)", "", "<b>Real BUY/SELL signals this week</b>"]
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
    out += ["", "<b>Live record since launch</b>"]
    if done:
        R = [a["R"] for a in done]
        out.append(f"{len(done)} closed · {sum(r > 0 for r in R)} won · {round(100 * sum(r > 0 for r in R) / len(R))}% · "
                   f"{sum(R):+.2f}R total ({sum(R) / len(R):+.2f}R per trade)")
    else:
        out.append("No closed signals yet.")
    if m:
        out.append(f"Backtest for comparison: {m.get('trades')} trades, {m.get('win_rate_pct')}% won, {m.get('avg_R', 0):+.2f}R per trade.")
    pw = [a for a in log if a.get("kind") == "plan" and a.get("created", 0) >= ws and a.get("R") is not None]
    if pw:
        pR = [a["R"] for a in pw]
        out += ["", f"<b>Plan trades this week</b>: {len(pR)} · {sum(r > 0 for r in pR)} won · {sum(pR):+.2f}R"]
    aw = [x for x in alog if x.get("closed", 0) >= ws]
    if aw:
        h = sum(x["result"] == "held" for x in aw)
        out += ["", f"<b>🟠 Watch areas this week</b>: {h} held, {len(aw) - h} broke."]
        if alog:
            H = sum(x["result"] == "held" for x in alog)
            out.append(f"All time: {H} of {len(alog)} held ({round(100 * H / len(alog))}%).")
    try:
        from cot import cot_line
        cl = cot_line(jl("cot.json"))
        if cl:
            out += ["", esc(cl)]
    except Exception:
        pass
    out += ["", "<i>R = profit measured in risk units: +1R means you made what you risked. "
                "1 week is a small sample; judge the record over months.</i>"]
    if LANG == "km":
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
        intraday_alerts(df, lv, conf, ict, state, news)   # old 🟠 alerts: off unless INTRADAY_ALERTS=on
        if os.environ.get("LEVEL_ALERTS") == "on":   # level heads-ups had no edge in testing: off
            near_level_alert(df, lv, conf, ict, state)
        pre_news(news, state)
        macro_shift(macro, news, state)
    except Exception as e:
        print("level alerts failed:", e)
    due = due_session(state, datetime.now(timezone.utc)) if not os.environ.get("SESSION_FORCE") else \
        (os.environ["SESSION_FORCE"], "forced|" + os.environ["SESSION_FORCE"], datetime.now(timezone.utc))
    if due:
        name, key, start = due
        text = briefing_text(name, ict, conf, lv, news, df, lines, start, macro)
        path = "session_plan.png"
        analysis_chart(df, lv, conf, lines, path, f"Gold · {name} session plan · {local(time.time())}")
        import html as _h, re as _re
        if len(_h.unescape(_re.sub(r"<[^>]+>", "", text))) <= 1024:     # Telegram counts visible characters
            mid = send_photo(path, text, f"{name} session")
        else:   # Telegram captions are limited: photo with the headline, then the full briefing as a reply
            mid = send_photo(path, text.split("\n\n")[0], f"{name} session")
            if mid:
                send(text, f"{name} session", reply_to=mid)
        if name == "Asia" or os.environ.get("MACRO_CARD_FORCE"):   # fundamentals as a picture, once a day with the morning prep
            try:
                mc = macro_card(macro, news, "macro_card.png", jl("cot.json"))
                if mc:
                    send_photo(mc[0], mc[1], "Fundamentals", reply_to=mid if isinstance(mid, int) else None)
                    state["macro_snap"] = macro_snapshot(macro)
            except Exception as e:
                print("macro card failed:", e)
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
        elif pulse_send(ict, conf, lv, news, df, lines, macro, why) or not os.environ.get("TELEGRAM_TOKEN"):
            state.setdefault("pulsed", {})[pk] = time.time()
            state["pulsed"] = {k: v for k, v in state["pulsed"].items() if time.time() - v < 3 * 86400}
            print("pulse sent", pk)
    try:
        site_file(df, lv, conf, ict, news, macro, state)
    except Exception as e:
        print("intraday.json failed:", e)
    loc = datetime.now(local_tz())
    mkey = loc.strftime("%Y-%m-%d")
    if (loc.weekday() < 5 and loc.hour == MAP_HOUR_LOCAL and loc.minute < 25 and mkey not in state.get("map", {})) or os.environ.get("MAP_FORCE"):
        try:
            path, text = market_map(df, lv, lines, "market_map.png")
            if send_photo(path, text, "Market map") or not os.environ.get("TELEGRAM_TOKEN"):
                state.setdefault("map", {})[mkey] = time.time()
                state["map"] = {k: v for k, v in state["map"].items() if time.time() - v < 7 * 86400}
                print("market map sent")
        except Exception as e:
            print("market map failed:", e)
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
            try:
                from cot import cot_line
                cl = cot_line(jl("cot.json"))
                if cl:
                    body += ["", esc(cl)]
            except Exception as e:
                print("cot line failed:", e)
            body += ["", "<i>Rules of thumb, not promises: the surprise versus the forecast matters more than the number itself.</i>"]
            if send("\n".join(body), "Week ahead"):
                state.setdefault("weekly", {})[wk] = time.time()
    json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
