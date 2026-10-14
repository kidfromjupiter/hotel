'use client';

import { useState, useEffect } from 'react';
import ServiceUsageReport from '@/components/ServiceUsageReport';
import { HiOutlineDownload, HiOutlineChartPie, HiOutlineTrendingUp, HiOutlineRefresh } from 'react-icons/hi';
import { getMonthlyRevenue, getOccupancyReport, getGuestBillingReport, getServiceTrendsReport, getServiceUsageReport } from '@/lib/api';

const CURRENT_YEAR = new Date().getFullYear();

export default function AdminReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revenueData, setRevenueData] = useState<{ room: number; service: number; tax: number; total: number } | null>(null);
  const [monthlyRows, setMonthlyRows] = useState<Array<{ branch_name: string; month: string; room_revenue: number; service_revenue: number; tax_revenue: number; total_revenue: number }>>([]);
  const [occupancyBranches, setOccupancyBranches] = useState<Array<{ branch_name: string; occupancy_rate_percent: number }>>([]);
  const [billingRows, setBillingRows] = useState<Array<{ guest_name: string; booking_id: number; outstanding_balance: number; payment_status: string }>>([]);
  const [trendRows, setTrendRows] = useState<Array<{ rank: number; service_name: string; times_used: number; unique_guests: number }>>([]);
  const [startDate, setStartDate] = useState(`${CURRENT_YEAR}-${String(new Date().getMonth() + 1).padStart(2, '0')}-01`);
  const [endDate, setEndDate] = useState(new Date(Date.now() + 86400000).toLocaleDateString('en-CA'));

  const [occupancyPeriod, setOccupancyPeriod] = useState<{ start: string; end: string } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (endDate <= startDate) throw new Error('End date must be after start date.');
      const [revenue, occupancy, billing, trends] = await Promise.all([
        getMonthlyRevenue(CURRENT_YEAR),
        getOccupancyReport(startDate, endDate),
        getGuestBillingReport(),
        getServiceTrendsReport(),
      ]);

      const totalRoom = revenue.data.reduce((s, r) => s + r.room_revenue, 0);
      const totalService = revenue.data.reduce((s, r) => s + r.service_revenue, 0);
      const totalTax = revenue.data.reduce((s, r) => s + r.tax_revenue, 0);
      const totalRevenue = revenue.data.reduce((sum, row) => sum + row.total_revenue, 0);
      setRevenueData({ room: totalRoom, service: totalService, tax: totalTax, total: totalRevenue });
      setMonthlyRows(revenue.data);
      setOccupancyBranches(occupancy.branches);
      setOccupancyPeriod({ start: startDate, end: endDate });
      setBillingRows(billing.data);
      setTrendRows(trends.top_services);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);


  async function exportCsv() {
    if (loading || error || !revenueData || !occupancyPeriod) return;
    const services = await getServiceUsageReport();

    const rows: Array<Array<string | number>> = [
      ['Report', 'Year', 'Period start', 'Period end (exclusive)', 'Branch', 'Metric', 'Value', 'Unit'],
      ['Payments received', CURRENT_YEAR, '', '', 'All branches', 'Room revenue', revenueData.room, 'LKR'],
      ['Payments received', CURRENT_YEAR, '', '', 'All branches', 'Service revenue', revenueData.service, 'LKR'],
      ['Payments received', CURRENT_YEAR, '', '', 'All branches', 'Tax received', revenueData.tax, 'LKR'],
      ['Payments received', CURRENT_YEAR, '', '', 'All branches', 'Total revenue', revenueData.total, 'LKR'],
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
    billingRows.forEach(row => rows.push(['Guest billing', CURRENT_YEAR, '', '', row.guest_name,
      `Booking ${row.booking_id} ${row.payment_status}`, row.outstanding_balance, 'LKR']));
    monthlyRows.forEach(row => {
      rows.push(['Monthly revenue', CURRENT_YEAR, '', '', row.branch_name, `${row.month} room`, row.room_revenue, 'LKR']);
      rows.push(['Monthly revenue', CURRENT_YEAR, '', '', row.branch_name, `${row.month} service`, row.service_revenue, 'LKR']);
      rows.push(['Monthly revenue', CURRENT_YEAR, '', '', row.branch_name, `${row.month} tax`, row.tax_revenue, 'LKR']);
    });
    services.data.forEach(row => rows.push(['Service usage', CURRENT_YEAR, '', '',
      `${row.branch_name} room ${row.room_number}`, row.service_name, row.total_quantity, 'units']));
    trendRows.forEach(row => rows.push(['Service trends', CURRENT_YEAR, '', '', 'All branches',
      `${row.rank}. ${row.service_name} (${row.unique_guests} guests)`, row.times_used, 'units']));

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
          <label className="text-xs text-slate-600">From<input aria-label="Occupancy from" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="block border rounded px-2 py-1" /></label>
          <label className="text-xs text-slate-600">To (exclusive)<input aria-label="Occupancy to" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="block border rounded px-2 py-1" /></label>
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
                  <span className="font-bold text-slate-500">Payments received (including LKR {revenueData.tax.toLocaleString()} tax)</span>
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
      <section className="rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="font-bold text-lg mb-3">Monthly revenue by branch</h2>
        <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="text-left">Branch</th><th>Month</th><th className="text-right">Rooms</th><th className="text-right">Services</th><th className="text-right">Tax</th><th className="text-right">Received</th></tr></thead><tbody>
          {monthlyRows.map(row => <tr key={`${row.branch_name}-${row.month}`} className="border-t"><td>{row.branch_name}</td><td className="text-center">{row.month}</td><td className="text-right">{row.room_revenue.toLocaleString()}</td><td className="text-right">{row.service_revenue.toLocaleString()}</td><td className="text-right">{row.tax_revenue.toLocaleString()}</td><td className="text-right">{row.total_revenue.toLocaleString()}</td></tr>)}
        </tbody></table></div>
      </section>
      <ServiceUsageReport />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="rounded-2xl bg-white p-6 shadow-xl">
          <h2 className="font-bold text-lg mb-3">Guest billing and unpaid balances</h2>
          <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="text-left">Guest</th><th>Booking</th><th>Status</th><th className="text-right">Due (LKR)</th></tr></thead><tbody>
            {billingRows.map(row => <tr key={row.booking_id} className="border-t"><td>{row.guest_name}</td><td className="text-center">{row.booking_id}</td><td className="text-center">{row.payment_status}</td><td className="text-right">{row.outstanding_balance.toLocaleString()}</td></tr>)}
          </tbody></table></div>
        </section>
        <section className="rounded-2xl bg-white p-6 shadow-xl">
          <h2 className="font-bold text-lg mb-3">Top services and guest preferences</h2>
          <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="text-left">Service</th><th>Units</th><th>Guests</th></tr></thead><tbody>
            {trendRows.map(row => <tr key={row.rank} className="border-t"><td>{row.rank}. {row.service_name}</td><td className="text-center">{row.times_used}</td><td className="text-center">{row.unique_guests}</td></tr>)}
          </tbody></table></div>
        </section>
      </div>
    </div>
  );
}
