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

## Best setup: everything combined (11 Nov 2026, night, owner: "combine everything, best setup, A+ and B+, that's it")

All 213 intraday 4H breakouts (2 years), each with every tested ingredient attached: Day Meter, trend quality (ER),
breakout candle body, close location, stretch past the line, candle size, volatility regime, repeat breakouts, daily
EMA20 / 1H EMA50 side, session, direction. 2,430 threshold combinations, chosen on the OLDER 70% only.

| Ingredient (one at a time, older / newest) | Result |
|---|---|
| Day Meter high third | +0.33 / +0.60R (low third +0.01 / -0.08) · confirmed |
| Trend quality (ER) low third | +0.05 / +0.14R · confirmed (choppy = weak) |
| **Close location** of the breakout 4H candle (inside B+ set) | **close >= 70%: +0.44 / +0.68R · weaker close: +0.23 / -0.15R** · NEW |
| Body size, stretch past line, candle size, volatility, repeat count, session | mixed between halves: no filter |
| Daily EMA20 / 1H EMA50 side | already agree on 93-100% of breakouts: nothing to add |

Neighbours of the chosen cut: strong close 0.6 / 0.65 / 0.7 / 0.75 / 0.8 and ER 0.20-0.35 all better than no close filter,
on older AND newest data. Luck test: strong close vs random picks of the same size inside the B+ set p = 0.03
(the old A+ "Day Meter 100%" split alone: p = 0.28).

| Final (SL 0.55%, TP1 1R + BE, TP2 3R, 12 h) | Trades | /month | Win | Avg R | Newest 30% | Quarters + |
|---|---|---|---|---|---|---|
| 💎 A+ = breakout + strong close (>=70%) + ER > 0.30 + Day Meter >= 100% | 34 | 1.4 | 79% | +0.61R | 9 trades, 89% win, +0.89R | 4/4 |
| ⭐ B+ = same, Day Meter 70-100% | 24 | 1.0 | 75% | +0.48R | 4 trades, +0.48R | 2/2 |
| A+ and B+ together (judge: PROVEN, t 4.5) | 58 | 2.4 | 78% | +0.56R | 13 trades, 77% win, +0.76R | 7/7 |
| (old A+/B+, before this study) | 90 | 3.8 | 71% | +0.41R | 22 trades, +0.45R | 7/7 |
| Dropped by the new rules (weak close or ER 0.255-0.30) | 32 | 1.3 | 59% | +0.16R | +0.00R | t 0.8 |

Trade-off, honestly: fewer signals (2.4 instead of 3.8 a month), so total R per month is about the same (~+1.3R vs ~+1.5R)
but with a higher win rate, shorter losing streaks (max 2) and a better newest-data result. Softer alternative if members
want more signals: close >= 60% and ER > 0.255: 82 trades, 73% win, +0.47R, newest +0.60R.

Decision (owner): LIVE as the only signal. Scalp (SCALP=on), S+ (SPLUS=on) and the Volume Plan (VP_PLAN=on) are off.
Scripts: studies/best_setup.py, studies/best_setup_check.py.

## Mentor model at 1-2 setups a day (11 Nov 2026, night) · HTF key level -> 15m / 5m confirmation -> OB entry, TP 2R

Key levels: Daily / 4H / 1H FVG + OB, previous-day high/low, Asia high/low. Price taps a level -> on 15m or 5m an
optional sweep, then MSS with displacement -> LIMIT at the OB (edge or 50%), SL under the OB (mentor) or under the
sweep, TP 2R, max 2 trades a day, 8 h. 192 versions.

| Result | |
|---|---|
| All 192 versions | median -0.07R per trade (older -0.08, newest -0.05) |
| Versions with 1+ trade a day | 68, **none positive on both older and newest data** |
| Mentor version, all levels, 15m, SL under OB | ~0.9 a day, 37% win, +0.02R (newest -0.04 / +0.01): break-even before spread/slippage beyond $0.40 |
| Same on 5m | ~1.4 a day, 32% win, **-0.15R, t -3.0 (reliably losing)**, SL ~$3.7 |
| SL under OB vs under the sweep | -0.13R vs -0.03R (the OB gets run through, as in the earlier test) |
| Best found (D+4H only, 15m, ~0.4 a day) | +0.10 to +0.12R, t ~1.1 after 192 tries: what luck looks like, not proven |

Why: with TP 2R you need 34%+ wins just to break even, and a $4-6 stop makes the $0.40 cost ~0.08R per trade. More
levels and 5m entries add trades but they are the weaker ones. Decision: no new signal; A+ / B+ stays the only one.
Script: studies/ltf_ict.py.

## Strategy Edge Auditor: WHY the mentor LTF setups fail (11 Nov 2026, night)

442 mentor setups (all levels, 15m sweep + MSS, limit at OB, HTF bias, max 2/day), audited trade by trade. Every stop
model is compared at the SAME $ risk (results in R), TP = 2 x that stop.

| Question | Answer |
|---|---|
| Direction: $10 your way before $10 against? | **54%**: close to a coin flip. This is the root problem |
| Stop under OB | 63% stopped; about 4 in 10 stop-outs later reached +2R (stop hunt), 6 in 10 never did (wrong way) |
| Costs | median 0.06R per trade ($0.40 on a $6.2 stop): small, NOT the main problem on 15m |
| A under OB ($6) / B under sweep ($12) / C ATR x1.5 ($9) / D beyond HTF zone ($19) | +0.01 / +0.01 / +0.02 / +0.03R, all t < 0.6: **a wider stop does not create an edge** |
| Clean trend / moving day / with the 4H structure | worse (-0.12 / -0.05 / -0.00R): these entries fight momentum |
| New York 08-12 NY time | 107 trades, 47% win, +0.29R, t 2.0, older +0.32 / newest +0.21: CANDIDATE only (found by slicing ~20 ways) |
| NY + Daily/4H level only | 43 trades, +0.44R (older +0.48 / newest +0.35): candidate, too few trades |

Conclusion: the setups fail because the direction is ~50/50, not because of the stop, the entry or the costs. Fixing
the stop only changes how the break-even is reached. The one lead (New York session, ~1 a week) needs live paper
tracking before it can be a signal. Script: studies/edge_auditor.py.

## Decision (owner, 11 Nov 2026, night): 📐 Setup ideas
The session post in 📊 Analysis is now one mentor-style setup idea (setupidea.py): Swing 4H / Internal 15m / LTF 5m
bias, Swing High / Low, TARGET BUY / TARGET SELL lines with SL / TP1 / TP2, details on the picture. When a closed 15m
candle confirms a line, the bot sends 📐 SETUP in 📈 Signals (max 2 a day, not 15 min around big news, not chased), and
track.py replies TP / SL and counts it (kind "setup"). Labelled honestly as analysis, small size 0.25-0.5%: these
trigger lines tested near 50/50 above, so the LIVE record decides. SETUP_IDEAS=off turns it off, SETUP_TOPIC=setups
moves the alerts to 🔎 Setup Analysis.

## Decision (owner, 11 Nov 2026, night): ONE signal = the M15 setup, graded by the 4H
The separate 4H breakout signal is OFF (BREAKOUT_SIGNALS=on brings it back). The 4H now only gives key levels and
judges the M15 setup: 💎 A+ = with the 4H swing trend AND (6/7 confirmations OR a tested 4H breakout the same way in
the last 12 h: strong close + clean trend); ⭐ B+ = with the 4H trend and 4/7+. Counter-4H or weaker setups are noted
in 🔎 Setup Analysis, not sent. Replay of 30 sessions: 8 A+, 6 B+ (about 1-2 a day). HONEST NOTE: the only rule
proven on 2 years was the 4H breakout itself (78% win, +0.56R); the M15 setups and the grade are not proven yet,
so every signal says risk 0.25-0.5% and the live record in Proof decides.

## 2-year replay of the LIVE M15 signal (11 Nov 2026, night) · studies/m15_replay.py
setupidea.py exactly as the bot runs it, every session (998), watch() after every 15m close, graded like track.py
(half at TP1 + SL to entry, TP2, 8 h, $0.40). No historical news calendar, so the news pause is not applied.

| Version | Signals | /month | Win | Avg R | Older / newest | Quarters + |
|---|---|---|---|---|---|---|
| As launched (breakouts + zone reactions) | 501 | 21 | 50% | +0.007R (t 0.2) | +0.01 / +0.01 | |
| Zone reactions only | 138 | 6 | 43% | **-0.147R** | -0.12 / -0.19 | |
| **Now: TARGET-line breakouts only** | 383 | 16 | 53% | **+0.070R** (t 1.2) | +0.03 / +0.16 | 4/9 |
| 💎 A+ | 249 | 10 | 55% | +0.104R (t 1.5) | +0.07 / +0.19 | 6/9 |
| ⭐ B+ | 134 | 6 | 50% | +0.006R | -0.04 / +0.09 | 4/9 |

Decision: zone-reaction trades are no longer sent (ZONE_SIGNALS=on brings them back); zones stay on the card as key
levels and a reaction gets a note in Setup Analysis. Positive but NOT proven (t < 2), longest losing streak 9:
risk 0.25-0.5%, the live record decides. For comparison the 4H breakout alone was 78% win, +0.56R, proven (2-3 a month).

## Shorter trades for members who sleep (11 Nov 2026, night)
| Exit on the live M15 signal (383 replayed) | Avg R | A+ |
|---|---|---|
| now: TP1 + TP2, max 8 h | +0.070 | +0.104 |
| max 4 h / 3 h / 2 h | +0.046 / +0.045 / +0.044 | +0.08 / +0.07 / +0.05 |
| single TP 1R, max 2-3 h | +0.04 | +0.06-0.07 |
| **8 h but closed by 24:00 Cambodia, no new trade 00:00-06:00** | **+0.086** | **+0.107** |
Decision: closed by midnight (LIVE). ⚡ Scalp after an A+/B+ 4H breakout re-tested with today's stricter breakout:
57 trades, 60% win, +0.62R, newest 62% +0.77R, t 3.3, PROVEN -> back on by default (SCALP=off stops it), ~2-3 a month.

## More scalps (owner: "2-3 a month?!") · studies/scalp_more.py
Same 5m dip entry (TP 2R, 3 h), looser triggers. Every breakout-window version was positive on both halves:
| Trigger | /month | Win | Avg R | Older / newest | Proven |
|---|---|---|---|---|---|
| A+/B+ breakout, 12 h, 1 a day (was live) | 2.4 | 60% | +0.62 | +0.56 / +0.77 | yes |
| any 4H breakout, 12 h | 7.0 | 47% | +0.23 | +0.26 / +0.15 | yes |
| **any 4H breakout, 24 h, 2 a day (LIVE)** | **17** | **45%** | **+0.15** | +0.13 / +0.22 | **yes (t 2.2, 7/9 q)** |
| 4H structure only / 4H+1H agree (no breakout) | 18-32 | 39-41% | ~0 to +0.07 | | no |
| after an M15 A+/B+ signal | 11 | 36% | -0.06 | | no |
More R per month than the rare version (~+2.6R vs ~+1.5R). Scalps inside an A+/B+ window are marked 💎 strong.

## Scalp "analyses along" (studies/scalp_filters.py)
One check at a time on the wide scalp, kept only if better on BOTH halves. Clean 4H trend (efficiency > CHOP_ER, the
same rule as A+/B+): choppy-market scalps lost (-0.08R). LIVE wide scalp = any 4H breakout, 24 h, 2 a day, clean trend:
230 trades (~10 a month), 51% win at 2R, +0.35R, newest 51 trades 63% win +0.74R, t 3.8, 7/9 quarters, PROVEN.
(1H agreeing and "skip the 2nd scalp after a loss" also helped a little; not added, to keep the rule simple.)

## 🎰 Fun Scalp (owner: aggressive scalps for cent accounts, own topic) · 11 Nov 2026
Same 5m entry, direction = 4H structure, no breakout needed. 2 years: 2 a day ~40/month, 40% win at 2R, +0.03R
(t 0.7); 3 a day 0R; 4 a day -0.01R. Coin-flip territory -> LIVE as a labelled gamble in its own topic, 2 a day,
counted apart from the signal record (FUN_SCALP=off stops it, FUN_PER_DAY changes the cap). 1-minute history is not
available for testing, so the entry stays on 5m.

## 🎰 Fun Scalp TP1/TP2/TP3 (studies/fun_targets.py) · 11 Nov 2026
Same live entries, 969 trades in 2 years (~40/month), $0.40 cost. Ways to take profit:
one target 2R +0.03R (40% wins) · ½ TP1 → rest TP3 +0.02R · ½ TP1 → rest TP2 −0.01R · ⅓ at each, SL to entry after TP1
+0.02R (53% end in profit; TP1 reached 51%, TP2 25%, TP3 14%) · ⅓ each with the SL trailing to TP1 +0.01R · 1R only −0.02R
· 3R only +0.04R (35% wins). None proven (t ≤ 0.7, 3–5 of 9 quarters positive); worst run 11–14 losses, max drop 37–54R.
Decision: still a labelled gamble. LIVE uses ⅓ at TP1 / TP2 / TP3 with the SL to entry after TP1 (same result as the
best others, more wins felt, and each TP is a real action for members).
Owner follow-up (same day): drop the 3R target, split 1R→2R into three: ⅓ at 1R / 1.5R / 2R, SL to entry after TP1:
−0.004R (52% end in profit; TP1 50%, TP2 34%, TP3 24%), trailing the SL to TP1 −0.005R, 0.7/1.3/2R −0.02R. All within
luck of the 1/2/3R version (+0.02R, t 0.6): no real difference, all break-even. LIVE now: 1R / 1.5R / 2R (owner's choice).

## 🎰 Fun Scalp filters (studies/fun_filters.py) · 11 Nov 2026
Live entries + live exits (⅓ at 1R / 1.5R / 2R). Filters (8 tried, the first chosen in advance from scalp_filters.py):
no filter 40/mo −0.00R · **clean 4H trend (efficiency > 0.30) 14/mo, 60% in profit, +0.20R, t 3.3, older +0.16 /
newest +0.31, 7 of 9 quarters: PROVEN** · same with 3 a day 19/mo +0.17R t 3.3 PROVEN · + 1H agrees 11/mo +0.26R PROVEN
· London/NY hours only −0.04R · skipping dead hours +0.01R · 1H agrees alone +0.02R.
Overlap: 209 of the 230 ⚡ wide scalps are the same candle; the 237 fun-only trades still +0.14R.
LIVE: clean trend only, 3 a day, and no fun scalp while a ⚡ Scalp is open (never the same trade in two topics).
FUN_CLEAN=off goes back to the unfiltered version.

## ⏱ Live timing check · 11 Nov 2026
The loop runs back to back (no gaps between jobs), each cycle 20 s after the 5-min mark, all steps in ~8 s.
Bug found: session.py and setupidea.watch each dropped the last 5m row, and the feed sometimes has not opened the new
candle yet, so M15 signals came 5-10 min after the 15m close (11 Nov SELL: close 07:15 NY, sent 07:25).
Fixed with engine.closed() (cut by the clock), now used everywhere. ⚡ Scalp and 🎰 Fun Scalp already cut by the clock.
