# XAU.KH Breakout EA (MT5)

Robot for MetaTrader 5 that trades the channel's tested 4H Breakout rules on gold.

1. MT5 → File → Open Data Folder → MQL5 → Experts → copy `XAUKH_Breakout_EA.mq5` here.
2. Open MetaEditor (F4), open the file, press Compile (F7). It must say 0 errors.
3. First run the Strategy Tester (Ctrl+R): Expert = XAUKH_Breakout_EA, Symbol = XAUUSDm (or XAUUSD), model "Every tick based on real ticks", 1–2 years.
4. Then attach it to a gold chart on a DEMO account and turn on Algo Trading.
5. Real accounts are blocked until `InpAllowLive = true`. Only do that after weeks of demo that match the channel.

Rules: 4H candle (02/06/10/14/18/22 UTC) closes beyond the 30-candle high/low → enter.
SL 0.55% (PREMIUM 0.65%), TP1 0.75R close half + SL to entry, TP2 3R, 12 h time exit (PREMIUM ~5 days).
Day Meter ≥70% COMBO = full risk, quiet day = half risk (or skip), ≥100% = PREMIUM swing.
Safety: demo-only default, daily loss limit, spread filter, trading hours, kill switch, one trade at a time.
