import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import StockCard from './components/StockCard';
import StockTable from './components/StockTable';
import StockDetailModal from './components/StockDetailModal';
import { ArrowUpRight, ArrowDownRight, Zap, RefreshCw, BarChart2, ShieldCheck, Activity, Grid } from 'lucide-react';

export default function App() {
  const [screenerData, setScreenerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tolerance, setTolerance] = useState(0.20);
  const [strictOnly, setStrictOnly] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, BULLISH, BEARISH, MOMENTUM

  const loadScreenerData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/open_high_low_data.json?t=' + Date.now());
      if (response.ok) {
        const data = await response.json();
        setScreenerData(data);
      }
    } catch (error) {
      console.warn("Error loading JSON:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScreenerData();
    // Auto-refresh every 5 minutes during market hours
    const interval = setInterval(() => {
      const now = new Date();
      const h = now.getHours(), m = now.getMinutes();
      const inMarketHours = (h > 9 || (h === 9 && m >= 15)) && (h < 15 || (h === 15 && m <= 30));
      if (inMarketHours) loadScreenerData();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRunScanner = async () => {
    setLoading(true);
    try {
      await loadScreenerData();
    } catch (err) {
      console.error("Scan error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Filter stocks according to tolerance & strict settings
  const rawStocks = screenerData?.all_matches || [];
  const filteredStocks = rawStocks.filter(stock => {
    if (strictOnly && !stock.exact_match) return false;
    return stock.diff_from_open_pct <= tolerance;
  });

  const openLowStocks   = filteredStocks.filter(s => s.setup_type === 'OPEN_LOW');
  const openHighStocks  = filteredStocks.filter(s => s.setup_type === 'OPEN_HIGH');
  const momentumStocks  = filteredStocks.filter(s => s.momentum_confirmed);
  const breakoutStocks  = (screenerData?.breakout_stocks || []);

  const displayedStocks = activeTab === 'BULLISH'   ? openLowStocks
                        : activeTab === 'BEARISH'   ? openHighStocks
                        : activeTab === 'MOMENTUM'  ? momentumStocks
                        : activeTab === 'BREAKOUT'  ? breakoutStocks
                        : filteredStocks;

  const handleExportCSV = () => {
    const exportList = displayedStocks.length ? displayedStocks : filteredStocks;
    if (!exportList.length) return;
    
    const headers = [
      "Ticker", "Setup", "Open", "5mEntry", "LTP", "PnL%",
      "ChangePct", "VolSurge", "Stoploss", "Target1", "Target2",
      "ShadowDiff", "ExactMatch", "MomentumConfirmed", "PrevDayHigh", "PrevDayLow",
      "VWAP", "AboveVWAP", "Risk"
    ];
    const csvRows = [
      headers.join(","),
      ...exportList.map(s => [
        s.ticker, s.setup_type,
        s.open, s.entry_price, s.ltp, s.pnl_pct,
        s.change_pct, s.vol_surge, s.stoploss, s.target_1, s.target_2,
        s.diff_from_open_pct, s.exact_match,
        s.momentum_confirmed, s.prev_day_high, s.prev_day_low,
        s.vwap, s.above_vwap, s.risk_per_share
      ].join(","))
    ];

    const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nifty_fo_screener_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="container" style={{ paddingTop: '24px', paddingBottom: '60px' }}>
      
      {/* Header Bar */}
      <Header 
        scanTime={screenerData?.scan_time}
        onRefresh={handleRunScanner}
        isRefreshing={loading}
        onExportCSV={handleExportCSV}
        tolerance={tolerance}
        setTolerance={setTolerance}
        strictOnly={strictOnly}
        setStrictOnly={setStrictOnly}
      />

      {/* Loading Skeleton — shown only on very first load when no data exists yet */}
      {loading && !screenerData && (
        <div style={{ marginBottom: '24px' }}>
          <div className="grid grid-4" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(5, 1fr)' }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="glass-card kpi-card skeleton" style={{ height: '90px' }} />
            ))}
          </div>
          <div className="grid grid-3" style={{ marginBottom: '24px' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass-card skeleton" style={{ height: '180px' }} />
            ))}
          </div>
          <div className="glass-card skeleton" style={{ height: '320px' }} />
        </div>
      )}

      {/* Hero KPI Stats Grid — hidden during initial skeleton load */}
      {(!loading || screenerData) && (
      <div className="grid grid-4" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(5, 1fr)' }}>
        <div className="glass-card kpi-card">
          <div className="kpi-title">Nifty F&O Stocks Scanned</div>
          <div className="kpi-value mono" style={{ color: 'var(--accent-cyan)' }}>
            {screenerData?.total_scanned || 250}
          </div>
          <div className="kpi-subtitle">NSE Derivative Universe</div>
        </div>

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--bullish)' }}>
          <div className="kpi-title">Open = Low (BUY)</div>
          <div className="kpi-value mono" style={{ color: 'var(--bullish)' }}>
            {openLowStocks.length}
          </div>
          <div className="kpi-subtitle" style={{ color: 'var(--bullish)' }}>Bullish Intraday Setups</div>
        </div>

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--bearish)' }}>
          <div className="kpi-title">Open = High (SELL)</div>
          <div className="kpi-value mono" style={{ color: 'var(--bearish)' }}>
            {openHighStocks.length}
          </div>
          <div className="kpi-subtitle" style={{ color: 'var(--bearish)' }}>Bearish Intraday Setups</div>
        </div>

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--accent-amber)' }}>
          <div className="kpi-title">Exact Matches</div>
          <div className="kpi-value mono" style={{ color: 'var(--accent-amber)' }}>
            {filteredStocks.filter(s => s.exact_match).length}
          </div>
          <div className="kpi-subtitle" style={{ color: 'var(--accent-amber)' }}>Zero Shadow Candidates</div>
        </div>

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--momentum)', background: 'rgba(245, 158, 11, 0.06)' }}>
          <div className="kpi-title" style={{ color: 'var(--momentum)' }}>🔥 Momentum Confirmed</div>
          <div className="kpi-value mono" style={{ color: 'var(--momentum)' }}>
            {momentumStocks.length}
          </div>
          <div className="kpi-subtitle" style={{ color: 'var(--momentum)' }}>5-min close crosses Prev Day extreme</div>
        </div>

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid #a78bfa', background: 'rgba(167,139,250,0.06)', cursor: 'pointer' }}
          onClick={() => setActiveTab('BREAKOUT')}>
          <div className="kpi-title" style={{ color: '#a78bfa' }}>🚀 5m Breakout</div>
          <div className="kpi-value mono" style={{ color: '#a78bfa' }}>
            {breakoutStocks.length}
          </div>
          <div className="kpi-subtitle" style={{ color: '#a78bfa' }}>5m Close &gt; Prev Day High</div>
        </div>
      </div>
      )} {/* end KPI conditional */}

      {/* Top Priority High-Probability Cards */}
      {(() => {
        const cardStocks = activeTab === 'MOMENTUM' ? momentumStocks
                         : activeTab === 'BULLISH'  ? openLowStocks
                         : activeTab === 'BEARISH'  ? openHighStocks
                         : filteredStocks;
        const cardTitle  = activeTab === 'MOMENTUM' ? '🔥 Top Momentum Picks'
                         : activeTab === 'BULLISH'  ? '🟢 Top Bullish Setups'
                         : activeTab === 'BEARISH'  ? '🔴 Top Bearish Setups'
                         : '⚡ Top High-Volume Priority Candidates';
        return cardStocks.length > 0 ? (
          <div style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Zap size={20} color="var(--accent-amber)" /> {cardTitle}
              </h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Sorted by Volume Surge &amp; Setup Strength
              </span>
            </div>
            <div className="grid grid-3">
              {cardStocks.slice(0, 6).map(stock => (
                <StockCard 
                  key={stock.ticker} 
                  stock={stock} 
                  onClick={() => setSelectedStock(stock)} 
                />
              ))}
            </div>
          </div>
        ) : null;
      })()} 

      {/* Full Tabbed Filter Table */}
      <StockTable 
        stocks={displayedStocks}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        allCount={filteredStocks.length}
        bullishCount={openLowStocks.length}
        bearishCount={openHighStocks.length}
        momentumCount={momentumStocks.length}
        breakoutCount={breakoutStocks.length}
        onSelectStock={setSelectedStock}
      />

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetailModal 
          stock={selectedStock} 
          onClose={() => setSelectedStock(null)} 
        />
      )}

    </div>
  );
}
