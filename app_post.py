"""📲 XAU.KH App topic, posted ONCE (owner, 13 Nov 2026: "a topic just for the app, make it convenient").
Creates the "App · កម្មវិធី" topic (closed: only the bot posts), sends one welcome post with a button for every part of
the app, pins it, and posts a short "new: XAU.KH App" note in Announcement. State in app_state.json (committed by
loop.py), so nothing is posted twice. APP_POST=off stops it.  Run: python app_post.py"""
import json
import os

STATE = "app_state.json"

WELCOME = (
    "📲 <b>XAU.KH App · កម្មវិធី XAU.KH</b>\n\n"
    "Everything about gold in one place, inside Telegram. Free, no sign-up.\n"
    "អ្វីៗទាំងអស់អំពីមាស នៅកន្លែងតែមួយ ក្នុង Telegram។ ឥតគិតថ្លៃ មិនចាំបាច់ចុះឈ្មោះ។\n\n"
    "🟢 <b>Today · ថ្ងៃនេះ</b>: price, direction, today's buy / sell areas, the bot's alert, next big news countdown\n"
    "តម្លៃ ទិសដៅ តំបន់ទិញ/លក់ថ្ងៃនេះ សញ្ញាបូត និងម៉ោងព័ត៌មានធំបន្ទាប់\n\n"
    "📈 <b>Chart</b>: live chart and the bot's zones · ក្រាហ្វផ្ទាល់ និងតំបន់របស់បូត\n"
    "🏆 <b>Record · លទ្ធផល</b>: every signal, wins and losses · សញ្ញាទាំងអស់ ឈ្នះ និងចាញ់\n"
    "💰 <b>Scale Up</b>: your money, your goal, lot size for you · ទំហំ lot សម្រាប់គណនីរបស់អ្នក\n"
    "📒 <b>Journal</b>: follow the signals like a trade diary · កំណត់ត្រាការជួញដូរ\n"
    "🎓 <b>Guide · មគ្គុទ្ទេសក៍</b>: how to use XAU.KH · របៀបប្រើ XAU.KH\n\n"
    "💡 <b>Tip:</b> every signal and analysis post has a <b>📲 Open App</b> button under it.\n"
    "💡 គ្រប់សញ្ញា និងការវិភាគ មានប៊ូតុង <b>📲 Open App</b> នៅខាងក្រោម។\n"
    "In a private chat with the bot, the <b>XAU.KH</b> button next to the message box opens it too, or type /app.\n\n"
    "<i>Analysis to learn from, not financial advice. Always use a stop loss.</i>"
)

BUTTONS = [[("🟢 Today · ថ្ងៃនេះ", "today"), ("📈 Chart", "chart")],
           [("🏆 Record · លទ្ធផល", "record"), ("💰 Scale Up", "scaleup")],
           [("📒 Journal", "journal"), ("🎓 Guide", "guide")]]

ANNOUNCE = ("📣 <b>New: XAU.KH App · ថ្មី: កម្មវិធី XAU.KH</b>\n\n"
            "Gold price, direction, buy / sell areas, chart, news countdown and the honest record, all inside Telegram.\n"
            "តម្លៃមាស ទិសដៅ តំបន់ទិញ/លក់ ក្រាហ្វ ម៉ោងព័ត៌មាន និងលទ្ធផលពិត ទាំងអស់នៅក្នុង Telegram។\n\n"
            "Tap the button below · ចុចប៊ូតុងខាងក្រោម 👇")


def load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save(st):
    json.dump(st, open(STATE, "w"), indent=1)


def keyboard():
    import tg
    rows = [[{"text": t, "url": tg.app_url(tab)} for t, tab in row] for row in BUTTONS]
    return json.dumps({"inline_keyboard": rows}, ensure_ascii=False)


def main():
    if os.environ.get("APP_POST", "on") == "off":
        print("app post: off"); return
    import tg
    if not (os.environ.get("TELEGRAM_TOKEN") and tg.group_id()):
        print("app post: no Telegram group/secrets"); return
    st = load()
    if not st.get("welcome"):
        res = tg._send_tg("sendMessage", "app", {"text": WELCOME, "parse_mode": "HTML", "disable_web_page_preview": "true",
                                                 "reply_markup": keyboard()})
        mid = (res or {}).get("message_id")
        if not mid:
            print("app post: welcome failed"); return
        st["welcome"] = mid
        save(st)
        print("app post: welcome", mid)
    if not st.get("pinned"):
        try:
            chat, _ = tg.target("app")
            tg._api("pinChatMessage", {"chat_id": chat, "message_id": st["welcome"], "disable_notification": "true"})
            st["pinned"] = True
        except Exception as e:
            print("app post: pin failed (give the bot 'Pin messages'):", e)
            st["pinned"] = "failed"
        save(st)
    if not st.get("announce"):
        res = tg._send_tg("sendMessage", "announcement", {"text": ANNOUNCE, "parse_mode": "HTML",
                                                          "reply_markup": tg.app_markup("today")})
        st["announce"] = (res or {}).get("message_id") or "failed"
        save(st)
        print("app post: announcement", st["announce"])


if __name__ == "__main__":
    main()
