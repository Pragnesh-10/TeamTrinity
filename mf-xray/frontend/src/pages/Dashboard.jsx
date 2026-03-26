import React from 'react';
import XirrChart from '../components/XirrChart';
import OverlapHeatmap from '../components/OverlapHeatmap';
import RebalancingCard from '../components/RebalancingCard';
import LlmReport from '../components/LlmReport';

export default function Dashboard({ result, onReset }) {
  if (result.status === 'error') {
    return (
      <div className="p-8 text-center text-red">
        <h2 className="text-2xl font-bold mb-4">Pipeline Error</h2>
        <p>{result.error_message}</p>
        <button className="mt-4 px-4 py-2 border rounded" onClick={onReset}>Go Back</button>
      </div>
    );
  }

  const { portfolio, per_fund, overlap, rebalancing, llm_report, disclaimer } = result;

  return (
    <div className="min-h-screen p-6 md:p-12 max-w-7xl mx-auto space-y-8">
      <header className="flex justify-between items-center pb-6 border-b border-border">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Portfolio Results</h1>
          <p className="text-gray-400">Analysis complete spanning {portfolio.date_range.from} to {portfolio.date_range.to}</p>
        </div>
        <button onClick={onReset} className="px-4 py-2 bg-surface border border-border rounded-lg hover:border-teal/50 transition-colors">
          New Scan
        </button>
      </header>

      {/* Card 1: Overview */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-surface p-6 rounded-2xl border border-border md:col-span-1 flex flex-col justify-center items-center text-center">
          <p className="text-gray-400 mb-2 font-medium uppercase tracking-wider text-xs">Portfolio XIRR</p>
          <h2 className={`text-5xl font-mono font-bold ${portfolio.portfolio_xirr_pct > 13.5 ? 'text-teal drop-shadow-[0_0_15px_rgba(0,212,170,0.5)]' : 'text-amber'}`}>
            {portfolio.portfolio_xirr_pct}%
          </h2>
          <p className="text-xs text-gray-500 mt-3 font-mono">Vs Nifty 50: ~13.5%</p>
        </div>
        
        <div className="bg-surface p-6 rounded-2xl border border-border md:col-span-3 grid grid-cols-3 gap-4 text-center items-center">
          <div>
            <p className="text-gray-400 text-sm mb-1">Total Invested</p>
            <p className="text-2xl font-mono">₹{portfolio.total_invested.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Current Value</p>
            <p className="text-2xl font-mono text-white">₹{portfolio.total_current_value.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Absolute Gain</p>
            <p className={`text-2xl font-mono ${portfolio.absolute_gain >= 0 ? 'text-teal' : 'text-red'}`}>
              {portfolio.absolute_gain >= 0 ? '+' : '-'}₹{Math.abs(portfolio.absolute_gain).toLocaleString()}
            </p>
            <p className={`text-xs mt-1 ${portfolio.absolute_return_pct >= 0 ? 'text-teal' : 'text-red'}`}>
              {portfolio.absolute_return_pct >= 0 ? '+' : ''}{portfolio.absolute_return_pct}%
            </p>
          </div>
        </div>
      </section>

      {/* Card 2: Per-fund returns */}
      <section className="bg-surface p-6 rounded-2xl border border-border">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">Fund Performance</h3>
        <XirrChart data={per_fund} />
      </section>

      {/* Card 3: Overlap */}
      <section className="bg-surface p-6 rounded-2xl border border-border">
        <div className="flex justify-between items-start mb-6">
          <h3 className="text-xl font-bold">Overlap Analysis</h3>
          <div className="text-right">
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${
              overlap.concentration_risk === 'high' ? 'bg-red/10 border-red/30 text-red' : 
              overlap.concentration_risk === 'moderate' ? 'bg-amber/10 border-amber/30 text-amber' : 
              'bg-teal/10 border-teal/30 text-teal'
            }`}>
              {overlap.concentration_risk} RISK (HHI: {overlap.hhi})
            </span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <OverlapHeatmap pairwise={overlap.pairwise} />
          <div>
            <h4 className="font-medium text-gray-300 mb-4 border-b border-border pb-2">Top 10 Effective Holdings</h4>
            <div className="space-y-3">
              {overlap.portfolio_top_10.map((stock, i) => (
                <div key={i} className="flex justify-between text-sm">
                  <span>{stock.stock}</span>
                  <span className="font-mono text-gray-400">{stock.effective_pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Card 4: Rebalancing */}
      <section className="bg-surface p-6 rounded-2xl border border-border">
        <h3 className="text-xl font-bold mb-4">Rebalancing Plan</h3>
        <p className="text-gray-400 mb-6 pb-6 border-b border-border">{rebalancing.summary}</p>
        <div className="space-y-4">
          {rebalancing.actions.map((action, i) => (
            <RebalancingCard key={i} action={action} />
          ))}
        </div>
      </section>

      {/* Card 5: LLM Report */}
      <section className="bg-surface p-6 rounded-2xl border border-border">
        <h3 className="text-xl font-bold mb-6">AI Synthesis</h3>
        <LlmReport markdown={llm_report} />
      </section>

      {/* Disclaimer */}
      <div className="mt-12 mb-8 border border-amber/30 bg-amber/5 px-6 py-4 rounded-lg flex items-start gap-4 text-amber text-sm font-medium">
        <span className="text-xl">⚠</span>
        <p>{disclaimer}</p>
      </div>
    </div>
  );
}
