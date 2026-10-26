"""Levels: calculates session highs/lows, prior day levels, midnight open, volume profile,
and VWAP bands -> levels.json. Run: python levels.py
"""
import json
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from zoneinfo import ZoneInfo
from engine import load

NY = ZoneInfo("America/New_York")

def to_ny(df):
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert(NY)
    else:
        df.index = df.index.tz_convert(NY)
    return df

def trade_dates(index):
    return (index - pd.Timedelta(hours=18)).date.astype(str)

def profile(df, bins=40):
    if len(df) == 0:
        return None
    p = (df["High"] + df["Low"] + df["Close"]) / 3
    v = df["Volume"].clip(lower=0).fillna(0)
    hist, edges = np.histogram(p, bins=bins, weights=v)
    poc_idx = np.argmax(hist)
    poc = (edges[poc_idx] + edges[poc_idx+1]) / 2
    tot = hist.sum()
    if tot == 0:
        return {"poc": poc, "vah": p.max(), "val": p.min(), "lvn": []}
    cumsum = hist.cumsum()
    target = 0.7 * cumsum[-1]
    vl, vh = poc_idx, poc_idx
    acc = hist[poc_idx]
    while acc < target and (vl > 0 or vh < len(hist) - 1):
        dn_vol = hist[vl - 1] if vl > 0 else 0
        up_vol = hist[vh + 1] if vh < len(hist) - 1 else 0
        if dn_vol >= up_vol and vl > 0:
            vl -= 1
            acc += hist[vl]
        elif vh < len(hist) - 1:
            vh += 1
            acc += hist[vh]
        else:
            break
    val = edges[vl]
    vah = edges[vh + 1]
    lvn = []
    mean_vol = hist.mean()
    for i in range(1, len(hist) - 1):
        if hist[i] < mean_vol * 0.3 and hist[i] < hist[i-1] and hist[i] < hist[i+1]:
            lvn.append(round((edges[i] + edges[i+1]) / 2, 2))
    return {"poc": round(float(poc), 2), "vah": round(float(vah), 2), "val": round(float(val), 2), "lvn": lvn}

def main():
    df = to_ny(load("5m", "30d"))
    dates = trade_dates(df.index)
    days = sorted(set(dates))
    today_str = days[-1]
    prev_str = days[-2] if len(days) > 1 else today_str
    
    prev_df = df[dates == prev_str]
    today_df = df[dates == today_str]
    price = float(df["Close"].iloc[-1])
    
    prev_high = float(prev_df["High"].max()) if len(prev_df) else price
    prev_low = float(prev_df["Low"].min()) if len(prev_df) else price
    prev_close = float(prev_df["Close"].iloc[-1]) if len(prev_df) else price
    
    midnight_mask = (today_df.index.hour == 0) & (today_df.index.minute == 0)
    midnight_open = float(today_df[midnight_mask]["Open"].iloc[0]) if len(today_df[midnight_mask]) else float(today_df["Open"].iloc[0])
    
    sessions = {}
    for name, start_h, end_h in [("Asia", 18, 2), ("London", 2, 5), ("New York", 7, 10)]:
        sub = today_df[(today_df.index.hour >= start_h) & (today_df.index.hour < end_h)] if start_h < end_h else today_df[(today_df.index.hour >= start_h) | (today_df.index.hour < end_h)]
        if len(sub):
            sessions[name] = {"high": round(float(sub["High"].max()), 2), "low": round(float(sub["Low"].min()), 2), "status": "complete" if datetime.now(NY).hour > end_h else "active"}
        else:
            sessions[name] = {"high": price, "low": price, "status": "active"}

    prof_prev = profile(prev_df)
    
    ladder = [
        {"name": "Prev day high", "price": round(prev_high, 2)},
        {"name": "Prev day low", "price": round(prev_low, 2)},
        {"name": "Prev day close", "price": round(prev_close, 2)},
        {"name": "Midnight open", "price": round(midnight_open, 2)},
    ]
    if prof_prev:
        ladder.extend([
            {"name": "Prev POC", "price": prof_prev["poc"]},
            {"name": "Prev VAH", "price": prof_prev["vah"]},
            {"name": "Prev VAL", "price": prof_prev["val"]},
        ])
    for s_name, s_data in sessions.items():
        ladder.extend([
            {"name": f"{s_name} high", "price": s_data["high"]},
            {"name": f"{s_name} low", "price": s_data["low"]},
        ])
        
    tp = (today_df["High"] + today_df["Low"] + today_df["Close"]) / 3
    v = today_df["Volume"].clip(lower=0).fillna(0)
    cv = v.cumsum()
    cpv = (v * tp).cumsum()
    cpv2 = (v * tp * tp).cumsum()
    vwap = (cpv / cv).iloc[-1] if cv.iloc[-1] > 0 else price
    var = (cpv2 / cv - vwap**2).iloc[-1] if cv.iloc[-1] > 0 else 0.01
    sd = np.sqrt(max(0.01, var))
    
    ladder.extend([
        {"name": "VWAP", "price": round(float(vwap), 2)},
        {"name": "VWAP +1s", "price": round(float(vwap + sd), 2)},
        {"name": "VWAP -1s", "price": round(float(vwap - sd), 2)},
        {"name": "VWAP +2s", "price": round(float(vwap + 2*sd), 2)},
        {"name": "VWAP -2s", "price": round(float(vwap - 2*sd), 2)},
    ])

    out = {
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "price": round(price, 2),
        "ladder": ladder,
        "sessions": sessions,
        "prev_day": {"high": round(prev_high, 2), "low": round(prev_low, 2)},
        "profile_prev_day": prof_prev
    }
    with open("levels.json", "w") as f:
        json.dump(out, f, indent=2)
    print("levels.json generated successfully.")

if __name__ == "__main__":
    main()