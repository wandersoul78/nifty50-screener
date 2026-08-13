"""
Combined Nifty F&O Stock, Nifty Options, Bank Nifty Options & Top Stock Options Pure Screener
========================================================================
Features:
1. Pure Yahoo Finance 5-Minute Post-Open Entry Engine for F&O Stock Universe (250 stocks).
2. Live NSE Options Engine for Nifty 50 Options (index=nse50_opt, step=50).
3. Live NSE Options Engine for Bank Nifty Options (index=nifty_bank_opt, step=100).
4. Live NSE Engine for Top Traded Stock Options (index=stock_opt).
5. Dynamic Expiry Selector & Output saved to combined_screener_data.json.
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
    "NTPCGREEN", "PREMIERENE", "RADICO", "SAIL", "SCHAEFFLER",
    "SUNDARMFIN", "SUPREMEIND", "TATACOMM", "TATAINVEST", "THERMAX",
    "TITAGARH", "TMCV", "TMPV", "TORNTPOWER", "UNOMINDA", "VMM", "WAAREEENER",
    "TATACAP"
]


def fetch_single_stock_5m(ticker):
    """Fetches official 1-day OHLC and 5-minute intraday candles for stock screening."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    symbol = ticker if ticker.startswith("^") else f"{ticker}.NS"
    
    official_open, official_high, official_low = None, None, None
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

    url_5m = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=5m"
    try:
        resp = session.get(url_5m, timeout=5)
        if resp.status_code != 200:
            return None
        
        data = resp.json()
        result = data['chart']['result'][0]
        timestamps = result.get('timestamp')
        if not timestamps:
            return None
        indicators = result['indicators']['quote'][0]
        
        opens   = indicators.get('open', [])
        highs   = indicators.get('high', [])
        lows    = indicators.get('low', [])
        closes  = indicators.get('close', [])
        volumes = indicators.get('volume', [])
        
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        if not dates:
            return None
            
        today_date = dates[-1].date()
        today_indices = [i for i in range(len(dates)) if dates[i].date() == today_date and opens[i] is not None and closes[i] is not None]
        
        if not today_indices:
            return None
            
        first_idx  = today_indices[0]
        latest_idx = today_indices[-1]
        
        entry_price  = float(closes[first_idx])
        latest_close = float(closes[latest_idx])

        day_open = official_open if official_open else float(opens[first_idx])
        day_high = official_high if official_high else float(max(highs[i] for i in today_indices if highs[i] is not None))
        day_low  = official_low  if official_low  else float(min(lows[i]  for i in today_indices if lows[i]  is not None))

        prev_indices = [i for i in range(len(dates)) if dates[i].date() < today_date and closes[i] is not None]
        if prev_indices:
            prev_close = float(closes[prev_indices[-1]])
        else:
            prev_close = day_open

        day_volume = sum(volumes[i] for i in today_indices if volumes[i] is not None)

        return {
            'ticker': ticker,
            'symbol': symbol,
            'date': str(today_date),
            'open': round(day_open, 2),
            'high': round(day_high, 2),
            'low': round(day_low, 2),
            'latest_close': round(latest_close, 2),
            'prev_close': round(prev_close, 2),
            'entry_price_5m': round(entry_price, 2),
            'volume': day_volume
        }
    except Exception:
        return None


def analyze_stock_open_high_low(stock, tolerance_pct=0.00):
    """Evaluates if stock meets 100% exact Open=Low (Bullish) or Open=High (Bearish) setup."""
    op = stock['open']
    hi = stock['high']
    lo = stock['low']
    close = stock['latest_close']
    entry = stock['entry_price_5m']
    prev_close = stock['prev_close']

    if op == 0:
        return None

    diff_low_pts  = abs(op - lo)
    diff_high_pts = abs(hi - op)

    diff_low_pct  = (diff_low_pts / op) * 100
    diff_high_pct = (diff_high_pts / op) * 100

    setup_type = None
    exact_match = False
    
    # 100% Exact Open = Low and Open = High check for Stocks
    if diff_low_pct <= tolerance_pct:
        setup_type = "OPEN_LOW"
        exact_match = (diff_low_pts == 0)
    elif diff_high_pct <= tolerance_pct:
        setup_type = "OPEN_HIGH"
        exact_match = (diff_high_pts == 0)

    if not setup_type:
        return None

    if setup_type == "OPEN_LOW":
        signal = "BULLISH"
        direction = "BUY"
        target = round(entry * 1.015, 2)
        stop_loss = round(op * 0.995, 2)
        diff_pct = diff_low_pct
        diff_pts = diff_low_pts
        pnl_pct = round(((close - entry) / entry) * 100, 2)
    else:
        signal = "BEARISH"
        direction = "SELL"
        target = round(entry * 0.985, 2)
        stop_loss = round(op * 1.005, 2)
        diff_pct = diff_high_pct
        diff_pts = diff_high_pts
        pnl_pct = round(((entry - close) / entry) * 100, 2)

    change_pct = round(((close - prev_close) / prev_close) * 100, 2)

    return {
        'ticker': stock['ticker'],
        'signal': signal,
        'direction': direction,
        'setup': setup_type,
        'exact_match': exact_match,
        'open': op,
        'high': hi,
        'low': lo,
        'latest_close': close,
        'entry_price_5m': entry,
        'target': target,
        'stop_loss': stop_loss,
        'pnl_pct': pnl_pct,
        'diff_from_open_pct': round(diff_pct, 3),
        'diff_pts': round(diff_pts, 2),
        'day_change_pct': change_pct,
        'volume': stock['volume']
    }


def fetch_nse_index_options(index_code="nse50_opt"):
    """
    Fetches live options data from NSE API for index_code:
    - 'nse50_opt' -> Nifty 50 Options
    - 'nifty_bank_opt' -> Bank Nifty Options
    - 'stock_opt' -> Top Active Stock Options
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nseindia.com/option-chain',
        'X-Requested-With': 'XMLHttpRequest'
    })
    try:
        session.get("https://www.nseindia.com/option-chain", timeout=10)
        time.sleep(0.5)
        url = f"https://www.nseindia.com/api/liveEquity-derivatives?index={index_code}"
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[!] NSE API fetch error ({index_code}): {e}")
    return None


def process_index_options(raw_opt, target_underlying="NIFTY", strike_step=50, num_strikes=6, option_max_tick=0.00, selected_expiry=None):
    """Processes option chain data for a specific index (NIFTY or BANKNIFTY) with 100% exact Open=Low / Open=High logic."""
    opt_matches = []
    opt_matrix = []
    available_expiries = []
    spot_price = 0.0
    atm_strike = 0
    active_expiry = "N/A"

    if not raw_opt or 'data' not in raw_opt:
        return {
            'spot_price': spot_price,
            'atm_strike': atm_strike,
            'active_expiry': active_expiry,
            'available_expiries': available_expiries,
            'opt_matches': opt_matches,
            'opt_matrix': opt_matrix
        }

    all_contracts = raw_opt['data']
    contracts = [c for c in all_contracts if c.get('underlying') == target_underlying]

    if contracts:
        spot_price = float(contracts[0].get('underlyingValue', 0.0))
        atm_strike = int(round(spot_price / float(strike_step)) * strike_step)
        min_strike = atm_strike - (num_strikes * strike_step)
        max_strike = atm_strike + (num_strikes * strike_step)

        def _parse_expiry(exp_str):
            try:
                return datetime.datetime.strptime(exp_str, "%d-%b-%Y").date()
            except Exception:
                return datetime.date.max

        exp_strings = list(set(c.get('expiryDate') for c in contracts if c.get('expiryDate')))
        exp_strings.sort(key=_parse_expiry)
        available_expiries = exp_strings

        if selected_expiry and selected_expiry in available_expiries:
            active_expiry = selected_expiry
        else:
            active_expiry = available_expiries[0] if available_expiries else "N/A"

        for c in contracts:
            if c.get('expiryDate') != active_expiry:
                continue

            strike = c.get('strikePrice', 0)
            if min_strike <= strike <= max_strike:
                opt_type = "CE" if c.get('optionType') in ["Call", "CE"] else "PE"
                op = float(c.get('openPrice', 0.0))
                hi = float(c.get('highPrice', 0.0))
                lo = float(c.get('lowPrice', 0.0))
                ltp = float(c.get('lastPrice', 0.0))
                oi = int(c.get('openInterest', 0))
                vol = int(c.get('volume', 0))

                if op == 0 or ltp == 0:
                    continue

                low_diff_pts = abs(op - lo)
                high_diff_pts = abs(hi - op)

                setup = None
                signal_type = None

                # Exact Open = Low and Open = High check for Index Options
                if low_diff_pts <= option_max_tick:
                    setup = "OPEN=LOW"
                    signal_type = "BULLISH"
                elif high_diff_pts <= option_max_tick:
                    setup = "OPEN=HIGH"
                    signal_type = "BEARISH"

                offset = strike - atm_strike
                offset_str = f"+{offset}" if offset > 0 else str(offset)

                contract_info = {
                    'symbol': f"{target_underlying} {strike} {opt_type}",
                    'underlying': target_underlying,
                    'option_type': opt_type,
                    'strike': strike,
                    'expiry': active_expiry,
                    'setup': setup if setup else "NONE",
                    'signal': signal_type if signal_type else "NEUTRAL",
                    'open': op,
                    'high': hi,
                    'low': lo,
                    'ltp': ltp,
                    'diff_pts': round(low_diff_pts if setup == "OPEN=LOW" else (high_diff_pts if setup == "OPEN=HIGH" else 0), 2),
                    'open_interest': oi,
                    'volume': vol,
                    'atm_offset': offset_str
                }

                opt_matrix.append(contract_info)
                if setup:
                    opt_matches.append(contract_info)

    return {
        'spot_price': spot_price,
        'atm_strike': atm_strike,
        'active_expiry': active_expiry,
        'available_expiries': available_expiries,
        'opt_matches': opt_matches,
        'opt_matrix': opt_matrix
    }


def process_top_stock_options(raw_stock_opt, max_tick_diff=0.50):
    """Processes Top Active Stock Options from NSE index=stock_opt API."""
    stock_opt_matches = []
    all_stock_contracts = []

    if not raw_stock_opt or 'data' not in raw_stock_opt:
        return {
            'matches': stock_opt_matches,
            'all_contracts': all_stock_contracts
        }

    items = raw_stock_opt['data']

    for c in items:
        underlying = c.get('underlying', '')
        opt_type = "CE" if c.get('optionType') in ["Call", "CE"] else ("PE" if c.get('optionType') in ["Put", "PE"] else c.get('optionType'))
        strike = c.get('strikePrice', 0)
        expiry = c.get('expiryDate', '')

        op = float(c.get('openPrice', 0.0))
        hi = float(c.get('highPrice', 0.0))
        lo = float(c.get('lowPrice', 0.0))
        ltp = float(c.get('lastPrice', 0.0))
        spot = float(c.get('underlyingValue', 0.0))
        change_pct = float(c.get('pChange', 0.0))
        oi = int(c.get('openInterest', 0))
        vol = int(c.get('volume', 0))
        trades = int(c.get('noOfTrades', 0))

        if op == 0 or ltp == 0:
            continue

        low_diff_pts = abs(op - lo)
        high_diff_pts = abs(hi - op)

        setup = None
        signal = None

        if low_diff_pts <= max_tick_diff:
            setup = "OPEN=LOW"
            signal = "BULLISH"
        elif high_diff_pts <= max_tick_diff:
            setup = "OPEN=HIGH"
            signal = "BEARISH"

        contract_info = {
            'symbol': f"{underlying} {strike} {opt_type}",
            'underlying': underlying,
            'spot_price': spot,
            'strike': strike,
            'option_type': opt_type,
            'expiry': expiry,
            'signal': signal if signal else "NEUTRAL",
            'setup': setup if setup else "NONE",
            'open': op,
            'high': hi,
            'low': lo,
            'ltp': ltp,
            'change_pct': change_pct,
            'open_interest': oi,
            'volume': vol,
            'no_of_trades': trades
        }

        all_stock_contracts.append(contract_info)
        if setup:
            stock_opt_matches.append(contract_info)

    return {
        'matches': stock_opt_matches,
        'all_contracts': all_stock_contracts
    }


def run_combined_screener(num_strikes=6, stock_tolerance=0.00, option_max_tick=0.00, nifty_expiry=None, banknifty_expiry=None):
    """
    Runs parallel scan for Stocks, Nifty Options, Bank Nifty Options, and Top Active Stock Options.
    """
    print("=" * 85)
    print(" 🚀 COMBINED STOCKS, INDEX OPTIONS & TOP STOCK OPTIONS SCREENER")
    print(f" Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 85)

    # ── 1. SCAN F&O STOCKS ──
    print("\n[1/4] Scanning Nifty F&O Stock Universe (250 stocks)...")
    stocks = _NIFTY_FO_FALLBACK
    stock_matches = []
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_single_stock_5m, ticker): ticker for ticker in stocks}
        for future in as_completed(futures):
            res = future.result()
            if res:
                match = analyze_stock_open_high_low(res, tolerance_pct=stock_tolerance)
                if match:
                    stock_matches.append(match)

    print(f"      [✓] Scanned {len(stocks)} F&O stocks -> Found {len(stock_matches)} matching stock setups.")

    # ── 2. SCAN NIFTY 50 OPTIONS ──
    print("\n[2/4] Scanning live Nifty 50 Options (nse50_opt)...")
    raw_nifty_opt = fetch_nse_index_options("nse50_opt")
    nifty_res = process_index_options(
        raw_nifty_opt, 
        target_underlying="NIFTY", 
        strike_step=50, 
        num_strikes=num_strikes, 
        option_max_tick=option_max_tick, 
        selected_expiry=nifty_expiry
    )
    print(f"      [✓] Nifty Spot: {nifty_res['spot_price']:,.2f} | ATM: {nifty_res['atm_strike']} | Expiry: {nifty_res['active_expiry']}")
    print(f"      [✓] Found {len(nifty_res['opt_matches'])} matching Nifty option setups.")

    # ── 3. SCAN BANK NIFTY OPTIONS ──
    print("\n[3/4] Scanning live Bank Nifty Options (nifty_bank_opt)...")
    raw_bank_opt = fetch_nse_index_options("nifty_bank_opt")
    bank_res = process_index_options(
        raw_bank_opt, 
        target_underlying="BANKNIFTY", 
        strike_step=100, 
        num_strikes=num_strikes, 
        option_max_tick=option_max_tick, 
        selected_expiry=banknifty_expiry
    )
    print(f"      [✓] Bank Nifty Spot: {bank_res['spot_price']:,.2f} | ATM: {bank_res['atm_strike']} | Expiry: {bank_res['active_expiry']}")
    print(f"      [✓] Found {len(bank_res['opt_matches'])} matching Bank Nifty option setups.")

    # ── 4. SCAN TOP ACTIVE STOCK OPTIONS ──
    print("\n[4/4] Scanning live Top Active Stock Options (stock_opt)...")
    raw_stock_opt = fetch_nse_index_options("stock_opt")
    stock_opt_res = process_top_stock_options(raw_stock_opt, max_tick_diff=option_max_tick)
    print(f"      [✓] Fetched {len(stock_opt_res['all_contracts'])} top stock options contracts -> Found {len(stock_opt_res['matches'])} matching setups.")

    output_payload = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock_matches_count': len(stock_matches),
        'stock_matches': stock_matches,
        'nifty_options': nifty_res,
        'banknifty_options': bank_res,
        'top_stock_options': stock_opt_res
    }

    json_path = "combined_screener_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, indent=2)

    print(f"\n[✓] Successfully saved all screener data to '{json_path}'.")
    return output_payload


if __name__ == "__main__":
    run_combined_screener()
