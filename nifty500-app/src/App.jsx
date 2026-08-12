import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StockTable from './components/StockTable';
import StockDetailModal from './components/StockDetailModal';

export default function App() {
  const [screenerData, setScreenerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [tolerance, setTolerance] = useState(0.20);
  const [selectedStock, setSelectedStock] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, SETUP, MOMENTUM

  const loadScreenerData = async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const response = await fetch('/nifty500_data.json?t=' + Date.now());
      if (response.ok) {
        const data = await response.json();
        setScreenerData(data);
      } else {
        setFetchError(`Server returned ${response.status}. Run the Python screener first.`);
      }
    } catch (error) {
      setFetchError('Could not load screener data. Check that the Python screener has run and nifty500_data.json exists.');
      console.warn('Error loading JSON:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScreenerData();
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
    await loadScreenerData();
  };

  const qualifiedStocks   = screenerData?.qualified_stocks || [];
  const momentumSetups    = screenerData?.momentum_setups || [];
  const momentumConfirmed = momentumSetups.filter(s => s.momentum_confirmed);
  const breakoutStocks    = screenerData?.breakout_stocks || qualifiedStocks.filter(s => s.breakout_5m);
  const gapStocks         = screenerData?.gap_stocks || [];

  const displayedStocks = activeTab === 'SETUP'      ? momentumSetups
                        : activeTab === 'MOMENTUM'   ? momentumConfirmed
                        : activeTab === 'BREAKOUT'   ? breakoutStocks
                        : activeTab === 'GAP_STOCKS' ? gapStocks
                        : qualifiedStocks;

  const handleExportCSV = () => {
    if (!displayedStocks.length) return;
    
    const headers = [
      "Ticker", "Price", "DayChg%", "WeeklyST", "SMA50", "SMA100", "SMA200",
      "50SMADist%", "VolSurge", "Setup", "EntryPrice",
      "Stoploss", "Target1", "Target2", "PnL%", "MomentumConfirmed", "Breakout5m"
    ];
    const csvRows = [
      headers.join(","),
      ...displayedStocks.map(s => [
        s.ticker, s.current_price, s.change_pct, s.weekly_supertrend,
        s.sma_50, s.sma_100, s.sma_200, s.ma_distance_pct, s.vol_surge,
        s.setup_type || "MA BULL STACK", s.entry_price || "",
        s.stoploss || "", s.target_1 || "", s.target_2 || "", s.pnl_pct || "",
        s.momentum_confirmed, s.breakout_5m
      ].join(","))
    ];

    const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nifty500_bullstack_screener_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="container" style={{ paddingTop: '24px', paddingBottom: '60px' }}>
      
      {/* Header */}
      <Header 
        scanTime={screenerData?.scan_time}
        onRefresh={handleRunScanner}
        isRefreshing={loading}
        onExportCSV={handleExportCSV}
        tolerance={tolerance}
        setTolerance={setTolerance}
      />

      {/* Error Banner — shown if JSON fetch fails */}
      {fetchError && (
        <div style={{
          background: 'rgba(244,63,94,0.10)', border: '1px solid rgba(244,63,94,0.35)',
          borderRadius: '10px', padding: '16px 20px', marginBottom: '20px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px'
        }}>
          <span style={{ color: '#f43f5e', fontWeight: '600', fontSize: '0.9rem' }}>
            ⚠️ {fetchError}
          </span>
          <button onClick={handleRunScanner} style={{
            padding: '7px 16px', borderRadius: '8px', fontSize: '0.82rem', fontWeight: '700',
            background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.4)',
            color: '#f43f5e', cursor: 'pointer'
          }}>
            Retry
          </button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && !screenerData && (
        <div style={{ marginBottom: '24px' }}>
          <div className="grid grid-5" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(6, 1fr)' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass-card kpi-card skeleton" style={{ height: '90px' }} />
            ))}
          </div>
          <div className="glass-card skeleton" style={{ height: '400px' }} />
        </div>
      )}

      {/* KPI Stats Grid */}
      {(!loading || screenerData) && (
        <div className="grid grid-5" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(6, 1fr)' }}>
          <div className="glass-card kpi-card">
            <div className="kpi-title">Nifty 500 Scanned</div>
            <div className="kpi-value mono" style={{ color: 'var(--accent-cyan)' }}>
              {screenerData?.total_scanned || 500}
            </div>
            <div className="kpi-subtitle">NSE Broad Universe</div>
          </div>

          <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--accent)' }}>
            <div className="kpi-title">MA Bull Stack Qualified</div>
            <div className="kpi-value mono" style={{ color: 'var(--accent)' }}>
              {screenerData?.qualified_count || qualifiedStocks.length}
            </div>
            <div className="kpi-subtitle" style={{ color: 'var(--accent)' }}>Wk ST + Price &gt; 50 &gt; 100 &gt; 200</div>
          </div>

          <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--bullish)' }}>
            <div className="kpi-title">Intraday Setups</div>
            <div className="kpi-value mono" style={{ color: 'var(--bullish)' }}>
              {momentumSetups.length}
            </div>
            <div className="kpi-subtitle" style={{ color: 'var(--bullish)' }}>Open=Low Setups</div>
          </div>

          <div className="glass-card kpi-card" style={{ borderLeft: '4px solid var(--momentum)', background: 'rgba(245, 158, 11, 0.06)' }}>
            <div className="kpi-title" style={{ color: 'var(--momentum)' }}>🔥 Momentum Confirmed</div>
            <div className="kpi-value mono" style={{ color: 'var(--momentum)' }}>
              {momentumConfirmed.length}
            </div>
            <div className="kpi-subtitle" style={{ color: 'var(--momentum)' }}>Open=Low + 5m Close &gt; Prev High</div>
          </div>

          <div className="glass-card kpi-card" style={{ borderLeft: '4px solid #a78bfa', background: 'rgba(167, 139, 250, 0.06)', cursor: 'pointer' }}
            onClick={() => setActiveTab('BREAKOUT')}>
            <div className="kpi-title" style={{ color: '#a78bfa' }}>🚀 5m Breakout</div>
            <div className="kpi-value mono" style={{ color: '#a78bfa' }}>
              {breakoutStocks.length}
            </div>
            <div className="kpi-subtitle" style={{ color: '#a78bfa' }}>5m Close &gt; Prev Day High</div>
          </div>

          <div className="glass-card kpi-card" style={{ borderLeft: '4px solid #ec4899', background: 'rgba(236, 72, 153, 0.06)', cursor: 'pointer' }}
            onClick={() => setActiveTab('GAP_STOCKS')}>
            <div className="kpi-title" style={{ color: '#ec4899' }}>⚡ Gap Up / Down</div>
            <div className="kpi-value mono" style={{ color: '#ec4899' }}>
              {gapStocks.length}
            </div>
            <div className="kpi-subtitle" style={{ color: '#ec4899' }}>Open &gt; High or &lt; Low</div>
          </div>
        </div>
      )}

      {/* Main Stock Table */}
      <StockTable 
        stocks={displayedStocks}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        allCount={qualifiedStocks.length}
        setupCount={momentumSetups.length}
        momCount={momentumConfirmed.length}
        breakoutCount={breakoutStocks.length}
        gapCount={gapStocks.length}
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
