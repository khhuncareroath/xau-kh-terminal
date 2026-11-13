"""Member commands: the bot answers in the group (any topic) or in a private chat.

  /check   live chart + what the market is doing + where the next signal is + what to do (English + Khmer)
  /signal  the open signal and its status
  /proof   the live record
  /lesson  a random short lesson
  /help    the list

loop.py calls serve(until) in the gap between its 5-minute cycles, so replies come within seconds.
Telegram long polling (getUpdates); the offset is kept in data/cache so restarts don't answer twice.
Each member can ask once per COOLDOWN_S; the /check chart is re-drawn at most every CHART_TTL_S.
"""
from engine import closed
import html
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

OFFSET = "data/cache/updates_offset.json"
COOLDOWN_S = 45
CHART_TTL_S = 120
_last_user = {}
_chart = {"t": 0, "path": None, "text": None}
_menu = False


def _tok():
    return os.environ.get("TELEGRAM_TOKEN")


def api(method, fields, timeout=30):
    r = urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{_tok()}/{method}",
                                                      data=urllib.parse.urlencode(fields).encode()), timeout=timeout)
    return json.load(r).get("result")


def photo(fields, path):
    b = uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in fields.items()]
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="photo"; filename="c.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
                 + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{_tok()}/sendPhoto", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    return json.load(urllib.request.urlopen(req, timeout=40)).get("result")


def document(fields, path, filename):
    b = uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in fields.items()]
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="document"; filename="{filename}"\r\nContent-Type: application/pdf\r\n\r\n'.encode()
                 + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{_tok()}/sendDocument", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    return json.load(urllib.request.urlopen(req, timeout=60)).get("result")


def lesson_chapter(arg=None):
    from academy_content import LESSONS
    if arg and arg.isdigit():
        return next((x for x in LESSONS if x["ch"] == int(arg)), None)
    k = min(jl("academy_state.json", {"next": 1}).get("next", 1), len(LESSONS)) - 1
    return LESSONS[max(k, 0)]


def jl(n, d=None):
    try:
        return json.load(open(n))
    except Exception:
        return {} if d is None else d


def fmt(x):
    return f"{x:,.2f}"


# ---------------------------------------------------------------- answers
def check_answer():
    """(chart path or None, HTML caption <= 1024 visible characters)."""
    if time.time() - _chart["t"] < CHART_TTL_S and _chart["text"]:
        return _chart["path"], _chart["text"]
    import pandas as pd
    import desk
    import radar
    import session
    from engine import load
    from levels import to_ny
    df = closed(to_ny(load("5m", "20d")))
    lines = session.breakout_lines(df)
    st = radar.status(df, lines)
    ict, lv = jl("ict.json"), jl("levels.json")
    F = desk.facts(ict, {}, lv, df, lines, st["used"])
    p = st["price"]
    lean = F["lean"]
    trend = {"bull": "UP ↑ (buyers)", "bear": "DOWN ↓ (sellers)", None: "MIXED ↔"}[lean]
    km_trend = {"bull": "ឡើង", "bear": "ចុះ", None: "ចំហៀង"}[lean]
    zone = ("big day" if st["zone"] == 2 else "moving day" if st["zone"] == 1 else "quiet day")
    nxt = session.local(lines[2].timestamp()) if hasattr(session, "local") else ""
    live = st.get("live")
    out = [f"🔎 <b>GOLD CHECK</b> · <b>{fmt(p)}</b> · {session.local(time.time())}",
           f"4H trend: <b>{'UP ↑' if st['trend'] > 0 else 'DOWN ↓' if st['trend'] < 0 else 'none'}</b> · "
           f"structure D/4H/1H: <b>{trend}</b>",
           f"Day Meter {st['used'] * 100:.0f}% ({zone})"]
    out += desk.quick(ict, lv, df, lines)
    if live and live.get("status") in ("filled", "pending", "tp1"):
        side = "BUY" if live["dir"] == "bull" else "SELL"
        out.append(f"📈 <b>Open signal: {side} {fmt(live['entry'])}</b> · SL {fmt(live['stop'])} · TP {fmt(live['target'])}")
        km = f"មានសញ្ញា{'ទិញ' if side == 'BUY' else 'លក់'}កំពុងបើក · ធ្វើតាមសញ្ញា កុំបើកថ្មី"
        todo = "Follow the open signal. Don't open a new trade against it."
    else:
        idea = (jl("setup_idea.json").get("idea") or {})
        if idea and time.time() < idea.get("valid_until", 0):
            b_, s_ = idea["BUY"], idea["SELL"]
            out.append(f"📐 {idea.get('session', 'Session')} setup idea: BUY if a 15m candle closes above <b>{fmt(b_['trig'])}</b> "
                       f"({b_['trig'] - p:+,.1f}) · SELL below <b>{fmt(s_['trig'])}</b> ({s_['trig'] - p:+,.1f})")
            near = min(abs(b_['trig'] - p), abs(p - s_['trig'])) <= 3
        else:
            near = False
        todo = ("Price is close to a setup line: get ready, wait for the 15m close." if near else
                "No signal now. Waiting is the trade. Don't force an entry.")
        km = ("ជិតបន្ទាត់ setup: ត្រៀមខ្លួន រង់ចាំទៀន 15m បិទ" if near else "មិនទាន់មានសញ្ញា: រង់ចាំ កុំបង្ខំចូល")
    out += [f"👉 <b>{todo}</b>", f"🇰🇭 ទិសដៅ{km_trend} · {km}",
            "<i>Not financial advice · /signal /proof /lesson</i>"]
    text = "\n".join(out)
    path = None
    try:
        path = session.analysis_chart(df, lv, {}, lines, "check.png", f"Gold check · {session.local(time.time())}")
    except Exception as e:
        print("check chart failed:", e)
    _chart.update(t=time.time(), path=path, text=text)
    return path, text


def signal_answer():
    log = jl("alerts_log.json", [])
    a = next((x for x in reversed(log) if x.get("kind") in ("m15", "model", "scalp", "plan", "splus")), None)
    if not a:
        return "No signal yet. · មិនទាន់មានសញ្ញា"
    side = "BUY" if a["dir"] == "bull" else "SELL"
    stt = {"filled": "🟢 running", "pending": "⏳ waiting for entry", "win": "🏆 TP hit", "tp1": "✅ TP1 banked",
           "loss": "❌ SL hit", "expired": "⚪ expired", "missed": "⚪ missed", "timed out": "⏱ closed (time)"}.get(a["status"], a["status"])
    import session
    return (f"📈 <b>Latest signal: {side} {fmt(a['entry'])}</b> ({session.local(a['created'])})\n"
            f"SL {fmt(a['stop'])} · TP {fmt(a['target'])}\nStatus: <b>{stt}</b>"
            + (f" · R {a['R']:+.2f}" if a.get("R") is not None else ""))


def proof_answer():
    s = jl("results.json")
    if not s.get("traded"):
        return "No closed trades yet."
    names = {"m15": "📐 M15 signals (A+ / B+)", "fun": "🎰 fun scalps (gamble)", "model": "⭐ 4H breakout (old)", "scalp": "🤬 scalp", "splus": "🎯 S+ setup", "plan": "🤬 plan setups", "late": "⚠️ late plans",
             "post-news": "📰 after-news (stopped)", "setup": "old ICT ideas (stopped)", "watch": "old watch ideas (stopped)"}
    rows = []
    for k, v in (s.get("by_kind") or {}).items():
        if v.get("traded"):
            rows.append(f"{names.get(k, k)}: {v['wins']}W / {v['losses']}L · {v.get('total_R', 0):+.1f}R")
    return ("🏆 <b>Live record since 3 Nov</b> (every result, wins and losses)\n"
            f"All signals: {s['wins']} wins · {s['losses']} losses · {s.get('total_R', 0):+.1f}R (🎰 fun scalps counted apart)\n" + "\n".join(rows)
            + "\n\n📐 M15 setups are new: their live record above is the real test.\n"
              "<i>A few weeks is a small sample: judge by months.</i>")


def lesson_answer(arg=None):
    import academy
    from academy_content import LESSONS
    if arg and arg.isdigit():
        L = next((x for x in LESSONS if x["ch"] == int(arg)), None)
        if not L:
            return f"Chapter 1–{len(LESSONS)} · វាយ /lesson 1"
        return academy.text(L)
    k = min(jl("academy_state.json", {"next": 1}).get("next", 1), len(LESSONS)) - 1   # today's (latest posted) chapter
    return academy.text(LESSONS[max(k, 0)])


def academy_answer():
    import academy
    return academy.contents()


HELP = ("🤖 <b>XAU.KH bot</b>\n/check: gold right now + what to do · មើលមាសឥឡូវ\n/signal: latest signal · សញ្ញាចុងក្រោយ\n"
        "/proof: live record · លទ្ធផល\n/academy: all 45 lessons · មេរៀនទាំងអស់\n/lesson 5: open chapter 5 · បើកមេរៀនទី 5\n"
        "/app: open the XAU.KH App · បើកកម្មវិធី")

APP_TEXT = ("📲 <b>XAU.KH App · កម្មវិធី XAU.KH</b>\nPrice, direction, buy / sell areas, chart, news countdown, record.\n"
            "តម្លៃ ទិសដៅ តំបន់ទិញ/លក់ ក្រាហ្វ ម៉ោងព័ត៌មាន លទ្ធផល។ ចុចខាងក្រោម 👇")


# ---------------------------------------------------------------- loop
def handle(msg):
    text = (msg.get("text") or "").strip()
    if not text.startswith("/"):
        return
    if time.time() - msg.get("date", 0) > 600:   # old command (bot was offline): don't answer late
        return
    cmd = text.split()[0].split("@")[0].lower()
    if cmd not in ("/check", "/signal", "/proof", "/lesson", "/academy", "/help", "/start", "/app"):
        return
    user = (msg.get("from") or {}).get("id")
    if user and time.time() - _last_user.get((user, cmd), 0) < COOLDOWN_S and cmd != "/help":
        return
    _last_user[(user, cmd)] = time.time()
    chat = msg["chat"]["id"]
    base = {"chat_id": chat, "parse_mode": "HTML",
            "reply_parameters": json.dumps({"message_id": msg["message_id"], "allow_sending_without_reply": True})}
    if msg.get("is_topic_message") and msg.get("message_thread_id"):
        base["message_thread_id"] = msg["message_thread_id"]
    try:
        if cmd == "/check":
            path, text = check_answer()
            if path:
                photo(dict(base, caption=text[:1024]), path)
                return
            api("sendMessage", dict(base, text=text, disable_web_page_preview="true"))
            return
        if cmd in ("/app", "/start", "/help"):   # 📲 the XAU.KH App button (tg.APP_LINK) under the answer
            import tg
            api("sendMessage", dict(base, text=(APP_TEXT if cmd == "/app" else HELP), disable_web_page_preview="true",
                                    reply_markup=tg.app_markup("today")))
            return
        arg = text.split()[1] if len(text.split()) > 1 else None
        if cmd == "/lesson":   # the full PDF when that chapter has one, else the text lesson
            import academy
            L = lesson_chapter(arg)
            pdf = L and academy.pdf_path(L["ch"])
            if pdf:
                document(dict(base, caption=academy.PDF_CAPTION.format(ch=L["ch"], t=L["title"])
                              + f"\n\n<i>/lesson {L['ch'] + 1} = next · /academy = all</i>"), pdf, academy.pdf_name(L))
                return
        text = {"/signal": signal_answer, "/proof": proof_answer, "/lesson": lambda: lesson_answer(arg),
                "/academy": academy_answer}.get(cmd, lambda: HELP)()
        api("sendMessage", dict(base, text=text, disable_web_page_preview="true"))
    except Exception as e:
        print("listener reply failed:", cmd, e)


def serve(until):
    """Answer commands until the unix time `until`. Never raises."""
    if not _tok():
        time.sleep(max(0, until - time.time()))
        return
    global _menu
    if not _menu:
        try:   # show the commands in Telegram's "/" menu
            api("setMyCommands", {"commands": json.dumps([
                {"command": "check", "description": "Gold right now + what to do · មើលមាសឥឡូវ"},
                {"command": "signal", "description": "Latest signal · សញ្ញាចុងក្រោយ"},
                {"command": "proof", "description": "Live record, wins and losses · លទ្ធផល"},
                {"command": "academy", "description": "All 45 lessons · មេរៀនទាំងអស់"},
                {"command": "lesson", "description": "Today's lesson, or /lesson 5 · មេរៀន"},
                {"command": "app", "description": "Open the XAU.KH App · បើកកម្មវិធី"}], ensure_ascii=False)})
            _menu = True
        except Exception as e:
            print("setMyCommands failed:", e)
    try:
        off = jl(OFFSET).get("offset", 0)
    except Exception:
        off = 0
    while time.time() < until - 3:
        wait = int(max(1, min(25, until - time.time() - 3)))
        try:
            ups = api("getUpdates", {"offset": off, "timeout": wait, "allowed_updates": json.dumps(["message"])},
                      timeout=wait + 10) or []
        except urllib.error.HTTPError as e:
            print("getUpdates:", e.code)   # 409 = another runner is polling: just wait
            time.sleep(min(10, max(0, until - time.time())))
            continue
        except Exception as e:
            print("getUpdates failed:", e)
            time.sleep(min(10, max(0, until - time.time())))
            continue
        for u in ups:
            off = u["update_id"] + 1
            if u.get("message"):
                handle(u["message"])
        if ups:
            os.makedirs("data/cache", exist_ok=True)
            json.dump({"offset": off}, open(OFFSET, "w"))
    time.sleep(max(0, until - time.time()))


if __name__ == "__main__":   # manual test: answer for 60 seconds
    serve(time.time() + 60)
