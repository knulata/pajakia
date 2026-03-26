import Link from "next/link";

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
            <Link href="/kalkulator" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Kalkulator
            </Link>
            <Link href="#konsultan" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Untuk Konsultan
            </Link>
            <Link href="#harga" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Harga
            </Link>
            <Link
              href="/konsultan"
              className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
            >
              Masuk
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero — Consultant-focused */}
      <section className="mx-auto max-w-6xl px-6 pb-20 pt-24">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-4 inline-block rounded-full bg-emerald-50 px-4 py-1.5 text-sm font-semibold text-[var(--accent)]">
            Untuk Konsultan Pajak Indonesia
          </div>
          <h1 className="mb-6 text-5xl font-extrabold leading-tight tracking-tight text-[var(--text)] md:text-6xl">
            Tangani <span className="text-[var(--primary)]">100+ klien</span>
            <br />
            tanpa tambah staf
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-[var(--text-secondary)] md:text-xl">
            Klien upload dokumen sendiri. AI ekstrak data otomatis. Anda tinggal review dan approve.
            Dari 20 klien jadi 100+ — dengan tim yang sama.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="https://wa.me/628131102445?text=Saya%20konsultan%20pajak%2C%20mau%20coba%20Pajakia"
              className="rounded-xl bg-[var(--primary)] px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-[var(--primary-dark)] hover:shadow-xl transition-all"
            >
              Coba Gratis 14 Hari
            </Link>
            <Link
              href="#demo"
              className="rounded-xl border-2 border-[var(--border)] px-8 py-4 text-lg font-bold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
            >
              Lihat Demo →
            </Link>
          </div>
          <p className="mt-4 text-sm text-[var(--text-secondary)]">
            Tanpa kartu kredit. Setup dalam 5 menit.
          </p>
        </div>
      </section>

      {/* Pain Point Stats */}
      <section className="border-y border-[var(--border)] bg-white">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-12 md:grid-cols-4">
          {[
            { value: "5 jam", label: "Rata-rata proses 1 SPT manual", color: "text-red-600" },
            { value: "15 menit", label: "Proses 1 SPT dengan Pajakia", color: "text-[var(--accent)]" },
            { value: "95%", label: "Akurasi OCR dokumen pajak", color: "text-[var(--primary)]" },
            { value: "Rp 500rb", label: "Per bulan, hingga 100 klien", color: "text-[var(--primary)]" },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <div className={`text-3xl font-extrabold ${s.color}`}>{s.value}</div>
              <div className="mt-1 text-sm text-[var(--text-secondary)]">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* The Problem */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="mb-4 text-3xl font-extrabold">Masalah yang Anda hadapi setiap hari</h2>
          <div className="mt-8 grid gap-6 text-left md:grid-cols-2">
            {[
              { pain: "WhatsApp penuh dengan foto bukti potong dari klien", icon: "😩" },
              { pain: "Input data manual satu per satu ke spreadsheet", icon: "😤" },
              { pain: "Kejar deadline sambil ngejar dokumen yang belum lengkap", icon: "😰" },
              { pain: "Klien tanya terus kapan SPT-nya selesai", icon: "😫" },
              { pain: "Susah scale — tambah klien = tambah staf", icon: "💸" },
              { pain: "Data klien tersebar di banyak tempat, tidak aman", icon: "🔓" },
            ].map((p) => (
              <div key={p.pain} className="flex items-start gap-3 rounded-xl border border-[var(--border)] bg-white p-4">
                <span className="text-2xl">{p.icon}</span>
                <span className="text-sm text-[var(--text-secondary)]">{p.pain}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution: How it Works */}
      <section className="border-y border-[var(--border)] bg-white" id="demo">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center">
            <div className="mb-4 inline-block rounded-full bg-blue-50 px-4 py-1.5 text-sm font-semibold text-[var(--primary)]">
              Cara Kerja
            </div>
            <h2 className="mb-4 text-3xl font-extrabold">Dari dokumen masuk sampai SPT jadi — otomatis</h2>
            <p className="mx-auto mb-12 max-w-2xl text-[var(--text-secondary)]">
              Pajakia menangani pekerjaan repetitif. Anda fokus pada advisory bernilai tinggi.
            </p>
          </div>

          <div className="grid gap-0 md:grid-cols-4">
            {[
              {
                step: "1",
                title: "Klien Upload Sendiri",
                desc: "Kirim link portal ke klien. Mereka upload bukti potong, faktur, laporan keuangan — tanpa login. Anda lihat checklist real-time.",
                icon: "📤",
                color: "bg-blue-50 border-blue-200",
              },
              {
                step: "2",
                title: "AI Ekstrak Data",
                desc: "OCR membaca dokumen, ekstrak semua angka dan data. Akurasi 95%. Confidence score per field — Anda tahu mana yang perlu dicek.",
                icon: "🤖",
                color: "bg-purple-50 border-purple-200",
              },
              {
                step: "3",
                title: "Review & Approve",
                desc: "Side-by-side view: dokumen asli vs data hasil OCR. Edit field yang salah, klik Verifikasi. Deteksi anomali otomatis sebelum filing.",
                icon: "✅",
                color: "bg-yellow-50 border-yellow-200",
              },
              {
                step: "4",
                title: "Generate & File",
                desc: "SPT 1770S, 1770SS, SPT Masa PPh 21, e-Faktur — semua di-generate otomatis. Export CSV untuk upload ke Coretax.",
                icon: "📊",
                color: "bg-green-50 border-green-200",
              },
            ].map((s) => (
              <div key={s.step} className={`relative rounded-2xl border p-6 ${s.color}`}>
                <div className="mb-3 flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--primary)] text-sm font-bold text-white">
                    {s.step}
                  </span>
                  <span className="text-2xl">{s.icon}</span>
                </div>
                <h3 className="mb-2 text-lg font-bold">{s.title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Showcase — The Big 8 */}
      <section className="mx-auto max-w-6xl px-6 py-20" id="konsultan">
        <div className="text-center">
          <div className="mb-4 inline-block rounded-full bg-emerald-50 px-4 py-1.5 text-sm font-semibold text-[var(--accent)]">
            Platform Lengkap untuk Konsultan
          </div>
          <h2 className="mb-4 text-3xl font-extrabold">Semua yang Anda butuhkan, satu tempat</h2>
          <p className="mx-auto mb-12 max-w-2xl text-[var(--text-secondary)]">
            Bukan cuma kalkulator pajak. Ini sistem operasi untuk praktik konsultan pajak modern.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Feature 1: Client Portal */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-2xl">📤</div>
            <h3 className="mb-2 text-lg font-bold">Portal Klien Self-Service</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Generate link unik untuk setiap klien. Mereka upload dokumen sendiri — tanpa install app, tanpa login.
              Checklist otomatis: Anda tahu dokumen mana yang sudah masuk dan mana yang belum.
            </p>
            <div className="mt-4 rounded-lg bg-gray-50 p-3">
              <div className="text-xs font-semibold text-[var(--text-secondary)]">BEFORE & AFTER</div>
              <div className="mt-2 flex items-center gap-2 text-sm">
                <span className="text-red-500">Before:</span>
                <span className="text-[var(--text-secondary)]">WhatsApp &quot;Pak, kirim bukti potong ya&quot; x 50 klien</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-green-500">After:</span>
                <span className="text-[var(--text-secondary)]">Kirim 1 link, klien upload sendiri</span>
              </div>
            </div>
          </div>

          {/* Feature 2: OCR + Verification */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100 text-2xl">🔍</div>
            <h3 className="mb-2 text-lg font-bold">OCR + Verifikasi Cerdas</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              AI baca bukti potong, faktur pajak, laporan keuangan. Tampilkan side-by-side: dokumen asli vs data hasil OCR.
              Field dengan confidence rendah di-highlight merah — Anda langsung tahu mana yang harus dicek.
            </p>
            <div className="mt-4 flex gap-2">
              <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">95% akurasi</span>
              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">Bukti Potong</span>
              <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">Faktur Pajak</span>
            </div>
          </div>

          {/* Feature 3: Kanban Board */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-100 text-2xl">📋</div>
            <h3 className="mb-2 text-lg font-bold">Filing Board (Kanban)</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Lihat semua SPT klien dalam satu board. Drag & drop dari &quot;Kumpul Data&quot; ke &quot;Review&quot; ke &quot;Dilaporkan&quot;.
              Tidak ada yang terlewat. Status setiap klien terlihat sekilas.
            </p>
            <div className="mt-4 flex gap-1">
              {["Draft", "Data", "AI", "Review", "Filed"].map((s, i) => (
                <div key={s} className={`flex-1 rounded py-1 text-center text-[10px] font-semibold ${
                  i === 3 ? "bg-yellow-100 text-yellow-800" : "bg-gray-100 text-gray-500"
                }`}>{s}</div>
              ))}
            </div>
          </div>

          {/* Feature 4: Deadline Management */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-red-100 text-2xl">📅</div>
            <h3 className="mb-2 text-lg font-bold">Deadline Tracker + Priority</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Semua deadline klien dalam satu kalender. Prioritas otomatis berdasarkan urgency x denda x kompleksitas.
              Reminder WhatsApp otomatis ke klien yang belum kirim dokumen.
            </p>
            <div className="mt-4 space-y-1">
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2 w-2 rounded-full bg-red-500"></span>
                <span className="text-[var(--text-secondary)]">3 overdue — perlu tindakan segera</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2 w-2 rounded-full bg-yellow-500"></span>
                <span className="text-[var(--text-secondary)]">8 jatuh tempo minggu ini</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2 w-2 rounded-full bg-green-500"></span>
                <span className="text-[var(--text-secondary)]">36 on track</span>
              </div>
            </div>
          </div>

          {/* Feature 5: Batch Processing */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 text-2xl">⚡</div>
            <h3 className="mb-2 text-lg font-bold">Batch Processing</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Upload 50 bukti potong sekaligus. Generate SPT untuk 20 klien dalam satu klik.
              Import daftar klien dari Excel. Bulk e-Bupot CSV untuk Coretax.
            </p>
            <div className="mt-4 rounded-lg bg-indigo-50 p-3 text-center">
              <div className="text-2xl font-extrabold text-indigo-600">50 → 1</div>
              <div className="text-xs text-indigo-600">dokumen diproses paralel</div>
            </div>
          </div>

          {/* Feature 6: Revenue Tracking */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-green-100 text-2xl">💰</div>
            <h3 className="mb-2 text-lg font-bold">Invoice & Revenue</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Buat invoice langsung dari dashboard. Track pembayaran, lihat MRR, piutang, dan revenue per klien.
              Anda menjalankan bisnis — bukan cuma ngerjain pajak.
            </p>
            <div className="mt-4 flex items-baseline gap-1">
              <span className="text-2xl font-extrabold text-green-600">Rp 52,5jt</span>
              <span className="text-xs text-green-600">/bulan dari 47 klien</span>
            </div>
          </div>

          {/* Feature 7: Multi-Year History */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-100 text-2xl">📈</div>
            <h3 className="mb-2 text-lg font-bold">Riwayat Multi-Tahun</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Lihat SPT klien dari tahun ke tahun. Bandingkan penghasilan, pajak terutang, dan kredit pajak.
              Auto-populate data tahun lalu untuk SPT tahun ini.
            </p>
            <div className="mt-4 flex gap-2 text-xs">
              <span className="rounded bg-gray-100 px-2 py-1 font-mono">2023</span>
              <span className="rounded bg-gray-100 px-2 py-1 font-mono">2024</span>
              <span className="rounded bg-blue-100 px-2 py-1 font-mono font-bold text-blue-700">2025</span>
            </div>
          </div>

          {/* Feature 8: SPT Generation */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-100 text-2xl">📊</div>
            <h3 className="mb-2 text-lg font-bold">Auto-Generate Semua SPT</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              SPT 1770SS, 1770S, SPT Masa PPh 21, e-Faktur PPN, e-Bupot — semua di-generate dari data yang sudah diverifikasi.
              Download PDF atau CSV untuk upload ke Coretax/DJP Online.
            </p>
            <div className="mt-4 flex flex-wrap gap-1">
              {["1770SS", "1770S", "PPh 21", "PPN", "e-Bupot"].map((t) => (
                <span key={t} className="rounded bg-teal-50 px-2 py-0.5 text-xs font-semibold text-teal-700">{t}</span>
              ))}
            </div>
          </div>

          {/* Feature 9: Security */}
          <div className="rounded-2xl border-2 border-[var(--accent)] bg-emerald-50 p-6 hover:shadow-lg transition-shadow">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-2xl">🔒</div>
            <h3 className="mb-2 text-lg font-bold">Keamanan Kelas Enterprise</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              Data klien Anda aman. Enkripsi AES-256 untuk NPWP/NIK. 2FA wajib untuk akun konsultan.
              Audit log lengkap — tunjukkan ke klien siapa mengakses data kapan. Server di Indonesia.
            </p>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {[
                { label: "Enkripsi", value: "AES-256" },
                { label: "2FA", value: "TOTP" },
                { label: "Data", value: "Indonesia" },
                { label: "Audit", value: "Full Log" },
              ].map((s) => (
                <div key={s.label} className="rounded bg-white/80 p-2 text-center">
                  <div className="text-xs text-[var(--text-secondary)]">{s.label}</div>
                  <div className="text-xs font-bold text-[var(--accent)]">{s.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof / Use Case */}
      <section className="border-y border-[var(--border)] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="mb-12 text-center text-3xl font-extrabold">Sehari di kehidupan konsultan Pajakia</h2>
          <div className="mx-auto max-w-3xl space-y-6">
            {[
              { time: "08:00", event: "Buka dashboard. 12 dokumen baru masuk dari portal klien semalam.", icon: "☀️" },
              { time: "08:15", event: "AI sudah ekstrak semua data. Review 12 dokumen — 10 auto-verified, 2 perlu koreksi minor.", icon: "🤖" },
              { time: "08:45", event: "Generate SPT batch untuk 8 klien yang datanya sudah lengkap. Selesai dalam 2 menit.", icon: "⚡" },
              { time: "09:00", event: "Kirim reminder otomatis via WhatsApp ke 5 klien yang belum upload bukti potong.", icon: "💬" },
              { time: "09:30", event: "Review 3 SPT yang flagged anomali. Konsultasi langsung dengan klien via WhatsApp.", icon: "🔍" },
              { time: "10:00", event: "Selesai. 8 SPT filed, 5 reminder terkirim, 12 dokumen diproses. Sisa hari untuk advisory.", icon: "✅" },
            ].map((item) => (
              <div key={item.time} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="flex h-10 w-16 items-center justify-center rounded-lg bg-blue-50 text-sm font-bold text-[var(--primary)]">
                    {item.time}
                  </div>
                  <div className="mt-2 h-full w-px bg-[var(--border)]"></div>
                </div>
                <div className="flex items-start gap-3 pb-2">
                  <span className="text-xl">{item.icon}</span>
                  <p className="text-sm text-[var(--text-secondary)]">{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="mb-4 text-center text-3xl font-extrabold">Manual vs Pajakia</h2>
        <p className="mb-12 text-center text-[var(--text-secondary)]">Hitung sendiri berapa jam yang bisa Anda hemat</p>
        <div className="mx-auto max-w-3xl overflow-hidden rounded-2xl border border-[var(--border)]">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-6 py-4 text-left text-sm font-semibold">Pekerjaan</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-red-600">Manual</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-[var(--accent)]">Pajakia</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {[
                { task: "Input data dari bukti potong", manual: "30 menit/dok", pajakia: "10 detik (OCR)" },
                { task: "Kejar dokumen klien", manual: "WA satu-satu", pajakia: "Link portal + auto-reminder" },
                { task: "Hitung PPh 21 Tahunan", manual: "15 menit", pajakia: "Instan" },
                { task: "Generate SPT 1770S", manual: "1-2 jam", pajakia: "1 klik" },
                { task: "Track deadline 50 klien", manual: "Spreadsheet", pajakia: "Auto + priority score" },
                { task: "Proses SPT Masa bulanan", manual: "2-3 hari", pajakia: "Batch — 2 jam" },
                { task: "Cari data klien tahun lalu", manual: "Bongkar folder", pajakia: "1 klik, multi-tahun" },
              ].map((r) => (
                <tr key={r.task} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm">{r.task}</td>
                  <td className="px-6 py-3 text-center text-sm text-red-600">{r.manual}</td>
                  <td className="px-6 py-3 text-center text-sm font-semibold text-[var(--accent)]">{r.pajakia}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Pricing */}
      <section className="border-y border-[var(--border)] bg-white" id="harga">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="mb-4 text-center text-3xl font-extrabold">Investasi yang masuk akal</h2>
          <p className="mb-12 text-center text-[var(--text-secondary)]">
            Biaya Pajakia lebih murah dari gaji 1 staf admin pajak per bulan
          </p>
          <div className="grid gap-8 md:grid-cols-3">
            {/* Free */}
            <div className="rounded-2xl border border-[var(--border)] bg-white p-8">
              <h3 className="text-lg font-bold">Gratis</h3>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold">Rp 0</span>
                <span className="text-sm text-[var(--text-secondary)]">/selamanya</span>
              </div>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Untuk coba-coba dan WP individu</p>
              <ul className="mt-6 space-y-3">
                {[
                  "Kalkulator PPh 21 (TER + progresif)",
                  "Scan 3 bukti potong/bulan",
                  "Tanya jawab via WhatsApp",
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent)]">✓</span>{f}
                  </li>
                ))}
              </ul>
              <Link href="/kalkulator" className="mt-8 block rounded-lg border border-[var(--border)] py-3 text-center font-semibold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors">
                Mulai Gratis
              </Link>
            </div>

            {/* Personal */}
            <div className="rounded-2xl border border-[var(--border)] bg-white p-8">
              <h3 className="text-lg font-bold">Personal</h3>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold">Rp 99rb</span>
                <span className="text-sm text-[var(--text-secondary)]">/per SPT</span>
              </div>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Untuk karyawan & freelancer</p>
              <ul className="mt-6 space-y-3">
                {[
                  "Semua fitur Gratis",
                  "SPT 1770S / 1770SS lengkap",
                  "Scan dokumen unlimited",
                  "Panduan filing Coretax",
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent)]">✓</span>{f}
                  </li>
                ))}
              </ul>
              <Link href="/dashboard" className="mt-8 block rounded-lg border border-[var(--border)] py-3 text-center font-semibold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors">
                Mulai Sekarang
              </Link>
            </div>

            {/* Konsultan — HIGHLIGHTED */}
            <div className="rounded-2xl border-2 border-[var(--primary)] bg-blue-50 p-8 shadow-lg relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-[var(--primary)] px-4 py-1 text-xs font-bold text-white">
                PALING POPULER
              </div>
              <h3 className="text-lg font-bold">Konsultan</h3>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold">Rp 500rb</span>
                <span className="text-sm text-[var(--text-secondary)]">/bulan</span>
              </div>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Hingga 100 klien. Hemat 80% waktu.</p>
              <ul className="mt-6 space-y-3">
                {[
                  "Dashboard multi-klien + Kanban board",
                  "Portal self-service untuk klien",
                  "OCR unlimited + verifikasi cerdas",
                  "Auto-generate semua jenis SPT",
                  "Batch processing (50+ dokumen)",
                  "Deadline tracker + auto-reminder WA",
                  "Invoice & revenue tracking",
                  "2FA + enkripsi + audit log",
                  "Riwayat multi-tahun",
                  "e-Bupot & e-Faktur CSV export",
                  "Data export & compliance tools",
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent)]">✓</span>{f}
                  </li>
                ))}
              </ul>
              <Link
                href="https://wa.me/628131102445?text=Saya%20konsultan%20pajak%2C%20mau%20coba%20Pajakia%20paket%20Konsultan"
                className="mt-8 block rounded-lg bg-[var(--primary)] py-3 text-center font-semibold text-white hover:bg-[var(--primary-dark)] transition-colors"
              >
                Coba Gratis 14 Hari
              </Link>
              <p className="mt-2 text-center text-xs text-[var(--text-secondary)]">Tanpa kartu kredit</p>
            </div>
          </div>

          {/* ROI Calculator */}
          <div className="mx-auto mt-12 max-w-2xl rounded-2xl border border-[var(--border)] bg-white p-8 text-center">
            <h3 className="text-lg font-bold">Hitung ROI Anda</h3>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">
              Dengan 50 klien x rata-rata fee Rp 1jt/klien/bulan = <strong className="text-[var(--text)]">Rp 50jt/bulan revenue</strong>.
              Pajakia cuma <strong className="text-[var(--text)]">Rp 500rb/bulan</strong> = <strong className="text-[var(--accent)]">1% dari revenue</strong>.
              Tapi menghemat 80% waktu admin yang bisa dipakai untuk tambah klien.
            </p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-6 py-20 text-center">
        <h2 className="mb-4 text-4xl font-extrabold">
          Siap tangani lebih banyak klien?
        </h2>
        <p className="mx-auto mb-8 max-w-xl text-lg text-[var(--text-secondary)]">
          Join konsultan pajak yang sudah pakai AI untuk scale praktik mereka.
          Setup 5 menit, gratis 14 hari, tanpa kartu kredit.
        </p>
        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            href="https://wa.me/628131102445?text=Saya%20konsultan%20pajak%2C%20mau%20coba%20Pajakia"
            className="rounded-xl bg-[var(--primary)] px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-[var(--primary-dark)] hover:shadow-xl transition-all"
          >
            Mulai Gratis Sekarang
          </Link>
          <Link
            href="https://wa.me/628131102445?text=Mau%20lihat%20demo%20Pajakia"
            className="rounded-xl border-2 border-[var(--border)] px-8 py-4 text-lg font-bold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
          >
            Minta Demo Live
          </Link>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="border-t border-[var(--border)] bg-gray-50">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-[var(--text-secondary)]">
            <div className="flex items-center gap-2">
              <span className="text-green-500">🔒</span> Enkripsi AES-256
            </div>
            <div className="flex items-center gap-2">
              <span>🇮🇩</span> Server di Indonesia
            </div>
            <div className="flex items-center gap-2">
              <span>🛡️</span> 2FA untuk konsultan
            </div>
            <div className="flex items-center gap-2">
              <span>📋</span> Audit log lengkap
            </div>
            <div className="flex items-center gap-2">
              <span>📦</span> Data export kapan saja
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div>
              <div className="text-xl font-extrabold text-[var(--primary)]">Pajakia</div>
              <div className="mt-1 text-sm text-[var(--text-secondary)]">
                Platform AI untuk konsultan pajak Indonesia
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-[var(--text-secondary)]">
              <Link href="/kalkulator" className="hover:text-[var(--text)]">Kalkulator</Link>
              <Link href="/konsultan" className="hover:text-[var(--text)]">Dashboard</Link>
              <Link href="https://wa.me/628131102445" className="hover:text-[var(--text)]">WhatsApp</Link>
            </div>
          </div>
          <div className="mt-8 text-center text-xs text-[var(--text-secondary)]">
            © {new Date().getFullYear()} Pajakia. Bukan pengganti konsultan pajak berlisensi.
          </div>
        </div>
      </footer>
    </div>
  );
}
