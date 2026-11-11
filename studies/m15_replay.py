"""2-year replay of the LIVE M15 signal (setupidea.py exactly as the bot runs it), 11 Nov 2026.

For every session (Asia 17:30, London 02:05, New York 07:00 New York time) the idea is built from the closed candles at
that moment, then setupidea.watch() is called after every 15m close until the next session, with the clock set to that
moment. Every signal it would send is graded like track.py: entry at the alert price, SL, half at TP1 then SL to entry,
rest to TP2, out after 8 h, $0.40 cost. Limitation: no historical news calendar, so the 15-min news pause is not applied.
Run: python studies/m15_replay.py START END OUT.json   (row indexes into the 2-year CSV; run chunks in parallel)
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, '/home/claude/xau-kh-terminal')
os.chdir(tempfile.mkdtemp())          # setupidea writes its state file in the working directory
import pandas as pd

import ict
import liqmap
from levels import to_ny

liqmap._daily_bias = lambda d: liqmap._bias(ict.resample(d, "D"))   # no Yahoo download in the replay
import setupidea
import signal_card
import tg

full = to_ny(pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True))
O, H, L, C = (full[k].to_numpy() for k in ("Open", "High", "Low", "Close"))
IDX = full.index
start, end, out_path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

sent = []
tg.send = lambda *a, **k: 1
tg.send_photo = lambda *a, **k: 1
tg.msg_link = lambda *a, **k: None
tg.log_alert = lambda e: sent.append(e)
signal_card.make = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no card"))
setupidea._news_near = lambda now: None
clock = {"t": 0.0}
setupidea.time.time = lambda: clock["t"]


def grade(e, j0):
    sg = 1 if e["dir"] == "bull" else -1
    en, st, tp1, tp2 = e["entry"], e["stop"], e["tp1"], e["target"]
    risk = abs(en - st)
    jend = min(j0 + 96, len(full) - 1)
    stop, got, left, hit1 = st, 0.0, 1.0, False
    for j in range(j0, jend + 1):
        if (L[j] <= stop) if sg > 0 else (H[j] >= stop):
            return got + left * (stop - en) * sg / risk - 0.4 / risk, hit1
        if not hit1 and ((H[j] >= tp1) if sg > 0 else (L[j] <= tp1)):
            got, left, hit1, stop = got + 0.5 * abs(tp1 - en) / risk, 0.5, True, en
        if hit1 and ((H[j] >= tp2) if sg > 0 else (L[j] <= tp2)):
            return got + left * abs(tp2 - en) / risk - 0.4 / risk, hit1
    return got + left * (C[jend] - en) * sg / risk - 0.4 / risk, hit1


SES = [(17, 30, (6, 0, 1, 2, 3)), (2, 5, (0, 1, 2, 3, 4)), (7, 0, (0, 1, 2, 3, 4))]
starts = []
for i in range(max(start, 6100), min(end, len(full) - 100)):
    t = IDX[i]
    for hh, mm, days in SES:
        if t.weekday() in days and t.hour == hh and t.minute == mm // 5 * 5:
            starts.append(i)
results = []
for n, i0 in enumerate(starts):
    clock["t"] = (IDX[i0] + pd.Timedelta(minutes=5)).timestamp()
    try:
        idea, _ = setupidea.build(full.iloc[i0 - 6000:i0 + 1])
    except Exception as ex:
        print("build failed", IDX[i0], ex)
        continue
    st = setupidea.jl(setupidea.STATE)
    idea.update(msg_id=None, session=str(IDX[i0]))
    st["idea"] = idea
    json.dump(st, open(setupidea.STATE, "w"), default=str)
    nxt = starts[n + 1] if n + 1 < len(starts) else i0 + 96
    for j in range(i0 + 1, min(nxt, i0 + 96)):
        if (IDX[j] + pd.Timedelta(minutes=5)).minute % 15:
            continue                      # watch only acts on a closed 15m candle
        clock["t"] = (IDX[j] + pd.Timedelta(minutes=5)).timestamp() + 30
        before = len(sent)
        setupidea.watch(full.iloc[j - 6000:j + 2])
        if len(sent) > before:
            e = sent[-1]
            r, hit1 = grade(e, j + 1)
            ck = (idea.get("checks") or {})
            results.append({"t": str(IDX[j + 1]), "j0": j + 1, "entry": e["entry"], "stop": e["stop"], "tp1p": e["tp1"], "tp2p": e["target"],
                            "dir": e["dir"], "tier": e.get("tier"), "R": round(r, 3), "tp1": hit1,
                            "kind": "zone" if "|zone|" in e["id"] else "break", "risk": round(abs(e["entry"] - e["stop"]), 2)})
            break
    if n % 50 == 0:
        print(f"{n}/{len(starts)} sessions, {len(results)} signals", flush=True)
json.dump(results, open(out_path, "w"))
print("done", len(starts), "sessions", len(results), "signals")
