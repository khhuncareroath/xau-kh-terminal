"""Free crypto history for the crypto research (BTC / ETH USDT-M perpetuals, Binance public archive).

Source: data.binance.vision (free, no key). Files:
  5m klines   futures/um/monthly/klines/{SYM}/5m           open, high, low, close, volume, taker buy volume
  funding     futures/um/monthly/fundingRate/{SYM}         every 8 h
  metrics     futures/um/daily/metrics/{SYM}               open interest (5 min), long/short ratios
Saved to data/crypto/{SYM}_5m.csv.gz, {SYM}_funding.csv.gz, {SYM}_oi.csv.gz. Run in GitHub Actions (this repo's
research sandbox cannot reach Binance). `python studies/crypto_data.py probe` checks which LIVE feeds answer from
the runner (Binance blocks US servers, and GitHub runners are in the US).
"""
import io
import json
import os
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import pandas as pd
import requests

BASE = "https://data.binance.vision/data/futures/um"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "crypto")
START = date(2020, 1, 1)
KCOLS = ["open_time", "Open", "High", "Low", "Close", "Volume", "close_time", "quote_volume", "count",
         "TakerBuy", "taker_buy_quote", "ignore"]


def _months(start, end):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _zip_csv(url, header_word):
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        return None
    z = zipfile.ZipFile(io.BytesIO(r.content))
    raw = z.read(z.namelist()[0]).decode()
    has_header = raw[:200].lower().startswith(header_word)
    return pd.read_csv(io.StringIO(raw), header=0 if has_header else None)


def klines(sym, today):
    last_full = date(today.year, today.month, 1) - timedelta(days=1)
    urls = [f"{BASE}/monthly/klines/{sym}/5m/{sym}-5m-{y}-{m:02d}.zip" for y, m in _months(START, last_full)]
    d = date(today.year, today.month, 1)
    while d < today:
        urls.append(f"{BASE}/daily/klines/{sym}/5m/{sym}-5m-{d.isoformat()}.zip")
        d += timedelta(days=1)
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(lambda u: _zip_csv(u, "open_time"), urls) if p is not None]
    df = pd.concat([p.set_axis(KCOLS, axis=1) for p in parts])
    t = pd.to_numeric(df["open_time"])
    t = t.where(t < 1e14, t // 1000)          # some newer files are in microseconds
    df.index = pd.to_datetime(t, unit="ms", utc=True)
    df = df[["Open", "High", "Low", "Close", "Volume", "TakerBuy"]].astype(float)
    return df[~df.index.duplicated()].sort_index()


def funding(sym, today):
    last_full = date(today.year, today.month, 1) - timedelta(days=1)
    urls = [f"{BASE}/monthly/fundingRate/{sym}/{sym}-fundingRate-{y}-{m:02d}.zip" for y, m in _months(START, last_full)]
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(lambda u: _zip_csv(u, "calc_time"), urls) if p is not None]
    df = pd.concat([p.iloc[:, [0, -1]].set_axis(["t", "funding"], axis=1) for p in parts])
    df.index = pd.to_datetime(pd.to_numeric(df["t"]), unit="ms", utc=True)
    return df[["funding"]].astype(float).sort_index()


def open_interest(sym, today):
    days, d = [], date(2021, 12, 1)            # the metrics archive starts in Dec 2021
    while d < today:
        days.append(d)
        d += timedelta(days=1)
    urls = [f"{BASE}/daily/metrics/{sym}/{sym}-metrics-{x.isoformat()}.zip" for x in days]
    with ThreadPoolExecutor(16) as ex:
        parts = [p for p in ex.map(lambda u: _zip_csv(u, "create_time"), urls) if p is not None]
    df = pd.concat(parts)
    df.index = pd.to_datetime(df["create_time"], utc=True)
    return df[["sum_open_interest", "sum_open_interest_value"]].astype(float).sort_index()


LIVE = {   # what the live bot could use from a GitHub runner
    "binance_futures": "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit=2",
    "binance_spot_mirror": "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=2",
    "binance_archive": "https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/5m/",
    "bybit": "https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=5&limit=2",
    "okx": "https://www.okx.com/api/v5/market/candles?instId=BTC-USDT-SWAP&bar=5m&limit=2",
    "okx_funding": "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP",
    "okx_oi": "https://www.okx.com/api/v5/public/open-interest?instId=BTC-USDT-SWAP",
    "bitget": "https://api.bitget.com/api/v2/mix/market/candles?symbol=BTCUSDT&productType=usdt-futures&granularity=5m&limit=2",
    "kraken_futures": "https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD",
    "coinbase": "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=300",
    "deribit": "https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL",
    "defillama_stables": "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1",
}


def probe():
    out = {}
    for k, u in LIVE.items():
        try:
            r = requests.get(u, timeout=20, headers={"User-Agent": "xau-kh-research"})
            out[k] = {"status": r.status_code, "sample": r.text[:160]}
        except Exception as e:   # noqa: BLE001 - we only report what answered
            out[k] = {"status": None, "error": str(e)[:160]}
        print(k, out[k].get("status"))
    try:   # Hyperliquid answers POST only
        r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "metaAndAssetCtxs"}, timeout=20)
        out["hyperliquid"] = {"status": r.status_code, "sample": r.text[:160]}
    except Exception as e:  # noqa: BLE001
        out["hyperliquid"] = {"status": None, "error": str(e)[:160]}
    print("hyperliquid", out["hyperliquid"].get("status"))
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:2] == ["probe"]:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "crypto_probe.json"), "w") as f:
            json.dump(probe(), f, indent=1)
        sys.exit(0)
    today = date.today()
    for sym in sys.argv[1:] or ["BTCUSDT", "ETHUSDT"]:
        for name, fn in (("5m", klines), ("funding", funding), ("oi", open_interest)):
            path = os.path.join(OUT, f"{sym}_{name}.csv.gz")
            if name == "oi" and os.path.exists(path) and os.path.getsize(path) > 1e6:
                print(sym, name, "kept (cached)")
                continue
            df = fn(sym, today)
            df.to_csv(path, compression="gzip")
            print(sym, name, len(df), df.index[0], df.index[-1])
