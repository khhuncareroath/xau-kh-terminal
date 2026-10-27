"""Health check -> status.json. Flags stale or broken data and messages the OWNER (never a public channel).
Runs last, even when an earlier step failed. Env: JOB_STATUS, TELEGRAM_TOKEN, TELEGRAM_OWNER_CHAT_ID (falls back to TELEGRAM_CHAT_ID if it is a private chat id)."""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MAX_AGE = {"ict.json": 90, "confluence.json": 90, "levels.json": 90, "quality.json": 90, "macro.json": 90, "news.json": 12 * 60}   # minutes
NEED = {"ict.json": ("timeframes", "setup", "chart"), "confluence.json": ("zones",), "levels.json": ("ladder",)}
COOLDOWN = 3 * 3600


def jl(n):
    try:
        return json.load(open(n))
    except Exception:
        return None


def market_open(ny):   # gold futures: Sunday 18:00 to Friday 17:00 New York
    wd, h = ny.weekday(), ny.hour
    return not (wd == 5 or (wd == 4 and h >= 17) or (wd == 6 and h < 18))


def age_min(d, now):
    try:
        return (now - datetime.strptime(d["time"], "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)).total_seconds() / 60
    except Exception:
        return None


def send(msg):
    tok = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_OWNER_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID", "")
    if not tok or not chat or chat.startswith("@"):
        print("owner alert (not sent, set TELEGRAM_OWNER_CHAT_ID):", msg); return False
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=data), timeout=20)
        return True
    except Exception as e:
        print("owner alert failed:", e); return False


def main():
    now, ny = datetime.now(timezone.utc), datetime.now(ZoneInfo("America/New_York"))
    open_ = market_open(ny)
    prev = jl("status.json") or {}
    problems, files = [], {}
    job = os.environ.get("JOB_STATUS", "success")
    if job != "success":
        problems.append(f"workflow step failed ({job})")
    for name, limit in MAX_AGE.items():
        d = jl(name)
        if d is None:
            if name in NEED:
                problems.append(f"{name} missing or unreadable")
            continue
        a = age_min(d, now)
        files[name] = {"age_min": None if a is None else round(a)}
        miss = [k for k in NEED.get(name, ()) if k not in d]
        if miss:
            problems.append(f"{name} lacks {', '.join(miss)}")
        if open_ and a is not None and a > limit:
            problems.append(f"{name} is {round(a)} min old (limit {limit})")
    out = {"time": now.strftime("%Y-%m-%d %H:%M UTC"), "ok": not problems, "market_open": open_, "job": job,
           "problems": problems, "files": files, "last_alert": prev.get("last_alert", 0), "alerting": prev.get("alerting", False)}
    t = time.time()
    if problems and (t - out["last_alert"] > COOLDOWN):
        if send("XAU.KH data problem:\n- " + "\n- ".join(problems)):
            out["last_alert"], out["alerting"] = t, True
    elif not problems and out["alerting"]:
        send("XAU.KH data is healthy again.")
        out["alerting"] = False
    json.dump(out, open("status.json", "w"), indent=2)
    print("status ok" if out["ok"] else "status problems: " + "; ".join(problems))


if __name__ == "__main__":
    main()
