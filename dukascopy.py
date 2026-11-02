"""Dukascopy history: free 1-minute spot XAUUSD candles for years, saved as 5-minute candles in data/xau_5m.csv.gz.
This is the price your members trade (spot), not futures, and it gives the backtest years instead of 60 days.

Run:  python dukascopy.py            (first run downloads DUKA_DAYS days, default 730 = 2 years; later runs only add new days)
      python dukascopy.py --check    (downloads one recent day and prints it, to verify the format)

Dukascopy files: https://datafeed.dukascopy.com/datafeed/XAUUSD/YYYY/MM/DD/BID_candles_min_1.bi5
(MM is zero-based: January = 00). Each file is LZMA-compressed; each record is 24 bytes: seconds from the start of the
UTC day, four prices as integers, and a float volume. The script detects the price scale and the price order itself,
and refuses to save anything that fails the sanity checks, so a format change cannot silently corrupt the backtest.
Volume is Dukascopy's traded volume on their own platform: a proxy for activity, fine for VWAP and volume profile shape.
"""
import io
import lzma
import os
import struct
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd

OUT = "data/xau_5m.csv.gz"
URL = "https://datafeed.dukascopy.com/datafeed/XAUUSD/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5"
DAYS = int(os.environ.get("DUKA_DAYS", 730))
ORDERS = [("open", "close", "low", "high"), ("open", "high", "low", "close")]


def fetch(day, tries=4):
    url = URL.format(y=day.year, m=day.month - 1, d=day.day)
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (xau-kh research)"})
            raw = urllib.request.urlopen(req, timeout=30).read()
            return day, (lzma.decompress(raw) if raw else b"")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return day, b""
            time.sleep(1.5 * (k + 1))
        except Exception:
            time.sleep(1.5 * (k + 1))
    return day, None   # failed: retried on the next run


def decode(day, blob):
    n = len(blob) // 24
    if n == 0:
        return None
    a = np.frombuffer(blob[:n * 24], dtype=">u4").reshape(n, 6)
    secs = a[:, 0].astype(np.int64)
    p = a[:, 1:5].astype(np.float64)
    vol = np.frombuffer(blob[:n * 24], dtype=">f4").reshape(n, 6)[:, 5].astype(np.float64)
    # pick the column order where low <= open,close <= high holds for (nearly) every candle
    best = None
    for order in ORDERS:
        c = {k: p[:, i] for i, k in enumerate(order)}
        ok = np.mean((c["low"] <= np.minimum(c["open"], c["close"])) & (c["high"] >= np.maximum(c["open"], c["close"])))
        if best is None or ok > best[0]:
            best = (ok, c)
    ok, c = best
    if ok < 0.99:
        raise ValueError(f"{day}: price columns fail the low/high check ({ok:.1%})")
    # pick the scale that puts gold in a sane range
    med = np.median(c["close"])
    scale = next((s for s in (1000, 100, 10, 1, 100000) if 300 < med / s < 30000), None)
    if scale is None:
        raise ValueError(f"{day}: cannot find a price scale (median raw {med})")
    start = pd.Timestamp(day, tz="UTC")
    idx = start + pd.to_timedelta(secs, unit="s")
    df = pd.DataFrame({"Open": c["open"] / scale, "High": c["high"] / scale, "Low": c["low"] / scale,
                       "Close": c["close"] / scale, "Volume": vol}, index=idx)
    return df[df["Volume"] > 0]   # Dukascopy writes flat zero-volume candles when the market is closed


def to5(df):
    return df.resample("5min").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()


def main():
    today = datetime.now(timezone.utc).date()
    if "--check" in sys.argv:
        d = today - timedelta(days=1)
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        day, blob = fetch(d)
        if blob is None:
            print("download failed: Dukascopy did not answer"); sys.exit(1)
        m = decode(day, blob)
        print(f"{day}: {len(blob)} bytes, {0 if m is None else len(m)} one-minute candles")
        if m is not None:
            print(m.head(3).round(2).to_string()); print(to5(m).tail(3).round(2).to_string())
        return
    old = None
    if os.path.exists(OUT):
        old = pd.read_csv(OUT, index_col=0)
        old.index = pd.to_datetime(old.index, utc=True)
    have = set() if old is None else set(old.index.date)
    days = [today - timedelta(days=k) for k in range(1, DAYS + 1)]
    todo = [d for d in days if d.weekday() != 5 and (d not in have or d >= today - timedelta(days=2))]
    print(f"dukascopy: {len(todo)} days to download", flush=True)
    budget = time.time() + float(os.environ.get("DUKA_MINUTES", 25)) * 60
    failed = bad = 0
    cur = old
    for k in range(0, len(todo), 60):          # newest days first, saved every 60 days so progress is never lost
        if time.time() > budget:
            print("dukascopy: time budget used, the rest continues on the next run", flush=True)
            break
        parts = []
        with ThreadPoolExecutor(8) as ex:
            for day, blob in ex.map(fetch, todo[k:k + 60]):
                if blob is None:
                    failed += 1
                    continue
                try:
                    m = decode(day, blob)
                except ValueError as e:
                    bad += 1
                    print("skipped:", e)
                    continue
                if m is not None and len(m):
                    parts.append(to5(m))
        if parts:
            cur = pd.concat(([cur] if cur is not None else []) + parts).sort_index()
            cur = cur[~cur.index.duplicated(keep="last")]
            save(cur)
        print(f"  {min(k + 60, len(todo))}/{len(todo)} days done, {0 if cur is None else len(cur)} candles saved", flush=True)
    if cur is None:
        print("no data downloaded"); sys.exit(1)
    jump = (cur["Close"].pct_change().abs() > 0.05).sum()
    print(f"dukascopy: {len(cur)} five-minute candles {cur.index[0]} -> {cur.index[-1]}, last close {cur['Close'].iloc[-1]:.2f}, "
          f"{failed} days failed (retried next run), {bad} days rejected, {jump} jumps over 5%")


def save(df):
    os.makedirs("data", exist_ok=True)
    tmp = OUT + ".tmp"
    df.round(3).to_csv(tmp, compression="gzip")
    os.replace(tmp, OUT)


if __name__ == "__main__":
    main()
