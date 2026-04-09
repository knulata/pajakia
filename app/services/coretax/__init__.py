"""Coretax integration — XML generation, validation, sanitization, error decoding."""

from app.services.coretax.xml_generator import (
    generate_ebupot_xml,
    generate_efaktur_xml,
    generate_spt_masa_pph21_xml,
)
from app.services.coretax.sanitizer import (
    sanitize_npwp,
    sanitize_nik,
    sanitize_filename,
    sanitize_currency,
    sanitize_date,
)
from app.services.coretax.validator import (
    validate_ebupot_xml,
    validate_efaktur_xml,
    ValidationResult,
    KNOWN_CORETAX_ERRORS,
)
from app.services.coretax.error_decoder import (
    decode_error_code,
    suggest_fix,
)

__all__ = [
    "generate_ebupot_xml",
    "generate_efaktur_xml",
    "generate_spt_masa_pph21_xml",
    "sanitize_npwp",
    "sanitize_nik",
    "sanitize_filename",
    "sanitize_currency",
    "sanitize_date",
    "validate_ebupot_xml",
    "validate_efaktur_xml",
    "ValidationResult",
    "KNOWN_CORETAX_ERRORS",
    "decode_error_code",
    "suggest_fix",
]
