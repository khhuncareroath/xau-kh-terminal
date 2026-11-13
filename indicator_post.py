"""📈 Posts the XAU.KH FLOW indicator topic ONCE (owner, 13 Nov 2026): creates the "Indicator · ឧបករណ៍" topic (left
open so members can post feedback), sends posts 1-7 (indicator/posts.py), pins post 1, uploads the guide PDF and the
.pine file. State in indicator_state.json (committed by loop.py), so it never posts twice.
When indicator/link.txt holds the TradingView link, Post 2 is edited once to include it.
INDICATOR_POST=off stops it.  Run: python indicator_post.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indicator import posts as P   # noqa: E402

STATE = "indicator_state.json"
TITLE = "indicator"


def load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save(st):
    json.dump(st, open(STATE, "w"), indent=1)


def link():
    try:
        s = open("indicator/link.txt").read().strip()
        return s if s.startswith("http") else None
    except Exception:
        return None


def main():
    if os.environ.get("INDICATOR_POST", "on") == "off":
        print("indicator: off"); return
    import tg
    if not (os.environ.get("TELEGRAM_TOKEN") and tg.group_id()):
        print("indicator: no Telegram group/secrets"); return
    st = load()
    st.setdefault("posts", {})
    lk = link()
    # 1) posts 1-7, one per cycle step, resumable if something fails half way
    for i in range(len(P.POSTS)):
        k = str(i + 1)
        if k in st["posts"]:
            continue
        res = tg._send_tg("sendMessage", TITLE, {"text": P.post(i, lk), "parse_mode": "HTML",
                                                  "disable_web_page_preview": "true",
                                                  "disable_notification": "true" if i else "false"})
        mid = (res or {}).get("message_id")
        if not mid:
            print("indicator: post", k, "failed"); save(st); return
        st["posts"][k] = mid
        if lk and i == 1:
            st["link_done"] = lk
        save(st)
        print("indicator: post", k, mid)
    # 2) pin post 1
    if not st.get("pinned"):
        try:
            chat, _ = tg.target(TITLE)
            tg._api("pinChatMessage", {"chat_id": chat, "message_id": st["posts"]["1"], "disable_notification": "true"})
            st["pinned"] = True
        except Exception as e:
            print("indicator: pin failed (give the bot 'Pin messages'):", e)
            st["pinned"] = "failed"
        save(st)
    # 3) the files
    for key, path, cap in (("pdf", "indicator/XAU_KH_FLOW_Guide.pdf", P.PDF_CAPTION),
                           ("pine", "indicator/XAU_KH_FLOW_public.pine", P.PINE_CAPTION)):
        if st.get(key):
            continue
        mid = tg.send_document(path, cap, TITLE, filename=os.path.basename(path))
        if not mid:
            print("indicator: upload failed", path); save(st); return
        st[key] = mid
        save(st)
        print("indicator: uploaded", path, mid)
    # 4) the TradingView link, once it exists
    if lk and st.get("link_done") != lk:
        try:
            chat, _ = tg.target(TITLE)
            tg._api("editMessageText", {"chat_id": chat, "message_id": st["posts"]["2"], "text": P.post(1, lk),
                                        "parse_mode": "HTML", "disable_web_page_preview": "true"})
            st["link_done"] = lk
            save(st)
            print("indicator: link added to post 2")
        except Exception as e:
            print("indicator: link edit failed:", e)


if __name__ == "__main__":
    main()
