import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#00d4aa', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function AllocationPieChart({ allocations }) {
  if (!allocations) return null;
  const data = Object.keys(allocations).map((fund, index) => ({
    name: fund.length > 25 ? fund.substring(0, 25) + '...' : fund,
    value: allocations[fund]
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0a0f1e]/90 border border-white/10 p-3 rounded-xl shadow-2xl backdrop-blur-md text-sm">
          <p className="font-medium text-white mb-1">{payload[0].name}</p>
          <p className="text-teal font-mono tracking-wider">₹{payload[0].value.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  if (data.length === 0) return <div className="h-64 flex items-center justify-center text-gray-500">No allocation data</div>;

  return (
    <div className="h-full w-full min-h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={65}
            outerRadius={95}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} cursor={{fill: "transparent"}} />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '15px', opacity: 0.8 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
