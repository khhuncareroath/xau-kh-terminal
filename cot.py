"""Big money in gold: the CFTC Commitments of Traders report (COMEX gold futures), managed money (hedge funds / CTAs).
Published every Friday 15:30 New York for the positions of the Tuesday before. Weekly context, not a timing tool.
Writes cot.json (latest week, change vs the previous week, and where the net position sits in its 1-year range).
Runs at most once every 6 hours; any failure is logged and skipped. Source: publicreporting.cftc.gov (dataset 72hh-3qpy)."""
import json
import os
import time
import urllib.parse
import urllib.request

URL = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
OUT = "cot.json"


def pick(rec, *need, avoid=("change", "pct", "spread", "old", "other", "traders")):
    for k in rec:
        kl = k.lower()
        if all(n in kl for n in need) and not any(a in kl for a in avoid):
            return k
    return None


def fetch():
    q = {"$where": "upper(market_and_exchange_names) like '%GOLD - COMMODITY EXCHANGE%'",
         "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": "53"}
    req = urllib.request.Request(URL + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "xau-kh-bot"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main():
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {}
    if time.time() - old.get("checked", 0) < 6 * 3600:
        return
    try:
        rows = fetch()
        r0 = rows[0]
        kl, ks = pick(r0, "m_money", "long", "all"), pick(r0, "m_money", "short", "all")
        koi, kd = pick(r0, "open_interest", "all"), pick(r0, "report_date")
        if not (kl and ks and kd):
            raise ValueError(f"fields not found in {list(r0)[:40]}")
        net = [int(float(r[kl])) - int(float(r[ks])) for r in rows if r.get(kl) and r.get(ks)]
        lo, hi = min(net), max(net)
        out = {"checked": time.time(), "date": r0[kd][:10], "long": int(float(r0[kl])), "short": int(float(r0[ks])),
               "net": net[0], "net_change": net[0] - net[1] if len(net) > 1 else None,
               "open_interest": int(float(r0[koi])) if koi and r0.get(koi) else None,
               "range_pct": round(100 * (net[0] - lo) / (hi - lo)) if hi > lo else None, "weeks": len(net)}
        json.dump(out, open(OUT, "w"), indent=1)
        print("cot:", out)
    except Exception as e:
        old["checked"] = time.time()
        old["error"] = str(e)[:300]
        json.dump(old, open(OUT, "w"), indent=1)
        print("cot failed:", e)


def cot_line(c):
    """One plain sentence for Telegram, or None."""
    if not c or c.get("net") is None or c.get("net_change") is None:
        return None
    ch, up = c["net_change"], c["net"] > 0
    more = (ch > 0) == up
    pos = c.get("range_pct")
    where = (" Their bet is near a 1-year high: if they start selling, gold can drop fast." if pos is not None and pos >= 85 else
             " Their bet is near a 1-year low: they have room to buy back." if pos is not None and pos <= 15 else "")
    return (f"🏦 Big funds (official CFTC data, {c['date']}): betting on gold going {'UP' if up else 'DOWN'} "
            f"({abs(c['net']):,} contracts). This week they made that bet {'bigger' if more else 'smaller'} "
            f"by {abs(ch):,}.{where}")


if __name__ == "__main__":
    main()
