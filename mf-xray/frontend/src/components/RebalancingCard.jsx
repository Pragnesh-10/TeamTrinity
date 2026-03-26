import React from 'react';

export default function RebalancingCard({ action }) {
  const isBuy = action.action === "BUY";
  
  return (
    <div className={`border-l-4 rounded-xl p-6 bg-surface border-y border-r border-border mb-4 ${isBuy ? 'border-l-teal' : 'border-l-amber'}`}>
      <div className="flex justify-between items-start">
        <div>
          <span className={`inline-block px-2 py-1 rounded text-xs font-bold mb-3 ${isBuy ? 'bg-teal/20 text-teal' : 'bg-amber/20 text-amber'}`}>
            [{action.action}]
          </span>
          <h4 className="text-lg font-bold">{action.fund_name}</h4>
          <p className="text-sm text-gray-400 mt-1 font-mono">
            Allocation: {action.current_pct}% → <span className="text-white">{action.target_pct}%</span>
          </p>
        </div>
        <div className="text-right">
          <p className="text-xl font-mono text-white">₹{action.amount.toLocaleString()}</p>
          {action.units_to_sell && (
            <p className="text-sm text-gray-500 mt-1">{action.units_to_sell} units</p>
          )}
        </div>
      </div>
      
      {!isBuy && (
        <div className="grid grid-cols-2 gap-4 mt-6 p-4 bg-background rounded-lg border border-border">
          <div>
            <p className="text-xs text-gray-500 uppercase">Est. STCG Tax</p>
            <p className="font-mono text-red">₹{action.stcg_tax}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Est. LTCG Tax</p>
            <p className="font-mono text-amber">₹{action.ltcg_tax}</p>
          </div>
        </div>
      )}
      
      <p className="mt-4 text-sm text-gray-300">
        <span className="text-teal font-bold mr-2">↳</span>
        {action.recommendation}
      </p>
    </div>
  );
}
