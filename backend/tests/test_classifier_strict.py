import pytest
from app.agents.nodes.classifier_node import _fallback_keyword_classify


def test_classify_backdoor_listing():
    title = "Emiten Cangkang Siap Lakukan Backdoor Listing dan Injeksi Aset"
    text = "Perubahan kegiatan usaha utama dan injeksi aset baru ke perusahaan dormant."
    res = _fallback_keyword_classify("TEST", title, text)
    assert res.category == "BACKDOOR_LISTING"
    assert res.confidence_score >= 0.85


def test_classify_konglo_move():
    title = "Grup Salim dan Barito Prajogo Pangestu Akumulasi Saham BUMI"
    text = "Crossing pasar negosiasi jumbo oleh smart money Salim Group senilai Rp 24 Triliun."
    res = _fallback_keyword_classify("BUMI", title, text)
    assert res.category == "KONGLO_MOVE"
    assert res.confidence_score >= 0.85


def test_classify_irrelevant_strict_rule():
    """
    Aturan Ketat:
    Berita rutinitas seperti pembagian dividen biasa atau RUPS biasa tanpa partisipasi
    konglomerat WAJIB diklasifikasikan sebagai IRRELEVANT.
    """
    title = "Jadwal Pembagian Dividen Tunai Saham ASII dan Laporan Keuangan"
    text = "Emiten mengumumkan pembayaran dividen rutin tahun buku 2025 kepada pemegang saham."
    res = _fallback_keyword_classify("ASII", title, text)
    assert res.category == "IRRELEVANT"
    assert res.confidence_score >= 0.90
