"""
Nifty 500 Supertrend + MA Screener - Streamlit Cloud App
"""
import streamlit as st
import pandas as pd
import time
from nifty500_screener import NIFTY500_STOCKS, run_nifty500_scan

st.set_page_config(
    page_title="Nifty 500 Supertrend Screener",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .main { background-color: #07090f; color: #f8fafc; }
  .stMetric {
    background: rgba(15, 20, 40, 0.7);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 16px; border-radius: 12px;
  }
  .stMetric label { color: #94a3b8 !important; font-size: 0.85rem !important; }
  .stMetric [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem !important; font-weight: 800 !important;
  }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Nifty 500 Supertrend + SMA Screener")
st.caption("Monthly ST(10,3) ✅  Weekly ST(10,3) ✅  Price > SMA(N) ✅  |  Bonus: Open=Low/High Intraday Setup Detection")

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Screener Settings")

ma_period = st.sidebar.number_input(
    "MA Period (days)", min_value=5, max_value=500, value=50, step=5,
    help="Moving Average period. Default=50 (50-day SMA)"
)
ma_type = st.sidebar.radio("MA Type", ["SMA", "EMA"], horizontal=True)
tolerance = st.sidebar.slider(
    "Open=Low/High Tolerance (%)", 0.00, 0.50, 0.20, 0.05,
    help="Buffer for intraday Open=Low/High setup detection"
)
if st.sidebar.button("🔄 Run Screener", use_container_width=True, type="primary"):
    st.cache_data.clear()

# ── Cached scan ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_scan(ma_period, ma_type, tolerance):
    return run_nifty500_scan(
        ma_period=ma_period, ma_type=ma_type, tolerance_pct=tolerance
    )

with st.spinner(f"Scanning {len(NIFTY500_STOCKS)} Nifty 500 stocks — Monthly ST + Weekly ST + {ma_type}({ma_period})…"):
    results = get_scan(ma_period, ma_type, tolerance)

qualified  = results.get("qualified_stocks", [])
setups     = results.get("momentum_setups",  [])
mom_conf   = [s for s in setups if s.get("momentum_confirmed")]

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🔭 Scanned",          results.get("total_scanned", 0),  "Nifty 500 Universe")
c2.metric("✅ ST Qualified",     results.get("qualified_count", 0), "Monthly + Weekly + MA")
c3.metric("📈 Intraday Setups",  results.get("momentum_setup_count", 0), "Open=Low or Open=High")
c4.metric("🔥 Momentum Conf.",   results.get("momentum_confirmed_count", 0), "5-min close crosses Prev extreme")
c5.metric("📅 Last Scan",        results.get("scan_time", "—")[:16], "")

st.info(
    f"💡 **Logic:** Stocks must be **above Monthly Supertrend(10,3)** + **above Weekly Supertrend(10,3)** "
    f"+ **price > {ma_type}({ma_period})**. Qualified stocks are then checked for today's Open=Low / Open=High "
    f"intraday setup. 🔥 Momentum = 5-min close crosses previous day's High/Low."
)
st.markdown("---")

# ── Helper: format table ──────────────────────────────────────────────────────
def fmt(stock_list, intraday=False):
    if not stock_list:
        return pd.DataFrame()
    df = pd.DataFrame(stock_list)
    base_cols = ["ticker", "current_price", "change_pct", "vol_surge",
                 "monthly_supertrend", "weekly_supertrend", "ma_value", "ma_distance_pct"]
    extra = ["setup_type", "entry_price", "stoploss", "target_1", "target_2",
             "diff_from_open_pct", "pnl_pct", "momentum_confirmed"] if intraday else []
    cols = [c for c in base_cols + extra if c in df.columns]
    df = df[cols].copy()

    rename = {
        "ticker": "Ticker", "current_price": "Price (₹)", "change_pct": "Day Chg%",
        "vol_surge": "Vol Surge", "monthly_supertrend": "Monthly ST (₹)",
        "weekly_supertrend": "Weekly ST (₹)", "ma_value": f"{ma_type}({ma_period}) ₹",
        "ma_distance_pct": "MA Dist%", "setup_type": "Setup", "entry_price": "Entry (₹)",
        "stoploss": "Stoploss (₹)", "target_1": "Target 1 (₹)", "target_2": "Target 2 (₹)",
        "diff_from_open_pct": "Shadow%", "pnl_pct": "PnL%", "momentum_confirmed": "🔥 Mom"
    }
    df.columns = [rename.get(c, c) for c in df.columns]

    for col in ["Price (₹)", "Monthly ST (₹)", "Weekly ST (₹)",
                f"{ma_type}({ma_period}) ₹", "Entry (₹)", "Stoploss (₹)",
                "Target 1 (₹)", "Target 2 (₹)"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"₹{float(x):,.2f}" if x else "—")

    for col in ["Day Chg%", "MA Dist%", "PnL%", "Shadow%"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{float(x):+.2f}%" if x is not None else "—")

    if "Vol Surge" in df.columns:
        df["Vol Surge"] = df["Vol Surge"].apply(lambda x: f"{float(x):.2f}x")
    if "🔥 Mom" in df.columns:
        df["🔥 Mom"] = df["🔥 Mom"].apply(lambda x: "🔥 YES" if x else "—")
    return df

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_all, tab_setup, tab_mom = st.tabs([
    f"✅ All Qualified ({len(qualified)})",
    f"📈 Intraday Setups ({len(setups)})",
    f"🔥 Momentum Confirmed ({len(mom_conf)})"
])

with tab_all:
    if qualified:
        st.dataframe(fmt(qualified), use_container_width=True, height=500)
    else:
        st.info("No stocks qualified. Try adjusting MA period or run after market open.")

with tab_setup:
    if setups:
        st.info("These stocks passed all 3 Supertrend + MA conditions **AND** show an Open=Low or Open=High intraday setup today.")
        st.dataframe(fmt(setups, intraday=True), use_container_width=True, height=500)
    else:
        st.warning("No intraday setups on qualified stocks today.")

with tab_mom:
    if mom_conf:
        st.info("🔥 **Elite picks**: Supertrend bullish + Open=Low setup + 5-min close **above previous day's High** (or below prev Low for OPEN=HIGH). Highest conviction trades.")
        st.dataframe(fmt(mom_conf, intraday=True), use_container_width=True, height=500)
    else:
        st.warning("No momentum-confirmed setups yet. Check again after 9:25 AM IST.")

# ── CSV Export ────────────────────────────────────────────────────────────────
if qualified:
    csv = pd.DataFrame(qualified).to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv,
                       f"nifty500_st_screener_{int(time.time())}.csv",
                       "text/csv", use_container_width=True)

st.caption(f"Last scan: {results.get('scan_time', '—')} | "
           f"Monthly ST(10,3) + Weekly ST(10,3) + {ma_type}({ma_period})")
