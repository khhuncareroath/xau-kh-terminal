"""News: this week's high/medium impact USD events -> news.json. Run: python news.py
Free feed rate-limits hard, so it refreshes at most every 3 hours and keeps the old file if the fetch fails."""
import json, os, time, urllib.request
from datetime import datetime, timezone
URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

def main():
    if os.path.exists("news.json") and time.time() - os.path.getmtime("news.json") < 3 * 3600:
        print("news.json is fresh, skipping"); return
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        raw = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        print("news fetch failed, keeping old file:", e); return
    ev = []
    for e in raw:
        if e.get("country") != "USD" or e.get("impact") not in ("High", "Medium"):
            continue
        t = datetime.fromisoformat(e["date"]).astimezone(timezone.utc)
        ev.append({"title": e["title"], "time": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "impact": e["impact"],
                   "forecast": e.get("forecast", ""), "previous": e.get("previous", "")})
    ev.sort(key=lambda x: x["time"])
    json.dump({"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "events": ev}, open("news.json", "w"), indent=2)
    print("news events:", len(ev))

if __name__ == "__main__":
    main()
