"use client";

import { useState } from "react";

interface PendingDocument {
  id: string;
  doc_type: string;
  file_name: string;
  ocr_confidence: number;
  extracted_data: Record<string, unknown>;
  low_confidence_fields: string[];
  is_verified: boolean;
}

const mockDocs: PendingDocument[] = [
  {
    id: "d1", doc_type: "bukti_potong_1721_a1", file_name: "bp_andi_2025.jpg",
    ocr_confidence: 0.92, extracted_data: { nama_wp: "Andi Wijaya", npwp: "01.234.567.8-901.000", penghasilan_bruto: 180000000, pph_dipotong: 7200000, masa_pajak: "Januari - Desember 2025", nama_pemotong: "PT Maju Bersama" },
    low_confidence_fields: ["npwp"], is_verified: false,
  },
  {
    id: "d2", doc_type: "faktur_pajak", file_name: "faktur_020.pdf",
    ocr_confidence: 0.78, extracted_data: { nomor_faktur: "020-24.12345678", npwp_penjual: "02.345.678.9-012.000", nama_penjual: "CV Sinar Abadi", dpp: 50000000, ppn: 5500000, tanggal: "2026-02-15" },
    low_confidence_fields: ["npwp_penjual", "dpp", "ppn"], is_verified: false,
  },
];

function confidenceColor(conf: number) {
  if (conf >= 0.95) return "text-green-600 bg-green-50";
  if (conf >= 0.8) return "text-yellow-600 bg-yellow-50";
  return "text-red-600 bg-red-50";
}

function docTypeLabel(type: string) {
  const labels: Record<string, string> = { bukti_potong_1721_a1: "Bukti Potong 1721-A1", bukti_potong_1721_a2: "Bukti Potong 1721-A2", faktur_pajak: "Faktur Pajak", bukti_potong_pph23: "Bukti Potong PPh 23", invoice: "Invoice", other: "Lainnya" };
  return labels[type] || type;
}

function formatRp(n: unknown) {
  if (typeof n !== "number") return String(n);
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
}

export default function DocumentReviewPage() {
  const [selected, setSelected] = useState<string | null>(null);
  const [editData, setEditData] = useState<Record<string, unknown>>({});
  const selectedDoc = mockDocs.find((d) => d.id === selected);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold">Review Dokumen</h1>
        <p className="text-sm text-[var(--text-secondary)]">Verifikasi hasil OCR sebelum diproses ke SPT</p>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-3">
          {mockDocs.map((doc) => (
            <button key={doc.id} onClick={() => { setSelected(doc.id); setEditData({ ...doc.extracted_data }); }}
              className={`w-full rounded-xl border p-4 text-left transition-colors ${selected === doc.id ? "border-[var(--primary)] bg-blue-50" : "border-[var(--border)] bg-white hover:bg-gray-50"}`}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-medium text-sm">{doc.file_name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{docTypeLabel(doc.doc_type)}</div>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${confidenceColor(doc.ocr_confidence)}`}>{Math.round(doc.ocr_confidence * 100)}%</span>
              </div>
              {doc.low_confidence_fields.length > 0 && (
                <div className="mt-2 flex gap-1">
                  {doc.low_confidence_fields.map((f) => (<span key={f} className="rounded bg-red-50 px-1.5 py-0.5 text-xs text-red-600">{f}</span>))}
                </div>
              )}
            </button>
          ))}
        </div>
        {selectedDoc ? (
          <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
            <div className="border-b border-[var(--border)] px-6 py-4">
              <h3 className="font-bold">Verifikasi: {selectedDoc.file_name}</h3>
              <p className="text-xs text-[var(--text-secondary)]">Perbaiki field yang salah, lalu klik Verifikasi</p>
            </div>
            <div className="p-6 space-y-4">
              {Object.entries(editData).map(([key, value]) => {
                const isLowConf = selectedDoc.low_confidence_fields.includes(key);
                return (
                  <div key={key}>
                    <label className="mb-1 flex items-center gap-2 text-xs font-semibold text-[var(--text-secondary)]">
                      {key.replace(/_/g, " ").toUpperCase()}
                      {isLowConf && <span className="rounded bg-red-100 px-1 py-0.5 text-[10px] text-red-700">LOW CONFIDENCE</span>}
                    </label>
                    <input type={typeof value === "number" ? "number" : "text"} value={typeof value === "number" ? value : String(value || "")}
                      onChange={(e) => setEditData((prev) => ({ ...prev, [key]: typeof value === "number" ? Number(e.target.value) : e.target.value }))}
                      className={`w-full rounded-lg border px-3 py-2 text-sm ${isLowConf ? "border-red-300 bg-red-50 focus:border-red-500" : "border-[var(--border)] focus:border-[var(--primary)]"} focus:outline-none focus:ring-2 focus:ring-blue-100`} />
                    {typeof value === "number" && <div className="mt-0.5 text-xs text-[var(--text-secondary)]">OCR: {formatRp(selectedDoc.extracted_data[key])}</div>}
                  </div>
                );
              })}
            </div>
            <div className="border-t border-[var(--border)] px-6 py-4 flex gap-2">
              <button className="flex-1 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">Verifikasi & Simpan</button>
              <button className="rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm hover:bg-gray-50">Skip</button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center rounded-xl border border-dashed border-gray-300 p-12 text-gray-400">Pilih dokumen untuk review</div>
        )}
      </div>
    </div>
  );
}
