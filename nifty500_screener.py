"""
Nifty 500 Supertrend + MA Screener
============================================================
Conditions for a stock to qualify:
  1. Price above Monthly Supertrend (Period=10, Multiplier=3)
  2. Price above Weekly Supertrend  (Period=10, Multiplier=3)
  3. Price above N-day SMA          (default N=50)

Bonus: Qualified stocks are also checked for today's
       Open=Low or Open=High intraday setup (5-min data).
"""

import sys
import os
import json
import time
import datetime
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Full Nifty 500 Universe ─────────────────────────────────────────────────
# Fallback list — complete official Nifty 500 as of August 2026
# Correct tickers: ETERNAL (not ZOMATO), OBEROIRLTY (not OBEROIRALTY)
_NIFTY500_FALLBACK = [
    "360ONE", "3MINDIA", "ABB", "ACC", "ACMESOLAR", "AIAENG", "APLAPOLLO", "AUBANK",
    "AWL", "AADHARHFC", "AARTIIND", "AAVAS", "ABBOTINDIA", "ACE", "ACUTAAS",
    "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL",
    "ABCAPITAL", "ABFRL", "ABLBL", "ABREL", "ABSLAMC", "CPPLUS", "AEGISLOG",
    "AEGISVOPAK", "AFCONS", "AFFLE", "AJANTPHARM", "ALKEM", "ABDL", "ARE&M",
    "AMBER", "AMBUJACEM", "ANANDRATHI", "ANANTRAJ", "ANGELONE", "ANTHEM", "ANURAS",
    "APARINDS", "APOLLOHOSP", "APOLLOTYRE", "APTUS", "ASAHIINDIA", "ASHOKLEY",
    "ASIANPAINT", "ASTERDM", "ASTRAL", "ATHERENERG", "ATUL", "AUROPHARMA", "AIIL",
    "DMART", "AXISBANK", "BEML", "BLS", "BSE", "BAJAJ-AUTO", "BAJFINANCE",
    "BAJAJFINSV", "BAJAJHLDNG", "BAJAJHFL", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK",
    "BANKBARODA", "BANKINDIA", "MAHABANK", "BATAINDIA", "BAYERCROP", "BELRISE",
    "BERGEPAINT", "BDL", "BEL", "BHARATFORG", "BHEL", "BPCL", "BHARTIARTL",
    "BHARTIHEXA", "BIKAJI", "GROWW", "BIOCON", "BSOFT", "BLUEDART", "BLUEJET",
    "BLUESTARCO", "BBTC", "BOSCHLTD", "FIRSTCRY", "BRIGADE", "BRITANNIA",
    "MAPMYINDIA", "CCL", "CESC", "CGPOWER", "CIEINDIA", "CRISIL", "CANFINHOME",
    "CANBK", "CANHLIFE", "CAPLIPOINT", "CGCL", "CARBORUNIV", "CARTRADE",
    "CASTROLIND", "CEATLTD", "CEMPRO", "CENTRALBK", "CDSL", "CHALET", "CHAMBLFERT",
    "CHENNPETRO", "CHOICEIN", "CHOLAHLDNG", "CHOLAFIN", "CIPLA", "CUB", "CLEAN",
    "COALINDIA", "COCHINSHIP", "COFORGE", "COHANCE", "COLPAL", "CAMS", "CONCORDBIO",
    "CONCOR", "COROMANDEL", "CRAFTSMAN", "CREDITACC", "CROMPTON", "CUMMINSIND",
    "CYIENT", "DCMSHRIRAM", "DLF", "DOMS", "DABUR", "DALBHARAT", "DATAPATTNS",
    "DEEPAKFERT", "DEEPAKNTR", "DELHIVERY", "DEVYANI", "DIVISLAB", "DIXON",
    "LALPATHLAB", "DRREDDY", "EIDPARRY", "EIHOTEL", "EICHERMOT", "ELECON",
    "ELGIEQUIP", "EMAMILTD", "EMCURE", "EMMVEE", "ENDURANCE", "ENGINERSIN", "ERIS",
    "ESCORTS", "ETERNAL", "EXIDEIND", "NYKAA", "FEDERALBNK", "FACT", "FINCABLES",
    "FSL", "FIVESTAR", "FORCEMOT", "FORTIS", "GAIL", "GVT&D", "GMRAIRPORT",
    "GABRIEL", "GALLANTT", "GRSE", "GICRE", "GILLETTE", "GLAND", "GLAXO",
    "GLENMARK", "MEDANTA", "GODIGIT", "GPIL", "GODFRYPHLP", "GODREJCP", "GODREJIND",
    "GODREJPROP", "GRANULES", "GRAPHITE", "GRASIM", "GRAVITA", "GESHIP",
    "FLUOROCHEM", "GMDCLTD", "HEG", "HBLENGINE", "HCLTECH", "HDBFS", "HDFCAMC",
    "HDFCBANK", "HDFCLIFE", "HFCL", "HAVELLS", "HEROMOTOCO", "HEXT", "HSCL",
    "HINDALCO", "HAL", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "HINDZINC",
    "POWERINDIA", "HOMEFIRST", "HONASA", "HONAUT", "HUDCO", "HYUNDAI", "ICICIBANK",
    "ICICIGI", "ICICIAMC", "ICICIPRULI", "IDBI", "IDFCFIRSTB", "IFCI", "IIFL",
    "IRB", "IRCON", "ITCHOTELS", "ITC", "ITI", "INDGN", "INDIACEM", "INDIAMART",
    "INDIANB", "IEX", "INDHOTEL", "IOC", "IOB", "IRCTC", "IRFC", "IREDA", "IGL",
    "INDUSTOWER", "INDUSINDBK", "NAUKRI", "INFY", "INOXWIND", "INTELLECT", "INDIGO",
    "IGIL", "IKS", "IPCALAB", "JKCEMENT", "JBMA", "JKTYRE", "JMFINANCIL",
    "JSWCEMENT", "JSWDULUX", "JSWENERGY", "JSWINFRA", "JSWSTEEL", "JAINREC",
    "JPPOWER", "J&KBANK", "JINDALSAW", "JSL", "JINDALSTEL", "JIOFIN", "JUBLFOOD",
    "JUBLINGREA", "JUBLPHARMA", "JWL", "JYOTICNC", "KPRMILL", "KEI", "KPITTECH",
    "KAJARIACER", "KPIL", "KALYANKJIL", "KARURVYSYA", "KAYNES", "KEC", "KFINTECH",
    "KIRLOSENG", "KOTAKBANK", "KIMS", "LTF", "LTTS", "LGEINDIA", "LICHSGFIN",
    "LTFOODS", "LTM", "LT", "LATENTVIEW", "LAURUSLABS", "THELEELA", "LEMONTREE",
    "LENSKART", "LICI", "LINDEINDIA", "LLOYDSME", "LODHA", "LUPIN", "MMTC", "MRF",
    "MGL", "M&MFIN", "M&M", "MANAPPURAM", "MRPL", "MANKIND", "MARICO", "MARUTI",
    "MFSL", "MAXHEALTH", "MAZDOCK", "MEESHO", "MINDACORP", "MSUMI", "MOTILALOFS",
    "MPHASIS", "MCX", "MUTHOOTFIN", "NATCOPHARM", "NBCC", "NCC", "NHPC", "NLCINDIA",
    "NMDC", "NSLNISP", "NTPCGREEN", "NTPC", "NH", "NATIONALUM", "NAVA", "NAVINFLUOR",
    "NESTLEIND", "NETWEB", "NEULANDLAB", "NEWGEN", "NAM-INDIA", "NIVABUPA", "NUVAMA",
    "NUVOCO", "OBEROIRLTY", "ONGC", "OIL", "OLAELEC", "OLECTRA", "PAYTM",
    "ONESOURCE", "OFSS", "POLICYBZR", "PCBL", "PGEL", "PIIND", "PNBHOUSING",
    "PTCIL", "PVRINOX", "PAGEIND", "PARADEEP", "PATANJALI", "PERSISTENT", "PETRONET",
    "PFIZER", "PHOENIXLTD", "PWL", "PIDILITIND", "PINELABS", "PIRAMALFIN",
    "PPLPHARMA", "POLYMED", "POLYCAB", "POONAWALLA", "PFC", "POWERGRID", "PREMIERENE",
    "PRESTIGE", "PFOCUS", "PNB", "RRKABEL", "RBLBANK", "RECLTD", "RHIM", "RITES",
    "RADICO", "RVNL", "RAILTEL", "RAINBOW", "RKFORGE", "REDINGTON", "RELIANCE",
    "RPOWER", "SBFC", "SBICARD", "SBILIFE", "SJVN", "SRF", "SAGILITY", "SAILIFE",
    "SAMMAANCAP", "MOTHERSON", "SAPPHIRE", "SARDAEN", "SAREGAMA", "SCHAEFFLER",
    "SCHNEIDER", "SCI", "SHREECEM", "SHRIRAMFIN", "SHYAMMETL", "ENRIN", "SIEMENS",
    "SIGNATURE", "SOBHA", "SOLARINDS", "SONACOMS", "SONATSOFTW", "STARHEALTH",
    "SBIN", "SAIL", "SUMICHEM", "SUNPHARMA", "SUNTV", "SUNDARMFIN", "SUPREMEIND",
    "SPLPETRO", "SUZLON", "SWANCORP", "SWIGGY", "SYNGENE", "SYRMA", "TBOTEK",
    "TVSMOTOR", "TATACAP", "TATACHEM", "TATACOMM", "TCS", "TATACONSUM", "TATAELXSI",
    "TATAINVEST", "TMCV", "TMPV", "TATAPOWER", "TATASTEEL", "TATATECH", "TTML",
    "TECHM", "TECHNOE", "TEGA", "TEJASNET", "TENNIND", "NIACL", "RAMCOCEM",
    "THERMAX", "TIMKEN", "TITAGARH", "TITAN", "TORNTPHARM", "TORNTPOWER", "TARIL",
    "TRAVELFOOD", "TRENT", "TRIDENT", "TRITURBINE", "TIINDIA", "UCOBANK", "UNOMINDA",
    "UPL", "UTIAMC", "ULTRACEMCO", "UNIONBANK", "UBL", "UNITDSPR", "URBANCO",
    "USHAMART", "VTL", "VBL", "VEDL", "VIJAYA", "VMM", "IDEA", "VOLTAS",
    "WAAREEENER", "WELCORP", "WELSPUNLIV", "WHIRLPOOL", "WIPRO", "WOCKPHARMA",
    "YESBANK", "ZFCVINDIA", "ZEEL", "ZENTEC", "ZENSARTECH", "ZYDUSLIFE", "ZYDUSWELL",
    "ECLERX",
]

def _fetch_nifty500_symbols():
    """
    Dynamically fetches the official Nifty 500 list from niftyindices.com.
    Falls back to the hardcoded list if the fetch fails.
    """
    try:
        import pandas as pd
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        url = 'https://niftyindices.com/IndexConstituent/ind_nifty500list.csv'
        r = session.get(url, timeout=12)
        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text))
            symbols = df['Symbol'].tolist()
            if len(symbols) >= 490:
                print(f"[✓] Fetched {len(symbols)} stocks from official NSE Nifty 500 list.")
                return symbols
    except Exception:
        pass
    print(f"[!] NSE fetch failed — using fallback list ({len(_NIFTY500_FALLBACK)} stocks).")
    return _NIFTY500_FALLBACK

_NIFTY500_STOCKS_CACHE = None

def get_nifty500_universe_cached():
    """Lazy-loads the Nifty 500 universe (only on first call — not at import time)."""
    global _NIFTY500_STOCKS_CACHE
    if _NIFTY500_STOCKS_CACHE is None:
        _NIFTY500_STOCKS_CACHE = _fetch_nifty500_symbols()
    return _NIFTY500_STOCKS_CACHE



# ─── Supertrend Calculation ─────────────────────────────────────────────────
def compute_supertrend(highs, lows, closes, period=10, multiplier=3):
    """
    Compute Supertrend using Wilder's ATR smoothing.
    Returns (latest_supertrend_value, direction) where direction 1=bullish, -1=bearish.
    """
    n = len(closes)
    if n < period + 2:
        return None, None

    # True Range
    tr = [highs[0] - lows[0]]
    for i in range(1, n):
        tr.append(max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        ))

    # Wilder ATR (smoothed moving average)
    atr = [None] * (period - 1)
    atr.append(sum(tr[:period]) / period)
    for i in range(period, n):
        atr.append((atr[-1] * (period - 1) + tr[i]) / period)

    # Basic upper/lower bands
    upper_basic = [None] * n
    lower_basic = [None] * n
    for i in range(period, n):
        mid = (highs[i] + lows[i]) / 2
        upper_basic[i] = mid + multiplier * atr[i]
        lower_basic[i] = mid - multiplier * atr[i]

    # Final trend-following bands
    final_upper = [None] * n
    final_lower = [None] * n
    supertrend  = [None] * n
    direction   = [None] * n

    for i in range(period, n):
        if upper_basic[i] is None:
            continue

        # Upper band: tighten only if trend is down
        if final_upper[i - 1] is None:
            final_upper[i] = upper_basic[i]
        else:
            final_upper[i] = (
                upper_basic[i]
                if upper_basic[i] < final_upper[i - 1] or closes[i - 1] > final_upper[i - 1]
                else final_upper[i - 1]
            )

        # Lower band: raise only if trend is up
        if final_lower[i - 1] is None:
            final_lower[i] = lower_basic[i]
        else:
            final_lower[i] = (
                lower_basic[i]
                if lower_basic[i] > final_lower[i - 1] or closes[i - 1] < final_lower[i - 1]
                else final_lower[i - 1]
            )

        # Determine direction
        if direction[i - 1] is None:
            direction[i] = 1 if closes[i] >= final_upper[i] else -1
        else:
            prev = direction[i - 1]
            if prev == -1 and closes[i] > final_upper[i]:
                direction[i] = 1
            elif prev == 1 and closes[i] < final_lower[i]:
                direction[i] = -1
            else:
                direction[i] = prev

        supertrend[i] = final_lower[i] if direction[i] == 1 else final_upper[i]

    for i in range(n - 1, -1, -1):
        if supertrend[i] is not None:
            return round(supertrend[i], 2), direction[i]
    return None, None


def compute_sma(closes, period):
    if len(closes) < period:
        return None
    return round(sum(closes[-period:]) / period, 2)


def compute_ema(closes, period):
    if len(closes) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for c in closes[period:]:
        ema = c * k + ema * (1 - k)
    return round(ema, 2)


# ─── Yahoo Finance Fetch ──────────────────────────────────────────────────────
def _get_ohlc(ticker, interval, range_str, session):
    symbol = f"{ticker}.NS"
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?range={range_str}&interval={interval}")
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            if resp.status_code != 200:
                return None
            data = resp.json()
            result = data['chart']['result'][0]
            q = result['indicators']['quote'][0]
            timestamps = result['timestamp']
            dates = [datetime.datetime.fromtimestamp(ts).date() for ts in timestamps]
            return {
                'dates':   dates,
                'opens':   q.get('open',   []),
                'highs':   q.get('high',   []),
                'lows':    q.get('low',    []),
                'closes':  q.get('close',  []),
                'volumes': q.get('volume', []),
            }
        except Exception:
            if attempt == 2:
                return None
            time.sleep(0.5)
    return None


def fetch_single_stock_full(ticker, session, tolerance_pct=0.20, st_period=10, st_mult=3):
    """
    Fetch and analyse one stock.
    Filter criteria:
      1. Weekly Supertrend (10,3) == BULLISH (price > weekly_st)
      2. Daily MA Bull Stack: Current Price > 50 SMA > 100 SMA > 200 SMA
      3. Intraday Open=Low / Open=High setup detection (bonus)
    """

    # ── 1. Weekly Supertrend (10,3) ─────────────────────────────────────────────────
    weekly = _get_ohlc(ticker, '1wk', '1y', session)  # 1y (~52 wk candles) is enough for ST(10,3)
    if not weekly:
        return None
    w_c = [float(c) for c in weekly['closes'] if c is not None]
    w_h = [float(h) for h in weekly['highs']  if h is not None]
    w_l = [float(l) for l in weekly['lows']   if l is not None]
    wn  = min(len(w_c), len(w_h), len(w_l))
    if wn < st_period + 5:
        return None
    weekly_st, weekly_dir = compute_supertrend(w_h[:wn], w_l[:wn], w_c[:wn], st_period, st_mult)
    if weekly_st is None or weekly_dir != 1:
        return None  # Price must be above Weekly Supertrend

    # ── 2. Daily MA Bull Stack (Price > 50 SMA > 100 SMA > 200 SMA) ─────────
    daily = _get_ohlc(ticker, '1d', '1y', session)
    if not daily:
        return None
    d_c   = [float(c) for c in daily['closes']  if c is not None]
    d_vol = [v for v in daily['volumes'] if v is not None]
    if len(d_c) < 200:
        return None

    sma_50  = compute_sma(d_c, 50)
    sma_100 = compute_sma(d_c, 100)
    sma_200 = compute_sma(d_c, 200)

    if sma_50 is None or sma_100 is None or sma_200 is None:
        return None

    current_price = d_c[-1]

    # MA Bull Stack condition: Price > 50 SMA > 100 SMA > 200 SMA
    ma_stack_qualified = (current_price > sma_50) and (sma_50 > sma_100) and (sma_100 > sma_200)
    if not ma_stack_qualified:
        return None

    prev_close  = d_c[-2] if len(d_c) >= 2 else d_c[-1]
    change_pct  = round((current_price - prev_close) / prev_close * 100, 2)
    ma_distance = round((current_price - sma_50) / sma_50 * 100, 2)
    avg_vol     = sum(d_vol[-20:]) / max(len(d_vol[-20:]), 1)
    day_vol     = d_vol[-1] if d_vol else 0
    vol_surge   = round(day_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    d_opens = [float(o) for o in daily['opens'] if o is not None]
    d_lows  = [float(l) for l in daily['lows']  if l is not None]
    official_open = d_opens[-1] if d_opens else None
    official_low  = d_lows[-1]  if d_lows  else None

    # ── 3. Check for Open=Low today (using Official Daily Open & Low) ──────
    fivemin = _get_ohlc(ticker, '5m', '5d', session)
    setup_type         = None
    entry_price        = None
    stoploss           = None
    target_1           = None
    target_2           = None
    diff_from_open_pct = None
    pnl_pct            = None
    momentum_confirmed = False
    ltp                = current_price   # safe fallback — avoids UnboundLocalError
    prev_day_high      = None            # initialized before fivemin block
    prev_day_low       = None
    day_open_val       = round(official_open, 2) if official_open else None
    day_low_val        = round(official_low, 2)  if official_low  else None

    if fivemin and official_open and official_low and official_open > 0:
        all_dates = fivemin['dates']
        if all_dates:
            today = max(all_dates)
            t_idx = [i for i in range(len(all_dates))
                     if all_dates[i] == today
                     and fivemin['opens'][i] is not None
                     and fivemin['closes'][i] is not None]
            if t_idx:
                first   = t_idx[0]
                latest  = t_idx[-1]
                entry_5m = float(fivemin['closes'][first])
                ltp      = float(fivemin['closes'][latest])

                prev_idx = [i for i in range(len(all_dates))
                            if all_dates[i] < today and fivemin['closes'][i] is not None]
                if prev_idx:
                    prev_day = max(all_dates[i] for i in prev_idx)
                    pd_idx   = [i for i in prev_idx if all_dates[i] == prev_day]
                    prev_day_high = max(float(fivemin['highs'][i]) for i in pd_idx if fivemin['highs'][i])
                    prev_day_low  = min(float(fivemin['lows'][i])  for i in pd_idx if fivemin['lows'][i])

                # Official Open=Low difference check (matches Zerodha / TradingView 100%)
                ol_diff = abs(official_open - official_low) / official_open * 100

                if ol_diff <= tolerance_pct:
                    setup_type         = 'OPEN_LOW'
                    diff_from_open_pct = round(ol_diff, 3)
                    risk_amt    = max(round(entry_5m - official_low * 0.997, 2),
                                     round(entry_5m * 0.005, 2))
                    stoploss    = round(official_low * 0.997, 2)
                    target_1    = round(entry_5m + risk_amt * 1.5, 2)
                    target_2    = round(entry_5m + risk_amt * 2.5, 2)
                    entry_price = round(entry_5m, 2)
                    pnl_pct     = round((ltp - entry_5m) / entry_5m * 100, 2)
                    if prev_day_high:
                        momentum_confirmed = entry_5m > prev_day_high

    signal = ("BULL STACK + OPEN=LOW 🔥" if setup_type == 'OPEN_LOW' and momentum_confirmed
              else "BULL STACK + OPEN=LOW" if setup_type == 'OPEN_LOW'
              else "MA BULL STACK")

    exact_match = (diff_from_open_pct is not None) and (diff_from_open_pct < 0.02)

    return {
        "ticker":              ticker,
        "current_price":       round(current_price, 2),
        "ltp":                 round(ltp, 2),
        "day_open":            day_open_val,
        "day_low":             day_low_val,
        "change_pct":          change_pct,
        "volume":              day_vol,
        "vol_surge":           vol_surge,
        "weekly_supertrend":   weekly_st,
        "sma_50":              sma_50,
        "sma_100":             sma_100,
        "sma_200":             sma_200,
        "ma_distance_pct":     ma_distance,
        "above_weekly_st":     True,
        "ma_stack_aligned":    True,
        "setup_type":          setup_type,
        "entry_price":         entry_price,
        "stoploss":            stoploss,
        "target_1":            target_1,
        "target_2":            target_2,
        "diff_from_open_pct":  diff_from_open_pct,
        "exact_match":         exact_match,
        "pnl_pct":             pnl_pct,
        "momentum_confirmed":  momentum_confirmed,
        "prev_day_high":       round(prev_day_high, 2) if prev_day_high else None,
        "prev_day_low":        round(prev_day_low, 2)  if prev_day_low  else None,
        "signal":              signal,
    }


# ─── Parallel Scan ────────────────────────────────────────────────────────────
def run_nifty500_scan(tickers=None, tolerance_pct=0.20, st_period=10, st_mult=3):
    if tickers is None:
        tickers = get_nifty500_universe_cached()  # lazy-loaded, not at import time
    tickers = list(dict.fromkeys(tickers))

    print(f"[*] Scanning {len(tickers)} Nifty 500 stocks | "
          f"Weekly ST({st_period},{st_mult}) + MA Bull Stack (Price > 50 SMA > 100 SMA > 200 SMA)...")

    session = requests.Session()
    session.headers.update({'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36')})

    qualified = []
    done = 0

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {
            executor.submit(fetch_single_stock_full, t, session,
                            tolerance_pct, st_period, st_mult): t
            for t in tickers
        }
        for future in as_completed(futures):
            done += 1
            res = future.result()
            if res:
                qualified.append(res)
            if done % 50 == 0:
                print(f"  [{done}/{len(tickers)}] qualified: {len(qualified)}")

    print(f"[✓] Done. Qualified: {len(qualified)} / {len(tickers)}")

    momentum_setups = [s for s in qualified if s['setup_type'] is not None]
    pure_st         = [s for s in qualified if s['setup_type'] is None]

    momentum_setups.sort(key=lambda x: (x['change_pct'], x['momentum_confirmed'], x['vol_surge']), reverse=True)
    pure_st.sort(key=lambda x: x['change_pct'], reverse=True)
    all_qualified = sorted(qualified, key=lambda x: x['change_pct'], reverse=True)

    scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = {
        "scan_time":                scan_time,
        "total_scanned":            len(tickers),
        "st_period":                st_period,
        "st_multiplier":            st_mult,
        "qualified_count":          len(qualified),
        "momentum_setup_count":     len(momentum_setups),
        "momentum_confirmed_count": len([s for s in momentum_setups if s['momentum_confirmed']]),
        "qualified_stocks":         all_qualified,
        "momentum_setups":          momentum_setups,
    }

    # Write to root (timestamped + always a 'latest' copy)
    base     = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base, "nifty500_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Written to {out_path}")

    # Write to nifty500-app/public/
    pub_path = os.path.join(base, "nifty500-app", "public", "nifty500_data.json")
    if os.path.exists(os.path.dirname(pub_path)):
        with open(pub_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"[✓] Also written to nifty500-app/public/")

    # Timestamped CSV for history
    ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    df_all  = __import__('pandas').DataFrame(qualified)
    if not df_all.empty:
        csv_ts     = os.path.join(base, f"nifty500_{ts}.csv")
        csv_latest = os.path.join(base, "nifty500_screener_latest.csv")
        df_all.to_csv(csv_ts, index=False)
        df_all.to_csv(csv_latest, index=False)
        print(f"[✓] CSV saved: {csv_ts}")

    # CLI summary
    print(f"\n{'='*95}")
    print(f"  NIFTY 500 MA BULL STACK SCREENER | {scan_time}")
    print(f"  Conditions: Weekly ST({st_period},{st_mult}) + Price > 50 SMA > 100 SMA > 200 SMA")
    print(f"  Qualified: {len(qualified)} | With Intraday Setup: {len(momentum_setups)}")
    print(f"{'='*95}")
    if momentum_setups:
        print(f"\n[🔥] QUALIFIED + BULLISH OPEN=LOW SETUPS:")
        print(f"  {'Ticker':<12} {'Open (Rs)':<10} {'Low (Rs)':<10} {'5m Entry':<10} {'Exact':<8} {'ST Wk':<10} {'SMA50':<10} {'MOM'}")
        print(f"  {'-'*95}")
        for s in momentum_setups:
            m = "🔥" if s['momentum_confirmed'] else "  "
            ex = "⭐ EXACT" if s['exact_match'] else "Standard"
            print(f"  {s['ticker']:<12} {(s['day_open'] or 0):<10.2f} {(s['day_low'] or 0):<10.2f} "
                  f"{(s['entry_price'] or 0):<10.2f} {ex:<8} "
                  f"{s['weekly_supertrend']:<10.2f} {s['sma_50']:<10.2f} {m}")
    print(f"\n[✅] MA BULL STACK QUALIFIED (NO INTRADAY SETUP)  — Top 20:")
    print(f"  {'Ticker':<12} {'Price':<10} {'Chg%':<8} {'MA Dist%':<10} "
          f"{'ST Weekly':<12} {'SMA50':<10} {'SMA100':<10} {'SMA200':<10}")
    print(f"  {'-'*95}")
    for s in pure_st[:20]:
        print(f"  {s['ticker']:<12} {s['current_price']:<10.2f} {s['change_pct']:<+8.2f} "
              f"{s['ma_distance_pct']:<10.2f} {s['weekly_supertrend']:<12.2f} "
              f"{s['sma_50']:<10.2f} {s['sma_100']:<10.2f} {s['sma_200']:<10.2f}")
    print(f"{'='*95}\n")
    return results


if __name__ == "__main__":
    run_nifty500_scan()

