"""Breaking news that moves gold, in Khmer, with an impact picture. Runs every cycle, works every 15 minutes.

1. Reads free headline feeds (Google News searches + ForexLive), keeps only new headlines that pass a keyword
   filter for gold / Fed / dollar / war / tariffs / elections / central banks.
2. One AI call (claude-haiku, budget-capped) rates them; only importance 4-5 for gold or USD is kept. Scheduled data
   releases (CPI, NFP...) are skipped: postnews.py covers those with real price reactions.
3. Posts a picture card (BREAKING · gold impact BULLISH/BEARISH/MIXED) with a Khmer caption: what happened, the
   market impact, and a short-term note. Max 6 posts a day, 20 minutes apart (importance 5 can break the gap).
Needs GEMINI_API_KEY (free tier, Google AI Studio) or ANTHROPIC_API_KEY; without either nothing is sent. The AI only explains news; it never gives a trade."""
import hashlib
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from tg import esc, local, send, send_photo

STATE = "breaking_state.json"
MODEL = os.environ.get("AI_MODEL", "claude-haiku-5-5")
CHECK_EVERY = 15 * 60
MAX_POSTS, MIN_GAP, MAX_AI = 6, 20 * 60, 30
Q = ["gold price", "Federal Reserve OR Powell OR FOMC", "US dollar OR Treasury yields", "tariffs OR trade war",
     "war OR missile OR ceasefire OR sanctions", "central bank gold buying", "US election OR Congress OR government shutdown"]
FEEDS = [f"https://news.google.com/rss/search?q={urllib.parse.quote(q + ' when:2h')}&hl=en-US&gl=US&ceid=US:en" for q in Q] + \
        ["https://www.forexlive.com/feed/news"]
KEYS = re.compile(r"\b(gold|bullion|fed|fomc|powell|rate cut|rate hike|dollar|treasur|yield|tariff|trade war|war|missile|attack|"
                  r"ceasefire|sanction|nuclear|election|congress|senate|shutdown|default|central bank|pboc|ecb|boj|inflation|"
                  r"recession|bank failure|crisis|opec|oil)\b", re.I)
SKIP = re.compile(r"\b(cpi|ppi|pce|nonfarm|non-farm|payrolls|jobless claims|gdp|pmi|retail sales|jolts)\b.*\b(rose|fell|came in|"
                  r"actual|vs|versus|expected|forecast)\b", re.I)

SYSTEM = """You select and explain breaking news for XAU.KH, a Cambodian gold (XAUUSD) trading channel.
From the headlines, keep ONLY news that can move gold or the US dollar strongly today: Fed/central-bank surprises,
war or geopolitical escalation/de-escalation, election or government results, tariffs/trade war, banking/financial
stress, big central-bank gold buying. Skip routine data releases (CPI, NFP, GDP...), opinion pieces, price-recap
articles ("gold rises 1%"), and anything older or minor. Usually keep 0 items; at most 2.
For each kept item return JSON fields:
 "id" (the given id), "importance" (4 or 5; 5 = market-shaking),
 "gold" ("bullish" | "bearish" | "mixed"), "usd" ("up" | "down" | "mixed"),
 "headline_en" (max 12 words, factual),
 "km_what" (1-2 short Khmer sentences: what happened; keep key English terms in brackets, e.g. (Fed), (Tariffs)),
 "km_impact" (1-2 short Khmer sentences: why it moves gold, e.g. safe-haven demand (Safe-Haven), weaker USD, rate-cut hopes),
 "km_short" (1 short Khmer sentence: short-term note, e.g. a quick dip first (Sell the news), or volatility),
 "en_short" (max 10 words, same short-term note in English).
Facts only from the headline. Never invent numbers, never give a trade or price target. Answer with a JSON array only."""


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def fetch():
    items = []
    for url in FEEDS:
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15).read()
            root = ET.fromstring(raw)
            for it in root.iter("item"):
                t = html.unescape((it.findtext("title") or "").strip())
                src = (it.findtext("source") or "").strip() or ("ForexLive" if "forexlive" in url else "")
                if t:
                    items.append({"title": re.sub(r"\s+-\s+[^-]{2,40}$", "", t) if "news.google" in url else t, "source": src})
        except Exception as e:
            print("feed failed:", url[:60], e)
    return items


GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def ask_ai(cands, gold, key):
    """key = ("anthropic", k) or ("gemini", k). Gemini has a free tier (Google AI Studio key, no card needed)."""
    lst = "\n".join(f"{i}. {c['title']} ({c['source']})" for i, c in enumerate(cands))
    prompt = f"Gold now: {gold}\nHeadlines (newest first):\n{lst}"
    kind, k = key
    if kind == "anthropic":
        body = {"model": MODEL, "max_tokens": 900, "system": SYSTEM, "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                     headers={"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=40))
        txt = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
    else:
        body = {"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500, "responseMimeType": "application/json"}}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={urllib.parse.quote(k)}"
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=40))
        txt = "".join(p_.get("text", "") for c in r.get("candidates", []) for p_ in c.get("content", {}).get("parts", []))
    m = re.search(r"\[.*\]", txt, re.S)
    return json.loads(m.group(0)) if m else []


def card(item, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import textwrap
    plt.rcParams["font.family"] = "DejaVu Sans"
    BG, CARD, INK, MUT, UP, DN, GOLD, RED = "#0B0B0D", "#1C1C1E", "#F5F5F7", "#8E8E93", "#30D158", "#FF453A", "#E3B04B", "#FF3B30"
    g = item.get("gold", "mixed")
    col, arrow, word = (UP, "↑", "BULLISH") if g == "bullish" else (DN, "↓", "BEARISH") if g == "bearish" else (GOLD, "↔", "MIXED")
    u = item.get("usd", "mixed")
    fig = plt.figure(figsize=(9, 5), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.05, 0.84), 0.2, 0.09, boxstyle="round,pad=0,rounding_size=0.02", fc=RED, ec="none"))
    ax.text(0.15, 0.885, "BREAKING", color="white", fontsize=14, fontweight="bold", ha="center", va="center")
    ax.text(0.95, 0.885, f"{item.get('source', '')}  ·  {local(time.time())}", color=MUT, fontsize=9, ha="right", va="center")
    ax.text(0.05, 0.70, "\n".join(textwrap.wrap(item.get("headline_en", ""), 44)[:3]), color=INK, fontsize=17, fontweight="bold", va="top")
    ax.add_patch(FancyBboxPatch((0.05, 0.13), 0.42, 0.22, boxstyle="round,pad=0,rounding_size=0.03", fc=col, alpha=0.16, ec="none"))
    ax.text(0.08, 0.30, "Gold impact", color=MUT, fontsize=10, va="center")
    ax.text(0.08, 0.20, f"{word} {arrow}", color=col, fontsize=24, fontweight="bold", va="center")
    ax.add_patch(FancyBboxPatch((0.50, 0.13), 0.45, 0.22, boxstyle="round,pad=0,rounding_size=0.03", fc=CARD, ec="none"))
    ax.text(0.53, 0.30, f"US dollar: {'↑ up' if u == 'up' else '↓ down' if u == 'down' else '↔ mixed'}", color=INK, fontsize=11, va="center")
    ax.text(0.53, 0.21, "\n".join(textwrap.wrap("Short-term: " + item.get("en_short", ""), 38)[:2]), color=MUT, fontsize=9.5, va="center")
    ax.text(0.05, 0.05, "XAU.KH · news explained, not a trade signal", color=MUT, fontsize=8)
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path


def main():
    key = (("anthropic", os.environ["ANTHROPIC_API_KEY"]) if os.environ.get("ANTHROPIC_API_KEY") else
           ("gemini", os.environ["GEMINI_API_KEY"]) if os.environ.get("GEMINI_API_KEY") else None)
    st = jl(STATE, {})
    now = time.time()
    if not key or now - st.get("checked", 0) < CHECK_EVERY:
        if not key:
            print("breaking news off (add the GEMINI_API_KEY secret (free) or ANTHROPIC_API_KEY)")
        return
    st["checked"] = now
    day = time.strftime("%Y-%m-%d", time.gmtime())
    if st.get("day") != day:
        st.update(day=day, posts=0, ai=0)
    seen = set(st.get("seen", []))
    new = []
    for it in fetch():
        h = hashlib.md5(it["title"].lower().encode()).hexdigest()[:12]
        if h in seen:
            continue
        seen.add(h)
        if KEYS.search(it["title"]) and not SKIP.search(it["title"]):
            new.append(it)
    st["seen"] = list(seen)[-1500:]
    if not st.get("primed"):              # first run: remember what is out there, post nothing old
        st["primed"] = True
        json.dump(st, open(STATE, "w")); print("breaking: primed with", len(seen), "headlines"); return
    if not new or st["ai"] >= MAX_AI or st["posts"] >= MAX_POSTS:
        json.dump(st, open(STATE, "w")); print(f"breaking: {len(new)} candidates, nothing to do"); return
    gold = jl("ict.json", {}).get("price")
    try:
        picks = ask_ai(new[:15], gold, key)
        st["ai"] += 1
    except Exception as e:
        print("breaking AI failed:", e); json.dump(st, open(STATE, "w")); return
    for p in sorted(picks, key=lambda x: -int(x.get("importance", 0))):
        if int(p.get("importance", 0)) < 4 or st["posts"] >= MAX_POSTS:
            continue
        if now - st.get("last_post", 0) < MIN_GAP and int(p.get("importance", 0)) < 5:
            continue
        try:
            src = new[int(p["id"])]["source"]
        except Exception:
            src = ""
        p["source"] = src
        g = p.get("gold", "mixed")
        tag = "📈 Bullish (ឡើង)" if g == "bullish" else "📉 Bearish (ចុះ)" if g == "bearish" else "↔️ Mixed (មិនច្បាស់)"
        cap = "\n".join([f"🚨 <b>ព័ត៌មានបន្ទាន់ (BREAKING)</b>", "", esc(p.get("km_what", "")), "",
                         f"<b>ឥទ្ធិពលលើមាស (Market Impact): {tag}</b>", esc(p.get("km_impact", "")), "",
                         f"⏱ <b>រយៈពេលខ្លី (Short-term):</b> {esc(p.get('km_short', ''))}", "",
                         "<i>ព័ត៌មានពន្យល់ មិនមែនសញ្ញាជួញដូរទេ · News explained, not a signal</i>"])
        try:
            ok = send_photo(card(p, "breaking_card.png"), cap[:1024], "Breaking")
        except Exception as e:
            print("breaking card failed:", e)
            ok = send(cap, "Breaking")
        if ok:
            st["posts"] += 1
            st["last_post"] = now
            print("breaking sent:", p.get("headline_en"))
    json.dump(st, open(STATE, "w"))


if __name__ == "__main__":
    main()
