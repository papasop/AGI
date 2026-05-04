"""
fetch_data.py
=============
Fetch OHLC data for the Global AI Hedge components plus the
historical CNY/USD and HKD/USD spot rates, and write data.json next to
index.html.

Index inception: 2022-11-30 (ChatGPT public launch). Base = 100.

Index composition:
    纽约时报        NYT          USD    50.0%
    拼多多          PDD          USD    25.0%
    比亚迪          002594.SZ    CNY    25.0%

Calendar handling
-----------------
Each component trades on a different exchange with a different holiday
calendar. The anchor calendar is BYD ∩ NYT (two liquid anchors with full history);
all other components are reindexed to that calendar.

For any component whose listing post-dates the start of the anchor calendar,
pre-IPO dates are back-filled with the first known close. This means that
component contributes a CONSTANT value to the index until it actually starts
trading. The distortion is bounded by its index weight and documented in the
JSON meta payload.

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
    # CN names, short, ticker, currency, sleeve, status.
    {"name": "\u7ebd\u7ea6\u65f6\u62a5", "short": "NYT", "ticker": "NYT", "ccy": "USD", "sleeve": "US", "status": "active"},
    {"name": "\u62fc\u591a\u591a", "short": "PDD", "ticker": "PDD", "ccy": "USD", "sleeve": "CN", "status": "active"},
    {"name": "\u6bd4\u4e9a\u8fea", "short": "BYD", "ticker": "002594.SZ", "ccy": "CNY", "sleeve": "CN", "status": "active"},
]

TARGET_WEIGHTS = {
    "NYT": 0.50,
    "PDD": 0.25,
    "002594.SZ": 0.25,
}

SYNTHETIC_FALLBACKS = {}


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


def generate_synthetic_yield(index: pd.Index, seed: int, base: float,
                             daily_vol: float, drift: float,
                             floor: float, ceiling: float) -> pd.DataFrame:
    rng = mulberry32(seed)
    close = base
    rows = []
    for _ in index:
        change = (rng() - 0.5) * 2 * daily_vol + drift
        open_ = close + (rng() - 0.5) * daily_vol * 0.35
        close = min(ceiling, max(floor, open_ + change))
        wick = (rng() * 0.5 + 0.2) * daily_vol
        high = min(ceiling, max(open_, close) + wick)
        low = max(floor, min(open_, close) - wick)
        rows.append({"Open": open_, "High": high, "Low": low, "Close": close})
    return pd.DataFrame(rows, index=index)


def fetch_ohlc(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, progress=False,
                     auto_adjust=False, threads=False)
    if df.empty:
        print(f"  WARNING: empty result for {ticker}")
        return pd.DataFrame(columns=["Open", "High", "Low", "Close"])
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    df.index = df.index.strftime("%Y-%m-%d")
    return df


def fetch_fx(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, progress=False,
                     auto_adjust=False, threads=False)
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


def normalize_tnx(df: pd.DataFrame) -> pd.DataFrame:
    # Yahoo's ^TNX is often quoted as yield * 10 (e.g. 43.5 = 4.35%).
    if df.empty:
        return df
    out = df.copy()
    if out["Close"].median() > 20:
        out[["Open", "High", "Low", "Close"]] = out[["Open", "High", "Low", "Close"]] / 10.0
    return out


def futures_price_to_implied_rate(df: pd.DataFrame) -> pd.DataFrame:
    # 30-Day Fed Funds futures are quoted as 100 minus the expected
    # average effective fed funds rate for the delivery month.
    if df.empty:
        return df
    out = pd.DataFrame(index=df.index)
    out["Open"] = 100.0 - df["Open"]
    out["High"] = 100.0 - df["Low"]
    out["Low"] = 100.0 - df["High"]
    out["Close"] = 100.0 - df["Close"]
    return out[["Open", "High", "Low", "Close"]]


def fetch_fed_funds_apr27(start: str, end: str) -> tuple[pd.DataFrame, str, str]:
    # Yahoo sometimes exposes only the continuous ZQ contract. Try the named
    # Apr-2027 symbols first, then fall back to the continuous contract.
    candidates = [
        ("ZQJ27.CBT", "Yahoo Finance named contract"),
        ("ZQJ2027.CBT", "Yahoo Finance named contract"),
        ("ZQJ27.CME", "Yahoo Finance named contract"),
        ("ZQ=F", "Yahoo Finance continuous 30-Day Fed Funds futures fallback"),
    ]
    for ticker, source_note in candidates:
        print(f"Fetching Fed Funds Apr27 ({ticker}) ...")
        df = fetch_ohlc(ticker, start, end)
        if not df.empty:
            return futures_price_to_implied_rate(df), ticker, source_note
    return pd.DataFrame(columns=["Open", "High", "Low", "Close"]), "ZQJ27", (
        "Synthetic fallback used because named and continuous yfinance tickers returned no data."
    )


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
    for component in COMPONENTS:
        name, short, ticker, ccy = component["name"], component["short"], component["ticker"], component["ccy"]
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

    # 3b) Fetch benchmark, aligned to the same anchor calendar.
    print("Fetching benchmark NASDAQ (^IXIC) ...")
    nasdaq = fetch_ohlc("^IXIC", args.start, args.end)
    if nasdaq.empty:
        print("  WARNING: empty benchmark result for ^IXIC")
    nasdaq_aligned = nasdaq.reindex(common).ffill().bfill()
    if nasdaq_aligned.isna().any().any():
        raise SystemExit("NASDAQ benchmark data missing; cannot align ^IXIC.")

    # 3c) Macro yield pane. US10Y uses Yahoo ^TNX when available; CN10Y
    # is a local synthetic curve because yfinance does not expose a stable
    # China 10Y government-bond ticker.
    print("Fetching yield US10Y (^TNX) ...")
    us10y = normalize_tnx(fetch_ohlc("^TNX", args.start, args.end))
    if us10y.empty:
        print("  WARNING: empty yield result for ^TNX; using synthetic fallback")
        us10y = generate_synthetic_yield(common, 2026, 3.70, 0.035, 0.0002, 2.0, 6.0)
    us10y_aligned = us10y.reindex(common).ffill().bfill()
    if us10y_aligned.isna().any().any():
        raise SystemExit("US10Y yield data missing; cannot align ^TNX.")
    print("Building yield CN10Y synthetic curve ...")
    cn10y_aligned = generate_synthetic_yield(common, 1010, 2.85, 0.025, -0.0005, 1.5, 4.0)
    print("Fetching Fed Funds Apr '27 implied rate (ZQJ27) ...")
    fed_funds, fed_funds_source, fed_funds_note = fetch_fed_funds_apr27(args.start, args.end)
    if fed_funds.empty:
        print("  WARNING: empty Fed Funds futures result; using synthetic fallback")
        fed_funds = generate_synthetic_yield(common, 202704, 3.08, 0.018, -0.00015, 1.0, 6.0)
    fed_funds_aligned = fed_funds.reindex(common).ffill().bfill()
    if fed_funds_aligned.isna().any().any():
        raise SystemExit("Fed Funds Apr27 implied-rate data missing; cannot align ZQJ27.")

    # 4) Align each component; back/forward-fill late-IPO gaps
    components_out = []
    pending_components = []
    fallback_notes = {}
    for component in COMPONENTS:
        name, short, ticker, ccy = component["name"], component["short"], component["ticker"], component["ccy"]
        status = component.get("status", "active")
        df = fetched[ticker]
        if status == "prelist" and df.empty:
            pending_components.append({
                "name": name,
                "short": short,
                "ticker": ticker,
                "ccy": ccy,
                "sleeve": component.get("sleeve"),
                "status": "prelist",
                "note": "Pre-listing watch code; excluded until exchange data exists.",
            })
            print(f"  {short:15s}: pre-listing watch only; excluded until data exists")
            continue
        if status == "prelist" and not df.empty:
            status = "active"
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
            "weight": TARGET_WEIGHTS.get(ticker, 0.0), "ccy": ccy,
            "sleeve": component.get("sleeve"),
            "status": status,
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
            "pending_components": pending_components,
            "weighting_policy": "Fixed target weights: NYT 50%, PDD 25%, 002594.SZ 25%.",
        },
        "components": components_out,
        "fx": {
            "CNY": [{"date": idx, "rate": float(r)} for idx, r in fx_cny.items()],
            "HKD": [{"date": idx, "rate": float(r)} for idx, r in fx_hkd.items()],
        },
        "benchmarks": {
            "NASDAQ": {
                "name": "Nasdaq Composite",
                "ticker": "^IXIC",
                "data": to_records(nasdaq_aligned),
            },
        },
        "yields": {
            "CN10Y": {
                "name": "China 10Y Government Bond Yield",
                "ticker": "CN10Y_SYNTH",
                "synthetic_fallback": "Synthetic local curve; yfinance has no stable China 10Y ticker.",
                "data": to_records(cn10y_aligned),
            },
            "US10Y": {
                "name": "US 10Y Treasury Yield",
                "ticker": "^TNX",
                "data": to_records(us10y_aligned),
            },
            "FEDFUNDS_APR27": {
                "name": "Fed Funds Apr '27 Implied Rate",
                "ticker": "ZQJ27",
                "source_ticker": fed_funds_source,
                "source_note": fed_funds_note,
                "quote_formula": "implied_rate = 100 - futures_price",
                "barchart_url": "https://www.barchart.com/futures/quotes/ZQJ27/interactive-chart",
                "tradingview_symbol": "CBOT:ZQJ2027",
                "data": to_records(fed_funds_aligned),
            },
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
    print(f"  NASDAQ:     {nasdaq_aligned['Close'].iloc[0]:.2f} \u2192 "
          f"{nasdaq_aligned['Close'].iloc[-1]:.2f}  "
          f"({(nasdaq_aligned['Close'].iloc[-1]/nasdaq_aligned['Close'].iloc[0] - 1) * 100:+.2f}%)")
    print(f"  CN10Y:      {cn10y_aligned['Close'].iloc[0]:.3f}% \u2192 "
          f"{cn10y_aligned['Close'].iloc[-1]:.3f}%")
    print(f"  US10Y:      {us10y_aligned['Close'].iloc[0]:.3f}% \u2192 "
          f"{us10y_aligned['Close'].iloc[-1]:.3f}%")
    print(f"  ZQJ27:      {fed_funds_aligned['Close'].iloc[0]:.3f}% \u2192 "
          f"{fed_funds_aligned['Close'].iloc[-1]:.3f}% implied "
          f"(source: {fed_funds_source})")


if __name__ == "__main__":
    main()
