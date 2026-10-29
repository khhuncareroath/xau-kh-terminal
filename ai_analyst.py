"""AI explainer: turns the engine's facts into a short, plain-language rationale.

The AI never decides direction, entry, stop or target: the rules and the backtest do that. Language models are
unreliable with exact numbers, so every number in the AI's answer is checked against the facts it was given;
if it invents one, the answer is thrown away and the rule-based reasons are used instead.

Secrets/vars: ANTHROPIC_API_KEY (required to enable), AI_MODEL (default claude-haiku-5-5),
AI_LANG ("en" or "km" for English + Khmer), AI_MAX_CALLS_PER_DAY (default 40).
Cost: it is only called when an alert is about to go out (a few times a day). Each call is roughly 1-2k tokens,
so a $5 credit lasts a very long time on a Haiku-class model. Check current prices on the Anthropic pricing page.
"""
import json
import os
import re
import time
import urllib.request

MODEL = os.environ.get("AI_MODEL", "claude-haiku-5-5")
LANG = os.environ.get("AI_LANG", "en")
MAX_CALLS = int(os.environ.get("AI_MAX_CALLS_PER_DAY", 40))
USAGE = "ai_usage.json"
SAFE_SMALL = {str(n) for n in (1, 2, 3, 4, 5, 7, 15, 30, 60, 100)}   # "1H", "5m", "15m", "2 closes" ...

SYSTEM = """You are the explainer for XAU.KH, a rules-based gold (XAUUSD futures) analysis service.
You receive facts computed by the engine. Write the "Why" for one trade idea:
- 2 to 3 short sentences, plain language for retail traders, calm and factual, no hype, no emojis.
- Explain what happened (liquidity, structure, zones, news) and what would prove the idea wrong.
- Use ONLY numbers that appear in the facts. Never invent prices, percentages or probabilities.
- Never say it will win or is guaranteed. It is an idea, not advice.
- If factors are missing or the backtest is weak, say so honestly in one short clause."""


def _numbers(s):
    return re.findall(r"\d[\d,]*\.?\d*", s)


def _allowed(facts):
    out = set(SAFE_SMALL)
    for n in _numbers(json.dumps(facts)):
        try:
            v = float(n.replace(",", ""))
        except ValueError:
            continue
        out |= {n.replace(",", ""), f"{v:g}", f"{v:.1f}", f"{v:.2f}", f"{v:,.2f}".replace(",", ""), str(int(v))}
    return out


def numbers_ok(text, facts):
    ok = _allowed(facts)
    bad = [n for n in _numbers(text) if n.rstrip(".").replace(",", "") not in ok]
    return not bad, bad


def _budget_ok():
    day = time.strftime("%Y-%m-%d", time.gmtime())
    try:
        u = json.load(open(USAGE))
    except Exception:
        u = {}
    if u.get("day") != day:
        u = {"day": day, "calls": 0, "tokens_in": u.get("tokens_in", 0), "tokens_out": u.get("tokens_out", 0)}
    return u, u["calls"] < MAX_CALLS


def explain(facts, timeout=25):
    """facts: dict of engine output for one idea. Returns text, or None (no key, budget used, error, or invented numbers)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    u, ok = _budget_ok()
    if not ok:
        print("AI daily call limit reached")
        return None
    ask = "Facts:\n" + json.dumps(facts, indent=1, default=str)
    if LANG == "km":
        ask += "\n\nWrite it in English, then the same text in Khmer on a new line starting with 'ខ្មែរ:'. Keep digits as 0-9."
    body = {"model": MODEL, "max_tokens": 400, "system": SYSTEM, "messages": [{"role": "user", "content": ask}]}
    try:
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                     headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=timeout))
        text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text").strip()
        use = r.get("usage", {})
        u["calls"] += 1
        u["tokens_in"] += use.get("input_tokens", 0)
        u["tokens_out"] += use.get("output_tokens", 0)
        json.dump(u, open(USAGE, "w"))
    except Exception as e:
        print("AI call failed:", e)
        return None
    good, bad = numbers_ok(text, facts)
    if not good:
        print("AI answer dropped, it used numbers that are not in the facts:", bad)
        return None
    return text or None


if __name__ == "__main__":   # quick self-test of the number guard
    f = {"entry": 4113.65, "stop": 4108.2, "swept": "London low 4112.4"}
    print(numbers_ok("London low 4112.4 was swept; invalid below 4108.20, 1H agrees.", f))
    print(numbers_ok("Expect a move to 4150 with 80% probability.", f))
