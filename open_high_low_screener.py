"""
Nifty F&O Pure Stock Screener - Open = Low & Open = High
========================================================================
Features:
1. Pure Yahoo Finance 5-Minute Post-Open Entry Price Engine (09:20 AM IST)
2. Complete F&O Universe: Nifty100 + Nifty Midcap150 (250 stocks, dynamically fetched)
3. Intraday Open=Low (Bullish) & Open=High (Bearish) Setup Analytics
"""

import sys
import os
import time
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Complete F&O Universe: Nifty100 + Nifty Midcap150 ───────────────────────
# Fallback list (kept in sync with official NSE indices: Nifty100 + Midcap150)
# Correct tickers: ETERNAL (not ZOMATO), OBEROIRLTY (not OBEROIRALTY)
_NIFTY_FO_FALLBACK = [
    # Nifty 100 (Large Cap)
    "360ONE", "ABB", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER",
    "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT", "ATGL", "AUBANK", "AWL", "AXISBANK",
    "BAJAJ-AUTO", "BAJAJFINSV", "BAJAJHLDNG", "BAJFINANCE", "BANKBARODA", "BEL",
    "BHARTIARTL", "BPCL", "BRITANNIA", "CANBK", "CGPOWER", "CIPLA", "COALINDIA",
    "COFORGE", "COLPAL", "DABUR", "DALBHARAT", "DIVISLAB", "DIXON", "DLF", "DMART",
    "DRREDDY", "EICHERMOT", "ETERNAL", "FEDERALBNK", "GAIL", "GODREJCP", "GODREJPROP",
    "GRASIM", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDPETRO", "HINDUNILVR", "HUDCO", "HYUNDAI",
    "ICICIBANK", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "INDIGO", "INDUSINDBK",
    "INDUSTOWER", "INFY", "IOC", "IRCTC", "IRFC", "ITC", "JINDALSTEL", "JIOFIN",
    "JSWENERGY", "JSWSTEEL", "JUBLFOOD", "KALYANKJIL", "KOTAKBANK", "LT", "LUPIN",
    "M&M", "MARICO", "MARUTI", "MAXHEALTH", "MCX", "MFSL", "MOTHERSON", "MOTILALOFS",
    "MPHASIS", "MRF", "MUTHOOTFIN", "NAUKRI", "NESTLEIND", "NHPC", "NMDC", "NTPC",
    "NYKAA", "OBEROIRLTY", "OFSS", "OIL", "ONGC", "PAGEIND", "PATANJALI", "PAYTM",
    "PERSISTENT", "PETRONET", "PFC", "PHOENIXLTD", "PIDILITIND", "PIIND", "PNB",
    "POLICYBZR", "POLYCAB", "POWERGRID", "PRESTIGE", "RECLTD", "RELIANCE", "RVNL",
    "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SJVN",
    "SOLARINDS", "SRF", "SUNPHARMA", "SUZLON", "SWIGGY", "TATACONSUM", "TATAELXSI",
    "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TIINDIA", "TITAN", "TORNTPHARM",
    "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UNITDSPR", "UPL", "VBL", "VEDL",
    "VOLTAS", "WIPRO", "YESBANK", "ZYDUSLIFE",
    # Nifty Midcap 150
    "3MINDIA", "ABBOTINDIA", "ABCAPITAL", "ACC", "AIAENG", "AIIL", "AJANTPHARM",
    "ALKEM", "ANTHEM", "APARINDS", "APLAPOLLO", "APOLLOTYRE", "ASHOKLEY", "ASTRAL",
    "AUROPHARMA", "BAJAJHFL", "BALKRISIND", "BANKINDIA", "BDL", "BERGEPAINT",
    "BHARATFORG", "BHARTIHEXA", "BHEL", "BIOCON", "BLUESTARCO", "BSE", "COCHINSHIP",
    "COROMANDEL", "CRISIL", "ENDURANCE", "ENRIN", "ESCORTS", "EXIDEIND", "FLUOROCHEM",
    "FORTIS", "GICRE", "GLAXO", "GLENMARK", "GMRAIRPORT", "GODFRYPHLP", "GODREJIND",
    "GROWW", "GVT&D", "HDBFS", "HEXT", "HONAUT", "ICICIAMC", "ICICIGI",
    "INDIANB", "IPCALAB", "IREDA", "ITCHOTELS", "JKCEMENT", "JSL", "JSWINFRA",
    "KEI", "KPITTECH", "KPRMILL", "LAURUSLABS", "LENSKART", "LGEINDIA", "LICHSGFIN",
    "LICI", "LINDEINDIA", "LLOYDSME", "LTF", "LTM", "LTTS", "M&MFIN", "MAHABANK",
    "MANKIND", "MEDANTA", "NAM-INDIA", "NATIONALUM", "NIACL", "NLCINDIA",
    "NTPCGREEN", "PAGEIND", "PREMIERENE", "RADICO", "SAIL", "SCHAEFFLER",
    "SUNDARMFIN", "SUPREMEIND", "SWIGGY", "TATACOMM", "TATAINVEST", "THERMAX",
    "TITAGARH", "TMCV", "TMPV", "TORNTPOWER", "UNOMINDA", "VMM", "WAAREEENER",
    "TATACAP",
]

def _fetch_nse_index_symbols(index_csv_url, session):
    """Fetch stock symbols from a niftyindices.com CSV URL."""
    try:
        r = session.get(index_csv_url, timeout=10)
        if r.status_code == 200:
            import io
            df = pd.read_csv(io.StringIO(r.text))
            return df['Symbol'].tolist()
    except Exception:
        pass
    return []

def get_fno_universe():
    """
    Dynamically fetches the F&O universe from NSE (Nifty100 + Midcap150).
    Falls back to the hardcoded list if the fetch fails.
    """
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    base = 'https://niftyindices.com/IndexConstituent/'
    nifty100  = _fetch_nse_index_symbols(base + 'ind_nifty100list.csv', session)
    midcap150 = _fetch_nse_index_symbols(base + 'ind_niftymidcap150list.csv', session)
    combined  = list(dict.fromkeys(nifty100 + midcap150))  # deduplicate, preserve order
    if len(combined) >= 200:
        print(f"[✓] Fetched {len(nifty100)} Nifty100 + {len(midcap150)} Midcap150 = {len(combined)} unique F&O stocks from NSE.")
        return combined
    else:
        print(f"[!] NSE fetch returned only {len(combined)} stocks — using fallback list ({len(_NIFTY_FO_FALLBACK)} stocks).")
        return _NIFTY_FO_FALLBACK

NIFTY_FO_STOCKS = get_fno_universe()

def fetch_single_stock_5m(ticker, session):
    """
    Fetches official 1-day OHLC (matches Zerodha / TradingView 100%) and 5-minute candles for 5m Entry.
    """
    symbol = ticker if ticker.startswith("^") else f"{ticker}.NS"
    
    # ── 1. Fetch Official Daily OHLC (matches Zerodha & TradingView pre-market 100%) ──
    official_open = None
    official_high = None
    official_low  = None
    url_1d = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    try:
        r_1d = session.get(url_1d, timeout=5)
        if r_1d.status_code == 200:
            d_1d = r_1d.json()['chart']['result'][0]
            q_1d = d_1d['indicators']['quote'][0]
            if q_1d.get('open') and q_1d['open'][-1] is not None:
                official_open = float(q_1d['open'][-1])
                official_high = float(q_1d['high'][-1]) if q_1d.get('high') and q_1d['high'][-1] is not None else None
                official_low  = float(q_1d['low'][-1])  if q_1d.get('low')  and q_1d['low'][-1]  is not None else None
    except Exception:
        pass

    # ── 2. Fetch 5-Minute Candles for Intraday Entry & PnL ─────────────────────
    url_5m = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=5m"
    try:
        resp = session.get(url_5m, timeout=5)
        if resp.status_code != 200:
            return None
        
        data = resp.json()
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        indicators = result['indicators']['quote'][0]
        
        opens = indicators.get('open', [])
        highs = indicators.get('high', [])
        lows = indicators.get('low', [])
        closes = indicators.get('close', [])
        volumes = indicators.get('volume', [])
        
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        if not dates:
            return None
            
        today_date = dates[-1].date()
        today_indices = [i for i in range(len(dates)) if dates[i].date() == today_date and opens[i] is not None and closes[i] is not None]
        
        if not today_indices:
            return None
            
        first_idx = today_indices[0]
        latest_idx = today_indices[-1]
        
        entry_price = float(closes[first_idx])
        latest_close = float(closes[latest_idx])

        # Use Official Daily OHLC if available (matches Zerodha / TradingView 100%)
        day_open = official_open if official_open else float(opens[first_idx])
        day_high = official_high if official_high else float(max([highs[i] for i in today_indices if highs[i] is not None]))
        day_low  = official_low  if official_low  else float(min([lows[i] for i in today_indices if lows[i] is not None]))
        
        # ── Previous trading day indices ──────────────────────────────────────
        prev_indices = [i for i in range(len(dates)) if dates[i].date() < today_date and closes[i] is not None]
        if prev_indices:
            prev_close = float(closes[prev_indices[-1]])
            prev_day_date = max(dates[i].date() for i in prev_indices)
            prev_day_indices = [i for i in prev_indices if dates[i].date() == prev_day_date]
            prev_day_high = float(max(highs[i] for i in prev_day_indices if highs[i] is not None)) if prev_day_indices else 0.0
            prev_day_low  = float(min(lows[i]  for i in prev_day_indices if lows[i]  is not None)) if prev_day_indices else 0.0
        else:
            prev_close    = day_open
            prev_day_high = 0.0
            prev_day_low  = 0.0

        day_volume = sum([volumes[i] for i in today_indices if volumes[i] is not None])
        avg_vol = sum([v for v in volumes if v is not None]) / len(dates) * len(today_indices) if len(dates) > 0 else day_volume
        vol_surge = round(day_volume / avg_vol, 2) if avg_vol > 0 else 1.0
        
        chg_pct = round(((latest_close - prev_close) / prev_close) * 100, 2)
        
        return {
            "ticker": ticker,
            "day_open": round(day_open, 2),
            "entry_price": round(entry_price, 2),
            "day_high": round(day_high, 2),
            "day_low": round(day_low, 2),
            "latest_close": round(latest_close, 2),
            "prev_close": round(prev_close, 2),
            "prev_day_high": round(prev_day_high, 2),
            "prev_day_low": round(prev_day_low, 2),
            "change_pct": chg_pct,
            "volume": day_volume,
            "vol_surge": vol_surge
        }
    except Exception:
        return None

def fetch_all_stocks_parallel(tickers):
    print(f"[*] Parallel fetching 5-min candles for {len(set(tickers))} Nifty F&O & Momentum stocks via Yahoo Finance...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    
    results = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_ticker = {executor.submit(fetch_single_stock_5m, ticker, session): ticker for ticker in set(tickers)}
        for future in as_completed(future_to_ticker):
            res = future.result()
            if res:
                results[res["ticker"]] = res
                
    print(f"[✓] Successfully retrieved 5-min candles for {len(results)} stocks.")
    return results

def analyze_open_high_low(stock_dict, tolerance_pct=0.15):
    results = []
    scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for ticker, data in stock_dict.items():
        day_open     = data['day_open']
        entry_price  = data['entry_price']
        day_high     = data['day_high']
        day_low      = data['day_low']
        latest_close = data['latest_close']
        chg_pct      = data['change_pct']
        vol_surge    = data['vol_surge']
        day_volume   = data['volume']
        prev_day_high = data.get('prev_day_high', 0.0)
        prev_day_low  = data.get('prev_day_low', 0.0)
        
        if day_open <= 0:
            continue
            
        open_low_diff_pct = abs(day_open - day_low) / day_open * 100
        is_open_low = open_low_diff_pct <= tolerance_pct
        
        open_high_diff_pct = abs(day_open - day_high) / day_open * 100
        is_open_high = open_high_diff_pct <= tolerance_pct
        
        if not (is_open_low or is_open_high):
            continue

        setup_type = "OPEN_LOW" if is_open_low else "OPEN_HIGH"
        signal = "BULLISH (BUY)" if is_open_low else "BEARISH (SELL)"
        entry_move_pct = round(((entry_price - day_open) / day_open) * 100, 2)

        # ── Momentum Qualification Filter ─────────────────────────────────────
        # OPEN=LOW: 5-min close must break ABOVE previous day's high
        # OPEN=HIGH: 5-min close must break BELOW previous day's low
        momentum_confirmed = False
        if is_open_low and prev_day_high > 0:
            momentum_confirmed = entry_price > prev_day_high
        elif is_open_high and prev_day_low > 0:
            momentum_confirmed = entry_price < prev_day_low
        
        if is_open_low:
            stoploss = round(day_low * 0.997, 2)
            risk = round(entry_price - stoploss, 2)
            risk_amt = max(risk, round(entry_price * 0.005, 2))
            target_1 = round(entry_price + (risk_amt * 1.5), 2)
            target_2 = round(entry_price + (risk_amt * 2.5), 2)
            diff_from_open = round(open_low_diff_pct, 3)
            pnl_pct = round(((latest_close - entry_price) / entry_price) * 100, 2)
        else:
            stoploss = round(day_high * 1.003, 2)
            risk = round(stoploss - entry_price, 2)
            risk_amt = max(risk, round(entry_price * 0.005, 2))
            target_1 = round(entry_price - (risk_amt * 1.5), 2)
            target_2 = round(entry_price - (risk_amt * 2.5), 2)
            diff_from_open = round(open_high_diff_pct, 3)
            pnl_pct = round(((entry_price - latest_close) / entry_price) * 100, 2)
            
        vwap = round((day_high + day_low + latest_close) / 3, 2)
        above_vwap = latest_close >= vwap
        
        results.append({
            "ticker": ticker,
            "setup_type": setup_type,
            "signal": signal,
            "open": day_open,
            "high": day_high,
            "low": day_low,
            "entry_price": entry_price,
            "entry_move_pct": entry_move_pct,
            "ltp": latest_close,
            "pnl_pct": pnl_pct,
            "risk_per_share": risk_amt,
            "change_pct": chg_pct,
            "diff_from_open_pct": diff_from_open,
            "volume": day_volume,
            "vol_surge": vol_surge,
            "vwap": vwap,
            "above_vwap": above_vwap,
            "stoploss": stoploss,
            "target_1": target_1,
            "target_2": target_2,
            "exact_match": diff_from_open < 0.02,
            "momentum_confirmed": momentum_confirmed,
            "prev_day_high": round(prev_day_high, 2),
            "prev_day_low": round(prev_day_low, 2)
        })
        
    open_low_stocks  = [r for r in results if r["setup_type"] == "OPEN_LOW"]
    open_high_stocks = [r for r in results if r["setup_type"] == "OPEN_HIGH"]
    momentum_stocks  = [r for r in results if r["momentum_confirmed"]]

    open_low_stocks.sort(key=lambda x: (x["change_pct"], x["momentum_confirmed"], x["vol_surge"]), reverse=True)
    open_high_stocks.sort(key=lambda x: (x["change_pct"], x["momentum_confirmed"], x["vol_surge"]), reverse=True)
    momentum_stocks.sort(key=lambda x: (x["change_pct"], x["vol_surge"]), reverse=True)

    return {
        "scan_time": scan_time,
        "total_scanned": len(stock_dict),
        "open_low_count": len(open_low_stocks),
        "open_high_count": len(open_high_stocks),
        "momentum_count": len(momentum_stocks),
        "open_low_stocks": open_low_stocks,
        "open_high_stocks": open_high_stocks,
        "momentum_stocks": momentum_stocks,
        "all_matches": open_low_stocks + open_high_stocks
    }

def print_cli_table(results):
    momentum_stocks = results.get('momentum_stocks', [])
    print("\n" + "="*105)
    print(f"  NIFTY F&O INTRADAY YAHOO SCREENER | SCAN TIME: {results['scan_time']}")
    print(f"  Total Scanned: {results['total_scanned']} | Open=Low (Bullish): {results['open_low_count']} | Open=High (Bearish): {results['open_high_count']} | Momentum: {results.get('momentum_count', 0)}")
    print("="*105)

    print("\n[+] OPEN = LOW STOCKS (BULLISH BUY SETUPS - 5-MIN ENTRY):")
    print("-" * 105)
    print(f"{'Ticker':<12} {'Open (Rs)':<10} {'5m Entry':<12} {'LTP (Rs)':<10} {'PnL %':<8} {'Risk (Rs)':<10} {'Stoploss':<10} {'Target 1':<10} {'MOM':<5}")
    print("-" * 105)
    for s in results['open_low_stocks']:
        exact_star = "*" if s['exact_match'] else " "
        mom_flag   = "🔥" if s.get('momentum_confirmed') else "  "
        print(f"{s['ticker'] + exact_star:<12} {s['open']:<10.2f} {s['entry_price']:<12.2f} {s['ltp']:<10.2f} {s['pnl_pct']:<+8.2f} {s['risk_per_share']:<10.2f} {s['stoploss']:<10.2f} {s['target_1']:<10.2f} {mom_flag}")
    if not results['open_low_stocks']:
        print("  No Open=Low setups detected in current tolerance threshold.")

    print("\n[-] OPEN = HIGH STOCKS (BEARISH SELL SETUPS - 5-MIN ENTRY):")
    print("-" * 105)
    print(f"{'Ticker':<12} {'Open (Rs)':<10} {'5m Entry':<12} {'LTP (Rs)':<10} {'PnL %':<8} {'Risk (Rs)':<10} {'Stoploss':<10} {'Target 1':<10} {'MOM':<5}")
    print("-" * 105)
    for s in results['open_high_stocks']:
        exact_star = "*" if s['exact_match'] else " "
        mom_flag   = "🔥" if s.get('momentum_confirmed') else "  "
        print(f"{s['ticker'] + exact_star:<12} {s['open']:<10.2f} {s['entry_price']:<12.2f} {s['ltp']:<10.2f} {s['pnl_pct']:<+8.2f} {s['risk_per_share']:<10.2f} {s['stoploss']:<10.2f} {s['target_1']:<10.2f} {mom_flag}")
    if not results['open_high_stocks']:
        print("  No Open=High setups detected in current tolerance threshold.")

    if momentum_stocks:
        print("\n[🔥] MOMENTUM CONFIRMED STOCKS (5-MIN CLOSE CROSSES PREV DAY EXTREME):")
        print("-" * 105)
        print(f"{'Ticker':<12} {'Setup':<12} {'5m Entry':<12} {'Prev High':<12} {'Prev Low':<12} {'LTP (Rs)':<10} {'PnL %':<8} {'Target 1':<10}")
        print("-" * 105)
        for s in momentum_stocks:
            setup = "OPEN=LOW" if s['setup_type'] == 'OPEN_LOW' else "OPEN=HIGH"
            print(f"{s['ticker']:<12} {setup:<12} {s['entry_price']:<12.2f} {s['prev_day_high']:<12.2f} {s['prev_day_low']:<12.2f} {s['ltp']:<10.2f} {s['pnl_pct']:<+8.2f} {s['target_1']:<10.2f}")
    else:
        print("\n[🔥] No Momentum Confirmed stocks (5-min close did not cross prev day High/Low).")

    print("=" * 105 + "\n")

def run_screener(tolerance_pct=0.15):
    stock_dict = fetch_all_stocks_parallel(NIFTY_FO_STOCKS) or {}
    results = analyze_open_high_low(stock_dict, tolerance_pct=tolerance_pct)
    print_cli_table(results)
    
    json_path = os.path.join(os.path.dirname(__file__), "open_high_low_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    public_dir = os.path.join(os.path.dirname(__file__), "public")
    if os.path.exists(public_dir):
        public_json_path = os.path.join(public_dir, "open_high_low_data.json")
        with open(public_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    if results["all_matches"]:
        df_export = pd.DataFrame(results["all_matches"])
        csv_filename = f"open_high_low_screener_latest.csv"
        csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
        df_export.to_csv(csv_path, index=False)
        
    return results

if __name__ == "__main__":
    tolerance = 0.15
    if len(sys.argv) > 1:
        try:
            tolerance = float(sys.argv[1])
        except ValueError:
            pass
    run_screener(tolerance_pct=tolerance)
