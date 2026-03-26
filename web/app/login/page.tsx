"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle OAuth callback — check for code in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (code) {
      handleCallback(code);
    }
  }, []);

  async function handleCallback(code: string) {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/auth/google/callback?code=${encodeURIComponent(code)}`
      );
      if (!res.ok) throw new Error("Login gagal. Silakan coba lagi.");
      const data = await res.json();

      if (data.requires_2fa) {
        // Store temp token and redirect to 2FA page
        localStorage.setItem("pajakia_temp_token", data.temp_token);
        window.location.href = "/login/2fa";
        return;
      }

      // Store tokens
      localStorage.setItem("pajakia_token", data.access_token);
      localStorage.setItem("pajakia_refresh_token", data.refresh_token);
      localStorage.setItem("pajakia_user", JSON.stringify(data.user));

      // Redirect based on role
      if (data.user.role === "consultant" || data.user.role === "admin") {
        window.location.href = "/konsultan";
      } else {
        window.location.href = "/dashboard";
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Login gagal");
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/google/login`);
      const data = await res.json();
      window.location.href = data.url;
    } catch {
      setError("Tidak dapat terhubung ke server. Coba lagi.");
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--bg)]">
      <div className="w-full max-w-md px-6">
        {/* Logo */}
        <div className="mb-8 text-center">
          <Link href="/" className="text-3xl font-extrabold text-[var(--primary)]">
            Pajakia
          </Link>
          <p className="mt-2 text-[var(--text-secondary)]">
            Masuk ke dashboard Anda
          </p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl border border-[var(--border)] bg-white p-8 shadow-sm">
          {loading ? (
            <div className="py-8 text-center">
              <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-[var(--primary)] border-t-transparent"></div>
              <p className="text-sm text-[var(--text-secondary)]">Memproses login...</p>
            </div>
          ) : (
            <>
              {error && (
                <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* Google Login Button */}
              <button
                onClick={handleGoogleLogin}
                className="flex w-full items-center justify-center gap-3 rounded-xl border-2 border-[var(--border)] bg-white px-6 py-4 text-base font-semibold text-[var(--text)] transition-all hover:border-[var(--primary)] hover:shadow-md"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Masuk dengan Google
              </button>

              {/* Divider */}
              <div className="my-6 flex items-center gap-3">
                <div className="h-px flex-1 bg-[var(--border)]"></div>
                <span className="text-xs text-[var(--text-secondary)]">atau</span>
                <div className="h-px flex-1 bg-[var(--border)]"></div>
              </div>

              {/* WhatsApp Login */}
              <Link
                href="https://wa.me/628131102445?text=Halo%20Pajakia%2C%20saya%20mau%20daftar"
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-[#25D366] px-6 py-4 text-base font-semibold text-white transition-all hover:bg-[#1da851]"
              >
                <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                Daftar via WhatsApp
              </Link>
            </>
          )}
        </div>

        {/* Trust signals */}
        <div className="mt-6 flex items-center justify-center gap-4 text-xs text-[var(--text-secondary)]">
          <span>🔒 Enkripsi AES-256</span>
          <span>🇮🇩 Server Indonesia</span>
        </div>

        {/* Back to home */}
        <div className="mt-4 text-center">
          <Link href="/" className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]">
            ← Kembali ke beranda
          </Link>
        </div>
      </div>
    </div>
  );
}
