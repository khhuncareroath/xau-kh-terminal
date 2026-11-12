"""Breaking news that moves gold, in Khmer, with an impact picture. Runs every cycle, works every 15 minutes.

1. Reads free headline feeds (Google News searches + ForexLive), keeps only new headlines that pass a keyword
   filter for gold / Fed / dollar / war / tariffs / elections / central banks.
2. One AI call (claude-haiku, budget-capped) rates them; only importance 4-5 for gold or USD is kept. Scheduled data
   releases (CPI, NFP...) are skipped: postnews.py covers those with real price reactions.
3. Posts a picture card (BREAKING · gold impact BULLISH/BEARISH/MIXED) with a Khmer caption: what happened, the
   market impact, and a short-term note. Max 6 posts a day, 20 minutes apart (importance 5 can break the gap).
4. ⚡ BIG MOVE (12 Nov 2026, after Trump's "no deal with Iran" post dropped gold ~$40 with no post): every cycle, if gold
   moved 3x its normal hourly range in the last hour ($20+, not around a scheduled release), post the move with the
   headlines of the last 2 h that could explain it. For 2 h after that, a big-power headline may go past the daily cap
   (hard max 5 a day). BIG_MOVE=off stops it.
With ANTHROPIC_API_KEY or GEMINI_API_KEY the AI explains in Khmer; without a key a free rules mode posts only clear
news types (Fed cut/hike, war, ceasefire, tariffs, trade deal, central-bank gold, crisis, election) from trusted sources. The AI only explains news; it never gives a trade."""
import hashlib
import html
import json
import os
import re
import time
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from tg import esc, local, send, send_photo

STATE = "breaking_state.json"
MODEL = os.environ.get("AI_MODEL", "claude-haiku-5-5")
CHECK_EVERY = 15 * 60
MAX_POSTS, MIN_GAP, MAX_AI = 2, 3 * 3600, 30   # only the big ones: max 2 a day, 3 h apart
HARD_MAX = 5          # importance 5 (or news that comes with a big price move) may go past MAX_POSTS, never past this
# ⚡ BIG MOVE (12 Nov 2026): gold moved 3x its normal hourly range in the last hour (and $20+). 2 years of 5m: ~2.6 a week.
MOVE_X, MOVE_MIN_USD, MOVE_GAP, MOVE_LINK_S = 3.0, 20.0, 3 * 3600, 2 * 3600
Q = ["gold price", "Federal Reserve OR Powell OR FOMC", "US dollar OR Treasury yields", "tariffs OR trade war",
     "war OR missile OR ceasefire OR sanctions", "central bank gold buying", "US election OR Congress OR government shutdown",
     # 12 Nov 2026: Trump's "we don't need a deal with Iran" post dropped gold ~$40 and was missed (no Trump / Iran query)
     "Trump says OR Trump Truth Social OR Trump posts", "Iran OR Israel OR Russia OR China talks OR deal OR strikes"]
FEEDS = [f"https://news.google.com/rss/search?q={urllib.parse.quote(q + ' when:2h')}&hl=en-US&gl=US&ceid=US:en" for q in Q] + \
        ["https://www.forexlive.com/feed/news"]
KEYS = re.compile(r"\b(trump|white house|iran|israel|russia|putin|china|deal|talks|strikes?|gold|bullion|fed|fomc|powell|rate cut|rate hike|dollar|treasur|yield|tariff|trade war|war|missile|attack|"
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
                t = html.unescape((it.findtext("title") or "").strip()).replace("\u2019", "'").replace("\u2018", "'")
                src = (it.findtext("source") or "").strip() or ("ForexLive" if "forexlive" in url else "")
                if t:
                    items.append({"title": re.sub(r"\s+-\s+[^-]{2,40}$", "", t) if "news.google" in url else t, "source": src})
        except Exception as e:
            print("feed failed:", url[:60], e)
    return items


GEMINI_MODEL = os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash-lite"
# free-tier models in Oct 2026 (2.5 Flash is no longer free; Plus / Advanced app subscriptions do NOT include the API)
GEMINI_FALLBACK = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-flash-latest"]


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
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4000, "responseMimeType": "application/json"}}
        txt, errs = "", []
        for mdl in dict.fromkeys([GEMINI_MODEL] + GEMINI_FALLBACK):   # old ids get retired from the free tier: try the next
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={urllib.parse.quote(k)}"
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
            try:
                r = json.load(urllib.request.urlopen(req, timeout=40))
            except urllib.error.HTTPError as e:
                errs.append(f"{mdl}: HTTP {e.code} {e.read()[:160]!r}")
                if e.code in (400, 403, 404, 429):
                    continue
                raise
            txt = "".join(p_.get("text", "") for c in r.get("candidates", []) for p_ in c.get("content", {}).get("parts", [])
                          if not p_.get("thought"))
            print("breaking AI model:", mdl)
            break
        if not txt and errs:
            raise RuntimeError("Gemini failed: " + " | ".join(errs))
    m = re.search(r"\[.*\]", txt, re.S)
    return json.loads(m.group(0)) if m else []


def card(item, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import textwrap
    plt.rcParams["font.family"] = "DejaVu Sans"
    try:
        from signal_card import _fonts
        plt.rcParams["font.family"] = _fonts()
    except Exception:
        pass
    BG, CARD, INK, MUT, UP, DN, GOLD, RED = "#F2F2F7", "#FFFFFF", "#1C1C1E", "#8E8E93", "#34C759", "#FF3B30", "#C9971C", "#FF3B30"
    g = item.get("gold", "mixed")
    col, arrow, word = (UP, "↑", "BULLISH") if g == "bullish" else (DN, "↓", "BEARISH") if g == "bearish" else (GOLD, "↔", "MIXED")
    u = item.get("usd", "mixed")
    fig = plt.figure(figsize=(9, 5), dpi=150); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.05, 0.84), 0.2, 0.09, boxstyle="round,pad=0,rounding_size=0.02", fc=RED, ec="none"))
    ax.text(0.15, 0.885, item.get("badge", "BREAKING"), color="white", fontsize=14, fontweight="bold", ha="center", va="center")
    ax.text(0.95, 0.885, f"{item.get('source', '')}  ·  {local(time.time())}", color=MUT, fontsize=9, ha="right", va="center")
    ax.text(0.05, 0.70, "\n".join(textwrap.wrap(item.get("headline_en", ""), 44)[:3]), color=INK, fontsize=17, fontweight="bold", va="top")
    ax.add_patch(FancyBboxPatch((0.05, 0.13), 0.42, 0.22, boxstyle="round,pad=0,rounding_size=0.03", fc=col, alpha=0.16, ec="none"))
    ax.text(0.08, 0.30, "Gold impact", color=MUT, fontsize=10, va="center")
    ax.text(0.08, 0.20, f"{word} {arrow}", color=col, fontsize=24, fontweight="bold", va="center")
    ax.add_patch(FancyBboxPatch((0.50, 0.13), 0.45, 0.22, boxstyle="round,pad=0,rounding_size=0.03", fc=CARD, ec="none"))
    if item.get("box"):     # ⚡ BIG MOVE card: the likely reason instead of the dollar line
        ax.text(0.53, 0.30, item.get("box_title", "Likely reason"), color=MUT, fontsize=10, va="center")
        ax.text(0.53, 0.20, "\n".join(textwrap.wrap(item["box"], 40)[:3]), color=INK, fontsize=10, va="center")
    else:
        ax.text(0.53, 0.30, f"US dollar: {'↑ up' if u == 'up' else '↓ down' if u == 'down' else '↔ mixed'}", color=INK, fontsize=11, va="center")
        ax.text(0.53, 0.21, "\n".join(textwrap.wrap("Short-term: " + item.get("en_short", ""), 38)[:2]), color=MUT, fontsize=9.5, va="center")
    ax.text(0.05, 0.05, "XAU.KH · news explained, not a trade signal", color=MUT, fontsize=8)
    fig.savefig(path, facecolor=BG); plt.close(fig)
    return path


# ---- free mode: no AI. Only clear news types with a well-known effect on gold, from trusted sources ----
TRUSTED = re.compile(r"reuters|bloomberg|associated press|\bap\b|cnbc|wall street journal|wsj|financial times|forexlive|"
                     r"marketwatch|bbc|cnn|nikkei|kitco|fxstreet", re.I)
RULES = [   # (category, pattern, gold direction, Khmer reason)
    ("fed_dove", r"\b(fed|fomc|powell|federal reserve)\b.*\b(cuts? rates?|rate cut|cuts? interest|dovish|lowers rates?)\b|\b(rate cut|cuts rates?)\b.*\b(fed|fomc)\b",
     "bullish", "Fed បន្ថយការប្រាក់ (Rate cut) → ដុល្លារ (USD) ចុះ → មាសច្រើនតែឡើង"),
    ("fed_hawk", r"\b(fed|fomc|powell|federal reserve)\b.*\b(hikes? rates?|rate hike|raises rates?|hawkish)\b",
     "bearish", "Fed តឹងរ៉ឹង (Hawkish) → ដុល្លារ (USD) ឡើង → មាសច្រើនតែចុះ"),
    ("war", r"\b(missile|airstrikes?|strikes?(?!.{0,12}\bdeal)|struck|attacks?|invasion|invades|war escalat|declares war|bombing|military action)\b",
     "bullish", "ភាពតានតឹង/សង្គ្រាម → អ្នកវិនិយោគរកទ្រព្យសុវត្ថិភាព (Safe-Haven) → មាសច្រើនតែឡើង"),
    ("talks_off", r"\b(no deal|(don't|do not|doesn't|does not) need (a|any) deal|rejects? (a |the |any )?(deal|talks|offer)|"
     r"talks? (collapse|collapsed|fail|failed|break down|broke down|ended?|off)|walks? away|calls? off|won't negotiate|ends? talks)\b",
     "mixed", "គ្មានកិច្ចព្រមព្រៀង / ការចរចាបរាជ័យ → ភាពមិនប្រាកដ → មាសអាចប្រែប្រួលខ្លាំង (Volatility)"),
    ("peace", r"\b(ceasefire|cease-fire|truce|peace deal|peace agreement)\b",
     "bearish", "បទឈប់បាញ់ (Ceasefire) → ការភ័យខ្លាចថយចុះ → មាសអាចចុះ"),
    ("tariff", r"\b(new tariffs?|tariff hikes?|raises? tariffs?|imposes? tariffs?|trade war)\b",
     "bullish", "ពន្ធគយថ្មី (Tariffs) → ភាពមិនប្រាកដ → មាសច្រើនតែឡើង"),
    ("trade_deal", r"\b(trade deal|trade agreement|tariff (cut|pause|relief)|lifts? tariffs?|removes? tariffs?)\b",
     "bearish", "កិច្ចព្រមព្រៀងពាណិជ្ជកម្ម (Trade deal) → ការភ័យខ្លាចថយចុះ → មាសអាចចុះ"),
    ("cb_gold", r"\bcentral banks?\b.*\b(buy|bought|buying|add|added|adds|purchases?)\b.*\bgold\b",
     "bullish", "ធនាគារកណ្ដាលទិញមាស → តម្រូវការមាសកើនឡើង → ល្អសម្រាប់មាស"),
    ("crisis", r"\b(government shutdown|shutdown begins|debt default|defaults? on|bank (collapse|failure|run)|collapses?)\b",
     "bullish", "វិបត្តិ (Crisis) → អ្នកវិនិយោគរកទ្រព្យសុវត្ថិភាព (Safe-Haven) → មាសច្រើនតែឡើង"),
    ("election", r"\b(wins? (the )?(election|presidency|control of)|election results?|declared winner)\b",
     "mixed", "លទ្ធផលបោះឆ្នោត → ទីផ្សារអាចប្រែប្រួលខ្លាំង (Volatility)"),
]
RULES = [(k, re.compile(p_, re.I), g, km) for k, p_, g, km in RULES]
# war / peace / election / crisis headlines count only when they involve the powers that move gold (a regional
# conflict elsewhere rarely does), tariffs only between the big economies
MAJOR = re.compile(r"\b(u\.?s\.?|united states|america|american|washington|trump|white house|pentagon|russia|russian|"
                   r"putin|ukraine|kyiv|china|chinese|beijing|taiwan|iran|iranian|tehran|israel|israeli|gaza|hezbollah|"
                   r"north korea|nato|europe|eu)\b", re.I)
NEEDS_MAJOR = {"talks_off", "war", "peace", "election", "crisis", "tariff", "trade_deal"}
BROKEN = re.compile(r"\b(despite|violat\w*|breach\w*|collaps\w*|breaks?|broken|ends?)\b", re.I)
NEG = re.compile(r"\b(no|not|won't|wont|unlikely|rules? out|against|delay|delays|rush|patient|could|may|might|considers?|weighs?|expected|bets?|odds|\?)", re.I)


KM_WHAT = {
    "fed_dove": "ធនាគារកណ្ដាលអាមេរិក (Fed) បានបន្ថយអត្រាការប្រាក់ (Rate Cut)។",
    "fed_hawk": "ធនាគារកណ្ដាលអាមេរិក (Fed) បានដំឡើងអត្រាការប្រាក់ ឬបង្ហាញជំហរតឹងរ៉ឹង (Hawkish)។",
    "war": "មានការវាយប្រហារ ឬភាពតានតឹងយោធាថ្មី (Geopolitical Risk)។",
    "talks_off": "ការចរចាត្រូវបានបដិសេធ ឬបរាជ័យ (No Deal / Talks Collapse)។",
    "peace": "ភាគីពាក់ព័ន្ធបានព្រមព្រៀងឈប់បាញ់ (Ceasefire)។",
    "tariff": "មានការដាក់ពន្ធគយថ្មី (Tariffs) ឬសង្គ្រាមពាណិជ្ជកម្ម (Trade War)។",
    "trade_deal": "មានកិច្ចព្រមព្រៀងពាណិជ្ជកម្ម ឬការកាត់បន្ថយពន្ធគយ (Trade Deal)។",
    "cb_gold": "ធនាគារកណ្ដាលបានទិញមាសបន្ថែម (Central Bank Buying)។",
    "crisis": "មានវិបត្តិហិរញ្ញវត្ថុ ឬនយោបាយ (Crisis) ដូចជា Shutdown ឬធនាគារបរាជ័យ។",
    "election": "លទ្ធផលបោះឆ្នោតត្រូវបានប្រកាស (Election Result)។",
}
KM_SHORT = {
    "fed_dove": "ពេលប្រកាស តម្លៃអាចលោតឡើងចុះខ្លាំង មុនរកទិសដៅច្បាស់ (Volatility)។",
    "fed_hawk": "ពេលប្រកាស តម្លៃអាចលោតឡើងចុះខ្លាំង មុនរកទិសដៅច្បាស់ (Volatility)។",
    "war": "បើភាពតានតឹងធូរស្រាលវិញ មាសអាចធ្លាក់មកវិញលឿន។",
    "talks_off": "ទិសដៅមាសមិនច្បាស់ មើលប្រតិកម្មតម្លៃពិតមុនសម្រេចចិត្ត។",
    "peace": "ប្រសិនបើបទឈប់បាញ់បរាជ័យ មាសអាចឡើងវិញ។",
    "tariff": "ទីផ្សារអាចប្រតិកម្មខ្លាំងនៅម៉ោងដំបូង (Volatility)។",
    "trade_deal": "អាចមានការលក់មាសរយៈពេលខ្លី (Risk-on)។",
    "cb_gold": "ជាកត្តារយៈពេលវែង មិនមែនសញ្ញាចូលភ្លាមៗទេ។",
    "crisis": "តម្លៃអាចប្រែប្រួលខ្លាំង ប្រើ lot តូច។",
    "election": "ពេលខ្លះមានការធ្លាក់បន្តិចសិន (Sell the news) មុនរកទិសដៅ។",
}
KM_TAG = {"bullish": "📈 វិជ្ជមានសម្រាប់មាស (Bullish)", "bearish": "📉 អវិជ្ជមានសម្រាប់មាស (Bearish)",
          "mixed": "↔️ មិនទាន់ច្បាស់ (Mixed)"}


def rules_pick(cands, st):
    """Return list of items like the AI output, at most one per category every 6 hours."""
    out, now = [], time.time()
    last = st.setdefault("cat_last", {})
    for i, c in enumerate(cands):
        if not TRUSTED.search(c.get("source", "")):
            continue
        for k, rx, g, km in RULES:
            if k.startswith("fed") and NEG.search(c["title"]):
                continue                    # "no rush to cut", "won't hike": direction unclear without AI, skip
            if k in NEEDS_MAJOR and not MAJOR.search(c["title"]):
                continue
            if k == "peace" and BROKEN.search(c["title"]):
                continue                    # "strikes ... despite ceasefire" is a breach, not peace (12 Nov: wrongly BEARISH)
            if rx.search(c["title"]) and now - last.get(k, 0) > 12 * 3600 and k not in {o["_cat"] for o in out}:
                out.append({"id": i, "importance": 4, "gold": g, "usd": "mixed", "headline_en": c["title"][:110],
                            "km_reason": km, "en_short": "Expect fast moves around this news", "_cat": k})
                break
    return out


def scheduled_news_near(now, before=60, after=15):
    """A high-impact calendar release from `before` min ago to `after` min ahead: postnews.py covers those moves."""
    news = jl("news.json", {})
    from datetime import datetime
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        try:
            m = (datetime.fromisoformat(str(e["time"]).replace("Z", "+00:00")).timestamp() - now) / 60
        except Exception:
            continue
        if -before <= m <= after:
            return e.get("title", "news")
    return None


def big_move():
    """(sign, usd, from_price, now_price, minutes, normal_range) when the last 60 min moved >= MOVE_X x the median 60-min
    range of the 5 days before (and MOVE_MIN_USD+), else None. Closed 5m candles only."""
    import numpy as np
    from engine import closed, load
    df = load("5m", "10d")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = closed(df)
    h, l, c = (df[k].to_numpy(float) for k in ("High", "Low", "Close"))
    if len(c) < 600 or not os.environ.get("XAU_SIM") and df.index[-1] < __import__("pandas").Timestamp.now(tz="UTC") - __import__("pandas").Timedelta(minutes=20):
        return None
    w = 12
    rng = np.array([h[i - w:i].max() - l[i - w:i].min() for i in range(max(w, len(c) - 1452), len(c) - w)])
    norm = float(np.median(rng)) if len(rng) else 0.0
    hi_j, lo_j = int(np.argmax(h[-w:])), int(np.argmin(l[-w:]))
    down, up = h[-w:].max() - c[-1], c[-1] - l[-w:].min()
    mv = max(down, up)
    if norm <= 0 or mv < max(MOVE_MIN_USD, MOVE_X * norm):
        return None
    sg, j, frm = (-1, hi_j, h[-w:].max()) if down >= up else (1, lo_j, l[-w:].min())
    return sg, float(mv), float(frm), float(c[-1]), (w - j) * 5, norm


def move_post(st, now):
    """⚡ BIG MOVE: say what gold just did and which headlines could explain it. Runs every cycle (5 min)."""
    if now - st.get("move_t", 0) < MOVE_GAP or os.environ.get("BIG_MOVE", "on") == "off":
        return
    try:
        m = big_move()
    except Exception as e:
        print("big move check failed:", e); return
    if not m:
        return
    sg, mv, frm, px, mins, norm = m
    sched = scheduled_news_near(now)
    if sched:
        print("big move during scheduled news (postnews covers it):", sched); st["move_t"] = now; return
    # headlines of the last 2 hours: the ones kept by earlier cycles + a fresh read now
    recent = [x for x in st.get("recent", []) if now - x["t"] <= MOVE_LINK_S]
    try:
        have = {x["title"] for x in recent}
        recent += [{"title": it["title"], "source": it["source"], "t": now} for it in fetch()
                   if it["title"] not in have and KEYS.search(it["title"]) and not SKIP.search(it["title"])]
    except Exception as e:
        print("big move headlines failed:", e)
    score = lambda x: (2 if any(rx.search(x["title"]) for _, rx, _, _ in RULES) else 0) + (1 if MAJOR.search(x["title"]) else 0) + \
        (1 if TRUSTED.search(x.get("source", "")) else 0)
    why = sorted([x for x in recent if score(x) >= 2], key=lambda x: (-score(x), -x["t"]))[:2]
    word, km = ("rose", "ឡើង") if sg > 0 else ("fell", "ធ្លាក់")
    fmt = lambda v: f"{v:,.2f}"
    lines = [f"⚡ <b>មាស{km}ខ្លាំង (BIG MOVE)</b>", "",
             f"{'📈' if sg > 0 else '📉'} មាស{km} <b>${mv:,.0f}</b> ក្នុងរយៈពេល {mins} នាទី ({fmt(frm)} → {fmt(px)}) "
             f"= ប្រហែល {mv / norm:.0f} ដងនៃចលនាធម្មតាក្នុង 1 ម៉ោង (~${norm:,.0f})។", ""]
    if why:
        lines.append("📰 <b>មូលហេតុដែលអាចកើតមាន (Possible reason):</b>")
        lines += [f"• <i>{esc(x['title'][:120])}</i>{' · ' + esc(x['source']) if x.get('source') else ''}" for x in why]
    else:
        lines.append("📰 មិនទាន់មានព័ត៌មានច្បាស់ទេ (No clear headline yet) · អាចជាការលក់/ទិញធំៗ ឬ Stop-loss ច្រើន។ "
                     "ព័ត៌មាននឹងបង្ហោះនៅទីនេះ ពេលវាចេញ។")
    lines += ["", "⏱ <b>កត្តាប្រុងប្រយ័ត្ន:</b> ក្រោយចលនាខ្លាំង តម្លៃអាចលោតឡើងចុះលឿន (Volatility) · ប្រើ lot តូច។", "",
              "<i>ព័ត៌មានពន្យល់ មិនមែនសញ្ញាជួញដូរទេ · News explained, not a signal</i>"]
    cap = "\n".join(lines)
    item = {"badge": "BIG MOVE", "headline_en": f"Gold {word} ${mv:,.0f} in {mins} min ({fmt(frm)} → {fmt(px)})",
            "gold": "bullish" if sg > 0 else "bearish", "source": "XAU.KH",
            "box": why[0]["title"] if why else "No clear headline yet", "box_title": "Possible reason"}
    try:
        ok = send_photo(card(item, "move_card.png"), cap[:1024], "Breaking")
    except Exception as e:
        print("move card failed:", e)
        ok = send(cap, "Breaking")
    if ok:
        st["move_t"] = now
        print("big move sent:", item["headline_en"])


def main():
    key = (("anthropic", os.environ["ANTHROPIC_API_KEY"]) if os.environ.get("ANTHROPIC_API_KEY") else
           ("gemini", os.environ["GEMINI_API_KEY"]) if os.environ.get("GEMINI_API_KEY") else None)
    st = jl(STATE, {})
    now = time.time()
    if st.get("primed"):
        move_post(st, now)          # every cycle: a 5-min late price alert beats a 15-min late headline
        json.dump(st, open(STATE, "w"))
    if now - st.get("checked", 0) < CHECK_EVERY:
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
    st["recent"] = [x for x in st.get("recent", []) if now - x["t"] <= MOVE_LINK_S] + \
        [{"title": it["title"], "source": it["source"], "t": now} for it in new][:60]
    if not st.get("primed"):              # first run: remember what is out there, post nothing old
        st["primed"] = True
        json.dump(st, open(STATE, "w")); print("breaking: primed with", len(seen), "headlines"); return
    moved = now - st.get("move_t", 0) <= MOVE_LINK_S     # a ⚡ BIG MOVE in the last 2 h: its headline gets through
    if not new or st["ai"] >= MAX_AI or st["posts"] >= (HARD_MAX if moved else MAX_POSTS):
        json.dump(st, open(STATE, "w")); print(f"breaking: {len(new)} candidates, nothing to do"); return
    gold = jl("ict.json", {}).get("price")
    if key:
        try:
            picks = ask_ai(new[:15], gold, key)
            st["ai"] += 1
        except Exception as e:
            print("breaking AI failed, using rules:", e); picks = rules_pick(new, st)
    else:
        picks = rules_pick(new, st)
    for p in picks:     # news of the powers that move gold, right after a big price move = market-shaking
        try:
            if moved and MAJOR.search(new[int(p["id"])]["title"]):
                p["importance"] = 5
        except Exception:
            pass
    for p in sorted(picks, key=lambda x: -int(x.get("importance", 0))):
        big = int(p.get("importance", 0)) >= 5
        if int(p.get("importance", 0)) < 4 or st["posts"] >= (HARD_MAX if big else MAX_POSTS):
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
        if p.get("km_reason"):        # free rules mode, written like a Khmer news post
            k = p["_cat"]
            cap = "\n".join([f"🚨 <b>ព័ត៌មានបន្ទាន់ (BREAKING)</b>", "",
                             f"📌 <b>ព្រឹត្តិការណ៍ (Event):</b> {KM_WHAT[k]}",
                             f"<i>{esc(p['headline_en'])}{' · ' + esc(p.get('source', '')) if p.get('source') else ''}</i>", "",
                             f"<b>ឥទ្ធិពលលើទីផ្សារ (Market Impact): {KM_TAG[p['gold']]}</b>", esc(p["km_reason"]), "",
                             f"⏱ <b>កត្តាប្រុងប្រយ័ត្ន (Short-term Note):</b> {KM_SHORT[k]}", "",
                             "<i>ច្បាប់ទូទៅ មិនមែនការសន្យា · មិនមែនសញ្ញាជួញដូរទេ</i>"])
        else:
            cap = None
        cap = cap or "\n".join([f"🚨 <b>ព័ត៌មានបន្ទាន់ (BREAKING)</b>", "", esc(p.get("km_what", "")), "",
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
            if p.get("_cat"):
                st.setdefault("cat_last", {})[p["_cat"]] = now
            print("breaking sent:", p.get("headline_en"))
    json.dump(st, open(STATE, "w"))


if __name__ == "__main__":
    main()
