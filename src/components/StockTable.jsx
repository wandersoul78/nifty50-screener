import React, { useState } from 'react';
import { Search, ArrowUpDown, ArrowUpRight, ArrowDownRight, Zap, Target, Shield, TrendingUp, TrendingDown } from 'lucide-react';

export default function StockTable({ stocks, onSelectStock }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('change_pct');
  const [sortAsc, setSortAsc] = useState(false);
  const [activeFilter, setActiveFilter] = useState('ALL');

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const filteredStocks = stocks.filter(stock => {
    const matchesSearch = stock.ticker.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;

    if (activeFilter === 'OPEN_LOW')  return stock.setup_type === 'OPEN_LOW';
    if (activeFilter === 'OPEN_HIGH') return stock.setup_type === 'OPEN_HIGH';
    if (activeFilter === 'VOL_SURGE') return stock.vol_surge >= 1.5;
    if (activeFilter === 'MOMENTUM')  return stock.momentum_confirmed === true;
    return true;
  });

  const sortedStocks = [...filteredStocks].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (typeof aVal === 'string') {
      return sortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return sortAsc ? aVal - bVal : bVal - aVal;
  });

  return (
    <div className="glass-card" style={{ padding: '20px' }}>
      
      {/* Table Header Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        
        {/* Search Input */}
        <div style={{ position: 'relative', width: '260px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input 
            type="text" 
            placeholder="Search F&O ticker..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 12px 9px 36px',
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { id: 'ALL',       label: `All Setups (${stocks.length})` },
            { id: 'OPEN_LOW',  label: `🟢 Open = Low (${stocks.filter(s => s.setup_type === 'OPEN_LOW').length})` },
            { id: 'OPEN_HIGH', label: `🔴 Open = High (${stocks.filter(s => s.setup_type === 'OPEN_HIGH').length})` },
            { id: 'VOL_SURGE', label: `⚡ Vol Surge >1.5x (${stocks.filter(s => s.vol_surge >= 1.5).length})` },
            { id: 'MOMENTUM',  label: `🔥 Momentum (${stocks.filter(s => s.momentum_confirmed).length})` }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              style={{
                padding: '7px 14px',
                borderRadius: '20px',
                fontSize: '0.8rem',
                fontWeight: '600',
                cursor: 'pointer',
                border: tab.id === 'MOMENTUM'
                  ? '1px solid #f59e0b'
                  : '1px solid var(--border-color)',
                background: activeFilter === tab.id
                  ? (tab.id === 'MOMENTUM' ? '#f59e0b' : 'var(--accent-indigo)')
                  : (tab.id === 'MOMENTUM' ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.04)'),
                color: activeFilter === tab.id ? '#fff'
                  : (tab.id === 'MOMENTUM' ? '#f59e0b' : 'var(--text-muted)'),
                transition: 'all 0.2s ease'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

      </div>

      {/* Main Data Table */}
      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('ticker')} style={{ cursor: 'pointer' }}>
                Stock Symbol <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('setup_type')} style={{ cursor: 'pointer' }}>
                Setup Signal <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('open')} style={{ cursor: 'pointer' }}>
                Day Open <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('entry_price')} style={{ cursor: 'pointer', color: 'var(--accent-cyan)' }}>
                5-Min Entry (Session +5m) <ArrowUpDown size={12} />
              </th>
              {activeFilter === 'MOMENTUM' && (
                <>
                  <th onClick={() => handleSort('prev_day_high')} style={{ cursor: 'pointer', color: '#f59e0b' }}>
                    Prev Day High <ArrowUpDown size={12} />
                  </th>
                  <th onClick={() => handleSort('prev_day_low')} style={{ cursor: 'pointer', color: '#f59e0b' }}>
                    Prev Day Low <ArrowUpDown size={12} />
                  </th>
                </>
              )}
              <th onClick={() => handleSort('ltp')} style={{ cursor: 'pointer' }}>
                Current LTP (₹) <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('change_pct')} style={{ cursor: 'pointer', color: sortField === 'change_pct' ? 'var(--accent-cyan)' : undefined }}>
                Day Chg% <ArrowUpDown size={12} style={{ opacity: sortField === 'change_pct' ? 1 : 0.4 }} />
              </th>
              <th onClick={() => handleSort('pnl_pct')} style={{ cursor: 'pointer' }}>
                Trade PnL % <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('stoploss')} style={{ cursor: 'pointer', color: 'var(--bearish)' }}>
                Stoploss (₹) <ArrowUpDown size={12} />
              </th>
              <th onClick={() => handleSort('target_1')} style={{ cursor: 'pointer', color: 'var(--bullish)' }}>
                Target 1 (₹) <ArrowUpDown size={12} />
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedStocks.length === 0 ? (
              <tr>
                <td colSpan={activeFilter === 'MOMENTUM' ? 11 : 9} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  {activeFilter === 'MOMENTUM'
                    ? 'No momentum-confirmed stocks yet. Momentum requires 5-min close to cross the previous day\'s High/Low.'
                    : 'No matching Open=Low or Open=High stocks found. Try adjusting tolerance or filters.'}
                </td>
              </tr>
            ) : (
              sortedStocks.map((stock) => {
                const isBullish  = stock.breakout_type ? stock.breakout_type === 'BULLISH' : stock.setup_type === 'OPEN_LOW';
                const entryPrice = stock.entry_price || stock.ltp;
                const ltpPrice   = stock.ltp;
                const pnlPct     = stock.pnl_pct !== undefined ? stock.pnl_pct : (isBullish ? ((ltpPrice - entryPrice)/entryPrice*100) : ((entryPrice - ltpPrice)/entryPrice*100));
                const isMomentum = stock.momentum_confirmed || stock.breakout_type;

                return (
                  <tr
                    key={stock.ticker}
                    onClick={() => onSelectStock(stock)}
                    style={{
                      cursor: 'pointer',
                      background: isMomentum ? 'rgba(245,158,11,0.04)' : undefined
                    }}
                  >
                    <td style={{ fontWeight: '700' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span>{stock.ticker}</span>
                        {isMomentum && (
                          <span style={{
                            fontSize: '0.62rem', padding: '2px 6px', borderRadius: '4px',
                            background: stock.breakout_type ? 'rgba(167,139,250,0.18)' : 'rgba(245,158,11,0.18)',
                            color: stock.breakout_type ? '#a78bfa' : '#f59e0b',
                            fontWeight: '700', letterSpacing: '0.04em'
                          }}>
                            {stock.breakout_type ? '🚀 5M BREAK' : '🔥 MOM'}
                          </span>
                        )}
                        {stock.exact_match && (
                          <span className="badge badge-exact" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>
                            EXACT
                          </span>
                        )}
                      </div>
                    </td>

                    <td>
                      <span className={isBullish ? "badge badge-bullish" : "badge badge-bearish"}>
                        {isBullish ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                        {stock.breakout_type ? (isBullish ? "BREAKOUT (>HIGH)" : "BREAKDOWN (<LOW)") : (isBullish ? "OPEN = LOW" : "OPEN = HIGH")}
                      </span>
                    </td>

                    <td className="mono" style={{ color: 'var(--text-muted)' }}>
                      ₹{stock.open}
                    </td>

                    <td className="mono" style={{ fontWeight: '800', color: 'var(--accent-cyan)' }}>
                      ₹{entryPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>

                    {activeFilter === 'MOMENTUM' && (
                      <>
                        <td className="mono" style={{ fontWeight: '700', color: isBullish ? 'var(--bullish)' : 'var(--bearish)' }}>
                          ₹{(stock.prev_day_high || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="mono" style={{ fontWeight: '700', color: isBullish ? 'var(--bearish)' : 'var(--bullish)' }}>
                          ₹{(stock.prev_day_low || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                      </>
                    )}

                    <td className="mono" style={{ fontWeight: '700' }}>
                      ₹{ltpPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>

                    <td>
                      <span className="mono" style={{
                        fontWeight: '700',
                        color: (stock.change_pct ?? 0) >= 0 ? 'var(--bullish)' : 'var(--bearish)',
                      }}>
                        {(stock.change_pct ?? 0) >= 0 ? '+' : ''}{(stock.change_pct ?? 0).toFixed(2)}%
                      </span>
                    </td>

                    <td>
                      <span className="mono" style={{
                        fontWeight: '800',
                        color: pnlPct >= 0 ? 'var(--bullish)' : 'var(--bearish)',
                        background: pnlPct >= 0 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '3px'
                      }}>
                        {pnlPct >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                        {pnlPct >= 0 ? `+${pnlPct.toFixed(2)}%` : `${pnlPct.toFixed(2)}%`}
                      </span>
                    </td>

                    <td className="mono" style={{ color: 'var(--bearish)', fontWeight: '700' }}>
                      ₹{stock.stoploss}
                    </td>

                    <td className="mono" style={{ color: 'var(--bullish)', fontWeight: '700' }}>
                      ₹{stock.target_1}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
