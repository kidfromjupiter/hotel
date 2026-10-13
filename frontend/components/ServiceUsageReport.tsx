'use client';

import { useEffect, useState } from 'react';
import { getServiceUsageReport } from '@/lib/api';
import type { ServiceUsageReportItem } from '@/lib/api';

export default function ServiceUsageReport() {
  const [rows, setRows] = useState<ServiceUsageReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    setRows([]);

    getServiceUsageReport()
      .then(report => {
        if (active) setRows(report.data);
      })
      .catch(() => {
        if (active) setError('Could not load service usage. Please try again.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, [reloadKey]);

  return (
    <section className="rounded-2xl bg-white/80 p-6 shadow-xl border border-white/40">
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-800">Service Usage</h2>
          <p className="text-xs text-slate-500 mt-1">
            All recorded service charges across all branches; no date filter.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setReloadKey(key => key + 1)}
          disabled={loading}
          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          {error ? 'Retry service usage' : 'Refresh service usage'}
        </button>
      </div>

      {loading ? (
        <p role="status" className="text-sm text-slate-600">Loading service usage...</p>
      ) : error ? (
        <p role="alert" className="text-sm text-red-700">{error}</p>
      ) : rows.length === 0 ? (
        <p className="text-sm text-slate-600">No service usage data available.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <caption className="sr-only">Service usage across all branches</caption>
            <thead className="border-b border-slate-200 text-slate-600">
              <tr>
                <th scope="col" className="py-3 pr-4">Service</th>
                <th scope="col" className="py-3 px-4 text-right">Bookings using service</th>
                <th scope="col" className="py-3 px-4 text-right">Days used</th>
                <th scope="col" className="py-3 pl-4 text-right">Service charges (LKR)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row.service_name} className="border-b border-slate-100">
                  <th scope="row" className="py-3 pr-4 font-medium text-slate-800">
                    {row.service_name}
                  </th>
                  <td className="py-3 px-4 text-right">{row.total_bookings_used.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right">{row.total_days_used.toLocaleString()}</td>
                  <td className="py-3 pl-4 text-right">
                    {row.total_revenue.toLocaleString(undefined, {
                      minimumFractionDigits: 2, maximumFractionDigits: 2
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
