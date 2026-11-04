"""Macro: dollar index and 10-year yield versus gold -> macro.json. Run: python macro.py
Needs yfinance (already used by most gold engines; add 'yfinance' to requirements.txt if missing)."""
import json
from datetime import datetime, timezone
import yfinance as yf

def series(t):
    d = yf.download(t, period="5d", interval="1h", progress=False, auto_adjust=True)
    return d["Close"].squeeze().dropna()

def main():
    dx, ty, gc = series("DX-Y.NYB"), series("^TNX"), series("GC=F")
    dxc = (dx.iloc[-1] / dx.iloc[-24] - 1) * 100
    tyc = (ty.iloc[-1] - ty.iloc[-24]) * 100          # basis points
    gcc = (gc.iloc[-1] / gc.iloc[-24] - 1) * 100
    score = (-1 if dxc > .15 else 1 if dxc < -.15 else 0) + (-1 if tyc > 3 else 1 if tyc < -3 else 0)
    verdict = "Supports gold up" if score > 0 else "Supports gold down" if score < 0 else "Mixed signals"
    note = f"Dollar {dxc:+.2f}% and 10y yield {tyc:+.0f}bp in 24h: {verdict.lower()}"
    if score < 0 and gcc > .3 or score > 0 and gcc < -.3:
        note += ". Gold is moving against both, so the move is less trustworthy"
    dx5 = (dx.iloc[-1] / dx.iloc[0] - 1) * 100
    ty5 = (ty.iloc[-1] - ty.iloc[0]) * 100
    gc5 = (gc.iloc[-1] / gc.iloc[0] - 1) * 100
    out = {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "dxy": {"last": round(float(dx.iloc[-1]), 2), "chg_pct": round(float(dxc), 2), "chg_5d_pct": round(float(dx5), 2)},
           "us10y": {"last": round(float(ty.iloc[-1]), 3), "chg_bp": round(float(tyc), 1), "chg_5d_bp": round(float(ty5), 1)},
           "gold_chg_5d_pct": round(float(gc5), 2),
           "gold_chg_pct": round(float(gcc), 2), "score": score, "verdict": verdict, "note": note}
    try:   # risk mood: stock-market fear (VIX) and the S&P 500; fear often brings safe-haven buying in gold
        vx, sp = series("^VIX"), series("ES=F")
        out["vix"] = {"last": round(float(vx.iloc[-1]), 1), "chg_pct": round(float((vx.iloc[-1] / vx.iloc[-24] - 1) * 100), 1)}
        out["spx"] = {"chg_pct": round(float((sp.iloc[-1] / sp.iloc[-24] - 1) * 100), 2)}
    except Exception as e:
        print("risk mood unavailable:", e)
    json.dump(out, open("macro.json", "w"), indent=2); print(note)

if __name__ == "__main__":
    main()
