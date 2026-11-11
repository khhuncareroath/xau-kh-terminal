"""Posts the 'how to use this channel' guide ONCE and pins it (the bot needs the 'Pin messages' admin right; if it
does not have it, the guide is still posted and the owner can pin it by hand). Bump VERSION to update the text:
the pinned message is EDITED in place (silent, no new post). A new post happens only if there is no saved guide."""
import json
import os
import urllib.parse
import urllib.request

from tg import group_id, send, setup_sections

VERSION = "2026-11-11n"
STATE = "guide_state.json"

GUIDE = """📌 <b>HOW TO USE XAU.KH · របៀបប្រើ</b>

✅ <b>BUY/SELL NOW</b>: one tested signal, the 4H breakout. <b>Intraday only</b>: closes within 12 h. Risk 1% max.
It is sent only when ALL of these are true:
 1️⃣ 4H candle closes beyond the 1-week high/low
 2️⃣ strong close (near the high for BUY, near the low for SELL)
 3️⃣ clean 4H trend (not choppy)
 4️⃣ Day Meter 70%+ (the day is moving)
💎 <b>A+</b>: all 4 + Day Meter 100%+ (79% win in 2-year test) · full size
⭐ <b>B+</b>: all 4, Day Meter 70–100% (75% win in test) · full size
⏭ Other breakouts are <b>not sent</b>: about 2–3 A+/B+ a month. Fewer, but stronger.
🎯 <b>TP1 hit</b>: close half, move SL to entry.

📐 <b>SETUP IDEA</b> (📊 Analysis, every session): Swing / Internal bias, Swing High / Low, 🟢 TARGET BUY and 🔴 TARGET SELL lines.
When a 15m candle <b>closes</b> beyond a line, the bot sends 📐 <b>SETUP</b> in 📈 Signals (entry, SL, TP1, TP2). Max 2 a day.
Setup ideas are analysis, not tested like A+/B+: <b>small size 0.25–0.5%</b>. Every result is shown, wins AND losses.

📡 <b>Strategy Radar</b>: live chart between signals. Not an entry.
📏 Day Meter: 70% = B+ zone · 100% = A+ zone
KE TV HX = buy · LUK MOA = sell (on the charts)
🧾 <b>Signal proof</b> / 📊 Friday report: every result, wins AND losses.
📰 News in 30 min: no new entries 15 min before and after.

🔔 <b>Get an alert only for real trades</b>: mute the group, then unmute only 📈 Signals. Your phone rings only for a confirmed BUY/SELL. · បិទសំឡេង group ហើយបើកតែ Signals
🤖 Type <b>/check</b> anytime: gold right now + what to do · វាយ /check ដើម្បីមើលមាសឥឡូវ
🎓 <b>/academy</b>: all 45 lessons · <b>/lesson 5</b>: open chapter 5 · មេរៀនទាំងអស់

💡 <b>Small loss = small lot, not a small SL.</b> Risk 0.5–1% of your account per trade.
💰 Every signal shows the $ result per 0.01 lot: SL $22 = −$22 at 0.01 lot.

🇰🇭 💎 A+ = ល្អបំផុត · ⭐ B+ = ល្អ (២–៣ ដង/ខែ) · 📐 Setup = គំនិតពីការវិភាគ ប្រើ lot តូច
រង់ចាំទៀន 15m បិទលើ/ក្រោមខ្សែ TARGET ទើបចូល។
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


RULES_VERSION = "2026-11-11n"
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
