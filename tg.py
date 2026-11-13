"""Delivery helpers shared by notify.py, postnews.py and track.py.
Telegram: TELEGRAM_TOKEN + TELEGRAM_CHAT_ID. ntfy.sh: NTFY_TOPIC. Messages use Telegram HTML (bold, code)."""
import html
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

SITE = os.environ.get("SITE_URL", "")
TZ = ZoneInfo(os.environ.get("DISPLAY_TZ", "Asia/Phnom_Penh"))   # times in alerts are shown in your members' time zone


def esc(s):
    return html.escape(str(s), quote=False)


def local(ts):
    """'14:35 GMT+7' from a unix time or ISO string."""
    d = datetime.fromtimestamp(ts, TZ) if isinstance(ts, (int, float)) else datetime.fromisoformat(str(ts)).astimezone(TZ)
    off = int(d.utcoffset().total_seconds() // 3600)
    return d.strftime("%H:%M") + f" GMT{off:+d}"


def fmt(p):
    return f"{p:,.2f}"


def mark_post():
    """Remembers when the channel last got a message (session.py's quiet-time check-in uses it)."""
    try:
        import time as _t
        os.makedirs("data/cache", exist_ok=True)
        open("data/cache/last_post", "w").write(str(_t.time()))
    except Exception:
        pass


# ---------------------------------------------------------------- sections (Telegram group with Topics)
# Set TELEGRAM_GROUP_ID (a supergroup with Topics turned on, the bot is admin with "Manage topics") and every post
# goes to its own section. The bot creates the sections itself and closes them so only admins post there; members
# talk in the group's "General" topic. Without TELEGRAM_GROUP_ID everything goes to TELEGRAM_CHAT_ID as before.
SECTIONS = {   # key: (topic name, Telegram icon colour, wanted topic-icon emoji in order of preference)
    "rules":    ("Rules · ច្បាប់", 16766590, ["❗", "❗️", "‼", "📝"]),
    "announce": ("Announcement · ដំណឹង", 16478047, ["📣", "📢", "🔥"]),
    "signals":  ("Signals · សញ្ញា", 9367192, ["📈", "🎯", "💰"]),
    "setups":   ("Setup Analysis · វិភាគ Setup", 7322096, ["🔎", "🔍", "💡"]),
    "analysis": ("Analysis · វិភាគ", 7322096, ["📊", "📉", "🔎"]),
    "news":     ("News Events · ព័ត៌មាន", 16478047, ["📰", "🗞", "⚡"]),
    "proof":    ("Proof · លទ្ធផល", 16766590, ["🏆", "✅", "💎"]),
    "learn":    ("Education · មេរៀន", 13338331, ["📚", "🎓", "💡"]),
    "fun":      ("Fun Scalp · លេងសើច", 16478047, ["🎰", "🎲", "🎯"]),
    "indicator": ("Indicator · ឧបករណ៍", 9367192, ["📈", "📊", "💡"]),
}
OPEN_SECTIONS = {"indicator"}   # members may post here (feedback, screenshots): the topic is not closed
TOPICS_FILE = "topics.json"


def group_id():
    """The sectioned group: secret/variable TELEGRAM_GROUP_ID, else telegram.json (read every cycle, so a change
    there works within minutes without restarting the bot). Empty = old single-channel mode."""
    g = os.environ.get("TELEGRAM_GROUP_ID")
    if not g:
        try:
            g = json.load(open("telegram.json")).get("group_id")
        except Exception:
            g = None
    return str(g) if g else None


def section_for(title):
    """Every send() / send_photo() call passes a title; it decides the section."""
    t = (title or "").lower()
    if t == "rules":
        return "rules"
    if t == "announcement":
        return "announce"
    if t == "indicator":
        return "indicator"     # 📈 XAU.KH FLOW TradingView indicator topic (indicator_post.py)
    if t in ("guide", "lesson"):
        return "learn"
    if "fun scalp" in t:
        return "fun"        # 🎰 gamble-for-fun scalps and their results: their own topic, never in Signals
    if t in ("breaking", "after the news", "news soon"):
        return "news"
    if "proof" in t:
        return "proof"
    if any(k in t for k in ("session", "pulse", "check-in", "market map", "fundamentals", "week ahead")):
        return "analysis"
    if any(k in t for k in ("setup", "radar", "zone", "heads up", "near", "area", "level failed", "watch", "signal chart")):
        return "setups"     # the thinking behind trades: separate from the clean signal feed
    if any(k in t for k in ("update", "retest", "expired")):
        return "analysis"   # updates about a plan are not entries: 📈 Signals only gets entries and their results
    if any(k in t for k in ("buy", "sell", "plan", "idea", "result", "tp1")):
        return "signals"
    return "analysis"


# Thai letters look like Khmer and AI models sometimes mix them in (13 Nov 2026: Thai "ั" inside a Khmer word).
# Owner rule: never any Thai in posts. Look-alike Thai marks become the Khmer mark, every other Thai letter is removed.
_THAI_TO_KHMER = {0x0E31: "\u17D0", 0x0E34: "\u17B7", 0x0E35: "\u17B8", 0x0E36: "\u17B9", 0x0E37: "\u17BA",
                  0x0E38: "\u17BB", 0x0E39: "\u17BC", 0x0E48: "\u17CB", 0x0E4C: "\u17CD", 0x0E4D: "\u17C6", 0x0E47: "\u17CE"}
_NO_THAI = {c: _THAI_TO_KHMER.get(c) for c in range(0x0E00, 0x0E80)}


def no_thai(s):
    return s.translate(_NO_THAI) if isinstance(s, str) else s


def _clean(fields):
    return {k: (no_thai(v) if k in ("text", "caption", "name", "question", "explanation", "options") else v) for k, v in fields.items()}


def _api(method, fields, timeout=20):
    fields = _clean(fields)
    tok = os.environ.get("TELEGRAM_TOKEN")
    r = urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/{method}",
                                                      data=urllib.parse.urlencode(fields).encode()), timeout=timeout)
    return json.load(r).get("result")


def _topics():
    try:
        d = json.load(open(TOPICS_FILE))
    except Exception:
        d = {}
    if d.get("chat") != group_id():   # a different group: start fresh
        d = {"chat": group_id(), "topics": {}}
    return d


def thread_id(key, fresh=False):
    """The topic id for a section, creating (and closing to members) the topic the first time."""
    d = _topics()
    if fresh:
        d["topics"].pop(key, None)
    if key not in d["topics"]:
        name, color, want = SECTIONS[key]
        try:
            fields = {"chat_id": d["chat"], "name": name, "icon_color": color}
            icon = _icon(want)
            if icon:
                fields["icon_custom_emoji_id"] = icon
            res = _api("createForumTopic", fields)
            d["topics"][key] = res["message_thread_id"]
            try:   # closed topic = only admins (the bot) can post, members read and react
                if key in OPEN_SECTIONS:
                    raise StopIteration
                _api("closeForumTopic", {"chat_id": d["chat"], "message_thread_id": res["message_thread_id"]})
            except StopIteration:
                pass
            except Exception as e:
                print("could not close topic (give the bot 'Manage topics'):", e)
            json.dump(d, open(TOPICS_FILE, "w"), indent=1, ensure_ascii=False)
            print("created section", name)
        except Exception as e:
            print("could not create section", key, e)
            return None
    return d["topics"].get(key)


_ICONS = None


def _icon(want):
    """Telegram's free topic icons (the same ones you can pick in the app). Returns the id of the first wanted emoji."""
    global _ICONS
    if _ICONS is None:
        try:
            _ICONS = {st.get("emoji"): st.get("custom_emoji_id") for st in _api("getForumTopicIconStickers", {}) or []}
        except Exception as e:
            print("topic icons not available:", e)
            _ICONS = {}
    for e in want:
        if _ICONS.get(e):
            return _ICONS[e]
    return None


def setup_sections():
    """Creates every section once, in a fixed order, so the group looks complete from day one."""
    if group_id() and os.environ.get("TELEGRAM_TOKEN"):
        for key in SECTIONS:
            thread_id(key)


def msg_link(mid, title):
    """t.me link to a message in the private group (members of the group can open it)."""
    g = group_id()
    if not (g and isinstance(mid, int) and g.startswith("-100")):
        return None
    th = _topics()["topics"].get(section_for(title))
    return f"https://t.me/c/{g[4:]}/{th}/{mid}" if th else f"https://t.me/c/{g[4:]}/{mid}"


def target(title):
    """(chat_id, message_thread_id or None) for a post with this title."""
    group = group_id()
    if group:
        return group, thread_id(section_for(title))
    return os.environ.get("TELEGRAM_CHAT_ID"), None


def _send_tg(method, title, fields, files=None, timeout=20):
    """Sends with the right chat/topic. If a topic was deleted, it is made again once."""
    chat, th = target(title)
    for attempt in range(2):
        f = dict(_clean(fields), chat_id=chat)
        if th:
            f["message_thread_id"] = th
        try:
            if files is None:
                return _api(method, f, timeout)
            import uuid
            b = uuid.uuid4().hex
            parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in f.items()]
            for k, (fname, data) in files.items():
                parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
                             f'Content-Type: {"application/pdf" if fname.endswith(".pdf") else "image/png" if fname.endswith(".png") else "text/plain"}\r\n\r\n'.encode() + data + b"\r\n")
            parts.append(f"--{b}--\r\n".encode())
            tok = os.environ.get("TELEGRAM_TOKEN")
            req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/{method}", data=b"".join(parts),
                                         headers={"Content-Type": f"multipart/form-data; boundary={b}"})
            return json.load(urllib.request.urlopen(req, timeout=timeout)).get("result")
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")
            if th and attempt == 0 and ("thread not found" in msg or "TOPIC_DELETED" in msg or "TOPIC_ID_INVALID" in msg):
                th = thread_id(section_for(title), fresh=True)
                continue
            raise RuntimeError(msg[:200])


def send(text, title="XAU.KH", reply_to=None, silent=False):
    """Sends to Telegram (HTML) and ntfy. Returns the Telegram message_id (or True if only ntfy worked, None if nothing)."""
    tok, topic = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("NTFY_TOPIC")
    chat = group_id() or os.environ.get("TELEGRAM_CHAT_ID")
    mid = None
    if tok and chat:
        try:
            body = {"text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
            if silent:   # no sound / no notification for members
                body["disable_notification"] = "true"
            if reply_to:
                body["reply_parameters"] = json.dumps({"message_id": reply_to, "allow_sending_without_reply": True})
            res = _send_tg("sendMessage", title, body)
            mid = (res or {}).get("message_id") or True
        except Exception as e:
            print("telegram failed:", e)
    if topic:
        try:
            plain = html.unescape(text.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")
                                  .replace("<i>", "").replace("</i>", ""))
            h = {"Title": title.encode("utf-8").decode("latin-1", "ignore"), "Priority": "high", "Tags": "chart_with_upwards_trend"}
            if SITE:
                h["Click"] = SITE
            urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{topic}", data=plain.encode(), headers=h), timeout=20)
            mid = mid or True
        except Exception as e:
            print("ntfy failed:", e)
    if not mid:
        print("nothing sent (no secrets or all failed). Message was:\n" + text)
    else:
        mark_post()
    return mid


def send_photo(path, caption, title="XAU.KH", reply_to=None):
    """Sends a chart image with an HTML caption (Telegram limit: 1024 characters). Returns the message_id or None."""
    tok = os.environ.get("TELEGRAM_TOKEN")
    chat = group_id() or os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        print(f"photo not sent (no Telegram secrets): {path}\n{caption}")
        return None
    fields = {"caption": caption[:1024], "parse_mode": "HTML"}
    if reply_to:
        fields["reply_parameters"] = json.dumps({"message_id": reply_to, "allow_sending_without_reply": True})
    try:
        res = _send_tg("sendPhoto", title, fields, files={"photo": ("chart.png", open(path, "rb").read())}, timeout=40)
        mid = (res or {}).get("message_id")
        if mid:
            mark_post()
        return mid
    except Exception as e:
        print("telegram photo failed:", e)
        return None


def send_document(path, caption, title="XAU.KH", reply_to=None, filename=None):
    """Sends a file (e.g. a lesson PDF) with an HTML caption. Returns the message_id or None."""
    if not os.environ.get("TELEGRAM_TOKEN") or not (group_id() or os.environ.get("TELEGRAM_CHAT_ID")):
        print(f"document not sent (no Telegram secrets): {path}")
        return None
    fields = {"caption": caption[:1024], "parse_mode": "HTML"}
    if reply_to:
        fields["reply_parameters"] = json.dumps({"message_id": reply_to, "allow_sending_without_reply": True})
    try:
        res = _send_tg("sendDocument", title, fields,
                       files={"document": (filename or os.path.basename(path), open(path, "rb").read())}, timeout=60)
        mid = (res or {}).get("message_id")
        if mid:
            mark_post()
        return mid
    except Exception as e:
        print("telegram document failed:", e)
        return None


def log_alert(entry):
    """Every idea that went out is recorded so track.py can grade it later."""
    path = "alerts_log.json"
    try:
        log = json.load(open(path))
    except Exception:
        log = []
    log.append(entry)
    json.dump(log[-500:], open(path, "w"), indent=1)
