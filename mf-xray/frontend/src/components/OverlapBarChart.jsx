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
        <div className="bg-surface border border-border p-3 rounded-lg shadow-xl text-sm z-50">
          <p className="font-bold text-white mb-1">{data.fullName}</p>
          <p className="font-mono text-teal">Total Exposure: {data.pct}%</p>
          {data.pct > 5 && <p className="text-xs text-red mt-1">⚠ Exceeds 5% Risk Threshold</p>}
        </div>
      );
    }
    return null;
  };

  if (data.length === 0) return <div className="h-64 flex items-center justify-center text-gray-500">No major overlap detected</div>;

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3f5f" horizontal={true} vertical={false} />
          <XAxis type="number" domain={[0, Math.max(20, ...data.map(d => d.pct))]} hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#9ca3af', fontSize: 12 }} 
            width={120}
          />
          <Tooltip cursor={{ fill: '#1f2937' }} content={<CustomTooltip />} />
          <ReferenceLine x={5} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'top', value: '5% Limit', fill: '#ef4444', fontSize: 10 }} />
          <Bar dataKey="pct" radius={[0, 4, 4, 0]} maxBarSize={30}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.pct > 5 ? '#ef4444' : '#f59e0b'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
