"""Replay of the LIVE ⏳ second chance (second.main + track.step) over 2 years, to check it matches
studies/second_chance.py. The clock moves every 5 minutes after each replayed M15 signal; Telegram is mocked.
Live-only rules applied here: no new trade 00-06 Cambodia, closed by 24:00 Cambodia (the study had neither).
Run: python studies/second_replay.py"""
import sys, os, json, tempfile
sys.path.insert(0, '/home/claude/xau-kh-terminal')
os.chdir(tempfile.mkdtemp())
import numpy as np, pandas as pd
import engine, tg, second, track, notify

df = pd.read_csv('/home/claude/spot/xau_5m.csv.gz', index_col=0, parse_dates=True)
split = df.index[int(len(df) * 0.7)]
starts = np.asarray((df.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1), dtype="int64")
M = json.load(open('/tmp/m15_a.json')) + json.load(open('/tmp/m15_b.json'))
clock = {"t": 0}
second.time.time = lambda: clock["t"]
view = {}
engine.load = lambda *a, **k: view["df"]
engine.closed = lambda d, *a, **k: d
sent = []
tg.send = tg.send_photo = lambda *a, **k: 1
tg.msg_link = lambda *a, **k: None
tg.local = lambda t: ""
tg.log_alert = lambda e: sent.append(e)
notify.news_soon = lambda *a, **k: False
import signal_card
signal_card.make = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no card"))

out = []
for r in M[:int(os.environ.get("NMAX", 10**6))]:
    j0 = r["j0"]
    created = int(starts[j0]) + 25
    parent = {"id": f"m15|{r['t']}", "kind": "m15", "model": "setup_idea", "dir": r["dir"], "entry": r["entry"], "stop": r["stop"],
              "tp1": r["tp1p"], "target": r["tp2p"], "created": created, "status": "filled"}
    json.dump([parent], open("alerts_log.json", "w"))
    if os.path.exists(second.STATE):
        os.remove(second.STATE)
    sent.clear()
    for step in range(1, 6 * 12 + 8):
        jl = j0 + step                       # candles j0 .. jl-1 are closed
        clock["t"] = int(starts[jl]) + 20
        view["df"] = df.iloc[max(0, jl - 1440):jl]
        second.main()
        if sent:
            break
    if not sent:
        continue
    a = dict(sent[0])
    bars = [(int(starts[k]), *map(float, df.iloc[k][["Open", "High", "Low", "Close"]])) for k in range(jl, min(jl + 110, len(df)))]
    track.step(a, bars)
    if a["status"] in track.TRADED:
        R = a["R"] - track.COST / abs(a["entry"] - a["stop"])
        out.append((pd.Timestamp(r["t"]), R, a["status"]))
    else:
        out.append((pd.Timestamp(r["t"]), None, a["status"]))

X = pd.DataFrame(out, columns=["t", "R", "status"])
print(X.status.value_counts().to_dict())
T = X.dropna()
import research as Rz
jd = Rz.judge([(t, r) for t, r in zip(T.t, T.R)], split)
print(f"LIVE CODE: {len(T)} re-entries traded ({len(T)/24:.1f}/mo), {100*(T.R>0).mean():.0f}% win, {T.R.mean():+.3f}R, t {jd['t_stat']}, "
      f"older {jd['older_70pct']} newest {jd['newest_30pct']}, quarters {jd['positive_quarters']}, proven {jd['proven']}, total {T.R.sum():+.1f}R")
