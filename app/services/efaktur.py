"""e-Faktur batch generation and PPN management."""

import csv
import io
import logging
from dataclasses import dataclass, field
from datetime import date

logger = logging.getLogger(__name__)


@dataclass
class FakturPajakItem:
    kode_transaksi: str = "01"  # 01=kepada bukan pemungut
    kode_status: str = "0"  # 0=normal, 1=pengganti
    nomor_faktur: str = ""
    tanggal: str = ""  # DD/MM/YYYY
    npwp_pembeli: str = ""
    nama_pembeli: str = ""
    alamat_pembeli: str = ""
    dpp: float = 0
    ppn: float = 0
    ppnbm: float = 0
    is_creditable: bool = True  # Pajak masukan yang dapat dikreditkan
    barang_jasa: list = field(default_factory=list)


@dataclass
class FakturLine:
    nama: str
    harga_satuan: float
    jumlah: float
    diskon: float = 0
    dpp: float = 0
    ppn: float = 0
    tarif_ppnbm: float = 0
    ppnbm: float = 0


@dataclass
class PPNSummary:
    masa: int  # Month
    tahun: int
    total_keluaran_dpp: float = 0
    total_keluaran_ppn: float = 0
    total_masukan_dpp: float = 0
    total_masukan_ppn: float = 0
    kurang_bayar: float = 0
    lebih_bayar: float = 0
    faktur_keluaran: list = field(default_factory=list)
    faktur_masukan: list = field(default_factory=list)


def generate_efaktur_csv(fakturs: list[FakturPajakItem]) -> str:
    """Generate CSV file compatible with e-Faktur import format.

    Format: FK (faktur header) + OF (detail barang/jasa) rows
    This follows the DJP e-Faktur CSV import specification.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    for fp in fakturs:
        # FK row — Faktur header
        kode_jenis = f"{fp.kode_transaksi}{fp.kode_status}"
        writer.writerow([
            "FK",  # Record type
            kode_jenis,  # Kode-Status
            fp.nomor_faktur,  # Nomor Faktur
            fp.tanggal,  # Tanggal
            fp.npwp_pembeli,  # NPWP Pembeli
            fp.nama_pembeli,  # Nama Pembeli
            fp.alamat_pembeli,  # Alamat Pembeli
            int(fp.dpp),  # DPP
            int(fp.ppn),  # PPN
            int(fp.ppnbm),  # PPnBM
            0,  # ID Keterangan Tambahan
            0,  # FG Pengganti
            0,  # Referensi
        ])

        # OF rows — Detail barang/jasa
        for line in fp.barang_jasa:
            if isinstance(line, dict):
                line = FakturLine(**line)
            writer.writerow([
                "OF",  # Record type
                line.nama,
                int(line.harga_satuan),
                int(line.jumlah),
                int(line.dpp),
                int(line.diskon),
                int(line.ppn),
                line.tarif_ppnbm,
                int(line.ppnbm),
            ])

    return output.getvalue()


def calculate_ppn_summary(
    faktur_keluaran: list[FakturPajakItem],
    faktur_masukan: list[FakturPajakItem],
    masa: int,
    tahun: int,
) -> PPNSummary:
    """Calculate monthly PPN summary (SPT Masa PPN)."""
    total_keluaran_dpp = sum(f.dpp for f in faktur_keluaran)
    total_keluaran_ppn = sum(f.ppn for f in faktur_keluaran)
    total_masukan_dpp = sum(f.dpp for f in faktur_masukan if f.is_creditable)
    total_masukan_ppn = sum(f.ppn for f in faktur_masukan if f.is_creditable)

    selisih = total_keluaran_ppn - total_masukan_ppn
    kurang_bayar = max(0, selisih)
    lebih_bayar = max(0, -selisih)

    return PPNSummary(
        masa=masa,
        tahun=tahun,
        total_keluaran_dpp=total_keluaran_dpp,
        total_keluaran_ppn=total_keluaran_ppn,
        total_masukan_dpp=total_masukan_dpp,
        total_masukan_ppn=total_masukan_ppn,
        kurang_bayar=kurang_bayar,
        lebih_bayar=lebih_bayar,
        faktur_keluaran=[f.__dict__ for f in faktur_keluaran],
        faktur_masukan=[f.__dict__ for f in faktur_masukan],
    )


def invoices_to_fakturs(
    invoices: list[dict],
    seller_npwp: str,
    ppn_rate: float = 0.11,
) -> list[FakturPajakItem]:
    """Convert a list of invoices to e-Faktur entries.

    Each invoice dict: buyer_npwp, buyer_name, buyer_address, date, items: [{name, price, qty}]
    """
    fakturs = []
    for inv in invoices:
        items = inv.get("items", [])
        lines = []
        total_dpp = 0

        for item in items:
            price = item.get("price", 0)
            qty = item.get("qty", 1)
            dpp = price * qty
            ppn = round(dpp * ppn_rate)
            total_dpp += dpp
            lines.append(FakturLine(
                nama=item.get("name", ""),
                harga_satuan=price,
                jumlah=qty,
                dpp=dpp,
                ppn=ppn,
            ))

        total_ppn = round(total_dpp * ppn_rate)

        fakturs.append(FakturPajakItem(
            tanggal=inv.get("date", date.today().strftime("%d/%m/%Y")),
            npwp_pembeli=inv.get("buyer_npwp", ""),
            nama_pembeli=inv.get("buyer_name", ""),
            alamat_pembeli=inv.get("buyer_address", ""),
            dpp=total_dpp,
            ppn=total_ppn,
            barang_jasa=lines,
        ))

    return fakturs
