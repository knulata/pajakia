"use client";

import { useState, useCallback } from "react";

interface ChecklistItem { doc_type: string; label: string; uploaded: boolean; }

const mockPortalData = {
  client_name: "Budi Santoso", tax_year: 2025,
  checklist: [
    { doc_type: "bukti_potong_1721_a1", label: "Bukti Potong 1721-A1 (Karyawan Swasta)", uploaded: false },
    { doc_type: "bukti_potong_pph23", label: "Bukti Potong PPh 23", uploaded: true },
    { doc_type: "financial_statement", label: "Laporan Keuangan", uploaded: false },
  ] as ChecklistItem[],
  consents_granted: ["data_access"],
  expires_at: "2026-04-25T00:00:00Z",
};

const consentLabels: Record<string, { label: string; desc: string }> = {
  data_access: { label: "Akses Data Pajak", desc: "Konsultan dapat melihat data pajak Anda" },
  document_processing: { label: "Proses Dokumen", desc: "Dokumen akan diproses melalui OCR AI" },
  spt_filing: { label: "Pelaporan SPT", desc: "Konsultan melaporkan SPT atas nama Anda" },
  whatsapp_communication: { label: "Komunikasi WhatsApp", desc: "Konsultan menghubungi via WhatsApp" },
};

export default function ClientPortalPage() {
  const [data] = useState(mockPortalData);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [consents, setConsents] = useState<string[]>(data.consents_granted);

  const handleUpload = useCallback(async (docType: string) => {
    setUploading(true);
    await new Promise((r) => setTimeout(r, 1500));
    setUploading(false);
    setUploadSuccess(docType);
    setTimeout(() => setUploadSuccess(null), 3000);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-2xl px-4 py-8">
        <div className="mb-8 text-center"><h1 className="text-3xl font-extrabold text-[var(--primary)]">Pajakia</h1><p className="mt-2 text-[var(--text-secondary)]">Portal Upload Dokumen</p></div>
        <div className="rounded-xl bg-white p-6 shadow-sm border border-[var(--border)]">
          <h2 className="text-xl font-bold">Halo, {data.client_name}</h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Konsultan pajak Anda membutuhkan dokumen berikut untuk SPT Tahun {data.tax_year}.</p>
          <p className="mt-2 text-xs text-[var(--text-secondary)]">Link berlaku sampai: {new Date(data.expires_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}</p>
        </div>
        <div className="mt-6 rounded-xl bg-white shadow-sm border border-[var(--border)]">
          <div className="border-b border-[var(--border)] px-6 py-4"><h3 className="font-bold">Dokumen yang Dibutuhkan</h3><p className="text-xs text-[var(--text-secondary)]">{data.checklist.filter((c) => c.uploaded).length} dari {data.checklist.length} sudah diupload</p></div>
          <div className="divide-y divide-[var(--border)]">
            {data.checklist.map((item) => (
              <div key={item.doc_type} className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className={`text-xl ${item.uploaded || uploadSuccess === item.doc_type ? "" : "opacity-30"}`}>{item.uploaded || uploadSuccess === item.doc_type ? "✅" : "📄"}</span>
                  <div><div className="text-sm font-medium">{item.label}</div>{item.uploaded && <div className="text-xs text-green-600">Sudah diupload</div>}{uploadSuccess === item.doc_type && <div className="text-xs text-green-600">Upload berhasil!</div>}</div>
                </div>
                {!item.uploaded && uploadSuccess !== item.doc_type && (
                  <label className="cursor-pointer rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">
                    {uploading ? "Uploading..." : "Upload"}
                    <input type="file" className="hidden" accept="image/jpeg,image/png,application/pdf" disabled={uploading} onChange={(e) => { if (e.target.files?.[0]) handleUpload(item.doc_type); }} />
                  </label>
                )}
              </div>
            ))}
          </div>
        </div>
        <div className="mt-6 rounded-xl bg-white shadow-sm border border-[var(--border)]">
          <div className="border-b border-[var(--border)] px-6 py-4"><h3 className="font-bold">Persetujuan</h3><p className="text-xs text-[var(--text-secondary)]">Berikan persetujuan untuk memproses data pajak Anda</p></div>
          <div className="p-6 space-y-3">
            {Object.entries(consentLabels).map(([key, { label, desc }]) => (
              <label key={key} className="flex items-start gap-3 cursor-pointer">
                <input type="checkbox" checked={consents.includes(key)} onChange={(e) => { if (e.target.checked) setConsents((p) => [...p, key]); else setConsents((p) => p.filter((c) => c !== key)); }} className="mt-1 h-4 w-4 rounded border-gray-300" />
                <div><div className="text-sm font-medium">{label}</div><div className="text-xs text-[var(--text-secondary)]">{desc}</div></div>
              </label>
            ))}
            <button className="mt-4 rounded-lg bg-[var(--primary)] px-6 py-2.5 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">Simpan Persetujuan</button>
          </div>
        </div>
        <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center"><div className="text-sm text-blue-800"><strong>Data Anda aman.</strong> Dokumen dienkripsi dan disimpan di server Indonesia. Hanya konsultan Anda yang dapat mengakses data ini.</div></div>
      </div>
    </div>
  );
}
