import React, { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, Download, SlidersHorizontal, Zap, Activity, BarChart2, Clock } from 'lucide-react';

export default function Header({ scanTime, onRefresh, isRefreshing, onExportCSV,
                                  maPeriod, setMaPeriod, maType, setMaType, tolerance, setTolerance }) {
  const [localPeriod, setLocalPeriod] = useState(maPeriod);

  const applyPeriod = () => { if (localPeriod >= 5 && localPeriod <= 500) setMaPeriod(localPeriod); };

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
                Nifty 500 Supertrend Screener
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '2px' }}>
                Monthly ST(10,3) + Weekly ST(10,3) + SMA Filter + Intraday Setup Detection
              </p>
            </div>
          </div>
        </div>

        {/* Live dot + scan time */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(15,23,42,0.6)', padding: '8px 16px', borderRadius: '30px', border: '1px solid var(--border-color)' }}>
          <div className="live-dot" />
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Last Scan: <span className="mono" style={{ color: 'var(--text-main)', fontWeight: '600' }}>{scanTime || 'Not scanned yet'}</span>
          </div>
          <span style={{ opacity: 0.3 }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--accent)', fontWeight: '600' }}>
            <BarChart2 size={14} /> Supertrend Engine
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
        display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap'
      }}>
        {/* MA Period */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <SlidersHorizontal size={16} color="var(--accent)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>MA Period:</span>
          <input
            type="number" min={5} max={500} value={localPeriod}
            onChange={e => setLocalPeriod(Number(e.target.value))}
            onBlur={applyPeriod}
            onKeyDown={e => e.key === 'Enter' && applyPeriod()}
            style={{
              width: '72px', background: 'rgba(129,140,248,0.1)',
              border: '1px solid rgba(129,140,248,0.3)', borderRadius: '8px',
              padding: '5px 10px', color: 'var(--accent)', fontFamily: 'var(--font-mono)',
              fontWeight: '700', fontSize: '0.9rem', textAlign: 'center'
            }}
          />
          <div style={{ display: 'flex', gap: '5px' }}>
            {[20, 50, 100, 200].map(v => (
              <button key={v} onClick={() => { setLocalPeriod(v); setMaPeriod(v); }}
                style={{
                  background: maPeriod === v ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                  color: maPeriod === v ? '#090d16' : 'var(--text-muted)',
                  border: '1px solid var(--border-color)',
                  padding: '3px 8px', borderRadius: '6px', fontSize: '0.75rem',
                  fontWeight: '600', cursor: 'pointer'
                }}>{v}</button>
            ))}
          </div>
        </div>

        {/* MA Type */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Type:</span>
          {['SMA', 'EMA'].map(t => (
            <button key={t} onClick={() => setMaType(t)}
              style={{
                background: maType === t ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                color: maType === t ? '#090d16' : 'var(--text-muted)',
                border: '1px solid var(--border-color)',
                padding: '4px 12px', borderRadius: '6px', fontSize: '0.8rem',
                fontWeight: '700', cursor: 'pointer'
              }}>{t}</button>
          ))}
        </div>

        {/* Tolerance */}
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
