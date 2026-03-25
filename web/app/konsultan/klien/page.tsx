"use client";

import { useState } from "react";

interface ClientData {
  id: string;
  name: string;
  npwp: string;
  entity_type: string;
  phone: string;
  is_pkp: boolean;
  status: string;
  obligations: string[];
  fee_monthly: number;
}

const mockClients: ClientData[] = [
  { id: "1", name: "PT Maju Bersama", npwp: "01.234.567.8-901.000", entity_type: "PT", phone: "628123456789", is_pkp: true, status: "active", obligations: ["spt_masa_ppn", "spt_masa_pph21", "spt_masa_pph23", "spt_tahunan_badan"], fee_monthly: 2_500_000 },
  { id: "2", name: "CV Sinar Abadi", npwp: "02.345.678.9-012.000", entity_type: "CV", phone: "628234567890", is_pkp: true, status: "active", obligations: ["spt_masa_ppn", "spt_masa_pph21", "spt_tahunan_badan"], fee_monthly: 1_500_000 },
  { id: "3", name: "Budi Santoso", npwp: "03.456.789.0-123.000", entity_type: "Orang Pribadi", phone: "628345678901", is_pkp: false, status: "active", obligations: ["spt_tahunan_op"], fee_monthly: 0 },
  { id: "4", name: "Dewi Lestari", npwp: "04.567.890.1-234.000", entity_type: "Orang Pribadi", phone: "628456789012", is_pkp: false, status: "active", obligations: ["spt_tahunan_op"], fee_monthly: 0 },
  { id: "5", name: "PT Karya Digital", npwp: "05.678.901.2-345.000", entity_type: "PT", phone: "628567890123", is_pkp: true, status: "active", obligations: ["spt_masa_ppn", "spt_masa_pph21", "spt_masa_pph23", "spt_masa_pph4_2", "spt_tahunan_badan"], fee_monthly: 3_000_000 },
];

function formatRp(n: number) {
  return n > 0 ? new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n) : "—";
}

export default function ClientsPage() {
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);

  const filtered = mockClients.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.npwp.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold">Klien</h1>
          <p className="text-sm text-[var(--text-secondary)]">{mockClients.length} klien terdaftar</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
        >
          + Tambah Klien
        </button>
      </div>

      {/* Search */}
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Cari nama atau NPWP..."
        className="w-full rounded-lg border border-[var(--border)] px-4 py-3 focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
      />

      {/* Add Client Form */}
      {showForm && (
        <div className="rounded-xl border border-[var(--primary)] bg-blue-50 p-6">
          <h3 className="mb-4 font-bold">Klien Baru</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <input placeholder="Nama *" className="rounded-lg border border-[var(--border)] px-4 py-2" />
            <input placeholder="NPWP" className="rounded-lg border border-[var(--border)] px-4 py-2" />
            <input placeholder="No. HP / WhatsApp" className="rounded-lg border border-[var(--border)] px-4 py-2" />
            <select className="rounded-lg border border-[var(--border)] px-4 py-2">
              <option>Orang Pribadi</option>
              <option>PT</option>
              <option>CV</option>
              <option>Yayasan</option>
            </select>
            <input placeholder="Fee Bulanan (Rp)" type="number" className="rounded-lg border border-[var(--border)] px-4 py-2" />
            <div className="flex items-center gap-2">
              <input type="checkbox" id="pkp" />
              <label htmlFor="pkp" className="text-sm">PKP (Pengusaha Kena Pajak)</label>
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">Simpan</button>
            <button onClick={() => setShowForm(false)} className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm">Batal</button>
          </div>
        </div>
      )}

      {/* Client List */}
      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--border)] bg-gray-50">
              <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Klien</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">NPWP</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Jenis</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Kewajiban</th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-secondary)]">Fee/Bulan</th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {filtered.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="font-medium">{c.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{c.phone}</div>
                </td>
                <td className="px-6 py-4 text-sm font-mono">{c.npwp}</td>
                <td className="px-6 py-4">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    c.is_pkp ? "bg-purple-100 text-purple-800" : "bg-gray-100 text-gray-800"
                  }`}>
                    {c.entity_type} {c.is_pkp ? "(PKP)" : ""}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {c.obligations.map((o) => (
                      <span key={o} className="rounded bg-blue-50 px-1.5 py-0.5 text-xs text-[var(--primary)]">
                        {o.replace("spt_", "").replace("_", " ").toUpperCase()}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-4 text-right text-sm font-medium">{formatRp(c.fee_monthly)}</td>
                <td className="px-6 py-4 text-center">
                  <button className="rounded border border-[var(--border)] px-3 py-1 text-xs hover:bg-gray-50">
                    💬 Request Docs
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
