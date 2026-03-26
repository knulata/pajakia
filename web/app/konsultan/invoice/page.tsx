"use client";

import { useState } from "react";

interface InvoiceData { id: string; invoice_number: string; client_name: string; total: number; status: string; due_date: string | null; paid_at: string | null; }

const mockInvoices: InvoiceData[] = [
  { id: "i1", invoice_number: "INV-202603-0001", client_name: "PT Maju Bersama", total: 2775000, status: "sent", due_date: "2026-04-15", paid_at: null },
  { id: "i2", invoice_number: "INV-202603-0002", client_name: "CV Sinar Abadi", total: 1665000, status: "paid", due_date: "2026-04-15", paid_at: "2026-03-10" },
  { id: "i3", invoice_number: "INV-202603-0003", client_name: "PT Karya Digital", total: 3330000, status: "overdue", due_date: "2026-03-15", paid_at: null },
  { id: "i4", invoice_number: "INV-202602-0004", client_name: "Budi Santoso", total: 500000, status: "paid", due_date: "2026-03-15", paid_at: "2026-03-05" },
];

function formatRp(n: number) { return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n); }

function statusBadge(s: string) {
  const styles: Record<string, string> = { draft: "bg-gray-100 text-gray-800", sent: "bg-blue-100 text-blue-800", paid: "bg-green-100 text-green-800", overdue: "bg-red-100 text-red-800", cancelled: "bg-gray-100 text-gray-500" };
  const labels: Record<string, string> = { draft: "Draft", sent: "Terkirim", paid: "Lunas", overdue: "Terlambat", cancelled: "Batal" };
  return <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${styles[s] || styles.draft}`}>{labels[s] || s}</span>;
}

export default function InvoicePage() {
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState("");
  const filtered = filter ? mockInvoices.filter((i) => i.status === filter) : mockInvoices;
  const totalUnpaid = mockInvoices.filter((i) => i.status === "sent" || i.status === "overdue").reduce((sum, i) => sum + i.total, 0);
  const totalPaid = mockInvoices.filter((i) => i.status === "paid").reduce((sum, i) => sum + i.total, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-extrabold">Invoice</h1><p className="text-sm text-[var(--text-secondary)]">Kelola tagihan dan pembayaran klien</p></div>
        <button onClick={() => setShowCreate(!showCreate)} className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">+ Buat Invoice</button>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-[var(--border)] bg-white p-5"><div className="text-sm text-[var(--text-secondary)]">Belum Dibayar</div><div className="mt-1 text-2xl font-extrabold text-orange-600">{formatRp(totalUnpaid)}</div></div>
        <div className="rounded-xl border border-[var(--border)] bg-white p-5"><div className="text-sm text-[var(--text-secondary)]">Sudah Dibayar</div><div className="mt-1 text-2xl font-extrabold text-green-600">{formatRp(totalPaid)}</div></div>
        <div className="rounded-xl border border-[var(--border)] bg-white p-5"><div className="text-sm text-[var(--text-secondary)]">Total Invoice</div><div className="mt-1 text-2xl font-extrabold">{mockInvoices.length}</div></div>
      </div>
      <div className="flex gap-2">
        {["", "sent", "paid", "overdue", "draft"].map((f) => (
          <button key={f} onClick={() => setFilter(f)} className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${filter === f ? "bg-[var(--primary)] text-white" : "border border-[var(--border)] text-[var(--text-secondary)] hover:bg-gray-50"}`}>
            {f === "" ? "Semua" : f === "sent" ? "Terkirim" : f === "paid" ? "Lunas" : f === "overdue" ? "Terlambat" : "Draft"}
          </button>
        ))}
      </div>
      {showCreate && (
        <div className="rounded-xl border border-[var(--primary)] bg-blue-50 p-6">
          <h3 className="mb-4 font-bold">Invoice Baru</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <select className="rounded-lg border border-[var(--border)] px-4 py-2"><option>Pilih Klien...</option><option>PT Maju Bersama</option><option>CV Sinar Abadi</option></select>
            <input type="date" className="rounded-lg border border-[var(--border)] px-4 py-2" />
          </div>
          <div className="mt-4 space-y-2">
            <div className="text-sm font-medium">Item</div>
            <div className="grid grid-cols-[1fr_80px_120px] gap-2">
              <input placeholder="Deskripsi" className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm" />
              <input placeholder="Qty" type="number" defaultValue={1} className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm" />
              <input placeholder="Harga" type="number" className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm" />
            </div>
            <button className="text-sm text-[var(--primary)] hover:underline">+ Tambah Item</button>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">Buat & Kirim</button>
            <button onClick={() => setShowCreate(false)} className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm">Batal</button>
          </div>
        </div>
      )}
      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm overflow-hidden">
        <table className="w-full">
          <thead><tr className="border-b border-[var(--border)] bg-gray-50">
            <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">No. Invoice</th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Klien</th>
            <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-secondary)]">Total</th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Status</th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Jatuh Tempo</th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Aksi</th>
          </tr></thead>
          <tbody className="divide-y divide-[var(--border)]">
            {filtered.map((inv) => (
              <tr key={inv.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-mono">{inv.invoice_number}</td>
                <td className="px-6 py-4 text-sm font-medium">{inv.client_name}</td>
                <td className="px-6 py-4 text-right text-sm font-medium">{formatRp(inv.total)}</td>
                <td className="px-6 py-4 text-center">{statusBadge(inv.status)}</td>
                <td className="px-6 py-4 text-sm">{inv.due_date ? new Date(inv.due_date).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" }) : "—"}</td>
                <td className="px-6 py-4 text-center">
                  <div className="flex justify-center gap-1">
                    {inv.status === "sent" && <button className="rounded border border-green-300 px-2 py-1 text-xs text-green-700 hover:bg-green-50">Tandai Lunas</button>}
                    <button className="rounded border border-[var(--border)] px-2 py-1 text-xs hover:bg-gray-50">Detail</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
