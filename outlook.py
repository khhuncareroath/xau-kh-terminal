"""📊 Daily Outlook card (morning, with the Asia session post): the ZTD-style fundamentals picture in our style.

Shows: price + yesterday's move, Dollar / US 10y yield / VIX tiles with their usual effect on gold, the overall
macro lean, today's high-impact US news with "higher / lower than forecast" outcomes, and key levels
(Resistance / Pivot / Support = 4H signal line or previous-day high, POC/midnight open, 4H line or previous-day low).
The Khmer story goes in the caption (images cannot render Khmer script well).

make(macro, news, lv, lines, price, path) -> (path, caption)
"""
from datetime import datetime, timedelta, timezone

from signal_card import BG, CARD, INK, MUT, UP, DN, BLUE, DARK, _fonts
from tg import esc, fmt, local

EVENT_DIR = [(("cpi", "pce", "ppi", "inflation"), -1), (("non-farm", "nonfarm", "payroll", "employment change"), -1),
             (("unemployment rate",), 1), (("jobless claims", "unemployment claims"), 1), (("gdp",), -1),
             (("ism", "pmi"), -1), (("retail sales",), -1), (("jolts", "job openings"), -1), (("hourly earnings",), -1)]


def _events(news, hours=30):
    now = datetime.now(timezone.utc)
    out = []
    for e in news.get("events", []):
        if e.get("impact") != "High":
            continue
        t = datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        if now - timedelta(minutes=30) <= t <= now + timedelta(hours=hours):
            sg = next((v for keys, v in EVENT_DIR if any(k in e["title"].lower() for k in keys)), None)
            out.append((t, e, sg))
    return sorted(out, key=lambda x: x[0])[:4]


def levels(lv, lines, price):
    lad = {x["name"]: float(x["price"]) for x in lv.get("ladder", []) if x.get("price")}
    res = [p for p in (lad.get("Prev day high"), lad.get("Asia high"), lines[0]) if p and p > price]
    sup = [p for p in (lad.get("Prev day low"), lad.get("Asia low"), lines[1]) if p and p < price]
    R, S = (min(res) if res else lines[0]), (max(sup) if sup else lines[1])
    cands = [p for p in (lad.get("Prev POC"), lad.get("Midnight open"), lad.get("VWAP")) if p and S < p < R]
    piv = min(cands, key=lambda p: abs(p - price)) if cands else (R + S) / 2   # always between support and resistance
    return R, piv, S


def tiles(macro):
    out = []
    d, y, v = macro.get("dxy") or {}, macro.get("us10y") or {}, macro.get("vix") or {}
    if d.get("last") is not None:
        out.append(("Dollar (DXY)", f"{d['last']:.2f}", f"{d.get('chg_pct', 0):+.2f}%", -1 if d.get("chg_pct", 0) > 0.1 else 1 if d.get("chg_pct", 0) < -0.1 else 0))
    if y.get("last") is not None:
        out.append(("US 10y yield", f"{y['last']:.2f}%", f"{y.get('chg_bp', 0):+.0f} bp", -1 if y.get("chg_bp", 0) > 3 else 1 if y.get("chg_bp", 0) < -3 else 0))
    if v.get("last") is not None:
        out.append(("Fear (VIX)", f"{v['last']:.1f}", f"{v.get('chg_pct', 0):+.1f}%", 1 if v.get("chg_pct", 0) > 5 else -1 if v.get("chg_pct", 0) < -5 else 0))
    return out


def make(macro, news, lv, lines, price, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams["font.family"] = _fonts()
    T, ev = tiles(macro), _events(news)
    R, P, S = levels(lv, lines, price)
    lean = sum(t[3] for t in T)
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor=BG)
    box = lambda x, y, w, h, fc=CARD: fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.02",
                                                                      transform=fig.transFigure, fc=fc, ec="none"))
    fig.text(0.06, 0.955, "XAU.KH", color=BLUE, fontsize=14, fontweight="bold", va="center")
    fig.text(0.94, 0.955, "DAILY OUTLOOK · " + datetime.now(timezone.utc).strftime("%a %d %b"), color=MUT, fontsize=10, va="center", ha="right")
    gchg = macro.get("gold_chg_pct")
    fig.text(0.06, 0.885, f"Gold {price:,.2f}", color=INK, fontsize=30, fontweight="bold", va="center")
    if gchg is not None:
        fig.text(0.06, 0.835, f"Last 24h: {gchg:+.2f}%", color=UP if gchg > 0 else DN, fontsize=12, fontweight="bold", va="center")
    # macro tiles
    fig.text(0.06, 0.78, "What moves gold today", color=MUT, fontsize=10, va="center")
    w = 0.88 / max(len(T), 1)
    for k, (name, val, chg, eff) in enumerate(T):
        x = 0.06 + k * w
        box(x, 0.62, w - 0.02, 0.14)
        fig.text(x + 0.02, 0.735, name, color=MUT, fontsize=9, va="center")
        fig.text(x + 0.02, 0.695, val, color=INK, fontsize=16, fontweight="bold", va="center")
        fig.text(x + 0.02, 0.66, chg, color=MUT, fontsize=9.5, va="center")
        c = UP if eff > 0 else DN if eff < 0 else MUT
        fig.text(x + w - 0.04, 0.66, "gold ↑" if eff > 0 else "gold ↓" if eff < 0 else "neutral", color=c, fontsize=10,
                 fontweight="bold", va="center", ha="right")
    lc = UP if lean > 0 else DN if lean < 0 else MUT
    box(0.06, 0.545, 0.88, 0.055, fc=lc)
    fig.text(0.5, 0.5725, ("Macro leans gold UP: BUY signals have the wind behind them" if lean > 0 else
                           "Macro leans gold DOWN: SELL signals have the wind behind them" if lean < 0 else
                           "Macro is mixed: follow the chart signals only"), color="white", fontsize=11.5,
             fontweight="bold", va="center", ha="center")
    # news
    fig.text(0.06, 0.505, "Big US news (next 30 h)", color=MUT, fontsize=10, va="center")
    y = 0.47
    if not ev:
        fig.text(0.06, y, "No high-impact news. Normal day.", color=INK, fontsize=11.5, va="center")
        y -= 0.045
    for t, e, sg in ev:
        fig.text(0.06, y, f"{local(t.timestamp())}  {e['title'][:34]}", color=INK, fontsize=11, fontweight="bold", va="center")
        fc = f"fcst {e['forecast']}" if e.get("forecast") else ""
        fig.text(0.94, y, fc, color=MUT, fontsize=9.5, va="center", ha="right")
        if sg:
            fig.text(0.06, y - 0.027, f"higher than forecast → gold {'↑' if sg > 0 else '↓'} · lower → gold {'↓' if sg > 0 else '↑'}",
                     color=MUT, fontsize=8.5, va="center")
        y -= 0.065
    # key levels, right under the news
    b0 = y - 0.2
    box(0.04, b0, 0.92, 0.2, fc=DARK)
    fig.text(0.08, b0 + 0.17, "Key levels", color="#AEAEB2", fontsize=10, va="center")
    for k, (lab, val, c) in enumerate((("Resistance", R, DN), ("Pivot", P, "#FFD60A"), ("Support", S, UP))):
        x = 0.08 + k * 0.29
        fig.text(x, b0 + 0.115, lab, color="#AEAEB2", fontsize=9.5, va="center")
        fig.text(x, b0 + 0.07, f"{val:,.2f}" if val else "–", color=c, fontsize=17, fontweight="bold", va="center")
    fig.text(0.08, b0 + 0.025, "Usual effect, not a promise · signals only in the Signals section", color="#636366", fontsize=7.5, va="center")
    fig.savefig(path, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    # Khmer story for the caption
    km = ["🌅 <b>DAILY OUTLOOK · ទិដ្ឋភាពថ្ងៃនេះ</b>", ""]
    if gchg is not None:
        km.append(f"• មាស 24 ម៉ោងចុងក្រោយ: <b>{gchg:+.2f}%</b> · ឥឡូវ {fmt(price)}")
    for name, val, chg, eff in T:
        kn = {"Dollar (DXY)": "ដុល្លារ", "US 10y yield": "ទិន្នផលសញ្ញាប័ណ្ណ 10 ឆ្នាំ", "Fear (VIX)": "ភ័យខ្លាច (VIX)"}[name]
        km.append(f"• {kn} {chg} → {'ល្អសម្រាប់មាស ↑' if eff > 0 else 'មិនល្អសម្រាប់មាស ↓' if eff < 0 else 'មិនសូវប៉ះពាល់'}")
    km.append(f"• សរុប: {'ម៉ាក្រូគាំទ្រមាសឡើង' if lean > 0 else 'ម៉ាក្រូគាំទ្រមាសធ្លាក់' if lean < 0 else 'ម៉ាក្រូចម្រុះ: មើលតែសញ្ញា chart'}")
    for t, e, sg in ev:
        km.append(f"📰 {local(t.timestamp())} <b>{esc(e['title'])}</b>" + (f" (ព្យាករ {e['forecast']})" if e.get("forecast") else ""))
    km += ["", f"🔴 Resistance <b>{fmt(R)}</b> · 🟡 Pivot <b>{fmt(P) if P else '–'}</b> · 🟢 Support <b>{fmt(S)}</b>",
           "<i>ឥទ្ធិពលធម្មតា មិនមែនការធានា · សញ្ញាមកតែក្នុង 📈 Signals</i>"]
    return path, "\n".join(km)
