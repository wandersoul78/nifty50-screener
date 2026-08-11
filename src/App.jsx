import React, { useState, useEffect } from 'react';
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

  const openLowStocks = filteredStocks.filter(s => s.setup_type === 'OPEN_LOW');
  const openHighStocks = filteredStocks.filter(s => s.setup_type === 'OPEN_HIGH');
  const momentumStocks = filteredStocks.filter(s => s.momentum_confirmed);

  const displayedStocks = activeTab === 'BULLISH'  ? openLowStocks
                        : activeTab === 'BEARISH'  ? openHighStocks
                        : activeTab === 'MOMENTUM' ? momentumStocks
                        : filteredStocks;

  const handleExportCSV = () => {
    if (!filteredStocks.length) return;
    
    const headers = ["Ticker", "Setup", "LTP", "ChangePct", "VolSurge", "Open", "Low", "High", "Stoploss", "Target1", "ExactMatch"];
    const csvRows = [
      headers.join(","),
      ...filteredStocks.map(s => [
        s.ticker,
        s.setup_type,
        s.ltp,
        s.change_pct,
        s.vol_surge,
        s.open,
        s.low,
        s.high,
        s.stoploss,
        s.target_1,
        s.exact_match
      ].join(","))
    ];

    const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `yahoo_stocks_screener_${Date.now()}.csv`;
    a.click();
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

      {/* Hero KPI Stats Grid */}
      <div className="grid grid-4" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(5, 1fr)' }}>
        <div className="glass-card kpi-card">
          <div className="kpi-title">Nifty F&O Stocks Scanned</div>
          <div className="kpi-value mono" style={{ color: 'var(--accent-cyan)' }}>
            {screenerData?.total_scanned || 215}
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

        <div className="glass-card kpi-card" style={{ borderLeft: '4px solid #f59e0b', background: 'rgba(245, 158, 11, 0.06)' }}>
          <div className="kpi-title" style={{ color: '#f59e0b' }}>🔥 Momentum Confirmed</div>
          <div className="kpi-value mono" style={{ color: '#f59e0b' }}>
            {momentumStocks.length}
          </div>
          <div className="kpi-subtitle" style={{ color: '#f59e0b' }}>5-min close crosses Prev Day extreme</div>
        </div>
      </div>

      {/* Top Priority High-Probability Cards */}
      {filteredStocks.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={20} color="var(--accent-amber)" /> Top High-Volume Priority Candidates
            </h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Sorted by Volume Surge & Setup Strength
            </span>
          </div>
          
          <div className="grid grid-3">
            {filteredStocks.slice(0, 6).map(stock => (
              <StockCard 
                key={stock.ticker} 
                stock={stock} 
                onClick={() => setSelectedStock(stock)} 
              />
            ))}
          </div>
        </div>
      )}

      {/* Full Tabbed Filter Table */}
      <StockTable 
        stocks={displayedStocks}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        allCount={filteredStocks.length}
        bullishCount={openLowStocks.length}
        bearishCount={openHighStocks.length}
        momentumCount={momentumStocks.length}
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
