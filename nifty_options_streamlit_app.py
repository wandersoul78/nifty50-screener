"""
Nifty 50 Options Open=Low & Open=High Web Dashboard (Streamlit)
========================================================================
Standalone Web Dashboard for Nifty Options Open=Low & Open=High setup analysis.
"""

import sys
import os
import json
import time
import datetime
import pandas as pd
import streamlit as st

# Import standalone options screener module
from nifty_options_ohl_screener import run_nifty_options_ohl_screener, get_nifty_spot_yahoo, fetch_nse_live_options

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Page Configuration
st.set_page_config(
    page_title="Nifty Options Open=Low & High Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphism Theme)
st.markdown("""
<style>
    .main {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }
    .bullish-badge {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
    }
    .bearish-badge {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def load_local_json_data():
    """Loads latest json data if available."""
    json_path = "nifty_options_ohl_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def main():
    st.title("⚡ Nifty 50 Options Open=Low & Open=High Screener")
    st.caption("Live Options Analytics for ATM ± 6 Strikes (NSE India + Yahoo Finance)")

    # Sidebar Controls
    st.sidebar.title("⚙️ Controls & Parameters")
    
    num_strikes = st.sidebar.slider("Strikes Range (ATM ± N)", min_value=3, max_value=10, value=6, step=1)
    tolerance = st.sidebar.slider("Tolerance (Max ₹ Tick Diff)", min_value=0.0, max_value=2.0, value=0.5, step=0.1)
    
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto Refresh (Every 30s)", value=False)
    
    run_scan_btn = st.sidebar.button("🔄 Refresh Live Options Data", use_container_width=True)

    # State management for scan data
    if "options_data" not in st.session_state or run_scan_btn:
        with st.spinner("Fetching live Nifty options chain from NSE..."):
            st.session_state.options_data = run_nifty_options_ohl_screener(
                num_strikes=num_strikes, 
                max_tick_diff=tolerance
            )

    data = st.session_state.options_data or load_local_json_data()

    if not data:
        st.error("Failed to load options data. Click 'Refresh Live Options Data' to try again.")
        return

    spot_price = data.get('spot_price', 0.0)
    atm_strike = data.get('atm_strike', 0)
    expiry = data.get('expiry', 'N/A')
    timestamp = data.get('timestamp', 'N/A')

    matches = data.get('matches', [])
    evaluated = data.get('all_evaluated_contracts', [])

    # Header Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Nifty 50 Spot", f"₹{spot_price:,.2f}")
    with m2:
        st.metric("ATM Strike", f"{atm_strike}")
    with m3:
        st.metric("Nearest Expiry", f"{expiry}")
    with m4:
        st.metric("Total Setups Found", f"{len(matches)}")
    with m5:
        st.metric("Last Updated", f"{timestamp.split()[-1] if ' ' in timestamp else timestamp}")

    st.markdown("---")

    # Filter Tabs
    tab_setups, tab_chain, tab_all = st.tabs(["🎯 Matching Setups", "📊 Option Chain Matrix", "📋 All Contracts List"])

    df_matches = pd.DataFrame(matches)
    df_eval = pd.DataFrame(evaluated)

    with tab_setups:
        st.subheader("🎯 Matching Open = Low & Open = High Setups")
        
        if not df_matches.empty:
            # Filter options
            signal_filter = st.radio("Filter Signal:", ["ALL", "BULLISH (OPEN=LOW)", "BEARISH (OPEN=HIGH)"], horizontal=True)
            
            filtered_matches = df_matches.copy()
            if signal_filter == "BULLISH (OPEN=LOW)":
                filtered_matches = filtered_matches[filtered_matches['signal'] == 'BULLISH']
            elif signal_filter == "BEARISH (OPEN=HIGH)":
                filtered_matches = filtered_matches[filtered_matches['signal'] == 'BEARISH']

            # Render Cards View
            st.markdown("##### 📌 High-Conviction Option Setup Cards")
            card_cols = st.columns(3)
            for idx, row in filtered_matches.iterrows():
                col = card_cols[idx % 3]
                is_bullish = row['signal'] == 'BULLISH'
                badge_class = "bullish-badge" if is_bullish else "bearish-badge"
                
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; font-size: 1.25rem;">{row['symbol']}</h3>
                            <span class="{badge_class}">{row['setup']}</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0 12px 0;">ATM Offset: <b>{row['atm_offset']}</b> | Expiry: <b>{row['expiry']}</b></p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;">
                            <div>LTP: <b style="font-size: 1.1rem; color: #38bdf8;">₹{row['ltp']:.2f}</b></div>
                            <div>Open: <b>₹{row['open']:.2f}</b></div>
                            <div>High: <b>₹{row['high']:.2f}</b></div>
                            <div>Low: <b>₹{row['low']:.2f}</b></div>
                            <div>Open Interest: <b>{row['open_interest']:,}</b></div>
                            <div>Volume: <b>{row['volume']:,}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("##### 📄 Data Table View")
            display_cols = ['symbol', 'signal', 'setup', 'open', 'high', 'low', 'ltp', 'diff_pts', 'open_interest', 'volume']
            st.dataframe(filtered_matches[display_cols], use_container_width=True)

        else:
            st.info("ℹ️ No exact Open=Low or Open=High option setups found matching tolerance rules at this moment.")

    with tab_chain:
        st.subheader("📊 Option Chain Matrix (Calls vs Puts around ATM)")
        if not df_eval.empty:
            # Pivot table to construct Call vs Put Option Chain
            strikes = sorted(df_eval['strike'].unique())
            chain_rows = []

            for strike in strikes:
                ce_row = df_eval[(df_eval['strike'] == strike) & (df_eval['option_type'] == 'CE')]
                pe_row = df_eval[(df_eval['strike'] == strike) & (df_eval['option_type'] == 'PE')]

                ce = ce_row.iloc[0].to_dict() if not ce_row.empty else {}
                pe = pe_row.iloc[0].to_dict() if not pe_row.empty else {}

                is_atm = (strike == atm_strike)

                chain_rows.append({
                    'CE Setup': ce.get('setup', '-'),
                    'CE LTP': f"₹{ce.get('ltp', 0.0):.2f}" if ce else '-',
                    'CE Open': f"₹{ce.get('open', 0.0):.2f}" if ce else '-',
                    'CE High/Low': f"₹{ce.get('high', 0.0):.2f} / ₹{ce.get('low', 0.0):.2f}" if ce else '-',
                    'STRIKE': f"🎯 {strike} (ATM)" if is_atm else f"{strike}",
                    'PE High/Low': f"₹{pe.get('high', 0.0):.2f} / ₹{pe.get('low', 0.0):.2f}" if pe else '-',
                    'PE Open': f"₹{pe.get('open', 0.0):.2f}" if pe else '-',
                    'PE LTP': f"₹{pe.get('ltp', 0.0):.2f}" if pe else '-',
                    'PE Setup': pe.get('setup', '-')
                })

            df_matrix = pd.DataFrame(chain_rows)
            st.dataframe(df_matrix, use_container_width=True)

    with tab_all:
        st.subheader("📋 All Evaluated Option Contracts (ATM ± 6)")
        if not df_eval.empty:
            all_cols = ['symbol', 'atm_offset', 'setup', 'open', 'high', 'low', 'ltp', 'open_interest', 'volume']
            st.dataframe(df_eval[all_cols], use_container_width=True)

    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
