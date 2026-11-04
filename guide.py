"""Posts the 'how to use this channel' guide once and pins it (the bot needs the 'Pin messages' admin right; if it
does not have it, the guide is still posted and the owner can pin it by hand). Bump VERSION to post a new guide."""
import json
import os
import urllib.parse
import urllib.request

from tg import send

VERSION = "2026-11-04"
STATE = "guide_state.json"

GUIDE = """📌 <b>HOW TO USE XAU.KH · របៀបប្រើ</b>

✅ <b>BUY/SELL NOW ✅ tested</b>: the 4H signal (2 years: 69% win). Risk 1% max.
🟡 <b>BUY/SELL NOW 🟡 plan trade</b>: promising, not proven yet. Risk 0.5% max.
🎯 <b>TP1 hit</b>: close half, move SL to entry. The rest runs with no risk.

🇬🇧🇺🇸🌏 <b>Session plan</b>: the map for the session. ✅ = level with the trend.
🔔 <b>Near level</b>: heads-up only. Wait for the 15m candle to close.
📰 <b>News in 30 min</b>: no new entries 15 min before and after.
📊 <b>Friday report</b>: every result, wins and losses.

💡 <b>Small loss = small lot, not a small SL.</b>
SL 25 points × 0.02 lot = about $50 risk. Pick the lot so the loss is 0.5–1% of your account.
$1 move = 10 pips.

🇰🇭 សញ្ញា ✅ = បានសាកល្បង 2 ឆ្នាំ · 🟡 = ផែនការ ហានិភ័យ 0.5% ប៉ុណ្ណោះ
ដល់ TP1 បិទពាក់កណ្ដាល ហើយប្ដូរ SL មកចំណុចចូល។
កុំចូលមុនព័ត៌មានធំ 15 នាទី។ មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។"""


def main():
    try:
        st = json.load(open(STATE))
    except Exception:
        st = {}
    if st.get("version") == VERSION:
        return
    mid = send(GUIDE, "Guide")
    if not mid:
        return
    st = {"version": VERSION, "msg_id": mid if isinstance(mid, int) else None}
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
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
