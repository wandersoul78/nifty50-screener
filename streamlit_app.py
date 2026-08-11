"""
Nifty F&O Intraday Open = Low / High Screener - Streamlit Cloud Web App
========================================================================
Hosted live on Streamlit Cloud + GitHub.
Fetches 215+ Nifty F&O stock 5-minute candles via Yahoo Finance API.
"""

import sys
import os
import time
import datetime
import pandas as pd
import streamlit as st
from open_high_low_screener import NIFTY_FO_STOCKS, fetch_all_stocks_parallel, analyze_open_high_low

# Page Configuration
st.set_page_config(
    page_title="Nifty F&O Open=Low/High Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Glassmorphism & Modern Dark Theme
st.markdown("""
<style>
    .main {
        background-color: #090d16;
        color: #f8fafc;
    }
    .stMetric {
        background: rgba(18, 26, 44, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Nifty F&O Open = Low / Open = High Screener")
st.caption("Intraday Momentum Setups (5-Min Post-Open Entry Trigger) powered by Yahoo Finance API")

# Sidebar Controls
st.sidebar.header("⚙️ Screener Controls")

tolerance = st.sidebar.slider(
    "Open Buffer Tolerance (%)",
    min_value=0.00,
    max_value=0.50,
    value=0.20,
    step=0.05,
    help="Filter stocks where Open price is within X% of Low or High"
)

strict_only = st.sidebar.checkbox(
    "Zap Exact Matches Only (Diff < 0.02%)",
    value=False,
    help="Only show stocks with near-zero shadow"
)

if st.sidebar.button("🔄 Run Live Scanner", use_container_width=True, type="primary"):
    st.cache_data.clear()

# Cache market scanning for 60 seconds to prevent rate-limiting
@st.cache_data(ttl=60)
def get_market_scan_data(tol_val):
    stock_dict = fetch_all_stocks_parallel(NIFTY_FO_STOCKS) or {}
    results = analyze_open_high_low(stock_dict, tolerance_pct=tol_val)
    return results

with st.spinner("Fetching 215+ Nifty F&O 5-minute stock candles..."):
    scan_results = get_market_scan_data(tolerance)

raw_stocks = scan_results.get("all_matches", [])

# Apply filters
filtered_stocks = [
    s for s in raw_stocks 
    if s["diff_from_open_pct"] <= tolerance and (not strict_only or s["exact_match"])
]

open_low_stocks   = [s for s in filtered_stocks if s["setup_type"] == "OPEN_LOW"]
open_high_stocks  = [s for s in filtered_stocks if s["setup_type"] == "OPEN_HIGH"]
momentum_stocks   = [s for s in filtered_stocks if s.get("momentum_confirmed") is True]
exact_count       = len([s for s in filtered_stocks if s["exact_match"]])

# KPI Summary Section
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Scanned", scan_results.get("total_scanned", 201), "NSE F&O Universe")

with col2:
    st.metric("Open = Low (BUY)", len(open_low_stocks), "Bullish Setups")

with col3:
    st.metric("Open = High (SELL)", len(open_high_stocks), "Bearish Setups")

with col4:
    st.metric("Exact Matches", exact_count, "Zero Shadow Candidates")

with col5:
    st.metric("🔥 Momentum", len(momentum_stocks), "5-min close crosses Prev Day extreme")

st.info("💡 **PnL (Entry → LTP)** shows exact gain/loss from 09:20 AM Entry Price to Current LTP (🟢 Green = Profit, 🔴 Red = Loss). **Shadow Diff = 0.000%** indicates an EXACT Open = Low / Open = High match with zero shadow.")

st.markdown("---")

# Main Filtered Stock Tables
tab_all, tab_bull, tab_bear, tab_mom = st.tabs([
    f"📊 All Setups ({len(filtered_stocks)})",
    f"🟢 Bullish Open=Low ({len(open_low_stocks)})",
    f"🔴 Bearish Open=High ({len(open_high_stocks)})",
    f"🔥 Momentum ({len(momentum_stocks)})"
])

def format_df_for_display(stock_list, include_momentum_cols=False):
    if not stock_list:
        return pd.DataFrame()
    df = pd.DataFrame(stock_list).copy()
    
    cols = [
        "ticker", "setup_type", "open", "entry_price", "ltp", "pnl_pct", 
        "change_pct", "vol_surge", "stoploss", "target_1", "target_2", "diff_from_open_pct", "exact_match",
        "momentum_confirmed"
    ]
    # Only keep columns that actually exist (prev_day_high/low may be absent in older cached data)
    if include_momentum_cols:
        for extra in ["prev_day_high", "prev_day_low"]:
            if extra in df.columns:
                cols.append(extra)
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    
    rename_map = {
        "ticker": "Ticker", "setup_type": "Setup", "open": "Open (₹)",
        "entry_price": "5m Entry (₹)", "ltp": "LTP (₹)", "pnl_pct": "PnL % (Entry→LTP)",
        "change_pct": "Day Chg (%)", "vol_surge": "Vol Surge", "stoploss": "Stoploss (₹)",
        "target_1": "Target 1 (₹)", "target_2": "Target 2 (₹)", "diff_from_open_pct": "Shadow Diff (%)",
        "exact_match": "Exact", "momentum_confirmed": "🔥 Momentum",
        "prev_day_high": "Prev Day High (₹)", "prev_day_low": "Prev Day Low (₹)"
    }
    df.columns = [rename_map.get(c, c) for c in df.columns]
    
    # Format Entry to LTP Gain/Loss with Green / Red Indicators
    df["PnL % (Entry→LTP)"] = df["PnL % (Entry→LTP)"].apply(
        lambda x: f"🟢 +{float(x):.2f}%" if float(x) >= 0 else f"🔴 {float(x):.2f}%"
    )
    
    # Format precision for Streamlit Cloud rendering
    df["Shadow Diff (%)"] = df["Shadow Diff (%)"].apply(lambda x: f"{float(x):.3f}%")
    df["Day Chg (%)"]     = df["Day Chg (%)"].apply(lambda x: f"{float(x):+.2f}%")
    df["Vol Surge"]       = df["Vol Surge"].apply(lambda x: f"{float(x):.2f}x")
    df["Open (₹)"]        = df["Open (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["5m Entry (₹)"]    = df["5m Entry (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["LTP (₹)"]         = df["LTP (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["Stoploss (₹)"]    = df["Stoploss (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["Target 1 (₹)"]   = df["Target 1 (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["Target 2 (₹)"]   = df["Target 2 (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    df["Exact"]           = df["Exact"].apply(lambda x: "⭐ EXACT" if x else "Standard")
    df["🔥 Momentum"]     = df["🔥 Momentum"].apply(lambda x: "🔥 YES" if x else "—")
    if "Prev Day High (₹)" in df.columns:
        df["Prev Day High (₹)"] = df["Prev Day High (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    if "Prev Day Low (₹)" in df.columns:
        df["Prev Day Low (₹)"]  = df["Prev Day Low (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
    
    return df

with tab_all:
    if filtered_stocks:
        df_display = format_df_for_display(filtered_stocks)
        st.dataframe(df_display, use_container_width=True, height=480)
    else:
        st.info("No stock setups match current tolerance criteria.")

with tab_bull:
    if open_low_stocks:
        df_bull = format_df_for_display(open_low_stocks)
        st.dataframe(df_bull, use_container_width=True, height=480)
    else:
        st.info("No Bullish Open=Low setups detected.")

with tab_bear:
    if open_high_stocks:
        df_bear = format_df_for_display(open_high_stocks)
        st.dataframe(df_bear, use_container_width=True, height=480)
    else:
        st.info("No Bearish Open=High setups detected.")

with tab_mom:
    if momentum_stocks:
        st.info(
            "🔥 **Momentum Condition:** Open=Low stocks whose 5-min close is **above** the previous day's High, "
            "or Open=High stocks whose 5-min close is **below** the previous day's Low. "
            "These are the highest-conviction breakout/breakdown setups."
        )
        df_mom = format_df_for_display(momentum_stocks, include_momentum_cols=True)
        st.dataframe(df_mom, use_container_width=True, height=480)
    else:
        st.warning(
            "No momentum-confirmed stocks right now. Momentum requires the 5-min candle close "
            "to cross the previous day's High (for Open=Low) or Low (for Open=High)."
        )

# CSV Export Button
if filtered_stocks:
    df_export = pd.DataFrame(filtered_stocks)
    csv_bytes = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_bytes,
        file_name=f"nifty50_yahoo_screener_{int(time.time())}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption(f"Last Scan Execution Time: {scan_results.get('scan_time')}")
