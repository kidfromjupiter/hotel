'use client';

import { useState, useEffect } from 'react';
import ServiceUsageReport from '@/components/ServiceUsageReport';
import { HiOutlineDownload, HiOutlineChartPie, HiOutlineTrendingUp, HiOutlineRefresh } from 'react-icons/hi';
import { getMonthlyRevenue, getOccupancyReport } from '@/lib/api';

const CURRENT_YEAR = new Date().getFullYear();

export default function AdminReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revenueData, setRevenueData] = useState<{ room: number; service: number; total: number } | null>(null);
  const [occupancyBranches, setOccupancyBranches] = useState<Array<{ branch_name: string; occupancy_rate_percent: number }>>([]);

  const [occupancyPeriod, setOccupancyPeriod] = useState<{ start: string; end: string } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const now = new Date();
      const startOfMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
      const localDate = (date: Date) =>
        `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const today = localDate(now);


      const [revenue, occupancy] = await Promise.all([
        getMonthlyRevenue(CURRENT_YEAR),
        now.getDate() === 1
          ? Promise.resolve({ branches: [] })
          : getOccupancyReport(startOfMonth, today),
      ]);

      const totalRoom = revenue.data.reduce((s, r) => s + r.room_revenue, 0);
      const totalService = revenue.data.reduce((s, r) => s + r.service_revenue, 0);
      const totalRevenue = revenue.data.reduce((sum, row) => sum + row.total_revenue, 0);
      setRevenueData({ room: totalRoom, service: totalService, total: totalRevenue });
      setOccupancyBranches(occupancy.branches);
      setOccupancyPeriod({ start: startOfMonth, end: today });
    } catch (e: any) {
      setError(e.message ?? 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);


  function exportCsv() {
    if (loading || error || !revenueData || !occupancyPeriod) return;

    const rows: Array<Array<string | number>> = [
      ['Report', 'Year', 'Period start', 'Period end (exclusive)', 'Branch', 'Metric', 'Value', 'Unit'],
      ['Invoice summary', CURRENT_YEAR, '', '', 'All branches', 'Room charges', revenueData.room, 'LKR'],
      ['Invoice summary', CURRENT_YEAR, '', '', 'All branches', 'Service charges', revenueData.service, 'LKR'],
      ['Invoice summary', CURRENT_YEAR, '', '', 'All branches', 'Invoice total including tax', revenueData.total, 'LKR'],
    ];

    for (const branch of occupancyBranches) {
      rows.push([
        'Occupancy', CURRENT_YEAR, occupancyPeriod.start, occupancyPeriod.end,
        branch.branch_name, 'Occupancy rate', branch.occupancy_rate_percent, '%',
      ]);
    }

    if (!occupancyBranches.length) {
      rows.push([
        'Occupancy', CURRENT_YEAR, occupancyPeriod.start, occupancyPeriod.end,
        'All branches', 'No completed-night occupancy data', '', '',
      ]);
    }

    const escapeCell = (value: string | number) => {
      const raw = String(value);
      const safe = typeof value === 'string' && /^[=+@\-\t\r\n]/.test(raw)
        ? "'" + raw : raw;
      return '"' + safe.replace(/"/g, '""') + '"';
    };
    const csv = rows.map(row => row.map(escapeCell).join(',')).join('\r\n');
    const blob = new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hotel-reports-${CURRENT_YEAR}-${occupancyPeriod.end}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const total = revenueData?.total ?? 0;
  const breakdownTotal = (revenueData?.room ?? 0) + (revenueData?.service ?? 0);
  const breakdownDenominator = breakdownTotal || 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Financial & Operations Reports</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Live data — revenue and occupancy analytics.</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-bold rounded-xl shadow-sm transition-colors"
          >
            <HiOutlineRefresh size={18} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button onClick={exportCsv} disabled={loading || !!error || !revenueData || !occupancyPeriod} className="disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white text-sm font-bold rounded-xl shadow-lg transition-colors">
            <HiOutlineDownload size={20} />
            Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 font-medium text-sm">
          ⚠️ {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500 font-medium text-sm">Loading report data...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Revenue Breakdown */}
          <div className="bg-white/80 backdrop-blur-md border border-white/40 shadow-xl shadow-slate-200/50 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-sky-100 text-sky-600 rounded-lg"><HiOutlineChartPie size={24} /></div>
              <div>
                <h3 className="text-lg font-bold text-slate-800">Revenue Breakdown</h3>
                <p className="text-xs text-slate-500 font-medium">Year {CURRENT_YEAR} — All Branches</p>
              </div>
            </div>
            {revenueData ? (
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between text-sm font-bold text-slate-700 mb-1.5">
                    <span>Room Bookings</span>
                    <span className="text-sky-600">LKR {revenueData.room.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-3">
                    <div className="bg-sky-500 h-3 rounded-full" style={{ width: `${(revenueData.room / breakdownDenominator) * 100}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm font-bold text-slate-700 mb-1.5">
                    <span>Services & Add-ons</span>
                    <span className="text-teal-600">LKR {revenueData.service.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-3">
                    <div className="bg-teal-500 h-3 rounded-full" style={{ width: `${(revenueData.service / breakdownDenominator) * 100}%` }} />
                  </div>
                </div>
                <div className="mt-6 pt-4 border-t border-slate-200 flex justify-between items-center">
                  <span className="font-bold text-slate-500">Total Invoice Value (Including Tax)</span>
                  <span className="text-2xl font-black text-slate-900">LKR {total.toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm">No revenue data available.</p>
            )}
          </div>

          {/* Occupancy by Branch */}
          <div className="bg-white/80 backdrop-blur-md border border-white/40 shadow-xl shadow-slate-200/50 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg"><HiOutlineTrendingUp size={24} /></div>
              <div>
                <h3 className="text-lg font-bold text-slate-800">Branch Occupancy</h3>
                <p className="text-xs text-slate-500 font-medium">Completed nights this month — Live data</p>
              </div>
            </div>
            {occupancyBranches.length > 0 ? (
              <div className="space-y-4">
                {occupancyBranches.map((branch, i) => {
                  const rate = branch.occupancy_rate_percent;
                  const barColor = rate >= 80 ? 'bg-green-500' : rate >= 60 ? 'bg-sky-500' : 'bg-orange-400';
                  const textColor = rate >= 80 ? 'text-green-600' : rate >= 60 ? 'text-sky-600' : 'text-orange-500';
                  return (
                    <div key={i}>
                      <div className="flex justify-between text-sm font-bold text-slate-700 mb-1.5">
                        <span>{branch.branch_name}</span>
                        <span className={textColor}>{rate.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5">
                        <div className={`${barColor} h-2.5 rounded-full`} style={{ width: `${Math.min(rate, 100)}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-slate-400 text-sm">No completed-night occupancy data available for this period.</p>
            )}
          </div>
        </div>
      )}
      <ServiceUsageReport />
    </div>
  );
}
