import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function XirrChart({ data }) {
  const sortedData = [...data].sort((a, b) => b.xirr_pct - a.xirr_pct);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const fund = payload[0].payload;
      return (
        <div className="bg-surface border border-border p-4 rounded-lg shadow-xl text-sm">
          <p className="font-bold mb-2">{label}</p>
          <p className="text-teal mb-1">XIRR: <span className="font-mono">{fund.xirr_pct}%</span></p>
          <p className="text-gray-400">Current Value: <span className="font-mono">₹{fund.current_value.toLocaleString()}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis 
            dataKey="fund_name" 
            type="category" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#9ca3af', fontSize: 12, width: 140 }}
            width={140}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
          <Bar dataKey="xirr_pct" radius={[0, 4, 4, 0]} minPointSize={2}>
            {sortedData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.xirr_pct > 12 ? '#00d4aa' : entry.xirr_pct >= 8 ? '#f59e0b' : '#ef4444'} 
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
