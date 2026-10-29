"""Spot offset (optional): your levels come from COMEX futures (they have real volume, which VWAP and volume profile
need), but most members trade spot XAUUSD at a broker, and the two prices differ by several dollars.
This measures that gap so alerts can show the spot-equivalent entry.  -> spot.json

Needs a free Twelve Data key in the repo secret TWELVEDATA_KEY (one call per run fits the free daily allowance).
Without the key it does nothing and alerts simply skip the spot line."""
import json
import os
import time
import urllib.request

import pandas as pd

from engine import load


def main():
    key = os.environ.get("TWELVEDATA_KEY")
    if not key:
        print("spot: no TWELVEDATA_KEY, skipping"); return
    try:
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=36&timezone=UTC&apikey={key}"
        vals = json.load(urllib.request.urlopen(url, timeout=20)).get("values", [])
        spot = pd.Series({pd.Timestamp(v["datetime"], tz="UTC"): float(v["close"]) for v in vals})
        fut = load("5m", "2d")["Close"]
        if fut.index.tz is None:
            fut.index = fut.index.tz_localize("UTC")
        both = pd.concat([fut.tz_convert("UTC"), spot], axis=1, join="inner").dropna()
        if len(both) < 6:
            print("spot: too few matching candles"); return
        basis = float((both.iloc[:, 0] - both.iloc[:, 1]).median())   # median of matched candles ignores odd prints
        json.dump({"basis": round(basis, 2), "matched": len(both), "t": time.time(), "spot": float(spot.sort_index().iloc[-1])},
                  open("spot.json", "w"), indent=2)
        print(f"spot: futures - spot = {basis:.2f} over {len(both)} candles")
    except Exception as e:
        print("spot: failed, alerts will skip the spot line:", e)


if __name__ == "__main__":
    main()
