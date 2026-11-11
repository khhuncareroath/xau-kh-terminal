"""Posts the 'how to use this channel' guide ONCE and pins it (the bot needs the 'Pin messages' admin right; if it
does not have it, the guide is still posted and the owner can pin it by hand). Bump VERSION to update the text:
the pinned message is EDITED in place (silent, no new post). A new post happens only if there is no saved guide."""
import json
import os
import urllib.parse
import urllib.request

from tg import send, target

VERSION = "2026-11-11a"
STATE = "guide_state.json"

GUIDE = """📌 <b>HOW TO USE XAU.KH · របៀបប្រើ</b>

✅ <b>BUY/SELL NOW</b>: tested 4H breakout. Closes within 12 h. Risk 1% max.
🖕 <b>COMBO</b>: breakout on a moving day (68% win in test) · full size
🖕🖕 <b>PREMIUM SWING</b>: breakout on a big day (77% win) · hold 1–5 days
◽ <b>Normal</b>: quiet-day breakout · half size or skip
🤬 <b>Smaller setup</b> (🟡 plan / 🔷 experimental): small size 0.25–0.5%
🎯 <b>TP1 hit</b>: close half, move SL to entry.

📡 <b>Strategy Radar</b>: live chart between signals. Not an entry.
📏 Day Meter: 70% = 🖕 zone · 100% = 🖕🖕 zone
KE TV HX = buy · LUK MOA = sell (on the charts)
🧾 <b>Signal proof</b> / 📊 Friday report: every result, wins AND losses.
📰 News in 30 min: no new entries 15 min before and after.

💡 <b>Small loss = small lot, not a small SL.</b> Risk 0.5–1% of your account per trade.

🇰🇭 🖕🖕 = ល្អបំផុត · 🖕 = ល្អ · 🤬 = តូច ប្រើ lot តូច
ដល់ TP1 បិទពាក់កណ្ដាល ហើយប្ដូរ SL មកចំណុចចូល។
កុំចូលមុនព័ត៌មានធំ 15 នាទី។ មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។"""

SECTIONS_TEXT = """
🗂 <b>Sections · ផ្នែក</b>
🎯 Signals: entries, TP/SL results, Radar · ចូល / លទ្ធផល
📊 Analysis: each session, market map · វិភាគ
📰 News: only big news + after-news · ព័ត៌មានធំ
🧾 Proof: every result, wins AND losses · លទ្ធផលពិត
📚 Learn: guide and lessons · រៀន
💬 General: chat with members · ជជែក
"""
if os.environ.get("TELEGRAM_GROUP_ID"):   # only in the sectioned group
    GUIDE = GUIDE.replace("\n\n", "\n" + SECTIONS_TEXT + "\n", 1)


def main():
    try:
        st = json.load(open(STATE))
    except Exception:
        st = {}
    if st.get("version") == VERSION:
        return
    tok = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_GROUP_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    if st.get("msg_id") and st.get("chat", os.environ.get("TELEGRAM_CHAT_ID")) != chat:
        st = {}   # moved to the sectioned group: post the guide there once
    if st.get("msg_id") and tok and chat:   # already posted: edit the pinned guide, never post it again
        try:
            body = urllib.parse.urlencode({"chat_id": chat, "message_id": st["msg_id"], "text": GUIDE, "parse_mode": "HTML",
                                           "disable_web_page_preview": "true"}).encode()
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/editMessageText", data=body), timeout=20)
            print("guide edited in place")
        except Exception as e:
            print("guide edit failed (kept the old text, no new post):", e)
        st["version"] = VERSION
        json.dump(st, open(STATE, "w"))
        return
    mid = send(GUIDE, "Guide")
    if not mid:
        return
    st = {"version": VERSION, "msg_id": mid if isinstance(mid, int) else None, "chat": chat}
    if tok and chat and isinstance(mid, int):
        try:
            body = urllib.parse.urlencode({"chat_id": chat, "message_id": mid, "disable_notification": "true"}).encode()
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/pinChatMessage", data=body), timeout=20)
            st["pinned"] = True
        except Exception as e:
            print("pin failed (give the bot the 'Pin messages' right, or pin it by hand):", e)
            st["pinned"] = False
    json.dump(st, open(STATE, "w"))
    print("guide posted", st)


if __name__ == "__main__":
    main()
