"""Posts the 'how to use this channel' guide ONCE and pins it (the bot needs the 'Pin messages' admin right; if it
does not have it, the guide is still posted and the owner can pin it by hand). Bump VERSION to update the text:
the pinned message is EDITED in place (silent, no new post). A new post happens only if there is no saved guide."""
import json
import os
import urllib.parse
import urllib.request

from tg import group_id, send, setup_sections

VERSION = "2026-11-11w"
STATE = "guide_state.json"

GUIDE = """📌 <b>HOW TO USE XAU.KH · របៀបប្រើ</b>

📊 <b>Analysis</b> (every session): the 4H gives the key levels and the trend; the M15 gives the setup.
🟢 TARGET BUY / 🔻 TARGET SELL lines · Demand / Supply zones = key levels.

✅ <b>SIGNAL</b> (📈 Signals): sent only when a <b>15m candle closes</b> beyond a TARGET line AND the 4H agrees.
💎 <b>A+</b>: with the 4H trend + 6 of 7 confirmations, or a fresh 4H breakout the same way
⭐ <b>B+</b>: with the 4H trend + at least 4 of 7 confirmations (smaller size)
📊 2-year replay of these exact rules: 💎 A+ 55% win · ⭐ B+ about break-even · all ~16 a month
⏭ Against the 4H trend or too few confirmations: <b>not sent</b> (reason shown in 🔎 Setup Analysis)
🎯 <b>TP1 hit</b>: close half, move SL to entry. Max 2 signals a day, all closed by 24:00 (no trades while you sleep).
⚡ <b>SCALP</b>: a quick 5m entry on a small dip after a 4H breakout, TP 2R, closes within 3 h. Only in a clean 4H trend. Tested 2 years: ~2–3 a week, 51% win (wins are 2× losses). 💎 = strong breakout.

🎰 <b>Fun Scalp</b> (own topic): fast 5m scalps, up to 2 a day, any hour. A <b>gamble for fun</b> on a <b>cent account</b> only: about break-even in testing. Not part of 📈 Signals.
🔎 <b>Setup Analysis</b>: why each signal, ✅/❌ checklist.
🏆 <b>Proof</b> / 📊 Friday report: every result, wins AND losses.
📰 News in 30 min: no new entries 15 min before and after.
🎲 <b>News bet</b> (📰 News): the bot's BUY/SELL lean from the fundamentals before big news, with its win/loss record. A gamble, not a signal: tiny size or just watch.

🔔 <b>Get an alert only for real trades</b>: mute the group, then unmute only 📈 Signals. · បិទសំឡេង group ហើយបើកតែ Signals
🤖 Type <b>/check</b> anytime: gold right now + what to do · វាយ /check ដើម្បីមើលមាសឥឡូវ
🎓 <b>/academy</b>: all 45 lessons · <b>/lesson 5</b>: open chapter 5 · មេរៀនទាំងអស់

💡 <b>Small loss = small lot, not a small SL.</b> Risk 0.25–0.5% of your account per trade.
💰 Every signal shows the $ at SL per 0.01 lot.

🇰🇭 💎 A+ = ល្អបំផុត · ⭐ B+ = ល្អ · 4H ជាអ្នកវិនិច្ឆ័យ M15
រង់ចាំទៀន 15m បិទ ទើបចូល។ ដល់ TP1 បិទពាក់កណ្ដាល ហើយប្ដូរ SL មកចំណុចចូល។
កុំចូលមុនព័ត៌មានធំ 15 នាទី។ មិនមែនដំបូន្មានហិរញ្ញវត្ថុទេ។"""

SECTIONS_TEXT = """
🗂 <b>Sections · ផ្នែក</b>
📈 Signals: entry cards + Hit TP / SL replies only · សញ្ញាចូល
🔎 Setup Analysis: why each trade · ហេតុផល
🎰 Fun Scalp: gamble-for-fun scalps, cent account · លេងសើច
📊 Analysis: each session, market map · វិភាគ
📰 News Events: only big news + after-news · ព័ត៌មានធំ
🏆 Proof: every result, wins AND losses · លទ្ធផលពិត
📚 Education: guide and lessons · មេរៀន
💬 General: chat with members · ជជែក
❗ Rules · 📣 Announcement: from the admin
"""
if group_id():   # only in the sectioned group
    GUIDE = GUIDE.replace("\n\n", "\n" + SECTIONS_TEXT + "\n", 1)


RULES_VERSION = "rules-2026-11-11"   # change ONLY when the rules text changes: the Rules post is then EDITED in place
                                    # (silent). Different prefix from VERSION so a guide update can never touch it.
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
    if st.get("chat") == group_id() and st.get("msg_id"):
        if st.get("version") == RULES_VERSION or str(st.get("version", "")).startswith("2026-"):
            if st.get("version") != RULES_VERSION:   # old shared version numbers: adopt, never re-post
                st["version"] = RULES_VERSION
                json.dump(st, open("rules_state.json", "w"))
            return
        tok = os.environ.get("TELEGRAM_TOKEN")
        try:   # rules text changed: edit the existing post, no new message, no alert
            body = urllib.parse.urlencode({"chat_id": group_id(), "message_id": st["msg_id"], "text": RULES,
                                           "parse_mode": "HTML"}).encode()
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/editMessageText", data=body), timeout=20)
            print("rules edited in place")
        except Exception as e:
            print("rules edit failed (kept the old post, no new one):", e)
        st["version"] = RULES_VERSION
        json.dump(st, open("rules_state.json", "w"))
        return
    mid = send(RULES, "Rules", silent=True)   # first time in this group only
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
    mid = send(GUIDE, "Guide", silent=True)
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
