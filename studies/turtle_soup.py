"""🐢 Turtle Soup at 8:30 (owner's TikTok idea, 12 Nov 2026: "1 Minute Liquidity Strategy", TWS / TBS).

Rule as written for a robot:
  levels  = high and low of a reference range that ends at 8:30 (tested: the hour before 8:30, and the whole night/Asia)
  window  = from 8:30 for 2 hours, at most 1 trade a day
  TWS     = a candle's WICK goes beyond the level but the candle CLOSES back inside -> enter at that close
  TBS     = a candle's BODY closes beyond the level, and within 3 candles a candle closes back inside -> enter there
  SL      = just beyond the sweep's extreme (+$0.50), risk $2-15
  TP      = 1.2R (as in the video), 2R, or the other side of the range
Data limit: 5m candles (no 1m history), entry at the next 5m open, $0.40 cost.
'8:30' tested both ways: 8:30 New York (US data / NY open) and 8:30 Cambodia (Asia morning).
Run: python studies/turtle_soup.py
"""
import sys
sys.path.insert(0, '/home/claude/xau-kh-terminal')
import numpy as np
import pandas as pd
import research as R
from levels import to_ny

df = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
split = df.index[int(len(df) * 0.7)]
O, H, L, C = (df[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
n = len(df)
b4 = R._bias(df, "4H", pd.Timedelta(hours=4))


def sim(tz, ref_hours, mode, tp_kind, trend=None, window_h=2):
    loc = df.index.tz_convert(tz)
    starts = np.where((loc.hour == 8) & (loc.minute == 30))[0]
    out = []
    for s in starts:
        r0 = s - int(ref_hours * 12)
        if r0 < 300:
            continue
        hi, lo = H[r0:s].max(), L[r0:s].min()
        end = min(s + window_h * 12, n - 40)
        done = False
        for i in range(s, end):
            for sg, lvl in ((-1, hi), (1, lo)):          # sweep of the high -> SELL, of the low -> BUY
                if trend and b4[i] != ({1: "bull", -1: "bear"}[sg] if trend == "with" else {1: "bear", -1: "bull"}[sg]):
                    continue
                wick = (H[i] > lvl and C[i] < lvl) if sg < 0 else (L[i] < lvl and C[i] > lvl)
                body = False
                if mode in ("tbs", "both") and i - 1 >= s:
                    for k in range(max(s, i - 3), i):     # a body closed beyond in the last 3 candles, now back inside
                        if ((C[k] > lvl) if sg < 0 else (C[k] < lvl)) and ((C[i] < lvl) if sg < 0 else (C[i] > lvl)):
                            body = True
                ok = (mode == "tws" and wick) or (mode == "tbs" and body) or (mode == "both" and (wick or body))
                if not ok:
                    continue
                j0 = i + 1
                ext = H[max(s, i - 3):i + 1].max() if sg < 0 else L[max(s, i - 3):i + 1].min()
                stop = ext + 0.5 if sg < 0 else ext - 0.5
                en = O[j0]
                risk = (stop - en) if sg < 0 else (en - stop)
                if not 2 <= risk <= 15:
                    continue
                tgt = (en + sg * 1.2 * risk if tp_kind == "1.2R" else en + sg * 2 * risk if tp_kind == "2R"
                       else (lo if sg < 0 else hi))
                if (tgt - en) * sg <= 0.5 * risk:
                    continue
                res = None
                for j in range(j0, min(j0 + 48, n - 1)):    # 4 h max
                    if (H[j] >= stop) if sg < 0 else (L[j] <= stop):
                        res = -1.0; break
                    if (L[j] <= tgt) if sg < 0 else (H[j] >= tgt):
                        res = abs(tgt - en) / risk; break
                if res is None:
                    res = (C[j] - en) * sg / risk
                out.append((df.index[j0], res - 0.4 / risk, "long" if sg > 0 else "short"))
                done = True
                break
            if done:
                break
    return out


rows = []
for tz, tzn in (("America/New_York", "8:30 NY"), ("Asia/Phnom_Penh", "8:30 KH")):
    for ref, refn in ((1, "1h range"), (8.5 if tz == "America/New_York" else 3, "night range")):
        for mode in ("tws", "tbs", "both"):
            for tp in ("1.2R", "2R", "range"):
                for trend in (None, "with"):
                    tr = sim(tz, ref, mode, tp, trend)
                    if len(tr) < 20:
                        continue
                    jd = R.judge(tr, split)
                    r = np.array([x[1] for x in tr])
                    rows.append((f"{tzn} · {refn} · {mode.upper()} · TP {tp} · {'with 4H' if trend else 'any'}", len(r),
                                 100 * (r > 0).mean(), r.mean(), jd['t_stat'], jd['older_70pct']['avg_R'],
                                 jd['newest_30pct']['avg_R'], jd['positive_quarters'], jd['proven']))
rows.sort(key=lambda x: -x[3])
print(f"{len(rows)} versions tested. Best 12 and worst 3 by avg R:")
for r in rows[:12] + [x for x in rows if "1.2R" in x[0] and "1h" in x[0]] + rows[-3:]:
    print(f"{r[0]:55} n={r[1]:4d} win {r[2]:.0f}% avg {r[3]:+.3f}R t={r[4]:+.1f} older {r[5]:+.2f} newest {r[6]:+.2f} "
          f"q {r[7]}{' · PROVEN' if r[8] else ''}")
print("all versions average:", f"{np.mean([r[3] for r in rows]):+.3f}R", "· proven:", sum(r[8] for r in rows))
