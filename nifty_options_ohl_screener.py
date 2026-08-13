"""
Nifty 50 Options Pure Screener - Open = Low & Open = High Setup
========================================================================
Features:
1. Standalone Nifty Options Screener (keeps existing stock screeners untouched).
2. Uses NSE API (https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_opt)
   combined with Yahoo Finance Nifty Spot Price (^NSEI) for ATM determination.
3. Screens 6 strikes above & below ATM (13 strikes total, Call & Put options).
4. Identifies Open = Low (Bullish) and Open = High (Bearish) setups.
5. Saves results to nifty_options_ohl_data.json and nifty_options_ohl_latest.csv.
"""

import sys
import os
import time
import json
import datetime
import pandas as pd
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def get_nifty_spot_yahoo():
    """
    Fetches the latest Nifty 50 spot price from Yahoo Finance (^NSEI).
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?range=1d&interval=1m"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data['chart']['result'][0]
            indicators = result['indicators']['quote'][0]
            closes = indicators.get('close', [])
            valid_closes = [c for c in closes if c is not None]
            if valid_closes:
                return float(valid_closes[-1])
    except Exception as e:
        print(f"[!] Warning: Could not fetch Nifty spot from Yahoo Finance ({e})")
    return None


def fetch_nse_live_options():
    """
    Fetches live Nifty options data from NSE India API:
    https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_opt
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
        # Step 1: Pre-visit option-chain page to acquire required session cookies
        session.get("https://www.nseindia.com/option-chain", timeout=10)
        time.sleep(0.5)

        # Step 2: Fetch live equity options data
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_opt"
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[!] NSE API Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Error fetching from NSE API: {e}")
        return None


def run_nifty_options_ohl_screener(num_strikes=6, max_tick_diff=0.50, tolerance_pct=0.10):
    """
    Screens Nifty 50 Options for Open=Low (Bullish) and Open=High (Bearish) setups.
    
    Parameters:
    - num_strikes: Number of strikes up and down of ATM (default 6 = 13 strikes total).
    - max_tick_diff: Max point difference between Open and High/Low in ₹ (default ₹0.50).
    - tolerance_pct: Max % difference between Open and High/Low (default 0.10%).
    """
    print("=" * 85)
    print(" 🚀 NIFTY 50 OPTIONS OPEN = HIGH / OPEN = LOW SCREENER")
    print(f" Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 85)

    # 1. Fetch Yahoo Spot Price
    yahoo_spot = get_nifty_spot_yahoo()

    # 2. Fetch NSE Live Options Data
    print("[1/3] Fetching live Nifty options data from NSE API (liveEquity-derivatives)...")
    raw_data = fetch_nse_live_options()

    if not raw_data or 'data' not in raw_data:
        print("[❌] Failed to receive valid options data from NSE API.")
        return None

    all_contracts = raw_data['data']
    nifty_contracts = [c for c in all_contracts if c.get('underlying') == 'NIFTY']

    if not nifty_contracts:
        print("[❌] No Nifty contracts found in API response.")
        return None

    # Determine Spot Price (Yahoo Finance primary, NSE underlyingValue fallback)
    nse_spot = nifty_contracts[0].get('underlyingValue', 0.0)
    spot_price = yahoo_spot if yahoo_spot is not None else nse_spot

    if not spot_price or spot_price == 0:
        print("[❌] Could not determine Nifty spot price.")
        return None

    # Calculate ATM Strike & Range (Nifty strike step size is 50)
    atm_strike = int(round(spot_price / 50.0) * 50)
    min_strike = atm_strike - (num_strikes * 50)
    max_strike = atm_strike + (num_strikes * 50)

    # Determine nearest expiry date chronologically (format: DD-MMM-YYYY)
    def _parse_expiry(exp_str):
        try:
            return datetime.datetime.strptime(exp_str, "%d-%b-%Y").date()
        except Exception:
            return datetime.date.max

    exp_strings = list(set(c.get('expiryDate') for c in nifty_contracts if c.get('expiryDate')))
    exp_strings.sort(key=_parse_expiry)
    nearest_expiry = exp_strings[0] if exp_strings else "N/A"

    print(f"[2/3] Nifty Spot Price : {spot_price:,.2f} (Yahoo: {yahoo_spot if yahoo_spot else 'N/A'}, NSE: {nse_spot})")
    print(f"      ATM Strike       : {atm_strike}")
    print(f"      Target Strikes   : {min_strike} to {max_strike} (ATM ± {num_strikes} strikes)")
    print(f"      Nearest Expiry   : {nearest_expiry}")
    print("[3/3] Evaluating Open=Low and Open=High setups...\n")

    screened_results = []
    evaluated_contracts = []

    for c in nifty_contracts:
        if c.get('expiryDate') != nearest_expiry:
            continue

        strike = c.get('strikePrice', 0)
        if min_strike <= strike <= max_strike:
            opt_type = "CE" if c.get('optionType') == "Call" or c.get('optionType') == "CE" else ("PE" if c.get('optionType') == "Put" or c.get('optionType') == "PE" else c.get('optionType'))
            op = float(c.get('openPrice', 0.0))
            hi = float(c.get('highPrice', 0.0))
            lo = float(c.get('lowPrice', 0.0))
            ltp = float(c.get('lastPrice', 0.0))
            oi = int(c.get('openInterest', 0))
            volume = int(c.get('volume', 0))

            if op == 0 or ltp == 0:
                continue

            low_diff_pts = abs(op - lo)
            high_diff_pts = abs(hi - op)
            low_diff_pct = (low_diff_pts / op) * 100
            high_diff_pct = (high_diff_pts / op) * 100

            setup = None
            signal_type = None

            # Open = Low (Bullish)
            if low_diff_pts <= max_tick_diff or low_diff_pct <= tolerance_pct:
                setup = "OPEN=LOW"
                signal_type = "BULLISH"

            # Open = High (Bearish)
            elif high_diff_pts <= max_tick_diff or high_diff_pct <= tolerance_pct:
                setup = "OPEN=HIGH"
                signal_type = "BEARISH"

            offset = strike - atm_strike
            offset_str = f"+{offset}" if offset > 0 else str(offset)

            contract_info = {
                'symbol': f"NIFTY {strike} {opt_type}",
                'option_type': opt_type,
                'strike': strike,
                'expiry': nearest_expiry,
                'setup': setup if setup else "NONE",
                'signal': signal_type if signal_type else "NEUTRAL",
                'open': op,
                'high': hi,
                'low': lo,
                'ltp': ltp,
                'diff_pts': round(low_diff_pts if setup == "OPEN=LOW" else (high_diff_pts if setup == "OPEN=HIGH" else 0), 2),
                'open_interest': oi,
                'volume': volume,
                'atm_offset': offset_str,
                'spot_price': spot_price,
                'atm_strike': atm_strike
            }

            evaluated_contracts.append(contract_info)

            if setup:
                screened_results.append(contract_info)

    # DataFrames
    df_eval = pd.DataFrame(evaluated_contracts)
    df_matches = pd.DataFrame(screened_results)

    # Sort evaluated contracts by strike and option_type
    if not df_eval.empty:
        df_eval = df_eval.sort_values(by=['strike', 'option_type']).reset_index(drop=True)

    print("📊 EVALUATED ATM ± 6 STRIKES CONTRACTS:")
    print("-" * 105)
    cols = ['symbol', 'atm_offset', 'setup', 'open', 'high', 'low', 'ltp', 'open_interest', 'volume']
    if not df_eval.empty:
        print(df_eval[cols].to_string(index=False))
    print("-" * 105)

    if not df_matches.empty:
        print("\n🎯 MATCHING OPEN = LOW & OPEN = HIGH OPTION SETUPS:")
        print("=" * 105)
        match_cols = ['symbol', 'signal', 'setup', 'open', 'high', 'low', 'ltp', 'diff_pts', 'open_interest', 'volume']
        print(df_matches[match_cols].to_string(index=False))
        print("=" * 105)
    else:
        print("\nℹ️ No exact Open=Low or Open=High option setups found matching tolerance rules at this moment.")

    # Save to files
    json_path = "nifty_options_ohl_data.json"
    latest_csv_path = "nifty_options_ohl_latest.csv"

    output_payload = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'spot_price': spot_price,
        'atm_strike': atm_strike,
        'expiry': nearest_expiry,
        'matches_count': len(screened_results),
        'matches': screened_results,
        'all_evaluated_contracts': evaluated_contracts
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, indent=2)

    if not df_eval.empty:
        df_eval.to_csv(latest_csv_path, index=False)

    print(f"\n[✓] Results saved to '{json_path}' and '{latest_csv_path}'.")
    return output_payload


if __name__ == "__main__":
    run_nifty_options_ohl_screener()
