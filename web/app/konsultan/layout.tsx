"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/konsultan", label: "Dashboard", icon: "📊" },
  { href: "/konsultan/klien", label: "Klien", icon: "👥" },
  { href: "/konsultan/board", label: "Progress SPT", icon: "📋" },
  { href: "/konsultan/coretax", label: "Coretax", icon: "🚀" },
  { href: "/konsultan/deadline", label: "Deadline", icon: "📅" },
  { href: "/konsultan/dokumen", label: "Dokumen", icon: "📄" },
  { href: "/konsultan/invoice", label: "Invoice", icon: "💰" },
  { href: "/konsultan/batch", label: "Batch", icon: "⚡" },
  { href: "/konsultan/analytics", label: "Analitik", icon: "📈" },
  { href: "/konsultan/keamanan", label: "Keamanan", icon: "🔒" },
];

export default function ConsultantLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <svg width="28" height="28" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
              <rect width="64" height="64" rx="16" fill="#1a56db"/>
              <text x="32" y="45" textAnchor="middle" fontFamily="system-ui" fontWeight="800" fontSize="36" fill="white" letterSpacing="-2">P</text>
              <circle cx="44" cy="18" r="6" fill="#25D366" opacity="0.9"/>
              <path d="M41.5 18l2 2 3-3" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span className="text-xl font-extrabold text-[var(--primary)]">Pajakia</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/konsultan/activity"
              className="text-sm text-[var(--text-secondary)] hover:text-[var(--text)]"
            >
              Log Aktivitas
            </Link>
            <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
              Konsultan
            </span>
            <div className="h-8 w-8 rounded-full bg-[var(--primary)] flex items-center justify-center text-white text-sm font-bold">
              K
            </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-6 py-6">
        <div className="mb-6 flex gap-1 overflow-x-auto rounded-lg bg-gray-100 p-1">
          {navItems.map((item) => {
            const isActive =
              item.href === "/konsultan"
                ? pathname === "/konsultan"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 whitespace-nowrap rounded-md px-4 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-white text-[var(--text)] shadow-sm"
                    : "text-[var(--text-secondary)] hover:text-[var(--text)]"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </div>

        <div className="mb-4 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-sm font-bold text-blue-900">Mode demo konsultan</div>
              <p className="text-xs text-blue-800">
                Data di dashboard ini adalah contoh. Fitur yang bisa dicoba langsung: Coretax XML generator, validator, error decoder, dan kalkulator PPh 21.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link
                href="/konsultan/coretax"
                className="rounded-lg bg-[var(--primary)] px-3 py-2 text-xs font-semibold text-white hover:bg-[var(--primary-dark)]"
              >
                Mulai demo Coretax
              </Link>
              <Link
                href="https://wa.me/628131102445?text=Halo%20Pajakia%2C%20saya%20mau%20ikut%20pilot%20konsultan%20pajak"
                className="rounded-lg border border-blue-300 bg-white px-3 py-2 text-xs font-semibold text-blue-800 hover:bg-blue-100"
              >
                Ikut pilot
              </Link>
            </div>
          </div>
        </div>

        {children}
      </div>
    </div>
  );
}
