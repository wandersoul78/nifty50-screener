import React from 'react';
import { ArrowUpRight, ArrowDownRight, Zap, Target, Shield, LogIn, TrendingUp, TrendingDown } from 'lucide-react';

export default function StockCard({ stock, onClick }) {
  const isBullish  = stock.setup_type === 'OPEN_LOW';
  const isMomentum = stock.momentum_confirmed === true;
  const entryPrice = stock.entry_price || stock.ltp;
  const ltpPrice   = stock.ltp;
  const pnlPct     = stock.pnl_pct !== undefined ? stock.pnl_pct : (isBullish ? ((ltpPrice - entryPrice)/entryPrice*100) : ((entryPrice - ltpPrice)/entryPrice*100));

  return (
    <div 
      className="glass-card" 
      onClick={onClick}
      style={{
        padding: '18px',
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
        borderLeft: isMomentum
          ? '4px solid #f59e0b'
          : isBullish ? '4px solid var(--bullish)' : '4px solid var(--bearish)',
        boxShadow: isMomentum ? '0 0 18px rgba(245,158,11,0.12)' : undefined,
        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
      }}
    >
      {/* Momentum Corner Badge — clean pill, no ribbon clipping */}
      {isMomentum && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
          color: '#000',
          fontSize: '0.58rem',
          fontWeight: '800',
          padding: '3px 8px',
          borderRadius: '20px',
          letterSpacing: '0.06em',
          zIndex: 2,
          boxShadow: '0 2px 8px rgba(245,158,11,0.45)',
          display: 'flex',
          alignItems: 'center',
          gap: '3px'
        }}>
          🔥 MOMENTUM
        </div>
      )}
      {/* Top Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: '800', letterSpacing: '-0.01em' }}>
              {stock.ticker}
            </h3>
            {isMomentum && (
              <span style={{
                fontSize: '0.62rem', padding: '2px 6px', borderRadius: '4px',
                background: 'rgba(245,158,11,0.18)', color: '#f59e0b',
                fontWeight: '700', letterSpacing: '0.04em'
              }}>
                🔥 MOMENTUM
              </span>
            )}
            {stock.exact_match && (
              <span className="badge badge-exact" title="Exact Open=Low / Open=High Match">
                <Zap size={11} /> EXACT
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Diff from Open: <span className="mono" style={{ color: 'var(--text-main)' }}>{stock.diff_from_open_pct}%</span>
          </div>
        </div>

        <span className={isBullish ? "badge badge-bullish" : "badge badge-bearish"}>
          {isBullish ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {isBullish ? "OPEN = LOW" : "OPEN = HIGH"}
        </span>
      </div>

      {/* 5-Min Entry Price vs LTP Highlight */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        background: 'rgba(56, 189, 248, 0.08)',
        border: '1px solid rgba(56, 189, 248, 0.2)',
        padding: '10px 12px',
        borderRadius: '8px',
        marginBottom: '12px'
      }}>
        <div>
          <span style={{ fontSize: '0.675rem', color: 'var(--accent-cyan)', fontWeight: '700', display: 'block' }}>5-MIN ENTRY (Session Open +5m):</span>
          <span className="mono" style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--accent-cyan)' }}>
            ₹{entryPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.675rem', color: 'var(--text-muted)', display: 'block' }}>CURRENT LTP:</span>
          <span className="mono" style={{ fontSize: '1.05rem', fontWeight: '700' }}>
            ₹{ltpPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>

        {/* PnL Badge */}
        <div style={{
          background: pnlPct >= 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
          color: pnlPct >= 0 ? 'var(--bullish)' : 'var(--bearish)',
          border: pnlPct >= 0 ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
          padding: '4px 8px',
          borderRadius: '6px',
          fontSize: '0.8rem',
          fontWeight: '800',
          display: 'flex',
          alignItems: 'center',
          gap: '3px'
        }}>
          {pnlPct >= 0 ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {pnlPct >= 0 ? `+${pnlPct.toFixed(2)}%` : `${pnlPct.toFixed(2)}%`}
        </div>
      </div>

      {/* Metric Badges Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '8px', 
        padding: '10px', 
        background: 'rgba(15, 23, 42, 0.6)', 
        borderRadius: '10px',
        fontSize: '0.775rem'
      }}>
        <div>
          <span style={{ color: 'var(--text-muted)' }}>{isBullish ? 'Open / Low:' : 'Open / High:'}</span>
          <span className="mono" style={{ display: 'block', fontWeight: '700', marginTop: '1px' }}>
            ₹{stock.open}
          </span>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)' }}>Risk / Share:</span>
          <span className="mono" style={{ display: 'block', fontWeight: '700', marginTop: '1px', color: 'var(--accent-amber)' }}>
            ₹{stock.risk_per_share || Math.abs(entryPrice - stock.stoploss).toFixed(2)}
          </span>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <Shield size={12} color="var(--bearish)" /> Stoploss:
          </span>
          <span className="mono" style={{ display: 'block', fontWeight: '700', color: 'var(--bearish)', marginTop: '1px' }}>
            ₹{stock.stoploss}
          </span>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <Target size={12} color="var(--bullish)" /> Target 1:
          </span>
          <span className="mono" style={{ display: 'block', fontWeight: '700', color: 'var(--bullish)', marginTop: '1px' }}>
            ₹{stock.target_1}
          </span>
        </div>
      </div>
    </div>
  );
}
