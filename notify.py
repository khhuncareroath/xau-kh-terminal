"""Best-setup alert. Looks at everything the engines produced, scores each idea, and sends ONE alert: the best one.
Delivery (both optional, either or both):
  Telegram: secrets TELEGRAM_TOKEN + TELEGRAM_CHAT_ID (use a channel like @xaukh_alerts so anyone can subscribe)
  ntfy.sh : secret NTFY_TOPIC (people install the free ntfy app and subscribe to that topic, no account needed)
Optional env: SITE_URL (link in the alert), MIN_ALERT_SCORE (default 75), ALERT_COOLDOWN_H (default 3).
Scores are a hand-made ranking, not a backtested edge. These are analysis ideas, not signals."""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime

MIN_SCORE = float(os.environ.get("MIN_ALERT_SCORE", 75))
COOLDOWN = float(os.environ.get("ALERT_COOLDOWN_H", 3)) * 3600
SITE = os.environ.get("SITE_URL", "")
TV = "https://www.tradingview.com/chart/?symbol=COMEX%3AGC1%21"


def jl(n):
    try:
        return json.load(open(n))
    except Exception:
        return {}


def news_soon(news, mins=60):
    now = time.time()
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        try:
            t = datetime.fromisoformat(e["time"].replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        m = (t - now) / 60
        if -15 <= m <= mins:
            return f"{e['title']} in {max(0, round(m))} min"
    return None


def candidates(ict, conf, q):
    qs = (q or {}).get("score", 50)
    out, zones = [], [z for z in conf.get("zones", []) if z.get("rating") == "A"]
    st = ict.get("setup") or {}
    stage = st.get("stage") or 0
    sw = (ict.get("sweeps") or [{}])[-1].get("time", "")
    if stage in (2, 3) and st.get("dir") and all(st.get(k) for k in ("entry", "stop", "target", "zone")) and (st.get("rr") or 0) >= 1.5:
        s = (55 if stage == 3 else 40) + 0.3 * qs + min(st["rr"], 4) * 5
        h1 = ((ict.get("timeframes") or {}).get("1H") or {}).get("bias")
        s += 10 if h1 == st["dir"] else -10 if h1 in ("bull", "bear") else 0
        lo, hi = st["zone"]
        if any(z["low"] <= hi + 3 and z["high"] >= lo - 3 for z in zones):
            s += 10
        out.append({"kind": "setup", "rank": stage, "score": s, "dir": st["dir"], "key": f"setup|{st['dir']}|{sw}",
                    "title": ("Retest in play" if stage == 3 else "Setup forming") + f" · {'Bullish' if st['dir'] == 'bull' else 'Bearish'}",
                    "lines": [st.get("label", ""), f"Entry {st['entry']} · Stop {st['stop']} · Target {st['target']} · about 1:{st['rr']}"]})
    near = [z for z in zones if abs(z.get("distance", 99)) <= 5]
    if near:
        z = min(near, key=lambda z: abs(z["distance"]))
        s = 30 + 0.3 * qs + (15 if abs(z["distance"]) <= 2 else 8) + min(z.get("score", 12), 16)
        side = {"support": "support", "resistance": "resistance"}.get(z.get("role"), "A zone")
        out.append({"kind": "zone", "rank": 1, "score": s, "dir": None, "key": f"zone|{round(z['mid'])}",
                    "title": f"Price at A-rated {side}",
                    "lines": [f"Zone {z['low']}-{z['high']} ({z['distance']:+.1f} pts away)", "Wait for a sweep and a structure shift before acting."]})
    return out


def send(msg, title):
    sent = False
    tok, chat, topic = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID"), os.environ.get("NTFY_TOPIC")
    if tok and chat:
        try:
            data = urllib.parse.urlencode({"chat_id": chat, "text": msg, "disable_web_page_preview": "true"}).encode()
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=data), timeout=20)
            sent = True
        except Exception as e:
            print("telegram failed:", e)
    if topic:
        try:
            h = {"Title": title.encode("utf-8").decode("latin-1", "ignore"), "Priority": "high", "Tags": "chart_with_upwards_trend"}
            if SITE:
                h["Click"] = SITE
            urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), headers=h), timeout=20)
            sent = True
        except Exception as e:
            print("ntfy failed:", e)
    if not sent:
        print("nothing sent (no secrets or all failed). Message was:\n" + msg)
    return sent


def main():
    ict, conf, q, news, state = jl("ict.json"), jl("confluence.json"), jl("quality.json"), jl("news.json"), jl("notify_state.json")
    if (q or {}).get("grade") == "Avoid":
        print("quality is Avoid, no alert"); return
    ns = news_soon(news)
    if ns:
        print("high-impact news soon, holding alerts:", ns); return
    cands = candidates(ict, conf, q)
    if not cands:
        print("no candidate"); return
    best = max(cands, key=lambda c: c["score"])
    if best["score"] < MIN_SCORE:
        print(f"best idea scored {best['score']:.0f}, below {MIN_SCORE:.0f}"); return
    now = time.time()
    same = state.get("key") == best["key"]
    if same and best["rank"] <= state.get("rank", 0):
        print("already alerted"); return
    if not same and now - state.get("t", 0) < COOLDOWN and best["score"] < state.get("score", 0) + 10:
        print("cooldown, not clearly better than last alert"); return
    lines = [f"XAU.KH · {best['title']}", *best["lines"], f"Price {ict.get('price', '')}"]
    if q:
        lines.append(f"Quality {q['grade']} ({q['score']})" + "".join("\n! " + f for f in q.get("flags", [])))
    lines += [f"Best of {len(cands)} idea(s) right now. Analysis idea, not a signal: confirm with your own entry model.", TV]
    if SITE:
        lines.append(SITE)
    if send("\n".join(l for l in lines if l), best["title"]):
        json.dump({"key": best["key"], "rank": best["rank"], "score": round(best["score"], 1), "t": now}, open("notify_state.json", "w"))
        print("sent", best["key"])


if __name__ == "__main__":
    main()
