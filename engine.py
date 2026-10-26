"""Engine: core data loading and technical indicator helpers."""
import yfinance as yf
import pandas as pd
import numpy as np

def load(interval="5m", period="30d"):
    df = yf.download("GC=F", period=period, interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def atr(df, window=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()