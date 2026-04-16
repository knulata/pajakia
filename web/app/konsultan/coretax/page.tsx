"use client";

import { useState, useRef } from "react";
import * as XLSX from "xlsx";

type Tab = "generator" | "validator" | "decoder" | "queue" | "errors";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

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
  { id: "q1", type: "ebupot", status: "succeeded", masa: 2, tahun: 2026, ref: "BPE-2026-002847", retries: 0, when: "5 menit lalu", error: null },
  { id: "q2", type: "efaktur", status: "retrying", masa: 3, tahun: 2026, ref: null, retries: 2, error: "Coretax maintenance — retry in 30 min", when: "1 jam lalu" },
  { id: "q3", type: "spt_masa_pph21", status: "succeeded", masa: 2, tahun: 2026, ref: "BPE-2026-002831", retries: 0, when: "2 jam lalu", error: null },
  { id: "q4", type: "ebupot", status: "queued", masa: 3, tahun: 2026, ref: null, retries: 0, when: "3 jam lalu", error: null },
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
    queued: "Antri", uploading: "Upload", retrying: "Retry",
    succeeded: "Berhasil", failed: "Gagal", cancelled: "Batal",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${styles[s] || styles.queued}`}>
      {labels[s] || s}
    </span>
  );
}

/** Required column headers for bukti potong e-Bupot CSV/XLSX */
const EBUPOT_COLUMNS = [
  "nama_penerima", "npwp_penerima", "nik_penerima",
  "kode_objek_pajak", "penghasilan_bruto", "tarif",
  "pph_dipotong", "nomor_bukti_potong", "tanggal_bukti_potong",
];

function EBUPOT_TEMPLATE_CSV() {
  const header = EBUPOT_COLUMNS.join(",");
  const sample1 = [
    "Andi Wijaya", "1234567890123456", "3201234567890001",
    "21-100-01", "180000000", "5",
    "9000000", "BP-2026-0001", "2026-01-31",
  ].join(",");
  const sample2 = [
    "Siti Rahma", "2345678901234567", "3201234567890002",
    "21-100-01", "120000000", "5",
    "6000000", "BP-2026-0002", "2026-01-31",
  ].join(",");
  return `${header}\n${sample1}\n${sample2}\n`;
}

function parseFileToRows(file: File): Promise<Record<string, unknown>[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target!.result as ArrayBuffer);
        const wb = XLSX.read(data, { type: "array", cellDates: false, raw: false });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json(sheet, { defval: "", raw: false }) as Record<string, unknown>[];
        resolve(rows);
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(reader.error);
    reader.readAsArrayBuffer(file);
  });
}

function downloadBlob(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function CoretaxPage() {
  const [tab, setTab] = useState<Tab>("generator");

  // Error Decoder state
  const [errorMsg, setErrorMsg] = useState("");
  const [decoded, setDecoded] = useState<{ title: string; explanation: string; fix: string; severity: string } | null>(null);

  // Generator state
  const [genRows, setGenRows] = useState<Record<string, unknown>[]>([]);
  const [genFileName, setGenFileName] = useState("");
  const [genPemotongNpwp, setGenPemotongNpwp] = useState("");
  const [genPemotongNama, setGenPemotongNama] = useState("");
  const [genMasa, setGenMasa] = useState(3);
  const [genTahun, setGenTahun] = useState(2026);
  const [genBusy, setGenBusy] = useState(false);
  const [genError, setGenError] = useState("");
  const [genSuccess, setGenSuccess] = useState("");
  const genFileRef = useRef<HTMLInputElement>(null);

  // Validator state
  const [valXml, setValXml] = useState("");
  const [valFileName, setValFileName] = useState("");
  const [valBusy, setValBusy] = useState(false);
  const [valResult, setValResult] = useState<{
    is_valid: boolean;
    total_records: number;
    errors: Array<{ code: string; label: string; location: string; fix: string; field?: string; value?: string }>;
    warnings: Array<{ code: string; label: string; location: string; fix: string; field?: string; value?: string }>;
  } | null>(null);
  const [valType, setValType] = useState<"ebupot" | "efaktur">("ebupot");
  const valFileRef = useRef<HTMLInputElement>(null);

  // ---- Error Decoder ----
  async function handleDecode() {
    if (!errorMsg.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/coretax/decode-error`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error_message: errorMsg }),
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const data = await res.json();
      setDecoded({
        title: data.title || "Unknown",
        explanation: data.explanation || "",
        fix: data.fix || "",
        severity: data.severity || "warning",
      });
    } catch {
      setDecoded({
        title: "Koneksi gagal",
        explanation: "Tidak dapat terhubung ke Pajakia API.",
        fix: "Cek koneksi internet dan coba lagi.",
        severity: "warning",
      });
    }
  }

  // ---- Generator ----
  async function handleGenFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setGenError("");
    setGenSuccess("");
    try {
      const rows = await parseFileToRows(file);
      // Validate header
      if (rows.length === 0) {
        setGenError("File kosong atau tidak dapat dibaca.");
        return;
      }
      const first = rows[0];
      const missing = EBUPOT_COLUMNS.filter((c) => !(c in first));
      if (missing.length > 0) {
        setGenError(
          `Kolom wajib hilang: ${missing.join(", ")}. Download template untuk lihat format yang benar.`
        );
        return;
      }
      setGenRows(rows);
      setGenFileName(file.name);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : "Gagal parse file.");
    }
  }

  async function handleGenerate() {
    if (genRows.length === 0) {
      setGenError("Upload file dulu.");
      return;
    }
    if (!genPemotongNpwp.trim() || !genPemotongNama.trim()) {
      setGenError("NPWP dan nama pemotong wajib diisi.");
      return;
    }
    setGenBusy(true);
    setGenError("");
    setGenSuccess("");
    try {
      const bukti_potong = genRows.map((r) => ({
        nama_penerima: String(r.nama_penerima || "").trim(),
        npwp_penerima: String(r.npwp_penerima || "").trim(),
        nik_penerima: String(r.nik_penerima || "").trim(),
        kode_objek_pajak: String(r.kode_objek_pajak || "21-100-01").trim(),
        penghasilan_bruto: Number(String(r.penghasilan_bruto || "0").replace(/[^\d.-]/g, "")) || 0,
        tarif: Number(String(r.tarif || "5").replace(/[^\d.-]/g, "")) || 5,
        pph_dipotong: Number(String(r.pph_dipotong || "0").replace(/[^\d.-]/g, "")) || 0,
        nomor_bukti_potong: String(r.nomor_bukti_potong || "").trim(),
        tanggal_bukti_potong: String(r.tanggal_bukti_potong || "").trim(),
      }));

      const res = await fetch(`${API_BASE}/api/v1/coretax/xml/ebupot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bukti_potong,
          pemotong_npwp: genPemotongNpwp,
          pemotong_nama: genPemotongNama,
          masa: genMasa,
          tahun: genTahun,
        }),
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const xml = await res.text();
      downloadBlob(xml, `ebupot_${genTahun}${String(genMasa).padStart(2, "0")}.xml`, "application/xml");
      setGenSuccess(`XML dibuat untuk ${bukti_potong.length} bukti potong. File terdownload.`);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : "Gagal generate XML.");
    } finally {
      setGenBusy(false);
    }
  }

  function downloadTemplate() {
    downloadBlob(EBUPOT_TEMPLATE_CSV(), "template_ebupot.csv", "text/csv");
  }

  // ---- Validator ----
  async function handleValFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setValResult(null);
    const text = await file.text();
    setValXml(text);
    setValFileName(file.name);
  }

  async function handleValidate() {
    if (!valXml.trim()) {
      return;
    }
    setValBusy(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/coretax/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xml_content: valXml, type: valType }),
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const data = await res.json();
      setValResult(data);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal validasi.");
    } finally {
      setValBusy(false);
    }
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
          Generate XML, validasi sebelum upload, terjemahkan error — semua lewat browser, tanpa perlu install apapun.
        </p>
      </div>

      {/* How it works callout */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-5">
        <div className="font-bold text-[var(--primary)] text-sm mb-2">Cara pakai (tanpa install apapun)</div>
        <div className="grid gap-3 md:grid-cols-3 text-sm text-[var(--text)]">
          <div className="flex items-start gap-2">
            <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white">1</span>
            <div>Upload Excel bukti potong di tab Generator → Pajakia otomatis memperbaiki NPWP &amp; tanggal → download XML siap upload.</div>
          </div>
          <div className="flex items-start gap-2">
            <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white">2</span>
            <div>Upload XML ke <a href="https://coretax.pajak.go.id" target="_blank" rel="noopener noreferrer" className="text-[var(--primary)] underline">coretax.pajak.go.id</a>. Apabila ditolak → salin pesan errornya.</div>
          </div>
          <div className="flex items-start gap-2">
            <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white">3</span>
            <div>Paste pesan error di tab Error Decoder → Pajakia beritahu bagian mana yang salah + cara memperbaikinya.</div>
          </div>
        </div>
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
          { id: "validator" as Tab, label: "✅ Validator Pra-Upload" },
          { id: "decoder" as Tab, label: "🔍 Error Decoder" },
          { id: "queue" as Tab, label: "🔁 Antrian Retry" },
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

      {/* Generator */}
      {tab === "generator" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold">Generate e-Bupot XML dari Excel</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Upload file Excel/CSV bukti potong Anda. Pajakia auto-sanitize NPWP (fix bug Excel scientific notation),
              format tanggal ke ISO, dan hapus karakter terlarang — lalu generate XML Coretax-ready.
            </p>
          </div>

          {/* Template download */}
          <div className="rounded-lg bg-gray-50 p-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold">Belum punya template?</div>
              <div className="text-xs text-[var(--text-secondary)]">
                Download template CSV dengan kolom yang benar + 2 baris contoh.
              </div>
            </div>
            <button
              onClick={downloadTemplate}
              className="rounded-lg border border-[var(--border)] bg-white px-4 py-2 text-sm font-semibold hover:bg-gray-100"
            >
              📥 Download Template
            </button>
          </div>

          {/* File upload */}
          <div>
            <label className="block text-sm font-medium mb-2">1. Upload file bukti potong</label>
            <div
              onClick={() => genFileRef.current?.click()}
              className="rounded-lg border-2 border-dashed border-[var(--border)] p-6 text-center cursor-pointer hover:border-[var(--primary)] hover:bg-blue-50"
            >
              <div className="text-3xl mb-1">📁</div>
              <div className="font-semibold text-sm">{genFileName || "Klik untuk upload Excel/CSV"}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-1">
                Kolom wajib: {EBUPOT_COLUMNS.join(", ")}
              </div>
              <input
                ref={genFileRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                className="hidden"
                onChange={handleGenFile}
              />
            </div>
            {genRows.length > 0 && (
              <div className="mt-2 rounded-lg bg-green-50 p-3 text-sm text-green-800">
                ✅ {genRows.length} baris terbaca dari <strong>{genFileName}</strong>
              </div>
            )}
          </div>

          {/* Pemotong details */}
          <div>
            <label className="block text-sm font-medium mb-2">2. Data pemotong</label>
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                type="text"
                placeholder="NPWP Pemotong (16 digit)"
                value={genPemotongNpwp}
                onChange={(e) => setGenPemotongNpwp(e.target.value)}
                className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm"
              />
              <input
                type="text"
                placeholder="Nama Pemotong"
                value={genPemotongNama}
                onChange={(e) => setGenPemotongNama(e.target.value)}
                className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm"
              />
            </div>
          </div>

          {/* Period */}
          <div>
            <label className="block text-sm font-medium mb-2">3. Periode pajak</label>
            <div className="grid gap-3 sm:grid-cols-2">
              <select
                value={genMasa}
                onChange={(e) => setGenMasa(Number(e.target.value))}
                className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm"
              >
                {["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"].map((n, i) => (
                  <option key={i} value={i + 1}>{n} ({String(i + 1).padStart(2, "0")})</option>
                ))}
              </select>
              <select
                value={genTahun}
                onChange={(e) => setGenTahun(Number(e.target.value))}
                className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm"
              >
                {[2026, 2025, 2024].map((y) => (<option key={y} value={y}>{y}</option>))}
              </select>
            </div>
          </div>

          {genError && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-800">❌ {genError}</div>
          )}
          {genSuccess && (
            <div className="rounded-lg bg-green-50 p-3 text-sm text-green-800">✅ {genSuccess}</div>
          )}

          <button
            onClick={handleGenerate}
            disabled={genBusy || genRows.length === 0}
            className="w-full rounded-lg bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-white hover:bg-[var(--primary-dark)] disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {genBusy ? "Generating..." : `Generate XML (${genRows.length} bukti potong)`}
          </button>
        </div>
      )}

      {/* Validator */}
      {tab === "validator" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold">Validator Pra-Upload</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Upload XML yang akan Anda kirim ke Coretax. Pajakia akan cek 22 jenis error yang dikenal — sebelum Coretax menolaknya.
            </p>
          </div>

          <div className="flex gap-2">
            <label className="text-sm">Jenis file:</label>
            <select
              value={valType}
              onChange={(e) => setValType(e.target.value as "ebupot" | "efaktur")}
              className="rounded-lg border border-[var(--border)] px-3 py-1 text-sm"
            >
              <option value="ebupot">e-Bupot</option>
              <option value="efaktur">e-Faktur</option>
            </select>
          </div>

          <div
            onClick={() => valFileRef.current?.click()}
            className="rounded-lg border-2 border-dashed border-[var(--border)] p-8 text-center cursor-pointer hover:border-[var(--primary)] hover:bg-blue-50"
          >
            <div className="text-4xl mb-2">📄</div>
            <div className="font-semibold">{valFileName || "Klik untuk pilih file XML"}</div>
            <div className="text-xs text-[var(--text-secondary)] mt-1">
              Atau drag &amp; drop file ke sini
            </div>
            <input
              ref={valFileRef}
              type="file"
              accept=".xml,text/xml"
              className="hidden"
              onChange={handleValFile}
            />
          </div>

          <button
            onClick={handleValidate}
            disabled={valBusy || !valXml}
            className="w-full rounded-lg bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-white hover:bg-[var(--primary-dark)] disabled:bg-gray-300"
          >
            {valBusy ? "Memvalidasi..." : "Validasi Sekarang"}
          </button>

          {valResult && (
            <div className="rounded-lg border border-[var(--border)] p-4 space-y-3">
              <div className="flex items-center gap-3">
                <span className={`rounded-full px-3 py-1 text-xs font-bold ${valResult.is_valid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                  {valResult.is_valid ? "✅ VALID — siap upload" : "❌ ADA ERROR"}
                </span>
                <div className="text-sm">
                  <strong>{valResult.total_records}</strong> record diperiksa,{" "}
                  <strong className="text-red-600">{valResult.errors.length}</strong> error,{" "}
                  <strong className="text-yellow-600">{valResult.warnings.length}</strong> warning
                </div>
              </div>

              {valResult.errors.length > 0 && (
                <div className="space-y-2">
                  {valResult.errors.map((err, i) => (
                    <div key={i} className="rounded-lg bg-red-50 p-3 text-sm">
                      <div className="font-semibold text-red-800">❌ {err.code}: {err.label}</div>
                      <div className="text-xs text-red-700">
                        Lokasi: <code>{err.location}</code>
                        {err.field && <> | Field: <code>{err.field}</code></>}
                        {err.value && <> | Value: <code>{err.value}</code></>}
                      </div>
                      <div className="mt-1 text-xs text-red-600">Fix: {err.fix}</div>
                    </div>
                  ))}
                </div>
              )}

              {valResult.warnings.length > 0 && (
                <div className="space-y-2">
                  {valResult.warnings.map((w, i) => (
                    <div key={i} className="rounded-lg bg-yellow-50 p-3 text-sm">
                      <div className="font-semibold text-yellow-800">⚠️ {w.code}: {w.label}</div>
                      <div className="text-xs text-yellow-700">
                        Lokasi: <code>{w.location}</code>
                        {w.value && <> | {w.value}</>}
                      </div>
                      <div className="mt-1 text-xs text-yellow-600">Fix: {w.fix}</div>
                    </div>
                  ))}
                </div>
              )}

              {valResult.is_valid && valResult.errors.length === 0 && (
                <div className="rounded-lg bg-green-50 p-3 text-sm text-green-800">
                  🎉 File bersih! Silakan upload ke{" "}
                  <a href="https://coretax.pajak.go.id" target="_blank" rel="noopener noreferrer" className="underline font-semibold">
                    coretax.pajak.go.id
                  </a>.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Error Decoder */}
      {tab === "decoder" && (
        <div className="rounded-xl border border-[var(--border)] bg-white p-6">
          <h3 className="mb-1 text-lg font-bold">Coretax Error Decoder</h3>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Paste pesan error dari Coretax. Pajakia terjemahkan dan berikan solusi spesifik.
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
              decoded.severity === "critical" ? "border-red-200 bg-red-50" : "border-yellow-200 bg-yellow-50"
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

      {/* Queue */}
      {tab === "queue" && (
        <div className="rounded-xl border border-[var(--border)] bg-white">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
            <div>
              <h3 className="text-lg font-bold">Antrian Auto-Retry</h3>
              <p className="text-sm text-[var(--text-secondary)]">
                Pelacakan otomatis untuk submission yang pernah gagal (segera hadir — akan aktif setelah database terhubung)
              </p>
            </div>
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

      {/* 22 Error Catalog */}
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
    </div>
  );
}
