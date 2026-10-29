"""Delivery helpers shared by notify.py, postnews.py and track.py.
Telegram: TELEGRAM_TOKEN + TELEGRAM_CHAT_ID. ntfy.sh: NTFY_TOPIC. Messages use Telegram HTML (bold, code)."""
import html
import json
import os
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


def send(text, title="XAU.KH", reply_to=None):
    """Sends to Telegram (HTML) and ntfy. Returns the Telegram message_id (or True if only ntfy worked, None if nothing)."""
    tok, chat, topic = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID"), os.environ.get("NTFY_TOPIC")
    mid = None
    if tok and chat:
        try:
            body = {"chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
            if reply_to:
                body["reply_parameters"] = json.dumps({"message_id": reply_to, "allow_sending_without_reply": True})
            r = urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage",
                                                              data=urllib.parse.urlencode(body).encode()), timeout=20)
            mid = json.load(r).get("result", {}).get("message_id") or True
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
    return mid


def log_alert(entry):
    """Every idea that went out is recorded so track.py can grade it later."""
    path = "alerts_log.json"
    try:
        log = json.load(open(path))
    except Exception:
        log = []
    log.append(entry)
    json.dump(log[-500:], open(path, "w"), indent=1)
