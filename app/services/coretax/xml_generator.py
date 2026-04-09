"""Generate Coretax-compatible XML files for upload.

Coretax now requires XML format (replacing CSV/PDF) for:
- e-Bupot Unifikasi (PPh 21, 23, 26, 4(2))
- e-Faktur (PPN)
- SPT Masa PPh 21

Reference: https://www.pajak.go.id/index.php/en/node/112031
"""

from datetime import datetime
from xml.dom import minidom
from xml.etree import ElementTree as ET

from app.services.coretax.sanitizer import (
    sanitize_npwp,
    sanitize_nik,
    sanitize_currency,
    sanitize_date,
)


def _pretty(elem: ET.Element) -> str:
    """Return pretty-printed XML string for an element."""
    rough = ET.tostring(elem, encoding="unicode")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")


def generate_ebupot_xml(
    bukti_potong_list: list[dict],
    pemotong_npwp: str,
    pemotong_nama: str,
    masa: int,
    tahun: int,
) -> str:
    """Generate e-Bupot Unifikasi XML for batch upload to Coretax.

    Each bukti_potong dict expects keys:
    - nama_penerima, npwp_penerima, nik_penerima
    - kode_objek_pajak (e.g. "21-100-01" for gaji karyawan)
    - penghasilan_bruto, pph_dipotong
    - tarif (e.g. 5, 15, 25, 30, 35)
    - tanggal_bukti_potong
    - nomor_bukti_potong
    """
    root = ET.Element("CoretaxBuktiPotong", attrib={
        "xmlns": "http://coretax.pajak.go.id/schema/v1",
        "version": "1.0",
    })

    # Header
    header = ET.SubElement(root, "Header")
    ET.SubElement(header, "JenisBukti").text = "BPPU"  # Bukti Potong PPh Unifikasi
    ET.SubElement(header, "MasaPajak").text = f"{masa:02d}"
    ET.SubElement(header, "TahunPajak").text = str(tahun)
    ET.SubElement(header, "NPWPPemotong").text = sanitize_npwp(pemotong_npwp)
    ET.SubElement(header, "NamaPemotong").text = pemotong_nama
    ET.SubElement(header, "TanggalLapor").text = datetime.now().date().isoformat()
    ET.SubElement(header, "JumlahBukti").text = str(len(bukti_potong_list))

    # Bukti Potong items
    bukti_list = ET.SubElement(root, "DaftarBuktiPotong")
    for i, bp in enumerate(bukti_potong_list, start=1):
        item = ET.SubElement(bukti_list, "BuktiPotong", attrib={"nomor": str(i)})

        ET.SubElement(item, "NomorBP").text = str(bp.get("nomor_bukti_potong", f"BP{i:06d}"))
        ET.SubElement(item, "TanggalBP").text = sanitize_date(
            bp.get("tanggal_bukti_potong") or datetime.now().date()
        )

        # Penerima
        penerima = ET.SubElement(item, "Penerima")
        npwp = sanitize_npwp(bp.get("npwp_penerima", ""))
        nik = sanitize_nik(bp.get("nik_penerima", ""))
        ET.SubElement(penerima, "NPWP").text = npwp
        ET.SubElement(penerima, "NIK").text = nik
        ET.SubElement(penerima, "Nama").text = str(bp.get("nama_penerima", "")).strip()

        # Pajak
        pajak = ET.SubElement(item, "DataPajak")
        ET.SubElement(pajak, "KodeObjekPajak").text = str(bp.get("kode_objek_pajak", "21-100-01"))
        ET.SubElement(pajak, "DPP").text = str(sanitize_currency(bp.get("penghasilan_bruto", 0)))
        ET.SubElement(pajak, "Tarif").text = str(bp.get("tarif", 5))
        ET.SubElement(pajak, "PPhDipotong").text = str(sanitize_currency(bp.get("pph_dipotong", 0)))

    return _pretty(root)


def generate_efaktur_xml(
    faktur_list: list[dict],
    seller_npwp: str,
    seller_nama: str,
    masa: int,
    tahun: int,
    ppn_rate: float = 0.11,
) -> str:
    """Generate e-Faktur XML for Coretax PPN upload.

    Each faktur dict expects:
    - nomor_faktur, tanggal_faktur
    - npwp_pembeli, nama_pembeli
    - dpp, ppn (or compute from dpp * ppn_rate)
    - kode_transaksi (default "01")
    - barang_jasa: list of {nama, harga, jumlah}
    """
    root = ET.Element("CoretaxFakturPajak", attrib={
        "xmlns": "http://coretax.pajak.go.id/schema/v1",
        "version": "1.0",
    })

    header = ET.SubElement(root, "Header")
    ET.SubElement(header, "NPWPPenjual").text = sanitize_npwp(seller_npwp)
    ET.SubElement(header, "NamaPenjual").text = seller_nama
    ET.SubElement(header, "MasaPajak").text = f"{masa:02d}"
    ET.SubElement(header, "TahunPajak").text = str(tahun)
    ET.SubElement(header, "TarifPPN").text = str(ppn_rate * 100)
    ET.SubElement(header, "JumlahFaktur").text = str(len(faktur_list))

    daftar = ET.SubElement(root, "DaftarFaktur")
    for i, f in enumerate(faktur_list, start=1):
        faktur = ET.SubElement(daftar, "Faktur", attrib={"nomor": str(i)})

        kode = str(f.get("kode_transaksi", "01"))
        nomor = str(f.get("nomor_faktur", "")).strip()
        ET.SubElement(faktur, "KodeTransaksi").text = kode
        ET.SubElement(faktur, "NomorFaktur").text = nomor
        ET.SubElement(faktur, "TanggalFaktur").text = sanitize_date(f.get("tanggal_faktur"))

        # Pembeli
        pembeli = ET.SubElement(faktur, "Pembeli")
        ET.SubElement(pembeli, "NPWP").text = sanitize_npwp(f.get("npwp_pembeli", ""))
        ET.SubElement(pembeli, "Nama").text = str(f.get("nama_pembeli", "")).strip()
        ET.SubElement(pembeli, "Alamat").text = str(f.get("alamat_pembeli", "")).strip()

        # Items
        dpp = sanitize_currency(f.get("dpp", 0))
        ppn = sanitize_currency(f.get("ppn", 0)) or int(round(dpp * ppn_rate))

        items = ET.SubElement(faktur, "Items")
        for bj in f.get("barang_jasa", []):
            item = ET.SubElement(items, "Item")
            ET.SubElement(item, "Nama").text = str(bj.get("nama", "Item"))
            ET.SubElement(item, "Harga").text = str(sanitize_currency(bj.get("harga", 0)))
            ET.SubElement(item, "Jumlah").text = str(bj.get("jumlah", 1))

        totals = ET.SubElement(faktur, "Totals")
        ET.SubElement(totals, "DPP").text = str(dpp)
        ET.SubElement(totals, "PPN").text = str(ppn)

    return _pretty(root)


def generate_spt_masa_pph21_xml(
    employees: list[dict],
    pemotong_npwp: str,
    pemotong_nama: str,
    masa: int,
    tahun: int,
) -> str:
    """Generate SPT Masa PPh 21 XML for Coretax.

    Each employee dict expects:
    - npwp, nik, nama
    - status_ptkp (TK/0, K/1, etc)
    - bruto_bulan, pph_dipotong
    """
    root = ET.Element("CoretaxSPTMasa", attrib={
        "xmlns": "http://coretax.pajak.go.id/schema/v1",
        "jenis": "PPh21",
        "version": "1.0",
    })

    header = ET.SubElement(root, "Header")
    ET.SubElement(header, "NPWPPemotong").text = sanitize_npwp(pemotong_npwp)
    ET.SubElement(header, "NamaPemotong").text = pemotong_nama
    ET.SubElement(header, "MasaPajak").text = f"{masa:02d}"
    ET.SubElement(header, "TahunPajak").text = str(tahun)
    ET.SubElement(header, "JumlahPegawai").text = str(len(employees))

    total_bruto = sum(sanitize_currency(e.get("bruto_bulan", 0)) for e in employees)
    total_pph = sum(sanitize_currency(e.get("pph_dipotong", 0)) for e in employees)
    ET.SubElement(header, "TotalBruto").text = str(total_bruto)
    ET.SubElement(header, "TotalPPh").text = str(total_pph)

    daftar = ET.SubElement(root, "DaftarPegawai")
    for i, e in enumerate(employees, start=1):
        peg = ET.SubElement(daftar, "Pegawai", attrib={"nomor": str(i)})
        ET.SubElement(peg, "NPWP").text = sanitize_npwp(e.get("npwp", ""))
        ET.SubElement(peg, "NIK").text = sanitize_nik(e.get("nik", ""))
        ET.SubElement(peg, "Nama").text = str(e.get("nama", "")).strip()
        ET.SubElement(peg, "StatusPTKP").text = str(e.get("status_ptkp", "TK/0"))
        ET.SubElement(peg, "PenghasilanBruto").text = str(sanitize_currency(e.get("bruto_bulan", 0)))
        ET.SubElement(peg, "PPhDipotong").text = str(sanitize_currency(e.get("pph_dipotong", 0)))

    return _pretty(root)
