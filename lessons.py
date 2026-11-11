"""One short lesson per weekday at 12:00 local time (DISPLAY_TZ), in the quiet hours before London.
Never a trade call. Each lesson ties to how the channel's signals work, so members use them better.
State: lessons_state.json (which lesson is next). Lessons rotate."""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from tg import send


TZ = ZoneInfo(os.environ.get("DISPLAY_TZ", "Asia/Phnom_Penh"))
HOUR = 12
STATE = "lessons_state.json"

LESSONS = [
    ("Risk is set by the lot, not the stop",
     "A tight SL feels safe but gets hit by normal noise. Keep the SL where the idea is wrong, then shrink the lot.\n"
     "Gold: 0.01 lot = $1 per $1 move. SL 25 points × 0.02 lot = $50. Choose the lot so a loss is 0.5–1% of your account."),
    ("Why 55% still means losing streaks",
     "With a 55% win rate, 5 or more losses in a row will still happen a few times a year (the 2-year test had 9). That is normal, not broken.\n"
     "If you risk 1% per trade, 3 losses = -3%. If you risk 10%, 3 losses = -27%. Small risk is what lets you reach the wins."),
    ("TP1: close half, move SL to entry",
     "After TP1 the rest of the trade cannot lose. Many 'wins' in our record are exactly this: half at TP1, half back at entry.\n"
     "Don't skip it to hold for TP2. The tested results assume you take TP1."),
    ("No signal is also a signal",
     "Many sessions end without a signal: no 15m close beyond a TARGET line, or the 4H does not agree.\n"
     "Forcing a trade on a quiet day is where most accounts lose money."),
    ("Our signal in one line",
     "Each session the analysis draws a TARGET BUY and a TARGET SELL line. A 15m candle that CLOSES beyond a line, with the 4H trend\n"
     "on the same side, is the signal: 💎 A+ when the 4H agrees strongly, ⭐ B+ otherwise. Wicks don't count, only closes."),
    ("Volume profile: P, b and D",
     "P shape = most volume at the top of the session: buyers won. b shape = at the bottom: sellers won. D = balanced.\n"
     "On our chart the POC is a key level: price often reacts there. Use it as a map, not as an entry by itself."),
    ("What the POC is",
     "POC (point of control) = the price where the most volume traded in a session. It is where the market agreed on value.\n"
     "Price often comes back to test it. Our tests: entering on the POC retest alone was not profitable."),
    ("News: stay out 15 minutes",
     "Around big US news (CPI, NFP, FOMC) the spread widens and price can jump $10–30 in seconds. Stops slip.\n"
     "Rule: no new entries 15 minutes before and after. The 📰 warning comes 30 minutes before."),
    ("Spread is a real cost",
     "Every trade pays the spread. On gold it is about $0.20–0.40 normally, much more around news.\n"
     "This is why tiny scalps (SL 3–5 points) lose over time: the cost is a big part of the stop."),
    ("Don't move your stop away",
     "Moving the SL further when price comes close turns a small loss into a big one.\n"
     "Moving it to entry after TP1 is fine. Moving it away from price never is."),
    ("Revenge trading",
     "After a loss the urge is to win it back right away with a bigger lot. That trade has no setup, only emotion.\n"
     "Take a break. The next tested signal will come; your account needs to still be there."),
    ("Judge by months, not days",
     "One week can be red even with a good strategy. 20–30 trades is the minimum to see if something works.\n"
     "That is why the Friday report shows every result since launch, not just this week."),
    ("Why we post losses",
     "Channels that only show wins hide the real record. You cannot trust a win rate you cannot check.\n"
     "Every signal here gets a result reply: TP, SL or closed. That is the proof."),
    ("Swing vs internal structure",
     "Swing (4H) = the big direction. Internal (1H) = the current pullback inside it.\n"
     "Trades with the swing have better odds. A pullback against it is often just a pause."),
    ("What 'R' means",
     "R = profit measured in risk. +1R = you made what you risked. -1R = a full stop loss.\n"
     "+0.30R per trade means: risk $50 each time, earn about $15 per trade on average over many trades."),
    ("Sessions in your time (winter)",
     "Asia ≈ 06:00–14:00 · London ≈ 14:00–19:00 · New York ≈ 19:00–24:00 (Phnom Penh time).\n"
     "Most big moves come in London and New York. The session plan arrives 30 minutes before each."),
    ("One trade at a time",
     "Opening many small positions at once (like 10 × 0.03) is still one big position. Count the total lot.\n"
     "Total risk across all open trades should stay under 1–2% of the account."),
    ("Weekend gaps",
     "Gold closes Saturday morning and reopens Monday morning (Phnom Penh time). Price can open far from the close.\n"
     "A stop does not protect you inside a gap. Holding over the weekend is extra risk."),
    ("Keep a simple journal",
     "Write: date, buy/sell, entry, SL, TP, result, and one line on how you felt.\n"
     "After 20 trades you will see your own mistakes clearly. Most of them repeat."),
    ("The plan before the trade",
     "Before entering, know three numbers: entry, where you are wrong (SL), where you take profit (TP).\n"
     "If you can't say all three, it isn't a trade yet. Every signal here gives you all three."),
]

KM = [
    ("ហានិភ័យកំណត់ដោយ lot មិនមែនដោយ SL ទេ",
     "SL តូចពេក ងាយប៉ះដោយការឡើងចុះធម្មតា។ ដាក់ SL នៅកន្លែងដែលគំនិតខុស ហើយបន្ថយ lot វិញ។\n"
     "មាស: 0.01 lot = $1 ក្នុងការឡើងចុះ $1។ SL 25 × 0.02 lot = $50។ ជ្រើស lot ឱ្យខាតមិនលើស 0.5–1% នៃគណនី។"),
    ("ឈ្នះ 62% ក៏នៅតែមានចាញ់ជាប់ៗគ្នា",
     "ឈ្នះ 62% ក៏អាចចាញ់ 3 ដងជាប់គ្នា ពីរបីដងក្នុងមួយឆ្នាំ។ នេះធម្មតា មិនមែនខូចទេ។\n"
     "ហានិភ័យ 1% → ចាញ់ 3 ដង = -3%។ ហានិភ័យ 10% → ចាញ់ 3 ដង = -27%។"),
    ("TP1: បិទពាក់កណ្ដាល ហើយប្ដូរ SL មកចំណុចចូល",
     "ក្រោយ TP1 ចំណែកនៅសល់មិនអាចខាតទៀតទេ។\n"
     "កុំរំលង TP1 ដើម្បីរង់ចាំ TP2។ លទ្ធផលសាកល្បងគិតថាអ្នកយក TP1។"),
    ("គ្មានសញ្ញា ក៏ជាសញ្ញាដែរ",
     "ថ្ងៃភាគច្រើន មិនមានសញ្ញា 4H ទេ។ បូតស្ងាត់ ព្រោះគ្មានឱកាសល្អ។\n"
     "ការបង្ខំចូលនៅថ្ងៃស្ងាត់ ជាមូលហេតុដែលគណនីភាគច្រើនខាត។"),
    ("សញ្ញា 4H ក្នុងមួយបន្ទាត់",
     "ទៀន 4H បិទលើតម្លៃខ្ពស់បំផុតនៃមួយសប្តាហ៍មុន → ទិញ។ បិទក្រោមតម្លៃទាបបំផុត → លក់។\n"
     "សាកល្បង 2 ឆ្នាំ: 217 ដង ចំណេញ 62%។"),
    ("Volume Profile: P, b និង D",
     "P = volume ច្រើននៅខាងលើ: អ្នកទិញឈ្នះ។ b = នៅខាងក្រោម: អ្នកលក់ឈ្នះ។ D = ស្មើគ្នា។\n"
     "🟡 ទិញ P ពេលតម្លៃត្រឡប់មក POC · លក់ b ពេលត្រឡប់មក POC · D = មិនចូល។"),
    ("POC ជាអ្វី",
     "POC = តម្លៃដែលមានការជួញដូរច្រើនបំផុតក្នុងមួយសម័យ។\n"
     "តម្លៃច្រើនតែត្រឡប់មកសាកវាវិញ។ នោះជាកន្លែងដែល 🟡 ចូល។"),
    ("ព័ត៌មានធំ: នៅក្រៅ 15 នាទី",
     "ពេលព័ត៌មានធំ (CPI, NFP, FOMC) spread រីកធំ ហើយតម្លៃអាចលោត $10–30 ក្នុងប៉ុន្មានវិនាទី។\n"
     "កុំចូលថ្មី 15 នាទីមុន និង 15 នាទីក្រោយព័ត៌មាន។"),
    ("Spread ជាថ្លៃពិត",
     "រាល់ការជួញដូរ បង់ spread ប្រហែល $0.20–0.40 ពេលធម្មតា ច្រើនជាងនេះពេលព័ត៌មាន។\n"
     "ដូច្នេះ scalp SL 3–5 តែងតែខាតយូរៗទៅ។"),
    ("កុំរំកិល SL ឱ្យឆ្ងាយ",
     "រំកិល SL ឱ្យឆ្ងាយពេលតម្លៃជិតដល់ ធ្វើឱ្យខាតតិចក្លាយជាខាតច្រើន។\n"
     "ប្ដូរ SL មកចំណុចចូលក្រោយ TP1 គឺល្អ។"),
    ("ការជួញដូរដើម្បីយកសងវិញ",
     "ក្រោយខាត ចិត្តចង់យកមកវិញភ្លាម ដោយ lot ធំ។ ការចូលនោះគ្មានការរៀបចំ មានតែអារម្មណ៍។\n"
     "សម្រាកសិន។ សញ្ញាល្អនឹងមកទៀត។"),
    ("វាយតម្លៃជាខែ មិនមែនជាថ្ងៃ",
     "មួយសប្តាហ៍អាចខាត ទោះយុទ្ធសាស្ត្រល្អក៏ដោយ។\n"
     "ត្រូវការយ៉ាងតិច 20–30 ការជួញដូរ ទើបដឹងថាល្អឬអត់។"),
    ("ហេតុអ្វីយើងបង្ហាញការខាត",
     "Channel ដែលបង្ហាញតែឈ្នះ លាក់កំណត់ត្រាពិត។\n"
     "នៅទីនេះ រាល់សញ្ញាមានលទ្ធផល: TP, SL ឬបិទ។ នោះជាភស្តុតាង។"),
    ("Swing និង Internal",
     "Swing (4H) = ទិសដៅធំ។ Internal (1H) = ការត្រឡប់ក្រោយបច្ចុប្បន្ន។\n"
     "ចូលតាម Swing មានឱកាសល្អជាង។"),
    ("'R' មានន័យអ្វី",
     "R = ចំណេញវាស់ដោយហានិភ័យ។ +1R = ចំណេញស្មើហានិភ័យ។ -1R = ប៉ះ SL ពេញ។\n"
     "+0.30R = ហានិភ័យ $50 ម្ដង ចំណេញមធ្យម $15 ក្នុងមួយដង។"),
    ("សម័យជួញដូរ (ម៉ោងកម្ពុជា រដូវរងា)",
     "អាស៊ី ≈ 06:00–14:00 · ឡុងដ៍ ≈ 14:00–19:00 · ញូវយ៉ក ≈ 19:00–24:00។\n"
     "ចលនាធំៗច្រើននៅឡុងដ៍ និងញូវយ៉ក។ ផែនការមកមុនសម័យនីមួយៗ 30 នាទី។"),
    ("រាប់ lot សរុប",
     "បើក 10 × 0.03 ក៏ស្មើ 0.30 lot ដែរ។\n"
     "ហានិភ័យសរុបនៃការជួញដូរទាំងអស់ មិនគួរលើស 1–2% នៃគណនី។"),
    ("គម្លាតចុងសប្តាហ៍",
     "មាសបិទព្រឹកថ្ងៃសៅរ៍ ហើយបើកវិញព្រឹកថ្ងៃច័ន្ទ (ម៉ោងកម្ពុជា)។ តម្លៃអាចបើកឆ្ងាយពីតម្លៃបិទ។\n"
     "SL មិនការពារអ្នកក្នុងគម្លាតនេះទេ។ ទុកការជួញដូរលើសចុងសប្តាហ៍ គឺហានិភ័យបន្ថែម។"),
    ("កត់ត្រាការជួញដូរ",
     "សរសេរ: ថ្ងៃ, ទិញ/លក់, ចូល, SL, TP, លទ្ធផល និងអារម្មណ៍មួយបន្ទាត់។\n"
     "ក្រោយ 20 ដង អ្នកនឹងឃើញកំហុសខ្លួនឯងច្បាស់។"),
    ("ផែនការមុនចូល",
     "មុនចូល ត្រូវដឹង 3 លេខ: ចំណុចចូល, SL, TP។ បើមិនដឹងទាំង 3 មិនទាន់ជាការជួញដូរទេ។\n"
     "រាល់សញ្ញានៅទីនេះ ផ្ដល់ទាំង 3។"),
]


def main():
    now = datetime.now(TZ)
    if now.weekday() > 4 or now.hour != HOUR or now.minute >= 25:
        return
    try:
        st = json.load(open(STATE))
    except Exception:
        st = {"next": 0}
    day = now.strftime("%Y-%m-%d")
    if st.get("day") == day:
        return
    i = st.get("next", 0) % len(LESSONS)
    title, body = LESSONS[i]
    kt, kb = KM[i]
    msg = f"📘 <b>មេរៀន · {kt}</b>\n\n{kb}\n\n<i>{title}: {body}</i>"
    if send(msg, "Lesson") or not os.environ.get("TELEGRAM_TOKEN"):
        json.dump({"next": i + 1, "day": day}, open(STATE, "w"))
        print("lesson sent", i, title)


if __name__ == "__main__":
    main()
