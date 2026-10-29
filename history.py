"""History: saves every 5m candle into data/gc_5m.csv.gz so the backtest sample grows past Yahoo's 60-day limit.
Run each workflow cycle:  python history.py
The newest bar is dropped because it is still forming."""
import os

from engine import HIST, load_history


def main():
    df = load_history().iloc[:-1]
    os.makedirs("data", exist_ok=True)
    df.round(2).to_csv(HIST, compression="gzip")
    print(f"history: {len(df)} bars, {df.index[0]} -> {df.index[-1]}")


if __name__ == "__main__":
    main()
