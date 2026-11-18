// ✋ trade-check: the mini app's private pre-trade check. Deployed to Supabase project "xau-kh".
// POST JSON with the Telegram Mini App initData (proves who the member is), and an action:
//   {action:"check", initData, image (base64, no data: prefix), media, side, entry?, sl?, tp?, reason?}
//   {action:"mark",  initData, id, taken}        -> "I took it" / "I skipped"
//   {action:"list",  initData}                   -> the member's own checks + bill
// Each member only ever reads or writes rows with their own Telegram id. Grading (TP / SL hit) is done by the bot's loop.
// Secrets (Supabase → Edge Functions → Secrets): TELEGRAM_TOKEN, and GEMINI_API_KEY or ANTHROPIC_API_KEY.
// Optional: TRADECHECK_PER_DAY (default 10), TRADECHECK_OWNER_ONLY=<telegram id> to test alone first.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";
import { applyChk, Ctx, evaluate, fill, newsNear, READ_PROMPT, Read, Side, Trade } from "./rules.ts";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const RAW = "https://raw.githubusercontent.com/khhuncareroath/xau-kh-terminal/main/";
const PER_DAY = Number(Deno.env.get("TRADECHECK_PER_DAY") || 10);
const GEMINI_MODELS = [Deno.env.get("GEMINI_MODEL") || "", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash",
  "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-flash-latest"].filter(Boolean);
const CLAUDE_MODEL = Deno.env.get("TRADECHECK_MODEL") || "claude-haiku-5-5";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, "Content-Type": "application/json" } });

// ---------- who is asking (Telegram's signed initData)
async function hmac(key: Uint8Array, msg: string) {
  const k = await crypto.subtle.importKey("raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg)));
}
const hex = (b: Uint8Array) => [...b].map(x => x.toString(16).padStart(2, "0")).join("");
async function verify(initData: string, token: string): Promise<number | null> {
  const p = new URLSearchParams(initData);
  const hash = p.get("hash");
  if (!hash) return null;
  p.delete("hash");
  const lines = [...p.entries()].map(([k, v]) => `${k}=${v}`).sort().join("\n");
  const secret = await hmac(new TextEncoder().encode("WebAppData"), token);
  if (hex(await hmac(secret, lines)) !== hash) return null;
  const age = Date.now() / 1000 - Number(p.get("auth_date") || 0);
  if (!(age >= 0 && age < 24 * 3600)) return null;
  try { const id = JSON.parse(p.get("user") || "{}").id; return typeof id === "number" ? id : null; } catch { return null; }
}

// ---------- reading the screenshot
const parseJson = (txt: string) => JSON.parse(txt.slice(txt.indexOf("{"), txt.lastIndexOf("}") + 1));
async function readChart(image: string, media: string): Promise<Read> {
  const ak = Deno.env.get("ANTHROPIC_API_KEY"), gk = Deno.env.get("GEMINI_API_KEY");
  if (!ak && !gk) return { pro_visible: false, error: "no AI key set on the server" };
  try {
    if (ak) {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": ak, "anthropic-version": "2023-06-01", "content-type": "application/json" },
        body: JSON.stringify({ model: CLAUDE_MODEL, max_tokens: 500, messages: [{ role: "user", content: [
          { type: "image", source: { type: "base64", media_type: media, data: image } }, { type: "text", text: READ_PROMPT }] }] }),
      });
      if (!r.ok) return { pro_visible: false, error: `AI error ${r.status}: ${(await r.text()).slice(0, 160)}` };
      const o = await r.json();
      return applyChk(parseJson((o.content || []).map((c: { text?: string }) => c.text || "").join("")));
    }
    const errs: string[] = [];
    for (const mdl of [...new Set(GEMINI_MODELS)]) {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${mdl}:generateContent?key=${encodeURIComponent(gk!)}`, {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ contents: [{ role: "user", parts: [{ inline_data: { mime_type: media, data: image } }, { text: READ_PROMPT }] }],
          generationConfig: { temperature: 0, maxOutputTokens: 1500, responseMimeType: "application/json" } }),
      });
      if (!r.ok) { errs.push(`${mdl} ${r.status}`); if ([400, 403, 404, 429].includes(r.status)) continue; break; }
      const o = await r.json();
      const txt = (o.candidates || []).flatMap((c: { content?: { parts?: { text?: string; thought?: boolean }[] } }) =>
        (c.content?.parts || []).filter(p => !p.thought).map(p => p.text || "")).join("");
      return applyChk(parseJson(txt));
    }
    return { pro_visible: false, error: "AI: " + errs.join(", ") };
  } catch (e) {
    return { pro_visible: false, error: `could not read the screenshot (${String(e).slice(0, 120)})` };
  }
}

// ---------- live context from the bot's public files
async function liveCtx(): Promise<{ live: number | null; liveAgeS: number; events: unknown[] }> {
  const get = async (f: string) => { try { const r = await fetch(RAW + f + "?t=" + Date.now()); return r.ok ? await r.json() : {}; } catch { return {}; } };
  const [lv, nw] = await Promise.all([get("levels.json"), get("news.json")]);
  const t = Date.parse(String(lv.time || "").replace(" UTC", "Z").replace(" ", "T"));
  return { live: typeof lv.price === "number" ? lv.price : null, liveAgeS: Number.isFinite(t) ? (Date.now() - t) / 1000 : 1e9, events: nw.events || [] };
}

const khMidnightUtc = () => {
  const kh = new Date(Date.now() + 7 * 3600e3);
  return new Date(Date.UTC(kh.getUTCFullYear(), kh.getUTCMonth(), kh.getUTCDate()) - 7 * 3600e3).toISOString();
};
const n = (v: unknown) => (v === null || v === undefined || v === "" ? null : Number.isFinite(Number(v)) ? Number(v) : null);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  const token = Deno.env.get("TELEGRAM_TOKEN");
  if (!token) return json({ error: "server not set up yet (TELEGRAM_TOKEN)" }, 500);
  let b: Record<string, unknown>;
  try { b = await req.json(); } catch { return json({ error: "bad request" }, 400); }
  const user = await verify(String(b.initData || ""), token);
  if (!user) return json({ error: "Open this from the XAU.KH bot in Telegram." }, 401);
  const owner = Deno.env.get("TRADECHECK_OWNER_ONLY");
  if (owner && String(user) !== owner.trim()) return json({ error: "Trade check is in testing. Coming soon · មកដល់ឆាប់ៗ" }, 403);
  const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const action = String(b.action || "check");

  if (action === "list") {
    const { data, error } = await db.from("trade_checks")
      .select("id,created_at,side,entry,sl,tp,reason,verdict,checks,rr,taken,status,result_r")
      .eq("tg_user", user).order("created_at", { ascending: false }).limit(100);
    if (error) return json({ error: "db error" }, 500);
    const rows = data || [];
    const wk = rows.filter(r => Date.parse(r.created_at) > Date.now() - 7 * 864e5);
    const done = wk.filter(r => r.taken && r.result_r !== null);
    const sum = (rs: typeof done) => ({ trades: rs.length, r: Math.round(rs.reduce((a, r) => a + Number(r.result_r), 0) * 100) / 100 });
    return json({ checks: rows, week: { checks: wk.length, skipped: wk.filter(r => r.status === "skipped").length,
      followed: sum(done.filter(r => r.verdict !== "NO-GO")), overrode: sum(done.filter(r => r.verdict === "NO-GO")) } });
  }

  if (action === "mark") {
    const id = Number(b.id), took = !!b.taken;
    const { data } = await db.from("trade_checks").select("id,verdict,status").eq("id", id).eq("tg_user", user).limit(1);
    if (!data || !data.length) return json({ error: "not found" }, 404);
    if (data[0].status !== "checked") return json({ ok: true, already: true });
    await db.from("trade_checks").update({ taken: took, status: took ? "open" : "skipped" }).eq("id", id).eq("tg_user", user);
    return json({ ok: true, override: took && data[0].verdict === "NO-GO" });
  }

  // action === "check"
  const side = String(b.side || "").toUpperCase();
  if (side !== "BUY" && side !== "SELL") return json({ error: "Pick BUY or SELL." }, 400);
  const image = String(b.image || "");
  if (image.length < 1000) return json({ error: "Add a chart screenshot." }, 400);
  if (image.length > 8_000_000) return json({ error: "Screenshot too big. Try a smaller one." }, 400);
  const { count } = await db.from("trade_checks").select("id", { count: "exact", head: true })
    .eq("tg_user", user).gte("created_at", khMidnightUtc());
  if ((count || 0) >= PER_DAY) return json({ error: `Daily limit reached (${PER_DAY} checks). Tomorrow again · ថ្ងៃនេះអស់ហើយ` }, 429);

  const media = ["image/png", "image/webp", "image/jpeg"].includes(String(b.media)) ? String(b.media) : "image/jpeg";
  const [read, live] = await Promise.all([readChart(image, media), liveCtx()]);
  const { count: losses } = await db.from("trade_checks").select("id", { count: "exact", head: true })
    .eq("tg_user", user).eq("status", "loss").gte("closed_at", khMidnightUtc());
  const ctx: Ctx = { live: live.live, liveAgeS: live.liveAgeS, news: newsNear(live.events as never[], Date.now()), lossesToday: losses || 0 };
  const trade: Trade = { side: side as Side, entry: n(b.entry), sl: n(b.sl), tp: n(b.tp), reason: String(b.reason || "").slice(0, 300), auto: [] };
  const err = fill(trade, read, ctx);
  if (err) return json({ error: err }, 400);
  const res = evaluate(trade, read, ctx);
  const chartRead = Object.fromEntries(["bias", "score", "h1", "h4", "trigger", "wall_up", "wall_down", "poi_low", "poi_high",
    "price", "timeframe", "chk_ok", "pro_visible", "error"].map(k => [k, (read as Record<string, unknown>)[k] ?? null]));
  const { data: ins, error } = await db.from("trade_checks").insert({
    tg_user: user, side, entry: trade.entry, sl: trade.sl, tp: trade.tp, reason: trade.reason || null, verdict: res.verdict,
    checks: res.lines, chart_read: { ...chartRead, source: "app" }, live_price: live.live, rr: res.rr,
  }).select("id").limit(1);
  if (error) return json({ error: "Could not save the check." }, 500);
  return json({ id: ins?.[0]?.id, trade, result: res, read: chartRead });
});
