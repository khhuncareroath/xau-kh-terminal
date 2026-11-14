"""₿ Crypto · គ្រីបតូ: BTC perpetual (Bitget) map and data for the XAU.KH group. Quality only, no spam.

Posts (all in the "Crypto · គ្រីបតូ" topic, details on the picture, short Khmer-friendly caption):
  daily map     once a day after the UTC daily close (~07:15 Cambodia): 4H chart with the levels that matter
                (yesterday / last week high-low, the 30-candle 4H breakout lines, 7-day volume POC, 4H structure) and
                two if/then lines. A MAP, not a forecast: on gold the analysis direction tested 50/50.
  weekly data   Sunday ~09:00 Cambodia: price vs open interest (7-day change quadrant), funding, taker buy/sell,
                stablecoin supply, one plain verdict. Context only, never a trade by itself.
  proof         Friday ~20:00 Cambodia in 🏆 Proof: what was tested on crypto, what passed, what failed.
Signals: NONE until a crypto rule passes research.judge on BTC AND on ETH (studies/CRYPTO_RESULTS.md). The gold rules
were tested on 7 years of BTC/ETH (Nov 2026) and did not pass, so nothing is sent as a trade.
Paper: the one lead (🧪 SWING: 4H close beyond the last 30 4H candles, clean 4H trend ER > 0.35, SL 2 x 4H ATR,
TP 4R, max 5 days; studies/crypto_robust.py: positive on BTC and ETH in most settings, but BTC t 1.9 and weak on the
newest data = NOT proven) is tracked silently: the owner gets a private note, members see it only in the Friday record.

Data (free, answers from GitHub runners, checked 14 Nov 2026 by studies/crypto_data.py probe): Bitget USDT-M candles,
OKX funding / open interest / taker volume, DefiLlama stablecoins. Binance futures and Bybit block US servers.
Env: CRYPTO=off stops everything, CRYPTO_DRY=1 renders the pictures without sending (crypto_preview/).
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "crypto_state.json")
DRY = os.environ.get("CRYPTO_DRY") == "1"
OUTDIR = os.path.join(HERE, "crypto_preview") if DRY else "/tmp"
UA = {"User-Agent": "XAU.KH-crypto"}
BG, CARD, INK, MUT, GRID = "#F2F2F7", "#FFFFFF", "#1C1C1E", "#8E8E93", "#E5E5EA"
UP, DN, BLUE, PURP, ORANGE, BTC = "#34C759", "#FF3B30", "#007AFF", "#AF52DE", "#FF9500", "#F7931A"


# ------------------------------------------------------------------------------------------------ data
def _get(url, **kw):
    r = requests.get(url, timeout=20, headers=UA, **kw)
    r.raise_for_status()
    return r.json()


def candles(gran="4H", limit=200):
    """BTCUSDT perpetual candles, oldest first, UTC index. Bitget first, OKX if Bitget fails."""
    try:
        g = {"1D": "1Dutc", "1W": "1Wutc"}.get(gran, gran)          # daily candles on the UTC day, like the tests
        d = _get("https://api.bitget.com/api/v2/mix/market/candles",
                 params={"symbol": "BTCUSDT", "productType": "usdt-futures", "granularity": g, "limit": limit})["data"]
        df = pd.DataFrame([r[:6] for r in d], columns=["t", "Open", "High", "Low", "Close", "Volume"])
        src = "Bitget"
    except Exception as e:  # noqa: BLE001
        print("bitget failed, using OKX:", e)
        bar = {"1D": "1Dutc", "1W": "1Wutc"}.get(gran, gran)
        d = _get("https://www.okx.com/api/v5/market/candles", params={"instId": "BTC-USDT-SWAP", "bar": bar, "limit": min(limit, 300)})["data"]
        df = pd.DataFrame([r[:6] for r in d], columns=["t", "Open", "High", "Low", "Close", "Volume"])
        src = "OKX"
    df.index = pd.to_datetime(pd.to_numeric(df.pop("t")), unit="ms", utc=True)
    df = df.astype(float).sort_index()
    df.attrs["src"] = src
    return df


def okx(path, **params):
    try:
        return _get("https://www.okx.com" + path, params=params).get("data") or []
    except Exception as e:  # noqa: BLE001
        print("okx failed", path, e)
        return []


def funding_hist():
    d = okx("/api/v5/public/funding-rate-history", instId="BTC-USDT-SWAP", limit=100)
    if not d:
        return None
    s = pd.Series([float(x["realizedRate"] or x["fundingRate"]) for x in d],
                  index=pd.to_datetime([int(x["fundingTime"]) for x in d], unit="ms", utc=True))
    return s.sort_index()


def oi_daily():
    """[time, open interest USD, volume USD] daily, ~6 months."""
    d = okx("/api/v5/rubik/stat/contracts/open-interest-volume", ccy="BTC", period="1D")
    if not d:
        return None
    df = pd.DataFrame([[int(r[0]), float(r[1]), float(r[2])] for r in d], columns=["t", "oi", "vol"])
    df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
    return df.sort_index()


def taker_daily():
    d = okx("/api/v5/rubik/stat/taker-volume", ccy="BTC", instType="CONTRACTS", period="1D")
    if not d:
        return None
    df = pd.DataFrame([[int(r[0]), float(r[1]), float(r[2])] for r in d], columns=["t", "sell", "buy"])
    df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
    return df.sort_index()


def stables():
    try:
        d = _get("https://stablecoins.llama.fi/stablecoincharts/all")
        s = pd.Series([float(x["totalCirculatingUSD"].get("peggedUSD", 0)) for x in d],
                      index=pd.to_datetime([int(x["date"]) for x in d], unit="s", utc=True))
        return s.sort_index()
    except Exception as e:  # noqa: BLE001
        print("defillama failed:", e)
        return None


# ------------------------------------------------------------------------------------------------ levels
def _poc(h1, days=7):
    x = h1[h1.index >= h1.index[-1] - pd.Timedelta(days=days)]
    tp = (x["High"] + x["Low"] + x["Close"]) / 3
    hist, edges = np.histogram(tp, bins=60, weights=x["Volume"])
    k = int(hist.argmax())
    return float((edges[k] + edges[k + 1]) / 2)


def levels(d4, d1, h1):
    from engine import atr
    from ict import structure, swings
    done = d1.iloc[:-1]                       # last CLOSED daily candle = yesterday (UTC)
    wk = d1[d1.index >= d1.index[-1] - pd.Timedelta(days=7)].iloc[:-1]
    c4 = d4.iloc[:-1]                         # closed 4H candles
    ev = structure(c4, atr(c4).to_numpy(), swings(c4))
    trend = ev[-1]["dir"] if ev else None
    rng = (done["High"] - done["Low"]).tail(20)
    adr = float(rng.median())
    today = d1.iloc[-1]
    return {
        "price": float(d4["Close"].iloc[-1]),
        "pdh": float(done["High"].iloc[-1]), "pdl": float(done["Low"].iloc[-1]),
        "pwh": float(wk["High"].max()), "pwl": float(wk["Low"].min()),
        "brk_up": float(c4["High"].tail(30).max()), "brk_dn": float(c4["Low"].tail(30).min()),
        "poc": _poc(h1), "trend": trend, "adr": adr,
        "used": float((today["High"] - today["Low"]) / adr) if adr > 0 else None,
    }


NAMES = [("brk_up", "4H breakout ↑", PURP, "-"), ("brk_dn", "4H breakout ↓", PURP, "-"),
         ("pwh", "Week high", BLUE, "--"), ("pwl", "Week low", BLUE, "--"),
         ("pdh", "Day high", ORANGE, ":"), ("pdl", "Day low", ORANGE, ":"),
         ("poc", "POC 7d", MUT, "-.")]


def merged(lv):
    """Levels sorted by price; levels within 0.1% of each other become one ("Week + Day low"). Day = yesterday (UTC)."""
    out = []
    for k, name, col, ls in sorted(NAMES, key=lambda z: lv[z[0]]):
        v = lv[k]
        if out and abs(v - out[-1][0]) <= v * 0.001:
            a, b = out[-1][1].split(" "), name.split(" ")
            nm = f"{a[0]} + {b[0]} {a[-1]}" if len(a) == 2 and len(b) == 2 and a[-1] == b[-1] else f"{out[-1][1]} + {name}"
            out[-1] = (out[-1][0], nm, out[-1][2], out[-1][3])
        else:
            out.append((v, name, col, ls))
    return out


def if_then(lv):
    """Two plain lines: the nearest level above and below, and the one after it."""
    p = lv["price"]
    m = merged(lv)
    above = [(v, n) for v, n, _, _ in m if v > p * 1.001]
    below = [(v, n) for v, n, _, _ in m if v < p * 0.999][::-1]
    up = (above[0], above[1] if len(above) > 1 else None) if above else None
    dn = (below[0], below[1] if len(below) > 1 else None) if below else None
    return up, dn


def fmt(x):
    return f"{x:,.0f}"


# ------------------------------------------------------------------------------------------------ pictures
def _fonts():
    sys.path.insert(0, HERE)
    from signal_card import _fonts as f
    return f()


def _pill(fig, x, y, text, fg, bg, fs=10):
    fig.text(x, y, f" {text} ", color=fg, fontsize=fs, fontweight="bold", va="center",
             bbox=dict(boxstyle="round,pad=0.35", fc=bg, ec="none"))


def _candles(ax, df):
    w = (df.index[1] - df.index[0]) * 0.65
    for t, r in df.iterrows():
        col = UP if r["Close"] >= r["Open"] else DN
        ax.vlines(t, r["Low"], r["High"], color=col, lw=0.8, zorder=2)
        ax.bar(t, max(abs(r["Close"] - r["Open"]), r["Close"] * 1e-5), bottom=min(r["Open"], r["Close"]), width=w,
               color=col, zorder=3)


def map_card(d4, lv, path, now):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = _fonts()
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor=BG)
    fig.text(0.06, 0.955, "BTC/USDT · PERP", fontsize=18, fontweight="bold", color=INK)
    _pill(fig, 0.06, 0.918, "DAILY MAP · ផែនទីប្រចាំថ្ងៃ", "white", BTC)
    _pill(fig, 0.52, 0.918, "map, not forecast", INK, GRID)
    fig.text(0.94, 0.955, now.strftime("%d %b %Y"), fontsize=10, color=MUT, ha="right")
    ax = fig.add_axes([0.06, 0.36, 0.76, 0.53])
    ax.set_facecolor(CARD)
    x = d4.tail(120)
    _candles(ax, x)
    lines = merged(lv)
    lo, hi = x["Low"].min(), x["High"].max()
    for v, name, col, ls in lines:
        ax.axhline(v, color=col, ls=ls, lw=1.1, zorder=1)
        lo, hi = min(lo, v), max(hi, v)
    pad = (hi - lo) * 0.06
    ax.set_ylim(lo - pad, hi + pad)
    ys, gap = [], (hi - lo + 2 * pad) * 0.035     # right-side tags, nudged apart so they do not overlap
    for v, *_ in lines:
        ys.append(v if not ys or v - ys[-1] >= gap else ys[-1] + gap)
    for (v, name, col, _), y in zip(lines, ys):
        y0, y1 = ax.get_ylim()
        fy = 0.36 + 0.53 * (y - y0) / (y1 - y0)
        fig.text(0.83, fy, f"{name}  {fmt(v)}", fontsize=7.6 if len(name) < 20 else 6.4, color="white", va="center",
                 fontweight="bold", bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"))
    ax.axhline(lv["price"], color=INK, lw=0.6, alpha=0.5)
    ax.grid(color=GRID, lw=0.6)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(labelsize=7.5, colors=MUT)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    # bottom box
    up, dn = if_then(lv)
    box = fig.add_axes([0.06, 0.05, 0.88, 0.27])
    box.set_facecolor("#1C1C1E")
    box.set_xticks([]); box.set_yticks([])
    for s in box.spines.values():
        s.set_visible(False)
    tr = {"bull": ("4H structure: UP", UP), "bear": ("4H structure: DOWN", DN)}.get(lv["trend"], ("4H structure: —", MUT))
    used = f"{lv['used'] * 100:.0f}%" if lv["used"] is not None else "—"
    rows = [(f"Price {fmt(lv['price'])}", "white"), (tr[0], tr[1]),
            (f"Normal day ±{fmt(lv['adr'])} · today used {used}", "white")]
    if up:
        rows.append((f"▲ Above {fmt(up[0][0])} ({up[0][1]}) → next {fmt(up[1][0]) if up[1] else 'no level above'}", UP))
    if dn:
        rows.append((f"▼ Below {fmt(dn[0][0])} ({dn[0][1]}) → next {fmt(dn[1][0]) if dn[1] else 'no level below'}", DN))
    rows.append(("Levels show WHERE price may react, not which way. No crypto signal is live yet.", MUT))
    for i, (t, c) in enumerate(rows):
        box.text(0.04, 0.88 - i * 0.155, t, color=c, fontsize=10 if i < 5 else 8, fontweight="bold" if i < 5 else None,
                 transform=box.transAxes, va="center")
    fig.text(0.94, 0.02, f"XAU.KH · data {d4.attrs.get('src', 'Bitget')} · futures = high risk", fontsize=7, color=MUT, ha="right")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return up, dn


QUAD = {   # 7-day change of price and open interest (the same 4 boxes as the Checkonchain chart members know)
    (1, 1): ("Leveraged rally", "price ↑ with new leverage: fragile if funding is hot", ORANGE),
    (1, -1): ("Spot rally", "price ↑ while leverage leaves: healthier move", UP),
    (-1, 1): ("Leveraged sell-off", "price ↓ with new shorts: squeeze risk both ways", DN),
    (-1, -1): ("Deleveraging sell-off", "price ↓ and leverage flushed: pressure is clearing", BLUE),
}


def verdict(px, oi, fu):
    if oi is None or len(oi) < 8 or len(px) < 8:
        return None
    dp = float(px.iloc[-1] / px.iloc[-8] - 1)
    do = float(oi["oi"].iloc[-1] / oi["oi"].iloc[-8] - 1)
    q = QUAD[(1 if dp >= 0 else -1, 1 if do >= 0 else -1)]
    hot = None
    if fu is not None and len(fu):   # base rate is 0.01% / 8 h: well above = longs pay a lot, below zero = shorts pay
        f = float(fu.iloc[-1])
        hot = "hot: longs crowded" if f >= 0.0002 else "negative: shorts crowded" if f <= -0.0001 else "normal"
    return {"dp": dp, "do": do, "name": q[0], "text": q[1], "color": q[2], "funding": hot,
            "funding_now": float(fu.iloc[-1]) if fu is not None and len(fu) else None}


def data_card(d1, oi, fu, tk, st, path, now):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = _fonts()
    px = d1["Close"]
    v = verdict(px, oi, fu)
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor=BG)
    fig.text(0.06, 0.955, "BTC · WEEKLY DATA", fontsize=18, fontweight="bold", color=INK)
    _pill(fig, 0.06, 0.918, "ទិន្នន័យប្រចាំសប្តាហ៍", "white", BTC)
    _pill(fig, 0.45, 0.918, "context, not a signal", INK, GRID)
    fig.text(0.94, 0.955, now.strftime("%d %b %Y"), fontsize=10, color=MUT, ha="right")

    def panel(rect, title):
        ax = fig.add_axes(rect)
        ax.set_facecolor(CARD)
        ax.set_title(title, fontsize=9, color=INK, loc="left", fontweight="bold")
        ax.grid(color=GRID, lw=0.5)
        ax.tick_params(labelsize=6.5, colors=MUT)
        for s in ax.spines.values():
            s.set_visible(False)
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        return ax

    a = panel([0.07, 0.64, 0.86, 0.23], "Price (black) and OKX open interest (orange), 90 days")
    p90 = px.tail(90)
    a.plot(p90.index, p90.values, color=INK, lw=1.2)
    a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    if oi is not None:
        b = a.twinx()
        o90 = oi["oi"][oi.index >= p90.index[0]] / 1e9
        b.plot(o90.index, o90.values, color=ORANGE, lw=1.1)
        b.tick_params(labelsize=6.5, colors=ORANGE)
        b.set_ylabel("OI $bn", fontsize=7, color=ORANGE)
    a2 = panel([0.07, 0.40, 0.40, 0.18], "Funding every 8 h (%)")
    if fu is not None:
        f = fu * 100
        a2.bar(f.index, f.values, width=0.25, color=[UP if x >= 0 else DN for x in f.values])
        a2.axhline(0, color=MUT, lw=0.6)
    a3 = panel([0.55, 0.40, 0.38, 0.18], "Taker buy ÷ sell, daily")
    if tk is not None:
        r = (tk["buy"] / tk["sell"]).tail(30)
        a3.bar(r.index, r.values - 1, bottom=1, width=0.7, color=[UP if x >= 1 else DN for x in r.values])
        a3.axhline(1, color=MUT, lw=0.6)
    a4 = panel([0.07, 0.30, 0.86, 0.06], "")
    a4.axis("off")
    if st is not None and len(st) > 32:
        st = st.iloc[:-1]                      # the last point is today, still filling in
        ch = st.iloc[-1] / st.iloc[-31] - 1
        a4.text(0, 0.5, f"Stablecoin supply ${st.iloc[-1] / 1e9:,.0f}bn · 30 days {ch * 100:+.1f}%  "
                         f"({'new money coming in' if ch > 0 else 'money leaving'})", fontsize=9.5, color=INK, va="center")
    box = fig.add_axes([0.06, 0.05, 0.88, 0.22])
    box.set_facecolor("#1C1C1E"); box.set_xticks([]); box.set_yticks([])
    for s in box.spines.values():
        s.set_visible(False)
    rows = []
    if v:
        rows = [(f"{v['name']}", v["color"], 14),
                (f"7 days: price {v['dp'] * 100:+.1f}% · open interest {v['do'] * 100:+.1f}%", "white", 10),
                (v["text"], "white", 10)]
        if v["funding_now"] is not None:
            rows.append((f"Funding now {v['funding_now'] * 100:+.4f}% / 8 h · {v['funding']}", "white", 10))
    rows.append(("Tested: funding extremes made money on BTC but NOT on ETH -> context only.", MUT, 8))
    for i, (t, c, fs) in enumerate(rows):
        box.text(0.04, 0.84 - i * 0.18, t, color=c, fontsize=fs, fontweight="bold" if fs >= 10 else None,
                 transform=box.transAxes, va="center")
    fig.text(0.94, 0.02, "XAU.KH · data OKX, DefiLlama · futures = high risk", fontsize=7, color=MUT, ha="right")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return v


# ------------------------------------------------------------------------------------------------ posts
def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(s):
    json.dump(s, open(STATE, "w"), indent=1)


def send_photo(path, caption, title):
    if DRY:
        print(f"[dry] {title}: {path}\n{caption}\n")
        return 1
    from tg import send_photo as sp
    return sp(path, caption, title=title)


def post_map(now):
    d4, d1, h1 = candles("4H", 200), candles("1D", 60), candles("1H", 200)
    lv = levels(d4, d1, h1)
    path = os.path.join(OUTDIR, "crypto_map.png")
    up, dn = map_card(d4, lv, path, now)
    lines = ["₿ <b>BTC · Daily map</b> · ផែនទី BTC ថ្ងៃនេះ"]
    if up:
        lines.append(f"▲ លើស {fmt(up[0][0])} → {fmt(up[1][0]) if up[1] else 'no level above'}")
    if dn:
        lines.append(f"▼ ក្រោម {fmt(dn[0][0])} → {fmt(dn[1][0]) if dn[1] else 'no level below'}")
    lines.append("ផែនទី មិនមែនការទស្សន៍ទាយ · Futures = ហានិភ័យខ្ពស់")
    return send_photo(path, "\n".join(lines), "Crypto map")


def post_data(now):
    d1 = candles("1D", 120)
    oi, fu, tk, st = oi_daily(), funding_hist(), taker_daily(), stables()
    path = os.path.join(OUTDIR, "crypto_data.png")
    v = data_card(d1, oi, fu, tk, st, path, now)
    cap = ["₿ <b>BTC · Weekly data</b> · ទិន្នន័យប្រចាំសប្តាហ៍"]
    if v:
        cap.append(f"{v['name']} · price {v['dp'] * 100:+.1f}% · OI {v['do'] * 100:+.1f}% (7d)")
    cap.append("បរិបទទីផ្សារ មិនមែនសញ្ញា (context, not a signal)")
    return send_photo(path, "\n".join(cap), "Crypto data")


# ------------------------------------------------------------------------------------------------ 🧪 paper swing
SW_ER, SW_STOP, SW_TGT, SW_DAYS, SW_COST = 0.35, 2.0, 4.0, 5, 0.0012


def swing_check(st, now):
    """Opens / closes the silent paper trade. Returns a short owner note when something happened."""
    from engine import atr
    pp = st.setdefault("paper", {"open": None, "closed": [], "last_bar": None})
    d4 = candles("4H", 200)
    closed = d4[d4.index + pd.Timedelta(hours=4) <= now]
    notes = []
    tr = pp["open"]
    if tr:   # manage with 1H candles since the entry (stop first when one candle touches both)
        h1 = candles("1H", 200)
        h1 = h1[h1.index >= pd.Timestamp(tr["t"]) - pd.Timedelta(hours=1)]
        sg, en, sl, tp = tr["sg"], tr["entry"], tr["stop"], tr["tgt"]
        risk = abs(en - sl)
        out = None
        for t, r in h1.iterrows():
            if t + pd.Timedelta(hours=1) <= pd.Timestamp(tr["t"]):
                continue
            if (r["Low"] <= sl) if sg > 0 else (r["High"] >= sl):
                out = (sl, "SL"); break
            if (r["High"] >= tp) if sg > 0 else (r["Low"] <= tp):
                out = (tp, "TP"); break
        if out is None and now >= pd.Timestamp(tr["t"]) + pd.Timedelta(days=SW_DAYS):
            out = (float(h1["Close"].iloc[-1]), "time")
        if out:
            R = (out[0] - en) * sg / risk - SW_COST * en / risk
            pp["closed"].append(dict(tr, exit=round(out[0], 1), how=out[1], r=round(R, 2), t_close=now.isoformat()))
            pp["open"] = None
            notes.append(f"🧪 paper swing closed ({out[1]}): {R:+.2f}R")
    if pp["open"] is None and len(closed) > 40:
        k = len(closed) - 1
        bar = str(closed.index[k])
        hi30 = closed["High"].iloc[k - 30:k].max(); lo30 = closed["Low"].iloc[k - 30:k].min()
        c = closed["Close"].to_numpy()
        sg = 1 if c[k] > hi30 else -1 if c[k] < lo30 else 0
        w = c[k - 30:k + 1]; path = np.abs(np.diff(w)).sum()
        er = abs(w[-1] - w[0]) / path if path > 0 else 0
        late = now - (closed.index[k] + pd.Timedelta(hours=4)) > pd.Timedelta(hours=2)
        if sg and er > SW_ER and bar != pp.get("last_bar") and not late:
            a4 = float(atr(closed).iloc[-1])
            en = float(d4["Close"].iloc[-1])
            pp["open"] = {"t": now.isoformat(), "sg": sg, "entry": round(en, 1), "stop": round(en - sg * SW_STOP * a4, 1),
                          "tgt": round(en + sg * SW_TGT * SW_STOP * a4, 1), "bar": bar}
            pp["last_bar"] = bar
            o = pp["open"]
            notes.append(f"🧪 paper swing {'BUY' if sg > 0 else 'SELL'} BTC {fmt(en)} · SL {fmt(o['stop'])} · TP {fmt(o['tgt'])} "
                         f"(not sent to members)")
    return notes


def paper_line(st):
    cl = (st.get("paper") or {}).get("closed") or []
    op = (st.get("paper") or {}).get("open")
    if not cl and not op:
        return "🧪 Paper swing (testing, not a signal): no trade yet."
    rs = [x["r"] for x in cl]
    w = sum(r > 0 for r in rs)
    line = f"🧪 Paper swing (testing, not a signal): {len(rs)} closed, {w} won, {sum(rs):+.1f}R"
    if op:
        line += f" · 1 open ({'BUY' if op['sg'] > 0 else 'SELL'} {fmt(op['entry'])})"
    return line + " · 7-year test: +0.25R a trade, NOT proven yet."


PROOF_TEXT = ("₿ <b>Crypto · test record</b> · លទ្ធផលតេស្ត\n"
              "No crypto signal yet. Gold rules tested on 7 years of BTC + ETH: none passed "
              "(4H breakout ~0R, scalp and volume turn lost after fees).\n"
              "មិនទាន់មានសញ្ញា Crypto ទេ: យើងផ្ញើតែសញ្ញាដែលបានតេស្តរួច។\n"
              "Full table: studies/CRYPTO_RESULTS.md")


INTRO = ("₿ <b>Crypto · គ្រីបតូ</b>: BTC only, quality only\n"
         "• Every day: 1 BTC map (levels, not a forecast) · Sunday: 1 data card (open interest, funding, flows)\n"
         "• Signals: only after a rule passes our tests. Gold rules were tested on 7 years of BTC + ETH and did NOT pass, "
         "so there is no crypto signal yet.\n\n"
         "⚠️ <b>Futures = ហានិភ័យខ្ពស់ (high risk)</b>\n"
         "• Leverage 20x: តម្លៃទៅផ្ទុយតែ 5% = Liquidation (បាត់លុយទាំងអស់ក្នុង position)\n"
         "• Funding: បង់រៀងរាល់ 8 ម៉ោង ពេលកាន់ position\n"
         "• ទីផ្សារបើក 24/7 រួមទាំងចុងសប្តាហ៍ (weekend wicks)\n"
         "• Exchange អាចបង្កកការដកប្រាក់ ឬ ត្រូវ hack បាន\n"
         "• Cambodia: since Sep 2026 NBC + SERC require a licence for crypto services; check the rules yourself\n"
         "• No referral or affiliate links here, ever.")


def owner_note(text):
    chat = os.environ.get("TELEGRAM_OWNER_CHAT_ID")
    if DRY or not chat:
        print("[owner]", text)
        return
    from tg import _api
    try:
        _api("sendMessage", {"chat_id": chat, "text": text})
    except Exception as e:  # noqa: BLE001
        print("owner note failed:", e)


def main():
    if os.environ.get("CRYPTO", "on").lower() == "off":
        print("crypto off")
        return
    now = datetime.now(timezone.utc)
    st = load_state()
    os.makedirs(OUTDIR, exist_ok=True)
    today = now.strftime("%Y-%m-%d")
    if not st.get("intro"):
        if DRY:
            print("[dry] intro:\n" + INTRO)
        else:
            from tg import send
            if send(INTRO, title="Crypto intro"):
                st["intro"] = today
    week = now.strftime("%G-W%V")
    if DRY or (now.hour == 0 and now.minute >= 10 or now.hour >= 1) and st.get("map") != today:
        if post_map(now):
            st["map"] = today
    if DRY or (now.weekday() == 6 and now.hour >= 2 and st.get("data") != week):
        if post_data(now):
            st["data"] = week
    try:
        for n in swing_check(st, now):
            owner_note(n)
    except Exception as e:  # noqa: BLE001
        print("paper swing check failed:", e)
    if not DRY and now.weekday() == 4 and now.hour >= 13 and st.get("proof") != week:
        from tg import send
        if send(PROOF_TEXT + "\n" + paper_line(st), title="Crypto proof"):
            st["proof"] = week
    if not DRY:
        save_state(st)


if __name__ == "__main__":
    main()
