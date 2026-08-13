"""
Combined Nifty F&O Stock, Nifty Options, Bank Nifty Options & Top Stock Options Web Dashboard
==============================================================================================
Features:
1. Streamlit Cloud Main App File (`streamlit_app.py`).
2. 4 Screener Modes:
   - 📈 Nifty F&O Stocks (Open = Low / High)
   - ⚡ Nifty 50 Options
   - 🏦 Bank Nifty Options
   - 🔥 Top Traded Stock Options
3. Options pages contain controls directly on page (Expiry Selector & Strike Range).
4. Option Chain Matrix Table with separate High & Low columns.
"""

import sys
import os
import json
import time
import datetime
import pandas as pd
import streamlit as st

from combined_screener import run_combined_screener

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Page Configuration
st.set_page_config(
    page_title="Nifty & Bank Nifty Options Screener",
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
        font-size: 0.85rem;
    }
    .bearish-badge {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def load_local_json_data():
    """Loads latest combined screener json data if available."""
    json_path = "combined_screener_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def render_options_page(title, subtitle, opt_data, index_name="NIFTY"):
    """Generic renderer for Option Chain pages (Nifty & Bank Nifty)."""
    st.title(title)
    st.caption(subtitle)

    available_expiries = opt_data.get('available_expiries', [])
    current_expiry = opt_data.get('active_expiry', available_expiries[0] if available_expiries else 'N/A')

    # Controls directly on Options page
    ctrl1, ctrl2 = st.columns([1, 1])
    with ctrl1:
        selected_expiry = st.selectbox(
            f"📅 Select {index_name} Expiry Date", 
            options=available_expiries, 
            index=available_expiries.index(current_expiry) if current_expiry in available_expiries else 0,
            key=f"{index_name}_expiry_select"
        )
    with ctrl2:
        num_strikes = st.slider(
            f"🎯 Strike Range (ATM ± N Strikes)", 
            min_value=3, 
            max_value=10, 
            value=st.session_state.get(f"{index_name}_strikes", 6), 
            step=1,
            key=f"{index_name}_strikes_slider"
        )

    # Re-trigger scanner if controls change
    state_exp_key = f"{index_name}_opt_expiry"
    state_strk_key = f"{index_name}_opt_strikes"

    if selected_expiry != st.session_state.get(state_exp_key) or num_strikes != st.session_state.get(state_strk_key):
        st.session_state[state_exp_key] = selected_expiry
        st.session_state[state_strk_key] = num_strikes
        with st.spinner(f"Updating {index_name} option chain for selected expiry & strikes..."):
            nifty_exp = st.session_state.get("NIFTY_opt_expiry")
            bank_exp = st.session_state.get("BANKNIFTY_opt_expiry")
            st.session_state.combined_data = run_combined_screener(
                num_strikes=num_strikes, 
                nifty_expiry=nifty_exp,
                banknifty_expiry=bank_exp
            )
            st.rerun()

    spot_price = opt_data.get('spot_price', 0.0)
    atm_strike = opt_data.get('atm_strike', 0)
    opt_matches = opt_data.get('opt_matches', [])
    opt_matrix = opt_data.get('opt_matrix', [])

    # Header Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(f"{index_name} Spot", f"₹{spot_price:,.2f}")
    with m2:
        st.metric("ATM Strike", f"{atm_strike}")
    with m3:
        st.metric("Active Expiry", f"{current_expiry}")
    with m4:
        st.metric("Matching Option Setups", f"{len(opt_matches)}")

    st.markdown("---")

    # ── SECTION 1: MATCHING OPTION SETUP CARDS ──
    st.markdown(f"### 🎯 Matching Open = Low & Open = High Option Cards ({current_expiry})")
    
    if opt_matches:
        card_cols = st.columns(3)
        for idx, opt in enumerate(opt_matches):
            col = card_cols[idx % 3]
            is_bullish = opt['signal'] == 'BULLISH'
            badge_class = "bullish-badge" if is_bullish else "bearish-badge"

            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1.25rem;">{opt['symbol']}</h3>
                        <span class="{badge_class}">{opt['setup']}</span>
                    </div>
                    <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0 12px 0;">ATM Offset: <b>{opt['atm_offset']}</b> | Expiry: <b>{opt['expiry']}</b></p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;">
                        <div>LTP: <b style="font-size: 1.1rem; color: #38bdf8;">₹{opt['ltp']:.2f}</b></div>
                        <div>Open: <b>₹{opt['open']:.2f}</b></div>
                        <div>High: <b>₹{opt['high']:.2f}</b></div>
                        <div>Low: <b>₹{opt['low']:.2f}</b></div>
                        <div>Open Interest: <b>{opt['open_interest']:,}</b></div>
                        <div>Volume: <b>{opt['volume']:,}</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"ℹ️ No exact Open=Low or Open=High option setups matching tolerance rules for expiry '{current_expiry}'.")

    st.markdown("---")

    # ── SECTION 2: FULL OPTION CHAIN MATRIX TABLE WITH SEPARATE HIGH & LOW COLUMNS ──
    st.markdown(f"### 📊 {index_name} Option Chain Matrix Table (ATM ± {num_strikes} Strikes)")
    
    if opt_matrix:
        df_matrix_raw = pd.DataFrame(opt_matrix)
        strikes = sorted(df_matrix_raw['strike'].unique())
        chain_rows = []

        for strike in strikes:
            ce_row = df_matrix_raw[(df_matrix_raw['strike'] == strike) & (df_matrix_raw['option_type'] == 'CE')]
            pe_row = df_matrix_raw[(df_matrix_raw['strike'] == strike) & (df_matrix_raw['option_type'] == 'PE')]

            ce = ce_row.iloc[0].to_dict() if not ce_row.empty else {}
            pe = pe_row.iloc[0].to_dict() if not pe_row.empty else {}

            is_atm = (strike == atm_strike)

            chain_rows.append({
                'CE Setup': ce.get('setup', '-'),
                'CE High': f"₹{ce.get('high', 0.0):.2f}" if ce else '-',
                'CE Low': f"₹{ce.get('low', 0.0):.2f}" if ce else '-',
                'CE Open': f"₹{ce.get('open', 0.0):.2f}" if ce else '-',
                'CE LTP': f"₹{ce.get('ltp', 0.0):.2f}" if ce else '-',
                'STRIKE': f"🎯 {strike} (ATM)" if is_atm else f"{strike}",
                'PE LTP': f"₹{pe.get('ltp', 0.0):.2f}" if pe else '-',
                'PE Open': f"₹{pe.get('open', 0.0):.2f}" if pe else '-',
                'PE High': f"₹{pe.get('high', 0.0):.2f}" if pe else '-',
                'PE Low': f"₹{pe.get('low', 0.0):.2f}" if pe else '-',
                'PE Setup': pe.get('setup', '-')
            })

        df_matrix = pd.DataFrame(chain_rows)
        st.dataframe(df_matrix, use_container_width=True)


def main():
    # ── SIDEBAR NAVIGATION (4 MODES) ──
    st.sidebar.title("🎯 Screener Navigation")
    screener_mode = st.sidebar.radio(
        "Select Active Screener:",
        [
            "📈 Nifty F&O Stocks (Open = Low / High)",
            "⚡ Nifty 50 Options",
            "🏦 Bank Nifty Options",
            "🔥 Top Traded Stock Options"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    run_scan_btn = st.sidebar.button("🔄 Refresh Live Scanner Data", use_container_width=True)

    # Initial data load
    data = st.session_state.get("combined_data") or load_local_json_data() or {}
    
    if "combined_data" not in st.session_state or run_scan_btn:
        with st.spinner("Scanning live market data..."):
            nifty_exp = st.session_state.get("NIFTY_opt_expiry")
            bank_exp = st.session_state.get("BANKNIFTY_opt_expiry")
            st.session_state.combined_data = run_combined_screener(
                num_strikes=6,
                nifty_expiry=nifty_exp,
                banknifty_expiry=bank_exp
            )
            data = st.session_state.combined_data

    if not data:
        st.error("Failed to load screener data. Click 'Refresh Live Scanner Data' to run the scanner.")
        return

    timestamp = data.get('timestamp', 'N/A')

    # =========================================================================
    # PAGE 1: NIFTY F&O STOCKS SCREENER
    # =========================================================================
    if screener_mode == "📈 Nifty F&O Stocks (Open = Low / High)":
        st.title("📈 Nifty F&O Stocks Screener")
        st.caption("Shows F&O Stocks that meet Open = Low (Bullish) or Open = High (Bearish) setup.")

        stock_matches = data.get('stock_matches', [])
        bullish_stocks = [s for s in stock_matches if s.get('signal') == 'BULLISH']
        bearish_stocks = [s for s in stock_matches if s.get('signal') == 'BEARISH']

        # Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Setups Found", f"{len(stock_matches)}")
        with c2:
            st.metric("Bullish (Open = Low)", f"{len(bullish_stocks)}")
        with c3:
            st.metric("Bearish (Open = High)", f"{len(bearish_stocks)}")
        with c4:
            st.metric("Last Updated", f"{timestamp.split()[-1] if ' ' in timestamp else timestamp}")

        st.markdown("---")

        if stock_matches:
            stock_filter = st.radio("Filter Stock Setups:", ["ALL", "BULLISH (OPEN=LOW)", "BEARISH (OPEN=HIGH)"], horizontal=True)
            
            filtered_stocks = stock_matches
            if stock_filter == "BULLISH (OPEN=LOW)":
                filtered_stocks = bullish_stocks
            elif stock_filter == "BEARISH (OPEN=HIGH)":
                filtered_stocks = bearish_stocks

            # Sort by highest absolute day change %
            sorted_stocks = sorted(filtered_stocks, key=lambda x: abs(x.get('day_change_pct', 0.0)), reverse=True)
            top_6_cards = sorted_stocks[:6]  # Show top 6 momentum stock cards

            st.markdown("### 📌 Top 6 Highest Change % Stock Cards")
            card_cols = st.columns(3)
            for idx, s in enumerate(top_6_cards):
                col = card_cols[idx % 3]
                is_bullish = s['signal'] == 'BULLISH'
                badge_class = "bullish-badge" if is_bullish else "bearish-badge"
                setup_label = "OPEN=LOW (BULLISH)" if is_bullish else "OPEN=HIGH (BEARISH)"
                change_color = "#4ade80" if s.get('day_change_pct', 0) >= 0 else "#f87171"

                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; font-size: 1.3rem;">{s['ticker']}</h3>
                            <span class="{badge_class}">{setup_label}</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0 12px 0;">
                            Change: <b style="color: {change_color}; font-size: 1rem;">{s.get('day_change_pct', 0.0):+.2f}%</b> | 5m Entry: <b>₹{s['entry_price_5m']:.2f}</b>
                        </p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;">
                            <div>Open: <b>₹{s['open']:.2f}</b></div>
                            <div>Close: <b style="color: #38bdf8;">₹{s['latest_close']:.2f}</b></div>
                            <div>High: <b>₹{s['high']:.2f}</b></div>
                            <div>Low: <b>₹{s['low']:.2f}</b></div>
                            <div>Target: <b style="color: #4ade80;">₹{s['target']:.2f}</b></div>
                            <div>StopLoss: <b style="color: #f87171;">₹{s['stop_loss']:.2f}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("### 📄 Detailed Stocks Table")
            if filtered_stocks:
                table_rows = []
                for s in sorted_stocks:
                    table_rows.append({
                        'Ticker': s['ticker'],
                        'Signal': s['signal'],
                        'Setup': s['setup'],
                        'Chng_%': f"{s.get('day_change_pct', 0.0):+.2f}%",
                        'PnL_%': f"{s['pnl_pct']:+.2f}%",
                        'Open': s['open'],
                        'High': s['high'],
                        'Low': s['low'],
                        'Entry_Price': s['entry_price_5m'],
                        'Close': s['latest_close'],
                        'Target': s['target'],
                        'StopLoss': s['stop_loss'],
                        'Volume': f"{s['volume']:,}"
                    })
                df_table = pd.DataFrame(table_rows)
                st.dataframe(df_table, use_container_width=True)

        else:
            st.info("ℹ️ No F&O stocks matching Open=Low or Open=High setup at this moment.")

    # =========================================================================
    # PAGE 2: NIFTY 50 OPTIONS SCREENER
    # =========================================================================
    elif screener_mode == "⚡ Nifty 50 Options":
        nifty_data = data.get('nifty_options', {})
        render_options_page(
            title="⚡ Nifty 50 Options Screener",
            subtitle="Live Nifty 50 Option Chain analytics and Open=Low / Open=High setups.",
            opt_data=nifty_data,
            index_name="NIFTY"
        )

    # =========================================================================
    # PAGE 3: BANK NIFTY OPTIONS SCREENER
    # =========================================================================
    elif screener_mode == "🏦 Bank Nifty Options":
        bank_data = data.get('banknifty_options', {})
        render_options_page(
            title="🏦 Bank Nifty Options Screener",
            subtitle="Live Bank Nifty Option Chain analytics and Open=Low / Open=High setups.",
            opt_data=bank_data,
            index_name="BANKNIFTY"
        )

    # =========================================================================
    # PAGE 4: TOP TRADED STOCK OPTIONS SCREENER
    # =========================================================================
    elif screener_mode == "🔥 Top Traded Stock Options":
        st.title("🔥 Top Traded Stock Options Screener")
        st.caption("Live analytics for top liquid Stock Options (Call & Put) from NSE India.")

        top_stock_data = data.get('top_stock_options', {})
        stock_opt_matches = top_stock_data.get('matches', [])
        all_stock_contracts = top_stock_data.get('all_contracts', [])

        # Calculate metrics
        total_contracts = len(all_stock_contracts)
        max_gainer = "-"
        if all_stock_contracts:
            top_c = max(all_stock_contracts, key=lambda x: x.get('change_pct', 0.0))
            max_gainer = f"{top_c['symbol']} ({top_c['change_pct']:+.2f}%)"

        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Active Stock Contracts", f"{total_contracts}")
        with m2:
            st.metric("Top Premium Gainer", f"{max_gainer}")
        with m3:
            st.metric("Matching Setup Contracts", f"{len(stock_opt_matches)}")
        with m4:
            st.metric("Last Updated", f"{timestamp.split()[-1] if ' ' in timestamp else timestamp}")

        st.markdown("---")

        # ── SECTION 1: MATCHING SETUP STOCK OPTION CARDS ──
        st.markdown("### 🎯 Matching Open = Low & Open = High Stock Option Cards")
        if stock_opt_matches:
            card_cols = st.columns(3)
            for idx, opt in enumerate(stock_opt_matches):
                col = card_cols[idx % 3]
                is_bullish = opt['signal'] == 'BULLISH'
                badge_class = "bullish-badge" if is_bullish else "bearish-badge"
                chg_color = "#4ade80" if opt.get('change_pct', 0) >= 0 else "#f87171"

                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; font-size: 1.25rem;">{opt['symbol']}</h3>
                            <span class="{badge_class}">{opt['setup']}</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0 12px 0;">
                            Stock Spot: <b>₹{opt['spot_price']:,.2f}</b> | Expiry: <b>{opt['expiry']}</b>
                        </p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;">
                            <div>LTP: <b style="font-size: 1.1rem; color: #38bdf8;">₹{opt['ltp']:.2f}</b></div>
                            <div>Change: <b style="color: {chg_color};">{opt['change_pct']:+.2f}%</b></div>
                            <div>Open: <b>₹{opt['open']:.2f}</b></div>
                            <div>High: <b>₹{opt['high']:.2f}</b></div>
                            <div>Low: <b>₹{opt['low']:.2f}</b></div>
                            <div>Open Interest: <b>{opt['open_interest']:,}</b></div>
                            <div>Volume: <b>{opt['volume']:,}</b></div>
                            <div>No of Trades: <b>{opt['no_of_trades']:,}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No exact Open=Low or Open=High stock option setups matching tolerance rules at this moment.")

        st.markdown("---")

        # ── SECTION 2: TOP TRADED STOCK OPTIONS TABLE ──
        st.markdown("### 📊 Top Traded Stock Options Table")
        if all_stock_contracts:
            df_stk_opt = pd.DataFrame(all_stock_contracts)
            cols = ['symbol', 'underlying', 'spot_price', 'strike', 'option_type', 'expiry', 'setup', 'open', 'high', 'low', 'ltp', 'change_pct', 'open_interest', 'volume', 'no_of_trades']
            st.dataframe(df_stk_opt[cols], use_container_width=True)


if __name__ == "__main__":
    main()
