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


# plain Khmer: what each event is and why it moves gold (English version: session.EVENT_RULES)
EVENT_KM = [
    (("cpi", "pce", "inflation"), "អតិផរណា (ថ្លៃទំនិញឡើង)។ ខ្ពស់ជាងការរំពឹង → Fed មិនកាត់ការប្រាក់ → ដុល្លារឡើង → មាសចុះ។ ទាបជាង → មាសឡើង។"),
    (("ppi",), "ថ្លៃដើមរបស់ក្រុមហ៊ុន (PPI) ជាសញ្ញាមុនរបស់អតិផរណា។ ខ្ពស់ → អតិផរណាអាចឡើង → មាសចុះ។ ទាប → មាសឡើង។"),
    (("non-farm", "nonfarm", "payroll", "employment change"), "ការងារថ្មីនៅអាមេរិក (NFP)។ ការងារច្រើន → សេដ្ឋកិច្ចខ្លាំង ដុល្លារខ្លាំង → មាសចុះ។ តិច → មាសឡើង។"),
    (("unemployment rate",), "អត្រាគ្មានការងារ។ ខ្ពស់ → សេដ្ឋកិច្ចខ្សោយ → Fed ងាយកាត់ការប្រាក់ → មាសឡើង។"),
    (("jobless claims", "unemployment claims"), "ចំនួនអ្នកសុំប្រាក់ឧបត្ថម្ភគ្មានការងារ។ ច្រើន → ការងារខ្សោយ → មាសឡើងបន្តិច។"),
    (("fomc", "federal funds", "fed chair", "powell", "interest rate decision"), "ការសម្រេចការប្រាក់របស់ Fed។ តឹង (hawkish) → ដុល្លារឡើង → មាសចុះ។ ទន់ (dovish) → មាសឡើង។ សន្និសីទសារព័ត៌មានច្រើនតែរំកិលមាសខ្លាំងជាងការសម្រេច។"),
    (("gdp",), "កំណើនសេដ្ឋកិច្ច (GDP)។ ខ្លាំងជាងការរំពឹង → ដុល្លារឡើង → មាសចុះ។"),
    (("ism", "pmi"), "ការស្ទង់មតិអាជីវកម្ម (PMI)។ ខ្លាំង → ដុល្លារឡើង → មាសចុះ។ ខ្សោយ → មាសឡើង។"),
    (("retail sales",), "ការចំណាយរបស់អតិថិជន។ លក់ដាច់ → ដុល្លារឡើង → មាសចុះ។"),
    (("jolts", "job openings"), "កន្លែងការងារទំនេរ។ ច្រើន → ទីផ្សារការងារតឹង → Fed តឹង → មាសចុះ។"),
]


def explain(group, fac, lean, macro):
    """🧠 Plain-language fundamentals for beginners: the event, today's picture, the two scenarios, and (if an AI key is
    set) 2-3 lines of today's economic / political context from the headlines. Never gives a trade itself."""
    from session import explain_event
    from tg import esc
    lines = ["🧠 <b>Fundamentals explained · ពន្យល់សេដ្ឋកិច្ច</b>", ""]
    seen = set()
    for _, e, sg in group:
        k = next((km for keys, km in EVENT_KM if any(x in e["title"].lower() for x in keys)), None)
        en = explain_event(e["title"])
        if en in seen:
            continue
        seen.add(en)
        lines += [f"📌 <b>{esc(e['title'])}</b>", en] + ([f"🇰🇭 {k}"] if k else []) + [""]
    lines.append("<b>Today's picture · ស្ថានភាពថ្ងៃនេះ</b>")
    why = {"Dollar": "gold is priced in dollars: a stronger dollar makes gold cost more abroad, so it falls · ដុល្លារខ្លាំង មាសចុះ",
           "US 10y": "higher yields pay more than gold (gold pays nothing), money leaves gold · ការប្រាក់ខ្ពស់ មាសចុះ",
           "Forecast": "the market has already priced in the forecast: only a SURPRISE moves gold · មានតែលេខភ្ញាក់ផ្អើលទេ ដែលរំកិលមាស",
           "Gold 4H": "the trend before the news often continues after the first spike · និន្នាការច្រើនតែបន្ត"}
    for v, en_, km in fac:
        w = next((txt for k_, txt in why.items() if en_.startswith(k_)), "")
        lines.append(f"• {en_}" + (f"\n   <i>{w}</i>" if w else ""))
    fc = [(e["title"], e.get("forecast")) for _, e, _ in group if e.get("forecast")]
    sgs = [sg for _, _, sg in group if sg]
    if fc and sgs:
        hi_up = sum(sgs) > 0
        f0 = f"{esc(fc[0][0])} {esc(fc[0][1])}"
        lines += ["", "<b>The 2 scenarios · លទ្ធផល ២ យ៉ាង</b>",
                  f"⬆️ Higher than {f0} → gold usually {'UP ↑' if hi_up else 'DOWN ↓'}"
                  + (f" ({'BUY' if hi_up else 'SELL'} wins)" if lean else ""),
                  f"⬇️ Lower than {f0} → gold usually {'DOWN ↓' if hi_up else 'UP ↑'}"
                  + (f" ({'SELL' if hi_up else 'BUY'} wins)" if lean else ""),
                  "↔️ Same as forecast → small move, the trend usually continues · ដូចការរំពឹង មាសរំកិលតិច"]
    ctx = _ai_context(group, macro)
    if ctx:
        lines += ["", "<b>Context today · បរិបទថ្ងៃនេះ</b>", esc(ctx)]
    lines += ["", "<i>Fundamentals give the usual direction, not a promise: the market often moves before or against the "
                  "numbers · មិនមែនការធានាទេ</i>"]
    return "\n".join(lines)


def _ai_context(group, macro):
    """2-3 short lines (Khmer + English terms) on today's economic / political context, from the latest headlines.
    Only with ANTHROPIC_API_KEY or GEMINI_API_KEY; returns '' otherwise or on any error."""
    import urllib.parse
    import urllib.request
    key = (("anthropic", os.environ["ANTHROPIC_API_KEY"]) if os.environ.get("ANTHROPIC_API_KEY") else
           ("gemini", os.environ["GEMINI_API_KEY"]) if os.environ.get("GEMINI_API_KEY") else None)
    if not key:
        return ""
    try:
        import breaking
        heads = "\n".join(f"- {h['title']}" for h in breaking.fetch()[:25])
        ev = ", ".join(e["title"] + f" (forecast {e.get('forecast')}, previous {e.get('previous')})" for _, e, _ in group)
        prompt = (f"Upcoming US release: {ev}. Dollar today {(macro.get('dxy') or {}).get('chg_pct')}%, US 10y "
                  f"{(macro.get('us10y') or {}).get('chg_bp')}bp.\nToday's headlines:\n{heads}\n\n"
                  "For Cambodian beginners who do not know economics or politics: in 3 short lines of simple Khmer "
                  "(keep English terms like Fed, CPI, dollar), explain what the market expects from this release and the "
                  "economic or political news today that matters for gold (Fed, tariffs, war, elections...). Facts only "
                  "from the headlines, no predictions, no trade advice. Plain text, no markdown.")
        if key[0] == "anthropic":
            body = {"model": os.environ.get("AI_MODEL", "claude-haiku-5-5"), "max_tokens": 400,
                    "messages": [{"role": "user", "content": prompt}]}
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                         headers={"x-api-key": key[1], "anthropic-version": "2023-06-01", "content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=40))
            txt = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
        else:
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600}}
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/{os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')}"
                   f":generateContent?key={urllib.parse.quote(key[1])}")
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(),
                                                                        headers={"content-type": "application/json"}), timeout=40))
            txt = "".join(p.get("text", "") for c in r.get("candidates", []) for p in c.get("content", {}).get("parts", []))
        return txt.strip()[:700]
    except Exception as e:
        print("news context AI failed:", e)
        return ""


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
        try:   # 🧠 the fundamentals explained for beginners, as a reply under the bet
            send(explain(group, fac, lean, macro), "news soon", reply_to=mid if isinstance(mid, int) else None, silent=True)
        except Exception as e:
            print("news explain failed:", e)
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
