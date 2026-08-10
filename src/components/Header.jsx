import React from 'react';
import { TrendingUp, RefreshCw, Download, Sliders, Zap, Clock } from 'lucide-react';

export default function Header({ 
  scanTime, 
  onRefresh, 
  isRefreshing, 
  onExportCSV, 
  tolerance, 
  setTolerance, 
  strictOnly, 
  setStrictOnly
}) {
  return (
    <header className="glass-card" style={{ padding: '20px 24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Left: Branding & Market Clock */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <div style={{
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--bullish))',
              padding: '10px',
              borderRadius: '12px',
              color: '#090d16',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <TrendingUp size={24} strokeWidth={2.5} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.4rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Yahoo Finance Nifty F&O Open = Low / High Screener
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.825rem', marginTop: '2px' }}>
                Intraday Momentum Setups (5-Min Post-Open Entry Trigger)
              </p>
            </div>
          </div>
        </div>

        {/* Center: Live Scan Time & Market Clock */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(15, 23, 42, 0.6)', padding: '8px 16px', borderRadius: '30px', border: '1px solid var(--border-color)' }}>
          <div className="live-dot" />
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Last Scan: <span className="mono" style={{ color: 'var(--text-main)', fontWeight: '600' }}>{scanTime || 'Scanning...'}</span>
          </div>
          <span style={{ opacity: 0.3 }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: '600' }}>
            <Clock size={14} /> 5-Min Opening Candle Engine
          </div>
        </div>

        {/* Right: Actions & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          
          <button 
            className="btn btn-secondary" 
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw size={16} className={isRefreshing ? 'spin-icon' : ''} />
            {isRefreshing ? 'Scanning...' : 'Rescan Market'}
          </button>

          <button 
            className="btn btn-primary" 
            onClick={onExportCSV}
          >
            <Download size={16} /> Export CSV
          </button>

        </div>
      </div>

      {/* Tolerance & Filter Control Toolbar */}
      <div style={{ 
        marginTop: '20px', 
        paddingTop: '16px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <Sliders size={16} color="var(--accent-cyan)" />
            <span>Open Buffer Tolerance:</span>
            <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: '700' }}>{tolerance.toFixed(2)}%</span>
          </div>
          
          <input 
            type="range" 
            min="0.00" 
            max="0.50" 
            step="0.05"
            value={tolerance}
            onChange={(e) => setTolerance(parseFloat(e.target.value))}
            style={{ width: '130px', accentColor: 'var(--accent-cyan)', cursor: 'pointer' }}
          />

          <div style={{ display: 'flex', gap: '6px' }}>
            {[0.00, 0.05, 0.10, 0.20, 0.30].map(val => (
              <button 
                key={val} 
                onClick={() => setTolerance(val)}
                style={{
                  background: tolerance === val ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.05)',
                  color: tolerance === val ? '#090d16' : 'var(--text-muted)',
                  border: '1px solid var(--border-color)',
                  padding: '3px 8px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                {val === 0 ? 'Exact (0%)' : `${val}%`}
              </button>
            ))}
          </div>
        </div>

        {/* Strict Match Toggle */}
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem', color: 'var(--text-main)', userSelect: 'none' }}>
          <input 
            type="checkbox" 
            checked={strictOnly}
            onChange={(e) => setStrictOnly(e.target.checked)}
            style={{ accentColor: 'var(--accent-amber)', width: '16px', height: '16px', cursor: 'pointer' }}
          />
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Zap size={14} color="var(--accent-amber)" /> Exact Match Only (Diff &lt; 0.02%)
          </span>
        </label>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </header>
  );
}
