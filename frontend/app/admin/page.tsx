'use client';

import { useState, useEffect } from 'react';
import { HiOutlineCurrencyDollar, HiOutlineUsers, HiOutlineHome, HiOutlineCube } from 'react-icons/hi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMonthlyRevenue, getBranches } from '@/lib/api';

const STATIC_METRICS = [
  { title: 'Overall Occupancy', value: '—', trend: 'Live', trendUp: true, icon: HiOutlineHome },
  { title: 'Active Branches', value: '—', trend: 'Live', trendUp: true, icon: HiOutlineCube },
  { title: 'New Guests Today', value: '—', trend: 'Live', trendUp: true, icon: HiOutlineUsers },
];


export default function AdminDashboardPage() {
  const [chartData, setChartData] = useState<{ name: string; revenue: number }[]>([]);
  const [totalRevenue, setTotalRevenue] = useState<string>('—');
  const [branchCount, setBranchCount] = useState<string>('—');
  const [chartLoading, setChartLoading] = useState(true);

  useEffect(() => {
    const year = new Date().getFullYear();
    Promise.all([
      getMonthlyRevenue(year),
      getBranches(),
    ]).then(([revenue, branches]) => {
      // Build chart data — aggregate all branches per month
      const monthMap: Record<string, number> = {};
      revenue.data.forEach(r => {
        monthMap[r.month] = (monthMap[r.month] ?? 0) + r.total_revenue;
      });
      const data = Object.entries(monthMap).map(([month, rev]) => ({
        name: month,
        revenue: rev,
      }));
      setChartData(data);

      const total = revenue.data.reduce((s, r) => s + r.total_revenue, 0);
      setTotalRevenue(`LKR ${total.toLocaleString()}`);
      setBranchCount(String(branches.length));
    }).catch(() => {
      setChartData([]);
    }).finally(() => {
      setChartLoading(false);
    });
  }, []);

  const metrics = [
    { title: 'Total Revenue (YTD)', value: totalRevenue, trend: 'Live', trendUp: true, icon: HiOutlineCurrencyDollar },
    { title: 'Overall Occupancy', value: '—', trend: 'Live', trendUp: true, icon: HiOutlineHome },
    { title: 'Active Branches', value: branchCount, trend: 'Live', trendUp: true, icon: HiOutlineCube },
    { title: 'New Guests Today', value: '—', trend: 'Live', trendUp: true, icon: HiOutlineUsers },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Overview of hotel operations and financial performance.</p>
        </div>
        <button className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-colors">
          Download Full Report
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50 relative overflow-hidden group hover:bg-white/90 transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <metric.icon size={80} className="text-sky-500" />
            </div>
            <div className="relative z-10">
              <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">{metric.title}</p>
              <div className="mt-4 flex items-end justify-between">
                <p className="text-3xl font-black text-slate-900">{metric.value}</p>
                <span className={`text-sm font-bold px-2 py-1 rounded-md ${metric.trendUp ? 'bg-sky-100 text-sky-700' : 'bg-red-100 text-red-700'}`}>
                  {metric.trend}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="lg:col-span-2 bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Revenue Overview ({new Date().getFullYear()})</h3>
          <div className="w-full mt-4">
            {chartLoading ? (
              <div className="flex items-center justify-center h-80">
                <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} height={40} tickMargin={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} tickFormatter={(v: number) => `LKR ${(v/1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    itemStyle={{ color: '#0f172a', fontWeight: 'bold' }}
                    formatter={(value: any) => [`LKR ${Number(value ?? 0).toLocaleString()}`, 'Revenue']}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Branch Status</h3>
          <div className="space-y-4">
            <p className="text-sm text-slate-500 font-medium">Fetching live occupancy data from the Reports module...</p>
            <p className="text-xs text-slate-400">Visit <span className="font-bold text-sky-600">Reports</span> for detailed branch occupancy analytics.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
