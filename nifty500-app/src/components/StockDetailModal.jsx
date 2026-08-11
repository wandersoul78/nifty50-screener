import React from 'react';
import { X, ArrowUpRight, ArrowDownRight, Zap, Target, Shield, LogIn, TrendingUp, TrendingDown, Activity, CheckCircle } from 'lucide-react';

export default function StockDetailModal({ stock, onClose, maPeriod, maType }) {
  if (!stock) return null;

  const isBullish     = stock.setup_type === 'OPEN_LOW';
  const isMomentum    = stock.momentum_confirmed === true;
  const price         = stock.current_price || stock.ltp;
  const entryPrice    = stock.entry_price || price;
  const stoplossPrice = stock.stoploss;
  const pnlPct        = stock.pnl_pct;
  const monthlySt     = stock.monthly_supertrend;
  const weeklySt      = stock.weekly_supertrend;
  const maValue       = stock.ma_value;
  const maDist        = stock.ma_distance_pct;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(7, 9, 15, 0.85)', backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: '20px'
    }} onClick={onClose}>
      
      <div className="glass-card" style={{
        width: '100%', maxWidth: '720px', padding: '28px', position: 'relative',
        border: isMomentum ? '1px solid rgba(245,158,11,0.5)' : '1px solid rgba(129,140,248,0.4)',
        boxShadow: isMomentum ? '0 0 40px rgba(245,158,11,0.18)' : '0 0 40px rgba(129,140,248,0.15)'
      }} onClick={e => e.stopPropagation()}>
        
        {/* Close Button */}
        <button onClick={onClose} style={{
          position: 'absolute', top: '20px', right: '20px',
          background: 'rgba(255, 255, 255, 0.08)', border: 'none', color: 'var(--text-muted)',
          width: '32px', height: '32px', borderRadius: '50%', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: '800' }}>{stock.ticker}</h2>
            <span className="badge badge-st">
              <Activity size={13} /> SUPERTREND BULLISH
            </span>
            {stock.setup_type && (
              <span className={isBullish ? "badge badge-bullish" : "badge badge-bearish"}>
                {isBullish ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                {isBullish ? "OPEN = LOW" : "OPEN = HIGH"}
              </span>
            )}
            {isMomentum && (
              <span className="badge badge-momentum">
                🔥 MOMENTUM CONFIRMED
              </span>
            )}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Nifty 500 Multi-Timeframe Supertrend + {maType}({maPeriod}) Matrix
          </p>
        </div>

        {/* Supertrend & MA Alignment Status Box */}
        <div style={{
          background: 'rgba(129, 140, 248, 0.08)', border: '1px solid rgba(129, 140, 248, 0.25)',
          borderRadius: '12px', padding: '16px', marginBottom: '20px'
        }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--accent)', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle size={15} /> MULTI-TIMEFRAME CONFLUENCE CONFIRMED
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '10px 12px', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>MONTHLY ST (10,3)</span>
              <span className="mono" style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--bullish)' }}>₹{monthlySt}</span>
              <span style={{ fontSize: '0.65rem', color: 'var(--bullish)', display: 'block', marginTop: '2px' }}>▲ Price Above</span>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '10px 12px', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>WEEKLY ST (10,3)</span>
              <span className="mono" style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--bullish)' }}>₹{weeklySt}</span>
              <span style={{ fontSize: '0.65rem', color: 'var(--bullish)', display: 'block', marginTop: '2px' }}>▲ Price Above</span>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '10px 12px', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>{maType}({maPeriod}) FILTER</span>
              <span className="mono" style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--accent2)' }}>₹{maValue}</span>
              <span style={{ fontSize: '0.65rem', color: 'var(--accent)', display: 'block', marginTop: '2px' }}>+{maDist}% Distance</span>
            </div>
          </div>
        </div>

        {/* Intraday Trade Setup Grid if available */}
        {stock.setup_type ? (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '700', marginBottom: '10px' }}>
              ⚡ INTRADAY {stock.setup_type} TRADE MATRIX
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
              <div style={{ background: 'rgba(56, 189, 248, 0.08)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--accent-cyan)', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <LogIn size={12} /> ENTRY
                </span>
                <span className="mono" style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--accent-cyan)', display: 'block', marginTop: '4px' }}>
                  ₹{entryPrice}
                </span>
              </div>

              <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(244, 63, 94, 0.25)' }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--bearish)', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <Shield size={12} /> STOPLOSS
                </span>
                <span className="mono" style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--bearish)', display: 'block', marginTop: '4px' }}>
                  ₹{stoplossPrice}
                </span>
              </div>

              <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--bullish)', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <Target size={12} /> TARGET 1
                </span>
                <span className="mono" style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--bullish)', display: 'block', marginTop: '4px' }}>
                  ₹{stock.target_1}
                </span>
              </div>

              <div style={{ background: 'rgba(99, 102, 241, 0.08)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--accent)', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '3px' }}>
                  <Target size={12} /> TARGET 2
                </span>
                <span className="mono" style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--accent)', display: 'block', marginTop: '4px' }}>
                  ₹{stock.target_2}
                </span>
              </div>
            </div>
          </div>
        ) : null}

        {/* Live Performance */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
          padding: '14px 18px', borderRadius: '10px', display: 'flex',
          justifyContent: 'space-between', alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CURRENT PRICE:</span>
            <span className="mono" style={{ fontSize: '1.3rem', fontWeight: '800', display: 'block', marginTop: '2px', color: 'var(--accent-cyan)' }}>
              ₹{price}
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DAY CHANGE:</span>
            <span className="mono" style={{
              fontSize: '1.3rem', fontWeight: '800',
              color: stock.change_pct >= 0 ? 'var(--bullish)' : 'var(--bearish)',
              display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px', marginTop: '2px'
            }}>
              {stock.change_pct >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              {stock.change_pct >= 0 ? `+${stock.change_pct}%` : `${stock.change_pct}%`}
            </span>
          </div>
        </div>

      </div>
    </div>
  );
}
