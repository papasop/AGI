"""
fetch_data.py
=============
Fetch OHLC data for the Leading China AI Index components plus the
historical CNY/USD and HKD/USD spot rates, and write data.json next to
index.html.

Index inception: 2022-11-30 (ChatGPT public launch). Base = 100.

Index composition:
    比亚迪          002594.SZ    CNY    10.0%
    拼多多          PDD          USD    10.0%
    福晶科技        002222.SZ    CNY    10.0%
    曦智科技-P      01879.HK     HKD    10.0%   (IPO'd 2026-04-28)
    拓荆科技        688072.SS    CNY    10.0%
    纽约时报        NYT          USD    50.0%

Calendar handling
-----------------
Each component trades on a different exchange with a different holiday
calendar, and 曦智科技 (Lightelligence) IPO'd literally days ago. The
anchor calendar is BYD ∩ NYT (two liquid anchors with full history);
all other components are reindexed to that calendar.

For components whose listing post-dates the start of the anchor calendar
(Piotech 2022, Lightelligence 2026), pre-IPO dates are back-filled with
the first known close. This means those components contribute a CONSTANT
value to the index until they actually start trading. The distortion is
bounded by their weight (10% each) and clearly documented in the JSON
meta payload.

Usage:
    pip install yfinance pandas
    python fetch_data.py [--start 2022-11-30] [--end 2026-04-30]
"""
import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf


COMPONENTS = [
    # (CN name,    short,            ticker,         weight, ccy)
    ("\u6bd4\u4e9a\u8fea",      "BYD",            "002594.SZ", 0.10, "CNY"),
    ("\u62fc\u591a\u591a",      "PDD",            "PDD",       0.10, "USD"),
    ("\u798f\u6676\u79d1\u6280", "Fujing",        "002222.SZ", 0.10, "CNY"),
    ("\u66e6\u667a\u79d1\u6280-P", "Lightelligence", "01879.HK",  0.10, "HKD"),
    ("\u62d3\u8346\u79d1\u6280", "Piotech",       "688072.SS", 0.10, "CNY"),
    ("\u7eb1\u7ea6\u65f6\u62a5", "NYT",           "NYT",       0.50, "USD"),
]

SYNTHETIC_FALLBACKS = {
    # Yahoo Finance may not expose this newly listed HK ticker yet.
    "01879.HK": {
        "seed": 11,
        "base": 30,
        "vol": 0.028,
        "drift": 0.00220,
        "start": "2026-04-28",
        "note": "Synthetic fallback used because yfinance returned no data.",
    },
}


def mulberry32(seed: int):
    def rand() -> float:
        nonlocal seed
        seed = (seed + 0x6D2B79F5) & 0xFFFFFFFF
        t = seed
        t = (t ^ (t >> 15)) * (t | 1)
        t &= 0xFFFFFFFF
        t ^= (t + ((t ^ (t >> 7)) * (t | 61))) & 0xFFFFFFFF
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rand


def generate_synthetic_ohlc(index: pd.Index, seed: int, base: float,
                            daily_vol: float, drift: float) -> pd.DataFrame:
    rng = mulberry32(seed)
    close = base
    rows = []
    for idx in index:
        ret = (rng() - 0.5) * 2 * daily_vol + drift
        open_ = close * (1 + (rng() - 0.5) * 0.004)
        new_close = open_ * (1 + ret)
        wick_frac = (rng() * 0.5 + 0.2) * daily_vol
        high = max(open_, new_close) * (1 + wick_frac)
        low = min(open_, new_close) * (1 - wick_frac)
        rows.append({"Open": open_, "High": high, "Low": low, "Close": new_close})
        close = new_close
    return pd.DataFrame(rows, index=index)


def fetch_ohlc(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        print(f"  WARNING: empty result for {ticker}")
        return pd.DataFrame(columns=["Open", "High", "Low", "Close"])
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    df.index = df.index.strftime("%Y-%m-%d")
    return df


def fetch_fx(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise SystemExit(f"FX series unavailable: {ticker}")
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    s = df["Close"].dropna()
    s.index = s.index.strftime("%Y-%m-%d")
    return s


def to_records(df: pd.DataFrame) -> list:
    return [
        {"date": idx,
         "open":  float(r["Open"]),
         "high":  float(r["High"]),
         "low":   float(r["Low"]),
         "close": float(r["Close"])}
        for idx, r in df.iterrows()
    ]


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2022-11-30",
                    help="Index inception (default: ChatGPT public launch)")
    ap.add_argument("--end",   default=date.today().isoformat())
    ap.add_argument("--out",   default=str(script_dir / "data.json"))
    args = ap.parse_args()

    # 1) Fetch all stock OHLC
    fetched = {}
    for name, short, ticker, weight, ccy in COMPONENTS:
        print(f"Fetching {short:15s} ({ticker:12s}, {ccy}) ...")
        fetched[ticker] = fetch_ohlc(ticker, args.start, args.end)

    # 2) Anchor calendar = BYD \u2229 NYT (liquid full-history anchors)
    byd = fetched["002594.SZ"]
    nyt = fetched["NYT"]
    if byd.empty or nyt.empty:
        raise SystemExit("BYD or NYT data missing; cannot establish anchor calendar.")
    common = byd.index.intersection(nyt.index)
    print(f"Anchor calendar: {len(common)} common BYD\u2229NYT days "
          f"({common[0]} \u2192 {common[-1]})")

    # 3) Fetch FX, align to anchor calendar
    print("Fetching FX  CNY=X (CNY per USD) ...")
    fx_cny = fetch_fx("CNY=X", args.start, args.end)
    print("Fetching FX  HKD=X (HKD per USD) ...")
    fx_hkd = fetch_fx("HKD=X", args.start, args.end)
    fx_cny = fx_cny.reindex(common).ffill().bfill()
    fx_hkd = fx_hkd.reindex(common).ffill().bfill()

    # 4) Align each component; back/forward-fill late-IPO gaps
    components_out = []
    fallback_notes = {}
    for name, short, ticker, weight, ccy in COMPONENTS:
        df = fetched[ticker]
        if df.empty and ticker in SYNTHETIC_FALLBACKS:
            fb = SYNTHETIC_FALLBACKS[ticker]
            fb_index = common[common >= fb["start"]]
            if len(fb_index) == 0:
                fb_index = common[-1:]
            df = generate_synthetic_ohlc(
                fb_index, fb["seed"], fb["base"], fb["vol"], fb["drift"]
            )
            fallback_notes[ticker] = fb["note"]
            print(f"  {short:15s}: using synthetic fallback from {fb_index[0]}")
        inception = df.index.min() if len(df) else None
        # Reindex to common, then ffill (post-IPO holidays) + bfill (pre-IPO)
        df_aligned = df.reindex(common).ffill().bfill()
        if df_aligned.isna().any().any():
            raise SystemExit(f"Could not back-fill {ticker} \u2014 series is empty?")
        components_out.append({
            "name": name, "short": short, "ticker": ticker,
            "weight": weight, "ccy": ccy,
            "inception": inception,
            "synthetic_fallback": fallback_notes.get(ticker),
            "data": to_records(df_aligned),
        })
        late = " (back-filled pre-IPO!)" if inception and inception > common[0] else ""
        print(f"  {short:15s}: aligned to {len(df_aligned)} days, "
              f"real history from {inception}{late}")

    # 5) Write JSON
    payload = {
        "meta": {
            "start": args.start,
            "end":   args.end,
            "n":     len(common),
            "calendar_anchors": ["002594.SZ", "NYT"],
            "fx_unit_CNY": "CNY per USD (yfinance: CNY=X)",
            "fx_unit_HKD": "HKD per USD (yfinance: HKD=X)",
            "note": ("Pre-inception dates of late-listed components are "
                     "back-filled with their first known close. The index "
                     "therefore inherits a constant contribution from those "
                     "components prior to their actual IPO."),
            "synthetic_fallbacks": fallback_notes,
        },
        "components": components_out,
        "fx": {
            "CNY": [{"date": idx, "rate": float(r)} for idx, r in fx_cny.items()],
            "HKD": [{"date": idx, "rate": float(r)} for idx, r in fx_hkd.items()],
        },
    }
    with open(args.out, "w") as f:
        json.dump(payload, f, separators=(",", ":"))

    weights_sum = sum(c["weight"] for c in components_out)
    print(f"\nWrote {args.out}")
    print(f"  Components: {len(components_out)} | weights sum: {weights_sum:.3f}")
    print(f"  CNY/USD:    {fx_cny.iloc[0]:.4f} \u2192 {fx_cny.iloc[-1]:.4f}  "
          f"({(fx_cny.iloc[-1]/fx_cny.iloc[0] - 1) * 100:+.2f}%)")
    print(f"  HKD/USD:    {fx_hkd.iloc[0]:.4f} \u2192 {fx_hkd.iloc[-1]:.4f}  "
          f"({(fx_hkd.iloc[-1]/fx_hkd.iloc[0] - 1) * 100:+.2f}%)")


if __name__ == "__main__":
    main()
