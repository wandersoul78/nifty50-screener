import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUpRight, ArrowDownRight, Search, TrendingUp, TrendingDown } from 'lucide-react';

const fmt = (v, decimals = 2) => v != null ? `₹${Number(v).toLocaleString('en-IN', { minimumFractionDigits: decimals })}` : '—';
const fmtPct = v => v != null ? `${Number(v) >= 0 ? '+' : ''}${Number(v).toFixed(2)}%` : '—';

export default function StockTable({ stocks, activeTab, setActiveTab,
                                     allCount, setupCount, momCount, breakoutCount,
                                     onSelectStock }) {
  const [search, setSearch]   = useState('');
  const [sortField, setSort]  = useState('change_pct');
  const [sortAsc, setSortAsc] = useState(false);

  const handleSort = field => {
    if (sortField === field) setSortAsc(a => !a);
    else { setSort(field); setSortAsc(false); }
  };

  const filtered = useMemo(() => {
    let s = stocks;
    if (search) s = s.filter(x => x.ticker.toLowerCase().includes(search.toLowerCase()));
    s = [...s].sort((a, b) => {
      const va = a[sortField] ?? (typeof a[sortField] === 'string' ? '' : -Infinity);
      const vb = b[sortField] ?? (typeof b[sortField] === 'string' ? '' : -Infinity);
      if (typeof va === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      return sortAsc ? va - vb : vb - va;
    });
    return s;
  }, [stocks, search, sortField, sortAsc]);

  const SortTh = ({ field, children }) => (
    <th onClick={() => handleSort(field)} title={`Sort by ${field}`}>
      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        {children}
        <ArrowUpDown size={12} style={{ opacity: sortField === field ? 1 : 0.3 }} />
      </span>
    </th>
  );

  const showIntraday = activeTab === 'SETUP' || activeTab === 'MOMENTUM' || activeTab === 'BREAKOUT';

  return (
    <div className="glass-card" style={{ padding: '20px' }}>
      {/* Tab nav + search */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div className="tab-nav">
          <button className={`tab-pill ${activeTab === 'ALL' ? 'active-all' : ''}`}
            onClick={() => setActiveTab('ALL')}>
            ✅ Bull Stack Qualified ({allCount})
          </button>
          <button className={`tab-pill ${activeTab === 'SETUP' ? 'active-setup' : ''}`}
            onClick={() => setActiveTab('SETUP')}>
            📈 Intraday Setups ({setupCount})
          </button>
          <button className={`tab-pill ${activeTab === 'MOMENTUM' ? 'active-momentum' : ''}`}
            onClick={() => setActiveTab('MOMENTUM')}>
            🔥 Momentum ({momCount})
          </button>
          <button className={`tab-pill ${activeTab === 'BREAKOUT' ? 'active-momentum' : ''}`}
            onClick={() => setActiveTab('BREAKOUT')}
            style={{ background: activeTab === 'BREAKOUT' ? '#a78bfa' : undefined, borderColor: '#a78bfa', color: activeTab === 'BREAKOUT' ? '#fff' : '#a78bfa' }}>
            🚀 5m Breakout ({breakoutCount || 0})
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(15,23,42,0.5)', padding: '8px 14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <Search size={15} color="var(--text-muted)" />
          <input
            placeholder="Search ticker…" value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-main)', fontSize: '0.85rem', width: '130px' }}
          />
        </div>
      </div>

      {/* Info banners */}
      {activeTab === 'ALL' && (
        <div style={{ background: 'rgba(129,140,248,0.08)', border: '1px solid rgba(129,140,248,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          ✅ Stocks meeting <strong style={{color:'var(--accent)'}}>Weekly ST(10,3) == BULLISH</strong> + <strong style={{color:'var(--accent)'}}>Price &gt; 50 SMA &gt; 100 SMA &gt; 200 SMA</strong> (Institutional Bull Stack).
        </div>
      )}
      {activeTab === 'SETUP' && (
        <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          📈 Bull Stack qualified stocks that also show an <strong style={{color:'var(--bullish)'}}>Open=Low (BUY)</strong> or <strong style={{color:'var(--bearish)'}}>Open=High (SELL)</strong> intraday setup today.
        </div>
      )}
      {activeTab === 'MOMENTUM' && (
        <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          🔥 <strong style={{color:'var(--momentum)'}}>Elite picks</strong>: MA Bull Stack + Weekly ST + Open=Low setup + <strong>5-min close above previous day's High</strong>.
        </div>
      )}
      {activeTab === 'BREAKOUT' && (
        <div style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)', borderRadius: '8px', padding: '10px 14px', marginBottom: '14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          🚀 <strong style={{color:'#a78bfa'}}>5m Breakout</strong>: MA Bull Stack qualified stocks where <strong style={{color:'#a78bfa'}}>5-min close is above previous day's High</strong> (no Open=Low required).
        </div>
      )}

      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-dim)' }}>
          {search ? `No results for "${search}"` : 'No stocks found for current filter.'}
        </div>
      ) : (
        <div className="data-table-wrapper" style={{ maxHeight: '550px', overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <SortTh field="ticker">Ticker</SortTh>
                <SortTh field="current_price">Price (₹)</SortTh>
                <SortTh field="change_pct">Day Chg%</SortTh>
                <SortTh field="weekly_supertrend">Weekly ST</SortTh>
                <SortTh field="sma_50">50 SMA</SortTh>
                <SortTh field="sma_100">100 SMA</SortTh>
                <SortTh field="sma_200">200 SMA</SortTh>
                <SortTh field="ma_distance_pct">50 SMA Dist%</SortTh>
                <SortTh field="vol_surge">Vol Surge</SortTh>
                {showIntraday && <SortTh field="day_open">Open (₹)</SortTh>}
                {showIntraday && <SortTh field="day_low">Low (₹)</SortTh>}
                {showIntraday && <SortTh field="entry_price">Entry (₹)</SortTh>}
                {showIntraday && <SortTh field="stoploss">Stoploss</SortTh>}
                {showIntraday && <SortTh field="target_1">Target 1</SortTh>}
                {showIntraday && <SortTh field="pnl_pct">PnL%</SortTh>}
                {showIntraday && <th>🔥</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => {
                const isBull = s.setup_type === 'OPEN_LOW';
                const isMom  = s.momentum_confirmed;
                return (
                  <tr key={s.ticker}
                    className={isMom ? 'momentum-row' : ''}
                    onClick={() => onSelectStock(s)}
                    style={{ cursor: 'pointer' }}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: '800', fontSize: '0.92rem' }}>{s.ticker}</span>
                        {isMom && <span className="badge badge-momentum" style={{fontSize:'0.6rem',padding:'2px 6px'}}>🔥 MOM</span>}
                        {s.exact_match && <span className="badge badge-momentum" style={{fontSize:'0.6rem',padding:'2px 6px',background:'rgba(245,158,11,0.2)',color:'#f59e0b'}}>⭐ EXACT</span>}
                      </div>
                    </td>
                    <td className="mono" style={{ fontWeight: '700', color: 'var(--accent)' }}>{fmt(s.current_price)}</td>
                    <td className="mono" style={{ color: s.change_pct >= 0 ? 'var(--bullish)' : 'var(--bearish)' }}>
                      {s.change_pct >= 0 ? <TrendingUp size={13} style={{display:'inline',marginRight:'3px'}} /> : <TrendingDown size={13} style={{display:'inline',marginRight:'3px'}} />}
                      {fmtPct(s.change_pct)}
                    </td>
                    <td className="mono" style={{ color: 'var(--bullish)', fontSize: '0.8rem' }}>{fmt(s.weekly_supertrend)}</td>
                    <td className="mono" style={{ color: 'var(--accent)', fontSize: '0.8rem' }}>{fmt(s.sma_50)}</td>
                    <td className="mono" style={{ color: 'var(--accent2)', fontSize: '0.8rem' }}>{fmt(s.sma_100)}</td>
                    <td className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{fmt(s.sma_200)}</td>
                    <td className="mono" style={{ color: s.ma_distance_pct > 5 ? 'var(--bullish)' : 'var(--accent)', fontWeight: '700' }}>
                      +{Number(s.ma_distance_pct).toFixed(2)}%
                    </td>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>{Number(s.vol_surge).toFixed(2)}x</td>
                    {showIntraday && <td className="mono" style={{ color: 'var(--text-main)' }}>{fmt(s.day_open)}</td>}
                    {showIntraday && <td className="mono" style={{ color: 'var(--text-main)' }}>{fmt(s.day_low)}</td>}
                    {showIntraday && <td className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: '700' }}>{fmt(s.entry_price)}</td>}
                    {showIntraday && <td className="mono" style={{ color: 'var(--bearish)', fontSize: '0.8rem' }}>{fmt(s.stoploss)}</td>}
                    {showIntraday && <td className="mono" style={{ color: 'var(--bullish)', fontSize: '0.8rem' }}>{fmt(s.target_1)}</td>}
                    {showIntraday && (
                      <td className="mono" style={{ color: (s.pnl_pct ?? 0) >= 0 ? 'var(--bullish)' : 'var(--bearish)', fontWeight: '700' }}>
                        {fmtPct(s.pnl_pct)}
                      </td>
                    )}
                    {showIntraday && (
                      <td style={{ fontSize: '1rem' }}>{isMom ? '🔥' : '—'}</td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: '12px', fontSize: '0.78rem', color: 'var(--text-dim)', textAlign: 'right' }}>
        {filtered.length} stocks shown
      </div>
    </div>
  );
}
