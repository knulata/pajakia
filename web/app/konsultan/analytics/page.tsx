"use client";

function formatRp(n: number) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
}

const monthlyData = [
  { month: "Oct", revenue: 38_000_000, clients: 35, spt: 42 },
  { month: "Nov", revenue: 42_500_000, clients: 40, spt: 48 },
  { month: "Dec", revenue: 45_000_000, clients: 43, spt: 87 },
  { month: "Jan", revenue: 48_000_000, clients: 45, spt: 53 },
  { month: "Feb", revenue: 50_000_000, clients: 46, spt: 51 },
  { month: "Mar", revenue: 52_500_000, clients: 47, spt: 156 },
];

const topClients = [
  { name: "PT Karya Digital", revenue: 3_000_000, obligations: 5, compliance: 100 },
  { name: "PT Maju Bersama", revenue: 2_500_000, obligations: 4, compliance: 75 },
  { name: "CV Sinar Abadi", revenue: 1_500_000, obligations: 3, compliance: 83 },
];

export default function AnalyticsPage() {
  const currentMonth = monthlyData[monthlyData.length - 1];
  const prevMonth = monthlyData[monthlyData.length - 2];
  const revenueGrowth = ((currentMonth.revenue - prevMonth.revenue) / prevMonth.revenue * 100).toFixed(1);
  const maxRevenue = Math.max(...monthlyData.map((d) => d.revenue));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold">Analitik</h1>

      {/* Top Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm">
          <div className="text-sm text-[var(--text-secondary)]">MRR</div>
          <div className="mt-1 text-2xl font-extrabold">{formatRp(currentMonth.revenue)}</div>
          <div className="mt-1 text-xs text-green-600">↑ {revenueGrowth}% dari bulan lalu</div>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm">
          <div className="text-sm text-[var(--text-secondary)]">ARR (Proyeksi)</div>
          <div className="mt-1 text-2xl font-extrabold">{formatRp(currentMonth.revenue * 12)}</div>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm">
          <div className="text-sm text-[var(--text-secondary)]">SPT Diproses Bulan Ini</div>
          <div className="mt-1 text-2xl font-extrabold">{currentMonth.spt}</div>
          <div className="mt-1 text-xs text-green-600">↑ {((currentMonth.spt / prevMonth.spt - 1) * 100).toFixed(0)}%</div>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm">
          <div className="text-sm text-[var(--text-secondary)]">Revenue per Klien</div>
          <div className="mt-1 text-2xl font-extrabold">{formatRp(Math.round(currentMonth.revenue / currentMonth.clients))}</div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Revenue Chart (simple bar chart) */}
        <div className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-bold">Pendapatan Bulanan</h2>
          <div className="flex items-end gap-3 h-48">
            {monthlyData.map((d) => (
              <div key={d.month} className="flex flex-1 flex-col items-center gap-1">
                <div className="text-xs font-medium">{formatRp(d.revenue / 1_000_000)}jt</div>
                <div
                  className="w-full rounded-t bg-[var(--primary)] transition-all"
                  style={{ height: `${(d.revenue / maxRevenue) * 140}px` }}
                />
                <div className="text-xs text-[var(--text-secondary)]">{d.month}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Entity Breakdown */}
        <div className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-bold">Komposisi Klien</h2>
          <div className="space-y-4">
            {[
              { label: "PT", count: 15, pct: 32, color: "bg-blue-500" },
              { label: "CV", count: 8, pct: 17, color: "bg-purple-500" },
              { label: "Orang Pribadi", count: 20, pct: 43, color: "bg-green-500" },
              { label: "Yayasan/Lainnya", count: 4, pct: 8, color: "bg-orange-500" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{item.label}</span>
                  <span className="text-[var(--text-secondary)]">{item.count} ({item.pct}%)</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100">
                  <div className={`h-2 rounded-full ${item.color}`} style={{ width: `${item.pct}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 pt-4 border-t border-[var(--border)]">
            <div>
              <div className="text-sm text-[var(--text-secondary)]">PKP</div>
              <div className="text-xl font-bold">23</div>
            </div>
            <div>
              <div className="text-sm text-[var(--text-secondary)]">Non-PKP</div>
              <div className="text-xl font-bold">24</div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Clients */}
      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="border-b border-[var(--border)] px-6 py-4">
          <h2 className="font-bold">Klien Teratas (by Revenue)</h2>
        </div>
        <div className="divide-y divide-[var(--border)]">
          {topClients.map((c, i) => (
            <div key={c.name} className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-4">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--primary)] text-white text-sm font-bold">
                  {i + 1}
                </span>
                <div>
                  <div className="font-medium">{c.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{c.obligations} kewajiban pajak</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-sm font-medium">{formatRp(c.revenue)}/bln</div>
                </div>
                <div className={`rounded-full px-3 py-1 text-xs font-medium ${
                  c.compliance === 100 ? "bg-green-100 text-green-800" :
                  c.compliance >= 80 ? "bg-yellow-100 text-yellow-800" :
                  "bg-red-100 text-red-800"
                }`}>
                  {c.compliance}% compliant
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
