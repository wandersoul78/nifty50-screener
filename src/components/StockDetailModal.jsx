import React from 'react';
import { X, ArrowUpRight, ArrowDownRight, Zap, Target, Shield, LogIn, TrendingUp, TrendingDown } from 'lucide-react';

export default function StockDetailModal({ stock, onClose }) {
  if (!stock) return null;

  const isBullish = stock.setup_type === 'OPEN_LOW';
  const openPrice = stock.open;
  const highPrice = stock.high;
  const lowPrice = stock.low;
  const entryPrice = stock.entry_price || stock.ltp;
  const ltpPrice = stock.ltp;
  const stoplossPrice = stock.stoploss;
  const riskAmount = stock.risk_per_share || Math.abs(entryPrice - stoplossPrice).toFixed(2);
  const pnlPct = stock.pnl_pct !== undefined ? stock.pnl_pct : (isBullish ? ((ltpPrice - entryPrice)/entryPrice*100) : ((entryPrice - ltpPrice)/entryPrice*100));

  const totalRange = max(highPrice - lowPrice, 0.01);
  const bodyTop = Math.max(openPrice, entryPrice);
  const bodyBottom = Math.min(openPrice, entryPrice);
  
  const upperWickPct = ((highPrice - bodyTop) / totalRange) * 100;
  const bodyPct = ((bodyTop - bodyBottom) / totalRange) * 100;
  const lowerWickPct = ((bodyBottom - lowPrice) / totalRange) * 100;

  function max(a, b) { return a > b ? a : b; }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }} onClick={onClose}>
      
      <div 
        className="glass-card" 
        style={{
          width: '100%',
          maxWidth: '720px',
          padding: '28px',
          position: 'relative',
          border: isBullish ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(244, 63, 94, 0.4)',
          boxShadow: isBullish ? '0 0 40px rgba(16, 185, 129, 0.15)' : '0 0 40px rgba(244, 63, 94, 0.15)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'rgba(255, 255, 255, 0.08)',
            border: 'none',
            color: 'var(--text-muted)',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: '800' }}>{stock.ticker}</h2>
            <span className={isBullish ? "badge badge-bullish" : "badge badge-bearish"}>
              {isBullish ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              {isBullish ? "OPEN = LOW BUY SETUPS" : "OPEN = HIGH SELL SETUPS"}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            9:30 AM Trade Matrix (Fixed Entry Price + Current Live PnL)
          </p>
        </div>

        {/* Candle Anatomy Bar Visualization */}
        <div style={{ 
          background: 'rgba(15, 23, 42, 0.8)', 
          padding: '16px', 
          borderRadius: '12px', 
          marginBottom: '20px',
          border: '1px solid var(--border-color)' 
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <span>09:15 AM Opening Candle Structure</span>
            <span style={{ color: isBullish ? 'var(--bullish)' : 'var(--bearish)', fontWeight: '700' }}>
              {isBullish ? `Lower Shadow: ${stock.diff_from_open_pct}% (Zero Lower Wick)` : `Upper Shadow: ${stock.diff_from_open_pct}% (Zero Upper Wick)`}
            </span>
          </div>

          <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', background: '#090d16' }}>
            <div style={{ width: `${upperWickPct}%`, background: 'rgba(255, 255, 255, 0.2)' }} title="Upper Wick" />
            <div style={{ width: `${bodyPct}%`, background: isBullish ? 'var(--bullish)' : 'var(--bearish)' }} title="Real Body" />
            <div style={{ width: `${lowerWickPct}%`, background: 'rgba(255, 255, 255, 0.2)' }} title="Lower Wick" />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '8px' }}>
            <span>Low: ₹{lowPrice}</span>
            <span>Open: ₹{openPrice}</span>
            <span>9:30 AM Entry: ₹{entryPrice}</span>
            <span>High: ₹{highPrice}</span>
          </div>
        </div>

        {/* Trade Entry, Stoploss & Targets 3-Card Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
          
          {/* Entry Price Card */}
          <div style={{ background: 'rgba(56, 189, 248, 0.08)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '700' }}>
              <LogIn size={14} color="var(--accent-cyan)" /> 9:30 AM ENTRY PRICE
            </span>
            <span className="mono" style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--accent-cyan)', display: 'block', marginTop: '4px' }}>
              ₹{entryPrice}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block', marginTop: '2px' }}>
              Close of 9:15-9:30 Candle
            </span>
          </div>

          {/* Stoploss Card */}
          <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(244, 63, 94, 0.25)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--bearish)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '700' }}>
              <Shield size={14} color="var(--bearish)" /> STOPLOSS (SL)
            </span>
            <span className="mono" style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--bearish)', display: 'block', marginTop: '4px' }}>
              ₹{stoplossPrice}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block', marginTop: '2px' }}>
              Risk: ₹{riskAmount} / share
            </span>
          </div>

          {/* Target Card */}
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--bullish)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '700' }}>
              <Target size={14} color="var(--bullish)" /> TARGET 1 (1:1.5)
            </span>
            <span className="mono" style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--bullish)', display: 'block', marginTop: '4px' }}>
              ₹{stock.target_1}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block', marginTop: '2px' }}>
              Target 2: ₹{stock.target_2}
            </span>
          </div>

        </div>

        {/* Live Performance & PnL Bar */}
        <div style={{ 
          background: pnlPct >= 0 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)', 
          border: pnlPct >= 0 ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
          padding: '14px 18px', 
          borderRadius: '10px', 
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <div>
            <span style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>CURRENT LIVE MARKET PRICE (LTP):</span>
            <span className="mono" style={{ fontSize: '1.3rem', fontWeight: '800', display: 'block', marginTop: '2px' }}>
              ₹{ltpPrice}
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>INTRADAY TRADE PNL:</span>
            <span className="mono" style={{ 
              fontSize: '1.35rem', 
              fontWeight: '800', 
              color: pnlPct >= 0 ? 'var(--bullish)' : 'var(--bearish)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: '4px',
              marginTop: '2px'
            }}>
              {pnlPct >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
              {pnlPct >= 0 ? `+${pnlPct.toFixed(2)}%` : `${pnlPct.toFixed(2)}%`}
            </span>
          </div>
        </div>

      </div>
    </div>
  );
}
