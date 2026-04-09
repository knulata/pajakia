"""Decode Coretax error messages — paste the cryptic message, get the fix.

Coretax often returns errors like:
- "ERR-7823: Submission rejected"
- "Invalid NPWP format in row 14"
- "File contains forbidden characters"

This module maps known error patterns to plain-language explanations and fixes.
"""

import re
from dataclasses import dataclass


@dataclass
class DecodedError:
    code: str
    title: str
    explanation: str
    fix: str
    severity: str  # "critical" | "warning" | "info"
    auto_fixable: bool


# Pattern → DecodedError mapping. Order matters (most specific first).
ERROR_PATTERNS: list[tuple[str, DecodedError]] = [
    (
        r"(?i)npwp.*15.*digit|npwp.*length.*15",
        DecodedError(
            code="NPWP_OLD_FORMAT",
            title="NPWP masih format 15 digit lama",
            explanation="Sejak 2024, Coretax wajib NPWP 16 digit. NPWP 15 digit perlu di-pad dengan '0' di depan.",
            fix="Pajakia auto-pad NPWP 15 digit menjadi 16 digit. Jalankan ulang upload.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)scientific.*notation|1\.\d+e\+",
        DecodedError(
            code="EXCEL_SCIENTIFIC",
            title="Excel mengubah NPWP jadi notasi ilmiah",
            explanation="Microsoft Excel otomatis convert angka panjang (NPWP, NIK) ke format 1.23E+15. Coretax menolak ini.",
            fix="Format kolom NPWP/NIK sebagai 'Text' di Excel SEBELUM mengetik data. Atau pakai Pajakia yang otomatis fix ini.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)forbidden.*character|invalid.*character|illegal.*character",
        DecodedError(
            code="FORBIDDEN_CHAR",
            title="Karakter terlarang dalam data",
            explanation="Coretax menolak karakter: ' (apostrophe), \" (quote), <, >, soft enter (Shift+Enter), dan beberapa karakter Unicode.",
            fix="Hapus karakter terlarang dari nama, alamat, dan keterangan. Pajakia auto-clean.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)file.*too.*large|exceeds.*size.*limit",
        DecodedError(
            code="FILE_TOO_LARGE",
            title="File lebih dari 10MB",
            explanation="Coretax membatasi upload file maksimal 10MB.",
            fix="Pisahkan menjadi beberapa file. Pajakia auto-split jika lebih dari 1000 record.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)duplicate.*nomor|nomor.*duplicate|nomor bukti.*sudah ada",
        DecodedError(
            code="DUPLICATE_NOMOR",
            title="Nomor bukti potong duplikat",
            explanation="Setiap nomor bukti potong harus unik dalam satu masa pajak.",
            fix="Gunakan nomor unik untuk setiap bukti potong. Pajakia auto-generate nomor jika kosong.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)invalid.*date|format.*tanggal|date.*format",
        DecodedError(
            code="INVALID_DATE",
            title="Format tanggal salah",
            explanation="Coretax wajib format ISO YYYY-MM-DD (contoh: 2025-12-31). Format DD/MM/YYYY ditolak.",
            fix="Pajakia auto-convert semua format tanggal ke ISO. Atau gunakan format YYYY-MM-DD secara manual.",
            severity="critical",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)kode.*objek.*pajak|kop.*invalid|invalid.*tax.*code",
        DecodedError(
            code="INVALID_KOP",
            title="Kode Objek Pajak tidak valid",
            explanation="Kode Objek Pajak harus format XX-XXX-XX (contoh: 21-100-01 untuk gaji karyawan).",
            fix="Cek daftar Kode Objek Pajak resmi DJP. Pajakia punya database lengkap kode KOP.",
            severity="critical",
            auto_fixable=False,
        ),
    ),
    (
        r"(?i)session.*expired|timeout|sesi.*berakhir",
        DecodedError(
            code="SESSION_EXPIRED",
            title="Sesi Coretax kedaluwarsa",
            explanation="Coretax sering timeout setelah 15-30 menit idle. Draft Anda hilang.",
            fix="Pajakia browser extension auto-save draft setiap 30 detik. Login ulang dan resume dari Pajakia.",
            severity="warning",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)maintenance|sedang dalam pemeliharaan|service.*unavailable|503",
        DecodedError(
            code="MAINTENANCE",
            title="Coretax sedang maintenance",
            explanation="DJP Coretax sering downtime untuk pemeliharaan, biasanya 4-8 jam.",
            fix="Pajakia simpan submission Anda di queue. Akan auto-retry begitu Coretax up. Cek status: pajak.go.id",
            severity="warning",
            auto_fixable=True,
        ),
    ),
    (
        r"(?i)faktur.*tidak.*muncul|data.*tidak.*tampil|missing.*data",
        DecodedError(
            code="DATA_NOT_DISPLAYED",
            title="Data faktur tidak muncul setelah upload",
            explanation="Bug Coretax: kadang data sudah terupload tapi tidak ditampilkan di dashboard. DJP konfirmasi ini.",
            fix="Tunggu 5-10 menit, refresh halaman. Jika tetap tidak muncul, cek di menu 'Riwayat Upload'. Data biasanya tetap masuk database.",
            severity="warning",
            auto_fixable=False,
        ),
    ),
    (
        r"(?i)e-?bupot|bukti.*potong",
        DecodedError(
            code="EBUPOT_GENERIC",
            title="Error pada upload e-Bupot",
            explanation="Error spesifik tidak terdeteksi dari pesan. Kemungkinan penyebab: format XML salah, NPWP invalid, atau kode objek pajak tidak dikenal.",
            fix="Jalankan validator Pajakia sebelum upload. Validator akan deteksi 22 jenis error Coretax.",
            severity="warning",
            auto_fixable=False,
        ),
    ),
    (
        r"(?i)e-?faktur",
        DecodedError(
            code="EFAKTUR_GENERIC",
            title="Error pada upload e-Faktur",
            explanation="Error spesifik tidak terdeteksi. Kemungkinan: nomor faktur salah format, NPWP pembeli invalid, atau DPP/PPN tidak konsisten.",
            fix="Jalankan validator Pajakia. Pastikan nomor faktur format XXX-YY.NNNNNNNN dan PPN = DPP × 11%.",
            severity="warning",
            auto_fixable=False,
        ),
    ),
]


def decode_error_code(error_message: str) -> DecodedError | None:
    """Try to match an error message to a known pattern.

    Returns None if no pattern matches.
    """
    if not error_message:
        return None

    msg = error_message.strip()

    for pattern, decoded in ERROR_PATTERNS:
        if re.search(pattern, msg):
            return decoded

    return None


def suggest_fix(error_message: str) -> dict:
    """Decode an error and return a JSON-friendly dict with the fix.

    Returns a generic "unknown" response if the error doesn't match any known pattern.
    """
    decoded = decode_error_code(error_message)

    if decoded:
        return {
            "matched": True,
            "code": decoded.code,
            "title": decoded.title,
            "explanation": decoded.explanation,
            "fix": decoded.fix,
            "severity": decoded.severity,
            "auto_fixable": decoded.auto_fixable,
            "original_message": error_message,
        }

    return {
        "matched": False,
        "code": "UNKNOWN",
        "title": "Error tidak dikenal",
        "explanation": "Pesan error ini belum ada dalam database Pajakia.",
        "fix": "Coba: 1) Cek format file, 2) Validasi NPWP, 3) Hubungi support Pajakia dengan screenshot error ini.",
        "severity": "warning",
        "auto_fixable": False,
        "original_message": error_message,
    }
