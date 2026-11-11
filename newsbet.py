"""🎲 NEWS BET (owner, 11 Nov 2026): before each high-impact US release the bot reads the fundamentals and leans BUY
or SELL gold, then grades the bet itself and keeps a running record. Posted in 📰 News, never in 📈 Signals.

Fundamental read (each factor votes +1 gold up / -1 gold down / 0):
  1. Dollar (DXY, 24h): up >= 0.15% -> gold down · down -> gold up
  2. US 10-year yield (24h): up >= 3bp -> gold down · down -> gold up
  3. What economists expect: forecast vs previous. Cooler inflation / jobs expected -> softer Fed -> gold up (and the
     mirror), using the usual effect of each event (outlook.EVENT_DIR)
  4. Gold's 4H structure: the trend often carries through the release
Lean = sign of the sum; 0 = "no bet: fundamentals mixed". Confidence: |sum| 1 = low, 2 = medium, 3-4 = high.
Trade: entry = first price at the release, SL $15, TP $30 (2R), closed after 60 min. Result replied under the bet.

HONEST LABEL: studies/RESULTS.md: "lean before the news" did not pass the 2-year test, and at the release the spread
widens and stops slip. This is a labelled gamble on fundamentals: tiny size or just watch. The record decides.
NEWS_BET=off turns it off.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd

STATE = "newsbet_state.json"
SL, TP, HOLD_MIN = 15.0, 30.0, 60
ON = os.environ.get("NEWS_BET", "on") != "off"


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def _num(x):
    try:
        return float(str(x).replace("%", "").replace("K", "").replace("M", "").replace(",", "").strip())
    except Exception:
        return None


def read(group, macro, df):
    """Factors for one release group [(t, event, sign_if_higher)]: [(vote, English, Khmer)] and the lean."""
    out = []
    dxy = (macro.get("dxy") or {}).get("chg_pct")
    if dxy is not None:
        v = -1 if dxy >= 0.15 else 1 if dxy <= -0.15 else 0
        out.append((v, f"Dollar {dxy:+.2f}% today" + (" → gold ↓" if v < 0 else " → gold ↑" if v > 0 else " (flat)"),
                    "ដុល្លារ" + ("ឡើង → មាសចុះ" if v < 0 else "ចុះ → មាសឡើង" if v > 0 else "ថេរ")))
    y = (macro.get("us10y") or {}).get("chg_bp")
    if y is not None:
        v = -1 if y >= 3 else 1 if y <= -3 else 0
        out.append((v, f"US 10y yield {y:+.0f}bp" + (" → gold ↓" if v < 0 else " → gold ↑" if v > 0 else " (flat)"),
                    "ទិន្នផលសញ្ញាប័ណ្ណ" + ("ឡើង → មាសចុះ" if v < 0 else "ចុះ → មាសឡើង" if v > 0 else "ថេរ")))
    votes = []
    for _, e, sg in group:
        f, p = _num(e.get("forecast")), _num(e.get("previous"))
        if sg and f is not None and p is not None and f != p:
            votes.append(sg * (1 if f > p else -1))
    if votes:
        v = 1 if sum(votes) > 0 else -1 if sum(votes) < 0 else 0
        out.append((v, "Forecast vs previous: economists expect "
                    + ("data that helps gold ↑" if v > 0 else "data that hurts gold ↓" if v < 0 else "mixed data"),
                    "ការរំពឹងទុក " + ("ល្អសម្រាប់មាស" if v > 0 else "អាក្រក់សម្រាប់មាស" if v < 0 else "ចម្រុះ")))
    try:
        import ict
        import liqmap
        b = liqmap._bias(ict.resample(df, "4H"))
        v = 1 if b == "bull" else -1 if b == "bear" else 0
        out.append((v, f"Gold 4H structure {'up' if v > 0 else 'down' if v < 0 else 'ranging'}",
                    "និន្នាការ 4H " + ("ឡើង" if v > 0 else "ចុះ" if v < 0 else "ចំហៀង")))
    except Exception as e:
        print("newsbet 4H bias failed:", e)
    s = sum(v for v, *_ in out)
    lean = "BUY" if s > 0 else "SELL" if s < 0 else None
    conf = None if not lean else "low" if abs(s) == 1 else "medium" if abs(s) == 2 else "high"
    return out, lean, conf, s


def record(st):
    done = [b for b in st.get("bets", []) if b.get("R") is not None]
    w = sum(1 for b in done if b["R"] > 0)
    return w, len(done) - w, round(sum(b["R"] for b in done), 1)


def check(df, news, macro):
    """Every cycle: post a bet 20-35 min before a high-impact release; grade bets whose hour is over."""
    if not ON:
        return
    from outlook import EVENT_DIR
    from tg import esc, fmt, local, send
    st = jl(STATE, {})
    now = datetime.now(timezone.utc)
    # 1) new bet
    groups = {}
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        t = datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        if timedelta(minutes=20) <= t - now <= timedelta(minutes=35):
            sg = next((v for keys, v in EVENT_DIR if any(k in e["title"].lower() for k in keys)), None)
            groups.setdefault(t, []).append((t, e, sg))
    for t, group in sorted(groups.items()):
        key = t.isoformat()
        if any(b["key"] == key for b in st.get("bets", [])):
            continue
        fac, lean, conf, s = read(group, macro, df)
        w, l_, tot = record(st)
        titles = ", ".join(dict.fromkeys(e["title"] for _, e, _ in group))
        rec = f"📊 Record so far: {w}W {l_}L · {tot:+.1f}R" if w + l_ else "📊 First news bet: the record starts now"
        lines = [f"🎲 <b>NEWS BET · {esc(titles)}</b> · {local(t.timestamp())}", ""]
        if lean:
            bull = lean == "BUY"
            lines += [f"{'🟢' if bull else '🔴'} <b>Lean: {lean} gold</b> · confidence {conf} ({abs(s)}/{len(fac)})",
                      f"🇰🇭 {'ទិញ' if bull else 'លក់'}មាស · ទំនុកចិត្ត {'ទាប' if conf == 'low' else 'មធ្យម' if conf == 'medium' else 'ខ្ពស់'}", ""]
        else:
            lines += ["⚪ <b>No bet</b>: the fundamentals point both ways · មិនភ្នាល់ទេ", ""]
        lines += [f"{'✅' if (v > 0) == (lean == 'BUY') and v != 0 else '❌' if v != 0 else '▫️'} {en}" for v, en, _ in fac]
        if lean:
            lines += ["", f"📍 Entry: price at {local(t.timestamp())} · 🛑 SL ${SL:.0f} · 🎯 TP ${TP:.0f} · closed after {HOLD_MIN} min"]
        lines += [rec, "<i>Gamble on fundamentals, not a tested signal (betting before news lost in our 2-year test). "
                       "Spread widens at the release · tiny size or just watch · ការភ្នាល់ មិនមែនសញ្ញា</i>"]
        mid = send("\n".join(lines), "news soon")
        st.setdefault("bets", []).append({"key": key, "titles": titles, "lean": lean, "conf": conf, "score": s,
                                         "msg_id": mid if isinstance(mid, int) else None})
        st["bets"] = st["bets"][-60:]
        json.dump(st, open(STATE, "w"), indent=1)
        print("news bet posted", titles, lean, conf)
    # 2) grade finished bets
    changed = False
    d5 = df.iloc[:-1]
    for b in st.get("bets", []):
        if not b.get("lean") or b.get("R") is not None:
            continue
        t = pd.Timestamp(b["key"])
        if now < t.to_pydatetime() + timedelta(minutes=HOLD_MIN + 5):
            continue
        w = d5[(d5.index >= t) & (d5.index < t + pd.Timedelta(minutes=HOLD_MIN))]
        if len(w) < 3:
            b["R"] = 0.0; b["note"] = "no data"; changed = True
            continue
        sg = 1 if b["lean"] == "BUY" else -1
        en = float(w["Open"].iloc[0])
        out, how = None, None
        for _, r in w.iterrows():
            if (r["Low"] <= en - SL) if sg > 0 else (r["High"] >= en + SL):
                out, how = -1.0, "SL"; break
            if (r["High"] >= en + TP) if sg > 0 else (r["Low"] <= en - TP):
                out, how = TP / SL, "TP"; break
        if out is None:
            ex = float(w["Close"].iloc[-1])
            out, how = round((ex - en) * sg / SL, 2), f"closed at {fmt(ex)} after {HOLD_MIN} min"
        b.update(R=out, entry=round(en, 2), how=how)
        changed = True
        wn, ln, tot = record(st)
        send(f"{'🏆' if out > 0 else '❌' if out < 0 else '⚪'} <b>News bet result</b> · {b['lean']} from {fmt(en)} · "
             f"{'Hit TP' if how == 'TP' else 'Hit SL' if how == 'SL' else how} · <b>{out:+.1f}R</b>\n"
             f"📊 Record: {wn}W {ln}L · {tot:+.1f}R · លទ្ធផលពិត ទាំងឈ្នះ និងចាញ់", "after the news", reply_to=b.get("msg_id"))
    if changed:
        json.dump(st, open(STATE, "w"), indent=1)
