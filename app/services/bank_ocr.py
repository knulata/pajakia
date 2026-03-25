"""Bank statement OCR — extract transactions from Indonesian bank statements."""

import base64
import json
import logging

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BANK_STATEMENT_PROMPT = """Anda adalah ahli keuangan Indonesia. Ekstrak semua transaksi dari foto/PDF mutasi rekening bank ini.

Format output JSON:
{
  "bank": "BCA/Mandiri/BRI/BNI/dll",
  "nomor_rekening": "",
  "nama_pemilik": "",
  "periode": {"dari": "YYYY-MM-DD", "sampai": "YYYY-MM-DD"},
  "mata_uang": "IDR",
  "saldo_awal": 0,
  "saldo_akhir": 0,
  "transaksi": [
    {
      "tanggal": "YYYY-MM-DD",
      "keterangan": "",
      "debit": 0,
      "kredit": 0,
      "saldo": 0,
      "kategori": ""
    }
  ],
  "ringkasan": {
    "total_debit": 0,
    "total_kredit": 0,
    "jumlah_transaksi": 0
  }
}

Kategori yang mungkin:
- "gaji" — penerimaan gaji/honorarium
- "transfer_masuk" — transfer dari pihak lain
- "transfer_keluar" — transfer ke pihak lain
- "pembayaran" — pembayaran tagihan/vendor
- "pajak" — pembayaran pajak (PPh, PPN, dll)
- "bunga" — bunga bank
- "biaya_admin" — biaya administrasi bank
- "tarik_tunai" — penarikan tunai/ATM
- "setor_tunai" — setoran tunai
- "lainnya" — transaksi lain

PENTING:
- Semua angka harus number, bukan string
- Debit = uang keluar, Kredit = uang masuk
- Jika tidak terbaca, isi null
- Kembalikan HANYA JSON"""


async def extract_bank_statement(image_data: bytes, mime_type: str = "image/jpeg") -> dict:
    """Extract transactions from a bank statement image/PDF page."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    b64 = base64.b64encode(image_data).decode("utf-8")

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": BANK_STATEMENT_PROMPT},
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
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        return json.loads(content)

    except json.JSONDecodeError:
        logger.warning("Bank OCR returned non-JSON: %s", content[:200])
        return {"raw_text": content, "parse_error": True}
    except Exception as e:
        logger.error("Bank OCR failed: %s", e)
        return {"error": str(e)}


def categorize_for_tax(transactions: list[dict]) -> dict:
    """Categorize bank transactions into tax-relevant buckets."""
    income = []
    expenses = []
    tax_payments = []

    for txn in transactions:
        cat = txn.get("kategori", "lainnya")
        amount_in = txn.get("kredit", 0) or 0
        amount_out = txn.get("debit", 0) or 0

        if cat == "pajak":
            tax_payments.append(txn)
        elif amount_in > 0 and cat in ("gaji", "transfer_masuk"):
            income.append(txn)
        elif amount_out > 0 and cat in ("pembayaran", "transfer_keluar"):
            expenses.append(txn)

    return {
        "income": {
            "count": len(income),
            "total": sum(t.get("kredit", 0) or 0 for t in income),
            "transactions": income,
        },
        "expenses": {
            "count": len(expenses),
            "total": sum(t.get("debit", 0) or 0 for t in expenses),
            "transactions": expenses,
        },
        "tax_payments": {
            "count": len(tax_payments),
            "total": sum(t.get("debit", 0) or 0 for t in tax_payments),
            "transactions": tax_payments,
        },
    }
