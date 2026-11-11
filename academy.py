"""📚 XAU.KH Academy: one lesson a day in Education, in the owner's 45-chapter order (academy_content.py).

Each lesson: the text (Khmer-first, English terms), for chart chapters today's real analysis picture ("find it on
today's chart"), then a Telegram quiz poll (tap an answer, see right away if it is right).
Posted once a day at HOUR local time on weekdays. State: academy_state.json (next lesson).  Run every cycle.
"""
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from academy_content import LESSONS
from tg import _api, send, send_document, send_photo, target

TZ = ZoneInfo(os.environ.get("DISPLAY_TZ", "Asia/Phnom_Penh"))
HOUR = int(os.environ.get("ACADEMY_HOUR", 12))
STATE = "academy_state.json"
TOTAL = 45
CHART_HINT = {"structure": "📍 <b>On today's real chart</b>: find the <b>HH / HL / LH / LL</b> labels and the <b>CHOCH / BOS</b> line.\n"
                           "📍 <b>លើ chart ថ្ងៃនេះ</b>: រក HH HL LH LL និង CHOCH / BOS",
              "liquidity": "📍 <b>On today's chart</b>: find <b>ELQ</b> (range edges), <b>ILQ</b> (orange) and <b>$$</b> (sweeps).\n"
                           "📍 រក ELQ, ILQ និង $$ លើ chart ថ្ងៃនេះ",
              "fvg": "📍 <b>On today's chart</b>: the green/red shaded boxes marked <b>FVG</b> and the <b>OB</b> box.\n📍 រក FVG និង OB",
              "pd": "📍 <b>On today's chart</b>: the <b>EQ 50%</b> line splits premium (above) and discount (below).\n📍 រក EQ 50%",
              "vp": "📍 <b>On today's chart</b>: the blue bars on the right = volume profile, <b>POC</b> = busiest price.\n📍 រក POC"}


PDF_DIR = "academy_pdfs"


def pdf_path(ch):
    """The full-lesson PDF for a chapter, if it has been written yet."""
    p = os.path.join(PDF_DIR, f"ch{ch:02d}.pdf")
    return p if os.path.exists(p) else None


def pdf_name(L):
    return f"XAUKH_Academy_Ch{L['ch']:02d}.pdf"


PDF_CAPTION = ("📖 <b>មេរៀនពេញ · Full lesson (PDF)</b>\nChapter {ch}: {t}\n"
               "ចុចបើក អានលើទូរស័ព្ទបាន · Tap to open")


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def header(L):
    done = round(10 * L["ch"] / TOTAL)
    return (f"📚 <b>XAU.KH ACADEMY</b> · {L['part']}\n{'▰' * done}{'▱' * (10 - done)} Chapter {L['ch']}/{TOTAL}\n\n"
            f"<b>{L['title']}</b>\n\n")


def text(L):
    """The lesson as one message (used by /lesson N)."""
    q, opts, ok, why = L["quiz"]
    return (header(L) + L["body"] + f"\n\n🧠 <b>Quiz</b>: {q}\n" + "\n".join(f"{'ABCD'[i]}. {o}" for i, o in enumerate(opts))
            + f"\n<tg-spoiler>✅ {'ABCD'[ok]}: {why}</tg-spoiler>\n\n<i>/academy = all chapters · /lesson {L['ch'] + 1} = next</i>")


def contents():
    out = ["📚 <b>XAU.KH ACADEMY · 45 Chapters</b>", "Type <b>/lesson N</b> to open a chapter · វាយ /lesson លេខ · 📖 = PDF", ""]
    part = None
    for L in LESSONS:
        if L["part"] != part:
            part = L["part"]
            out.append(f"\n<b>{part}</b>")
        out.append(f"{L['ch']}. {L['title'].split(' · ')[0]}" + (" 📖" if pdf_path(L["ch"]) else ""))
    return "\n".join(out)


def post(k):
    L = LESSONS[k]
    head = header(L)
    pdf = pdf_path(L["ch"])
    foot = ("📖 PDF មេរៀនពេញនៅខាងក្រោម ↓ · Quiz ↓" if pdf else "Quiz below ↓") + " · មេរៀនបន្ទាប់ថ្ងៃស្អែក · /check ដើម្បីអនុវត្ត"
    mid = send(head + L["body"] + f"\n\n<i>{foot}</i>", "Lesson")
    if not mid:
        return False
    if pdf:
        send_document(pdf, PDF_CAPTION.format(ch=L["ch"], t=L["title"]), "Lesson",
                      reply_to=mid if isinstance(mid, int) else None, filename=pdf_name(L))
    elif L.get("chart"):
        try:
            import session
            from engine import load
            from levels import to_ny
            df = to_ny(load("5m", "20d")).iloc[:-1]
            path = session.analysis_chart(df, jl("levels.json", {}), {}, session.breakout_lines(df), "academy_chart.png",
                                          f"Academy · Chapter {L['ch']} · today's chart")
            send_photo(path, CHART_HINT.get(L["chart"], ""), "Lesson", reply_to=mid if isinstance(mid, int) else None)
        except Exception as e:
            print("academy chart failed:", e)
    q, opts, ok, why = L["quiz"]
    try:
        chat, th = target("Lesson")
        f = {"chat_id": chat, "question": f"🧠 Quiz · Ch.{L['ch']}: {q}"[:300],
             "options": json.dumps([{"text": o[:100]} for o in opts], ensure_ascii=False),
             "type": "quiz", "correct_option_id": ok, "is_anonymous": "true",
             "explanation": why[:200], "explanation_parse_mode": "HTML"}
        if th:
            f["message_thread_id"] = th
        _api("sendPoll", f)
    except Exception as e:
        print("academy quiz failed:", e)
    return True


def main():
    now = datetime.now(TZ)
    st = jl(STATE, {"next": 0})
    today = now.strftime("%Y-%m-%d")
    force = os.environ.get("ACADEMY_FORCE")
    launch = "day" not in st          # very first lesson: post right away, then daily at HOUR
    if not force and not launch and (now.weekday() >= 5 or now.hour != HOUR or st.get("day") == today):
        print("academy: not now"); return
    k = st.get("next", 0)
    if k >= len(LESSONS):
        print("academy: waiting for the next chapters"); return
    if post(k):
        json.dump({"next": k + 1, "day": today, "t": time.time()}, open(STATE, "w"))
        print("academy: posted chapter", LESSONS[k]["ch"])


if __name__ == "__main__":
    main()
