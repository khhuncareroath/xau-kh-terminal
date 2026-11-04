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
    ("Why 69% still means losing streaks",
     "With a 69% win rate, 3 losses in a row will still happen a few times a year. That is normal, not broken.\n"
     "If you risk 1% per trade, 3 losses = -3%. If you risk 10%, 3 losses = -27%. Small risk is what lets you reach the wins."),
    ("TP1: close half, move SL to entry",
     "After TP1 the rest of the trade cannot lose. Many 'wins' in our record are exactly this: half at TP1, half back at entry.\n"
     "Don't skip it to hold for TP2. The tested results assume you take TP1."),
    ("No signal is also a signal",
     "Most days the 4H breakout does not trigger. The bot stays quiet because the tested edge is not there.\n"
     "Forcing a trade on a quiet day is where most accounts lose money."),
    ("The 4H breakout in one line",
     "When a 4H candle closes above the highest price of the past week (30 candles), buy. Below the lowest, sell.\n"
     "Big moves start with a breakout. Tested on 2 years of spot gold: 169 trades, 69% profitable."),
    ("Volume profile: P, b and D",
     "P shape = most volume at the top of the session: buyers won. b shape = at the bottom: sellers won. D = balanced.\n"
     "Our 🟡 plan trade buys a P pullback to the POC and sells a b pullback. D = no trade."),
    ("What the POC is",
     "POC (point of control) = the price where the most volume traded in a session. It is where the market agreed on value.\n"
     "Price often comes back to test it. That retest is where the 🟡 plan trade enters."),
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
     "Gold closes Friday 17:00 New York and reopens Sunday 18:00. Price can open far from Friday's close.\n"
     "A stop does not protect you inside a gap. Holding over the weekend is extra risk."),
    ("Keep a simple journal",
     "Write: date, buy/sell, entry, SL, TP, result, and one line on how you felt.\n"
     "After 20 trades you will see your own mistakes clearly. Most of them repeat."),
    ("The plan before the trade",
     "Before entering, know three numbers: entry, where you are wrong (SL), where you take profit (TP).\n"
     "If you can't say all three, it isn't a trade yet. Every signal here gives you all three."),
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
    if send(f"📘 <b>Lesson · {title}</b>\n\n{body}", "Lesson") or not os.environ.get("TELEGRAM_TOKEN"):
        json.dump({"next": i + 1, "day": day}, open(STATE, "w"))
        print("lesson sent", i, title)


if __name__ == "__main__":
    main()
