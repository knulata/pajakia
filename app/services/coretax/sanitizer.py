"""Sanitize data fields to prevent the most common Coretax upload failures.

Common Coretax bugs this fixes:
- Excel converting NPWP to scientific notation (e.g., 1.23E+15)
- NPWP/NIK with wrong digit count or stray separators
- Filenames with forbidden characters (apostrophes, quotes, soft enters)
- Currency values with thousand separators or "Rp" prefix
- Date formats that don't match Coretax's expected ISO format
"""

import re
from datetime import datetime, date


# Coretax forbids these characters in filenames
FORBIDDEN_FILENAME_CHARS = r"[\'\"<>:|?*\x00-\x1f]"


def sanitize_npwp(value: str | int | float | None) -> str:
    """Force NPWP to a 16-digit string (Coretax-compatible).

    Handles:
    - Scientific notation from Excel ("1.23E+15")
    - Old 15-digit format (auto-pads with leading 0)
    - Numbers with separators ("01.234.567.8-901.000")
    - Float representations ("12345678901234.0")

    Returns empty string if input is invalid.
    """
    if value is None or value == "":
        return ""

    # Convert to string, handle floats from Excel
    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        # Avoid scientific notation
        s = f"{int(value):d}" if value.is_integer() else f"{value:.0f}"
    else:
        s = str(value).strip()

    # Handle scientific notation
    if "E" in s.upper():
        try:
            s = f"{int(float(s)):d}"
        except ValueError:
            return ""

    # Strip all non-digit characters
    digits = re.sub(r"\D", "", s)

    if not digits:
        return ""

    # Coretax requires 16 digits (NPWP 16 since 2024 reform)
    # Old 15-digit NPWPs are padded with leading 0
    if len(digits) == 15:
        digits = "0" + digits
    elif len(digits) < 15:
        # Probably invalid, but pad anyway
        digits = digits.zfill(16)
    elif len(digits) > 16:
        # Truncate (shouldn't happen but defensive)
        digits = digits[:16]

    return digits


def sanitize_nik(value: str | int | float | None) -> str:
    """Force NIK to a 16-digit string. Same Excel scientific-notation issue as NPWP."""
    if value is None or value == "":
        return ""

    if isinstance(value, float):
        if value != value:
            return ""
        s = f"{int(value):d}" if value.is_integer() else f"{value:.0f}"
    else:
        s = str(value).strip()

    if "E" in s.upper():
        try:
            s = f"{int(float(s)):d}"
        except ValueError:
            return ""

    digits = re.sub(r"\D", "", s)
    if not digits:
        return ""

    return digits.zfill(16)[:16]


def sanitize_filename(name: str) -> str:
    """Strip characters that Coretax silently rejects.

    Coretax rejects: apostrophes, double quotes, soft enters, control chars,
    angle brackets, colons, pipes, question marks, asterisks.
    """
    if not name:
        return "document"

    # Replace forbidden chars with underscore
    cleaned = re.sub(FORBIDDEN_FILENAME_CHARS, "_", name)

    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Strip soft enters / line separators
    cleaned = cleaned.replace("\u2028", "").replace("\u2029", "")

    # Coretax doesn't like leading/trailing dots
    cleaned = cleaned.strip(".")

    if not cleaned:
        return "document"

    return cleaned


def sanitize_currency(value: str | int | float | None) -> int:
    """Convert any currency representation to a plain integer (no decimals).

    Handles:
    - "Rp 1.234.567" -> 1234567
    - "1,234,567.00" -> 1234567
    - "1234567.50" -> 1234568 (rounded)
    - 1234567 -> 1234567
    """
    if value is None or value == "":
        return 0

    if isinstance(value, (int, float)):
        return int(round(value))

    s = str(value).strip()

    # Remove "Rp" prefix and whitespace
    s = re.sub(r"(?i)\brp\.?\s*", "", s)

    # Detect format: if there's both . and ,, the last one is decimal
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            # European format: 1.234,56
            s = s.replace(".", "").replace(",", ".")
        else:
            # US format: 1,234.56
            s = s.replace(",", "")
    elif "," in s:
        # Could be decimal or thousands separator
        # If there are exactly 2 digits after the last comma, treat as decimal
        parts = s.split(",")
        if len(parts[-1]) == 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif s.count(".") > 1:
        # Multiple dots = thousands separators (Indonesian style)
        s = s.replace(".", "")
    elif "." in s:
        # Single dot — could be decimal or thousands. If 3 digits after, it's thousands.
        parts = s.split(".")
        if len(parts[-1]) == 3 and len(parts[0]) <= 3:
            s = s.replace(".", "")

    try:
        return int(round(float(s)))
    except (ValueError, TypeError):
        return 0


def sanitize_date(value: str | date | datetime | None) -> str:
    """Convert any date format to Coretax's expected YYYY-MM-DD ISO format.

    Handles:
    - "01/12/2025" (DD/MM/YYYY) -> "2025-12-01"
    - "12-31-2025" (MM-DD-YYYY) -> "2025-12-31"
    - "2025-12-31" -> "2025-12-31"
    - "31 Desember 2025" -> "2025-12-31"
    - datetime/date objects
    """
    if value is None or value == "":
        return ""

    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    s = str(value).strip()

    # Indonesian month names
    id_months = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
        "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "agu": 8,
        "sep": 9, "okt": 10, "nov": 11, "des": 12,
    }

    # Try Indonesian "31 Desember 2025" format
    m = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", s, re.IGNORECASE)
    if m:
        day, month_str, year = m.groups()
        month = id_months.get(month_str.lower())
        if month:
            return f"{year}-{month:02d}-{int(day):02d}"

    # Try common formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue

    return ""
