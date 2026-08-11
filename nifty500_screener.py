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
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Full Nifty 500 Universe ────────────────────────────────────────────────
NIFTY500_STOCKS = [
    # Banking & Finance
    "HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","INDUSINDBK","BANKBARODA",
    "CANBK","PNB","FEDERALBNK","AUBANK","BANDHANBNK","IDFCFIRSTB","BAJFINANCE",
    "BAJAJFINSV","CHOLAFIN","SHRIRAMFIN","MUTHOOTFIN","RECLTD","PFC","ICICIPRULI",
    "SBILIFE","HDFCLIFE","LICHSGFIN","HDFCAMC","BSE","MCX","MANAPPURAM","YESBANK",
    "JIOFIN","MOTILALOFS","MFSL","SBICARD","RBLBANK","IIFL","CREDITACC","UJJIVANSFB",
    "EQUITASBNK","ESAFSFB","APTUS","HOMEFIRST","AAVAS","CANFINHOME","REPCO","MASFIN",
    "LICI","ICICIGI","NIACL","GODIGIT","POLICYBZR","ABSLAMC","NIPPONLIFE",
    "UTIAMC","360ONE","IIFLWAM","FINCABLES",
    # IT & Technology
    "TCS","INFY","HCLTECH","WIPRO","TECHM","PERSISTENT","COFORGE","MPHASIS","LTTS",
    "TATAELXSI","NAUKRI","OFSS","KPITTECH","HAPPSTMNDS","SONATSOFTW","RATEGAIN",
    "ZENSAR","INTELLECT","BIRLASOFT","TANLA","ROUTE","FSL","NEWGEN","QUICKHEAL",
    "NUCLEUS","LTIM","CYIENT","MASTECH","NIITLTD","SUBEXLTD","TATACOMM","RAILTEL",
    # Automobile
    "MARUTI","M&M","HEROMOTOCO","EICHERMOT","TVSMOTOR","BOSCHLTD","BHARATFORG",
    "MOTHERSON","BALKRISIND","MRF","ASHOKLEY","ESCORTS","BAJAJ-AUTO","APOLLOTYRE",
    "ENDURANCE","SUPRAJIT","GABRIEL","SUNDRMFAST","CRAFTSMAN","LUMAXTECH","WABCO",
    "SANSERA","MINDA","AMARAJABAT","TITAGARH","VARROC","SMLISUZU",
    # Energy & Power
    "RELIANCE","NTPC","ONGC","POWERGRID","COALINDIA","GAIL","BPCL","IOC",
    "HINDPETRO","TATAPOWER","JSWENERGY","NHPC","PETRONET","OIL","ADANIGREEN",
    "ADANIPOWER","ATGL","IGL","MGL","GUJGASLTD","TORNTPOWER","CESC","JPPOWER",
    "IRCON","IREDA","SJVN","NLCINDIA","SUZLON","INOXGREEN","INOXWIND",
    # Metals & Mining
    "TATASTEEL","JSWSTEEL","HINDALCO","JINDALSTEL","VEDL","NMDC","NATIONALUM",
    "SAIL","APLAPOLLO","WELCORP","HINDZINC","MOIL","RATNAMANI","MIDHANI","GPIL",
    "SANDUMA","SHYAMMETL","GRAVITA",
    # FMCG & Consumer
    "ITC","HINDUNILVR","NESTLEIND","BRITANNIA","TATACONSUM","VBL","DABUR","GODREJCP",
    "COLPAL","MARICO","UNITDSPR","BERGEPAINT","PIDILITIND","BALRAMCHIN","UBL",
    "EMAMILTD","JYOTHYLAB","RADICO","DEVYANI","WESTLIFE","DODLA","TRENT",
    "BATAINDIA","PAGEIND","MCDOWELL-N","BAJAJCON","SYMPHONY","SAREGAMA","VMART",
    # Pharma & Healthcare
    "SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA","TORNTPHARM",
    "ALKEM","BIOCON","GLENMARK","APOLLOHOSP","GRANULES","SYNGENE","IPCALAB",
    "METROPOLIS","LALPATHLAB","MAXHEALTH","NAVINFLUOR","AJANTPHARM","GSKPHARMA",
    "PFIZER","ERIS","CAPLIPOINT","NATCOPHARM","JUBLPHARMA","LAURUSLABS","SOLARA",
    "STARHEALTH","MEDANTA",
    # Capital Goods & Infra
    "LT","BEL","HAL","SIEMENS","ABB","BHEL","CGPOWER","HAVELLS","POLYCAB","VOLTAS",
    "DIXON","ASTRAL","CUMMINSIND","TIINDIA","RVNL","MAZDOCK","CONCOR","IRCTC",
    "CROMPTON","AIAENG","THERMAX","GRINDWELL","ELECON","KSB","CARBORUNIV","HEG",
    "JYOTICNC","KEI","POWERINDIA","TDPOWERSYS","APARINDS","POLYPLEX","ORIENTELEC",
    # Cement & Real Estate
    "ULTRACEMCO","GRASIM","AMBUJACEM","ACC","DALBHARAT","SHREECEM","RAMCOCEM",
    "NUVOCO","HEIDELBERG","DLF","GODREJPROP","PHOENIXLTD","OBEROIRALTY","PRESTIGE",
    "SOBHA","BRIGADE","NCLIND","SUNTECK","KOLTEPATIL","ANANTRAJ","KEYSTONE",
    # Chemicals & Agri
    "SRF","DEEPAKNTR","UPL","CHAMBLFERT","ATUL","PIIND","AARTIIND","TATACHEM",
    "GNFC","NOCIL","VINATI","GALAXYSURF","FINEORG","SUDARSCHEM","ALKYLAMINE",
    "PCBL","BALAMINES","COROMANDEL","RALLIS","DHANUKA","INSECTICID","PI",
    # Telecom & Media
    "BHARTIARTL","IDEA","INDUSTOWER","SUNTV","ZEEL","PVRINOX","TIPS",
    # Others & New Age
    "ADANIENT","ADANIPORTS","ZOMATO","SUZLON","NYKAA","KALYANKJIL","ABFRL",
    "EXIDEIND","SWIGGY","BSOFT","HUDCO","NBCC","CENTRALBK","PATANJALI","AWL",
    "DMART","SOLARINDS","HFCL","AETHER","KAYNES","HYUNDAI","PAYTM","PGEL",
    "GMRAIRPORT","KFINTECH","IRFC","JUBLFOOD","TITAN","ASIANPAINT","INDIGO",
    "TATATECH","BLUEDARTEQ","SHOPERSTOP","VGUARD","BAJAJELEC","WHIRLPOOL",
    "BLUESTAR","AMBER","TRIDENT","VARDHMAN","SIYARAM","WELSPUNIND","KITEX",
    "ARVIND","RAYMOND","GODREJIND","MAHINDLOG","DELHIVERY","CARTRADE",
    "EASEMYTRIP","IXIGO","POLICYBZR","SWIGGY","NYKAA",
]

# Deduplicate while preserving order
NIFTY500_STOCKS = list(dict.fromkeys(NIFTY500_STOCKS))


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


def fetch_single_stock_full(ticker, session, ma_period=50, ma_type='SMA',
                             tolerance_pct=0.20, st_period=10, st_mult=3):
    """Fetch and analyse one stock. Returns result dict or None if not qualified."""

    # ── 1. Monthly Supertrend ────────────────────────────────────────────
    monthly = _get_ohlc(ticker, '1mo', '5y', session)
    if not monthly:
        return None
    m_c = [float(c) for c in monthly['closes'] if c is not None]
    m_h = [float(h) for h in monthly['highs']  if h is not None]
    m_l = [float(l) for l in monthly['lows']   if l is not None]
    mn  = min(len(m_c), len(m_h), len(m_l))
    if mn < st_period + 5:
        return None
    monthly_st, monthly_dir = compute_supertrend(m_h[:mn], m_l[:mn], m_c[:mn], st_period, st_mult)
    if monthly_st is None or monthly_dir != 1:
        return None

    # ── 2. Weekly Supertrend ─────────────────────────────────────────────
    weekly = _get_ohlc(ticker, '1wk', '3y', session)
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
        return None

    # ── 3. Daily MA ──────────────────────────────────────────────────────
    daily = _get_ohlc(ticker, '1d', '1y', session)
    if not daily:
        return None
    d_c   = [float(c) for c in daily['closes']  if c is not None]
    d_vol = [v for v in daily['volumes'] if v is not None]
    if len(d_c) < ma_period:
        return None
    ma_val = compute_ema(d_c, ma_period) if ma_type == 'EMA' else compute_sma(d_c, ma_period)
    if ma_val is None:
        return None
    current_price = d_c[-1]
    if current_price <= ma_val:
        return None

    prev_close  = d_c[-2] if len(d_c) >= 2 else d_c[-1]
    change_pct  = round((current_price - prev_close) / prev_close * 100, 2)
    ma_distance = round((current_price - ma_val) / ma_val * 100, 2)
    avg_vol     = sum(d_vol[-20:]) / max(len(d_vol[-20:]), 1)
    day_vol     = d_vol[-1] if d_vol else 0
    vol_surge   = round(day_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    # ── 4. Check for Open=Low / Open=High today (5-min) ─────────────────
    fivemin = _get_ohlc(ticker, '5m', '5d', session)
    setup_type         = None
    entry_price        = None
    stoploss           = None
    target_1           = None
    target_2           = None
    diff_from_open_pct = None
    pnl_pct            = None
    momentum_confirmed = False
    prev_day_high      = None
    prev_day_low       = None
    ltp                = current_price

    if fivemin:
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
                day_open = float(fivemin['opens'][first])
                entry_5m = float(fivemin['closes'][first])
                day_high  = max(float(fivemin['highs'][i])  for i in t_idx if fivemin['highs'][i])
                day_low   = min(float(fivemin['lows'][i])   for i in t_idx if fivemin['lows'][i])
                ltp       = float(fivemin['closes'][latest])

                # Previous day high/low for momentum check
                prev_idx = [i for i in range(len(all_dates))
                            if all_dates[i] < today and fivemin['closes'][i] is not None]
                if prev_idx:
                    prev_day = max(all_dates[i] for i in prev_idx)
                    pd_idx   = [i for i in prev_idx if all_dates[i] == prev_day]
                    prev_day_high = max(float(fivemin['highs'][i]) for i in pd_idx if fivemin['highs'][i])
                    prev_day_low  = min(float(fivemin['lows'][i])  for i in pd_idx if fivemin['lows'][i])

                if day_open > 0:
                    ol_diff = abs(day_open - day_low)  / day_open * 100
                    oh_diff = abs(day_open - day_high) / day_open * 100

                    if ol_diff <= tolerance_pct:
                        setup_type         = 'OPEN_LOW'
                        diff_from_open_pct = round(ol_diff, 3)
                        risk_amt    = max(round(entry_5m - day_low * 0.997, 2),
                                         round(entry_5m * 0.005, 2))
                        stoploss    = round(day_low * 0.997, 2)
                        target_1    = round(entry_5m + risk_amt * 1.5, 2)
                        target_2    = round(entry_5m + risk_amt * 2.5, 2)
                        entry_price = round(entry_5m, 2)
                        pnl_pct     = round((ltp - entry_5m) / entry_5m * 100, 2)
                        if prev_day_high:
                            momentum_confirmed = entry_5m > prev_day_high

                    elif oh_diff <= tolerance_pct:
                        setup_type         = 'OPEN_HIGH'
                        diff_from_open_pct = round(oh_diff, 3)
                        risk_amt    = max(round(day_high * 1.003 - entry_5m, 2),
                                         round(entry_5m * 0.005, 2))
                        stoploss    = round(day_high * 1.003, 2)
                        target_1    = round(entry_5m - risk_amt * 1.5, 2)
                        target_2    = round(entry_5m - risk_amt * 2.5, 2)
                        entry_price = round(entry_5m, 2)
                        pnl_pct     = round((entry_5m - ltp) / entry_5m * 100, 2)
                        if prev_day_low:
                            momentum_confirmed = entry_5m < prev_day_low

    signal = ("ST_BULLISH + OPEN=LOW 🔥" if setup_type == 'OPEN_LOW' and momentum_confirmed
              else "ST_BULLISH + OPEN=LOW" if setup_type == 'OPEN_LOW'
              else "ST_BULLISH + OPEN=HIGH 🔥" if setup_type == 'OPEN_HIGH' and momentum_confirmed
              else "ST_BULLISH + OPEN=HIGH" if setup_type == 'OPEN_HIGH'
              else "ST_BULLISH")

    return {
        "ticker":              ticker,
        "current_price":       round(current_price, 2),
        "ltp":                 round(ltp, 2),
        "change_pct":          change_pct,
        "volume":              day_vol,
        "vol_surge":           vol_surge,
        "monthly_supertrend":  monthly_st,
        "weekly_supertrend":   weekly_st,
        "ma_value":            ma_val,
        "ma_distance_pct":     ma_distance,
        "above_monthly_st":    True,
        "above_weekly_st":     True,
        "above_ma":            True,
        "setup_type":          setup_type,
        "entry_price":         entry_price,
        "stoploss":            stoploss,
        "target_1":            target_1,
        "target_2":            target_2,
        "diff_from_open_pct":  diff_from_open_pct,
        "pnl_pct":             pnl_pct,
        "momentum_confirmed":  momentum_confirmed,
        "prev_day_high":       round(prev_day_high, 2) if prev_day_high else None,
        "prev_day_low":        round(prev_day_low, 2)  if prev_day_low  else None,
        "signal":              signal,
    }


# ─── Parallel Scan ────────────────────────────────────────────────────────────
def run_nifty500_scan(tickers=None, ma_period=50, ma_type='SMA',
                      tolerance_pct=0.20, st_period=10, st_mult=3):
    if tickers is None:
        tickers = NIFTY500_STOCKS
    tickers = list(dict.fromkeys(tickers))

    print(f"[*] Scanning {len(tickers)} Nifty 500 stocks | "
          f"Monthly ST({st_period},{st_mult}) + Weekly ST({st_period},{st_mult}) + {ma_type}({ma_period})")

    session = requests.Session()
    session.headers.update({'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36')})

    qualified = []
    done = 0

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {
            executor.submit(fetch_single_stock_full, t, session,
                            ma_period, ma_type, tolerance_pct,
                            st_period, st_mult): t
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

    momentum_setups.sort(key=lambda x: (x['momentum_confirmed'], x['vol_surge']), reverse=True)
    pure_st.sort(key=lambda x: x['ma_distance_pct'], reverse=True)

    scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = {
        "scan_time":                scan_time,
        "total_scanned":            len(tickers),
        "ma_period":                ma_period,
        "ma_type":                  ma_type,
        "st_period":                st_period,
        "st_multiplier":            st_mult,
        "qualified_count":          len(qualified),
        "momentum_setup_count":     len(momentum_setups),
        "momentum_confirmed_count": len([s for s in momentum_setups if s['momentum_confirmed']]),
        "qualified_stocks":         pure_st + momentum_setups,
        "momentum_setups":          momentum_setups,
    }

    # Write to root
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

    # CLI summary
    print(f"\n{'='*95}")
    print(f"  NIFTY 500 SCREENER | {scan_time}")
    print(f"  Conditions: Monthly ST({st_period},{st_mult}) + Weekly ST({st_period},{st_mult}) + {ma_type}({ma_period})")
    print(f"  Qualified: {len(qualified)} | With Intraday Setup: {len(momentum_setups)}")
    print(f"{'='*95}")
    if momentum_setups:
        print(f"\n[🔥] ST-QUALIFIED + INTRADAY SETUP:")
        print(f"  {'Ticker':<12} {'Setup':<12} {'Price':<10} {'Entry':<10} "
              f"{'ST Mo':<10} {'ST Wk':<10} {'SMA':<10} {'MOM'}")
        print(f"  {'-'*88}")
        for s in momentum_setups:
            m = "🔥" if s['momentum_confirmed'] else "  "
            print(f"  {s['ticker']:<12} {(s['setup_type'] or ''):<12} "
                  f"{s['current_price']:<10.2f} {(s['entry_price'] or 0):<10.2f} "
                  f"{s['monthly_supertrend']:<10.2f} {s['weekly_supertrend']:<10.2f} "
                  f"{s['ma_value']:<10.2f} {m}")
    print(f"\n[✅] ST QUALIFIED (NO INTRADAY SETUP)  — Top 20:")
    print(f"  {'Ticker':<12} {'Price':<10} {'Chg%':<8} {'MA Dist%':<10} "
          f"{'ST Monthly':<12} {'ST Weekly':<12} {'MA Value':<10}")
    print(f"  {'-'*88}")
    for s in pure_st[:20]:
        print(f"  {s['ticker']:<12} {s['current_price']:<10.2f} {s['change_pct']:<+8.2f} "
              f"{s['ma_distance_pct']:<10.2f} {s['monthly_supertrend']:<12.2f} "
              f"{s['weekly_supertrend']:<12.2f} {s['ma_value']:<10.2f}")
    print(f"{'='*95}\n")
    return results


if __name__ == "__main__":
    ma_period = 50
    ma_type   = 'SMA'
    if len(sys.argv) > 1:
        try:
            ma_period = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        ma_type = sys.argv[2].upper()
    run_nifty500_scan(ma_period=ma_period, ma_type=ma_type)
