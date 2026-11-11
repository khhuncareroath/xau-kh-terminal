"""Engine: core data loading and technical indicator helpers.

Live data (when the TWELVEDATA_KEY secret is set): spot XAUUSD, the price members trade at their brokers.
  * Prices: Twelve Data 5m candles (about 17 days per call), on top of the Dukascopy spot history
    (data/xau_5m.csv.gz, restored from the spot-data branch) for the older days.
  * Volume: spot gold has no central exchange, so it has no real volume. VWAP and volume profile use the
    volume of COMEX gold futures (Yahoo GC=F) at the same 5-minute time: same market, same activity.
  * Each source is fetched at most once per 4 minutes and shared by every script in that cycle, which keeps
    Twelve Data well inside its free daily limit. If Twelve Data fails, everything falls back to Yahoo futures.
Set LIVE_SOURCE=futures to force the old Yahoo futures prices.

Fallback data source: Yahoo Finance GC=F (COMEX gold futures, front month). Two honest limits:
  * Yahoo's intraday futures data is delayed (usually about 10 minutes).
  * Yahoo only serves the last ~60 days of 5m candles. history.py saves every candle we see
    into data/gc_5m.csv.gz so the backtest sample keeps growing past 60 days.
Set XAU_SIM=path/to/csv to run every script on a saved or simulated file instead (used for tests).
"""
import json
import os
import time

import numpy as np
import pandas as pd

HIST = "data/gc_5m.csv.gz"


def _read_csv(path):
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


def _yahoo(interval, period):
    import yfinance as yf
    df = yf.download("GC=F", period=period, interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


CACHE_S = 240
TD_URL = "https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=5000&timezone=UTC&apikey={key}"


def _cached(name, fetch):
    """Runs fetch() at most once per CACHE_S seconds across all scripts; the time is kept inside the cache folder
    (not taken from file dates, which a git checkout resets)."""
    os.makedirs("data/cache", exist_ok=True)
    path, meta = f"data/cache/{name}.csv.gz", f"data/cache/{name}.json"
    try:
        info = json.load(open(meta))
        if time.time() - info["t"] < CACHE_S and os.path.exists(path):
            return _read_csv(path), info
    except Exception:
        pass
    df, info = fetch()
    df.to_csv(path, compression="gzip")
    info["t"] = time.time()
    json.dump(info, open(meta, "w"))
    return df, info


def _yahoo_5m():
    df = _yahoo("5m", "59d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    return df.tz_convert("UTC")[["Open", "High", "Low", "Close", "Volume"]].astype(float), {"source": "yahoo"}


def _twelvedata():
    import urllib.request
    r = json.load(urllib.request.urlopen(TD_URL.format(key=os.environ["TWELVEDATA_KEY"]), timeout=25))
    if r.get("status") != "ok" or not r.get("values"):
        raise RuntimeError(f"Twelve Data: {r.get('message', r.get('status'))}")
    v = r["values"]
    df = pd.DataFrame({"Open": [float(x["open"]) for x in v], "High": [float(x["high"]) for x in v],
                       "Low": [float(x["low"]) for x in v], "Close": [float(x["close"]) for x in v], "Volume": 0.0},
                      index=pd.to_datetime([x["datetime"] for x in v], utc=True)).sort_index()
    return df, {"source": "twelvedata", "bars": len(df)}


def live_source():
    """'spot' when Twelve Data is configured and answering, else 'futures'. Written to data/cache/source.json."""
    try:
        return json.load(open("data/cache/source.json"))["source"]
    except Exception:
        return "spot" if os.environ.get("TWELVEDATA_KEY") and os.environ.get("LIVE_SOURCE", "spot") == "spot" else "futures"


def _spot_5m():
    """Spot prices (Dukascopy history + Twelve Data recent) with futures volume. Raises if Twelve Data is unavailable."""
    td, _ = _cached("twelvedata", _twelvedata)
    fut, _ = _cached("yahoo", _yahoo_5m)
    parts = [td]
    if os.path.exists(SPOT):
        base = _read_csv(SPOT)
        parts.insert(0, base[base.index < td.index[0]])
    px = pd.concat(parts)
    px = px[~px.index.duplicated(keep="last")].sort_index()
    vol = fut["Volume"].reindex(px.index)
    if vol.notna().sum() > 0.5 * len(td):
        # the newest futures bars are ~10 min late: use the recent median until they arrive
        px["Volume"] = vol.fillna(float(fut["Volume"].tail(48).median()))
    else:   # futures volume missing (holiday, Yahoo down): Dukascopy volume where present, else flat
        px["Volume"] = px["Volume"].where(px["Volume"] > 0, 1.0)
    return px


def closed(df, minutes=5, now=None):
    """Only candles that have CLOSED by now (by the clock, not by position). Safe to apply twice. Dropping "the last
    row" was wrong two ways: the feed sometimes has not opened the new candle yet (a closed candle got dropped), and
    session.py + setupidea.watch dropped it twice (M15 signals came 5-10 min late)."""
    if os.environ.get("XAU_SIM") and now is None:
        return df.iloc[:-1]
    now = pd.Timestamp(time.time() if now is None else now, unit="s", tz="UTC")
    idx = df.index if df.index.tz is not None else df.index.tz_localize("UTC")
    return df[idx + pd.Timedelta(minutes=minutes) <= now]


def load(interval="5m", period="30d"):
    sim = os.environ.get("XAU_SIM")
    if sim:
        df = _read_csv(sim)
        days = int(str(period).rstrip("d")) if str(period).endswith("d") else 60
        df = df[df.index >= df.index[-1] - pd.Timedelta(days=days)]
        if interval != "5m":
            rule = {"1h": "1h", "15m": "15min"}.get(interval, interval)
            df = df.resample(rule).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()
        return df
    if interval == "5m" and os.environ.get("TWELVEDATA_KEY") and os.environ.get("LIVE_SOURCE", "spot") == "spot":
        try:
            df = _spot_5m()
            json.dump({"source": "spot", "t": time.time()}, open("data/cache/source.json", "w"))
            days = int(str(period).rstrip("d")) if str(period).endswith("d") else 60
            return df[df.index >= df.index[-1] - pd.Timedelta(days=days)]
        except Exception as e:
            print(f"spot data unavailable, using Yahoo futures: {e}")
            os.makedirs("data/cache", exist_ok=True)
            json.dump({"source": "futures", "t": time.time(), "error": str(e)[:200]}, open("data/cache/source.json", "w"))
            df, _ = _cached("yahoo", _yahoo_5m)
            days = int(str(period).rstrip("d")) if str(period).endswith("d") else 60
            return df[df.index >= df.index[-1] - pd.Timedelta(days=days)]
    return _yahoo(interval, period)


SPOT = "data/xau_5m.csv.gz"


def load_history():
    """For the backtest. XAU_SOURCE=spot: years of spot XAUUSD from dukascopy.py.
    Otherwise: saved futures candles + the freshest 59 days from Yahoo, de-duplicated (fresh data wins)."""
    if os.environ.get("XAU_SOURCE") == "spot" and os.path.exists(SPOT) and not os.environ.get("XAU_SIM"):
        return _read_csv(SPOT)
    fresh = load("5m", "59d")
    if fresh.index.tz is None:
        fresh.index = fresh.index.tz_localize("UTC")
    if os.path.exists(HIST) and not os.environ.get("XAU_SIM"):
        old = _read_csv(HIST)
        fresh = pd.concat([old, fresh.tz_convert("UTC")])
        fresh = fresh[~fresh.index.duplicated(keep="last")].sort_index()
    return fresh


def atr(df, window=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()
