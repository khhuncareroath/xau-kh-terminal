"""Posts the 'how to use this channel' guide ONCE and pins it (the bot needs the 'Pin messages' admin right; if it
does not have it, the guide is still posted and the owner can pin it by hand). Bump VERSION to update the text:
the pinned message is EDITED in place (silent, no new post). A new post happens only if there is no saved guide."""
import json
import os
import urllib.parse
import urllib.request

from tg import group_id, send, setup_sections

VERSION = "2026-11-11d"
STATE = "guide_state.json"

GUIDE = """📌 <b>HOW TO USE XAU.KH · របៀបប្រើ</b>

✅ <b>BUY/SELL NOW</b>: tested 4H breakout. Closes within 12 h. Risk 1% max.
🖕 <b>COMBO</b>: breakout on a moving day (68% win in test) · full size
🖕🖕 <b>PREMIUM SWING</b>: breakout on a big day (77% win) · hold 1–5 days
⏭ Quiet-day breakouts are <b>not sent</b> (only 50/50 in testing)
🤬 <b>COMBO SCALP</b>: after a 🖕 breakout, a fast 5m entry with a small SL (~$7), TP 2R. Enter at once or skip. Size 0.25–0.5%
🤬 <b>Plan</b> 🟡: other smaller setups, small size 0.25–0.5%
🎯 <b>TP1 hit</b>: close half, move SL to entry.

📡 <b>Strategy Radar</b>: live chart between signals. Not an entry.
📏 Day Meter: 70% = 🖕 zone · 100% = 🖕🖕 zone
KE TV HX = buy · LUK MOA = sell (on the charts)
🧾 <b>Signal proof</b> / 📊 Friday report: every result, wins AND losses.
📰 News in 30 min: no new entries 15 min before and after.

💡 <b>Small loss = small lot, not a small SL.</b> Risk 0.5–1% of your account per trade.
💰 Every signal shows the $ result per 0.01 lot: SL $22 = −$22 at 0.01 lot.

🇰🇭 🖕🖕 = ល្អបំផុត · 🖕 = ល្អ · 🤬 = តូច ប្រើ lot តូច
ដល់ TP1 បិទពាក់កណ្ដាល ហើយប្ដូរ SL មកចំណុចចូល។
កុំចូលមុនព័ត៌មានធំ 15 នាទី។ មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។"""

SECTIONS_TEXT = """
🗂 <b>Sections · ផ្នែក</b>
📈 Signals: entry cards + Hit TP / SL replies only · សញ្ញាចូល
🔎 Setup Analysis: why each trade, Radar, heads-up · ហេតុផល
📊 Analysis: each session, market map · វិភាគ
📰 News Events: only big news + after-news · ព័ត៌មានធំ
🏆 Proof: every result, wins AND losses · លទ្ធផលពិត
📚 Education: guide and lessons · មេរៀន
💬 General: chat with members · ជជែក
❗ Rules · 📣 Announcement: from the admin
"""
if group_id():   # only in the sectioned group
    GUIDE = GUIDE.replace("\n\n", "\n" + SECTIONS_TEXT + "\n", 1)


RULES_VERSION = "1"
RULES = """❗ <b>RULES · ច្បាប់ក្រុម</b>

1. Be respectful. No insults, no politics. · គោរពគ្នា
2. No ads, no links to other groups or brokers. · ហាមផ្សាយពាណិជ្ជកម្ម
3. ⚠️ Admins <b>never</b> DM you first and never ask for money, passwords or your account. Anyone who does is a scammer. · Admin មិនដែល DM មុនទេ
4. Signals are education, not financial advice. Risk 0.5–1% per trade, always use SL. · មិនមែនដំបូន្មានហិរញ្ញវត្ថុ
5. Every result is shown in 🏆 Proof, wins AND losses. · លទ្ធផលពិតទាំងអស់
6. Chat in 💬 General. The other sections are read-only. · ជជែកនៅ General

Breaking the rules = removed. · បំពានច្បាប់ = ដកចេញ"""


def post_rules():
    """Posts the rules once in the Rules section (sectioned group only)."""
    if not group_id():
        return
    try:
        st = json.load(open("rules_state.json"))
    except Exception:
        st = {}
    if st.get("version") == RULES_VERSION and st.get("chat") == group_id():
        return
    mid = send(RULES, "Rules")
    if mid:
        json.dump({"version": RULES_VERSION, "chat": group_id(), "msg_id": mid}, open("rules_state.json", "w"))


def main():
    setup_sections()
    post_rules()
    try:
        st = json.load(open(STATE))
    except Exception:
        st = {}
    tok = os.environ.get("TELEGRAM_TOKEN")
    chat = group_id() or os.environ.get("TELEGRAM_CHAT_ID")
    if st.get("msg_id") and st.get("chat", os.environ.get("TELEGRAM_CHAT_ID")) != chat:
        st = {}   # moved to the sectioned group: post the guide there once
    if st.get("version") == VERSION:
        return
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
