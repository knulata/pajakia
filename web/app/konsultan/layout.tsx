"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/konsultan", label: "Dashboard", icon: "📊" },
  { href: "/konsultan/klien", label: "Klien", icon: "👥" },
  { href: "/konsultan/deadline", label: "Deadline", icon: "📅" },
  { href: "/konsultan/batch", label: "Batch", icon: "⚡" },
  { href: "/konsultan/analytics", label: "Analitik", icon: "📈" },
];

export default function ConsultantLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      {/* Top Nav */}
      <nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-2xl font-extrabold text-[var(--primary)]">
            Pajakia
          </Link>
          <div className="flex items-center gap-4">
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
        {/* Tab Nav */}
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

        {children}
      </div>
    </div>
  );
}
