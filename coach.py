"""💊 XAU.KH Coach: the owner's private trade partner in Telegram (owner, 27 Nov 2026).

Type your idea like to a friend ("sell 3575 sl 3582 tp 3555 London POC", Khmer or English) and/or send a screenshot.
Reply = 1 picture (your trade drawn on the live chart with the real levels and the flow) + 3 lines:
  GO / WAIT / NO  ·  👁 the ONE thing you missed  ·  ✅ the realistic better option (+ lot size)
/scan = "can I trade now?" with no input: READY SELL / READY BUY / WAIT + the zones to watch.

Code decides, never the AI: every number comes from live 5m spot candles (Bias Flow trends, session VAH/POC/VAL,
session and swing highs/lows = stop pools, news, A+/B+ signals). "Reached x/10" = how often gold got that far from
the current price, at this time of day, before the session ended, in the last 90 days.
The AI (free: Gemini + an OpenRouter model) only reads the screenshot and understands casual text; 2 models vote.

🛡 Calm guard: no SL = NO (it places one for you if you leave it out) · 30 min pause after a loss · 2 losses = done
for today · max 3 taken trades a day. Wins/losses are known automatically: the ✅ I took it button saves the trade
(private Supabase table, tradecheck.py) and tradecheck.grade() follows it on the candles.

Owner only (TELEGRAM_OWNER_CHAT_ID). Secrets: GEMINI_API_KEY, OPENROUTER_API_KEY (both optional, free).
Variables: COACH_ACCOUNT (e.g. 3000) + COACH_RISK (% per trade, default 1) for the lot size.
"""
import base64
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

import tradecheck as tc

KH = timezone(timedelta(hours=7))
PAUSE_MIN, MAX_LOSSES, MAX_TRADES = 30, 2, 3
NEWS_BEFORE, NEWS_AFTER = 30, 15
MIN_RISK, MAX_RISK, MIN_RR = 1.5, 25.0, 1.5
OR_MODELS = [m for m in os.environ.get("OPENROUTER_MODELS", "").split(",") if m] + [
    "qwen/qwen2.5-vl-72b-instruct:free", "meta-llama/llama-4-maverick:free", "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.2-24b-instruct:free"]

HOW = ("💊 <b>Coach</b> · type your idea or send a screenshot:\n"
       "<code>sell 3575 sl 3582 tp 3555 London POC</code>\n"
       "Only BUY/SELL is fine too: I place the SL and TP on real levels.\n"
       "/scan = can I trade now? · /mytrades = your 7-day bill\n"
       "🇰🇭 សរសេរ ទិញ/លក់ + តម្លៃ ឬផ្ញើរូប · /scan = ឥឡូវចូលបានទេ?")


def owner(user):
    return str(user) == str(os.environ.get("TELEGRAM_OWNER_CHAT_ID", "")).strip() and os.environ.get("COACH", "on") != "off"


def looks_like_trade(text):
    t = (text or "").lower()
    return bool(re.search(r"\b(buy|sell|long|short)\b", t) or "ទិញ" in t or "លក់" in t)


def f2(x):
    return f"{x:,.2f}"


# ------------------------------------------------------------------ market context (all real data)
def context(now=None):
    import biasflow as bf
    from engine import closed, load
    now_ts = time.time() if now is None else now
    df = load("5m", "120d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = closed(df, 5, now=now_ts)
    df = df[df["Volume"] >= 0]
    now = pd.Timestamp(int(now_ts), unit="s", tz="UTC")   # whole seconds: the candle index can't hold fractions
    d15 = bf.closed_tf(df, "15m", pd.Timedelta(minutes=15), now)
    tr = bf.trends(df, now)
    pr = bf.pairs(tr)
    price = float(df["Close"].iloc[-1])
    a15 = float((d15["High"] - d15["Low"]).tail(96).mean())
    vp = bf.sessions(d15)
    pnm, ppoc = bf.prev_session_poc(d15)
    levels = []   # (price, name, kind)  kind: "pool" = highs/lows where stops sit, "value" = VAH/POC/VAL
    for nm, v in vp.items():
        for k in ("vah", "poc", "val"):
            levels.append((v[k], f"{nm} {k.upper()}", "value"))
    for nm, ts in bf.blocks(d15)[-3:]:   # the latest Asia / London / New York only
        b = d15.loc[ts]
        levels += [(float(b["High"].max()), f"{nm} high", "pool"), (float(b["Low"].min()), f"{nm} low", "pool")]
    ny = d15.copy()
    ny["day"] = (ny.index.tz_convert(bf.NY) + pd.Timedelta(hours=6)).date   # gold day starts 18:00 New York
    days = sorted(ny["day"].unique())
    if len(days) >= 2:
        pdy = ny[ny["day"] == days[-2]]
        levels += [(float(pdy["High"].max()), "Yesterday high", "pool"), (float(pdy["Low"].min()), "Yesterday low", "pool")]
    h, l = d15["High"].to_numpy()[-192:], d15["Low"].to_numpy()[-192:]   # 15m swing highs/lows of the last 2 days
    for k in range(3, len(h) - 3):
        if h[k] == h[k - 3:k + 4].max() and h[k + 1:].max() < h[k]:
            levels.append((float(h[k]), "15m swing high", "pool"))
        if l[k] == l[k - 3:k + 4].min() and l[k + 1:].min() > l[k]:
            levels.append((float(l[k]), "15m swing low", "pool"))
    seen, lv = set(), []
    for p, n, k in sorted(levels, key=lambda x: x[0]):
        key = round(p, 0)
        if key not in seen and abs(p - price) < 8 * a15:
            seen.add(key)
            lv.append((p, n, k))
    return dict(df=df, d15=d15, now=now, tr=tr, pr=pr, price=price, a15=a15, vp=vp, prev=(pnm, ppoc), levels=lv,
                kz=bf.killzone(datetime.fromtimestamp(d15.index[-1].timestamp(), KH)), reach=_reach_table(df, now))


def _reach_table(df, now):
    """For starts at this time of day (±1 h) on the last 90 days: how far gold went up / down before the session end."""
    import biasflow as bf
    c, h, l = df["Close"], df["High"], df["Low"]
    ny_now = now.tz_convert(bf.NY)
    end_h = {"Asia": 2, "London": 8, "New York": 17}.get(bf.session_of(now) or "", (ny_now.hour + 4) % 24)
    horizon = max(2, min(8, (end_h - ny_now.hour) % 24 or 4))
    ups, dns = [], []
    for back in range(1, 91):
        t = now - pd.Timedelta(days=back)
        if t.tz_convert(bf.NY).weekday() == 5:
            continue
        for off in (-60, 0, 60):
            t0 = t + pd.Timedelta(minutes=off)
            i = int(df.index.searchsorted(t0))
            j = int(df.index.searchsorted(t0 + pd.Timedelta(hours=horizon)))
            if i <= 0 or j - i < 6 or abs((df.index[i] - t0).total_seconds()) > 900:
                continue
            p0 = float(c.iloc[i - 1])
            ups.append(float(h.iloc[i:j].max()) - p0)
            dns.append(p0 - float(l.iloc[i:j].min()))
    return np.array(ups), np.array(dns), horizon


def reach(ctx, level):
    """How often (out of 10) gold got from the current price to `level` in the time left, at this time of day."""
    ups, dns, _ = ctx["reach"]
    d = level - ctx["price"]
    arr = ups if d > 0 else dns
    if len(arr) < 20:
        return None
    return int(round(10 * float((arr >= abs(d)).mean())))


# ------------------------------------------------------------------ the brain
def _flow(ctx):
    st = ctx["pr"][2]["status"]
    return 1 if st == "ALIGNED BULLISH" else -1 if st == "ALIGNED BEARISH" else 0


def zones(ctx, S, need=5):
    """Real levels on the side where an S trade would enter (above price for SELL, below for BUY), nearest first,
    that price reached at least `need`/10 times."""
    p = ctx["price"]
    out = []
    for lvl, nm, k in ctx["levels"]:
        if (lvl - p) * S >= 0 or abs(lvl - p) < 0.15 * ctx["a15"]:
            continue
        r = reach(ctx, lvl)
        if r is not None and r >= need:
            out.append((lvl, nm, k, r))
    return sorted(out, key=lambda z: abs(z[0] - p))


def place(ctx, S, E):
    """SL beyond the nearest stop pool behind the entry (+ buffer), TP at the next real level giving >= 1.5R (else 2R)."""
    buf = max(2.0, 0.4 * ctx["a15"])
    behind = sorted([x for x in ctx["levels"] if (x[0] - E) * S < 0 and x[2] == "pool"], key=lambda x: abs(x[0] - E))
    sl = None
    for lvl, nm, _ in behind:
        cand = lvl - S * buf
        if MIN_RISK <= abs(E - cand) <= MAX_RISK:
            sl = round(cand, 2)
            break
    if sl is None:
        sl = round(E - S * max(MIN_RISK * 2, 1.2 * ctx["a15"]), 2)
    risk = abs(E - sl)
    ahead = sorted([x for x in ctx["levels"] if (x[0] - E) * S > 0], key=lambda x: abs(x[0] - E))
    tp = next((round(lvl, 2) for lvl, nm, _ in ahead if abs(lvl - E) >= MIN_RR * risk), round(E + S * 2 * risk, 2))
    return sl, tp


def lot(risk_usd_per_oz):
    acc = float(os.environ.get("COACH_ACCOUNT", 0) or 0)
    pct = float(os.environ.get("COACH_RISK", 1) or 1)
    if acc <= 0 or risk_usd_per_oz <= 0:
        return f"0.01 lot risks ${risk_usd_per_oz:,.2f}"
    lots = max(0.01, int(acc * pct / 100 / (risk_usd_per_oz * 100) * 100) / 100)
    return f"lot <b>{lots:.2f}</b> ({pct:g}% of ${acc:,.0f})"


def guard(user):
    """Calm guard from the private trade table. -> (blocked reason or None)."""
    if not tc.SB_URL:
        return None
    since = tc._since_kh_midnight()
    rows = tc._sb("GET", f"trade_checks?select=status,taken,closed_at&tg_user=eq.{int(user)}&created_at=gte.{since}") or []
    losses = [r for r in rows if r.get("status") == "loss"]
    if len(losses) >= MAX_LOSSES:
        return f"{len(losses)} losses today. Done for today, the market is open again tomorrow · ថ្ងៃនេះឈប់"
    last = max((pd.Timestamp(r["closed_at"]) for r in losses if r.get("closed_at")), default=None)
    if last is not None:
        left = PAUSE_MIN - (pd.Timestamp.now(tz="UTC") - last.tz_convert("UTC")).total_seconds() / 60
        if left > 0:
            return f"You just lost a trade. Pause {left:.0f} more min: no revenge trade · សម្រាក {left:.0f} នាទី"
    if sum(1 for r in rows if r.get("taken")) >= MAX_TRADES:
        return f"{MAX_TRADES} trades taken today. Enough: overtrading kills accounts · គ្រប់ហើយថ្ងៃនេះ"
    return None


def news(ctx):
    now = ctx["now"].timestamp()
    for e in tc._jl("news.json").get("events", []):
        if str(e.get("impact", "")).lower() != "high":
            continue
        try:
            t = datetime.fromisoformat(e["time"].replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        if -NEWS_AFTER * 60 <= t - now <= NEWS_BEFORE * 60:
            return e.get("title", "news"), t
    return None


def active_signal():
    for a in reversed(tc._jl("alerts_log.json", [])):
        if a.get("kind") == "model" and a.get("status") in ("pending", "filled") and time.time() - a.get("created", 0) < 12 * 3600:
            return a
    return None


def evaluate(trade, ctx, user=None, ai=None):
    """-> dict(verdict GO|WAIT|NO, missed, better, plan, notes). Code only."""
    S = 1 if trade["side"] == "BUY" else -1
    side = trade["side"]
    p, a15 = ctx["price"], ctx["a15"]
    E = trade.get("entry") or p
    market = trade.get("entry") is None or abs(E - p) <= 0.25 * a15
    auto = []
    if trade.get("sl") is None or trade.get("tp") is None:
        sl, tp = place(ctx, S, E)
        if trade.get("sl") is None:
            trade["sl"] = sl; auto.append("SL")
        if trade.get("tp") is None:
            trade["tp"] = tp; auto.append("TP")
    trade["entry"] = round(E, 2)
    SL, TP = trade["sl"], trade["tp"]
    risk = (E - SL) * S
    rr = (TP - E) * S / risk if risk > 0 else 0
    issues = []   # (severity, verdict, missed text, better text)
    flow = _flow(ctx)
    tfl = " · ".join(f"{k} {'▲' if ctx['tr'][k]['state'] == 'bull' else '▼' if ctx['tr'][k]['state'] == 'bear' else '–'}"
                     for k in ("D", "H4", "H1", "M15"))

    def best_zone(side_s, need=5):
        z = zones(ctx, side_s, need)
        if not z:
            return None
        lvl, nm, _, r = z[0]
        sl_, tp_ = place(ctx, side_s, lvl)
        return lvl, nm, r, sl_, tp_

    def plan_text(side_s, lvl, nm, r, sl_, tp_):
        return (f"{'BUY' if side_s == 1 else 'SELL'} limit <b>{f2(lvl)}</b> ({nm}, reached {r}/10) · SL {f2(sl_)} · "
                f"TP {f2(tp_)} · {lot(abs(lvl - sl_))}")

    g = guard(user) if user else None
    if g:
        issues.append((100, "NO", f"🛡 {g}", "Close the chart. The best trade now is no trade."))
    if risk <= 0:
        issues.append((90, "NO", f"For a {side} the SL must be {'below' if S == 1 else 'above'} the entry {f2(E)}.",
                       f"Send just '{side.lower()}' and I'll place the SL on a real level."))
    nw = news(ctx)
    if nw:
        mins = (nw[1] - ctx["now"].timestamp()) / 60
        issues.append((80, "WAIT", f"📰 {nw[0]} {'in ' + str(int(mins)) + ' min' if mins > 0 else 'just came out'}: spreads jump, SL can slip.",
                       "Wait 15 min after the news, then check again."))
    if flow == -S:
        bz = best_zone(-S)
        issues.append((70, "NO", f"H1 + M15 are {'bullish' if flow == 1 else 'bearish'}: you're {side.lower()}ing against the flow.",
                       (f"Better idea: {plan_text(-S, *bz)}" if bz else f"Wait for the flow to turn {'🔴' if S == -1 else '🟢'}.")))
    sig = active_signal()
    if sig and (1 if sig.get("dir") == "bull" else -1) == -S:
        issues.append((65, "NO", f"An A+/B+ signal is open the other way ({'BUY' if sig.get('dir') == 'bull' else 'SELL'} {f2(sig['entry'])}).",
                       "The tested signal is the stronger trade: follow it or stay out."))
    if risk > 0 and risk < MIN_RISK:
        issues.append((60, "NO", f"SL is only ${risk:.2f} away: normal gold noise hits that.",
                       f"SL {f2(place(ctx, S, E)[0])} (behind the nearest stop pool)."))
    if risk > MAX_RISK:
        issues.append((60, "NO", f"SL is ${risk:.0f} away: too big for one trade.", "Find an entry closer to a level, or skip."))
    if 0 < rr < 1:
        issues.append((58, "NO", f"You risk more than you can win (RR {rr:.1f}).", f"TP {f2(place(ctx, S, E)[1])} or a better entry."))
    if not market:   # a limit: is it realistic?
        r = reach(ctx, E)
        if r is not None and r < 4:
            near = [z for z in zones(ctx, S, 5) if abs(z[0] - p) < abs(E - p)]
            z = near[-1] if near else None
            better = (f"More realistic: {plan_text(S, z[0], z[1], z[3], *place(ctx, S, z[0]))}" if z else
                      "Leave it, but don't wait for it: it's a bonus if it fills.")
            issues.append((55, "WAIT", f"{f2(E)} is ${abs(E - p):.0f} away: gold got that far only {r}/10 times by session end.", better))
    else:   # at market: selling into support / buying into resistance, or in the middle of nowhere?
        into = [x for x in ctx["levels"] if 0 <= (p - x[0]) * S <= 0.35 * a15 and
                ("low" in x[1] if S == -1 else "high" in x[1] or "VAH" in x[1])]
        at = [x for x in ctx["levels"] if -0.15 * a15 <= (x[0] - p) * -S <= 0.6 * a15]
        if into:
            lvl, nm, _ = into[0]
            bz = best_zone(S)
            issues.append((52, "WAIT", f"You're {side.lower()}ing right into the {nm} {f2(lvl)}: price often bounces there first.",
                           (f"Wait for the zone: {plan_text(S, *bz)}" if bz else f"Wait for a clean break of {f2(lvl)}.")))
        elif not at:
            bz = best_zone(S)
            issues.append((50, "WAIT", f"You're {side.lower()}ing in the middle of nowhere: no level, no swept stops here.",
                           (f"Wait for the zone: {plan_text(S, *bz)}" if bz else "Wait for price to reach a level.")))
    if risk > 0:   # SL in a stop pool?
        buf = max(2.0, 0.4 * a15)
        for lvl, nm, k in ctx["levels"]:
            if k == "pool" and (lvl - E) * S < 0 and -1.0 <= (SL - lvl) * -S <= 0.5 * buf:
                new = round(lvl - S * buf, 2)
                issues.append((45, "WAIT" if abs(E - new) <= MAX_RISK else "NO",
                               f"Your SL {f2(SL)} sits right at the {nm} {f2(lvl)}: stops there get hunted first.",
                               f"SL {f2(new)} · {lot(abs(E - new))}"))
                break
    if risk > 0 and rr >= 1:   # TP blocked?
        for lvl, nm, k in sorted(ctx["levels"], key=lambda x: abs(x[0] - E)):
            if (lvl - E) * S > 0.3 * risk and (TP - lvl) * S > 0.15 * risk and abs(lvl - E) < 0.6 * abs(TP - E):
                issues.append((30, "GO", f"{nm} {f2(lvl)} is halfway to your TP: price often stalls there.",
                               f"Take half at {f2(lvl)}, move SL to entry."))
                break
    if 0 < rr < MIN_RR:
        issues.append((35, "WAIT", f"RR is only {rr:.1f}.", f"TP {f2(place(ctx, S, E)[1])} or wait for a better entry."))
    if flow == 0:
        issues.append((40, "WAIT", "H1 + M15 are mixed: no clear direction yet.", "Wait for the 🔴/🟢 flow alert."))
    if not ctx["kz"] and not sig:
        issues.append((20, "GO", "Outside the London / NY killzone: moves are weaker now.", "Smaller size, or wait for 13:30 / 19:30."))
    if ai and ai.get("price") and abs(float(ai["price"]) - p) > max(5.0, a15):
        issues.append((48, "WAIT", f"Your screenshot shows {f2(float(ai['price']))} but gold is {f2(p)} now: the chart is old.",
                       "Take a fresh screenshot, or just type the trade."))
    if ai and ai.get("side") and ai["side"] != side and ai.get("agree"):
        issues.append((25, "GO", f"The AI models read your chart as {ai['side']}.", "Look again before you click."))
    issues.sort(key=lambda x: -x[0])
    verdict = "NO" if any(i[1] == "NO" for i in issues) else "WAIT" if any(i[1] == "WAIT" for i in issues) else "GO"
    top = next((i for i in issues if i[1] == verdict), issues[0] if issues else None)
    if verdict == "GO":
        good = [f"flow {'▲' if S == 1 else '▼'}" if flow == S else None, f"at {nm}" if (nm := next((n for l_, n, _ in ctx['levels'] if -0.15 * a15 <= (l_ - E) * -S <= 0.6 * a15), None)) else None,
                "killzone" if ctx["kz"] else None, f"RR {rr:.1f}"]
        missed = "Looks clean: " + " · ".join(x for x in good if x) + (f". Watch: {top[2]}" if top else "")
        better = f"Plan: {side} {f2(E)} · SL {f2(SL)} · TP {f2(TP)} · {lot(risk)}" + (f" · {top[3]}" if top else "")
    else:
        missed, better = top[2], top[3]
    return dict(verdict=verdict, missed=missed, better=better, rr=rr, auto=auto, flow=tfl, trade=trade, issues=issues)


def scan(ctx, user=None):
    """No input: the best side now, or WAIT + the zones to watch."""
    flow = _flow(ctx)
    if flow:
        res = evaluate({"side": "BUY" if flow == 1 else "SELL", "entry": None, "sl": None, "tp": None}, ctx, user)
        if res["verdict"] == "GO":
            return "READY " + ("BUY" if flow == 1 else "SELL"), res
    up = zones(ctx, -1, 5)[:1]
    dn = zones(ctx, 1, 5)[:1]
    watch = " · ".join([f"sell zone <b>{f2(z[0])}</b> ({z[1]}, {z[3]}/10)" for z in up] +
                       [f"buy zone <b>{f2(z[0])}</b> ({z[1]}, {z[3]}/10)" for z in dn])
    why = {1: "Flow is 🟢 but price isn't at a level yet.", -1: "Flow is 🔴 but price isn't at a level yet.",
           0: "H1 + M15 are mixed: no clear direction."}[flow]
    return "WAIT", dict(verdict="WAIT", missed=why, better=f"Watch {watch}. You'll get a 👀 alert there." if watch else "Nothing near.",
                        flow=" · ".join(f"{k} {'▲' if ctx['tr'][k]['state'] == 'bull' else '▼' if ctx['tr'][k]['state'] == 'bear' else '–'}" for k in ("D", "H4", "H1", "M15")),
                        trade=None, rr=0, auto=[])


# ------------------------------------------------------------------ AI (free): read the screenshot, understand text
READ = """You see a trading chart screenshot (gold / XAUUSD, any platform). Read ONLY what is visible. Return ONE JSON:
{"side_bias": "BUY"|"SELL"|"NONE" (which way the visible structure points),
 "price": number or null (the last price shown), "timeframe": string or null,
 "sweep": true|false (a wick that took a recent high/low and closed back),
 "cisd": true|false (a strong candle that broke the opposite way after that),
 "drawn_entry": number or null, "drawn_sl": number or null, "drawn_tp": number or null (only if a position/lines are drawn)}"""

PARSE = """Extract the gold trade from this message (Khmer or English, casual). ទិញ = BUY, លក់ = SELL.
Return ONE JSON: {"side": "BUY"|"SELL"|null, "entry": number|null, "sl": number|null, "tp": number|null, "reason": string}
Message: """


def _gemini(prompt, img=None, media="image/jpeg"):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    parts = ([{"inline_data": {"mime_type": media, "data": base64.b64encode(img).decode()}}] if img else []) + [{"text": prompt}]
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 800, "responseMimeType": "application/json"}}
    for mdl in dict.fromkeys(tc.GEMINI_MODELS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={urllib.parse.quote(key)}"
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(),
                                                                        headers={"content-type": "application/json"}), timeout=60))
            txt = "".join(x.get("text", "") for c in r.get("candidates", []) for x in c.get("content", {}).get("parts", []) if not x.get("thought"))
            return dict(tc._parse_json(txt), model=mdl.split("/")[-1])
        except Exception as e:
            print("coach gemini", mdl, "failed:", str(e)[:80])
    return None


def _openrouter(prompt, img=None, media="image/jpeg"):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    content = [{"type": "text", "text": prompt}] + ([{"type": "image_url", "image_url": {
        "url": f"data:{media};base64,{base64.b64encode(img).decode()}"}}] if img else [])
    for mdl in dict.fromkeys(OR_MODELS):
        body = {"model": mdl, "temperature": 0, "messages": [{"role": "user", "content": content}]}
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {key}", "content-type": "application/json"}), timeout=60))
            return dict(tc._parse_json(r["choices"][0]["message"]["content"]), model=mdl.split("/")[-1].replace(":free", ""))
        except Exception as e:
            print("coach openrouter", mdl, "failed:", str(e)[:80])
    return None


def read_chart(img, media):
    """2 free models read the screenshot. -> dict(side, agree, votes text, price, drawn levels) or None."""
    reads = [x for x in (_gemini(READ, img, media), _openrouter(READ, img, media)) if x]
    if not reads:
        return None
    sides = [x.get("side_bias") for x in reads if x.get("side_bias") in ("BUY", "SELL")]
    votes = " · ".join(f"{x['model']} {'▲' if x.get('side_bias') == 'BUY' else '▼' if x.get('side_bias') == 'SELL' else '–'}"
                       f"{' sweep✓' if x.get('sweep') else ''}{' CISD✓' if x.get('cisd') else ''}" for x in reads)
    first = reads[0]
    return dict(side=sides[0] if sides and len(set(sides)) == 1 else None, agree=len(set(sides)) == 1 and len(sides) == len(reads),
                votes=votes, price=first.get("price"), entry=first.get("drawn_entry"), sl=first.get("drawn_sl"), tp=first.get("drawn_tp"))


def parse(text):
    trade, err = tc.parse_caption(text or "")
    if trade and trade["side"]:
        return trade
    ai = _gemini(PARSE + (text or "")[:500]) or _openrouter(PARSE + (text or "")[:500])
    if ai and ai.get("side") in ("BUY", "SELL"):
        return {"side": ai["side"], "entry": tc._num(str(ai.get("entry"))) if ai.get("entry") else None,
                "sl": tc._num(str(ai.get("sl"))) if ai.get("sl") else None, "tp": tc._num(str(ai.get("tp"))) if ai.get("tp") else None,
                "reason": str(ai.get("reason") or "")[:300], "auto": []}
    return None


# ------------------------------------------------------------------ the picture
def picture(ctx, res, path, better_zone=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from signal_card import BG, INK, MUT, UP, DN, BLUE, _fonts
    _fonts()
    d = ctx["d15"].tail(64)   # last 16 hours
    fig = plt.figure(figsize=(8, 6.2), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.04, 0.08, 0.80, 0.78])
    ax.set_facecolor(BG)
    x = np.arange(len(d))
    o, h, l, c = (d[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
    col = np.where(c >= o, UP, DN)
    ax.vlines(x, l, h, color=col, lw=0.8)
    ax.bar(x, np.maximum(np.abs(c - o), 0.05), bottom=np.minimum(o, c), color=col, width=0.7)
    t = res.get("trade")
    ys = [float(l.min()), float(h.max())] + ([t["entry"], t["sl"], t["tp"]] if t else [])
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.06
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_xlim(-1, len(d) + 22)
    near = sorted(ctx["levels"], key=lambda z: abs(z[0] - (t["entry"] if t else ctx["price"])))[:8]
    for lvl, nm, k in near:   # the 8 levels nearest the trade, names on the left
        lo, hi = min(lo, lvl), max(hi, lvl)
    pad = (hi - lo) * 0.06
    ax.set_ylim(lo - pad, hi + pad)
    gap, groups = (hi - lo) * 0.035, []
    for lvl, nm, k in sorted(near):
        ax.axhline(lvl, color="#AEAEB2" if k == "pool" else "#5E9EFF", lw=0.8, ls=":" if k == "pool" else "--", zorder=1)
        if groups and lvl - groups[-1][0] < gap:   # levels almost at the same price share one label
            groups[-1][1].append(f"{nm} {lvl:,.1f}")
        else:
            groups.append([lvl, [f"{nm} {lvl:,.1f}"]])
    for lvl, names in groups:
        ax.text(0, lvl, " / ".join(names), fontsize=7, color="#6E6E73", ha="left", va="bottom",
                bbox=dict(boxstyle="round,pad=0.15", fc=BG, ec="none", alpha=0.8), zorder=4)
    if t:
        S = 1 if t["side"] == "BUY" else -1
        x0 = len(d) - 1
        ax.fill_between([x0, len(d) + 20], t["entry"], t["tp"], color=UP, alpha=0.12, zorder=0)
        ax.fill_between([x0, len(d) + 20], t["entry"], t["sl"], color=DN, alpha=0.12, zorder=0)
        for y, lab, cc in ((t["entry"], f"{t['side']} {t['entry']:,.2f}", INK), (t["sl"], f"SL {t['sl']:,.2f}", DN), (t["tp"], f"TP {t['tp']:,.2f}", UP)):
            ax.plot([x0, len(d) + 20], [y, y], color=cc, lw=1.6)
            ax.text(len(d) + 20, y, lab, fontsize=8.5, color=cc, fontweight="bold", va="center", ha="right", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=cc, lw=0.8))
    if better_zone:
        ax.axhspan(better_zone - 0.4, better_zone + 0.4, color="#FFD60A", alpha=0.35, zorder=0)
        ax.text(2, better_zone, f"better zone {better_zone:,.2f}", fontsize=7.5, color="#B38600", va="bottom", fontweight="bold")
    ax.axhline(ctx["price"], color=BLUE, lw=0.8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=MUT, labelsize=7)
    ax.set_xticks([])
    ax.yaxis.tick_right()
    v = res["verdict"]
    vc = {"GO": UP, "READY BUY": UP, "READY SELL": UP, "WAIT": "#FF9F0A", "NO": DN}.get(v, INK)
    fig.text(0.04, 0.95, "XAU.KH COACH", color=BLUE, fontsize=12, fontweight="bold")
    fig.text(0.96, 0.95, v, color=vc, fontsize=16, fontweight="bold", ha="right")
    fig.text(0.04, 0.905, f"{res['flow']}   ·   price {ctx['price']:,.2f}   ·   {datetime.fromtimestamp(ctx['now'].timestamp(), KH):%d %b %H:%M} UTC+7",
             color=INK, fontsize=9)
    fig.text(0.04, 0.03, "dotted = stops (highs/lows) · dashed = session VAH / POC / VAL · reminder, not advice", color=MUT, fontsize=7)
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path


# ------------------------------------------------------------------ Telegram
def _text(res, ai=None, title=None):
    icon = {"GO": "✅", "READY BUY": "🟢", "READY SELL": "🔴", "WAIT": "⏸", "NO": "❌"}.get(res["verdict"], "")
    km = {"GO": "ចូលបាន", "READY BUY": "ត្រៀម BUY", "READY SELL": "ត្រៀម SELL", "WAIT": "រង់ចាំ", "NO": "កុំចូល"}.get(res["verdict"], "")
    lines = [f"{icon} <b>{res['verdict']}</b>" + (f" · {title}" if title else "") + f" · {km}",
             f"👁 {res['missed']}", f"✅ {res['better']}"]
    if res.get("auto"):
        lines.append(f"<i>I placed your {' + '.join(res['auto'])} on real levels.</i>")
    if ai:
        lines.append(f"🤖 {ai['votes']}" + ("" if ai.get("agree") else " · the AIs disagree: trust the data above"))
    return "\n".join(lines)


def _send(base, res, ctx, ai=None, title=None, save=None):
    bz = None
    m = re.search(r"limit <b>([\d,.]+)</b>", res.get("better") or "")
    if m:
        bz = tc._num(m.group(1))
    path = picture(ctx, res, "coach.png", bz)
    cap = _text(res, ai, title)
    kw = {}
    if save:
        t = res["trade"]
        row = tc._sb("POST", "trade_checks", {
            "tg_user": int(save), "side": t["side"], "entry": t["entry"], "sl": t["sl"], "tp": t["tp"],
            "reason": t.get("reason") or None, "verdict": {"GO": "GO", "WAIT": "CAUTION", "NO": "NO-GO"}[res["verdict"]],
            "checks": [{"m": i[1], "t": i[2]} for i in res["issues"][:6]], "chart_read": {"coach": True, "ai": ai},
            "live_price": ctx["price"], "rr": round(res["rr"], 2)}, prefer="return=representation")
        if row:
            cid = row[0]["id"]
            kw["reply_markup"] = json.dumps({"inline_keyboard": [[
                {"text": "✅ I took it · ចូលហើយ", "callback_data": f"tc:take:{cid}"},
                {"text": "✋ I skipped · មិនចូល", "callback_data": f"tc:skip:{cid}"}]]})
    import listener
    listener.photo(dict(base, caption=cap[:1024], **kw), path)


def handle(msg, base):
    """Owner's private text or photo. Returns True when handled."""
    if (msg.get("chat") or {}).get("type") != "private" or not owner((msg.get("from") or {}).get("id")):
        return False
    user = msg["from"]["id"]
    text = (msg.get("text") or msg.get("caption") or "").strip()
    is_photo = bool(msg.get("photo")) or str((msg.get("document") or {}).get("mime_type", "")).startswith("image/")
    cmd = text.split()[0].split("@")[0].lower() if text.startswith("/") else ""
    if cmd in ("/coach",):
        tc._api("sendMessage", dict(base, text=HOW)); return True
    if not is_photo and cmd != "/scan" and not looks_like_trade(text):
        return False
    tc._api("sendChatAction", {"chat_id": msg["chat"]["id"], "action": "upload_photo"})
    try:
        ctx = context()
    except Exception as e:
        print("coach context failed:", e)
        tc._api("sendMessage", dict(base, text="I couldn't load live prices right now. Try again in a minute."))
        return True
    if cmd == "/scan":
        v, res = scan(ctx, user)
        res["verdict"] = v
        _send(base, res, ctx, title="scan")
        return True
    ai = None
    if is_photo:
        try:
            fid = (max(msg["photo"], key=lambda p_: p_.get("file_size", 0))["file_id"] if msg.get("photo") else msg["document"]["file_id"])
            fp = tc._api("getFile", {"file_id": fid})["file_path"]
            img = urllib.request.urlopen(f"https://api.telegram.org/file/bot{tc._tok()}/{fp}", timeout=30).read()
            ai = read_chart(img, "image/png" if fp.lower().endswith(".png") else "image/jpeg")
        except Exception as e:
            print("coach screenshot failed:", e)
    trade = parse(text) if text else None
    if not trade and ai and (ai.get("side") or ai.get("entry")):
        trade = {"side": ai.get("side") or ("BUY" if (ai.get("tp") or 0) > (ai.get("entry") or 0) else "SELL"),
                 "entry": ai.get("entry"), "sl": ai.get("sl"), "tp": ai.get("tp"), "reason": "from screenshot", "auto": []}
    if not trade:
        v, res = scan(ctx, user)
        res["verdict"] = v
        _send(base, res, ctx, ai, title="no trade found, here's the market")
        return True
    res = evaluate(trade, ctx, user, ai)
    _send(base, res, ctx, ai, title=f"{trade['side']} {f2(trade['entry'])}", save=user)
    return True
