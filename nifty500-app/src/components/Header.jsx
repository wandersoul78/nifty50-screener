import React from 'react';
import { RefreshCw, Download, Zap, Activity, BarChart2 } from 'lucide-react';

export default function Header({ scanTime, onRefresh, isRefreshing, onExportCSV,
                                  tolerance, setTolerance }) {
  return (
    <header className="glass-card" style={{ padding: '20px 24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>

        {/* Branding */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #818cf8, #a78bfa)',
              padding: '10px', borderRadius: '12px', color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Activity size={24} strokeWidth={2.5} />
            </div>
            <div>
              <h1 style={{
                fontSize: '1.4rem', fontWeight: '800', letterSpacing: '-0.02em',
                background: 'linear-gradient(to right, #818cf8, #e0e7ff)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
              }}>
                Nifty 500 MA Bull Stack Screener
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '2px' }}>
                Weekly ST(10,3) + MA Bull Stack (Price &gt; 50 SMA &gt; 100 SMA &gt; 200 SMA) + Intraday Setups
              </p>
            </div>
          </div>
        </div>

        {/* Live status + scan time */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(15,23,42,0.6)', padding: '8px 16px', borderRadius: '30px', border: '1px solid var(--border-color)' }}>
          <div className="live-dot" />
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Last Scan: <span className="mono" style={{ color: 'var(--text-main)', fontWeight: '600' }}>{scanTime || 'Scanning…'}</span>
          </div>
          <span style={{ opacity: 0.3 }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--accent)', fontWeight: '600' }}>
            <BarChart2 size={14} /> MA Bull Stack Engine
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={onRefresh} disabled={isRefreshing}>
            <RefreshCw size={16} className={isRefreshing ? 'spin-icon' : ''} />
            {isRefreshing ? 'Scanning…' : 'Re-scan'}
          </button>
          <button className="btn btn-primary" onClick={onExportCSV}>
            <Download size={16} /> Export CSV
          </button>
        </div>
      </div>

      {/* Controls toolbar */}
      <div style={{
        marginTop: '20px', paddingTop: '16px',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <span className="badge badge-st">Filter Stack:</span>
          <span>Price &gt; 50 SMA &gt; 100 SMA &gt; 200 SMA</span>
          <span style={{ opacity: 0.4 }}>|</span>
          <span>Weekly Supertrend(10,3) == BULLISH</span>
        </div>

        {/* Intraday Open Buffer Tolerance */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <Zap size={15} color="var(--momentum)" />
          <span>Open Buffer:</span>
          <span className="mono" style={{ color: 'var(--momentum)', fontWeight: '700' }}>{tolerance.toFixed(2)}%</span>
          <input type="range" min="0" max="0.50" step="0.05" value={tolerance}
            onChange={e => setTolerance(parseFloat(e.target.value))}
            style={{ width: '100px', accentColor: 'var(--momentum)', cursor: 'pointer' }} />
        </div>
      </div>
    </header>
  );
}
