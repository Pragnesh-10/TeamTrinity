import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function XirrChart({ data }) {
  const sortedData = [...data].sort((a, b) => b.xirr_pct - a.xirr_pct);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const fund = payload[0].payload;
      return (
        <div className="bg-[#0a0f1e]/90 border border-white/10 p-4 rounded-xl shadow-2xl backdrop-blur-md text-sm">
          <p className="font-bold text-white mb-2 max-w-[200px] truncate">{label}</p>
          <div className="flex justify-between items-center gap-4">
             <p className="text-gray-400 text-xs uppercase tracking-wider">XIRR</p>
             <p className="text-teal font-mono font-bold">{fund.xirr_pct}%</p>
          </div>
          <div className="flex justify-between items-center gap-4 mt-1 border-t border-white/5 pt-1">
             <p className="text-gray-400 text-xs uppercase tracking-wider">Value</p>
             <p className="font-mono text-gray-200">₹{fund.current_value.toLocaleString()}</p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 160, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis 
            dataKey="fund_name" 
            type="category" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#9ca3af', fontSize: 11, width: 150, dx: -10 }}
            width={150}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="xirr_pct" radius={[4, 4, 4, 4]} barSize={24} minPointSize={2}>
            {sortedData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.xirr_pct > 12 ? 'url(#tealGradient)' : entry.xirr_pct >= 8 ? 'url(#amberGradient)' : 'url(#redGradient)'} 
              />
            ))}
          </Bar>
          <defs>
             <linearGradient id="tealGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#00d4aa" stopOpacity={0.6}/>
                <stop offset="100%" stopColor="#00d4aa" stopOpacity={1}/>
             </linearGradient>
             <linearGradient id="amberGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.6}/>
                <stop offset="100%" stopColor="#f59e0b" stopOpacity={1}/>
             </linearGradient>
             <linearGradient id="redGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.6}/>
                <stop offset="100%" stopColor="#ef4444" stopOpacity={1}/>
             </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
