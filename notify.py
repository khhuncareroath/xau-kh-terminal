"""Telegram alerts when a new sweep or shift appears. Needs repo secrets TELEGRAM_TOKEN and TELEGRAM_CHAT_ID. Skips quietly without them."""
import json, os, urllib.parse, urllib.request

def jl(n):
    return json.load(open(n)) if os.path.exists(n) else {}

def main():
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    ict, q, state = jl("ict.json"), jl("quality.json"), jl("notify_state.json")
    st = ict.get("setup") or {}
    stage = st.get("stage") or 0
    if stage not in (1, 2, 3) or not st.get("dir"):
        return
    sw = (ict.get("sweeps") or [{}])[-1].get("time", "")
    key = f"{st['dir']}|{stage}|{sw}"
    if state.get("key") == key:
        return
    lines = [f"XAU.KH · {'Bullish' if st['dir'] == 'bull' else 'Bearish'} idea", st.get("label", ""), f"Price {ict.get('price', '')}"]
    if st.get("entry") and st.get("stop") and st.get("target"):
        lines.append(f"Entry {st['entry']} · Stop {st['stop']} · Target {st['target']}" + (f" · about 1:{st['rr']}" if st.get("rr") else ""))
    if q: lines.append(f"Quality {q['grade']} ({q['score']})" + ("".join("\n! " + f for f in q.get("flags", []))))
    lines.append("Analysis idea, not a signal. Confirm with your own entry model.")
    msg = "\n".join(l for l in lines if l)
    if not (tok and chat):
        print("no Telegram secrets, would send:\n" + msg); return
    data = urllib.parse.urlencode({"chat_id": chat, "text": msg}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=data), timeout=20)
    json.dump({"key": key}, open("notify_state.json", "w")); print("sent")

if __name__ == "__main__":
    main()
