import React from 'react';

export default function OverlapHeatmap({ pairwise }) {
  return (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-300 mb-4 border-b border-border pb-2">Top Overlapping Pairs</h4>
      
      {pairwise.slice(0, 5).map((pair, idx) => (
        <div key={idx} className="bg-background border border-border rounded-lg overflow-hidden">
          <div className="p-4 flex justify-between items-center border-b border-border">
            <div className="w-2/3">
              <p className="text-xs font-medium text-gray-400">{pair.fund_a}</p>
              <p className="text-xs text-center py-1 font-mono text-gray-600">×</p>
              <p className="text-xs font-medium text-gray-400">{pair.fund_b}</p>
            </div>
            <div className={`px-3 py-2 rounded font-mono font-bold text-lg ${
              pair.overlap_pct > 30 ? 'bg-red/20 text-red' : 
              pair.overlap_pct > 15 ? 'bg-amber/20 text-amber' : 
              'bg-teal/20 text-teal'
            }`}>
              {pair.overlap_pct}%
            </div>
          </div>
          
          <div className="px-4 py-3 bg-white/5">
            <p className="text-xs text-gray-500 uppercase mb-2">Common Holdings</p>
            <div className="flex flex-wrap gap-2">
              {pair.top_shared.slice(0, 3).map((stock, i) => (
                <span key={i} className="text-xs bg-surface border border-border px-2 py-1 rounded">
                  {stock.stock} <span className="text-gray-500">{(stock.min_weight_pct)}%</span>
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
      
      {pairwise.length === 0 && (
        <p className="text-sm text-gray-500 italic">Not enough funds for overlap analysis.</p>
      )}
    </div>
  );
}
