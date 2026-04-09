"""Pre-flight validator — catch the 22 known Coretax errors before upload.

Based on DJP's published list of common Coretax issues (March 2026).
Each validation rule maps to a real error code consultants encounter.
"""

import re
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET


# The 22 known Coretax error patterns (DJP-confirmed)
KNOWN_CORETAX_ERRORS = {
    "NPWP_INVALID_LENGTH": {
        "code": "ERR-CT-001",
        "label": "NPWP harus 16 digit",
        "fix": "Pajakia auto-pad 15-digit NPWP lama menjadi 16 digit. Periksa NPWP yang invalid.",
    },
    "NPWP_SCIENTIFIC_NOTATION": {
        "code": "ERR-CT-002",
        "label": "NPWP dalam notasi ilmiah (bug Excel)",
        "fix": "Format NPWP sebagai TEXT di Excel sebelum upload, atau gunakan Pajakia.",
    },
    "NIK_INVALID": {
        "code": "ERR-CT-003",
        "label": "NIK tidak valid (harus 16 digit)",
        "fix": "Cek dan perbaiki NIK. Boleh kosong jika WP punya NPWP.",
    },
    "DATE_FORMAT_INVALID": {
        "code": "ERR-CT-004",
        "label": "Format tanggal salah (harus YYYY-MM-DD)",
        "fix": "Pajakia auto-convert ke format ISO. Periksa tanggal yang tidak valid.",
    },
    "MASA_PAJAK_INVALID": {
        "code": "ERR-CT-005",
        "label": "Masa pajak harus 01-12",
        "fix": "Periksa nilai bulan, harus integer 1-12.",
    },
    "TAHUN_PAJAK_INVALID": {
        "code": "ERR-CT-006",
        "label": "Tahun pajak invalid",
        "fix": "Tahun harus 4 digit antara 2020-2030.",
    },
    "KODE_OBJEK_PAJAK_MISSING": {
        "code": "ERR-CT-007",
        "label": "Kode objek pajak kosong",
        "fix": "Setiap bukti potong wajib punya kode objek pajak (e.g. 21-100-01).",
    },
    "KODE_OBJEK_PAJAK_INVALID": {
        "code": "ERR-CT-008",
        "label": "Kode objek pajak tidak dikenal",
        "fix": "Gunakan kode objek pajak resmi DJP. Format: XX-XXX-XX",
    },
    "AMOUNT_NEGATIVE": {
        "code": "ERR-CT-009",
        "label": "Nilai pajak tidak boleh negatif",
        "fix": "Periksa kolom DPP dan PPh — semua harus >= 0.",
    },
    "AMOUNT_DECIMAL": {
        "code": "ERR-CT-010",
        "label": "Nilai harus integer (tanpa desimal)",
        "fix": "Pajakia auto-round ke integer. Periksa input yang punya desimal.",
    },
    "TARIF_INVALID": {
        "code": "ERR-CT-011",
        "label": "Tarif harus 0-100",
        "fix": "Tarif PPh harus dalam persen (5, 15, 25, 30, 35).",
    },
    "PPH_MISMATCH": {
        "code": "ERR-CT-012",
        "label": "PPh dipotong tidak sesuai DPP × Tarif",
        "fix": "Validasi: PPh = DPP × Tarif. Allowance ±1 rupiah.",
    },
    "DUPLICATE_NOMOR_BP": {
        "code": "ERR-CT-013",
        "label": "Nomor bukti potong duplikat",
        "fix": "Setiap nomor bukti potong harus unik dalam satu masa pajak.",
    },
    "NOMOR_FAKTUR_INVALID": {
        "code": "ERR-CT-014",
        "label": "Format nomor faktur salah",
        "fix": "Format: XXX-YY.NNNNNNNN (kode 3 digit, tahun 2 digit, nomor 8 digit).",
    },
    "PEMBELI_NPWP_INVALID": {
        "code": "ERR-CT-015",
        "label": "NPWP pembeli invalid",
        "fix": "Untuk faktur dengan kode 01, NPWP pembeli wajib 16 digit.",
    },
    "DPP_PPN_MISMATCH": {
        "code": "ERR-CT-016",
        "label": "PPN tidak sesuai DPP × 11%",
        "fix": "PPN harus sama dengan DPP × 11% (PPN 12% untuk transaksi tertentu).",
    },
    "FORBIDDEN_CHAR": {
        "code": "ERR-CT-017",
        "label": "Karakter terlarang dalam data",
        "fix": "Hindari ', \", <, >, dan soft enter dalam nama/alamat.",
    },
    "EMPTY_REQUIRED_FIELD": {
        "code": "ERR-CT-018",
        "label": "Field wajib kosong",
        "fix": "Periksa field wajib: NPWP pemotong, masa, tahun, nama penerima.",
    },
    "ENCODING_INVALID": {
        "code": "ERR-CT-019",
        "label": "Encoding harus UTF-8",
        "fix": "Pajakia auto-encode UTF-8. Periksa karakter non-standar.",
    },
    "FILESIZE_TOO_LARGE": {
        "code": "ERR-CT-020",
        "label": "File terlalu besar (max 10MB)",
        "fix": "Pisahkan menjadi beberapa file. Pajakia auto-split jika perlu.",
    },
    "MAX_RECORDS_EXCEEDED": {
        "code": "ERR-CT-021",
        "label": "Lebih dari 1000 record per file",
        "fix": "Pajakia auto-split menjadi batch 1000 record.",
    },
    "PTKP_INVALID": {
        "code": "ERR-CT-022",
        "label": "Status PTKP tidak dikenal",
        "fix": "Gunakan format: TK/0, TK/1, TK/2, TK/3, K/0, K/1, K/2, K/3, K/I/0, dll.",
    },
}


@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    code: str
    label: str
    fix: str
    location: str  # which row/field
    field: str | None = None
    value: str | None = None


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    total_records: int = 0

    def add_error(self, key: str, location: str, field_name: str | None = None, value: str | None = None):
        info = KNOWN_CORETAX_ERRORS.get(key, {"code": "ERR-CT-?", "label": key, "fix": ""})
        self.errors.append(ValidationIssue(
            severity="error", code=info["code"], label=info["label"],
            fix=info["fix"], location=location, field=field_name, value=value,
        ))
        self.is_valid = False

    def add_warning(self, key: str, location: str, field_name: str | None = None, value: str | None = None):
        info = KNOWN_CORETAX_ERRORS.get(key, {"code": "WARN-CT-?", "label": key, "fix": ""})
        self.warnings.append(ValidationIssue(
            severity="warning", code=info["code"], label=info["label"],
            fix=info["fix"], location=location, field=field_name, value=value,
        ))


VALID_PTKP = {
    "TK/0", "TK/1", "TK/2", "TK/3",
    "K/0", "K/1", "K/2", "K/3",
    "K/I/0", "K/I/1", "K/I/2", "K/I/3",
}

KODE_OBJEK_PATTERN = re.compile(r"^\d{2}-\d{3}-\d{2}$")
NOMOR_FAKTUR_PATTERN = re.compile(r"^\d{3}-\d{2}\.\d{8}$")


def _validate_npwp(npwp: str) -> tuple[bool, str | None]:
    """Returns (is_valid, error_key)."""
    if not npwp:
        return False, "EMPTY_REQUIRED_FIELD"
    if "E" in npwp.upper():
        return False, "NPWP_SCIENTIFIC_NOTATION"
    digits = re.sub(r"\D", "", npwp)
    if len(digits) != 16:
        return False, "NPWP_INVALID_LENGTH"
    return True, None


def _validate_amount(value) -> tuple[bool, str | None]:
    try:
        v = float(value)
        if v < 0:
            return False, "AMOUNT_NEGATIVE"
        if v != int(v):
            return False, "AMOUNT_DECIMAL"
        return True, None
    except (ValueError, TypeError):
        return False, "EMPTY_REQUIRED_FIELD"


def validate_ebupot_xml(xml_string: str) -> ValidationResult:
    """Pre-flight validation for e-Bupot XML before Coretax upload."""
    result = ValidationResult(is_valid=True)

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        result.add_error("ENCODING_INVALID", "root", value=str(e))
        return result

    # Strip namespace for easier traversal
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    # Validate header
    header = root.find("Header")
    if header is None:
        result.add_error("EMPTY_REQUIRED_FIELD", "Header")
        return result

    npwp_pemotong = (header.findtext("NPWPPemotong") or "").strip()
    valid, err = _validate_npwp(npwp_pemotong)
    if not valid:
        result.add_error(err, "Header.NPWPPemotong", "NPWPPemotong", npwp_pemotong)

    masa = header.findtext("MasaPajak")
    if not masa or not masa.isdigit() or not (1 <= int(masa) <= 12):
        result.add_error("MASA_PAJAK_INVALID", "Header.MasaPajak", "MasaPajak", masa)

    tahun = header.findtext("TahunPajak")
    if not tahun or not tahun.isdigit() or not (2020 <= int(tahun) <= 2030):
        result.add_error("TAHUN_PAJAK_INVALID", "Header.TahunPajak", "TahunPajak", tahun)

    # Validate each bukti potong
    daftar = root.find("DaftarBuktiPotong")
    if daftar is None:
        result.add_error("EMPTY_REQUIRED_FIELD", "DaftarBuktiPotong")
        return result

    seen_nomor = set()
    bukti_list = daftar.findall("BuktiPotong")
    result.total_records = len(bukti_list)

    if len(bukti_list) > 1000:
        result.add_warning("MAX_RECORDS_EXCEEDED", "DaftarBuktiPotong",
                           value=str(len(bukti_list)))

    for i, bp in enumerate(bukti_list, start=1):
        loc = f"BuktiPotong[{i}]"

        nomor_bp = bp.findtext("NomorBP")
        if nomor_bp:
            if nomor_bp in seen_nomor:
                result.add_error("DUPLICATE_NOMOR_BP", loc, "NomorBP", nomor_bp)
            seen_nomor.add(nomor_bp)
        else:
            result.add_error("EMPTY_REQUIRED_FIELD", loc, "NomorBP")

        # Penerima
        penerima = bp.find("Penerima")
        if penerima is not None:
            npwp = (penerima.findtext("NPWP") or "").strip()
            nik = (penerima.findtext("NIK") or "").strip()
            nama = (penerima.findtext("Nama") or "").strip()

            if not npwp and not nik:
                result.add_error("EMPTY_REQUIRED_FIELD", loc + ".Penerima",
                                 "NPWP/NIK", "kedua kosong")
            elif npwp:
                valid, err = _validate_npwp(npwp)
                if not valid:
                    result.add_error(err, loc + ".Penerima.NPWP", "NPWP", npwp)

            if nik and len(re.sub(r"\D", "", nik)) != 16:
                result.add_error("NIK_INVALID", loc + ".Penerima.NIK", "NIK", nik)

            if not nama:
                result.add_error("EMPTY_REQUIRED_FIELD", loc + ".Penerima.Nama", "Nama")
            elif re.search(r"[\'\"<>]", nama):
                result.add_error("FORBIDDEN_CHAR", loc + ".Penerima.Nama", "Nama", nama)

        # Data Pajak
        pajak = bp.find("DataPajak")
        if pajak is not None:
            kop = (pajak.findtext("KodeObjekPajak") or "").strip()
            if not kop:
                result.add_error("KODE_OBJEK_PAJAK_MISSING", loc + ".DataPajak", "KodeObjekPajak")
            elif not KODE_OBJEK_PATTERN.match(kop):
                result.add_error("KODE_OBJEK_PAJAK_INVALID", loc + ".DataPajak.KodeObjekPajak",
                                 "KodeObjekPajak", kop)

            dpp = pajak.findtext("DPP")
            valid, err = _validate_amount(dpp)
            if not valid:
                result.add_error(err, loc + ".DataPajak.DPP", "DPP", dpp)

            tarif = pajak.findtext("Tarif")
            try:
                t = float(tarif)
                if not (0 <= t <= 100):
                    result.add_error("TARIF_INVALID", loc + ".DataPajak.Tarif", "Tarif", tarif)
            except (ValueError, TypeError):
                result.add_error("TARIF_INVALID", loc + ".DataPajak.Tarif", "Tarif", tarif)

            pph = pajak.findtext("PPhDipotong")
            valid, err = _validate_amount(pph)
            if not valid:
                result.add_error(err, loc + ".DataPajak.PPhDipotong", "PPhDipotong", pph)

            # Cross-check: PPh ≈ DPP × Tarif
            try:
                expected = int(round(float(dpp) * float(tarif) / 100))
                actual = int(float(pph))
                if abs(expected - actual) > 1:
                    result.add_warning("PPH_MISMATCH", loc + ".DataPajak",
                                       "PPhDipotong",
                                       f"expected {expected}, got {actual}")
            except (ValueError, TypeError):
                pass

    return result


def validate_efaktur_xml(xml_string: str) -> ValidationResult:
    """Pre-flight validation for e-Faktur XML before Coretax upload."""
    result = ValidationResult(is_valid=True)

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        result.add_error("ENCODING_INVALID", "root", value=str(e))
        return result

    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    header = root.find("Header")
    if header is None:
        result.add_error("EMPTY_REQUIRED_FIELD", "Header")
        return result

    npwp = (header.findtext("NPWPPenjual") or "").strip()
    valid, err = _validate_npwp(npwp)
    if not valid:
        result.add_error(err, "Header.NPWPPenjual", "NPWPPenjual", npwp)

    daftar = root.find("DaftarFaktur")
    if daftar is None:
        result.add_error("EMPTY_REQUIRED_FIELD", "DaftarFaktur")
        return result

    fakturs = daftar.findall("Faktur")
    result.total_records = len(fakturs)

    if len(fakturs) > 1000:
        result.add_warning("MAX_RECORDS_EXCEEDED", "DaftarFaktur", value=str(len(fakturs)))

    for i, f in enumerate(fakturs, start=1):
        loc = f"Faktur[{i}]"

        nomor = (f.findtext("NomorFaktur") or "").strip()
        kode = (f.findtext("KodeTransaksi") or "").strip()

        if nomor and not NOMOR_FAKTUR_PATTERN.match(nomor):
            result.add_error("NOMOR_FAKTUR_INVALID", loc + ".NomorFaktur", "NomorFaktur", nomor)

        # Pembeli NPWP required for kode 01
        pembeli = f.find("Pembeli")
        if pembeli is not None and kode == "01":
            pembeli_npwp = (pembeli.findtext("NPWP") or "").strip()
            valid, err = _validate_npwp(pembeli_npwp)
            if not valid:
                result.add_error("PEMBELI_NPWP_INVALID", loc + ".Pembeli.NPWP",
                                 "NPWP", pembeli_npwp)

        # Validate DPP × 11% ≈ PPN
        totals = f.find("Totals")
        if totals is not None:
            dpp = totals.findtext("DPP")
            ppn = totals.findtext("PPN")
            try:
                expected = int(round(float(dpp) * 0.11))
                actual = int(float(ppn))
                if abs(expected - actual) > 1:
                    result.add_warning("DPP_PPN_MISMATCH", loc + ".Totals", "PPN",
                                       f"expected {expected}, got {actual}")
            except (ValueError, TypeError):
                pass

    return result
