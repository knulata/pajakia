"use client";

import { useState } from "react";

type Tab = "generator" | "validator" | "decoder" | "queue" | "errors";

const KNOWN_ERRORS = [
  { code: "ERR-CT-001", label: "NPWP harus 16 digit", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-002", label: "NPWP dalam notasi ilmiah (bug Excel)", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-003", label: "NIK tidak valid (harus 16 digit)", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-004", label: "Format tanggal salah (harus YYYY-MM-DD)", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-005", label: "Masa pajak harus 01-12", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-006", label: "Tahun pajak invalid", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-007", label: "Kode objek pajak kosong", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-008", label: "Kode objek pajak tidak dikenal", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-009", label: "Nilai pajak tidak boleh negatif", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-010", label: "Nilai harus integer (tanpa desimal)", severity: "warning", auto_fixable: true },
  { code: "ERR-CT-011", label: "Tarif harus 0-100", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-012", label: "PPh dipotong tidak sesuai DPP × Tarif", severity: "warning", auto_fixable: false },
  { code: "ERR-CT-013", label: "Nomor bukti potong duplikat", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-014", label: "Format nomor faktur salah", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-015", label: "NPWP pembeli invalid", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-016", label: "PPN tidak sesuai DPP × 11%", severity: "warning", auto_fixable: true },
  { code: "ERR-CT-017", label: "Karakter terlarang dalam data", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-018", label: "Field wajib kosong", severity: "critical", auto_fixable: false },
  { code: "ERR-CT-019", label: "Encoding harus UTF-8", severity: "critical", auto_fixable: true },
  { code: "ERR-CT-020", label: "File terlalu besar (max 10MB)", severity: "warning", auto_fixable: true },
  { code: "ERR-CT-021", label: "Lebih dari 1000 record per file", severity: "warning", auto_fixable: true },
  { code: "ERR-CT-022", label: "Status PTKP tidak dikenal", severity: "critical", auto_fixable: false },
];

const MOCK_QUEUE = [
  { id: "q1", type: "ebupot", status: "succeeded", masa: 2, tahun: 2026, ref: "BPE-2026-002847", retries: 0, when: "5 menit lalu" },
  { id: "q2", type: "efaktur", status: "retrying", masa: 3, tahun: 2026, ref: null, retries: 2, error: "Coretax maintenance — retry in 30 min", when: "1 jam lalu" },
  { id: "q3", type: "spt_masa_pph21", status: "succeeded", masa: 2, tahun: 2026, ref: "BPE-2026-002831", retries: 0, when: "2 jam lalu" },
  { id: "q4", type: "ebupot", status: "queued", masa: 3, tahun: 2026, ref: null, retries: 0, when: "3 jam lalu" },
  { id: "q5", type: "efaktur", status: "failed", masa: 1, tahun: 2026, ref: null, retries: 8, error: "Max retries exceeded — manual fix needed", when: "Kemarin" },
];

function statusBadge(s: string) {
  const styles: Record<string, string> = {
    queued: "bg-blue-100 text-blue-800",
    uploading: "bg-yellow-100 text-yellow-800",
    retrying: "bg-orange-100 text-orange-800",
    succeeded: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
    cancelled: "bg-gray-100 text-gray-500",
  };
  const labels: Record<string, string> = {
    queued: "Antri",
    uploading: "Upload",
    retrying: "Retry",
    succeeded: "Berhasil",
    failed: "Gagal",
    cancelled: "Batal",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${styles[s] || styles.queued}`}>
      {labels[s] || s}
    </span>
  );
}

export default function CoretaxPage() {
  const [tab, setTab] = useState<Tab>("generator");
  const [errorMsg, setErrorMsg] = useState("");
  const [decoded, setDecoded] = useState<{ title: string; explanation: string; fix: string; severity: string } | null>(null);
  const [genType, setGenType] = useState<"ebupot" | "efaktur" | "spt_masa_pph21">("ebupot");
  const [valResult, setValResult] = useState<{ valid: boolean; errors: number; warnings: number; records: number } | null>(null);

  function handleDecode() {
    if (!errorMsg.trim()) return;
    // Mock — in production this hits POST /coretax/decode-error
    const lower = errorMsg.toLowerCase();
    if (lower.includes("npwp") && (lower.includes("15") || lower.includes("scientific"))) {
      setDecoded({
        title: "NPWP Format Salah",
        explanation: "NPWP 15 digit lama atau ter-convert ke notasi ilmiah oleh Excel.",
        fix: "Pajakia auto-fix saat generate XML. Format NPWP sebagai TEXT di Excel.",
        severity: "critical",
      });
    } else if (lower.includes("forbidden") || lower.includes("character")) {
      setDecoded({
        title: "Karakter Terlarang",
        explanation: "Coretax menolak ', \", <, >, dan soft enter dalam data.",
        fix: "Pajakia auto-clean. Atau hapus karakter manual sebelum upload.",
        severity: "critical",
      });
    } else if (lower.includes("maintenance") || lower.includes("503")) {
      setDecoded({
        title: "Coretax Sedang Maintenance",
        explanation: "Server DJP downtime, biasanya 4-8 jam.",
        fix: "Submission masuk retry queue Pajakia. Auto-retry begitu Coretax up.",
        severity: "warning",
      });
    } else {
      setDecoded({
        title: "Error tidak dikenal",
        explanation: "Pesan error belum di database Pajakia.",
        fix: "Hubungi support dengan screenshot error ini.",
        severity: "warning",
      });
    }
  }

  function handleValidate() {
    // Mock validation result
    setValResult({ valid: false, errors: 3, warnings: 2, records: 47 });
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-extrabold">Coretax Co-Pilot</h1>
          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
            🚀 BARU
          </span>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">
          Generate XML, validasi sebelum upload, decode error, dan auto-retry — semua dalam satu tempat.
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          { label: "Submission Bulan Ini", value: "142", sub: "↑ 23% vs bulan lalu", color: "text-blue-600" },
          { label: "Berhasil", value: "127", sub: "89% success rate", color: "text-green-600" },
          { label: "Auto-Retry", value: "12", sub: "8 berhasil setelah retry", color: "text-orange-600" },
          { label: "Manual Fix", value: "3", sub: "Perlu intervensi", color: "text-red-600" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl border border-[var(--border)] bg-white p-5">
            <div className="text-xs text-[var(--text-secondary)]">{s.label}</div>
            <div className={`mt-1 text-2xl font-extrabold ${s.color}`}>{s.value}</div>
            <div className="mt-1 text-xs text-[var(--text-secondary)]">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-gray-100 p-1 overflow-x-auto">
        {[
          { id: "generator" as Tab, label: "🛠️ Generator XML" },
          { id: "validator" as Tab, label: "✅ Pre-flight Validator" },
          { id: "decoder" as Tab, label: "🔍 Error Decoder" },
          { id: "queue" as Tab, label: "🔁 Retry Queue" },
          { id: "errors" as Tab, label: "📚 22 Error Catalog" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.id ? "bg-white shadow-sm" : "text-[var(--text-secondary)] hover:text-[var(--text)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === "generator" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6">
          <h3 className="mb-1 text-lg font-bold">Generate XML untuk Coretax</h3>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Pajakia auto-format XML sesuai schema Coretax v1.0. NPWP otomatis dipad 16 digit, tanggal di-convert ke ISO,
            karakter terlarang dihapus.
          </p>

          <div className="mb-4 grid gap-3 sm:grid-cols-3">
            {[
              { id: "ebupot" as const, label: "e-Bupot Unifikasi", desc: "PPh 21, 23, 26, 4(2)", icon: "📋" },
              { id: "efaktur" as const, label: "e-Faktur PPN", desc: "Pajak Pertambahan Nilai", icon: "🧾" },
              { id: "spt_masa_pph21" as const, label: "SPT Masa PPh 21", desc: "Pemotongan bulanan", icon: "👥" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setGenType(t.id)}
                className={`rounded-lg border p-4 text-left transition-all ${
                  genType === t.id
                    ? "border-2 border-[var(--primary)] bg-blue-50"
                    : "border-[var(--border)] hover:border-[var(--primary)]"
                }`}
              >
                <div className="mb-2 text-2xl">{t.icon}</div>
                <div className="font-semibold text-sm">{t.label}</div>
                <div className="mt-0.5 text-xs text-[var(--text-secondary)]">{t.desc}</div>
              </button>
            ))}
          </div>

          <div className="rounded-lg bg-gray-50 p-4">
            <div className="mb-2 text-xs font-semibold text-[var(--text-secondary)]">SUMBER DATA</div>
            <div className="grid gap-3 sm:grid-cols-2">
              <button className="rounded-lg border border-[var(--border)] bg-white px-4 py-3 text-left hover:border-[var(--primary)]">
                <div className="font-medium text-sm">📄 Dari dokumen yang sudah diverifikasi</div>
                <div className="text-xs text-[var(--text-secondary)]">47 dokumen siap di-generate</div>
              </button>
              <button className="rounded-lg border border-[var(--border)] bg-white px-4 py-3 text-left hover:border-[var(--primary)]">
                <div className="font-medium text-sm">📊 Upload Excel/CSV</div>
                <div className="text-xs text-[var(--text-secondary)]">Pajakia auto-sanitize sebelum convert</div>
              </button>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between rounded-lg bg-blue-50 p-4">
            <div>
              <div className="text-sm font-semibold">Periode</div>
              <div className="text-xs text-[var(--text-secondary)]">Pilih masa dan tahun pajak</div>
            </div>
            <div className="flex gap-2">
              <select className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm">
                <option>Januari</option><option>Februari</option><option>Maret</option>
                <option>April</option><option>Mei</option><option>Juni</option>
                <option>Juli</option><option>Agustus</option><option>September</option>
                <option>Oktober</option><option>November</option><option>Desember</option>
              </select>
              <select className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm">
                <option>2026</option><option>2025</option><option>2024</option>
              </select>
            </div>
          </div>

          <div className="mt-6 flex gap-2">
            <button className="flex-1 rounded-lg bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">
              Generate XML
            </button>
            <button className="rounded-lg border border-[var(--border)] px-4 py-3 text-sm font-semibold hover:bg-gray-50">
              Preview
            </button>
          </div>
        </div>
      )}

      {tab === "validator" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6">
          <h3 className="mb-1 text-lg font-bold">Pre-flight Validator</h3>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Cek file XML terhadap 22 error Coretax yang sudah dikenal — sebelum upload, bukan setelah ditolak.
          </p>

          <div className="rounded-lg border-2 border-dashed border-[var(--border)] p-8 text-center">
            <div className="mb-2 text-4xl">📁</div>
            <div className="font-semibold">Drop file XML di sini atau klik untuk pilih</div>
            <div className="mt-1 text-xs text-[var(--text-secondary)]">
              Mendukung: e-Bupot XML, e-Faktur XML, SPT Masa PPh 21 XML
            </div>
            <button
              onClick={handleValidate}
              className="mt-4 rounded-lg bg-[var(--primary)] px-6 py-2 text-sm font-semibold text-white"
            >
              Validate Sekarang
            </button>
          </div>

          {valResult && (
            <div className="mt-4 rounded-lg border border-[var(--border)] p-4">
              <div className="mb-3 flex items-center gap-3">
                <span className={`rounded-full px-3 py-1 text-xs font-bold ${valResult.valid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                  {valResult.valid ? "✅ VALID" : "❌ DITOLAK"}
                </span>
                <div className="text-sm">
                  <strong>{valResult.records}</strong> record diperiksa,{" "}
                  <strong className="text-red-600">{valResult.errors}</strong> error,{" "}
                  <strong className="text-yellow-600">{valResult.warnings}</strong> warning
                </div>
              </div>

              <div className="space-y-2">
                <div className="rounded-lg bg-red-50 p-3 text-sm">
                  <div className="font-semibold text-red-800">❌ ERR-CT-013: Nomor bukti potong duplikat</div>
                  <div className="text-xs text-red-700">Lokasi: BuktiPotong[14], BuktiPotong[27]</div>
                  <div className="mt-1 text-xs text-red-600">Fix: Pajakia auto-generate nomor unik. Klik &quot;Auto-Fix&quot;.</div>
                </div>
                <div className="rounded-lg bg-red-50 p-3 text-sm">
                  <div className="font-semibold text-red-800">❌ ERR-CT-001: NPWP harus 16 digit</div>
                  <div className="text-xs text-red-700">Lokasi: BuktiPotong[3].Penerima.NPWP, value: &quot;01234567890123&quot;</div>
                  <div className="mt-1 text-xs text-red-600">Fix: Auto-pad ke 16 digit (tambah 0 di depan).</div>
                </div>
                <div className="rounded-lg bg-yellow-50 p-3 text-sm">
                  <div className="font-semibold text-yellow-800">⚠️ ERR-CT-012: PPh tidak sesuai DPP × Tarif</div>
                  <div className="text-xs text-yellow-700">Lokasi: BuktiPotong[8], expected 750000, got 745000</div>
                  <div className="mt-1 text-xs text-yellow-600">Selisih 5000. Cek apakah perhitungan benar.</div>
                </div>
              </div>

              <button className="mt-4 w-full rounded-lg bg-[var(--accent)] px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-700">
                🔧 Auto-Fix Semua Error (3 dapat diperbaiki otomatis)
              </button>
            </div>
          )}
        </div>
      )}

      {tab === "decoder" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6">
          <h3 className="mb-1 text-lg font-bold">Coretax Error Decoder</h3>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Paste error message dari Coretax. Pajakia decode dan kasih solusi spesifik.
          </p>

          <textarea
            value={errorMsg}
            onChange={(e) => setErrorMsg(e.target.value)}
            placeholder="Contoh: 'Invalid NPWP format in row 14' atau 'Service unavailable 503'"
            rows={4}
            className="w-full rounded-lg border border-[var(--border)] px-4 py-3 text-sm focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
          <button
            onClick={handleDecode}
            className="mt-3 rounded-lg bg-[var(--primary)] px-6 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
          >
            Decode Error
          </button>

          {decoded && (
            <div className={`mt-4 rounded-lg border-2 p-4 ${
              decoded.severity === "critical"
                ? "border-red-200 bg-red-50"
                : "border-yellow-200 bg-yellow-50"
            }`}>
              <div className="mb-2 flex items-center gap-2">
                <span className="text-2xl">{decoded.severity === "critical" ? "🚨" : "⚠️"}</span>
                <h4 className="font-bold">{decoded.title}</h4>
              </div>
              <div className="mb-3">
                <div className="text-xs font-semibold text-[var(--text-secondary)]">PENJELASAN</div>
                <div className="text-sm">{decoded.explanation}</div>
              </div>
              <div>
                <div className="text-xs font-semibold text-[var(--text-secondary)]">SOLUSI</div>
                <div className="text-sm font-medium">{decoded.fix}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "queue" && (
        <div className="rounded-xl border border-[var(--border)] bg-white">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
            <div>
              <h3 className="text-lg font-bold">Retry Queue</h3>
              <p className="text-sm text-[var(--text-secondary)]">
                Submission yang gagal upload akan auto-retry dengan exponential backoff
              </p>
            </div>
            <button className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-gray-50">
              🔄 Retry Semua
            </button>
          </div>

          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--border)] bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Type</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Periode</th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Status</th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">Retry</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--text-secondary)]">Reference / Error</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-secondary)]">Waktu</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {MOCK_QUEUE.map((q) => (
                <tr key={q.id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm font-medium">
                    {q.type === "ebupot" ? "📋 e-Bupot" : q.type === "efaktur" ? "🧾 e-Faktur" : "👥 SPT Masa PPh 21"}
                  </td>
                  <td className="px-6 py-3 text-sm">{q.masa.toString().padStart(2, "0")}/{q.tahun}</td>
                  <td className="px-6 py-3 text-center">{statusBadge(q.status)}</td>
                  <td className="px-6 py-3 text-center text-sm">{q.retries}/8</td>
                  <td className="px-6 py-3 text-sm">
                    {q.ref ? (
                      <code className="text-xs font-mono text-green-700">{q.ref}</code>
                    ) : q.error ? (
                      <span className="text-xs text-red-600">{q.error}</span>
                    ) : (
                      <span className="text-xs text-[var(--text-secondary)]">—</span>
                    )}
                  </td>
                  <td className="px-6 py-3 text-right text-xs text-[var(--text-secondary)]">{q.when}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "errors" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6">
          <h3 className="mb-1 text-lg font-bold">22 Error Coretax (Database Pajakia)</h3>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Semua error yang sudah dikenal dan punya solusi otomatis di Pajakia. Sumber: DJP + komunitas konsultan.
          </p>

          <div className="space-y-2">
            {KNOWN_ERRORS.map((e) => (
              <div key={e.code} className="flex items-start gap-3 rounded-lg border border-[var(--border)] p-3">
                <code className="flex-shrink-0 rounded bg-gray-100 px-2 py-1 text-xs font-mono">{e.code}</code>
                <div className="flex-1">
                  <div className="text-sm font-medium">{e.label}</div>
                </div>
                <div className="flex gap-1">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    e.severity === "critical" ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {e.severity}
                  </span>
                  {e.auto_fixable && (
                    <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-800">
                      🔧 auto-fix
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Browser Extension Promo */}
      <div className="rounded-xl border-2 border-[var(--primary)] bg-gradient-to-r from-blue-50 to-indigo-50 p-6">
        <div className="flex items-start gap-4">
          <div className="text-4xl">🧩</div>
          <div className="flex-1">
            <h3 className="font-bold">Pajakia Browser Extension</h3>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Install Chrome extension untuk auto-fill form Coretax langsung dari dashboard, decode error inline,
              dan auto-save draft setiap 30 detik (Coretax sering timeout!).
            </p>
            <div className="mt-3 flex gap-2">
              <button className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">
                Download Extension (.crx)
              </button>
              <button className="rounded-lg border border-[var(--border)] bg-white px-4 py-2 text-sm font-semibold">
                Lihat Cara Install
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
