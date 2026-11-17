"""✋ Pre-trade check: send the bot a chart screenshot + your trade BEFORE you click.

Private chat only. Example caption on the photo:
    BUY 3865.8 SL 3858 TP 3880 · bounce from POC
    SELL 3880 SL 3888 TP 3860 - FLIP at the POI

1. Claude reads the XAU.KH PRO panel from the screenshot (exactly from the CHK line when it is visible).
2. CODE runs the checks (the AI never decides): side vs BIAS, score, FLIP/GO trigger, risk:reward, stop size,
   room to the next WALL, entry vs live price, high-impact news, losses today.
3. Reply: ✅ GO / ⚠️ CAUTION / ⛔ NO-GO with every reason, plus what PRO wants instead.
4. Buttons "I took it" / "I skipped". Taken trades are graded on the 5m candles (loop.py runs this file every
   cycle), and the bot tells you the week's bill: followed the check vs overrode a NO-GO.

Privacy: checks are saved in Supabase (NOT in this public repo). Each member sees only their own rows:
in this private chat and through the my-checks edge function in the mini app.

Secrets: ANTHROPIC_API_KEY or GEMINI_API_KEY (free tier; Claude is used when both are set), SUPABASE_URL, SUPABASE_SERVICE_KEY (without the two Supabase ones it still checks,
it just can't save or grade).
Variables: TRADECHECK = owner (default: only TELEGRAM_OWNER_CHAT_ID) | all | off
           TRADECHECK_PER_DAY (default 10 per member), TRADECHECK_MAX_RISK (default 25 = PRO's "skip if risk > $")
           TRADECHECK_MODEL (default AI_MODEL, else claude-haiku-5-5; must read images)
"""
import base64
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

MODE = os.environ.get("TRADECHECK", "owner").lower()
PER_DAY = int(os.environ.get("TRADECHECK_PER_DAY", 10))
MAX_RISK = float(os.environ.get("TRADECHECK_MAX_RISK", 25))
MODEL = os.environ.get("TRADECHECK_MODEL") or os.environ.get("AI_MODEL") or "claude-haiku-5-5"
SB_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
MIN_RR, HARD_RR = 2.0, 1.5      # PRO plans at 2R; under 1.5R is a no
MIN_RISK = 1.5                  # a stop under $1.50 sits inside normal gold noise
CHASE = 3.0                     # entry this far from the live price = old screenshot or chasing
NEWS_BEFORE, NEWS_AFTER = 30, 15  # minutes around a high-impact release
MAX_LOSSES = 2                  # 2 losses today = done for the day
EXPIRE_H = 24
KH = timezone(timedelta(hours=7))
_used = {}

HOW = ("✋ <b>Trade check</b> · send a chart screenshot (XAU.KH PRO panel visible) with just <b>BUY</b> or <b>SELL</b>.\n"
       "I fill in entry (live price), SL (behind the nearest WALL) and TP (2R), then check it.\n"
       "Your own numbers are fine too: <code>BUY 3865.8 SL 3858 TP 3880 · reason</code>\n"
       "Check BEFORE you click.\n"
       "🇰🇭 ផ្ញើរូបក្រាហ្វ + សរសេរ BUY ឬ SELL ប៉ុណ្ណោះ · bot ដាក់ SL TP ឲ្យ")
DEFAULT_RISK = 8.0   # $ stop when no WALL is in a sensible range behind the entry


# ---------------------------------------------------------------- small helpers
def _tok():
    return os.environ.get("TELEGRAM_TOKEN")


def _api(method, fields, timeout=30):
    r = urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{_tok()}/{method}",
                                                      data=urllib.parse.urlencode(fields).encode()), timeout=timeout)
    return json.load(r).get("result")


def _jl(n, d=None):
    try:
        return json.load(open(n))
    except Exception:
        return {} if d is None else d


def _f(x):
    return f"{x:,.2f}"


def _num(s):
    try:
        return float(str(s).replace(",", ""))
    except Exception:
        return None


def allowed(user):
    if MODE == "off" or not user:
        return False
    if MODE == "all":
        return True
    return str(user) == str(os.environ.get("TELEGRAM_OWNER_CHAT_ID", "")).strip()


def _day_kh(ts=None):
    return datetime.fromtimestamp(ts or time.time(), KH).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- Supabase (server key: never sent to members)
def _sb(method, path, body=None, prefer=None):
    if not (SB_URL and SB_KEY):
        return None
    h = {"apikey": SB_KEY, "Content-Type": "application/json"}
    if not SB_KEY.startswith("sb_"):   # legacy service_role key (a JWT) also goes in Authorization; new sb_secret_ keys don't
        h["Authorization"] = f"Bearer {SB_KEY}"
    if prefer:
        h["Prefer"] = prefer
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{path}", method=method, headers=h,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        raw = urllib.request.urlopen(req, timeout=20).read()
        return json.loads(raw) if raw else []
    except Exception as e:
        print("supabase", method, path.split("?")[0], "failed:", e)
        return None


def _since_kh_midnight():
    d = datetime.now(KH).replace(hour=0, minute=0, second=0, microsecond=0)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def losses_today(user):
    rows = _sb("GET", f"trade_checks?select=id&tg_user=eq.{int(user)}&status=eq.loss"
                      f"&closed_at=gte.{_since_kh_midnight()}")
    return len(rows) if rows else 0


def checks_today(user):
    rows = _sb("GET", f"trade_checks?select=id&tg_user=eq.{int(user)}&created_at=gte.{_since_kh_midnight()}")
    if rows is not None:
        return len(rows)
    return _used.get((user, _day_kh()), 0)


# ---------------------------------------------------------------- 1 · the caption
_N = r"(\d[\d,]*(?:\.\d+)?)"


def parse_caption(text):
    """'BUY 3865.8 SL 3858 TP 3880 · reason' -> dict, or (None, error)."""
    t = (text or "").strip()
    up = t.upper()
    side = None
    m = re.search(r"\b(BUY|LONG|SELL|SHORT)\b", up)
    if m:
        side = "BUY" if m.group(1) in ("BUY", "LONG") else "SELL"
    elif "ទិញ" in t:
        side = "BUY"
    elif "លក់" in t:
        side = "SELL"
    sl = re.search(r"\bS\.?L\b\s*[:=@]?\s*" + _N, up)
    tp = re.search(r"\bT\.?P\d?\b\s*[:=@]?\s*" + _N, up)
    en = re.search(r"\b(?:BUY|LONG|SELL|SHORT|ENTRY|E|@)\b\s*(?:LIMIT|AT|@)?\s*[:=@]?\s*" + _N, up) \
        or re.search(r"(?:ទិញ|លក់)\s*" + _N, t)
    used = [x.span() for x in (sl, tp, en) if x]
    if not en:   # first number that is not the SL / TP
        for x in re.finditer(_N, up):
            if not any(a <= x.start() < b for a, b in used):
                en = x
                break
    if not side:
        return None, "Write BUY or SELL with the screenshot."
    entry = _num(en.group(en.lastindex)) if en else None
    slv = _num(sl.group(1)) if sl else None
    tpv = _num(tp.group(1)) if tp else None
    reason = ""
    r = re.split(r"\s[·|\-–—:]\s|\n", t, maxsplit=1)
    if len(r) > 1:
        reason = r[1].strip()
    return {"side": side, "entry": entry, "sl": slv, "tp": tpv, "reason": reason[:300], "auto": []}, None


def fill(trade, read):
    """Fill what the member left out: entry = live price, SL = behind the nearest WALL, TP = 2R. -> error or None."""
    S = 1 if trade["side"] == "BUY" else -1
    if trade["entry"] is None:
        lp, lt = live_price()
        cp = read.get("price") if read.get("pro_visible") else None
        trade["entry"] = lp if lp and time.time() - lt < 1800 else cp
        if trade["entry"] is None:
            return "I couldn't get the live price. Add your entry, e.g. BUY 3866"
        trade["auto"].append("entry = live price")
    E = trade["entry"]
    if trade["sl"] is None:
        wall = read.get("wall_down") if S == 1 else read.get("wall_up")
        sl = None
        if wall and (E - wall) * S > 0:
            sl = round(wall - S * 0.5, 2)
            if not (MIN_RISK <= abs(E - sl) <= MAX_RISK):
                sl = None
        if sl is not None:
            trade["auto"].append(f"SL just {'below' if S == 1 else 'above'} the {'▼' if S == 1 else '▲'} WALL {_f(wall)}")
        else:
            sl = round(E - S * DEFAULT_RISK, 2)
            trade["auto"].append(f"SL ${DEFAULT_RISK:.0f} away (no WALL in range)")
        trade["sl"] = sl
    if (E - trade["sl"]) * S <= 0:
        return (f"For a {trade['side']} the SL must be {'BELOW' if S == 1 else 'ABOVE'} the entry {_f(E)}. "
                f"{_f(trade['sl'])} is on the wrong side. Send just {trade['side']} and I'll place it.")
    if trade["tp"] is None:
        trade["tp"] = round(E + S * MIN_RR * abs(E - trade["sl"]), 2)
        trade["auto"].append(f"TP at {MIN_RR:.0f}R")
    if (trade["tp"] - E) * S <= 0:
        return f"For a {trade['side']} the TP must be {'ABOVE' if S == 1 else 'BELOW'} the entry {_f(E)}."
    return None


# ---------------------------------------------------------------- 2 · reading the screenshot
READ_PROMPT = """This is a TradingView chart of gold with the "XAU.KH PRO" indicator. Read ONLY what is visible.
Return ONE JSON object and nothing else:
{"pro_visible": true/false,          // is the XAU.KH PRO panel visible?
 "chk": "",                          // the line starting with "CHK" copied EXACTLY, or "" if not visible
 "bias": "BUY|SELL|NONE|UNKNOWN",    // the BIAS row: "BIAS ▲ BUY" = BUY, "BIAS ▼ SELL" = SELL, "no clear trend" = NONE
 "score": null,                      // the number before "/5" in the score cell, e.g. "1/5 · watch" -> 1
 "h1": "UP|DOWN|NONE|UNKNOWN", "h4": "UP|DOWN|NONE|UNKNOWN",   // the 1H and 4H structure cells (▲ = UP, ▼ = DOWN)
 "wall_up": null, "wall_down": null, // numbers after "▲ WALL" and "▼ WALL"
 "poi_low": null, "poi_high": null,  // the "POI a–b" numbers in the BIAS row
 "next": "",                         // the text after "NEXT ▸"
 "trigger": "FLIP_BUY|FLIP_SELL|GO_BUY|GO_SELL|NONE|UNKNOWN", // a FLIP or GO label (not "skip") on the last ~10 candles
 "price": null,                      // the chart's current price (last price tag on the right axis)
 "timeframe": ""}
Never guess a number you cannot read: use null."""


GEMINI_MODELS = [m for m in [os.environ.get("GEMINI_MODEL")] if m] + [
    "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest", "gemini-flash-latest"]   # same list as breaking.py: old ids get retired from the free tier


def _parse_json(txt):
    return json.loads(txt[txt.index("{"): txt.rindex("}") + 1])


def _read_claude(key, img_bytes, media):
    body = {"model": MODEL, "max_tokens": 500, "messages": [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": media, "data": base64.b64encode(img_bytes).decode()}},
        {"type": "text", "text": READ_PROMPT}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    out = json.load(urllib.request.urlopen(req, timeout=60))
    return _parse_json("".join(c.get("text", "") for c in out.get("content", [])))


def _read_gemini(key, img_bytes, media):
    body = {"contents": [{"role": "user", "parts": [
        {"inline_data": {"mime_type": media, "data": base64.b64encode(img_bytes).decode()}}, {"text": READ_PROMPT}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 1500, "responseMimeType": "application/json"}}
    errs = []
    for mdl in dict.fromkeys(GEMINI_MODELS):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={urllib.parse.quote(key)}"
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            errs.append(f"{mdl} {e.code}")
            if e.code in (400, 403, 404, 429):
                continue
            raise
        txt = "".join(p_.get("text", "") for c in r.get("candidates", []) for p_ in c.get("content", {}).get("parts", [])
                      if not p_.get("thought"))
        print("trade check read with", mdl)
        return _parse_json(txt)
    raise RuntimeError("Gemini: " + ", ".join(errs))


def read_chart(img_bytes, media="image/jpeg"):
    """Claude if ANTHROPIC_API_KEY is set, else Gemini (GEMINI_API_KEY, free tier). Never raises."""
    ak, gk = os.environ.get("ANTHROPIC_API_KEY"), os.environ.get("GEMINI_API_KEY")
    if not ak and not gk:
        return {"pro_visible": False, "error": "no AI key: add ANTHROPIC_API_KEY or GEMINI_API_KEY in GitHub secrets"}
    try:
        d = _read_claude(ak, img_bytes, media) if ak else _read_gemini(gk, img_bytes, media)
    except urllib.error.HTTPError as e:
        why = e.read().decode("utf-8", "ignore")[:200]
        print("trade check read failed:", e.code, why)
        return {"pro_visible": False, "error": f"AI error {e.code}: {why}"}
    except Exception as e:
        print("trade check read failed:", e)
        return {"pro_visible": False, "error": f"could not read the screenshot ({type(e).__name__}: {str(e)[:120]})"}
    return apply_chk(d)


def apply_chk(d):
    """The CHK line (PRO prints it in the panel) is exact, so it overrides what the AI read by eye.
    Format: CHK b-1 s1 h-1 f0 u3872.96 d3854.70 p3877.66-3901.37"""
    chk = (d.get("chk") or "").strip()
    if not chk.upper().startswith("CHK"):
        d["chk_ok"] = False
        return d
    g = lambda k: (re.search(rf"\b{k}(-?[\d.]+|na)\b", chk) or [None, None])[1]
    b, s, h, f = g("b"), g("s"), g("h"), g("f")
    if b in ("1", "-1", "0"):
        d["bias"] = {"1": "BUY", "-1": "SELL", "0": "NONE"}[b]
    if s and s != "na":
        d["score"] = int(float(s))
    if h in ("1", "-1", "0"):
        d["h4"] = {"1": "UP", "-1": "DOWN", "0": "NONE"}[h]
    if f in ("1", "-1", "0"):
        d["trigger"] = {"1": "FLIP_BUY", "-1": "FLIP_SELL", "0": "NONE"}[f]
    for k, key in (("u", "wall_up"), ("d", "wall_down")):
        v = g(k)
        d[key] = _num(v) if v and v != "na" else None
    p = re.search(r"\bp([\d.]+)-([\d.]+)\b", chk)
    d["poi_low"], d["poi_high"] = (_num(p.group(1)), _num(p.group(2))) if p else (None, None)
    d["chk_ok"] = True
    return d


# ---------------------------------------------------------------- 3 · the rules (code decides, not the AI)
def live_price():
    lv = _jl("levels.json")
    p = lv.get("price")
    try:
        t = datetime.strptime(lv.get("time", ""), "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        t = 0
    return (float(p), t) if p else (None, 0)


def news_near(now=None):
    now = now or time.time()
    for e in _jl("news.json").get("events", []):
        if str(e.get("impact", "")).lower() != "high":
            continue
        try:
            t = datetime.fromisoformat(e["time"].replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        if -NEWS_AFTER * 60 <= t - now <= NEWS_BEFORE * 60:
            return e.get("title", "news"), t
    return None


def evaluate(trade, read, user=None, now=None):
    """-> (verdict, [(mark, text)], instead). mark: '✗' = no, '!' = careful, '✓' = ok."""
    S = 1 if trade["side"] == "BUY" else -1
    E, SL, TP = trade["entry"], trade["sl"], trade["tp"]
    risk = abs(E - SL)
    rr = round(abs(TP - E) / risk, 2) if risk > 0 else 0   # rounded so an exact 2R fill is not flagged
    out = []
    add = lambda m, t: out.append((m, t))
    seen = read.get("pro_visible")
    bias = read.get("bias", "UNKNOWN") if seen else "UNKNOWN"
    bS = {"BUY": 1, "SELL": -1}.get(bias, 0)

    # chart reading
    if not seen:
        add("!", "XAU.KH PRO panel not visible in the screenshot: chart checks skipped")
    if bS == -S:
        add("✗", f"{trade['side']} against BIAS {'▲ BUY' if bS == 1 else '▼ SELL'} (1H + 4H structure)")
    elif bS == S:
        add("✓", f"With BIAS {'▲ BUY' if S == 1 else '▼ SELL'}")
    elif seen:
        add("!", "No clear BIAS" if bias == "NONE" else "Couldn't read BIAS")
    sc = read.get("score") if seen else None
    if sc is not None:
        add("✗" if sc <= 1 else "!" if sc <= 3 else "✓",
            f"Score {sc}/5 → " + ("skip" if sc <= 1 else "half size at most" if sc <= 3 else "full size OK"))
    trig = str(read.get("trigger") or "UNKNOWN")
    tS = 1 if trig.endswith("BUY") else -1 if trig.endswith("SELL") else 0
    if seen:
        if tS == S:
            add("✓", f"{trig.split('_')[0]} {'▲' if S == 1 else '▼'} on the chart")
        elif tS == -S:
            add("✗", f"The chart's trigger is the other way ({trig.replace('_', ' ')})")
        else:
            add("!", "No FLIP / GO yet: the level is not proven, waiting is the trade")

    # the numbers
    add("✗" if rr < HARD_RR else "!" if rr < MIN_RR else "✓", f"Risk:reward {rr:.1f}R (need {MIN_RR:.0f}R)")
    if risk < MIN_RISK:
        add("!", f"SL only ${risk:.2f} away: inside normal gold noise")
    elif risk > MAX_RISK:
        add("✗", f"SL ${risk:.2f} away: bigger than your ${MAX_RISK:.0f} limit")
    else:
        add("✓", f"SL ${risk:.2f} away")
    wall = read.get("wall_up") if S == 1 else read.get("wall_down")
    if seen and wall and (wall - E) * S > 0 and (TP - wall) * S > 0:
        room = abs(wall - E) / risk if risk > 0 else 0
        add("✗" if room < 1 else "!" if room < MIN_RR else "✓",
            f"TP is past the {'▲' if S == 1 else '▼'} WALL {_f(wall)}: real room {room:.1f}R")
    lp, lt = live_price()
    now = now or time.time()
    if lp and now - lt < 1800:
        if abs(E - lp) > CHASE:
            add("!", f"Entry is {abs(E - lp):.1f} from the live price {_f(lp)}: old screenshot, or a limit far away")
        cp = read.get("price") if seen else None
        if cp and abs(cp - lp) > 2 * CHASE:
            add("!", f"Chart shows {_f(cp)} but live is {_f(lp)}: is this screenshot old?")
    n = news_near(now)
    if n:
        mins = (n[1] - now) / 60
        add("✗", f"High-impact news {'in ' + str(int(mins)) + ' min' if mins > 0 else str(int(-mins)) + ' min ago'}: {n[0]}")
    if user and SB_URL:
        lo = losses_today(user)
        if lo >= MAX_LOSSES:
            add("✗", f"{lo} losses today: done for the day")

    verdict = "NO-GO" if any(m == "✗" for m, _ in out) else "CAUTION" if any(m == "!" for m, _ in out) else "GO"

    # what PRO wants instead
    instead = ""
    if bS == -S:
        pl, ph = read.get("poi_low"), read.get("poi_high")
        instead = (f"PRO's side is {'BUY' if bS == 1 else 'SELL'}"
                   + (f": wait for price at the POI {_f(pl)}–{_f(ph)}" if pl and ph else "")
                   + f", then sweep → {'▲' if bS == 1 else '▼'} FLIP / GO")
    elif seen and tS != S and verdict != "GO":
        instead = "Same side, but wait for the sweep → FLIP or ABSORB → GO on 5m first"
    elif rr < MIN_RR:
        instead = f"Move the TP or tighten the entry until it pays at least {MIN_RR:.0f}R, or skip"
    return verdict, out, instead, rr


def reply_text(trade, read, verdict, out, instead, rr):
    head = {"GO": "✅ <b>GO</b>", "CAUTION": "⚠️ <b>CAUTION</b>", "NO-GO": "⛔ <b>NO-GO</b>"}[verdict]
    if not read.get("pro_visible") and verdict != "NO-GO":
        head = "❓ <b>NOT CHECKED</b> · I couldn't read the chart, so this is NOT an OK"
    km = {"GO": "អាចចូលបាន តាមផែនការ", "CAUTION": "ប្រយ័ត្ន · បន្ថយ lot ឬរង់ចាំ", "NO-GO": "កុំចូល · រង់ចាំ"}[verdict]
    L = [f"{head} · {trade['side']} {_f(trade['entry'])} · SL {_f(trade['sl'])} · TP {_f(trade['tp'])} · {rr:.1f}R"]
    order = {"✗": 0, "!": 1, "✓": 2}
    for m, t in sorted(out, key=lambda x: order[x[0]]):
        L.append(f"{'✗' if m == '✗' else '⚠' if m == '!' else '✓'} {html.escape(t, quote=False)}")
    if trade.get("auto"):
        L.append(f"🤖 <i>I filled in: {html.escape(' · '.join(trade['auto']), quote=False)}</i>")
    if instead:
        L.append(f"👉 <b>{html.escape(instead, quote=False)}</b>")
    if not read.get("pro_visible"):
        km = "មិនបានពិនិត្យក្រាហ្វ · កុំចាត់ទុកថាអាចចូលបាន"
        L.append("<i>Fix: crop to the chart + PRO panel, or send the picture as a File (no compression)."
                 + (f" Reason: {html.escape(str(read['error']), quote=False)}" if read.get("error") else "") + "</i>")
    L.append(f"🇰🇭 {km}")
    if read.get("pro_visible"):
        src = "CHK line (exact)" if read.get("chk_ok") else "the panel, by eye"
        bits = [f"BIAS {read.get('bias')}", f"score {read.get('score') if read.get('score') is not None else '?'}/5",
                f"trigger {str(read.get('trigger', '?')).replace('_', ' ')}"]
        if read.get("wall_up") or read.get("wall_down"):
            bits.append(f"walls {read.get('wall_up') or '–'} / {read.get('wall_down') or '–'}")
        L.append(f"<i>📖 Read from {src}: {html.escape(' · '.join(bits), quote=False)}. Wrong? Send a clearer screenshot.</i>")
    if trade.get("reason"):
        L.append(f"<i>Your reason: {html.escape(trade['reason'], quote=False)}</i>")
    else:
        L.append("<i>Tip: add your reason after a ·  (naming it is half the check)</i>")
    L.append("<i>A rules check, not financial advice.</i>")
    return "\n".join(L)


# ---------------------------------------------------------------- Telegram entry points (called by listener.py)
def handle_photo(msg, base):
    """A photo in a private chat. Returns True if it was handled."""
    if (msg.get("chat") or {}).get("type") != "private":
        return False
    user = (msg.get("from") or {}).get("id")
    if not allowed(user):
        return False
    send = lambda t, **kw: _api("sendMessage", dict(base, text=t, disable_web_page_preview="true", **kw))
    trade, err = parse_caption(msg.get("caption"))
    if err:
        send(f"⚠️ {err}\n\n{HOW}")
        return True
    if checks_today(user) >= PER_DAY:
        send(f"Daily limit reached ({PER_DAY} checks). Tomorrow again · ថ្ងៃនេះអស់ហើយ")
        return True
    _used[(user, _day_kh())] = _used.get((user, _day_kh()), 0) + 1
    _api("sendChatAction", {"chat_id": msg["chat"]["id"], "action": "typing"})
    try:
        if msg.get("photo"):
            fid = max(msg["photo"], key=lambda p: p.get("file_size", 0))["file_id"]
        else:
            fid = msg["document"]["file_id"]
        fp = _api("getFile", {"file_id": fid})["file_path"]
        img = urllib.request.urlopen(f"https://api.telegram.org/file/bot{_tok()}/{fp}", timeout=30).read()
    except Exception as e:
        print("trade check download failed:", e)
        send("Couldn't download the screenshot. Try again.")
        return True
    media = "image/png" if fp.lower().endswith(".png") else "image/webp" if fp.lower().endswith(".webp") else "image/jpeg"
    read = read_chart(img, media)
    err = fill(trade, read)
    if err:
        send(f"⚠️ {err}")
        return True
    verdict, out, instead, rr = evaluate(trade, read, user)
    text = reply_text(trade, read, verdict, out, instead, rr)
    row = _sb("POST", "trade_checks", {
        "tg_user": int(user), "side": trade["side"], "entry": trade["entry"], "sl": trade["sl"], "tp": trade["tp"],
        "reason": trade["reason"] or None, "verdict": verdict, "checks": [{"m": m, "t": t} for m, t in out],
        "chart_read": {k: read.get(k) for k in ("bias", "score", "h1", "h4", "trigger", "wall_up", "wall_down",
                                               "poi_low", "poi_high", "price", "timeframe", "chk_ok", "pro_visible", "error")},
        "live_price": live_price()[0], "rr": round(rr, 2)}, prefer="return=representation")
    kw = {}
    if row:
        cid = row[0]["id"]
        kw["reply_markup"] = json.dumps({"inline_keyboard": [[
            {"text": "✅ I took it · ចូលហើយ", "callback_data": f"tc:take:{cid}"},
            {"text": "✋ I skipped · មិនចូល", "callback_data": f"tc:skip:{cid}"}]]})
    send(text, **kw)
    return True


def on_callback(cq):
    """Buttons under a check. Only the member who made the check can press them (row filter on tg_user)."""
    data = cq.get("data") or ""
    if not data.startswith("tc:"):
        return False
    user = (cq.get("from") or {}).get("id")
    try:
        _, act, cid = data.split(":")
        cid = int(cid)
    except Exception:
        return True
    rows = _sb("GET", f"trade_checks?select=id,verdict,status&id=eq.{cid}&tg_user=eq.{int(user)}")
    if not rows or rows[0]["status"] != "checked":
        _api("answerCallbackQuery", {"callback_query_id": cq["id"], "text": "Already saved."})
        return True
    took = act == "take"
    _sb("PATCH", f"trade_checks?id=eq.{cid}&tg_user=eq.{int(user)}",
        {"taken": took, "status": "open" if took else "skipped"})
    over = took and rows[0]["verdict"] == "NO-GO"
    _api("answerCallbackQuery", {"callback_query_id": cq["id"],
                                 "text": "Logged as an override of a NO-GO." if over else "Saved."})
    m = cq.get("message") or {}
    if m:
        _api("editMessageReplyMarkup", {"chat_id": m["chat"]["id"], "message_id": m["message_id"],
                                        "reply_markup": json.dumps({"inline_keyboard": []})})
        note = ("🔴 Taken against a NO-GO. It goes on your bill: you'll see if overriding pays."
                if over else "📒 Tracking it. I'll tell you when SL or TP is hit." if took
                else "👍 Skipped. Waiting is a position too.")
        _api("sendMessage", {"chat_id": m["chat"]["id"], "text": note, "reply_parameters": json.dumps(
            {"message_id": m["message_id"], "allow_sending_without_reply": True})})
    return True


def week_bill(user):
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = _sb("GET", f"trade_checks?select=verdict,taken,status,result_r&tg_user=eq.{int(user)}"
                      f"&created_at=gte.{since}") or []
    done = [r for r in rows if r.get("taken") and r.get("result_r") is not None]
    fol = [r for r in done if r["verdict"] != "NO-GO"]
    ovr = [r for r in done if r["verdict"] == "NO-GO"]
    s = lambda rs: sum(float(r["result_r"]) for r in rs)
    return (f"📒 <b>Last 7 days</b> · {len(rows)} checks, {sum(1 for r in rows if r.get('status') == 'skipped')} skipped\n"
            f"✅ Followed the check: {len(fol)} trades · <b>{s(fol):+.1f}R</b>\n"
            f"🔴 Overrode a NO-GO: {len(ovr)} trades · <b>{s(ovr):+.1f}R</b>")


def mytrades(msg, base):
    user = (msg.get("from") or {}).get("id")
    if (msg.get("chat") or {}).get("type") != "private" or not allowed(user):
        return False
    _api("sendMessage", dict(base, text=week_bill(user) if SB_URL else "Saving is not set up yet.",
                             disable_web_page_preview="true"))
    return True


# ---------------------------------------------------------------- grading (loop.py runs this every cycle)
def grade():
    rows = _sb("GET", "trade_checks?select=id,tg_user,side,entry,sl,tp,rr,verdict,created_at&status=eq.open")
    if not rows:
        return
    import pandas as pd
    from engine import closed, load
    df = closed(load("5m", "5d"))
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    for r in rows:
        t0 = pd.Timestamp(r["created_at"]).tz_convert("UTC")
        bars = df[df.index >= t0.floor("5min")]
        S = 1 if r["side"] == "BUY" else -1
        E, SL, TP = float(r["entry"]), float(r["sl"]), float(r["tp"])
        risk = abs(E - SL)
        st, res = None, None
        for _, b in bars.iterrows():
            hit_sl = b["Low"] <= SL if S == 1 else b["High"] >= SL
            hit_tp = b["High"] >= TP if S == 1 else b["Low"] <= TP
            if hit_sl:   # both in one candle counts as a loss (can't know which came first)
                st, res = "loss", -1.0
                break
            if hit_tp:
                st, res = "win", round(abs(TP - E) / risk, 2)
                break
        if not st and len(bars) and (bars.index[-1] - t0) > pd.Timedelta(hours=EXPIRE_H):
            st, res = "expired", round((float(bars["Close"].iloc[-1]) - E) * S / risk, 2)
        if not st:
            continue
        _sb("PATCH", f"trade_checks?id=eq.{r['id']}",
            {"status": st, "result_r": res, "closed_at": datetime.now(timezone.utc).isoformat()})
        word = {"win": "🏆 TP hit", "loss": "❌ SL hit", "expired": f"⏱ {EXPIRE_H}h, closed at market"}[st]
        tag = " · this was a NO-GO you overrode" if r["verdict"] == "NO-GO" else ""
        try:
            _api("sendMessage", {"chat_id": r["tg_user"], "parse_mode": "HTML", "disable_web_page_preview": "true",
                                 "text": f"{word}: {r['side']} {_f(E)} → <b>{res:+.2f}R</b>{tag}\n\n{week_bill(r['tg_user'])}"})
        except Exception as e:
            print("trade check result message failed:", e)


if __name__ == "__main__":
    try:
        grade()
    except Exception as e:
        print("trade check grading failed:", e)
