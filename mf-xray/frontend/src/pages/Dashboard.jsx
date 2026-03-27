import React, { useMemo } from 'react';
import AllocationPieChart from '../components/AllocationPieChart';
import OverlapBarChart from '../components/OverlapBarChart';
import XirrChart from '../components/XirrChart';
import FirePlanner from './FirePlanner';

export default function Dashboard({ result, onReset }) {
  const { 
    portfolio_summary, xirr, overlap, issues_detected, 
    recommendations, before_after, expense_loss, tax_liability, disclaimer, audit_trail,
    per_fund_xirr
  } = result;

  const fireInitialInput = useMemo(() => {
    return {
      existing_investments: portfolio_summary?.total_current_value || 0,
    };
  }, [portfolio_summary?.total_current_value]);

  return (
    <div className="min-h-screen p-6 md:p-12 max-w-7xl mx-auto space-y-8">
      <header className="flex justify-between items-center pb-6 border-b border-border">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Agent Analysis Report</h1>
          <p className="text-gray-400">
            A single narrative combining portfolio diagnostics and your FIRE path.
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-surface text-sm font-medium border border-border rounded-lg hover:border-teal/50 transition-colors"
        >
          Start Over
        </button>
      </header>

      {/* Core KPIs */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-surface p-6 rounded-2xl border border-border md:col-span-1 flex flex-col justify-center items-center text-center">
          <p className="text-gray-400 mb-2 font-medium uppercase tracking-wider text-xs">Portfolio XIRR</p>
          <h2 className="text-5xl font-mono font-bold text-teal drop-shadow-[0_0_15px_rgba(0,212,170,0.5)]">
            {xirr}
          </h2>

        </div>
        
        <div className="bg-surface p-6 rounded-2xl border border-border md:col-span-3 grid grid-cols-4 gap-4 text-center items-center">
          <div>
            <p className="text-gray-400 text-sm mb-1">Total Invested</p>
            <p className="text-2xl font-mono">₹{portfolio_summary.total_invested.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Current Value</p>
            <p className="text-2xl font-mono text-white">₹{portfolio_summary.total_current_value.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Expense Drag</p>
            <p className="text-2xl font-mono text-red">{expense_loss}</p>
            <p className="text-xs text-gray-500 mt-1">vs Direct-Plan equivalent</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Est. STCG Tax</p>
            <p className="text-2xl font-mono text-amber">₹{tax_liability?.stcg_liability?.toLocaleString() || 0}</p>
            <p className="text-xs text-gray-500 mt-1" title={tax_liability?.regime_notes}>[i] Hover for Regime Rules</p>
          </div>
        </div>
      </section>

      {/* Visualizations */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface p-6 rounded-2xl border border-border">
          <h3 className="text-xl font-bold mb-6">Asset Allocation</h3>
          <AllocationPieChart allocations={portfolio_summary.allocations || {}} />
        </div>
        <div className="bg-surface p-6 rounded-2xl border border-border">
          <h3 className="text-xl font-bold mb-6">Stock Overlap Exposure</h3>
          <OverlapBarChart overlap={overlap} />
        </div>
      </section>

      {/* Per-Fund XIRR Chart */}
      {per_fund_xirr && per_fund_xirr.length > 0 && (
        <section className="bg-surface p-6 rounded-2xl border border-border">
          <h3 className="text-xl font-bold mb-6">Per-Fund XIRR Breakdown</h3>
          <XirrChart data={per_fund_xirr} />
        </section>
      )}

      {/* FIRE Plan (prefilled from portfolio) */}
      <section className="bg-surface p-6 rounded-2xl border border-border">
        <div className="flex items-start justify-between gap-6 mb-4">
          <div>
            <h3 className="text-2xl font-bold">FIRE Plan</h3>
            <p className="text-sm text-gray-400 mt-1">
              Prefilled with your portfolio’s current value to connect today’s holdings to your retirement trajectory.
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Starting Corpus (from X-Ray)</p>
            <p className="font-mono text-lg">
              ₹{(portfolio_summary?.total_current_value || 0).toLocaleString()}
            </p>
          </div>
        </div>
        <FirePlanner title="Inputs and live results" initialInput={fireInitialInput} />
      </section>


      <section className="bg-surface p-6 rounded-2xl border border-border">
        <div className="flex justify-between items-start mb-6">
          <h3 className="text-2xl font-bold flex items-center gap-3">
            <span className="bg-teal/20 text-teal p-2 rounded-lg">⚡</span> Agent Recommendations
          </h3>
          <div className="text-right">
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Target Overlap Reduction</p>
            <div className="flex items-center gap-3 font-mono">
              <span className="text-red/80 strike-through">{before_after.overlap_before}</span>
              <span className="text-gray-500">→</span>
              <span className="text-teal font-bold">{before_after.overlap_after}</span>
            </div>
          </div>
        </div>

        {issues_detected.length > 0 && (
          <div className="mb-6 space-y-2">
            {issues_detected.map((issue, idx) => (
              <div key={idx} className="bg-red/10 border border-red/30 text-red px-4 py-3 rounded-lg text-sm">
                ⚠ {issue}
              </div>
            ))}
          </div>
        )}

        <div className="space-y-4">
          {recommendations.map((rec, idx) => (
            <div key={idx} className="border border-border bg-background p-6 rounded-xl relative overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-teal to-blue-500"></div>
              <h4 className="text-lg font-bold text-white mb-4">{rec.action}</h4>
              
              {rec.literacy_insight && (
                <div className="bg-teal/10 border border-teal/20 p-3 rounded-lg mb-4">
                  <p className="text-xs text-teal font-medium uppercase tracking-wider mb-1">💡 Financial Literacy Insight</p>
                  <p className="text-sm text-teal/90">{rec.literacy_insight}</p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase font-bold mb-1">Agent Reasoning</p>
                  <p className="text-sm text-gray-300">{rec.reason}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-bold mb-1">Predicted Impact</p>
                  <p className="text-sm text-gray-300">{rec.impact}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>



      {/* Compliance */}
      <div className="mt-8 border border-amber/30 bg-amber/5 px-6 py-4 rounded-lg flex justify-center text-center text-amber text-sm font-medium">
        <p>⚖ {disclaimer}</p>
      </div>
    </div>
  );
}
