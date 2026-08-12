"""
Nifty Trading Screener Suite - Streamlit Cloud Web App
========================================================================
1. Nifty F&O Open = Low / Open = High Intraday Screener
2. Nifty 500 Supertrend + MA Multitimeframe Screener
"""

import sys
import os
import time
import datetime
import pandas as pd
import streamlit as st

from open_high_low_screener import get_fno_universe_cached, fetch_all_stocks_parallel, analyze_open_high_low
from nifty500_screener import get_nifty500_universe_cached, run_nifty500_scan

# Page Configuration
st.set_page_config(
    page_title="Nifty Trading Screener Suite",
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

# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.title("🎯 Screener Mode")
app_mode = st.sidebar.radio(
    "Select Active Screener:",
    [
        "📈 Nifty F&O Open = Low/High Intraday",
        "🚀 Nifty 500 Supertrend + MA Screener"
    ],
    index=0
)
st.sidebar.markdown("---")


# ==============================================================================
# MODE 1: Nifty F&O Open = Low / Open = High Screener
# ==============================================================================
if app_mode == "📈 Nifty F&O Open = Low/High Intraday":

    st.title("📈 Nifty F&O Open = Low / Open = High Screener")
    st.caption("Intraday Momentum Setups (5-Min Post-Open Entry Trigger) powered by Yahoo Finance API")

    st.sidebar.header("⚙️ F&O Screener Controls")

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

    if st.sidebar.button("🔄 Run Live F&O Scanner", use_container_width=True, type="primary"):
        st.cache_data.clear()

    @st.cache_data(ttl=60)
    def get_market_scan_data(tol_val):
        stock_dict = fetch_all_stocks_parallel(get_fno_universe_cached()) or {}
        results = analyze_open_high_low(stock_dict, tolerance_pct=tol_val)
        return results

    with st.spinner("Fetching 250 Nifty F&O 5-minute stock candles..."):
        scan_results = get_market_scan_data(tolerance)

    raw_stocks = scan_results.get("all_matches", [])

    filtered_stocks = [
        s for s in raw_stocks 
        if s["diff_from_open_pct"] <= tolerance and (not strict_only or s["exact_match"])
    ]

    filtered_stocks.sort(key=lambda s: s.get("change_pct", 0), reverse=True)
    open_low_stocks   = sorted([s for s in filtered_stocks if s["setup_type"] == "OPEN_LOW"], key=lambda s: s.get("change_pct", 0), reverse=True)
    open_high_stocks  = sorted([s for s in filtered_stocks if s["setup_type"] == "OPEN_HIGH"], key=lambda s: s.get("change_pct", 0), reverse=True)
    momentum_stocks   = sorted([s for s in filtered_stocks if s.get("momentum_confirmed") is True], key=lambda s: s.get("change_pct", 0), reverse=True)
    breakout_stocks   = sorted(scan_results.get("breakout_stocks", []), key=lambda s: s.get("breakout_gap", 0), reverse=True)
    exact_count       = len([s for s in filtered_stocks if s["exact_match"]])

    # KPI Summary Section
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Scanned", scan_results.get("total_scanned", 250), "NSE F&O Universe")
    with col2:
        st.metric("Open = Low (BUY)", len(open_low_stocks), "Bullish Setups")
    with col3:
        st.metric("Open = High (SELL)", len(open_high_stocks), "Bearish Setups")
    with col4:
        st.metric("Exact Matches", exact_count, "Zero Shadow Candidates")
    with col5:
        st.metric("🚀 5m Breakouts", len(breakout_stocks), "5m Close > High or < Low")

    st.info("💡 **PnL (Entry → LTP)** shows exact gain/loss from 1st 5-Min Candle Close Entry Price to Current LTP (🟢 Green = Profit, 🔴 Red = Loss).")

    st.markdown("---")

    tab_all, tab_bull, tab_bear, tab_mom, tab_break = st.tabs([
        f"📊 All Setups ({len(filtered_stocks)})",
        f"🟢 Bullish Open=Low ({len(open_low_stocks)})",
        f"🔴 Bearish Open=High ({len(open_high_stocks)})",
        f"🔥 Momentum ({len(momentum_stocks)})",
        f"🚀 5m Breakouts ({len(breakout_stocks)})"
    ])

    def format_df_for_display(stock_list, include_momentum_cols=False):
        if not stock_list:
            return pd.DataFrame()
        df = pd.DataFrame(stock_list).copy()
        
        cols = [
            "ticker", "setup_type", "open", "entry_price", "ltp", "pnl_pct", 
            "change_pct", "vol_surge", "stoploss", "target_1", "target_2", "exact_match",
            "momentum_confirmed", "breakout_type", "signal"
        ]
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
            "target_1": "Target 1 (₹)", "target_2": "Target 2 (₹)",
            "exact_match": "Exact", "momentum_confirmed": "🔥 Momentum",
            "prev_day_high": "Prev Day High (₹)", "prev_day_low": "Prev Day Low (₹)",
            "breakout_type": "Type", "signal": "Signal"
        }
        df.columns = [rename_map.get(c, c) for c in df.columns]
        
        if "PnL % (Entry→LTP)" in df.columns:
            df["PnL % (Entry→LTP)"] = df["PnL % (Entry→LTP)"].apply(
                lambda x: f"🟢 +{float(x):.2f}%" if x is not None and float(x) >= 0 else f"🔴 {float(x):.2f}%" if x is not None else "—"
            )
        
        if "Day Chg (%)" in df.columns:
            df["Day Chg (%)"]     = df["Day Chg (%)"].apply(lambda x: f"{float(x):+.2f}%")
        if "Vol Surge" in df.columns:
            df["Vol Surge"]       = df["Vol Surge"].apply(lambda x: f"{float(x):.2f}x")
        if "Open (₹)" in df.columns:
            df["Open (₹)"]        = df["Open (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "5m Entry (₹)" in df.columns:
            df["5m Entry (₹)"]    = df["5m Entry (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "LTP (₹)" in df.columns:
            df["LTP (₹)"]         = df["LTP (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "Stoploss (₹)" in df.columns:
            df["Stoploss (₹)"]    = df["Stoploss (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "Target 1 (₹)" in df.columns:
            df["Target 1 (₹)"]   = df["Target 1 (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "Target 2 (₹)" in df.columns:
            df["Target 2 (₹)"]   = df["Target 2 (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        if "Exact" in df.columns:
            df["Exact"]           = df["Exact"].apply(lambda x: "⭐ EXACT" if x else "Standard")
        if "🔥 Momentum" in df.columns:
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
            df_mom = format_df_for_display(momentum_stocks, include_momentum_cols=True)
            st.dataframe(df_mom, use_container_width=True, height=480)
        else:
            st.info("No Momentum-confirmed setups detected.")

    with tab_break:
        if breakout_stocks:
            df_break = format_df_for_display(breakout_stocks, include_momentum_cols=True)
            st.dataframe(df_break, use_container_width=True, height=480)
        else:
            st.info("No 5-min Breakout / Breakdown setups detected.")

    if filtered_stocks:
        df_export = pd.DataFrame(filtered_stocks)
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download F&O CSV Report",
            data=csv_bytes,
            file_name=f"nifty_fo_screener_{int(time.time())}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.caption(f"Last Scan Execution Time: {scan_results.get('scan_time')}")


# ==============================================================================
# MODE 2: Nifty 500 Supertrend + MA Multitimeframe Screener
# ==============================================================================
else:

    st.title("🚀 Nifty 500 MA Bull Stack + Weekly ST Screener")
    st.caption("Weekly ST(10,3) ✅  Price > 50 SMA > 100 SMA > 200 SMA ✅  |  Intraday Setups & 5m Breakouts")

    st.sidebar.header("⚙️ Nifty 500 Controls")

    tolerance = st.sidebar.slider(
        "Open Buffer Tolerance (%)",
        min_value=0.00,
        max_value=0.50,
        value=0.20,
        step=0.05,
        help="Filter Open=Low stocks where Open price is within X% of Low"
    )

    strict_only = st.sidebar.checkbox(
        "Zap Exact Matches Only (Diff < 0.02%)",
        value=False,
        help="Only show stocks with near-zero shadow"
    )

    if st.sidebar.button("🔄 Run Nifty 500 Scanner", use_container_width=True, type="primary"):
        st.cache_data.clear()

    @st.cache_data(ttl=300)
    def get_nifty500_scan(tol):
        return run_nifty500_scan(tolerance_pct=tol)

    with st.spinner(f"Scanning {len(get_nifty500_universe_cached())} Nifty 500 stocks — Weekly ST(10,3) + MA Bull Stack (Price > 50 > 100 > 200 SMA)…"):
        nifty500_results = get_nifty500_scan(tolerance)

    qualified  = sorted(nifty500_results.get("qualified_stocks", []), key=lambda s: s.get("change_pct", 0), reverse=True)
    raw_setups = nifty500_results.get("momentum_setups",  [])
    breakout_stocks = sorted(nifty500_results.get("breakout_stocks", []), key=lambda s: s.get("breakout_gap", 0), reverse=True)

    setups = sorted([
        s for s in raw_setups
        if s.get("diff_from_open_pct", 99) <= tolerance and (not strict_only or s.get("exact_match"))
    ], key=lambda s: s.get("change_pct", 0), reverse=True)
    mom_conf   = sorted([s for s in setups if s.get("momentum_confirmed")], key=lambda s: s.get("change_pct", 0), reverse=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🔭 Scanned", nifty500_results.get("total_scanned", 0), "Nifty 500 Universe")
    with col2:
        st.metric("✅ Bull Stack Qualified", nifty500_results.get("qualified_count", 0), "Weekly ST + 50>100>200 SMA")
    with col3:
        st.metric("🟢 Open = Low Setups", len(setups), "Bullish Buy Candidates")
    with col4:
        st.metric("🔥 Momentum Conf.", len(mom_conf), "Open=Low + 5m > Prev High")
    with col5:
        st.metric("🚀 5m Breakout", len(breakout_stocks), "5m Close > Prev Day High")

    st.info(
        "💡 **Logic:** Stocks must have **Price > Weekly Supertrend(10,3)** + **Price > 50 SMA > 100 SMA > 200 SMA** "
        "(MA Bull Stack evaluated in background). "
        "🚀 **5m Breakout:** 5-min close breaks above previous day's High (no Open=Low required)."
    )
    st.markdown("---")

    def fmt_500(stock_list, intraday=False):
        if not stock_list:
            return pd.DataFrame()
        df = pd.DataFrame(stock_list)
        base_cols = ["ticker", "current_price", "change_pct", "vol_surge",
                     "weekly_supertrend", "sma_50", "sma_100", "sma_200", "ma_distance_pct"]
        extra = ["day_open", "day_low", "entry_price", "stoploss", "target_1", "target_2",
                 "exact_match", "pnl_pct", "momentum_confirmed", "breakout_5m"] if intraday else []
        cols = [c for c in base_cols + extra if c in df.columns]
        df = df[cols].copy()

        rename = {
            "ticker": "Ticker", "current_price": "Price (₹)", "change_pct": "Day Chg%",
            "vol_surge": "Vol Surge", "weekly_supertrend": "Weekly ST (₹)",
            "sma_50": "50 SMA (₹)", "sma_100": "100 SMA (₹)", "sma_200": "200 SMA (₹)",
            "ma_distance_pct": "50 SMA Dist%", "day_open": "Open (₹)", "day_low": "Low (₹)",
            "entry_price": "5m Entry (₹)", "stoploss": "Stoploss (₹)",
            "target_1": "Target 1 (₹)", "target_2": "Target 2 (₹)",
            "exact_match": "Exact", "pnl_pct": "PnL%", "momentum_confirmed": "🔥 Mom",
            "breakout_5m": "🚀 Breakout"
        }
        df.columns = [rename.get(c, c) for c in df.columns]

        for col in ["Price (₹)", "Weekly ST (₹)", "50 SMA (₹)", "100 SMA (₹)", "200 SMA (₹)",
                    "Open (₹)", "Low (₹)", "5m Entry (₹)", "Stoploss (₹)", "Target 1 (₹)", "Target 2 (₹)"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"₹{float(x):,.2f}" if x is not None and not pd.isna(x) else "—")

        for col in ["Day Chg%", "50 SMA Dist%", "PnL%"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{float(x):+.2f}%" if x is not None and not pd.isna(x) else "—")

        if "Vol Surge" in df.columns:
            df["Vol Surge"] = df["Vol Surge"].apply(lambda x: f"{float(x):.2f}x" if x is not None else "—")
        if "Exact" in df.columns:
            df["Exact"] = df["Exact"].apply(lambda x: "⭐ EXACT" if x else "Standard")
        if "🔥 Mom" in df.columns:
            df["🔥 Mom"] = df["🔥 Mom"].apply(lambda x: "🔥 YES" if x else "—")
        if "🚀 Breakout" in df.columns:
            df["🚀 Breakout"] = df["🚀 Breakout"].apply(lambda x: "🚀 YES" if x else "—")
        return df

    tab_all, tab_setup, tab_mom, tab_break = st.tabs([
        f"✅ Bull Stack Qualified ({len(qualified)})",
        f"📈 Intraday Setups ({len(setups)})",
        f"🔥 Momentum Confirmed ({len(mom_conf)})",
        f"🚀 5m Breakouts ({len(breakout_stocks)})"
    ])

    with tab_all:
        if qualified:
            st.dataframe(fmt_500(qualified), use_container_width=True, height=500)
        else:
            st.info("No stocks qualified for current settings.")

    with tab_setup:
        if setups:
            st.dataframe(fmt_500(setups, intraday=True), use_container_width=True, height=500)
        else:
            st.info("No Open=Low intraday setups detected.")

    with tab_mom:
        if mom_conf:
            st.info("🔥 **Elite Buy Picks**: Weekly ST + MA Bull Stack + Open=Low setup + 5-min close **above previous day's High**. Highest conviction bullish breakout trades.")
            st.dataframe(fmt_500(mom_conf, intraday=True), use_container_width=True, height=500)
        else:
            st.warning("No momentum-confirmed Open=Low setups yet.")

    if qualified:
        csv = pd.DataFrame(qualified).to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Nifty 500 CSV Report",
            csv,
            f"nifty500_bullstack_screener_{int(time.time())}.csv",
            "text/csv",
            use_container_width=True
        )

    st.caption(f"Last scan: {nifty500_results.get('scan_time', '—')} | Weekly ST(10,3) + MA Bull Stack (Price > 50 > 100 > 200 SMA)")

