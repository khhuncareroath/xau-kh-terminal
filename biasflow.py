"""🧭 Bias Flow · Alerts (owner, 27 Nov 2026: "follow ZENN28's model"). Reminders only: no entries, no signals.

Every 15 minutes, after each 15m candle closes (loop.py runs this every 5-minute cycle; it acts once per new 15m candle):
 1. Structure trend for D, H4, H1, M15 from CLOSED candles. Swing pivots: 3 bars each side (confirmed 3 bars later).
    A close above the last swing high = ▲ Bull, a close below the last swing low = ▼ Bear (otherwise unchanged).
 2. Flow: pairs Daily+H4, H4+H1, H1+M15 -> ALIGNED BULLISH / ALIGNED BEARISH / MIXED. When a pair changes:
    🟢/🔴 it became aligned · 🔥 all 3 aligned the same way · ⚪ back to mixed. The post has the table (pair, higher TF,
    lower TF, status, since in UTC+7), the price and the latest Asia / London / New York VAH · POC · VAL
    (New York time: Asia 18:00-02:00, London 02:00-08:00, New York 08:00-17:00; value area 70%, 24 rows, 15m candles).
 3. 👀 Setup watch: H1+M15 aligned + inside a killzone (UTC+7: London 13:30-16:00, NY 19:30-22:30) + the last 15m
    candle traded through the POC of the previous session (London killzone: Asia POC; NY killzone: London POC).
    At most one per killzone per day.
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

GUIDE = (
    "🧭 <b>Bias Flow · Alerts: how to use them</b>\n"
    "<i>The alert only reminds you to look. You check, you decide. No reaction = no trade.</i>\n"
    "ការជូនដំណឹងគ្រាន់តែរំលឹកឱ្យមើល · អ្នកពិនិត្យ និងសម្រេចចិត្តខ្លួនឯង\n\n"
    "🔴 <b>SELL: 5 checks</b>\n"
    "1️⃣ Flow: <b>H1 + M15 ALIGNED BEARISH</b> (better if H4 or Daily is Bear too)\n"
    "2️⃣ Location: price comes UP into the previous session's <b>POC / VAH</b> (premium)\n"
    "3️⃣ Time: inside a killzone · London 13:30–16:00 · NY 19:30–22:30 (UTC+7)\n"
    "4️⃣ Reaction on 3m–5m: <b>$ swept</b> above a high → <b>CISD</b> down\n"
    "5️⃣ Entry: the bearish <b>FVG</b> after the CISD · SL above the sweep high · TP the next VAL / low\n\n"
    "🟢 <b>BUY: 5 checks</b>\n"
    "1️⃣ Flow: <b>H1 + M15 ALIGNED BULLISH</b> (better if H4 or Daily is Bull too)\n"
    "2️⃣ Location: price comes DOWN into the previous session's <b>POC / VAL</b> (discount)\n"
    "3️⃣ Time: inside a killzone · London 13:30–16:00 · NY 19:30–22:30 (UTC+7)\n"
    "4️⃣ Reaction on 3m–5m: <b>$ swept</b> below a low → <b>CISD</b> up\n"
    "5️⃣ Entry: the bullish <b>FVG</b> after the CISD · SL below the sweep low · TP the next VAH / high\n\n"
    "⛔ Missing one check = no trade · ខ្វះមួយ = មិនចូល\n"
    "🟢🔴 = a pair became aligned · 🔥 = all 3 aligned · ⚪ = back to mixed · 👀 = setup watch (POC touched in a killzone)\n"
    "<i>Education, not financial advice. Always use a stop loss · ការអប់រំ មិនមែនដំបូន្មានហិរញ្ញវត្ថុ</i>"
)


# ------------------------------------------------------------------ logic
def closed_tf(df, rule, span, now):
    """Candles of this timeframe that have fully closed by `now` (5m data must be closed candles already)."""
    import ict
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
        out[name] = {"state": st, "since": float((d.index[j] + span).timestamp()) if j is not None else None}
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


def sessions(d15, now):
    """Latest Asia / London / New York session (started by `now`) -> dict name: {vah, poc, val, live, start}."""
    out = {}
    idx_ny = d15.index.tz_convert(NY)
    now_ny = now.tz_convert(NY)
    for name, s, e in SESSIONS:
        day = now_ny.normalize()
        for back in range(0, 6):           # newest session that has started AND has at least one closed candle
            st = (day - pd.Timedelta(days=back)).replace(hour=s)
            en = (st + pd.Timedelta(days=1)).replace(hour=e) if s > e else st.replace(hour=e)   # Asia: evening -> next day
            if st > now_ny:
                continue
            m = (idx_ny >= st) & (idx_ny < en)
            vp = profile(d15[m])
            if vp:
                vp.update(live=now_ny < en, start=float(st.timestamp()), end=float(en.timestamp()))
                out[name] = vp
                break
    return out


def killzone(t_ict):
    for name, (h0, m0), (h1, m1), prev in KILLZONES:
        a = t_ict.replace(hour=h0, minute=m0, second=0, microsecond=0)
        b = t_ict.replace(hour=h1, minute=m1, second=0, microsecond=0)
        if a <= t_ict <= b:
            return name, prev
    return None, None


# ------------------------------------------------------------------ text
ARROW = {"bull": "▲ Bull", "bear": "▼ Bear", None: "· none"}
SHORT = {"Daily + H4": "D+H4", "H4 + H1": "H4+H1", "H1 + M15": "H1+M15"}
ST_SHORT = {"ALIGNED BULLISH": "ALIGNED ▲", "ALIGNED BEARISH": "ALIGNED ▼", "MIXED": "MIXED"}


def fmt(x):
    return f"{x:,.2f}"


def when(ts):
    return datetime.fromtimestamp(ts, ICT).strftime("%d %b %H:%M") if ts else "-"


def table(tr, pr):
    rows = [f"{'Pair':<7}{'Higher':<10}{'Lower':<11}{'Status':<10}Since"]
    for p in pr:
        rows.append(f"{SHORT[p['pair']]:<7}{(p['hi'] + ' ' + ARROW[tr[p['hi']]['state']]):<10}"
                    f"{(p['lo'] + ' ' + ARROW[tr[p['lo']]['state']]):<11}{ST_SHORT[p['status']]:<10}{when(p['since'])}")
    return "<pre>" + "\n".join(rows) + "</pre>"


def vp_lines(vp):
    out = ["📊 <b>Session value · VAH · POC · VAL</b>"]
    for name, _, _ in SESSIONS:
        v = vp.get(name)
        if v:
            out.append(f"{'🌏' if name == 'Asia' else '🇬🇧' if name == 'London' else '🇺🇸'} {name}: "
                       f"{fmt(v['vah'])} · <b>{fmt(v['poc'])}</b> · {fmt(v['val'])}" + (" <i>(live)</i>" if v["live"] else ""))
    return out


def flow_post(changes, tr, pr, price, t_ict, vp):
    al = [p["status"] for p in pr]
    head = []
    if al.count("ALIGNED BULLISH") == 3 or al.count("ALIGNED BEARISH") == 3:
        bull = al[0] == "ALIGNED BULLISH"
        head.append(f"🔥 <b>ALL 3 ALIGNED {'BULLISH' if bull else 'BEARISH'}</b> · D, H4, H1, M15 all {'▲ Bull' if bull else '▼ Bear'}")
        head.append("🇰🇭 គ្រប់ timeframe ទិសដូចគ្នា · " + ("ទិញ (BUY) ប៉ុណ្ណោះ" if bull else "លក់ (SELL) ប៉ុណ្ណោះ") + " តាមលក្ខខណ្ឌ 5 ចំណុច")
    else:
        for p in changes:
            if p["status"] == "MIXED":
                head.append(f"⚪ <b>{p['pair']} back to MIXED</b>")
            else:
                bull = p["status"] == "ALIGNED BULLISH"
                head.append(f"{'🟢' if bull else '🔴'} <b>{p['pair']} {p['status']}</b>")
        km = [("ទិសឡើង" if p["status"] == "ALIGNED BULLISH" else "ទិសចុះ" if p["status"] == "ALIGNED BEARISH" else "ចម្រុះ (រង់ចាំ)")
              for p in changes]
        head.append("🇰🇭 " + " · ".join(f"{SHORT[p['pair']]}: {k}" for p, k in zip(changes, km)))
    return "\n".join(head + [f"💰 Gold <b>{fmt(price)}</b> · {t_ict:%H:%M} UTC+7", table(tr, pr)] + vp_lines(vp)
                     + ["<i>Reminder only, not a signal · you check, you decide</i>"])


def watch_post(kz, prev, p, poc, price, t_ict):
    bull = p["status"] == "ALIGNED BULLISH"
    return "\n".join([
        f"👀 <b>Setup watch · {kz} killzone</b>",
        f"H1 + M15 <b>{p['status']}</b> · the last 15m candle traded through the <b>{prev} POC {fmt(poc)}</b>",
        f"💰 Gold <b>{fmt(price)}</b> · {t_ict:%H:%M} UTC+7",
        "",
        f"⏳ Wait for the reaction on 3m–5m: <b>$ swept → CISD → FVG entry</b>. No reaction = no trade.",
        f"🇰🇭 រង់ចាំប្រតិកម្មលើ 3m–5m: $ swept → CISD → ចូលនៅ FVG · គ្មានប្រតិកម្ម = មិនចូល",
        f"{'🟢 Look for BUY reactions only' if bull else '🔴 Look for SELL reactions only'} · check the 5 points in the pinned guide",
        "<i>Reminder only, not a signal · you decide</i>",
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
    if not dry and not st.get("guide"):
        mid = tg.send(GUIDE, TITLE)
        if not mid:
            print("bias flow: guide post failed"); return
        st["guide"] = mid
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
    t_ict = datetime.fromtimestamp(last15, ICT)
    vp = sessions(d15, pd.Timestamp(last15, unit="s", tz="UTC"))
    old = st.get("pairs")
    status = {p["pair"]: p["status"] for p in pr}
    if old is None:
        print("bias flow: first run, saving the current flow without posting")
    else:
        changes = [p for p in pr if old.get(p["pair"]) != p["status"]]
        if changes:
            mid = send(flow_post(changes, tr, pr, price, t_ict, vp))
            if not mid and not dry:
                print("bias flow: post failed, will retry next cycle"); return
            print("bias flow: posted", [(p["pair"], p["status"]) for p in changes])
    # 👀 setup watch
    h1m15 = pr[2]
    kz, prev = killzone(t_ict)
    if kz and h1m15["status"] != "MIXED" and vp.get(prev):
        key = f"{t_ict:%Y-%m-%d}|{kz}"
        poc = vp[prev]["poc"]
        bar = d15.iloc[-1]
        if key not in st.get("watch", []) and bar["Low"] <= poc <= bar["High"]:
            mid = send(watch_post(kz, prev, h1m15, poc, price, t_ict))
            if mid or dry:
                st["watch"] = (st.get("watch", []) + [key])[-20:]
                print("bias flow: setup watch", key)
    st.update(pairs=status, last15=last15, trends=tr, t=time.time())
    if not dry:
        json.dump(st, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
