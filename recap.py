"""Trade recap lesson: when a signal closes, post what happened and the lesson in 📚 Education.

Basic English + Khmer. Every trade, win or loss, becomes a short lesson, so members learn the system from real trades.
Called from track.py right after the result reply.
"""
from datetime import datetime, timezone

from tg import fmt, local, msg_link, send

KIND = {"scalp": "🤬 scalp", "model": "4H breakout", "plan": "Plan setup 🤬", "post-news": "After-news setup", "late": "Late plan"}


def _pips(a, px):
    return (px - a["entry"]) * (1 if a["dir"] == "bull" else -1) * 10


def _lesson(a):
    s, R = a["status"], a.get("R") or 0
    tier = a.get("tier") or ""
    if s == "win":
        return ("We let the winner run. TP1 locked half the profit, the rest went to TP2. Patience paid.",
                "យើងទុកឱ្យការជួញដូរឈ្នះដើរ។ TP1 ការពារចំណេញពាក់កណ្ដាល ហើយនៅសល់ទៅដល់ TP2។ ការអត់ធ្មត់ផ្ដល់ផល។")
    if s == "tp1":
        return ("TP1 paid, then price came back to entry. This is why we close half at TP1 and move SL to entry: "
                "the trade still ends in profit, with no stress.",
                "TP1 ចំណេញហើយ បន្ទាប់មកតម្លៃត្រលប់មកចំណុចចូល។ នេះហើយជាហេតុដែលយើងបិទពាក់កណ្ដាលនៅ TP1 "
                "ហើយប្ដូរ SL មកចំណុចចូល: នៅតែចំណេញ គ្មានស្ត្រេស។")
    if s == "loss":
        extra = (" It was a quiet day (low Day Meter): these fail more, that is why the size was half." if "normal" in tier else "")
        return ("A loss is part of the plan. In the 2-year test about 1 in 3 breakouts lose. We lost only 1R because the "
                "stop was fixed. Do not revenge trade: the next signal is a new trade." + extra,
                "ការខាតគឺជាផ្នែកមួយនៃផែនការ។ ក្នុងការសាកល្បង 2 ឆ្នាំ ប្រហែល 1 ក្នុង 3 ខាត។ យើងខាតតែ 1R ព្រោះ SL ច្បាស់។ "
                "កុំសងសឹកទីផ្សារ: សញ្ញាបន្ទាប់ជាការជួញដូរថ្មី។")
    if s == "timed out":
        return ("Time limit reached, so we closed it. Intraday trades do not stay open overnight: news can jump the price.",
                "ដល់ពេលកំណត់ ដូច្នេះបិទ។ ការជួញដូរក្នុងថ្ងៃ មិនទុកពេលយប់ទេ: ព័ត៌មានអាចធ្វើឱ្យតម្លៃលោត។")
    if s in ("expired", "missed"):
        return ("Price never gave our entry, so there was no trade. Never chase a price that left without you.",
                "តម្លៃមិនមកដល់ចំណុចចូល ដូច្នេះគ្មានការជួញដូរ។ កុំដេញតាមតម្លៃដែលរត់ចេញ។")
    return None


def post(a, summary=None):
    les = _lesson(a)
    if not les:
        return None
    s = a["status"]
    bull = a["dir"] == "bull"
    side = "BUY" if bull else "SELL"
    icon = {"win": "🏆", "tp1": "✅", "loss": "❌", "timed out": "⏱", "expired": "⚪", "missed": "⚪"}.get(s, "•")
    exit_px = a["target"] if s == "win" else a.get("exit")
    res = (f"{_pips(a, exit_px):+,.0f} pips" if exit_px is not None and s in ("win", "loss", "timed out") else
           f"TP1 {_pips(a, a['tp1']):+,.0f} pips, rest at entry" if s == "tp1" and a.get("tp1") else "no trade")
    lines = [f"📚 <b>TRADE RECAP · {side} {fmt(a['entry'])} → {icon} {res}</b>",
             f"{KIND.get(a.get('kind'), 'Signal')} · opened {local(a['created'])}" + (f" · R {a['R']:+.2f}" if a.get("R") is not None else ""),
             "",
             "<b>What happened · អ្វីបានកើតឡើង</b>",
             f"• Entry {fmt(a['entry'])} · SL {fmt(a['stop'])}" + (f" · TP1 {fmt(a['tp1'])}" if a.get("tp1") else "")
             + f" · TP2 {fmt(a['target'])}"]
    if a.get("hit1"):
        lines.append("• TP1 hit → half closed, SL moved to entry ✅")
    lines.append({"win": "• TP2 hit 🏆", "tp1": "• Price came back to entry → rest closed at 0", "loss": "• SL hit ❌",
                  "timed out": "• Time limit → closed", "expired": "• Entry never came", "missed": "• Price left without us"}[s])
    lines += ["", "<b>Lesson · មេរៀន</b>", les[0], f"<i>{les[1]}</i>"]
    if summary and summary.get("traded"):
        lines += ["", f"📊 Record so far: {summary['wins']} win{'s' if summary['wins'] != 1 else ''} · {summary['losses']} loss{'es' if summary['losses'] != 1 else ''} · total {summary.get('total_R', 0):+.1f}R"]
    link = msg_link(a.get("msg_id"), "Result")
    if link:
        lines.append(f'👉 <a href="{link}">See the signal</a>')
    return send("\n".join(lines), "Lesson")
