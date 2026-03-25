"use client";

import { useState } from "react";
import Link from "next/link";

const PTKP_OPTIONS = [
  { value: "TK/0", label: "TK/0 — Tidak Kawin, tanpa tanggungan", amount: 54000000 },
  { value: "TK/1", label: "TK/1 — Tidak Kawin, 1 tanggungan", amount: 58500000 },
  { value: "TK/2", label: "TK/2 — Tidak Kawin, 2 tanggungan", amount: 63000000 },
  { value: "TK/3", label: "TK/3 — Tidak Kawin, 3 tanggungan", amount: 67500000 },
  { value: "K/0", label: "K/0 — Kawin, tanpa tanggungan", amount: 58500000 },
  { value: "K/1", label: "K/1 — Kawin, 1 tanggungan", amount: 63000000 },
  { value: "K/2", label: "K/2 — Kawin, 2 tanggungan", amount: 67500000 },
  { value: "K/3", label: "K/3 — Kawin, 3 tanggungan", amount: 72000000 },
];

const BRACKETS = [
  { limit: 60000000, rate: 0.05 },
  { limit: 250000000, rate: 0.15 },
  { limit: 500000000, rate: 0.25 },
  { limit: 5000000000, rate: 0.30 },
  { limit: Infinity, rate: 0.35 },
];

function formatRp(n: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);
}

interface CalcResult {
  grossIncome: number;
  biayaJabatan: number;
  iuranPensiun: number;
  netIncome: number;
  ptkpAmount: number;
  taxableIncome: number;
  taxDue: number;
  taxPaid: number;
  difference: number;
  effectiveRate: number;
  breakdown: { bracket: string; rate: string; amount: number; tax: number }[];
}

function calculate(
  gross: number,
  ptkpStatus: string,
  iuranPensiun: number,
  taxPaid: number
): CalcResult {
  const ptkp = PTKP_OPTIONS.find((p) => p.value === ptkpStatus);
  const ptkpAmount = ptkp?.amount ?? 54000000;
  const biayaJabatan = Math.min(gross * 0.05, 6000000);
  const netIncome = gross - biayaJabatan - iuranPensiun;
  const taxableIncome = Math.max(0, netIncome - ptkpAmount);

  let remaining = taxableIncome;
  let taxDue = 0;
  let prevLimit = 0;
  const breakdown: CalcResult["breakdown"] = [];

  for (const { limit, rate } of BRACKETS) {
    const bracketSize = limit === Infinity ? remaining : limit - prevLimit;
    const taxable = Math.min(remaining, bracketSize);
    if (taxable <= 0) break;
    const tax = taxable * rate;
    taxDue += tax;
    breakdown.push({
      bracket:
        limit === Infinity
          ? `> ${formatRp(prevLimit)}`
          : `${formatRp(prevLimit)} – ${formatRp(limit)}`,
      rate: `${rate * 100}%`,
      amount: taxable,
      tax,
    });
    remaining -= taxable;
    prevLimit = limit;
  }

  const difference = taxDue - taxPaid;
  const effectiveRate = gross > 0 ? (taxDue / gross) * 100 : 0;

  return {
    grossIncome: gross,
    biayaJabatan,
    iuranPensiun,
    netIncome,
    ptkpAmount,
    taxableIncome,
    taxDue,
    taxPaid,
    difference,
    effectiveRate,
    breakdown,
  };
}

export default function KalkulatorPage() {
  const [gross, setGross] = useState("");
  const [ptkp, setPtkp] = useState("TK/0");
  const [iuran, setIuran] = useState("");
  const [paid, setPaid] = useState("");
  const [result, setResult] = useState<CalcResult | null>(null);

  const handleCalc = () => {
    const g = parseFloat(gross.replace(/\D/g, "")) || 0;
    const i = parseFloat(iuran.replace(/\D/g, "")) || 0;
    const p = parseFloat(paid.replace(/\D/g, "")) || 0;
    if (g === 0) return;
    setResult(calculate(g, ptkp, i, p));
  };

  const handleInput = (
    setter: (v: string) => void,
    value: string
  ) => {
    const num = value.replace(/\D/g, "");
    if (num === "") {
      setter("");
      return;
    }
    setter(new Intl.NumberFormat("id-ID").format(parseInt(num)));
  };

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-2xl font-extrabold text-[var(--primary)]">
            PajakAI
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primary-dark)]"
          >
            Dashboard
          </Link>
        </div>
      </nav>

      <div className="mx-auto max-w-4xl px-6 py-12">
        <h1 className="mb-2 text-3xl font-extrabold">Kalkulator PPh 21</h1>
        <p className="mb-8 text-[var(--text-secondary)]">
          Hitung pajak penghasilan karyawan tahun 2025 — metode tarif progresif (UU HPP).
        </p>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Input Form */}
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-lg font-bold">Data Penghasilan</h2>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium">
                  Penghasilan Bruto Setahun *
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[var(--text-secondary)]">
                    Rp
                  </span>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={gross}
                    onChange={(e) => handleInput(setGross, e.target.value)}
                    placeholder="120.000.000"
                    className="w-full rounded-lg border border-[var(--border)] py-3 pl-10 pr-4 text-right text-lg font-semibold focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
                  />
                </div>
                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                  Termasuk gaji, tunjangan, bonus, THR
                </p>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">
                  Status PTKP
                </label>
                <select
                  value={ptkp}
                  onChange={(e) => setPtkp(e.target.value)}
                  className="w-full rounded-lg border border-[var(--border)] px-4 py-3 focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  {PTKP_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">
                  Iuran Pensiun/THT Setahun
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[var(--text-secondary)]">
                    Rp
                  </span>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={iuran}
                    onChange={(e) => handleInput(setIuran, e.target.value)}
                    placeholder="0"
                    className="w-full rounded-lg border border-[var(--border)] py-3 pl-10 pr-4 text-right focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">
                  PPh 21 Sudah Dipotong (dari Bukti Potong)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[var(--text-secondary)]">
                    Rp
                  </span>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={paid}
                    onChange={(e) => handleInput(setPaid, e.target.value)}
                    placeholder="0"
                    className="w-full rounded-lg border border-[var(--border)] py-3 pl-10 pr-4 text-right focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-blue-100"
                  />
                </div>
              </div>

              <button
                onClick={handleCalc}
                className="w-full rounded-lg bg-[var(--primary)] py-3 text-lg font-bold text-white hover:bg-[var(--primary-dark)] transition-colors"
              >
                Hitung PPh 21
              </button>
            </div>
          </div>

          {/* Result */}
          <div>
            {result ? (
              <div className="space-y-4">
                {/* Summary Card */}
                <div className="rounded-2xl border border-[var(--primary)] bg-blue-50 p-6">
                  <div className="text-sm font-medium text-[var(--primary)]">
                    PPh 21 Terutang
                  </div>
                  <div className="mt-1 text-4xl font-extrabold text-[var(--text)]">
                    {formatRp(result.taxDue)}
                  </div>
                  <div className="mt-2 text-sm text-[var(--text-secondary)]">
                    Tarif efektif: {result.effectiveRate.toFixed(2)}%
                  </div>

                  {result.taxPaid > 0 && (
                    <div
                      className={`mt-4 rounded-lg p-3 ${
                        result.difference > 0
                          ? "bg-red-100 text-red-800"
                          : result.difference < 0
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      <div className="text-sm font-medium">
                        {result.difference > 0
                          ? "Kurang Bayar"
                          : result.difference < 0
                          ? "Lebih Bayar (Restitusi)"
                          : "Nihil"}
                      </div>
                      <div className="text-xl font-bold">
                        {formatRp(Math.abs(result.difference))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Calculation Steps */}
                <div className="rounded-2xl border border-[var(--border)] bg-white p-6 shadow-sm">
                  <h3 className="mb-4 font-bold">Perhitungan</h3>
                  <div className="space-y-2 text-sm">
                    <Row label="Penghasilan Bruto" value={result.grossIncome} />
                    <Row
                      label="Biaya Jabatan (5%, maks 6jt)"
                      value={-result.biayaJabatan}
                      negative
                    />
                    {result.iuranPensiun > 0 && (
                      <Row
                        label="Iuran Pensiun"
                        value={-result.iuranPensiun}
                        negative
                      />
                    )}
                    <div className="border-t border-[var(--border)] pt-2">
                      <Row label="Penghasilan Neto" value={result.netIncome} bold />
                    </div>
                    <Row label={`PTKP (${ptkp})`} value={-result.ptkpAmount} negative />
                    <div className="border-t border-[var(--border)] pt-2">
                      <Row
                        label="Penghasilan Kena Pajak (PKP)"
                        value={result.taxableIncome}
                        bold
                      />
                    </div>
                  </div>
                </div>

                {/* Tax Brackets */}
                {result.breakdown.length > 0 && (
                  <div className="rounded-2xl border border-[var(--border)] bg-white p-6 shadow-sm">
                    <h3 className="mb-4 font-bold">Tarif Progresif</h3>
                    <div className="space-y-3">
                      {result.breakdown.map((b, i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between text-sm"
                        >
                          <div>
                            <span className="font-medium">{b.rate}</span>
                            <span className="ml-2 text-[var(--text-secondary)]">
                              × {formatRp(b.amount)}
                            </span>
                          </div>
                          <div className="font-semibold">{formatRp(b.tax)}</div>
                        </div>
                      ))}
                      <div className="border-t border-[var(--border)] pt-2 flex justify-between font-bold">
                        <span>Total PPh 21</span>
                        <span>{formatRp(result.taxDue)}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* CTA */}
                <div className="rounded-2xl border border-[var(--border)] bg-white p-6 text-center shadow-sm">
                  <p className="mb-3 text-sm text-[var(--text-secondary)]">
                    Mau langsung siapkan SPT Tahunan Anda?
                  </p>
                  <Link
                    href="/dashboard"
                    className="inline-block rounded-lg bg-[var(--primary)] px-6 py-3 font-semibold text-white hover:bg-[var(--primary-dark)]"
                  >
                    Siapkan SPT — Rp 99.000
                  </Link>
                </div>
              </div>
            ) : (
              <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-[var(--border)] bg-white p-12">
                <div className="text-center">
                  <div className="mb-3 text-5xl">🧮</div>
                  <p className="text-[var(--text-secondary)]">
                    Masukkan penghasilan bruto Anda
                    <br />
                    dan klik "Hitung PPh 21"
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  negative,
  bold,
}: {
  label: string;
  value: number;
  negative?: boolean;
  bold?: boolean;
}) {
  return (
    <div className={`flex justify-between ${bold ? "font-bold" : ""}`}>
      <span className={negative ? "text-[var(--text-secondary)]" : ""}>
        {label}
      </span>
      <span className={negative ? "text-red-600" : ""}>
        {negative && value < 0 ? "- " : ""}
        {formatRp(Math.abs(value))}
      </span>
    </div>
  );
}
