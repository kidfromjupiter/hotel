'use client';

import { useState, useEffect } from 'react';
import { HiOutlineCurrencyDollar, HiOutlineUsers, HiOutlineHome, HiOutlineCube } from 'react-icons/hi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMonthlyRevenue, getBranches, getOccupancyReport } from '@/lib/api';

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
  const [loadError, setLoadError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setChartLoading(true);
    setLoadError('');
    const year = new Date().getFullYear();
    Promise.all([
      getMonthlyRevenue(year),
      getBranches(),
    ]).then(([revenue, branches]) => {
      if (!active) return;
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
      if (!active) return;
      setChartData([]);
      setTotalRevenue('\u2014');
      setBranchCount('\u2014');
      setLoadError('Could not load dashboard data. Please try again.');
    }).finally(() => {
      if (active) setChartLoading(false);
    });
    return () => { active = false; };
  }, [reloadKey]);

  const [occupancy, setOccupancy] = useState<Awaited<ReturnType<typeof getOccupancyReport>> | null>(null);
  const [occupancyLoading, setOccupancyLoading] = useState(true);
  const [occupancyError, setOccupancyError] = useState('');
  const [occupancyReloadKey, setOccupancyReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setOccupancyLoading(true);
    setOccupancyError('');
    setOccupancy(null);
    const now = new Date();
    const localDate = (date: Date) =>
      `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const start = localDate(new Date(now.getFullYear(), now.getMonth(), 1));
    const end = localDate(now);
    const result = now.getDate() === 1
      ? Promise.resolve({ period: { start_date: start, end_date: end }, branches: [] })
      : getOccupancyReport(start, end);

    result.then(data => {
      if (active) setOccupancy(data);
    }).catch(() => {
      if (active) setOccupancyError('Could not load occupancy data.');
    }).finally(() => {
      if (active) setOccupancyLoading(false);
    });
    return () => { active = false; };
  }, [occupancyReloadKey]);

  const occupiedNights = occupancy?.branches.reduce((sum, b) => sum + b.occupied_nights, 0) ?? 0;
  const possibleNights = occupancy?.branches.reduce((sum, b) => sum + b.total_possible_nights, 0) ?? 0;
  const occupancyValue = occupancyLoading ? '...' : possibleNights > 0
    ? `${((occupiedNights / possibleNights) * 100).toFixed(2)}%` : '\u2014';
  const occupancyStatus = occupancyLoading ? 'Loading' : occupancyError
    ? 'Unavailable' : possibleNights > 0 ? 'Month to date' : 'No data';

  const dataStatus = chartLoading ? 'Loading' : loadError ? 'Unavailable' : 'Live';
  const metrics = [
    { title: 'Total Revenue (YTD)', value: chartLoading ? '...' : totalRevenue, trend: dataStatus, trendUp: !loadError, icon: HiOutlineCurrencyDollar },
    { title: 'Occupancy (Month to Date)', value: occupancyValue, trend: occupancyStatus, trendUp: !occupancyError, icon: HiOutlineHome },
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
        <button className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-colors">
          Download Full Report
        </button>
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
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} height={40} tickMargin={10} />
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
          <h3 className="text-lg font-bold text-slate-800 mb-4">Branch Status</h3>
          <div className="space-y-4">
            <p className="text-xs text-slate-500">
              Completed nights this month; today is excluded.
            </p>
            {occupancyLoading ? (
              <p role="status" className="text-sm text-slate-600">Loading occupancy...</p>
            ) : occupancyError ? (
              <div role="alert" className="text-sm text-red-700">
                <p>{occupancyError}</p>
                <button onClick={() => setOccupancyReloadKey(key => key + 1)}
                  className="mt-2 rounded-lg px-3 py-2 font-bold hover:bg-red-50">
                  Retry occupancy
                </button>
              </div>
            ) : occupancy?.period.start_date === occupancy?.period.end_date ? (
              <p className="text-sm text-slate-600">No completed nights yet this month.</p>
            ) : !occupancy?.branches.length ? (
              <p className="text-sm text-slate-600">No branch occupancy data available.</p>
            ) : (
              <>
                <p className="text-xs text-slate-500">
                  {occupancy.period.start_date} to {occupancy.period.end_date} (end excluded)
                </p>
                {occupancy.branches.map(branch => (
                  <div key={branch.branch_name} className="border-b border-slate-200 pb-3">
                    <div className="flex justify-between gap-3 text-sm font-bold text-slate-800">
                      <span>{branch.branch_name}</span>
                      <span>{branch.total_possible_nights > 0
                        ? `${branch.occupancy_rate_percent.toFixed(2)}%` : 'No rooms'}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      {branch.total_rooms} rooms; {branch.occupied_nights} occupied nights / {branch.total_possible_nights} possible nights
                    </p>
                  </div>
                ))}
              </>
            )}
            <a href="/admin/reports" className="inline-block text-sm font-bold text-sky-600 hover:underline">
              View detailed reports
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
