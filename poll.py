"""One-time member feedback poll in the group's General topic.

Posts an anonymous multiple-choice poll once, closes it after POLL_HOURS and saves the vote counts to
poll_state.json (committed with the other json files), so the next improvements follow what members ask for.
Change POLL_ID to run a new poll.  Run every cycle:  python poll.py
"""
import json
import os
import time

from tg import _api, group_id

POLL_ID = "fix-first-2026-11"
POLL_HOURS = 24
QUESTION = "What should XAU.KH fix first? · XAU.KH គួរកែអ្វីមុនគេ?"
OPTIONS = [
    "Too many messages · សារច្រើនពេក",
    "Signals lose / come late · សញ្ញាខាត ឬយឺត",
    "SL too big · SL ធំពេក",
    "Hard to understand, want Khmer · ពិបាកយល់ ចង់បានខ្មែរ",
    "Want more signals per day · ចង់បានសញ្ញាច្រើន",
    "Want lessons / how to trade · ចង់រៀន",
    "Website not useful · វេបសាយមិនមានប្រយោជន៍",
]
STATE = "poll_state.json"


def main():
    g = group_id()
    if not (g and os.environ.get("TELEGRAM_TOKEN")):
        print("poll: no group"); return
    try:
        st = json.load(open(STATE))
    except Exception:
        st = {}
    if st.get("id") != POLL_ID:
        res = _api("sendPoll", {"chat_id": g, "question": QUESTION, "options": json.dumps([{"text": o} for o in OPTIONS], ensure_ascii=False),
                                "is_anonymous": "true", "allows_multiple_answers": "true"})
        st = {"id": POLL_ID, "msg_id": res["message_id"], "t": time.time(), "closed": False}
        json.dump(st, open(STATE, "w"), indent=1, ensure_ascii=False)
        print("poll: posted"); return
    if st.get("closed") or time.time() - st["t"] < POLL_HOURS * 3600:
        print("poll: running" if not st.get("closed") else "poll: done"); return
    res = _api("stopPoll", {"chat_id": g, "message_id": st["msg_id"]})
    st["closed"] = True
    st["total"] = res.get("total_voter_count")
    st["results"] = sorted([(o["text"], o["voter_count"]) for o in res.get("options", [])], key=lambda x: -x[1])
    json.dump(st, open(STATE, "w"), indent=1, ensure_ascii=False)
    owner = os.environ.get("TELEGRAM_OWNER_CHAT_ID")
    if owner:
        _api("sendMessage", {"chat_id": owner, "text": "📊 Poll results (" + str(st["total"]) + " voters):\n"
                             + "\n".join(f"{v} · {t}" for t, v in st["results"])})
    print("poll: closed", st["results"])


if __name__ == "__main__":
    main()
