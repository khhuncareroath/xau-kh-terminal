//+------------------------------------------------------------------+
//|  XAUKH_Breakout_EA.mq5                                            |
//|  XAU.KH 4H Breakout robot for MT5 (gold only).                    |
//|                                                                    |
//|  Trades the same tested rules as the XAU.KH channel:              |
//|   - a 4H candle closes above the highest high (BUY) or below the  |
//|     lowest low (SELL) of the previous 30 4H candles               |
//|   - 4H candles start at 02/06/10/14/18/22 UTC (as in the backtest)|
//|   - Day Meter = today's range / normal day (median of 20 days)    |
//|       >= 100%  PREMIUM swing : SL 0.65%, hold up to 120 H1 bars   |
//|       >=  70%  COMBO intraday: SL 0.55%, close within 12 h        |
//|       <   70%  Normal        : same as combo, risk x 0.5 (or skip)|
//|   - TP1 = 0.75R: close half, move SL to entry. TP2 = 3R.          |
//|   - one trade at a time                                           |
//|                                                                    |
//|  SAFETY: runs on DEMO accounts only unless InpAllowLive = true.   |
//|  Daily loss limit, spread filter, trading hours, kill switch.     |
//|  Past results do not guarantee future results.                    |
//+------------------------------------------------------------------+
#property copyright "XAU.KH"
#property version   "1.00"

#include <Trade\Trade.mqh>

//--- inputs
input bool   InpEnabled          = true;   // Kill switch: false = never open new trades
input bool   InpAllowLive        = false;  // Allow REAL accounts (keep false until demo is proven)
input double InpRiskPct          = 1.0;    // Risk per trade, % of equity (COMBO / PREMIUM)
input double InpNormalFactor     = 0.5;    // Normal (quiet day) risk multiplier, 0 = skip normal trades
input bool   InpUsePremium       = true;   // Use PREMIUM swing on big days (holds up to ~5 days)
input double InpMaxDailyLossPct  = 3.0;    // Stop new trades after this daily loss (% of balance)
input double InpMaxSpread        = 0.60;   // Max spread in price ($) to enter
input int    InpEntryWindowMin   = 30;     // Minutes after the 4H close to still enter
input int    InpServerGMTOffset  = 0;      // Broker server time minus UTC in hours (Exness = 0)
input int    InpStartHourKH      = 0;      // Trading hours, Cambodia time: start (0-23)
input int    InpEndHourKH        = 24;     // Trading hours, Cambodia time: end (1-24)
input long   InpMagic            = 260411; // Magic number
input int    InpDeviationPts     = 50;     // Max slippage in points

CTrade trade;

//--- signal state
datetime g_lastBlock = 0;     // start (UTC) of the last processed closed 4H block
int      g_pendDir   = 0;     // pending signal direction
datetime g_pendUntil = 0;     // pending signal valid until (UTC)
datetime g_pendBlock = 0;
string   g_status    = "starting";
double   g_hiNext = 0, g_loNext = 0, g_dayUsed = -1;
datetime g_lastM1 = 0;

const datetime GRID_ANCHOR = D'2000.01.03 02:00';
const int      BLOCK = 4 * 3600;

//+------------------------------------------------------------------+
datetime ToUTC(datetime server) { return server - InpServerGMTOffset * 3600; }

int DayOfWeekUTC(datetime t) { MqlDateTime d; TimeToStruct(t, d); return d.day_of_week; }

datetime NthSunday(int year, int month, int n)
{
   MqlDateTime d; d.year = year; d.mon = month; d.day = 1; d.hour = 0; d.min = 0; d.sec = 0;
   datetime first = StructToTime(d);
   int dow = DayOfWeekUTC(first);
   int add = (7 - dow) % 7;
   return first + (add + 7 * (n - 1)) * 86400;
}

bool IsUSDST(datetime utc)
{
   MqlDateTime d; TimeToStruct(utc, d);
   datetime start = NthSunday(d.year, 3, 2) + 7 * 3600;   // 02:00 EST
   datetime end   = NthSunday(d.year, 11, 1) + 6 * 3600;  // 02:00 EDT
   return utc >= start && utc < end;
}

long TradeDayKey(datetime utc)
{
   int off = IsUSDST(utc) ? -4 : -5;
   datetime ny = utc + off * 3600;
   return (long)((ny - 18 * 3600) / 86400);   // New York 18:00 to 18:00
}

datetime BlockStart(datetime utc) { return GRID_ANCHOR + ((utc - GRID_ANCHOR) / BLOCK) * BLOCK; }

double Median(double &a[], int n)
{
   double b[]; ArrayResize(b, n);
   for(int i = 0; i < n; i++) b[i] = a[i];
   ArraySort(b);
   if(n % 2 == 1) return b[n / 2];
   return 0.5 * (b[n / 2 - 1] + b[n / 2]);
}

//+------------------------------------------------------------------+
//| Builds 4H blocks and the Day Meter from H1 data                  |
//+------------------------------------------------------------------+
bool Analyse(int &sig, datetime &closedStart, double &dayUsed)
{
   sig = 0; closedStart = 0; dayUsed = -1;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, PERIOD_H1, 0, 1300, r);
   if(n < 300) { g_status = "waiting for H1 history"; return false; }
   datetime nowUTC = ToUTC(TimeCurrent());

   //--- 4H blocks
   datetime bs[]; double bh[], bl[], bc[];
   int nb = 0;
   for(int i = 0; i < n; i++)
   {
      datetime s = BlockStart(ToUTC(r[i].time));
      if(nb == 0 || bs[nb - 1] != s)
      {
         nb++;
         ArrayResize(bs, nb); ArrayResize(bh, nb); ArrayResize(bl, nb); ArrayResize(bc, nb);
         bs[nb - 1] = s; bh[nb - 1] = r[i].high; bl[nb - 1] = r[i].low; bc[nb - 1] = r[i].close;
      }
      else
      {
         bh[nb - 1] = MathMax(bh[nb - 1], r[i].high);
         bl[nb - 1] = MathMin(bl[nb - 1], r[i].low);
         bc[nb - 1] = r[i].close;
      }
   }
   int kc = -1;
   for(int k = nb - 1; k >= 0; k--)
      if(bs[k] + BLOCK <= nowUTC) { kc = k; break; }
   if(kc < 31) { g_status = "not enough 4H history"; return false; }

   double hi30 = -DBL_MAX, lo30 = DBL_MAX;
   for(int k = kc - 30; k < kc; k++) { hi30 = MathMax(hi30, bh[k]); lo30 = MathMin(lo30, bl[k]); }
   if(bc[kc] > hi30) sig = 1;
   else if(bc[kc] < lo30) sig = -1;
   closedStart = bs[kc];

   g_hiNext = -DBL_MAX; g_loNext = DBL_MAX;   // lines for the next 4H close
   for(int k = kc - 29; k <= kc; k++) { g_hiNext = MathMax(g_hiNext, bh[k]); g_loNext = MathMin(g_loNext, bl[k]); }

   //--- Day Meter
   long keys[]; double rh[], rl[];
   int nd = 0;
   for(int i = 0; i < n; i++)
   {
      long key = TradeDayKey(ToUTC(r[i].time));
      if(nd == 0 || keys[nd - 1] != key)
      {
         nd++;
         ArrayResize(keys, nd); ArrayResize(rh, nd); ArrayResize(rl, nd);
         keys[nd - 1] = key; rh[nd - 1] = r[i].high; rl[nd - 1] = r[i].low;
      }
      else { rh[nd - 1] = MathMax(rh[nd - 1], r[i].high); rl[nd - 1] = MathMin(rl[nd - 1], r[i].low); }
   }
   long today = TradeDayKey(nowUTC);
   if(nd >= 11 && keys[nd - 1] == today)
   {
      int m = MathMin(20, nd - 1);
      double rng[]; ArrayResize(rng, m);
      for(int i = 0; i < m; i++) rng[i] = rh[nd - 2 - i] - rl[nd - 2 - i];
      double adr = Median(rng, m);
      if(adr > 0) dayUsed = (rh[nd - 1] - rl[nd - 1]) / adr;
   }
   return true;
}

//+------------------------------------------------------------------+
bool HasOurPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
         return true;
   }
   return false;
}

double TodayPnL()
{
   MqlDateTime d; TimeToStruct(TimeCurrent(), d); d.hour = 0; d.min = 0; d.sec = 0;
   datetime dayStart = StructToTime(d);
   double pnl = 0;
   if(HistorySelect(dayStart, TimeCurrent() + 60))
   {
      for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
      {
         ulong t = HistoryDealGetTicket(i);
         if(HistoryDealGetInteger(t, DEAL_MAGIC) != InpMagic) continue;
         if(HistoryDealGetString(t, DEAL_SYMBOL) != _Symbol) continue;
         pnl += HistoryDealGetDouble(t, DEAL_PROFIT) + HistoryDealGetDouble(t, DEAL_COMMISSION) + HistoryDealGetDouble(t, DEAL_SWAP);
      }
   }
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
         pnl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   }
   return pnl;
}

bool InTradingHours()
{
   MqlDateTime d; TimeToStruct(ToUTC(TimeCurrent()) + 7 * 3600, d);   // Cambodia = UTC+7
   if(InpStartHourKH <= 0 && InpEndHourKH >= 24) return true;
   if(InpStartHourKH < InpEndHourKH) return d.hour >= InpStartHourKH && d.hour < InpEndHourKH;
   return d.hour >= InpStartHourKH || d.hour < InpEndHourKH;   // window across midnight
}

string GV(ulong ticket, string k) { return "XKH_" + IntegerToString((long)ticket) + "_" + k; }

double NormLots(double lots)
{
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) step = 0.01;
   lots = MathFloor(lots / step) * step;
   if(lots < mn) return 0;
   return MathMin(lots, mx);
}

//+------------------------------------------------------------------+
void TryEnter()
{
   if(g_pendDir == 0) return;
   datetime nowUTC = ToUTC(TimeCurrent());
   if(nowUTC > g_pendUntil) { g_pendDir = 0; g_status = "signal expired (spread / hours / limit)"; return; }
   if(!InpEnabled) { g_status = "kill switch ON: no new trades"; return; }
   if(HasOurPosition()) { g_pendDir = 0; g_status = "trade running: new 4H signal skipped (as in the backtest)"; return; }
   if(!InTradingHours()) { g_status = "outside trading hours"; return; }
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   if(TodayPnL() <= -bal * InpMaxDailyLossPct / 100.0) { g_status = "daily loss limit reached"; return; }
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask - bid > InpMaxSpread) { g_status = "spread too wide, waiting"; return; }

   int dir = g_pendDir;
   bool premium = InpUsePremium && g_dayUsed >= 1.0;
   bool combo = g_dayUsed >= 0.7;
   double factor = (premium || combo) ? 1.0 : InpNormalFactor;
   if(factor <= 0) { g_pendDir = 0; g_status = "normal (quiet day) signal skipped by settings"; return; }

   double price = dir > 0 ? ask : bid;
   double stopPct = premium ? 0.0065 : 0.0055;
   double R = price * stopPct;
   int dg = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double sl  = NormalizeDouble(price - dir * R, dg);
   double tp1 = NormalizeDouble(price + dir * 0.75 * R, dg);
   double tp2 = NormalizeDouble(price + dir * 3.0 * R, dg);

   double lossPerLot = 0;
   if(!OrderCalcProfit(dir > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, 1.0, price, sl, lossPerLot) || lossPerLot == 0)
   { g_status = "cannot calculate lot size"; return; }
   double riskMoney = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPct / 100.0 * factor;
   double lots = NormLots(riskMoney / MathAbs(lossPerLot));
   if(lots <= 0)
   {
      g_pendDir = 0;
      g_status = StringFormat("account too small: 0.01 lot would risk $%.2f, allowed $%.2f", MathAbs(lossPerLot) * SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), riskMoney);
      return;
   }

   string kind = premium ? "PREMIUM" : combo ? "COMBO" : "NORMAL";
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPts);
   bool ok = dir > 0 ? trade.Buy(lots, _Symbol, 0, sl, tp2, "XAUKH " + kind)
                     : trade.Sell(lots, _Symbol, 0, sl, tp2, "XAUKH " + kind);
   if(!ok) { g_status = "order failed: " + trade.ResultRetcodeDescription(); return; }

   for(int i = PositionsTotal() - 1; i >= 0; i--)   // remember TP1 and the hold for the new position
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
      {
         GlobalVariableSet(GV(t, "tp1"), tp1);
         GlobalVariableSet(GV(t, "prem"), premium ? 1 : 0);
         GlobalVariableSet(GV(t, "done"), 0);
      }
   }
   g_pendDir = 0;
   g_status = StringFormat("%s %s %.2f lots, SL %.2f, TP1 %.2f, TP2 %.2f", kind, dir > 0 ? "BUY" : "SELL", lots, sl, tp1, tp2);
   Print("XAU.KH ", g_status);
}

//+------------------------------------------------------------------+
void Manage()
{
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      long type = PositionGetInteger(POSITION_TYPE);
      double open = PositionGetDouble(POSITION_PRICE_OPEN);
      double vol = PositionGetDouble(POSITION_VOLUME);
      double tp = PositionGetDouble(POSITION_TP);
      datetime opened = (datetime)PositionGetInteger(POSITION_TIME);
      bool prem = GlobalVariableCheck(GV(t, "prem")) && GlobalVariableGet(GV(t, "prem")) > 0.5;

      //--- time exit: intraday 12 h (clock), premium 120 H1 candles
      bool timeUp = prem ? (iBarShift(_Symbol, PERIOD_H1, opened) >= 120) : (TimeCurrent() - opened >= 12 * 3600);
      if(timeUp) { trade.PositionClose(t); Print("XAU.KH time exit ", t); continue; }

      //--- TP1: close half, stop to entry
      if(!GlobalVariableCheck(GV(t, "tp1"))) continue;
      if(GlobalVariableGet(GV(t, "done")) > 0.5) continue;
      double tp1 = GlobalVariableGet(GV(t, "tp1"));
      bool hit = type == POSITION_TYPE_BUY ? bid >= tp1 : ask <= tp1;
      if(!hit) continue;
      double half = NormLots(vol / 2.0);
      double mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
      if(half > 0 && vol - half >= mn - 1e-9) trade.PositionClosePartial(t, half);
      trade.PositionModify(t, open, tp);
      GlobalVariableSet(GV(t, "done"), 1);
      Print("XAU.KH TP1 hit: half closed, SL to entry ", t);
   }
}

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   bool demo = AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO;
   if(!demo && !InpAllowLive && !MQLInfoInteger(MQL_TESTER))
   {
      Alert("XAU.KH EA: this is a REAL account. The robot will not trade until InpAllowLive = true. Test on demo first.");
   }
   if(StringFind(_Symbol, "XAU") < 0)
      Alert("XAU.KH EA: attach this robot to a GOLD chart (XAUUSD / XAUUSDm).");
   EventSetTimer(20);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); Comment(""); }

void OnTimer() { OnTick(); }

void OnTick()
{
   bool demo = AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO;
   bool allowed = demo || InpAllowLive || MQLInfoInteger(MQL_TESTER);

   Manage();

   datetime m1 = iTime(_Symbol, PERIOD_M1, 0);
   if(m1 != g_lastM1)
   {
      g_lastM1 = m1;
      int sig; datetime cs; double du;
      if(Analyse(sig, cs, du))
      {
         g_dayUsed = du;
         if(cs != g_lastBlock)
         {
            g_lastBlock = cs;
            datetime closeUTC = cs + BLOCK;
            if(sig != 0 && ToUTC(TimeCurrent()) - closeUTC <= InpEntryWindowMin * 60)
            {
               g_pendDir = sig; g_pendBlock = cs; g_pendUntil = closeUTC + InpEntryWindowMin * 60;
               Print("XAU.KH 4H breakout ", sig > 0 ? "BUY" : "SELL", " at the close of ", TimeToString(closeUTC), " UTC");
            }
            else if(!HasOurPosition()) g_status = "waiting for a 4H close beyond a line";
         }
      }
   }
   if(allowed) TryEnter();
   else if(g_pendDir != 0) { g_pendDir = 0; g_status = "REAL account: trading blocked (InpAllowLive = false)"; }

   string zone = g_dayUsed < 0 ? "-" : g_dayUsed >= 1.0 ? "PREMIUM zone" : g_dayUsed >= 0.7 ? "COMBO zone" : "quiet day";
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   Comment(StringFormat("XAU.KH Breakout EA  |  %s  |  %s\n"
                        "4H BUY above %.2f (%.1f away)   SELL below %.2f (%.1f away)\n"
                        "Day Meter %.0f%% (%s)   Today P/L $%.2f\n"
                        "Status: %s",
                        demo ? "DEMO" : "REAL", InpEnabled ? "ON" : "KILL SWITCH",
                        g_hiNext, g_hiNext - bid, g_loNext, bid - g_loNext,
                        g_dayUsed < 0 ? 0 : g_dayUsed * 100, zone, TodayPnL(), g_status));
}
//+------------------------------------------------------------------+
