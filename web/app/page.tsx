import Link from "next/link";

const features = [
  {
    icon: "🧮",
    title: "Kalkulator PPh 21",
    desc: "Hitung pajak penghasilan dengan metode TER terbaru. Gratis, instan, akurat.",
    href: "/kalkulator",
    cta: "Hitung Sekarang",
  },
  {
    icon: "📸",
    title: "Scan Bukti Potong",
    desc: "Foto bukti potong 1721-A1/A2 — AI ekstrak semua data otomatis dalam hitungan detik.",
    href: "/dashboard",
    cta: "Upload Dokumen",
  },
  {
    icon: "💬",
    title: "Asisten WhatsApp",
    desc: "Kirim foto dokumen pajak ke WhatsApp. Kami proses, Anda tinggal review dan file.",
    href: "https://wa.me/628131102445?text=Halo%20Pajakia",
    cta: "Chat di WhatsApp",
  },
];

const stats = [
  { value: "70 juta+", label: "Wajib Pajak di Indonesia" },
  { value: "~5.000", label: "Konsultan Pajak Terdaftar" },
  { value: "35%", label: "WP Tidak Lapor SPT" },
  { value: "Rp 99rb", label: "Mulai dari" },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-2xl font-extrabold text-[var(--primary)]">
            Pajakia
          </Link>
          <div className="flex items-center gap-6">
            <Link
              href="/kalkulator"
              className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]"
            >
              Kalkulator
            </Link>
            <Link
              href="/konsultan"
              className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]"
            >
              Konsultan
            </Link>
            <Link
              href="/dashboard"
              className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
            >
              Masuk
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pb-20 pt-24 text-center">
        <div className="mx-auto max-w-3xl">
          <div className="mb-4 inline-block rounded-full bg-blue-50 px-4 py-1.5 text-sm font-medium text-[var(--primary)]">
            AI-Powered Tax Preparation
          </div>
          <h1 className="mb-6 text-5xl font-extrabold leading-tight tracking-tight text-[var(--text)] md:text-6xl">
            Pajak jadi{" "}
            <span className="text-[var(--primary)]">mudah</span>
            <br />
            dengan AI
          </h1>
          <p className="mb-8 text-lg text-[var(--text-secondary)] md:text-xl">
            Hitung PPh 21, scan bukti potong, siapkan SPT Tahunan — semua dibantu
            kecerdasan buatan. Untuk karyawan, freelancer, UMKM, dan konsultan pajak.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/kalkulator"
              className="rounded-xl bg-[var(--primary)] px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-[var(--primary-dark)] hover:shadow-xl transition-all"
            >
              Hitung Pajak Gratis
            </Link>
            <Link
              href="https://wa.me/628131102445?text=Halo%20Pajakia"
              className="rounded-xl border-2 border-[var(--border)] px-8 py-4 text-lg font-bold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
            >
              💬 Chat WhatsApp
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-[var(--border)] bg-white">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-12 md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-extrabold text-[var(--primary)]">
                {s.value}
              </div>
              <div className="mt-1 text-sm text-[var(--text-secondary)]">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="mb-4 text-center text-3xl font-extrabold">
          Semua yang Anda butuhkan
        </h2>
        <p className="mb-12 text-center text-[var(--text-secondary)]">
          Dari hitung pajak sampai lapor SPT — satu platform untuk semua.
        </p>
        <div className="grid gap-8 md:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-[var(--border)] bg-white p-8 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="mb-4 text-4xl">{f.icon}</div>
              <h3 className="mb-2 text-xl font-bold">{f.title}</h3>
              <p className="mb-6 text-[var(--text-secondary)]">{f.desc}</p>
              <Link
                href={f.href}
                className="font-semibold text-[var(--primary)] hover:underline"
              >
                {f.cta} →
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* For Consultants */}
      <section className="border-y border-[var(--border)] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-block rounded-full bg-emerald-50 px-4 py-1.5 text-sm font-medium text-[var(--accent)]">
              Untuk Konsultan Pajak
            </div>
            <h2 className="mb-4 text-3xl font-extrabold">
              Tangani 3-5x lebih banyak klien
            </h2>
            <p className="mb-8 text-[var(--text-secondary)]">
              AI membantu proses dokumen, hitung pajak, dan kelola klien — Anda fokus
              pada advisory dan review. Tingkatkan kapasitas tanpa tambah staf.
            </p>
            <div className="grid gap-4 text-left sm:grid-cols-2">
              {[
                "OCR otomatis bukti potong & faktur pajak",
                "Dashboard multi-klien dengan deadline tracker",
                "Koleksi dokumen via WhatsApp klien Anda",
                "Auto-prepare SPT Masa & Tahunan",
                "Deteksi anomali sebelum filing",
                "Integrasi Coretax (batch upload)",
              ].map((item) => (
                <div key={item} className="flex items-start gap-2">
                  <span className="mt-0.5 text-[var(--accent)]">✓</span>
                  <span className="text-sm">{item}</span>
                </div>
              ))}
            </div>
            <div className="mt-8">
              <Link
                href="https://wa.me/628131102445?text=Saya%20konsultan%20pajak%2C%20tertarik%20dengan%20Pajakia"
                className="rounded-xl bg-[var(--accent)] px-8 py-4 text-lg font-bold text-white hover:bg-emerald-700 transition-colors inline-block"
              >
                Hubungi Kami
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="mb-4 text-center text-3xl font-extrabold">Harga</h2>
        <p className="mb-12 text-center text-[var(--text-secondary)]">
          Mulai gratis. Bayar hanya saat Anda butuh lebih.
        </p>
        <div className="grid gap-8 md:grid-cols-3">
          {[
            {
              name: "Gratis",
              price: "Rp 0",
              period: "selamanya",
              features: [
                "Kalkulator PPh 21",
                "Tanya jawab pajak via WhatsApp",
                "Scan 3 bukti potong/bulan",
              ],
              cta: "Mulai Gratis",
              href: "/kalkulator",
              highlight: false,
            },
            {
              name: "Personal",
              price: "Rp 99.000",
              period: "per SPT",
              features: [
                "Semua fitur Gratis",
                "Persiapan SPT 1770S/1770SS",
                "Scan dokumen unlimited",
                "Panduan filing Coretax",
              ],
              cta: "Mulai Sekarang",
              href: "/dashboard",
              highlight: true,
            },
            {
              name: "Konsultan",
              price: "Rp 500.000",
              period: "per bulan",
              features: [
                "Dashboard multi-klien",
                "OCR & auto-prepare semua SPT",
                "WhatsApp portal untuk klien",
                "Hingga 20 klien",
              ],
              cta: "Hubungi Sales",
              href: "https://wa.me/628131102445?text=Tertarik%20paket%20Konsultan",
              highlight: false,
            },
          ].map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl border p-8 ${
                plan.highlight
                  ? "border-[var(--primary)] bg-blue-50 shadow-lg"
                  : "border-[var(--border)] bg-white"
              }`}
            >
              <h3 className="text-lg font-bold">{plan.name}</h3>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold">{plan.price}</span>
                <span className="text-sm text-[var(--text-secondary)]">
                  /{plan.period}
                </span>
              </div>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent)]">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href={plan.href}
                className={`mt-8 block rounded-lg py-3 text-center font-semibold transition-colors ${
                  plan.highlight
                    ? "bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)]"
                    : "border border-[var(--border)] text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)]"
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div>
              <div className="text-xl font-extrabold text-[var(--primary)]">
                Pajakia
              </div>
              <div className="mt-1 text-sm text-[var(--text-secondary)]">
                Asisten pajak cerdas untuk Indonesia
              </div>
            </div>
            <div className="text-sm text-[var(--text-secondary)]">
              © {new Date().getFullYear()} Pajakia. Bukan pengganti konsultan pajak berlisensi.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
