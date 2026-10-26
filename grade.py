"""Scorecard: freezes a briefing every 4 hours and grades it 6 hours later -> grade_log.json, grade.json.
Bias held = price ended on the bias side. Zone respected = price touched an A/B zone and ended on its correct side."""
import json, os
from datetime import datetime, timezone

def jl(n, d):
    return json.load(open(n)) if os.path.exists(n) else d

def main():
    ict, conf = jl("ict.json", {}), jl("confluence.json", {})
    price = conf.get("price") or ict.get("price")
    if not price: print("no price"); return
    now = datetime.now(timezone.utc).timestamp()
    log = jl("grade_log.json", [])
    W = {"D": 1, "4H": 1.5, "1H": 1.5, "15m": 1, "5m": .5}
    sc = sum({"bull": 1, "bear": -1}.get((v or {}).get("bias"), 0) * W.get(k, 0) for k, v in (ict.get("timeframes") or {}).items())
    d = 1 if sc >= 1.5 else -1 if sc <= -1.5 else 0
    bid = int(now // (4 * 3600))
    if not any(e["id"] == bid for e in log):
        zs = [{"lo": z["low"], "hi": z["high"], "role": z["role"], "rating": z["rating"]} for z in conf.get("zones", [])
              if z.get("rating") in ("A", "B") and z.get("role") in ("support", "resistance")][:4]
        log.append({"id": bid, "t": now, "dir": d, "p0": price, "hi": price, "lo": price, "zones": zs, "done": False})
    cs = (ict.get("chart") or {}).get("candles", [])[-4:]
    for e in log:
        if e["done"]: continue
        for c in cs: e["hi"], e["lo"] = max(e["hi"], c[1]), min(e["lo"], c[2])
        e["hi"], e["lo"] = max(e["hi"], price), min(e["lo"], price)
        if now - e["t"] >= 6 * 3600:
            e["done"], e["p1"] = True, price
            e["held"] = None if e["dir"] == 0 else (price - e["p0"]) * e["dir"] > 0
            for z in e["zones"]:
                z["touched"] = e["lo"] <= z["hi"] and e["hi"] >= z["lo"]
                z["ok"] = z["touched"] and (price >= z["lo"] if z["role"] == "support" else price <= z["hi"])
    log = log[-200:]
    done = [e for e in log if e["done"]]
    gb = [e for e in done if e["held"] is not None]
    zz = [(z, e) for e in done for z in e["zones"] if "touched" in z]
    by = {r: {"touched": sum(z["touched"] for z, _ in zz if z["rating"] == r), "respected": sum(z["ok"] for z, _ in zz if z["rating"] == r)} for r in ("A", "B")}
    out = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "graded": len(gb), "held": sum(e["held"] for e in gb),
           "held_pct": round(100 * sum(e["held"] for e in gb) / len(gb)) if gb else 0,
           "zones_touched": sum(v["touched"] for v in by.values()), "zones_respected": sum(v["respected"] for v in by.values()), "by_rating": by}
    json.dump(log, open("grade_log.json", "w")); json.dump(out, open("grade.json", "w"), indent=2); print(out)

if __name__ == "__main__":
    main()
