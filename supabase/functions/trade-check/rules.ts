// ✋ Trade check rules: the same rules as tradecheck.py (the Telegram bot), for the mini app.
// Pure functions, no Deno / network, so they can be tested anywhere. Code decides; the AI only reads the picture.
// If you change a rule here, change it in tradecheck.py too.

export const MIN_RR = 2.0;        // PRO plans at 2R
export const HARD_RR = 1.5;       // under 1.5R is a no
export const MIN_RISK = 1.5;      // a stop under $1.50 sits inside normal gold noise
export const MAX_RISK = 25;       // PRO's "skip if risk > $"
export const DEFAULT_RISK = 8.0;  // $ stop when no WALL is in a sensible range behind the entry
export const CHASE = 3.0;         // entry this far from the live price = old screenshot or chasing
export const NEWS_BEFORE = 30, NEWS_AFTER = 15;  // minutes around a high-impact release
export const MAX_LOSSES = 2;      // 2 losses today = done for the day

export type Side = "BUY" | "SELL";
export interface Trade { side: Side; entry: number | null; sl: number | null; tp: number | null; reason: string; auto: string[] }
export interface Read {
  pro_visible?: boolean; chk?: string; chk_ok?: boolean; bias?: string; score?: number | null; h1?: string; h4?: string;
  wall_up?: number | null; wall_down?: number | null; poi_low?: number | null; poi_high?: number | null;
  next?: string; trigger?: string; price?: number | null; timeframe?: string; error?: string;
}
export interface Ctx { live: number | null; liveAgeS: number; news: { title: string; minsAway: number } | null; lossesToday: number }
export type Mark = "✗" | "!" | "✓";
export interface Result { verdict: "GO" | "CAUTION" | "NO-GO"; lines: { m: Mark; t: string }[]; instead: string; rr: number; notChecked: boolean }

export const READ_PROMPT = `This is a TradingView chart of gold with the "XAU.KH PRO" indicator. Read ONLY what is visible.
Return ONE JSON object and nothing else:
{"pro_visible": true/false,          // is the XAU.KH PRO panel visible?
 "chk": "",                          // the line starting with "CHK" copied EXACTLY, or "" if not visible
 "bias": "BUY|SELL|NONE|UNKNOWN",    // the BIAS row: "BIAS ▲ BUY" = BUY, "BIAS ▼ SELL" = SELL, "no clear trend" = NONE
 "score": null,                      // the number before "/5" in the score cell, e.g. "1/5 · watch" -> 1
 "h1": "UP|DOWN|NONE|UNKNOWN", "h4": "UP|DOWN|NONE|UNKNOWN",   // the 1H and 4H structure cells (▲ = UP, ▼ = DOWN)
 "wall_up": null, "wall_down": null, // numbers after "▲ WALL" and "▼ WALL"
 "poi_low": null, "poi_high": null,  // the "POI a–b" numbers in the BIAS row
 "next": "",                         // the text after "NEXT ▸"
 "trigger": "FLIP_BUY|FLIP_SELL|GO_BUY|GO_SELL|NONE|UNKNOWN", // a FLIP or GO label (not "skip") on the last ~10 candles
 "price": null,                      // the chart's current price (last price tag on the right axis)
 "timeframe": ""}
Never guess a number you cannot read: use null.`;

const num = (s: unknown): number | null => {
  const v = parseFloat(String(s ?? "").replace(/,/g, ""));
  return Number.isFinite(v) ? v : null;
};
export const fmt = (x: number) => x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** The CHK line PRO prints (CHK b-1 s1 h-1 f0 u3872.96 d3854.70 p3877.66-3901.37) is exact: it overrides the AI's eye. */
export function applyChk(d: Read): Read {
  const chk = String(d.chk || "").trim();
  if (!/^CHK/i.test(chk)) { d.chk_ok = false; return d; }
  const g = (k: string) => { const m = chk.match(new RegExp(`\\b${k}(-?[\\d.]+|na)\\b`)); return m ? m[1] : null; };
  const b = g("b"), s = g("s"), h = g("h"), f = g("f");
  if (b === "1" || b === "-1" || b === "0") d.bias = { "1": "BUY", "-1": "SELL", "0": "NONE" }[b];
  if (s && s !== "na") d.score = Math.trunc(parseFloat(s));
  if (h === "1" || h === "-1" || h === "0") d.h4 = { "1": "UP", "-1": "DOWN", "0": "NONE" }[h];
  if (f === "1" || f === "-1" || f === "0") d.trigger = { "1": "FLIP_BUY", "-1": "FLIP_SELL", "0": "NONE" }[f];
  const u = g("u"), dn = g("d");
  d.wall_up = u && u !== "na" ? num(u) : null;
  d.wall_down = dn && dn !== "na" ? num(dn) : null;
  const p = chk.match(/\bp([\d.]+)-([\d.]+)\b/);
  d.poi_low = p ? num(p[1]) : null;
  d.poi_high = p ? num(p[2]) : null;
  d.chk_ok = true;
  return d;
}

/** Fill what the member left out: entry = live price, SL = behind the nearest WALL, TP = 2R. Returns an error or "". */
export function fill(t: Trade, read: Read, ctx: Ctx): string {
  const S = t.side === "BUY" ? 1 : -1;
  if (t.entry == null) {
    const cp = read.pro_visible ? read.price ?? null : null;
    t.entry = ctx.live != null && ctx.liveAgeS < 1800 ? ctx.live : cp;
    if (t.entry == null) return "I couldn't get the live price. Type your entry.";
    t.auto.push("entry = live price");
  }
  const E = t.entry;
  if (t.sl == null) {
    const wall = S === 1 ? read.wall_down : read.wall_up;
    let sl: number | null = null;
    if (wall && (E - wall) * S > 0) {
      sl = Math.round((wall - S * 0.5) * 100) / 100;
      if (!(Math.abs(E - sl) >= MIN_RISK && Math.abs(E - sl) <= MAX_RISK)) sl = null;
    }
    if (sl != null) t.auto.push(`SL just ${S === 1 ? "below" : "above"} the ${S === 1 ? "▼" : "▲"} WALL ${fmt(wall!)}`);
    else { sl = Math.round((E - S * DEFAULT_RISK) * 100) / 100; t.auto.push(`SL $${DEFAULT_RISK.toFixed(0)} away (no WALL in range)`); }
    t.sl = sl;
  }
  if ((E - t.sl) * S <= 0)
    return `For a ${t.side} the SL must be ${S === 1 ? "BELOW" : "ABOVE"} the entry ${fmt(E)}. ${fmt(t.sl)} is on the wrong side.`;
  if (t.tp == null) {
    t.tp = Math.round((E + S * MIN_RR * Math.abs(E - t.sl)) * 100) / 100;
    t.auto.push(`TP at ${MIN_RR.toFixed(0)}R`);
  }
  if ((t.tp - E) * S <= 0) return `For a ${t.side} the TP must be ${S === 1 ? "ABOVE" : "BELOW"} the entry ${fmt(E)}.`;
  return "";
}

export function evaluate(t: Trade, read: Read, ctx: Ctx): Result {
  const S = t.side === "BUY" ? 1 : -1;
  const E = t.entry!, SL = t.sl!, TP = t.tp!;
  const risk = Math.abs(E - SL);
  const rr = risk > 0 ? Math.round((Math.abs(TP - E) / risk) * 100) / 100 : 0;
  const out: { m: Mark; t: string }[] = [];
  const add = (m: Mark, tx: string) => out.push({ m, t: tx });
  const seen = !!read.pro_visible;
  const bias = seen ? read.bias || "UNKNOWN" : "UNKNOWN";
  const bS = bias === "BUY" ? 1 : bias === "SELL" ? -1 : 0;

  if (!seen) add("!", "XAU.KH PRO panel not readable in the screenshot: chart checks skipped");
  if (bS === -S) add("✗", `${t.side} against BIAS ${bS === 1 ? "▲ BUY" : "▼ SELL"} (1H + 4H structure)`);
  else if (bS === S) add("✓", `With BIAS ${S === 1 ? "▲ BUY" : "▼ SELL"}`);
  else if (seen) add("!", bias === "NONE" ? "No clear BIAS" : "Couldn't read BIAS");
  const sc = seen ? read.score ?? null : null;
  if (sc != null) add(sc <= 1 ? "✗" : sc <= 3 ? "!" : "✓", `Score ${sc}/5 → ${sc <= 1 ? "skip" : sc <= 3 ? "half size at most" : "full size OK"}`);
  const trig = String(read.trigger || "UNKNOWN");
  const tS = trig.endsWith("BUY") ? 1 : trig.endsWith("SELL") ? -1 : 0;
  if (seen) {
    if (tS === S) add("✓", `${trig.split("_")[0]} ${S === 1 ? "▲" : "▼"} on the chart`);
    else if (tS === -S) add("✗", `The chart's trigger is the other way (${trig.replace("_", " ")})`);
    else add("!", "No FLIP / GO yet: the level is not proven, waiting is the trade");
  }
  add(rr < HARD_RR ? "✗" : rr < MIN_RR ? "!" : "✓", `Risk:reward ${rr.toFixed(1)}R (need ${MIN_RR.toFixed(0)}R)`);
  if (risk < MIN_RISK) add("!", `SL only $${risk.toFixed(2)} away: inside normal gold noise`);
  else if (risk > MAX_RISK) add("✗", `SL $${risk.toFixed(2)} away: bigger than the $${MAX_RISK} limit`);
  else add("✓", `SL $${risk.toFixed(2)} away`);
  const wall = S === 1 ? read.wall_up : read.wall_down;
  if (seen && wall && (wall - E) * S > 0 && (TP - wall) * S > 0) {
    const room = risk > 0 ? Math.abs(wall - E) / risk : 0;
    add(room < 1 ? "✗" : room < MIN_RR ? "!" : "✓", `TP is past the ${S === 1 ? "▲" : "▼"} WALL ${fmt(wall)}: real room ${room.toFixed(1)}R`);
  }
  if (ctx.live != null && ctx.liveAgeS < 1800) {
    if (Math.abs(E - ctx.live) > CHASE)
      add("!", `Entry is ${Math.abs(E - ctx.live).toFixed(1)} from the live price ${fmt(ctx.live)}: old screenshot, or a limit far away`);
    const cp = seen ? read.price ?? null : null;
    if (cp && Math.abs(cp - ctx.live) > 2 * CHASE) add("!", `Chart shows ${fmt(cp)} but live is ${fmt(ctx.live)}: is this screenshot old?`);
  }
  if (ctx.news) {
    const m = ctx.news.minsAway;
    add("✗", `High-impact news ${m > 0 ? "in " + Math.trunc(m) + " min" : Math.trunc(-m) + " min ago"}: ${ctx.news.title}`);
  }
  if (ctx.lossesToday >= MAX_LOSSES) add("✗", `${ctx.lossesToday} losses today: done for the day`);

  const verdict = out.some(x => x.m === "✗") ? "NO-GO" : out.some(x => x.m === "!") ? "CAUTION" : "GO";
  let instead = "";
  if (bS === -S) {
    instead = `PRO's side is ${bS === 1 ? "BUY" : "SELL"}` +
      (read.poi_low && read.poi_high ? `: wait for price at the POI ${fmt(read.poi_low)}–${fmt(read.poi_high)}` : "") +
      `, then sweep → ${bS === 1 ? "▲" : "▼"} FLIP / GO`;
  } else if (seen && tS !== S && verdict !== "GO") instead = "Same side, but wait for the sweep → FLIP or ABSORB → GO on 5m first";
  else if (rr < MIN_RR) instead = `Move the TP or tighten the entry until it pays at least ${MIN_RR.toFixed(0)}R, or skip`;
  return { verdict, lines: out, instead, rr, notChecked: !seen && verdict !== "NO-GO" };
}

/** High-impact news within the window, from news.json's events. */
export function newsNear(events: { title?: string; time?: string; impact?: string }[], nowMs: number) {
  for (const e of events || []) {
    if (String(e.impact || "").toLowerCase() !== "high" || !e.time) continue;
    const t = Date.parse(e.time);
    if (!Number.isFinite(t)) continue;
    const mins = (t - nowMs) / 60000;
    if (mins >= -NEWS_AFTER && mins <= NEWS_BEFORE) return { title: e.title || "news", minsAway: mins };
  }
  return null;
}
