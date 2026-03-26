import Link from "next/link";

/* ── WhatsApp Chat Mockup Components ── */
const WA_BG_PATTERN = "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4cfc6' fill-opacity='0.15'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")";

function WaChatBubble({ from, children, time, tail }: { from: "client" | "pajakia"; children: React.ReactNode; time: string; tail?: boolean }) {
  const isClient = from === "client";
  return (
    <div className={`flex ${isClient ? "justify-end" : "justify-start"} ${tail ? "mt-1" : "mt-2"}`}>
      <div className={`relative max-w-[85%] rounded-lg px-2.5 py-1.5 text-[12px] leading-snug shadow-sm ${
        isClient ? "bg-[#d9fdd3] text-[#111b21]" : "bg-white text-[#111b21]"
      }`}>
        {!isClient && !tail && (
          <div className="mb-0.5 text-[11px] font-semibold text-[#1a56db]">Pajakia AI</div>
        )}
        <div>{children}</div>
        <div className="mt-0.5 text-right text-[9px] text-[#667781]">
          {time} {isClient && <span className="ml-0.5 text-[#53bdeb]">✓✓</span>}
        </div>
      </div>
    </div>
  );
}

function WaImageBubble({ time }: { time: string }) {
  return (
    <div className="flex justify-end mt-2">
      <div className="relative rounded-lg overflow-hidden bg-[#d9fdd3] shadow-sm">
        <div className="bg-gradient-to-br from-gray-100 to-gray-200 p-2" style={{ width: 150, height: 80 }}>
          <div className="rounded bg-white p-2 shadow-sm" style={{ transform: "rotate(-1deg)" }}>
            <div className="mb-1 h-1.5 w-16 rounded bg-gray-800"></div>
            <div className="mb-1.5 text-[6px] font-bold text-gray-600">BUKTI PEMOTONGAN PPh 21</div>
            <div className="space-y-0.5">
              <div className="flex gap-1"><div className="h-1 w-10 rounded bg-gray-300"></div><div className="h-1 w-12 rounded bg-gray-400"></div></div>
              <div className="flex gap-1"><div className="h-1 w-8 rounded bg-gray-300"></div><div className="h-1 w-14 rounded bg-blue-300"></div></div>
            </div>
          </div>
        </div>
        <div className="px-2 py-0.5 text-right text-[9px] text-[#667781]">
          {time} <span className="ml-0.5 text-[#53bdeb]">✓✓</span>
        </div>
      </div>
    </div>
  );
}

/** Fixed-height WhatsApp phone — consistent 480px across all instances */
function WaPhoneMockup({ children, label }: { children: React.ReactNode; label?: string }) {
  return (
    <div className="flex flex-col items-center">
      {label && <div className="mb-2 text-sm font-semibold text-[var(--text-secondary)]">{label}</div>}
      <div className="flex w-[280px] flex-col overflow-hidden rounded-[1.75rem] border-[5px] border-gray-800 shadow-2xl" style={{ height: 480 }}>
        {/* Header — fixed */}
        <div className="flex items-center justify-between bg-[#008069] px-3 py-1.5 text-white flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-xs">←</span>
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/20 text-[10px] font-bold">P</div>
            <div>
              <div className="text-xs font-semibold">Pajakia</div>
              <div className="text-[8px] opacity-80">online</div>
            </div>
          </div>
          <div className="flex gap-2 text-xs">📞 ⋮</div>
        </div>
        {/* Chat area — fills remaining space, hides overflow */}
        <div className="flex-1 overflow-hidden px-2.5 py-2 bg-[#efeae2]" style={{ backgroundImage: WA_BG_PATTERN }}>
          {children}
        </div>
        {/* Input bar — fixed */}
        <div className="flex items-center gap-1.5 bg-[#f0f2f5] px-2.5 py-1.5 flex-shrink-0">
          <span className="text-sm">😊</span>
          <span className="text-sm">📎</span>
          <div className="flex-1 rounded-full bg-white px-2.5 py-1 text-[10px] text-gray-400">Ketik pesan</div>
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#008069] text-[10px] text-white">🎤</div>
        </div>
      </div>
    </div>
  );
}

/** Small phone for the 3-step section — fixed 280px height */
function MiniPhoneMockup({ headerText, headerColor, children }: { headerText: string; headerColor: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto w-[200px]">
      <div className="flex flex-col overflow-hidden rounded-2xl border-[4px] border-gray-800 shadow-xl" style={{ height: 220 }}>
        <div className={`${headerColor} px-3 py-1 text-left text-[9px] font-semibold text-white flex-shrink-0`}>
          {headerText}
        </div>
        <div className="flex-1 overflow-hidden bg-[#efeae2]" style={{ backgroundImage: headerColor.includes("primary") ? "none" : WA_BG_PATTERN, backgroundColor: headerColor.includes("primary") ? "white" : undefined }}>
          {children}
        </div>
      </div>
    </div>
  );
}

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
            <Link href="/kalkulator" className="hidden sm:block text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Kalkulator
            </Link>
            <Link href="#cara-kerja" className="hidden sm:block text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Cara Kerja
            </Link>
            <Link href="#harga" className="hidden sm:block text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text)]">
              Harga
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
            >
              Masuk
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero — WhatsApp first */}
      <section className="mx-auto max-w-6xl px-6 pb-16 pt-16 md:pt-20">
        <div className="grid items-center gap-12 md:grid-cols-2">
          {/* Left: Copy */}
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#25D366]/10 px-4 py-1.5 text-sm font-semibold text-[#128C7E]">
              <span>💬</span> WhatsApp-First Tax Processing
            </div>
            <h1 className="mb-6 text-4xl font-extrabold leading-tight tracking-tight text-[var(--text)] md:text-5xl lg:text-6xl">
              Foto bukti potong.
              <br />
              <span className="text-[var(--primary)]">SPT langsung jadi.</span>
            </h1>
            <p className="mb-8 text-lg text-[var(--text-secondary)]">
              Klien kirim foto dokumen pajak via WhatsApp. AI baca semua data dalam 10 detik.
              Anda tinggal review di dashboard. Tidak perlu input manual. Tidak perlu app baru.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row">
              <Link
                href="https://wa.me/628131102445?text=Halo%20Pajakia%2C%20mau%20coba%20kirim%20bukti%20potong"
                className="flex items-center justify-center gap-2 rounded-xl bg-[#25D366] px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-[#1da851] hover:shadow-xl transition-all"
              >
                <svg viewBox="0 0 24 24" className="h-6 w-6 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                Kirim Bukti Potong Sekarang
              </Link>
              <Link
                href="#cara-kerja"
                className="flex items-center justify-center rounded-xl border-2 border-[var(--border)] px-8 py-4 text-lg font-bold text-[var(--text)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
              >
                Lihat Cara Kerja →
              </Link>
            </div>
            <p className="mt-3 text-sm text-[var(--text-secondary)]">
              Gratis untuk 3 dokumen pertama. Tanpa install app.
            </p>
          </div>

          {/* Right: WhatsApp Mockup */}
          <div className="flex justify-center">
            <WaPhoneMockup>
              <WaImageBubble time="09:01" />
              <WaChatBubble from="pajakia" time="09:01">
                📸 Foto diterima! Memproses...
              </WaChatBubble>
              <WaChatBubble from="pajakia" time="09:01" tail>
                <div>
                  <div className="font-semibold">✅ Bukti Potong berhasil dibaca!</div>
                  <div className="mt-1.5 space-y-0.5 text-[12px]">
                    <div>👤 Andi Wijaya</div>
                    <div>🏢 PT Maju Bersama</div>
                    <div>💰 Bruto: <b>Rp 180.000.000</b></div>
                    <div>📊 PPh 21: <b>Rp 7.200.000</b></div>
                  </div>
                  <div className="mt-1.5 text-[11px] text-[#667781]">
                    Data tersimpan ✅
                  </div>
                </div>
              </WaChatBubble>
            </WaPhoneMockup>
          </div>
        </div>
      </section>

      {/* Comparison: The Old Way vs Pajakia */}
      <section className="border-y border-[var(--border)] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="mb-12 text-center text-3xl font-extrabold">Yang berubah dengan Pajakia</h2>
          <div className="grid gap-8 md:grid-cols-2">
            {/* Old Way */}
            <div className="rounded-2xl border-2 border-red-100 bg-red-50/50 p-6">
              <div className="mb-4 text-sm font-bold text-red-600">❌ CARA LAMA</div>
              <WaPhoneMockup label="Tanpa Pajakia">
                <WaChatBubble from="client" time="09:00">
                  Pak, ini bukti potong saya
                </WaChatBubble>
                <WaImageBubble time="09:01" />
                <WaChatBubble from="pajakia" time="11:30">
                  <div className="text-[12px]">
                    Terima kasih Bu. Saya input dulu datanya ke spreadsheet ya. Mohon tunggu 1-2 hari.
                  </div>
                </WaChatBubble>
                <WaChatBubble from="client" time="14:00">
                  Pak sudah selesai belum ya?
                </WaChatBubble>
                <WaChatBubble from="pajakia" time="16:45">
                  <div className="text-[12px]">Masih proses Bu, banyak antrian 🙏</div>
                </WaChatBubble>
              </WaPhoneMockup>
              <div className="mt-4 space-y-2 text-sm text-red-700">
                <div className="flex items-start gap-2"><span>⏱️</span> Input manual 30 menit per dokumen</div>
                <div className="flex items-start gap-2"><span>📱</span> Foto dokumen tenggelam di chat</div>
                <div className="flex items-start gap-2"><span>😤</span> Klien follow up terus</div>
                <div className="flex items-start gap-2"><span>🤦</span> Salah ketik? Ketahuan pas filing</div>
              </div>
            </div>

            {/* New Way */}
            <div className="rounded-2xl border-2 border-green-100 bg-green-50/50 p-6">
              <div className="mb-4 text-sm font-bold text-green-600">✅ DENGAN PAJAKIA</div>
              <WaPhoneMockup label="Dengan Pajakia">
                <WaChatBubble from="client" time="09:00">
                  Ini bukti potong saya
                </WaChatBubble>
                <WaImageBubble time="09:00" />
                <WaChatBubble from="pajakia" time="09:00">
                  📸 Foto diterima! Sedang diproses AI...
                </WaChatBubble>
                <WaChatBubble from="pajakia" time="09:00" tail>
                  <div>
                    <div className="font-semibold">✅ Berhasil dibaca!</div>
                    <div className="mt-1 text-[12px]">
                      👤 Siti Rahma<br/>
                      💰 Bruto: <b>Rp 120.000.000</b><br/>
                      📊 PPh: <b>Rp 3.600.000</b>
                    </div>
                    <div className="mt-1 text-[11px] text-[#667781]">Data tersimpan ✅</div>
                  </div>
                </WaChatBubble>
                <WaChatBubble from="client" time="09:01">
                  Wah cepat sekali! 🙏
                </WaChatBubble>
              </WaPhoneMockup>
              <div className="mt-4 space-y-2 text-sm text-green-700">
                <div className="flex items-start gap-2"><span>⚡</span> AI proses 10 detik per dokumen</div>
                <div className="flex items-start gap-2"><span>📊</span> Data langsung masuk dashboard</div>
                <div className="flex items-start gap-2"><span>😊</span> Klien langsung lihat hasilnya</div>
                <div className="flex items-start gap-2"><span>✅</span> Akurasi 95%, flagged jika ragu</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works — Step by Step */}
      <section className="mx-auto max-w-6xl px-6 py-20" id="cara-kerja">
        <div className="text-center">
          <div className="mb-4 inline-block rounded-full bg-blue-50 px-4 py-1.5 text-sm font-semibold text-[var(--primary)]">
            Cara Kerja
          </div>
          <h2 className="mb-4 text-3xl font-extrabold">Dari foto WhatsApp sampai SPT jadi</h2>
          <p className="mx-auto mb-16 max-w-xl text-[var(--text-secondary)]">
            Tiga langkah. Tanpa install app. Tanpa login portal. Cukup WhatsApp.
          </p>
        </div>

        <div className="grid gap-12 md:grid-cols-3">
          {/* Step 1 */}
          <div className="text-center">
            <div className="mb-6">
              <MiniPhoneMockup headerText="Pajakia" headerColor="bg-[#008069]">
                <div className="space-y-1.5 px-2 py-2">
                  <div className="flex justify-end">
                    <div className="rounded-lg bg-[#d9fdd3] px-2 py-1">
                      <div className="h-12 w-20 rounded bg-gray-200 flex items-center justify-center text-[7px] text-gray-400">📸 foto</div>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="rounded-lg bg-white px-2 py-1 text-[8px]">📸 Diterima! Memproses...</div>
                  </div>
                </div>
              </MiniPhoneMockup>
            </div>
            <div className="mb-2 flex items-center justify-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#25D366] text-sm font-bold text-white">1</span>
              <h3 className="text-lg font-bold">Klien Kirim Foto</h3>
            </div>
            <p className="text-sm text-[var(--text-secondary)]">
              Klien foto bukti potong, faktur pajak, atau dokumen apapun — langsung kirim via WhatsApp. Tanpa download app, tanpa buat akun.
            </p>
          </div>

          {/* Step 2 */}
          <div className="text-center">
            <div className="mb-6">
              <MiniPhoneMockup headerText="Pajakia" headerColor="bg-[#008069]">
                <div className="space-y-1.5 px-2 py-2">
                  <div className="flex justify-start">
                    <div className="rounded-lg bg-white px-2 py-1">
                      <div className="text-[8px] font-semibold">✅ Berhasil dibaca!</div>
                      <div className="mt-0.5 text-[7px] text-gray-600">
                        👤 Andi Wijaya<br/>
                        💰 Rp 180.000.000<br/>
                        📊 PPh: Rp 7.200.000
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="rounded-lg bg-white px-2 py-1 text-[7px]">
                      <span className="text-green-600 font-bold">Confidence: 95%</span>
                    </div>
                  </div>
                </div>
              </MiniPhoneMockup>
            </div>
            <div className="mb-2 flex items-center justify-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--primary)] text-sm font-bold text-white">2</span>
              <h3 className="text-lg font-bold">AI Baca & Ekstrak</h3>
            </div>
            <p className="text-sm text-[var(--text-secondary)]">
              Dalam 10 detik, AI membaca semua data — nama, NPWP, penghasilan, pajak terutang. Hasil langsung dikirim balik ke WhatsApp klien.
            </p>
          </div>

          {/* Step 3 */}
          <div className="text-center">
            <div className="mb-6">
              <MiniPhoneMockup headerText="Dashboard Konsultan" headerColor="bg-[var(--primary)]">
                <div className="p-2.5 bg-white h-full">
                  <div className="mb-1.5 flex items-center justify-between">
                    <div className="text-[8px] font-bold">Andi Wijaya</div>
                    <div className="rounded bg-green-100 px-1 text-[7px] font-bold text-green-700">95%</div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-[7px]"><span className="text-gray-500">Bruto</span><span className="font-semibold">180.000.000</span></div>
                    <div className="flex justify-between text-[7px]"><span className="text-gray-500">PPh 21</span><span className="font-semibold">7.200.000</span></div>
                    <div className="flex justify-between text-[7px]"><span className="text-gray-500">PTKP</span><span className="font-semibold">TK/0</span></div>
                  </div>
                  <div className="mt-2 flex gap-1">
                    <div className="flex-1 rounded bg-green-500 py-0.5 text-center text-[7px] font-bold text-white">Verifikasi</div>
                    <div className="flex-1 rounded bg-gray-200 py-0.5 text-center text-[7px] font-bold text-gray-600">Edit</div>
                  </div>
                </div>
              </MiniPhoneMockup>
            </div>
            <div className="mb-2 flex items-center justify-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--accent)] text-sm font-bold text-white">3</span>
              <h3 className="text-lg font-bold">Anda Review & Approve</h3>
            </div>
            <p className="text-sm text-[var(--text-secondary)]">
              Data masuk ke dashboard Anda. Side-by-side view: dokumen asli vs hasil OCR. Satu klik verifikasi, lalu generate SPT.
            </p>
          </div>
        </div>

        {/* Arrow annotation */}
        <div className="mt-12 rounded-2xl bg-gradient-to-r from-[#25D366]/10 via-[var(--primary)]/10 to-[var(--accent)]/10 p-6 text-center">
          <div className="text-lg font-bold">
            30 menit kerja manual → <span className="text-[var(--primary)]">10 detik AI + 1 klik review</span>
          </div>
          <div className="mt-1 text-sm text-[var(--text-secondary)]">Per dokumen. Kalikan 50 klien. Hitung sendiri berapa jam yang dihemat.</div>
        </div>
      </section>

      {/* What Consultants Get */}
      <section className="border-y border-[var(--border)] bg-white" id="konsultan">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center">
            <h2 className="mb-4 text-3xl font-extrabold">Dashboard untuk konsultan yang serius scale</h2>
            <p className="mx-auto mb-12 max-w-xl text-[var(--text-secondary)]">
              Semua dokumen WhatsApp masuk ke satu dashboard. Track, review, approve, generate — tanpa spreadsheet.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              { icon: "📋", title: "Kanban Filing Board", desc: "Lihat semua SPT klien per status. Drag & drop dari Draft → Review → Filed. Tidak ada yang terlewat." },
              { icon: "🔍", title: "Verifikasi Side-by-Side", desc: "Dokumen asli di kiri, data OCR di kanan. Field confidence rendah di-highlight merah. Edit langsung, klik Verifikasi." },
              { icon: "📅", title: "Deadline + Auto-Reminder", desc: "Semua deadline klien di satu tempat. Priority score otomatis. Reminder WhatsApp ke klien yang telat kirim dokumen." },
              { icon: "⚡", title: "Batch Processing", desc: "Upload 50 dokumen sekaligus. Generate SPT untuk 20 klien dalam satu klik. Import klien dari Excel." },
              { icon: "💰", title: "Invoice & Revenue", desc: "Buat invoice, track pembayaran, lihat MRR. Anda menjalankan bisnis, bukan cuma ngerjain pajak." },
              { icon: "🔒", title: "Enterprise Security", desc: "Enkripsi AES-256, 2FA wajib, audit log lengkap, data di Indonesia. Tunjukkan ke klien bahwa data mereka aman." },
            ].map((f) => (
              <div key={f.title} className="rounded-xl border border-[var(--border)] p-5 hover:shadow-md transition-shadow">
                <div className="mb-2 text-2xl">{f.icon}</div>
                <h3 className="mb-1 font-bold">{f.title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Consultant Daily Timeline */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid gap-12 md:grid-cols-2 items-center">
          <div>
            <h2 className="mb-4 text-3xl font-extrabold">Pagi Anda dengan Pajakia</h2>
            <p className="mb-8 text-[var(--text-secondary)]">
              Sebelum jam 10 pagi, Anda sudah proses 12 dokumen, file 8 SPT, dan kirim 5 reminder.
              Sisa hari untuk advisory — pekerjaan yang benar-benar bernilai.
            </p>
            <div className="space-y-4">
              {[
                { time: "08:00", text: "Buka dashboard. 12 dokumen dari WhatsApp klien sudah diproses AI semalam." },
                { time: "08:15", text: "Review 12 dokumen — 10 auto-verified, 2 perlu koreksi minor." },
                { time: "08:45", text: "Generate SPT batch untuk 8 klien. Selesai 2 menit." },
                { time: "09:00", text: "Auto-reminder WhatsApp ke 5 klien yang belum kirim dokumen." },
                { time: "09:30", text: "Review 2 SPT yang flagged anomali. Konsultasi via WA." },
                { time: "10:00", text: "Selesai. 8 SPT filed. Sisa hari untuk advisory." },
              ].map((item) => (
                <div key={item.time} className="flex gap-3">
                  <div className="flex h-8 w-14 flex-shrink-0 items-center justify-center rounded-lg bg-blue-50 text-xs font-bold text-[var(--primary)]">
                    {item.time}
                  </div>
                  <p className="text-sm text-[var(--text-secondary)]">{item.text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Consultant notification mockup */}
          <div className="flex justify-center">
            <WaPhoneMockup label="Notifikasi ke Konsultan">
              <WaChatBubble from="pajakia" time="08:00">
                <div>
                  <div className="font-semibold">📬 Dokumen baru dari klien!</div>
                  <div className="mt-1 text-[12px]">
                    👤 Klien: Andi Wijaya<br/>
                    📄 Tipe: Bukti Potong A1<br/>
                    📊 Status: data berhasil diekstrak<br/>
                    🎯 Confidence: 95%
                  </div>
                  <div className="mt-1 text-[11px] text-[#667781]">Buka dashboard untuk review.</div>
                </div>
              </WaChatBubble>
              <WaChatBubble from="pajakia" time="08:02">
                <div>
                  <div className="font-semibold">📬 Dokumen baru dari klien!</div>
                  <div className="mt-1 text-[12px]">
                    👤 Klien: Siti Rahma<br/>
                    📄 Tipe: Faktur Pajak<br/>
                    📊 Status: data berhasil diekstrak<br/>
                    🎯 Confidence: 88%
                  </div>
                </div>
              </WaChatBubble>
              <WaChatBubble from="pajakia" time="08:05">
                <div>
                  <div className="font-semibold">📬 3 dokumen baru!</div>
                  <div className="mt-1 text-[12px]">
                    👤 PT Karya Digital<br/>
                    📄 3x Faktur Pajak<br/>
                    📊 Semua berhasil diekstrak ✅
                  </div>
                </div>
              </WaChatBubble>
              <WaChatBubble from="pajakia" time="08:06">
                <div className="text-[12px]">
                  📊 <b>Ringkasan pagi ini:</b><br/>
                  12 dokumen masuk, 10 auto-verified<br/>
                  2 perlu review manual<br/>
                  <br/>
                  Buka dashboard → review → approve 🚀
                </div>
              </WaChatBubble>
            </WaPhoneMockup>
          </div>
        </div>
      </section>

      {/* Numbers */}
      <section className="border-y border-[var(--border)] bg-gradient-to-r from-[var(--primary)] to-[#1e40af] text-white">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-12 md:grid-cols-4">
          {[
            { value: "10 detik", label: "Per dokumen (OCR)" },
            { value: "95%", label: "Akurasi AI" },
            { value: "100+", label: "Klien per konsultan" },
            { value: "80%", label: "Waktu admin dihemat" },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-extrabold">{s.value}</div>
              <div className="mt-1 text-sm opacity-80">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="mx-auto max-w-6xl px-6 py-20" id="harga">
        <h2 className="mb-4 text-center text-3xl font-extrabold">Harga tumbuh bersama bisnis Anda</h2>
        <p className="mb-12 text-center text-[var(--text-secondary)]">
          Bayar sesuai jumlah klien. Selalu di bawah 3% dari revenue Anda. Gratis 14 hari.
        </p>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[
            {
              name: "Starter",
              price: "Rp 299rb",
              period: "/bulan",
              clients: "Hingga 10 klien",
              desc: "Konsultan baru memulai",
              features: ["WhatsApp OCR otomatis", "Dashboard + Kanban board", "Deadline tracker", "Auto-generate SPT", "Portal upload klien"],
              highlight: false,
              roi: "10 klien x Rp 5jt = Rp 50jt/thn. Pajakia: 7%.",
            },
            {
              name: "Pro",
              price: "Rp 599rb",
              period: "/bulan",
              clients: "Hingga 25 klien",
              desc: "Paling populer",
              features: ["Semua fitur Starter", "Batch processing", "Invoice & revenue tracking", "Auto-reminder WhatsApp", "e-Bupot & e-Faktur CSV"],
              highlight: true,
              roi: "25 klien x Rp 5jt = Rp 125jt/thn. Pajakia: ~6%.",
            },
            {
              name: "Business",
              price: "Rp 999rb",
              period: "/bulan",
              clients: "Hingga 50 klien",
              desc: "Konsultan berkembang",
              features: ["Semua fitur Pro", "Multi-year history", "Anomaly detection", "Data export & compliance", "Priority support"],
              highlight: false,
              roi: "50 klien x Rp 5jt = Rp 250jt/thn. Pajakia: ~5%.",
            },
            {
              name: "Enterprise",
              price: "Rp 1,5jt",
              period: "/bulan",
              clients: "Hingga 100+ klien",
              desc: "Kantor konsultan besar",
              features: ["Semua fitur Business", "Unlimited klien", "2FA + audit log wajib", "API access", "Dedicated onboarding"],
              highlight: false,
              roi: "100 klien x Rp 5jt = Rp 500jt/thn. Pajakia: ~4%.",
            },
          ].map((plan) => (
            <div key={plan.name} className={`rounded-2xl border p-6 ${plan.highlight ? "border-2 border-[var(--primary)] bg-blue-50 shadow-lg relative" : "border-[var(--border)] bg-white"}`}>
              {plan.highlight && <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-[var(--primary)] px-3 py-0.5 text-xs font-bold text-white">POPULER</div>}
              <h3 className="text-lg font-bold">{plan.name}</h3>
              <div className="mt-2 flex items-baseline gap-0.5">
                <span className="text-3xl font-extrabold">{plan.price}</span>
                <span className="text-sm text-[var(--text-secondary)]">{plan.period}</span>
              </div>
              <div className="mt-1 text-sm font-semibold text-[var(--primary)]">{plan.clients}</div>
              <p className="mt-1 text-xs text-[var(--text-secondary)]">{plan.desc}</p>
              <ul className="mt-4 space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-xs"><span className="text-[var(--accent)]">✓</span>{f}</li>
                ))}
              </ul>
              <div className="mt-4 rounded-lg bg-gray-50 p-2 text-center text-[10px] text-[var(--text-secondary)]">{plan.roi}</div>
              <Link
                href="https://wa.me/628131102445?text=Mau%20coba%20Pajakia%20paket%20{plan.name}"
                className={`mt-4 block rounded-lg py-2.5 text-center text-sm font-semibold transition-colors ${plan.highlight ? "bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)]" : "border border-[var(--border)] hover:border-[var(--primary)] hover:text-[var(--primary)]"}`}
              >
                Coba Gratis 14 Hari
              </Link>
            </div>
          ))}
        </div>

        <div className="mx-auto mt-8 max-w-3xl text-center text-sm text-[var(--text-secondary)]">
          Semua paket termasuk: enkripsi AES-256, server Indonesia, backup harian. Tanpa kartu kredit untuk trial.
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-t border-[var(--border)] bg-gradient-to-b from-white to-gray-50">
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <h2 className="mb-4 text-4xl font-extrabold">
            Coba sekarang — kirim satu bukti potong
          </h2>
          <p className="mx-auto mb-8 max-w-xl text-lg text-[var(--text-secondary)]">
            Lihat sendiri bagaimana AI membaca dokumen pajak dalam 10 detik.
            Langsung via WhatsApp, gratis, tanpa daftar.
          </p>
          <Link
            href="https://wa.me/628131102445?text=Halo%20Pajakia%2C%20mau%20coba%20kirim%20bukti%20potong"
            className="inline-flex items-center gap-3 rounded-2xl bg-[#25D366] px-10 py-5 text-xl font-bold text-white shadow-xl hover:bg-[#1da851] hover:shadow-2xl transition-all"
          >
            <svg viewBox="0 0 24 24" className="h-7 w-7 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            Kirim Bukti Potong via WhatsApp
          </Link>
          <div className="mt-4 flex items-center justify-center gap-6 text-sm text-[var(--text-secondary)]">
            <span>🔒 Enkripsi AES-256</span>
            <span>🇮🇩 Server Indonesia</span>
            <span>⚡ Hasil dalam 10 detik</span>
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
                WhatsApp-first tax processing untuk Indonesia
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
