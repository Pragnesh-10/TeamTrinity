import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import AllocationPieChart from '../components/AllocationPieChart';
import OverlapBarChart from '../components/OverlapBarChart';
import XirrChart from '../components/XirrChart';
import FirePlanner from './FirePlanner';
import { ShieldAlert, TrendingUp, DollarSign, Activity, FileWarning, ArrowLeft, Target, Layers, Zap, Scale } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 15 },
  show: { opacity: 1, scale: 1, y: 0, transition: { type: "spring", stiffness: 200, damping: 20 } }
};

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

  const formattedXirr = useMemo(() => {
    if (typeof xirr === 'number' && Number.isFinite(xirr)) return `${xirr.toFixed(2)}%`;
    if (typeof xirr === 'string') {
      const match = xirr.trim().match(/^(-?\d+(?:\.\d+)?)\s*(%)?\s*$/);
      if (match && Number.isFinite(Number(match[1]))) {
        return `${Number(match[1]).toFixed(2)}${match[2] ? '%' : ''}`;
      }
    }
    return xirr;
  }, [xirr]);

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white p-4 md:p-8 font-sans overflow-hidden relative">
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-teal/5 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface/30 p-6 rounded-[2rem] border border-white/5 backdrop-blur-xl shadow-2xl">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-teal via-blue-400 to-indigo-500 bg-clip-text text-transparent drop-shadow-sm">
              Portfolio X-Ray Results
            </h1>
            <p className="text-gray-400 mt-1.5 font-medium text-sm">AI-driven deep structural analysis & FIRE trajectory mapping.</p>
          </div>
          <button onClick={onReset} className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-5 py-2.5 rounded-2xl font-semibold transition-all hover:scale-105 active:scale-95 border border-white/10 shadow-lg">
            <ArrowLeft className="w-4 h-4" /> Analyze Another
          </button>
        </motion.div>

        {/* Core Metrics Grid */}
        <motion.div variants={containerVariants} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div variants={itemVariants} className="group bg-surface/50 p-6 rounded-3xl border border-white/5 relative overflow-hidden backdrop-blur-md transition-all hover:border-teal/30 hover:bg-surface/70">
            <div className="absolute top-[-10px] right-[-10px] p-4 opacity-5 group-hover:opacity-10 transition-opacity rotate-12"><DollarSign className="w-32 h-32 text-teal" /></div>
            <p className="text-gray-400 mb-2 font-bold uppercase tracking-[0.2em] text-xs">Total Current Value</p>
            <p className="text-3xl font-black text-white drop-shadow-md tracking-tight">₹{portfolio_summary?.total_current_value?.toLocaleString()}</p>
            <p className="text-teal/80 text-sm font-medium mt-3 flex items-center gap-2 bg-teal/10 w-fit px-3 py-1 rounded-full border border-teal/20">
              <Target className="w-3.5 h-3.5" /> Invested: ₹{portfolio_summary?.total_invested?.toLocaleString()}
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="group bg-surface/50 p-6 rounded-3xl border border-white/5 relative overflow-hidden backdrop-blur-md transition-all hover:border-amber-500/30 hover:bg-surface/70">
            <div className="absolute top-[-10px] right-[-10px] p-4 opacity-5 group-hover:opacity-10 transition-opacity rotate-12"><TrendingUp className="w-32 h-32 text-amber-500" /></div>
            <p className="text-gray-400 mb-2 font-bold uppercase tracking-[0.2em] text-xs">Portfolio XIRR</p>
            <p className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-amber-400 to-orange-500 drop-shadow-md tracking-tight">
              {formattedXirr}
            </p>
            {tax_liability && (
                <p className="text-amber-500/80 text-sm font-medium mt-3 flex items-center gap-2 bg-amber-500/10 w-fit px-3 py-1 rounded-full border border-amber-500/20" title={tax_liability.regime_notes}>
                    <Scale className="w-3.5 h-3.5" /> STCG: ₹{tax_liability.stcg_liability?.toLocaleString() || 0}
                </p>
            )}
          </motion.div>

          <motion.div variants={itemVariants} className="group bg-surface/50 p-6 rounded-3xl border border-white/5 relative overflow-hidden backdrop-blur-md transition-all hover:border-blue-500/30 hover:bg-surface/70">
             <div className="absolute top-[-10px] right-[-10px] p-4 opacity-5 group-hover:opacity-10 transition-opacity rotate-12"><Layers className="w-32 h-32 text-blue-500" /></div>
             <p className="text-gray-400 mb-2 font-bold uppercase tracking-[0.2em] text-xs">Overlap Exposure</p>
             <div className="flex items-baseline gap-2">
                 <p className="text-4xl font-black text-white drop-shadow-md tracking-tight">{overlap?.score || 0}</p>
                 <span className="text-gray-500 text-lg font-bold">/10</span>
             </div>
             <p className={`text-sm font-medium mt-3 w-fit px-3 py-1 rounded-full border ${overlap?.score > 7 ? 'text-red-400 bg-red-400/10 border-red-500/20' : overlap?.score > 4 ? 'text-amber-400 bg-amber-400/10 border-amber-500/20' : 'text-blue-400 bg-blue-400/10 border-blue-500/20'}`}>
              {overlap?.score > 7 ? 'Critical Redundancy' : overlap?.score > 4 ? 'Moderate Overlap' : 'Well Diversified'}
             </p>
          </motion.div>

          <motion.div variants={itemVariants} className="group bg-surface/50 p-6 rounded-3xl border border-white/5 relative overflow-hidden backdrop-blur-md transition-all hover:border-red-500/30 hover:bg-surface/70">
            <div className="absolute top-[-10px] right-[-10px] p-4 opacity-5 group-hover:opacity-10 transition-opacity rotate-12"><ShieldAlert className="w-32 h-32 text-red-500" /></div>
            <p className="text-gray-400 mb-2 font-bold uppercase tracking-[0.2em] text-xs">Expense Drag Risk</p>
            <p className="text-3xl font-black text-red-400 drop-shadow-md tracking-tight">{expense_loss}</p>
            <p className="text-red-400/80 text-sm font-medium mt-3 bg-red-500/10 w-fit px-3 py-1 rounded-full border border-red-500/20">
              vs Direct Plan Equivalent
            </p>
          </motion.div>
        </motion.div>

        {/* Charts & Analysis Module */}
        <motion.div variants={containerVariants} initial="hidden" animate="show" className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          
          <motion.div variants={itemVariants} className="bg-surface/40 p-6 md:p-8 rounded-[2rem] border border-white/5 backdrop-blur-lg shadow-xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-teal/5 blur-3xl rounded-full mix-blend-screen pointer-events-none group-hover:bg-teal/10 transition-colors" />
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 relative z-10">
                  <div className="flex items-center gap-4">
                      <div className="bg-gradient-to-br from-teal/20 to-teal/5 p-3 rounded-2xl border border-teal/10 shadow-inner">
                          <Activity className="w-6 h-6 text-teal" />
                      </div>
                      <div>
                          <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Growth Velocity</h3>
                          <p className="text-xs text-gray-500 font-medium tracking-wide uppercase mt-1">Per-Fund Component XIRR Breakdown</p>
                      </div>
                  </div>
              </div>
              <div className="relative z-10 w-full rounded-2xl p-4 bg-[#0a0f1e]/50 border border-white/5 min-h-[350px]">
                  {per_fund_xirr && per_fund_xirr.length > 0 ? (
                  <XirrChart data={per_fund_xirr} />
                  ) : (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-500 space-y-3">
                      <FileWarning className="w-10 h-10 opacity-20" />
                      <p className="text-sm font-medium">Insufficient cashflow historical data for granular rendering.</p>
                  </div>
                  )}
              </div>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-surface/40 p-6 md:p-8 rounded-[2rem] border border-white/5 backdrop-blur-lg shadow-xl flex flex-col">
              <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-4">
                    <div className="bg-blue-500/20 p-3 rounded-2xl border border-blue-500/10"><Layers className="w-5 h-5 text-blue-400" /></div>
                    <h3 className="text-2xl font-bold">Asset Allocation</h3>
                  </div>
              </div>
              <div className="bg-[#0a0f1e]/50 rounded-2xl p-4 border border-white/5 flex-1 flex items-center justify-center min-h-[350px]">
                  <AllocationPieChart allocations={portfolio_summary?.allocations || {}} />
              </div>
          </motion.div>

        </motion.div>

        {/* AI Recommendations */}
        <motion.div variants={itemVariants} initial="hidden" animate="show" className="bg-gradient-to-br from-[#111827] to-[#1a2235] p-6 md:p-8 rounded-[2rem] border border-teal/20 shadow-2xl relative overflow-hidden shadow-teal/5">
            <div className="absolute -top-32 -right-32 w-96 h-96 bg-teal/10 blur-[100px] pointer-events-none" />
            
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 relative z-10">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                    <span className="bg-teal/20 text-teal p-2 rounded-xl text-xs uppercase tracking-widest font-black border border-teal/30 shadow-inner flex items-center"><Zap className="w-4 h-4 mr-1"/> AI</span>
                    Synthesized Directives
                </h3>
                {before_after && (
                    <div className="bg-black/40 border border-white/10 px-5 py-3 rounded-2xl backdrop-blur-md">
                        <p className="text-xs text-gray-500 uppercase tracking-widest mb-1 text-right">Target Overlap</p>
                        <div className="flex items-center gap-3 font-mono text-sm md:text-base">
                            <span className="text-red-400/80 line-through decoration-red-500/50 decoration-2">{before_after.overlap_before}</span>
                            <span className="text-gray-600">→</span>
                            <span className="text-teal font-bold">{before_after.overlap_after}</span>
                        </div>
                    </div>
                )}
            </div>

            {issues_detected && issues_detected.length > 0 && (
                <div className="mb-8 space-y-3 relative z-10">
                    {issues_detected.map((issue, idx) => (
                    <div key={idx} className="bg-red-500/10 border border-red-500/30 text-red-200 px-5 py-4 rounded-xl text-sm flex gap-3 shadow-inner">
                        <ShieldAlert className="w-5 h-5 text-red-400 shrink-0" /> {issue}
                    </div>
                    ))}
                </div>
            )}

            <div className="space-y-5 relative z-10">
                {recommendations?.map((rec, idx) => (
                <div key={idx} className="group bg-[#0a0f1e]/80 backdrop-blur-xl border border-white/5 p-6 rounded-2xl relative overflow-hidden transition-all hover:border-teal/30 hover:-translate-y-1 hover:shadow-2xl hover:shadow-teal/5">
                    <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-teal to-blue-500 shadow-[0_0_10px_rgba(0,212,170,0.8)] opacity-70 group-hover:opacity-100 transition-opacity"></div>
                    <div className="pl-4">
                        <h4 className="text-lg font-bold text-white mb-4 tracking-wide">{rec.action}</h4>
                        
                        {rec.literacy_insight && (
                        <div className="bg-teal/5 border border-teal/20 p-4 rounded-xl mb-5 flex gap-3 items-start">
                            <span className="text-teal text-lg">💡</span>
                            <div>
                                <p className="text-xs text-teal font-bold uppercase tracking-widest mb-1">Financial Literacy Insight</p>
                                <p className="text-sm text-teal/90 leading-relaxed font-medium">{rec.literacy_insight}</p>
                            </div>
                        </div>
                        )}
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-surface/30 p-5 rounded-xl border border-white/5">
                            <div>
                                <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-2 flex items-center gap-2"><Activity className="w-3 h-3"/> Agent Reasoning</p>
                                <p className="text-sm text-gray-300 leading-relaxed">{rec.reason}</p>
                            </div>
                            <div>
                                <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-2 flex items-center gap-2"><Target className="w-3 h-3"/> Predicted Impact</p>
                                <p className="text-sm text-gray-300 leading-relaxed">{rec.impact}</p>
                            </div>
                        </div>
                    </div>
                </div>
                ))}
                {!recommendations?.length && (
                    <div className="text-center p-12 bg-[#0a0f1e]/50 rounded-2xl border border-white/5">
                        <p className="text-gray-400 font-medium">No structural optimizations required. Portfolio is highly efficient.</p>
                    </div>
                )}
            </div>
        </motion.div>

        {/* FIRE Planner Module */}
        <motion.div variants={itemVariants} initial="hidden" animate="show" className="pt-8">
            <div className="bg-surface/40 p-6 md:p-8 rounded-[2rem] border border-white/5 backdrop-blur-lg shadow-xl mb-4 text-center sm:text-left flex flex-col sm:flex-row justify-between items-center gap-4">
              <div>
                 <h3 className="text-2xl font-bold flex items-center justify-center sm:justify-start gap-3">
                    <TrendingUp className="w-6 h-6 text-teal" /> Financial Independence Planner
                 </h3>
                 <p className="text-sm text-gray-400 mt-2">Connecting your current diagnostic portfolio size to your specific retirement timeline.</p>
              </div>
              <div className="bg-[#0a0f1e]/80 px-6 py-4 rounded-xl border border-white/5 shadow-inner">
                 <p className="text-[10px] text-gray-500 uppercase tracking-widest font-black mb-1">X-Ray Starting Corpus</p>
                 <p className="font-mono text-xl font-bold text-teal">₹{(portfolio_summary?.total_current_value || 0).toLocaleString()}</p>
              </div>
            </div>
            {/* The actual FirePlanner Component rendering its own internal advanced UI */}
            <FirePlanner initialInput={fireInitialInput} />
        </motion.div>

        {/* Footer & Compliance */}
        <motion.div variants={itemVariants} className="pt-16 pb-12 text-center space-y-8">
          <div className="bg-amber-500/5 border border-amber-500/20 px-6 py-4 rounded-2xl inline-flex justify-center text-center text-amber-500 text-xs md:text-sm font-medium shadow-inner max-w-4xl mx-auto">
            <p className="flex items-center justify-center gap-2"><Scale className="w-4 h-4 shrink-0" /> {disclaimer}</p>
          </div>
          
          <div className="text-left w-full max-w-6xl mx-auto bg-surface/20 p-6 md:p-8 rounded-[2rem] border border-white/5 relative group mt-8">
            <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="w-2 h-2 rounded-full bg-teal animate-pulse" />
                <h4 className="text-[10px] font-bold text-gray-500 font-mono uppercase tracking-[0.2em]">Diagnostic Neural Net Trace Logs</h4>
            </div>
            
            <div className="space-y-3 font-mono text-[11px] md:text-xs text-gray-500/70 max-h-48 overflow-y-auto pr-4 custom-scrollbar relative z-10 selection:bg-teal/20 selection:text-teal group-hover:text-gray-400 transition-colors">
              {audit_trail?.map((log, i) => (
                <div key={i} className="flex gap-4 p-2 rounded-lg hover:bg-white/5 transition-colors border-l-2 border-transparent hover:border-teal/30">
                    <span className="text-gray-600 shrink-0 w-8 tabular-nums">[{String(i+1).padStart(2,'0')}]</span>
                    <span className="leading-relaxed">{log}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
