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

## ICT order blocks and momentum "confirmation" indicators (11 Nov)

| Idea | Result | Decision |
|---|---|---|
| ICT/SMC order-block limit entries, SL past the OB ($3-6), 62 variants (5m/15m, 1H/4H bias, premium/discount) | median -0.16R older, -0.18R newest; best-on-older -0.42R newest | rejected |
| Momentum-confirmation indicator (strong candle breaks highs above VWAP/EMA, trend filter), 72 variants | median -0.08R older, -0.22R newest; best-on-older 14% win newest | rejected |
| PREMIUM as an intraday trade | 86 trades, 70% win, +0.28R, newest 80% win | live (no swing) |
| Mentor "full confirmation" filters on COMBO breakouts (VWAP, EMA50/200, 1H structure, strong candle) | VWAP/EMA/1H already agree on ~97-100% of COMBO breakouts; candle-strength filters helped on newest data but not on older | no change: the signal already has full confirmation |

## Exits and sessions on COMBO (11 Nov, evening)

| Idea | Result | Decision |
|---|---|---|
| TP1 0.75R -> 1R (half off, stop to entry, rest 3R, 12h) | +0.22R -> +0.30R; older +0.25 -> +0.29, newest +0.16 -> +0.31; win 68% -> 65%; every TP1 0.9-1.25R beat 0.75R on both halves; PREMIUM +0.28 -> +0.37R | LIVE (TP1_R = 1.0) |
| Hold 24h instead of 12h | +0.39R with TP1 1R (newest +0.33) | better, but crosses the night: owner wants intraday, offered as an option |
| Trailing stop after TP1 (15m swing, ATR x3/x5, EMA20) | all at or below the fixed 3R target | rejected |
| Partial size 1/3 or 2/3 at TP1, no break-even | no clear gain (no BE: win 56%) | no change |
| Session of the breakout | London 02-08 NY best (+0.41R); NY 08-13 +0.25 older but -0.36 newest (13 trades) | not consistent: no filter |

Script: scratchpad exits.py (2-year CSV).

## Does the analysis predict direction? (11 Nov, evening; 1,405 session posts over 2 years, next 8 hours)

| Part of the analysis | Agrees with which way gold moved $10 first | Decision |
|---|---|---|
| TARGET BUY / SELL lines (15m close beyond trigger -> target) | reached 71% when triggered; RANDOM lines at the same distances 77% | no edge: targets are small vs gold's range; no "accuracy %" will be advertised |
| Top-down bias (D/4H/1H, 30m/15m, all six) | 50% / 50% / 50% (all six agree: 52%) | coin flip |
| Draw on liquidity, premium/discount zone, last CHOCH/BOS, EMA50 side | 52% / 50% / 50% / 50% | coin flip |
| 4H breakout trend state, 24h momentum, side of the day open, Day Meter >= 100% | 50% / 51% / 52% / 52% | coin flip at a random hour |

Conclusion: at a random time gold's next move is close to 50/50 whatever the picture shows. The proven edge is only at
the 4H-breakout moment with the Day Meter filter and the scaled exit (the signals). The analysis is a MAP (where price
may react, where the next signal fires, when news hits), not a forecast. Bug found: the D pill was always blank
(live 5m feed ~20 days < 30 daily candles): fixed with 6 months of daily candles.
Scripts: scratchpad ana_bt.py, ana_dir.py, ana_dir2.py.

## Strong signals only (11 Nov, owner's choice) · renamed A+ / B+

| Set (TP1 1R, 2 years) | Trades | Per month | Win | Avg R | Newest 30% |
|---|---|---|---|---|---|
| B+ = Day Meter >= 70% + clean trend (was COMBO) | 92 | ~4 | 72% | +0.42R | 67% win, +0.40R |
| A+ = Day Meter >= 100% + clean trend (was PREMIUM) | 53 | ~2 | 72% | +0.47R | 80% win, +0.65R |
| Scalp after an A+/B+ breakout | 81 | ~3 | 58% | +0.59R | 56% win, +0.59R |
| (old COMBO, choppy included) | 137 | ~6 | 67% | +0.34R | 67%, +0.34R |

Clean trend = 4H efficiency > CHOP_ER (0.255). Choppy breakouts are now skipped with a note in Setup Analysis.

## Owner's ICT / SMC model (11 Nov, evening) · HTF zone -> 15m sweep + MSS -> 5m OB/CISD retest

Rules: Daily + 4H FVG / order-block zones (active until a close beyond the far edge); price taps a zone; within 6 h on
15m a liquidity sweep (low below the last 15m swing low) then MSS (15m close beyond the last swing high, body >= 0.6 ATR);
entry = limit at the last opposite 15m candle (OB / CISD level), waits 2 h, cancelled if the stop is hit first;
SL beyond the sweep extreme + 0.1 ATR ($2-20); TP 3R; max 12 h. 66 versions tested (entry x exit x bias x session x VP).

| Version | Trades | Win | Avg R | Older / newest | t | Proven |
|---|---|---|---|---|---|---|
| OB retest + Daily/4H bias + 3R | 84 (~3.5/month) | 45% | +0.44R | +0.41 / +0.52 | 2.29 | YES |
| same, 2R / half 1R + 3R | 84 | 48% / 59% | +0.28 / +0.18 | +0.28 / +0.20 | 1.8 / 1.5 | close |
| same without the HTF bias | 95 | 39% | +0.23 (3R) | +0.30 / +0.06 | 1.3 | no |
| market entry or FVG retest (any filters) | | | mostly ~0 or negative on newest | | | no |
| London/NY-only or volume-profile filter | | | weaker (fewer trades, no gain) | | | no |

Robustness (3R, bias): displacement 0.4/0.6/0.8/1.0 ATR -> +0.37/+0.44/+0.51/+0.25R; window 4/6/8 h -> +0.21/+0.44/+0.40;
max SL $15/20/25 -> +0.23/+0.44/+0.38; limit wait 1/2/4 h -> +0.42/+0.44/+0.40. Positive in 8 of 9 quarters, longs +0.25R
and shorts +0.70R. Median SL $10.6 (middle half $5.7-14.1). Candidate for a live signal (limit-order alert).
Script: scratchpad owner_ict.py / owner_rob.py.

**Correction (same evening):** the first study processed setups in zone order, not time order, which changed which
overlapping trades were taken. With the live code (splus.py, time order): 96 trades, 42% win, +0.29R, newest +0.34R,
t 1.67, 6 of 7 quarters positive; every setting tried stayed positive (+0.12 to +0.38R) but none reached t 2.
Decision (owner): live as 🎯 S+ SETUP at small size (0.25-0.5%) until the live record proves it.

## One model: A+/B+ breakout + ICT OB entry (11 Nov, owner's request)

After each A+/B+ breakout (92), within 12 h: 15m sweep + MSS in the breakout direction -> limit at the OB (top / middle /
volume-profile POC-VAL inside the OB), SL a bit under the OB or under the sweep, TP 2R/3R (71 setups).
SL under the OB (~$5-8): -0.12 to -0.63R in every version (the OB gets run through). SL under the sweep (~$10): only
21-23 fills, older +0.5 to +1.3R but newest -0.25 to -0.57R: not reliable. The volume-profile entry did not help.
Current A+/B+ market entry: 92 trades, 72% win, +0.42R (newest +0.40R). Decision: no combined model; the breakout entry stays.
