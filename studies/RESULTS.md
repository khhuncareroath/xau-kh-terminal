# Research log, 11 Nov 2026 (2 years of 5m spot gold, $0.40 cost per trade, same proof rules as research.judge)

| Idea (source) | Result | Decision |
|---|---|---|
| News Playbook (Rith): continuation, pullback, fade, "lean before" | no version passed; after-news pullback 98 trades, 19% win, -0.55R, t -4.6 | post-news trade levels OFF, reaction reported only |
| Breakouts near news | 7-14 trades per bucket, no clear difference | no filter |
| ATR stop (ATR indicator research), smaller stops | all worse than fixed 0.55%; 0.75% slightly better but within noise | keep 0.55% |
| Luck test (permutation zip) | random trades same exits / same buy-sell mix: about 0R; ours +0.15 / +0.22 / +0.48R, p < 0.01 | edge is not luck |
| Regime filter (efficiency ratio 30x4H) | quiet day + choppy lost on older AND newest data; COMBO + clean trend 73% / 70% win | skip quiet + choppy (30 of 218 trades); kept 188: 65% win, +0.18R |
| range_extreme (counter-trend) | t 1.95 not proven, 0/2 live | not sent as a trade |

Scripts: newsplay.py, newsfilter.py, atrstop.py, luck.py, regime.py (run with the repo on PYTHONPATH and the 2-year CSV).

## Small-SL search (same day)

| Idea | Result | Decision |
|---|---|---|
| Retest entry after 4H breakout, SL 0.25-0.55% | all worse than market entry (retests pick the failing breakouts) | rejected |
| Trend-day pullback (Day Meter + 1H bias, 5m EMA20 / 15m FVG, structure SL ~$7), 36 variants, best picked on older 70% | newest 30%: about 0R | rejected |
| COMBO window (12h after COMBO breakout) + 15m FVG dip + 5m confirmation, structure SL ~$7, TP 2R, first per day | 120 trades, 50% win, +0.33R ($0.40) / +0.28R ($0.70), newest +0.39R, luck p=0.04; needs alert within ~1 min | LIVE as 🤬 COMBO SCALP, small size (scalp.py) |
| Same as limit order at the FVG | too few trades, inconsistent | rejected |
| Main signal tiers | COMBO only: 144 trades 68% win; COMBO + clean trend 98 trades 72% | owner chose COMBO only |
