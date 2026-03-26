"use client";

import { useState } from "react";

export default function SecurityPage() {
  const [showSetup2FA, setShowSetup2FA] = useState(false);
  const [totpEnabled] = useState(false);
  const [ipAllowlist, setIpAllowlist] = useState<string[]>([]);
  const [newIp, setNewIp] = useState("");

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-extrabold">Keamanan</h1><p className="text-sm text-[var(--text-secondary)]">Pengaturan keamanan akun konsultan</p></div>

      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="border-b border-[var(--border)] px-6 py-4">
          <div className="flex items-center justify-between">
            <div><h2 className="font-bold">Autentikasi 2 Faktor (2FA)</h2><p className="text-sm text-[var(--text-secondary)]">Tambahkan lapisan keamanan ekstra</p></div>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${totpEnabled ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{totpEnabled ? "Aktif" : "Nonaktif"}</span>
          </div>
        </div>
        <div className="p-6">
          {!totpEnabled ? (
            !showSetup2FA ? (
              <button onClick={() => setShowSetup2FA(true)} className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]">Aktifkan 2FA</button>
            ) : (
              <div className="max-w-md space-y-4">
                <div className="rounded-lg bg-gray-50 p-6 text-center">
                  <div className="mx-auto h-48 w-48 rounded-lg bg-gray-200 flex items-center justify-center text-gray-400 text-sm">QR Code akan muncul di sini</div>
                  <p className="mt-3 text-sm text-[var(--text-secondary)]">Scan QR code dengan Google Authenticator atau Authy</p>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium">Masukkan Kode dari App</label>
                  <div className="flex gap-2">
                    <input type="text" maxLength={6} placeholder="000000" className="w-32 rounded-lg border border-[var(--border)] px-4 py-2 text-center text-lg tracking-widest" />
                    <button className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">Konfirmasi</button>
                  </div>
                </div>
                <button onClick={() => setShowSetup2FA(false)} className="text-sm text-[var(--text-secondary)] hover:underline">Batal</button>
              </div>
            )
          ) : (
            <div className="flex items-center justify-between">
              <div className="text-sm text-green-600 font-medium">2FA sudah aktif</div>
              <button className="text-sm text-red-600 hover:underline">Nonaktifkan 2FA</button>
            </div>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="border-b border-[var(--border)] px-6 py-4"><h2 className="font-bold">IP Allowlist</h2><p className="text-sm text-[var(--text-secondary)]">Batasi akses hanya dari IP tertentu (opsional)</p></div>
        <div className="p-6 space-y-4">
          <div className="flex gap-2">
            <input type="text" value={newIp} onChange={(e) => setNewIp(e.target.value)} placeholder="Contoh: 203.0.113.50" className="flex-1 rounded-lg border border-[var(--border)] px-4 py-2 text-sm" />
            <button onClick={() => { if (newIp.trim()) { setIpAllowlist((prev) => [...prev, newIp.trim()]); setNewIp(""); } }} className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm hover:bg-gray-50">Tambah</button>
          </div>
          {ipAllowlist.length > 0 ? (
            <div className="space-y-2">
              {ipAllowlist.map((ip, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-2">
                  <code className="text-sm">{ip}</code>
                  <button onClick={() => setIpAllowlist((prev) => prev.filter((_, idx) => idx !== i))} className="text-xs text-red-600 hover:underline">Hapus</button>
                </div>
              ))}
              <button className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">Simpan Allowlist</button>
            </div>
          ) : <p className="text-sm text-[var(--text-secondary)]">Tidak ada IP restriction — semua IP diizinkan.</p>}
        </div>
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="border-b border-[var(--border)] px-6 py-4"><h2 className="font-bold">Privasi Data</h2></div>
        <div className="p-6 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-[var(--border)] p-4"><div className="text-sm font-medium">Enkripsi Data</div><div className="mt-1 text-xs text-[var(--text-secondary)]">NPWP & NIK dienkripsi AES-256-GCM</div><span className="mt-2 inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-800">Aktif</span></div>
            <div className="rounded-lg border border-[var(--border)] p-4"><div className="text-sm font-medium">Lokasi Data</div><div className="mt-1 text-xs text-[var(--text-secondary)]">Semua data disimpan di Indonesia (ap-southeast-1)</div><span className="mt-2 inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-800">Indonesia</span></div>
            <div className="rounded-lg border border-[var(--border)] p-4"><div className="text-sm font-medium">Retensi Data</div><div className="mt-1 text-xs text-[var(--text-secondary)]">Data disimpan 5 tahun sesuai UU Perpajakan</div><span className="mt-2 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-800">5 Tahun</span></div>
            <div className="rounded-lg border border-[var(--border)] p-4"><div className="text-sm font-medium">Audit Log</div><div className="mt-1 text-xs text-[var(--text-secondary)]">Setiap akses data dicatat otomatis</div><span className="mt-2 inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-800">Aktif</span></div>
          </div>
          <div className="flex gap-2 pt-2">
            <button className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm hover:bg-gray-50">Export Semua Data Saya</button>
            <button className="rounded-lg border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50">Hapus Akun & Data</button>
          </div>
        </div>
      </div>
    </div>
  );
}
