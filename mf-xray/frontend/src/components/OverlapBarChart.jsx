import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

export default function OverlapBarChart({ overlap }) {
  // Convert { "Reliance": "14%", "HDFC": "11%" } to array
  const data = Object.keys(overlap).map(stock => ({
    name: stock.length > 15 ? stock.substring(0, 15) + '...' : stock,
    fullName: stock,
    pct: typeof overlap[stock] === 'number'
      ? parseFloat((overlap[stock] * 100).toFixed(1))
      : parseFloat(overlap[stock].replace('%', ''))
  })).sort((a, b) => b.pct - a.pct).slice(0, 10);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0a0f1e]/90 border border-white/10 p-4 rounded-xl shadow-2xl backdrop-blur-md text-sm z-50">
          <p className="font-bold text-white mb-2 max-w-[200px] truncate">{data.fullName}</p>
          <div className="flex justify-between items-center gap-4">
             <p className="text-gray-400 text-xs uppercase tracking-wider">Exposure</p>
             <p className="text-teal font-mono font-bold">{data.pct}%</p>
          </div>
          {data.pct > 5 && (
              <div className="mt-2 pt-2 border-t border-red-500/20">
                 <p className="text-[10px] text-red-400 uppercase tracking-widest font-black flex items-center gap-1">
                    ⚠ Exceeds 5% Risk Threshold
                 </p>
              </div>
          )}
        </div>
      );
    }
    return null;
  };

  if (data.length === 0) return <div className="h-64 flex items-center justify-center text-gray-500">No major overlap detected</div>;

  return (
    <div className="h-full w-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={true} vertical={false} />
          <XAxis type="number" domain={[0, Math.max(20, ...data.map(d => d.pct))]} hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#9ca3af', fontSize: 11, width: 120, dx: -5 }} 
            width={120}
          />
          <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} content={<CustomTooltip />} />
          <ReferenceLine x={5} stroke="#ef4444" strokeWidth={2} strokeDasharray="4 4" label={{ position: 'top', value: '5% Limit', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />
          <Bar dataKey="pct" radius={[4, 4, 4, 4]} barSize={20}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.pct > 5 ? 'url(#redOverlapGradient)' : 'url(#amberOverlapGradient)'} />
            ))}
          </Bar>
          <defs>
             <linearGradient id="amberOverlapGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.6}/>
                <stop offset="100%" stopColor="#f59e0b" stopOpacity={1}/>
             </linearGradient>
             <linearGradient id="redOverlapGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.6}/>
                <stop offset="100%" stopColor="#ef4444" stopOpacity={1}/>
             </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
