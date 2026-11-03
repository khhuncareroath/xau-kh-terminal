"""Chart feed for the dashboard: real candles on 5 timeframes plus everything the engine drew on them -> chart.json
Run after ict.py and confluence.py:  python chart.py
Times are unix seconds (UTC). Prices are COMEX gold futures (GC=F), delayed about 10 minutes by Yahoo."""
import json
import os
from datetime import datetime, timezone

import numpy as np

from engine import load
from ict import resample, session_vwap
from levels import to_ny

KEEP = {"5m": 288, "15m": 192, "1H": 168, "4H": 120, "D": 60}   # 1 day, 2 days, 1 week, 20 days, ~3 months


def jl(n):
    try:
        return json.load(open(n))
    except Exception:
        return {}


def rows(d):
    return [[int(t.timestamp()), round(float(r.Open), 2), round(float(r.High), 2), round(float(r.Low), 2), round(float(r.Close), 2),
             round(float(r.Volume), 0)] for t, r in zip(d.index, d.itertuples())]


def main():
    df = to_ny(load("5m", "59d"))
    df = df[df["Volume"] >= 0]
    vm, vs = session_vwap(df)
    from engine import live_source
    out = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "symbol": "XAUUSD spot" if live_source() == "spot" else "GC futures", "tf": {}}
    for tf, n in KEEP.items():
        d = resample(df, tf).tail(n)
        item = {"candles": rows(d)}
        if tf in ("5m", "15m"):
            step = "5min" if tf == "5m" else "15min"
            m = vm.resample(step).last().reindex(d.index)
            s = vs.resample(step).last().reindex(d.index)
            item["vwap"] = [[int(t.timestamp()), round(float(a), 2), round(float(b), 2)] for t, a, b in zip(d.index, m, s)
                            if np.isfinite(a) and np.isfinite(b)]
        out["tf"][tf] = item

    ict, conf, lv = jl("ict.json"), jl("confluence.json"), jl("levels.json")
    st = ict.get("setup") or {}
    out["setup"] = {k: st.get(k) for k in ("stage", "label", "dir", "zone", "entry", "stop", "target", "rr", "sweep_time",
                                          "shift_time", "sweep_extreme", "sweep_name")}
    for k in ("sweep_time", "shift_time"):
        if st.get(k):
            out["setup"][k + "_ts"] = int(datetime.fromisoformat(st[k]).timestamp())
    out["zones"] = [{"lo": z["low"], "hi": z["high"], "rating": z["rating"], "role": z["role"],
                     "label": ", ".join(s["name"] for s in z.get("sources", [])[:3])} for z in conf.get("zones", [])]
    keep = ("Prev day high", "Prev day low", "Midnight open", "Prev POC", "Prev VAH", "Prev VAL", "Asia high", "Asia low",
            "London high", "London low", "New York high", "New York low")
    out["levels"] = [{"name": x["name"], "price": x["price"]} for x in lv.get("ladder", []) if x["name"] in keep]
    out["pd_arrays"] = {tf: {"ob": (v or {}).get("order_blocks", []), "fvg": (v or {}).get("fvgs", [])}
                        for tf, v in (ict.get("timeframes") or {}).items()}
    out["sweeps"] = [{**s, "ts": int(datetime.fromisoformat(s["time"]).timestamp())} for s in ict.get("sweeps", []) if s.get("time")]
    with open("chart.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("chart.json:", {k: len(v["candles"]) for k, v in out["tf"].items()}, f"{os.path.getsize('chart.json') // 1024} KB")


if __name__ == "__main__":
    main()
