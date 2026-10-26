"""Quality filter: scores how clean the current environment is (0-100) -> quality.json. Run after confluence.py, news.py, macro.py."""
import json, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def jl(n):
    return json.load(open(n)) if os.path.exists(n) else {}

def main():
    ict, conf, news, macro = jl("ict.json"), jl("confluence.json"), jl("news.json"), jl("macro.json")
    now, ny = datetime.now(timezone.utc), datetime.now(ZoneInfo("America/New_York"))
    score, flags = 50, []
    tfb = {k: (v or {}).get("bias") for k, v in (ict.get("timeframes") or {}).items()}
    htf = [tfb.get(k) for k in ("D", "4H", "1H")]
    ref = max(("bull", "bear"), key=htf.count) if htf.count("bull") != htf.count("bear") else None
    n = htf.count(ref) if ref else 0
    score += 20 if n == 3 else 10 if n == 2 else -10
    if n < 2: flags.append("Higher timeframes disagree")
    st = ict.get("setup") or {}
    if (st.get("stage") or 0) >= 2 and st.get("stage") != 4: score += 15
    price = conf.get("price") or ict.get("price") or 0
    near = [z for z in conf.get("zones", []) if z.get("rating") == "A" and abs(z.get("distance", 99)) <= 6]
    if near: score += 10
    else: flags.append("No A-rated zone within 6 points")
    m = macro.get("score")
    if m and ref:
        agree = (m > 0) == (ref == "bull")
        score += 10 if agree else -10
        if not agree: flags.append("Dollar and yields point the other way")
    for e in news.get("events", []):
        mins = (datetime.fromisoformat(e["time"].replace("Z", "+00:00")) - now).total_seconds() / 60
        if e["impact"] == "High" and -15 <= mins <= 60: score -= 25; flags.append(f"{e['title']} within 60 min"); break
        if e["impact"] == "High" and 60 < mins <= 180: score -= 10; flags.append(f"{e['title']} within 3 hours"); break
    if ny.weekday() == 4 and ny.hour >= 12: score -= 15; flags.append("Friday afternoon: thin liquidity and weekend risk")
    if ny.weekday() == 6: score -= 15; flags.append("Weekend open: gaps and thin liquidity")
    score = max(0, min(100, score))
    g = "A" if score >= 75 else "B" if score >= 60 else "C" if score >= 40 else "Avoid"
    json.dump({"time": now.strftime("%Y-%m-%d %H:%M UTC"), "score": score, "grade": g, "flags": flags}, open("quality.json", "w"), indent=2)
    print("quality", g, score, flags)

if __name__ == "__main__":
    main()
