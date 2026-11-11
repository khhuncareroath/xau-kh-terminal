"""Live signals from the research models -> live_models.json. Run every cycle after ict.py.

Each research model in research.py is run on the last 20 days of 5m candles with the SAME code the backtest uses,
so a live signal is exactly what the backtest would have taken. Trick: a few flat candles are appended after the
last real candle. A model that would enter on one of those future candles has just triggered: that is a live signal,
with its entry (the current price), stop and target computed by the model itself.

notify.py sends a trade-style alert only for models that backtest.json marks as proven. Signals from unproven
models are still saved here (and shown on the site) so their live record can be compared with the backtest."""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import research
from backtest import candidates
from engine import load
from levels import to_ny

PAD = research.LAT + 3


def jl(n):
    try:
        return json.load(open(n))
    except Exception:
        return {}


def main():
    df = to_ny(load("5m", "20d"))
    df = df[df["Volume"] >= 0].iloc[:-1]          # drop the candle that is still forming
    n_real = len(df)
    last = float(df["Close"].iloc[-1])
    pad_idx = [df.index[-1] + pd.Timedelta(minutes=5 * (k + 1)) for k in range(PAD)]
    pad = pd.DataFrame({"Open": last, "High": last, "Low": last, "Close": last, "Volume": 0.0}, index=pad_idx)
    dfp = pd.concat([df, pad])
    dfp.attrs["n_real"] = n_real   # models use it to refuse candles that have not really closed yet

    found = []
    real_run = research._run_trade

    def recorder(o, h, l, c, j0, j_end, sg, stop, tgt):
        if j0 >= n_real - 2:   # entry now, or up to 10 minutes ago if a cycle was missed
            found.append({"entry": float(o[j0]), "dir": "bull" if sg > 0 else "bear", "stop": float(stop), "target": float(tgt),
                          "_t": dfp.index[j0]})
        return real_run(o, h, l, c, j0, j_end, sg, stop, tgt)

    real_scaled = research._run_scaled

    def recorder_scaled(o, h, l, c, j0, j_end, sg, stop, tp1_r, tp2_r, part=0.5):
        if j0 >= n_real - 2:
            en = float(o[j0]); risk = abs(en - stop)
            found.append({"entry": en, "dir": "bull" if sg > 0 else "bear", "stop": float(stop), "target": en + sg * tp2_r * risk,
                          "tp1": en + sg * tp1_r * risk, "part": part, "_t": dfp.index[j0]})
        return real_scaled(o, h, l, c, j0, j_end, sg, stop, tp1_r, tp2_r, part)

    research._run_trade = recorder
    research._run_scaled = recorder_scaled
    sigs = []
    try:
        runs = {"sweep_htf": lambda d: research.sweep_htf(d, candidates), "value": research.value_models,
                "sessions": research.session_breakouts, "trend_pullback": research.trend_pullback, "vwap_fade": research.vwap_fade,
                "trend_breakout": research.trend_breakout, "trend_buy": research.trend_buy,
                "trend_tight": research.trend_tight, "trend_intraday": research.trend_intraday, "breakout_cisd": research.breakout_cisd, "crt_daily": research.crt_daily, "vp_shape": research.vp_shape, "vp_late": research.vp_late, "range_extreme": research.range_extreme}
        for name, fn in runs.items():
            before = len(found)
            try:
                res = fn(dfp)
            except Exception as e:
                print(f"  {name}: failed ({e})")
                continue
            new = found[before:]
            if not new:
                continue
            for s in new:
                t = s.pop("_t")
                # for groups of models, the sub-model is the one whose trade list has a trade starting at that time
                lists = res.items() if isinstance(res, dict) else [(name, res)]
                m = next((k for k, v in lists if any(x[0] == t for x in v)), None)
                if m is None:
                    continue   # the model computed levels but then rejected the trade (for example the stop was too small)
                s["trigger_time"] = str(t)   # planned entry time: identical on every cycle, so the alert is sent once
                risk = abs(s["entry"] - s["stop"])
                sigs.append({**{k: round(v, 2) if isinstance(v, float) else v for k, v in s.items()}, "model": m,
                             "rr": round(abs(s["target"] - s["entry"]) / risk, 2) if risk else None})
    finally:
        research._run_trade = real_run
        research._run_scaled = real_scaled

    bt = jl("backtest.json").get("models", {})
    for s in sigs:
        m = bt.get(s["model"], {})
        s["proven"] = bool(m.get("proven"))
        s["backtest"] = m.get("all")
        s["description"] = research.DESCRIBE.get(s["model"], s["model"])
        if s["model"] in research.TREND_PREFERENCE:   # STRONG COMBO label: how much of a normal day has already moved
            try:
                u = research.day_used(df, pd.Timestamp(s["trigger_time"]))
                s["day_used"] = round(u, 2) if u is not None else None
                e = research.efficiency(df, pd.Timestamp(s["trigger_time"]))
                s["efficiency"] = round(e, 3) if e is not None else None
                cl = research.close_location(df, pd.Timestamp(s["trigger_time"]), s["dir"])
                s["close_loc"] = round(cl, 3) if cl is not None else None
            except Exception as e:
                print("day_used failed:", e)
    out = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "last_bar": str(df.index[-1]),
           "price": round(last, 2), "signals": sigs}
    json.dump(out, open("live_models.json", "w"), indent=1)
    print(f"live models: {len(sigs)} signal(s)" + "".join(f"\n  {s['model']} {s['dir']} @ {s['entry']} stop {s['stop']} "
                                                         f"target {s['target']} proven={s['proven']}" for s in sigs))


if __name__ == "__main__":
    main()
