"""⚖️ Live vs test: every Friday, each signal type's REAL results next to what the 2-year test said to expect.

Honest early warning: if live results fall clearly below the test (more than 2 standard errors, with 15+ trades),
the post says so plainly. Fewer than 15 live trades: "too early to judge" (a few trades prove nothing either way).
Posted to 🏆 Proof right after the Friday weekly proof (session.py). Run alone to print it: python livecheck.py
"""
import json
import math

# what the tests said (studies/RESULTS.md); "since": live trades before this time used older rules and are not counted
EXPECT = [
    # key, name (EN · KM), match(alert), expected avg R, expected % in profit, since (unix)
    ("m15a", "📈 Signal A+", lambda a: a.get("model") == "setup_idea" and a.get("tier") == "A+", 0.15, 58, 0),
    # B+ is no longer sent (12 Nov 2026); its row only appears if BPLUS_SIGNALS is turned back on
    ("m15b", "📈 Signal B+", lambda a: a.get("model") == "setup_idea" and a.get("tier") == "B+", 0.14, 58, 1794470400),
    ("vol", "📈 Signal A+ · 📊 Volume", lambda a: a.get("model") == "vp_turn", 0.26, 48, 0),
    ("scalp", "⚡ Scalp", lambda a: a.get("kind") == "scalp", 0.35, 51, 0),
    ("fun", "🎰 Fun Scalp", lambda a: a.get("kind") == "fun", 0.17, 59, 1794409500),   # clean-trend version, from 11 Nov 2026 22:05 Cambodia
]
TRADED = ("win", "tp1", "loss", "timed out")
MIN_N = 15


def jl(n, d):
    try:
        return json.load(open(n))
    except Exception:
        return d


def rows(log):
    out = []
    import os
    for key, name, match, exp_r, exp_w, since in EXPECT:
        if key == "m15b" and os.environ.get("BPLUS_SIGNALS", "on") != "on":
            continue
        rs = [a["R"] for a in log if a.get("status") in TRADED and a.get("R") is not None
              and a.get("created", 0) >= since and match(a)]
        n = len(rs)
        avg = sum(rs) / n if n else None
        win = 100 * sum(r > 0 for r in rs) / n if n else None
        if n < MIN_N:
            verdict = ("⏳", f"too early ({n}/{MIN_N} trades)", f"នៅដំបូង ({n}/{MIN_N})")
        else:
            sd = math.sqrt(sum((r - avg) ** 2 for r in rs) / (n - 1)) or 1.0
            se = sd / math.sqrt(n)
            if avg < exp_r - 2 * se:
                verdict = ("⚠️", "BEHIND the test: watch closely", "ខ្សោយជាងតេស្ត")
            elif avg >= exp_r - se:
                verdict = ("✅", "in line with the test", "ស្របនឹងតេស្ត")
            else:
                verdict = ("🟡", "a bit below, still within normal luck", "ទាបបន្តិច ធម្មតា")
        out.append(dict(key=key, name=name, n=n, avg=avg, win=win, exp_r=exp_r, exp_w=exp_w, total=sum(rs), verdict=verdict))
    return out


def text(log):
    lines = ["⚖️ <b>LIVE vs TEST · លទ្ធផលពិត ធៀបនឹងតេស្ត</b>",
             "<i>Real results since each type started, next to what the 2-year test expected.</i>", ""]
    behind = []
    for r in rows(log):
        ico, en, km = r["verdict"]
        live = (f"{r['n']} trades · {r['win']:.0f}% in profit · {r['avg']:+.2f}R avg ({r['total']:+.1f}R)"
                if r["n"] else "no trades yet")
        lines += [f"{ico} <b>{r['name']}</b>: {en} · {km}",
                  f"   Live: {live}",
                  f"   Test: {r['exp_w']}% in profit · {r['exp_r']:+.2f}R avg", ""]
        if ico == "⚠️":
            behind.append(r["name"])
    if behind:
        lines.append(f"⚠️ <b>{', '.join(behind)}</b> is doing worse live than in testing. Use smaller size until it recovers; "
                     "if it stays behind, it will be paused and re-tested. · ប្រើទំហំតូច")
    else:
        lines.append("No signal type is clearly behind its test right now. · មិនមានប្រភេទណាខ្សោយជាងតេស្តទេ")
    lines.append("<i>R = times the risk. +0.10R a trade ≈ +$1 per $10 risked. Losses are always counted.</i>")
    return "\n".join(lines)


if __name__ == "__main__":
    print(text(jl("alerts_log.json", [])))
