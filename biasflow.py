"""🧭 Bias Flow · Alerts (owner, 27 Nov 2026: "follow ZENN28's model"). Reminders only: no entries, no signals.

Every 15 minutes, after each 15m candle closes (loop.py runs this every 5-minute cycle; it acts once per new 15m candle):
 1. Structure trend for D, H4, H1, M15 from CLOSED candles. Swing pivots: 3 bars each side (confirmed 3 bars later).
    A close above the last swing high = ▲ Bull, a close below the last swing low = ▼ Bear (otherwise unchanged).
 2. Flow: pairs Daily+H4, H4+H1, H1+M15 -> ALIGNED BULLISH / ALIGNED BEARISH / MIXED. When a pair changes:
    🟢/🔴 it became aligned · 🔥 all 3 aligned the same way · ⚪ back to mixed. The post has the table (pair, higher TF,
    lower TF, status, since in UTC+7), the price and the latest Asia / London / New York VAH · POC · VAL
    (New York time: Asia 18:00-02:00, London 02:00-08:00, New York 08:00-17:00; value area 70%, 24 rows, 15m candles).
 3. 👀 Setup watch: H1+M15 aligned + inside a killzone (UTC+7: London 13:30-16:00, NY 19:30-22:30, by the 15m
    candle's open time) + that 15m candle traded through the POC of the session BEFORE the current one.
    At most one per killzone per day.
 Ported from the owner's reference bias_flow_alerts.py (27 Nov 2026): same pivots, sessions, profile, messages and
 guide; data = the bot's own closed spot candles instead of Twelve Data calls.
 4. When the topic is first used: posts and pins the SELL / BUY 5-check guide.
State in biasflow_state.json (committed by loop.py), so a restart never repeats an alert. BIAS_FLOW=off stops it.
Run: python biasflow.py   ·   python biasflow.py --dry  (prints what it would post, sends nothing)
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

TITLE = "bias flow"           # tg.section_for -> the 🧭 Bias Flow · Alerts topic
STATE = "biasflow_state.json"
ICT = ZoneInfo("Asia/Phnom_Penh")
NY = ZoneInfo("America/New_York")
PIVOT = 3
TFS = [("D", "D", pd.Timedelta(days=1)), ("H4", "4H", pd.Timedelta(hours=4)),
       ("H1", "1H", pd.Timedelta(hours=1)), ("M15", "15m", pd.Timedelta(minutes=15))]
PAIRS = [("Daily + H4", "D", "H4"), ("H4 + H1", "H4", "H1"), ("H1 + M15", "H1", "M15")]
SESSIONS = [("Asia", 18, 2), ("London", 2, 8), ("New York", 8, 17)]       # New York wall clock, start -> end
KILLZONES = [("London", (13, 30), (16, 0), "Asia"), ("New York", (19, 30), (22, 30), "London")]   # UTC+7, prev session
ROWS, VA = 24, 0.70

GUIDE = """📌 <b>Bias Flow · how it works (easy)</b>

Only 2 kinds of alert:
🔴 / 🟢 <b>Direction</b>: H1 and M15 agree → today look only for SELL (🔴) or BUY (🟢). <b>Don't trade yet.</b>
🔥 = all timeframes agree = the strongest direction.
👀 <b>Get ready</b>: price came back to the key level (POC) inside a killzone → <b>open the 5m chart now.</b>

<b>On the 5m chart (only after 👀):</b>
1️⃣ Price grabs liquidity: takes a high (for SELL) or a low (for BUY) = $ swept
2️⃣ A strong candle turns the other way = CISD
3️⃣ Enter on the pullback into the gap (FVG) · SL beyond the sweep · TP at least 2R
❌ No reaction, big news within 15 min, or SL too big = <b>no trade</b>

⏰ Killzones (Cambodia time): London 13:30–16:00 · New York 19:30–22:30

🇰🇭 <b>ងាយៗ</b>
🔴/🟢 = ទិសថ្ងៃនេះ (រកតែ SELL ឬ BUY) · មិនទាន់ចូល
👀 = តម្លៃមកដល់ POC ក្នុង killzone → បើក chart 5m
5m: $ swept → CISD → ចូលនៅ FVG · គ្មានប្រតិកម្ម = មិនចូល

<i>Alert = reminder. The decision is yours · ការអប់រំ មិនមែនដំបូន្មាន</i>"""


# ------------------------------------------------------------------ logic
def closed_tf(df, rule, span, now):
    """Candles of this timeframe that have fully closed by `now` (5m data must be closed candles already)."""
    import ict
    if rule == "4H":   # like TradingView / ZENN28: 4H candles start at 18:00 New York (06:00 / 10:00 / 14:00 ... UTC+7 in winter)
        x = df.copy()
        x.index = x.index.tz_convert(NY) + pd.Timedelta(hours=6)
        d = x.resample("4h").agg(ict.AGG).dropna()
        d.index = (d.index - pd.Timedelta(hours=6)).tz_convert("UTC")
    else:
        d = ict.resample(df, rule)
    return d[d.index + span <= now]


def trend(d):
    """(state 'bull'/'bear'/None, time the state began = close time of the breaking candle) from closed candles."""
    h, l, c = d["High"].to_numpy(), d["Low"].to_numpy(), d["Close"].to_numpy()
    sh = sl = None
    state, since = None, None
    for j in range(len(d)):
        k = j - PIVOT                       # the pivot at k is confirmed once bar k+3 has closed
        if k >= PIVOT:
            if h[k] == h[k - PIVOT:k + PIVOT + 1].max():
                sh = h[k]
            if l[k] == l[k - PIVOT:k + PIVOT + 1].min():
                sl = l[k]
        new = "bull" if sh is not None and c[j] > sh else "bear" if sl is not None and c[j] < sl else state
        if new != state:
            state, since = new, j
    return state, since


def trends(df, now):
    out = {}
    for name, rule, span in TFS:
        d = closed_tf(df, rule, span, now)
        st, j = trend(d)
        out[name] = {"state": st, "since": float(d.index[j].timestamp()) if j is not None else None}
    return out


def pairs(tr):
    res = []
    for label, hi, lo in PAIRS:
        a, b = tr[hi], tr[lo]
        status = ("ALIGNED BULLISH" if a["state"] == "bull" == b["state"] else
                  "ALIGNED BEARISH" if a["state"] == "bear" == b["state"] else "MIXED")
        since = max([x for x in (a["since"], b["since"]) if x is not None], default=None)
        res.append({"pair": label, "hi": hi, "lo": lo, "status": status, "since": since})
    return res


def profile(d):
    """VAH, POC, VAL of 15m candles: 24 rows from the low to the high, each candle's volume spread evenly over the
    rows it traded through, value area 70% grown from the POC towards the bigger neighbour."""
    if len(d) == 0:
        return None
    lo, hi = float(d["Low"].min()), float(d["High"].max())
    if hi <= lo:
        return None
    step = (hi - lo) / ROWS
    vol = np.zeros(ROWS)
    for h_, l_, v in zip(d["High"], d["Low"], d["Volume"].fillna(0)):
        a, b = int((l_ - lo) / step), int(min(ROWS - 1, (h_ - lo) / step))
        vol[a:b + 1] += (v if v > 0 else 1.0) / (b - a + 1)
    p = int(vol.argmax())
    top = bot = p
    acc, total = vol[p], vol.sum()
    while acc < VA * total and (top < ROWS - 1 or bot > 0):
        up = vol[top + 1] if top < ROWS - 1 else -1
        dn = vol[bot - 1] if bot > 0 else -1
        if up >= dn:
            top += 1; acc += up
        else:
            bot -= 1; acc += dn
    return {"vah": lo + (top + 1) * step, "poc": lo + (p + 0.5) * step, "val": lo + bot * step}


def session_of(t):
    h = t.astimezone(NY).hour
    return "Asia" if (h >= 18 or h < 2) else "London" if h < 8 else "New York" if h < 17 else None


def blocks(d15):
    """Consecutive runs of 15m candles in the same session (by the candle's open time, New York clock)."""
    out, cur, name = [], [], None
    for t in d15.index:
        s_ = session_of(t)
        if s_ != name:
            if cur and name:
                out.append((name, cur))
            cur, name = [], s_
        if s_:
            cur.append(t)
    if cur and name:
        out.append((name, cur))
    return out


def sessions(d15, now=None):
    """Latest Asia / London / New York block (the current one may still be developing) -> VAH / POC / VAL."""
    bl = blocks(d15)
    cur = session_of(d15.index[-1]) if len(d15) else None
    out = {}
    for name, ts in bl:
        if len(ts) >= 3:
            vp = profile(d15.loc[ts])
            if vp:
                vp["live"] = name == cur and ts[-1] == d15.index[-1]
                out[name] = vp
    return out


def prev_session_poc(d15):
    """POC of the session BEFORE the one we are in now (Asia -> for London, London -> for New York ...)."""
    bl = blocks(d15)
    if session_of(d15.index[-1]) is not None and bl:
        bl = bl[:-1]                         # drop the current (developing) block
    if not bl:
        return None, None
    name, ts = bl[-1]
    vp = profile(d15.loc[ts]) if len(ts) >= 3 else None
    return (name, vp["poc"]) if vp else (None, None)


def killzone(t_ict):
    """Killzone of a 15m candle by its OPEN time (UTC+7), start included, end excluded."""
    hm = t_ict.strftime("%H:%M")
    for name, (h0, m0), (h1, m1), _ in KILLZONES:
        if f"{h0:02d}:{m0:02d}" <= hm < f"{h1:02d}:{m1:02d}":
            return name
    return None


# ------------------------------------------------------------------ text
ARROW = {"bull": "▲ Bull", "bear": "▼ Bear", None: "· none"}
SHORT = {"Daily + H4": "D+H4", "H4 + H1": "H4+H1", "H1 + M15": "H1+M15"}
ST_SHORT = {"ALIGNED BULLISH": "ALIGNED ▲", "ALIGNED BEARISH": "ALIGNED ▼", "MIXED": "MIXED"}


def fmt(x):
    return f"{x:,.2f}"


def when(ts):
    return datetime.fromtimestamp(ts, ICT).strftime("%d %b %H:%M") if ts else "-"


def arrow(x):
    return "▲" if x == "bull" else "▼" if x == "bear" else "–"


COOLDOWN_H = 6          # the same direction is not re-posted within 6 hours (H1+M15 often flickers)


def tf_line(tr):
    return " · ".join(f"{k} {arrow(tr[k]['state'])}" for k in ("D", "H4", "H1", "M15"))


def direction_post(bull, tr, pr, price, pnm, poc):
    full = len({p["status"] for p in pr}) == 1
    n = sum(tr[k]["state"] == ("bull" if bull else "bear") for k in ("D", "H4", "H1", "M15"))
    side = "BUY" if bull else "SELL"
    head = (f"🔥 <b>STRONG {side} DAY · all timeframes agree</b>" if full else
            f"{'🟢' if bull else '🔴'} <b>{side} bias · H1 + M15 aligned {'BULLISH' if bull else 'BEARISH'}</b>")
    mark = lambda p: "✅" if p["status"] == ("ALIGNED BULLISH" if bull else "ALIGNED BEARISH") else "–"
    lines = [head,
             f"🇰🇭 {'ទិសឡើង · រកតែ BUY · កុំ SELL' if bull else 'ទិសចុះ · រកតែ SELL · កុំ BUY'}",
             f"H4-H1 {mark(pr[1])} · H1-M15 {mark(pr[2])} · Daily-H4 {mark(pr[0])}",
             f"{tf_line(tr)}  ·  strength {n}/4",
             f"💰 Price <b>{price:,.2f}</b>"]
    if poc:
        lines.append(f"🎯 Wait for price to come back {'DOWN' if bull else 'UP'} to <b>{poc:,.2f}</b> ({pnm} POC) "
                     f"in a killzone (London 13:30–16:00 · NY 19:30–22:30)")
    lines += ["👀 You'll get a <b>Get ready</b> alert when it's there. Don't trade yet.",
              "<i>Reminder, not a signal · you decide</i>"]
    return "\n".join(lines)


def joined_post(bull, tr, pr, price, pnm, poc):
    """H4 + H1 lines up with an H1 + M15 flow already running: the bigger picture agrees (ZENN28's two ✅)."""
    side = "BUY" if bull else "SELL"
    lines = [f"{'🟢🟢' if bull else '🔴🔴'} <b>H4-H1 {'BULLISH' if bull else 'BEARISH'} aligned ✅ · H1-M15 ✅</b>",
             f"🇰🇭 timeframe ធំក៏ស្រប · រកតែ {side} · កុំតាម{'ទិញ' if bull else 'លក់'}ពេលវារត់ហើយ",
             f"{tf_line(tr)}  ·  price <b>{price:,.2f}</b>",
             "⛔ Don't chase a market that already ran. Wait for the pullback, then a setup."]
    if poc:
        lines.append(f"🎯 Pullback zone: <b>{poc:,.2f}</b> ({pnm} POC) in a killzone → 👀 alert")
    lines.append("<i>Reminder, not a signal · you decide</i>")
    return "\n".join(lines)


def ready_plan(bull, poc):
    """The 💊 coach's plan for the Get-ready level: entry at the POC, SL behind the stop pool, TP, lot. Never raises."""
    try:
        import coach
        ctx = coach.context()
        res = coach.evaluate({"side": "BUY" if bull else "SELL", "entry": round(poc, 2), "sl": None, "tp": None}, ctx)
        t = res["trade"]
        risk = abs(t["entry"] - t["sl"])
        return (f"📋 Ready plan: {'BUY' if bull else 'SELL'} {t['entry']:,.2f} · SL <b>{t['sl']:,.2f}</b> · TP <b>{t['tp']:,.2f}</b> "
                f"(RR {res['rr']:.1f}) · {coach.lot(risk)}\n<i>Only after the 5m reaction. Price moved on? Send it to the 💊 coach.</i>")
    except Exception as e:
        print("bias flow: ready plan failed:", e)
        return None


def watch_post(kz, pnm, status, poc, price):
    bull = "BULL" in status
    side = "BUY" if bull else "SELL"
    return "\n".join([
        f"👀 <b>GET READY · {side}</b>",
        f"Price is at the <b>{pnm} POC {poc:,.2f}</b> in the {kz} killzone (now {price:,.2f}).",
        "Open the 5m chart and wait for:",
        f"1️⃣ price takes a {'low' if bull else 'high'} ($ swept)",
        f"2️⃣ a strong candle {'up' if bull else 'down'} (CISD)",
        f"3️⃣ enter on the pullback into the FVG · SL {'below' if bull else 'above'} the sweep",
        "❌ No reaction = no trade.",
        f"🇰🇭 តម្លៃនៅ POC · បើក 5m: $ swept → CISD → ចូល FVG ({'BUY' if bull else 'SELL'}) · គ្មានប្រតិកម្ម = មិនចូល",
        "<i>Reminder, not a signal · you decide</i>",
    ])


# ------------------------------------------------------------------ run
def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def main(dry=False, df=None, now=None):
    if os.environ.get("BIAS_FLOW", "on") == "off":
        print("bias flow: off"); return
    import tg
    from engine import closed, load
    st = jl(STATE, {})
    send = (lambda text: print("---\n" + text) or 1) if dry else (lambda text: tg.send(text, TITLE))
    live = df is None
    if live and not dry and not (os.environ.get("TELEGRAM_TOKEN") and tg.group_id()):
        print("bias flow: no Telegram group/secrets"); return
    import hashlib
    gh = hashlib.sha1(GUIDE.encode()).hexdigest()[:10]
    if not dry and st.get("guide") and st.get("guide_hash") != gh:   # guide text changed: edit the pinned message
        try:
            chat, _ = tg.target(TITLE)
            tg._api("editMessageText", {"chat_id": chat, "message_id": st["guide"], "text": GUIDE, "parse_mode": "HTML",
                                        "disable_web_page_preview": "true"})
            st["guide_hash"] = gh
            json.dump(st, open(STATE, "w"), indent=1)
            print("bias flow: pinned guide updated")
        except Exception as e:
            print("bias flow: guide edit failed:", e)
    if not dry and not st.get("guide"):
        mid = tg.send(GUIDE, TITLE)
        if not mid:
            print("bias flow: guide post failed"); return
        st["guide"], st["guide_hash"] = mid, gh
        try:
            chat, _ = tg.target(TITLE)
            tg._api("pinChatMessage", {"chat_id": chat, "message_id": mid, "disable_notification": "true"})
            st["guide_pinned"] = True
        except Exception as e:
            print("bias flow: pin failed (give the bot 'Pin messages'):", e)
        json.dump(st, open(STATE, "w"), indent=1)
    if df is None:
        df = load("5m", "120d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    now = pd.Timestamp(time.time() if now is None else now, unit="s", tz="UTC")
    df = closed(df, 5, now=now.timestamp())
    df = df[df["Volume"] >= 0]
    d15 = closed_tf(df, "15m", pd.Timedelta(minutes=15), now)
    if len(d15) < 50:
        print("bias flow: not enough data"); return
    last15 = float((d15.index[-1] + pd.Timedelta(minutes=15)).timestamp())
    if st.get("last15") == last15 and not dry:
        print("bias flow: waiting for the next 15m close"); return
    if now.timestamp() - last15 > 40 * 60:
        print("bias flow: data is stale (market closed?)"); st["last15"] = last15
        json.dump(st, open(STATE, "w"), indent=1); return
    tr = trends(df, now)
    pr = pairs(tr)
    price = float(d15["Close"].iloc[-1])
    vp = sessions(d15)
    old = st.get("pairs")
    status = {p["pair"]: p["status"] for p in pr}
    pnm, poc = prev_session_poc(d15)
    if old is None:
        print("bias flow: first run, flow saved; alerts start from the next change")
    else:
        # only what matters (owner, 27 Nov): H1+M15 turning aligned, or all 3 pairs turning aligned. No "mixed" posts.
        new = pr[2]["status"]
        full_now = len(set(status.values())) == 1 and new != "MIXED"
        full_before = len(set(old.values())) == 1 and old.get("H1 + M15") != "MIXED"
        turned = new != "MIXED" and old.get("H1 + M15") != new
        last = st.get("last_dir", {})
        cool = turned and last15 - last.get(new, 0) < COOLDOWN_H * 3600 and not (full_now and not full_before)
        if (turned and not cool) or (full_now and not full_before):
            mid = send(direction_post(new == "ALIGNED BULLISH", tr, pr, price, pnm, poc))
            if not mid and not dry:
                print("bias flow: post failed, will retry next cycle"); return
            st["last_dir"] = dict(last, **{new: last15})
            print("bias flow: posted direction", new, "all3" if full_now else "")
        elif turned:
            print("bias flow: same direction again within", COOLDOWN_H, "h: not re-posted")
        h4h1 = pr[1]["status"]
        jkey = f"{datetime.fromtimestamp(last15, ICT):%Y-%m-%d}|{h4h1}"
        if (h4h1 != "MIXED" and h4h1 == new and old.get("H4 + H1") != h4h1 and not (full_now and not full_before)
                and jkey not in st.get("joined", [])):
            mid = send(joined_post(h4h1 == "ALIGNED BULLISH", tr, pr, price, pnm, poc))
            if mid or dry:
                st["joined"] = (st.get("joined", []) + [jkey])[-10:]
                print("bias flow: H4+H1 joined", h4h1)
    # 👀 setup watch (ZENN28): H1+M15 aligned · killzone · this 15m candle traded through the previous session's POC
    h1m15 = pr[2]["status"]
    t_open = datetime.fromtimestamp(d15.index[-1].timestamp(), ICT)
    kz = killzone(t_open)
    if kz and h1m15 != "MIXED" and poc:
        key = f"{t_open:%Y-%m-%d}|{kz}"          # at most one per killzone per day
        bar = d15.iloc[-1]
        if key not in st.get("watch", []) and bar["Low"] <= poc <= bar["High"]:
            plan = ready_plan("BULL" in h1m15, poc)
            mid = send(watch_post(kz, pnm, h1m15, poc, price) + (f"\n{plan}" if plan else ""))
            if mid or dry:
                st["watch"] = (st.get("watch", []) + [key])[-20:]
                print("bias flow: setup watch", key)
    st.update(pairs=status, last15=last15, trends=tr, t=time.time())
    if not dry:
        json.dump(st, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
