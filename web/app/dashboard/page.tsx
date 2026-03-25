"use client";

import { useState, useRef } from "react";
import Link from "next/link";

type Tab = "overview" | "documents" | "filings";

export default function DashboardPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [dragOver, setDragOver] = useState(false);
  const [uploads, setUploads] = useState<
    { name: string; status: string; type: string }[]
  >([]);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const newUploads = Array.from(files).map((f) => ({
      name: f.name,
      status: "Diproses...",
      type: f.type.includes("image") ? "Foto" : "Dokumen",
    }));
    setUploads((prev) => [...newUploads, ...prev]);

    // Simulate processing
    setTimeout(() => {
      setUploads((prev) =>
        prev.map((u) =>
          newUploads.find((n) => n.name === u.name)
            ? { ...u, status: "Berhasil diekstrak" }
            : u
        )
      );
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-2xl font-extrabold text-[var(--primary)]">
            Pajakia
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/kalkulator"
              className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]"
            >
              Kalkulator
            </Link>
            <div className="h-8 w-8 rounded-full bg-[var(--primary)] flex items-center justify-center text-white text-sm font-bold">
              U
            </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-6xl px-6 py-8">
        <h1 className="mb-1 text-2xl font-extrabold">Dashboard</h1>
        <p className="mb-8 text-[var(--text-secondary)]">
          Kelola dokumen pajak dan SPT Anda
        </p>

        {/* Quick Stats */}
        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          {[
            { label: "Dokumen Diproses", value: uploads.length.toString(), icon: "📄" },
            { label: "SPT Draft", value: "0", icon: "📋" },
            { label: "Deadline Berikutnya", value: "31 Mar 2027", icon: "⏰" },
          ].map((s) => (
            <div
              key={s.label}
              className="rounded-xl border border-[var(--border)] bg-white p-5 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{s.icon}</span>
                <div>
                  <div className="text-2xl font-extrabold">{s.value}</div>
                  <div className="text-sm text-[var(--text-secondary)]">
                    {s.label}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-1 rounded-lg bg-gray-100 p-1">
          {(
            [
              ["overview", "Ringkasan"],
              ["documents", "Dokumen"],
              ["filings", "SPT"],
            ] as [Tab, string][]
          ).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                tab === key
                  ? "bg-white text-[var(--text)] shadow-sm"
                  : "text-[var(--text-secondary)] hover:text-[var(--text)]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {tab === "overview" && (
          <div className="space-y-6">
            {/* Upload Zone */}
            <div
              className={`rounded-2xl border-2 border-dashed p-12 text-center transition-colors ${
                dragOver
                  ? "border-[var(--primary)] bg-blue-50"
                  : "border-[var(--border)] bg-white"
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                handleFiles(e.dataTransfer.files);
              }}
            >
              <div className="mb-3 text-5xl">📸</div>
              <h3 className="mb-2 text-lg font-bold">
                Upload Bukti Potong atau Dokumen Pajak
              </h3>
              <p className="mb-4 text-sm text-[var(--text-secondary)]">
                Drag & drop foto atau PDF — AI akan mengekstrak data otomatis
              </p>
              <input
                ref={fileRef}
                type="file"
                multiple
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => handleFiles(e.target.files)}
              />
              <button
                onClick={() => fileRef.current?.click()}
                className="rounded-lg bg-[var(--primary)] px-6 py-3 font-semibold text-white hover:bg-[var(--primary-dark)]"
              >
                Pilih File
              </button>
            </div>

            {/* Quick Actions */}
            <div className="grid gap-4 sm:grid-cols-2">
              <Link
                href="/kalkulator"
                className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="mb-2 text-2xl">🧮</div>
                <h3 className="font-bold">Hitung PPh 21</h3>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  Kalkulator pajak penghasilan karyawan
                </p>
              </Link>
              <Link
                href="https://wa.me/628131102445?text=Halo%20Pajakia%2C%20saya%20mau%20siapkan%20SPT"
                className="rounded-xl border border-[var(--border)] bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="mb-2 text-2xl">💬</div>
                <h3 className="font-bold">Kirim via WhatsApp</h3>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  Foto bukti potong langsung dari HP
                </p>
              </Link>
            </div>
          </div>
        )}

        {tab === "documents" && (
          <div className="rounded-2xl border border-[var(--border)] bg-white shadow-sm">
            {uploads.length === 0 ? (
              <div className="p-12 text-center">
                <div className="mb-3 text-4xl">📂</div>
                <p className="text-[var(--text-secondary)]">
                  Belum ada dokumen. Upload bukti potong untuk memulai.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-[var(--border)]">
                {uploads.map((u, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between px-6 py-4"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">
                        {u.type === "Foto" ? "🖼️" : "📄"}
                      </span>
                      <div>
                        <div className="font-medium">{u.name}</div>
                        <div className="text-xs text-[var(--text-secondary)]">
                          {u.type}
                        </div>
                      </div>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        u.status.includes("Berhasil")
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {u.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "filings" && (
          <div className="rounded-2xl border border-[var(--border)] bg-white p-12 text-center shadow-sm">
            <div className="mb-3 text-4xl">📋</div>
            <h3 className="mb-2 text-lg font-bold">Belum Ada SPT</h3>
            <p className="mb-4 text-sm text-[var(--text-secondary)]">
              Upload bukti potong terlebih dahulu, lalu kami akan bantu siapkan SPT Anda.
            </p>
            <button
              onClick={() => setTab("overview")}
              className="rounded-lg bg-[var(--primary)] px-6 py-3 font-semibold text-white hover:bg-[var(--primary-dark)]"
            >
              Upload Dokumen
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
