"""📰 Pre-news card: posted ~30 minutes before high-impact US news, as a picture with a short Khmer caption.

Shows: the event(s) and the time, forecast vs previous, what a higher / lower number usually means for gold, and how
much gold REALLY moved on past releases of that event (measured on 2 years of 5m spot gold, Nov 2024 - Nov 2026,
from the close before the release to the furthest point in the next 15 / 60 minutes; all release dates, no filtering):
  NFP  (22 releases): 15 min median $14, middle half $8-33, biggest $98 · 60 min median $18, biggest $106
  CPI  (23 releases): 15 min median $18, middle half $10-32, biggest $71 · 60 min median $21
  FOMC (16 meetings, 14:00 NY): 15 min median $17, middle half $10-28, biggest $103 · 60 min median $30, biggest $111
make(group, path) -> (path, caption); group = [(utc_time, event_dict, direction_if_higher)]
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from signal_card import BG, CARD, INK, MUT, UP, DN, BLUE, DARK, _fonts  # noqa: E402
from tg import esc, local  # noqa: E402

MOVES = {"NFP": dict(n=22, med=14, lo=8, hi=33, mx=98, m60=18),
         "CPI": dict(n=23, med=18, lo=10, hi=32, mx=71, m60=21),
         "FOMC": dict(n=16, med=17, lo=10, hi=28, mx=103, m60=30)}
KIND = [("FOMC", ("fomc", "federal funds", "fed chair", "powell", "interest rate decision")),
        ("NFP", ("non-farm", "nonfarm", "payroll", "unemployment rate", "hourly earnings")),
        ("CPI", ("cpi",))]
KM = {"NFP": "ការងារថ្មីអាមេរិក (NFP)", "CPI": "អតិផរណាអាមេរិក (CPI)", "FOMC": "ការសម្រេចការប្រាក់ Fed (FOMC)"}


def kind(titles):
    low = " ".join(titles).lower()
    return next((k for k, keys in KIND if any(x in low for x in keys)), None)


def _box(ax, x, y, w, h, fc, ec=None, r=0.025):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec or fc,
                                lw=1.2, transform=ax.transAxes))


def make(group, path):
    _fonts()
    t = group[0][0]
    titles = list(dict.fromkeys(e["title"] for _, e, _ in group))
    k = kind(titles)
    mv = MOVES.get(k)
    rows = [(e["title"], e.get("forecast") or "-", e.get("previous") or "-", sg) for _, e, sg in group][:4]
    signs = {s for *_, s in rows if s}
    sg = signs.pop() if len(signs) == 1 else None   # the higher/lower boxes only when every event points the same way
    H = 5.0 + 0.55 * len(rows) + (1.75 if mv else 0) + (1.4 if sg else 0)
    fig = plt.figure(figsize=(8, H), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    u = 1 / H   # one inch in axes units
    y = 1 - 0.55 * u
    ax.text(0.06, y, "XAU.KH", color=BLUE, fontsize=17, fontweight="bold", va="center")
    ax.text(0.94, y, "NEWS ALERT", color=MUT, fontsize=11, va="center", ha="right")
    y -= 0.85 * u
    _box(ax, 0.06, y - 0.42 * u, 0.88, 0.62 * u, DN)
    ax.text(0.5, y - 0.11 * u, f"High-impact US news at {local(t.timestamp())}", color="white", fontsize=15,
            fontweight="bold", ha="center", va="center")
    y -= 1.05 * u
    # table: event / forecast / previous / if higher
    ax.text(0.06, y, "Event", color=MUT, fontsize=10); ax.text(0.56, y, "Forecast", color=MUT, fontsize=10)
    ax.text(0.71, y, "Previous", color=MUT, fontsize=10); ax.text(0.94, y, "If higher", color=MUT, fontsize=10, ha="right")
    for title, f, p, rs in rows:
        y -= 0.55 * u
        ax.text(0.06, y, title[:30], color=INK, fontsize=12.5, fontweight="bold")
        ax.text(0.56, y, f, color=INK, fontsize=12.5); ax.text(0.71, y, p, color=MUT, fontsize=12.5)
        if rs:
            ax.text(0.94, y, "gold ↑" if rs > 0 else "gold ↓", color=UP if rs > 0 else DN, fontsize=12.5,
                    fontweight="bold", ha="right")
    y -= 0.5 * u
    ax.plot([0.06, 0.94], [y, y], color="#D1D1D6", lw=1, transform=ax.transAxes)
    if sg:
        y -= 0.95 * u
        for i, (lab, d) in enumerate((("Higher than forecast", sg), ("Lower than forecast", -sg))):
            x = 0.06 + i * 0.45
            _box(ax, x, y - 0.35 * u, 0.43, 0.95 * u, CARD, "#E5E5EA")
            ax.text(x + 0.03, y + 0.3 * u, lab, color=MUT, fontsize=10.5, va="center")
            ax.text(x + 0.03, y - 0.08 * u, "gold usually " + ("UP ↑" if d > 0 else "DOWN ↓"), color=UP if d > 0 else DN,
                    fontsize=15, fontweight="bold", va="center")
        y -= 0.45 * u
    if mv:
        y -= 0.85 * u
        _box(ax, 0.06, y - 0.45 * u, 0.88, 1.15 * u, DARK)
        ax.text(0.09, y + 0.42 * u, f"How much gold moved on the last {mv['n']} {k} releases (2 years)", color="#AEAEB2",
                fontsize=10, va="center")
        ax.text(0.09, y, f"First 15 min: usually \\${mv['lo']}-{mv['hi']}  ({mv['lo'] * 10}-{mv['hi'] * 10} pips)",
                color="white", fontsize=14, fontweight="bold", va="center")
        ax.text(0.09, y - 0.3 * u, f"Biggest: \\${mv['mx']} · first hour usually \\${mv['m60']} · direction can flip",
                color="#FFD60A", fontsize=10.5, va="center")
        y -= 0.45 * u
    y -= 0.6 * u
    for line in ("No new entries 15 min before → 15 min after", "Spread widens · SL can slip · use small lot or wait"):
        ax.text(0.06, y, "•  " + line, color=INK, fontsize=11.5, va="center")
        y -= 0.4 * u
    ax.text(0.06, max(y - 0.1 * u, 0.012), "Usual effect, not a promise · XAU.KH · Education, not financial advice",
            color=MUT, fontsize=8.5, va="center")
    fig.savefig(path, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)

    when = local(t.timestamp())
    km = [f"📰 <b>ព័ត៌មានធំ ម៉ោង {when}</b>" + (f" · {KM[k]}" if k else "") + f"\n{esc(', '.join(titles))}"]
    if sg:
        km.append(f"• លេខចេញ<b>ខ្ពស់</b>ជាងការរំពឹង → មាសទំនង{'ឡើង ↑' if sg > 0 else 'ធ្លាក់ ↓'} · "
                  f"<b>ទាប</b>ជាង → មាសទំនង{'ធ្លាក់ ↓' if sg > 0 else 'ឡើង ↑'}")
    elif any(r[3] for r in rows):
        km.append("• " + " · ".join(f"{esc(r[0])} ខ្ពស់ → មាស{'ឡើង ↑' if r[3] > 0 else 'ធ្លាក់ ↓'}" for r in rows if r[3]))
    if mv:
        km.append(f"• ពីមុន មាសរត់ <b>${mv['lo']}–{mv['hi']}</b> ក្នុង 15 នាទីដំបូង (ធំបំផុត ${mv['mx']})")
    km.append("• ⛔ កុំចូលថ្មី 15 នាទីមុន → 15 នាទីក្រោយ · spread ធំ\n<i>Signals only in 🚨 Signals · ការអប់រំ មិនមែនដំបូន្មាន</i>")
    return path, "\n".join(km)
