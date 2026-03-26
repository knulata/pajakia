"use client";

import { useState } from "react";

const STATUSES = [
  { key: "draft", label: "Draft", color: "bg-gray-100" },
  { key: "data_collection", label: "Kumpul Data", color: "bg-blue-50" },
  { key: "ai_processing", label: "Proses AI", color: "bg-purple-50" },
  { key: "review", label: "Review", color: "bg-yellow-50" },
  { key: "approved", label: "Disetujui", color: "bg-green-50" },
  { key: "filed", label: "Dilaporkan", color: "bg-emerald-50" },
];

interface Filing {
  id: string;
  client_name: string;
  filing_type: string;
  tax_year: number;
  tax_month: number | null;
  deadline: string | null;
  tax_due: number | null;
}

const mockColumns: Record<string, Filing[]> = {
  draft: [
    { id: "1", client_name: "PT Maju Bersama", filing_type: "spt_masa_ppn", tax_year: 2026, tax_month: 2, deadline: "2026-03-31", tax_due: 15_000_000 },
    { id: "2", client_name: "Budi Santoso", filing_type: "spt_1770ss", tax_year: 2025, tax_month: null, deadline: "2026-03-31", tax_due: 2_500_000 },
  ],
  data_collection: [
    { id: "3", client_name: "CV Sinar Abadi", filing_type: "spt_masa_pph21", tax_year: 2026, tax_month: 2, deadline: "2026-03-20", tax_due: 8_000_000 },
  ],
  ai_processing: [
    { id: "4", client_name: "Dewi Lestari", filing_type: "spt_1770s", tax_year: 2025, tax_month: null, deadline: "2026-03-31", tax_due: null },
  ],
  review: [
    { id: "5", client_name: "PT Karya Digital", filing_type: "spt_masa_ppn", tax_year: 2026, tax_month: 2, deadline: "2026-03-31", tax_due: 22_000_000 },
    { id: "6", client_name: "PT Karya Digital", filing_type: "spt_masa_pph21", tax_year: 2026, tax_month: 2, deadline: "2026-03-20", tax_due: 12_000_000 },
  ],
  approved: [],
  filed: [
    { id: "7", client_name: "Andi Wijaya", filing_type: "spt_1770ss", tax_year: 2025, tax_month: null, deadline: "2026-03-31", tax_due: 0 },
  ],
};

function formatRp(n: number | null) {
  if (n === null) return "—";
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
}

function filingLabel(type: string) {
  return type.replace("spt_", "SPT ").replace("masa_", "Masa ").replace("1770ss", "1770SS").replace("1770s", "1770S").toUpperCase();
}

export default function FilingBoardPage() {
  const [year, setYear] = useState(2025);
  const [columns] = useState(mockColumns);
  const [dragItem, setDragItem] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold">Filing Board</h1>
          <p className="text-sm text-[var(--text-secondary)]">Drag & drop filing ke status berikutnya</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">Tahun:</label>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm">
            <option value={2025}>2025</option>
            <option value={2026}>2026</option>
          </select>
        </div>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4">
        {STATUSES.map((status) => {
          const items = columns[status.key] || [];
          return (
            <div key={status.key} className={`min-w-[280px] flex-shrink-0 rounded-xl border border-[var(--border)] ${status.color}`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => { if (dragItem) setDragItem(null); }}>
              <div className="border-b border-[var(--border)] px-4 py-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold">{status.label}</h3>
                  <span className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold shadow-sm">{items.length}</span>
                </div>
              </div>
              <div className="space-y-2 p-3">
                {items.map((filing) => (
                  <div key={filing.id} draggable onDragStart={() => setDragItem(filing.id)}
                    className="cursor-grab rounded-lg border border-[var(--border)] bg-white p-3 shadow-sm hover:shadow-md transition-shadow active:cursor-grabbing">
                    <div className="font-medium text-sm">{filing.client_name}</div>
                    <div className="mt-1 text-xs text-[var(--text-secondary)]">{filingLabel(filing.filing_type)}</div>
                    {filing.tax_month && <div className="mt-0.5 text-xs text-[var(--text-secondary)]">Masa {filing.tax_month}/{filing.tax_year}</div>}
                    <div className="mt-2 flex items-center justify-between">
                      {filing.deadline && <span className="text-xs text-[var(--text-secondary)]">{new Date(filing.deadline).toLocaleDateString("id-ID", { day: "numeric", month: "short" })}</span>}
                      <span className="text-xs font-medium">{formatRp(filing.tax_due)}</span>
                    </div>
                  </div>
                ))}
                {items.length === 0 && <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">Kosong</div>}
              </div>
            </div>
          );
        })}
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-white p-4 shadow-sm">
        <h3 className="mb-3 font-bold text-sm">Aksi Batch</h3>
        <div className="flex flex-wrap gap-2">
          <button className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm hover:bg-gray-50">Approve Semua yang Review</button>
          <button className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm hover:bg-gray-50">Generate SPT Semua yang Approved</button>
          <button className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm hover:bg-gray-50">Export Semua yang Filed ke CSV</button>
        </div>
      </div>
    </div>
  );
}
