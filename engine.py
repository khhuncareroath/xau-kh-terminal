"""Engine: core data loading and technical indicator helpers.

Data source: Yahoo Finance GC=F (COMEX gold futures, front month). Two honest limits:
  * Yahoo's intraday futures data is delayed (usually about 10 minutes).
  * Yahoo only serves the last ~60 days of 5m candles. history.py saves every candle we see
    into data/gc_5m.csv.gz so the backtest sample keeps growing past 60 days.
Set XAU_SIM=path/to/csv to run every script on a saved or simulated file instead (used for tests).
"""
import os

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
    return _yahoo(interval, period)


def load_history():
    """Saved candles + the freshest 59 days from Yahoo, de-duplicated (fresh data wins)."""
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
