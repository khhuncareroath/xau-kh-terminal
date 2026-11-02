"""News: this week's high/medium impact USD events -> news.json. Run: python news.py

The free ForexFactory feed rate-limits hard, so it is fetched at most every 3 hours, plus every 30 minutes in the
2 hours after a high-impact release (to pick up the "actual" figure for postnews.py). If a fetch fails, the old file
is kept. Freshness is judged by the "time" saved INSIDE news.json: the file's own date cannot be trusted, because
GitHub resets every file's date when it checks the repo out (that bug froze the calendar from Oct 27 to Nov 2)."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
MAX_AGE = timedelta(hours=3)
AFTER_RELEASE = timedelta(minutes=30)


def saved():
    try:
        d = json.load(open("news.json"))
        return d, datetime.strptime(d["time"], "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
    except Exception:
        return None, None


def needs_refresh(d, t, now):
    if d is None or t is None:
        return "no saved calendar"
    if now - t >= MAX_AGE:
        return f"calendar is {(now - t).total_seconds() / 3600:.1f}h old"
    # new week: the saved calendar was fetched before this week's Sunday 21:00 UTC open
    week_start = (now - timedelta(days=(now.weekday() + 1) % 7)).replace(hour=21, minute=0, second=0, microsecond=0)
    if week_start > now:
        week_start -= timedelta(days=7)
    if t < week_start <= now:
        return "new trading week"
    for e in d.get("events", []):
        if e.get("impact") != "High" or e.get("actual"):
            continue
        et = datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        if timedelta(0) <= now - et <= timedelta(hours=2) and now - t >= AFTER_RELEASE:
            return f"waiting for the actual figure of {e['title']}"
    return None


def main():
    now = datetime.now(timezone.utc)
    d, t = saved()
    why = needs_refresh(d, t, now)
    if not why:
        print(f"news.json is fresh (fetched {t:%a %H:%M} UTC), skipping"); return
    print("refreshing news:", why)
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        raw = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        print("news fetch failed, keeping old file:", e); return
    ev = []
    for e in raw:
        if e.get("country") != "USD" or e.get("impact") not in ("High", "Medium"):
            continue
        et = datetime.fromisoformat(e["date"]).astimezone(timezone.utc)
        ev.append({"title": e["title"], "time": et.strftime("%Y-%m-%dT%H:%M:%SZ"), "impact": e["impact"],
                   "forecast": e.get("forecast", ""), "previous": e.get("previous", ""), "actual": e.get("actual", "")})
    ev.sort(key=lambda x: x["time"])
    json.dump({"time": now.strftime("%Y-%m-%d %H:%M UTC"), "events": ev}, open("news.json", "w"), indent=2)
    print("news events:", len(ev))


if __name__ == "__main__":
    main()
