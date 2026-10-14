'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiOutlineCurrencyDollar, HiOutlineUsers, HiOutlineHome, HiOutlineCube } from 'react-icons/hi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMonthlyRevenue, getBranches, getOccupancyReport } from '@/lib/api';

interface OccupancyBranchData {
  branch_name: string;
  total_rooms: number;
  occupied_nights: number;
  total_possible_nights: number;
  occupancy_rate_percent: number;
}

export default function AdminDashboardPage() {
  const [chartData, setChartData] = useState<{ name: string; revenue: number }[]>([]);
  const [totalRevenue, setTotalRevenue] = useState<string>('—');
  const [branchCount, setBranchCount] = useState<string>('—');
  const [overallOccupancy, setOverallOccupancy] = useState<string>('—');
  const [occupancyBranches, setOccupancyBranches] = useState<OccupancyBranchData[]>([]);
  const [chartLoading, setChartLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setChartLoading(true);
    setLoadError('');
    const now = new Date();
    const year = now.getFullYear();
    const startOfMonth = `${year}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
    const localDate = (date: Date) =>
      `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    let occStart = startOfMonth;
    let occEnd = localDate(now);

    if (startOfMonth === occEnd) {
      const past = new Date(now);
      past.setDate(past.getDate() - 30);
      occStart = localDate(past);
    }

    Promise.all([
      getMonthlyRevenue(year),
      getBranches(),
      getOccupancyReport(occStart, occEnd).catch(() => null),
    ]).then(([revenue, branches, occupancy]) => {
      if (!active) return;
      // Build chart data — aggregate all branches per month
      const monthMap: Record<string, number> = {};
      revenue.data.forEach(r => {
        monthMap[r.month] = (monthMap[r.month] ?? 0) + r.total_revenue;
      });
      const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
      ];
      const data = months.map(month => ({
        name: month,
        revenue: monthMap[month] ?? 0,
      }));
      setChartData(data);

      const total = revenue.data.reduce((s, r) => s + r.total_revenue, 0);
      setTotalRevenue(`LKR ${total.toLocaleString()}`);
      setBranchCount(String(branches.length));

      if (occupancy && occupancy.branches && occupancy.branches.length > 0) {
        setOccupancyBranches(occupancy.branches);
        const totalOccNights = occupancy.branches.reduce((s, b) => s + b.occupied_nights, 0);
        const totalPossNights = occupancy.branches.reduce((s, b) => s + b.total_possible_nights, 0);
        const rate = totalPossNights > 0 ? (totalOccNights / totalPossNights) * 100 : 0;
        setOverallOccupancy(`${rate.toFixed(1)}%`);
      }
    }).catch(() => {
      if (!active) return;
      setChartData([]);
      setTotalRevenue('\u2014');
      setBranchCount('\u2014');
      setOverallOccupancy('\u2014');
      setOccupancyBranches([]);
      setLoadError('Could not load dashboard data. Please try again.');
    }).finally(() => {
      if (active) setChartLoading(false);
    });
    return () => { active = false; };
  }, [reloadKey]);

  const dataStatus = chartLoading ? 'Loading' : loadError ? 'Unavailable' : 'Live';
  const metrics = [
    { title: 'Total Revenue (YTD)', value: chartLoading ? '...' : totalRevenue, trend: dataStatus, trendUp: !loadError, icon: HiOutlineCurrencyDollar },
    { title: 'Overall Occupancy', value: chartLoading ? '...' : overallOccupancy, trend: overallOccupancy !== '\u2014' ? 'Live' : dataStatus, trendUp: !loadError, icon: HiOutlineHome },
    { title: 'Active Branches', value: chartLoading ? '...' : branchCount, trend: dataStatus, trendUp: !loadError, icon: HiOutlineCube },
    { title: 'New Guests Today', value: '\u2014', trend: 'Not available', trendUp: true, icon: HiOutlineUsers },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Overview of hotel operations and financial performance.</p>
        </div>
        <Link
          href="/admin/reports"
          className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-colors inline-block"
        >
          Download Full Report
        </Link>
      </div>

      {loadError && (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p>{loadError}</p>
          <button onClick={() => setReloadKey(key => key + 1)}
            className="rounded-lg px-4 py-2 font-bold hover:bg-red-100">
            Retry
          </button>
        </div>
      )}

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
            ) : loadError ? (
              <div className="flex items-center justify-center h-80 text-sm text-slate-600">
                Revenue chart unavailable. Use Retry above to reload.
              </div>
            ) : chartData.length === 0 ? (
              <div className="flex items-center justify-center h-80 text-sm text-slate-600">
                No revenue data available for this year.
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
                  <XAxis dataKey="name" interval={0} tickFormatter={(month: string) => month.slice(0, 3)} axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} height={40} tickMargin={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} tickFormatter={(v) => `LKR ${(v/1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    itemStyle={{ color: '#0f172a', fontWeight: 'bold' }}
                    formatter={(value) => [`LKR ${Number(value ?? 0).toLocaleString()}`, 'Revenue']}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800">Branch Occupancy</h3>
            <span className="text-xs font-semibold px-2 py-0.5 bg-sky-100 text-sky-700 rounded-md">
              MTD
            </span>
          </div>
          {occupancyBranches.length > 0 ? (
            <div className="space-y-4">
              {occupancyBranches.map((branch) => (
                <div key={branch.branch_name} className="space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="font-bold text-slate-700">{branch.branch_name}</span>
                    <span className="font-extrabold text-sky-600">{branch.occupancy_rate_percent}%</span>
                  </div>
                  <div className="w-full bg-slate-200/60 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-sky-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(branch.occupancy_rate_percent, 3))}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>{branch.occupied_nights} occupied nights</span>
                    <span>{branch.total_rooms} rooms</span>
                  </div>
                </div>
              ))}
              <div className="pt-2 border-t border-slate-100">
                <Link href="/admin/reports" className="text-xs font-bold text-sky-600 hover:text-sky-700 flex items-center justify-between">
                  <span>View Full Occupancy Report</span>
                  <span>→</span>
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-slate-500 font-medium">Fetching live occupancy data from the Reports module...</p>
              <p className="text-xs text-slate-400">Visit <Link href="/admin/reports" className="font-bold text-sky-600 hover:underline">Reports</Link> for detailed branch occupancy analytics.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
