"use client";

import Link from "next/link";

const mockStats = {
  active_clients: 47,
  monthly_revenue: 52_500_000,
  overdue: 3,
  due_soon: 8,
  docs_processed_month: 156,
  spt_filed_month: 12,
};

const urgentDeadlines = [
  { client: "PT Maju Bersama", type: "SPT Masa PPN", date: "25 Mar 2026", days: -2, status: "overdue" },
  { client: "CV Sinar Abadi", type: "SPT Masa PPh 21", date: "20 Mar 2026", days: -7, status: "overdue" },
  { client: "Budi Santoso", type: "SPT Tahunan OP", date: "31 Mar 2026", days: 6, status: "due_soon" },
  { client: "PT Karya Digital", type: "SPT Masa PPh 23", date: "20 Apr 2026", days: 26, status: "upcoming" },
];

const recentActivity = [
  { icon: "📄", text: "Bukti potong Andi Wijaya berhasil diekstrak", time: "5 menit lalu" },
  { icon: "✅", text: "SPT 1770S Dewi Lestari selesai di-generate", time: "1 jam lalu" },
  { icon: "⚠️", text: "Anomali terdeteksi: PPh 21 PT Maju Bersama", time: "2 jam lalu" },
  { icon: "💬", text: "Dokumen diterima via WhatsApp dari CV Sinar Abadi", time: "3 jam lalu" },
  { icon: "📊", text: "e-Faktur batch 23 transaksi berhasil di-generate", time: "Kemarin" },
];

function formatRp(n: number) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
}

export default function ConsultantDashboard() {
  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Klien Aktif", value: mockStats.active_clients.toString(), icon: "👥", color: "blue" },
          { label: "Pendapatan Bulanan", value: formatRp(mockStats.monthly_revenue), icon: "💰", color: "green" },
          { label: "Overdue", value: mockStats.overdue.toString(), icon: "🔴", color: "red" },
          { label: "Segera Jatuh Tempo", value: mockStats.due_soon.toString(), icon: "🟡", color: "yellow" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-[var(--text-secondary)]">{s.label}</div>
                <div className="mt-1 text-2xl font-extrabold">{s.value}</div>
              </div>
              <span className="text-3xl">{s.icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Urgent Deadlines */}
        <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
            <h2 className="font-bold">Deadline Mendesak</h2>
            <Link href="/konsultan/deadline" className="text-sm font-medium text-[var(--primary)] hover:underline">
              Lihat Semua →
            </Link>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {urgentDeadlines.map((d, i) => (
              <div key={i} className="flex items-center justify-between px-6 py-3">
                <div>
                  <div className="font-medium text-sm">{d.client}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{d.type}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm">{d.date}</div>
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                    d.status === "overdue" ? "bg-red-100 text-red-800" :
                    d.status === "due_soon" ? "bg-yellow-100 text-yellow-800" :
                    "bg-green-100 text-green-800"
                  }`}>
                    {d.status === "overdue" ? `${Math.abs(d.days)} hari terlambat` :
                     `${d.days} hari lagi`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
          <div className="border-b border-[var(--border)] px-6 py-4">
            <h2 className="font-bold">Aktivitas Terbaru</h2>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {recentActivity.map((a, i) => (
              <div key={i} className="flex items-start gap-3 px-6 py-3">
                <span className="mt-0.5 text-lg">{a.icon}</span>
                <div className="flex-1">
                  <div className="text-sm">{a.text}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{a.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Link href="/konsultan/batch" className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm hover:shadow-md transition-shadow text-center">
          <div className="mb-2 text-3xl">⚡</div>
          <h3 className="font-bold">Batch Upload</h3>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Upload 50+ bukti potong sekaligus</p>
        </Link>
        <Link href="/konsultan/klien" className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm hover:shadow-md transition-shadow text-center">
          <div className="mb-2 text-3xl">➕</div>
          <h3 className="font-bold">Tambah Klien</h3>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Onboard klien baru</p>
        </Link>
        <Link href="/kalkulator" className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm hover:shadow-md transition-shadow text-center">
          <div className="mb-2 text-3xl">🧮</div>
          <h3 className="font-bold">Kalkulator Cepat</h3>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Hitung PPh 21 untuk klien</p>
        </Link>
      </div>
    </div>
  );
}
