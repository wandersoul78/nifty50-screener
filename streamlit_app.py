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

open_low_stocks = [s for s in filtered_stocks if s["setup_type"] == "OPEN_LOW"]
open_high_stocks = [s for s in filtered_stocks if s["setup_type"] == "OPEN_HIGH"]
exact_count = len([s for s in filtered_stocks if s["exact_match"]])

# KPI Summary Section
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Scanned", scan_results.get("total_scanned", 201), "NSE F&O Universe")

with col2:
    st.metric("Open = Low (BUY)", len(open_low_stocks), "Bullish Setups")

with col3:
    st.metric("Open = High (SELL)", len(open_high_stocks), "Bearish Setups")

with col4:
    st.metric("Exact Matches", exact_count, "Zero Shadow Candidates")

st.markdown("---")

# Main Filtered Stock Tables
tab_all, tab_bull, tab_bear = st.tabs([
    f"🔥 All Setups ({len(filtered_stocks)})",
    f"🟢 Bullish Open=Low ({len(open_low_stocks)})",
    f"🔴 Bearish Open=High ({len(open_high_stocks)})"
])

def format_df_for_display(stock_list):
    if not stock_list:
        return pd.DataFrame()
    df = pd.DataFrame(stock_list)
    cols = [
        "ticker", "setup_type", "open", "entry_price", "ltp", 
        "change_pct", "vol_surge", "stoploss", "target_1", "target_2", "diff_from_open_pct", "exact_match"
    ]
    df = df[cols]
    df.columns = [
        "Ticker", "Setup", "Open (₹)", "5m Entry (₹)", "LTP (₹)", 
        "Change (%)", "Vol Surge", "Stoploss (₹)", "Target 1 (₹)", "Target 2 (₹)", "Diff (%)", "Exact"
    ]
    return df

with tab_all:
    if filtered_stocks:
        df_display = format_df_for_display(filtered_stocks)
        st.dataframe(df_display, use_container_width=True, height=450)
    else:
        st.info("No stock setups match current tolerance criteria.")

with tab_bull:
    if open_low_stocks:
        df_bull = format_df_for_display(open_low_stocks)
        st.dataframe(df_bull, use_container_width=True, height=450)
    else:
        st.info("No Bullish Open=Low setups detected.")

with tab_bear:
    if open_high_stocks:
        df_bear = format_df_for_display(open_high_stocks)
        st.dataframe(df_bear, use_container_width=True, height=450)
    else:
        st.info("No Bearish Open=High setups detected.")

# CSV Export Button
if filtered_stocks:
    df_export = format_df_for_display(filtered_stocks)
    csv_bytes = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_bytes,
        file_name=f"nifty50_yahoo_screener_{int(time.time())}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption(f"Last Scan Execution Time: {scan_results.get('scan_time')}")
