"use client";

import { useState } from "react";

type FilterStatus = "all" | "overdue" | "due_soon" | "upcoming";

const mockDeadlines = [
  { client: "PT Maju Bersama", type: "SPT Masa PPN", period: "02/2026", date: "2026-03-31", days: -2, status: "overdue", penalty: 500000 },
  { client: "CV Sinar Abadi", type: "SPT Masa PPh 21", period: "02/2026", date: "2026-03-20", days: -7, status: "overdue", penalty: 100000 },
  { client: "PT Karya Digital", type: "SPT Masa PPh 4(2)", period: "02/2026", date: "2026-03-20", days: -7, status: "overdue", penalty: 100000 },
  { client: "Budi Santoso", type: "SPT Tahunan OP", period: "2025", date: "2026-03-31", days: 6, status: "due_soon", penalty: 100000 },
  { client: "Dewi Lestari", type: "SPT Tahunan OP", period: "2025", date: "2026-03-31", days: 6, status: "due_soon", penalty: 100000 },
  { client: "PT Maju Bersama", type: "SPT Masa PPh 21", period: "03/2026", date: "2026-04-20", days: 26, status: "upcoming", penalty: 100000 },
  { client: "PT Maju Bersama", type: "SPT Masa PPh 23", period: "03/2026", date: "2026-04-20", days: 26, status: "upcoming", penalty: 100000 },
  { client: "CV Sinar Abadi", type: "SPT Masa PPN", period: "03/2026", date: "2026-04-30", days: 36, status: "upcoming", penalty: 500000 },
  { client: "PT Karya Digital", type: "SPT Tahunan Badan", period: "2025", date: "2026-04-30", days: 36, status: "upcoming", penalty: 1000000 },
];

function formatRp(n: number) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
}

export default function DeadlinePage() {
  const [filter, setFilter] = useState<FilterStatus>("all");

  const filtered = filter === "all" ? mockDeadlines : mockDeadlines.filter((d) => d.status === filter);
  const overdue = mockDeadlines.filter((d) => d.status === "overdue");
  const dueSoon = mockDeadlines.filter((d) => d.status === "due_soon");
  const totalPenaltyRisk = overdue.reduce((sum, d) => sum + d.penalty, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold">Deadline Pajak</h1>

      {/* Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border-2 border-red-200 bg-red-50 p-5">
          <div className="text-sm font-medium text-red-800">Terlambat</div>
          <div className="mt-1 text-3xl font-extrabold text-red-900">{overdue.length}</div>
          <div className="mt-1 text-xs text-red-700">Potensi denda: {formatRp(totalPenaltyRisk)}</div>
        </div>
        <div className="rounded-xl border-2 border-yellow-200 bg-yellow-50 p-5">
          <div className="text-sm font-medium text-yellow-800">Segera (7 hari)</div>
          <div className="mt-1 text-3xl font-extrabold text-yellow-900">{dueSoon.length}</div>
        </div>
        <div className="rounded-xl border-2 border-green-200 bg-green-50 p-5">
          <div className="text-sm font-medium text-green-800">Akan Datang</div>
          <div className="mt-1 text-3xl font-extrabold text-green-900">
            {mockDeadlines.filter((d) => d.status === "upcoming").length}
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {[
          { key: "all", label: "Semua" },
          { key: "overdue", label: "🔴 Terlambat" },
          { key: "due_soon", label: "🟡 Segera" },
          { key: "upcoming", label: "🟢 Akan Datang" },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key as FilterStatus)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === key
                ? "bg-[var(--primary)] text-white"
                : "bg-white border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Deadline List */}
      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="divide-y divide-[var(--border)]">
          {filtered.map((d, i) => (
            <div key={i} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center gap-4">
                <span className={`h-3 w-3 rounded-full ${
                  d.status === "overdue" ? "bg-red-500" :
                  d.status === "due_soon" ? "bg-yellow-500" : "bg-green-500"
                }`} />
                <div>
                  <div className="font-medium">{d.client}</div>
                  <div className="text-sm text-[var(--text-secondary)]">
                    {d.type} — Masa {d.period}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-sm font-medium">{d.date}</div>
                  <div className={`text-xs ${
                    d.status === "overdue" ? "text-red-600 font-semibold" :
                    d.status === "due_soon" ? "text-yellow-700" : "text-green-700"
                  }`}>
                    {d.days < 0 ? `${Math.abs(d.days)} hari terlambat` : `${d.days} hari lagi`}
                  </div>
                </div>
                {d.status === "overdue" && (
                  <span className="rounded bg-red-100 px-2 py-1 text-xs font-medium text-red-800">
                    Denda {formatRp(d.penalty)}
                  </span>
                )}
                <button className="rounded border border-[var(--border)] px-3 py-1.5 text-xs font-medium hover:bg-gray-50">
                  💬 Ingatkan
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
