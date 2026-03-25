"""OCR service for Indonesian tax documents using OpenAI Vision API."""

import base64
import json
import logging
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BUKTI_POTONG_PROMPT = """Anda adalah ahli pajak Indonesia. Ekstrak semua data dari foto bukti potong ini ke dalam format JSON.

Untuk Bukti Potong 1721-A1 (karyawan swasta), ekstrak:
{
  "jenis_formulir": "1721-A1",
  "masa_pajak": "01-12",
  "tahun_pajak": 2025,
  "npwp_pemotong": "",
  "nama_pemotong": "",
  "npwp_penerima": "",
  "nama_penerima": "",
  "nik": "",
  "alamat": "",
  "jenis_kelamin": "",
  "status_ptkp": "TK/0",
  "nama_jabatan": "",
  "penghasilan_bruto": {
    "gaji": 0,
    "tunjangan_pph": 0,
    "tunjangan_lainnya": 0,
    "honorarium": 0,
    "premi_asuransi": 0,
    "natura": 0,
    "bonus_thr": 0,
    "total_bruto": 0
  },
  "pengurang": {
    "biaya_jabatan": 0,
    "iuran_pensiun": 0,
    "total_pengurang": 0
  },
  "perhitungan_pph": {
    "neto_setahun": 0,
    "neto_masa_sebelumnya": 0,
    "total_neto": 0,
    "ptkp": 0,
    "pkp": 0,
    "pph21_terutang": 0,
    "pph21_telah_dipotong": 0,
    "pph21_kurang_lebih_bayar": 0
  },
  "nomor_bukti_potong": "",
  "tanggal_bukti_potong": ""
}

Untuk Bukti Potong 1721-A2 (PNS/TNI/Polri), formatnya serupa tapi dengan komponen tunjangan yang berbeda.

PENTING:
- Semua angka harus berupa number, bukan string
- Jika tidak terbaca, isi dengan null
- Status PTKP harus dalam format: TK/0, TK/1, K/0, K/1, dll
- Kembalikan HANYA JSON, tanpa teks tambahan"""

FAKTUR_PAJAK_PROMPT = """Anda adalah ahli pajak Indonesia. Ekstrak data dari foto faktur pajak ini ke dalam format JSON:

{
  "jenis": "faktur_pajak",
  "kode_transaksi": "",
  "nomor_seri": "",
  "tanggal": "",
  "npwp_penjual": "",
  "nama_penjual": "",
  "alamat_penjual": "",
  "npwp_pembeli": "",
  "nama_pembeli": "",
  "alamat_pembeli": "",
  "barang_jasa": [
    {
      "nama": "",
      "harga_satuan": 0,
      "jumlah": 0,
      "harga_total": 0
    }
  ],
  "dpp": 0,
  "ppn": 0,
  "ppnbm": 0,
  "total": 0
}

Kembalikan HANYA JSON, tanpa teks tambahan."""


async def extract_bukti_potong(image_data: bytes, mime_type: str = "image/jpeg") -> dict:
    """Extract data from a bukti potong image using GPT-4 Vision."""
    return await _extract_with_vision(image_data, mime_type, BUKTI_POTONG_PROMPT)


async def extract_faktur_pajak(image_data: bytes, mime_type: str = "image/jpeg") -> dict:
    """Extract data from a faktur pajak image using GPT-4 Vision."""
    return await _extract_with_vision(image_data, mime_type, FAKTUR_PAJAK_PROMPT)


async def detect_document_type(image_data: bytes, mime_type: str = "image/jpeg") -> str:
    """Auto-detect the type of tax document from an image."""
    result = await _extract_with_vision(
        image_data,
        mime_type,
        'Identifikasi jenis dokumen pajak Indonesia dalam foto ini. '
        'Kembalikan HANYA satu dari: "1721-A1", "1721-A2", "faktur_pajak", '
        '"bukti_potong_pph23", "bukti_potong_pph4_2", "unknown". '
        'Tanpa penjelasan, hanya satu kata/frasa.',
    )
    return result.get("type", "unknown") if isinstance(result, dict) else str(result)


async def _extract_with_vision(image_data: bytes, mime_type: str, prompt: str) -> dict:
    """Send image to OpenAI Vision API and parse JSON response."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    b64 = base64.b64encode(image_data).decode("utf-8")

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        return json.loads(content)

    except json.JSONDecodeError:
        logger.warning("OCR returned non-JSON: %s", content[:200])
        return {"raw_text": content, "parse_error": True}
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return {"error": str(e)}
