"use client";

import { useState, useRef } from "react";

interface BatchItem {
  name: string;
  status: "pending" | "processing" | "success" | "failed";
  type: string;
  client: string;
  anomalies: number;
  extracted?: { bruto: number; pph: number };
}

export default function BatchPage() {
  const [items, setItems] = useState<BatchItem[]>([]);
  const [processing, setProcessing] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const newItems: BatchItem[] = Array.from(files).map((f) => ({
      name: f.name,
      status: "pending" as const,
      type: "Bukti Potong",
      client: f.name.split("_")[0] || "Unknown",
      anomalies: 0,
    }));
    setItems((prev) => [...prev, ...newItems]);
  };

  const processAll = () => {
    setProcessing(true);
    // Simulate batch processing
    setItems((prev) =>
      prev.map((item) =>
        item.status === "pending" ? { ...item, status: "processing" as const } : item
      )
    );

    setTimeout(() => {
      setItems((prev) =>
        prev.map((item) => {
          if (item.status === "processing") {
            const success = Math.random() > 0.1;
            return {
              ...item,
              status: success ? "success" as const : "failed" as const,
              anomalies: success ? Math.floor(Math.random() * 3) : 0,
              extracted: success
                ? { bruto: Math.floor(Math.random() * 200_000_000) + 50_000_000, pph: Math.floor(Math.random() * 20_000_000) }
                : undefined,
            };
          }
          return item;
        })
      );
      setProcessing(false);
    }, 3000);
  };

  const success = items.filter((i) => i.status === "success").length;
  const failed = items.filter((i) => i.status === "failed").length;
  const totalAnomalies = items.reduce((sum, i) => sum + i.anomalies, 0);

  function formatRp(n: number) {
    return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(n);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold">Batch Processing</h1>
          <p className="text-sm text-[var(--text-secondary)]">Upload dan proses puluhan dokumen sekaligus</p>
        </div>
        {items.length > 0 && items.some((i) => i.status === "pending") && (
          <button
            onClick={processAll}
            disabled={processing}
            className="rounded-lg bg-[var(--primary)] px-6 py-2.5 text-sm font-bold text-white hover:bg-[var(--primary-dark)] disabled:opacity-50"
          >
            {processing ? "Memproses..." : `⚡ Proses ${items.filter((i) => i.status === "pending").length} Dokumen`}
          </button>
        )}
      </div>

      {/* Upload Zone */}
      <div
        className="rounded-2xl border-2 border-dashed border-[var(--border)] bg-white p-12 text-center hover:border-[var(--primary)] transition-colors cursor-pointer"
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          multiple
          accept="image/*,.pdf"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="mb-3 text-5xl">📦</div>
        <h3 className="mb-2 text-lg font-bold">Drag & Drop atau Klik untuk Upload</h3>
        <p className="text-sm text-[var(--text-secondary)]">
          Upload foto bukti potong, faktur pajak, atau dokumen lainnya<br/>
          Mendukung JPG, PNG, PDF — hingga 200 file sekaligus
        </p>
      </div>

      {/* Results Summary */}
      {items.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="rounded-lg border border-[var(--border)] bg-white p-4 text-center">
            <div className="text-2xl font-extrabold">{items.length}</div>
            <div className="text-xs text-[var(--text-secondary)]">Total</div>
          </div>
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-center">
            <div className="text-2xl font-extrabold text-green-800">{success}</div>
            <div className="text-xs text-green-700">Berhasil</div>
          </div>
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
            <div className="text-2xl font-extrabold text-red-800">{failed}</div>
            <div className="text-xs text-red-700">Gagal</div>
          </div>
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-center">
            <div className="text-2xl font-extrabold text-yellow-800">{totalAnomalies}</div>
            <div className="text-xs text-yellow-700">Anomali</div>
          </div>
        </div>
      )}

      {/* Item List */}
      {items.length > 0 && (
        <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--border)] bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Dokumen</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Jenis</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Status</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-secondary)]">Bruto</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-secondary)]">PPh</th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Anomali</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {items.map((item, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm font-medium">{item.name}</td>
                  <td className="px-6 py-3 text-sm text-[var(--text-secondary)]">{item.type}</td>
                  <td className="px-6 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.status === "success" ? "bg-green-100 text-green-800" :
                      item.status === "failed" ? "bg-red-100 text-red-800" :
                      item.status === "processing" ? "bg-blue-100 text-blue-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {item.status === "success" ? "Berhasil" :
                       item.status === "failed" ? "Gagal" :
                       item.status === "processing" ? "Memproses..." : "Menunggu"}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right text-sm">
                    {item.extracted ? formatRp(item.extracted.bruto) : "—"}
                  </td>
                  <td className="px-6 py-3 text-right text-sm">
                    {item.extracted ? formatRp(item.extracted.pph) : "—"}
                  </td>
                  <td className="px-6 py-3 text-center">
                    {item.anomalies > 0 ? (
                      <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                        {item.anomalies} ⚠️
                      </span>
                    ) : item.status === "success" ? (
                      <span className="text-xs text-green-600">✓</span>
                    ) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Batch SPT Generation */}
      {success > 0 && (
        <div className="rounded-xl border border-[var(--accent)] bg-emerald-50 p-6 text-center">
          <h3 className="mb-2 text-lg font-bold text-emerald-900">
            {success} dokumen berhasil diekstrak
          </h3>
          <p className="mb-4 text-sm text-emerald-700">
            Siap untuk generate SPT secara batch?
          </p>
          <button className="rounded-lg bg-[var(--accent)] px-6 py-3 font-bold text-white hover:bg-emerald-700">
            Generate {success} SPT Sekaligus
          </button>
        </div>
      )}
    </div>
  );
}
